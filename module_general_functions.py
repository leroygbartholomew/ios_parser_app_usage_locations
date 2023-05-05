# This is a library containg functions that can be used with other
# Python scripts for parsing iOS BIOME data.  These are some of the 
# functions used by several different modules.             
#
# Version 1.0
# Date  2023-04-03
# Copyright (C) 2023 - Aaron Dee Roberts
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>
# ======================================================================
# FUNCTIONS LIST: ======================================================
# ======================================================================

#
# FOR CONVERTING A CONVENTIONAL DATE/TIME WITH SECONDS TO MAC ABSOLUTE TIME (SECONDS SINCE 2000-01-01 00:00:00)
# def datetime_to_mactime(timestamp):
# ======================================================================

# import sys
import os
import datetime
# import re
import struct # for date decode
import sqlite3
from sqlite3 import OperationalError


# FOR CONVERTING A CONVENTIONAL DATE/TIME WITH SECONDS TO MAC ABSOLUTE TIME (SECONDS SINCE 2000-01-01 00:00:00)
def datetime_to_epoch(timestamp, epoch = 'mac_absolute'):
	# times: mac_absolute, unix, unix_millisecond, unix_microsecond
	# Requires import datetime, import time
	# Needs time accurate to seconds and 4 digit year (EX: 2023-04-20 12:02:15)
	# Very flexible and does not matter if year or month are first OR if "-" or "/" is used.  
	# One or two spaces need to be between the date and time.  
	# AM and PM can be used along with the UTC amount (EX: UTC-5).  The code will adjust it all accordingly. 
	# Returns "INVALID" if the format is incorrect.
	
	date_time = timestamp
	
	# SETTING CERTAIN VARIABLES TO MAKE SURE THEY HAVE DEFAULTS
	is_pm = False
	is_tz = False
	t_offset = '0'
	
	# GET RID OF THE ( AND ) THAT MAY BE AROUND THE UTC
	x = '(' in date_time
	if x == True:
		y = date_time.replace('(', '')
		date_time = y
	y = None
	x = None

	x = ')' in date_time
	if x == True:
		y = date_time.replace(')', '')
		date_time = y
	y = None
	x = None

	# CHECK FOR DOUBLE SPACES AND REMOVE TO SINGLE SPACE
	x = '  ' in date_time
	if x == True:
		y = date_time.replace('  ', ' ')
		date_time = y
	x = None
	y = None
	
	
	# CHECK FOR PM AND SET THE VARIABLE
	x = "PM" in date_time.upper()
	if x == True:
		is_pm = True
		y = date_time.replace('PM', '')
		date_time = y
	x = None
	
	# REMOVE THE AM TO AVOID ISSUES LATER
	x1 = 'AM' in date_time.upper()
	if x1 == True:
		y1 = date_time.replace('AM', '')
		date_time = y1
	x1 = None
	y1 = None
	
	
	# CHECK FOR THE UTC, GET ANY OFFSET, AND REMOVE 
	x = 'UTC' in date_time.upper()
	if x == True:
		is_tz = True
		tz_i = date_time.upper().index('UTC')
		z = date_time.upper()[tz_i:]
		t_offset = z[3:]
		y = date_time[0:tz_i]
		date_time = y
	x = None
	y = None
	tz_i = None
	
	# THIS IS TO TAKE SPACES OFF OF THE END OF THE UTC AND ASSIGN 0 AS AN OFFSET...AVOID ERROR LATER
	x = " " in t_offset
	if x == True:
		t_offset.replace(' ', '')
	if t_offset == "":
		t_offset = '0'
	x = None
	

	
	# SETTING THE EPOCH
	if epoch == 'mac_absolute':
		epoch_start = datetime.datetime(2001, 1, 1, 0, 0, 0) # SET THE EPOCH FOR MAC ABSOLUTE
	if epoch == 'unix' or epoch == 'unix_millisecond' or epoch == 'unix_microsecond':
		epoch_start = datetime.datetime(1970, 1, 1, 0, 0, 0) # SET FOR UNIX EPOCH


	try:
		x = " " in date_time
		if x == True:
			split_date_time = date_time.split(" ")

		x = False
		
		# ACCOUNT FOR MULTIPLE SPACES BEETWEEN DATE AND TIME
		x_ct = 0
		
		split_time = split_date_time[1].split(":")
		
		# USING THIS TO ACCOUNT FOR "/" USED IN DATES INSTEAD OF "-"
		x = "-" in split_date_time[0]
		if x == True:
			split_date = split_date_time[0].split("-")
			
		x = "/" in split_date_time[0]
		if x == True:
			split_date = split_date_time[0].split("/")
		
		date_time_comb = split_date + split_time
		date_time = ""


		# ACCONTING FOR YEAR FIRST
		if len(split_date[0]) == 4:
			intYear = int(date_time_comb[0])
			intMonth = int(date_time_comb[1])
			intDay = int(date_time_comb[2])
		
		# ACCOUNTING FOR MONTH FIRST
		if len(split_date[0]) == 2 or len(split_date[0]) == 1:
			intYear = int(date_time_comb[2])
			intMonth = int(date_time_comb[0])
			intDay = int(date_time_comb[1])
		
		
		# ASSIGN HOUR, MINUTE, SECOND
		intHour = int(date_time_comb[3])
		# ADD 12 HOURS IF THE PM IS PRESENT
		if is_pm == True:
			intHour += 12
		intMinute = int(date_time_comb[4])
		intSecond = int(date_time_comb[5])
		
		# assigned regular string date
		date_time = datetime.datetime(intYear, intMonth, intDay, intHour, intMinute, intSecond)
		time_diff = (date_time - epoch_start)
		time_return_utc = time_diff.total_seconds()
		
			
		# ADJUST THE OFFSET TO SECONDS, MILLISECONDS, MICROSECONDS
		if epoch == 'mac_absolute' or epoch == 'unix':
			t_offset_sec = int(t_offset) * 60 * 60
		
		if epoch == 'unix_millisecond':
			t_offset_sec = int(t_offset) * 60 * 60 * 1000
			time_return_utc = time_return_utc * 1000

		if epoch == 'unix_microsecond':
			t_offset_sec = int(t_offset) * 60 * 60 * 1000000
			time_return_utc = time_return_utc * 1000000
		
		# REVERSE THE OFFSET SO IT ADJUSTS BACK TO UTC
		tod = 0 - t_offset_sec
		t_offset_sec = 0 + tod
		time_return_utc = time_return_utc + (t_offset_sec)

		return str(time_return_utc)
		
	except:
		 print(f'Invalid format entered. {date_time} is not the proper format for the date time and will cause an error.')
		 return 'INVALID'

