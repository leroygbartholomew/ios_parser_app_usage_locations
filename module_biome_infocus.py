# THIS SCRIPT WILL EXECUTE THE QUEIRIES BELOW TO PARSE OUT DATA FOR THE SELECTED APPLICATION.
# APPLICATION: inFocus BIOME parser (as of 2023-04-03)
# DATABASES REQUIRED: inFocus Apple BIOM files (and OPTIONAL: knowledgeC.db)
#
#       /private/var/db/biome/streams/restricted/_DKEvent.App.inFocus/local
# 
#
# This is a library containg functions that can be used with other
# Python scripts for parsing iOS BIOME inFocus data.  
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
# IMPORT INFOCUS BIOM DATA INTO SQLITE DATABASE
# 		import_infocus_biomes
#
#
# FOR PARSING THE INFOCUS BIOMS AND INCLUDING THEM IN A TSV AND SQLITE DATABASE
# DATABASE SHOULD ALREADY BE ATTACHED WITH THE CURSER (sql_cur) AND tsv_out OPENED FOR W OR RW.
# 		parse_infocus_bioms(bytes_to_search, buf_file, if_counter, sql_cur, tsv_out)
#
#
# COMBINE TABLES BIOME_INFOCUS AND ZOBJECT
# 		combine_tables_biome_if_zobject(sql_cur):
# ======================================================================


# import sys
# import os
# import datetime
import re
#import struct # for date decode
import sqlite3
from sqlite3 import OperationalError
import module_biome_functions


def get_rootpath():
	print('This program will parse data from the iOS BIOMEs and store the')
	print('records in a TSV file along with a SQLite database file.  It can')
	print('also import tables from the knowledeC.db file that may be of use')
	print('for forensic analysis.  If you do not have the knowledgeC.db or')
	print('do not wish to incorporate it and just recover and decode BIOME data')
	print('you can proceed without the knowledgeC.db by selecting "N" when')
	print('asked about incorporating it.  Some of the forensicaly important')
	print('artifacts were moved to the BIOMEs in iOS 16 and above')
	print()
	print('The locations of the BIOME which contains the inFocus data: ')
	print()
	print('   /private/var/db/biome/streams/restricted/(sub folder for each type)')
	print()
	print('   EX: /private/var/db/biome/streams/restricted/_DKEvent.App.inFocus/local')

	print()
	print('The files have no extnesion but the name is an Apple absolute time milliseconds (number / 1000000)')
	print('You can export the parent folder and then point the script to it (upcoming prompt),')
	print('or you can simply place the files in the same folder as this script and it will default here.')
	print('If subfolders contain more data, you only need point to the parent folder. ')
	print('This script will search subfolders for additional files')
	print()
	print('NOTE: This looks for any "SEGB" within the first 256 kb of the file.  If it finds one in a')
	print('file that is NOT a protobuf it will error out if it also contains an "/app/inFocus" or other key')
	print('text or hex data that is NOT part of an actual protobuf BIOME file.')
	print('This just means you should not just run it on the root of the drive or a')
	print('place with many other scripts that may contain those words.')
	print()
	print('Provide the folder containing the  biome files to be decoded.')
	print()

	rootpath = input('INPUT (BIOME folder):  ')

	# ASSIGN THE ROOT PATH TO "." AS A DEFAULT
	if rootpath == "":
		rootpath_w = r"./data_to_parse"
	else:
		rootpath_w = rootpath

	rootpath = None
	
	return rootpath_w


