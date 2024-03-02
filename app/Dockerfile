FROM python:3.8

WORKDIR /app

# copy all local files to the image
COPY . ./ 
COPY .env ./

#RUN python3.8 -m pip install --upgrade pip \
#&& python3.8 -m pip install -r requirements.txt 

# install all python requirements using pip3
RUN pip3 install -r requirements.txt
EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

# run the actual streamlit server
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
