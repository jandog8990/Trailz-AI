from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner
from JsonLineParser import JsonLineParser 
import re
import extruct

# clean links that contain the same url with different query params
def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link

# crawler that loops through current html page, extracts urls
# then passes this to a function for parsing html page contents
class ImbdCrawler(CrawlSpider):
    name = 'imbd'
    #allowed_domains = ['www.imbd.com']
    #start_urls = ['https://www.imbd.com']
    allowed_domains = ['www.mtbproject.com']
    start_urls = ['https://www.mtbproject.com/directory/8009314/albuquerque'] 
    trail_urls = [] 
    #start_urls = ['https://www.mtbproject.com/trail/720764/manzano-monster-loop']

    # initialize method to open the current jsonlines file and find all 
    # crawled urls from previous run sessions
    def __init__(self, name=None, **kwargs):
        super(ImbdCrawler, self).__init__()
        print("---- THIS IS THE INIT METHOD ----")
        print(" -> we'll parse old data here")
        parser = JsonLineParser()
        self.trail_urls = parser.parse() 
        print("---- TRAIL URLS PARSED! ----\n") 
    
    # eliminate scraped urls that don't match imbd
    rules = (
        Rule(
            process_links=process_links,
            callback='parse_item',
            follow=True # allows following of links from each response
        ),
    )
   
    def parse_item(self, response):
        # before parsing the item let's ensure it's 
        if response.url not in self.trail_urls: 
            return {
                'url': response.url,
                'metadata': extruct.extract(
                    response.text,
                    response.url,
                    syntaxes=['opengraph', 'json-ld']
                ),
            }
