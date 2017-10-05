#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import numpy as np
import os, glob
import pandas as pd

filename="../Ruotsi/b_testi.csv"
time_diff=3600 # timedifference between each measurement in seconds

# Function 1
def arrange_list(dates,slev,qual,difference):
    # Called by: Main, Calls: check_list/Function 2, sorting_hat/Function3
    (inorder,inds)=check_listorder(dates,difference)    # Function 2
    if not inorder:
        print("")
        variables=[]
        for ind in range(len(dates)):
            variables.append([dates[ind],slev[ind],qual[ind]])

        for inde in range(1,len(variables)):
            if variables[inde][0]<=variables[inde-1][0]:
                print("haa",inde)
        variables=(sorted(variables))

        for inde in range(1,len(variables)):
            if variables[inde][0]<=variables[inde-1][0]:
                print("buu")
            print(variables[inde])


def main():
    # Called by: - , Calls: arrange_list/Function1
    try:
        file_ = open(filename, 'r')
        data = file_.readlines()
        file_.close()
    except:
        exit("Can't open file: ",filename)
    date_str=[]
    slev=[]
    quality=[]
    for ind in range(0,len(data)):
        date_str.append(data[ind].split(";")[0])    # Reads in the variables
        slev.append(float(data[ind].split(";")[1]))
        quality.append(data[ind].split(";")[2])
    date=[]
    time=[]
    for line in date_str:
       date.append((line.split()[0]).strip())
       time.append((line.split()[1]).strip())

    date_time = []
    year = []
    month = []
    day = []
    hour = []
    min = []

    for line in date:
        splitline = line.split("-")
        year.append(int((splitline[0]).strip()))
        month.append(int((splitline[1]).strip()))
        day.append(int((splitline[2]).strip()))
    for clockline in time:
        splitline2 = clockline.split(":")
        hour.append(int((splitline2[0]).strip()))
        min.append(int((splitline2[1]).strip()))
    for i in range(len(year)):
        date_time.append(datetime.datetime(year[i], month[i], day[i], hour[i], min[i]))

    #print(date_time)
    #print(time_diff)
    arrange_list(date_time,slev,quality,time_diff)    # Function 1



if __name__ == '__main__':
    main()