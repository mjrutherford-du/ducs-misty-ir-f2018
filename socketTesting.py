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
        "EventName": "TimeOfFlightRight",  # "CenterTimeOfFlight"
        "Message": ""
    }
}


'''
A socket class to interact and get real time data from the sensors onboard Misty.
Currently only works with the Time of Flight sensors, but easily changed based on the subscribe message.
And just how the data is handled.
The position attribute decides which TOF sensor to connect to. Currently only Right and Center are supported by this class.
But again, that is very simple to just add in the subscription messages.

The id I used was for testing to see both print out, not really neccessary but decided not to take it out.
'''
class MySocket:
    def __init__(self, addr, id='Bob', position='CENTER'):
        print("INIT")
        self.test = True if addr == "ws://echo.websocket.org/" else False
        self.id = id
        self.data = None
        self.position = position
        self.distance = 8080
        self.messageCount = 0
        self.totalMessages = 20
        websocket.enableTrace(True)
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
        self.ws = websocket.WebSocketApp(addr, on_message=self.onMessage, on_error=self.onError, on_close=self.onClose)
        self.ws.on_open = self.onOpen
        # self.wst = threading.Thread(target=self.ws.run_forever)
        # self.wst.daemon = True
        # self.wst.start()
        self.ws.run_forever(ping_timeout=10)

    def onMessage(self, message):
        if self.test:
            print(f"{self.id}::MESSAGE: {message}")
        self.data = message
        if self.test:
            self.ws.send("Hello again")
        else:
            # this is essentially the part that only works for the time of flight sensors.
            # just the return messages are different.
            messObj = json.loads(message)
            if self.messageCount >= 1:
                self.distance = messObj['message']['distanceInMeters']
        self.messageCount += 1
        print(f"{self.position}-Distance(m)::{self.distance}")
        if self.messageCount >= self.totalMessages:
            # self.wst.join()
            print(f"{self.id}::Closing")
            if not self.test:
                self.ws.send(json.dumps(unsubscribeMessages[self.position]))
            self.ws.close()

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


if __name__ == "__main__":
    # testSockets()

    # changeImage()
    # exit()
    addr = "ws://echo.websocket.org/"
    addr = "ws://" + IPADDRESS + "/pubsub"
    # this should be able to listen to the Center and right TOF sensors at the same time.
    # and the readings begin as soon as the sockets are created.
    sock = MySocket(addr, id="Steve")
    sock2 = MySocket(addr, id="James", position='RIGHT')
    print("Finishedsocketing")
