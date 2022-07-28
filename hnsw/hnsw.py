import typing as T
import math
import random

from hnsw.element import Element, Elements
from layered_graph import LayeredGraph


def search_layer(graph: LayeredGraph, q: Element, ep: T.List[Element], ef: int, l: int) -> T.List[Element]:
    ''' Search closest ef elements in layer l, with ep as the entry point set

    Args:
        graph: layered graph
        q: query element
        ep: entry points
        ef: number of nearest to q elements to return
        l: layer number

    Returns: ef closest neighbors to q
    '''
    assert len(ep) <= ef  # TODO(spw): need this or not?

    visited = {e for e in ep}
    result = Elements(q, False, ep)
    candidates = Elements(q, True, ep)

    while len(candidates) > 0:
        curr = candidates.pop_nearest()
        furthest_res = result.furthest()

        if curr.distance(q) > furthest_res.distance(q):
            break

        for next in graph.get_neighbors(l, curr):
            if next in visited:
                continue

            visited.add(next)
            furthest_res = result.furthest()
            if next.distance(q) < furthest_res.distance(q) or len(result) < ef:
                candidates.push(next)
                result.push(next)
                if len(result) < ef:
                    result.pop_furthest()

    return result.values


def select_neighbors_simple(q: Element, candidates: T.List[Element], m: int) -> T.List[Element]:
    ''' Select m nearest elements from candidates to q 

    Args:
        q: base element
        candidates: candidate elements 
        m: number of neighbors to return 

    Returns:
        m nearest elements to q
    '''

    assert q is not None
    assert len(candidates) >= m

    elements = Elements(q, True, candidates)
    return [elements.pop_nearest() for i in range(0, m)]


def select_neighbors_heuristic(graph: LayeredGraph, q: Element, c: T.List[Element],
                               m: int, l: int, extend: bool = False, keep: bool = False) -> T.List[Element]:
    ''' Select nearest neighbors heuristically

    Args:
        q: base element
        c: candidate elements
        m: number of neighbors to return
        l: layer number
        extend: flag indicating whether or not to extend candidate list
        keep: flag indicating whether or not to add discarded elements

    Returns:
        m elements selected by the heuristic
    '''

    result = Elements(q, nearest=True)
    candidates = Elements(q, nearest=True, elements=c)

    if extend:
        for curr in c:
            for next in graph.get_neighbors(l, curr):
                if next not in candidates:
                    candidates.push(next)

    to_discard = Elements(q, nearest=True)
    while len(candidates) > 0 and len(result) < m:
        curr = candidates.nearest()
        if len(result) == 0 or curr.distance(q) < result.nearest().distance(q):
            result.push(curr)
        else:
            to_discard.push(curr)

    if keep:
        while len(to_discard) > 0 and len(result) < m:
            result.push(to_discard.nearest())

    return result.values


def insert(graph: LayeredGraph, q: Element, m: int, m_max: int, ef: int, ml: int):
    ''' Insert element to graph with 

    Args:
        graph: layered graph
        q: new element
        m: number of established connections
        m_max: maximum number of connections for each element per layer
        ef: size of the dynamic candidate list
        ml: normalization factor for level generation
    '''

    result = Elements(q, nearest=False)
    entry_points: T.List[Element] = [graph.entry_point()]
    new_layer = math.floor(-math.log(random.random()))
    assert(new_layer <= graph.max_top_layer)

    # l in [new_layer+1, top_layer], from top to bottom.
    # only find one entry point for next layer
    for l in range(graph.top_layer, new_layer, -1):
        elements = search_layer(graph, q, ep, 1, l)
        entry_points = [Elements(q, nearest=True, elements=elements).nearest()]

    # l in [0, new_layer], from top to bottom.
    # Find a entry point set for next layer
    for l in range(min(graph.top_layer, new_layer), -1, -1):
        elements = search_layer(graph, q, entry_points, ef, l)
        neighbors = select_neighbors_heuristic(graph, q, elements, m, l)
        for e in neighbors:
            graph.add_edge(l, q, e)

        # shrink connections if old element's edges greater than m_max
        for e in neighbors:
            curr_neighbors = graph.get_neighbors(l, e)
            if len(curr_neighbors) > m_max:
                new_neighbors = select_neighbors_heuristic(graph, e, curr_neighbors, m_max, l)
                graph.set_neighbors(l, e, new_neighbors)
        entry_points = elements

    if new_layer > graph.top_layer:
        graph.set_entry_point(p)
