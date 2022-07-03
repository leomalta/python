from itertools import chain, takewhile
from re import compile
from common.geometry import Point
from life.life import LIFE

__config_regex__ = compile(r'(\d*)([bo$!])')
__rule_regex__ = compile(r'.*\srule\s*=\s*B\s*(\d+).*S\s*(\d+)')
__config_rule_regex__ = compile(r'B(\d+)S(\d+)')


def parse_rule(rulestr):
    rulematch = __config_rule_regex__.match(rulestr)
    if rulematch:
        return frozenset(int(d) for d in rulematch[1]), frozenset(int(d) for d in rulematch[2])


def from_rle(rlestring):
    rule_match = __rule_regex__.match(rlestring)
    rule = ({int(d) for d in rule_match[1]}, {int(d) for d in rule_match[2]}) \
        if rule_match else LIFE
    p = Point()
    configuration = set()
    for partrle in __config_regex__.findall(rlestring):
        if partrle[1] == '!':
            break
        digit = int(partrle[0]) if partrle[0] != '' else 1
        if partrle[1] == '$':
            p = Point(0, p.y + digit)
        else:
            if partrle[1] == 'o':
                configuration |= {Point(p.x + i, p.y) for i in range(digit)}
            p = Point(p.x + digit, p.y)
    return configuration, rule


def __adj_parts_rle__(sortedconfiguration, point, minX):
    def prev(cell): 
        return sortedconfiguration[sortedconfiguration.index(cell) - 1]
    def func(cell): 
        return cell == sortedconfiguration[0] or \
            (cell.y == prev(cell).y and cell.x == prev(cell).x + 1)
    while len(sortedconfiguration):
        adjpart = list(takewhile(func, sortedconfiguration))
        if point.y != adjpart[0].y:
            point = Point(minX, point.y)
        yield '$'*(adjpart[0].y - point.y) + \
            (str(adjpart[0].x - point.x - 1) if adjpart[0].x - point.x > 2 else "") +\
            ("b" if adjpart[0].x != point.x + 1 else "") + \
            (str(len(adjpart)) if len(adjpart) > 1 else "") + "o"
        sortedconfiguration = sortedconfiguration[len(adjpart):]
        point = adjpart[-1]


def to_rle(configuration, rule=None):
    if len(configuration) == 0:
        return ""
    xsorted = sorted(configuration)
    ysorted = sorted(configuration, key=lambda cell: cell.y +
                     (cell.x / (abs(xsorted[-1].x) + 1)))
    minpoint = Point(xsorted[0].x, ysorted[0].y)
    configsize = (Point(xsorted[-1].x, ysorted[-1].y) - minpoint).shift(1)
    s = "" if rule is None else \
        ("x=" + str(configsize.x) + ", " + "y=" + str(configsize.y) + ", " +
         "rule=" + ("B" + ''. join(str(b) for b in sorted(rule[0])) if len(rule[0]) else "") +
         ("/S" + ''. join(str(s) for s in sorted(rule[1])) if len(rule[1]) else "") + "\n")
    minpoint = Point(minpoint.x - 1, minpoint.y)
    return ''.join(chain(s, __adj_parts_rle__(ysorted, minpoint, minpoint.x), "!"))
