# Credit
'''
1. https://gist.github.com/braunfuss/41caab61817fbae71a25bba82a02a8c0 
2. https://forum.step.esa.int/t/slower-snappy-processing/6354/7 {How to improve snappy's performance and increase the processing speed}
3. http://step.esa.int/docs/tutorials/Performing%20SAR%20processing%20in%20Python%20using%20snappy.pdf {Visualising Bands via Plotting Function}
4. https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth {Copying file from one directory to another}
5. https://forum.step.esa.int/t/surface-subsidence/5180/7 {How to estimate average vertical displacement}
'''

# Import Libraries
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
from merge_S1_SLC import combine
#----------------------------------#

HashMap = jpy.get_type('java.util.HashMap')
parameters = HashMap()

path_S1_SLC_data = r'D:\Sentinel-1 Subsidence\Raw Data' # E:\Sentinel 1 Code\Data\Original' #### Used only for testing
processing_output_dir = r"E:\Sentinel 1 Code\Data\Processing"
output_dir = r"E:\Sentinel 1 Code\Data\Output"
snaphu_bin_path = r"E:\Sentinel 1 Code\Data\snaphu\bin"
snaphin_dir_path = r'E:\Sentinel 1 Code\Data\Processing\snaphin'
snaphu_export_dir_name = 'snaphin'

UTM_WGS84 = "GEOGCS[\"WGS84(DD)\",DATUM[\"WGS84\",SPHEROID[\"WGS84\", 6378137.0, 298.257223563]]," \
            "PRIMEM[\"Greenwich\", 0.0],UNIT[\"degree\", 0.017453292519943295],AXIS[\"Geodetic longitude\", EAST]," \
            "AXIS[\"Geodetic latitude\", NORTH]] " 

def read(filename):
    return ProductIO.readProduct(filename)

def write(product, filename, format=None):
    return ProductIO.writeProduct(product, filename, format if format else "BEAM-DIMAP")
    # Allowed formats to write: GeoTIFF-BigTIFF,HDF5,Snaphu,BEAM-DIMAP,
	# GeoTIFF+XML,PolSARPro,NetCDF-CF,NetCDF-BEAM,ENVI,JP2,
    # Generic Binary BSQ,Gamma,CSV,NetCDF4-CF,GeoTIFF,NetCDF4-BEAM

def TOPSAR_split(product, firstBurstIndex, lastBurstIndex):
    parameters = HashMap()
    parameters.put('subswath', 'IW1')
    parameters.put('selectedPolarisations', 'VV')
    parameters.put('firstBurstIndex', firstBurstIndex)
    parameters.put('lastBurstIndex', lastBurstIndex)
    return GPF.createProduct('TOPSAR-Split', parameters, product)

def TOPSAR_split_m(product):
    parameters = HashMap()
    parameters.put('subswath', 'IW1')
    parameters.put('selectedPolarisations', 'VV')
    parameters.put('firstBurstIndex', 6)
    parameters.put('lastBurstIndex', 9)
    return GPF.createProduct('TOPSAR-Split', parameters, product)

def TOPSAR_split_s(product):
    parameters = HashMap()
    parameters.put('subswath', 'IW1')
    parameters.put('selectedPolarisations', 'VV')
    parameters.put('firstBurstIndex', 3)
    parameters.put('lastBurstIndex', 6)
    return GPF.createProduct('TOPSAR-Split', parameters, product)

def apply_orbit_file(product):
    parameters = HashMap()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', 3)
    parameters.put('continueOnFail', True)
    return GPF.createProduct('Apply-Orbit-File', parameters, product)

def back_geocoding(product):    
    parameters = HashMap()
    parameters.put("Digital Elevation Model", "SRTM 1Sec HGT")
    parameters.put("DEM Resampling Method", "BICUBIC_INTERPOLATION")
    parameters.put("Resampling Type", "BISINC_5_POINT_INTERPOLATION")
    parameters.put("Mask out areas with no elevation", True)
    parameters.put("Output Deramp and Demod Phase", True)    
    return GPF.createProduct("Back-Geocoding", parameters, product)

