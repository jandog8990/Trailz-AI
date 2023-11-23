import jsonlines

# parse the jsonlines file to get previously visited urls
class JsonLineParser:
    def parse(self, jlFile):
        trailPattern = "https://www.mtbproject.com/trail"
        mtbUrls = []
        with jsonlines.open(jlFile) as reader:
            for obj in reader:
                if "url" in obj:
                    url = obj["url"]
                    if trailPattern in url:
                        mtbUrls.append(url)

        print(f"Len urls = {len(mtbUrls)}")
        print(f"MTB urls = {mtbUrls[1:10]}")
        return mtbUrls
