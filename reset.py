#!/usr/bin/env python

import os
import sys
import getopt
import logging

import Experiment

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] name [...]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  name:  The experiment to reset.\n")
    sys.exit(-1)
    
def main():
    
    Experiment.initLogging()
    odict, args = getOptions()
    doAmazing(odict, args)
    

def doAmazing(odict, args):

    for name in args:    
        exp = Experiment.Experiment(name)
        sys.stdout.write("Are you sure you want to wipe out %s?  " % (exp))
        sys.stdout.flush()
        yn = sys.stdin.readline().strip()
        if (yn.lower()== "y"):
            exp.reset()
        else:
            print "Aborted!"
    

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help", "debug"] )
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
        
    if (len(args) < 1):
        usage()

    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)

    return odict, args


if __name__ == '__main__':
    main()