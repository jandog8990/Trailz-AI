import pickle

with open('mtb_routes.pkl', 'rb') as f:
    mtb_routes = pickle.load(f)
with open('mtb_descs.pkl', 'rb') as f:
    mtb_descs = pickle.load(f)
print("MTB routes 0:")
print(mtb_routes[100])
print("\n")

print("MTB descs 0:")
print(mtb_descs[100])
print("\n")
