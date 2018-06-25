  
#Python libraries that we need to import for our bot
import RPi.GPIO as GPIO
import random
import time
from flask import Flask, request
from pymessenger.bot import Bot
import cv2
import numpy as np
import os
 
app = Flask(__name__)
ACCESS_TOKEN = 'ACCESS_TOKEN'
VERIFY_TOKEN = 'TESTINGTOKEN'
bot = Bot(ACCESS_TOKEN)
global_recipient=1660711783998078
#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                str = message['message']['text']
                segs = str.split()
                if message['message'].get('text'):
                    if segs[0] == 'Watch':
                        watch(int(segs[1]),recipient_id)
                    elif segs[0]=='Open':
                        open(recipient_id)
##                send_message(recipient_id, 'skip')
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"
 
 
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
 
def open(recipient_id):
    GPIO.setmode(GPIO.BOARD)

    ControlPin=[7,11,13,15]

    for pin in ControlPin:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
	
    seq=[[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]
    i=0
    for i in range(650):
        for halfstep in range(8):
            for pin in range(4):
			#print(seq[halfstep][pin])
                GPIO.output(ControlPin[pin],seq[7-halfstep][pin])
            time.sleep(0.001)
##    send_message(recipient_id,'Door Opened')
    i=0
    time.sleep(5)
    halfstep = 0
    pin = 0
    for i in range(650):
        for halfstep in range(8):
            for pin in range(4):
			#print(seq[halfstep][pin])
                GPIO.output(ControlPin[pin],seq[halfstep][pin])
            time.sleep(0.001)
    send_message(recipient_id,'Door Closed')
	
    GPIO.cleanup()
    print('in open')
    
    
 
def watch(timer,recipient_id):
    timeout = time.time()+timer
    print(timer)
    font = cv2.FONT_HERSHEY_SIMPLEX
    #name holds the detected face's name
    name = ['']
    #if face recognized break from loop
    facerecognized = False
    #recognizer for face recognizing
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    #face detection
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
    
    #iniciate id counter
    id = 0

    # names related to ids: example ==> Marcelo: id=1,  etc
    names = ['None', 'William', 'Michelle']
    
    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)
    while True:
        if time.time()>timeout or facerecognized == True:
            break
        else:
            ret, img =cam.read()
            img = cv2.flip(img, -1) # Flip vertically
            
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale( 
                gray,
                scaleFactor = 1.2,
                minNeighbors = 5,
                minSize = (int(minW), int(minH)),
               )
            
            for(x,y,w,h) in faces:

                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                facerecognized = True
                # Check if confidence is less them 100 ==> "0" is perfect match 
                if (confidence < 100):
                    id = names[id]
                    name.append(str(id))
                    confidence = "  {0}%".format(round(100 - confidence))
                else:
                    id = "someone"
                    confidence = "  {0}%".format(round(100 - confidence))
                cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
                cv2.imwrite("pic.jpg", gray[y:y+h,x:x+w])
                
            cv2.imshow('image', img)
            
        time.sleep(1)
        
    cam.release()
    cv2.destroyAllWindows()
    send_message(recipient_id,' '.join(name)+" is at your door")
    print("end of watch")

 
#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


 
if __name__ == "__main__":
    app.run()
