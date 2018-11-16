#!/usr/bin/python
# -*- coding: utf-8 -*-

# mistyFuncLib.py
# author: Vince Luo
# Sep. 29, 2018


import requests
import cv2
import pyqrcode
import json
import re
import base64
import time
import imageio
import os
from gtts import gTTS
import speech_recognition as sr
import pyzbar.pyzbar as pyzbar
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from aip import AipOcr


# Config for misty
ip_address = "192.168.1.5"
headers = {'Content-Type': "application/json",
           'Cache-Control': "no-cache"}

# Config for the Baidu OCR API
config = {
    'appId': '',
    'apiKey': '',
    'secretKey': ''
}
client = AipOcr(**config)


## Image Part

# Obtains a list of the images currently stored on Misty.
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


# Displays an image on Misty's screen.
def change_display_image(file_name, time_out):
    if file_name not in get_list_of_image():
        raise Exception(file_name, "not found on the robot")
    else:
        url = "http://" + ip_address + "/api/images/change"
        payload = json.dumps(
            {"FileName": file_name, "TimeOutSeconds": time_out, "Alpha": 1})
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)


# Saves an image file to Misty. Valid image file types are .jpg, .jpeg, .gif, .png. Maximum file size is 3 MB.
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
                          "ImmediatelyApply": False, "OverwriteExisting": True})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Enables you to remove an image file from Misty that you have previously uploaded.
def delete_image_asset_from_robot(image_name):
    url = "http://" + ip_address + "/api/images/delete"
    payload = json.dumps({"FileName": image_name})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Force-clears an error message from Misty’s display.
def clear_display_text():
    url = "http://" + ip_address + "/api/beta/text/clear"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Obtains a system or user-uploaded image file currently stored on Misty
def get_image(file_name, need_base64=False):
    url = "http://" + ip_address + "/api/alpha/image?FileName="+file_name+"&Base64="+str(need_base64)
    response = requests.request("GET", url, headers=headers)
    if need_base64 is True:
        image_info = json.loads(response.text)[0]['result']
        base64_str = image_info['base64']
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        img.save(file_name)
    else:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    print("Done")


# Takes a photo with Misty's 4K camera.
def take_picture(file_name=None, need_base64=False):
    url = "http://" + ip_address + "/api/alpha/camera?&Base64=" + str(need_base64)
    response = requests.request("GET", url, headers=headers)
    if need_base64 is True:
        image_info = json.loads(response.text)[0]['result']
        if file_name is None:
            file_name = image_info['name'] + ".jpg"
        base64_str = image_info['base64']
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        img.save(file_name)
    else:
        if file_name is None:
            ext = response.headers['content-type'][-3:]
            file_name = "cameraPic."+ext
        with open(file_name, 'wb') as f:
            f.write(response.content)
    print("Done")


# Takes a photo using Misty’s Occipital Structure Core depth sensor.
def slam_get_visible_image(file_name=None, need_base64=True):
    url = "http://" + ip_address + "/api/alpha/slam/visibleimage?&Base64=" + str(need_base64)
    response = requests.request("GET", url, headers=headers)
    if need_base64 is True:
        image_info = json.loads(response.text)[0]['result']
        if file_name is None:
            file_name = image_info['name'] + ".jpg"
        base64_str = image_info['base64']
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        img.save(file_name)
    else:
        if file_name is None:
            ext = response.headers['content-type'][-3:]
            file_name = "visibaleImg."+ext
        with open(file_name, 'wb') as f:
            f.write(response.content)
    print("Done")


# Provides the current distance of objects from Misty’s Occipital Structure Core depth sensor.
def slam_get_depth_image():
    url = "http://" + ip_address + "/api/alpha/slam/depthimage"
    response = requests.request("GET", url, headers=headers)
    print(response.text)

# Opens the data stream from the Occipital Structure Core depth sensor, 
# so you can obtain image and depth data when Misty is not actively tracking or mapping.
def slam_start_streaming():
    url = "http://" + ip_address + "/api/alpha/slam/streaming/start"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Closes the data stream from the Occipital Structure Core depth sensor.
def slam_stop_streaming():
    url = "http://" + ip_address + "/api/alpha/slam/streaming/stop"
    response = requests.request("POST", url, headers=headers)
    print(response.text)


# Save a planty of images to the gif file
def save_images_to_gif(startwith="VisibleImage"):
    images = []
    file_names = sorted((fn for fn in os.listdir('.') if fn.startswith(startwith)))
    for filename in file_names:
        images.append(imageio.imread(filename))
    imageio.mimsave(startwith+'.gif', images, duration=0.3)
    print("Done")


# Decode the QRcode
# To use this function, you need to install "zbar" first: brew install zbar
# And then: pip install pyzbar, opencv-python
def decode_qrcode(file_name):
    im = cv2.imread(file_name)
    decoded_objects = pyzbar.decode(im)
    info = ""
    if decoded_objects != []:
        for obj in decoded_objects:
            info = str(obj.data)[2:-1]
            print(info)
    else:
        print("Didn't find QRcode from the image. Please try again.")

    return info


