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


def NowPlaying(hermes, intentMessage):
  conf = read_configuration_file(CONFIG_INI)
  current_session_id = intentMessage.session_id
  addr_ = conf['global']['ip']
  port_ =conf['global']['port']
  user_ =conf['global']['user'] 
  password_ =conf['global']['password']
  headers = {'Content-type': 'application/json',}
  kodi_url = 'http://'+user_+':'+password_+'@'+addr_+':'+port_+'/jsonrpc'
  
  
  request ="{\"jsonrpc\": \"2.0\", \"method\": \"Player.GetItem\", \"params\": { \"properties\": [\"title\", \"album\", \"artist\"], \"playerid\": 1 }, \"id\": \"AudioGetItem\"}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  response = requests.get(url)
  print(url)
  json_data = simplejson.loads(response.text)
  album = json_data['result']['item'][0]['album'] 
  artist = json_data['result']['item'][0]['artist']
  label = json_data['result']['item'][0]['label']
  
  result_sentence ="C'est l'album {} de {} et le titre est {}.".format(str(album),str(artist),str(label))
     
  data='{"jsonrpc": "2.0", "id": 1,"method": "GUI.ShowNotification", "params": {"title": "Lecture", "message":"information"}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  

  
  hermes.publish_end_session(current_session_id, result_sentence)

def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:NowPlaying", NowPlaying) \
         .start()
