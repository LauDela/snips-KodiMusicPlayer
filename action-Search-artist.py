#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes    
from hermes_python.ontology import *
from requests.utils import requote_uri
import configparser
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


def searchArtist(hermes, intentMessage):
  conf = read_configuration_file(CONFIG_INI)
  artist_name = intentMessage.slots.artist.first().value
  addr_ = conf['global']['ip']
  port_ =conf['global']['port']
  user_ =conf['global']['user'] 
  password_ =conf['global']['password']
  headers = {'Content-type': 'application/json',}
  current_session_id = intentMessage.session_id
  
  request ="{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"audioLibrary.Getartists\", \"params\": { \"filter\": {\"field\": \"artist\", \"operator\": \"startswith\", \"value\": \""+artist_name+"\"}}}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  kodi_url = 'http://'+user_+':'+password_+'@'+addr_+':'+port_+'/jsonrpc'
  try:
    response = requests.get(url)
    json_data = simplejson.loads(response.text)
    artist = json_data['result']['artists'][0]['artist']
    label = json_data['result']['artists'][0]['label']
    artistid = json_data['result']['artists'][0]['artistid']  
    try:
      requests.get("http://192.168.10.89/sonos.php?params="+str(artistid),timeout=2)
    except requests.exceptions.ReadTimeout: #this confirms you that the request has reached server
      retour = "C'est partit pour du "+ str(label)
      hermes.publish_end_session(current_session_id, str(retour))
    except:
      hermes.publish_end_session(current_session_id, "Oups problème")
  except:
    hermes.publish_end_session(current_session_id, "Désolé je n'ai rien trouvé, peux tu reformuler ta demande ?")

  
def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:Search-artist", searchArtist) \
         .start()
