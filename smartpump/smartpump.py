#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartpump.py
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

from smartdevice import *

'''
Handle Smart Pump Usage

Example:
  
'''

class SmartPump:
	def __init__(self,device, pump_data):
		logging.info("Creating Smart Pump: "+str(pump_data))
		
		# Create Device
		self.device = device
		
		# Store pump data
		self.pump_data = pump_data
		
		# Initialize timestamp
		self.timestamp = 0
		
		# Default pump on
		self.set_pump_on()
		
	# Get Current Timestamp
	def get_timestamp(self):
		return self.timestamp
		
		
	# Turn Pump on
	def set_pump_on(self):
		#JB - Update DB
		
		logging.debug("Smart Pump: Set Pump On: "+ str(time.time() - self.get_timestamp()))
		self.timestamp = time.time()
		self.current_status = True
		
		# Turn Pump On
		try:
			self.device.set_on()
		except:
			logging.critical("Smart Pump Failed Turning Device on")
		
	
	# Turn Pump Off
	def set_pump_off(self):
		#JB - Update DB
		
		logging.debug("Smart Pump: Set Pump Off: "+ str(time.time() - self.get_timestamp()))
		self.timestamp = time.time()
		self.current_status = False
		
		# Turn Pump Off
		try:
			self.device.set_off()
		except:
			logging.critical("Smart Pump Failed Turning Device off")
		
		
	# Get pump status
	def get_status(self):
		return self.current_status
	
	# Get actual Status of the device 
	def get_device_status(self):
		try:
			currentState = self.device.query()
			return currentState["state"]
		except:
			logging.critical("Smart Pump: Failed Device Query")
			return False
	
	# Refresh
	def refresh(self):
		#JB - Update DB
		#JB - Check Schedule
		
		# Check if Pump has been on long enough
		if self.get_status():
			if (time.time() - self.get_timestamp()) > self.pump_data["pump_on"]:
				self.set_pump_off()
		else:
			if (time.time() - self.get_timestamp()) > self.pump_data["pump_off"]:
				self.set_pump_on()
		
		
