# Example of Pool map_async with callback and without
from random import random
import time 
from multiprocessing.pool import Pool
import os

# callback func
final_result = []
def custom_callback(result):
    print(f"Callback got final results: {result}")

# exected func
def task(id):
    value = random()
    print(f"Task {id} executing with {value}", flush=True)
    return value

if __name__ == '__main__':
    # create and configure process pool
    cpu_count = os.cpu_count()
    N = 200 
    CHUNK_LEN = 10
   
    # run the processing pool map_async method
    st = time.time() 
    pool = Pool(processes=cpu_count)
    result = pool.map_async(task, range(N), chunksize=CHUNK_LEN) 
    res = result.get() 
    et = time.time() 
    dur = et-st 
    pool.close()
    pool.join()
    
    # see the results
    print(f"Total time = {dur} sec")
    print("Final result:")
    print(res)
    print("\n")
