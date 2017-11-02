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

# This needs to be checked and if okey run first on the time range wanted first and then later to whole files.
# For storage these files probably should be 1 hour time range since space is best saved.


headerfilename=('header.txt')                       # Header titles as a txt file, should be in the working directory
path="..\Data\MEMS_GL\\"     # Path for the original data file folder, best not to have anything else
output_path= "..\CMEMS_hourly_checked\\"      # than the .txt data file in this directory
time_difference=60                                  # Time difference in minutes between measurements
max_sealevel_difference=50                          # In cm
write_files=True                                  # Normally true, if only wanting to print out problematic measurements then False
check_files=True                                # Normallu True, only false if you don't want the check to be made

# Function 2
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

    (header)=update_header(header, station, lat, lon, datum, source)
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

    return variables, header,station, okey


# Function 4
def update_header(Headers, stationname, latitude, longitude,datum,source):
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


    output_file=output_path+"Gl_"+station.replace(" ", "")+".txt"                   # HERE OUTPUTFILENAME
    # output_file=output_path+"Gl_"+filename[:-3]+".txt"                             # replace takes away empty spaces

    #print("outputpath",output_path)
    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    (sl_variables, missing, tot_values, start, end)=check_data(filename,sl_variables)   # Function 6 ##########Here
    #print(Headers)
    #print(output_file)
    Headers_filled=fill_headers(Headers,missing,tot_values,start,end)               # Function 9
    write_output(Headers_filled,sl_variables,order,output_file)                             # Function 10

