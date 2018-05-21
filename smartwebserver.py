#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartwebserver.py
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
import SocketServer
import logging
import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class SmartWeb(BaseHTTPRequestHandler):
    mainLoopQueue=None
    guest_key = None
    admin_key = None
    
    def log_message(self, format, *args):
		return
		
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        
        logging.debug("do_GET:path:" + self.path)
        
        # JB - FUTURE: Return a Proper Icon
        if self.path.find("favicon.ico") != -1:
			# Found Icon Request
			logging.debug("do_GET:Found Icon Request")
			self.wfile.write("<html><body></body></html>")
			return
        
        #Check for guest or admin key
        if self.path.find(self.guest_key) != -1:
			guestMode=True
			adminMode=False
        elif self.path.find(self.admin_key) != -1:
			guestMode = False
			adminMode = True
        else:
			#NO ACCESS
			self.wfile.write("<html><body><h1>Access Denied</h1></body></html>")
			return
			
        #JB - MAke a Generic routine for this.
		#     Also do not hard code mode names
		#     Should work for do_POST as well
        #If Admin Check if System is enabled/disabled
        if adminMode:
			if self.path.find("system=on") != -1:
				logging.info("SmartWeb:Enabling System")
				self.mainLoopQueue.put({'cmd':"onoff", 'data':"on"})
				
			if self.path.find("system=off") != -1:
				logging.info("SmartWeb:Disabling System")
				self.mainLoopQueue.put({'cmd':"onoff", 'data':"off"})
				
			if self.path.find("mode=dayoff")!=-1:
				logging.info("SmartWeb:Setting Mode to dayoff")
				self.mainLoopQueue.put({'cmd':"mode", 'data':"dayoff"})
				
			if self.path.find("mode=default")!=-1:
				logging.info("SmartWeb:Setting Mode to default")
				self.mainLoopQueue.put({'cmd':"mode", 'data':"default"})
		
        # JB - Show some status 		
        myHTML = "<html><body><h1>Access Granted</h1></body></html>"
        
        self.wfile.write(myHTML)
        

    def do_HEAD(self):
        self._set_headers()
        
    # IFTTT gets events from Motion Sensors being triggered and sends the event to this web server
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        
        if post_body.find("system=on") != -1:
			logging.info("SmartWeb:Enabling System from ALEXA")
			self.mainLoopQueue.put({'cmd':"onoff", 'data':"on"})		
        elif post_body.find("system=off") != -1:
			logging.info("SmartWeb:Disabling System from ALEXA")
			self.mainLoopQueue.put({'cmd':"onoff", 'data':"off"})
        elif post_body.find("mode=dayoff")!= -1:
			logging.info("SmartWeb:Setting Mode to dayoff from ALEXA")
			self.mainLoopQueue.put({'cmd':"mode", 'data':"dayoff"})
        elif post_body.find("mode=default")!= -1:
			logging.info("SmartWeb:Setting Mode to default  from ALEXA")
			self.mainLoopQueue.put({'cmd':"mode", 'data':"default"})
        else:
			# Send Update back to Main
			self.mainLoopQueue.put({'cmd':"Web", 'data':post_body})
        
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
