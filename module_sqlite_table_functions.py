# This is a library containg functions that can be used with other
# Python scripts for importing sqlite table data and queries to combine tables   
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
# FOR IMPORTING IMPORTANT TABLES FROM KNOWLEDGEC.DB INTO THE CURRENTLY CONNECTED DATABASE
# 		import_knowledgec(sqlite_cursor)
#
# TO CREATE THE _DEVICE_LOCATIONS TABLE (CALLED FROM MULTIPLE PLACES)
# def create_device_locations_table(of_db, of_log):
#
#
# IMPORT DATE FROM THE CACHE.SQLITE FOR ANALYSIS WITH OTHER DATA
# def import_cache_sqlite_data(of_db, of_log, file_path):
#
## INSERT RECORDS FROM ZRTCLLOCATIONMO INTO _DEVICE_LOCATIONS TABLE
# def insert_zrt_locations(of_db, of_log):
#
# ======================================================================

# import sys
import os
import datetime
# import re
import struct # for date decode
import sqlite3
from sqlite3 import OperationalError


    
# FOR IMPORTING IMPORTANT TABLES FROM KNOWLEDGEC.DB INTO THE CURRENTLY CONNECTED DATABASE
def import_knowledgec(of_db, of_log):
	
	print()
	print('Do you want to import knowledgeC ZOBJECT,')
	print(f'ZSTRUCTUREDMETADATA, and ZSOURCE into the {of_db}?')
	print('To do this you MUST have the knowledgeC.db file.')
	print()
	print('knowledgeC.db can be found at:')
	print('    /private/var/mobile/Library/CoreDuet/Knowledge')
	print()
	print('If you don\'t have it, select "N" for NO!')
	print('Y = Yes, N (or any other key) = No')
	print()

	log_file = open(of_log, 'a')
	
	err_lock = 1

	while err_lock == 1:
		ret = input('INPUT (Y or N):   ')
		print()
		if ret == "y" or ret == "Y":
			print('Importing knowledgeC data')
			log_file.write('========================================\n')
			log_file.write('====== Importing database tables ========\n')
			log_file.write('========================================\n')
			log_file.write('\n')
	
			print('If you wish to specify a path for the knowledgeC.db, you may')
			print('do so here.  If the knowledgeC.db is in the "data_to_parse",')
			print('subfolder of this script\'s folder, you can just hit enter.')
			print('If not, You\'ll need to specify where it is, including the filename')
			print()
			
			err_lock = 1 # Equals 0 if file exists (see below)
			
			while err_lock == 1:
				
				kc_ret = input('INPUT (Path):   ')
				print()
				
				if kc_ret == "": 
					kc = './data_to_parse/knowledgeC.db'
					# print(f'{kc} in the current directing is being used')
					
				elif kc_ret  == "N" or kc_ret == "n":
					return # Allow for exit if database is not there
					
				else:
					kc = kc_ret
				
				if os.path.isfile(kc) is True:
					err_lock = 0
					print(f'Using {kc} to import the data from.')
					print()
				else:
					print(f'{kc} does not exist. Specify a file that exists or  "N" to exit')
					print()
					
				kc_ret = None
				
				
			# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
			sql_con = sqlite3.connect(of_db)
			sql_con.row_factory = sqlite3.Row
			sql_cur = sql_con.cursor()

			try:
				sqlquery = f"""ATTACH DATABASE '{kc}' AS KC"""
				
				sql_cur.execute(sqlquery)
				

				print(f'{kc} attached as "KC" in database')
				
				commands_used = f'Query to attach knowledgeC.db: \n{sqlquery}\n\n'

				sqlquery = """CREATE TABLE IF NOT EXISTS 'ZOBJECT' AS SELECT * FROM KC.ZOBJECT ORDER BY ZSTARTDATE"""
				
				sql_cur.execute(sqlquery)
				
				commands_used = commands_used + f'Command to import ZOBJECT:\n{sqlquery}\n\n'
				
				sqlquery = """CREATE TABLE IF NOT EXISTS 'ZSTRUCTUREDMETADATA' AS SELECT * FROM KC.ZSTRUCTUREDMETADATA"""
				
				sql_cur.execute(sqlquery)
				
				commands_used = commands_used + f'Command to import ZSTRUCTUREDMETADATA:\n{sqlquery}\n\n'
				
				sqlquery = """CREATE TABLE IF NOT EXISTS 'ZSOURCE' AS SELECT * FROM KC.ZSOURCE"""
				
				sql_cur.execute(sqlquery)
				
				commands_used = commands_used + f'Command to import ZSOURCE:\n{sqlquery}\n\n'
				
				#DON'T FORGET TO COMMIT!
				sql_con.commit() 

				log_file.write('\n')
				log_file.write('QUERY USED TO IMPORT DATA:\n')
				log_file.write(commands_used)
				log_file.write('\n')
				print('Tables imported.')
				print()
				err_lock = 0
			except:
				print('There was a problem importing tables.  ')
			
			# PUT YOUR TOYS AWAY
			sql_con.close()
			log_file.close()
			
			print()
			print('====================================================')
			print()
				
		elif ret == "n" or ret == "N":
			print('Proceeding without importing knowledgeC data')
			print()
			err_lock = 0

		else:
			print('Please select "N" or "Y".')


