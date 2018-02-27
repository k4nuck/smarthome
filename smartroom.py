#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

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
	
	def __init__ (self, name):
		self.name = name
		self.devices = {}
		self.switch_devices=[]
		self.motion_devices=[]
	
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
	
	# Turn all Switches on in a room			
	def turn_switches_on_in_room(self):
		for device_name in self.get_switch_devices():
			device = self.get_device(device_name)
			device.set_on()
	
	# Turn all Switches off in a room		
	def turn_switches_off_in_room(self):
		for device_name in self.get_switch_devices():
			device = self.get_device(device_name)
			device.set_off()
