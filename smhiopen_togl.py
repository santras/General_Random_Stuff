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
    #Called by: Main , Calls: update_header/Function11
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
    header=update_header(header,name,lat,lon)          # Function 11  - Updating header
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
    # Called by: Main, Calls: check_data/Function5
    # Makes an output folder if it doesen't exist and calls in functions to check data
    # #HERE CONTINUE

    output_file=output_path+"Gl_"+filename+".txt"                   # HERE OUTPUTFILENAME

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    ### HERE CONTINUE
    check_data(filename,sl_variables)                                   # Function 5
    #Headers_filled=fill_headers(Headers,station,lat,lon,missing,tot_values,start,end)
    #write_output(Headers_filled,data,order,output_name)

# Function 5
def check_data(name,sl_variables):
    # Called by: process file/Function 4, Calls: -
    # order, missing values, total values,start date, end date
    #print((sl_variables[0:10][0]))

    #print(transposed_var)
    #print("len sl",len(sl_variables))
    transposed = []
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    print("len trans",len(transposed))
    (inorder,inds)=check_listorder(transposed[0],time_difference*60) # Function 6, checking if entries with 60 min time interval

    if not inorder:
        print("File "+name+" is not in order or entries are missing, ordering.")
        sl_variables=sorted(sl_variables)

        transposed = []
        for i in range(3):
            transposed.append([row[i] for row in sl_variables])
        (inorder, inds) = check_listorder(transposed[0],time_difference * 60)  # Function 6

        #print(inds)

        if not inorder:
            #print(len(inds))
            print("File ",name," seems to have missing entries, making new 'empty' entries to patch. ")
        #     maxi=(max(sl_variables))[0]
        #     print(maxi)
            ind_copied=0
        #     while not inorder:                      # Is the whole file in order
            new_variable=[]
            #print("inds",inds)
            for ind in range(len(inds)):
                index_wrong = (inds[ind])             # The first one where time step not = time_difference
                #print("wrongh",index_wrong)
                for index in range(ind_copied,(index_wrong) ):
                    new_variable.append(sl_variables[index])
                    #print("ii",ind,index)
                #print("len 1",len(new_variable))
                ind_copied=(index_wrong)
                thisone=sl_variables[index_wrong-1]
                #print("This",thisone)
                nextone=sl_variables[index_wrong]

                rounds=((nextone[0]-thisone[0])/datetime.timedelta(seconds=time_difference*60))
                #print(rounds)
                for indexi in range(0,int(rounds)-1):
                    #print("hi")
                    #while (nextone[0] > thisone[0]):
                    thisone = ([thisone[0] + datetime.timedelta(seconds=time_difference * 60),999,9])
                    #print("thisone",thisone)
                    new_variable.append(thisone)  # 999 for sea level and 9 =missing value for quality label
                    #print("len2",len(new_variable))
                    #round=round+1
                    #print("while-inner", thisone)
                #print("round",round)
            for index in range(ind_copied,len(sl_variables)):
                new_variable.append(sl_variables[index])
                #print("aa",index)

        print("here new")
        transposed=[]
        for i in range(3):
            transposed.append([row[i] for row in new_variable])
        (inorder, inds) = check_listorder(transposed[0], time_difference * 60)  # Function 6
        if inorder:
            print("yhaa")
        else:
            #print(new_variable)
            print(inds,len(sl_variables),len(new_variable))
        #for ind in range(len(sl_variables)):
         #   print(ind,sl_variables[ind],new_variable[ind])



        #         new_variables = sl_variables[ind_copied:ind_tocopy]
        #         print((max(new_variables))[0])
        #         if ((max(new_variables))[0])==maxi:
        #             break
        #         thisone = sl_variables[ind_tocopy]
        #         nextone = sl_variables[ind_tocopy + 1]
        #
        #         while (nextone[0]>thisone[0]):                          # This is the first gap that came up with check_listorder and is now being filled
        #             thisone[0]=thisone[0]+datetime.timedelta(seconds=time_difference*60)
        #             new_variables.append([thisone,999,9])   # 999 for sea level and 9 =missing value for quality label
        #             print("while-inner", thisone)
        #
        #         for i in range(3):
        #             transposed.append([row[i] for row in sl_variables])
        #         (inorder, inds) = check_listorder(transposed[0], time_difference * 60,current_ind=(ind_tocopy+1))  # Function 6
        #         ind_copied = ind_tocopy
        #     print("here")









    #missing_lines=check_time(date,time,slev,quality)                                 # Using a module below to check that no missing lines exist
    #if missing_lines>0:
    #print("There is gaps here for ",missing_lines," hours.") # No missing lines should exist in SMHI data, that's why just check
    #length =len(date)
    #start_date=date[0]
    #end_date=date[length-1]
    #(missing_values,new_slev,quality)=check_values(slev)
    #data=[]
    #for index in range(len(new_slev)):
     #   data.append(("{}\t{}\t{:6.4}\t{:3.1}\n".format(date[index],time[index],str(new_slev[index]),str(quality[index]))))
    #return missing_values,length,start_date,end_date,data


