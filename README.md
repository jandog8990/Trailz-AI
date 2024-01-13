# Trailz AI App 
MTB Trail Recommendation app that uses HuggingFace and PineCone
VectorDB to embed text descriptions of trail data and upload
to a backend PineCone DB that allows NLP searching. 

### Steps for Running Search ###

1. First we run the mtb-project-crawler project to crawl and scrape mtb data and store in a jsonline file for storing trail/ urls. 
    * Run the crawler using: 
        $scrapy crawl mtbproject --logfile mtbproject.log -o mtbproject.jl:jsonlines
2. Run MTBTrailController.py to store data to a MongoDB 
    1. Uses a pool processor to split urls and process them in chunks
    2. Calls MTBTrailUrlParser.py & MTBTrailParser.py for creating Routes and Descriptions
    3. Calls MTBTrailMongoDB.py to load the route/description tuples to Atlas
3. Run PineConeDatasetUpload.py that takes text data, embeds and uploads to PineCone
    * Uses PineCone upsert to upload batches of vector data to PineCone 
4. Run PineConeSearch.py that searches for trails using NLP
    * Uses an embedded query search for natural text search
    * Uses conditional filter for searching based on metadata
5. MapBox API for showing the trail route data 
