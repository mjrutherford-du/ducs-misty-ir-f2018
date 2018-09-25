import requests
import threading
import cv2  # This is what i was using for some image processing.
# I will try to clean up and put things in appropriate files.
import numpy as np
import json


'''
This is ugly initial tests.
It does include a basic sequence of actions using the RESTful API.
'''

IPADDRESS = "192.168.1.5" #"172.20.10.4"

def imageStuff(vals=[15,14,16], headings=["Connection", "Battery Level", "IP Address"]):
    WIDTH = 10  # 300
    HEIGHt = 10  # 300
    img = np.zeros((HEIGHt, WIDTH, 3), np.uint8)
    img = cv2.putText(img, "Device Info", (70, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # returned a list, of an object, with attribute 'result', which maps to a dictionary, with a bunch of keys.
    # headings = ["Connection", "Battery Level", "IP Address"]
    # vals = [15, 14, 16]
    for i, (title, val) in enumerate(zip(headings, vals)):
        img = cv2.putText(img, title + ":  " + str(val), (30, 50 + 20 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    # cv2.imshow("img", img)
    # cv2.waitKey(0)

    d = bytearray(img)
    # print(d)
    d = bytes(img)
    # print(d)

    print(img)
    flimg = img.flatten()
    print(flimg)
    sflimg = "".join(str(x) + "," for x in (img.flatten())[:-1])
    sflimg += str(flimg[-1])
    # print(sflimg)
    print(len(sflimg))
    return img


# could include the get to get all audio, then put that into a list and just start playing from there.
def playAudio(fileName):
    print("[INFO] Playing Audio: {}".format(fileName))
    url = "http://{}/api/audio/play".format(IPADDRESS)

    # payload = "{\n\t\"FileName\": \"002-Ahhh.wav\",\n\t\"Volume\": 100\n}"
    payload = "{" + "\n\t\"FileName\": \"{}\",\n\t\"Volume\": 100\n".format(fileName) + "}"
    # payload = "{" + payload + "}"
    # payload = "{\n\t\"FileName\": \"" + fileName + "\",\n\t\"Volume\": 100\n}"
    print("[INFO] Audio PayLoad: {}".format(payload))
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def changeImage(fileName="pink_sunset.jpg", timeout=5, alpha=0.5):
    url = f"http://{IPADDRESS}/api/images/change"

    # payload = "{\n\t\"FileName\": \"pink_sunset.jpg\",\n\t\"TimeOutSeconds\": 5,\n\t\"Alpha\": 0.5\n}"
    payload = "{" + f"\n\t\"FileName\": \"{fileName}\",\n\t\"TimeOutSeconds\": {timeout},\n\t\"Alpha\": {alpha}\n" + "}"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

# time as -1 if want to drive without a time limit.
def drive(speed=20, angularvelocity=0, time=1000):
    # drive straight 5 seconds

    url = f"http://{IPADDRESS}/api/drive/time"
    if time == -1:
        print("Driving forever")
        url = f"http://{IPADDRESS}/api/drive"
        initPayload = "\n\t\"LinearVelocity\": {},\n\t\"AngularVelocity\": {}\n".format(speed,angularvelocity)
    else:
        initPayload = "\n\t\"LinearVelocity\": {},\n\t\"AngularVelocity\": {},\n\t\"TimeMS\": {}\n".format(speed, angularvelocity, time)
    print(f"Driving: \n{initPayload}")
    initPayload = "{" + initPayload + "}"
    payload = initPayload
    # payload = "{\n\t\"LinearVelocity\": 20,\n\t\"AngularVelocity\": 0,\n\t\"TimeMS\": 5000\n}"
    # print(payload)
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def getDeviceInfo():
    url = "http://{}/api/info/device".format(IPADDRESS)

    response = requests.request("GET", url)
    # returned a list, of an object, with attribute 'result', which maps to a dictionary, with a bunch of keys.
    # so might convert the string to a json object..
    # but would have to test how it works.
    print(response.text)
    return response.text

# szys send a byte array, but think it just wants comma separated values as a list essentially.
# and as ints
def sendImageToMisty(image, fileName):
    url = "http://{}/api/images"
    # convert to byte array.
    # data = str(bytearray(image))
    flattenedImage = image.flatten()
    sflimg = "".join(str(x) + "," for x in flattenedImage[:-1])
    sflimg += str(flattenedImage[-1])
    data = sflimg
    width = 10
    height = 10
    print(sflimg)
    bimg = bytearray(image)
    sflimg = ""
    for i in range(len(bimg)):
        # print(bimg[i])
        sflimg += str(bimg[i]) + ","
    sflimg = sflimg[:-1]
    print(sflimg)
    # print(sflimg)
    # sflimg = str(image)
    # print(sflimg)
    payload = {
        "FileName": fileName,
        "DataAsByteArrayString": sflimg,
        "Width": width,
        "Height": height,
        "ImmediatelyApply": True,
        "OverwriteExisting": True
    }
    payload = json.dumps(payload)
    print(payload)
    # payload = "\n\t\"FileName\": {},\n\t\"DataAsByteArrayString\": \"{}\",\n\t\"Width\": {},\n\t\"Height\": {},\n\t\"ImmediatelyApply\": {},\n\t\"OverwriteExisting\": {}".format(fileName, data, width, height, "true", True)
    # payload = "{" + payload + "}"
    headers = {
        'Content-Type': "application/json"
    }
    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

def basicSequence():
    print("[INFO] Starting Basic Sequence")
    info = getDeviceInfo()
    print(info)
    print(type(info))
    info = json.loads(info)[0]
    print(info)
    print(type(info))
    info = info['result']
    currProfName = info['currentProfileName']
    battPercentage = info['batteryLevel']['batteryChargePercent']
    ip = info['ipAddress']
    print(ip)
    # img = imageStuff([currProfName, battPercentage, ip])
    playAudio("032-Bewbewbeeew.wav")
    # sendImageToMisty(img, "deviceInfo.jpg")

    print("About to change image to pink sunset.")
    # playAudio("032-Bewbewbeeew.wav")
    changeImage("pink_sunset.jpg")
    drive()
    playAudio("002-Growl-01.wav")
    drive(speed=20, angularvelocity=100, time=2000)  # this actually turns in place pretty well, turns 90 degrees to the right on the table but turns to the left.
    playAudio("006-EhMeEhmeUh.wav")
    drive(speed=20, angularvelocity=-100, time=700)
    playAudio("001-OooOooo.wav")

    drive(speed=0, angularvelocity=0, time=1000)  # just a stop


# basicSequence()
# exit()
#### Also, could call to get the device info, then write that to an image, and send it to misty to seee the info on screen.
# so get device info, then write on image, then send that image.

def createDeviceInfoImage():
    deviceInfo = getDeviceInfo()


#### TODO::: SET UP SOCKETS TO LISTEN TO RESPONCES!!!

import websocket
import time
import _thread as thread  # for python 3.4+

# def testSockets():
#     sock = socket()
class socket:
    def __init__(self):
        print("[INFO] Testing Sockets")
        self.subscribeMessage = {
            "Operation": "subscribe",
            "Type": "TimeOfFlight",
            "DebounceMs": 100,
            "EventName": "CenterTimeOfFlight",
            "Message": "",
            "ReturnProperty": None,
            "EventConditions": {
                "Property": "SensorPosition",
                "Inequality": "=",
                "Value": "Center"
            }
        }

        self.unsubscribeMessage = {
            "Operation": "unsubscribe",
            "EventName": "CenterTimeOfFlight",
            "Message": ""
        }


        # so here would set a data variable to store the message. so can access elsewhere.
        self.messageCount = 0
        websocket.enableTrace(True)
        # "ws://" IPADDRESS + "/pubsub"
        self.addr = "ws://" + IPADDRESS + "/pubsub"
        # addr = "ws://echo.websocket.org/"
        self.webSock = websocket.WebSocketApp(self.addr, on_message=self.onMessage, on_error=self.onError, on_close=self.onClose)
        self.webSock.on_open = self.onOpen
        # can have a pingTimeout=10
        self.webSock.run_forever(ping_timeout=10)

    def onMessage(self, ws, message):
        self.messageCount += 1
        print(message)
        if self.messageCount >= 10:
            # want to close the web socket, which with misty would involve first sending an unsubscribe.
            ws.close()
            # onClose(ws)

    def onError(self, ws, error):
        print("ERROR")
        print(error)

    # should send a unsubscribe message.
    def onClose(self, ws):
        print("Closed")
        # misty
        ws.send(str(self.unsubscribeMessage))

    def run(self, *args):
        self.ws.send(str(self.subscribeMessage))
    # this is typical. so here would just send a subscribe message.
    def onOpen(self, ws):
        print("ON OPEN")
        # def run(*args):
        #     # misty
        #     self.ws.send(str(self.subscribeMessage))
        #
        #     # test
        #     # for i in range(3):
        #     #     time.sleep(1)
        #     #     ws.send("Hello {}".format(i))
        #     # # i = 0
        #     # # while True:
        #     # #     time.sleep(1)
        #     # #     i += 1
        #     # #     ws.send("Hello {}".format(i))
        #     # time.sleep(1)
        #     # ws.close()
        #     # print("Thread terminated")

        # thread.start_new_thread(run, ())
        thread.start_new_thread(self.run, ())


    # websocket.enableTrace(True)
    # # "ws://" IPADDRESS + "/pubsub"
    # addr = "ws://" + IPADDRESS + "/pubsub"
    # # addr = "ws://echo.websocket.org/"
    # webSock = websocket.WebSocketApp(addr, on_message=onMessage, on_error=onError, on_close=onClose)
    # webSock.on_open = onOpen
    # # can have a pingTimeout=10
    # webSock.run_forever()


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
            # onClose(ws)

    def onError(ws, error):
        print("ERROR")
        print(error)
        print("Finished reporting error.")

    # should send a unsubscribe message.

    # this is typical. so here would just send a subscribe message.
    def onOpen(ws):
        print("ON OPEN")
        def run(*args):
            # misty
            print("RUN")
            # print("\"" + str(subscribeMessage) + "\"")
            print(json.dumps(subscribeMessage))
            # print(json.load(subscribeMessage))

            ws.send(json.dumps(unsubscribeMessage))
            print("Now subscribing")
            ws.send(json.dumps(subscribeMessage))
            # playAudio("002-Growl-01.wav")
            drive(time=-1)
            # ws.send("\"" + str(subscribeMessage) + "\"")

            # test
            # for i in range(3):
            #     time.sleep(1)
            #     ws.send("Hello {}".format(i))
            # # i = 0
            # # while True:
            # #     time.sleep(1)
            # #     i += 1
            # #     ws.send("Hello {}".format(i))
            # time.sleep(1)
            # ws.close()
            # print("Thread terminated")

        thread.start_new_thread(run, ())
        # thread.start_new_thread(run, ())

    websocket.enableTrace(True)
    # "ws://" IPADDRESS + "/pubsub"
    addr = "ws://" + IPADDRESS + "/pubsub"
    # addr = "ws://echo.websocket.org/"
    webSock = websocket.WebSocketApp(addr, on_message=onMessage, on_error=onError, on_close=onClose)
    webSock.on_open = onOpen
    # can have a pingTimeout=10
    webSock.run_forever(ping_timeout=10)

# playAudio("002-Growl-01.wav")
# drive(time=-1)
# testSockets()
# drive(speed=0, angularvelocity=0, time=1000)  # just a stop
# exit()

'''
Using their wrapper, wasn't able to get the sockets working.
'''
# from mistyPy import Robot
# mia = Robot(IPADDRESS)
# mia.changeLED(0,0,255)
# print("changed LED")
# mia.changeImage("Happy.jpg")
# mia.subscribe("TimeOfFlight")
# incoming_data = mia.time_of_flight()
# print(incoming_data)

subscribeMessage = {
    "$id": "1",
    "Operation": "subscribe",
    "Type": "TimeOfFlight",
    "DebounceMs": 100,
    "EventName": "CenterTimeOfFlight",
    "Message": "",
    "ReturnProperty": None,
    "EventConditions": [{
        "Property": "SensorPosition",
        "Inequality": "=",
        "Value": "Center"
    }]
}
r = json.dumps(subscribeMessage)
# print(r)
# print(type(r))


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

changeImage()
exit()
addr = "ws://echo.websocket.org/"
addr = "ws://" + IPADDRESS + "/pubsub"
sock = MySocket(addr, id="Steve")
sock2 = MySocket(addr, id="James", position='RIGHT')
print("Finishedsocketing")

# IMAGE STUFF
def imageStuff(vals=[15,14,16], headings=["Connection", "Battery Level", "IP Address"]):
    img = np.zeros((300, 300, 3), np.uint8)
    img = cv2.putText(img, "Device Info", (70, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # returned a list, of an object, with attribute 'result', which maps to a dictionary, with a bunch of keys.
    # headings = ["Connection", "Battery Level", "IP Address"]
    # vals = [15, 14, 16]
    for i, (title, val) in enumerate(zip(headings, vals)):
        img = cv2.putText(img, title + ":  " + str(val), (30, 50 + 20 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imshow("img", img)
    cv2.waitKey(0)

    d = bytearray(img)
    # print(d)
    d = bytes(img)
    # print(d)

    print(img)
    flimg = img.flatten()
    print(flimg)
    sflimg = "".join(str(x) + "," for x in (img.flatten())[:-1])
    sflimg += str(flimg[-1])
    # print(sflimg)
    print(len(sflimg))
    return sflimg

# imageStuff()