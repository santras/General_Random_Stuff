#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import numpy as np
import os, glob
import pandas as pd
from timeit import default_timer as timer


# The purpose of this code is to test which way of reading in the variables is the most effiecint in this situation.
# File name and path are given as a variable filename (in the beginning of this file). Each test is reapeated 6 times
# and the average is taken.
# At the moment this is a bit off, since I do different things to different test.. but I think it does give an estimation

filename="../Ruotsi/Stockholm_smhi-opendata_6_2069_20170904_033725.csv"




def simple_open(name):

    start = timer()
    try:
        file=open(name,"r")
        data=file.readlines()
        file.close()
    except:
        exit("Can't test, can't open file./simple")
    end = timer()

    res=end-start
    return res


def pandas_open(name):

    start = timer()
    #try:
    data=pd.read_csv(name,header=20)
    #except:
        #exit("Can't test, can't open file./pandas")
    end = timer()

    res=end-start
    return res

def numpy_open(name):

    start = timer()
    try:
        data=np.loadtxt(name,skiprows=20,delimiter=(";"),usecols=1)
    except:
       exit("Can't test, can't open file./numpy")
    end = timer()

    res=end-start
    return res



def main():

    timer_res=[]
    for i in range(0,6):
        timer_res.append(simple_open(filename))
    print("Simple: ",timer_res)
    print("Simple average: ",np.average(timer_res))

    timer_res=[]
    for i in range(0, 6):
        timer_res.append(pandas_open(filename))
    print("Pandas: ", timer_res)
    print("Pandas average: ", np.average(timer_res))

    timer_res = []
    for i in range(0, 1):
        timer_res.append(numpy_open(filename))
    print("Numpy: ", timer_res)
    print("Numpy average: ", np.average(timer_res))


if __name__ == '__main__':
    main()