#Function 6
def check_data(name,sl_variables):
    # Called by: process file/Function 5, Calls: check_listorder / function 7
    # Checks the data, if multible measurements from same time_difference keeps only the "at the hour" measurement.  Checks
    # if that measurement is okey in value (difference before and after), if not (or missing), checks the mean of closest
    # values, if that okey, replaces the measurement with mean. Checks order, inserts missing values, counts number of
    # total values, missing, start date and end date


    var_onlyhour = []
    new_variables = []
    missing = 0
    # Transferring only the at the hour measurements to var_onlyhour
    for ind in range(len(sl_variables)):
        this_minute = sl_variables[ind][0].strftime("%M")
        if this_minute == "00":  # When at the hour example 12:000
            var_onlyhour.append(sl_variables[ind])
            if (sl_variables[ind][2]==9) or (np.isnan(sl_variables[ind][1])):
                missing=missing+1
    # print("lengths:",len(sl_variables),len(var_onlyhour))
    # print(var_onlyhour[0:20])

    if len(var_onlyhour)==0:                        # If the file is empty
        return [], missing, 0, [], []

    # Ordering the new set of measurements
    var_onlyhour = sorted(var_onlyhour)
    if check_files==False:
        return var_onlyhour, missing, len(var_onlyhour), var_onlyhour[0][0], var_onlyhour[-1][0]

    # Checking the order of the new set of measurements, gives false if time interval something else than
    # given time interval between measurements
    transposed = []  # Trick to only send timestamps to the check_listorder function 7
    for i in range(3):
        transposed.append([row[i] for row in var_onlyhour])
    (inorder, inds) = check_listorder(transposed[0],
                                      time_difference * 60)  # Function 7, checking if entries with 60 min time interval
    if not inorder:
        print(
            "File " + name + " is not in order with the given time interval between measurements, probably missing entries."
                             " Trying to solve the problem.")

    # Goes through the measurements and checks that the difference is not too big between measurements,
    #  makes nans out of possibly bad values
    missing = 0
    too_big = []
    for ind in range(len(sl_variables)):
        if (sl_variables[ind][2] == 9) or np.isnan(sl_variables[ind][1]):  # If either condition
            missing = missing + 1  # Then change both to nan and flag=9
            sl_variables[ind][2] = 9
            sl_variables[ind][1] = np.nan
        elif ind > 0:  # Only check from second row forward
            if np.isnan(sl_variables[ind - 1][1]):  # If previous is nan, you can't count change
                if (ind != (len(sl_variables) - 1)):
                    if np.abs(sl_variables[ind + 1][1] - sl_variables[ind][1]) > max_sealevel_difference:
                        too_big.append([sl_variables[ind][0], sl_variables[ind][1]])
                        missing = missing + 1  # Then change both to nan and flag=9
                        sl_variables[ind][2] = 9
                        sl_variables[ind][1] = np.nan
            elif np.abs(sl_variables[ind][1] - sl_variables[ind - 1][1]) > max_sealevel_difference:
                too_big.append([sl_variables[ind][0], sl_variables[ind][1]])
                missing = missing + 1  # Then change both to nan and flag=9
                sl_variables[ind][2] = 9
                sl_variables[ind][1] = np.nan

    print("Too big jump between measurements: ", len(too_big))
    if write_files == False:
        print("date, sea level, sea level previous hour, sea level next hour")
        if len(too_big) != 0:
            for ind in range(len(too_big)):
                print(too_big[ind])
                for index in range(len(sl_variables)):
                    if too_big[ind][0] == sl_variables[index][0]:
                        match_ind = index
                    elif too_big[ind - 1][0] == sl_variables[index][0]:
                        match_ind = index
                if match_ind < 10:
                    print(sl_variables[0:match_ind + 10])
                elif match_ind > (len(sl_variables) - 10):
                    print(sl_variables[(match_ind - 10):-1])
                else:
                    print(sl_variables[match_ind - 10:match_ind + 10])

        return [], missing, 0, [], []

        # Passing the first item directly
    new_variables.append(var_onlyhour[0])
    # Next ones are checked weather they have the proper time difference or not
    for ind in range(1, len(var_onlyhour)):
        if var_onlyhour[ind][0] - new_variables[-1][0] > datetime.timedelta(seconds=time_difference * 60):
            while var_onlyhour[ind][0] - new_variables[-1][0] > datetime.timedelta(seconds=time_difference * 60):
                new_variables.append(
                    [new_variables[-1][0] + datetime.timedelta(seconds=time_difference * 60), np.nan, 9])

        new_variables.append(var_onlyhour[ind])

    transposed = []  # Trick to only send timestamps to the check_listorder function 7
    for i in range(3):
        transposed.append([row[i] for row in new_variables])
    (inorder, inds) = check_listorder(transposed[0],
                                      time_difference * 60)  # Function 7, checking if entries with 60 min time interval
    if not inorder:
        print("Warning, something went wrong in ordering the file")

    # Fixes back the values that can be "corrected" with the mean of the hour, but can only do this if new data
    # are with smaller freaquency than the originals

    if len(new_variables) < len(sl_variables):
        for ind in range(len(new_variables)):
            if new_variables[ind][2] == 9:  # We made sure that all missing are both nan and flag=9
                helper = []
                for index in range(len(
                        sl_variables)):  # Going through whole data to find measurements from within the time range
                    if np.abs(sl_variables[index][0] - new_variables[ind][0]) <= datetime.timedelta(
                            seconds=0.5 * time_difference * 60): # If time difference withinh half of the time step of original
                        # print(np.abs(sl_variables[index][0]-new_variables[ind][0]))
                        if sl_variables[index][2] != 9:             # Go through all measurements within the timestep and keep the ones that are okey
                            helper.append(sl_variables[index][1])    # The measurements that are now put in are not necessarily okey.. not checked
                        else:
                            helper.append(np.nan)
                if (len(helper) == 0):
                    nothing = 1
                elif (np.isnan(helper).sum() <= 0.5 * len(helper)) and (
                        len(helper) - np.isnan(helper).sum() != 0):  # If less than half values bad to use in mean
                    new_variables[ind][1] = np.nanmean(helper)
                    new_variables[ind][2] = 7
                elif (len(helper) - np.isnan(helper).sum() != 0):  # Not empty nor only nans
                    new_variables[ind][1] = np.nanmean(helper)
                    new_variables[ind][2] = 8
                if (not np.isnan(new_variables[ind][1])) and (not np.isnan(new_variables[ind - 1][
                                                                               1])):  # Then lastly testing that the mean replacing the number is reasonable.
                    if np.abs(new_variables[ind][1] - new_variables[ind - 1][1]) > max_sealevel_difference + 20:
                        new_variables[ind][1] = np.nan
                        new_variables[ind][2] = 9

    missing_round2 = 0
    for ind in range(len(new_variables)):
        if new_variables[ind][2] == 9:
            missing_round2 = missing_round2 + 1

    first_day = str(new_variables[0][0])
    last_day = str(new_variables[-1][0])
    return new_variables, missing_round2, len(new_variables), first_day, last_day



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