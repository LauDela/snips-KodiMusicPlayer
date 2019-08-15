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


def searchAlbum(hermes, intentMessage):
  conf = read_configuration_file(CONFIG_INI)
  current_session_id = intentMessage.session_id
  album_name = intentMessage.slots.album_name.first().value
  artist_name = intentMessage.slots.artiste.first().value
  addr_ = conf['global']['ip']
  port_ =conf['global']['port']
  user_ =conf['global']['user'] 
  password_ =conf['global']['password']
  headers = {'Content-type': 'application/json',}
  if artist_name :
    request ="{\"jsonrpc\": \"2.0\", \"method\": \"AudioLibrary.GetAlbums\", \"params\": { \"limits\": { \"start\" : 0, \"end\": 50 }, \"properties\": [\"artist\", \"year\", \"title\"], \"sort\": { \"order\": \"ascending\", \"method\": \"album\", \"ignorearticle\": true }, \"filter\": {\"and\":[{\"field\": \"album\", \"operator\":\"contains\",\"value\":\""+ album_name +"\"},{\"field\": \"artist\", \"operator\":\"contains\",\"value\":\""+ artist_name +"\"}] }, \"id\": \"libAlbums\"}"
  else:
    request ="{\"jsonrpc\": \"2.0\", \"method\": \"AudioLibrary.GetAlbums\", \"params\": { \"limits\": { \"start\" : 0, \"end\": 50 }, \"properties\": [\"artist\", \"year\", \"title\"], \"sort\": { \"order\": \"ascending\", \"method\": \"album\", \"ignorearticle\": true }, \"filter\": {\"field\": \"album\", \"operator\":\"contains\",\"value\":\""+ album_name +"\"} }, \"id\": \"libAlbums\"}"
  
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  kodi_url = 'http://'+user_+':'+password_+'@'+addr_+':'+port_+'/jsonrpc'
  
  try:
    response = requests.get(url)
    json_data = simplejson.loads(response.text)
    artist = json_data['result']['albums'][0]['artist']
    titre = json_data['result']['albums'][0]['title']
    albumid = json_data['result']['albums'][0]['albumid']
    annee = json_data['result']['albums'][0]['year']
    try:
      requests.get("http://192.168.10.89/sonos.php?album="+str(albumid),timeout=2)
    except requests.exceptions.ReadTimeout: #this confirms you that the request has reached server
      retour = "Veuillez patienter, je recherche l'album "+str(titre)+" de "+str(artist)
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
        h.subscribe_intent("LauDela:Search-album", searchAlbum) \
         .start()
