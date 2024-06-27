# THIS SCRIPT WILL EXECUTE THE QUEIRIES BELOW TO PARSE OUT DATA FOR THE SELECTED APPLICATION.
# APPLICATION: iOS device locations as of 2023-03-23
# DATABASES REQUIRED: Cache.sqlite
#
#       \private\var\mobile\Library\Caches\com.apple.routined\
#           Cache.sqlite
#
# Version 1.1 (updated for offset adjustment in Google Earth)
# Date  2023-03-23
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
#
# UTC QUERY USED
# SELECT "<Placemark><name>" || DATETIME(ZTIMESTAMP + 978307200, 'unixepoch') || "  UTC  (" || SUBSTR(ZHORIZONTALACCURACY, 1, 7) || " Meters)</name><description><![CDATA[<p>" || DATETIME(ZTIMESTAMP + 978307200, 'unixepoch') || "</p>]]></description><TimeStamp><when>" || SUBSTR(DATETIME(ZTIMESTAMP + 978307200, 'unixepoch'), 1, 10) || "T" || SUBSTR(DATETIME(ZTIMESTAMP + 978307200, 'unixepoch'), 12, 8) || "</when></TimeStamp><Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" || ZLONGITUDE || ", " || ZLATITUDE || "</coordinates></Point></Placemark>" AS placemark, ZTIMESTAMP, ZLONGITUDE, ZLATITUDE, ZALTITUDE, ZHORIZONTALACCURACY
# FROM ZRTCLLOCATIONMO WHERE ZHORIZONTALACCURACY < 200 ORDER BY ZTIMESTAMP
#
# HEADER AND FOOTER OF KML FILE
# <?xml version="1.0" encoding="utf-8"?>
# <kml xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns="http://www.opengis.net/kml/2.2">
# <Document>
#
# </Document>
# </kml>


import sys
import os
import datetime
import sqlite3

# PRE SETTING A FEW VARIABLES
isError = 0 # Allows for determining when to exit a while loop
response = "" # Basic input response
zone_dic = {} #dictionary to house timezone response. 


# LIST THE FUNCTONS FOR REPEATED USE

# FUNCTION FOR RETURNING MAC ABSOLUTE TIME FROM FORMATTED DATE TIME OR JUST DATE
def datetime_to_mac(timestamp, isEnd = 0):
	# Requires import datetime, import time
	# Returns "INVALID" if the format is incorrect.
	
	date_time = timestamp
	epoch_start = datetime.datetime(2001, 1, 1, 0, 0, 0) # SET THE EPOCH FOR MAC ABSOLUTE
	try:
		x = " " in date_time
		if x == True:
			split_date_time = date_time.split(" ")
		else:
			split_date_time = [date_time,'00:00:00']

		# USING THIS TO ACCOUNT FOR "/" USED IN DATES INSTEAD OF "-"
		x = "-" in split_date_time[0]
		if x == True:
			split_date = split_date_time[0].split("-")
		elif x == False:
			split_date = split_date_time[0].split("/")
		# ACCOUNT FOR NO TIME ADDED AND IF IT'S FROM THE START OR END (isEnd)
		if split_date_time[1] != '00:00:00':
			split_time = split_date_time[1].split(":")
		else:
			if isEnd == 1:
				split_time = ['23','59','59']
			else:
				split_time = ['00','00','00']

		isEnd = 0
		date_time_comb = split_date + split_time
		date_time = ""
		intYear = int(date_time_comb[0])
		intMonth = int(date_time_comb[1])
		intDay = int(date_time_comb[2])
		intHour = int(date_time_comb[3])
		intMinute = int(date_time_comb[4])
		intSecond = int(date_time_comb[5])

		# assigned regular string date
		date_time = datetime.datetime(intYear, intMonth, intDay, intHour, intMinute, intSecond)
		time_diff = (date_time - epoch_start)
		time_return_utc = time_diff.total_seconds()
		return str(time_return_utc)
		
	except:
		 print(f'Invalid format entered. {date_time} is not the proper format for the date time and will cause an error.')
		 return 'INVALID'

