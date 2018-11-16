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

def driveLocamotionTrack(leftSpeed, rightSpeed):
    url = f"http://{IPADDRESS}/api/drive/track"
    payload = {
        "LeftTrackSpeed": leftSpeed,
        "RightTrackSpeed": rightSpeed
    }
    payload = json.dumps(payload)
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def stopDriving():
    url = f"http://{IPADDRESS}/api/drive/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)

def getDeviceInfo():
    url = "http://{}/api/info/device".format(IPADDRESS)

    response = requests.request("GET", url)
    # returned a list, of an object, with attribute 'result', which maps to a dictionary, with a bunch of keys.
    # so might convert the string to a json object..
    # but would have to test how it works.
    print(response.text)
    return response.text

# -5 to 5 for position
# 0 to 10 for velocity
def set_head_position(position, velocity):
    url = "http://" + IPADDRESS + "/api/beta/head/position"
    payload = json.dumps({"Axis": "pitch",
                          "position": position,
                          "Velocity": velocity})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def getMap():
    # documentation says /smooth, but that gets a 404
    # but if i use /raw instead, then that seems to work.
    url = "http://{}/api/alpha/slam/map/raw".format(IPADDRESS)
    # url = "http://{}/api/alpha/slam/map/smooth".format(IPADDRESS)

    response = requests.request("GET", url)
    # just get a 404 error.
    # print("MAP RESPONSE:")
    # print(response)
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
                innerList1.append(orig[i][j])
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
def getAndViewMap(currentPosition=None, isBlocking=True, timesBigger=1, dilateSize=0, wantTrimming=False):
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
    # then, for the hallway, since the robot thinks it starts in the middle of the world...
    # the hallway only ggrows down the image, and above the starting spot will never be filled in.
    # so FOR THAT SPECIFIC USE CASE, can trim the output image down.
    firstObjectFound = 0
    robotColor = (28/255, 231/255, 248/255)
    whiteColor = (0.99, 0.99, 0.99)
    borderColor = (0, 0, 0)
    havePosition = currentPosition is not None
    pX = currentPosition['x'] if havePosition else 0
    pY = currentPosition['y'] if havePosition else 0
    for i in range(len(grid)):
        innymap = []
        for j in range(len(grid[i])):
            for _ in range(timesBigger):
                if currentPosition is not None and i == currentPosition['x'] and j == currentPosition['y']:
                    innymap.append(robotColor)
                else:
                    innymap.append(colorMap[grid[i][j]])

                # TODO:: TEST THIS, SHOULD BE GOOD FOR MAKING MISTY EASIER TO SEE ON MY MAP
                # if havePosition and dilateSize > 0 and i >= (pY - dilateSize) and i <= pY + dilateSize and j >= pX - dilateSize and j <= pX + dilateSize:
                #     if i == pY and j == pX:
                #         innymap.append((0.99, 0, 0))
                #     else:
                #         innymap.append(robotColor)
                # else:
                #     innymap.append(colorMap[grid[i][j]])

                # for trimming.
                if wantTrimming and firstObjectFound == 0 and grid[i][j] != 0:
                    firstObjectFound = i

        # counting border.
        if i % 5 == 0:
            for _ in range(timesBigger):
                innymap.append(whiteColor)
        else:
            for _ in range(timesBigger):
                innymap.append(borderColor)

        for _ in range(timesBigger):
            map.append(innymap)
    # and could dialate the current position even more.
    # for trimming..
    if wantTrimming and firstObjectFound != 0:
        map = map[(firstObjectFound * timesBigger):]

    n_grid = np.array(map)
    cv2.imshow("test", n_grid)
    if isBlocking:
        cv2.waitKey(0)
    return grid


def getMapGrid():
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
    return grid

