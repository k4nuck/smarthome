#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartcontroller.py
#  
#  Copyright 2018  <pi@raspberrypi>
#  Joseph Bersito
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 

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
		
		# Get Config Data for Harmony Hub
		with open("/home/pi/.harmony_settings.json") as harmony_object:
			harmony_data = json.load(harmony_object)
			self.ip = harmony_data["ip"]
			self.port = harmony_data["port"]
			logging.debug("ip:"+self.ip+" - port:"+self.port)
	
	# Since the smartthings access gets values for all devices.  We get it once and cache for some delta
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
	
	# Query from the cache.  Invalidate if necessary
	def smartthings_query_cache(self, device_type, device_name):
		# Check cache - Invalidate after 3 seconds
		if (self.smartthings_cache_timestamp == None) or ((time.time() - self.smartthings_cache_timestamp) > 3):
			self.update_smartthings_cache()
		else:
			logging.debug("Using smartthings query cache")
		
		return self.smartthings_cache[device_type][device_name]
		
	# Query Harmony Devices
	def harmony_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		#This IP and PORT from config
		ip = self.ip
		port = self.port
		activity_callback=None
		client = harmony_client.create_and_connect_client(ip, port, activity_callback)
	
		config = client.get_config()
		current_activity_id = client.get_current_activity()
		
		client.disconnect(send_close=True)
		
		activity = [x for x in config['activity'] if int(x['id']) == current_activity_id][0]
		
		if activity['label'] == "PowerOff":
			data["state"] = False
		else:
			data["state"] = True
		
		return data	
		
	# Public Accessor to query any type of device
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			return self.smartthings_query_cache(device_type, device_name)
		if controller == "HARMONY":
			return self.harmony_query(device_type,device_name)
		else:
			logging.warning( "SmartController:Query:UNKNOWN Controller: "+controller)
			return None
			
	# Public Accessor to set value for any device type
	def set(self, controller, device_type, device_name, cmd):
		#JB - Support Set for HARMONY Devices
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["set",device_type,device_name, cmd])	
			return req
		else:
			logging.warning( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None


