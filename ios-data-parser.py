# This is the main file for the iOS parser.  This front end will assign needed
# variables and call functions from the other modules to use in parsing and
# organizing data from  the iOS file system. 
#           
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
#

import sys
import os
import datetime
# import re
# import struct # for date decode
# import sqlite3
import module_biome_functions
import module_general_functions
import module_biome_infocus
import module_sqlite_table_functions
import module_locations_kml
import module_kml_cellebrite_import


def basic_instructions():
	print('===================================================================')
	print('====================== BASIC INSTRUCTIONS =========================')
	print('===================================================================')
	print('These modules perform various task on specific iOS files from')
	print('forensic extractions.  The simplest and easiest way to work with')
	print('the data is to place all of the SQLite database files needed')
	print('in the "data_to_parse" subfolder of this program and put the')
	print('BIOMES data in a subfolder in the "data_to_parse".  The BIOMES')
	print('don\'t need to all be separated.  You can simply copy the entire')
	print('folder with all of the various BIOME files in their original')
	print('sub folders and the program will find them.  Don\'t forget to')
	print('include the SQLite database WAL files if you think they may')
	print('have important data.  These will be merged with the corresponding')
	print('databases when read.  ')
	print()
	input('PRESS [ENTER] TO PROCEED...')
	print('===================================================================')
	print()
	print('Files from the iOS filesystem need to do everything are located here:')
	print()
	print('    /private/var/mobile/Library/Caches/com.apple.routined/Cache.sqlite')
	print('    /private/var/mobile/Library/CoreDuet/Knowledge/knowledgeC.db')
	print('    /private/var/db/biome/streams/restricted/[all subfolders] or a specific one')
	print('       EX: /private/var/db/biome/streams/restricted/_DKEvent.App.inFocus/local')
	print()
	print('NOTE: Make sure you inclue any write ahead logs to use the data within them')
	print()
	input('PRESS [ENTER] TO PROCEED...')
	print('===================================================================')
	print()
	print('The filesystem in the "data_to_parse" folder should like like:')
	print()
	print('EXAMPLE: ')
	print('    data_to_parse')
	print('        restricted')
	print('            _DKEvent.App.inFocus')
	print('                local')
	print('                    696728864888793')
	print('                    697122793753266')
	print('                    697495486024309')
	print('                    697836804570298')
	print('        knowledgeC.db')
	print('        knowledgeC.db-wal')
	print('        Cache.sqlite')
	print('        Cache.sqlite-wal')
	print()
	input('PRESS [ENTER] TO PROCEED...')
	print('===================================================================')
	print()
	print('Lastly, the items in the sections are arragned the order that is')
	print('best for making sure you have data in your work database that will')
	print('be there to allow for the next step.  If you have the data to')
	print('do each step, it\'s suggested that you do it in that order')
	print()
	input('PRESS [ENTER] TO PROCEED...')
	

# GIVE THE STARTING INSTRUCTIONS
lines = """
========================================================================================
========================================================================================

This program uses various modules to parse, decode, and organize various data from
the iOS full filesystem extractions.  It includes functions to parse various BIOMES data
as well as automate some of the querying that is done to organize data such as that in
the knowledgeC.db and routined Cache.sqlite databases.

The data will be output to various files including KML location files,
TSV (tab separated variable), and SQLite database files.  The procedures are also logged
in a log file with the corresponding file name for reporting purposes.  You can specify
a base file name or if you want the defaults (outputing to the "data_output" subfolder
with the base file name "iOS_Parser_Output", just hit ENTER and it will default

"""

# CHECK THE INPUT AND OUTPUT FOLDERS AND CREATE THEM IF THEY DON'T EXIST
of_folder = './data_output'
if_folder = './data_to_parse'

of_check = os.path.exists(of_folder)
if_check = os.path.exists(if_folder)

if of_check == False:
	os.makedirs(of_folder)
if if_check == False:
	os.makedirs(if_folder)


print(lines)
lines = ''

of = input('   INPUT (Base output file name): ')
print()

