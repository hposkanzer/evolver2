#!/usr/bin/env python
'''
Created on Aug 4, 2010

@author: hmp
'''
import os
import sys
import getopt
import Experiment
import logging.config

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--local-only] [exp_dir]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  local-only:  Keep thumbnails on the local disk, instead of S3.\n")
    sys.stderr.write( "  exp_dir:  Evolve this experiment.  If not provided, all experiments are evolved.\n")
    sys.exit(-1)
    
def main():
    
    logging.config.fileConfig("logging.conf")
    odict, args = getOptions()
    doAmazing(odict, args)
    

def doAmazing(odict, args):
    
    if args:
        exp_dirs = [args[0]]
    else:
        exp_dirs = Experiment.getAllExperiments()
        
    for exp_dir in exp_dirs:
        exp = Experiment.Experiment(exp_dir)
        exp.regenHTML(local_only=odict.has_key("local-only"))
    

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help", "debug", "local-only"] )
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