#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to take files in gl -format and select a
# time period and then save a file for that period in gl format.


headerfilename=('header.txt')           # Header titles as a txt file, should be in the working directory
path="..\Data\MEMS_GL\\"                      # Path for the original data file folder, best not to have anything else
output_path="..\Time_range\Timerange_2006_2007\\"      # than the .txt data file in this directory
time_period_start=datetime.datetime(2006,1,1,0,0)                    # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
time_period_end=datetime.datetime(2007,12,31,23,0)
source="CMEMS"
timeinterval=""


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

    for line in (data[0:20]):
        if not (line.strip() == "" or line.strip()[0] == "#"):
            splitline=line.split()
            if splitline[0]=="Station":
                station=splitline[1].strip()
            elif splitline[0]=="Longitude":
                lon=splitline[1].strip()
            elif splitline[0]=="Latitude":
                lat = splitline[1].strip()
            elif splitline[0]=="Datum":
                if len(splitline)==1:
                    datum=""
                else:
                    datum=splitline[1].strip()
           # elif splitline[0]=="Source":
           #     print(splitline)
            #    source = splitline[1].strip()

    (header)=update_header(header, station, lat, lon, datum)
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
def update_header(Headers, stationname, latitude, longitude,datum):
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
    Headers["Interval"] = timeinterval
    Headers["Time system"] = "UTC"
    return Headers

# Function 5
def process_file(filename,sl_variables,Headers,order,station):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and creates needed variables for header, then it updates and orders
    # the header and finally writes the output of spesified time period.

    # HERE OUTPUTFILENAME
    output_file=output_path+station.replace(" ", "")+time_period_start.strftime("%Y-%m-%d")+time_period_end.strftime("%Y-%m-%d")+".txt"

    # output_file=output_path+"Gl_"+filename[:-3]+".txt"                             # replace takes away empty spaces

    #print("outputpath",output_path)
    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    (sl_variables, missing, tot_values)=check_data(filename,sl_variables)   # Function 6
    start=time_period_start.strftime("%Y-%m-%d %H:%M:%S")
    end=time_period_end.strftime("%Y-%m-%d %H:%M:%S")
    #print(Headers)
    #print(output_file)
    Headers_filled=fill_headers(Headers,missing,tot_values,start,end)               # Function 9
    write_output(Headers_filled,sl_variables,order,output_file)                             # Function 10

#Function 6
def check_data(name,sl_variables):
    # Called by: process file/Function 5
    # Gets the time period, counts number of total values and missing

    new_variables = []
    count=0
    missing=0
    for ind in range(len(sl_variables)):
        if (sl_variables[ind][0]>=time_period_start) and (sl_variables[ind][0]<=time_period_end):
            new_variables.append(sl_variables[ind])
            count=count+1
            if sl_variables[ind][2]==9:
                missing=missing+1
                sl_variables[ind][1]=np.nan


    return new_variables,missing,len(new_variables)


# Funtion 9
def fill_headers(Headers,missing,total,starttime,endtime):
    # Called by: process_file /Function 4 , Calls: -
    # Fills headers
    # Almost completely like in tgtools
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)

    return Headers

# Function 10
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





####################################################################################################



def main():
    # Called by: -, Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, gettin header model

    os.chdir(path)
    for file in glob.glob("*.txt"):                 # Opens all that ends with .csv in the path folder one by one
        (sl_variables,Header_dict,station,okey)=open_glfiles(file,Header_dict)        # Function 3

        if not okey:
            print("Something went wrong opening Cmems file",file,"exiting program.")
            exit()
        process_file(file,sl_variables,Header_dict,header_order,station) # Function 5






if __name__ == '__main__':
    main()