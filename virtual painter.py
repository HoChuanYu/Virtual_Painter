import cv2
import numpy as np
import  time
import os
#from cvzone.HandTrackingModule import HandDetector
import HandTrackingModule as htm

folderPath = "header"
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

img_test = cv2.imread('test.PNG')
img_test = cv2.resize(img_test, (1280, 720), interpolation=cv2.INTER_AREA)
cursor = cv2.imread('cursor2.png')
cursor = cv2.resize(cursor, (20, 20), interpolation=cv2.INTER_AREA)

while True:
    #step 1: Import image
    success, img = cap.read()
    img = cv2.flip(img,1)
    img_test = cv2.imread('test.PNG')
    img_test = cv2.resize(img_test, (1280, 720), interpolation=cv2.INTER_AREA)

    #step 2: hand tracking
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)

    if len(lmList) != 0:

        x1, y1 = lmList[8][1:];  #index finger tip position
        x2, y2 = lmList[12][1:]; #middle finger tip position

        #step 3: check which finger are up
        fingers = detector.fingersUP()
        #print(fingers)
        #draw mode: when only index up
        if fingers[1] and fingers[2] == False:
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
            if y1 < 125:
                if 180 < x1 < 280:
                    header = overlayLis[0]
                    drawColor = (0, 0, 255)
                    #print('mode 1')
                elif 450 < x1 < 550:
                    header = overlayLis[1]
                    drawColor = (255, 0, 0)
                    #print('mode 2')
                elif 700 < x1 < 850:
                    header = overlayLis[2]
                    drawColor = (0, 255, 0)
                    #print('mode 3')
                elif 1050 < x1 < 1250:
                    header = overlayLis[3]
                    drawColor = (0, 0, 0)
                    #print('mode 4')
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
            img_test[y1:y1 + 20, x1:x1 + 20] = cursor


    cv2.imshow('cursor', cursor)
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)

    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    img_test = cv2.bitwise_and(img_test, imgInv)
    img_test = cv2.bitwise_or(img_test, imgCanvas)

    #setting the header img
    img[0:125, 0:1280] = header
    img = cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)
    img_test = cv2.addWeighted(img_test, 0.5, imgCanvas, 0.5, 0)
    cv2.imshow('img', img)
    cv2.imshow('imgCanvas', imgCanvas)
    cv2.imshow('test PDF', img_test)
    cv2.waitKey(1)