# TO CREATE THE _DEVICE_LOCATIONS TABLE (CALLED FROM MULTIPLE PLACES)
def create_device_locations_table(of_db, of_log):
	
	log_file = open(of_log,'a')
		
	# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
	sql_con = sqlite3.connect(of_db)
	sql_con.row_factory = sqlite3.Row
	sql_cur = sql_con.cursor()

	log_file.write('=====================================================================================\n')
	log_file.write('============== Building device_locations table if it doesn\'t exist =================\n')
	log_file.write('=====================================================================================\n\n')
	
	sqlite_mt = ("""CREATE TABLE IF NOT EXISTS _device_locations( 
	Z_PK INTEGER PRIMARY KEY, 
	Z_ENT INTEGER, 
	Z_OPT INTEGER, 
	ZSIGNALENVIRONMENTTYPE INTEGER, 
	ZTYPE INTEGER, 
	ZALTITUDE FLOAT, 
	ZCOURSE FLOAT, 
	ZHACCURACYTYPE TEXT,
	ZHORIZONTALACCURACY FLOAT, 
	ZHACCURACYUNITS TEXT,
	ZVERTICALACCURACY FLOAT,
	ZLATITUDE FLOAT, 
	ZLONGITUDE FLOAT, 
	ZSPEED FLOAT, 
	ZTIMESTAMP TIMESTAMP,
	ZENDTIME TIMESTAMP,
	AGGREGATEDLOCATIONS INTEGER,
	DELETED TEXT
	 );""")
	 
	 
	# EXECUTE THE QUERY
	sql_cur.execute(sqlite_mt)
	
	log_file.write('Query used to build tables:\n')
	log_file.write(f'{sqlite_mt}\n\n')
	
	
	sql_con.commit()
	sql_con.close()
	log_file.close()

