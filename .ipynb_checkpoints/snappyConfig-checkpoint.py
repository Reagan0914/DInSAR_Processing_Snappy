"""
This file contains parameter hashmap configurations for snappy preprocessing operators.

Any changes made here will affect the processing output.
"""

from snappy import HashMap
from snappy import jpy

SRTM1SEC = "SRTM 1Sec HGT"

UTM_WGS84 = "GEOGCS[\"WGS84(DD)\",DATUM[\"WGS84\",SPHEROID[\"WGS84\", 6378137.0, 298.257223563]]," \
            "PRIMEM[\"Greenwich\", 0.0],UNIT[\"degree\", 0.017453292519943295],AXIS[\"Geodetic longitude\", EAST]," \
            "AXIS[\"Geodetic latitude\", NORTH]] "

def TOPSAR_Split_config(subswath, firstBurstIndex, lastBurstIndex, polarizations):
    """
    This function ....
    """
    parameters = HashMap()
    parameters.put('subswath', subswath)
    parameters.put('selectedPolarisations', polarizations)
    parameters.put('firstBurstIndex', firstBurstIndex)
    parameters.put('lastBurstIndex', lastBurstIndex)
    return parameters

def ApplyOrbitFile_config():
    parameters = HashMap()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', 3)
    parameters.put('continueOnFail', True)
    return parameters

def BackGeocoding_config():
    parameters = HashMap()
    parameters.put("Digital Elevation Model", "SRTM 1Sec HGT")
    parameters.put("DEM Resampling Method", "BICUBIC_INTERPOLATION")
    parameters.put("Resampling Type", "BISINC_5_POINT_INTERPOLATION")
    parameters.put("Mask out areas with no elevation", True)
    parameters.put("Output Deramp and Demod Phase", True)
    return parameters

def EnhancedSpectralDiversity_config():
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
    return parameters

def Interferogram_config():
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
    return parameters

def TOPSAR_Deburst_config():
    parameters = HashMap()
    parameters.put('selectedPolarisations','VV')
    return parameters

def TopoPhaseRemoval_config():
    parameters = HashMap()
    parameters.put("Orbit Interpolation Degree", 3)
    parameters.put("Digital Elevation Model", "SRTM 1Sec HGT")
    parameters.put("Tile Extension[%]", 100)
    parameters.put("Output topographic phase band", True)
    parameters.put("Output elevation band", False)
    return parameters

def Multilook_config():
    parameters = HashMap()
    parameters.put("GR Square Pixel", True)
    parameters.put("nRgLooks", 8)
    parameters.put("nAzLooks", 2)
    return parameters

def GoldsteinPhaseFiltering_config():
    parameters = HashMap()
    parameters.put("Adaptive Filter Exponent in(0,1]:", 1.0)
    parameters.put("FFT Size", 64)
    parameters.put("Window Size", 3)
    parameters.put("Use coherence mask", False)
    parameters.put("Coherence Threshold in[0,1]:", 0.2)
    return parameters

def SnaphuExport_config(snaphu_directory):
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
    return parameters

def SnaphuImport_config():
    parameters = HashMap()
    parameters.put("doNotKeepWrapped", True)
    return parameters

def Default_config():
    return HashMap()

def TerrainCorrection_config(projection):
    '''Range Doppler Terrain Correction'''
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
    return parameters

def RadiometricCalibration_config():
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    return parameters

def CreateStack_config():
    parameters = HashMap()
    parameters.put("resamplingType", "NONE")
    parameters.put("extent", "Master")
    parameters.put("initialOffsetMethod", "Product Geolocation")
    return parameters

def BandMaths_config(BandName, expression):
    parameters = HashMap()
    band_descriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    target_band = band_descriptor()
    target_band.name = BandName
    target_band.type = 'float32'
    target_band.expression = expression
    target_bands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    target_bands[0] = target_band
    parameters.put('targetBands', target_bands)
    return parameters

def SliceAssembly_config():
    parameters = HashMap()
    parameters.put('selectedPolarizations', 'VV')
    return  parameters
