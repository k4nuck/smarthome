#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smarthomeutils.py
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

import sys
import logging
import time

from smarthomedb import *

class SmartHomeUtils:
	# Initialization
	def __init__ (self, dbname):
		logging.info("SmartHomeUtils: dbname:"+ str(dbname))
		
		if dbname == None:
			dbname = "smarthomedb"
		self.myHomeDB = SmartHomeDB(dbname)
		
	# Return number of seconds from datetime
	def get_seconds_from_datetime(self, t):
		return time.mktime(t.timetuple())
	
	# Return datetime from seconds
	def get_datetime_from_seconds(self, seconds):
		return datetime.datetime.fromtimestamp(seconds)
	
	# Get datetime from HH:MM
	def get_datetime_from_hh_mm(self, hh,mm):
		return datetime.time(hh,mm)
		
	# Get current timestamp
	def get_current_timestamp(self):
		return time.time()
	
	
	# Get DB Handle
	def get_db_handle(self):
		return self.myHomeDB
	
	# Return CurrentState Record
	def get_current_state_from_db(self):
		return self.get_db_handle().find_by_key("CurrentState")
		
	# Update Current State Record
	def commit_current_state_in_db(self, rec):
		self.get_db_handle().update("CurrentState",rec)
		
		
