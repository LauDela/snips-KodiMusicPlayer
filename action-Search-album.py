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
  annee = json_data['result']['albums'][0]['year']
  albumid = json_data['result']['albums'][0]['albumid']  
  print("Retour:"+album)
  result_sentence ="L'album est {} de {} sorti en {} et son identifiant est {}.".format(str(album),str(artist),str(annee),str(albumid))
  print(result_sentence)
  request ="{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"Playlist.Clear\", \"params\": {\"playlistid\": 1}}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  print("Creation de la playlist " + url)
  response = requests.get(url)
  print("Retour = " + str(response.status_code), str(response.reason))
  #print("Retour=" + str(response))
  request ="{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"Playlist.Add\", \"params\": {\"playlistid\": 1, \"item\": { \"albumid\":"+str(albumid)+"}}}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  print("Ajout a la playlist " + url)
  response = requests.get(url)
  print("Retour=" + str(response))
  request ="{\"jsonrpc\": \"2.0\", \"id\": 1,\"method\": \"Player.Open\", \"params\": {\"item\": {\"playlistid\": 1}}}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  print("lecture de la playlist " + url)
  response = requests.get(url)
  print("Retour=" + str(response))
  request ="{\"jsonrpc\": \"2.0\", \"id\": 1,\"method\": \"GUI.ShowNotification\", \"params\": {\"title\": \"TEST\", \"message\":\"Lancement de la playliste\"}}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  print("POPUP " + url)
  response = requests.post(url)
  print("Retour=" + str(response))
  
  result_sentence = "c'est parti"
  current_session_id = intentMessage.session_id
  hermes.publish_end_session(current_session_id, "c'est partit")
#  snips_speak(hermes, intentMessage,result_sentence)

def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:Search-album", searchAlbum) \
         .start()
