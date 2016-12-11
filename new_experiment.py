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


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--s3] [--tile-mode] [--reflect-mode] [--grid-mode] [--no-op] [--frame frame] [name]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  s3:  Keep thumbnails on S3.\n")
    sys.stderr.write( "  tile-mode:  Always apply a TileTransformer first.\n")
    sys.stderr.write( "  reflect-mode:  Always apply a ReflectTransformer last.\n")
    sys.stderr.write( "  grid-mode:  Produce lots of immutable creatures.\n")
    sys.stderr.write( "  no-op:  Do not generate creatures or preserve state.\n")
    sys.stderr.write( "  frame:  Use source images from this video frame.\n")
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
    exp.initialize(not odict.get("s3", False), 
                   odict.get("no-op", False), 
                   odict.get("debug", False), 
                   odict.get("tile-mode", False), 
                   odict.get("reflect-mode", False), 
                   odict.get("grid-mode", False),
                   odict.get("frame"))
    
    return exp.getURL()


def getCGIOptions():
    
    odict = cgi.parse()
    args = []
    
    if int(odict.get("s3", [0])[0]):
        odict["s3"] = True
    else:
        odict["s3"] = False
    
    if int(odict.get("tile-mode", [0])[0]):
        odict["tile-mode"] = True
    else:
        odict["tile-mode"] = False
    
    if int(odict.get("reflect-mode", [0])[0]):
        odict["reflect-mode"] = True
    else:
        odict["reflect-mode"] = False
    
    if int(odict.get("grid-mode", [0])[0]):
        odict["grid-mode"] = True
    else:
        odict["grid-mode"] = False
    
    if int(odict.get("no-op", [0])[0]):
        odict["no-op"] = True
    else:
        odict["no-op"] = False

    if odict.has_key("frame"):
        odict["frame"] = int(odict["frame"][0])

    if int(odict.get("debug", [0])[0]):
        odict["debug"] = True
    else:
        odict["debug"] = False

    return (odict, args)
    

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help", "debug", "s3", "tile-mode", "reflect-mode", "grid-mode", "no-op", "frame="] )
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
        
    if odict.has_key("s3"):
        odict["s3"] = True
        
    if odict.has_key("tile-mode"):
        odict["tile-mode"] = True
        
    if odict.has_key("reflect-mode"):
        odict["reflect-mode"] = True
        
    if odict.has_key("grid-mode"):
        odict["grid-mode"] = True
        
    if odict.has_key("no-op"):
        odict["no-op"] = True
        
    if odict.has_key("frame"):
        odict["frame"] = int(odict["frame"])

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
