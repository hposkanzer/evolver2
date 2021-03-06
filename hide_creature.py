#!/usr/bin/python

import cgi
import os
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
    sys.stderr.write( "Usage:  %s [--debug] -e exp -c creature\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creature.\n")
    sys.stderr.write( "  creature:  The name of the creature to hide.\n")
    sys.exit(-1)
    
    
def main():
    
    try:

        Experiment.initLogging(os.environ.has_key("GATEWAY_INTERFACE"))
        
        if os.environ.has_key("GATEWAY_INTERFACE"):
            # CGI
            (odict, args) = getCGIOptions()
        else:
            # Command line.  All the output is still CGI-ish, though.  Sorry.
            (odict, args) = getOptions()
        (odict, args) = processOptions(odict, args)
            
        data = hideCreature(odict, odict["e"], odict["c"])
        data = Location.getJsonModule().dumps(data, indent=2)
        
        print "Content-type: application/json"
        print "Content-length: %s" % (len(data))
        print
        print data

    except:
        msg = string.join(apply( traceback.format_exception, sys.exc_info() ), "")
        if (msg[-1] == "\n"):
            msg = msg[:-1]
        logging.getLogger().warning(msg)
        data = "Huh?\n%s" % (msg)
        print "Status: 500 Internal Server Error"
        print "Content-type: text/plain"
        print "Content-length: %s" % (len(data))
        print
        print data


def hideCreature(odict, exp, creature):
    
    exp = Experiment.Experiment(exp)
    creature = exp.hideCreature(creature)
    return creature.getInfo()
    

def getCGIOptions():
    
    odict = cgi.parse()
    args = []
    
    if not odict.has_key("e"):
        raise UsageError.UsageError("No experiment specified")
    odict["e"] = odict["e"][0]
    
    if not odict.has_key("c"):
        raise UsageError.UsageError("No creature specified")
    odict["c"] = odict["c"][0]
    
    return (odict, args)


def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:c:", ["help", "debug"] )
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
        
    if not odict.has_key("c"):
        usage()
        
    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()

    if not Picklable.isValidID(odict["e"]):
        raise Picklable.InvalidID(odict["e"])
    if not Picklable.isValidID(odict["c"]):
        raise Picklable.InvalidID(odict["c"])
        
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    return (odict, args)


if __name__ == '__main__':
    main()
