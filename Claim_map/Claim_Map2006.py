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
#Claim_CSV_Files = "2007.csv,2008.csv,2009.csv,2010.csv"
Claim_CSV_Files = "2006.csv"
Claim_Struct_Check = "2359080E"
#**************************************************************************
#*********** End User Specified Params ************************************

#*********** Begin MXD setup **********************************
# Specify output path and final output PDF
outPath = r"C:\TEMP\Claim_map\\"
finalPdf = arcpy.mapping.PDFDocumentCreate(outPath + "ClaimReport.pdf")


Pole_Template_shp = "C:\\TEMP\\Claim_map\\poles\\Pole_Template.shp"

csvFile = Claim_CSV_Files.split(",")


try:
	for curFile in csvFile:
				
				
		yr = curFile.rstrip('.csv')
		print yr
		#yr0 = yr.split()
		yr_text = "Patrol Year " + yr
		print yr_text
						
						
		mxd = arcpy.mapping.MapDocument(r"C:\TEMP\Claim_map\Claim_maps_2006.mxd")
		df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
		
		fc_All_Poles = arcpy.mapping.ListLayers(mxd, "all_pole_2011", df)[0]
		fc_Select_poles = arcpy.mapping.ListLayers(mxd, "Poles", df)[0]
		
		
		print "Processing " + curFile;
		
		print "Join"
		# Process: Add Join
		arcpy.AddJoin_management(fc_All_Poles, "NUMBER", curFile, "Original_Structure_Number", "KEEP_COMMON")
		
		print "delete"
		# Process: Delete Features
		arcpy.Delete_management(Pole_Template_shp, "ShapeFile")
		
		print "append"
		# Process: Append
		arcpy.CopyFeatures_management(fc_All_Poles, Pole_Template_shp, "", "0", "0", "0")
		
		print "Remove Join"
		arcpy.RemoveJoin_management(fc_All_Poles, curFile)
		
		
		
		del mxd, df, fc_All_Poles, fc_Select_poles
		
		
		
		mxd = arcpy.mapping.MapDocument(r"C:\TEMP\Claim_map\Claim_maps_2006.mxd")
		df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
		
		fc_All_Poles = arcpy.mapping.ListLayers(mxd, "all_pole_2011", df)[0]
		fc_Select_poles = arcpy.mapping.ListLayers(mxd, "Poles", df)[0]    
		
		
		
		#update year label to yr  
		for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):              
		    if elm.text == "Patrol Year":                                       
		        elm.text = yr_text                                        
		
		
		# Refresh thte view to make sure changes take place.
		arcpy.RefreshActiveView()    
		
		arrStruct = Claim_Struct_Check.split(",")
		arcpy.SelectLayerByAttribute_management(fc_Select_poles, "NEW_SELECTION", "\"Original_S\" = '" + arrStruct[0] + "'")
		df.zoomToSelectedFeatures()
		arcpy.SelectLayerByAttribute_management(fc_Select_poles, "CLEAR_SELECTION")
		
		
		
		
		print "generating map"
		#Export each theme to a temporary PDF and append to the final PDF
		
		
		tmpPdf = outPath + curFile.replace(".", "_") + ".pdf"
		if os.path.exists(tmpPdf):
		      	os.remove(tmpPdf)
		arcpy.mapping.ExportToPDF(mxd, tmpPdf)
		
		
		#reverse update year label 
		for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):              
		    if elm.text == yr_text :                                       
		        elm.text = "Patrol Year"
		
		
		
		del tmpPdf, mxd, df, fc_All_Poles, fc_Select_poles
		
		print "Completed PDF of " + curFile
  		

except Exception as e:
	print e.message
	#arcpy.AddError(e.message)
    
#
raw_input("Press ENTER to exit")

