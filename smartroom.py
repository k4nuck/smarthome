#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from smartdevice import *

class SmartRoom:
	
	def __init__ (self, name):
		self.name = name
		self.devices = {}
	
	def add_device(self, device):
		
