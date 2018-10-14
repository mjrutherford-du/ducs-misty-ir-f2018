#!/usr/bin/python
# -*- coding: utf-8 -*-

# mistyFuncLib.py
# author: Vince Luo
# Sep. 29, 2018


import json
import requests
from gtts import gTTS
import hashlib
import time
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play


ip_address = "192.168.1.5"

headers = {'Content-Type': "application/json",
           'Cache-Control': "no-cache"}
           
rooms_text = [
    "This is Room 266, The Advanced Manufacturing Laboratory",
    "This is Room 278, The Perceptual and Cognitive Dynamics Laboratory",
    "This is Room 262, The Dynometer Booth",
    "This is Room 258, The Wind Tunnel",
    "This is Room 256, Jerry Edelstein and Andrei Roudik's office",
    "This is Room 248, The Mechatronics / Robotics / Vision Research Laboratory",
    "This is Room 222, The Unmanned Systems and Research Laboratory, where I was worked on",
    "This is Room 226, A Mechanical Engineering Laboratory",
    "This is Room 242, The ECE Instructional Laboratory",
    "This is Room 246, The Power Instructional Laboratory",
]


# Display and LED
def change_led(r, g, b):
    if r not in range(256):
        raise Exception("The red value need to be in 0-255 range")
    if g not in range(256):
        raise Exception("The green value need to be in 0-255 range")
    if b not in range(256):
        raise Exception("The blue value need to be in 0-255 range")
    url = "http://" + ip_address + "/api/led/change"
    payload = json.dumps({"red": r, "green": g, "blue": b})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def get_list_of_image():
    image_list = []
    url = "http://" + ip_address + "/api/images"
    response = requests.request("GET", url, headers=headers)
    for i in response.json():
        for j in i["result"]:
            image_list.append(j["name"])
    print(response.text)
    print(image_list)
    return image_list


def change_display_image(file_name, time_out):
    if file_name not in get_list_of_image():
        raise Exception(file_name, "not found on the robot")
    else:
        url = "http://" + ip_address + "/api/images/change"
        payload = json.dumps(
            {"FileName": file_name, "TimeOutSeconds": time_out, "Alpha": 1})
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)


def save_image_to_misty(image_name):
    with open(image_name, "rb") as image_file:
        byte_array = bytearray(image_file.read())

    new_string = ""
    for i in range(len(byte_array)):
        if i == (len(byte_array) - 1):
            new_string += str(byte_array[i])
        else:
            new_string += (str(byte_array[i]) + ",")

    url = "http://"+ip_address+"/api/images"
    payload = json.dumps({"FileName": image_name, "DataAsByteArrayString": new_string, "Width": "480", "Height": "272",
                          "ImmediatelyApply": True, "OverwriteExisting": True})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def delete_image_asset_from_robot(image_name):
    url = "http://" + ip_address + "/api/images/delete"
    payload = json.dumps({"FileName": image_name})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


## Audio

def get_list_of_audio_clips():
    audio_list = []
    url = "http://" + ip_address + "/api/audio/clips"
    response = requests.request("GET", url, headers=headers)
    for i in response.json():
        for j in i["result"]:
            audio_list.append(j["name"])
    # print(response.text)
    print(audio_list)
    return audio_list


def play_audio_clip(file_name, volume):
    if file_name not in get_list_of_audio_clips():
        raise Exception(file_name, "not found on the robot")
    elif volume not in range(101):
        raise Exception("Invalid volume value")
    else:
        url = "http://" + ip_address + "/api/audio/play"
        payload = json.dumps(
            {"AssetId": file_name, "Volume": volume})
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)


def save_audio_to_misty(audio_name):
    with open(audio_name, "rb") as audio_file:
        byte_array = bytearray(audio_file.read())

    new_string = ""
    for i in range(len(byte_array)):
        if i == (len(byte_array) - 1):
            new_string += str(byte_array[i])
        else:
            new_string += (str(byte_array[i]) + ",")

    url = "http://"+ip_address+"/api/audio"
    payload = json.dumps({"FilenameWithoutPath": audio_name, "DataAsByteArrayString": new_string,
                          "ImmediatelyApply": False, "OverwriteExisting": True})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Enables you to remove an audio file from Misty that you have previously uploaded
def delete_audio_asset_from_robot(file_name):
    url = "http://" + ip_address + "/api/beta/audio/delete"
    payload = json.dumps({"FileName": file_name})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def convert_and_play_text_to_audio(text):
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    tts = gTTS(text=text, lang= language)
    # Saving the converted audio in a mp3 file
    tts.save(hashlib.md5(text).hexdigest()[:15]+".mp3")
    save_audio_to_misty(hashlib.md5(text).hexdigest()[:15]+".mp3")
    play_audio_clip(hashlib.md5(text).hexdigest()[:15]+".mp3", 100)
    delete_audio_asset_from_robot(hashlib.md5(text).hexdigest()[:15]+".mp3")


