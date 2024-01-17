import jsonlines

# parse the jsonlines file so that we can parse trails
class MTBJsonLineParser:
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
        