def testDrawMap(X, pX, pY, timesBigger=3, diNum=2,wantBlocking=False, wantTruncate=False, isTesting=False):
    # here, for the testing, the map passed in was a grid of tuples, but the getMap is just a grid on ints.
    # so there is a mismatch. either need to convert in here, or do it before.
    # think need to do it in here, because should be faster.
    height = len(X)
    width = len(X[0])
    # print(f"Height: {len(X)}, Width: {len(X[0])}")
    # print("Map:", X)
    # print("="*30)
    # print("=" * 30)
    # print("=" * 30)
    # print("=" * 30)
    # print("=" * 30)
    # timesBigger = 3
    newX = []
    startObjectFirst = 0
    # diNum = 2
    # diNum2 = 1
    # newX2 = []
    colorMap = [(0.5, 0.5, 0.5), (0.99, 0, 0), (0, 0, .99), (0, 0.99, 0)]
    pColor = (28 / 255, 231 / 255, 248 / 255)
    whiteColor = (0.99, 0.99, 0.99)
    borderColor = (0, 0, 0)  #(0, 0.99, 0)
    for i in range(len(X)):
        innerList1 = []  # i guess it would just be add the same list twice.
        # innerList2 = []
        for j in range(len(X[i])):
            for _ in range(timesBigger):
                # if want border to overlap actual image.
                # if j >= width - 3 and i % 5 == 0:
                #     # could also, instead of drawing more on the image, just add some padding.
                #     # so it would just be outside of this j loop, but then would actually could just do the check for when
                #     # j is right at the end, then just add number of tick pixels that want.
                #     innerList1.append(whiteColor)
                #     # innerList2.append((0.99, 0.99, 0.99))
                # else:
                #     if i >= (pY - diNum) and i <= pY + diNum and j >= pX - diNum and j <= pX + diNum:
                #         # print("Adding more player")
                #         # print("pY:",pY, "pX:", pX, "i:",i,"j:",j)
                #         innerList1.append(pColor)
                #     else:
                #         innerList1.append(X[i][j])
                #     # if i >= (pY - diNum2) and i <= pY + diNum2 and j >= pX - diNum2 and j <= pX + diNum2:
                #     #     # print("Adding more player")
                #     #     # print("pY:",pY, "pX:", pX, "i:",i,"j:",j)
                #     #     innerList2.append(pColor)
                #     # else:
                #     #     innerList2.append(X[i][j])

                if i >= (pY - diNum) and i <= pY + diNum and j >= pX - diNum and j <= pX + diNum:
                    # print("Adding more player")
                    # print("pY:",pY, "pX:", pX, "i:",i,"j:",j)
                    if i == pY and j == pX:
                        innerList1.append((0.99, 0, 0))
                    else:
                        innerList1.append(pColor)
                else:
                    if isTesting:
                        innerList1.append(X[i][j])
                    else:
                        innerList1.append(colorMap[X[i][j]])

                if isTesting and startObjectFirst == 0 and X[i][j] != (0.5, 0.5, 0.5):
                    # print("[IT HAPPENED, ", i)
                    startObjectFirst = i
                elif startObjectFirst == 0 and X[i][j] != 0:
                    startObjectFirst = i
                    if startObjectFirst > 5:
                        startObjectFirst -= 5
        # Version 2 of the numbers, was to add it to the outside of the image.
        bcolor = borderColor
        if i % 5 == 0:
            bcolor = whiteColor
        for _ in range(timesBigger):
            innerList1.append(bcolor)

        for _ in range(timesBigger):
            newX.append(innerList1)

    # make the y axis.
    bcolor = borderColor
    blist = []
    for i in range(width):
        if i % 5 == 0:
            bcolor = whiteColor
        else:
            bcolor = borderColor
        for _ in range(timesBigger):
            blist.append(bcolor)
    # then have to add to the bottom border extra to match the side border.
    for _ in range(timesBigger):
        blist.append(whiteColor)

    for _ in range(timesBigger):
        newX.append(blist)

    if startObjectFirst != 0 and wantTruncate:
        # print("Shortening")
        X = X[startObjectFirst:]
        # pY -= startObjectFirst
        height = len(X)
        # height = height - startObjectFirst
        startObjectFirst *= timesBigger
        startObjectFirst -= 5
        newX = newX[startObjectFirst:]

    # drawing
    # print(newX)
    # print(len(newX))
    newX = np.array(newX)
    # newX2 = np.array(newX2)
    if isTesting:
        X = np.array(X)
    # wait for this calculation till here, because if truncating, depends on how much cutting out.
    heightOut = timesBigger * height
    widthOut = timesBigger * width
    # i guess I could just do tick marks and count them, there aren't that many.
    # size 0.25 for times 2
    # x numbers
    # works well for 1 and 2 digit numbers, 3 digit will prolly be too big
    x_label_step_size = 5
    y_label_step_size = 10
    for i in range(0, height, x_label_step_size):
        numIn = 3
        if i >= 100:
            numIn = 7
        elif i >= 10:
            numIn = 5
        cv2.putText(newX, "{}".format(i), (widthOut - numIn*timesBigger, heightOut - i*timesBigger), cv2.FONT_HERSHEY_SIMPLEX, 0.125*timesBigger, (255,255,255), 1, cv2.LINE_AA)

    for i in range(0, width, y_label_step_size):
        if i == 0:
            continue
        cv2.putText(newX, "{}".format(i), (widthOut - i*timesBigger - 2*timesBigger, heightOut - 2*timesBigger), cv2.FONT_HERSHEY_SIMPLEX, 0.125*timesBigger, (255,255,255), 1, cv2.LINE_AA)

    wantDrawGrid = False
    if wantDrawGrid:
        for i in range(0, height, 5):
            cv2.line(newX, (0, (i*timesBigger) + 1), (widthOut + timesBigger, i*timesBigger + 1), (0, 255, 0), timesBigger)
        for i in range(0, width, 5):
            cv2.line(newX, ((i*timesBigger) + 1, 0), (i*timesBigger + 1, heightOut + timesBigger), (0, 255, 0), timesBigger)
    # print(X)
    if isTesting:
        cv2.imshow("test", X)
    cv2.imshow("testbigger", newX)
    # base = [[tstColor for i in range(100)] for j in range(100)]
    # base = np.array(base)
    # cv2.imshow("base", base)
    # cv2.imshow("thing", newX2)
    if wantBlocking:
        cv2.waitKey(0)


