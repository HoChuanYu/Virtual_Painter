import cv2
from cvzone.HandTrackingModule import HandDetector

class PicZoom():
    def __init__(self):
        self.detector = HandDetector(detectionCon=0.7)
        self.startDist = None
        self.scale = 0
        self.cx, self.cy = 500, 500

    def zoom(self, img, png):
        hands, img = self.detector.findHands(img)
        img1 = cv2.imread("images.jfif")
        # if len(hands) != 0:
        #     if detector.fingersUp(hands[0]) == [1, 1, 1, 1, 1]:
        #         print('all up')
        #     else:
        #         print('one down')

        if len(hands) == 2:
            #print(detector.fingersUp(hands[0]))
            if self.detector.fingersUp(hands[0]) == [1, 1, 0, 0, 0] and \
                    self.detector.fingersUp(hands[1]) == [1, 0, 1, 1, 1]:
                # print("Zoom Gesture")
                self.lmList1 = hands[0]["lmList"]
                self.lmList2 = hands[1]["lmList"]
                # point 8 is the tip of the index finger
                if self.startDist is None:
                    # length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)
                    length, info, img = self.detector.findDistance(hands[0]["center"], hands[1]["center"], img)

                    self.startDist = length

                # length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)
                length, info, img = self.detector.findDistance(hands[0]["center"], hands[1]["center"], img)

                self.scale = int((length - self.startDist) // 2)
                self.cx, self.cy = info[4:]
                print(self.scale)
        else:
            self.startDist = None

        try:
            h1, w1, _ = img1.shape
            newH, newW = ((h1 + self.scale) // 2) * 2, ((w1 + self.scale) // 2) * 2
            img1 = cv2.resize(img1, (newW, newH))

            img[self.cy - newH // 2:self.cy + newH // 2, self.cx - newW // 2:self.cx + newW // 2] = img1
        except:
            pass

        return img


    def screenShot(self, img, png, shot_count):
        hands, img = self.detector.findHands(img)
        #print(detector.fingersUp(hands[0]))    
        # TODO 手的動作還不確定，截圖可能要再看能不能確定現在判斷的是左手還右手
        print('test')

        if (len(hands) == 2) and (self.detector.fingersUp(hands[1]) == [1, 1, 1, 1, 1] and self.detector.fingersUp(hands[0]) == [1, 1, 1, 1, 1]):
            self.lmList1 = hands[0]["lmList"]
            self.lmList2 = hands[1]["lmList"]
            x1, y1 = self.lmList1[2]
            x2, y2 = self.lmList2[2]
            #cv2.rectangle(png, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
            PNG_Cropped = png[min(y1,y2):max(y1,y2), min(x1,x2):max(x1,x2)]
            cv2.imwrite('ScreenShot'+str(shot_count) + '.png', PNG_Cropped)
            cv2.imshow('ScreenShot'+str(shot_count),PNG_Cropped)
            cv2.waitKey(1)
            return shot_count+1, False, png
        else:
            return shot_count, True, png
