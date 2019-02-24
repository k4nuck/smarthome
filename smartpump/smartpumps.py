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
import time

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
		logging.debug("Smart Pumps JSON: "+ str(json_data))
		
		devices = json_data["devices"]
		
		for device in devices:
			controller = device["controller"]
			device_type = device["device_type"]
			device_name = device["device_name"]
			
			# Create Smart Device
			smart_device = SmartDevice(controller, device_type, device_name)
			
			logging.info("=========================")
			logging.info("Device: "+ device_name)
			
			# Create Pump Data
			pump_data = {}
			pump_on = device["pump"]["on"]
			pump_off = device["pump"]["off"]
			
			pump_data["pump_on"] = pump_on
			pump_data["pump_off"] = pump_off
			
			logging.info("Pump On: "+ str(pump_on)+" seconds")
			logging.info("Pump Off: " +str(pump_off)+" seconds")
			
			cfg_schedule = device["schedule"]
			schedule = []
			for aSchedule in cfg_schedule:
				start_hh = aSchedule["start_hh"]
				start_mm = aSchedule["start_mm"]
				end_hh = aSchedule["end_hh"]
				end_mm = aSchedule["end_mm"]
				
				logging.info("---------------")
				
				
				# Convert to Time Object
				starttime = self.home_utils.get_datetime_from_hh_mm(start_hh,start_mm)
				endtime = self.home_utils.get_datetime_from_hh_mm(end_hh,end_mm)
				
				logging.info("Schedule Start: "+ str(datetime.time(start_hh,start_mm)))
				logging.info("Schedule End: "+ str(datetime.time(end_hh, end_mm)))
				
				schedule.append({"start_hh":start_hh, "start_mm":start_mm, "end_hh":end_hh, "end_mm":end_mm})
				
			pump_data["schedule"] = schedule
			
			# Create the pump 
			pump = SmartPump(smart_device, pump_data)
			self.pumps.append(pump)
			
		# Set Vacation Mode
		self.set_vacation_mode(False)
	
	# Enable/Disable the system
	def set_system_status(self,val):
		logging.info("Smartpumps Status Set: "+ str(val))
		self.system_status = val
	
	# Get Satus of the system
	def get_system_status(self):
		return self.system_status
		
	# Handle Vacation
	def set_vacation_mode(self, val):
		logging.info("Smart Pumps Vacation Mode: " + str(val))
		
		for pump in self.pumps:
			pump.set_vacation_mode(val)
		
	
	
	# Refresh Pumps
	def refresh(self):
		logging.debug("Smart Pumps Refresh:Status:"+ str(self.get_system_status()))
		
		if not self.get_system_status():
			logging.debug("Smart Pumps system disabled.  Return")
			return
		
		# Refresh all pumps
		for pump in self.pumps:
			pump.refresh()
