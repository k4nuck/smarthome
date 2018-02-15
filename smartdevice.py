#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

from smartcontroller import *


'''
	EXAMPLE of use
	fan = SmartDevice("SAMSUNG", "switch", "Fan Outlet")
	req = fan.query()
	for device in req:
				print "---------------------"
				print "Type:"+device["type"]
				print "Name:"+device["name"]
				print "State:"+str(device["state"])
				
	fan.set("on")
'''
class SmartDevice:
	smartcontroller=None
	
	#JB - Should we keep track of state change made manually vs automated
	def __init__ (self,controller, device_type, device_name):
		if(SmartDevice.smartcontroller==None):
			SmartDevice.smartcontroller = SmartController()
		self.controller = controller
		self.device_type = device_type
		self.device_name = device_name
		self.time = time.time()
		
	def query(self):
		req = SmartDevice.smartcontroller.query(self.controller, self.device_type, self.device_name)
		return req
				
	def set(self, cmd):
		req = SmartDevice.smartcontroller.set(self.controller, self.device_type, self.device_name,cmd)
		return req
		
	def get_device_name(self):
		return self.device_name
		
	def get_device_type(self):
		return self.device_type
		
	def get_last_active(self):
		return self.time
		
	def set_last_active(self):
		self.time = time.time()
		
		
		
if __name__ == '__main__':
	'''
	fan = SmartDevice("SAMSUNG", "switch", "Fan Outlet")
	req = fan.query()
	for device in req:
				print "---------------------"
				print "Type:"+device["type"]
				print "Name:"+device["name"]
				print "State:"+str(device["state"])
				
	fan.set("on")
	'''