def list_timezones(): # Here to later list the timezones when selecting and re-list when an invalid one used.
	print('          UTC - Universal Time Coordinated')
	print('          EST - Eastern Standard Time (UTC-5), Daylight Savings (UTC-4)')
	print('          CST - Central Standard Time (UTC-6), Daylight Savings (UTC-5)')
	print('          MST - Mountain Standard Time (UTC-7), Daylight Savings (UTC-6)')
	print('          PST - Pacific Standard Time (UTC-8), Daylight Savings (UTC-7)')
	print()

def get_cache_sqlite(of_folder = './data_output/', if_folder = './data_to_parse/'):
	# PROMPT TO INFORM WHAT DATABASES ARE NEEDED AND ASK TO PROCEED OR ABORT
	print()
	print("This program requires the following database files in the current folder to proceed.")
	print("If you don't have them press \"N\" to exit or any other key to proceed.")
	print("DATABASE:  Cache.sqlite")
	print('LOCATION: \\private\\var\\mobile\\Library\\Caches\\com.apple.routined\\')
	print()
	response = input("INPUT:  ")
	if response == "N" or response == "n":
		print('"N" selected, aborting')
		return

	response = "" #RESET THE RESPONSE

	print()
	print("Provide the path to the database including the file including the file name.")
	print()
	print("    EXAMPLE: C:\\WORK\\Cache.sqlite.")
	print()
	print('If nothing is entered, the default is \"Cache.sqlite\" in the "data_to_parse"')
	print('subfolder of the current location')
	print()
	file_path = input("INPUT:  ")
	print()

	if file_path.upper() == "N":
		print('"N" selected, aborting')
		return
	elif file_path =="":
		file_path = f"{if_folder}Cache.sqlite"
	else:
		print(f"{file_path} is being used.")

	# CHECK TO SEE IF THE FILE EXISTS
	print(f'Checking to see if {file_path} exists.')
	if os.path.isfile(file_path) is True:
		print(f'{file_path} does exist so we are proceeding.')
	else:
		print(f'{file_path} does not appear to exist.  Aborting.')
		print()
		
		return 'INVALID'

	return file_path
	

