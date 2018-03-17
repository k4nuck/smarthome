#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time

from smartthings_cli import *
from pyharmony import client as harmony_client

'''
' Generic Interface for Smart Devices
' Current support:
'      Samsung Smartthings
' Format of return
'      {"type":"<DEVICE TYPE>", "name":"<DEVICE NAME>", "state":<BOOL>}
'''
class SmartController:
	
	def __init__ (self):
		self.smartthings_cache={}
		self.smartthings_cache_timestamp=None
		self.smartthings=SmartThings()
	
	def update_smartthings_cache(self):
		logging.debug("Update Smartthings Cache")
		
		# Get All Smartthings Motion Sensors
		req = self.smartthings.smart_request(["query","motion","all"])
		for device in req:
			if device["type"] not in self.smartthings_cache:
				self.smartthings_cache[device["type"]] = {}
			
			# Update Cache
			self.smartthings_cache[device["type"]][device["name"]] = {"type":device["type"], "name":device["name"], "state":device["state"]}
			
		# Get All Smartthings Switches
		req = self.smartthings.smart_request(["query","switch","all"])
		for device in req:
			if device["type"] not in self.smartthings_cache:
				self.smartthings_cache[device["type"]] = {}
			
			# Update Cache
			self.smartthings_cache[device["type"]][device["name"]] = {"type":device["type"], "name":device["name"], "state":device["state"]}
			
		logging.debug(self.smartthings_cache)
		
		#Update timestampe
		self.smartthings_cache_timestamp = time.time()
	
	def smartthings_query_cache(self, device_type, device_name):
		# Check cache - Invalidate after 3 seconds
		if (self.smartthings_cache_timestamp == None) or ((time.time() - self.smartthings_cache_timestamp) > 3):
			self.update_smartthings_cache()
		else:
			logging.debug("Using smartthings query cache")
		
		return self.smartthings_cache[device_type][device_name]
		
	def harmony_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		#JB - This IP and PORT need to be in a config
		ip = "192.168.1.59"
		port ="5222"
		activity_callback=None
		client = harmony_client.create_and_connect_client(ip, port, activity_callback)
	
		config = client.get_config()
		current_activity_id = client.get_current_activity()
		activity = [x for x in config['activity'] if int(x['id']) == current_activity_id][0]
		
		if activity['label'] == "Power Off":
			data["state"] = False
		else:
			data["state"] = True
		
		return data	
		
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			return self.smartthings_query_cache(device_type, device_name)
		if controller == "HARMONY":
			return self.harmony_query(device_type,device_name)
		else:
			logging.warning( "SmartController:Query:UNKNOWN Controller: "+controller)
			return None
			
	def set(self, controller, device_type, device_name, cmd):
		#JB - Support Set for HARMONY Devices
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["set",device_type,device_name, cmd])	
			return req
		else:
			logging.warning( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None