# Generate a QRcode
# To use this function, you need to install: pip install pyqrcode, pypng
def generate_qrcode(content, file_name, scale=10):
    qr_code = pyqrcode.create(content)
    qr_code.png(file_name, scale=scale)
    print("Done")


# Detect a face from a image
def detect_face(file_name):
    # Create the haar cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Read the image
    image = cv2.imread(file_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) != 0:
        print("Hello Human!")
        print("Found {0} faces!".format(len(faces)))
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Faces found", image)
        cv2.waitKey(0)
    else:
        print("Nothing")


# Draw the text contains one word into the image and save it to the misty
def draw_your_name(name):
    img = Image.new('RGB', (480, 272), color='black')
    fnt = ImageFont.truetype("/Library/Fonts/Phosphate.ttc", size=40)
    d = ImageDraw.Draw(img)
    d.text((170, 110), name, font=fnt, align="center", fill='white')
    img.save('name.png')
    time.sleep(1.5)
    save_image_to_misty('name.png')


# Draw the command contains multiple lines into the image and save it to the misty
def draw_your_command(text, color='white'):
    img = Image.new('RGB', (480, 272), color='black')
    fnt = ImageFont.truetype("/Library/Fonts/Phosphate.ttc", size=40)
    d = ImageDraw.Draw(img)
    d.multiline_text((0, 0), text, font=fnt, align="center", fill=color, spacing=2)
    img.save('command.png')
    time.sleep(1.5)
    save_image_to_misty('command.png')


# Draw the text contains multiple lines into the image and save it to the misty
def draw_multi_lines(text, file_name):
    img = Image.new('RGB', (480, 272), color='black')
    fnt = ImageFont.truetype("/Library/Fonts/Phosphate.ttc", size=35)
    d = ImageDraw.Draw(img)
    d.multiline_text((0, 0), text, font=fnt, align="center", fill='white', spacing=2)
    img.save(file_name)
    time.sleep(1.5)
    save_image_to_misty(file_name)


# Using the Baidu OCR API to get text from the image
def detect_word(file_name):
    with open(file_name, 'rb') as fp:
        image = fp.read()
    result = client.basicGeneral(image)
    if 'words_result' in result:
        words = '\n'.join([w['words'] for w in result['words_result']])
        if words != "":
            print('Detected: '+words)
            return words
        else:
            print('Nothing Detected!')
            return None
    else:
        print('Nothing Detected!')
        return None


# Resize the image to a small version
def resize_image(file_name, basewidth=500):
    img = Image.open(file_name)
    wpersent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpersent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save('resized_'+file_name)
    print("Resized Done")


## Audio Part

# Lists the default system audio files currently stored on Misty.
def get_list_of_audio_clips():
    audio_list = []
    url = "http://" + ip_address + "/api/audio/clips"
    response = requests.request("GET", url, headers=headers)
    for i in response.json():
        for j in i["result"]:
            audio_list.append(j["name"])
    print(audio_list)
    return audio_list


# Lists all audio files (default system files 
# and user-uploaded files) currently stored on Misty.
def get_list_of_audio_files():
    url = "http://" + ip_address + "/api/audio"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


# Plays an audio file that has been previously uploaded to Misty.
def play_audio_clip(file_name, volume=100):
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


# Saves an audio file to Misty. Maximum size is 3 MB.
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


# Convert text to audio
def convert_text_to_audio(text, file_name):
    tts = gTTS(text=text, lang='en')
    tts.save(file_name)


# Convert mp3 to wav for detecting
def convert_mp3_to_wav(file_name, extension):
    song = AudioSegment.from_mp3(file_name+"."+extension)
    song.export(file_name+".wav", format="wav")
    print("Successfully Converted: "+file_name+"."+extension+" to "+file_name+".wav")


# Sets the default loudness of Misty's speakers for audio playback
def set_default_volume(volume):
    url = "http://" + ip_address + "/api/alpha/audio/volume"
    payload = json.dumps({"Volume": volume})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Obtains a system or user-uploaded audio file currently stored on Misty.
def get_audio_file(file_name):
    url = "http://" + ip_address + "/api/alpha/audio/file?FileName="+file_name
    response = requests.request("GET", url, headers=headers)
    with open(file_name, 'wb') as f:
        f.write(response.content)


# Directs Misty to initiate an audio recording and save it with the specified file name
def start_recording_audio(file_name):
    url = "http://" + ip_address + "/api/beta/audio/startrecord"
    payload = json.dumps({"FileName": file_name+".wav"})
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

    return r.recognize_google(audio)


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


## Configuration Part

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


# Connects Misty to a specified WiFi source
def set_wifi_connection(network_name, password):
    url = "http://" + ip_address + "/api/wifi"
    payload = json.dumps({"NetworkName": network_name,
                          "Password": password})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


## Head Movement

