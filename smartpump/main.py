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

import multiprocessing 
import time
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from subprocess import call

sys.path.append("/home/pi/projects/smarthome/") 

from smartpumps import *
from smartpump import *

# Process for sending commands to the server from command line
def fifo_worker(mainLoopQueue):
	
	logging.info("FIFO Worker Spawned")
	
	# Create FIFO File if needed
	path = "/home/pi/projects/smarthome/smartpump/pump.fifo"
	if not os.path.exists(path):
		os.mkfifo(path)
	
	#Wait for Commands
	while True:
		fifo = open(path, "r")
		for line in fifo:
			logging.info( "FIFO;Received: (" + line + ")")
			
			if line=="exit":
				mainLoopQueue.put({'cmd':line, 'data':None})
				
			if line=="status":
				mainLoopQueue.put({'cmd':line, 'data':None})
					
		fifo.close()

# Process for notifying server of delta time has passed
def timer_worker(mainLoopQueue):
	logging.info("TIMER Worker Spawned")
	
	#Sleep and then notify parent
	while True:
		time.sleep(60)
		mainLoopQueue.put({'cmd':"Time", 'data':None})
		
# Main
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
	
	# Get data from JSON File
	with open("/home/pi/projects/smarthome/smartpump/smartpump_config.json") as json_object:
		json_data = json.load(json_object)
		myPumps = SmartPumps(json_data)
		logging.info("Smart Pump JSON: "+ str(json_data))
		
	
	#JB - Get FROM json file
	#    Device
	#    Time Pump Should be On
	#    Time Pump should be Off
	#    Time System is on
	#    Time System is off
	
	# Get Recirc Pump Status
	#pump = SmartPump(SmartDevice("SAMSUNG", "switch", "Recirculation Pump"))
	#logging.info("Pump Status: "+ str(pump.get_status()))

	# JB - Setup Threads

if __name__ == '__main__':
	main()
