import re
import json

with open('mtbtrailz.log', 'r') as f:
    regex = 'ERROR:root:'
    errMap = {} 
    count = 0 
    for line in f:
        if regex in line: 
            err_str = line.strip() 
            err = err_str.split(regex)[1]
            data = eval(err) 
            errMap[count] = data 
            count+=1 
   
    print(f"Err total len = {len(errMap)}")
    print(f"First elem len = {len(errMap[0])}")
    print("\n")
    #print(errMap[len(errMap)-1])
