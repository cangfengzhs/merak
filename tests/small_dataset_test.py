import numpy as np
import unittest

from typing import Dict, List
from tqdm import tqdm
from merak.point import Point
from merak.hnsw import HNSW,HNSWConfig
from merak.point_store import MemoryPointStore,NebulaPointStore
from merak.client import Client
import time
import ipdb

point_count=1000
dim = 20

data = np.load("data_{}_{}.npz".format(point_count,dim))

client = Client("192.168.8.212",9669)

point_store = MemoryPointStore()

#point_store = NebulaPointStore(client,"random_small")
config = HNSWConfig()

hnsw = HNSW(config,point_store)


def import_data(array):
    #ipdb.set_trace()
    with tqdm(desc="Import",total=len(array)) as pbar:
        for i in range(len(array)):
            p = Point(i+1,array[i])
            hnsw.insert(p)
            pbar.update(1)
    print("Finish import data")

def search():
    pass


class TestHNSWSmallData(unittest.TestCase):
    def setUp(self) -> None:
        # cook data
        arr = data["arr"]
        self._points = {}
        self._nearest = dict()
        for i in range(len(arr)):
            id = i+1
            vec = arr[i]
            self._nearest[id] =[Point(x+1,[]) for x in data["nearest"][i].tolist()]
            p = Point(id, vec)
            self._points[id] = p


    def test_search(self):
        start_time = time.time()
        id= 1
        knns = hnsw.knn_search(self._points[id], 20+1)
        end_time = time.time()
        for p in knns:
            print(p, sep=" ")
        print()

        for p in self._nearest[id]:
            print(p, sep=" ")
        print()

        count = 0
        for p in knns:
            if p in self._nearest[id]:
                count+=1
        print("use time: {}".format(end_time-start_time))
        print("acc: {}".format(count/len(self._nearest[id])))


if __name__ == '__main__':
    import_data(data["arr"])
    unittest.main()