# Function 6
def check_listorder(dates,diff,current_ind=1):
    # Called by: check_data/Function5, Calls:-
    # Checks that the time difference between measurements is correct

    count = 0
    inds = []
    #print(transposed[0:10])
    print("len dates",len(dates))
    for ind in range(current_ind, len(dates)):
        #print(dates[ind]-dates[ind-1])
        if (dates[ind]-dates[ind-1]) != datetime.timedelta(seconds=diff):
            #print("difference",(dates[ind]-dates[ind-1]))
            count = count + 1
            inds.append(ind)
            # print(ind)
    if count == 0:
        ok = True
    else:
        ok = False
    return ok, inds


# NO MORE IN USE?
def check_time(date_string,time_string,slev,quality):           #checking this
    # Called by: , Calls: -
    # Check that time input is okey and no missing input... next measuremnt =1h
    date_time=[]
    year=[]
    month=[]
    day=[]
    hour=[]
    min=[]
    for line in date_string:
        splitline = line.split("-")
        year.append(int((splitline[0]).strip()))
        month.append(int((splitline[1]).strip()))
        day.append(int((splitline[2]).strip()))
    #print(day)
    for clockline in time_string:
        splitline2 = clockline.split(":")
        hour.append(int((splitline2[0]).strip()))
        min.append(int((splitline2[1]).strip()))
    #print(min)
    for i in range(len(year)):
        if year[i]>2017:
            print('Year high',i)
        if year[i]<1800:
            print('Year low',i)
        if month[i]<1:
            print(month[i])
            print('Month low',i)
        if month[i]>12:
            print('Month high',i)
        if day[i]>31:
            print('Day high',i)
        if day[1]<1:
            print('Day low',i)
        if hour[i]>24:
            print('Hour high',i)
        if hour[i]<0:
            print('Hour low',i)
        if min[i]<0:
            print('Min low',i)
        if min[i]>60:
            print('Min high',i)
        try:
            date_time.append(datetime.datetime(year[i], month[i], day[i], hour[i], min[i]))
        except:
            print('Something wrong here',i,year[i],month[i],day[i],hour[i],min[i])

    time_diff=datetime.timedelta(seconds=3600)
    count=0
    for ind in range(len(date_time)-1):
        if (date_time[ind+1]-date_time[ind])!=time_diff:
            count=count+1
            print(ind)

    if count!=0:
        (date_time,slev,quality)=order_file(date_time,slev,quality)         #####Working here
        # Notice that some files are okey and don't go to order_file function
    return count

