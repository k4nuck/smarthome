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
import SocketServer
import json
import logging
from logging.handlers import RotatingFileHandler

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import call
from smartwebhost import *

# Process to Handle all Web Events
def web_worker(guest_key, admin_key, port, post_address):
	logging.info( "WEB Worker Spawned:" + str(port) + ":Post address:" + post_address)
	
	server_class=HTTPServer
	handler_class=SmartWebHost
	
	server_address = ('', port)
	handler_class.guest_key = guest_key
	handler_class.admin_key = admin_key
	handler_class.post_address = post_address
	
	httpd = server_class(server_address, handler_class)
   
   # Start Web Server
	httpd.serve_forever()

# Process for sending commands to the server from command line
def fifo_worker(mainLoopQueue):
	
	logging.info("FIFO Worker Spawned")
	
	# Create FIFO File if needed
	path = "/home/pi/projects/smarthome/smartweb/smartweb.fifo"
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

# Main Server
def main():
	# Setup Logging
	log_level = logging.INFO
	logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=log_level)
	hdlr = RotatingFileHandler("/home/pi/projects/smarthome/smartweb/smartweb.log", maxBytes=(1048576*5), backupCount=5)
	logger = logging.getLogger("")
	formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	
	logging.info( "Smart Web Started")
	
	# Get Webkey
	with open("/home/pi/.smarthome_key.json") as webkey_object:
		webkey_data = json.load(webkey_object)
		guest_key = webkey_data["webkey"]["guest"]
		admin_key = webkey_data["webkey"]["admin"]
		port = webkey_data["webkey"]["port"]
		post_address = webkey_data["webkey"]["post_address"]
		
		logging.debug("guest:"+guest_key+":admin:"+admin_key)
	
	# Create Queue
	mainLoopQueue = multiprocessing.Queue()
	
	#Spawn Threads
	fifo_thread = multiprocessing.Process(target=fifo_worker, args=(mainLoopQueue,))
	web_thread = multiprocessing.Process(target=web_worker, args=(guest_key, admin_key, port, post_address))
	
	logging.info( "Smart Web: Kicking off threads")
		
	#Start Threads
	fifo_thread.start()
	web_thread.start()
	
	#Main Loop
	while True:
		obj= mainLoopQueue.get()
		logging.debug("Smart Web: Main Loop:Item:%s" % obj["cmd"])
		
		#Handle Status
		if obj["cmd"]=="status":
			logging.info( "Show Status")
		
		# Handle Exit
		if obj["cmd"]=="exit":
			logging.info( "Smart Web: Quitting")
			fifo_thread.terminate()
			web_thread.terminate()
			return
			
	 

if __name__ == '__main__':
	main()
	

