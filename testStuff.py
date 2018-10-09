import requests
import threading
# import cv2  # This is what i was using for some image processing.
# I will try to clean up and put things in appropriate files.
import numpy as np
import json

# Import the required module for text
# to speech conversion
from gtts import gTTS

#for audio conversion
from pydub import AudioSegment
from pydub.playback import play

'''
This is ugly initial tests.
It does include a basic sequence of actions using the RESTful API.
'''

IPADDRESS = "192.168.1.5" #"172.20.10.4"

#def imageStuff(vals=[15,14,16], headings=["Connection", "Battery Level", "IP Address"]):
    #WIDTH = 10  # 300
    #HEIGHt = 10  # 300
    #img = np.zeros((HEIGHt, WIDTH, 3), np.uint8)
    # img = cv2.putText(img, "Device Info", (70, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # returned a list, of an object, with attribute 'result', which maps to a dictionary, with a bunch of keys.
    # headings = ["Connection", "Battery Level", "IP Address"]
    # vals = [15, 14, 16]
    #for i, (title, val) in enumerate(zip(headings, vals)):
       #  img = cv2.putText(img, title + ":  " + str(val), (30, 50 + 20 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    # cv2.imshow("img", img)
    # cv2.waitKey(0)

    #d = bytearray(img)
    # print(d)
    #d = bytes(img)
    # print(d)

    #print(img)
    #flimg = img.flatten()
    #print(flimg)
    #sflimg = "".join(str(x) + "," for x in (img.flatten())[:-1])
   # sflimg += str(flimg[-1])
    # print(sflimg)
    #print(len(sflimg))
    #return img

def uploadAudio(fileName):
    print("[INFO] Uploading Audio: {}".format(fileName))
    url = "http://{}/api/audio/".format(IPADDRESS)

    byteArray = open(fileName + '.mp3', 'rb').read()
    dataAsByteArrayString = byteArray.decode('cp855')

    payload = {
        "FileName": fileName,
        "DataAsByteArrayString": dataAsByteArrayString,
        "ImmediatelyApply": True,
        "OverwriteExisting": True
    }
    payload = json.dumps(payload)
    print(payload)
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

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
    url = "http://{}/api/images/change".format(IPADDRESS)

    # payload = "{\n\t\"FileName\": \"pink_sunset.jpg\",\n\t\"TimeOutSeconds\": 5,\n\t\"Alpha\": 0.5\n}"
    payload = "{" + "\n\t\"FileName\": \"{}\",\n\t\"TimeOutSeconds\": {},\n\t\"Alpha\": {}\n" + "}".format(fileName, timeout, alpha)
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

# time as -1 if want to drive without a time limit.
def drive(speed=20, angularvelocity=0, time=1000):
    # drive straight 5 seconds

    url = "http://{}/api/drive/time".format(IPADDRESS)
    if time == -1:
        print("Driving forever")
        url = "http://{}/api/drive".format(IPADDRESS)
        initPayload = "\n\t\"LinearVelocity\": {},\n\t\"AngularVelocity\": {}\n".format(speed,angularvelocity)
    else:
        initPayload = "\n\t\"LinearVelocity\": {},\n\t\"AngularVelocity\": {},\n\t\"TimeMS\": {}\n".format(speed, angularvelocity, time)
    print("Driving: \n{}".format(initPayload))
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
    #playAudio("032-Bewbewbeeew.wav")
    # sendImageToMisty(img, "deviceInfo.jpg")

    print("About to change image to pink sunset.")
    # playAudio("032-Bewbewbeeew.wav")
    #changeImage("pink_sunset.jpg")
    #playAudio("002-Growl-01.wav")
    #drive(speed=20, angularvelocity=100, time=2000)  # this actually turns in place pretty well, turns 90 degrees to the right on the table but turns to the left.
    #playAudio("006-EhMeEhmeUh.wav")
    drive(speed=20, angularvelocity=-100, time=100)
    #playAudio("001-OooOooo.wav")
    mytext = 'Misty Test!'

    # Language in which you want to convert
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=mytext, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome
    myobj.save("welcome.mp3")

    # Playing the converted file
    uploadAudio("welcome")
    playAudio("welcome.mp3")
    #drive(speed=0, angularvelocity=0, time=1000)  # just a stop

basicSequence()
 #exit()
#### Also, could call to get the device info, then write that to an image, and send it to misty to seee the info on screen.
# so get device info, then write on image, then send that image.

def createDeviceInfoImage():
    deviceInfo = getDeviceInfo()
# imageStuff()