#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats

# Progress:
# This code hasen't even been started it seems


# The purpose of this code is to take files in gl -format and change the height refrence frame to EVRF07


headerfilename=('header.txt')           # Header titles as a txt file, should be in the working directory
path = "..\Data\Time_range\Timerange_2006_2007_nonchecked"  # \MEMS_GL"        # Path for the original data file folder, best not to have anything else
output_path = "..\EVRF07_2006_2007_unchecked\\"                                       # than the .txt data file in this directory
set_country=""                                                    # Set only if you run for 1 country at the time, since it effects the results
datum="EVRF2007"
station_country_list=("cmems_countries.txt")                       # This is a list of filenames of stations and the country they are in, needed unless set_country is set
time_period_start=datetime.datetime(2006,1,1,0,0)                   # From when to where this data is, this only affects the name of the outputfile, the header is taken from values
time_period_end=datetime.datetime(2007,12,31,23,0)

Estonia=19  # Change in cm according to evrs.bkg.bund.de
Latvia=15
Lithuania=12
Poland=17
Germany=1
Denmark=0
Sweden=-1
Finland=-1
Russia = 25  # Lähde Jaakko Mäkinen, tämä pitää tarkistaa Ekman 1999 Marine Geodecy

# Function 1
def open_rfile(file_name):
    # Called by: get_headers / Function 2,Calls: -
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        #print(len(data))
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened in open_rfile/Function1.".format(file_name))   # Returns empty data variable and False if not successfull
        ok=False
        data=[]
        return data,ok

    return data, ok

# Function 2
def get_headers():
    # Called by: Main , Calls: open_rfile/Function 1
    # Reads a headerfile that contains the header titles and the order they should be in in the final header
    # Almost completely like in tgtools
    (headerfile,opened)=open_rfile(headerfilename)  # Function 1
    if not opened:
        print('Failed to generate headers, need a headerfile for model in get_headers/Function2.')
        exit('Ending program')
    Headers = {}
    order=[]
    for line in headerfile:                 # Reads the lines of the file into a dictionary
        if not (line.strip() == "" or line.strip()[0] == "#"):
            if ":" in line:                     # Some unchanging variables are saved in into the dictionary from the headerfile
                splitline = line.split(":")
                key = splitline[0].strip()
                value = splitline[1].strip()
            else:
                key = line.strip()
                value = ""
            Headers[key] = value
            order.append(key)
    return Headers,order

# Function 3
def open_glfiles(file,header):
    # Called by: Main , Calls:update_header
    # Opens gl  files, then reads the data and updates the header
    (data,okey) = open_rfile(file)
    print(file)

    # taking values and order from header

    station=""
    lat=np.nan
    lon=np.nan
    source=""
    missing=0
    start=[]
    end_t=[]
    tot=0


    for line in (data[0:20]):
        if not (line.strip() == "" or line.strip()[0] == "#"):
            splitline=line.split()
            if splitline[0]=="Station":
                station=splitline[1].strip()
            elif splitline[0]=="Longitude":
                lon=splitline[1].strip()
            elif splitline[0]=="Latitude":
                lat = splitline[1].strip()
            elif splitline[0]=="Source":
                if len(splitline)==1:
                    source=""
                else:
                    source=splitline[1].strip()
            elif splitline[0]=="Missing":
                missing=splitline[2].strip()
            elif splitline[0]=="Start":
                start=splitline[2].strip()
            elif splitline[0]=="End":
                end_t=splitline[2].strip()
            elif splitline[0]=="Total":
                tot=splitline[2].strip()

    (header)=update_header(header, station, lat, lon, source, missing,start,end_t,tot)
    #print(header)

    if not (data[20][0]=="-"):    # juts an extra check that header size is ok
        print("Header size of file is not expected in file: ",file)
        exit()
    date=[]
    time=[]
    slev=[]
    qual=[]
    for ind in range(21,len(data)):
        splitline=(data[ind]).split()
        date.append(splitline[0].strip())
        time.append(splitline[1].strip())
        slev.append(float(splitline[2].strip()))
        qual.append(int(splitline[3].strip()))

    variables=[]
    for ind in range(len(date)):
        splitdate=((date[ind]).split("-"))
        splittime=((time[ind]).split(":"))
        thisdate=(datetime.datetime(int(splitdate[0]),int(splitdate[1]),int(splitdate[2]),int(splittime[0]),
                                     int(splittime[1])))
        variables.append([thisdate,slev[ind],qual[ind]])

    #print(variables[0:10])

    return variables, header,station, okey

