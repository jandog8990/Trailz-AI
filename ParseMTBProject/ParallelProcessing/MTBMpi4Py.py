import numpy
from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
print(f"Rank = {rank}")
print(f"Size = {size}")

a = 1
b = 10000000

num_per_rank = b // size
summ = numpy.zeros(1)

temp = 0
lower_bound = a + rank * num_per_rank
upper_bound = a + (rank+1) * num_per_rank
print(f"This is processor {rank} and I'm summing numbers from {lower_bound} to {upper_bound-1}", flush=True)

# NOTE: The barrier ensures that all processes complete before continuing
comm.Barrier()
start_time = time.time()

for i in range(lower_bound, upper_bound):
    temp = temp + i
summ[0] = temp

if rank == 0:
    total = numpy.zeros(1)
else:
    total = None

comm.Barrier()

# collect partial results and add to the total sum
comm.Reduce(summ, total, op=MPI.SUM, root=0)
stop_time = time.time()

# check the rank
if rank == 0:
    # add the numbers to 100000000
    for i in range(a + (size) * num_per_rank, b+1):
        total[0] = total[0] + i
    print("The sum of all numbers: ", int(total[0]))
    print("Time spent with ", size, " threads in ms")
    print("-----", int((time.time() - start_time) * 1000), "-----")  
