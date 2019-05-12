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

    addon_name = conf['global']['favorite_addon1'] 
    movie_name = intentMessage.slots.movie_name.first().value
    addr_ = conf['global']['ip']
    port_ =conf['global']['port']

    def openAddon():
        request = "{\"jsonrpc\": \"2.0\", \"method\": \"Addons.ExecuteAddon\", \"params\": { \"addonid\": \"plugin.video." + addon_name + "\", \"params\":{\"action\":\"alert\"}}, \"id\": \"1\"}"
        url = "http://" + addr_ + ":" + port_ + "/jsonrpc?request=" + request
        response = requests.get(url)
        json_data = simplejson.loads(response.text)
        

    def searchMovie():
        print("o")
        request = "{\"jsonrpc\": \"2.0\", \"method\": \"Files.GetDirectory\", \"params\": { \"directory\": \"plugin://plugin.video.exodus/?action=movieSearchterm%26name=" + movie_name + "\"}, \"id\": 1 }"
        url = "http://" + addr_ + ":" + port_ + "/jsonrpc?request=" + request
        response = requests.get(url)
        json_data = simplejson.loads(response.text)

    try:           
        openAddon()
        time.sleep(3)
        searchMovie()
        hermes.publish_end_session(intentMessage.session_id, "")
    except requests.exceptions.RequestException:
        hermes.publish_end_session(intentMessage.session_id, "Erreur de connection.")
    except Exception:
        hermes.publish_end_session(intentMessage.session_id, "Erreur de l'application.")





if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("Ianou:Search-movie", subscribe_intent_callback) \
         .start()