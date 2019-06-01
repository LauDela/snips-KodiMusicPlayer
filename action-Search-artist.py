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


def searchArtist(hermes, intentMessage):
  conf = read_configuration_file(CONFIG_INI)
  artist_name = intentMessage.slots.artist.first().value
  addr_ = conf['global']['ip']
  port_ =conf['global']['port']
  user_ =conf['global']['user'] 
  password_ =conf['global']['password']
  headers = {'Content-type': 'application/json',}
  #request ="{\"jsonrpc\": \"2.0\", \"method\": \"AudioLibrary.GetArtist s\", \"params\": { \"limits\": { \"start\" : 0, \"end\": 50 }, \"properties\": [\"artist\"], \"sort\": { \"order\": \"ascending\", \"method\": \"artist\", \"ignorearticle\": true }, \"filter\": {\"field\": \"artist\", \"operator\":\"contains\",\"value\":\""+ artist_name +"\"} }, \"id\": \"libArtists\"}"
  request ="{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"audioLibrary.Getartists\", \"params\": { \"filter\": {\"field\": \"artist\", \"operator\": \"startswith\", \"value\": \""+artist_name+"\"}}}"
  url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
  kodi_url = 'http://'+user_+':'+password_+'@'+addr_+':'+port_+'/jsonrpc'
  print(url)
  response = requests.get(url)
  json_data = simplejson.loads(response.text)
  #album = json_data['result']['albums'][0]['title'] 
  artist = json_data['result']['artists'][0]['artist']
  label = json_data['result']['artists'][0]['label']
  artistid = json_data['result']['artists'][0]['artistid']  
  print("Retour:"+artist)
  result_sentence ="J'ai trouvé l'artiste ou groupe {}. Voici quelques titres.".format(str(label))
  current_session_id = intentMessage.session_id
  print(result_sentence)
  

  
  data = '{"id":"160","jsonrpc":"2.0","method":"Playlist.Clear","params":{"playlistid":1}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
  data='{"jsonrpc": "2.0", "id": 1, "method": "Playlist.Add", "params": {"playlistid": 1, "item": { "artistid":'+str(artistid)+'}}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
    
  data='{"jsonrpc": "2.0", "id": 1,"method": "Player.Open", "params": {"item": {"playlistid": 1},"playerid":0}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
  data='{"jsonrpc": "2.0", "id": 1,"method": "Player.Open", "params": {"item": {"position":0,"playlistid": 1}}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
  data='{"jsonrpc":"2.0","method":"Player.SetShuffle","params":{"playerid":1,"shuffle":true},"id":1}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
    
  data='{"jsonrpc": "2.0", "id": 1,"method": "GUI.ShowNotification", "params": {"title": "TEST", "message":"Lancement de la playliste"}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
  
  #result_sentence = "c'est parti"
  
  hermes.publish_end_session(current_session_id, "c'est partit")

def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:Search-artist", searchArtist) \
         .start()
