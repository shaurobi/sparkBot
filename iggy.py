from itty import *
import urllib2
import json
import random

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents



@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken. i.e.
    /batman    - replies to the room with text
    /batcave   - echoes the incoming text to the room
    /batsignal - replies to the room with an image
    """
    webhook = json.loads(request.body)
    print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        if 'batman' in in_message or "whoareyou" in in_message:
            msg = "I'm Batman!"
        elif 'help' in in_message:
            msg = "**Hi!** I'm Iggy the IoT Bot. \n Ask for the **chlorine** level to see what the tanks doing. \n You can also ask **who** is on duty and **start** a Webex meeting if needed!"
        elif 'batcave' in in_message:
            message = result.get('text').split('batcave')[1].strip(" ")
            if len(message) > 0:
                msg = "The Batcave echoes, '{0}'".format(message)
            else:
                msg = "The Batcave is silent..."
        elif 'batsignal' in in_message:
            print "NANA NANA NANA NANA"
        elif 'who' in in_message:
                msg = "Current supervisor on duty is Roger Greene (roggreen@cisco.com)"
        elif 'start' in in_message:
                msg = "Click on the below link to start a webex \n http://cs.co/shaun"
        elif 'chlorine' in in_message:
                chlorine = None
                chlorine = random.randrange(0, 100)
                if chlorine > 80:
                        msg = "Alert! Chlorine is dangerously high at " +str(chlorine) + "%"
                else:
                        msg = "Chlorine currently at " + str(chlorine) + "%"
    if msg != None:
        print msg
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"

### set environment variables ###
bot_email = "iggy@sparkbot.io"
bot_name = "Iggy"
auth = open("auth.txt")
bearer = auth.read()
bearer = bearer.rstrip("\n")
run_itty(server='wsgiref', host='0.0.0.0', port=80)