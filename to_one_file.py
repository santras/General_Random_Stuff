#!/usr/bin/env python
# coding: utf-8

# Purpose of this code is to make 1 file of the now separated decades of data of FMI Open Sealevels. Later I
# could modify the code to work on other stuff as well.

path=('.\Suomi\\')
folderlist=("FMIdata1971_1979\\", 'FMIdata1980_1989\\', 'FMIdata1990_1999\\', 'FMIdata2000_2009\\','FMIdata2010_2017\\')
outputfolder=('FMI_1971_2017\\')

def file_read(file_name):
    # Open a file
    try:
        file = open(file_name, 'r')
        data = file.readlines()
        file.close()
        ok = True
    except:
        print("File {} couldn't be opened".format(file_name))
        ok = False
        data = []
        return data, ok
    return data, ok


def file_process(file,round):
    (sdata,found)=file_read(file)
    if not found:
        print(file+' not found.')
        return found,[],[],[],[]
    if round==0:
        station_info=sdata[0]
        lat_info=sdata[1]
        lon_info=sdata[2]
    else:
        station_info=[]
        lat_info=[]
        lon_info=[]
    return found,station_info,lat_info,lon_info,sdata[4:]

def write_out(station,lat,lon,data):
    # Open a file
    if ((lat.split()[1]).strip())=='60.03188' and ((lon.split()[1]).strip())=='20.38482':  #Föglö
        name_dummu=(path+outputfolder+'Foglo')
    else:
        name_dummu=(path+outputfolder+(station.split()[1]))
    name=((name_dummu.strip())+'_NN2000.txt')
    try:
        file = open(name, 'w')
        file.writelines(station)
        file.writelines(lat)
        file.writelines(lon)
        file.writelines(data)
        file.close()
        ok = True
    except:
        ok = False
        exit(("File {} couldn't be opened or written".format(f_name)))

    return ok

def main():
    (names,okey)=file_read('filenames.txt')
    if not okey:
        exit('Unable to find namefile for filenames')
    for name_ind in range(len(names)):                       # One station at a time
        count=0
        station_data=[]
        for folder in folderlist:
            (found,station,lat,lon,data)=file_process(path+folder+(names[name_ind].strip()),count)
            if found:
                if count==0:
                    station_out=station
                    lat_out=lat
                    lon_out=lon
                count = count + 1
                station_data[len(station_data):(len(station_data)+len(data))]=data[0:len(data)]     # Check this
        write_success=write_out(station_out,lat_out,lon_out,station_data)



if __name__ == '__main__':
    main()