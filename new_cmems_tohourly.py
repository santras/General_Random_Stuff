#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to change Copernicus CMEMS data so that it only contains 1 value per hour
# Test that all date in order and no missing values
# Takes the header from a file that contains the header titles and the order, location of the file header.txt can be
# changed from the beginning of this file. With it it updates the changed information to the header.
# Writes output file in the "gl"-format.


headerfilename=('header.txt')                       # Header titles as a txt file, should be in the working directory
path="..\Data_new\Other\Solution\\"                            # Path for the original data file folder, best not to have anything else
output_path= "..\..\CMEMS_hourly_EVRF07\Add_FastCheck\\"        # than the .txt data file in this directory
time_difference=60                                  # Time difference in minutes between measurements
max_sealevel_difference=50                          # Sea level change in 1 hour that is considered too suspicious, in cm
check_files=True                          # Normally True, only false if you don't want the check to be made (check= remove suspicious)
patching_missing=True                    # Normally True, only false if you don't want to add missing measurements as nan-values



# Function 1
def open_rfile(file_name):
    # Called by: get_headers / Function 2,Calls: -
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened in open_rfile/Function1.".format(file_name))
        # Returns empty data variable and False if not successfull
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

# Function 3
def open_cmemsfiles(file,header):
    # Called by: Main , Calls: update_header / Function 4
    # Opens CMEMS  files, then reads the data and maybe updates the header, Checks the sea level data
    (data,okey) = open_rfile(file)

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
            elif splitline[0]=="Source":
                if len(splitline)==1:
                    source=""
                else:
                    source=splitline[1].strip()
    # Update the heder
    (header)=update_header(header, station, lat, lon, datum, source) # Function 4

    if not (data[20][0]=="-"):    # juts an extra check that header size is normal
        print("Header size of file is not expected in file: ",file)
        exit()

    # Reading the file
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
    for ind in range(len(slev)):
        splitdate=((date[ind]).split("-"))
        splittime=((time[ind]).split(":"))
        thisdate=(datetime.datetime(int(splitdate[0]),int(splitdate[1]),int(splitdate[2]),int(splittime[0]),
                                     int(splittime[1])))
        # Making sure that if value=nan then flag=9 and vise versa
        if np.isnan(slev[ind]) or qual[ind]==9:
            variables.append([thisdate, np.nan, 9])
        else:
            variables.append([thisdate,float(slev[ind]),int(qual[ind])])

    return variables, header, station, okey


# Function 4
def update_header(Headers, stationname, latitude, longitude,datum,source):
    #Called by: open_ncfiles/Function3,  Calls:-
    # Updates header info
    # like in tgtools
    Headers["Source"] = source
    Headers["Datum"] = datum
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    Headers["Unit"] = "centimeters"
    if time_difference==60:
        Headers["Interval"] = "1 hour"
    else:
        Headers["Interval"] = time_difference+" minutes"
    Headers["Time system"] = "UTC"
    return Headers

# Function 5
def process_file(filename,sl_variables,Headers,order,station):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and then calls in functions to check that data is in order
    # and creates needed variables for header, then it updates and orders the header and finally writes the output.

    #output_file=output_path+"Gl_"+station.replace(" ", "")+".txt"                   # HERE OUTPUTFILENAME
    output_file = output_path + "Gl_" + filename[:-4] + ".txt"

    if not os.path.exists(output_path):                             # Making the output folder if it doesen't allready exist
        os.makedirs(output_path, exist_ok=True)

    # Not writing the outputfile if no data
    if len(sl_variables)==0:
        print("File "+filename+" was empty." )
        return

    (sl_variables, missing, tot_values, start, end)=check_data(filename,sl_variables)   # Function 6

    # If after check (and taking the hourly measurements) no data left then not writing the output
    if tot_values==0:
        print("Coudn't find at the hour measurements in file " + filename + " .")
        return

    Headers_filled=fill_headers(Headers,missing,tot_values,start,end)               # Function 8
    write_output(Headers_filled,sl_variables,order,output_file)                     # Function 9

