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
# FOR MAKING BYTE ARRAY STRING OUT OF HEX STRING IF NEEDED.
# 		hex_format(hex_string)
#
# FOR DECODING THE PACKED BYTE WITH 5/3 DIVISION.  
# 		byte_5_3_decode(hex_offset)
#
# FOR GETTING THE LENGTH VALUE OF ON BYTE
# 		pb_string_len_decode(hexoffset)
#
# FOR DECODING BASE 16 HEX TO DECIMAL
# 		hex_to_decimal(hexdata)
#
# FOR DECODING 64 BIT HEX DATE TIME
# 		biom_date_decode(hexdata)
#
# FOR CHECKING A FILE FOR "SEGB" WITHIN THE FIRST 256 BYTES
# 		check_file_segb(biome_file_name)
#
# FOR IMPORTING IMPORTANT TABLES FROM KNOWLEDGEC.DB INTO THE CURRENTLY CONNECTED DATABASE
# 		import_knowledgec(sqlite_cursor)
#
# CREATE A LIST OF FILES CONTAINING SEGB WITHING THE FIRST 256 BYTES
#			get_segb_file_list(rootpath_w):
#
# ======================================================================

# import sys
import os
import datetime
# import re
import struct # for date decode
import sqlite3
from sqlite3 import OperationalError


# CREATE A LIST OF FILES CONTAINING SEGB WITHING THE FIRST 256 BYTES
def get_segb_file_list(rootpath_w):
	segb_list = [] # LIST FOR FILES CONTAINING SEGB

	for root, dirs, files in os.walk(rootpath_w):
		for file in files:
			file_name = os.path.join(root, file)
			segb_tf, segb_loc = check_file_segb(file_name)
			if segb_tf == True:
				segb_list.append(file_name)

	return segb_list

# FOR CHECKING A FILE FOR "SEGB" WITHIN THE FIRST 256 BYTES
def check_file_segb(biome_file_name):

    segb = b'\x53\x45\x47\x42'

    with open(biome_file_name, 'rb') as mf:
        fc = mf.read(256)

    tf_loc = fc.find(segb)

    if tf_loc != -1: # -1 meaning nothing was found
        tf = True
    else:
        tf = False

    return tf, tf_loc

# FOR MAKING BYTE ARRAY STRING OUT OF HEX STRING IF NEEDED.
def hex_format(hex_string): 
    sep_count = 0
    sh_str = ""
    sep_dic = []
    while sep_count < len(separator):
        sep_dic.append(hex_string[sep_count:sep_count + 2])  # Separate the separator bytes into a dictionary
        sep_count += 2  # to allow for additions needed for byte array

    for sep_loop in sep_dic:
        sh_str = sh_str + '\\x' + sep_loop
        # print(sh_str)
    return sh_str

# FOR DECODING THE PACKED BYTE WITH 5/3 DIVISION.  
def byte_5_3_decode(hex_offset):

    bits = bin(int(hex_offset.hex(),16))[2:].zfill(8)
    #print(f'Bits: {bits}')
    lbit = bits[0:5]
    rbit = bits[5:8]
    
    #DEFINE THE VALUES FOR THE BITS
    lbit_v_dic = {1:16, 2:8, 3:4, 4:2, 5:1}
    rbit_v_dic = {1:4, 2:2, 3:1}
    
    # ASSIGN THE PIECES OF THE BIT STRING
    lbit_dic = {}
    lbit_dic[1] = int(lbit[0:1])
    lbit_dic[2] = int(lbit[1:2])
    lbit_dic[3] = int(lbit[2:3])
    lbit_dic[4] = int(lbit[3:4])
    lbit_dic[5] = int(lbit[4:5])
    rbit_dic = {}
    rbit_dic[1] = int(rbit[0:1])
    rbit_dic[2] = int(rbit[1:2])
    rbit_dic[3] = int(rbit[2:3])

    
    v_count = 1
    lt_count = 0
    rt_count = 0
    
    for l_val in lbit_dic.items():
        key_v = lbit_dic[v_count]
        if key_v == 1:
            lt_count = lt_count + lbit_v_dic[v_count]

        v_count += 1
    
    v_count = 1 # Set it back to 1 for the left side.
    
    for r_val in rbit_dic.items():
        key_v = rbit_dic[v_count]
        if key_v == 1:
            rt_count = rt_count + rbit_v_dic[v_count]
            
        v_count += 1
    
    return lt_count, rt_count

# FOR GETTING THE LENGTH VALUE OF ON BYTE
def pb_string_len_decode(hexoffset):
    hexoffset_u = hexoffset.hex()
    hexoffset_u = bytearray.fromhex(hexoffset_u).hex() # HEX VALUE OF STRING SIZE
    hexoffset_val = int(hexoffset_u, 16) # INTEGER VALUE OF STRING SIZE
    return hexoffset_val

# FOR DECODING BASE 16 HEX TO DECIMAL
def hex_to_decimal(hexdata):
    h = hexdata.hex()
    d = int(h, base = 16)
    return d

# FOR DECODING 64 BIT HEX DATE TIME
def biom_date_decode(hexdata):
    hexdata_i = float(struct.unpack('<d',hexdata)[0])#proper decoding into seconds since 2001-01-01 #[0] is for the touple assignment
    x = datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=hexdata_i)
    hexdata_t = x.strftime('%Y-%m-%d %H:%M:%S')
    # hexdata_t = x.strftime('%Y-%m-%d %H:%M:%S.%f') # FOR FRACTIONS OF SECOND
    return hexdata_i, hexdata_t


