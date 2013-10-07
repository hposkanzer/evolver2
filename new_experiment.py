#!/usr/bin/python

import cgi
import os
import sys
import getopt
import traceback
import string
import logging

import Picklable
import Experiment


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--local-only] [--tile-mode] [--no-op] [name]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  local-only:  Keep thumbnails on the local disk, instead of S3.\n")
    sys.stderr.write( "  tile-mode:  Always apply a Shift filter first.\n")
    sys.stderr.write( "  no-op:  Do not generate creatures or preserve state.\n")
    sys.stderr.write( "  name:  Create this experiment name.  If not provided, a name is generated.\n")
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
            
        if args:
            url = newExperiment(odict, args[0])
        else:
            url = newExperiment(odict)
        
        print "Location: %s" % (url)
        print

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


def newExperiment(odict, name=None):
    
    exp = Experiment.Experiment(name)
    exp.initialize(odict.get("local-only", False), odict.get("no-op", False), odict.get("debug", False), odict.get("tile-mode", False))
    
    return exp.getURL()


def getCGIOptions():
    
    odict = cgi.parse()
    args = []
    
    if int(odict.get("local-only", [0])[0]):
        odict["local-only"] = True
    else:
        odict["local-only"] = False
    
    if int(odict.get("tile-mode", [0])[0]):
        odict["tile-mode"] = True
    else:
        odict["tile-mode"] = False
    
    if int(odict.get("no-op", [0])[0]):
        odict["no-op"] = True
    else:
        odict["no-op"] = False

    if int(odict.get("debug", [0])[0]):
        odict["debug"] = True
    else:
        odict["debug"] = False

    return (odict, args)
    

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help", "debug", "local-only", "tile-mode", "no-op"] )
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
        
    if odict.has_key("local-only"):
        odict["local-only"] = True
        
    if odict.has_key("tile-mode"):
        odict["tile-mode"] = True
        
    if odict.has_key("no-op"):
        odict["no-op"] = True

    return (odict, args)


def processOptions(odict, args):

    if (len(args) > 1):
        usage()
        
    if ((len(args) > 0) and not Picklable.isValidID(args[0])):
        raise Picklable.InvalidID(args[0])
    
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    return (odict, args)


if __name__ == '__main__':
    main()
