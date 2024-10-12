FROM python:3.12.4

WORKDIR /app

# copy all local files to the image
COPY . /app 

#RUN python3.8 -m pip install --upgrade pip \
#&& python3.8 -m pip install -r requirements.txt 

# install all python requirements using pip3
RUN pip3 install --no-cache-dir -r requirements.txt

# run command for loading/caching embed model
#RUN python -c 'from sentence_transformers import SentenceTransformer; SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2", cache_folder="./.model")'

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

# run the actual streamlit server
ENTRYPOINT ["streamlit", "run", "--client.showSidebarNavigation=False", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
