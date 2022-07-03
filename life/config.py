from life.rleparser import to_rle
from os import makedirs
from os.path import exists, join, dirname


def log(filepath, filename, configuration, rule, conffitness, iterations):
    logdir = join(dirname(filepath), "log")
    if not exists(logdir):
        makedirs(logdir)
    with open(join(logdir, filename), "a") as logfile:
        logfile.write("\n".join([" | ".join(["{:02.2f}".format(conffitness),
                                            str(len(configuration)),
                                            str(iterations) if iterations else ""]),
                                 to_rle(configuration, rule), "\n"]))
