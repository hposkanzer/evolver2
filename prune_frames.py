#!/usr/bin/python

import os
import sys
import getopt
import shutil

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-i dir]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  dir:  the directory containing the frame directories. Defaults to ./frames.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    pruneFrames(odict["i"])


def pruneFrames(dir):
    srcimgs = set(filter(lambda x: x.endswith(".jpg") and not x.endswith(".t.jpg"), os.listdir(os.path.join(dir, "0001"))))
    framedirs = os.listdir(dir)
    for frame in framedirs:
        framedir = os.path.join(dir, frame)
        target = set(filter(lambda x: x.endswith(".jpg") and not x.endswith(".t.jpg"), os.listdir(framedir)))
        if target != srcimgs:
            print "Pruning %s..." % (framedir)
            shutil.rmtree(framedir)
            
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hi:", ["help"] )
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

    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()
        
    if (not odict.has_key("i")):
        odict["i"] = "frames"

    return (odict, args)


if __name__ == '__main__':
    main()
