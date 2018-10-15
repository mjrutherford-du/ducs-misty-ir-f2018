import websocket  # this is pip install websocket-client !! not regular websocket
import time
import _thread as thread  # for python 3.4+
import threading
import json

'''
Generally socket utility.
Ideally use the MySocket class, that should work the best and allow for the creation of multiple sockets.
The testSockets() function is simply a test that I know works so that can be used to verify if the sockets are working.

@updated: 9/25/18
@created date: 9/25/18
@author: David Cowie
'''

IPADDRESS = "192.168.1.5" #"172.20.10.4"

subscriptionMessages = {
    'CENTER': {
        "$id": "1",
        "Operation": "subscribe",
        "Type": "TimeOfFlight",
        "DebounceMs": 50,  # 100
        "EventName": "TimeOfFlight1",  # Center
        "Message": "",
        "ReturnProperty": None,
        "EventConditions": [{
            "Property": "SensorPosition",
            "Inequality": "=",
            "Value": "Center"
        }]
    },
    'RIGHT': {
        "$id": "2",
        "Operation": "subscribe",
        "Type": "TimeOfFlight",
        "DebounceMs": 50,  # 100
        "EventName": "TimeOfFlightRight",  # Center
        "Message": "",
        "ReturnProperty": None,
        "EventConditions": [{
            "Property": "SensorPosition",
            "Inequality": "=",
            "Value": "Right"
        }]
    },
    'SELF': {
        "$id": "3",
        "Operation": "subscribe",
        "Type": "SelfState",
        "DebounceMs": 250,  # 100
        "EventName": "SelfStateEvent",  # Center
        "Message": "",
        "ReturnProperty": None,
        # not sure if for self, event conditions should just be null, or just each attribute is null.
        "EventConditions": None
    }
}

unsubscribeMessages = {
    'CENTER': {
        "Operation": "unsubscribe",
        "EventName": "TimeOfFlight1",  # "CenterTimeOfFlight"
        "Message": ""
    },
    'RIGHT': {
        "Operation": "unsubscribe",
        "EventName": "TimeOfFlightRight",
        "Message": ""
    },
    'SELF': {
        "Operation": "unsubscribe",
        "EventName": "SelfStateEvent",
        "Message": ""
    }
}

# these would be what data should be returned out of the data recieved from the socket.
def handleTOFSocket(message):
    # print(f"Handling message {message}")
    retData = None
    try:
        retData = message['message']['distanceInMeters']
    except Exception as e:
        # print("Error")
        return None
    return retData
    # return str(message) + " handled!"

def handleTOFSocket2(message):
    # print(f"Handling message {message}")
    return str(message) + " handled2!"

def handleSelfSocket(data):
    # so could tune this, to be specific.
    # cause could still get the whole self.data object, but this can be easier for certain things
    # like world position.
    # print("============ HANDLING STUFFF ==================")
    # print(data)
    # if data is not None:
    #     print(data['message'])

        # print(data['message']['occupancyGridCell'])
    retData = None
    try:
        retData = data['message']['occupancyGridCell']
    except Exception as e:
        print("ERROR")
        return None
    return retData

handleMessageMap = {
    'CENTER': handleTOFSocket,
    'RIGHT': handleTOFSocket2,
    'SELF': handleSelfSocket
}

