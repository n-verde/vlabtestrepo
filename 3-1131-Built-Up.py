# ============CALCULATE BUILT-UP AREAS FROM SENTINEL-2 IMGS=================
# Natalia Verde, AUTh, February 2019

# 3rd script for 11.3.1 indicator
# part of the SDG indicator 11.3.1 workflow for VLab Workshop in Florence, February 2019

# This script .......
# Based on: http://doi.org/10.1364/JOSAA.35.000035

# ==============IMPORTS=============================================

import os
import pathlib
from datetime import *

import rasterio as rio
import numpy as np

# =============FUNCTIONS============================================


def bua(s2img_path, exportpath):
    # calculates Built-Up Area for a Sentinel-2 image

    # open image as array
    with rio.open(str(s2img_path), 'r') as image:
        B03 = image.read(2)  # band 3 is 2nd in stack
        B04 = image.read(3)  # band 3 is 3d in stack
        B08 = image.read(7)  # band 8 is 7th in stack
        B11 = image.read(8)  # band 11 is 8th in stack
        B12 = image.read(9)  # band 12 is 9th in stack

        # get metadata for later export
        export_meta = image.profile

        # compute water index
        # http://ceeserver.cee.cornell.edu/wdp2/cee6150/Readings/Gao_1996_RSE_58_257-266_NDWI.pdf
        ndwi = (B08 - B11) / (B08 + B11)

        # compute NDVI
        ndvi = (B08 - B04) / (B08 + B04)

        # compute Normalized Built-up Area Index (NBAI)
        # https://www.omicsonline.org/scientific-reports/JGRS-SR136.pdf
        nbai = ((B12 - B11) / B03) / ((B12 + B11) / B03)

        # mask vegetation
        ndvi_masked = np.ma.masked_where((ndvi > 0), nbai, copy=True)
        # mask water
        builtup = np.ma.masked_where((ndwi > 0.5), ndvi_masked, copy=True)

        # export the built-up area image
        # change the count or number of bands from 4 to 1
        export_meta['count'] = 1
        # change the data type to float rather than integer
        export_meta['dtype'] = "float64"
        # write the built-up raster object
        with rio.open(os.path.join(exportpath, 'built-up-area.tif'), 'w', **export_meta) as eximage:
            eximage.write(builtup, 1)

# =============MAIN PROGRAM=========================================

startedTime = datetime.now(timezone.utc)

# get current working directory
cwd = pathlib.Path.cwd()

# path to read clipped, mosaic images
imgsPath = os.path.join(cwd, 'Clipped-Mos')

# path to read Past
pastPath = os.path.join(imgsPath, 'Past', 'clipped-mos.tif')
# path to read Now
nowPath = os.path.join(imgsPath, 'Now', 'clipped-mos.tif')

# path to export built-up area images
if not os.path.exists("Built-Up"):
    os.makedirs("Built-Up")
buaPath = pathlib.Path("Built-Up")

# path to export built-up Past
if not os.path.exists(os.path.join(buaPath, 'Past')):
    os.makedirs(os.path.join(buaPath, 'Past'))
expastPath = pathlib.Path(os.path.join(buaPath, 'Past'))

# path to export built-up Now
if not os.path.exists(os.path.join(buaPath, 'Now')):
    os.makedirs(os.path.join(buaPath, 'Now'))
exnowPath = pathlib.Path(os.path.join(buaPath, 'Now'))

# calculate Built-Up Areas -------------------------------
bua(pastPath, expastPath)  # Past
bua(nowPath, exnowPath)  # Now

# change detection (subtract current state from past state) -------------------------



endedTime = datetime.now(timezone.utc)

print("---------------------------------------------")
print("Built-up area calculation completed in " + str(endedTime - startedTime))
