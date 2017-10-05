#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import numpy as np
import os, glob
import pandas as pd

# The purpose of this code is to change SMHI Open Data to GL-format
# Test that all date in order and no missing values
# Make header
# Write file

# Problems with this code: a bit messy, not enough comments? Is there a readme?
# While ordering file in function order_file() there is a possible problem if file starts with a time stamp that is not
# the earliest measurement. This brings a warning, but so far no fix has been made.
# To readme:
# Explination on the where the files should be, how to change input/output names and paths
# Explinations on naming, and that Scandinavian letters are not in use
# Explination on making the output folder and that files are re-written without warnings

headerfilename=('header.txt')           # Header titles as a txt file, should be in the working directory
path="..\Ruotsi\\"                      # Path for the original data file folder, best not to have anything else
output_path= path + "\Sweden_GL\\"      # than the .csv data file in this directory
time_difference=60                      # Time difference in minutes between measurements

# Function 1
def open_rfile(file_name):
    # Called by: ,Calls: -
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
def open_swedenfiles(file,header):
    #Called by: Main , Calls: update_header/Function7
    # Opens Swedens open data .csv files and sorts the problem with Scandinavian letters, then reads the data and
    # updates the header
    try:
        file_ = open(file, 'r')
        data = file_.readlines()
        file_.close()
    except:
        print("Problem opening file: ", file)
        data = []
        okey = False

    name=((data[1].split(";"))[0])
    if name.startswith("BARS"):          # Trying to deal with Scandinavians.. basically just rewriting them
        name="Barseback"
    elif name.startswith("BJ"):
        name="Bjorn"
    elif name.startswith("DRAG"):
        name="Draghallan"
    elif name.startswith("FURU"):
        name="Furuogrund"
    elif name.startswith("G"):
        name="Goteborg"
    elif name.startswith("MAL"):
        name="Malmo"
    elif name.startswith("SKAN"):
        name="Skanor"
    elif name.startswith("SM"):
        name="Smogen"
    elif name.startswith("Ã"):
        name="Olands Norra Udde"
    else:
        name=name.title()       # This makes the name start with big letter but to be small otherwise

    lat = ((data[1].split(";"))[2])
    lon = ((data[1].split(";"))[3])
    header=update_header(header,name,lat,lon)          # Function 7  - Updating header
    okey = True
    date_str=[]
    slev=[]
    quality=[]
    sl_variables = []

    if ((data[6].split(";"))[0])=="Datum Tid (UTC)":    # juts an extra check that header size is ok
        for ind in range(7,len(data)):
            date_str.append(data[ind].split(";")[0])    # Reads in the variables
            slev.append(float(data[ind].split(";")[1]))
            quality.append(data[ind].split(";")[2])
        date=[]
        time=[]
        for line in date_str :
            date.append((line.split()[0]).strip())
            time.append((line.split()[1]).strip())
        year=[]
        month=[]
        day=[]
        #print(date[0:10])
        #print(time[0:10])
        for line in date:
            year.append(int((line.split("-")[0]).strip()))
            month.append(int((line.split("-")[1]).strip()))
            day.append(int((line.split("-")[2]).strip()))
        #print(year)
        hour=[]
        minutes=[]
        for line in time:
            hour.append(int((line.split(":")[0]).strip()))
            minutes.append(int((line.split(":")[1]).strip()))
        #print(minutes[0:10])
        date_time=[]
        for inde in range(len(minutes)):                    # changes date + time strings into datetime
            date_time.append(datetime.datetime(year[inde],month[inde],day[inde],hour[inde],minutes[inde]))

        for ii in range(len(date_time)):
            sl_variables.append([date_time[ii],slev[ii],quality[ii]])

    else:
        print("Header size don't match expected in open_swedenfiles/Function3 with file : ",file)
        okey=False

    return sl_variables,header,okey

# Function 4
def process_file(filename,sl_variables,Headers,order):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and calls in functions to check data
    # #HERE CONTINUE

    output_file=output_path+"Gl_"+filename+".txt"                   # HERE OUTPUTFILENAME

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    ### HERE CONTINUE
    (sl_variables, missing, tot_values, start, end)=check_data(filename,sl_variables)   # Function 5
    #print(Headers)
    Headers_filled=fill_headers(Headers,missing,tot_values,start,end)               # Function 8
    write_output(Headers_filled,sl_variables,order,output_file)                             # Function 9

