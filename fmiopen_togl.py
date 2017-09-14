#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import numpy as np

# The purpose of this code is to change FMI Open Data to GL-format
# Convert mm to cm
# Test that all date in order and no missing values
# Make header
# Write file
headerfilename=('header.txt')

def open_rfile(file_name):
    #Open a readable file
    try:
        file=open(file_name,'r')
        data=file.readlines()
        #print(len(data))
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened".format(file_name))
        ok=False
        data=[]
        return data,ok

    return data, ok

# os.path.exists(file_name):

def get_headers():      # Almost completely like in tgtools
    (headerfile,opened)=open_rfile(headerfilename)
    if not opened:
        print('Failed to generate headers, need a headerfile for model.')
        exit('Ending program')
    Headers = {}
    order=[]
    for line in headerfile:
        if not (line.strip() == "" or line.strip()[0] == "#"):
            if ":" in line:
                splitline = line.split(":")
                key = splitline[0].strip()
                value = splitline[1].strip()
            else:
                key = line.strip()
                value = ""
            Headers[key] = value
            order.append(key)
    return Headers,order
    #print(Headers)

def process_file(Headers,order,file):
    (file_strings,opened)=open_rfile(file)
    if not opened:
        #print("File {} couldn't be opened.".format(file))
        return
    station = ((file_strings[0].split())[1])
    lat = ((file_strings[1].split())[1])
    lon = ((file_strings[2].split())[1])
    data=check_data(file_strings[4:])

def check_data(file_strings):
    # order, missing values, total values,start date, end date
    date=[]
    time=[]
    slev=[]
    for line in file_strings:
        date.append(((line.split())[0]).strip())
        time.append(((line.split())[1]).strip())
        slev.append(float(((line.split())[2]).strip()))
    check_time(date,time)
    length =len(date)
    start_date=date[0]
    end_date=date[length]
    check_values(slev)


def check_time(date_string,time_string):
    date_time=[]
    for line in date_string:                        ############## I'm here trying make these working
        year = int[(date_string[0:4])]
        month = int(date_string[6:7])
        day = int(date_string[9:10])
        hour = int(time_string[0:1])
        min = int(time_string[3:4])
        date_time.append(datetime.datetime(year, month, day, hour, min))

    time_diff=datetime.timedelta(hour=1)
    count=0
    for ind in range(len(date_time)-1):
        if (date_time[ind+1]-date_time)!=time_diff:
            count=count+1

    print(count)

def check_values(values):
    count=0
    for line in values:
        if np.isnan(line):
            count=count+1

    print('Max: '+(str(np.max(values))))
    print('Min: ' + (str(np.min(values))))








def fill_headers(Headers):
    Headers["Source"] = "FMI"
    Headers["Interval"] = "1 hour"
    Headers["Start time"] = startime
    Headers["End time"] = endtime
    Headers["Datum"] = "msl/yr"
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude






# From FMIopen_process.py
#     HeaderDict = tgtools.getHeaders("header.txt")
#
#     if HeaderDict == None:
#     print("! Error: Failed to generate headers.")
#     exit()
#
#     HeaderDict["Source"] = "FMI"
#     HeaderDict["Interval"] = "1 hour"
#     HeaderDict["Start time"] = startTime
#     HeaderDict["End time"] = endTime
#     HeaderDict["Datum"] = "msl/yr"
#     HeaderDict["Total observations"] = str(total)
#     HeaderDict["Missing values"] = str(missing)
#     HeaderDict["Station"] = stationName
#     #if latitude*longitude==0:
#     #longitude,latitude=FindLatLon(stationName)
#     HeaderDict["Longitude"] = longitude
#     HeaderDict["Latitude"] = latitude
#
#     tgtools.writeOutput(HeaderDict, Data, outputFile)

#    From tgtools.py
#     def getHeaders(filename="header.txt"):
#         '''This function reads the header file and returns a dictionary with the
#         header fields as keys.
#
#         Values are either default values specified in the
#         file or empty strings. Default filename is "header.txt".
#         '''
#
#         Headers = {}
#
#         try:
#             headerfile = open(filename, 'r')
#         except IOError:
#             print ("! Error: file %s not found." % (filename))
#             exit()
#
#         for line in headerfile:
#             if not (line.strip() == "" or line.strip()[0] == "#"):
#                 if ":" in line:
#                     splitline = line.split(":")
#                     key = splitline[0].strip()
#                     value = splitline[1].strip()
#                 else:
#                     key = line.strip()
#                     value = ""
#                 Headers[key] = value
#         return Headers
# def writeOutput(HeaderDict, Data, outputFile):
# 	'''Writes header and data into output file and closes the file.
# 	'''
# 	print ("Writing header...")
# 	if len(HeaderDict.keys()) == 0:
# 		# Check for empty header, warn if so.
# 		print ("! Warning: empty header")
#
# 	Header = []
# 	order = getOrder()
#
# 	for key in order:
# 		try:
# 			Header.append([key, HeaderDict[key]])
# 		except KeyError:
# 			Header.append([key, ""])
#
# 	Data = sorted(unique(Data))
#
# 	# The header writing code, contains various checks.
# 	for line in Header:
# 		# Loop through all header lines
# 		if not len(line) ==  2:
# 			# Header line should only have to elements (key and value)
# 			print ("! Warning: broken header line:", line)
#
# 		else:
# 			# If there's nothing in either position of the header,
# 			# replace it with an empty string.
# 			if line[0] == None:
# 				line[0] = ""
# 			if line[1] == None:
# 				line[1] = ""
#
# 			# Warn if header key or value are empty.
# 			if line[0] == "":
# 				print ("! Warning: nameless header field: ", line)
# 			if line[1] == "":
# 				print ("! Warning: valueless header field: ", line)
#
# 			# Finally write header line. Limit first field to 20 characters.
# 			if len(line[0]) > 20:
# 				print ('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))
# 			output = "%-20s%s\n" % (line[0][0:20], line[1])
# 			outputFile.write(output)
# def getOrder(filename="header.txt"):
# 	order = []
#
# 	try:
# 		headerfile = open(filename, 'r')
# 	except IOError:
# 		try:
# 			headerfile = open('../../tgdata/python/'+filename, 'r')
# 		except IOError:
# 			print ("! Error: file %s not found." % (filename))
# 			exit()
#
# 	for line in headerfile:
# 		if not (line.strip() == "" or line.strip()[0] == "#"):
# 			if ":" in line:
# 				splitline = line.split(":")
# 				key = splitline[0].strip()
# 			else:
# 				key = line.strip()
# 			order.append(key)
#
# 	return order







def main():
    (Header_dict,header_order)=get_headers()
    (filenames,found)=open_rfile('filenames.txt')
    if not found:
        print('Needs a file with filenames to be processed')
        exit('Ending program')
    for line in filenames:
        process_file(Header_dict,header_order,line.strip())
    #fill_headers(Header_dict)




if __name__ == '__main__':
    main()