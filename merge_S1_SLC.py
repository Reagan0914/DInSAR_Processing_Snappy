"""
There are times when a certain Sentinel 1 acquired image will not completely overlap with your area of interest.
In such a scenario, we have multiple images acquired from the same date that cover our study area.

In this script, we take multiple (actually two!) Sentinel 1 SLC raw images acquired along the same relative orbit track (check product metadata)
and merge them in a way that the study area can be completely accounted for.

The script is borne out of the discussion on ESA's Step Forum: https://forum.step.esa.int/t/concatenate-two-s1-tops-slc-products/3555/2 

This script will do the following tasks:
1. Apply TOPSAR Split to each image. Make sure that after the images have been split, the entire area covered by them should overlap with your area of interest. 
   In doing so, we must account for what sub-swath and what # of bursts actually fall in the area you're interested in. 
   Use the WorldView in SNAP desktop to guide your parameter tuning.   
2. Apply TOPSAR Slice Assembly. In this step we have to tell the algorithm TOPSAR Split products that we want to concatenate. We will export them in BEAM-DIMAP format. 
"""

#------------Import Libraries---------------#
import os
import subprocess
import shutil
import snappy
from snappy import ProductIO
from snappy import GPF
from snappy import HashMap
from snappy import jpy
from datetime import datetime 
import sys
from multiprocessing import Process

HashMap = jpy.get_type('java.util.HashMap')
parameters = HashMap()

#--------------Declare Input and Output Directories-------------------------#
path_files_to_be_merged = r"D:\Sentinel-1 Subsidence\Raw Data"
output_dir = r"D:\Sentinel-1 Subsidence\Raw Data"

#-------------Get Filenames------------#
files = []
for f in os.listdir(path_files_to_be_merged):
    if f.split('_')[5][:8] == '20200609': # Day for which there are multiple files
        files.append(f)

def read(filename):
    return ProductIO.readProduct(filename)

def write(product, filename, format=None):
    return ProductIO.writeProduct(product, filename, format if format else "BEAM-DIMAP")
    # Allowed formats to write: GeoTIFF-BigTIFF,HDF5,Snaphu,BEAM-DIMAP,
	# GeoTIFF+XML,PolSARPro,NetCDF-CF,NetCDF-BEAM,ENVI,JP2,
    # Generic Binary BSQ,Gamma,CSV,NetCDF4-CF,GeoTIFF,NetCDF4-BEAM

def TOPSAR_split(product, first_burst, last_burst):
    parameters = HashMap()
    parameters.put('subswath', 'IW1')
    parameters.put('selectedPolarisations', 'VV')
    parameters.put('firstBurstIndex', first_burst)
    parameters.put('lastBurstIndex', last_burst)
    return GPF.createProduct('TOPSAR-Split', parameters, product)

def Slice_Assembly(list_of_products):
    parameters = HashMap()
    parameters.put('selectedPolarizations', 'VV')
    return GPF.createProduct('SliceAssembly', parameters, list_of_products)

def combine():
    #print("Started Processing at: {}".format(datetime.now()))
    #print('Reading SAR data')
    file1 = read(os.path.join(path_files_to_be_merged, files[0]))
    file2 = read(os.path.join(path_files_to_be_merged, files[1]))
    #print(file1.getName())
    #print(file2.getName())
    #print("Apply Slice Assembly")
    merged_product = Slice_Assembly((TOPSAR_split(file1, 8, 9),TOPSAR_split(file2, 1, 2)))
    write(merged_product, output_dir + "\S1_SLC_{}_{}_{}_Split_SplAmb".format(files[0].split('_')[5][:8], files[0].split('_')[-1][:-4], files[1].split('_')[-1][:-4]))
    return merged_product

if __name__ == '__main__':
    process = Process(target=combine)
    process.start()
    process.join()


