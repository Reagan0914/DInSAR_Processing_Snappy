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
from SnappyTools import snappyConfig, snappyOperators as sp


#--------------Declare Input and Output Directories-------------------------#
product_PATH = r"D:\Sentinel-1 Subsidence\Raw Data"
output_dir = r"D:\Sentinel-1 Subsidence\Raw Data"
input_files = sorted(list(iglob(join(product_PATH, 'S1*.zip'))))

#--------------Find Input Files to be Merge------------------#
date = []
for f in input_files:
    date.append(f.split(" ")[-1].split("_")[5][:8])

def find_files_to_merge(list_of_input_files):
    files_to_merge = []
    for i in range(len(date)-1):
        if date[i] == date[i+1]:
            #print("\n" + "{}".format(input_files[i]) + "\n" + "{}".format(input_files[i+1]))
            files_to_merge.append(list_of_input_files[i])
            files_to_merge.append(list_of_input_files[i+1])
    return files_to_merge
