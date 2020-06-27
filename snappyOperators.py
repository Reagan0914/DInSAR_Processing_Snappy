"""
This file contains the definitions for
SNAP operators functions that will be used to process Sentienl 1 SAR data
"""

import logging
import os
import shutil
import subprocess
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
    TOPSAR_Split_Out = GPF.createProduct("TOPSAR-Split", parameters, inFile)
    logger.info("Finished Process: TOPSAR Split")
    return TOPSAR_Split_Out

def ApplyOrbitFile(inFile):
    parameters = sc.ApplyOrbitFile_config()
    ApplyOrbitFile_Out = GPF.createProduct('Apply-Orbit-File', parameters, inFile)
    logger.info("Finished Process: Apply Orbit File")
    return ApplyOrbitFile_Out

def BackGeocoding(inFile1, inFile2):
    '''
    Coregistration of Master and Slave Sentinel 1 SLC Images
    '''
    parameters = sc.BackGeocoding_config()
    BackGeocoding_Out = GPF.createProduct('Back-Geocoding', parameters, [inFile1, inFile2])
    logger.info("Finished Process: Back Geocoding")
    return BackGeocoding_Out

def EnhancedSpectralDiversity(inFile):
    parameters = sc.EnhancedSpectralDiversity_config()
    EnhancedSpectralDiversity_Out = GPF.createProduct('Enhanced-Spectral-Diversity', parameters, inFile)
    logger.info("Finished Process: Enhanced Spectral Diversity")
    return EnhancedSpectralDiversity_Out

def Interferogram(inFile`):
    parameters = sc.Interferogram_config()
    Interferogram_Out = GPF.createProduct('Interferogram', parameters, inFile)
    logger.info("Finished Process: Interferogram")
    return Interferogram_Out

def TOPSAR_Deburst(inFile):
    parameters = sc.TOPSAR_Deburst_config()
    TOPSAR_Deburst_Out = GPF.createProduct('TOPSAR-Deburst', parameters, inFile)
    logger.info("Finished Process: TOPSAR-Deburst")
    return TOPSAR_Deburst_Out

def TopoPhaseRemoval(inFile):
    parameters = sc.TopoPhaseRemoval_config()
    TopoPhaseRemoval_Out = GPF.createProduct('TopoPhaseRemoval', parameters, inFile)
    logger.info("Finished Process: Topographic Phase Removal")
    return TopoPhaseRemoval_Out

def Multilook(inFile):
    parameters = sc.Multilook_config()
    Multilook_Out = GPF.createProduct('Multilook`', parameters, inFile)
    logger.info("Finished Process: Multilook")
    return Multilook_Out

def GoldsteinPhaseFiltering(inFile):
    parameters = sc.GoldsteinPhaseFiltering_config()
    GoldsteinPhaseFiltering_Out = GPF.createProduct('GoldsteinPhaseFiltering', parameters, inFile)
    logger.info("Finished Process: Goldstein Phase Filtering")
    return GoldsteinPhaseFiltering_Out

def SnaphuExport(inFile, targetFolder):
    parameters = sc.SnaphuExport_config()
    SnaphuExport_Out = GPF.createProduct('SnaphuExport', parameters, inFile)
    logger.info("Finished Process: Snaphu Export")
    return SnaphuExport_Out

def list_files_in_directory(dir_path):
    print ("Files present in the directory called {} are: \n".format(dir_path))
    for f in os.listdir(dir_path):
        print(f)

def copytree(src, dst, symlinks=False, ignore=None):
    """https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth"""
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def get_snaphu_command_from_config_file():
    with open(snaphu_bin_path + "\snaphu.conf") as f:
        snaphu_config_file = f.readlines()
        snaphu_cmd = ""
        for line in snaphu_config_file:
            if "snaphu -f" in line:
                snaphu_cmd = line
        snaphu_cmd = snaphu_cmd.replace("#", "").lstrip()
    return snaphu_cmd

def unwrap_phase(command):
    os.chdir(snaphu_bin_path)
    return subprocess.call(command, shell=True)

def read_unwrapped_phase():
    for f in os.listdir(snaphu_bin_path):
        if f.endswith('.hdr') and 'UnwPhase' in f:
            unwrapped_phase_product = read(snaphu_bin_path + "\\" + f)
    return unwrapped_phase_product

def SnaphuImport(inFile1, inFile2):
    parameters = sc.SnaphuImport_config()
    SnaphuImport_Out = GPF.createProduct('SnaphuImport', parameters, [inFile1, inFile2])
    logger.info("Finished Process: Snaphu Import")
    return SnaphuImport_Out

def PhaseToDisplacement(inFile):
    parameters = sc.Default_config()
    PhaseToDisplacement_Out = GPF.createProduct("PhaseToDisplacement", parameters, inFile)
    logger.info("Finished Process: Phase to Displacement")
    return PhaseToDisplacement_Out

def TerrainCorrection(inFile, Projection):
    parameters = sc.TerrainCorrection_config(Projection)
    TerrainCorrection_Out = GPF.createProduct('Terrain-Correction', parameters, inFile)
    logger.info("Finished Process: Terrain Correction")
    return TerrainCorrection_Out

def CreateStack(inFiles):
    parameters = sc.CreateStack_config()
    CreateStack_Out = GPF.createProduct('CreateStack', parameters, inFiles)
    logger.info("Finished Process: Create Stack")
    return CreateStack_Out
