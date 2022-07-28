import typing as T
import heapq
import math


class Element:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: 'Element') -> bool:
        return other.x == self.x and other.y == self.y

    def distance(self, other: 'Element') -> float:
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)


class Elements:
    ''' Helper class to get the nearest and furthest element in an element vector.
    '''

    def __init__(self, base: Element, nearest: bool = True, elements: T.List[Element] = []):
        self.elements: T.List[(float, Element)] = []
        self.base = base
        self.nearest = nearest
        for e in elements:
            self.push(e)

    def __len__(self) -> int:
        return len(self.elements)

    def __contains__(self, e: Element) -> bool:
        return e in self.elements

    @property
    def values(self) -> T.List[Element]:
        return self.elements

    def push(self, p: Element):
        if self.nearest:
            heapq.heappush(self.elements, (p.distance(self.base), p))
        else:
            heapq.heappush(self.elements, (-p.distance(self.base), p))

    def pop_nearest(self) -> Element:
        assert self.nearest is True
        return heapq.heappop(self.elements)[1]

    def nearest(self) -> Element:
        if self.nearest:
            return self.elements[0][1]
        else:
            return max(self.elements)[1]

    def pop_furthest(self) -> Element:
        assert self.nearest is False
        return heapq.heappop(self.elements)[1]

    def furthest(self) -> Element:
        if self.nearest is False:
            return self.elements[0][1]
        else:
            return max(self.elements)[1]