# Function 7
def order_file(dates,slev,qual):            ######THIS UNDER CONSTRUCTION
    # Called by: check_time, Calls: search_next, timediff_okey
    #Checks the order of the file, fills is missing rows and arranges the file according to time stamps

    # print(min(dates))
    if dates[0] != min(dates):                          #Checks that the first measurement is the earliest
        # Here later code to handle this
        print("Warning! Problems with orderin file, file doesen't start with it's earliest time stamp.")

    new_dates=[dates[0]]
    new_slev=[slev[0]]
    new_qual=[qual[0]]

    #Here okey
    maxi=max(dates)
    for ind in range(1,len(dates)):
        okey=timediff_okey(dates[ind-1],dates[ind])     # Function 9
        if not okey:
            #print("IN Function 7",dates[ind-1],dates[ind]) aiempi, myöhempi
            (new_dates, new_slev, new_qual)=search_next(dates[ind-1],dates[ind],dates,slev,qual,new_dates,new_slev,new_qual)
            if (new_dates[len(new_dates)-1])==maxi:
                print("Leaving really 'early'", len(dates), len(new_dates))
                return new_dates, new_slev, new_qual
        new_dates.append(dates[ind])
        new_slev.append(slev[ind])
        new_qual.append(qual[ind])
        if dates[ind]==maxi:
            print("Leaving 'early'",len(dates),len(new_dates))
            return new_dates, new_slev,new_qual
    print("Returning", len(dates), len(new_dates))
    return new_dates, new_slev,new_qual

# Function 8
def search_next(lastone,thisone,dates,slev,qual,new_dates,new_slev,new_qual):
    ## WORKING HERE
    # Called by: order_file, Calls: timediff_okey
    # Searching for the next or nexts to fill in.
    # Only go back after condition next to add is the current ind in order_file
    # If no measurement is found, row with time stamp and missing value indication is added
    end_condition=False
    count=0
    #Here lastone is last added to new_dates, thisone is next to be put in in the funtion order_file
    if ((thisone-lastone)<=datetime.timedelta(seconds=3600)):   # Additional check that I haven't made a mistake
        print("What is this",thisone,lastone,(thisone-lastone))
        exit("Uups, problems with checking the time difference between measurements in : search_next")

    while end_condition==False:     # Check for loop ending condition, back if next one is the next in file
        count=count+1
        match=False
        for ind in range(len(dates)):
            if (dates[ind]-lastone)==datetime.timedelta(seconds=3600):   #Finding the next match from file
                new_dates.append(dates[ind])
                new_slev.append(slev[ind])
                new_qual.append(qual[ind])
                lastone=dates[ind]          # Updating last measurements + lastone
                match=True

        if not match:   # Making a new "empty" entry if next not found
            lastone=lastone+datetime.timedelta(seconds=3600)        # Updating last measurements with "empty" and updating lastone
            new_dates.append(lastone)
            new_slev.append(999.0)
            new_qual.append(9)

        if thisone-lastone<datetime.timedelta(seconds=3600):    # Checking just to be sure no infiloops
            exit("Now we got proobleems in checking time difference between measurements: search_next/Function8")

        end_condition=timediff_okey(lastone, thisone)
        print(count, lastone,thisone,new_slev[len(new_dates)-1])
    print("Loop count: ",count)
    return new_dates, new_slev,new_qual

#Function 9
# Called by: , Calls: -
def timediff_okey(date1,date2):
    #Called by: search_next & order_file, Calls: -
    # Checks that the time step is 1h long
    okey=True
    if date2-date1!=datetime.timedelta(seconds=3600):
        okey=False
    return okey

# Function 10
def check_values(values):
    # Called by: , Calls: -
    # Checks how many values as Nan and changes the values to cm
    count=0
    maxi=values[0]
    mini=values[0]
    values_new=[]
    quality=[]

    for line in values:
        if np.isnan(line):
            count=count+1
            values_new.append(line)
            quality.append(9)
        else:
            if line>maxi:
                maxi=line
            if line<mini:
                mini=line
            values_new.append(0.1*line)             #change to cm
            quality.append(1)
    #print(values[0:5],values_new[0:5])
    #print('Max: '+str(maxi))
    #print('Min: '+str(mini))

    return(count,values_new,quality)

# Function 11
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

#Function 12
def fill_headers(Headers,missing,total,starttime,endtime):
    # Called by: , Calls: -
    # Fills headers
    # Almost completely like in tgtools
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)

    return Headers

# Function 13
def write_output(HeaderDict, data, order, outputfile):
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
    for ind in range(len(data)):
        file.write(data[ind])
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