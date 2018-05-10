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

import couchdb
import logging

class SmartHomeDB:
	DB=None
	
	def __init__ (self):
		logging.info("Creating SmartHomeDB")
		
		if SmartHomeDB.DB == None:
			couchserver = couchdb.Server("http://127.0.0.1:5984/")
			dbname = "mydb"  #JB - Change the name to proper DB
			if dbname in couchserver:
				logging.info("Found DB in Server")
				SmartHomeDB.DB = couchserver[dbname]
			else:
				logging.info("Creating DB in Server")
				SmartHomeDB.DB = couchserver.create(dbname)
	
	# Updates or Adds Record to the DB
	def update(self, key, record):
		try:
			logging.info("SmartHomeDB Update:key:"+key+":record:"+str(record))
			SmartHomeDB.DB[key] = record
		except:
			logging.error("SmartHomeDB Failed Update:Key:"+key+":record:"+str(record))
			
	# Find a Record by key
	def find_by_key(self,key):
		try:
			logging.info("SmartHomeDB: Find by Record:"+key)
			return SmartHomeDB.DB[key]
		except:
			logging.error("SmartHomeDB Failed to find by key:"+key)
			return None # JB - Probably want to return a default record.  Think about this

# JB - For Testing
if __name__ == '__main__':
	log_level = logging.INFO
	logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=log_level)
	
	myHomeDB = SmartHomeDB()
	
	myHomeDB.update("Joe",{"Test":"This is a test"})
	
	logging.info("Record from DB:"+str(myHomeDB.find_by_key("Joe")))
	