def start_parsing_kml(of_base, of_log, of_db, q_table = 'ZRTCLLOCATIONMO', of_folder = './data_output/', if_folder = './data_to_parse/'):
	
	log_file = open(of_log, 'a')
	file_path = '' # PRE-ASSIGN TO AVOID CRASH
	
	stime_start = ''
	stime_end = ''
	stime_label = ''
	stime_plot = ''
	shaccuracy = ''
	shaccuracytype = ''
	shaccuracyunits = ''
	shaccuracy_label = ""
	sdeleted = ''
	slatitude = ''
	slongitude = ''
	sspeed = ''
	saggregatedlocations = ''

	sname_label = ''
	
	
	if q_table == 'ZRTCLLOCATIONMO':
		# PROMPT TO INFORM WHAT DATABASES ARE NEEDED AND ASK TO PROCEED OR ABORT
		file_path = get_cache_sqlite()
		
		if file_path == 'INVALID':
			return
		
	# ASSIGN THE FILE_PATH VARIABLE IN CASE IT IS NOT ASSIGNED ABOVE.
	if file_path == None or file_path == "":
		file_path = of_db
	
	# ESTABLISHING THE HIGHEST DISTANCE RANGE (IN METERS)
	print()
	print("What do you want your accuracy cutoff to be?")
	print("Example would be 200 for all locations with accuracy below 200 meters.")
	print("200 meters is the default and will be used if nothing is entered.")
	print()
	acc_cutoff = input("INPUT:  ")
	if acc_cutoff == "":
		acc_cutoff = "200"
	print()

	# SETTING UP THE RANGE OF TIME
	print()
	print('You can select a time range for your results.')
	print('Selecting nothing will default to the earliest and/or latest.')
	print('The date alone can be used and the time will default to \"00:00:00\".')
	print('If no time value is entered on the end date it will default to 23:59:59. ')
	print('This means it will include the full day.')
	print('The format for the date is \"YYYY-MM-DD HH:MM:SS\" in UTC.')
	print('    EXAMPLE: \"2023-03-13 02:12:56\"  or  \"2023-03-13\"   or   \"2023-3-13\"')
	print()


	# SET THE START TIME
	start_timestamp = 'INVALID'
	while start_timestamp == 'INVALID':
		start_time = input('INPUT START TIME:   ')

		if start_time == "":
			start_time = '2001-01-01 00:00:00'

		start_timestamp = datetime_to_mac(start_time,0)

	# SET THE END TIME
	end_timestamp = 'INVALID'
	while end_timestamp == 'INVALID':
		end_time = input('INPUT END TIME:   ')
		
		if end_time =="":
			end_time = '2400-01-01 00:00:00' # Just in time for Buck Rogers' return to earth

		end_timestamp = datetime_to_mac(end_time,1)
	print()

	buck_addon = ""
	mac_addon = ""
	if end_time == '2400-01-01 00:00:00':
		buck_addon = ' - Just in time for Captain William Anthony Roger\'s return to earth'
	if start_time == '2001-01-01 00:00:00':
		mac_addon = ' - Beginning of Mac Absolute time.'
		
	print(f'Start Time:  {start_time}{mac_addon}')
	print(f'End Time:    {end_time}{buck_addon}')
	print()

	#SETTING UP THE TIME ZONE DICTIONARY
	time_zones = {
		'UTC':{'UTC':'-0'},
		'EST':{'UTC':'-0','EST':'-18000','EDT':'-14400'}, # -5, -4
		'CST':{'UTC':'-0','CST':'-21600','CDT':'-18000'}, # -6, -5
		'MST':{'UTC':'-0','MST':'-25200','MDT':'-21600'}, # -7, -6
		'PST':{'UTC':'-0','PST':'-28800','PDT':'-25200'} # -8, -7
	}
	

	# GETTING THE DESIRED TIME ZONE SET
	print('Select the timezone you want to adjust for.')
	print('Using UTC will ONLY output UTC.')
	print('Selecting any other timezone will output 3 files:')
	print('     UTC Times, Timezone STANDARD times, and Timezone DAYLIGHT SAVINGS times')
	print('     Allowed entries (Just the 3 letter prefix:')

	list_timezones() # Call the timezone list
	print()


	# SETTING THE DICTIONARY FOR THE SELECTED TIME ZONES

	isError = 1 # Set the error so it will only exit the loop upon clearing the error...choosing a correct timezone.

	while isError == 1:
		zone_select = input('INPUT:  ').upper()

		if zone_select == "" or zone_select == None:
			zone_select = "UTC"
			zone_dic = time_zones[zone_select]
			isError = 0
		else:
			try:
				zone_dic = time_zones[zone_select]
				isError = 0
			except KeyError: #Accounting for mistyping or improper entries
				print('Invalid zone entered.  Use one in the list or ENTER for the default UTC.')
				list_timezones()


	#GET DATE AND TIME FOR LOGGING
	now = datetime.datetime.now()
	# USAGE: # print (now.strftime("%Y-%m-%d %H:%M:%S LT"))

	# START THE LOGGING OF THE EVENTS FOR THE LOG FILE
	print(f'Starting the log file {of_log}') 

	log_file.write("=====================================================================================\n")
	log_file.write("============================== KML PARSING ==========================================\n")
	log_file.write("=====================================================================================\n")
	log_file.write(f'Starting log for obtaining locations from {file_path}.\n')
	log_file.write(now.strftime('Time started:  %Y-%m-%d %H:%M:%S LT\n'))
	log_file.write('\n')
	log_file.write('Parameters chosen:\n')
	if start_time == '2001-01-01 00:00:00':
		start_time = '2001-01-01 00:00:00 (Default earliest)'
	if end_time == '2400-01-01 00:00:00':
		end_time = '2400-01-01 00:00:00 (Default latest)'
	log_file.write(f'       Timezone: {zone_select},  Accuracy: < {acc_cutoff}\n')
	log_file.write(f'       Starting Time: {start_time},  Ending Time: {end_time}\n')
	log_file.write('\n')

	if q_table == 'ZRTCLLOCATIONMO':
		con = sqlite3.connect(file_path)
		
	if q_table == '_device_locations':
		con = sqlite3.connect(of_db)

	files_written = [] # Set space to write list of files written to

	getz = 0
	s_getz = ''
	
	for time_zone_label, time_zone_offset in zone_dic.items(): # Put the dictionary items into the variables and loop through each item.
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		
		# Get the integer of the already assigned time zone offset.
		getz = int(int(time_zone_offset) / 60 / 60)

		x = None
		y = None

		if getz < 0:
			x = abs(getz) #Removes the negative
			y = str(x).zfill(2)
			s_getz = '-' + y
		elif getz > 0:
			x = int(getz)
			y = str(x).zfill(2)
			s_getz = '+' + y
		else:
			s_getz = '-00' # Acounts for UTC so Google Earth will still show the slider

		
		if q_table == 'ZRTCLLOCATIONMO':
			sqlite_query_utc = f"""SELECT "<Placemark><name>" || DATETIME(ZTIMESTAMP + 978307200{time_zone_offset}, 'unixepoch') || "  {time_zone_label}  (" \
			|| SUBSTR(ZHORIZONTALACCURACY, 1, 7) || " Meters)</name><description><![CDATA[<p>" || \
			DATETIME(ZTIMESTAMP + 978307200{time_zone_offset}, 'unixepoch') || "</p>]]></description><TimeStamp><when>" || \
			SUBSTR(DATETIME(ZTIMESTAMP + 978307200{time_zone_offset}, 'unixepoch'), 1, 10) || "T" || \
			SUBSTR(DATETIME(ZTIMESTAMP + 978307200{time_zone_offset}, 'unixepoch'), 12, 8) || \
			"{s_getz}:00</when></TimeStamp><Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" \
			|| ZLONGITUDE || ", " || ZLATITUDE || "</coordinates></Point></Placemark>" AS placemark, \
			ZTIMESTAMP, ZLONGITUDE, ZLATITUDE, ZALTITUDE, ZHORIZONTALACCURACY
			FROM {q_table} \
			WHERE ZHORIZONTALACCURACY < {acc_cutoff} \
			AND ZTIMESTAMP BETWEEN {start_timestamp} AND {end_timestamp} \
			ORDER BY \
			ZTIMESTAMP"""
		
		if q_table == '_device_locations':
			
			sqlite_query_utc = f"""SELECT 
			DATETIME(ZTIMESTAMP + 978307200{time_zone_offset}, 'unixepoch') AS TIMESTAMP, DATETIME(ZENDTIME + 978307200{time_zone_offset}, 'unixepoch') AS ENDTIME, 
			SUBSTR(ZHORIZONTALACCURACY, 1, 7), ZHACCURACYTYPE, ZHACCURACYUNITS, DELETED, ZLATITUDE, ZLONGITUDE, ZSPEED, AGGREGATEDLOCATIONS 
			FROM {q_table}
			WHERE ZHORIZONTALACCURACY < {acc_cutoff} 
			AND ZTIMESTAMP BETWEEN {start_timestamp} AND {end_timestamp} 
			ORDER BY 
			ZTIMESTAMP"""


		log_file.write("Query being used:\n")
		log_file.write(f"{sqlite_query_utc}\n")
		log_file.write("\n")
		
		
		try:
			# EXECUTE THE QUERY
			cur.execute(sqlite_query_utc)
			records = cur.fetchall()
			log_file.write("Successful query\n")
			log_file.write('\n')

			# LOGGING THE TOTAL NUMBER OF RECORDS RETURNED
			num_records = str(len(records))
			log_file.write(f'Total rows in return: {num_records}\n')

			out_file = f'{of_folder}{of_base}_{time_zone_label}.kml'
			files_written.append(out_file)
			file2write = open(out_file,'w')
			file2write.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
			file2write.write("<kml xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns=\"http://www.opengis.net/kml/2.2\">\n")
			file2write.write("<Document>\n")
			if q_table == 'ZRTCLLOCATIONMO':
				for row in records:
					file2write.write(row[0] + "\n")

			if q_table == '_device_locations':
				print() # HERE FOR NOW TO AVOID CRASH

				for record in records:
					#print(*record) #NEED STAR TO RETURN RECORDS IN READABLE FORMAT
					stime_start = record[0]
					stime_end = record[1]
					shaccuracy = record[2]
					shaccuracytype = record[3]
					shaccuracyunits = record[4]
					sdeleted = record[5]
					slatitude = record[6]
					slongitude = record[7]
					sspeed = record[8]
					saggregatedlocations = record[9]
					
					
					if stime_start == None:
						stime_start = ''
					if stime_end == None:
						stime_end = ''
					if shaccuracy == None:
						shaccuracy = ''
					if shaccuracytype == None:
						shaccuracytype = ''
					if shaccuracyunits == None:
						shaccuracyunits = ''
					if sdeleted == None:
						sdeleted = ''
					if slatitude == None:
						slatitude = ''
					if slongitude == None:
						slongitude = ''
					if sspeed == None:
						sspeed = ''
					if saggregatedlocations == None:
						saggregatedlocations = ''
					
					if stime_start != '' or stime_start != None:
						# FORMAT THE TIME FOR THE TIME USED TO ACTUALLY PUT THE LOCATION IN THE TIME LINE
						stime_plot = stime_start[0:10] + 'T' + stime_start[11:19]
						if stime_end != '':
							stime_label = f'{stime_start} ({time_zone_label}) to {stime_end} ({time_zone_label})'
						else:
							stime_label = f'{stime_start} ({time_zone_label})'
					
						if shaccuracy != '':
							shaccuracy_label = f' - ({shaccuracy} {shaccuracyunits})'
						
						if saggregatedlocations != '':
							saggregatedlocations = f' ({saggregatedlocations} Locations)'
						
						if sdeleted != '':
							sdeleted = f' - {sdeleted}'
						
					sname_label = stime_label + shaccuracy_label + saggregatedlocations + sdeleted
					
					
					s_line_1 = f'<Placemark><name>{sname_label}</name><description><![CDATA[<p>{stime_start} {time_zone_label}'
					s_line_2 = f'</p>]]></description><TimeStamp><when>{stime_plot}</when></TimeStamp><Point><altitudeMode>'
					s_line_3 = f'clampedToGround</altitudeMode><coordinates>{slongitude}, {slatitude}</coordinates></Point></Placemark>'	
					
					s_line = s_line_1 + s_line_2 + s_line_3
					
					s_line_1 = None
					s_line_2 = None
					s_line_3 = None
					
					file2write.write(s_line + "\n")
				
					stime_start = ''
					stime_end = ''
					stime_label = ''
					stime_plot = ''
					shaccuracy = ''
					shaccuracytype = ''
					shaccuracyunits = ''
					shaccuracy_lable = ''
					sdeleted = ''
					slatitude = ''
					slongitude = ''
					sspeed = ''
					saggregatedlocations = ''
					
					sname_label = ''
					
					# print(s_line) # FOR TESTING =============
					
					s_line = ''

			file2write.write("</Document>\n")
			file2write.write("</kml>")
			file2write.close()
			
			
			log_file.write(f'File kml data written to: {out_file}\n')
			log_file.write('Contents include the header, first column of the query return, and footer.\n')
			log_file.write('\n')
			
		except Exception as e:
			print('FAILED !')
			print(f'Exception: {e}')
			if q_table == '_device_locations':
				print('Make sure you import data into the _device_locations table BEFORE ')
				print('attempting to do this.   ')
				print()
			if q_table == 'ZRTCLLOCATIONMO':
				print('There was a problem getting data from Cache.sqlite')
				print()
			input('Press ENTER after reading the above message.')
			print()
			log_file.write(f'FAILED to import using sql query \n')
			log_file.write(f'{sqlite_query_utc} \n\n')
		
	log_file.close()

	print('If you got this far with no errors, everything probably worked fine.')
	print('Files written: ')
	for files_written_for in files_written:
		print(f'       {files_written_for}')
		
	print()
	print('====================================================')
	print()

