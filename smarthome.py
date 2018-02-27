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
		
		# Load Home
		if(json != None):
			self.setup_home_from_json(json_data)
		
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
		
		rooms = json_data["rooms"]
		
		for room in rooms:
			room_name = room["name"]
			
			devices = room["devices"]
			for device in devices:
				controller = device["controller"]
				device_type = device["device_type"]
				device_name = device["device_name"]
				
				self.add_device_details_to_room(room_name, controller, device_type, device_name)
				
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
		
	# Handle Refresh
	def refresh(self):
		logging.debug("---------Start--------------")
		logging.debug("SmartHome Refresh")
		
		# Every 10 Minutes check if a room needs a refresh
		current_time = time.time()
		if (current_time - self.last_refresh) > 600:
			logging.debug("SmartHome:Full Refresh after 10 Minutes")
			self.last_refresh = current_time
			for room_name in self.room_names:
				self.rooms[room_name].refresh_last_active()
		
		# Check last activity in a room
		# If last Active was within 15 minutes turn on Room Lights
		for room_name in self.room_names:
			room = self.rooms[room_name]
			logging.debug("SmartHome:Room Name:"+room_name)
			logging.debug("SmartHome:Last Active:"+str(room.get_last_active()))
			
			if (current_time - room.get_last_active()) > 900:
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
