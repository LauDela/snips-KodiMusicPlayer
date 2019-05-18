#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import time
import simplejson
import requests

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
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

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):

    current_session_id = intentMessage.session_id
    album_name = intentMessage.slots.album_name.first().value
    addr_ = conf['global']['ip']
    port_ =conf['global']['port']
    user_ =conf['global']['user'] 
    password_ =conf['global']['password'] 
   

    def searchAlbum():
        #print("o")
        #request = "{\"jsonrpc\": \"2.0\", \"method\": \"Files.GetDirectory\", \"params\": { \"directory\": \"plugin://plugin.video.exodus/?action=movieSearchterm%26name=" + movie_name + "\"}, \"id\": 1 }"
        request ="{\"jsonrpc\": \"2.0\", \"method\": \"AudioLibrary.GetAlbums\", \"params\": { \"limits\": { \"start\" : 0, \"end\": 50 }, \"properties\": [\"artist\", \"year\", \"title\"], \"sort\": { \"order\": \"ascending\", \"method\": \"album\", \"ignorearticle\": true }, \"filter\": {\"field\": \"album\", \"operator\":\"contains\",\"value\":\""+ album_name +"\"} }, \"id\": \"libAlbums\"}"
        url = "http://" +user_+":"+password_+"@"+ addr_ + ":" + port_ + "/jsonrpc?request=" + request
        print(url)
        response = requests.get(url)
        print("OK2")
        json_data = simplejson.loads(response.text)
        print("OK3")
        album = json_data['result']['albums'][0]['title'] 
        print("Retour:"+album)
        #hermes.publish_end_session(current_session_id, "Album trouvé "+album)

    try:           
        #openAddon()
        #time.sleep(3)
        searchAlbum()
        hermes.publish_end_session(intentMessage.session_id, "Album trouvé "+album)
    except requests.exceptions.RequestException:
        hermes.publish_end_session(intentMessage.session_id, "Erreur de connection.")
    except Exception:
        hermes.publish_end_session(intentMessage.session_id, "Erreur de l'application.")





if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("LauDela:Search-album", subscribe_intent_callback) \
         .start()
