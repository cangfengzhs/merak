from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from typing import Dict, List
from time import sleep

class Client:
    def __init__(self, ip, port):
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
    def getNeighbors(self, vid):
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
        neighbors: Dict[int, List[str]] = {}
        for i in range(size):
            row = result.row_values(i)
            # two column in each row rank and dst
            rank = row[0].as_int()
            dst = row[1].as_string()
            if neighbors.get(rank):
                neighbors[rank].append(dst)
            else:
                neighbors[rank] = [dst]

        # todo: return Point by assemble id, vec and neighbors
        print(vid, vec, neighbors)

    def insertVertex(self, vid, vector):
        query = "INSERT VERTEX t1(col1) VALUES \'{}\': (\'{}\')".format(vid, vector)
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise RuntimeError("insert vertex failed")

    def insertEdge(self, src, level, dst):
        query = "INSERT EDGE e1() VALUES \'{}\' -> \'{}\' @{}: ()".format(src, dst, level)
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise RuntimeError("insert edge failed")

    def execute(self, query):
        return self.session.execute(query)

    def close(self):
        self.session.release()
        self.pool.close()

if __name__ == "__main__":
    client = Client("192.168.8.211", 3999)
    client.execute('create space if not exists test(partition_num=10, replica_factor=1, vid_type=FIXED_STRING(10))')
    client.execute('use test')
    client.execute('create tag if not exists t1(col1 string)')
    client.execute('create edge if not exists e1()')
    sleep(10)
    client.insertEdge("v1", 0, "v2") # src, level, dst
    client.insertVertex("v1", "some vector") # vid, vector
    client.getNeighbors("v1")
    client.close()
