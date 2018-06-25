# EyeOT

A Secuity Camera on a doorlock which can be operated using messenger.


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






# Further updates to be expected




