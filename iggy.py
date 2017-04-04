from itty import *
import urllib2
import json
import random
import urllib

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


def buildmessage(in_message, webhook, person):
    msg = None
    msgtype = None
    doc = None
    if 'batman' in in_message or 'whoareyou' in in_message:
        msg = 'I\'m Batman!'
    elif 'help' in in_message:
        msg = ("""Hi! I'm **Iggy the IoT Bot**.
    Here's a list of things you can do -
    Ask for the **chlorine** level to see what the tanks doing.
    You can also ask **who** is on duty and **start** a Webex meeting if needed.
    You can also request to view my **source code**""")
        msgtype = "markdown"

    elif 'who' in in_message:
        msg = 'Current supervisor on duty is Roger Greene (roggreen@cisco.com)'
        msgtype = "text"

    elif 'cash me outside' in in_message:
        msg = 'HOW BOUH DAT'
        msgtype = 'text'

    elif 'test' in in_message:
        print person
        msg = 'Message received loud and clear! thanks <@personEmail:' + person + '>'
        msgtype = "markdown"

    elif 'start' in in_message:
        msg = 'Click on the below link to start a Webex! \r\n http://cs.co/shaun'
        msgtype = 'markdown'

    elif 'source code' in in_message:
        msg = """You can view my source code at this link:
       https://github.com/shaurobi/sparkBot/tree/master"""
        msgtype = "text"

    elif 'chlorine' in in_message:
        chlorine = None
        chlorine = random.randrange(0, 100)
        msgtype = "text"
        if chlorine > 80:
            msg = "Alert! Chlorine is dangerously high at " + str(chlorine) + "%"
        else:
            msg = "Chlorine currently at " + str(chlorine) + "%"

    elif 'beer' in in_message:
        msg = "beer"
        doc = "http://employees.org/~shaurobi/beer1.jpg"

    elif 'weather' in in_message:
        city = in_message.partition('weather')
        city = str(city[2])
        msg1 = "Weather in " + city + " is currently " + str(getWeather(city)) + "degrees Celsius"
        msg = str(msg1)
        msgtype = "text"

    elif 'define' in in_message:
        word = in_message.partition('define')
        word = str(word[2])
        msg1 = word + ": " + getDefinition(word)
        msg = str(msg1)
        msgtype = "text"

    if doc != None:
        print repr(msg)
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], msgtype: msg, "files" : doc})
    elif msg != None:
        print repr(msg)
        print "Standard message"
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], msgtype: msg,})

def getWeather(city):
    """

    :type city: string
    """
    payload = {"q": city,
               "APPID": "83fcd7c8d13fa1ebfa85e29312efa126",
               "units": "metric"}
    params = urllib.urlencode(payload)
    request = "http://api.openweathermap.org/data/2.5/weather?" + params
    request = urllib2.Request(request)
    contents = urllib2.urlopen(request).read()
    contents = json.loads(contents)
    return contents['main']['temp']

def getDefinition(word):
    # type: (object) -> object
    #goes out to oxford to get the definition of a word
    url = "https://od-api.oxforddictionaries.com/api/v1/entries/en/" + word +"/definitions"
    request = urllib2.Request(url, data=None,
                              headers = {'app_key': "ac9c1f927595ea9925e18e35022ee6c9",
                                        'app_id': "047a9de2",})
    result = urllib2.urlopen(request).read()
    result = json.loads(result)
    definition = result["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
    return str(definition)

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken. i.e.
    /who - tells you who is on duty
    /start - drops webex details into the meeting
    """
    print request
    webhook = json.loads(request.body)
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        person = webhook['data']['personEmail']
        print in_message, person
        buildmessage(in_message, webhook, person)
    return "true"


### set environment variables  ###
bot_email = "iggy@sparkbot.io"
bot_name = "Iggy"
auth = open("auth.txt")
bearer = auth.read()
bearer = bearer.strip("\n")
run_itty(server='wsgiref', host='0.0.0.0', port=80)