# CREATE THE TABLES NEEDE TO STORE THE NEW INFOCUS DATA
# AND IMPORT INFOCUS BIOM DATA INTO SQLITE DATABASE
def import_infocus_biomes(of_tsv, of_db, segb_list, of_log):


	# DEFINE THE HEX FOR THE "/app/inFocus"
	in_focus_bytes = b'\x2F\x61\x70\x70\x2F\x69\x6E\x46\x6F\x63\x75\x73'
	in_focus_bytes_s = bytes(in_focus_bytes).decode()
	print(f'Searching for instances of hexadecimal: {in_focus_bytes.hex()}, ASCII: {in_focus_bytes_s}')
	print()

	
	# START BUILDING
	
	log_file = open(of_log, 'a')
	
	log_file.write('==================================================\n')
	log_file.write('========== Building database tables ==============\n')
	log_file.write('==================================================\n')
	log_file.write('\n')

	# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
	sql_con = sqlite3.connect(of_db)
	sql_con.row_factory = sqlite3.Row
	sql_cur = sql_con.cursor()
	
	# MAKE THE BIOME_INFOCUS TABLE IN THE CONNECTED DATABASE. 
	#make_infocus_table(of_db, sql_cur)
	sqlite_mt = ("""CREATE TABLE IF NOT EXISTS BIOME_INFOCUS (
	Z_PK INTEGER PRIMARY KEY,
	ZSTREAMNAME VARCHAR,
	ZSTARTDATE TIMESTAMP,
	ZSTARTDATE_T VARCHAR,
	ZENDDATE TIMESTAMP,
	ZENDDATE_T VARCHAR,
	SECONDS INTEGER,
	ZVALUESTRING VARCHAR,
	ZUUID VARCHAR,
	ZTRANSITION VARCHAR,
	ZVALUEINTEGER INTEGER,
	FILENAME VARCHAR,
	LOCATION_D INTEGER
	);""")


	# EXECUTE THE QUERY
	sql_cur.execute(sqlite_mt)
	
	log_file.write('Query used to build tables:\n')
	log_file.write(f'{sqlite_mt}\n\n')
	
	log_file.write('========================================\n')
	log_file.write('========== IMPORTING BIOME DATA ========\n')
	log_file.write('========================================\n\n')
	
	
	# ASSIGN THE RECORD COUNTER TO TOAL RECORDS PARSED
	if_counter = 0

	# OPEN THE TSV FILE FOR OUTPUTING RECORDS
	of_tsv_if = of_tsv[0:len(of_tsv)-4] + '_BIOMES_infocus.tsv'

	tsv_output = open(of_tsv_if, 'w')
	tsv_output.write('ZSTREAMNAME\tZSTARTDATE\tZSTARTDATE_T\tZENDDATE\tZENDDATE_T\tZVALUESTRING\tZUUID\tZTRANSITION\tFILENAME\tLOCATION_D\n')

	print('Gathering data... Please be patient')
	print()
	
	# CALL THE FUNCTION TO PARSE THE DATA FOR EACH IN THE SEGB_LIST
	for buf_file in segb_list:
		
		if_counter, dic_hits = parse_infocus_bioms(in_focus_bytes, buf_file, if_counter, sql_cur, tsv_output)
		
		#ONLY LOG FILES WHERE IT FOUND HITS
		if dic_hits != []:
			log_file.write('========================================\n')
			log_file.write('=============== FILE ===================\n')
			log_file.write('========================================\n')
			log_file.write('\n')
			log_file.write(f'File: {buf_file}\n')
			log_file.write(f'Hits (decimal): {dic_hits}\n')
			log_file.write('\n')
			
			print(f'inFocus hits found in {buf_file}.')

	# LIST THE RECORD NUMBER SO FAR IN THE INFOCUS BIOMES
	log_file.write('\n')
	log_file.write(f'Total records parsed from inFocus BIOMES: {if_counter}\n')
	log_file.write('\n')
	
	print(f'Total records parsed from inFocus BIOMES: {if_counter}\n')


	#DON'T FORGET TO COMMIT!
	sql_con.commit() 
	
	tsv_output.close()
	log_file.close()
	
	print('BIOME inFocus data gathered.')
	print()
	
	return if_counter