# ASSIGN THE NAMES OF THE TSV, LOG, AND DB (TEST THIS IN WINDOWS)
if of == "":
    of_tsv = './data_output/iOS_Parser_Output.tsv'
    of_db = './data_output/iOS_Parser_Output.db'
    of_log = './data_output/iOS_Parser_Output.log'
    of = './data_output/iOS_Parser_Output'
    workdb = 'iOS_Parser_Output.db'
    of_base = 'iOS_Parser_Output'
else:
    of_tsv = f'./data_output/{of}.tsv'
    of_db = f'./data_output/{of}.db'
    of_log = f'./data_output/{of}.log'
    workdb = f'{of}.db'
    of_base = f'{of}'


#GET DATE AND TIME FOR LOGGING
# datetime.datetime.now()
# USAGE: # print (now.strftime("%Y-%m-%d %H:%M:%S LT"))

# START THE LOGGING OF THE EVENTS FOR THE LOG FILE
print(f'Starting the log file {of_log}')
print() 

log_file = open(of_log, 'a')

log_file.write('==========================================================\n')
log_file.write('===================== LOG FILE ===========================\n')
log_file.write('==========================================================\n')
log_file.write('\n')
log_file.write(f'Starting the log file at {datetime.datetime.now()}\n\n')
log_file.write('')

log_file.close()

# SET THE OVERALL RECORD COUNTER
r_counter = 0 

# SET BIOME COUNT TO AVOID SHOWING 0 RECORDS IF THE MODULE IS NOT USED
biome_count = False 

# LOCK THE LIST TO MAKE SURE YOU CAN ONLY CHOOSE SOMETHING ON THE LIST



list_lock = 1

while list_lock == 1: 
	
	# lines = f"""
# ==================================================================================
# ==================================================================================
# =================== WHAT WOULD YOU LIKE TO DO? ===================================
# ==================================================================================
# BIN: 	Basic Instructins
# ==================================================================================
# ============================ APP USAGE ===========================================
# ==================================================================================
# KNC: 	Import the knowledgeC.db tables of interest.

# iF2:	Parse and import the inFocus BIOME artifacts into {workdb}.
# if3:	Combine the inFocus BIOME and ZOBJECT tables into a new table
# iF4: 	Add the inFocus BIOME data TO the ZOBJECT table (OPTIONAL)
# ==================================================================================
# =========================== LOCATIONS ============================================
# ==================================================================================
# IMPLOC: Import the Cache.sqlite ZRTCLLOCATIONMO table into {workdb}

# CSVKML: Import Cellebrite exported KML data into {workdb}, locations table

# CMBLOC: Combine the locations from ZRTCLLOCATIONMO into the
	# {workdb}, locations table
# LOCKML: Decode and export locations from {workdb} locations table
	# to a KML file for use with Google Earth

# KML:	Decode and export device locations directly from the
	# Cache.sqlite database into a KML file for use with Google Earth
