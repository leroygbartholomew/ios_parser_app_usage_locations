Version 1.1 
-Updated the dates in the KML files to work with Google Earth's timeline auto adjustment. 

A forensic parser for iOS app usage analysis and location parsing. Includes inFocus BIOME parsing. Start it with "ios-data-parser.py".

It uses the Cache.sqlite, KnowledgeC.db, and any locations exported using Cellebrite's Physical Analyzer (or any other locations that can be saved as a CSV file). The parser includes instructions and will walk you through the functions. There are a couple of needed subfolders that it will build if not already there.

The locations functions will export a KML file for using in Google Earth Pro that includes the horizontal accuracy and other information that is not in the KML exports from Physical Analyzer. One suggested use is to import the device locations from the Cache.sqlite, export any deleted records with PA (Physical Analyzer), then import those records into a combined table that can then be used to generate a KML which inclueds which records were deleted, accuracy radius of each, and aggregated locatiosn for those combined by PA.

App usage includes the importing of the inFocus BIOME data removed from the KnowledgeC.db in iOS 16+ then the combining to enable the querying of the data with the already existing queries. Additioally, the import will save the BIOME data in a CSV file as well as an SQLite database.

This uses the Python 3 standard libraries only. So, it should work without worrying about PIPing any other libraries or having some missing and not being available.  If the batch file doesn't work you may have to change "python3" to "python"

https://github.com/leroygbartholomew/ios_parser_app_usage_locations
