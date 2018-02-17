#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json

from smartdevice import *
from smartroom import *

	'''
	EXAMPLE
	with open("smarthome_config.json") as json_object:
		json_data = json.load(json_object)
		myHome = SmartHome("MyHome", json_data)
		
	rooms = myHome.get_room_names()
	for room_name in rooms:
		print "JB - " + room_name
		
		aRoom = myHome.get_room(room_name)
		switches = aRoom.get_switch_devices()
		print "JB - SWITCHES .........."
		for switch_name in switches:
			aSwitch = aRoom.get_device(switch_name)
			print "JB - Name: " + str(aSwitch.query()["name"])
			print "JB - State: " + str(aSwitch.query()["state"])
			
		motion = aRoom.get_motion_devices()
		print "JB - MOTION .........."
		for motion_name in motion:
			aMotion = aRoom.get_device(motion_name)
			print "JB - Name: " + str(aMotion.query()["name"])
			print "JB - State: " + str(aMotion.query()["state"])
	'''
class SmartHome:
	
	# If you dont want to initialize with JSON pass None
	def __init__ (self, name, json_data):
		self.name = name
		self.rooms = {}
		self.room_names = []
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
			
		myRoom.add_device(device)
		
	def add_device_details_to_room(self, room_name, controller, device_type, device_name):
		aDevice = SmartDevice(controller, device_type, device_name)
		
		self.add_device_to_room(room_name, aDevice)
		
	def get_room(self, name):
		return self.rooms[name]
		
	def get_room_names(self):
		return self.room_names
		
	# Use this to create Home for you from JSON
	def setup_home_from_json(self, json_data): 
		#print json_data
		
		rooms = json_data["rooms"]
		
		for room in rooms:
			room_name = room["name"]
			
			devices = room["devices"]
			for device in devices:
				controller = device["controller"]
				device_type = device["device_type"]
				device_name = device["device_name"]
				
				self.add_device_details_to_room(room_name, controller, device_type, device_name)
				
				
		


if __name__ == '__main__':
	'''
	with open("smarthome_config.json") as json_object:
		json_data = json.load(json_object)
		myHome = SmartHome("MyHome", json_data)
		
	rooms = myHome.get_room_names()
	for room_name in rooms:
		print "JB - " + room_name
		
		aRoom = myHome.get_room(room_name)
		switches = aRoom.get_switch_devices()
		print "JB - SWITCHES .........."
		for switch_name in switches:
			aSwitch = aRoom.get_device(switch_name)
			print "JB - Name: " + str(aSwitch.query()["name"])
			print "JB - State: " + str(aSwitch.query()["state"])
			
		motion = aRoom.get_motion_devices()
		print "JB - MOTION .........."
		for motion_name in motion:
			aMotion = aRoom.get_device(motion_name)
			print "JB - Name: " + str(aMotion.query()["name"])
			print "JB - State: " + str(aMotion.query()["state"])
			'''
			
		
