# EyeOT

A Secuity Camera on a doorlock which can be operated using messenger.


## Ingredients

### A Clean Pi
Installing a lot of stuff, some might not be able to be installed correctly if you don't have a clean Raspberry Pi. Installation of the latest version raspbian is mandatory. A full installation guide to installing a clean pi will be updated later on.

### Open CV
Installation of [OpenCV](https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/), refer to the link.

### PyMessenger
Assuming you've had the latest version of Raspbian, having the PYMEssenger library if you want to access your camera. 
Install this in your CV virtual environment.
```
pip3 install pymessenger==0.0.7.0
```
### Flask
Having Flask enables your MessengerBot to work, it handles the http request given from the messenger server. Again, install this in your CV virtual environment.
```
pip3 install Flask==0.12.2
```
### ngrok
It handles the http requests sent to the pi.

Installation refer to [ngrok Download](https://gist.github.com/jwebcat/ecaac7bc7ee26e01cd4a)

##Steps
### Step 1-Testing the camera
Enter your OpenCV environment
```
source ~/.profile
workon cv
```
create a new testing directory
```
mkdir test
cd test
```
Create a test.py in that directory. You can either use nano or Thonny which is a built in the Pi.
```
import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cap.set(3,640) # set Width
cap.set(4,480) # set Height
 
while(True):
    ret, frame = cap.read()
    frame = cv2.flip(frame, -1) # Flip camera vertically
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    cv2.imshow('frame', frame)
    cv2.imshow('gray', gray)
    
    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()
```
