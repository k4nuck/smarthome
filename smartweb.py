#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import SocketServer
import logging
import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from smarthome import *

class SmartWeb(BaseHTTPRequestHandler):
    mainLoopQueue=None
    myHome=None
    
    def log_message(self, format, *args):
		return
		
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def get_status_html(self):
        logging.info("SmartWeb:Getting Status")
		
        myHTMLlist=[]
        
        myHTMLlist.append("<html>")
        myHTMLlist.append("<body>")
        myHTMLlist.append("<h1>K4nuCK Home Dashboard</h1>")
        
        rooms = self.myHome.get_room_names()
        for room_name in rooms:
			myHTMLlist.append("<h2>"+room_name+"</h2>")
			aRoom = self.myHome.get_room(room_name)
			
			#Motion Sensors
			devices = aRoom.get_motion_devices()
			myHTMLlist.append("<h3>Motion Sensors</h3>")
			for device_name in devices:
				aDevice = aRoom.get_device(device_name)
				state = aDevice.query_state()
				myHTMLlist.append("<p style=\"text-indent :2em;\">"+device_name+": "+str(state)+"</p>")
				
			#Switches
			devices = aRoom.get_switch_devices()
			myHTMLlist.append("<h3>Switches</h3>")
			for device_name in devices:
				aDevice = aRoom.get_device(device_name)
				state = aDevice.query_state()
				myHTMLlist.append("<p style=\"text-indent :2em;\">"+device_name+": "+str(state)+"</p>")
			
        
        myHTMLlist.append("</body>")
        myHTMLlist.append("</html>")
        
        return ''.join(myHTMLlist)

    def do_GET(self):
        self._set_headers()
        
        logging.debug("do_GET:path:" + self.path)
        
        # JB - FUTURE: Return a Proper Icon
        if self.path.find("favicon.ico") != -1:
			# Found Icon Request
			logging.debug("do_GET:Found Icon Request")
			self.wfile.write("<html><body></body></html>")
			return
        
        # Show Status of Sensors and Switches
        myHTML = self.get_status_html()
        self.wfile.write(myHTML)
        

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        
        # Send Update back to Main
        self.mainLoopQueue.put({'cmd':"Web", 'data':post_body})
        
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
