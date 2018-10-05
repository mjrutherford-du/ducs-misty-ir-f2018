#!/usr/bin/python
# -*- coding: utf-8 -*-

# mistyFuncLib.py
# author: Vince Luo
# Sep. 29, 2018


import json
import requests
from gtts import gTTS
import hashlib


def change_led(ip_address, r, g, b):
    if r not in range(256):
        raise Exception("The red value need to be in 0-255 range")
    if g not in range(256):
        raise Exception("The green value need to be in 0-255 range")
    if b not in range(256):
        raise Exception("The blue value need to be in 0-255 range")
    url = "http://" + ip_address + "/api/led/change"
    payload = json.dumps({"red": r, "green": g, "blue": b})
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def get_list_of_image(ip_address):
    image_list = []
    url = "http://" + ip_address + "/api/images"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers)
    for i in response.json():
        for j in i["result"]:
            image_list.append(j["name"])
    print(response.text)
    print(image_list)
    return image_list


def change_display_image(ip_address, file_name, time_out):
    if file_name not in get_list_of_image(ip_address):
        raise Exception(file_name,"not found on the robot")
    else:
        url = "http://" + ip_address + "/api/images/change"
        payload = json.dumps(
            {"FileName": file_name, "TimeOutSeconds": time_out, "Alpha": 1})
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)


def save_image_to_misty(image_name, ip_address):
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
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def delete_image_asset_from_robot(image_name, ip_address):
    url = "http://" + ip_address + "/api/images/delete"
    payload = json.dumps({"FileName": image_name})
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def get_list_of_audio_clips(ip_address):
    audio_list = []
    url = "http://" + ip_address + "/api/audio/clips"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers)
    for i in response.json():
        for j in i["result"]:
            audio_list.append(j["name"])
    # print(response.text)
    print(audio_list)
    return audio_list


def play_audio_clip(file_name, volume, ip_address):
    if file_name not in get_list_of_audio_clips(ip_address):
        raise Exception(file_name,"not found on the robot")
    elif volume not in range(101):
        raise Exception("Invalid volume value")
    else:
        url = "http://" + ip_address + "/api/audio/play"
        payload = json.dumps(
            {"AssetId": file_name, "Volume": volume})
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)


def save_audio_to_misty(audio_name, ip_address):
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
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


# Still have problem in this delete function
def delete_audio_clip_from_robot(audio_name, ip_address):
    url = "http://" + ip_address + "/api/audio/delete"
    payload = json.dumps({"FileName": audio_name})
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def convert_text_to_audio(text):
    tts = gTTS(text=text, lang='en')
    tts.save(hashlib.md5(text).hexdigest()[:15]+".mp3")


if __name__ == "__main__":
    ipAddress = "192.168.1.5"
    # change_led(ipAddress, 124, 40, 20)
    # get_list_of_image(ipAddress)
    # change_display_image(ipAddress, "Angry.jpg", 10)
    # get_list_of_audio_clips(ipAddress)
    # play_audio_clip(ipAddress, "001-OooOooo.wav", 50)
    # delete_image_asset_from_robot("test.png", ipAddress)
    # save_image_to_misty("test.png", ipAddress)
    # save_audio_to_misty("test.mp3", ipAddress)
    # get_list_of_audio_clips(ipAddress)
    # play_audio_clip("test.mp3", 100, ipAddress)
    # delete_audio_clip_from_robot("test.mp3", ipAddress)
    # t = "Welcome to University of Denver"
    # convert_text_to_audio(t)
    # save_audio_to_misty(hashlib.md5(t).hexdigest()[:15]+".mp3", ipAddress)
    # play_audio_clip(hashlib.md5(t).hexdigest()[:15]+".mp3", 100, ipAddress)
    # delete_audio_clip_from_robot(hashlib.md5(t).hexdigest()[:15]+".mp3", ipAddress)
