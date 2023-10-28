import cv2
import mediapipe as mp
import math
import serial
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time

#Lấy các điểm mốc trên tay
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
#chay/dung chuong trinh
batdau = 0
hientai = 0
timecho = 1000
timecho2 = 200
#khởi tạo biến
quay = 0
cx = 0
cy = 0
theta1 = 0
theta2 = 0
h = 0
alpha = 0
phi = 0
phi1 = 0
phi2 = 0
#bien arc
radius = 500
startAngle = 180
endAngle = 225
thickness = 2
center = (840, 550)
angle = 0
axes = (radius, radius)
color = (0, 0, 255)
#bien canh tay robot
toadox = 0
toadoy = 0
toadox1 = 0
toadoy1 = 0
toadox2 = 0
toadoy2 = 0
gioihanx = 0
testx = 0
testy = 0
#Grab/open
grab = 0
xgrab = 0
ygrab = 0
x3 = 0
y3 = 0
#xoay
xoay = 0
xgiua = 0
ygiua = 0
xut = 0
yut = 0
xmocgiua = 0
ymocgiua = 0
xmocut = 0
ymocut = 0
# trai = 1, phai = 2, dung yen = 0
#bien serial
truyen = 0
goc1 = ""
goc2 = ""
serialSend = ""
serialData = serial.Serial('COM7', 9600)
#khởi tạo webcam 
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
  success, image = cap.read()
  hands = detector.findHands(image, draw = False)
  if hands:
    lmList = hands[0]['lmList']
    cx, cy = lmList[8][:2]
    xgrab, ygrab = lmList[4][:2]
    x3, y3 = lmList[3][:2]
    xgiua, ygiua = lmList[12][:2]
    xut, yut = lmList[20][:2]
    xmocgiua, ymocgiua = lmList[9][:2]
    xmocut, ymocut = lmList[17][:2]
    
    if cy > 550:
      cy = 550
    elif cy < 196:
      cy = 196
    else:
      cy = cy
#Gioi han x
    gioihanx = int(840 - math.sqrt(radius**2 - (550 - cy)**2))
    if cx < gioihanx:
      cx = gioihanx
    elif cx > 690:
      cx = 690
    else:
      cx = cx
#Điểm điều khiển
    image=cv2.circle(image,(cx,cy),1,(255,0,0),5)
    if xgrab < x3:
      grab = 1
    else:
      grab = 0
#xoay
    if ygiua < ymocgiua and yut > ymocut:
      xoay = 1
    elif ygiua > ymocgiua and yut < ymocut:
      xoay = 2
    else:
      xoay = 0
  else:
    xoay = 0
    cx = 600
    cy = 500
    grab = 0
 

#Động học nghịch
  toadox = 840 - cx
  toadoy = 550 - cy
  h = toadox**2 + toadoy**2
  theta2 = int(math.degrees(np.arccos((h - 260**2 - 260**2)/(2*260*260))))
  alpha = math.degrees(np.arctan(toadoy/toadox))
  phi1 = math.sin(math.radians(theta2))*250
  phi2 = 250 + math.cos(math.radians(theta2))*250
  phi = math.degrees(np.arctan(phi1/phi2))
  theta1 = int(alpha + phi)
# serial
  goc1 = str(theta1)
  if len(goc1)==1:
    goc1 = "00"+goc1
  elif len(goc1)==2:
    goc1 = "0"+goc1
  else:
    goc1 = goc1
  goc2 = str(theta2)
  if len(goc2)==1:
    goc2 = "00"+goc2
  elif len(goc2)==2:
    goc2 = "0"+goc2
  else:
    goc2 = goc2
  serialSend = str(grab) + str(goc1) + str(goc2) + str(xoay) + '\n'


  #print(serialSend)
  #serialData.write(serialSend.encode())
  if batdau == 1:
    millis = int(round(time.time() * 1000))
    if xoay == 0:
      if truyen == 1 and millis - hientai > timecho2:
        serialData.write(serialSend.encode())
        hientai = millis
        print("lmao")
        print(serialSend)
        truyen = 0
      if millis - hientai > timecho:
        serialData.write(serialSend.encode())
        hientai = millis
        print(serialSend)
    else:
      if millis - hientai > timecho2:
        serialData.write(serialSend.encode())
        hientai = millis
        print(serialSend)
        truyen = 1
#ve tay robot
  toadoy1 = 550 - int(math.sin(math.radians(theta1))*250)
  toadox1 = 840 - int(math.cos(math.radians(theta1))*250)
  image=cv2.line(image, (840, 550), (toadox1, toadoy1),(255,0,0),10)
  toadoy2 = cy
  toadox2 = cx
  image=cv2.line(image, (toadox1, toadoy1), (toadox2, toadoy2),(0,255,0),10)
  image=cv2.line(image, (toadox2, toadoy2), (toadox2 - 50, toadoy2), (0,0,255),10)
#Giới hạn vùng điều khiển
  image=cv2.ellipse(image, center, axes, angle, startAngle, endAngle, color, thickness)
  image=cv2.line(image, (690, 196), (690, 550), (0,0,255),2)
  image=cv2.line(image, (690, 550), (340, 550), (0,0,255),2)
  image=cv2.line(image, (690, 196), (487, 196), (0,0,255),2)
  
#Đảo ngược và hiển thị ảnh
  cv2.imshow('Cua so dieu khien',cv2.flip(image,1))
  k = cv2.waitKey(10)
  if k == 27:
    break
    cap.release()
    cv2.destroyAllWindows()
  elif k == ord('b'):# bam b de bat dau
    batdau = 1
    print('Bat dau dieu khien')
  elif k == ord('d'):# bam d de dung
    batdau = 0
    print('Tam dung')

    

