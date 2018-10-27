#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartpumps.py
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

from smartpump import *
from smartdevice import *
from smarthomeutils import *

'''
Handle Smart Pump Usage

Example:
  
'''

class SmartPumps:
	def __init__(self,json_data):
		self.pumps = []
		self.set_system_status(True)
		self.home_utils = SmartHomeUtils("smartpumpdb")
		
		# Create Pumps(s)
		logging.info("Smart Pumps JSON: "+ str(json_data))
		
		devices = json_data["devices"]
		
		for device in devices:
			controller = device["controller"]
			device_type = device["device_type"]
			device_name = device["device_name"]
			
			# Create Smart Device
			smart_device = SmartDevice(controller, device_type, device_name)
			
			# JB - Just create the pump for now
			pump = SmartPump(smart_device)
			self.pumps.append(pump)
			
			#JB - TEST converting HH:MM to datetime
			logging.info("SmartPumps HH MM Test:" + str(self.home_utils.get_datetime_from_hh_mm(6,30)))
	
	# Enable/Disable the system
	def set_system_status(self,val):
		self.system_status = val
	
	# Get Satus of the system
	def get_system_status(self):
		return self.system_status
	
	# Refresh Pumps
	def refresh(self):
		logging.info("Smart Pumps Refresh:Status:"+ str(self.get_system_status()))
		
		if not self.get_system_status():
			logging.info("Smart Pumps system disabled.  Return")
			return
		
		# Refresh all pumps
		for pump in self.pumps:
			pump.refresh()
