"""
This file contains the definitions for 
SNAP operators functions that will be used to process Sentienl 1 SAR data
"""

import logging
from snappy import GPF
from snappy import ProductIO
import snappyConfig as sc

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(name)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def read(filename):
    return ProductIO.readProduct(filename)

def write(product, filename, format=None):
    return ProductIO.writeProduct(product, filename, format if format else "BEAM-DIMAP")
    # Allowed formats to write: GeoTIFF-BigTIFF,HDF5,Snaphu,BEAM-DIMAP,
	# GeoTIFF+XML,PolSARPro,NetCDF-CF,NetCDF-BEAM,ENVI,JP2,
    # Generic Binary BSQ,Gamma,CSV,NetCDF4-CF,GeoTIFF,NetCDF4-BEAM

def TOPSAR_Split(inFile, subswath, firstBurstIndex, lastBurstIndex, polarizations):
    parameters = sc.TOPSAR_Split_config(subswath, firstBurstIndex, lastBurstIndex, polarizations)
    TOPSAR_Split_OutputProduct = GPF.createProduct("TOPSAR-Split", parameters, inFile)
    logger.info("Finished Process: TOPSAR Split")
    return TOPSAR_Split_OutputProduct

def ApplyOrbitFile(inFile):
    parameters = sc.ApplyOrbitFile_config()
    ApplyOrbitFile_OutputProduct = GPF.createProduct('Apply-Orbit-File', parameters, inFile)
    logger.info("Finished Process: Apply Orbit File")
    return ApplyOrbitFile_OutputProduct

def BackGeocoding():

