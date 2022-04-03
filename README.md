This repo contains a python code file analyzing urban growth rate and vegetation carbon sequestration proxied by net primary productivity (NPP) from MODIS, for 383 municipal cities in China, and three table files output from the analyiss.

py_code: python code computing the analysis based on Google Earth Engine (GEE) platform

urbanization_2001-2019: statistics for the urban growth and NPP flux changes for each city during 2001(Y1)-2019(Y2)

urbanization_2001-2010: statistics for the urban growth and NPP flux changes for each city during 2001(Y1)-2010(Y2)

urbanization_2010-2019: statistics for the urban growth and NPP flux changes for each city during 2010(Y1)-2019(Y2)

Each row in the tables represent result for a city during a period from a starting year (Y1) and ending year (Y2), and the headers for the table files are explained as following:

yr_to_yr: starting year to ending year

city_name: city name

both_urban_area: the area that both years are urban (squre meters)

both_nonUrban_area: area that both years are non-urban (squre meters)

Y1nonUrban_Y2urban_area: area that y1 is nonUrban and y2 urban (squre meters)

both_urban_npp_y2: total NPP in the area that both years are urban

both_nonUrban_npp_y2: total npp in the area that both years are non-urban

Y1nonUrban_Y2urban_npp_y2: total npp in the area that y1 nonUrban and y2 urban

both_urban_npp_y1: total npp in the area that both years are urban

both_nonUrban_npp_y1: total npp in the area that both years are non-urban

Y1nonUrban_Y2urban_npp_y1: total npp in the area that y1 nonUrban and y2 urban