def enhanced_spectral_diversity(product):
    parameters = HashMap()
    parameters.put("fineWinWidthStr", 512)
    parameters.put("fineWinHeightStr", 512)
    parameters.put("fineWinAccAzimuth", 16)
    parameters.put("fineWinAccRange", 16)
    parameters.put("fineWinOversampling", 128)
    parameters.put("xCorrThreshold", 0.1)
    parameters.put("cohThreshold", 0.15)
    parameters.put("numBlocksPerOverlap", 10)
    parameters.put("useSuppliedRangeShift", False)
    parameters.put("overallRangeShift", 0.0)
    parameters.put("useSuppliedAzimuthShift",False)
    parameters.put("overallAzimuthShift",0.0)
    return GPF.createProduct('Enhanced-Spectral-Diversity', parameters, product)

def interferogram(product):
    parameters = HashMap()  
    parameters.put("Subtract flat-earth phase", True)
    parameters.put("Degree of \"Flat Earth\" polynomial", 5)
    parameters.put("Number of \"Flat Earth\" estimation points", 501)
    parameters.put("Orbit interpolation degree", 3)
    parameters.put("Include coherence estimation", True)
    parameters.put("Square Pixel", True)
    parameters.put("Independent Window Sizes", False)
    parameters.put("Coherence Azimuth Window Size", 5)
    parameters.put("Coherence Range Window Size", 20)
    return GPF.createProduct("Interferogram", parameters, product)

def topsar_deburst(product):
    parameters = HashMap()
    parameters.put('selectedPolarisations','VV')
    return GPF.createProduct('TOPSAR-Deburst', parameters, product)

def topophase_removal(product):
    parameters = HashMap()
    parameters.put("Orbit Interpolation Degree", 3)
    parameters.put("Digital Elevation Model", "SRTM 1Sec HGT")
    parameters.put("Tile Extension[%]", 100)
    parameters.put("Output topographic phase band", True)
    parameters.put("Output elevation band", False)
    return GPF.createProduct("TopoPhaseRemoval", parameters, product)

def multilook(product):
    parameters = HashMap()
    parameters.put("GR Square Pixel", True)
    parameters.put("nRgLooks", 8)
    parameters.put("nAzLooks", 2)
    return GPF.createProduct('Multilook', parameters, product)

def goldstein_phasefiltering(product):
    parameters.put("Adaptive Filter Exponent in(0,1]:", 1.0)
    parameters.put("FFT Size", 64)
    parameters.put("Window Size", 3)
    parameters.put("Use coherence mask", False)
    parameters.put("Coherence Threshold in[0,1]:", 0.2)
    return GPF.createProduct("GoldsteinPhaseFiltering", parameters, product)

def snaphu_export(product, snaphu_directory):
    parameters = HashMap()
    parameters.put("targetFolder", snaphu_directory)
    parameters.put("statCostMode", "DEFO")
    parameters.put("initMethod", "MCF")
    parameters.put("numberOfTileRows", 5)
    parameters.put("numberOfTileCols", 5)
    parameters.put("numberOfProcessors", 32)
    parameters.put("rowOverlap", 0)
    parameters.put("colOverlap", 0)
    parameters.put("tileCostThreshold", 500)
    return GPF.createProduct("SnaphuExport", parameters, product)

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

def snaphu_import(src1, src2):
    parameters = HashMap()
    parameters.put("doNotKeepWrapped", True)
    return GPF.createProduct('SnaphuImport', parameters, [src1, src2])

def phase_to_disp(product):
    parameters = HashMap()
    return GPF.createProduct("PhaseToDisplacement", parameters, product)

