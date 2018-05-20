#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartweb.py
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
from smarthome import *
from smarthomeutils import *

class SmartWeb(BaseHTTPRequestHandler):
    mainLoopQueue=None
    myHome=None
    guest_key = None
    admin_key = None
    system_status = True
    
    def log_message(self, format, *args):
		return
		
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def get_status_html_from_db(self, guestMode, adminMode):
        logging.info("SmartWebDB:Getting Status:Guest:"+str(guestMode)+":admin:"+str(adminMode))
		
        # Get Current State from DB
        home_util = SmartHomeUtils()
        rec = home_util.get_current_state_from_db()
        logging.debug("SmartWebDB:rec:"+str(rec))
        
        date = datetime.datetime.fromtimestamp(rec["timestamp"])
        
        myHTMLlist=[]
        
        myHTMLlist.append("<html>")
        myHTMLlist.append("<body>")
        myHTMLlist.append("<h1>K4nuCK Home Dashboard</h1>")
        myHTMLlist.append("<p style=\"text-indent :2em;\">Last Update: "+str(date)+"</p>")
        myHTMLlist.append("<p style=\"text-indent :2em;\">System Status:"+str(self.system_status)+" - Admin:"+str(adminMode)+"</p>")
        
        refresh = home_util.get_datetime_from_seconds(rec["refresh_time"])
        activity = home_util.get_datetime_from_seconds(rec["activity_time"])
        
        myHTMLlist.append("<p style=\"text-indent :2em;\">Refresh Reset Time:"+str(refresh)+" - Activity Reset Time:"+str(activity)+"</p>")
        
        rooms = rec["rooms"]
        for rec_room in rooms:
			room_name = rec_room["name"]
			mode = rec_room["mode"]
			
			myHTMLlist.append("<h2>"+room_name+" - Mode: "+mode+"</h2>")
			
			# Room Info
			allow_force_off = rec_room["allow_force_off"]
			lights_stay_off = rec_room["lights_stay_off"]
			nighttime_mode = rec_room["nighttime_mode"] 
			nighttime_start = home_util.get_datetime_from_seconds(rec_room["nighttime_start"])
			nighttime_end = home_util.get_datetime_from_seconds(rec_room["nighttime_end"])
			
			# Sun Info
			sunrise = home_util.get_datetime_from_seconds(rec_room["sunrise"])
			sunset = home_util.get_datetime_from_seconds(rec_room["sunset"])
			sunrise_offset = rec_room["sunrise_offset"]
			sunset_offset = rec_room["sunset_offset"]
			
			# Weather Info
			weather_offset = rec_room["weather_offset"]
			forecast = rec_room["forecast"]
			location = rec_room["location"]
			day_of_week = rec_room["day_of_week"]
			
			myHTMLlist.append("<p style=\"text-indent :2em;\">Sunrise: "+str(sunrise)+" - Sunset: "+str(sunset)+" - Force Lights Off: "+str(lights_stay_off)+"</p>")
			
			if allow_force_off:
				myHTMLlist.append("<p style=\"text-indent :2em;\">Sunrise Offset: "+str(sunrise_offset) + " hours - Sunset Offset:"+str(sunset_offset)+" hours</p>")
				myHTMLlist.append("<p style=\"text-indent :2em;\">Location: "+location+" - Day of Week: " +day_of_week+ " - Forecast: "+forecast+" - Weather Offset: "+str(weather_offset)+" hours</p>")
			else:
				myHTMLlist.append("<p style=\"text-indent :2em;\">DO NOT ALLOW FORCE OFF</p>")
				
		    
			myHTMLlist.append("<p style=\"text-indent :2em;\">Night Time Mode: "+str(nighttime_mode)+" - Night Time Start: "+str(nighttime_start)+" - Night Time End: "+str(nighttime_end)+"</p>")
			
			# Switches
			myHTMLlist.append("<h3>Switches</h3>")
			switches = rec_room["switches"]
			for rec_device in switches:
				device_name = rec_device["name"]
				state = rec_device["state"]
				myHTMLlist.append("<p style=\"text-indent :2em;\">"+device_name+": "+str(state)+"</p>")
				
		    # Motion Sensors
			myHTMLlist.append("<h3>Motion Sensors</h3>")
			motions = rec_room["motions"]
			for rec_device in motions:
				device_name = rec_device["name"]
				state = rec_device["state"]
				myHTMLlist.append("<p style=\"text-indent :2em;\">"+device_name+": "+str(state)+"</p>")
		    
        myHTMLlist.append("</body>")
        myHTMLlist.append("</html>")
        
        return ''.join(myHTMLlist)
        
    # Return HTML that shows the status of the system
    def get_status_html(self, guestMode, adminMode):
        logging.info("SmartWeb:Getting Status:Guest:"+str(guestMode)+":admin:"+str(adminMode))
		
        myHTMLlist=[]
        
        myHTMLlist.append("<html>")
        myHTMLlist.append("<body>")
        myHTMLlist.append("<h1>K4nuCK Home Dashboard</h1>")
        myHTMLlist.append("<p style=\"text-indent :2em;\">System Status:"+str(self.system_status)+" - Admin:"+str(adminMode)+"</p>")
        
        refresh = self.myHome.get_refresh_time()
        activity = self.myHome.get_activity_time()
        
        myHTMLlist.append("<p style=\"text-indent :2em;\">Refresh Reset Time:"+str(refresh)+" - Activity Reset Time:"+str(activity)+"</p>")
        
        rooms = self.myHome.get_room_names()
        for room_name in rooms:
			aRoom = self.myHome.get_room(room_name)
			myHTMLlist.append("<h2>"+room_name+" - Mode: "+aRoom.get_mode()+"</h2>")
			
			#Some Room Info
			sun = aRoom.get_sun_data()
			lights_stay_off = aRoom.should_lights_stay_off()
			weather = aRoom.get_weather_data()
			weather_offset = aRoom.get_weather_offset()
			forecast = weather["forecast"]
			day_of_week = weather["day_of_week"]
			location = weather["location"]
			
			myHTMLlist.append("<p style=\"text-indent :2em;\">Sunrise: "+str(sun["sunrise"])+" - Sunset: "+str(sun["sunset"])+" - Force Lights Off: "+str(lights_stay_off)+"</p>")
			if aRoom.get_allow_force_off():
				myHTMLlist.append("<p style=\"text-indent :2em;\">Sunrise Offset: "+str(aRoom.get_sunrise_offset()) + " hours - Sunset Offset:"+str(aRoom.get_sunset_offset())+" hours</p>")
				myHTMLlist.append("<p style=\"text-indent :2em;\">Location: "+location+" - Day of Week: " +day_of_week+ " - Forecast: "+forecast+" - Weather Offset: "+str(weather_offset)+" hours</p>")
			else:
				myHTMLlist.append("<p style=\"text-indent :2em;\">DO NOT ALLOW FORCE OFF</p>")
				
			myHTMLlist.append("<p style=\"text-indent :2em;\">Night Time Mode: "+str(aRoom.nighttime_mode())+" - Night Time Start: "+str(aRoom.get_nighttime_start())+" - Night Time End: "+str(aRoom.get_nighttime_end())+"</p>") 	
				
			#Switches
			devices = aRoom.get_switch_devices()
			myHTMLlist.append("<h3>Switches</h3>")
			for device_name in devices:
				aDevice = aRoom.get_device(device_name)
				state = aDevice.query_state()
				myHTMLlist.append("<p style=\"text-indent :2em;\">"+device_name+": "+str(state)+"</p>")
				
			#Motion Sensors
			devices = aRoom.get_motion_devices()
			myHTMLlist.append("<h3>Motion Sensors</h3>")
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
			
        # Check if we want to get web page from DB
        if self.path.find("notfromdb") != -1:
			fromdb = False
        else:
			fromdb = True
			
		#JB - MAke a Generic routine for this.
		#     Also do not hard code mode names
		#     Should work for do_POST as well
        #If Admin Check if System is enabled/disabled
        if adminMode:
			if self.path.find("system=on") != -1:
				logging.info("SmartWeb:Enabling System")
				SmartWeb.system_status = True
				self.mainLoopQueue.put({'cmd':"onoff", 'data':"on"})
				
			if self.path.find("system=off") != -1:
				logging.info("SmartWeb:Disabling System")
				SmartWeb.system_status = False
				self.mainLoopQueue.put({'cmd':"onoff", 'data':"off"})
				
			if self.path.find("mode=dayoff")!=-1:
				logging.info("SmartWeb:Setting Mode to dayoff")
				self.mainLoopQueue.put({'cmd':"mode", 'data':"dayoff"})
				# Update the "web" object so that it stays in sync with the main Smart Home Object
				SmartWeb.myHome.set_mode("dayoff")
				
			if self.path.find("mode=default")!=-1:
				logging.info("SmartWeb:Setting Mode to default")
				self.mainLoopQueue.put({'cmd':"mode", 'data':"default"})
				# Update the "web" object so that it stays in sync with the main Smart Home Object
				SmartWeb.myHome.set_mode("default")
        
        # Show Status of Sensors and Switches
        if fromdb:
			myHTML = self.get_status_html_from_db(guestMode, adminMode)
        else:
			myHTML = self.get_status_html(guestMode, adminMode)
        
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
			SmartWeb.system_status = True
			self.mainLoopQueue.put({'cmd':"onoff", 'data':"on"})		
        elif post_body.find("system=off") != -1:
			logging.info("SmartWeb:Disabling System from ALEXA")
			SmartWeb.system_status = False
			self.mainLoopQueue.put({'cmd':"onoff", 'data':"off"})
        elif post_body.find("mode=dayoff")!= -1:
			logging.info("SmartWeb:Setting Mode to dayoff from ALEXA")
			self.mainLoopQueue.put({'cmd':"mode", 'data':"dayoff"})
			# Update the "web" object so that it stays in sync with the main Smart Home Object
			SmartWeb.myHome.set_mode("dayoff")
        elif post_body.find("mode=default")!= -1:
			logging.info("SmartWeb:Setting Mode to default  from ALEXA")
			self.mainLoopQueue.put({'cmd':"mode", 'data':"default"})
			# Update the "web" object so that it stays in sync with the main Smart Home Object
			SmartWeb.myHome.set_mode("default")
        else:
			# Send Update back to Main
			self.mainLoopQueue.put({'cmd':"Web", 'data':post_body})
        
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
