# Trailz AI App 
MTB Trail Recommendation app that uses HuggingFace and PineCone
VectorDB to embed text descriptions of trail data and upload
to a backend PineCone DB that allows NLP searching. 

### Steps for Running Search ###

1. First we run the mtb-project-crawler to crawl and scrape mtb data 
    * Run the crawler using: 
        $scrapy crawl mtbproject --logfile mtbproject.log -o mtbproject.jl:jsonlines
2. Run the MTBTrailController to store data to a mongo db 
3. Run PineConeDatasetUpload that takes text data, embeds and uploads to PineCone 
4. Run PineConeSearch that searches for trails using NLP 
5. MapBox API for showing the trail route data 
