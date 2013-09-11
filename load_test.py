#!/usr/bin/python

import cgi
import os
import glob
import sys
import getopt
import traceback
import string
import logging

import Location
import Picklable
import Experiment
import UsageError


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] -e exp\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creatures.\n")
    sys.exit(-1)
    
    
def main():
    
    Experiment.initLogging(os.environ.has_key("GATEWAY_INTERFACE"))
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    data = doit(odict, odict["e"])


def doit(odict, exp):
    
    exp = Experiment.Experiment(exp)
    
    for i in range(20):
        exp.newCreature()

    c = None
    try:    
        while True:
            l = glob.glob("exps/%s/creatures/*.html" % (exp.getName()))
            l = map(os.path.basename, l)
            l = map(lambda x: os.path.splitext(x)[0], l)
            for c in l:
                exp.newCreature(c)
    except:
        print "Failed on %s." % (c)
        traceback.print_exc(10)
        cre = exp.getCreature(c)
        cre.loadConfig()
        print cre.toString()
        sys.exit(1)
        

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:", ["help", "debug"] )
    except getopt.error:
        usage( str(sys.exc_info()[1]) )

    odict = {}
    for t in tt:
        s = t[0]
        while (s[0] == "-"):        # Strip leading '-'s
            s = s[1:]
        if not odict.has_key( s ):
            odict[s] = []
        odict[s] = t[1]

    if (odict.has_key("h") or odict.has_key("help")):
        usage()

    if not odict.has_key("e"):
        usage()
        
    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()

    if not Picklable.isValidID(odict["e"]):
        raise Picklable.InvalidID(odict["e"])
        
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    return (odict, args)


if __name__ == '__main__':
    main()
