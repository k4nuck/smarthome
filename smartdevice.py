#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

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
	
	def __init__ (self,controller, device_type, device_name):
		if(SmartDevice.smartcontroller==None):
			print "JB - Creating SmartController"
			SmartDevice.smartcontroller = SmartController()
		self.controller = controller
		self.device_type = device_type
		self.device_name = device_name
		
	def query(self):
		req = SmartDevice.smartcontroller.query(self.controller, self.device_type, self.device_name)
		return req
				
	def set(self, cmd):
		req = SmartDevice.smartcontroller.set(self.controller, self.device_type, self.device_name,cmd)
		return req
		
	def get_device_name(self):
		return self.device_name
		
		
		
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