# Function 4
def update_header(Headers, stationname, latitude, longitude,source,missing,starttime,endtime,total):
    #Called by: open_ncfiles/Function3,  Calls:-
    # Updates header info
    # like in tgtools
    # later, start, end, total, missing
    Headers["Source"] = source
    Headers["Datum"] = datum
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    Headers["Unit"] = "centimeters"
    Headers["Interval"] = "1 hour"
    Headers["Time system"] = "UTC"
    Headers["Missing values"]= missing
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = total
    return Headers

# Function 5
def process_file(filename,sl_variables,Headers,order,station,country):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and creates needed variables for header, then it updates and orders
    # the header and finally writes the output of spesified time period.

    # HERE OUTPUTFILENAME

    output_file=output_path+station.replace(" ","")+"_"+time_period_start.strftime("%Y-%m-%d")+"_"+time_period_end.strftime("%Y-%m-%d")+".txt"

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    sl_variables = change_to_evrf(sl_variables,country)             # Funtion 6

    write_output(Headers,sl_variables,order,output_file)                             # Function 7


# Function 6
def change_to_evrf(sl_variables,country):
    if country == "Estonia":
        to_add=Estonia
    elif country == "Latvia":
        to_add=Latvia
    elif country == "Lithuania":
        to_add=Lithuania
    elif country == "Russia":
        to_add = Russia
    elif country == "Poland":
        to_add = Poland
    elif country == "Germany":
        to_add = Germany
    elif country == "Denmark":
        to_add = Denmark
    elif country == "Sweden":
        to_add = Sweden
    elif country == "Finland":
        to_add=Finland
    else:
        print("Can't find country: ",country)

    new_variable=[]
    for ind in range(len(sl_variables)):
        new_variable.append([sl_variables[ind][0],sl_variables[ind][1]+to_add,sl_variables[ind][2]])

    return (new_variable)

# Function 7
def write_output(HeaderDict, sl_variables, order, outputfile):
    # Called by: process_file /Function 4  , Calls: -
    # Writes the output
    # Very much like in tgtools
    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []
    #print(order)
    #print(HeaderDict)
    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])
    #print(Header)
    # The header writing code, contains various checks.
    output=[]
    for line in Header:
        #print(line)
        # Loop through all header lines
        if not len(line) ==  2:
            # Header line should only have to elements (key and value)
            print ("! Warning: broken header line:", line)
        else:
            # If there's nothing in either position of the header,
 			# replace it with an empty string.
            if line[0] == None:
                line[0] = ""
            if line[1] == None:
                line[1] = ""
            # Warn if header key or value are empty.
            if line[0] == "" :
                print ("! Warning: nameless header field: ", line)
            if line[1] == "" :
                print ("! Warning: valueless header field: ", line)
            # Finally write header line. Limit first field to 20 characters.
            if len(line[0]) > 20 :
                print ('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))

            output.append("%-20s%s\n" % (line[0][0:20], line[1]))

    file = open(outputfile, 'w')
    #print(output)

    # Writing headers
    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')


    # Writing values
    date=[]
    time=[]
    slev=[]
    qual=[]

    for ii in range(len(sl_variables)):
        date.append((sl_variables[ii][0]).strftime("%Y-%m-%d"))
        time.append((sl_variables[ii][0]).strftime("%H:%M"))
        slev.append(str(sl_variables[ii][1]))
        qual.append(sl_variables[ii][2])
    prints=[]
    for ind in range(len(date)):
        prints.append("{}\t{}\t{:6.4}\t{:3}\n".format(date[ind],time[ind],slev[ind],qual[ind]))

    for ind in range(len(sl_variables)):
        file.write(prints[ind])
    file.close()

# Function 8
def check_country(filename):
    # Called by: Main, Calls: open_rfile()/ Function 1
    # Checks the country from the list if not given
    if not set_country=="":
        print("Defaulting to define country as: ",set_country)
        return  set_country
    (data,okey)=open_rfile(station_country_list)
    if not okey:
        print("Couldn't open file:",station_country_list)
        exit("Check availability of station_country_list or give default country.")
    found=False
    for line in data:
        splitline=line.split()
        if filename==splitline[0]:
            country=splitline[1]
            found=True
    if not found==True:
        exit("Couldn't match ",filename," to a country.")
    return country

####################################################################################################



def main():
    # Called by: -, Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, gettin header model

    os.chdir(path)
    for file in glob.glob("*.txt"):                 # Opens all that ends with .csv in the path folder one by one
        if not file==station_country_list:
            (sl_variables,Header_dict,station,okey)=open_glfiles(file,Header_dict)        # Function 3
            country =check_country(file)                                                   # list has stations by the filename

            if not okey:
                print("Something went wrong opening Cmems file",file,"exiting program.")
                exit()
            process_file(file,sl_variables,Header_dict,header_order,station,country) # Function 5






if __name__ == '__main__':
    main()