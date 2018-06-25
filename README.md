# EyeOT

A Secuity Camera on a doorlock which can be operated using messenger.</br>
Link to Youtube video : [NCU MIS IOT Project -EyeOT](https://youtu.be/chnJVtd9RYY)


## Ingredients
*Installations of libraries are recommended to be integrated to python3 using pip3
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

## Making the Camera

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
If everything works just fine skip to the next step. </br>If not and it gives Assertion Error, try this:
```
sudo modprobe bcm2835-v4l2
```
### Step 2-Setting up/Testingthe MessengerBot
Start a flask app in that same directory name it app.py. And put the code in it.</br>
```
#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
 
app = Flask(__name__)
ACCESS_TOKEN = 'ACCESS_TOKEN'
VERIFY_TOKEN = 'TESTING_TOKEN'
bot = Bot(ACCESS_TOKEN)
 
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
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
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
 
 
#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)
 
#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"
 
if __name__ == "__main__":
    app.run()

```
This app.py is supposed to echo whatever you typed in your messenger.</br>

Next, you have to make your bot in facebook.
Sign up for a facebook developer account, and sign in. After that, you'll see a MyApp icon in the top-right corner, click it and add a new App.</br>
You will then be prompted to what kind of product you're building, click the “Set Up” button on the Messenger option.</br>

Go to your your app’s settings page on the left-hand side and fill out the Basic Information in the Settings tab. Simply ignore the Privacy Policy thing, we're only in developer mode.</br>

At the left side of the screen click Product->Messenger->Settings->Token Generation. You will have to have a facebook page to enable this. This Access token will be put in the ACCESS_TOKEN part of the code.</br>

Then go back to your app.py run it.
```
python3 app.py
```
You should get something that looks like the following:


```
Running on http://127.0.0.1:5000/ (Press CTRL C to quit)
```
You can see that it's running on port 5000.</br>

Activate your ngrok on port 5000
```
ngrok http 5000
```
In the response, there should be something that looks like:
```
Forwarding:            https://d506a9d0.ngrok.io/ -> localhost:5000
```
Copy the url to your facebook developer page where there is an icon in the products menu which says webhook, and copy the url in it.
Check the following:</br>
messages, messaging_postbacks, message_deliveries, messaging_pre_checkouts boxes</br>

In the verify token line, type in the VERIFY_TOKEN in your code. For instance in the code above, it is TESTINGTOKEN.

For a very detailed step-by-step guide for this step, refer to [Building Facebook Messenger Bots with Python in less than 60 minutes](https://www.twilio.com/blog/2017/12/facebook-messenger-bot-python.html)

### Step 3-Making the Security Camera+Everything
This step can be divided into 3 sub-steps. As for step 1 and 2, I used the code from [Marcelo](https://github.com/Mjrovai/OpenCV-Face-Recognition) for substep 1 ane 2, which are used to train face-recognition models. I'll give a brief description of what's going on in it. If you wish for a detailed tutorial refer to the link.

#### SubStep 1-Collect Data
This step collects data(Dataset) that is to be trained later on into a .yml file.
```
while(True):

    ret, img = cam.read()
    img = cv2.flip(img, -1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif count >= 30: # Take 30 face sample and stop video
         break
```
First the camera is activated to capture a picture, and it will find the face and save the part that has the face in the dataset directory. Once it has taken 30 pictures, this program will terminate.

#### SubStep 2-Train Data
This step trains the data into a .yml file, which is the model app.py will refer to when doing facial recognition.
```
# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths:

        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

# Print the numer of faces trained and end program
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
```

The essence of this program is in recognizer.train(faces, np.array(ids)), where the model is formed by matching ids to their corresponding faces.

#### SubStep 3-Creating the Bot
This step is the final step of making EyeOT. I'll divide the code into three segments, the MessengerBot, watch() function, and open() function.

##### Segment 1-MessengerBot
I built the messenger bot part on the messenger bot we had when we're testing if the messenger bot is working.
```
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
```
The part I added is to get what message this bot has received into the code. For different messages, the bot will act responsively to the command given from the user. </br>
If the user typed in "Watch 10", it means that the user wishes the camera to be looking for people for 10 seconds, and call the watch() function.</br>
If the user typed in Open, the Pi will activate the stepmotor attached to it by calling the open() function.
```
recipient_id = message['sender']['id']
                str = message['message']['text']
                segs = str.split()
                if message['message'].get('text'):
                    if segs[0] == 'Watch':
                        watch(int(segs[1]),recipient_id)
                    elif segs[0]=='Open':
                        open(recipient_id)
```
I stripped out the part where the if statement took place.

##### Segment 2-Watch()
After being asked to watch for 10 seconds, this function will be activated, and it has a parameter(timer) that holds a number which is how long the camera will be activated.</br>

This function takes 2 parameter, one for how long this function is going to last, another is the recipient id for which the function will send a messenger message to.
```
def watch(timer,recipient_id):
```

This set the time for how long the loop for detecting faces will be executed.
```
timeout = time.time()+timer
```
The rest are facial recognition using te .yml file we built in the previous segment.</br>
<br/>
The ids we used in the first segment are referred to the names in this list. There are some other better implementation for this part, but we'll use a list for now.
```
names = ['None', 'William', 'Michelle']
```
Names of the id that's being recognized will be appended to the a list called name, and will be sent as a message back to the person who messaged this bot.
```
send_message(recipient_id,' '.join(name)+" is at your door")
```
##### Segment 2-Open()
This segement defines the function for opening the door. The doorlock is replaced with a steppermotor in this project, which means that we have to import RPi.GPIO. RPi.GPIO might not be in your CV virtual environment at this moment, but you can install it with the following:

```
pip3 install RPi.GPIO
```
With that we can move on to controlling the stepper motor.</br>
First thing we have to do is to understand how a stepper motor works and how to control it with a python script.
Refer to this [video](https://www.youtube.com/watch?v=Dc16mKFA7Fo) before moving on to working with your stepper motor.

Assuming you've fully comprehend everything in the video or understand how a stepper motor works, the following array should not be a problem for you.

```
seq=[[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]
```
This is the sequence which the circuits are to be activated.

</br>

Once the open() function is called, the axis will rotate clockwise for 90 degrees, and wait for a few seconds then rotate counter-clockwise for 90 degrees. After that's done, the Pi will send a message to the one who called it that the door has been closed to ensure that the locked has not remain unlocked.

### Activating your EyeOT
To activate this whole system, do what you did in when you were testing the bot. If everything is working you can the the Pi will be receiving and sending messages.


## Final Words
EyeOT is an easy-to-build IOT device. Though it still got some problems, and at times doesn't work as expected, I hope that in the near future, corrections can be made, and upgrades can be integrated.

# Further updates to be expected




