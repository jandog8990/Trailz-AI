from multiprocessing import Pool
import time
import math

N = 5000000 

def cube(x):
    return math.sqrt(x)

if __name__ == "__main__":
    st = time.time() 
    with Pool() as pool:
        result = pool.map(cube, range(10, N))
    et = time.time() 
    dur = et - st
    print(f"Total time = {dur} sec")
    print("Program done.")
    print(result)
