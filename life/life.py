from collections import Counter
from common.geometry import Point
from random import randint, sample

LIFE = {3}, {2, 3}
HIGHLIFE = {3, 6}, {2, 3}


def __gencell__(squaresize, hdisp, vdisp):
    return Point(randint(0, squaresize - 1) + hdisp*squaresize,
                 randint(0, squaresize - 1) + vdisp*squaresize)


def seed_configuration(squaresize, proportion, displacement):
    xdisp, ydisp = randint(0, displacement), randint(0, displacement)
    return {__gencell__(squaresize, xdisp, ydisp)
            for _ in range(randint(int((squaresize**2)*proportion[0]),
                                   int((squaresize**2)*proportion[1])))}


def seed_rule(born=(1, 8), range_b=(1, 8), surv=(1, 8), range_s=(1, 8)):
    return frozenset(sample(range(born[0], born[1] + 1),
                            k=randint(range_b[0], min(range_b[1], born[1] - born[0] + 1)))),  \
        frozenset(sample(range(surv[0], surv[1] + 1),
                         k=randint(range_s[0], min(range_s[1], surv[1] - surv[0] + 1))))


def neighbors(cell, distance):
    coef = (2 * distance) + 1
    for i in range(coef**2):
        yield cell + Point((i // coef), (i % coef)).shift(-distance)


def energy(configuration):
    return Counter(e for cell in configuration for e in neighbors(cell, 1))


def advance(configuration, rule):
    return {cell for cell, en in energy(configuration).items()
            if en - 1*(cell in configuration) in rule[1*(cell in configuration)]}


def partition(configuration, distance):
    sub = set(configuration)
    while len(sub) != 0:
        visited = {sub.pop()}
        part = set(visited)
        while len(visited) != 0 and len(sub) != 0:
            visited |= set(neighbors(visited.pop(), distance)) & sub
            part |= visited
            sub -= visited
        yield part


def profile(configuration, distance):
    return Counter(frozenset(Counter(energy(part).values()).items())
                   for part in partition(configuration, distance))


def centralize(configuration):
    minpoint = Point(min(configuration).x, min(configuration, key=lambda p: p.y).y)
    return {cell - minpoint for cell in configuration}


def split(configuration, distance):
    return Counter(map(lambda part: frozenset(centralize(part)), partition(configuration, distance)))


def isstill(configuration, rule, limit):
    nextconf = configuration
    for _ in range(limit):
        nextconf = advance(nextconf, rule)
        if(configuration == nextconf):
            return True
    return False


def cycle(configuration, rule, limit):
    ref = centralize(configuration)
    nextconf = configuration
    for i in range(limit):
        nextconf = advance(nextconf, rule)
        if(ref == centralize(nextconf)):
            return i+1
    return 0
