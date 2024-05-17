from MTBLoadDataset import MTBLoadDataset 
import pandas as pd
from datasets import Dataset
from pinecone import Pinecone

loadData = MTBLoadDataset()
fullset = loadData.load_full_dataset()
#metaset = loadData.load_dataset()

"""
# subset of the filtered dataset
print(f"Len metaset = {len(metaset)}")
keys = list(metaset.keys())
testkey = keys[19]
testval = metaset[testkey]
testval_keys = list(testval.keys())
print(f"Test key = {testkey}")
print(testval)
print("\n")
print(testval_keys) 
"""

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# get the full dataset entry
print(f"Len full metaset = {len(fullset)}")
df_pandas = fullset.to_pandas()
print(df_pandas.head())

print("Full set test:")
print(fullset[0])
print("\n")

# create a test obj
data = fullset.map(lambda x: {
    "id": x["_id"],
    "text": x["mainText"],
    "source": x["trail_url"],
    "metadata": x["metadata"]
})
print("New data:")
print(data[0])
print("\n")

# delete uneeded cols
data = data.remove_columns([
    "_id", "vector", "trail_url",
    "driving_directions", "gpx_file",
    "mainText"])
print(f"Data len = {len(data)}")

# check for dups
df = pd.DataFrame(data)
ids = df["id"]
dups = ids.duplicated()
print("DF Test:")
print(f"ids len = {len(ids)}")
print(dups)
print("\n")

# find the dups using ids and dups
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
dup_ids = ids.isin(ids[ids.duplicated()])
dup_vals = df[dup_ids].sort_values("id")
df_cols = dup_vals[['id', 'source', 'metadata']]
first_df = df_cols.iloc[0]
print("Dup First DF:")
print(first_df['id'])
print(first_df['metadata'])
print("\n")

#df.drop_duplicates()
#df.drop_duplicates(subset=['id'])
#ds = Dataset.from_pandas(df)
#print(f"New data len = {len(ds)}")
#print("\n")

# create jsonlines to upsert to canopy
#ds.to_json("canopy_routes.jsonl", orient="records", lines=True)
