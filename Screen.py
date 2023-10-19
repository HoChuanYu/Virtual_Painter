import cv2
import numpy as np
import time

#############################################
widthImg = 840
heightImg = 480
#############################################
class Screen():
    def getContours(self,img):
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(3,3),1)
        imgCanny = cv2.Canny(imgBlur,200,200)
        kernel = np.ones((5,5))
        imgDial = cv2.dilate((imgCanny),kernel,iterations=2)
        imgThres = cv2.erode(imgDial,kernel,iterations=1)
        biggest = np.float32([])
        maxArea = 0
        contours,hierarchy = cv2.findContours(imgThres,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 10000:
                # cv2.drawContours(img, cnt, -1, (255,0,0),3)
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt,0.02*peri,True)
                if area > maxArea and len(approx) == 4:#
                    biggest = approx
                    maxArea = area
                    # cv2.drawContours(img, cnt, -1, (0,0,255), 20)
        # cv2.imshow('thres',img)
        # print(maxArea)
        # print(biggest)
        if len(biggest) == 0:
            return []
        # print('123')  
        biggest = self.reorder(biggest)
        return biggest


    def reorder(self,myPoints):
        myPoints = myPoints.reshape((4,2))
        myPointsNew = np.zeros((4,1,2),np.int32)

        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] = myPoints[np.argmax(add)]
        
        diff = np.diff(myPoints, axis=1)
        myPointsNew[1] = myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]

        return myPointsNew

    def getWrap(self,img,biggest):
        if len(biggest) == 0:
            return img
        pts1 = np.float32(biggest)
        pts2 = np.float32([[0,0],[widthImg,0],[0,heightImg],[widthImg,heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        imgOutput = cv2.warpPerspective(img, matrix, (widthImg,heightImg))

        imgCropped = imgOutput[5:imgOutput.shape[0]-5,5:imgOutput.shape[1]-5]
        imgCropped = cv2.resize(imgCropped,(widthImg,heightImg))

        return imgCropped
        # return img

    def scanScreen(self, img):
        # imgThres = self.prePocessing(img)
        biggest = self.getContours(img)
        imgWarped = self.getWrap(img, biggest)
        return imgWarped