# FOR PARSING THE INFOCUS BIOMS AND INCLUDING THEM IN A TSV AND SQLITE DATABASE
def parse_infocus_bioms(bytes_to_search, buf_file, if_counter, sql_cur, tsv_out):

	# THIS FUNCTION IS CALLED FROM IMPORT_INFOCUS_BIOMES
	
	dic_hits = [] # Dictionary holding the hit locations for inFocus (Will error if not pre-definded)


	# READ THE FILE INTO MEMORY
	bf = open(buf_file, 'rb')
	buf = bf.read()
	bf.close()

	# GET THE SIZE OF THE BUF (READ FILE)
	buf_size = len(buf)

	for match in re.finditer(bytes_to_search, buf):
		dic_hits.append(match.start())
	

	# ITERATE THROUGH THE HITS AND PARSE THE RECORD
	for hit in dic_hits:

		# GET THE STREAM NAME (IN FOCUS)
		zstreamname_t = buf[hit:hit + len(bytes_to_search)].decode()

		int_pos = hit + len(bytes_to_search)

		int_pos += 15 

		# GET THE START DATE HEX
		zstartdate_b = buf[int_pos:int_pos + 8]
		zstartdate_i, zstartdate_t = module_biome_functions.biom_date_decode(zstartdate_b)

		int_pos += 9


		# GET THE END DATE HEX
		zenddate_b = buf[int_pos:int_pos + 8]
		zenddate_i, zenddate_t = module_biome_functions.biom_date_decode(zenddate_b)


		int_pos += 24 # SKIP PAST THE SET SIZE BYTES WE DON'T NEED

		# GET THE PACKED BYTE, UNPACK IT, AND GET IT'S VALUES (FOR THE ZVALUESTRING)
		# Not needed for THIS code but may for others.  It's kept here in case of modifications where it's needed.
		st_pb = buf[int_pos:int_pos + 1] # Get the current position through the next (add 1)
		lt_c, rt_c = module_biome_functions.byte_5_3_decode(st_pb) # Call the procedure to decode


		int_pos +=1 # MOVE PAST THE PACKED BYTE

		# GET THE BYTE HOLDING THE LENGTH OF THE ZVALUESTRI	NG
		st_pb_val = module_biome_functions.pb_string_len_decode(buf[int_pos:int_pos +1])


		int_pos += 1 # MOVE PAST THE LENGTH BYTE

		# GET THE ZVALUESTRING
		zvaluestring_t = buf[int_pos:int_pos + st_pb_val].decode()


		int_pos = int_pos + st_pb_val # MOVE PAST THE ZVALUESTRING
		st_pb_val = 0 # Reseet just in case

		# GET THE PACKED BYTE FOR THE NEXT THING.  
		# OR...JUST MOVE PAST THAT ONE AND GET THE STRING LENGTH
		int_pos += 1

		# GET THE LENGTH OF THE NEXT STRING
		st_pb_val = module_biome_functions.pb_string_len_decode(buf[int_pos:int_pos +1])

		int_pos += 1 # Move past this length designator

		# GET THAT LONG GUID
		zuuid_t = buf[int_pos:int_pos + st_pb_val].decode()

		int_pos = int_pos + st_pb_val # MOVE PAST THE zuuid STRING
		int_pos += 13 # Move past the static size items that are of no apparent forensic values
		st_pb_val = 0 # Reset just in case

		st_pb_val = module_biome_functions.pb_string_len_decode(buf[int_pos:int_pos +1]) # Get the string length
		int_pos += 1 # Move past the value offset

        # GET THE TRANSITION
		try:
			ztransition_t = buf[int_pos:int_pos + st_pb_val].decode()
		except:
			ztransition_t = '' # ERRORS AT 3996 if not here

		# MOVE THE POSITION PAST THE ZTRANSITION
		int_pos += st_pb_val


		st_pb_val = 0

		sec_i = zenddate_i - zstartdate_i


		# SET THE INSERT RECORD QUERY
		sql_insert = f"""INSERT INTO BIOME_INFOCUS (ZVALUEINTEGER, ZSTREAMNAME, ZSTARTDATE, ZSTARTDATE_T, 
		ZENDDATE, ZENDDATE_T, SECONDS, ZVALUESTRING, ZUUID, ZTRANSITION, FILENAME, LOCATION_D)
		VALUES ('',"{zstreamname_t}", '{zstartdate_i}', '{zstartdate_t}', '{zenddate_i}', '{zenddate_t}', '{sec_i}', '{zvaluestring_t}',
		'{zuuid_t}', '{ztransition_t}', '{buf_file}', '{hit}')"""

		sql_cur.execute(sql_insert)

		# OUTPUT THE RECORD TO THE TSV FILE

		tsv_out.write(f'{zstreamname_t}\t{zstartdate_i}\t{zstartdate_t}\t{zenddate_i}\t{zenddate_t}\t{sec_i}\t{zvaluestring_t}\t{zuuid_t}\t{ztransition_t}\t{buf_file}\t{hit}\n')

		# ADD ONE TO THE COUNTER FOR THE RECORDS TOTAL
		if_counter += 1
	
	
	return if_counter, dic_hits