# Function 5
def check_data(name,sl_variables):
    # Called by: process file/Function 4, Calls: check_listorder
    # Checks order, inserts missing values, counts number of total values,start date, end date

    transposed = []         # Trick to only send timestamps to the check_listorder function
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    (inorder,inds)=check_listorder(transposed[0],time_difference*60) # Function 6, checking if entries with 60 min time interval

    if not inorder:
        print("File "+name+" is not in order or entries are missing, ordering.")
        sl_variables=sorted(sl_variables)                           # And timestamps can be sorted..

        transposed = []
        for i in range(3):
            transposed.append([row[i] for row in sl_variables])
        (inorder, inds) = check_listorder(transposed[0],time_difference * 60)  # Function 6

        if not inorder:
            print("File ",name," seems to have missing entries, making new 'empty' entries to patch. ")
            ind_copied=0
            new_variable=[]                             # This will be sl_variable with new empty entries
            for ind in range(len(inds)):
                index_wrong = (inds[ind])             # The first one where time step not = time_difference
                for index in range(ind_copied,(index_wrong) ):  # Copies the "in order" part directly to new_variable
                    new_variable.append(sl_variables[index])
                ind_copied=(index_wrong)
                thisone=sl_variables[index_wrong-1]             # this is last "good"
                nextone=sl_variables[index_wrong]               # this is first after jump

                # Could be done with while loop as well.. but got a headacke from the indexes and infinite loops..
                rounds=((nextone[0]-thisone[0])/datetime.timedelta(seconds=time_difference*60))
                for indexi in range(0,int(rounds)-1):       # Adding the "empty" values
                    thisone = ([thisone[0] + datetime.timedelta(seconds=time_difference * 60),999,"9"])
                    new_variable.append(thisone)  # 999 for sea level and 9 =missing value for quality label

            for index in range(ind_copied,len(sl_variables)):       # Adding the what's left after last "problem"
                new_variable.append(sl_variables[index])

            transposed=[]
            for i in range(3):
                transposed.append([row[i] for row in new_variable])
            (inorder, inds) = check_listorder(transposed[0], time_difference * 60)  # Function 6, Just to be sure it's now in order,huoh..
            if not inorder:
                print("Problem with ordering in check_data/Function 5")
            sl_variables=new_variable

    missing=0
    for index in range(len(sl_variables)):              # Missing= either 9 as a quality flag or nan as the value
        if sl_variables[index][2]=="9":
            missing = missing + 1
        elif np.isnan(sl_variables[index][1]):
            sl_variables[index][2]="9"
            missing=missing+1
    #print(missing)

    transposed = []                                     # Start date and end date
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    start_date=min(transposed[0])
    end_date=max(transposed[0])
    #print(start_date,end_date)                         # Length of file
    length=len(sl_variables)


    return sl_variables,missing,length,start_date,end_date



# Function 6
def check_listorder(dates,diff,current_ind=1):
    # Called by: check_data/Function5, Calls:-
    # Checks that the time difference between measurements is correct

    count = 0
    inds = []
    for ind in range(current_ind, len(dates)):
        if (dates[ind]-dates[ind-1]) != datetime.timedelta(seconds=diff):
            count = count + 1
            inds.append(ind)
    if count == 0:
        ok = True
    else:
        ok = False
    return ok, inds


# #Function 9
# # Called by: , Calls: -
# def timediff_okey(date1,date2):
#     #Called by: search_next & order_file, Calls: -
#     # Checks that the time step is 1h long
#     okey=True
#     if date2-date1!=datetime.timedelta(seconds=3600):
#         okey=False
#     return okey



# Function 7
def update_header(Headers, stationname, latitude, longitude):
    #Called by: open_swedenfiles/Function3,  Calls:-
    # Updates header info
    # Almost completely like in tgtools
    Headers["Source"] = "FMI"
    Headers["Interval"] = "1 hour"
    Headers["Datum"] = "msl/yr"
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    return Headers

#Function 8
def fill_headers(Headers,missing,total,starttime,endtime):
    # Called by: , Calls: -
    # Fills headers
    # Almost completely like in tgtools
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)

    return Headers

# Function 9
def write_output(HeaderDict, sl_variables, order, outputfile):
    # Called by: , Calls: -
    # Very much like in tgtools
    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []
    #print(order)
    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])
    #print(Header)
    # The header writing code, contains various checks.
    output=[]
    for line in Header:
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

    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')

    dates=[]
    slev=[]
    qual=[]

    for ii in range(len(sl_variables)):
        dates.append((sl_variables[ii][0]).strftime("%Y-%m-%d %H:%M"))
        slev.append(str(sl_variables[ii][1]))
        qual.append(sl_variables[ii][2])
    prints=[]
    for ind in range(len(dates)):
        prints.append("{}\t{}\t{}\n ".format(dates[ind],slev[ind],qual[ind]))



    for ind in range(len(sl_variables)):
        file.write(prints[ind])
    file.close()









def main():
    # Called by: -, Calls: get_headers/Function2, open_swedenfiles/Function 3, process_file/Function 4
    # Use:
    (Header_dict,header_order)=get_headers()        # Function 2, gettin header model

    os.chdir(path)
    for file in glob.glob("*.csv"):                 # Opens all that ends with .csv in the path folder one by one
        (sl_variables,header,okey)=open_swedenfiles(file,Header_dict)        # Function 3
        # open_swedenfiles opens the files, updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable
        if not okey:
            print("Something went wrong opening datafile, exiting program.")
            exit()
        print(file)
        process_file(file,sl_variables,header,header_order) # Function 4
        # process_file, checks the order, adds missing, counts some header info, writes gl-files
    #(filenames,found)=open_rfile('filenames.txt')
    #if not found:
       # print('Needs a file with filenames to be processed')
        #exit('Ending program')
    #for line in filenames:
       # process_file(Header_dict,header_order,line.strip())





if __name__ == '__main__':
    main()