#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartwebhost.py
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
import requests


sys.path.append("/home/pi/projects/smarthome/") 

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from smarthomeutils import *

class SmartWebHost(BaseHTTPRequestHandler):
    guest_key = None
    admin_key = None
    post_address = None
    
    def log_message(self, format, *args):
		return
		
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    # Dash Board    
    def get_status_html_from_db(self, guestMode, adminMode):
        logging.info("SmartWeb:Getting Status:Guest:"+str(guestMode)+":admin:"+str(adminMode))
		
        # JB - Will be used in the future to display status
        
        logging.info("SmartWeb:Getting Status:Creating HTML")
        
        myHTMLlist=[]
        
        myHTMLlist.append("<html>")
        myHTMLlist.append("<body>")
        myHTMLlist.append("<h1>K4nuCK Home Dashboard</h1>")
        
        if adminMode:
			mode = "ADMIN Mode"
        else:
			mode = "GUEST Mode"
        
        myHTMLlist.append("<p style=\"text-indent :2em;\">"+mode+"</p>")
        myHTMLlist.append("</body>")
        myHTMLlist.append("</html>")
        
        logging.info("SmartWeb:Getting Status:html done:")
        
        return ''.join(myHTMLlist)
        
    # Return HTML
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
			logging.info("SmartWeb:No Access")
			self.wfile.write("<html><body><h1>Access Denied</h1></body></html>")
			return
			
        # Get HTML		
        myHTML = self.get_status_html_from_db(guestMode, adminMode)
        
        logging.info("SmartWeb:HTML:"+myHTML)
        
        self.wfile.write(myHTML)
        

    def do_HEAD(self):
        self._set_headers()
        
    # JB - Event Handler from Post    
    def handle_event(self, data):
		logging.info("SmartWeb:Handle_Event:data:"+data)
		
		return "Event Handled"
        
    # Handle events sent to server
    def do_POST(self):
        self._set_headers()
        
        logging.info("SmartWeb:GOT A POST")
        
        # Get and store data
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        
        # Return Success immediately        
        self.wfile.write("Success")
        
        # Process Event and get back data to send back to node red server
        data = self.handle_event(post_body)
        
        # Send data back
        url = self.post_address
        
        logging.info("SmartWeb:url:" + url)
        
        ret = requests.post(url, data)
        
        logging.info("Return from post:"+ret.text)