def convert_mp3_to_wav(file_name, extension):
    song = AudioSegment.from_mp3(file_name+"."+extension)
    song.export(file_name+".wav", format="wav")
    print "Successfully Converted: "+file_name+"."+extension+" to "+file_name+".wav"


# Sets the default loudness of Misty's speakers for audio playback
def set_default_volume(volume):
    url = "http://" + ip_address + "/api/alpha/audio/volume"
    payload = json.dumps({"Volume": volume})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


## Locomotion

# Drives Misty forward or backward at a specific speed until cancelled.
# linear_velocity: speed in a straight line (-100: backward, 100: forward)
# angular_velocity: speed and direction of rotation (-100: clockwise, 100: counter-clockwise)
def drive(linear_velocity, angular_velocity):
    url = "http://" + ip_address + "/api/drive"
    payload = json.dumps({"LinearVelocity": linear_velocity,
                          "AngularVelocity": angular_velocity})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Drives Misty forward or backward at a set speed, with a given rotation, for a specified amount of time.
# linear_velocity: speed in a straight line (-100: backward, 100: forward)
# angular_velocity: speed and direction of rotation (-100: clockwise, 100: counter-clockwise)
# time_in_ms: a value in milliseconds that specifies the duration of movement (0 to 1000ms)
def drive_time(linear_velocity, angular_velocity, time_in_ms):
    url = "http://" + ip_address + "/api/drive/time"
    payload = json.dumps({"LinearVelocity": linear_velocity,
                          "AngularVelocity": angular_velocity,
                          "TimeMS": time_in_ms})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Drives Misty left, right, forward, or backward, depending on the track speeds specified for the individual tracks.
# left_track_speed: a value for the speed of the left track (-100, 100)
# right_track_speed: a value for the speed of the right track (-100, 100)
def locomotion_track(left_track_speed, right_track_speed):
    url = "http://" + ip_address + "/api/drive/track"
    payload = json.dumps({"LeftTrackSpeed": left_track_speed,
                          "RightTrackSpeed": right_track_speed})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Stops Misty's movement
def stop():
    url = "http://" + ip_address + "/api/drive/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


## Misty Information

# Obtains a list of local WiFi networks and basic information regarding each
def get_available_wifi_networks():
    url = "http://" + ip_address + "/api/info/wifi"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


# Obtains Misty's current battery level
def get_battery_level():
    url = "http://" + ip_address + "/api/info/battery"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


# Obtains device-related information for the robot
def get_device_info():
    url = "http://" + ip_address + "/api/info/device"
    response = requests.request("GET", url, headers=headers)
    with open("device info.txt", mode='w') as f:
        f.write(response.text)


# Obtains information about a specified API command
def get_help(command=None):
    if command is None:
        url = "http://" + ip_address + "/api/info/help"
    else:
        url = "http://" + ip_address + "/api/info/help?command="+command
    response = requests.request("GET", url, headers=headers)
    print(response.text)



# Obtains the robot's recent log files.
def get_log_file(date=None):
    if date is None:
        url = "http://" + ip_address + "/api/info/logs"
        log_file_name = "full_logs.txt"
    else:
        url = "http://" + ip_address + "/api/info/logs?date=" + date
        log_file_name = "log_" + date + "_1.txt"
    response = requests.request("GET", url, headers=headers)
    with open(log_file_name, mode='w') as f:
        f.write(response.text)


# Provides a list of available WebSocket data from Misty to which you can subscribe
def get_websocket_help():
    url = "http://" + ip_address + "/api/beta/info/help/websocket"
    response = requests.request("GET", url, headers=headers)
    with open("device info.txt", mode='w') as f:
        f.write(response.text)


## Configuration

# Connects Misty to a specified WiFi source
def set_wifi_connection(network_name, password):
    url = "http://" + ip_address + "/api/wifi"
    payload = json.dumps({"NetworkName": network_name,
                          "Password": password})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


## Head Movement

# For Misty I, the MoveHead command can only control the up-down movement of Misty's head
def set_head_position(position, velocity):
    url = "http://" + ip_address + "/api/beta/head/position"
    payload = json.dumps({"Axis": "pitch",
                          "position": position,
                          "Velocity": velocity})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


## Faces - AI

# Initiates Misty's detection of faces in her line of vision
def start_face_detection():
    url = "http://" + ip_address + "/api/beta/faces/detection/start"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Stops Misty's detection of faces in her line of vision
def stop_face_detection():
    url = "http://" + ip_address + "/api/beta/faces/detection/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Trains Misty to recognize a specific face and applies a user-assigned ID to that face.
# face_id: Only alpha-numeric, -, and _ are valid characters
def start_face_training(face_id):
    url = "http://" + ip_address + "/api/beta/faces/training/start"
    payload = json.dumps({"faceId": face_id})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Halts face training that is currently in progress