# Moves Misty's head in one of three axes (tilt, turn, or up-down). 
# Note: For Misty I, the MoveHead command can only control the up-down movement of Misty's head.
def move_head(pitch, velocity=6):
    url = "http://" + ip_address + "/api/beta/head/move"
    payload = json.dumps({ "Pitch": pitch, "Roll": 0, "Yaw": 0, "Velocity": velocity})
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


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
def slam_get_raw_map():
    url = "http://" + ip_address + "/api/alpha/slam/map/raw"
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)[0]


# Drives Misty on a path defined by coordinates you specify
# path: A list containing 1 or more sets of integer pairs representing X and Y coordinates
def follow_path(path):
    url = "http://" + ip_address + "/api/alpha/drive/path"
    payload = json.dumps({"Path": path})
    response = requests.request("GET", url, data=payload, headers=headers)
    print(response.text)


## Features what misty can do for the human-robot interaction:

# Give misty your name, then misty will display your name and repeat it for you
def say_your_name():
    file_name = "SayYourName"
    if (file_name+'.png') not in get_list_of_image():
        t = """

            Hi there!
            Say your name please. 
            Ready, 3, 2, 1

            """
        draw_multi_lines(t, file_name)
        if (file_name+'.mp3') not in get_list_of_audio_clips():
            convert_text_to_audio(t, file_name + ".mp3")
            time.sleep(1.5)
            save_audio_to_misty(file_name + ".mp3")
            time.sleep(1.5)
    change_display_image(file_name+'.png', 5)
    play_audio_clip(file_name+".mp3")
    time.sleep(4.5)
    start_recording_audio("name")
    time.sleep(3)
    stop_recording_audio()
    time.sleep(1.5)
    get_audio_file("name.wav")
    time.sleep(1.5)
    name = speech_recognition("name.wav")
    t = "Your name is " + name
    convert_text_to_audio(t, "SayYourNameBack.mp3")
    draw_your_name(name)
    time.sleep(1.5)
    save_audio_to_misty("SayYourNameBack.mp3")
    time.sleep(1.5)
    play_audio_clip("SayYourNameBack.mp3")
    change_display_image('name.png', 3)

    os.remove(file_name + ".png")
    os.remove(file_name + ".mp3")
    os.remove("name.wav")
    os.remove("SayYourNameBack.mp3")
    os.remove("name.png")
    delete_audio_asset_from_robot("name.wav")
    delete_audio_asset_from_robot("SayYourNameBack.mp3")
    delete_image_asset_from_robot("name.png")
    print("Done")


# Show a paper of a word to misty, it will detect the word and display the word out
def give_me_command():
    file_name = 'showYourCommand.png'
    wanna_delete = False
    if file_name not in get_list_of_image():
        t = """

            Please show your
            command to 
            my eyes^_^

            """
        draw_multi_lines(t, file_name)
        time.sleep(0.5)
        wanna_delete = True
    change_display_image(file_name, 4)
    time.sleep(2)
    slam_start_streaming()
    slam_get_visible_image("takeVisPicCom.png")
    time.sleep(0.5)
    slam_stop_streaming()
    word = detect_word("takeVisPicCom.png")
    if word is not None:
        t = f"""
        
            Your command is:
            {word}
            
            """
        draw_your_command(t)
        command = True
    else:
        t = """
        
            ?_?
            I don\'t understand.
            Please try again!
            
            """
        draw_your_command(t, color='red')
        command = False
    change_display_image('command.png', 2)
    time.sleep(0.5)
    if wanna_delete:
        os.remove("showYourCommand.png")
    os.remove("command.png")
    # os.remove("takeVisPicCom.png")
    delete_image_asset_from_robot("command.png")
    print("Done")
    return command, word


# Recoding the motion graph while driving the misty
def drive_and_record_to_gif(speed=40, file_name="testImg", frame=20):
    drive(speed, -30)
    time.sleep(0.5)
    slam_start_streaming()
    for i in range(frame):
        if i < 9:
            slam_get_visible_image(file_name + "0" + str(i + 1) + ".png")
        else:
            slam_get_visible_image(file_name + str(i + 1) + ".png")
        time.sleep(0.1)
    slam_stop_streaming()
    time.sleep(0.5)
    stop()
    save_images_to_gif(file_name)


# Detect words from the image
def detect_words(file_name):
    is_detect = True
    slam_start_streaming()
    while is_detect:
        slam_get_visible_image(file_name)
        time.sleep(0.3)
        words = detect_word(file_name)
        if words == 'No':
            is_detect = False
        else:
            is_detect = True
    slam_stop_streaming()


# Demo for starting introduce the tour
def demo():
    audio_file1 = AudioSegment.from_mp3("introduction.mp3")
    audio_file2 = AudioSegment.from_mp3("letsgo.mp3")
    audio_file3 = AudioSegment.from_mp3("sorry.mp3")
    audio_file4 = AudioSegment.from_mp3("alright.mp3")
    play(audio_file1)
    loop = True
    while loop:
        command, word = give_me_command()
        if command is True:
            if word == 'Yes':
                play(audio_file2)
            elif word == 'No':
                play(audio_file4)
            loop = False
        else:
            play(audio_file3)

