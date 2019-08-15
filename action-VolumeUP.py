#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import time
import simplejson
import requests
import json
import soco

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


def volumeUP(hermes, intentMessage):
  current_session_id = intentMessage.session_id
  zone = soco.SoCo('192.168.10.4') 
  vol = float(zone.volume)+ float(10)  
  zone.volume = float(vol)
  hermes.publish_end_session(current_session_id,"OK")

def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:VolumeUP", volumeUP) \
         .start()
