from common.config import readjson
from itertools import chain
from life.config import log
from life.life import advance, partition, neighbors, seed_configuration, seed_rule, split
from life.metrics import measure
from life.rleparser import parse_rule
from random import choice, choices, randint
from threading import Thread
from time import process_time


CONFIG = readjson(__file__)
LOGFILE = '_'. join(
    [str(CONFIG['advances']), *CONFIG['metric'].split()]) + ".log"


def crossover(configuration1, configuration2):
    p = [*partition(configuration1, 1)] + [*partition(configuration2, 1)]
    return set().union(*choices(p, k=randint(1, len(p))))


def mutate(configuration, proportion):
    cpy = set(configuration)
    return cpy | {choice([*neighbors(cpy.pop(), 1)]) for _ in range(int(len(configuration)*proportion))}


def cyclesize(history):
    try:
        return len(history) - history[:-1].index(history[-1])
    except ValueError:
        return 0


def fitness(configuration, rule, times, currmin, limit):
    confhistory, parthistory = [configuration], [split(configuration, 2)]
    for i in range(1, times):
        nextconf = advance(confhistory[-1], rule)
        if len(nextconf) == 0:
            return 0
        if len(nextconf) > limit:
            break
        confhistory, parthistory = confhistory + \
            [nextconf], parthistory + [split(nextconf, 2)]
        cycle = cyclesize(parthistory)
        if cycle:
            return measure(CONFIG['metric'],
                           {'origin': configuration,
                            'configuration': nextconf,
                            'rule': rule,
                            'moving weight': CONFIG['moving weight'],
                            'iterations': i,
                            'cyclesize': cycle})
    # logdata(configuration, rule, currmin, i)
    return currmin


def __add__(population, fitness, configuration, rule):
    if fitness in population and (configuration, rule) in population[fitness]:
        return population
    if fitness not in population:
        population[fitness] = []
    population[fitness] += [(configuration, rule)]
    return population


def seed(population, times):
    for _ in range(times):
        rule = parse_rule(CONFIG['rule']) if 'rule' in CONFIG \
            else seed_rule(born=(1, 8), surv=(1, 8), range_b=(1, 3), range_s=(2, 4))
        configuration = seed_configuration(CONFIG['square size'],
                                           CONFIG['proportion'],
                                           CONFIG['displacement'])
        population = __add__(population, avgfitness(
            population), configuration, rule)
    return population


def sizepop(population): return len([*chain(*population.values())])


def avgfitness(population):
    return (sum(fit * len(poplist) for fit, poplist in population.items()) / sizepop(population)) if len(population) else 0.5


def minfitness(population):
    return min(sorted(population.keys())) if len(population) else 0.5


def maxfitness(population):
    return max(sorted(population.keys())) if len(population) else 0.5


def bestfit(population):
    if len(population) == 0:
        return 0, (set(), (frozenset(), frozenset()))
    popitem = sorted(population.items())[-1]
    return popitem[0], min(popitem[1], key=len)


def naturalfit(population):
    if len(population) == 0:
        return 0, (set(), (frozenset(), frozenset()))

    def func(x): return (x[0] * len(x[1])) / \
        (avgfitness(population)*sizepop(population))
    popitem = choices([i for i in population.items()], weights=[
                      *map(func, population.items())])[0]
    return popitem[0], choice(popitem[1])


def iterate(population, replacements, advances, sizelimit):
    nextpop = dict()
    for _ in range(replacements):
        fitparent1, (parent1, rule1) = naturalfit(population)
        nextpop = __add__(nextpop, fitparent1, parent1, rule1)
        fitparent2, (parent2, rule2) = naturalfit(population)
        nextpop = __add__(nextpop, fitparent2, parent2, rule2)
        child, rulechild = mutate(
            crossover(parent1, parent2), CONFIG['mutations']), (rule1[0], rule2[1])
        fitchild = fitness(child, rulechild, advances,
                           minfitness(population), sizelimit)
        if __name__ == '__main__':
            print('.', end='', flush=True)
        if fitchild == 0:
            continue
        nextpop = __add__(nextpop, fitchild, child, rulechild)
    if __name__ == '__main__':
        print('')
    return nextpop


def logdata(conf, rule, fit, iterations=None):
    Thread(target=log, args=(__file__, LOGFILE, conf, rule, fit, iterations)).start()


def run():
    currmax, currbest = 1, set()
    pop = dict()
    s = 0
    for i in range(CONFIG['iterations']):
        pop = seed(pop, CONFIG['random inserts'])
        st = process_time()
        pop = iterate(pop, CONFIG['replacements'],
                      CONFIG['advances'], CONFIG['max size'])
        t = (process_time() - st) / CONFIG['replacements']
        s += t
        maxfit, (bestconf, bestrule) = bestfit(pop)
        if __name__ == '__main__':
            print(i, ":\tt:", "{:.02f}".format(t),
                  "\tavg t:", "{:.02f}".format(s/(i+1)),
                  "\tpop:", "{:03d}".format(sizepop(pop)),
                  "\tavg:", "{:.02f}".format(avgfitness(pop)),
                  "\tmax:", "{:.02f}".format(maxfit))
        if currmax < maxfit or (currmax == maxfit and \
            len(bestconf) < len(currbest) or i % 50 == 49):
            currmax, currbest = maxfit, bestconf
            logdata(bestconf, bestrule, maxfit)


def simulate(population):
    return iterate(seed(population, CONFIG['random inserts']),
                   CONFIG['replacements'],
                   CONFIG['advances'],
                   CONFIG['max size'])


if __name__ == '__main__':
    run()
