# Trailz AI App 
MTB Trail Recommendation app that uses HuggingFace and PineCone
VectorDB to embed text descriptions of trail data and upload
to a backend PineCone DB that allows NLP searching. 

### Steps for Running Search ###

1. For basic search we can run PineConeSearch.py
    * Update PineConeSearch with your trail criteria 
    * $ python PineConeSearch.py

### Steps for generating/parsing data, uploading to MongoDB and PineConeDB

1. First we run the mtb-project-crawler project to crawl and scrape mtb data and store in a jsonline file for storing trail/ urls. 
   
### MTB Crawler and Data Scraper
    * cd MTBCrawlerScraper/
    * Run the crawler using: 
        $scrapy crawl mtbproject --logfile mtbproject.log -o mtbproject.jl:jsonlines
2. Run MTBTrailController.py to store data to a MongoDB 
    1. Uses a pool processor to split urls and process them in chunks
    2. Calls MTBTrailUrlParser.py & MTBTrailParser.py for creating Routes and Descriptions
    3. Calls MTBTrailMongoDB.py to load the route/description tuples to Atlas
3. Need to create the pkl data from the MongoDB to be used by PineCone
    * Run the MTBTrailPickleCreator.py which creates route and desc pkl files

### PineCone Vector DB Upload
    * cd PineCone/
4. Run PineConeEmbeddingCreator.py to create the data to insert to PineCone VectorDB
    * Creates new mtb_route_dataset.pkl pkl file with updated data 
5. Run PineConeCreateServerless.py to create the serverless index if it DNE 
6. Run PineConeDatasetUpload.py that takes text data, embeds and uploads to PineCone
    * Reads the mtb_route_dataset.pkl pkl file in app/pkl_data
    * Uses PineCone upsert to upload batches of vector data to PineCone 
7. Run PineConeSearch.py that searches for trails using NLP
    * Uses an embedded query search for natural text search
    * Uses conditional filter for searching based on metadata

### TODO: Mapping for each trail route
7. MapBox API for showing the trail route data 

### Class Diagram

1. PineConeSearchLoader.py - contains pine cone connections
2. MTBLoadDataset.py - load the dataset for the mtb data

### Steps for Deploying Docker to Google Cloud

1. See the app/README.md file for all GCloud commands
2. Follow all suceeding directions on setting up and mapping domains

