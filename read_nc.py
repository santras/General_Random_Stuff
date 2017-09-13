from netCDF4 import Dataset
import numpy as np
import datetime

data=Dataset('.\Data\BO_TS_MO_Aarhus.nc')

print (data.file_format)        # NETCDF VERSION

print (data.dimensions.keys())  # Dimensiot

#print (data.dimensions['TIME']) # Dimensio esimerkki

#print (data.variables.keys())

#print(data.variables['SLEV'])
# Max 10, Min -10, Observed sea level, Fill Value -999.0, units m, unlimited dimensions: Time, SLEV(Time, Depth)
#print(data.variables['SLEV_QC'])
# 0-9, Quality Flag, Fill value -128, conventions: OceanSITES reference table 2
# 0=no_qc_performed
# 1= good_data
# 2= probably_good_data
# 3= bad_data_that_are_potentially_correctable
# 4= bad_data
# 5= value_changed
# 6= not_used
# 7= nominal_value
# 8= interpolated_value
# 9= missing_value

#

#print(data.variables['TIME'])
# float64, valid_max: 90000.0, QC_procedure: 5, FillValue: 999999.0, QC_indicator: 1, days since 1950-01-01T00:00:00Z
#print(data.variables['TIME_QC'])
# Same as SLEV_QC

#print(data.variables['TEMP'])
#float32, Sea temperature, TEMP(TIME, DEPTH), valid_max: 32.0, valid_min: -2.0, degrees_C
#print(data.variables['TEMP_QC'])
# Same as SLEV_QC

#print(data.variables['DEPH'])
# float32 Depth, DEPH(TIME, DEPTH), max: 6000.0, min: 0.0, axis: Z, FillValue: -999.0, positive: down, units: m
#print(data.variables['DEPH_QC'])
# Same as SLEV_QC

#print(data.variables['LONGITUDE'])
#Longitude of each location, axis: X, min: -180.0, FillValue:99999.0, degree_east
#print(data.variables['LATITUDE'])
#Latitude of each location, axis: Y, min: -90.0, FillValue:99999.0, degree_north
#print(data.variables['POSITION_QC'])
# Same as SLEV_QC

#print (data.Conventions)
# CF-1.6 OceanSITES-Manual-1.2 Copernicus-InSituTAC-SRD-1.3 Copernicus-InSituTAC-ParametersList-3.0.0

for attr in data.ncattrs():
    print (attr, '=', getattr(data, attr))
# geospatial_lon_min = 10.2167
# naming_authority = Copernicus
# quality_control_indicator = 1
# format_version = 1.2
# history_version = 9
# cdm_data_type = Station
# data_type = OceanSITES time-series data
# data_assembly_center = Baltic INS TAC DU
# geospatial_vertical_min = 0.0000
# time_coverage_end = 2017-08-31T11:00:00Z
# id = MO_platform_code_yyyymm_datacode
# update_interval = daily
# citation = These data were collected and made freely available by the Copernicus project and the programs that contribute to it
# last_date_observation = 2017-08-31T11:00:00Z
# history = 2017-01-19T13:01:36Z File created by SMHI Baltic Sea PU.
# 2017-01-25T13:01:41Z Data converted by SMHI Baltic Sea PU.
# 2017-02-17T13:01:36Z Data converted by SMHI Baltic Sea PU.
# 2017-02-22T13:01:40Z Data converted by SMHI Baltic Sea PU.
# 2017-02-24T13:01:39Z Data converted by SMHI Baltic Sea PU.
# 2017-05-07T13:01:36Z Data converted by SMHI Baltic Sea PU.
# 2017-05-31T19:01:42Z Data converted by SMHI Baltic Sea PU.
# 2017-06-14T19:01:53Z Data converted by SMHI Baltic Sea PU.
# 2017-09-01T13:01:43Z Data converted by SMHI Baltic Sea PU.
# 2017-09-06T07:34:57Z Metadata modified by SMHI BOOS DU.
# distribution_statement = These data follow Copernicus standards; they are public and free of charge. User assumes all risk for use of data. User must display citation in any publication or product using data. User must contact PI prior to any commercial use of data.
# last_longitude_observation = 10.2167
# geospatial_lat_min = 56.1500
# quality_index = A
# data_mode = D
# site_code = Aarhus
# title = Baltic- NRT in situ Observations
# date_update = 2017-09-01T13:01:43Z
# source = land/onshore structure
# area = Baltic Sea
# contact = cmems-service@smhi.se
# author = cmems-service
# geospatial_lon_max = 10.2167
# summary = Oceanographic data from the Baltic Sea. Measured properties: the hydrographic conditions as currents, temperature and salinity.
# references = http://www.oceansites.org http://www.myocean.org
# platform_code = Aarhus
# Conventions = CF-1.6 OceanSITES-Manual-1.2 Copernicus-InSituTAC-SRD-1.3 Copernicus-InSituTAC-ParametersList-3.0.0
# time_coverage_start = 2005-01-01T00:00:00Z
# qc_manual = OceanSITES User's Manual v1.1
# geospatial_vertical_max = 0.0000
# institution_references = vh@dmi.dk
# pi_name = DMI
# wmo_platform_code =
# geospatial_lat_max = 56.1500
# comment = None
# netcdf_version = 3.5
# last_latitude_observation = 56.1500
# sea_level_datum = DVR90
# institution = DMI

