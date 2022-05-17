#FROM r-base
FROM ubuntu:20.04

RUN apt-get update && apt-get install -qy \
	apt-utils \
    gcc \
    libpython3-dev \
    git 

#RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# set time zone for mongodb
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install tzdata

RUN apt install gnupg2 -qy
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN apt-get install software-properties-common -qy
RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'
RUN apt update -qy
RUN apt-get install -qy r-base
RUN apt-get install -qy r-base-core
RUN apt-get install r-recommended


#RUN apt install software-properties-common

#RUN apt add-apt-repository ppa:c2d4u.team/c2d4u4.0+

#RUN apt-get install -qy r-base-core

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

