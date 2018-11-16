from socketClass import MySocket
import time
import msvcrt
from helpers import drive

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
            print(f"SOCKET 1:: {messageCount}, {sock.getMessageCount()} :: {sock1Data}")
            # print(f"Socket true new message count: {sock.getMessageCount()}")
            prevSock1Data = sock1Data

        sock2Data = sock2.getData()
        if sock2Data is not None and prevSock2Data != sock2Data:
            print(f"SOCKET 2:: {messageCount}, {sock2.getMessageCount()} :: {sock2Data}")
            # print(f"Socket true new message count: {sock2.getMessageCount()}")
            prevSock2Data = sock2Data

        # this works for windows.
        if msvcrt.kbhit():
            val = msvcrt.getch()
            if val == b'q':
                sock.unsubscribe()
                sock2.unsubscribe()
                break

        # if messageCount > 500:
        #     sock.unsubscribe()
        #     sock2.unsubscribe()
        #     break

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
    # batteryVoltage
    sock = MySocket(id="Bill", type="SELF", maxMessages=-1, interestedAttributes=['occupancyGridCell', 'orientation'], wantPrint=False)

    maxMessages = 100
    i = 0
    data = None
    prevData = None
    X = [[(j / 255, j / 255, i / 255) for i in range(100)] for j in range(100)]
    X = np.array(X)
    numNewMessagesRecieved = 0
    while True:
        i += 1
        # cv2.imshow('test', X)
        # if (cv2.waitKey(1) & 0xFF) == ord('q'):
        #     # could then also close the socket.
        #     sock.unsubscribe()
        #     break
        # print("i:", i)
        if msvcrt.kbhit():
            val = msvcrt.getch()
            if val == b'q':
                ret = sock.unsubscribe()
                if ret:
                    break
                else:
                    print("Error unsubscribing. Probably hasn't connected yet. Wait for readings.")

        # if i >= maxMessages:
        #     # error because it hasn't opened yet.
        #     ret = sock.unsubscribe()
        #     if ret:
        #         break
        #     else:
        #         maxMessages += 100
                # then think would also want to have this check so there is at least some way of breaking out.
                # even if it is an error.
                # or i guess currently i just have to terminate python from task manager. so could do it that way.
        # if i % 5 == 0:
        #     data = sock.getData()
        data = sock.getData()
        print(data)
        if data is not None and data != prevData:
            numNewMessagesRecieved += 1
            print(f"{numNewMessagesRecieved}::SOCKET DATA: {data}")
            prevData = data

        time.sleep(0.02)


from helpers import getAndViewMap, getMapGrid, testDrawMap
# this is the live update of the map as it is being created.
# it will also show Misty's position on the map.
# here, mapping should be enabled.
# can use the self state to verify if Misty has Pose (if it has a position)
# could return the map, and store a previous one and do a check if lost pose, so
# if nothing is returned from mapping, can still save it.
def testSocketMap():
    print("[INFO] Testing socket with the map.")
    maxMessages = -1
    # might want to hide the prints from the socket itself.
    # and could subscribe in another terminal, if can subscribe twice.
    sock = MySocket(id="Bill", type="SELF", maxMessages=maxMessages, interestedAttributes=['occupancyGridCell'], wantPrint=False)
    i = 0
    position = None
    while True:
        i += 1
        data = sock.getData()
        if data is not None:
            position = data[0]
        print(f"i:{i} - Position: {position}")
        # perhaps, don't call this everytime, maybe it is now like overloading misty?..
        # even though it worked perfectly last week.
        # think just a counter, like maybe every 50 update map?
        # if i > 0 and i % 50 == 0:
        getAndViewMap(position, isBlocking=False, timesBigger=2)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            # could then also close the socket.
            # should do a health check.
            sock.unsubscribe()
            break

    cv2.destroyAllWindows()

def tryFollowPath():
    print("Following path")
    maxMessages = -1
    # might want to hide the prints from the socket itself.
    # and could subscribe in another terminal, if can subscribe twice.
    sock = MySocket(id="Bill", type="SELF", maxMessages=maxMessages, interestedAttributes=['occupancyGridCell'], wantPrint=False)
    i = 0
    position = None
    goalX = 20
    goalY = 65
    while True:
        i += 1
        data = sock.getData()
        if data is not None:
            position = data[0]
        print(f"i:{i} - Position: {position}")
        # perhaps, don't call this everytime, maybe it is now like overloading misty?..
        # even though it worked perfectly last week.
        # think just a counter, like maybe every 50 update map?
        # if i > 0 and i % 50 == 0:
        if position is not None:
            if position['x'] > goalX:
                # i guess drive straight
                drive(30, 0, 1000)
            # if position['x']

        getAndViewMap(position, isBlocking=False, timesBigger=2)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            # could then also close the socket.
            # should do a health check.
            sock.unsubscribe()
            break

    cv2.destroyAllWindows()


