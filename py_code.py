# -*- coding: utf-8 -*-
import ee
ee.Initialize()

#input data
landcoverMOD12Q1 = ee.ImageCollection("MODIS/006/MCD12Q1") #Land (vegetation) cover
day8_psnnet = ee.ImageCollection("MODIS/006/MOD17A2H") #MODIS NPP
city_bnd = ee.FeatureCollection("users/zongyaosha/city_bnd") #All 383 Chinese cities with boundary.

scaleSize=500 # image scale
urban_land=13 # label of urban land in MCD12Q1 dataset
Y1=2001 # staring year
Y2=2019 # ending year

SubPeriod1_Y1=2001 # starting year for first sub-period
SubPeriod1_Y2=2010 # ending year for first sub-period

SubPeriod2_Y1=2010 # starting year for second sub-period
SubPeriod2_Y2=2019 # ending year for second sub-period

# get annual NPP from day8_psnnet for the input year
def getNPP(year):
    npp = (day8_psnnet.filterDate(year + '-1-1', year + '-12-31').select('PsnNet')).sum().multiply(0.1).int16()
    return npp.reproject('EPSG:4326', None, scaleSize)

# get land cover for the input year
def getLandCover(year):
    return landcoverMOD12Q1.filterDate(year+'-1-1', year+'-12-31').select('LC_Type1').first().reproject('EPSG:4326', None, scaleSize)


