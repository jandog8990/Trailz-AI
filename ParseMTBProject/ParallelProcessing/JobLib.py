from math import sqrt
from joblib import Parallel, delayed
from math import ceil
from tqdm import tqdm

# parallel jobs for sqrt
x = Parallel(n_jobs=2)(delayed(sqrt)(i ** 2) for i in range(10))
print(x)

# approximating pi using batch processing
def batch_process_function(row):
    k, pi = 1, 0
    for i in range(10**6):
        if i % 2 == 0:
            pi += 4 / k
        else:
            pi -= 4 / k
        k += 2
    return pi

# settings for the items
N = 1000 
items = range(N)
print("Items:")
print(items)
print("\n")

# Let's split the job into batches
N_WORKERS = 3 

# create the batch function
def proc_batch(batch):
    return [
        batch_process_function(row)
        for row in batch
    ]

# divide data into batches
batch_size = ceil(len(items) / N_WORKERS)
print(f"Batch size = {batch_size}")

# create the batches of data to send (this is a list of ranges)
batches = [
    items[ix:ix+batch_size]
    for ix in range(0, len(items), batch_size) 
]
print(f"Batches len = {len(batches)}")
print(batches)
print("\n")

#list_from_parallel = Parallel(n_jobs=2)(delayed(sqrt)(i ** 2) for i in range(1000000))

# tqdm - sliding bar for progess
# divide the work using parallel and batches list of ranges
result = Parallel(n_jobs=N_WORKERS)(delayed(proc_batch)(batch) for batch in batches)
print("RESULT:")
print(result)
print("\n")
