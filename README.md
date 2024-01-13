# Trailz AI App 
MTB Trail Recommendation app that uses HuggingFace and PineCone
VectorDB to embed text descriptions of trail data and upload
to a backend PineCone DB that allows NLP searching. 

###Steps

#1. First we run the mtb-project-crawler to crawl and scrape mtb data 
#2. Run the MTBTrailController to store data to a mongo db 
#3. Run PineConeDatasetUpload that takes text data, embeds and uploads to PineCone 
#3. Run PineConeSearch that searches for trails using NLP 
#4. MapBox API for showing the trail route data 
