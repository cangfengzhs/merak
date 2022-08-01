#!/usr/bin/env python3

import numpy as np
from transformers import RetriBertConfig
from merak.client import Client
from merak.point import Point
from typing import List, Dict
from collections import defaultdict
import pprint
import json
from abc import ABC, abstractmethod


class PointStore(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_point(self, id: int, get_neighbors=False) -> Point:
        pass

    @abstractmethod
    def save_point(self, point: Point):
        pass


class MemoryPointStore(PointStore):
    def __init__(self) -> None:
        super().__init__()
        self.points: Dict[int, Point] = dict()
        self.points[0] = Point(0, None)

    def get_point(self, id: int, get_neighbors=False) -> Point:
        return self.points[id]

    def save_point(self, point: Point):
        self.points[point.id] = point
        for layer, neighbors in point.neighbors.items():
            for n in neighbors:
                self.points[n].neighbors[layer].append(point.id)


class NebulaPointStore(PointStore):
    def __init__(self, client: Client, space: str) -> None:
        super().__init__()
        self.client_ = client
        self.space = space
        result = self.client_.execute("use {}".format(space))

    def __encode_vector(self, vector: np.ndarray) -> str:
        return json.dumps(vector.tolist())

    def __decode_vector(self, string: str) -> np.ndarray:
        return np.array(json.loads(string))

    def save_point(self, point: Point) -> bool:
        # insert vertex
        vector_string = self.__encode_vector(point.vector)
        ngql = "USE {} ;INSERT VERTEX point(vector) VALUES {}:(\"{}\")".format(self.space,
                                                                                     point.id, vector_string)
        result = self.client_.execute(ngql)

        assert result.is_succeeded()

        # insert edges
        ngql = "USE {} ;INSERT EDGE e() VALUES ".format(self.space)
        edges = []
        for layer, neighbors in point.neighbors.items():
            for n in neighbors:
                edges.append("{}->{}@{}:()".format(point.id, n, layer))
        ngql += ",".join(edges)
        result = self.client_.execute(ngql)
        assert result.is_succeeded()

    def get_point(self, id: int, get_neighbors=False) -> Point:
        point: Point = Point(id, None)
        # get vertex
        ngql = "USE {} ;FETCH PROP ON point {} YIELD properties(vertex).vector".format(self.space,
                                                                                             id)
        result = self.client_.execute(ngql)
        if not result.is_succeeded():

            raise RuntimeError("Fetch vector of {} failed".format(id))

        vec = result.row_values(0)[0].as_string()
        if len(vec) == 0:
            point.vector = None
        else:
            point.vector = self.__decode_vector(vec)

        # get neighbors
        if not get_neighbors:
            return point

        neighbors = defaultdict(set)

        ngql = "USE {} ;GO FROM {} OVER e YIELD rank(edge) as layer,dst(edge) as dst".format(self.space,
                                                                                                   id)
        result = self.client_.execute(ngql)

        if not result.is_succeeded():
            raise RuntimeError("Get neighbors failed")

        for i in range(result.row_size()):
            rank = result.row_values(i)[0].as_int()
            dst = result.row_values(i)[1].as_int()
            neighbors[rank].add(dst)

        ngql = "USE {} ;GO FROM {} OVER e REVERSELY YIELD rank(edge) as layer,src(edge) as dst".format(self.space,
                                                                                                             id)
        result = self.client_.execute(ngql)

        if not result.is_succeeded():
            raise RuntimeError("Get neighbors failed")

        for i in range(result.row_size()):
            rank = result.row_values(i)[0].as_int()
            dst = result.row_values(i)[1].as_int()
            neighbors[rank].add(dst)

        point.neighbors = neighbors

        return point
