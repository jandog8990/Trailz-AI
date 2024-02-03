FROM python:3.8
EXPOSE 8080
WORKDIR /app
COPY . ./ 
COPY .env ./
#RUN python3.8 -m pip install --upgrade pip \
#&& python3.8 -m pip install -r requirements.txt 
RUN pip3 install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
