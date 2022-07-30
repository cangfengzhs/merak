from typing import Dict, List, Tuple
from time import sleep
import numpy as np

from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config


class InsertBatch:
    def __init__(self):
        self._queries: List[str] = []

    def insert_vertex(self, vid: int, vecStr: str):
        query = f"INSERT VERTEX t1(col1) VALUES '{vid}': ('{vecStr}')"
        self._queries.append(query)

    def insert_edge(self, src: int, level: int, dst: int):
        query = f"INSERT EDGE e1() VALUES '{src}' -> '{dst}' @{level}: ()"
        self._queries.append(query)

    def __str__(self) -> str:
        return ';'.join(self._queries)


class Client:
    def __init__(self, ip: str, port: int):
        '''
        ip/port of nebula graphd
        '''
        config = Config()
        config.max_connection_pool_size = 10
        self.pool = ConnectionPool()
        ok = self.pool.init([(ip, port)], config)
        if not ok:
            raise RuntimeError("connect failed")
        self.session = self.pool.get_session('root', 'nebula')
        self.session.execute('USE test')

    # todo: return Point
    def get_neighbors(self, vid) -> Tuple[str, Dict]:
        '''
        given a id, return the vector of id, and its neighbor of Dict[level, List[dst id]]
        '''
        # todo: replace t1 as tag, col1 as property
        # todo: use int id?
        query = "FETCH PROP ON t1 \'{}\' YIELD properties(vertex).col1".format(vid)
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise RuntimeError("fetch failed")
        # get the vector of id
        try:
            vec = result.row_values(0)[0]
        except OutOfRangeException:
            raise RuntimeError("fetch no result")

        # todo: replace e1 as edge
        query = "GO FROM \'{}\' OVER e1 YIELD rank(edge) as rank, dst(edge) as dst".format(vid)
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise RuntimeError("go failed")

        # get neighbors of id
        size = result.row_size()
        neighbors: Dict[int, List[int]] = {}
        for i in range(size):
            row = result.row_values(i)
            # two column in each row rank and dst
            rank = row[0].as_int()
            dst = row[1].as_int()
            if neighbors.get(rank):
                neighbors[rank].append(dst)
            else:
                neighbors[rank] = [dst]

        # todo: return Point by assemble id, vec and neighbors
        return (vec, neighbors)

    def insert_vertex(self, vid, vector):
        query = "INSERT VERTEX t1(col1) VALUES \'{}\': (\'{}\')".format(vid, vector)
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise RuntimeError("insert vertex failed")

    def insert_edge(self, src, level, dst):
        query = "INSERT EDGE e1() VALUES \'{}\' -> \'{}\' @{}: ()".format(src, dst, level)
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise RuntimeError("insert edge failed")

    def insert_batch(self) -> InsertBatch:
        return InsertBatch()

    def insert(self, batch: InsertBatch):
        batchStr = ';'.join(batch)
        result = self.session.execute(batchStr)
        if not result.is_succeeded():
            raise RuntimeError(f"insert batch {batchStr} failed")

    def execute(self, query):
        return self.session.execute(query)

    def close(self):
        self.session.release()
        self.pool.close()


if __name__ == "__main__":
    client = Client("192.168.8.211", 3999)
    client.execute(
        'create space if not exists test(partition_num=10, replica_factor=1, vid_type=int)')
    client.execute('use test')
    client.execute('create tag if not exists t1(vec_str string)')
    client.execute('create edge if not exists e1()')
    sleep(10)
    client.insertEdge(1, 0, 2)  # src, level, dst
    client.insertVertex(1, "some vector")  # vid, vector
    client.get_neighbors(2)
    client.close()
