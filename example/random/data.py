#!/usr/bin/env python3

import numpy as np
from multiprocessing import Process
import sys

def generate_small(path):
    point_count = 10000
    dim = 100
    vec = np.random.random((point_count, dim)).astype(np.float16)
    id_list = np.array([i+1 for i in range(point_count)], dtype=np.int32)
    np.savez_compressed("{}/part0.npz".format(path), id=id_list, vector=vec)


def generate_middle(path):
    point_count = 1000000
    dim = 500
    part_count = 10
    assert(point_count % part_count == 0)
    id = 0
    for part in range(part_count):
        vec = np.random.random(
            (point_count/part_count, dim)).astype(np.float16)
        id_list = np.array(
            [id+i+1 for i in range(point_count/part_count)], dtype=np.int32)
        id += point_count/part_count
        np.savez_compressed("{}/part{}.npz".format(path,
                            part), id=id_list, vector=vec)


def generate_large(path):
    point_count = 100000000
    dim = 1000

    def worker(parts, part_size):
        for part in parts:
            vec = np.random.random((part_size, dim)).astype(np.float16)
            id_list = [part*part_size+i+1 for i in range(part_size)]
            id_list = np.array(id_list, dtype=np.int32)
            np.savez_compressed(
                "{}/part{}.npz".format(path, part), id=id_list, vector=vec)
    part_count = 1000
    assert(point_count % part_count == 0)
    worker_count = 40
    assert(part_count % worker_count == 0)
    part = 1
    worker_list = []
    for i in range(worker_count):
        p = Process(target=worker, args=(
            [x for x in range(part, part+part_count/worker_count)],))
        part += part_count/worker_count
        p.start()
        worker_list.append(p)
    for p in worker_list:
        p.join()


if __name__ == "__main__":
    if sys.argv[1] == "small":
        generate_small(sys.argv[2])
    elif sys.argv[1] == "middle":
        generate_middle(sys.argv[2])
    elif sys.argv[1] == "large":
        generate_large(sys.argv[2])
    else:
        exit(-1)
