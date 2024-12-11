### Steps for running the app locally
$ streamlit run app.py
$ streamlit run --client.showSidebarNavigation=False app.py --server.port 8080

### Docker image and container install

1. First create requirements.txt - contains all python requirements
2. Create the streamlit main app.py for running webapp
3. Expose your port using `EXPOSE 8080`
4. Create entry point that runs the streamlit app

### Build Docker image

1. docker build -t trailzai .
2. docker run --env-file ./env.list -p 8080:8080 trailzai 
3. docker build -t trailzai --build-arg GUARDRAILS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMTUxMTI2ODc1MTEwOTMxNDUxNCIsImFwaUtleUlkIjoiZWJkMDg4OGEtY2RjYS00ZTJhLTgxYzItODljNzkzZjRiNjc3IiwiaWF0IjoxNzI4NTMxODg2LCJleHAiOjE3MzYzMDc4ODZ9.MghnOti4s8EtRByVxeAwv_oHY6qoEP4h2awg08s7Q5o .

### General Gcloud commands

1. gcloud auth list
2. gcloud config set account jandog8990
3. gcloud projects list
4. gcloud config set project trailz-finder

### Docker deployment commands

1. First list the configurations for the current project
$ gcloud config list

2. Set the project in google cloud
$ gcloud projects list
$ gcloud config set project trailz-finder

3.  List/set the gcloud configurations for project
$ gcloud config configurations list
$ gcloud config configurations describe trailz-finder
$ gcloud config configurations activate trailz-finder

4.  Create the remote repository in the "Artifact Repository"
$ gcloud artifacts repositories list
$ gcloud artifacts repositories create trailz-docker-repo --repository-format=docker --location=us-central1 --description="Trailz finder Docker repo"
$ gcloud config get-value trailz-finder

5. Deploy the Docker app to the Cloud Run repo
    * Without a docker config file use this: 
    $ gcloud builds submit --region=us-central1 --tag us-central1-docker.pkg.dev/trailz-finder/trailz-docker-repo/trailz-image:tag1
    * With a cloudbuild.yaml containing docker config and build use this:
    $ gcloud builds submit --region=us-west2 --config cloudbuild.yaml

6. Check the installation in the Artifact Registry
https://console.cloud.google.com/artifacts?referrer=search&hl=en&project=trailz-finder

### Mapping Custom Domains in Cloud Run

1. Cloud Run location: https://console.cloud.google.com/run?project=trailz-finder 
2. Click Manage Custom Domains (top right) -> Add Mapping
3. Select the created Docker service (trailz-finder)
4. Select the Cloud Run Domain Mappings section -> Follow url and directions
5. Open SiteGround.com -> selection trailzai.com -> open DNS settings
6. Add the DNS settings given in the Cloud Run Domain Mappings
7. Let the DN records propagate, check the trailzai.com site 