def terrain_correction(src, projection):
    parameters = HashMap()
    parameters.put("demName", "SRTM 1Sec HGT")  # ~25 to 30m
    parameters.put("externalDEMNoDataValue", 0.0)
    parameters.put("externalDEMApplyEGM", True)
    parameters.put("demResamplingMethod", "BICUBIC_INTERPOLATION")
    parameters.put("imgResamplingMethod", "BICUBIC_INTERPOLATION")
    parameters.put("pixelSpacingInMeter", 10.0)
    parameters.put("pixelSpacingInDegree", 8.983152841195215E-5)
    parameters.put("mapProjection", projection)
    parameters.put("alignToStandardGrid", False)
    parameters.put("standardGridOriginX", 0.0)
    parameters.put("standardGridOriginY", 0.0)
    parameters.put("nodataValueAtSea", True)
    parameters.put("saveDEM", False)
    parameters.put("saveLatLon", False)
    parameters.put("saveIncidenceAngleFromEllipsoid", False)
    parameters.put("saveLocalIncidenceAngle", False)
    parameters.put("saveSelectedSourceBand", True)
    parameters.put("outputComplex", False)
    parameters.put("applyRadiometricNormalization", False)
    parameters.put("saveSigmaNought", False)
    parameters.put("saveGammaNought", False)
    parameters.put("saveBetaNought", False)
    parameters.put("incidenceAngleForSigma0", "Use projected local incidence angle from DEM")
    parameters.put("incidenceAngleForGamma0", "Use projected local incidence angle from DEM")
    parameters.put("auxFile", "Latest Auxiliary File")
    return GPF.createProduct("Terrain-Correction", parameters, src)

def create_stack(src):
    parameters = HashMap()
    parameters.put("resamplingType", "NONE")
    parameters.put("extent", "Master")
    parameters.put("initialOffsetMethod", "Product Geolocation")
    return GPF.createProduct("CreateStack", parameters, src)

def band_math(src, band_name, expression):
    parameters = HashMap()
    band_descriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    target_band = band_descriptor()
    target_band.name = band_name
    target_band.type = 'float32'
    target_band.expression = expression
        
    target_bands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    target_bands[0] = target_band
    parameters.put('targetBands', target_bands)
    
    return GPF.createProduct("BandMaths", parameters, src)

