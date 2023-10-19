import cv2
from cvzone.HandTrackingModule import HandDetector
from pdf2image import convert_from_path
import os
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.7,maxHands=1)
startDist = None
scale = 0
cx, cy = 500, 500

# Store Pdf with convert_from_path function

folderPath = "pdf_save"
myList = os.listdir(folderPath)
#print(myList)
overlayLis = []


images = convert_from_path("test.pdf", 500,poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
list(enumerate(images))
save_path = "pdf_save/"

for i, image in enumerate(images):
    fname = 'image'+str(i)+'.png'
    image = np.array(image)
    image = cv2.resize(image, (1280, 720))
    cv2.imwrite(f"{save_path}"+fname, image)
    #image.save(f"{save_path}"+fname, "PNG")

for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    image = cv2.resize(image,(1280, 720), interpolation=cv2.INTER_AREA)
    overlayLis.append(image)

#print(len(overlayLis))
header = overlayLis[0]

page = 0
flag = True

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)
    hands = detector.findHands(img, draw=False)
    image = overlayLis[page]
    if len(hands) == 1:
        #print(detector.fingersUp(hands[0]))
        print(page)
        if detector.fingersUp(hands[0]) == [1,1,0,0,1] and flag==True:
            if page < 6:
                page = page+1
                image = overlayLis[page]
                flag = False
            else:
                image = overlayLis[page]
                flag = False
        elif detector.fingersUp(hands[0]) == [0,0,0,0,0] and flag==True:
            if page > 0:
                page = page-1
                image = overlayLis[page]
                flag = False
            else:
                image = overlayLis[page]
                flag = False
        elif detector.fingersUp(hands[0]) == [1,0,0,0,0]:
            flag =True

    cv2.imshow("Image", image)
    cv2.waitKey(1)