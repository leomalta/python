from life.life import cycle, isstill, profile, split


def measure(metric, rundata):
    return globals()['_'.join(metric.split())](rundata)


def most_diff_shapes(rundata):
    return len([part for part in split(rundata['configuration'], 1).keys() if len(part) > 1])


def most_diff_parts(rundata):
    return len([part for part in profile(rundata['configuration'], 1).keys() if len(part) > 1])


def most_diff_groups(rundata):
    return len([part for part in profile(rundata['configuration'], 2).keys() if len(part) > 1])


def longest(rundata):
    return rundata['iterations']


def longest_cycle(rundata):
    return rundata['cyclesize']


def biggest_part(rundata):
    return max(len(part) for part in split(rundata['configuration'], 1))


def biggest_group(rundata):
    return max(len(part) for part in split(rundata['configuration'], 2))


def most_moving_parts(rundata):
    return max(sum([occur for part, occur in split(rundata['configuration'], 2).items()
                    if not isstill(part, rundata['rule'], rundata['cyclesize'])]), 0.5)


def most_non_still(rundata):
    return max(sum([occur for part, occur in split(rundata['configuration'], 1).items()
                    if not isstill(part, rundata['rule'], 1)]), 0.5)


def biggest_non_still(rundata):
    r = [len(part) for part, _ in split(rundata['configuration'],
                                        2).items() if not isstill(part, rundata['rule'], 3)]
    return max(r) if len(r) else 0.5


def total_moving_parts(rundata):
    return max(sum([(len(part)**2) * occur for part, occur in split(rundata['configuration'], 2).items()
                    if not isstill(part, rundata['rule'], rundata['cyclesize'])]), 1)


def weighted_parts(rundata):
    def func(x): return sum(split(x[0], 1).values()) * x[1] if isstill(x[0], rundata['rule'], rundata['cyclesize']) \
        else rundata['moving weight'] * x[1]
    return sum(map(func, split(rundata['configuration'], 2).items()))


def most_parts(rundata):
    return sum(split(rundata['configuration'], 2).values())


def most_shapes(rundata):
    return sum(split(rundata['configuration'], 1).values())


def biggest(rundata):
    return len(rundata['configuration'])


def most_growth(rundata):
    return len(rundata['configuration']) / len(rundata['origin'])


def cycle_part(rundata):
    return max([cycle(part, rundata['rule'], 50) for part in split(rundata['configuration'], 2).keys()])
