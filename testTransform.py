#!/usr/bin/python

import cgi
import os
import sys
import getopt
import traceback
import string
import logging
import pprint

import Location
import Picklable
import Experiment
import Creature
import UsageError


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] -e exp [-t transform]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creature.\n")
    sys.stderr.write( "  transform:  The name of the transform to test. If not given, a random transform is used.\n")
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
            
        data = newCreature(odict, odict["e"], odict.get("t"))
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


def newCreature(odict, exp, transform=None):
    
    exp = Experiment.Experiment(exp)
    exp.loadConfig()
    exp.loadImages()
    exp.loadTransforms()
    if transform:
        for xformCls in exp.xforms:
            if (xformCls.__name__ == transform):
                xform = xformCls()
                break
        else:
            raise UsageError.UsageError("No transform named '%s' found" % (transform))
    else:
        xform = exp.getRandomTransform()
    print "Creating new creature in %s using %s..." % (exp, xform.__class__.__name__)
    creature = Creature.Creature(exp)
    for i in range(xform.getExpectedInputCount()):
        xform.addInput(creature.getRandomSrcImage())
    creature.head = xform
    pprint.pprint(creature.getGenome())
    creature.run()
    return creature.getInfo()
    

def getCGIOptions():
    
    odict = cgi.parse()
    args = []
    
    if not odict.has_key("e"):
        raise UsageError.UsageError("No experiment specified")
    odict["e"] = odict["e"][0]
    
    if odict.has_key("t"):
        odict["t"] = odict["t"][0]
    
    return (odict, args)


def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:t:", ["help", "debug"] )
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
    if odict.has_key("p") and not Picklable.isValidID(odict["p"]):
        raise Picklable.InvalidID(odict["p"])
        
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    return (odict, args)


if __name__ == '__main__':
    main()
