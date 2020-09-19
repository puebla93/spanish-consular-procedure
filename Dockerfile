FROM python:3.8
LABEL Javier Puebla "jpuebla1993@gmail.com"

# Setting these enviroment variable to ensure that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# Creating root directory for our project in the container
RUN mkdir /cons_esp_habana

# Setting the working directory to /cons_esp_habana
WORKDIR /cons_esp_habana

# Copy the current directory contents into the container at /cons_esp_habana
ADD . /cons_esp_habana/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
