#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smarthome.py
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
import json
import time

from smartdevice import *
from smartroom import *
from smarthomedb import *

'''
Keep Track of Rooms in a House
Control Enabling / Disabling Devices in a Room

EXAMPLE
	with open("smarthome_config.json") as json_object:
		json_data = json.load(json_object)
		myHome = SmartHome("MyHome", json_data)
		
	rooms = myHome.get_room_names()
	for room_name in rooms:
		print room_name
		
		aRoom = myHome.get_room(room_name)
		switches = aRoom.get_switch_devices()
		print "SWITCHES .........."
		for switch_name in switches:
			aSwitch = aRoom.get_device(switch_name)
			print "Name: " + switch_name
			print "State: " + str(aSwitch.query_state())
			
		motion = aRoom.get_motion_devices()
		print "MOTION .........."
		for motion_name in motion:
			aMotion = aRoom.get_device(motion_name)
			print "Name: " + motion_name
			print "State: " + str(aMotion.query_state())	
'''
class SmartHome:
	
	# If you dont want to initialize with JSON pass None
	def __init__ (self, name, json_data):
		self.name = name
		self.rooms = {}
		self.devices = {}
		self.room_names = []
		self.last_refresh = 0
		self.on = True
		self.modes = {}
		self.myHomeDB = SmartHomeDB()
		
		# Default Refresh Rates if not in Config
		self.refresh_time=300
		self.activity_time=600
		
		# Load Home
		if(json != None):
			self.setup_home_from_json(json_data)
			
		logging.info("SmartHome Refresh Time:Refresh Time:"+str(self.get_refresh_time()))
		logging.info("SmartHome Refresh Time:Activity Time:"+str(self.get_activity_time()))
			
	
	# Enable/Disable the System
	def set_on_off(self, onoff):
		logging.info("MyHome Turning System:" + str(onoff))
		self.on=onoff
		
	# Create a Room and Add it to Home
	def add_room(self,name):
		self.rooms[name] = SmartRoom(name)
		self.room_names.append(name)
		
	# Add a device to a room
	# Will Create a room if it needs
	def add_device_to_room(self, name, device):
		# Check if room exist yet
		if name in self.rooms:
			myRoom = self.rooms[name]
		else:
			self.add_room(name)
			myRoom = self.rooms[name]
			
		#Add Device to Room	
		myRoom.add_device(device)
		
		#Update Device Cache
		name = device.get_device_name()
		self.devices[name] = device
		
		
	# Create a Device and Add it to a room
	def add_device_details_to_room(self, room_name, controller, device_type, device_name):
		
		#Check if Device already Exists
		if device_name not in self.devices:
			aDevice = SmartDevice(controller, device_type, device_name)
		else:
			aDevice = self.devices[device_name]
		
		self.add_device_to_room(room_name, aDevice)
		
	# Return a room object from a name
	def get_room(self, name):
		return self.rooms[name]
		
	# Return the names of all rooms in a home
	def get_room_names(self):
		return self.room_names
		
	# Return name of a room
	def get_name(self):
		return self.name
		
	# Set Room Based on Mode
	def set_mode_for_room(self, mode, room_name):
		logging.info("Set Mode for Room: "+ mode+ " - Room: "+room_name)
		
		# Get Room
		aRoom = self.get_room(room_name)
		aRoom.set_mode(mode)
		
		# Get Mode Settings
		mode = self.modes[room_name][mode]
		allow_force_off = mode["allow_force_off"] 
		sunset_offset = mode["sunset_offset"] 
		sunrise_offset = mode["sunrise_offset"] 
		weather_offset = mode["weather_offset"]
			
		# Get start hh and mm and create a datetime object
		current = datetime.datetime.now()
		hh = mode["nighttime_start_hh"]
		mm = mode["nighttime_start_mm"]
		nighttime_start = datetime.datetime(current.year,current.month, current.day,hh,mm)
			
		# Get end hh and mm and create datetime object
		hh = mode["nighttime_end_hh"]
		mm = mode["nighttime_end_mm"]
		nighttime_end = datetime.datetime(current.year,current.month, current.day,hh,mm)
			
		# Check if server bounced after midnight but before Night.  
		# We will know this is current is before both start and end night time date
		if current < nighttime_start and current < nighttime_end:
			logging.info("Set Mode For Room: current is before nighttime start and end")
			nighttime_start = nighttime_start - datetime.timedelta(days=1)
			
		# If Start is after end then add a day to end
		elif nighttime_start > nighttime_end:
			logging.info("Set Mode For Room: nighttime start is after end")
			nighttime_end = nighttime_end + datetime.timedelta(days=1)
			
		#Set Properties of the room
		aRoom.set_allow_force_off(allow_force_off)
		aRoom.set_sunset_offset(sunset_offset)
		aRoom.set_sunrise_offset(sunrise_offset)
		aRoom.set_weather_offset(weather_offset)
		aRoom.set_nighttime_start(nighttime_start)
		aRoom.set_nighttime_end(nighttime_end)
			
		logging.debug("Set Mode For Room:Name:"+room_name)
		logging.debug("Set Mode For Room:force Off:"+ str(allow_force_off))
		logging.debug("Set Mode For Room:sunset offset:"+ str(sunset_offset))
		logging.debug("Set Mode For Room:sunrise offset:"+ str(sunrise_offset))
		logging.debug("Set Mode For Room:weather offset:"+ str(weather_offset))
		logging.debug("Set Mode For Room: Nighttime Start:"+ str(nighttime_start))
		logging.debug("Set Mode For Room: Nighttime End:"+ str(nighttime_end))
		
	# Set Home based on Mode
	def set_mode(self, mode):
		logging.info("Set Mode: "+ mode)
		
		# Loop through each room and update the mode for each room
		room_names = self.get_room_names()
		for room_name in room_names:
			self.set_mode_for_room(mode,room_name)
	
	# Return number of seconds from datetime
	def get_seconds_from_datetime(self, t):
		return time.mktime(t.timetuple())
	
	# Return datetime from seconds
	def get_datetime_from_seconds(self, seconds):
		return datetime.datetime.fromtimestamp(seconds)
	
	# Get DB Handle
	def get_db_handle(self):
		return self.myHomeDB
	
	# Update CurrentState in the DB
	def update_current_state_in_db(self):
		rec = {}
		
		# Populate Rec
		rec["system_status"] = self.is_system_on()
		rec["refresh_time"] = self.refresh_time
		rec["activity_time"] = self.activity_time
		rec["city"] = SmartRoom.City
		rec["weather_loc_id"] = SmartRoom.Weather_Loc_id
		rec["rooms"]=[]
		
		# Room Info
		for room_name in self.room_names()
			aroom = self.get_room(room_name)
			
			rec_room={"name":room_name}
			
			# Sun Info
			sun = aroom.get_sun_data()
			rec_room["sunrise"]= self.get_seconds_from_datetime(sun["sunrise"])
			rec_room["sunset"]  = self.get_seconds_from_datetime(sun["sunset"])
			rec_room["sunrise_offset"] = aRoom.get_sunrise_offset()
			rec_room["sunset_offset"] = aRoom.get_sunset_offset()
			
			# Weather Info
			weather = aRoom.get_weather_data()
			rec_room["weather_offset"] = aRoom.get_weather_offset()
			rec_room["forecast"] = weather["forecast"]
			rec_room["location"] = weather["location"]
			rec_room["day_of_week"] = weather["day_of_week"]
			
			# Other
			rec_room["lights_stay_off"] = aRoom.should_lights_stay_off()
			rec_room["nighttime_mode"] = aRoom.nighttime_mode()
			rec_room["nighttime_start"] = self.get_seconds_from_datetime((aRoom.get_nighttime_start())
			rec_room["nighttime_end"] = self.get_seconds_from_datetime((aRoom.get_nighttime_end())
			
			rec_room["switches"] = []
			
			# Get Switch Device Information
			devices = aRoom.get_switch_devices()
			for device_name in devices:
				rec_device = {"name":device_name}
				aDevice = aRoom.get_device(device_name)
				rec_device["state"] = aDevice.query_state()
				rec_room["switches"].append(rec_device)
								
			rec_room["motions"] = []
			
			# Get Motion Device Information
			devices = aRoom.get_motion_devices()
			for device_name in devices:
				rec_device = {"name":device_name}
				aDevice = aRoom.get_device(device_name)
				rec_device["state"] = aDevice.query_state()
				rec_room["motions"].append(rec_device)
				
			# Add Room Data
			rec["rooms"].append(rec_room)
			
		# Commit
		self.get_db_handle().update("CurrentState",rec)
			
	# Use this to create Home from JSON
	def setup_home_from_json(self, json_data): 
		logging.info("Creating Home from JSON")
		
		settings = json_data["settings"]
		self.refresh_time = settings["refresh"]
		self.activity_time = settings["activity"]
		city = settings["city"]
		weather_loc_id = settings["weather_loc_id"]
		
		# Set City for Rooms
		SmartRoom.City = city
		
		# Set Weather Id
		SmartRoom.Weather_Loc_Id = weather_loc_id
		
		rooms = json_data["rooms"]
		
		for room in rooms:
			room_name = room["name"]
			
			# Save the modes for each room
			self.modes[room_name] = {}
			for mode in room["modes"]:
				self.modes[room_name][mode["mode"]] = mode
			
			# Create Devices
			devices = room["devices"]
			for device in devices:
				controller = device["controller"]
				device_type = device["device_type"]
				device_name = device["device_name"]
				self.add_device_details_to_room(room_name, controller, device_type, device_name)
			
		# Set Mode to Default
		self.set_mode("default")
		
		# Refresh After new Devices added
		self.refresh()
				
	# Handle Motion Sensor Triggered
	def handle_device_triggered(self, device_name):
		logging.info("SmartHome Device Triggered:" + device_name)
		
		# Find Device and update
		device = self.devices[device_name]
		device.set_last_active()
		
		# Refresh
		self.refresh()
		
	# Return if the system is active
	def is_system_on(self):
		return self.on
		
	# Return time in seconds of when the system will poll devices
	def get_refresh_time(self):
		return self.refresh_time
	
	# Return time in seconds of when a room should turn off its devices if no activity
	def get_activity_time(self):
		return self.activity_time
		
	# Handle Refresh
	def refresh(self):
		logging.debug("---------Start--------------")
		logging.debug("SmartHome Refresh")
		
		# check if a room needs a refresh - Set in configuration
		current_time = time.time()
		if (current_time - self.last_refresh) > self.get_refresh_time():
			logging.debug("SmartHome:Full Refresh after "+str(self.get_refresh_time()) +" Seconds")
			self.last_refresh = current_time
			for room_name in self.room_names:
				room = self.rooms[room_name]
				
				#If Expired then switches are already off.  Nothing to do
				# Unless the Room is forced off ... then we should do a refresh
				# JB - DON'T IMPLEMENT this until we start capturing MANUAL overrides
				if (current_time - room.get_last_active()) > self.get_activity_time():
					logging.debug("My Home Refresh: No Need to Refresh:"+ room_name)
				else:
					#Full Refresh .. In case Motion Sensors are constantly active.
					room.refresh_last_active()
		
		# Check last activity in a room
		# activity time set in configuration
		if self.is_system_on():
			for room_name in self.room_names:
				room = self.rooms[room_name]
				
				logging.debug("SmartHome:Room Name:"+room_name)
				logging.debug("SmartHome:Last Active:"+str(room.get_last_active()))
			
				if (current_time - room.get_last_active()) > self.get_activity_time():
					logging.debug("SmartHome:Refresh:Turn Room Off:" + room.get_name())
					logging.debug("SmartHome:Refresh:current_time:" + str(current_time))
					logging.debug("SmartHome:Refresh:Room time:" + str(room.get_last_active()))
					room.turn_switches_off_in_room()
				else:
					logging.debug("SmartHome:Refresh:Turn Room On:" + room.get_name())
					logging.debug("SmartHome:Refresh:current_time:" + str(current_time))
					logging.debug("SmartHome:Refresh:Room time:" + str(room.get_last_active()))
					room.turn_switches_on_in_room()
		
			logging.debug("----------End-------------")
			
		# Update DB
		self.update_current_state_in_db()
