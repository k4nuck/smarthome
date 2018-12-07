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
from smarthomeutils import *

'''
Handle Smart Pump Usage

Example:
  
'''

class SmartPump:
	def __init__(self,device, pump_data):
		logging.info("Creating Smart Pump: "+str(pump_data))
		
		self.home_utils = SmartHomeUtils("smartpumpdb")
		
		# Create Device
		self.device = device
		
		# Store pump data
		self.pump_data = pump_data
		
		# Initialize timestamp
		self.timestamp = 0
		
		# Default pump off
		self.set_pump_off()
		
		# Every 5 min check to make sure current state and device state on in sync
		self.set_refresh_time()
		
	# Set Refresh Time
	def set_refresh_time(self):
		self.refresh_time = time.time()
		
	# Get Refresh Time
	def get_refresh_time(self):
		return self.refresh_time
	
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
		
		# Check status of the Device to make sure there wasn't a failure earlier
		if (time.time() - self.get_refresh_time()) > 300:
			logging.debug("Smart Pump: Checking Device State")
			self.set_refresh_time()
			if self.get_status() != self.get_device_status():
				logging.critical("Smart Pump: DEVICE STATE NOT IN SYNC.  Set OFF")
				self.set_pump_off()
				
		# Check Schedules
		allowRun = False
		schedule = self.pump_data["schedule"]
		for aSchedule in schedule:
			starttime = aSchedule["starttime"]
			endtime = aSchedule["endtime"]
			currenttime = self.home_utils.get_datetime_now()
			
			logging.debug("Smart Pump: Start:"+str(starttime))
			logging.debug("Smart Pump: End:"+ str(endtime))
			logging.debug("Smart Pump: Current:" +str(currenttime))
			
			# Check if we are inside of the run time
			if (currenttime > starttime) and (currenttime < endtime):
				allowRun = True 
		
		logging.debug("Smart Pump: Allow Run: "+ str(allowRun))
			
		# Check if Pump has been on long enough
		if self.get_status():
			if (time.time() - self.get_timestamp()) > self.pump_data["pump_on"]:
				self.set_pump_off()
		else:
			if not allowRun:
				logging.info("Smart Pump: Not in Schedule.  RETURN")
				return
				
			if (time.time() - self.get_timestamp()) > self.pump_data["pump_off"]:
				self.set_pump_on()
		
		
