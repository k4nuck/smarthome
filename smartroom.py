#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartroom.py
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
import datetime
from datetime import timedelta

from astral import Astral
import pywapi
from smartdevice import *

'''
	Keep Track of Devices in a Room
	EXAMPLE of use
	myRoom = SmartRoom("My Room")
	myRoom.add_device(SmartDevice("SAMSUNG", "switch", "Fan Outlet"))
	myRoom.add_device(SmartDevice("SAMSUNG", "switch", "Hallway Outlet"))
	
	print "Fan State: " + str(myRoom.get_device("Fan Outlet").query()[0]["state"])
	print "Hallway State: " + str(myRoom.get_device("Hallway Outlet").query()[0]["state"])
'''
class SmartRoom:
	CalendarInfo=None
	City = None
	Weather_Loc_Id = None
	WeatherInfo = None
	
	def __init__ (self, name):
		self.name = name
		self.devices = {}
		self.switch_devices=[]
		self.motion_devices=[]
		self.allow_force_off = True
		self.sunset_offset = 0
		self.sunrise_offset = 0
		self.weather_offset = 0
		self.nighttime_start = None
		self.nighttime_end = None
		self.current_mode = "default"
		
		# Only initialize once
		if SmartRoom.CalendarInfo == None:
			SmartRoom.CalendarInfo = self.update_calendar_info()
		if SmartRoom.WeatherInfo == None:
			SmartRoom.WeatherInfo = self.update_weather_info()
	
	
	# Set Mode for Room
	def set_mode(self, mode):
		self.current_mode = mode
		
	# Return Mode for a Room
	def get_mode(self):
		return self.current_mode
	
	# Set NIght Time Start
	def set_nighttime_start(self, timestamp):
		self.nighttime_start = timestamp
		
	# Get NIght Time Start
	def get_nighttime_start(self):
		return self.nighttime_start
		
	# Set Night time End
	def set_nighttime_end(self, timestamp):
		self.nighttime_end = timestamp
		
	# Get Night Time End
	def get_nighttime_end(self):
		return self.nighttime_end
	
	# Set offset in hours when it isn't sunny out
	def set_weather_offset(self, weather_offset):
		self.weather_offset = weather_offset
		
	# Get weather offset
	def get_weather_offset(self):
		return self.weather_offset
	
	# TRUE- Will allow a room to leave its devices off depending on weather and sunrise/sunset
	def set_allow_force_off(self, force_off):
		self.allow_force_off = force_off
		
	# Set offset in hours from sunset (for forcing leaving the system off for a room)
	def set_sunset_offset(self, sunset_offset):
		self.sunset_offset = sunset_offset
		
	# Set offset in hours from sunrise (for forcing leaving the system off for a room)
	def set_sunrise_offset(self, sunrise_offset):
		self.sunrise_offset = sunrise_offset
		
	# Return if this room should be allowed to keep devices off
	def get_allow_force_off(self):
		return self.allow_force_off
		
	# Return sunset offset
	def get_sunset_offset(self):
		return self.sunset_offset
		
	# Return sunrise offset
	def get_sunrise_offset(self):
		return self.sunrise_offset
		
	# Get Calendar infor from Astral (Sunrise/Sunset)
	def update_calendar_info(self):
		calendarInfo = {}
		
		# From Config 
		city_name = SmartRoom.City
		astral = Astral()
		astral.solar_depression = 'civil'

		logging.info("Update Calendar Info:City:"+ str(city_name))

		# Get City Data
		city = astral[city_name]
		
		# Sun Data for City
		date=datetime.date.today()
		sun = city.sun(date, local=True)
		
		logging.info("Update Calendar Info:"+ str(date))
		
		# Update Calendar Info
		calendarInfo["current_date"] = date
		calendarInfo["sun"] = sun
		
		return calendarInfo
	
	# Get Weather information from weather.com
	def update_weather_info(self):
		weatherInfo={}
		
		#From Config
		weather_loc_id = SmartRoom.Weather_Loc_Id
		
		try:
			# Weather Data
			date=datetime.date.today()
			logging.info("Update Weather Info:loc id:"+weather_loc_id)
			weather = pywapi.get_weather_from_weather_com(weather_loc_id)
		
			logging.info("Update Weather Info:Location:"+ str(weather["location"]["name"]))
		
			# Update Weather Info
			weatherInfo["current_date"] = date
			weatherInfo["timestamp"] = time.time()
			weatherInfo["location"] = weather["location"]["name"]
			weatherInfo["day_of_week"] = weather["forecasts"][0]["day_of_week"]
			forecast = weather["forecasts"][0]["day"]["brief_text"]
		
			if forecast =="":
				forecast = weather["forecasts"][0]["night"]["brief_text"]
			
			weatherInfo["forecast"] = forecast
			weatherInfo["error"] = 0
		
			logging.info("Weather Info:day:"+ weatherInfo["day_of_week"])
			logging.info("Weather Info:Forecast:"+weatherInfo["forecast"])
		except:
			logging.critical("Update Weather Info: Getting Weather Data Failed")
			weatherInfo["current_date"] = date
			weatherInfo["timestamp"] = time.time()
			weatherInfo["location"] = "Unknown Location"
			weatherInfo["day_of_week"] = "Unknown Day of Week"
			weatherInfo["forecast"] = "Unknown Weather Conditions"
			weatherInfo["error"] = 1
			
		return weatherInfo
		
	# Return astral object (Update it if it is a new day)
	def get_sun_data(self):
		# Check if sun data needs to update
		current_date = SmartRoom.CalendarInfo["current_date"]
		date=datetime.date.today()
		
		if date != current_date:
			logging.info("Get Sun Data: NEW DATE: Updating current_date:"+ str(current_date)+" with:"+ str(date))
			SmartRoom.CalendarInfo = self.update_calendar_info()
			
		return SmartRoom.CalendarInfo["sun"]
		
	# Return Weather object (Update it if it is a new day)
	def get_weather_data(self):
		#check if weather data needs to be updated
		current_date = SmartRoom.WeatherInfo["current_date"]
		date=datetime.date.today()
		
		if date != current_date:
			logging.info("Get Weather Data: NEW DATE: Updating current_date:"+ str(current_date)+" with:"+ str(date))
			SmartRoom.WeatherInfo = self.update_weather_info()
		
		# Also Refresh after an hour
		current_timestamp = SmartRoom.WeatherInfo["timestamp"]
		timestamp = time.time()
		
		# On Error try again after 5 min
		if SmartRoom.WeatherInfo["error"] != 0 and (timestamp - current_timestamp > 300):
			logging.info("Get Weather Data: Refresh Because of Bad Weather Data")
			SmartRoom.WeatherInfo = self.update_weather_info()
		
		if timestamp - current_timestamp > 3600:
			logging.info("Get Weather Data: HOUR PAST")
			SmartRoom.WeatherInfo = self.update_weather_info()
			
		return SmartRoom.WeatherInfo
	
	# Add a Device to a Room
	def add_device(self, device):
		# Keep track of switches and motion sensors names
		# Also the key to devices dictionary
		device_name = device.get_device_name()
		device_type = device.get_device_type()
		if device_type=="motion":
			self.motion_devices.append(device_name)
		elif device_type=="switch":
			self.switch_devices.append(device_name)
			
		# Map of devices in a room
		self.devices[device_name] = device
		
	# Return a device by name from a room
	def get_device(self, device_name):
		return self.devices[device_name]
		
	# Return a list of motion sensor devices
	def get_motion_devices(self):
		return self.motion_devices
		
	# Return a list of switch devices
	def get_switch_devices(self):
		return self.switch_devices
		
	# Return the name of the room
	def get_name(self):
		return self.name	
		
	# CHeck real status of a motion sensor and update if still active
	def refresh_last_active(self):
		for device_name in self.motion_devices:
			device = self.get_device(device_name)
			if device.query_state():
				device.set_last_active()
		
	# Check last time room had movement
	def get_last_active(self):
		# If Room should be off then return 0
		# Do this for the scenario where Force Off is on but the 
		# lights were already on.  Want them to turn off
		if self.should_lights_stay_off():
			return 0
		
		last_active = None
		for device_name in self.motion_devices:
			device = self.get_device(device_name)
			
			logging.debug("Get Last Active:"+device_name)
			logging.debug("Device Time:"+ str(device.get_last_active()))
			logging.debug("Device ID:"+str(hex(id(device))))
			
			if(last_active ==None):
				last_active = device.get_last_active()
			elif(last_active < device.get_last_active()):
				last_active = device.get_last_active()
		return last_active
		
	#Check if Lights should be allowed on in this room
	def should_lights_stay_off(self):
		# Check if in nighttime mode .. Overrides if Room doesnt allow forcing off.
		if self.nighttime_mode():
			logging.debug("Should lights stay off:Night Time mode")
			return True
		
		# First Check if this Room ever forces off
		if not self.get_allow_force_off():
			logging.debug("should_lights_stay_off:NEVER:"+self.get_name())
			return False
			
		sunset_offset = self.get_sunset_offset()
		sunrise_offset = self.get_sunrise_offset()
		
		logging.debug("In should_lights_stay_off")
		lights_stay_off = False
		sun = self.get_sun_data()
		weather = self.get_weather_data()
		
		forecast = weather["forecast"]
		
		#If it isnt somewhat Sunny out or Clearthen offset with weather_offset
		if forecast.find("Sunny")== -1 and forecast.find("Clear")==-1 and forecast.find("P Cloudy"):
			weather_offset = self.get_weather_offset()
			sunset_offset += weather_offset
			sunrise_offset += weather_offset
		
		logging.debug("Lights Stay Off: sunset_offset:"+ str(sunset_offset))
		logging.debug("Lights Stay Off: sunrise_offset:"+ str(sunrise_offset))
		
		# Sunset and Sunrise Information
		# Offset by an hour window
		sunset = sun['sunset'] - timedelta(hours=sunset_offset)
		sunrise = sun['sunrise'] + timedelta(hours=sunrise_offset)

		logging.debug("Sunset(offset):"+ str(sunset))
		logging.debug("Sunrise(offset):"+ str(sunrise))

		# Get Current Time taking time zone into account
		tz_info = sunset.tzinfo
		currentTime = datetime.datetime.now(tz_info)
		
		logging.debug("Current Time:"+str(currentTime))
		
		if currentTime > sunset:
			logging.debug ("should_lights_stay_off:After Sunset:"+ self.get_name())
		else:
			if currentTime < sunrise:
				logging.debug ("should_lights_stay_off:Before Sunrise:"+ self.get_name())
			else:
				logging.debug ("should_lights_stay_off:Keep Lights Off:"+ self.get_name())
				lights_stay_off = True
		
		
		return lights_stay_off
		
	# Return true if Room currently is in nighttime mode
	# Meaning the lights shouldn't go on
	def nighttime_mode(self):
		current = datetime.datetime.now()
		
		# If Current is after start and end ... add a Day to both because it is the next day
		if (current > self.get_nighttime_start()) and (current > self.get_nighttime_end()):
			self.set_nighttime_start(self.get_nighttime_start()+ timedelta(days=1))
			self.set_nighttime_end(self.get_nighttime_end()+timedelta(days=1))
			
		# We are in nighttime mode
		elif (current > self.get_nighttime_start()) and (current < self.get_nighttime_end()):
			return True
		
		return False
	
	# Turn all Switches on in a room			
	def turn_switches_on_in_room(self):
		if self.should_lights_stay_off():
			logging.debug("Turn Switches On:  KEEP OFF!!")
			return
		
		for device_name in self.get_switch_devices():
			device = self.get_device(device_name)
			device.set_on()
	
	# Turn all Switches off in a room		
	def turn_switches_off_in_room(self):	
		for device_name in self.get_switch_devices():
			device = self.get_device(device_name)
			device.set_off()
