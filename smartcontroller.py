#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

from smartthings_cli import *

'''
' Generic Interface for Smart Devices
' Current support:
'      Samsung Smartthings
'''
class SmartController:
	
	def __init__ (self):
		# JB - Cache for the future
		self.cache={}
		self.smartthings=SmartThings()
		
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["query",device_type,device_name])[0]
			return req
		else:
			logging( "SmartController:Query:UNKNOWN Controller: "+controller)
			return None
			
	def set(self, controller, device_type, device_name, cmd):
		if controller == "SAMSUNG":
			req = self.smartthings.smart_request(["set",device_type,device_name, cmd])	
			return req
		else:
			logging( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None
