#!/usr/bin/env python3
import configparser
import random
import uuid

import paho.mqtt.client as mqtt
import json
from os import listdir
from os.path import isfile, join
from hermes_python.hermes import Hermes

sound_files = [f for f in listdir("sounds") if isfile(join("sounds", f))]
config = configparser.ConfigParser()
config.read("config.ini")

mqtt_host = config["secret"]["mqtt_host"]
mqtt_port = config["secret"].getint("mqtt_port")
site_id = config["secret"]["site_id"]


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hermes/intent/LauDela:Play")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("TEST 1")
    if msg.topic == "hermes/intent/LauDela:Play":
        payload = msg.payload
        print("playing some good stuff")
        with open("/home/pi/music/Hotel California.mp3", "rb") as sound_file:
            imagestring = sound_file.read()
            byte_array = bytearray(imagestring)
            generated_id = uuid.uuid4().hex
            client.publish("hermes/audioServer/" + site_id + "/playBytes/" + generated_id, byte_array)
            client.publish("hermes/dialogueManager/endSession", json.dumps({"sessionId": payload["sessionId"]}))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_host, mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()