# ==================================================================================
# ========================== OTHER FUNCTIONS =======================================
# ==================================================================================
# TENC: 	Encode a date time to an epoch
# ==================================================================================
# N:  	Nothing else.
# ==================================================================================
# """

	lines = f"""
===========================================================================================================
WHAT WOULD YOU LIKE TO DO? 
===========================================================================================================
	BIN: 	Basic Instructins
===========================================================================================================
APP USAGE 
===========================================================================================================
	KNC: 	Import the knowledgeC.db tables of interest.

	iF2:	Parse and import the inFocus BIOME artifacts into {workdb}.
	if3:	Combine the inFocus BIOME and ZOBJECT tables into a new table
	iF4: 	Add the inFocus BIOME data TO the ZOBJECT table (OPTIONAL)
===========================================================================================================
LOCATIONS
===========================================================================================================
	IMPLOC: Import the Cache.sqlite ZRTCLLOCATIONMO table into {workdb}

	CSVKML: Import Cellebrite exported KML data into {workdb}, locations table

	CMBLOC: Combine the locations from ZRTCLLOCATIONMO into the
			{workdb}, locations table
	LOCKML: Decode and export locations from {workdb} locations table
			to a KML file for use with Google Earth

	KML:	Decode and export device locations directly from the
			Cache.sqlite database into a KML file for use with Google Earth
===========================================================================================================
OTHER FUNCTIONS
===========================================================================================================
	TENC: 	Encode a date time to an epoch
===========================================================================================================
	N:  	Nothing else.
===========================================================================================================
"""

	print(lines)
	lines = ''

	x = input('    INPUT (From the list): ')
	x = x.upper()

	if x == 'BIN':
		#SHOW THE BASIC INSTRUCTIONS
		basic_instructions()
		
	elif x == 'KNC':
		# ASK ABOUT ACQUIRING KNOWLEDGE C DATA
		module_sqlite_table_functions.import_knowledgec(of_db, of_log)
		input('Press ENTER to return to the menu')
		print()

	elif x == 'IF2':
		# GET THE ROOT PATH OF WHERE THE BIOMES ARE
		rootpath_w = module_biome_infocus.get_rootpath()
		
		# CREATE A LIST OF FILES CONTAINING SEGB WITHING THE FIRST 256 BYTES
		segb_list = [] # LIST FOR FILES CONTAINING SEGB
		segb_list = module_biome_functions.get_segb_file_list(rootpath_w)

		# IMPORT INFOCUS BIOM DATA INTO SQLITE DATABASE
		module_biome_infocus.import_infocus_biomes(of_tsv, of_db, segb_list, of_log)
		
		input('Press ENTER to return to the menu')
		print()
		
	elif x == 'IF3':
		# MAKE A COMBINED TABLE WITH ZOBJECT AND INFOCUS, DECODED TIMESTAMPS AND SECONDS
		module_biome_infocus.combine_tables_biome_if_zobject(of_db, of_log)
		
		input('Press ENTER to return to the menu')
		print()

	elif x == 'IF4':
		# ADD INFOCUS BIOME ARTIFACTS TO ZOBJECT
		module_biome_infocus.add_infocus_to_zobject(of_db, of_log)
		
		input('Press ENTER to return to the menu')
		print()
	
	# EXPORT TO A KML FILE DIRECTLY FROM THE CACHE.SQLITE DATABASE
	elif x == "KML":
		module_locations_kml.start_parsing_kml(of_base, of_log, of_db, 'ZRTCLLOCATIONMO')
		
		input('Press ENTER to return to the menu')
		print()
	
	# IMPORT A CSV FILE WITH LOCATIONS (LIKE EXPORTED BY CELLEBRITE) INTO THE _DEVICE_LOCATIONS TABLE
	elif x == 'CSVKML':
		module_kml_cellebrite_import.import_locations_csv(of_db, of_log)
		
		input('Press ENTER to return to the menu')
		print()
	
	# IMPORT THE CACHE.SQLITE ZRTCLLOCATIONMO DATABASE IN THE WORKING DATABASE
	elif x == "IMPLOC":
		return_1 = cache_path = module_locations_kml.get_cache_sqlite()
		# DO THIS ONLY IF IT'S A VALID PATH
		if return_1 != 'INVALID':
			module_sqlite_table_functions.import_cache_sqlite_data(of_db, of_log, cache_path)
		
		input('Press ENTER to return to the menu')
		print()
	
	# EXPORT THE LOCATIONS FROM THE _DEVICE_LOCATIONS TO A KML		
	elif x == "LOCKML":
		module_locations_kml.start_parsing_kml(of_base, of_log, of_db, '_device_locations')
		
		input('Press ENTER to return to the menu')
		print()
	
	# INSERT THE TABLE FROM CACHE.SQLITE INTO THE _DEVICE_LOCATIONS TABLE
	elif x == 'CMBLOC':
		module_sqlite_table_functions.insert_zrt_locations(of_db, of_log)
		
		input('Press ENTER to return to the menu')
		print()
	
	elif x == 'TENC':
		module_general_functions.time_encoder()
		
	elif x == "N" or x == "EXIT":
		print('\n     Exiting')
		list_lock = 0
	
	elif x == "TEST":
		my_test = input('Provide date format test: ')
		time_return_utc = module_general_functions.datetime_to_epoch(my_test, 'mac_absolute')
		print(f'Mactime: {time_return_utc}')
	
	else:
		print(f'Please choose from the options provided. {x} is not an option')


# FINISH UP 
log_file = open(of_log, 'a')
log_file.write('========================================\n')
log_file.write('\n')
log_file.write(f'Ending Time:  {datetime.datetime.now()}\n')
log_file.write('\n')

log_file.close()

print()
print(f'Check the output folder for the reslting files')


        
# END
