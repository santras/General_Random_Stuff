#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob


# The purpose of this code is to change SMHI Open Data to GL-format
# Test that all date in order and no missing values
# Makes header from a file that contains the header titles and the order, location of the file header.txt can be
# changed from the beginning of this file
# Writes output file in the "gl"-format.


path="..\Data_GPS\GPS_enu\\"                      # Path for the original data file folder, best not to have anything else
output_path= "..\GPS_txt\\"      # than the .txt data file in this directory




# Function 3
def open_files(file):
    #Called by: Main , Calls: update_header/Function7
    # Opens Swedens open data .csv files and sorts the problem with Scandinavian letters, then reads the data and
    # updates the header
    okey=True
    try:
        file_ = open(file, 'r')
        data = file_.readlines()
        file_.close()

    except:
        print("Problem opening file: ", file)
        data = []
        okey = False

    date_num=[]
    date_=[]
    east=[]
    north=[]
    up = []

    for ind in range(len(data)):
            date_num.append(float(data[ind].split()[0]))   # Reads in the variables
            date_ .append( datetime.datetime(2000,1,1,0,0) + datetime.timedelta(hours=date_num[-1]))
            east.append(float(data[ind].split()[1]))
            north.append(float(data[ind].split()[2]))
            up.append(float(data[ind].split()[3]))

    return date_,east,north, up, okey

# Function 4
def process_file(name,date_,east,north, up):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and then calls in functions to check that data is in order
    # and creates needed variables for header, then it updates and orders the header and finally writes the output.


    output_file=output_path+name[:-4]+".txt"
    #output_path+"Gl_"+station.replace(" ", "")+".txt"                   # HERE OUTPUTFILENAME
    # output_file=output_path+"Gl_"+filename[:-3]+".txt"

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    write_output(date_ ,east,north, up,output_file)                             # Function 9



# Function 9
def write_output(date_ ,east,north, up,output_file):
    # Called by: process_file /Function 4  , Calls: -
    # Writes the output

    file = open(output_file, 'w')
    #print(output)

    # Writing headers

    # Writing values
    date=[]
    time=[]

    for ii in range(len(date_)):
        date.append((date_[ii]).strftime("%Y-%m-%d"))
        time.append((date_[ii]).strftime("%H:%M"))

    prints=[]
    for ind in range(len(date)):
        prints.append("{}\t{}\t{:6.4}\t{:6.4}\t{:6.4}\n".format(date[ind],time[ind],east[ind],north[ind],up[ind]))

    for ind in range(len(date_)):
        file.write(prints[ind])
    file.close()





####################################################################################################



def main():
    # Called by: -, Calls: get_headers/Function2, open_swedenfiles/Function 3, process_file/Function 4
    # Use: See readme file

    os.chdir(path)
    for file in glob.glob("*.enu"):                 # Opens all that ends with .enu in the path folder one by one
        (date_,east,north, up, okey)=open_files(file)        # Function 3
        # open_swedenfiles opens the files, updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable
        if not okey:
            print("Something went wrong opening datafile, exiting program.")
            exit()
        print(file)
        process_file(file, date_,east,north, up) # Function 4
        # process_file, checks the order, adds missing, counts some header info, writes gl-files





if __name__ == '__main__':
    main()