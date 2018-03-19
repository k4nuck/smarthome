#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from datetime import timedelta

from astral import Astral
from smartdevice import *

'''
	Keep Track of Devices in a Room
	EXAMPLE of use
	myRoom = SmartRoom("My Room")
	myRoom.add_device(SmartDevice("SAMSUNG", "switch", "Fan Outlet"))
	myRoom.add_device(SmartDevice("SAMSUNG", "switch", "Hallway Outlet"))
	
	print "Fan State: " + str(myRoom.get_device("Fan Outlet").query()[0]["state"])
	print "Hallway State: " + str(myRoom.get_device("Hallway Outlet").query()[0]["state"])
'''
class SmartRoom:
	CalendarInfo=None
	
	def __init__ (self, name):
		self.name = name
		self.devices = {}
		self.switch_devices=[]
		self.motion_devices=[]
		
		# Only initialize once
		if SmartRoom.CalendarInfo == None:
			SmartRoom.CalendarInfo = self.update_calendar_info()
		
	def update_calendar_info(self):
		calendarInfo = {}
		
		#JB - Config this
		city_name = 'New York'
		astral = Astral()
		astral.solar_depression = 'civil'

		# Get City Data
		city = astral[city_name]
		
		# Sun Data for City
		date=datetime.date.today()
		sun = city.sun(date, local=True)
		
		logging.info("Update Calendar Info:"+ str(date))
		
		# Update Calendar Info
		calendarInfo["current_date"] = date
		calendarInfo["sun"] = sun
		
		return calendarInfo
	
	def get_sun_data(self):
		# Check if sun data needs to update
		current_date = SmartRoom.CalendarInfo["current_date"]
		date=datetime.date.today()
		
		if date != current_date:
			logging.info("Get Sun Data: NEW DATE: Updating current_date:"+ str(current_date)+" with:"+ str(date))
			SmartRoom.CalendarInfo = self.update_calendar_info()
			
		return SmartRoom.CalendarInfo["sun"]
	
	def add_device(self, device):
		# Keep track of switches and motion sensors names
		# Also the key to devices dictionary
		device_name = device.get_device_name()
		device_type = device.get_device_type()
		if device_type=="motion":
			self.motion_devices.append(device_name)
		elif device_type=="switch":
			self.switch_devices.append(device_name)
			
		# Map of devices in a room
		self.devices[device_name] = device
		
	def get_device(self, device_name):
		return self.devices[device_name]
		
	def get_motion_devices(self):
		return self.motion_devices
		
	def get_switch_devices(self):
		return self.switch_devices
		
	def get_name(self):
		return self.name	
		
	# CHeck real status of a motion sensor and update if still active
	def refresh_last_active(self):
		for device_name in self.motion_devices:
			device = self.get_device(device_name)
			if device.query_state():
				device.set_last_active()
		
	# Check last time room had movement
	def get_last_active(self):
		last_active = None
		for device_name in self.motion_devices:
			device = self.get_device(device_name)
			
			logging.debug("Get Last Active:"+device_name)
			logging.debug("Device Time:"+ str(device.get_last_active()))
			logging.debug("Device ID:"+str(hex(id(device))))
			
			if(last_active ==None):
				last_active = device.get_last_active()
			elif(last_active < device.get_last_active()):
				last_active = device.get_last_active()
		return last_active
		
	#Check if Lights should be allowed on in this room
	def should_lights_stay_off(self):
		logging.debug("In should_lights_stay_off")
		lights_stay_off = False
		sun = self.get_sun_data()
		
		# Sunset and Sunrise Information
		# Offset by an hour window
		sunset = sun['sunset'] - timedelta(hours=1)
		sunrise = sun['sunrise'] + timedelta(hours=1)

		logging.debug("Sunset(offset):"+ str(sunset))
		logging.debug("Sunrise(offset):"+ str(sunrise))

		# Get Current Time taking time zone into account
		tz_info = sunset.tzinfo
		currentTime = datetime.datetime.now(tz_info)
		
		logging.debug("Current Time:"+str(currentTime))
		
		if currentTime > sunset:
			logging.info ("should_lights_stay_off:After Sunset:"+ self.get_name())
		else:
			if currentTime < sunrise:
				logging.info ("should_lights_stay_off:Before Sunrise:"+ self.get_name())
			else:
				logging.info ("should_lights_stay_off:Keep Lights Off:"+ self.get_name())
				lights_stay_off = True
		
		
		return lights_stay_off
	
	# Turn all Switches on in a room			
	def turn_switches_on_in_room(self):
		if self.should_lights_stay_off():
			logging.debug("Turn Switches On:  KEEP OFF!!")
			return
		
		for device_name in self.get_switch_devices():
			device = self.get_device(device_name)
			device.set_on()
	
	# Turn all Switches off in a room		
	def turn_switches_off_in_room(self):	
		for device_name in self.get_switch_devices():
			device = self.get_device(device_name)
			device.set_off()