'''
A socket class to interact and get real time data from the sensors onboard Misty.
Currently only works with the Time of Flight sensors, but easily changed based on the subscribe message.
And just how the data is handled.
The position attribute decides which TOF sensor to connect to. Currently only Right and Center are supported by this class.
But again, that is very simple to just add in the subscription messages.

The id I used was for testing to see both print out, not really neccessary but decided not to take it out.

Could use a map to map the TYPE to a function that takes the message and returns the desirable data.
As an alternative to using the class

USAGE would be like make a socket, or an array of sockets and then would like loop over them printing out data.
But also, if handle directly in the socket, that would be interesting cause get the immediate response
But also, can't do actions based on multiple socket readings...
except maybe for somethingg specific like the computer vision one or something.
    Or could have the mysocket be a parent class and could have specific sockets inherit from there.
'''
class MySocket:
    # position should really be like type
    # thinking could add in the option to pass in what atributes interested in, then those are what is returned from
    # the getData call, like maybe in a list, in the order of interest. then don't have to worry about using keys
    # outside of this class.
    # then actually, the getData function could be the same for every socket, it just loops over the interested
    # attribute names, and gets those data. Just depends on if prefer to have the caller know the names of the attributes or not.
    def __init__(self, addr="ws://" + IPADDRESS + "/pubsub", id='Bob', position='CENTER', type='TOF', maxMessages=-2, wantPrint=True, interestedAttributes=[]):
        print("INIT")
        self.wantPrint = wantPrint
        self.endOnMessageCount = True
        self.test = True if addr == "ws://echo.websocket.org/" else False
        self.id = id
        self.addr = addr
        self.type = type
        # could have raw data and socket specific data.
        self.data = None
        self.position = position if type == 'TOF' else 'SELF'
        self.distance = 8080
        self.messageCount = 0
        # WARNING -- Might want to make a different copy here. shouldn't be an issue, but should check.
        self.interestedAttributes = interestedAttributes
        self.unsubscribed = False
        # default behavior
        if maxMessages == -2:
            self.totalMessages = 20 if self.type == 'TOF' else 50
        else:
            if maxMessages > 0:
                self.totalMessages = maxMessages
            else:
                # should have an error.
                # or, don't have a max messages.
                self.endOnMessageCount = False
                self.totalMessages = 30  # just for now because don't want errors or anything.
        if len(interestedAttributes) == 0:
            # default behavior then.
            if type == 'TOF':
                self.interestedAttributes.append('distanceInMeters')
            else:  # for now assuming only TOF and SELF
                self.interestedAttributes.append('occupancyGridCell')

        # websocket.enableTrace(True)
        self.ws = None
        # self.ws = websocket.WebSocketApp(addr, on_message=self.onMessage, on_error=self.onError, on_close=self.onClose)
        # self.ws.on_open = self.onOpen
        # self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst = threading.Thread(target=self.instantiate)
        self.wst.start()
        # self.ws.run_forever()
        print(f"{self.id}-{position}::Running forever")

    def instantiate(self):
        print(f"{self.id} - {self.position}::INstantiate")
        self.ws = websocket.WebSocketApp(self.addr, on_message=self.onMessage, on_error=self.onError, on_close=self.onClose)
        self.ws.on_open = self.onOpen
        # self.wst = threading.Thread(target=self.ws.run_forever)
        # self.wst.daemon = True
        # self.wst.start()
        self.ws.run_forever(ping_timeout=10)

    '''
    A much more complicated implementation would be instead of having the caller, constantly call getData, which isn't
    changing as often as it is being called, could have it publish an event, which is subscribed too. (essentially, what
    the socket is doing), then the caller is notified of changes and could handle them there.
    But for out current simple purpose, this works fine.
    '''
    def getData(self):
        retData = []
        for att in self.interestedAttributes:
            try:
                retData.append(self.data['message'][att])
            except Exception as e:
                # print("Exception")
                retData.append(None)
        return retData
        # return handleMessageMap[self.position](self.data)

    # What to call when finished. So don't have to count messages in the socket class.
    def unsubscribe(self):
        # this is really unsubscribed but want to be, trying to be a protection against anything.
        self.unsubscribed = True
        self.ws.send(json.dumps(unsubscribeMessages[self.position]))
        # then normally would close.
        self.ws.close()

    def onMessage(self, message):
        if self.test:
            print(f"{self.id}::MESSAGE: {message}")

        self.data = json.loads(message)
        self.messageCount += 1

        if self.endOnMessageCount and self.messageCount >= self.totalMessages:
            # self.wst.join()
            print(f"{self.id}::Closing")
            if not self.test:
                self.ws.send(json.dumps(unsubscribeMessages[self.position]))
            self.ws.close()

        if self.test:
            self.ws.send(f"Hello again {self.id}- {self.messageCount}")
        else:
            # this is essentially the part that only works for the time of flight sensors.
            # just the return messages are different.

            # messObj = json.loads(message)
            if self.messageCount >= 1:
                if self.type == 'TOF':
                    self.distance = self.data['message']['distanceInMeters']
                elif self.type == 'SELF':
                    # this was just for printing purposes. So could just delete all of this for use
                    # then handle prining outside of class.
                    # print(self.data)
                    # print("KEYS:")
                    if self.wantPrint:
                        print(self.data['eventName'])
                    # print(list(self.data.keys))  # this line called an error. Think need to iterate it or something.
                    gridCell = self.data['message']['occupancyGridCell']
                    orientation = self.data['message']['orientation']
                    position = self.data['message']['position']
                    slamStatus = self.data['message']['slamStatus']
                    acceleration = self.data['message']['acceleration']
                    currentGoal = None  #self.data['message']['currentGoal']
                    if self.wantPrint:
                        print(f"\tGrid Cell: {gridCell}\n\tOrientation: {orientation}\n\tPosition: {position}\n\tSlam Status: {slamStatus}")
                        print(f"\tAcceleration: {acceleration}\n\tCurrentGoal: {currentGoal}")

        print(f"Message Number {self.messageCount}")
        # print(f"DATA:: {self.data}")
        if self.type == 'TOF' and self.wantPrint:
            print(f"{self.position}-Distance(m)::{self.distance}")


    def onError(self, error):
        print(f"{self.id}::On Error:: {error}")

    def onClose(self):
        print(f"{self.id}::CLOSED")

    def onOpen(self):
        print(f"{self.id} - {self.position}::On Open")
        # send a subscripbe message
        if self.test:
            self.ws.send("hello")
        else:
            print(json.dumps(subscriptionMessages[self.position]))
            self.ws.send(json.dumps(subscriptionMessages[self.position]))


'''
INFORMATION FROM THE SELF STATE MESSAGE
acceleration
batteryChargePercent
batteryVoltage
bumpedState
currentGoal
isCharging
localIPAddress
location
mentalState
occupancyGridCell
occupancyGridCellMeters
orientation
position
slamStatus
stringMessages
touchedState
'''


