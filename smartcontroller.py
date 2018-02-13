#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from smartthings_cli import *

'''
Example of input and output
#Switches - smartthings_cli.py vvvv
			req = smartthings.smart_request(["query","switch","all"])
			
			for device in req:
				print "---------------------"
				print "Type:"+device["type"]
				print "Name:"+device["name"]
				print "State:"+str(device["state"])
'''
class SmartController:
	
	def __init__ (self):
		# JB - Cache for the future
		self.cache={}
		self.smartthings=SmartThings()
		
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["query",device_type,device_name])	
			return req
		else:
			print "JB - SmartController:Query:UNKNOWN Controller: "+controller
			return None
			
	def set(self, controller, device_type, device_name, cmd):
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["set",device_type,device_name, cmd])	
			return req
		else:
			print "JB - SmartController:Set:UNKNOWN Controller: "+controller
			return None

if __name__ == '__main__':
	'''smart = SmartController()
	req = smart.set("SAMSUNG","switch","Fan Outlet", "on")'''
