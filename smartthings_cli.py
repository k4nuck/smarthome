#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" SmartThings CLI

Copyright 2015 Richard L. Lynch <rich@richlynch.com>

Description: Control SmartThings devices from the command line.

Dependencies: twisted, requests, future

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from future.standard_library import install_aliases
install_aliases()

import argparse
import logging
import requests
import json
import os
import sys
from urllib.parse import urlencode
import socket
from twisted.web import server, resource
from twisted.internet import reactor

'''
' Interface for Smartthings 
' Example of input and output
' #Switches - smartthings_cli.py vvvv
'			req = smartthings.smart_request(["query","switch","all"])
'			
'			for device in req:
'				print "---------------------"
'				print "Type:"+device["type"]
'				print "Name:"+device["name"]
'				print "State:"+str(device["state"])
''' 
class SmartThings:
	def __init__(self):
		logging.getLogger("requests").setLevel(logging.WARNING)
		logging.getLogger("urllib3").setLevel(logging.WARNING)
		
		#Load Config
		self.config=load_config()
		
	def smart_request(self, cmd_list):
		# Config from Init
		config = self.config
		
		client_id = None
		if 'client_id' in config:
			client_id = config['client_id']

		if not client_id:
			logging.error('client_id missing from config!')
			return None

		client_secret = None
		if 'client_secret' in config:
			client_secret = config['client_secret']

		if not client_secret:
			logging.error('client_secret missing from config!')
			return None

		access_token = None
		if 'access_token' in config:
			access_token = config['access_token']

		endpoint_base_url = None
		if 'endpoint_base_url' in config:
			endpoint_base_url = config['endpoint_base_url']

		endpoint_url = None
		if 'endpoint_url' in config:
			endpoint_url = config['endpoint_url']

		if not access_token:
			logging.error('access_token missing from config!')
			return None

		# Query Smartthings Server
		if not endpoint_url or not endpoint_base_url:
			endpoint_base_url, endpoint_url = get_endpoint_url(access_token)
			config['endpoint_base_url'] = endpoint_base_url
			config['endpoint_url'] = endpoint_url

		dev_lists = {}

		valid_device_types = [
			'switch',
			'motion',
			'temperature',
			'humidity',
			'contact',
			'acceleration',
			'presence',
			'battery',
			'threeAxis'
		]

		while len(cmd_list):
			cmd = cmd_list.pop(0)

			if cmd == 'set':
				device_type = cmd_list.pop(0)
				device_name = cmd_list.pop(0)
				device_cmd = cmd_list.pop(0)

				if not device_type in valid_device_types:
					logging.error("Invalid device type: %s", device_type)
					continue

				if not device_type in dev_lists:
					dev_lists[device_type] = get_status(access_token, endpoint_base_url, endpoint_url, device_type)
				update_device(access_token, endpoint_base_url, endpoint_url, dev_lists[device_type], device_type, device_name, device_cmd)
				return None
            

			devices=[]
			if cmd == 'query':
				device_type = cmd_list.pop(0)
				device_name = cmd_list.pop(0)

				if not device_type in valid_device_types:
					logging.error("Invalid device type: %s", device_type)
					continue

				if not device_type in dev_lists:
					dev_lists[device_type] = get_status(access_token, endpoint_base_url, endpoint_url, device_type)

				if device_name == 'all':
					for device_name in dev_lists[device_type]:
						device_state = dev_lists[device_type][device_name]['state']
						logging.debug('%s %s: %s', device_type, device_name, device_state)
						devices.append({"type":device_type, "name":device_name, "state":device_state})
                    
				else:
					if not device_name in dev_lists[device_type]:
						logging.error('%s "%s" does not exist!', device_type, device_name)
						continue
					device_state = dev_lists[device_type][device_name]['state']
					logging.debug('%s %s: %s', device_type, device_name, device_state)
					devices.append({"type":device_type, "name":device_name, "state":device_state})
               
                    
				return devices

''''
' Construct unique url for user
'''
def get_endpoint_url(access_token):
    """Retrieve the URL for the SmartApp"""
    endpoint_discovery_url = 'https://graph.api.smartthings.com/api/smartapps/endpoints'
    headers = {'Authorization': 'Bearer ' + access_token}
    logging.debug('Requesting endpoints from: %s', endpoint_discovery_url)
    req = requests.get(endpoint_discovery_url, headers=headers)
    req_json = req.json()
    logging.debug('Received endpoint discovery response: %s', req_json)
    endpoint_base_url = req_json[0]['base_url']
    endpoint_url = req_json[0]['url']
    logging.debug('Received endpoint URL: %s%s', endpoint_base_url, endpoint_url)
    return endpoint_base_url, endpoint_url

'''
' Make Request to smartthings server
' Get the status of a device
'''
def get_status(access_token, endpoint_base_url, endpoint_url, device_type):
    """Query the status and device ID of all devices of one type"""
    url = endpoint_base_url + endpoint_url
    url += '/' + device_type

    headers = {'Authorization': 'Bearer ' + access_token}

    logging.debug('Requesting status from: %s', url)
    req = requests.get(url, headers=headers)
    logging.debug('Response: %s', req.text)
    req_json = req.json()
    logging.debug('Received status response: %s', req_json)

    dev_list = {}
    for json_dev in req_json:
        key = json_dev['label']

        dev_list[key] = {}
        dev_list[key]['device_id'] = json_dev['id']

        if 'state' in json_dev['value']:
            dev_list[key]['state'] = json_dev['value']['state']

    return dev_list

'''
' Make Request to smartthings server
' Set value for a specific device
'''
def update_device(access_token, endpoint_base_url, endpoint_url, dev_list, device_type, device_name, cmd): # pylint: disable=too-many-arguments
    """Issue a command to a device"""

    if not device_name in dev_list:
        logging.error('%s "%s" does not exist!', device_type, device_name)
        return

    logging.debug('Issuing "%s" command to %s "%s"', cmd, device_type, device_name)

    url = endpoint_base_url + endpoint_url
    url += '/' + device_type
    url += '/' + dev_list[device_name]['device_id']
    url += '/' + cmd

    headers = {'Authorization': 'Bearer ' + access_token}

    logging.debug('Requesting status from: %s', url)
    req = requests.get(url, headers=headers)
    logging.debug('Response (%d): %s', req.status_code, req.text)

'''
' Load config file that has the key needed to access smartthings server
'''
def load_config():
    """Load the script's configuration from a JSON file"""
    home_dir = os.path.expanduser("~")
    config_fn = os.path.join(home_dir, '.smartthings_cli.json')

    logging.info( "Load Config:" + config_fn)

    if os.path.exists(config_fn):
        with open(config_fn) as json_file:
            config = json.load(json_file)
    else:
        config = {}

    return config