# COMBINE TABLES BIOME_INFOCUS AND ZOBJECT
def combine_tables_biome_if_zobject(of_db, of_log):


	print()
	print('Do you want to combine the BIOME_INFOCUS data with the ZOBJECT')
	print(f'table into a new table in {of_db}? ')
	print()
	print('Y = Yes, N (or any other key) = No')
	print()


	err_lock = 1

	while err_lock == 1:
		ret = input('INPUT (Y or N):   ')
		print()
		
		try:
			if ret == "y" or ret == "Y":
				print('Combining tables BIOME_INFOCUS and ZOBJECT')
				
				log_file = open(of_log, 'a')
				
				log_file.write('===============================================\n')
				log_file.write('======= COMBINING ACTIVITY TO NEW TABLE =======\n')
				log_file.write('===============================================\n\n')
				
				# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
				sql_con = sqlite3.connect(of_db)
				sql_con.row_factory = sqlite3.Row
				sql_cur = sql_con.cursor()
		
		
				sqlquery = """CREATE TABLE IF NOT EXISTS 'ACTIVITY_COMBINED' AS
				SELECT 
				datetime(ZOBJECT.ZSTARTDATE + 978307200,'unixepoch') AS "STARTTIME",
				ZOBJECT.ZSTARTDATE, 
				datetime(ZOBJECT.ZENDDATE + 978307200,'unixepoch') AS "ENDTIME",
				ZOBJECT.ZENDDATE,
				ZOBJECT.ZSTREAMNAME, 
				ZOBJECT.ZVALUESTRING, 
				ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE AS "SECONDS",
				ZOBJECT.ZVALUEINTEGER
				FROM ZOBJECT
				UNION ALL
				SELECT 
				datetime(BIOME_INFOCUS.ZSTARTDATE + 978307200,'unixepoch') AS "STARTTIME",
				BIOME_INFOCUS.ZSTARTDATE,
				datetime(BIOME_INFOCUS.ZENDDATE + 978307200,'unixepoch') AS "ENDTIME",
				BIOME_INFOCUS.ZENDDATE, 
				BIOME_INFOCUS.ZSTREAMNAME, 
				BIOME_INFOCUS.ZVALUESTRING, 
				BIOME_INFOCUS.ZENDDATE - BIOME_INFOCUS.ZSTARTDATE AS "SECONDS",
				BIOME_INFOCUS.ZVALUEINTEGER
				FROM BIOME_INFOCUS
				ORDER BY STARTTIME"""
				
				sql_cur.execute(sqlquery)
				sql_con.commit()
		
				log_file.write('QUERY USED TO COMBINE TABLES: \n')
				log_file.write(sqlquery)
				log_file.write('\n\n')

				err_lock = 0
				

				print('\nTables combined into "ACTIVITY_COMBINED" table\n')
	
				# PUT YOUR TOYS AWAY
				sql_con.close()
				
			elif ret == "n" or ret == "N":
				print('Proceeding without combinging tables')
				print()
				err_lock = 0

			else:
				print('Please select "N" or "Y".')
			
			log_file.write('\nTables combined into "ACTIVITY_COMBINED".\n\n')
			log_file.close()
			
		except Exception as e:
			print(f'Exception: {e}')
			print('Something went wrong.')
			print('Did you import the knowledgeC.db and BIOME data?')
			print('before trying to combine the tables?  Do that and try again.')
			input('Note the above message and press ENTER')
			print()
			err_lock = 0
			
