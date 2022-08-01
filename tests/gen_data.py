#!/usr/bin/env python3
import numpy as np



count = 10000
dim = 100


arr = np.random.random((count, dim))

nearest=[]
for i in range(len(arr)):
    vec = arr[i]
    distance = np.linalg.norm(vec-arr, axis=1)
    index = np.array([k for k in range(len(arr))])
    dis_pairs = list(zip(distance, index))
    dis_pairs.sort(key=lambda x: x[0])
    nearest.append([x[1] for x in dis_pairs[1:21]])
nearest = np.array(nearest)

np.savez("data_{}_{}.npz".format(count,dim),arr=arr,nearest=nearest)


 