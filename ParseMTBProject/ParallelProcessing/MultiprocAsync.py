import multiprocessing
from datetime import datetime
from multiprocessing import Pool
import time
import os

# get the cpu count
cpu_count = os.cpu_count()
print(f"cpu_count = {cpu_count}") 

# Syntax
# map_async(func, iterable[, chunksize[, callback[, error_callback]]])
"""
1. func: specifies func to be executed
2. iterable: data to be chunked or divided
3. chunksize: number of iterables given to each proc
4. callback: function to execute the batched args
5. error_callback: function returned with error
"""
lst = [(2, 2),  (4, 4), (5, 5),(6,6),(3, 3)]
result = []

def collect_result(val):
    return result.append(val)

"""
Multiply the two elems in the tuple
"""
def mul(x):
    print(f"start process: {x}")
    time.sleep(3)
    print(f"end process: {x}")
    res = x[0] * x[1]
    #res_ap = (x[0], x[1], res)
    #return res_ap
    return res

"""
Test the map_async() function for parallelization
"""
def test_map_async():
    pool = Pool(processes=cpu_count)
    result_f = pool.map_async(mul, lst, chunksize=2, callback=collect_result)
    pool.close()
    print(result_f.get(timeout=10))

if __name__ == '__main__':
    start = datetime.now()
    test_map_async()
    print("End time map_async: ", (datetime.now() - start).total_seconds())