def insar_pipeline(filename_1, filename_2):
    print("Started Processing at: {}".format(datetime.now()))
    print('Reading SAR data')
    master = read(filename_1) 
    slave = read(filename_2) 
    print("Master: ", filename_1)
    print("Slave: ", filename_2)

    print('TOPSAR-Split')
    master_TOPSAR_split = TOPSAR_split_m(master)
    slave_TOPSAR_split = TOPSAR_split_s(slave)
    
    print('Applying precise orbit files')
    master_orbitFile = apply_orbit_file(master_TOPSAR_split)
    slave_orbitFile = apply_orbit_file(slave_TOPSAR_split)
    
    print('back geocoding')
    backGeocoding = back_geocoding([master_orbitFile, slave_orbitFile])
    
    print('inerferogram generation')
    interferogram_product = interferogram(backGeocoding)
    
    print('TOPSAR_deburst')
    TOPSAR_deburst_product = topsar_deburst(interferogram_product)
    print("Writing TOPSAR Deburst File")
    write(TOPSAR_deburst_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb".format(date_m4, date_s4))
    print('Time Taken So Far: {}'.format(datetime.now()-t))

    print('TopoPhase removal')
    TOPO_phase_removal_product = topophase_removal(TOPSAR_deburst_product)
    
    print("Multilooking")
    Multilooked_Product = multilook(TOPO_phase_removal_product)
    
    print('Goldstein filtering')
    GP_filtering_product = goldstein_phasefiltering(Multilooked_Product)
    print("Writing Goldstein Filtered File")
    write(GP_filtering_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt".format(date_m5, date_s5))
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    
    print("SNAPHU Export")
    os.mkdir(os.path.join(processing_output_dir, snaphu_export_dir_name))
    snaphu_export_product = snaphu_export(GP_filtering_product, snaphin_dir_path)
    write(snaphu_export_product, snaphin_dir_path, "Snaphu")
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    print("Copying SNAPHU Export products to Snaphu 'bin' directory: \n")
    
    src_path = snaphin_dir_path           
    des_path = snaphu_bin_path
    copytree(src_path, des_path)
    #list_files_in_directory(des_path)
    print('Time Taken So Far: {}'.format(datetime.now()-t))

    print("Getting Snaphu Command from Config File")
    snaphu_command = get_snaphu_command_from_config_file()
    print("Started Phase Unwrapping using Snaphu")
    unwrap_phase(snaphu_command)
    print('Phase Unwrapping Finished in: {}'.format(datetime.now()-t))
    unwrapped_phase_product = read_unwrapped_phase()
    print(unwrapped_phase_product)
    print("Started SNAPHU Import")
    snaphu_import_product = snaphu_import(GP_filtering_product, unwrapped_phase_product)
    
    print("Convert Unwrapped Phase to Vertical Displacement")
    vertical_disp = phase_to_disp(snaphu_import_product)
    #print("Writing Displacement File")
    #write(vertical_disp, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt_Disp".format(date_m, date_s))

    print("Terrain Correction: Goldetein Filtering Prodcut: {}".format(GP_filtering_product.getName()))
    GPfiltered_TC = terrain_correction(GP_filtering_product, UTM_WGS84)
    #print("Writing Terrain Corrected Goldstein Filtered Product")
    #write(GPfiltered_TC, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt_TC".format(date_m, date_s))
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    print("Terrain Correction: Vertical Displacement Band: {}".format(vertical_disp.getName()))
    v_disp_TC = terrain_correction(vertical_disp, UTM_WGS84)
    #print("Writing Terrain Corrected Displacement Product")
    #write(v_disp_TC, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt_Disp_TC".format(date_m, date_s))
    print('Time Taken So Far: {}'.format(datetime.now()-t))

    # Stack together Coherence and Displacement Bands into a New Product
    print("Stacking Coherence, Intensity and Displacement Bands")
    stacked_product = create_stack([GPfiltered_TC, v_disp_TC])
    #print("Writing Stacked Product")
    #write(stacked_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt_Disp_TC_stack".format(date_m, date_s))
    
    print("Creating a Mask by removing low coherence values")
    band_names = list(stacked_product.getBandNames())
    # Use Band Maths to Create a new Band that masks out low coherence values
    masked_product1 = band_math(stacked_product, "displacement_masked_coh_point2","if {} <= 0.2 then NaN else {}".format(band_names[2], band_names[0]))
    masked_product2 = band_math(stacked_product, "displacement_masked_coh_point3","if {} <= 0.3 then NaN else {}".format(band_names[2], band_names[0]))
    masked_product3 = band_math(stacked_product, "displacement_masked_coh_point4","if {} <= 0.4 then NaN else {}".format(band_names[2], band_names[0]))
    
    print("Stacking the three Coherence Masked Displacement Bands along with Terrain Corrected Origianl Dispalcement and Goldstein Filtered Phase Product")
    final_stacked_product = create_stack([GPfiltered_TC, v_disp_TC, masked_product1, masked_product2, masked_product3])
    print("Saving Final Output as BEAM-DIMAP File")
    write(final_stacked_product, output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_FL_Disp_TC_Stack_Coh_masked".format(date_m4, date_s4))
    print("Processing Finished. Output File is Located at this directory {}".format(output_dir))
    print('Total Processing Time: {}'.format(datetime.now()-t))

def insar_pipeline_merged_master(merged_masterFile, slaveFile):
    print("Started Processing at: {}".format(datetime.now()))
    print('Reading SAR data')
    master = read(merged_masterFile) # May 16, 2020
    slave = read(slaveFile) # May 28, 2020
    print("Master: {}\n".format(master.getName()))
    print("Merged_Slave: {}\n".format(slave.getName()))
    master_TOPSAR_split = master
    slave_TOPSAR_split = TOPSAR_split(slave,6, 9)
    master_orbitFile = apply_orbit_file(master_TOPSAR_split)
    slave_orbitFile = apply_orbit_file(slave_TOPSAR_split)
    backGeocoding = back_geocoding([master_orbitFile, slave_orbitFile])
    interferogram_product = interferogram(backGeocoding)
    TOPSAR_deburst_product = topsar_deburst(interferogram_product)
    print("Writing Deburst Product. \n Check the directory: {}".format(processing_output_dir))
    write(TOPSAR_deburst_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb".format(date_m7, date_s7))
    TOPO_phase_removal_product = topophase_removal(TOPSAR_deburst_product)
    Multilooked_Product = multilook(TOPO_phase_removal_product)
    GP_filtering_product = goldstein_phasefiltering(Multilooked_Product)
    print("Writing Phase Filtered Product. \n Check the directory: {}".format(processing_output_dir))
    write(GP_filtering_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt".format(date_m7, date_s7))
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    print("SNAPHU Export")
    os.mkdir(os.path.join(processing_output_dir, snaphu_export_dir_name))
    snaphu_export_product = snaphu_export(GP_filtering_product, snaphin_dir_path)
    write(snaphu_export_product, snaphin_dir_path, "Snaphu")
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    src_path = snaphin_dir_path           
    des_path = snaphu_bin_path
    copytree(src_path, des_path)
    #list_files_in_directory(des_path)
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    snaphu_command = get_snaphu_command_from_config_file()
    print("Started Phase Unwrapping using Snaphu")
    unwrap_phase(snaphu_command)
    print('Phase Unwrapping Finished in: {}'.format(datetime.now()-t))
    unwrapped_phase_product = read_unwrapped_phase()
    print(unwrapped_phase_product)
    print("Started SNAPHU Import")
    snaphu_import_product = snaphu_import(GP_filtering_product, unwrapped_phase_product)
    
    print("Convert Unwrapped Phase to Vertical Displacement")
    vertical_disp = phase_to_disp(snaphu_import_product)
    print("Terrain Correction: Goldetein Filtering Prodcut: {}".format(GP_filtering_product.getName()))
    GPfiltered_TC = terrain_correction(GP_filtering_product, UTM_WGS84)
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    print("Terrain Correction: Vertical Displacement Band: {}".format(vertical_disp.getName()))
    v_disp_TC = terrain_correction(vertical_disp, UTM_WGS84)
    print('Time Taken So Far: {}'.format(datetime.now()-t))

    # Stack together Coherence and Displacement Bands into a New Product
    print("Stacking Coherence, Intensity and Displacement Bands")
    stacked_product = create_stack([GPfiltered_TC, v_disp_TC])
    print("Creating a Mask by removing low coherence values")
    band_names = list(stacked_product.getBandNames())
    # Use Band Maths to Create a new Band that masks out low coherence values
    masked_product1 = band_math(stacked_product, "displacement_masked_coh_point2","if {} <= 0.2 then NaN else {}".format(band_names[2], band_names[0]))
    masked_product2 = band_math(stacked_product, "displacement_masked_coh_point3","if {} <= 0.3 then NaN else {}".format(band_names[2], band_names[0]))
    masked_product3 = band_math(stacked_product, "displacement_masked_coh_point4","if {} <= 0.4 then NaN else {}".format(band_names[2], band_names[0]))
    
    print("Stacking the three Coherence Masked Displacement Bands along with Terrain Corrected Origianl Dispalcement and Goldstein Filtered Phase Product")
    final_stacked_product = create_stack([GPfiltered_TC, v_disp_TC, masked_product1, masked_product2, masked_product3])
    print("Saving Final Output as BEAM-DIMAP File")
    write(final_stacked_product, output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_FL_Disp_TC_Stack_Coh_masked".format(date_m7, date_s7))
    print("Processing Finished. Output File is Located at this directory {}".format(output_dir))
    print('Total Processing Time: {}'.format(datetime.now()-t))

def insar_pipeline_merged_slave(masterFile, merged_slaveFile):
    print("Started Processing at: {}".format(datetime.now()))
    print('Reading SAR data')
    master = read(masterFile) # May 4, 2020
    slave = read(merged_slaveFile) # May 16, 2020
    print("Master: {}\n".format(master.getName()))
    print("Merged_Slave: {}\n".format(slave.getName()))
    master_TOPSAR_split = TOPSAR_split_m(master)
    slave_TOPSAR_split = slave
    master_orbitFile = apply_orbit_file(master_TOPSAR_split)
    slave_orbitFile = apply_orbit_file(slave_TOPSAR_split)
    backGeocoding = back_geocoding([master_orbitFile, slave_orbitFile])
    interferogram_product = interferogram(backGeocoding)
    TOPSAR_deburst_product = topsar_deburst(interferogram_product)
    print("Writing Deburst Product")
    #write(TOPSAR_deburst_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb".format(date_m8, date_s8))
    TOPO_phase_removal_product = topophase_removal(TOPSAR_deburst_product)
    Multilooked_Product = multilook(TOPO_phase_removal_product)
    GP_filtering_product = goldstein_phasefiltering(Multilooked_Product)
    print("Writing Phase Filtered Product")
    #write(GP_filtering_product, processing_output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_Flt".format(date_m8, date_s8))
    print("SNAPHU Export")
    os.mkdir(os.path.join(processing_output_dir, snaphu_export_dir_name))
    snaphu_export_product = snaphu_export(GP_filtering_product, snaphin_dir_path)
    #write(snaphu_export_product, snaphin_dir_path, "Snaphu")
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    src_path = snaphin_dir_path           
    des_path = snaphu_bin_path
    #copytree(src_path, des_path)
    #list_files_in_directory(des_path)
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    snaphu_command = get_snaphu_command_from_config_file()
    print("Started Phase Unwrapping using Snaphu")
    unwrap_phase(snaphu_command)
    print('Phase Unwrapping Finished in: {}'.format(datetime.now()-t))
    unwrapped_phase_product = read_unwrapped_phase()
    print(unwrapped_phase_product)
    print("Started SNAPHU Import")
    snaphu_import_product = snaphu_import(GP_filtering_product, unwrapped_phase_product)
    
    print("Convert Unwrapped Phase to Vertical Displacement")
    vertical_disp = phase_to_disp(snaphu_import_product)
    print("Terrain Correction: Goldetein Filtering Prodcut: {}".format(GP_filtering_product.getName()))
    GPfiltered_TC = terrain_correction(GP_filtering_product, UTM_WGS84)
    print('Time Taken So Far: {}'.format(datetime.now()-t))
    print("Terrain Correction: Vertical Displacement Band: {}".format(vertical_disp.getName()))
    v_disp_TC = terrain_correction(vertical_disp, UTM_WGS84)
    print('Time Taken So Far: {}'.format(datetime.now()-t))

    # Stack together Coherence and Displacement Bands into a New Product
    print("Stacking Coherence, Intensity and Displacement Bands")
    stacked_product = create_stack([GPfiltered_TC, v_disp_TC])
    print("Creating a Mask by removing low coherence values")
    band_names = list(stacked_product.getBandNames())
    # Use Band Maths to Create a new Band that masks out low coherence values
    masked_product1 = band_math(stacked_product, "displacement_masked_coh_point2","if {} <= 0.2 then NaN else {}".format(band_names[2], band_names[0]))
    masked_product2 = band_math(stacked_product, "displacement_masked_coh_point3","if {} <= 0.3 then NaN else {}".format(band_names[2], band_names[0]))
    masked_product3 = band_math(stacked_product, "displacement_masked_coh_point4","if {} <= 0.4 then NaN else {}".format(band_names[2], band_names[0]))
    
    print("Stacking the three Coherence Masked Displacement Bands along with Terrain Corrected Origianl Dispalcement and Goldstein Filtered Phase Product")
    final_stacked_product = create_stack([GPfiltered_TC, v_disp_TC, masked_product1, masked_product2, masked_product3])
    print("Saving Final Output as BEAM-DIMAP File")
    #write(final_stacked_product, output_dir + "\S1_SLC_{}_{}_Split_Orb_Coreg_ESD_Ifg_Deb_DInSAR_ML_FL_Disp_TC_Stack_Coh_masked".format(date_m8, date_s8))
    print("Processing Finished. Output File is Located at this directory {}".format(output_dir))
    print('Total Processing Time: {}'.format(datetime.now()-t))
#-----------------------------------------------#

files = []
for f in os.listdir(path_S1_SLC_data):
    if f.endswith(".zip"):
        files.append(f)

file_path1 = os.path.join(path_S1_SLC_data, files[0]) # Mar 5 
file_path2 = os.path.join(path_S1_SLC_data, files[1]) # Mar 17
file_path3 = os.path.join(path_S1_SLC_data, files[2]) # Mar 29
file_path4 = os.path.join(path_S1_SLC_data, files[3]) # Apr 10
file_path5 = os.path.join(path_S1_SLC_data, files[4]) # Apr 22
file_path6 = os.path.join(path_S1_SLC_data, files[5]) # May 4
file_path7 = os.path.join(path_S1_SLC_data, files[6]) # May 16
file_path8 = os.path.join(path_S1_SLC_data, files[7]) # May 16
file_path9 = os.path.join(path_S1_SLC_data, files[8]) # May 28
file_path10 = os.path.join(path_S1_SLC_data, files[9]) # Jun 9
file_path11 = os.path.join(path_S1_SLC_data, files[10]) # Jun 9

files_to_be_processed_1 = [file_path1, file_path2]
files_to_be_processed_2 = [file_path2, file_path3]
files_to_be_processed_3 = [file_path3, file_path4]
files_to_be_processed_4 = [file_path4, file_path5]
files_to_be_processed_5 = [file_path5, file_path6]

dates_str = []
for i in files:
    dates_str.append(i.split('_')[5][:8]) # Extract the Data Aquisition Date from filename
date_m1 = dates_str[0]
date_s1 = dates_str[1]
date_m2 = dates_str[1]
date_s2 = dates_str[2]
date_m3 = dates_str[2]
date_s3 = dates_str[3]
date_m4 = dates_str[3]
date_s4 = dates_str[4]
date_m5 = dates_str[4]
date_s5 = dates_str[5]
date_m6 = dates_str[5]
date_s6 = dates_str[6]
date_m7 = dates_str[7]
date_s7 = dates_str[8]
date_m8 = '20200528'
date_s8 = '20200609'

#----------------------------------------------------#
t = datetime.now() # Start Time of the Script

if __name__ == "__main__":
    #process = Process(target=insar_pipeline, args=(files_to_be_processed_1[0], files_to_be_processed_1[1]))
    #process = Process(target=insar_pipeline, args=(files_to_be_processed_2[0], files_to_be_processed_2[1]))
    #process = Process(target=insar_pipeline, args=(files_to_be_processed_3[0], files_to_be_processed_3[1]))
    #process = Process(target=insar_pipeline, args=(files_to_be_processed_4[0], files_to_be_processed_4[1]))
    #process = Process(target=insar_pipeline, args=(files_to_be_processed_5[0], files_to_be_processed_5[1]))
    #process1 = Process(target=insar_pipeline_merged_slave, args=(file_path6, "D:\Sentinel-1 Subsidence\Raw Data\S1_SLC_20200516_B7AC_C089_Split_SplAmb.dim"))
    #process2 = Process(target=insar_pipeline_merged_master, args=("D:\Sentinel-1 Subsidence\Raw Data\S1_SLC_20200516_B7AC_C089_Split_SplAmb.dim", file_path9))
    process1 = Process(target=insar_pipeline_merged_slave, args=(file_path9, "D:\Sentinel-1 Subsidence\Raw Data\S1_SLC_20200609_1BC4_E18E_Split_SplAmb.dim"))
    process1.start()
    process1.join()
    print('Removing Snaphin Directory')
    shutil.rmtree(snaphin_dir_path)
    #process2.start()
    #process2.join()
    #print('Removing Snaphin Directory')
    #shutil.rmtree(snaphin_dir_path)
