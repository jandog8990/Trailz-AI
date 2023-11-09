import jsonlines

# Testing the jsonlines parser for the trail url info
class JsonLineParser:
    def parse(self):
        jlFile = "imbd.jl"
        trailPattern = "https://www.mtbproject.com/trail"
        mtbUrls = []
        with jsonlines.open(jlFile) as reader:
            for obj in reader:
                if "url" in obj: 
                    url = obj["url"]
                    if trailPattern in url: 
                        mtbUrls.append(url)
 
        print(f"Len urls = {len(mtbUrls)}")
        print(f'MTB url {mtbUrls[1:10]}')
        return mtbUrls 
