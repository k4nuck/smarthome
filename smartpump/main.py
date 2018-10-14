#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
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
import logging
from logging.handlers import RotatingFileHandler

sys.path.append("/home/pi/projects/smarthome/") 

from smartdevice import *

def main():
	# Setup Logging
	log_level = logging.INFO
	logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=log_level)
	hdlr = RotatingFileHandler("/home/pi/projects/smarthome/smartpump/smartpump.log", maxBytes=(1048576*5), backupCount=5)
	logger = logging.getLogger("")
	formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	
	logging.info( "Smart Pump Started")
	
	# Get Recirc Pump Status
	pump = SmartDevice("SAMSUNG", "switch", "Recirculation Pump")
	device = pump.query()
	
	logging.info("Pump Status: "+ str(device["state"]))

if __name__ == '__main__':
	main()
