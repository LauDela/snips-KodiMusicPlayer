#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import time
import simplejson
import requests

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


def searchAlbum(hermes, intentMessage):
  conf = read_configuration_file(CONFIG_INI)
  album_name = intentMessage.slots.album_name.first().value
  addr_ = conf['global']['ip']
  port_ =conf['global']['port']
  user_ =conf['global']['user'] 
  password_ =conf['global']['password']
  request ="{\"jsonrpc\": \"2.0\", \"method\": \"AudioLibrary.GetAlbums\", \"params\": { \"limits\": { \"start\" : 0, \"end\": 50 }, \"properties\": [\"artist\", \"year\", \"title\"], \"sort\": { \"order\": \"ascending\", \"method\": \"album\", \"ignorearticle\": true }, \"filter\": {\"field\": \"album\", \"operator\":\"contains\",\"value\":\""+ album_name +"\"} }, \"id\": \"libAlbums\"}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  print(url)
  response = requests.get(url)
  print("OK2")
  json_data = simplejson.loads(response.text)
  print("OK3")
  album = json_data['result']['albums'][0]['title'] 
  artist = json_data['result']['albums'][0]['artist']
  anee = json_data['result']['albums'][0]['year']  
  print("Retour:"+album)
  result_sentence ="L'album est {} de {} sorti en {}.".format(str(album),str(artist),str(annee))
  print(result_sentence)
  snips_speak(hermes, intentMessage,result_sentence)

def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:Search-album", searchAlbum) \
         .start()