def add_infocus_to_zobject(of_db, of_log):
	
	print('This will combine the data recovered from the inFocus BIOMEs to')
	print('the ZOBJECT table.  This will make queries that included this')
	print('information able to function correctly as they did bofore the')
	print('inFocus artifacts were moved to the BIOMEs.  This WILL alter the')
	print('ZOBJECT table by inserting the inFocus records into it. It does')
	print('NOT remove records from within the ZOBJECT table.')
	print()
	print('Be aware that if you do this multiple times, you will have duplicate records')
	print()

	try:
		err_lock = 1
		
		while err_lock == 1: 
			i_return = input('Proceed? (Y or N):  ').upper()
			print()
			
			if i_return == 'N':
				print('Operation aborted.  Nothing modified.')
				print()
				err_lock = 0
			elif i_return == 'Y':
				print('Continuing with table import')
				print()
				
				log_file = open(of_log, 'a')
				
				log_file.write('==================================================\n')
				log_file.write('========= IMPORTING INFOCUS TO ZOBJECT ===========\n')
				log_file.write('==================================================\n')
				log_file.write('\n')
					
				# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
				sql_con = sqlite3.connect(of_db)
				sql_con.row_factory = sqlite3.Row
				sql_cur = sql_con.cursor()
				
				sqlquery = """SELECT ZVALUEINTEGER, ZSTREAMNAME, ZSTARTDATE, ZENDDATE, ZVALUESTRING, ZUUID
				FROM BIOME_INFOCUS"""
				

				sql_cur.execute(sqlquery)
				records = sql_cur.fetchall()
				
				
				num_records = str(len(records))
				print(f'Total records to be imported: {num_records}')
				print()


				sqlquery = """INSERT INTO ZOBJECT 
				(ZVALUEINTEGER, ZSTREAMNAME, ZSTARTDATE, ZENDDATE, ZVALUESTRING, ZUUID)
				SELECT ZVALUEINTEGER, ZSTREAMNAME, ZSTARTDATE, ZENDDATE, ZVALUESTRING, ZUUID
				FROM BIOME_INFOCUS"""
				
				sql_cur.execute(sqlquery)
				sql_con.commit()
				

				
				log_file.write('QUERY USED TO IMPORT INFOCUS BIOME RECORDS: \n')
				log_file.write(sqlquery)
				log_file.write(f'\n\n{num_records} records imported into ZOBJECT\n\n')
				
				# PUT YOUR TOYS AWAY
				sql_con.close()
				log_file.close()
				
				
				
				print('inFocus data imported into ZOBJECT')
				print()
				print(f'{num_records} records imported into ZOBJECT')
				print()
				
				err_lock = 0
				
			else:
				print('Please select "Y" or "N".')
				print()	
		
	except Exception as e:
		print(f'Exeption occurred: {e}')
		print('Something went wrong.')
		print('Did you import the knowledgeC.db and the BIOME data?')
		print('before trying to import the inFocus records?')
		print('Do the import first and then try again.')
		input('An error occurred.  Note the above message and press ENTER')
		print()
		err_lock = 0

	
	
	
	


