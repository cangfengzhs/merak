#!/usr/bin/env python3
# 生成 n 个 m 维向量
# Example:
# random_embedding.py 1000000 500 rand.npy

import numpy as np
import sys

n = int(sys.argv[1])
m = int(sys.argv[2])
file = sys.argv[3]
arr = np.random.random((n,m))
np.save(file,arr)





