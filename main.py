#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2018  <pi@raspberrypi>
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
import SocketServer
import logging

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import call
from smarthome import *
from smartweb import *


def web_worker(mainLoopQueue,myHome):
	logging.info( "WEB Worker Spawned")
	
	server_class=HTTPServer
	handler_class=SmartWeb
	server_address = ('', 40000)
	
	handler_class.mainLoopQueue = mainLoopQueue
	handler_class.myHome = myHome
	
	httpd = server_class(server_address, handler_class)
   
   # Start Web Server
	httpd.serve_forever()


def fifo_worker(mainLoopQueue):
	
	logging.info("FIFO Worker Spawned")
	
	# Create FIFO File if needed
	path = "smart.fifo"
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
				
			if line=="off" or line=="on":
				mainLoopQueue.put({'cmd':"onoff", 'data':line})
						
		fifo.close()

def timer_worker(mainLoopQueue):
	logging.info("TIMER Worker Spawned")
	
	#Sleep and then notify parent
	while True:
		time.sleep(60)
		mainLoopQueue.put({'cmd':"Time", 'data':None})

def main():
	# Setup Logging
	log_level = logging.INFO
	logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=log_level)
	
	logging.info( "Smart App Started")
	
	#Create Smarthome
	with open("smarthome_config.json") as json_object:
		json_data = json.load(json_object)
		myHome = SmartHome("MyHome", json_data)
	
	# Create Queue
	mainLoopQueue = multiprocessing.Queue()
	
	#Spawn Threads
	fifo_thread = multiprocessing.Process(target=fifo_worker, args=(mainLoopQueue,))
	timer_thread = multiprocessing.Process(target=timer_worker, args=(mainLoopQueue,))
	web_thread = multiprocessing.Process(target=web_worker, args=(mainLoopQueue,myHome,))
	
	logging.info( "Smart App: Kicking off threads")
		
	#Start Threads
	fifo_thread.start()
	timer_thread.start()
	web_thread.start()
	
	#Main Loop
	while True:
		obj= mainLoopQueue.get()
		logging.debug("Smart App: Main Loop:Item:%s" % obj["cmd"])
		
		#Handle Timer Interupt
		if obj["cmd"]=="Time":
			myHome.refresh()
		
		# Handle Turning the System on or off
		if obj["cmd"]=="onoff":
			if obj["data"] == "on":
				onoff=True
			else:
				onoff=False
				
			myHome.set_on_off(onoff)
		
		#Handle Status
		if obj["cmd"]=="status":
			logging.info( "Show Status")
			logging.info( "--------------------")
			logging.info( "Home Name: "+ myHome.get_name())
			
			rooms = myHome.get_room_names()
			for room_name in rooms:
				logging.info( "-------------------")
				logging.info( "Room Name: " + room_name)
		
				aRoom = myHome.get_room(room_name)
				switches = aRoom.get_switch_devices()
				logging.info( ".........SWITCHES ..........")
				for switch_name in switches:
					aSwitch = aRoom.get_device(switch_name)
					logging.info( "Switch Name: " + switch_name)
					logging.info( "Switch State: " + str(aSwitch.query_state()))
			
				motion = aRoom.get_motion_devices()
				logging.info( "........MOTION ..........")
				for motion_name in motion:
					aMotion = aRoom.get_device(motion_name)
					logging.info( "Motion Sensor Name: " + motion_name)
					logging.info( "Motion Sensor State: " + str(aMotion.query_state()))
		
		# Handle Web Request
		if obj["cmd"]=="Web":
			myHome.handle_device_triggered(obj["data"])
		
		# Handle Exit
		if obj["cmd"]=="exit":
			logging.info( "Smart App: Quitting")
			fifo_thread.terminate()
			timer_thread.terminate()
			web_thread.terminate()
			return
			
	 

if __name__ == '__main__':
	main()
	

