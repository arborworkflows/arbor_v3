

#FROM r-base
FROM ubuntu:20.04

RUN apt-get update

# set time zone for mongodb
RUN echo 'building Arbor v3'
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install tzdata
#RUN dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get update && apt-get install -qy \
	apt-utils \
    gcc \
    libpython3-dev \
    libxml2-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libfontconfig1-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    libgsl-dev \
    git 

#RUN apt-get clean && rm -rf /var/lib/apt/lists/*



RUN apt install gnupg2 -qy
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN apt-get -qy install software-properties-common 
RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'
RUN apt update -qy
RUN apt-get install -qy r-base
RUN apt-get install -qy r-base-core
RUN apt-get install -qy r-recommended

RUN /usr/bin/Rscript --slave --no-save --no-restore-history -e 'install.packages("ape")'
RUN /usr/bin/Rscript --slave --no-save --no-restore-history -e 'install.packages("phytools")'
RUN /usr/bin/Rscript --slave --no-save --no-restore-history -e 'install.packages("geiger")'
RUN /usr/bin/Rscript --slave --no-save --no-restore-history -e 'install.packages("diversitree")'
RUN /usr/bin/Rscript --slave --no-save --no-restore-history -e 'install.packages("devtools")'
RUN /usr/bin/Rscript --slave --no-save --no-restore-history -e 'devtools::install_github("arborworkflows/aRbor")'
#RUN apt install software-properties-common

#RUN apt add-apt-repository ppa:c2d4u.team/c2d4u4.0+

#RUN apt-get install -qy r-base-core

WORKDIR /usr/src/app

# get pip3 for installations
RUN apt-get install -qy wget 
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN apt-get install -qy python3 
RUN apt-get install -qy python3-distutils
RUN python3 get-pip.py

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# run the webserver app
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]
#CMD uvicorn main:app --host 0.0.0.0 --port 80

# keep the container running, if needed for debug
#ENTRYPOINT ["tail", "-f","/dev/null"]