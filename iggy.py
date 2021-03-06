from itty import *
import requests
import json
import random


def webexGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    print("getting from " + url)
    contents = requests.get(url, headers= headers)
    print("response from GET =" + str(contents.status_code))
    return contents.json()


def webexPOST(url, data):
    """
    This method is used for:
        -posting a message to the Webex space to confirm that a command was received and processed
    """
    print("sending " + str(data) + "to " + url)
    contents = requests.post(url, data = json.dumps(data), headers=headers)
    print("response from POST =" + str(contents.status_code))
    return contents.status_code


def buildmessage(in_message, webhook, person):
    """
    This method checks the message content for a specific keyword, matches the keyword to an output, and then builds the
    return message which will then be posted back into the room in which it was received
    the "webhook" variable here is the incoming webhook defined later in the code.
    :type webhook: object
    :type in_message: str
    :type person: str"""
    msg = None
    msgtype = None
    doc = None
# TODO -- add logging for incoming messages as info
    if 'batman' in in_message or 'whoareyou' in in_message:
        msg = "I'm Batman!"
        msgtype = "text"
    elif 'help' in in_message:
        msg = ("""Hi! I'm **Iggy the IoT Bot**. Here's a list of things you can do -
    Ask for the CHLORINE level to see what the tanks doing.
    You can also ask WHO is on duty and START a Webex meeting if needed.
    You can also request to view my SOURCE CODE
    I can tell you the WEATHER in a city -- Iggy weather Melbourne, as an example.
    And you can ask me to DEFINE a word for you.""")
        msgtype = "markdown"

    elif 'who' in in_message:
        msg = 'Current supervisor on duty is Roger Greene (roggreen@cisco.com)'
        msgtype = "text"

    elif 'cash me outside' in in_message:
        msg = 'HOW BOUH DAT'
        msgtype = 'text'

    elif 'test' in in_message:
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

    elif 'roomid' in in_message:
        msg1 = "Room ID for this room is " + webhook['data']['roomId']
        msg= str(msg1)
        msgtype = "text"

    elif 'members' in in_message:
        peopleCount = random.randrange(100,10000)
        msgtype = "text"
        msg = "There are currently " + str(peopleCount) + " people in the Member's Section"

    elif 'southern' in in_message:
        peopleCount = random.randrange(1000,20000)
        msgtype = "text"
        msg = "There are currently " + str(peopleCount) + " people in the Southern Stand"

    elif 'define' in in_message:
        word1 = in_message.partition('define')
        word1 = str(word1[2]).lstrip()
        msg1 = word1 + ": " + getDefinition(word1)
        msg = str(msg1)
        msgtype = "text"
    elif 'dadjoke' in in_message:
        msg = getDadJoke()
        msgtype = "text"


### once we find the keyword, match to the message type below
### if there's a doc to be attached:
    if doc != None:
        print(repr(msg))
        webexPOST("https://api.ciscospark.com/v1/messages",
                      {"roomId": webhook['data']['roomId'], msgtype: msg, "files": doc})
### else if there's no doc/file to attach, but there's still a matched message:
    elif msg != None:
        print(repr(msg))
        ### after we log the message to console, refer it to sendSparkPOST() for message creation
        webexPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], msgtype: msg,})


def getDadJoke():
    """
    Gets a random Dad joke and returns it as a string
    :return joke: string
    """
    header1 ={ "Accept":"application/json"}
    uri = "https://icanhazdadjoke.com/"
    joke = requests.get(uri, headers=header1)
    joke = joke.json()
    return str(joke['joke'])

def getWeather(city):
    """
    Gets the weather for CITY and returns the main temperature in celsius.
    :type city: string
    """
    payload = {"q": city,
               "APPID": "83fcd7c8d13fa1ebfa85e29312efa126",
               "units": "metric"}
    uri = "http://api.openweathermap.org/data/2.5/weather?"
    contents = requests.post(uri, params=payload)
    contents = contents.json()
    return contents['main']['temp']

def getDefinition(word):
    # type: word = string
    # goes out to oxford to get the definition of a word
    word = str(word)
    url = "https://od-api.oxforddictionaries.com/api/v1/entries/en/" + word + "/definitions"
    request = requests.get(url, data=None,
                              headers={'app_key': "ac9c1f927595ea9925e18e35022ee6c9",
                                       'app_id': "047a9de2",})
    result = request.json()
    definition = str(result["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0])
    definition = str(definition)
    return definition

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed and passed to buildmessage(), which then sends the message.
    No further action taken here.
    """
# TODO -- log incoming requests to warning file
    webhook = json.loads(request.body)
    result = webexGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        print(result['text'], result['personEmail'])
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        person = webhook['data']['personEmail']
        buildmessage(in_message, webhook, person)
    return "true"


### set environment variables  ###
bot_email = "iggy@sparkbot.io"
bot_name = "Iggy"
### auth.txt is a local file, in the same directory as iggy.py, containing the API key for the specific BOT.
### Script won't work without it.
auth = open("auth.txt")
bearer = auth.read()
bearer = bearer.strip("\n")
headers = {"Accept": "application/json",
           "Content-Type": "application/json",
           "Authorization": "Bearer " + bearer}

###run_itty specifies the local server and default port. The IP of your server must be specified when you set up the Webhooks.
run_itty(server='wsgiref', host='0.0.0.0', port=80)
