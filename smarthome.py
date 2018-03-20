#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time

from smartdevice import *
from smartroom import *

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
		
		self.refresh_time=300
		self.activity_time=600
		
		# Load Home
		if(json != None):
			self.setup_home_from_json(json_data)
			
		logging.info("SmartHome Refresh Time:Refresh Time:"+str(self.get_refresh_time()))
		logging.info("SmartHome Refresh Time:Activity Time:"+str(self.get_activity_time()))
			
	
	def set_on_off(self, onoff):
		logging.info("MyHome Turning System:" + str(onoff))
		self.on=onoff
		
	def add_room(self,name):
		self.rooms[name] = SmartRoom(name)
		self.room_names.append(name)
		
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
		
		
	def add_device_details_to_room(self, room_name, controller, device_type, device_name):
		
		#Check if Device already Exists
		if device_name not in self.devices:
			aDevice = SmartDevice(controller, device_type, device_name)
		else:
			aDevice = self.devices[device_name]
		
		self.add_device_to_room(room_name, aDevice)
		
	def get_room(self, name):
		return self.rooms[name]
		
	def get_room_names(self):
		return self.room_names
		
	def get_name(self):
		return self.name
	
	# Use this to create Home for you from JSON
	def setup_home_from_json(self, json_data): 
		logging.info("Creating Home from JSON")
		
		settings = json_data["settings"]
		self.refresh_time = settings["refresh"]
		self.activity_time = settings["activity"]
		city = settings["city"]
		
		# Set City for Rooms
		SmartRoom.City = city
		
		rooms = json_data["rooms"]
		
		for room in rooms:
			room_name = room["name"]
			allow_force_off = room["allow_force_off"] 
			sunset_offset = room["sunset_offset"] 
			sunrise_offset = room["sunrise_offset"] 
			
			devices = room["devices"]
			for device in devices:
				controller = device["controller"]
				device_type = device["device_type"]
				device_name = device["device_name"]
				
				self.add_device_details_to_room(room_name, controller, device_type, device_name)
				
			#Room Should Created.  Get and Set Properties
			aRoom = self.rooms[room_name]
			aRoom.set_allow_force_off(allow_force_off)
			aRoom.set_sunset_offset(sunset_offset)
			aRoom.set_sunrise_offset(sunrise_offset)
			
			logging.debug("SmartHome:Name:"+room_name)
			logging.debug("SmartHome Load Data:force Off:"+ str(allow_force_off))
			logging.debug("SmartHome Load Data:sunset offset:"+ str(sunset_offset))
			logging.debug("SmartHome Load Data:sunrise offset:"+ str(sunrise_offset))
			
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
		
	def is_system_on(self):
		return self.on
		
	def get_refresh_time(self):
		return self.refresh_time
		
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
