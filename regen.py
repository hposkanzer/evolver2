#!/usr/bin/python
'''
Created on Aug 4, 2010

@author: hmp
'''
import os
import sys
import getopt
import logging

import Experiment

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [exp_dir]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp_dir:  Regenerate the HTML in this experiment.  If not provided, all experiments are regenerated.\n")
    sys.exit(-1)
    
def main():
    
    Experiment.initLogging()
    odict, args = getOptions()
    doAmazing(odict, args)
    

def doAmazing(odict, args):
    
    if args:
        exp_names = [args[0]]
    else:
        exp_names = Experiment.getAllExperiments()
        
    for exp_name in exp_names:
        exp = Experiment.Experiment(exp_name)
        exp.regenHTML()
    

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

    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
    
    return odict, args


if __name__ == '__main__':
    main()