#Function 6
def check_data(name,sl_variables):
    # Called by: process file/Function 5, Calls: check_listorder / function 7
    # Checks the data, keeps only at the hour measurements, checks the data, fills in the missing (with nans).
    # Checks order, inserts missing values, counts number of total values, missing, start date and end date.

    # Transferring only the at the hour measurements to var_onlyhour
    missing=0
    var_onlyhour=[]
    for ind in range(len(sl_variables)):
        this_minute = sl_variables[ind][0].strftime("%M")
        if this_minute == "00":  # When at the hour example 12:00
            if (sl_variables[ind][2]==9):
                missing=missing+1
            var_onlyhour.append(sl_variables[ind])

    # If file is empty
    if len(var_onlyhour)==0:
        #print("check1")
        return [], 0, 0, [], []

    # Ordering the new set of measurements
    # Stops checking if check_files is False and returns without padding and without further checks
    var_onlyhour = sorted(var_onlyhour)
    if check_files==False:
        #print("check2")
        return var_onlyhour, missing, len(var_onlyhour), var_onlyhour[0][0], var_onlyhour[-1][0]


    # Second check difference between measurements can't be too much
    too_big = []
    for ind in range(1, len(var_onlyhour)):
        # Checks difference with earlier measurement, if too big -> removes (missing value) measurement
        if (not np.isnan(var_onlyhour[ind][1])) and (not np.isnan(var_onlyhour[ind-1][1])) :
            if np.abs(var_onlyhour[ind][1] - var_onlyhour[ind-1][1]) > (max_sealevel_difference):
                too_big.append(["B",var_onlyhour[ind-1], var_onlyhour [ind]])
                var_onlyhour[ind][1]=np.nan
                var_onlyhour[ind][2]=9
                missing=missing+1
        # If earlier was missing, checks the differenc to next one -> removes if not ok
        elif (not np.isnan(var_onlyhour[ind][1])) and (not np.isnan(var_onlyhour[ind+1][1])):
            if np.abs(var_onlyhour[ind][1] - var_onlyhour[ind+1][1]) > (max_sealevel_difference):
                too_big.append(["A", var_onlyhour[ind+1], var_onlyhour[ind]])
                var_onlyhour[ind][1]=np.nan
                var_onlyhour[ind][2]=9
                missing=missing+1

    print("Too big jumps between measurements: ",len(too_big))

    # Ends if don't want to add "missing lines"
    if patching_missing==False:
        #print("check3")
        return var_onlyhour, missing, len(var_onlyhour), var_onlyhour[0][0], var_onlyhour[-1][0]

    # Checking the order of the new set of measurements, gives false if time interval something else than
    # given time interval between measurements
    transposed = []  # Trick to only send timestamps to the check_listorder function 7
    for i in range(3):
        transposed.append([row[i] for row in var_onlyhour])
    (inorder, inds) = check_listorder(transposed[0],time_difference * 60)  # Function 7, checking if entries with 60 min time interval


    if not inorder:
        print("File " + name + " is not in order with the given time interval between measurements, probably missing entries."
                " Trying to solve the problem.")

        new_variables=[]
        # Missing times are patched with nan and flag=9
        # Passing the first item directly
        new_variables.append(var_onlyhour[0])
        #   Next ones are checked weather they have the proper time difference or not, missing values added
        for ind in range(1, len(var_onlyhour)):
            if var_onlyhour[ind][0] - new_variables[-1][0] > datetime.timedelta(seconds=time_difference * 60):
                while var_onlyhour[ind][0] - new_variables[-1][0] > datetime.timedelta(seconds=time_difference * 60):
                    new_variables.append([new_variables[-1][0] + datetime.timedelta(seconds=time_difference * 60), np.nan, 9])
                    missing=missing+1
            new_variables.append(var_onlyhour[ind])

        transposed = []
        for i in range(3):
            transposed.append([row[i] for row in new_variables])
        (inorder, inds) = check_listorder(transposed[0],time_difference * 60)  # Function 7, checking if entries with 60 min time interval
        if not inorder:
            print("Warning, something went wrong in ordering the file")
        #print("check4")
        return new_variables, missing, len(new_variables), new_variables[0][0], new_variables[-1][0]

    return var_onlyhour, missing, len(var_onlyhour), var_onlyhour[0][0], var_onlyhour[-1][0]

# Function 7
def check_listorder(dates,diff,current_ind=1):
    # Called by: check_data/Function6, Calls:-
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


# Funtion 8
def fill_headers(Headers,missing,total,starttime,endtime):
    # Called by: process_file /Function 4 , Calls: -
    # Fills headers
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)
    return Headers

# Function 9
def write_output(HeaderDict, sl_variables, order, outputfile):
    # Called by: process_file /Function 4  , Calls: -
    # Writes the output
    # Very much like in tgtools
    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []

    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])

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

    try:
        file = open(outputfile, 'w')
        print(outputfile)
    except:
        print("Couldn't open file to print into.")


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

    try:
        for ind in range(len(sl_variables)):
            file.write(prints[ind])
    except:
        print("Couldn't write file")
    file.close()





####################################################################################################



def main():
    # Called by: -, Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, getting header model
    os.chdir(path)
    for file in glob.glob("*.txt"):                 # Opens all that ends with .txt in the path folder one by one
        print(file)
        (sl_variables,Header_dict,station,okey)=open_cmemsfiles(file,Header_dict)        # Function 3
        #open_cmemsfiles ,updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable
        if not okey:
            print("Something went wrong opening Cmems file",file,"exiting program.")
            exit()
        process_file(file,sl_variables,Header_dict,header_order,station) # Function 5
        # process_file, removes other than HH:00 taken measurements  checks the order, adds missing, counts some header info, writes gl-files





if __name__ == '__main__':
    main()