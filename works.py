#This is the simple one
import datetime
import math
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils

#global variables
width = 0
height = 0
EntranceCounter = 0
ExitCounter = 0
MinCountourArea = 5000  #Adjust ths value according to your usage
BinarizationThreshold = 80  #Adjust ths value according to your usage
OffsetRefLines = 75  #Adjust ths value according to your usage

#Check if an object in entering in monitored zone
def CheckEntranceLineCrossing(y, CoorYEntranceLine, CoorYExitLine):
  AbsDistance = abs(y - CoorYEntranceLine)	
  if ((AbsDistance <= 2) and (y < CoorYExitLine)):
		return 1
  else:
		return 0

#Check if an object in exitting from monitored zone
def CheckExitLineCrossing(y, CoorYEntranceLine, CoorYExitLine):
    AbsDistance = abs(y - CoorYExitLine)	
    if ((AbsDistance <= 2) and (y > CoorYEntranceLine)):
		return 1
    else:
		return 0

#camera = cv2.VideoCapture(0)
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
W = 640
H = 480
##force 640x480 webcam resolution
#camera.set(3,640)
#camera.set(4,480)
# grab an image from the camera
ReferenceFrame = None

# initialize the camera and grab a reference to the raw camera capture

 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
    image = frame.array
    vs = frame.array
#    height = np.size(vs,0)
#    width = np.size(vs,1)
    GrayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    GrayFrame = cv2.GaussianBlur(GrayFrame, (21, 21), 0)
    
    if ReferenceFrame is None:
        ReferenceFrame = GrayFrame
        #continue

    #Background subtraction and image binarization
    FrameDelta = cv2.absdiff(ReferenceFrame, GrayFrame)
    FrameThresh = cv2.threshold(FrameDelta, BinarizationThreshold, 255, cv2.THRESH_BINARY)[1]
    
#    #Background subtraction and image binarization
#    FrameDelta = cv2.absdiff(ReferenceFrame, GrayFrame)
#    FrameThresh = cv2.threshold(FrameDelta, BinarizationThreshold, 255, cv2.THRESH_BINARY)[1]
    FrameThresh = cv2.dilate(FrameThresh, None, iterations=3)
    #cnts = cv2.findContours(FrameThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    major = cv2.__version__.split('.')[0]
    if major == '3':
		_, contours, _ = cv2.findContours(FrameThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
		contours, _ = cv2.findContours(FrameThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#
    QttyOfContours = 0
#
#    #plot reference lines (entrance and exit lines) 
    CoorYEntranceLine = 220#(height / 2)-OffsetRefLines
    CoorYExitLine = 520#(height / 2)+OffsetRefLines
    cv2.line(image, (320, 0), (320, H), (0,0,255), 5)#blue entrance
    cv2.line(image, (420, 0), (420, H), (255,0,0), 5)#red exit

 #   cv2.line(image, (0,CoorYEntranceLine), (width,CoorYEntranceLine), (255, 0, 0), 2)
 #   cv2.line(image, (0,CoorYExitLine), (width,CoorYExitLine), (0, 0, 255), 2)
    for c in contours:
        #if a contour has small area, it'll be ignored
        if cv2.contourArea(c) < MinCountourArea:
            continue
        QttyOfContours = QttyOfContours+1    

        #draw an rectangle "around" the object
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        #find object's centroid
        CoordXCentroid = (x+x+w)/2
        CoordYCentroid = (y+y+h)/2
        ObjectCentroid = (CoordXCentroid,CoordYCentroid)
        print ObjectCentroid
        cv2.circle(image, ObjectCentroid, 1, (0, 0, 0), 5)
#        if CoordXCentroid > 220: 
#            ExitCounter += 1

        if (CheckEntranceLineCrossing(CoordXCentroid,320,420)):
            EntranceCounter += 1
        if (CheckEntranceLineCrossing(CoordXCentroid,420,320)):  
            ExitCounter += 1

        print "Total countours found: "+str(QttyOfContours)
    #
#    #Write entrance and exit counter values on frame and shows it
    cv2.putText(image, "Entrances: {}".format(str(EntranceCounter)), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 0, 1), 2)
    cv2.putText(image, "Exits: {}".format(str(ExitCounter)), (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
#    cv2.imshow("Original Frame", frame)
    
    
	# show the frame
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
 	# clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # grab the raw NumPy array representing the image
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        camera.close()
        cv2.destroyAllWindows()
        break
   

    #Dilate image and find all the contours

#
#    cv2.waitKey(1);


# cleanup the camera and close any open windows
#camera.close()
#cv2.destroyAllWindows()