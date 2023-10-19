import cv2
import numpy as np
import time
import os
import math
from PIL import Image
from pdf2image import convert_from_path
#from cvzone.HandTrackingModule import HandDetector
import HandTrackingModule as htm
import Zoomer as vz
import Screen as sc
import sys

screen_edge = []
screen = sc.Screen()


folderPath = "UI"
myList = os.listdir(folderPath)
#print(myList)
overlayLis = []

for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayLis.append(image)
#print(len(overlayLis))
header = overlayLis[0]

######################################
drawColor = (0, 0, 0)
brushThickness = 15
eraserThickness = 25
######################################

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

detector = htm.handDetector(detectionCon=0.85) #higher
Zoomer = vz.PicZoom()
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

#pdfname = input('please enter the pdf file name:')


#pdfname='test.pdf'
images = convert_from_path(str(sys.argv[1])+'.pdf',500)#poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
list(enumerate(images))

save_path = "pdf_save/"
back_ground = []
for i, image in enumerate(images):
    fname = 'image'+str(i)+'.png'
    image = np.array(image)
    image = cv2.resize(image, (1280, 720))
    back_ground.append(image)


# TODO 看一下這能不能成功，就不用另外轉圖片直接用image array做事就好
#save_path = "pdf_save/"
#folderPath = "pdf_save"
#myList = os.listdir(folderPath)
#back_ground = []
#
#back_ground = convert_from_path(pdfname, 500)
'''
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    back_ground.append(image)
'''
page_max = len(back_ground)
page = 0
cursor = cv2.imread('cursor2.png')
cursor = cv2.resize(cursor, (20, 20), interpolation=cv2.INTER_AREA)

Canvas = []
for i in range(0, page_max):
    Canvas.append(np.zeros((720, 1280, 3), np.uint8))

#read the next page and previous page icon
img_next_page = cv2.imread('page/next.png')
img_prev_page = cv2.imread('page/prev.png')
img_next_page = cv2.resize(img_next_page, (50,50),interpolation=cv2.INTER_AREA)
img_prev_page = cv2.resize(img_prev_page, (50,50),interpolation=cv2.INTER_AREA)

pen_radius = 30
drawColor_mode = 1
#1: green
#2: red
#3: yellow
cv2.circle(header, (880, 64), pen_radius, drawColor, cv2.FILLED)
shot_flag = False
shot_count = 1