#print (data.variables['SLEV'].units)
print('From here on SLEV')
print(data.variables['SLEV'])
# for attr in data.variables['SLEV'].ncattrs():
#     print (attr, '=', getattr(data.variables['SLEV'], attr))

#print(data.variables['SLEV'][0:10])
#tg_data=data.variables['SLEV'][0:1000,0]
#time=data.variables['TIME']
#print(data.variables['TIME'])
#print(np.shape((data.variables['TIME'])))
#print((data.variables['SLEV'][1127800:1127810]))
#print(len((data.variables['SLEV'][1127800:1127810])))
#print((data.variables['SLEV'][18:24]))

# print(tg_data)
#print(np.shape(tg_data))
# #print(np.transpose(tg_data,0))
# #print(np.shape(np.transpose(0,tg_data)))
# print(time)
#print(np.shape(time))
#print(len(time))
#print(time[0:10])
#print([time', tg_data'])
# test1=[1,2,3,1]   #This is how to make into a matrix
# test2=[3,4,5,6]
# test3=np.column_stack((test1,test2))
# print(test3)

#test=np.column_stack((tg_data*100, time))
#print(test)
#print(np.shape(test))

time_zero=datetime.datetime(1950,1,1,0,0,0)
#print(datetime.datetime(1950,1,1,0,0,0))
#print(datetime.timedelta(days=3.1254))
n_time=[]
luku=0

# for index in range (1127800,len(time)):
#     n_time.append(datetime.timedelta(days=time[index])+time_zero)
#     luku=luku+1
# #     #print(time[index])
# #     #print(datetime.timedelta(days=time[index]))
# #     #print((datetime.timedelta(days=time[index]))+time_zero)
# #     #print(n_time)
# print(n_time[0:10])
#print(tg_data[0:10])
#print((tg_data, time))

# >>> np.vstack((a,b,c))
# array([[ 0,  1],
#        [ 2,  1],
#        [-1, -1]])
# >>> np.vstack((a,b,c)).T
# array([[ 0,  2, -1],
#        [ 1,  1, -1]])

 #print(n_time[len(time)-1])
 #print(len(time))
 # print(n_time[0:12])
 # print(n_time[0],n_time[6],n_time[12])
 # print(tg_data[0]*100,tg_data[6]*100,tg_data[12]*100)


#time_end=data.variables['TIME'][622318-1]
#print(datetime.timedelta(days=time_end)+time_zero)
#print([tg_data[0],tg_data[5],tg_data[11]])
#test_time=[(datetime.timedelta(days=time[0])+time_zero),(datetime.timedelta(days=time[5])+time_zero),(datetime.timedelta(days=time[11])+time_zero)]
#koko=datetime.timedelta(days=time[11])+time_zero
#print(test)


# SIIS MITTAUKSET 10 MIN VÄLEIN / AARHUS
# SUOMEN 1h välein
