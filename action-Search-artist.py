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
  #print(url)
  try:
    response = requests.get(url)
    json_data = simplejson.loads(response.text)
    artist = json_data['result']['artists'][0]['artist']
    label = json_data['result']['artists'][0]['label']
    artistid = json_data['result']['artists'][0]['artistid']  
    #hermes.publish_continue_session(current_session_id,"La liste de lecture est en préparation. Veuillez patienter...",["LauDela:Search-artist"])
    hermes.publish_end_session(current_session_id, "Liste terminée")
    action_genereliste(hermes, intentMessage,artistid,conf)
    result_sentence ="J'ai trouvé l'artiste ou groupe {}. Voici quelques titres.".format(str(label))
    print(result_sentence)
    #hermes.publish_end_session(current_session_id, "Liste terminée")
  except:
    hermes.publish_end_session(current_session_id, "Désolé je n'ai rien trouvé, peux tu reformuler ta demande ?")

def action_genereliste(hermes, intentMessage,artistid,conf):
  addr_ = conf['global']['ip']
  port_ =conf['global']['port']
  user_ =conf['global']['user'] 
  password_ =conf['global']['password']
  headers = {'Content-type': 'application/json',}
  kodi_url = 'http://'+user_+':'+password_+'@'+addr_+':'+port_+'/jsonrpc'
  current_session_id = intentMessage.session_id
  zone = soco.SoCo('192.168.10.4')  
  zone.clear_queue()
  zone.stop()
  #hermes.publish_continue_session(current_session_id,"La liste de lecture est en préparation. Veuillez patienter...",["LauDela:Search-artist"])
  data = '{"id":"160","jsonrpc":"2.0","method":"Playlist.Clear","params":{"playlistid":1}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
  data='{"jsonrpc": "2.0", "id": 1, "method": "Playlist.Add", "params": {"playlistid": 1, "item": { "artistid":'+str(artistid)+'}}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = json.loads(json_obj)
  
  data='{"jsonrpc": "2.0", "id": 1, "method": "Playlist.GetItems", "params": {"playlistid": 1}}'
  response = requests.post(kodi_url, headers=headers, data=data)
  json_obj= response.text
  json_data = simplejson.loads(response.text)
  #hermes.publish_end_session(current_session_id, "LA liste de lecture est en préparation. Veuillez patienter...")
  
  for song in json_data['result']['items']:
    songId = song['id']
    data='{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetSongDetails", "params": {"songid": '+str(songId)+', "properties": ["title", "album", "artist","file"]}}'
    response = requests.post(kodi_url, headers=headers, data=data)
    json_obj0= response.text
    json_data0 = json.loads(json_obj0)
    chemin = json_data0['result']['songdetails']['file']
    chemin = chemin.replace("smb","x-file-cifs")
    chemin = requote_uri(chemin)
    print(chemin)
    zone.add_uri_to_queue(uri=chemin)
    
  print("fin boucle")
  #hermes.publish_continue_session(current_session_id,"La liste de lecture est terminée.",["LauDela:Search-artist"])
  zone.play_from_queue(index=0)
  zone.play_mode = 'SHUFFLE'
  




def snips_speak(hermes, intentMessage,sentence):
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, sentence)    

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:Search-artist", searchArtist) \
         .start()
