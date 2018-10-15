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
    return str(message) + " handled!"

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
    def __init__(self, addr, id='Bob', position='CENTER', type='TOF', maxMessages=-2):
        print("INIT")
        self.test = True if addr == "ws://echo.websocket.org/" else False
        self.id = id
        self.addr = addr
        self.type = type
        # could have raw data and socket specific data.
        self.data = None
        self.position = position if type == 'TOF' else 'SELF'
        self.distance = 8080
        self.messageCount = 0
        # default behavior
        if maxMessages == -2:
            self.totalMessages = 20 if self.type == 'TOF' else 50
        else:
            if maxMessages > 0:
                self.totalMessages = maxMessages
            else:
                # should have an error.
                # or, don't have a max messages.
                self.totalMessages = 30 # just for now because don't want errors or anything.
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

    def getData(self):
        return handleMessageMap[self.position](self.data)

    def onMessage(self, message):
        if self.test:
            print(f"{self.id}::MESSAGE: {message}")

        self.data = json.loads(message)
        self.messageCount += 1

        if self.messageCount >= self.totalMessages:
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

            messObj = json.loads(message)
            if self.messageCount >= 1:
                if self.type == 'TOF':
                    self.distance = messObj['message']['distanceInMeters']
                elif self.type == 'SELF':
                    # print(self.data)
                    # print("KEYS:")
                    print(self.data['eventName'])
                    # print(list(self.data.keys))  # this line called an error. Think need to iterate it or something.
                    gridCell = self.data['message']['occupancyGridCell']
                    orientation = self.data['message']['orientation']
                    position = self.data['message']['position']
                    slamStatus = self.data['message']['slamStatus']
                    acceleration = self.data['message']['acceleration']
                    currentGoal = self.data['message']['currentGoal']
                    print(f"\tGrid Cell: {gridCell}\n\tOrientation: {orientation}\n\tPosition: {position}\n\tSlam Status: {slamStatus}")
                    print(f"\tAcceleration: {acceleration}\n\tCurrentGoal: {currentGoal}")

        print(f"Message Number {self.messageCount}")
        # print(f"DATA:: {self.data}")
        if self.type == 'TOF':
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
This was initial socket testing. It works so I am keeping it an not changing it to use as a baseline test.
If this doesn't work then should probably restart Misty.
It just subscribes to the CENTER time of flight sensor.
And will print out num_messages messages. Also has functionality to drive until something too close then turn.
'''
NUM_MESSAGES = 10 #200

import time


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