#year1: staring year, year2: ending year , i: current system index id for the city, unchanged_area: area with unchanged vegetation type
# j is a flag variable, when j==0, the file header will be created
def createTable_diff(year1,year2,i,j,unchanged_area):
    f = open("/data/NPP"+year1+"_"+year2+".csv", "a")  #output to a csv file
    img_npp_prevyear=getNPP(year1)
    img_npp=getNPP(year2)

    if j==0: f.write('yr_to_yr,'
                     'city name,'
                     'both_urban_area,'
                     'both_nonUrban_area,'
                     'Y1nonUrban_Y2urban_area,'
                     'both_urban_npp_y2,'
                     'both_nonUrban_npp_y2,'
                     'Y1nonUrban_Y2urban_npp_y2,'
                     'both_urban_npp_y1,'
                     'both_nonUrban_npp_y1,'
                     'Y1nonUrban_Y2urban_npp_y1'
                     '\n')

    img_land=getLandCover(year2)
    img_land_prevyear=getLandCover(year1)

    current_feature=city_bnd.filterMetadata('system:index', 'equals', i)
    city_info=current_feature.getInfo()
    city_geom=current_feature.geometry()

    pixelArea=ee.Image.pixelArea().clip(city_geom).reproject(crs='EPSG:4326',scale=500) #pixel area at different lat/lon, for calculating total NPP

    included_area=img_land.lt(ee.Number(15)).And(img_land_prevyear.lt(ee.Number(15))) # pixels labeled by 15,16,17 excluded

    y1_urb_y2_urb=img_land_prevyear.eq(ee.Number(urban_land)).And(img_land.eq(ee.Number(urban_land))).And(included_area.eq(ee.Number(1))) #both years are urban
    y1_nonUrb_y2_nonUrb=img_land_prevyear.neq(ee.Number(urban_land)).And(img_land.neq(ee.Number(urban_land))).And(included_area.eq(ee.Number(1))) #both years are non-urban
    y1_nonUrb_y2_urb=img_land_prevyear.neq(ee.Number(urban_land)).And(img_land.eq(ee.Number(urban_land))).And(included_area.eq(ee.Number(1))) #y1 nonUrban and y2 urban


    y1_urb_y2_urb_area=y1_urb_y2_urb.multiply(pixelArea).rename("both_urban_area") #area for both years are urban
    y1_nonUrb_y2_nonUrb_area=y1_nonUrb_y2_nonUrb.multiply(pixelArea).rename("both_nonUrban_area") # area for both years are non-urban
    y1_nonUrb_y2_urb_area=y1_nonUrb_y2_urb.multiply(pixelArea).rename("Y1nonUrban_Y2urban_area") # area for y1 nonUrban and y2 urban


    y1_urb_y2_urb_npp_y2=img_npp.mask(y1_urb_y2_urb).multiply(pixelArea).rename("both_urban_npp_y2") # total npp in the area where both years are urban
    y1_nonUrb_y2_nonUrb_npp_y2=img_npp.mask(y1_nonUrb_y2_nonUrb).multiply(pixelArea).rename("both_nonUrban_npp_y2") # total npp in the area where both years are non-urban
    y1_nonUrb_y2_urb_npp_y2=img_npp.mask(y1_nonUrb_y2_urb).multiply(pixelArea).rename("Y1nonUrban_Y2urban_npp_y2") # total npp in the area where y1 nonUrban and y2 urban

    y1_urb_y2_urb_npp_y1=img_npp_prevyear.mask(y1_urb_y2_urb).multiply(pixelArea).rename("both_urban_npp_y1") # total npp in the area where both years are urban
    y1_nonUrb_y2_nonUrb_npp_y1=img_npp_prevyear.mask(y1_nonUrb_y2_nonUrb).multiply(pixelArea).rename("both_nonUrban_npp_y1") # total npp in the area where both years are non-urban
    y1_nonUrb_y2_urb_npp_y1=img_npp_prevyear.mask(y1_nonUrb_y2_urb).multiply(pixelArea).rename("Y1nonUrban_Y2urban_npp_y1") # total npp in the area where y1 nonUrban and y2 urban

    img=y1_urb_y2_urb_area.\
        addBands(y1_nonUrb_y2_nonUrb_area).\
		addBands(y1_nonUrb_y2_urb_area).\
        addBands(y1_urb_y2_urb_npp_y2).\
		addBands(y1_nonUrb_y2_nonUrb_npp_y2).\
        addBands(y1_nonUrb_y2_urb_npp_y2).\
		addBands(y1_urb_y2_urb_npp_y1).\
        addBands(y1_nonUrb_y2_nonUrb_npp_y1).\
		addBands(y1_nonUrb_y2_urb_npp_y1)

    resultmap = img.clip(city_geom).reduceRegions(
		collection=city_geom,
		reducer=ee.Reducer.sum(),
		scale=scaleSize
	)

    city_prop= resultmap.getInfo()["features"][0]["properties"]
    #output all the interested variables, see explanation for each variable above
    data_line=year1+"_"+year2+","\
              +city_info["features"][0]["properties"]["NAME"]\
			  +","+str(int(city_prop["both_urban_area"]))\
			  +","+str(int(city_prop["both_nonUrban_area"]))\
			  +","+str(int(city_prop["Y1nonUrban_Y2urban_area"]))\
			  +","+str(int(city_prop["both_urban_npp_y2"]))\
			  +","+str(int(city_prop["both_nonUrban_npp_y2"]))\
			  +","+str(int(city_prop["Y1nonUrban_Y2urban_npp_y2"]))\
			  +","+str(int(city_prop["both_urban_npp_y1"]))\
			  +","+str(int(city_prop["both_nonUrban_npp_y1"]))\
			  +","+str(int(city_prop["Y1nonUrban_Y2urban_npp_y1"]))\
			  +"\n"

    f.write(data_line) #write to csv file
    f.close()


# calculate the result
def loopFeatures_diff():
    #First prepare area of unchanged vegetated types for the full period and each sub-period
    mask_unchanged_fullperiod=getLandCover(Y1).\
        eq(getLandCover(Y2))
    mask_unchanged_SubPeriod_1=getLandCover(SubPeriod1_Y1).\
        eq(getLandCover(SubPeriod1_Y2))
    mask_unchanged_SubPeriod_2=getLandCover(SubPeriod2_Y1).\
        eq(getLandCover(SubPeriod2_Y2))

    lst=city_bnd.aggregate_array('system:index')
    n=lst.length()  #number of cities
    for i in range(0,n.getInfo(),1): #loop through each city and output the statistics for the city
        createTable_diff(str(Y1),str(Y2),lst.getString(i),i,mask_unchanged_fullperiod)
        createTable_diff(str(SubPeriod1_Y1),str(SubPeriod1_Y2),lst.getString(i),i,mask_unchanged_SubPeriod_1)
        createTable_diff(str(SubPeriod2_Y1),str(SubPeriod2_Y2),lst.getString(i),i,mask_unchanged_SubPeriod_2)

loopFeatures_diff()  #BEGIN PROCESS
