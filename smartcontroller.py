#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time

from smartthings_cli import *

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
		
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			return self.smartthings_query_cache(device_type, device_name)
		else:
			logging.warning( "SmartController:Query:UNKNOWN Controller: "+controller)
			return None
			
	def set(self, controller, device_type, device_name, cmd):
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["set",device_type,device_name, cmd])	
			return req
		else:
			logging.warning( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None


