#!/usr/bin/python

import os
import sys
import getopt

import change_sources

sys.path.append("/Users/hmp/workspace/evolver2")
sys.path.append("/Users/hmp/workspace/evolver2/xforms")
source_map_formats = {
              "IMG_1702_0010.jpg": "IMG_1702_%04d.jpg",
              "IMG_1703_0010.jpg": "IMG_1703_%04d.jpg",
              "IMG_1704_0010.jpg": "IMG_1704_%04d.jpg",
              "IMG_1705_0010.jpg": "IMG_1705_%04d.jpg",
              "IMG_1706_0010.jpg": "IMG_1706_%04d.jpg",
              "IMG_1707_0010.jpg": "IMG_1707_%04d.jpg"
              }

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s -e exp -s source\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creature.\n")
    sys.stderr.write( "  source:  The name of the source creature.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    evolveFrames(odict, odict["e"], odict["s"])


def evolveFrames(odict, exp, source):
    for frame in range(1, 101):
        evolveFrame(odict, exp, source, frame)
        
        
def evolveFrame(odict, exp, source, frame):
    destination = source + "_%04d" % (frame)
    source_map = {}
    for (k, v) in source_map_formats.items():
        source_map[k] = v % (frame)
    change_sources.newCreature(odict, exp, source, destination, source_map)
    
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:s:", ["help", "debug"] )
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
    if not odict.has_key("s"):
        usage()
        
    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()

    return (odict, args)


if __name__ == '__main__':
    main()
