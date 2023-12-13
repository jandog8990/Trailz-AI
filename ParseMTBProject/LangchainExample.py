from langchain.document_loaders import UnstructuredURLLoader

#"https://www.understandingwar.org/backgrounder/russian-offensive-campaign-assessment-february-8-2023",
#"https://www.understandingwar.org/backgrounder/russian-offensive-campaign-assessment-february-9-2023",
urls = [
    "https://www.mtbproject.com/trail/285392/tunnel-otero-west-figure-8"
]

loader = UnstructuredURLLoader(urls=urls)
data = loader.load()
print(f"Data len = {len(data)}")
print(data)
print("\n")