def time_encoder():
	# THIS IS FUNCTION THAT CALLS THE DATETIME TO EPOCH FUNCTION AND PASSES THE USER INPUT
	
	print()
	print('This will encode your date time (with seconds) to one of the epochs listed below')
	print('This utilized the same code used to import CSV files into a SQLite database')
	print('It\'s kept here in case you need it for any reason')
	
	lr = 0 # KEEP REPEAT ASKING UNTIL EXIT WITH "N"
	
	while lr == 0:
	
		print()
		print('What encoding do you wnat to use?')
		print()
		print('1 - Mac Absolute Time (seconds since midnight of 2001-01-01')
		print('2 - Unix Epoch (seconds since midnight of 1970-01-01')
		print('3 - Unix Epoch Millisecond (thousands of a second since 1970-01-01')
		print('4 - Unix Epoch Microsecond (millionths of a second since 1970-01-01')
		print('N - Go back to the previous menu')
		print()
		
		ls = 0 # KEEP ASKING UNTIL A VALID SELECTION
		
		while ls == 0:
			x = input('Choose which encoding: ')
		
			if x == "1":
				epoch = 'mac_absolute'
				ls = 1
			if x == '2': 
				epoch = 'unix'
				ls = 1
			if x == '3':
				epoch = 'unix_millisecond'
				ls = 1
			if x == '4':
				epoch = 'unix_microsecond'
				ls = 1
			if x.lower() == 'n':
				ls = 1 # DON'T RE LOOP THIS LOOP
				lr = 1 # DON'T RE LOOP THE MAIN LOOP
				
		
		ls = None
		x = None
		
		e_datetime = 'INVALID'
		
		ls = 0 # ALLOW TO EXIT THIS LOOP BUT STAY IN THE OUTER LOOP TO SELECT ANOTHER ENCODING
		
		while ls == 0 and lr == 0: # DON'T DO THIS IF THE MAIN LOOP IS NOT BEING RE-LOOPED
			while e_datetime == 'INVALID':
				print()
				print('Please provide the date and time to encode (you MUST us a 4 digit year)')
				print()
				x = input('ENTER DATE-TIME: ')
				if x.lower() == 'n':
					ls = 1
					e_datetime = 'NONE'
				else:
					e_datetime = datetime_to_epoch(x, epoch)
					ls = 1
			
		print(f'Encoded timestamp: {e_datetime}')
		print()
		

		# times: mac_absolute, unix, unix_millisecond, unix_microsecond
	
	
