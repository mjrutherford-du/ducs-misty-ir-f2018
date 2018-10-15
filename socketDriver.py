from socketClass import MySocket
import time

def testTOFSockets():
    # this should be able to listen to the Center and right TOF sensors at the same time.
    # and the readings begin as soon as the sockets are created.
    sock = MySocket(id="Steve", wantPrint=False, maxMessages=-1)
    sock2 = MySocket(id="James", position='RIGHT', wantPrint=False, maxMessages=-1)
    # so if do it this way, the data will catch up, but not for a while
    sock1Data = 0
    prevSock1Data = 0
    sock2Data = 0
    prevSock2Data = 0
    noChangeCount = 0
    messageCount = 0
    # An Issue is in the socket class, it recieves far fewer messages, then I count out here.
    # because this is constantly getting the data, where as the socket class message count only updates whenver it recieves
    # data. So can have a way of checking if data has changed.
    # like the socketClass will be at message count 15, while here it has gotten to 200.
    # obviously, for full use, would have it running indefinitely. but just need to be aware, and handle accordingly.
    while True:
        # print("Stuff")
        sock1Data = sock.getData()
        messageCount += 1
        if sock1Data is not None and prevSock1Data != sock1Data:
            print(f"{messageCount} 1sock data:: {sock1Data}")
            prevSock1Data = sock1Data

        sock2Data = sock2.getData()
        if sock2Data is not None and prevSock2Data != sock2Data:
            print(f"{messageCount} 2sock data:: {sock2Data}")
            prevSock2Data = sock2Data

        # if sock.getData() != sock1Data:
        #     sock1Data = sock.getData()
        #     print(f"1sock data:: {sock1Data}")
        #     noChangeCount = 0
        # if sock2.getData() != sock2Data:
        #     sock2Data = sock2.getData()
        #     print(f"2sock data::{sock2Data}")
        #     noChangeCount = 0
        noChangeCount += 1
        # if noChangeCount >= 30:
        #     break
        if messageCount > 500:
            sock.unsubscribe()
            sock2.unsubscribe()
            break
        # with 0.1 it was missing every other message
        # also want to check if this sleeps this thread or everything, but if it was everything, would have thought that
        # it would when it was 0.1, have skipped the output in the socket class also.
        time.sleep(0.02)
    print("Finishedsocketing")

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
import cv2
import numpy as np

# should work, but didn't have pose.
def testSelfSocket():
    # this is default behavior
    # sock = MySocket(id="Bill", type="SELF", maxMessages=20)
    # if want to see other attributes
    sock = MySocket(id="Bill", type="SELF", maxMessages=-1, interestedAttributes=['orientation'])

    maxMessages = 100
    i = 0
    data = None
    prevData = None
    X = [[(j / 255, j / 255, i / 255) for i in range(100)] for j in range(100)]
    X = np.array(X)
    while True:
        i += 1
        # cv2.imshow('test', X)
        # if (cv2.waitKey(1) & 0xFF) == ord('q'):
        #     # could then also close the socket.
        #     sock.unsubscribe()
        #     break
        if i >= maxMessages:
            # error because it hasn't opened yet.
            sock.unsubscribe()
            break
        # if i % 5 == 0:
        #     data = sock.getData()
        data = sock.getData()[0]
        # print(data)
        if data is not None and data != prevData:
            print(f"SOCKET DATA: {data}")
            prevData = data

        time.sleep(0.02)


from helpers import getAndViewMap
def testSocketMap():
    print("[INFO] Testing socket with the map.")
    maxMessages = -1
    sock = MySocket(id="Bill", type="SELF", maxMessages=maxMessages)
    i = 0
    # this makes a cool gradient lol.
    X = [[(j / 255, j / 255, i / 255) for i in range(100)] for j in range(100)]
    while True:
        i += 1
        position = sock.getData()[0]
        print(f"i:{i} - Position: {position}")
        getAndViewMap(position, isBlocking=False, timesBigger=2)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            # could then also close the socket.
            sock.unsubscribe()
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("[INFO] Socket Class Driver.")
    # testTOFSockets()
    testSelfSocket()
    # testSocketMap()