def cancel_face_training():
    url = "http://" + ip_address + "/api/beta/faces/training/cancel"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Directs Misty to recognize a face she sees, if it is among those she already knows
def start_face_recognition():
    url = "http://" + ip_address + "/api/beta/faces/recognition/start"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Stops the process of Misty recognizing a face she sees
def stop_face_recognition():
    url = "http://" + ip_address + "/api/beta/faces/recognition/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Obtains a list of the names of faces on which Misty has been successfully trained
def get_learned_faces():
    url = "http://" + ip_address + "/api/beta/faces"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


# Removes records of previously trained faces from Misty's memory
def clear_learned_faces():
    url = "http://" + ip_address + "/api/beta/faces/clearall"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


## Recording Audio

# Directs Misty to initiate an audio recording and save it with the specified file name
def start_recording_audio(file_name):
    url = "http://" + ip_address + "/api/beta/audio/startrecord"
    payload = json.dumps({"FileName": file_name})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Directs Misty to stop the current audio recording
def stop_recording_audio():
    url = "http://" + ip_address + "/api/beta/audio/stoprecord"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Converting audio file to text
def speech_recognition(file_name):
    r = sr.Recognizer()

    a = sr.AudioFile(file_name)
    with a as source:
        audio = r.record(source)

    try:
        print("You said: " + r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


## Alpha - Mapping & Tracking

# Obtains values representing Misty's current activity and sensor status
def slam_get_status():
    url = "http://" + ip_address + "/api/alpha/slam/status"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


# Resets the SLAM sensors
def slam_reset():
    url = "http://" + ip_address + "/api/alpha/slam/reset"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Starts Misty mapping an area
def slam_start_mapping():
    url = "http://" + ip_address + "/api/alpha/slam/map/start"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Stops Misty mapping an area
def slam_stop_mapping():
    url = "http://" + ip_address + "/api/alpha/slam/map/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Starts Misty tracking her location
def slam_start_tracking():
    url = "http://" + ip_address + "/api/alpha/slam/track/start"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Stops Misty tracking her location
def slam_stop_tracking():
    url = "http://" + ip_address + "/api/alpha/slam/track/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Obtains the current map Misty has generated
def slam_get_map():
    url = "http://" + ip_address + "/api/alpha/slam/map/smooth"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


# Drives Misty on a path defined by coordinates you specify
# path: A list containing 1 or more sets of integer pairs representing X and Y coordinates
def follow_path(path):
    url = "http://" + ip_address + "/api/alpha/drive/path"
    payload = json.dumps({"Path": path})
    response = requests.request("GET", url, data=payload, headers=headers)
    print(response.text)


def main():
    # change_led(124, 40, 20)
    # get_list_of_image()
    # change_display_image("Angry.jpg", 10)
    # get_list_of_audio_clips()
    # play_audio_clip("001-OooOooo.wav", 50)
    # delete_image_asset_from_robot("test.png")
    # save_image_to_misty("test.png")
    # save_audio_to_misty("test.mp3")
    # get_list_of_audio_clips()
    # play_audio_clip("test.mp3", 100)
    # t = """
    #
    # Welcome to ECS Building!
    #
    # """
    # convert_text_to_audio(t)
    # audio = AudioSegment.from_mp3(hashlib.md5(t).hexdigest()[:15]+".mp3")
    # play(audio)
    # save_audio_to_misty(hashlib.md5(t).hexdigest()[:15]+".mp3")
    # play_audio_clip(hashlib.md5(t).hexdigest()[:15]+".mp3", 100)
    # delete_audio_clip_from_robot(hashlib.md5(t).hexdigest()[:15]+".mp3")
    # get_available_wifi_networks()
    # get_battery_level()
    # set_head_position(5, 8)
    # play_audio_clip("test.mp3", 100)
    # time.sleep(5)
    # delete_audio_asset_from_robot("test.mp3")
    # start_recording_audio("new_record")
    # time.sleep(3)
    # stop_recording_audio()
    # get_log_file("2018-10-09")
    # get_device_info()
    # convert_mp3_to_wav(hashlib.md5(t).hexdigest()[:15], "mp3")
    # speech_recognition(hashlib.md5(t).hexdigest()[:15]+".wav")
    # get_help()
    # set_head_position(-2, 8)
    # start_face_training("Vince_Luo")
    # time.sleep(15)
    # get_learned_faces()
    # start_face_recognition()
    # time.sleep(10)
    # stop_face_recognition()
    #start_recording_audio("new record.wav")
    #time.sleep(1)
    #stop_recording_audio()
    #get_log_file()
    for t in rooms_text:
        convert_and_play_text_to_audio(t)
        time.sleep(5)


if __name__ == "__main__":
    main()