import pickle
def testSocketMapVersion2():
    print("[INFO] Testing socket with the map.")
    print("[IMPORTANT] HOPEFULLY YOU HAVE STARTED MAPPING IN THE API EXPLORER!!!!!!")
    '''
    IMPORTANT:
        Need to start mapping in the API explorer first.
        The reason I don't have that call in this function is because want to ensure that Misty has pos before
            starting the mapping process. Could check that here on my own (with subscribing to self state, and checking
            that data is being returned) but the API explorer is simplier and serves that purpose. 
    Also, navigation has been done using the API explorer and also using the driveController.py
        Both work fine. Reason for option is want to keep an eye to make sure POS is being maintained. So in API
        explorer, it is hard to see both at the same time. But can just keep watch of the self state from the console
        output of this function.
    '''
    maxMessages = -1
    # might want to hide the prints from the socket itself.
    # and could subscribe in another terminal, if can subscribe twice.
    sock = MySocket(id="Bill", type="SELF", maxMessages=maxMessages, interestedAttributes=['occupancyGridCell'],
                    wantPrint=False)
    i = 0
    position = None
    tBigger = 2
    dilateSize = 1
    wantingTruncate = False
    grid = None
    # would be nice to tell if a map has changed. But not sure how to do that without storing the previous map and doing
    # a large compare. But want to be able to save the grid. but think saving every step would be too expensive.
    # so just save a copy until the original is None, then save that one.
    previous_grid = None
    while True:
        i += 1
        data = sock.getData()
        if data is not None:
            position = data[0]
        if i % 5 == 0:
            print(f"i:{i} - Position: {position}")
        # perhaps, don't call this every time, maybe it is now like overloading misty?..
        # even though it worked perfectly last week.
        # think just a counter, like maybe every 50 update map?
        # if i > 0 and i % 50 == 0:
        grid = getMapGrid()
        # just need a check to ensure have a grid and have position.
        if grid is not None and position is not None:
            previous_grid = [list(b) for b in grid]  # not sure if really need to make a deep copy here...
            # but doing it just in case because don't want to have to try more than once.
            # testDrawMap(grid, position['x'], position['y'], timesBigger=tBigger, diNum=dilateSize, wantBlocking=False, wantTruncate=wantingTruncate)
            x = position['x']
            y = position['y']
            # x = len(grid) - x
            # y = len(grid[0]) - y
            testDrawMap(grid, y, x, timesBigger=tBigger, diNum=dilateSize, wantBlocking=False,
                        wantTruncate=wantingTruncate)

        if grid is None and previous_grid is not None:
            # then had a map and then lost it. So want to hold onto and save the map
            # then will just save in another file.
            with open("misty_map.txt", "wb") as fp:
                pickle.dump(previous_grid, fp)

        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            sock.unsubscribe()
            cv2.destroyAllWindows()
            with open("misty_map.txt", "wb") as fp:
                pickle.dump(previous_grid, fp)
            break
        elif key == ord('m'):
            print("Making bigger")
            tBigger += 1
            # speed = tBigger
        elif key == ord('n'):
            tBigger -= 1
            if tBigger <= 0:
                tBigger = 1
        elif key == ord('z'):
            dilateSize += 1
        elif key == ord('x'):
            dilateSize -= 1
            if dilateSize < 0:
                dilateSize = 0
        elif key == ord('t'):
            wantingTruncate = not wantingTruncate

    cv2.destroyAllWindows()

def view_saved_map():
    grid = None
    with open("misty_map_hallway_final.txt", "rb") as fp:
        grid = pickle.load(fp)
    testDrawMap(grid, 0, 0, timesBigger=1, wantTruncate=True)
    cv2.waitKey(0)
    return


if __name__ == "__main__":
    print("[INFO] Socket Class Driver.")

    # testTOFSockets()
    # testSelfSocket()
    # testSocketMap()
    # testSocketMapVersion2()
    view_saved_map()



'''
Notes for demo video:

WayPoints

For mapping
We needed mapping so misty could be able to navigate in the area to give a comprehensive tour of a

In order to have Misty give a tour, it is important to for Misty to have a map to navigate in.
So we created an essentially live video stream of Misty creating a map of her enviroment.
It involved subscribing to the self state to get position, and also hitting the API to get map updates. // the updated map.
It allowed us to have a dynamic visualization of the mapping process, which was really cool to see.
Some issues we had with the mapping was consistency of saving a map, and using waypoints to have misty follow a path.
We were able to get those features to work some of the time, but it was a little too inconsitent to make any progress with 
those features.
'''
