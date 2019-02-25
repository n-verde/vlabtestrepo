# Natalia Verde, AUTh, Feb 2019

# First must run in a terminal "docker pull thinkwhere/gdal-python" to get the base image

FROM thinkwhere/gdal-python

LABEL maintainer="nverde@topo.auth.gr"

#WORKDIR /root

# Update
RUN pip install --upgrade pip

# Install app dependencies

RUN apt-get update && apt-get install -y \
    unzip

RUN pip install sentinelsat==0.12.2 \
				pathlib==1.0.1 \
				pandas==0.24.1 \
				matplotlib==3.0.2 \
				Pillow==5.4.1 \
				Glymur==0.8.16 \
				satpy==0.12.0 \
				pyorbital==1.5.0 \
				rasterio==1.0.18
				
# To save your container as a docker image, open a new terminal and type:
# docker commit 11.3.1 nverde/11.3.1

# run python3 (in order to set docker image as python interpreter in PyCharm
#CMD ["python3"]

# works!