import cv2
import numpy as np
import time
import os
import math
#from cvzone.HandTrackingModule import HandDetector
import HandTrackingModule as htm

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

xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

folderPath = "pdf_save"
save_path = "pdf_save/"
myList = os.listdir(folderPath)
#print(myList)
back_ground = []

for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    back_ground.append(image)

page_max = len(back_ground)
page = 0

img_test = cv2.imread('test.PNG')
img_test = cv2.resize(img_test, (1280, 720), interpolation=cv2.INTER_AREA)
cursor = cv2.imread('cursor2.png')
cursor = cv2.resize(cursor, (20, 20), interpolation=cv2.INTER_AREA)

#read the next page and previous page icon
img_next_page = cv2.imread('UI/next.png')
img_prev_page = cv2.imread('UI/prev.png')
img_next_page = cv2.resize(img_next_page, (50,50),interpolation=cv2.INTER_AREA)
img_prev_page = cv2.resize(img_prev_page, (50,50),interpolation=cv2.INTER_AREA)


pen_radius = 30
drawColor_mode = 1
#1: blue
#2: red
#3: yellow
cv2.circle(header, (880, 64), pen_radius, drawColor, cv2.FILLED)



while True:
    #step 1: Import image
    success, img = cap.read()
    #img = cv2.flip(img,1)
    img_test = back_ground[page]
    img_test = cv2.resize(img_test, (1280, 720), interpolation=cv2.INTER_AREA)

    #step 2: hand tracking
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)

    if len(lmList) != 0:
        x0, y0 = lmList[4][1:];
        x1, y1 = lmList[8][1:];  #index finger tip position
        x2, y2 = lmList[12][1:]; #middle finger tip position



        #step 3: check which finger are up
        fingers = detector.fingersUP()
        #print(fingers)
        #draw mode: when only index up
        if fingers[1] and fingers[2] == False and y1 > 128:
            cv2.circle(img, (x1, y1), 15, (255, 255, 255), cv2.FILLED)
            cv2.circle(img_test, (x1, y1), 5, (255, 255, 255), cv2.FILLED)
            #print('drawing mode')
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(img_test, (xp, yp), (x1, y1),drawColor, eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(img_test, (xp, yp), (x1, y1), drawColor, brushThickness)
            xp, yp = x1, y1
        #selection mode: when two finger up
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            #print("Selection mode")
            #print(x1)
            if y1 < 128:
                if 0 < x1 < 145: #draw mode
                    header = overlayLis[drawColor_mode]
                    #drawColor = (0, 0, 0)
                elif 156 < x1 < 280: #erase mode
                    drawColor_mode = 0
                    header = overlayLis[drawColor_mode]
                    drawColor = (0, 0, 0)
                elif 280 < x1 < 430: # take picture
                    header = overlayLis[0]
                    #drawColor = (0, 0, 0)
                elif 430 < x1 < 540: # blue
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
                    length = math.hypot(x2 - x1, y2 - y1)
                    print(length)
                    pen_radius = int(length/10)

                    if drawColor_mode == 0:
                        eraserThickness = pen_radius
                    else:
                        brushThickness = pen_radius
            elif 128 < y1 < 180 and (0 < x1 < 50 or 1220 < x1 < 1280):
                #previous page
                length = math.hypot(x2 - x1, y2 - y1)
                print(length)

                if length < 40 and 0 < x2 < 50 and page > 0:

                    fname = 'image' + str(page) + '.png'

                    #save image

                    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)

                    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

                    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

                    img_test = cv2.bitwise_and(img_test, imgInv)
                    img_test = cv2.bitwise_or(img_test, imgCanvas)
                    #img_test = cv2.addWeighted(img_test, 0.5, imgCanvas, 0.5, 0)

                    cv2.imwrite(f"{save_path}" + fname, img_test)
                    page = page - 1
                    imgCanvas = np.zeros((720, 1280, 3), np.uint8)
                    time.sleep(0.5)

                elif length < 40 and 1220 < x2 < 1280 and page < page_max-1:

                    fname = 'image' + str(page) + '.png'

                    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)

                    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

                    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

                    img_test = cv2.bitwise_and(img_test, imgInv)
                    img_test = cv2.bitwise_or(img_test, imgCanvas)
                    #img_test = cv2.addWeighted(img_test, 0.5, imgCanvas, 0.5, 0)
                    cv2.imwrite(f"{save_path}" + fname, img_test)
                    page = page + 1
                    imgCanvas = np.zeros((720, 1280, 3), np.uint8)
                    time.sleep(0.5)

            cv2.circle(header, (880, 64), pen_radius, drawColor, cv2.FILLED)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
            print(x1,y1)
            if x1+20 < 1280 and y1+20 < 720 and x1 > 0 and y1 > 0:
                img_test[y1:y1 + 20, x1:x1 + 20] = cursor

    cv2.putText(img_test, str(page) , (1250, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)

    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    img_test = cv2.bitwise_and(img_test, imgInv)
    img_test = cv2.bitwise_or(img_test, imgCanvas)

    #setting the header img
    img[0:128, 0:1280] = header
    img_test[0:128, 0:1280] = header
    img_test[130:180, 1220:1270] = img_next_page
    img_test[130:180, 10:60] = img_prev_page

    #img = cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)
    #img_test = cv2.addWeighted(img_test, 0.5, imgCanvas, 0.5, 0)

    cv2.imshow('imgCanvas', imgCanvas)
    cv2.imshow('test PDF', img_test)
    cv2.waitKey(1)