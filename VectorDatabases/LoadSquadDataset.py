import pickle
from SquadDataset import SquadDataset

# load dataset and pickle
obj = SquadDataset()
dataset = obj.loadSQUAD()
with open('squad.pkl', 'wb') as f:
    pickle.dump(dataset, f)
