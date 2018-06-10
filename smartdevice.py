#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartdevice.py
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
		self.timestamp = time.time()
		self.overriden  = False
		
		# Initialize last active based on active
		self.query()
		
	# Query Device and return name, type, state
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
	
	# Wrapper to just return the state of the device
	def query_state(self):
		req = self.query()
		return req["state"]
		
	# Set Overriden
	def set_overriden(self, value):
		self.overriden = value
	
	# Get Overriden 
	def get_overriden(self):
		return self.overriden
			
	# Enable/Disable a device
	def set(self, cmd):	
		if self.get_overriden():
			logging.debug("SmartDevice:Overriden is set to True.  NOOP")
			return None
		
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
		
		# Update last activity here
		self.set_last_active()
		
		SmartDevice.smartcontroller.set(self.controller, self.device_type, self.device_name,cmd)
		return None
		
	# Wrapper to turn a device on
	def set_on(self):
		return self.set("on")
		
	# Wrapper to turn a device off
	def set_off(self):
		return self.set("off")
		
	# Return name of the device
	def get_device_name(self):
		return self.device_name
		
	# Return device type (Motion or Switch)
	def get_device_type(self):
		return self.device_type
		
	# Return the last time the device was triggered
	def get_last_active(self):
		return self.timestamp
		
	# Update that the device was active.
	def set_last_active(self):
		self.timestamp = time.time()
		logging.debug("Device Set Last Active:"+str(self.timestamp))
		