def testMappingDriver():
    X = np.random.random((100, 100))
    # X = [[(random.random(), random.random(), random.random()) for i in range(100)] for j in range(100)]
    startX = [[(0.5, 0.5, 0.5) for i in range(100)] for j in range(50)]
    tstColor = (0.9, 0, 0.9)  # (j/255, j/255, i/255)

    X = [[tstColor for i in range(100)] for j in range(100)]
    # pX, pY = 50, 50
    # X[pX][pY] = pColor
    # pY += len(startX)
    # then want to make bigger so this makes each pixel, 2x2 instead of 1x1
    # print(X)
    X = startX + X
    width = len(X[0])
    height = len(X)
    pX, pY = 50, 100
    # X[pY][pX] = pColor
    testDrawMap(X, pX, pY, True)
    speed = 1
    tBigger = 2
    dilateSize = 1
    wantingTruncate = False
    while True:

        pX += speed
        if pX >= width - 1:
            speed = -1 * speed
        elif pX <= 1:
            speed = -1 * speed
        testDrawMap(X, pX, pY, timesBigger=tBigger, diNum=dilateSize, wantBlocking=False, wantTruncate=wantingTruncate, isTesting=True)

        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            cv2.destroyAllWindows()
            break
        elif key == ord('m'):
            print("Making bigger")
            tBigger += 1
            # speed = tBigger
        elif key == ord('n'):
            tBigger -= 1
            if tBigger <= 0:
                tBigger = 1
            # speed = tBigger
        elif key == ord('z'):
            dilateSize += 1
        elif key == ord('x'):
            dilateSize -= 1
            if dilateSize < 0:
                dilateSize = 0
        elif key == ord('t'):
            wantingTruncate = not wantingTruncate


if __name__ == "__main__":
    # getAndViewMap(timesBigger=3)
    # exit()
    # set_head_position(5, 10)
    # testMappingDriver()
    # exit()
    print("[INFO] Main helpers.")
    getSlamStatus()
    # resetSlamSensors()
    # got a status of 32, don't know what that is.
    # getSlamStatus()
    myPath = "101:101,103:101,104:101,104:105"
    myPath = "104:105,104:101,103:101,101:101"
    myPath = "125:115,125:120,125:125,125:135,125:145,125:155"
    myPath = "65:60,60:60,55:60,50:60,40:60,30:60"
    follow_path(myPath)
    # getDeviceInfo()
    # now the map is gone.
    # getAndViewMap()
    # so from that map, just to try and visualize it, want to do a get map
    # extract the map part out from the thing, and then just for now maybe just make the everything 1 or 0


