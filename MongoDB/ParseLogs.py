import re
import json
from MTBTrailMongoDB import MTBTrailMongoDB

with open('old_trailz.log', 'r') as f:
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
    print(f"{type(errMap[0])}") 
    errList = errMap[0]
    err1 = errList[0]
    keyValue = err1['keyValue']
    print(keyValue['_id'])
    print("\n")
   
    # extract all ids from the err list
    idList = [] 
    for err in errList:
        keyVal = err['keyValue']
        idList.append(keyVal['_id'])
    print(f"Id list len = {len(idList)}")
    print("\n")
    #print(errMap[len(errMap)-1])
  
    # query the mongoDB to make sure we have all the ids listed
    trailMongoDB = MTBTrailMongoDB() 
    (trailRoutes, trailDescs) = trailMongoDB.find_mtb_trail_data_by_ids(idList) 
