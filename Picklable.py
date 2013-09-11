import string
import time
import logging
import random
import os
import sys

import Location

idDigits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
random.seed(os.getpid() + int(time.time()))

class Picklable:
    
    conf_file = "config.json"

    def __init__(self):
        self.logger = logging.getLogger(self.getLoggerName())
        self.loc = Location.getInstance()
        
    def getLoggerName(self):
        return self.__class__.__name__

    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d
    
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.logger = logging.getLogger(self.getLoggerName())


    def generateID(self):
        l = []
        i = int(time.time()*1000)
        while i:
            l.insert(0, idDigits[i % len(idDigits)])
            i = i / len(idDigits)
        return string.join(l, "") + random.choice(idDigits) + random.choice(idDigits)
        
        
    def loadConfig(self, fname=None):
        if not fname:
            fname = self.conf_file
        f = open(fname)
        config = Location.getJsonModule().load(f)
        f.close()
        if config.get("debug"):
            logging.getLogger().setLevel(logging.DEBUG) # Set the root level.
        return config

    def saveConfig(self, config, fname=None):
        if not fname:
            fname = self.conf_file
        f = open(fname, "w")
        Location.getJsonModule().dump(config, f, indent=2)
        f.write("\n")  # json doesn't include a trailing newline?
        f.close()


def isValidID(id):
    for c in id:
        if c not in idDigits:
            return False
    return True


class InvalidID(Exception):
    def __init__(self, exp):
        Exception.__init__(self, exp)


if __name__ == "__main__":
    p = Picklable()
    for i in range(5):
        print p.generateID()
        #time.sleep(0.01)