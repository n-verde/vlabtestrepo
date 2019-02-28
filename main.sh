#!/usr/bin/env bash

unzip aoi.zip

python 1-1131-DataDownload.py

ls -l

python 2-1131-PreProcessing.py

ls -l

python 3-1131-Built-Up.py
