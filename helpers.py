import requests
import numpy as np
import json
import cv2
import random
import time

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
headers = {'Content-Type': "application/json",
           'Cache-Control': "no-cache"}

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

def getMap():
    # documentation says /smooth, but that gets a 404
    # but if i use /raw instead, then that seems to work.
    url = "http://{}/api/alpha/slam/map/raw".format(IPADDRESS)

    response = requests.request("GET", url)
    # just get a 404 error.
    print("MAP RESPONSE:")
    print(response)
    # print(response.text)
    return json.loads(response.text)[0]

def getSlamStatus():
    url = "http://{}/api/alpha/slam/status".format(IPADDRESS)
    response = requests.request("GET", url)
    print(response.text)
    return response.text

def resetSlamSensors():
    url = "http://{}/api/alpha/slam/reset".format(IPADDRESS)

    response = requests.request("POST", url)
    print(response)
    print(response.text)

def slamStartMapping():
    url = "http://{}/api/alpha/slam/map/start".format(IPADDRESS)

    response = requests.request("POST", url)
    print(response)
    print(response.text)

def slamStopMapping():
    url = "http://{}/api/alpha/slam/map/stop".format(IPADDRESS)

    response = requests.request("POST", url)
    print(response)
    print(response.text)

# for the follow path, I found that it worked when I was still mapping.
# i didn't use the tracker. I just hit start mapping in the api explorer
# and was subscribed to SelfState, and I just took a few of those values.
def follow_path(path):
    url = "http://" + IPADDRESS + "/api/alpha/drive/path"
    payload = json.dumps({"Path": path})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

# this can just make the map easier to see.
def makeImageBigger(orig, timesBigger=2):
    newX = []
    for i in range(len(orig)):
        innerList1 = []  # i guess it would just be add the same list twice.
        for j in range(len(orig[i])):
            for _ in range(timesBigger):
                innerList1.append(X[i][j])
        for _ in range(timesBigger):
            newX.append(innerList1)

    return newX

# EXAMPLE USAGE IN SOCKET DRIVER
# like what i would do with getting the videofeed from the camera.
# just a wait_key(1) and === ord('q') to break.
# so have a while loop, where outside, created a socket to SelfState
# then inside, to a getData call to the socket,
# then pass that through to this function,
# might want a time.sleep to try and delay. or only call getandViewMap on an interval
# like a counter, every 10 iterations would be easy enough.
def getAndViewMap(currentPosition=None, isBlocking=True, timesBigger=1):
    mapRes = getMap()
    # print("====================")
    # print(mapRes)
    grid = mapRes['result']['grid']
    if grid is None:
        print("THE GRID IS NONE")
        return None
    if mapRes['result']['height'] == 0:
        print("NO HEIGHT. PROBABLY INVALID MAP, NO DATA")
        # should error out or just return
        return None
    # print("==================")
    # print(grid)
    colorMap = [(0.5, 0.5, 0.5), (0.99, 0, 0), (0, 0, .99), (0, 0.99, 0)]
    map = []
    # X should be forward and backwards, so compare that with i, and Y with j
    # could also just try to do the dilating here.
    for i in range(len(grid)):
        innymap = []
        for j in range(len(grid[i])):
            for _ in range(timesBigger):
                if currentPosition is not None and i == currentPosition['x'] and j == currentPosition['y']:
                    innymap.append((28/255, 231/255, 248/255))
                else:
                    innymap.append(colorMap[grid[i][j]])
        for _ in range(timesBigger):
            map.append(innymap)

    n_grid = np.array(map)
    cv2.imshow("test", n_grid)
    if isBlocking:
        cv2.waitKey(0)



X = np.random.random((100, 100))
# X = [[(random.random(), random.random(), random.random()) for i in range(100)] for j in range(100)]
X = [[(j/255, j/255, i/255) for i in range(100)] for j in range(100)]
# then want to make bigger so this makes each pixel, 2x2 instead of 1x1
# timesBigger = 5
# newX = []
# for i in range(len(X)):
#     innerList1 = [] # i guess it would just be add the same list twice.
#     for j in range(len(X[i])):
#         for _ in range(timesBigger):
#             innerList1.append(X[i][j])
#         # innerList1.append(X[i][j])
#     for _ in range(timesBigger):
#         newX.append(innerList1)
#     # newX.append(innerList1)

# newX = makeImageBigger(X, 2)
# newX = np.array(newX)
# X = np.array(X)
# # print(X)
# cv2.imshow("test", X)
# cv2.imshow("testbigger", newX)
# cv2.waitKey(0)


if __name__ == "__main__":
    # getAndViewMap(timesBigger=3)
    # exit()
    exit()
    print("[INFO] Main helpers.")
    getSlamStatus()
    # resetSlamSensors()
    # got a status of 32, don't know what that is.
    # getSlamStatus()
    myPath = "101:101,103:101,104:101,104:105"
    myPath = "104:105,104:101,103:101,101:101"
    # follow_path(myPath)
    # getDeviceInfo()
    # now the map is gone.
    getAndViewMap()
    # so from that map, just to try and visualize it, want to do a get map
    # extract the map part out from the thing, and then just for now maybe just make the everything 1 or 0