# IMPORT DATE FROM THE CACHE.SQLITE FOR ANALYSIS WITH OTHER DATA
def import_cache_sqlite_data(of_db, of_log, file_path):

	log_file = open(of_log,'a')
	log_file.write('====================================================================\n')
	log_file.write('Adding the Cache.sqlite ZRTCLLOCATIONMO table to the work database\n')
	log_file.write('====================================================================\n\n')
		
	# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
	sql_con = sqlite3.connect(of_db)
	sql_con.row_factory = sqlite3.Row
	sql_cur = sql_con.cursor()
	
	try:
		sqlquery = f"ATTACH DATABASE '{file_path}' AS CSQL"
		sql_cur.execute(sqlquery)
		
		log_file.write(f'Database {file_path} attached as CSQL\n')
		log_file.write(f'Query used: \n')
		log_file.write(f'{sqlquery}\n\n')
		
		sqlquery = f"""CREATE TABLE IF NOT EXISTS ZRTCLLOCATIONMO AS SELECT * FROM CSQL.ZRTCLLOCATIONMO"""
		
		sql_cur.execute(sqlquery)
		
		log_file.write(f'Query used: \n')
		log_file.write(f'{sqlquery}\n\n')
		log_file.write(f'ZRTCLLOCATIONMO table imported.\n\n')
		
		sql_con.commit()
		
		print()
		print(f'Data imported')
		print()
		
	except Exception as e:
		print(f'An exception has occurred: {e}')


	sql_con.close()
	log_file.close()

# INSERT RECORDS FROM ZRTCLLOCATIONMO INTO _DEVICE_LOCATIONS TABLE
def insert_zrt_locations(of_db, of_log):
	
	# CREATE OUR TARGET TABLE IF IT DOESN'T EXIST
	create_device_locations_table(of_db, of_log)
	
	log_file = open(of_log,'a')
	
	log_file.write('=====================================================================================\n')
	log_file.write('Adding the Cache.sqlite ZRTCLLOCATIONMO table records to the _device_locations table\n')
	log_file.write('=====================================================================================\n\n')
	
		
	# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
	sql_con = sqlite3.connect(of_db)
	sql_con.row_factory = sqlite3.Row
	sql_cur = sql_con.cursor()


	sqlquery = 'SELECT Z_PK FROM ZRTCLLOCATIONMO'

	try:
		sql_cur.execute(sqlquery)
		records = sql_cur.fetchall()
		num_records = str(len(records))
		# log_file.write(f'Total rows in return: {num_records}\n')	
		print(f'Total records to be imported: {num_records}')
		print()
	
	# NEED TO FIGURE OUT HOW TO NOTIFY IF OPERATIONAL ERROR NO TABLE
	except Exception as e:
		print('FAILED !')
		print(f'Exception: {e}')
		print('Make sure you import the data from Cache.sqlite BEFORE ')
		print('attempting to do this. Use "IMPLOC" ')
		print()
		
	sqlquery = """INSERT INTO _device_locations (Z_ENT, Z_OPT, ZSIGNALENVIRONMENTTYPE, ZTYPE, 
				ZALTITUDE, ZCOURSE, ZHORIZONTALACCURACY, ZLATITUDE, ZLONGITUDE, ZSPEED, ZTIMESTAMP)
				SELECT Z_ENT, Z_OPT, ZSIGNALENVIRONMENTTYPE, ZTYPE, ZALTITUDE, ZCOURSE, ZHORIZONTALACCURACY, 
				ZLATITUDE, ZLONGITUDE, ZSPEED, ZTIMESTAMP FROM ZRTCLLOCATIONMO"""
	
	
	try:
		sql_cur.execute(sqlquery)
		
		# print(f'Query Executed: {sqlquery}')
		
		log_file.write('Query used to import: \n')
		log_file.write(f'{sqlquery} \n\n')
		
		sql_con.commit()
	
		print(f'\n{num_records} records imported')
		
		
	# NEED TO FIGURE OUT HOW TO NOTIFY IF OPERATIONAL ERROR NO TABLE
	except Exception as e:
		print('FAILED !')
		print(f'Exception: {e}')
		print('Make sure you import the data from Cache.sqlite BEFORE ')
		print('attempting to do this. Use "IMPLOC" ')
		input('Press ENTER after reading the above message.')
		print()
		log_file.write(f'FAILED to import using sql query \n')
		log_file.write(f'{sqlquery} \n\n')
		

	# PUT OR TOYS AWAY
	sql_con.commit()
	sql_con.close()
	log_file.close()





