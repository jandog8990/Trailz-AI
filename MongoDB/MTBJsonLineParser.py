import jsonlines
import re

# parse the jsonlines file so that we can parse trails
class MTBJsonLineParser:
  
    def createTrailId(self, url):
        urlArr1 = re.split("trail/", url)
        urlArr2 = urlArr1[1].split("/")
        trailId = urlArr2[-1] + "-" + urlArr2[0]
        return trailId

    def parse(self, jsonFile):
        trailPattern1 = "https://www.mtbproject.com/trail"
        trailPattern2 = "https://www.mtbproject.com/index.php/trail"
        mtbUrls = []
        with jsonlines.open(jsonFile) as reader:
            for obj in reader:
                if "url" in obj:
                    url = obj["url"]
                    if (trailPattern1 in url) or (trailPattern2 in url):
                        mtbUrls.append(url)

        print(f"Len urls = {len(mtbUrls)}")
        print(f"MTB urls = {mtbUrls[1:10]}")
        return mtbUrls
        
    def parse_trailz(self, jsonFile):
        trailPattern1 = "https://www.mtbproject.com/trail"
        trailPattern2 = "https://www.mtbproject.com/index.php/trail"
        urlMap = {} 
        with jsonlines.open(jsonFile) as reader:
            for obj in reader:
                if "url" in obj:
                    url = obj["url"]
                    if (trailPattern1 in url) or (trailPattern2 in url):
                        trailId = self.createTrailId(url)
                        urlMap[trailId] = url

        return urlMap
        
