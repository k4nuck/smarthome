#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging

from smartcontroller import *


''''
	Create a Smart Device 
	EXAMPLE of use
		fan = SmartDevice("SAMSUNG", "switch", "Fan Outlet")
		device = fan.query()
		
		print "Type:"+device["type"]
		print "Name:"+device["name"]
		print "State:"+str(device["state"])
				
		fan.set("on")
		
	Quick Note On device state.  It purposely doesnt update
	when manually changing the state of a switch.  Doing that
	on purpose so that the auto switch doesn't fight with the 
	human trying to override the state.  
	After 15 minutes of inactivity auto will resume
'''
class SmartDevice:
	smartcontroller=None
	
	def __init__ (self,controller, device_type, device_name):
		if(SmartDevice.smartcontroller==None):
			SmartDevice.smartcontroller = SmartController()
		self.controller = controller
		self.device_type = device_type
		self.device_name = device_name
		self.device_state =None
		self.timestamp = 0
		
		# Initialize last active based on active
		self.query()
		
	def query(self):
		req = SmartDevice.smartcontroller.query(self.controller, self.device_type, self.device_name)
		
		# If Motion sensor is set to true, update last active time.
		logging.debug("SmartDevice:type:"+req["type"])
		if req["type"]=="motion":
			logging.debug("Found Motion: State:"+ str(req["state"]))
			if req["state"]:
				logging.debug("Setting Last Active:"+req["name"])
				logging.debug("Device ID:"+str(hex(id(self))))
				logging.debug("Current active:"+ str(self.get_last_active()))
				self.set_last_active()
				
		
		self.device_state = req["state"]
		
		return req
	
	def query_state(self):
		req = self.query()
		return req["state"]
			
	def set(self, cmd):
		if cmd =="on":
			if self.device_state:
				logging.debug("Device Set No OP:"+cmd)
				return None
			else:
				logging.debug("Device Set Make Request:"+cmd)
				self.device_state = True
		else:
			if not self.device_state:
				logging.debug("Device Set No OP:"+cmd)
				return None
			else:
				logging.debug("Device Set Make Request:"+cmd)
				self.device_state = False
				
		logging.info("SmartDevice:"+self.device_name+":Set Cmd:"+cmd)
		SmartDevice.smartcontroller.set(self.controller, self.device_type, self.device_name,cmd)
		return None
		
	def set_on(self):
		return self.set("on")
		
	def set_off(self):
		return self.set("off")
		
	def get_device_name(self):
		return self.device_name
		
	def get_device_type(self):
		return self.device_type
		
	def get_last_active(self):
		return self.timestamp
		
	def set_last_active(self):
		self.timestamp = time.time()
		logging.debug("Device Set Last Active:"+str(self.timestamp))
		
