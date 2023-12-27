from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner
import re
import extruct
from sys import path

PATH='/home/jandogonzales/Development/Machine Learning/MTB-Trailz/mtb-project-crawler/crawler/spiders' 
path.append(PATH)
from JsonLineParser import JsonLineParser 

# clean the links that contain the same url with different query params
def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link

# crawler that loops through current html page, extracts urls
# then passes this to a function for parsing html page contents
class MtbProjectCrawler(CrawlSpider):
    name = 'mtbproject'
    allowed_domains = ['www.mtbproject.com']
    start_urls = ['https://www.mtbproject.com/directory/8009314/albuquerque']
    trail_urls = []
    jlFile = PATH + "/mtbproject.jl"

    # initialize method to open current jsonlines file and find
    # previously crawled urls, that way we don't save twice
    def __init__(self, name=None, **kwargs):
        super(MtbProjectCrawler, self).__init__()
        print("Check the list of parsed urls...")
        # import the JsonLineParser and parse the input jl file 
        parser = JsonLineParser()
        self.trails_urls = parser.parse(self.jlFile)
        print("----- json lines file parsed -----\n")

    # eliminate scraped urls that don't match mtbproject
    rules = (
        Rule(
            process_links=process_links,
            callback="parse_item",
            follow=True # allows the following of links from each response
        ),
    )

    def parse_item(self, response):
        # extract contents from the trail url
        if response.url not in self.trail_urls:
            return {
                "url": response.url,
                "metadata": extruct.extract(
                    response.text,
                    response.url,
                    syntaxes=['opengraph', 'json-ld']
                )
            }
