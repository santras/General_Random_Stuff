#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to test the stations sea level values by plotting the data

#path="..\Data_new\Other\\"
#path2="..\CMEMS_hourly_EVRF07\Fast_check\\"     # Path for the original data file folder, best not to have anything else
path="..\Data_new\Other\Time_range\\"
path2="..\..\CMEMS_hourly_EVRF07\Fast_check\\"

output_path= ".\\"      # Outputpath for images
headerfilename=("header.txt")

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
    Headers["Interval"] = "1 hour"
    Headers["Time system"] = "UTC"
    return Headers

# Function 5
def process_file(filename,sl_variables,sl_variables2,Headers,order,station):
    # Called by: Main, Calls: write_output/Function9
    # Makes an output folder if it doesen't exist and then calls in functions to check that data is in order
    # and creates needed variables for header, then it updates and orders the header and finally writes the output.


    output_file=output_path+station.replace(" ", "")+"_pic.png"                   # HERE OUTPUTFILENAME
    # output_file=output_path+"Gl_"+filename[:-3]+".txt"                             # replace takes away empty spaces

    #print("outputpath",output_path)
    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    #print(Headers)
    #print(output_file)
    if len(sl_variables)==0:
        return

    sl_variables=sorted(sl_variables)
    print_var=[]
    count_dif=[]
    for ind in range(len(sl_variables)):
        #if (sl_variables[ind][0]>=datetime.datetime(2014,5,1)):
        for inde in range(len(sl_variables2)):
            if sl_variables[ind][0]==sl_variables2[inde][0]:
                #if (not np.isnan(sl_variables[ind][1])) and (not np.isnan(sl_variables2[inde][1])):
                if ((sl_variables[ind][1])<500) and ((sl_variables2[inde][1]<500)):
                    print_var.append([sl_variables[ind][0],sl_variables[ind][1]+37.7,sl_variables2[inde][1]])
                    count_dif.append(sl_variables[ind][1]+37.7-sl_variables2[inde][1])

    values = []
    print("Diff (W-wowo-Hel): ",np.nanmean(count_dif),np.nanmedian(count_dif),np.nanmin(count_dif),np.nanmax(count_dif),np.nanstd(count_dif))
    #write_plot(count_dif,"W-wowo-Hel","W_wowoHel.png",np.nanmax(count_dif),np.nanmin(count_dif))
    for i in range(3):
        values.append([row[i] for row in print_var])
    maxi = (np.nanmax(values[1]))
    mini=(np.nanmin(values[1]))
    time=values[0]
    #print(time[0:3])

    if (np.nanmax(values[2])>maxi):
        maxi=np.nanmax(values[2])
    if (np.nanmin(values[2]))<mini:
        mini=(np.nanmin(values[2]))

    #print(mini,maxi)

    write_plot(values, station, output_file, maxi, mini)


    #print(print_var[0:5])

    # else:
    #     year=[]
    #     month=[]
    #
    #     for ind in range(len(sl_variables)):
    #         year.append(sl_variables[ind][0].strftime("%Y"))
    #         month.append(sl_variables[ind][0].strftime("%m"))
    #
    #     values = []
    #     for i in range(3):
    #         values.append([row[i] for row in sl_variables])
    #
    #     maxi=(np.nanmax(values[1]))
    #     mini=(np.nanmin(values[1]))
    #     #print(month)
    #     counter=1
    #
    #     for y_num in sorted(set(year)):
    #         for m_num in sorted(set(month)):
    #             month_values = []
    #             output_file=output_path+station.replace(" ","")+"_"+y_num+m_num+"_"+to_outputname+".png"
    #             for ind in range(len(sl_variables)):
    #                 if year[ind]==y_num and month[ind]==m_num :
    #                     if not np.isnan(sl_variables[ind][1]):
    #                         month_values.append(sl_variables[ind])
    #             if len(month_values)!=0:
    #                 write_plot(month_values,station,output_file,maxi,mini)
    #
    #     return



   # write_plot(sl_variables,station,output_file)                             # Function 10


# Function 6
def write_plot(values, station, outputfile,maxi,mini):
    # Called by: process_file /Function 4  , Calls: -
    # Plots
    figu=plt.figure()
    #transposed = []  # Trick to only send timestamps to the check_listorder function 7
    #for i in range(3):
    #    transposed.append([row[i] for row in sl_variables])

    if station=="Hel":
        station="Wladislawowo-Hel"

    #s1mask = np.isfinite(values[1])
    plt.plot(values[0],values[1],linestyle="none",marker=".",color="b", markersize=4, label="Wladislawowo")   # marker='.' linestyle='-'
    plt.plot(values[0],values[2],linestyle="none",marker=".",color="r", markersize=4, label="Hel")      #'b'
    plt.gcf().autofmt_xdate()
    plt.xlabel("Time")
    plt.ylabel("Sea Level")
    plt.xlim(np.min(values[0]), np.max(values[0]))
    plt.ylim(mini, maxi)
    plt.title(station.upper())
    plt.legend()
    #plt.legend()
    #plt.show()
    figu.savefig(outputfile)
    plt.close(figu)



####################################################################################################



def main():
    # Called by: -, Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, getting header model
    os.chdir(path)
    print(path)
    for file in glob.glob("*01.txt"):                 # Opens all that ends with .txt in the path folder one by one
        print(file)
        (sl_variables,Header_dict,station,okey)=open_cmemsfiles(file,Header_dict)        # Function 3
        #open_cmemsfiles ,updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable
        if not okey:
            print("Something went wrong opening Cmems file",file,"exiting program.")
            exit()

        if station=="Wladyslawowo":
            station="Hel"

        find_name = path2+ station + "_EVRF2007.txt"

        #print(find_name)
        (sl_variables2, Header_dict, station2, okey) = open_cmemsfiles(find_name, Header_dict)
        if not okey:
            print("Something went wrong opening second Cmems file", file, "exiting program.")
            exit()


        process_file(file,sl_variables,sl_variables2,Header_dict,header_order,station) # Function 5
        # process_file, makes pictures





if __name__ == '__main__':
    main()