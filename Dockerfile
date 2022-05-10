#FROM r-base
FROM ubuntu

RUN apt-get install software-properties-common
RUN apt-get install add-apt-repository
RUN apt-get install -qy r-base

FROM python:3

#RUN apt install software-properties-common

#RUN apt add-apt-repository ppa:c2d4u.team/c2d4u4.0+

#RUN apt-get install -qy r-base-core

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]
