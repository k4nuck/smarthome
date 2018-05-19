#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smarthomedb.py
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
import couchdb
import logging
import datetime, time

'''
' Generic Interface to Couchdb to store Smarthome Data
' Currently Supports Add/Update by Key (SmartHomeDB.update)
' Currently Support Find By Key (SmartHomeDB.find_by_key)
'''
class SmartHomeDB:
	DB=None
	
	def __init__ (self):
		logging.info("Creating SmartHomeDB")
		
		if SmartHomeDB.DB == None:
			couchserver = couchdb.Server("http://127.0.0.1:5984/")
			dbname = "smarthomedb" 
			if dbname in couchserver:
				logging.info("Found DB in Server:"+dbname)
				SmartHomeDB.DB = couchserver[dbname]
			else:
				logging.info("Creating DB in Server:"+dbname)
				SmartHomeDB.DB = couchserver.create(dbname)
	
	# Updates or Adds Record to the DB
	def update(self, key, record):
		try:
			logging.debug("SmartHomeDB Update:key:"+key+":record:"+str(record))
			
			# Check if Document already exists
			#UPDATE
			if key in SmartHomeDB.DB:
				rec = SmartHomeDB.DB[key]
				rec["MyHome"] = record
				SmartHomeDB.DB.save(rec)
			#ADD
			else:
				SmartHomeDB.DB[key] = {"MyHome":record}
		except:
			logging.error("SmartHomeDB Failed Update:Error:"+str(sys.exc_info()[0])+":Key:"+key+":record:"+str(record))
			
	# Find a Record by key
	def find_by_key(self,key):
		try:
			logging.debug("SmartHomeDB: Find by Record:"+key)
			return SmartHomeDB.DB[key]["MyHome"]
		except:
			logging.error("SmartHomeDB Failed to find by key:"+key)
			return None # JB - Probably want to return a default record.  Think about this

# JB - For Testing
if __name__ == '__main__':
	log_level = logging.INFO
	logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=log_level)
	
	# Uncomment to Test Adding to DB
	'''
	status = True
	refresh = 300
	activity = 600
	rooms = []
	rooms.append({})
	rooms.append({})
	
	#Some Room Info
	name = "Living Room"
			
	# Get start hh and mm and create a datetime object
	current = datetime.datetime.now()
	hh = 9
	mm = 35
	t = datetime.datetime(current.year,current.month, current.day,hh,mm)
	sunrise = time.mktime(t.timetuple())
	#sunrise = "DATEINFO"
	
	rooms[0]["name"] = name
	rooms[0][ "sunrise"] = sunrise
	
	#-------
	
	#Some Room Info
	name = "Kitchen"
			
	# Get start hh and mm and create a datetime object
	current = datetime.datetime.now()
	hh = 10
	mm = 35
	t = datetime.datetime(current.year,current.month, current.day,hh,mm)
	sunrise = time.mktime(t.timetuple())
	#sunrise = "DATE INFO"
	
	rooms[1]["name"] = name
	rooms[1][ "sunrise"] = sunrise
	
	record = {"status":status, "refresh":refresh, "activity":activity, "rooms":rooms}
	
	#---------
	
	myHomeDB = SmartHomeDB()
	
	myHomeDB.update("Joe3",record)
	'''
	
	# Test Getting Current Record
	myHomeDB = SmartHomeDB()
	rec = myHomeDB.find_by_key("CurrentState")
	logging.info("Record from DB:"+str(rec))
	date = datetime.datetime.fromtimestamp(rec["timestamp"])
	logging.info("Timestamp:"+str(date))
	
	# Test Converting Date Back
	'''
	date = datetime.datetime.fromtimestamp(rec["rooms"][0]["sunrise"])
	logging.info("Sunrise:"+ str(date))
	
	date = datetime.datetime.fromtimestamp(rec["rooms"][1]["sunrise"])
	logging.info("Sunrise:"+ str(date))
	'''
