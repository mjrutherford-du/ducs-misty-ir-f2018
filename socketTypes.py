import json

'''
These are mini classes for the structure of the return message from each socket type.
So can just put the response into the class and deal with it that way.
Not sure if we will want/need to utilize these but this is a more object oriented approach.

Also, each response has a type so could just pass the response to a different handler function that could return one
of these classes.

@updated: 9/25/18
@created date: 9/25/18
@author: David Cowie
'''


'''
This was taken from their documentation.
Thinking just pass in this string, then this class would handle parsing the string to an object and creating attributes.

TimeOfFlight{
    "EventName":"TimeOfFlight",
    "Message":{
        "Created":"2018-03-30T20:36:46.5816862Z",
        "DistanceInMeters":0.184,
        "Expiry":"2018-03-30T20:36:46.9316897Z",
        "SensorId":"CD727A0A",
        "SensorPosition":"Right"
    },
    "Type":"TimeOfFlight"
}
'''

class SocketMessage:
    def __init__(self, message):
        data = json.loads(message)
        self.eventName = data['EventName']
        self.type = data['Type']


# time of Flight
# well, dont want to create one of these every time a message is recieved, only the first time, then just update.
# so maybe have an update
# so create this with the socket, so want to try and not have to specify the type of socket.
# could pass a string to the socket, cause The idea is the socket would create one of these
# then from the socket, would want like a getData() function, that could return the data in a useful format.
# so instead of having all the parsing logic in the socket, and have a bunch of if statements. can just call something
# to return a message object of the right type, then just call that update function, and then a get info function
# then use that and return that

# so like have an array of sockets created, and know which they are by name, then can just say socket.getData
# and if it is a time of flight socket, then it will return just the distance.
class TimeOfFlightMessage(SocketMessage):
    def __init__(self, message):
        SocketMessage.__init__(message)
        data = json.loads(message)
        data = data['message']
        self.distance = data['distanceInMeters']
        self.sensor_position = data['SensorPosition']
        # not including created or expiry cause I dont get them.

    def update(self, message):
        data = json.loads(message)
        self.distance = data['message']['distanceInMeters']

    def getData(self):
        return self.distance

    def __repr__(self):
        return f"TimeOfFlightMessage({self.sensor_position}, {self.distance}"

    def __str__(self):
        return f"[TOF]:{self.sensor_position} - Distance: {self.distance} m"
