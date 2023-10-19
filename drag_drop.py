import cv2
from cvzone.HandTrackingModule import HandDetector
import  cvzone
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8, maxHands=2)
colorR = (255, 0, 0)

cx, cy, w, h = 100, 100, 200, 200


class DragRect():
    def __init__(self, posCenter, size=[200, 200]):
        self.posCenter = posCenter
        self.size = size

    def update(self, cursor):
        cx, cy = self.posCenter
        w, h = self.size

        # if the index finger tip inside the rectangle region
        if cx - w // 2 < cursor[0] < cx + w // 2 and cy - h // 2 < cursor[1] < cy + h // 2:
            self.posCenter = cursor


rectList = []
for x in range(5):
    rectList.append(DragRect([x * 250 + 150, 150]))
rect = DragRect([150, 150])

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)  # hand imformation are inside hands
    # lmList, _ = detector.findPosition(img)  #already been remove from cvzon 1.5
    if hands:

        # Hand #1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # list of 21 landmarks point
        #bbbox1 = hand1["bbox"]  # bounding box info x,y,w,h
        #centerPoint1 = hand1["center"]  # center of the hand cx,cy
        #handType1 = hand1["type"]  # Hand Type Left or right

        # print(len(lmList1), lmList1)
        # print(bbbox1)
        #print(handType1)

        if lmList1:
            l, _, _ = detector.findDistance(lmList1[8], lmList1[12], img)
            print(l)
            if l < 40:
                cursor = lmList1[8]  # the point of index finger
                # call the update here
                for rect in rectList:
                    rect.update(cursor)

    # for rect in rectList:
    #     cx, cy = rect.posCenter
    #     w, h = rect.size
    #     cv2.rectangle(img, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), colorR, cv2.FILLED)
    #
    #     cvzone.cornerRect(img,(cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), 20, rt=0)

    imgNew = np.zeros_like(img, np.uint8)
    for rect in rectList:
        cx, cy = rect.posCenter
        w, h = rect.size
        cv2.rectangle(img, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), colorR, cv2.FILLED)
        cvzone.cornerRect(imgNew, (cx - w // 2, cy - h // 2, w, h), 20, rt=0)
    out = img.copy()
    alpha = 0.1
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1- alpha, 0)[mask]

    cv2.imshow("Image", out)
    cv2.waitKey(1)
