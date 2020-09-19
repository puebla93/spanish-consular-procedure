FROM python:3.8
LABEL Javier Puebla "jpuebla1993@gmail.com"

# Install tesseract
RUN apt-get update -y
RUN apt-get install -y tesseract-ocr

# Install imagemagick
RUN apt-get install -y imagemagick

# Setting these enviroment variable to ensure that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# Creating root directory for our project in the container
RUN mkdir /spanish_consular_procedure

# Setting the working directory to /spanish_consular_procedure
WORKDIR /spanish_consular_procedure

# Copy the current directory contents into the container at /spanish_consular_procedure
ADD . /spanish_consular_procedure/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
