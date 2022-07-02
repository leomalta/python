from json import dumps, loads
from os.path import splitext


def readjson(filepath):
    with open('.'.join([splitext(filepath)[0], "json"]), 'r+') as file:
        return loads(file.read())

def writejson(filepath, config):
    with open('.'.join([splitext(filepath)[0], "json"]), 'r+') as file:
        file.write(dumps(config, indent=4))
