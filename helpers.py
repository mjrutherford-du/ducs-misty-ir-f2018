import requests
import numpy as np
import json

'''
These are just simple helpers for Misty. Similar to their python wrapper class, but since there is only 1 robot,
I figured just using functions would be fine.


@updated: 9/25/18
@created date: 9/25/18
@author: David Cowie
'''


# thinking will put this in like a config file and just read it in everytime.
# or could pass in the IP address to every function but that would be tedious.
IPADDRESS = "192.168.1.5" #"172.20.10.4"

# could include the get to get all audio, then put that into a list and just start playing from there.
def playAudio(fileName):
    # print("[INFO] Playing Audio: {}".format(fileName))
    url = "http://{}/api/audio/play".format(IPADDRESS)

    # payload = "{\n\t\"FileName\": \"002-Ahhh.wav\",\n\t\"Volume\": 100\n}"
    payload = "{" + "\n\t\"FileName\": \"{}\",\n\t\"Volume\": 100\n".format(fileName) + "}"
    print("[INFO] Audio PayLoad: {}".format(payload))
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def changeImage(fileName="pink_sunset.jpg", timeout=5, alpha=0.5, wantPrint=True):
    if wantPrint:
        print("[INFO] Changing Image")
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
# there is also a drive endpoint to control speed of each track individually.
def drive(speed=20, angularvelocity=0, time=1000):
    # drive straight 5 seconds

    url = f"http://{IPADDRESS}/api/drive/time"
    # ill clean up this basic logic.
    if time == -1:
        print("Driving forever")
        url = f"http://{IPADDRESS}/api/drive"
        initPayload = "\n\t\"LinearVelocity\": {},\n\t\"AngularVelocity\": {}\n".format(speed, angularvelocity)
    else:
        initPayload = "\n\t\"LinearVelocity\": {},\n\t\"AngularVelocity\": {},\n\t\"TimeMS\": {}\n".format(speed, angularvelocity, time)
    print(f"Driving: \n{initPayload}")
    payload = "{" + initPayload + "}"
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

