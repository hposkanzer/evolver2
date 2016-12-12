#!/usr/bin/python

import os
import sys
import getopt

import Experiment
import Creature
import change_sources

sys.path.append("/Users/hmp/workspace/evolver2")
sys.path.append("/Users/hmp/workspace/evolver2/xforms")
source_map_formats = {
              "IMG_1702_\d\d\d\d.jpg": "IMG_1702_%04d.jpg",
              "IMG_1703_\d\d\d\d.jpg": "IMG_1703_%04d.jpg",
              "IMG_1704_\d\d\d\d.jpg": "IMG_1704_%04d.jpg",
              "IMG_1705_\d\d\d\d.jpg": "IMG_1705_%04d.jpg",
              "IMG_1706_\d\d\d\d.jpg": "IMG_1706_%04d.jpg",
              "IMG_1707_\d\d\d\d.jpg": "IMG_1707_%04d.jpg"
              }

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-m freq] -e exp -s source\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  freq:  Mutate every freq frames. Defaults to 0 (never).\n")
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creature.\n")
    sys.stderr.write( "  source:  The name of the source creature.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    evolveFrames(odict, odict["e"], odict["s"], odict["m"])


def evolveFrames(odict, exp, source, mutationFreq = 0):
    exp = Experiment.Experiment(exp)
    exp.loadConfig()
    exp.loadImages()
    exp.loadTransforms()
    source = Creature.Creature(exp, source)
    source.loadConfig()
    source_id = source.id
    for frame in range(1, 101):
        if (mutationFreq > 0 and frame % mutationFreq == 0):
            print "Evolving..."
            source.evolve()
        evolveFrame(odict, exp, source, source_id, frame)
        
        
def evolveFrame(odict, exp, source, source_id, frame):
    destination = source_id + "_%04d_3" % (frame)
    source_map = {}
    for (k, v) in source_map_formats.items():
        source_map[k] = v % (frame)
    change_sources.newCreatureInner(odict, exp, source, destination, source_map)
    
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hm:e:s:", ["help", "debug"] )
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

    if not odict.has_key("m"):
        odict["m"] = "0"
    odict["m"] = int(odict["m"])
    
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
