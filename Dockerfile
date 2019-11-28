FROM python:3.5 
ENV PYTHONBUFFERED 1
RUN mkdir /mysite  
WORKDIR /mysite   
COPY requirements.txt . 
ADD . /mysite/ 
RUN pip3 install -r requirements.txt 
