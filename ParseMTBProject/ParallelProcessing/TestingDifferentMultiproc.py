import multiprocessing
from datetime import datetime
from multiprocessing import Pool
from joblib import Parallel, delayed
import time
import os

def square(x):
    #print(f"Square {x}") 
    return x**2

def proc_square(batch):
    """ 
    print(f"Batch len = {len(batch)}") 
    print(f"Batch first elem = {batch[0]}")
    print(f"Batch last elem = {batch[len(batch)-1]}")
    print("\n")
    """ 
    arr = [square(row) for row in batch]
    print("Process Square:")
    print(arr) 
    print("\n")
    return arr

multiproc_result = []
def collect_result(val):
    return multiproc_result.append(val)

# get the CPU count and other vars
cpu_count = os.cpu_count()
#N_LEN = 1000000
#N_LEN = 20000 
N_LEN = 10
numbers = [*range(N_LEN)]

#if __name__ == '__main__':
st = time.time()

# ------------------------
# Chunk Parallel Test 1 
# ------------------------
chunks = []
#N_CHUNK = 1000
N_CHUNK = 2
st = time.time()
for i in range(1, N_LEN, N_CHUNK):
    chunks.append(numbers[i:min(i+N_CHUNK, N_LEN)])

res = Parallel(n_jobs=-1)(delayed(proc_square)(batch) for batch in chunks) 
et = time.time()
elapsed3 = et - st
print('Execution time (Batching): ', elapsed3, ' sec')
print("Response:")
print(res)
print("\n")

"""
# ------------------------
# Parallelization Test 1 
# ------------------------
result = Parallel(n_jobs=-1)(delayed(square)(num) for num in numbers)

et = time.time()
elapsed1 = et - st
print('Execution time (Parallel 1): ', elapsed1, ' sec')
#print(result)

# ------------------------
# Sequential Loop Test 1 
# ------------------------
st = time.time()
result2 = [square(num) for num in numbers]
et = time.time()
elapsed2 = et - st
print('Execution time (Sequential 1): ', elapsed2, ' sec')
"""

# --------------------------
# multiprocessing pool test
# --------------------------
pool = Pool(processes=cpu_count)
st = time.time()
result_pool = pool.map_async(square, numbers, chunksize=N_CHUNK, callback=collect_result)
pool.close()
res = result_pool.get(timeout=10)
et = time.time()
elapsed4 = et - st
print('Execution time (Pooling): ', elapsed4, ' sec')
print(res)
print("\n")
