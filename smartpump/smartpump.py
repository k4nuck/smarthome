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
from datetime import timedelta

from smartdevice import *
from smarthomeutils import *

'''
Handle Smart Pump Usage

Example:
  
'''

class SmartPump:
	def __init__(self,device, pump_data):
		logging.debug("Creating Smart Pump: "+str(pump_data))
		
		self.home_utils = SmartHomeUtils("smartpumpdb")
		
		# Create Device
		self.device = device
		
		# Store pump data
		self.pump_data = pump_data
		
		# Initialize timestamp
		rec = self.get_smartpump_state()
		self.timestamp = rec["timestamp"]
		
		# Default pump off
		self.set_pump_off_no_db()
		
		# Every 5 min check to make sure current state and device state on in sync
		self.set_refresh_time()
		
		# Flag to know when we are in schedule or out
		self.set_in_schedule(True)
		
		# Default Vacation Mode to False
		self.set_vacation_mode(False)
		
		# Update Cache to make sure we have a default
		self.update_smartpump_state()
		
	# In Schedule Flag
	def set_in_schedule(self,val):
		self.in_schedule = val
		
	# Return If we are in Schedule
	def get_in_schedule(self):
		return self.in_schedule
	
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
		self.set_pump_on_no_db()
		
		logging.debug("Smart Pump: Set Pump On: "+ str(time.time() - self.get_timestamp()))
		self.timestamp = time.time()
		
		# Update Cache
		self.update_smartpump_state()
		
	def set_pump_on_no_db(self):
		self.current_status = True
		
		# Turn Pump On
		try:
			self.device.set_on()
		except:
			logging.critical("Smart Pump Failed Turning Device on")
		
	
	# Turn Pump Off
	def set_pump_off(self):
		self.set_pump_off_no_db()
		
		logging.debug("Smart Pump: Set Pump Off: "+ str(time.time() - self.get_timestamp()))
		self.timestamp = time.time()
		
		# Update Cache
		self.update_smartpump_state()
	
	def set_pump_off_no_db(self):
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
	
	# Handle Vacation
	def set_vacation_mode(self, val):
		logging.info("Smart Pump Vacation Mode: " + str(val))
		self.vacation = val		
			
	def get_vacation_mode(self):
		return self.vacation
		
	# Update Cache
	def update_smartpump_state(self):
		logging.info("Smart Pump Set Cache")
		
		rec = {}
		
		# Populate Rec
		rec["timestamp"] = self.get_timestamp()
		
		# Commit
		name = self.device.get_device_name()
		self.home_utils.commit_record_in_db("SmartPump"+str(name)+"state",rec)
		
	# Get Cache
	def get_smartpump_state(self):
		name = self.device.get_device_name()
		rec = self.home_utils.get_record_from_db("SmartPump"+str(name)+"state")
		
		#Db Record Not found ... set default
		if rec ==None:
			logging.info("Smart Pump failed to find Record")
			rec={}
			rec["timestamp"] = 0
		
		logging.info("Smart Pump Cache:" + str(self.home_utils.get_datetime_from_seconds(rec["timestamp"])))
		
		return rec
	
	# Refresh
	def refresh(self):
		
		# Check status of the Device to make sure there wasn't a failure earlier
		if (time.time() - self.get_refresh_time()) > 300:
			logging.debug("Smart Pump: Checking Device State")
			self.set_refresh_time()
			if self.get_status() != self.get_device_status():
				logging.critical("Smart Pump: DEVICE STATE NOT IN SYNC.  Set OFF")
				self.set_pump_off()
				
		# Vacation Schedule
		vacation_start_time = self.home_utils.get_datetime_from_hh_mm(12,0)
		vacation_end_time = self.home_utils.get_datetime_from_hh_mm(13,0)
		
		# Check Schedules 
		allowRun = False
		schedule = self.pump_data["schedule"]
		for aSchedule in schedule:
			start_hh = aSchedule["start_hh"]
			start_mm = aSchedule["start_mm"]
			end_hh = aSchedule["end_hh"]
			end_mm = aSchedule["end_mm"]
			
			starttime = self.home_utils.get_datetime_from_hh_mm(start_hh,start_mm)
			endtime = self.home_utils.get_datetime_from_hh_mm(end_hh,end_mm)
			currenttime = self.home_utils.get_datetime_now()
			
			# Check if endttime crossed days.  
			# IE. Schedule 11:00pm to 6:00am
			if starttime > endtime:
				endtime = endtime + timedelta(days=1)
			
			logging.debug("Smart Pump: Start:"+str(starttime))
			logging.debug("Smart Pump: End:"+ str(endtime))
			logging.debug("Smart Pump: Current:" +str(currenttime))
			
			# Check if we are in vacation mode
			if self.get_vacation_mode():
				if (currenttime > vacation_start_time) and (currenttime < vacation_end_time):
					logging.debug("Smart Pump Vacation Mode; Allow")
					allowRun = True
			else:
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
				# Allow this to print once to info
				if self.get_in_schedule():
					logging.info("Smart Pump: Not in Schedule.  RETURN")
					self.set_in_schedule(False)
					
					# Make sure We didnt get out of schedule while pump was on
					# WE SHOULD NEVEr NEED TO DO THIS.  But being extra careful
					self.set_pump_off_no_db()
				return
				
			if (time.time() - self.get_timestamp()) > self.pump_data["pump_off"]:
				# We are back in schedule, print once
				if not self.get_in_schedule():
					logging.info("Smart Pump: Back in Schedule.")
					self.set_in_schedule(True)
					
				self.set_pump_on()
		
		
