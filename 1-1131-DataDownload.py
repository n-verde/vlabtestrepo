# ============DOWNLOAD SENTINEL-2 L2A PRODUCTS=================
# Natalia Verde, AUTh, February 2019

# 1st script for 11.3.1 indicator
# part of the SDG indicator 11.3.1 workflow for VLab Workshop in Florence, February 2019

# This script downloads Sentinel-2 L2A images with sentinelsat package. One for the past and one for a
# recent period, for each tile. It downloads the most recent, less cloudy image found in the query.
# Username and password for sentinel-API (ESA's Sci-HUB), is required by prompt and entered during the execution
# of the script
# INPUTS:   1. S2 tile codes
#           2. Past date range for search
#           3. Current date range for search
#           4. Minimum and Maximum cloud coverage of images

# ==============IMPORTS=============================================

from collections import OrderedDict
import getpass
from datetime import *
import pathlib
import os

from sentinelsat import SentinelAPI

# =================SETTINGS=========================================

# set which S2 tiles sthe study area belongs to
# S2tiles = ['34TFL', '34TFK']  # Thessaloniki is covered by 2 tiles
S2tiles = ['34TFL']  # Thessaloniki northen tile only

# set date range for image search (code will only download one image per tile)
# PREFERABLY IN A WET SEASON MONTH FOR BETTER DISCRIMINATION BETWEEN BARE SOIL AND IMPERVIOUS!!!!
# past/initial year
dateRangePast = (date(2018, 3, 1), date(2018, 4, 1))

# current year
dateRangeNow = (date(2018, 11, 1), 'NOW')

# set cloud coverage percentage
cloudMin = 0
cloudMax = 10

# =============MAIN PROGRAM=========================================

startedTime = datetime.now(timezone.utc)

# Get Sentinel API credentials ----------------------------------
# print("Enter credentials")
# username = input("Username: ")
# password = getpass.getpass("Password: ")

username = '***'
password = '***'

# Set Download Folder ----------------------------------------------
# set the folder where your data will be downloaded (create if it doesn't exist).
# NOTE: If you are running a docker container through PyCharm, your path is in the PyCharm project directory.

if not os.path.exists("Downloads"):
    os.makedirs("Downloads")
downPath = pathlib.Path("Downloads")

api = SentinelAPI(username, password)

# download Sentinel-2 L2A products with sentinelsat package -----------------------------


def downloadS2L2A(tiles, dateRange, clMin, clMax, folder):

    # product type: S2MSI2A (Options: SLC, GRD, OCN, S2MSI1C, S2MSI2A, S2MSI2Ap)
    query_kwargs = {
            'platformname': 'Sentinel-2',
            'producttype': 'S2MSI2A',
            'cloudcoverpercentage': (clMin, clMax),
            'date': dateRange}

    for tile in tiles:
        products = OrderedDict()
        kw = query_kwargs.copy()
        kw['filename'] = '*_T{}_*'.format(tile)
        pp = api.query(**kw)
        products.update(pp)

        print("---------------------------------------------")
        print("Found", len(products), "products, for tile", tile)

        # convert to Pandas DataFrame
        products_df = api.to_dataframe(products)

        # Get basic information about the product: its title, file size, MD5 sum, date, footprint and
        # its download url
        for productID in products_df.index:
            productData = api.get_product_odata(productID)

            # if the product is less than a certain size (thus file is broken), remove from list
            if productData['size'] < 200000000:
                products_df = products_df.drop([productID])

        print("Reduced to", len(products_df), "products, for tile", tile)

        # sort and limit to the latest and least cloudy products (one for each tile)
        products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
        products_df_sorted = products_df_sorted.head(1)

        print("Start downloading image for tile", tile)
        api.download_all(products_df_sorted.index, directory_path=folder)


if not os.path.exists(os.path.join(downPath, "Past")):
    os.makedirs(os.path.join(downPath, "Past"))
pastPath = os.path.join(downPath, "Past")

downloadS2L2A(S2tiles, dateRangePast, cloudMin, cloudMax, str(pastPath))

if not os.path.exists(os.path.join(downPath, "Now")):
    os.makedirs(os.path.join(downPath, "Now"))
nowPath = os.path.join(downPath, "Now")

downloadS2L2A(S2tiles, dateRangeNow, cloudMin, cloudMax, str(nowPath))

endedTime = datetime.now(timezone.utc)

print("---------------------------------------------")
print("Data downloading completed in " + str(endedTime - startedTime))
