import pickle
import re

# MTBLoadDataset - Class that loads data from route pkl dataset
class MTBLoadDataset: 
    # dataset map updating the _id 
    def update_id(self, objId): 
        newId = re.sub(r'[^a-zA-Z0-9\s]+', '', objId)
        newId = re.sub(' +', ' ', newId)
        newId = newId.replace(u'\xa0', u' ') 
        return newId

    # create ids from the pinecone results
    def create_ids(self, results):
        ids = [obj['id'] for obj in results['matches']]
        print(f"Ids len = {len(ids)}")
        print(ids)
        print("\n")
        return ids

    # get samples from the main dataset
    def create_metadata_set(self, dataset):
        return {
            data['_id']: {
                'mainText': data['mainText'],
                'metadata': data['metadata']
            } for data in dataset}
    
    # show results from query
    def get_final_results(self, results, metadata_set):
        ids = self.create_ids(results)
        final_results = {} 
        for i in ids:
            final_results[i] = metadata_set[i]
        return final_results
    
    # show results from query
    def show_results(self, results, metadata_set):
        ids = self.create_ids(results)
         
        for i in ids:
            print(f"Metadata Set[{i}]:")
            print(f"id = {i}") 
            print(metadata_set[i])
            print("\n")

    # load the pinecone dataset
    def load_dataset(self): 
        # open the dataset from pkl to get results
        with open('./pkl_data/mtb_route_dataset.pkl', 'rb') as f:
            dataset = pickle.load(f)

        # update the dataset ids
        print(type(dataset)) 
        new_dataset = dataset.map(
            lambda x: {
                '_id': self.update_id(x['_id'])
            })

        return self.create_metadata_set(new_dataset)

    # Canopy - load the full dataset with all fields present (ie trail url and gpx shit)
    def load_full_dataset(self):
        # open the dataset from pkl to get results
        with open('./pkl_data/mtb_route_dataset.pkl', 'rb') as f:
            dataset = pickle.load(f)

        # update the dataset ids
        new_dataset = dataset.map(
            lambda x: {
                '_id': self.update_id(x['_id'])
            })

        return new_dataset 
        
