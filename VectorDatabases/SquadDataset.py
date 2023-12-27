from datasets import Dataset, load_dataset
from sentence_transformers import SentenceTransformer
import pandas as pd

# class for loading the SquadDataset
class SquadDataset:
    # method for creating the squad dataset
    def loadSQUAD(self):

        # let's load the SQuAD dataset
        dataset = load_dataset('squad', split='train')
        dataset = dataset.select(list(range(3500)))

        # convert ds to df and drop dups on 'context'
        pd.set_option('display.max_columns', None) 
        df = pd.DataFrame(dataset)
        newdf = df.drop_duplicates(subset=['context'], keep='last')
        new_dataset = Dataset.from_pandas(newdf)

        # PineCone - needs three items:
        # 1. 'id', 'vector', 'metadata'
        # 2. build the embeddings from the 'context'
        # 3. multi-vector embedding model (switch btwn Italian/English)

        # let's use the HuggingFace multilingual library for sentence
        # transformation using multiple langs
        # https://huggingface.co/sentence-transformers/stsb-xlm-r-multilingual
        #"Early engineering courses provided by American Universities in the 1870s."
        model = SentenceTransformer('stsb-xlm-r-multilingual')

        # create the dataset using mappings
        new_dataset = new_dataset.map(
            lambda x: {
                'vector': model.encode(x['context']).tolist()
            }, batched=True, batch_size=16)

        # Create a mapping here to create a metadata field
        lang = "en"
        new_dataset = new_dataset.map(
            lambda x: {
                'metadata': {
                    'lang': lang,
                    'title': x["title"]
                }
            })
        return new_dataset
