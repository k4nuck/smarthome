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
from smartthings_cli import *
from smarthome import *

class S(BaseHTTPRequestHandler):
    mainLoopQueue=None
    smartthings=None
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        
        #Motion
        req = self.smartthings.smart_request(["query","motion","all"])
        motionReqStr=""
        	
        for device in req:
			motionReqStr+= device["name"]+" State: "+str(device["state"]) +"<br>"

        # Switches
        req = self.smartthings.smart_request(["query","switch","all"])
        switchReqStr=""
        	
        for device in req:
			switchReqStr+= device["name"]+" State: "+str(device["state"]) +"<br>"
			
        myHTML = "<html>" \
					"<body>" \
						"<h1> K4nuCK Home Dashboard</h1>" \
						"<h2>Motion Sensors</h2>" \
						"<p>"+motionReqStr+"</p>" \
						"<h2>Switches</h2>" \
						"<p>"+switchReqStr+"</p>" \
					"</body>" \
				 "</html>"
        
        self.wfile.write(myHTML)
        

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        
        self.mainLoopQueue.put({'cmd':"Web", 'data':post_body})
        
        #print post_body
        
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

def web_worker(mainLoopQueue,smartthings):
	print "JB - WEB Worker Spawned"
	
	#global MainLoopQueue
	#MainLoopQueue = mainLoopQueue
	
	server_class=HTTPServer
	#handler_class=S(mainLoopQueue)
	handler_class=S
	server_address = ('', 40000)
	
	handler_class.mainLoopQueue = mainLoopQueue
	handler_class.smartthings = smartthings
	
	httpd = server_class(server_address, handler_class)
    
	print 'JB - Starting httpd...'
	httpd.serve_forever()


def fifo_worker(mainLoopQueue):
	# Create FIFO File if needed
	#path = "/home/pi/projects/Smartthings/smart.fifo"
	path = "smart.fifo"
	if not os.path.exists(path):
		os.mkfifo(path)
	
	#Wait for Commands
	while True:
		fifo = open(path, "r")
		for line in fifo:
			print "Received: (" + line + ")\n",
			
			if line=="exit":
				mainLoopQueue.put({'cmd':line, 'data':None})
				
			if line=="status":
				mainLoopQueue.put({'cmd':line, 'data':None})
						
		fifo.close()

def timer_worker(mainLoopQueue):
	#Sleep and then notify parent
	while True:
		time.sleep(10)
		mainLoopQueue.put({'cmd':"Time", 'data':None})

def main():
	print "JB - Main Loop Start"
	
	# Setup Logging
	log_level = logging.INFO
	logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=log_level)
	logging.getLogger("requests").setLevel(logging.WARNING)
	
	#Create Smarttings Object
	smartthings = SmartThings()
	
	# Create Queue
	mainLoopQueue = multiprocessing.Queue()
	
	#Spawn Threads
	fifo_thread = multiprocessing.Process(target=fifo_worker, args=(mainLoopQueue,))
	timer_thread = multiprocessing.Process(target=timer_worker, args=(mainLoopQueue,))
	web_thread = multiprocessing.Process(target=web_worker, args=(mainLoopQueue,smartthings,))
	
	print "JB - Main Loop: Calling Start"
		
	#Start Threads
	fifo_thread.start()
	timer_thread.start()
	web_thread.start()
	
	#Main Loop
	while True:
		obj= mainLoopQueue.get()
		#print "JB - Main Loop:Item:%s" % obj
		
		#Handle Timer Interupt
		#if obj=="Time":
		#	print "JB - Wake up Time DO WORK!!!!"
		
		#Handle Status
		if obj["cmd"]=="status":
			print "JB - Show Status"
			#os.system("smartthings_cli query switch all")
			#os.system("smartthings_cli query motion all")
			#call(["ls", "-ltr"])
			
			#Switches - smartthings_cli.py vvvv
			req = smartthings.smart_request(["query","switch","all"])
			
			for device in req:
				print "---------------------"
				print "Type:"+device["type"]
				print "Name:"+device["name"]
				print "State:"+str(device["state"])
				
			#Motion
			req = smartthings.smart_request(["query","motion","all"])
			
			for device in req:
				print "---------------------"
				print "Type:"+device["type"]
				print "Name:"+device["name"]
				print "State:"+str(device["state"])
			
		
		if obj["cmd"]=="Web":
			print "JB = Main Loop: Web - Data:" + obj["data"]
			#obj["data"].wfile.write("<html><body><h1>K4nuCK Home Dashboard</h1></body></html>")
		
		# Handle Exit
		if obj["cmd"]=="exit":
			print "JB - Main Loop:Quitting"
			
			# Wait for the worker to finish
			#mainLoopQueue.close()
			#mainLoopQueue.join_thread()
			#pthread.join()
			
			print "JB - Main Loop:Item:Qutting:Done" 
			fifo_thread.terminate()
			timer_thread.terminate()
			web_thread.terminate()
			return
			
	 

if __name__ == '__main__':
	main()
	

