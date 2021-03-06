import websocket  # this is pip install websocket-client !! not regular websocket
import time
import _thread as thread  # for python 3.4+
import threading
import json
from helpers import *

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
    return data['message']['gridCell']

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
def testSockets():
    # sock = socket()
    print("[INFO] Testing Sockets")
    subscribeMessage = {
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
    }
    subscribeMessage_RIGHT = {
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
    }

    unsubscribeMessage = {
        "Operation": "unsubscribe",
        "EventName": "TimeOfFlight1",  # "CenterTimeOfFlight"
        "Message": ""
    }
    unsubscribeMessage_RIGHT = {
        "Operation": "unsubscribe",
        "EventName": "TimeOfFlightRight",  # "CenterTimeOfFlight"
        "Message": ""
    }
    messsageCheck = {
        "count": 0,
        "stopped": 0
    }
    timeOfFlightDistances = {
        'center': 7070,
        'right': 7070
    }

    # so here would set a data variable to store the message. so can access elsewhere.
    messageCount = 0

    def onClose(ws):
        print("Closed")
        # misty
        # ws.send(str(unsubscribeMessage))
        # ws.send(json.dumps(unsubscribeMessage))
        # ws.close()

    def onMessage(ws, message):
        print("ON MESSAGE")
        # print(message)
        # print(messsageCheck)
        messsageCheck["count"] += 1
        messObj = json.loads(message)
        # print(messObj)
        distance = 70
        if messsageCheck["count"] >= 2:
            distance = messObj['message']['distanceInMeters']
        print(f"Distance(m):: {distance}")
        if distance < 0.25 and messsageCheck['stopped'] != 1:
        # if distance < 0.25:
            drive(speed=0, angularvelocity=0, time=1000)  # just a stop
            # drive(speed=20, angularvelocity=-100, time=700)
            drive(speed=20, angularvelocity=-100, time=-1)
            messsageCheck['stopped'] = 1
        if distance >= 0.25 and messsageCheck['stopped'] != 0:
            # drive(speed=0, angularvelocity=0, time=1000)  # just a stop
            drive(time=-1)
            messsageCheck['stopped'] = 0


        # messageCount += 1
        # print(message)
        # messageCount = 10
        # print("Message Read")
        # changeImage("pink_sunset.jpg")
        if messsageCheck["count"] >= NUM_MESSAGES:
            print("Shutting Down.")
            # want to close the web socket, which with misty would involve first sending an unsubscribe.
            # ws.close()
            ws.send(json.dumps(unsubscribeMessage))
            ws.close()

    def onError(ws, error):
        print("ERROR")
        print(error)
        print("Finished reporting error.")

    # this is typical. so here would just send a subscribe message.
    def onOpen(ws):
        print("ON OPEN")
        def run(*args):
            print("RUN")
            print(json.dumps(subscribeMessage))
            # print(json.load(subscribeMessage))
            ws.send(json.dumps(unsubscribeMessage))
            print("Now subscribing")
            ws.send(json.dumps(subscribeMessage))
            drive(time=-1)
            # ws.send("\"" + str(subscribeMessage) + "\"")

        thread.start_new_thread(run, ())

    websocket.enableTrace(True)
    # "ws://" IPADDRESS + "/pubsub"
    addr = "ws://" + IPADDRESS + "/pubsub"
    # addr = "ws://echo.websocket.org/"
    webSock = websocket.WebSocketApp(addr, on_message=onMessage, on_error=onError, on_close=onClose)
    webSock.on_open = onOpen
    # can have a pingTimeout=10
    webSock.run_forever(ping_timeout=10)

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
def testSelfSocket():
    addr = "ws://" + IPADDRESS + "/pubsub"
    sock = MySocket(addr, id="Bill", type="SELF")

def testTOFSockets():
    # addr = "ws://echo.websocket.org/"
    addr = "ws://" + IPADDRESS + "/pubsub"
    # this should be able to listen to the Center and right TOF sensors at the same time.
    # and the readings begin as soon as the sockets are created.
    sock = MySocket(addr, id="Steve")
    sock2 = MySocket(addr, id="James", position='RIGHT')
    # so if do it this way, the data will catch up, but not for a while
    sock1Data = 0
    sock2Data = 0
    noChangeCount = 0
    # for i in range(5000):
    # could just make this a while true
    # this gets updates pretty quick
    # issue is sometimes it does miss some updates to the sockets. but with misty it should be slow enough
    while True:
        # print("Stuff")
        # sock1Data = sock.getData()
        # print(f"1sock data:: {sock1Data}")
        if sock.getData() != sock1Data:
            sock1Data = sock.getData()
            print(f"1sock data:: {sock1Data}")
            noChangeCount = 0
        if sock2.getData() != sock2Data:
            sock2Data = sock2.getData()
            print(f"2sock data::{sock2Data}")
            noChangeCount = 0
        noChangeCount += 1
        if noChangeCount >= 30:
            break
        # with 0.1 it was missing every other message
        # also want to check if this sleeps this thread or everything, but if it was everything, would have thought that
        # it would when it was 0.1, have skipped the output in the socket class also.
        time.sleep(0.02)
    print("Finishedsocketing")

if __name__ == "__main__":
    # testSockets()
    # exit()
    # changeImage()
    # exit()
    # testTOFSockets()
    testSelfSocket()
    exit()

