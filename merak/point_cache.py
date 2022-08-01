#!/usr/bin/env python3
import threading

from merak.graph import Node
from collections import OrderedDict
import rwlock


class NodeCache:
    def __init__(self, capacity=2048):
        self.capacity = capacity
        self.cache: OrderedDict[int, Node] = {}
        self.lock = rwlock.RWLock()

    def put(self, key: int, value: Node):
        self.lock.writer_lock.acquire()
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=True)
        self.cache[key] = value
        self.lock.writer_lock.release()

    def get(self, index) -> Node:
        self.lock.reader_lock.acquire()
        if index in self.cache:
            self.cache.move_to_end(index, last=False)
            self.lock.reader_lock.release()
            return self.cache.get(index)
        self.lock.reader_lock.release()
        return None
