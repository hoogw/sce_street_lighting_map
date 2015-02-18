#*************************************************************************
#*************************************************************************
# This python script auto batch generates Osmose Weekly Work Packet Maps
# Client: SOLO
# Inputs: MXD map, work packets csv file
# Output: Individual maps of each work packet and a merged PDF with all maps.
# Python version: 2.6.5
# Script Version: 1.0  Joe Hu 4/19/2011
#*************************************************************************
#*************************************************************************

# import the required libraries
import arcpy, os, csv

#*********** Begin User Specified Params **********************************
#*********** Edit this Portion ********************************************
WorkPacket_CSV_File = "work_packets.csv"
Point_CSV_File = "outages.csv"
outPath = r"C:\TEMP\SOLO_Map\\"
#legTitle = "Dark\\Light Project\n6th Patrol 4-20-2011"
#**************************************************************************
#*********** End User Specified Params ************************************

#*********** Begin MXD setup **********************************
# Specify output path and final output PDF
finalPdf = arcpy.mapping.PDFDocumentCreate(outPath + "OsmoseReport.pdf")

# Specify the map document and the data frame
mxd = arcpy.mapping.MapDocument(r"C:\TEMP\SOLO_Map\Osmose_map.mxd")
df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
#*********** End MXD setup *****************************************

#*********** Begin Geocoding of points CSV File ********************************
LampTemp_File = "C:\TEMP\SOLO_Map\LampTemp.csv"
LampCSV_Reader = csv.reader(open(Point_CSV_File, 'rb'), delimiter=',', quotechar='|')
f = open(LampTemp_File, 'w')
LampCSV_Writer = csv.writer(f, delimiter=',', quotechar='|')
LampCSV_Writer.writerow(['Original_Structure_Number', 'Field_Structure_Number', 'X', 'Y', 'Lens_Type'])
next(LampCSV_Reader)
for Lamp_row in LampCSV_Reader:
	XYval = Lamp_row[2].split(";")
	LampCSV_Writer.writerow([Lamp_row[0], Lamp_row[1], XYval[0], XYval[1], Lamp_row[3]])	
f.close()

# Process: Delete Features from exisitng Lamps shapefile
Osmose_Lamp_Points_shp = "C:\TEMP\SOLO_Map\osmose_work_packet\Osmose_Lamp_Points.shp"
arcpy.DeleteFeatures_management(Osmose_Lamp_Points_shp)

Reporting_Lamp = "Reporting_Lamp_Layer"

# Process: Make XY Event Layer to geocode the new lamps
arcpy.MakeXYEventLayer_management(LampTemp_File, "x", "y", Reporting_Lamp, "PROJCS['NAD_1983_UTM_Zone_11N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-117.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", "")

# Process: Append the new lamps to the empty shapefile
arcpy.Append_management(Reporting_Lamp, Osmose_Lamp_Points_shp, "TEST", "", "")
#*********** End Geocoding of points CSV File ********************************

#*********** Begin getting Handling Layer and legend Object ******************
# Select a Work Packet Layer (symbology style is controlled inthe actual MXD)
WorkPacketLayer = arcpy.mapping.ListLayers(mxd, "Week_Work_Packet", df)[0]

# Select the legend element and update the title
#legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
#legend.title = legTitle
#*********** End getting Handling Layer and legend Object *********************

#*********** Begin Reading Work Packet CSV and Loop Map to each grid **********
# Specify the name and path to the CSV file, then perform a read.  The first line (field names) of CSV was removed in a pre-process.
csvReader = csv.reader(open(WorkPacket_CSV_File, 'rb'), delimiter=',', quotechar='|')

# For each row in the CSV reader object, loop thorugh (skipping first line for field names)
next(csvReader)
for row in csvReader:

	# Create a Layer Definition based off the first delimited object (work parcket grid).
	# Create a selection on this work packet grid.
	# Zoom to the selected grid, then clear the selection
	# Change the work packet layer name to the current grid and outage count (to display in legend)
	WorkPacketLayer.definitionQuery = "\"Name_upper\" = '" + row[0] + "'"
	arcpy.SelectLayerByAttribute_management(WorkPacketLayer, "NEW_SELECTION", "\"Name_upper\" = '" + row[0] + "'")
	df.zoomToSelectedFeatures()
	arcpy.SelectLayerByAttribute_management(WorkPacketLayer, "CLEAR_SELECTION")
	WorkPacketLayer.name = "Work Packet " + row[0] + " (" + row[1] + ")"
	
	# Refresh thte view to make sure changes take place.
	arcpy.RefreshActiveView()

	#Export each theme to a temporary PDF and append to the final PDF
	tmpPdf = outPath + row[0] + "_Osmose.pdf"
	if os.path.exists(tmpPdf):
			os.remove(tmpPdf)
	arcpy.mapping.ExportToPDF(mxd, tmpPdf)
	finalPdf.appendPages(tmpPdf)
     
     	#delete the temporary pdf object.
	del tmpPdf
	
	print "Completed PDF of " + row[0]

# delete the final PDF and map object	
del mxd, finalPdf

print "Merge all PDFs completed"
#*********** End Reading Work Packet CSV and Loop Map to each grid **********

#Process complete. EXIT
#
raw_input("Press ENTER to exit")