#0
while True:
    #step 1: Import image
    success, img = cap.read()

    if not success:
        break
    #img = cv2.flip(img,1)
    img_test = back_ground[page]
    img_test = cv2.resize(img_test, (1280, 720), interpolation=cv2.INTER_AREA)

    # Screen Edge cut###########################################
    '''if screen_edge is np.empty:
        screen_edge=screen.getContours(img)
    img = screen.getWrap(img, screen_edge)'''
    #cv2.imshow('crpoimg',img)
    
    #截圖時獨立作業###############################################
    if shot_flag:     
        imgGray = cv2.cvtColor(Canvas[page], cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img_test = cv2.bitwise_and(img_test, imgInv)
        img_test = cv2.bitwise_or(img_test, Canvas[page])          
        shot_count, shot_flag, asd = Zoomer.screenShot(img, img_test, shot_count)
        #cv2.imshow("asd", asd)
        #cv2.waitKey(1)
        continue

    #step 2: hand tracking
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)

    if len(lmList) != 0:
        x0, y0 = lmList[4][1:];
        x1, y1 = lmList[8][1:];  #index finger tip position
        x2, y2 = lmList[12][1:]; #middle finger tip position

        #step 3: check which finger are up
        fingers = detector.fingersUP()

        #draw mode: when only index up
        if fingers[1] and (fingers[2] == False) and (y1 > 128):
            cv2.circle(img, (x1, y1), 15, (255, 255, 255), cv2.FILLED)
            cv2.circle(img_test, (x1, y1), 5, (255, 255, 255), cv2.FILLED)
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if drawColor == (0, 0, 0):
                #cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                #cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(Canvas[page], (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(img_test, (xp, yp), (x1, y1),drawColor, eraserThickness)
            else:
                #cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                #cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(Canvas[page], (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(img_test, (xp, yp), (x1, y1), drawColor, brushThickness)
            xp, yp = x1, y1
        #selection mode: when two finger up
        elif fingers[1] and fingers[2]:
            xp, yp = 0, 0
            if y1 < 128:
                if 0 < x1 < 145: #draw mode
                    header = overlayLis[drawColor_mode]
                elif 156 < x1 < 280: #erase mode
                    drawColor_mode = 0
                    header = overlayLis[drawColor_mode]
                    drawColor = (0, 0, 0)
                elif 280 < x1 < 430: # take picture
                    header = overlayLis[0]
                    shot_flag = True
                elif 430 < x1 < 540: # green
                    drawColor_mode = 1
                    header = overlayLis[drawColor_mode]
                    drawColor = (0, 255, 0)

                elif 540 < x1 < 670: # red
                    drawColor_mode = 2
                    header = overlayLis[drawColor_mode]
                    drawColor = (0, 0, 255)

                elif 670 < x1 < 800: # yellow
                    drawColor_mode = 3
                    header = overlayLis[drawColor_mode]
                    drawColor = (0, 255, 255)
                elif y2 < 128 and x1 > 800 and x2 > 800:
                    length = max(math.hypot(x2 - x1, y2 - y1),10)
                    print(length)
                    pen_radius = int(length/3)

                    if drawColor_mode == 0:
                        eraserThickness = pen_radius
                    else:
                        brushThickness = pen_radius
            elif 128 < y1 < 250 and (0 < x1 < 50 or 1220 < x1 < 1280):
                #previous page
                length = math.hypot(x2 - x1, y2 - y1)
                print(length)

                if length < 40 and 40 < x1 < 60 and page > 0:
                    print('page-1=', page)
                    fname = 'image' + str(page) + '.png'

                    #save image

                    #imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
                    imgGray = cv2.cvtColor(Canvas[page], cv2.COLOR_BGR2GRAY)

                    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

                    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

                    img_test = cv2.bitwise_and(img_test, imgInv)
                    #img_test = cv2.bitwise_or(img_test, imgCanvas)
                    img_test = cv2.bitwise_or(img_test, Canvas[page])

                    # TODO 先存在 back_ground裡面, code結束之後再把整個array存回PDF
                    #cv2.imwrite(f"{save_path}" + fname, img_test)
                    #back_ground[page] = img_test
                    page = page - 1
                    #imgCanvas = np.zeros((720, 1280, 3), np.uint8)
                    time.sleep(1)

                elif length < 40 and 1220 < x1 < 1240 and page < page_max-1:
                    print('page+1=', page)
                    fname = 'image' + str(page) + '.png'

                    #imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
                    imgGray = cv2.cvtColor(Canvas[page], cv2.COLOR_BGR2GRAY)

                    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

                    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

                    img_test = cv2.bitwise_and(img_test, imgInv)
                    #img_test = cv2.bitwise_or(img_test, imgCanvas)
                    img_test = cv2.bitwise_or(img_test, Canvas[page])

                    # TODO 先存在 back_ground裡面, code結束之後再把整個array存回PDF
                    #cv2.imwrite(f"{save_path}" + fname, img_test)
                    #back_ground[page] = img_test
                    page = page + 1
                    #imgCanvas = np.zeros((720, 1280, 3), np.uint8)
                    time.sleep(1)

            cv2.circle(header, (880, 64), pen_radius, drawColor, cv2.FILLED)
            #cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)


            if x1+20 < 1280 and y1+20 < 720 and x1 > 0 and y1 > 0:
                img_test[y1:y1 + 20, x1:x1 + 20] = cursor

    imgGray = cv2.cvtColor(Canvas[page], cv2.COLOR_BGR2GRAY)

    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img_test = cv2.bitwise_and(img_test, imgInv)
    img_test = cv2.bitwise_or(img_test, Canvas[page])

    #setting the header img
    full_Screen = np.zeros((848, 1280, 3), np.uint8)
    full_Screen[0:128, 0:1280] = header
    full_Screen[128:, :] = img_test
    full_Screen[130:180, 1220:1270] = img_next_page
    full_Screen[130:180, 10:60] = img_prev_page

    #cv2.imshow('imgCanvas', imgCanvas)
    cv2.imshow('test PDF', full_Screen)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

for i in range(0,page_max):
    img_test = back_ground[i]
    imgGray = cv2.cvtColor(Canvas[i], cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img_test = cv2.bitwise_and(img_test, imgInv)
    img_test = cv2.bitwise_or(img_test, Canvas[i])
    back_ground[i] = img_test
pdf_array=[]
for jpg in back_ground:
    jpg = cv2.cvtColor(jpg, cv2.COLOR_BGR2RGB)
    pdf_array.append(Image.fromarray(jpg,'RGB'))
pdf_array[0].save(r'fixed.pdf',save_all=True, append_images=pdf_array[1:])
# TODO 第一章多一張，黃色變藍色
