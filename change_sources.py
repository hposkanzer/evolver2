#!/usr/bin/python

import os
import sys
import getopt
import json

import Location
import Experiment
import Creature

sys.path.append("/Users/hmp/workspace/evolver2/xforms")

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s -e exp -s source -d destination [-m map]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creature.\n")
    sys.stderr.write( "  source:  The name of the source creature.\n")
    sys.stderr.write( "  destination:  The name of the destination creature.\n")
    sys.stderr.write( "  map:  A JSON file containing a mapping from old source filename to new.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    data = newCreature(odict, odict["e"], odict["s"], odict["d"], odict["m"])
    data = Location.getJsonModule().dumps(data, indent=2)
    
    print data


def newCreature(odict, exp, source, destination, source_map={}):
    
    exp = Experiment.Experiment(exp)
    exp.loadConfig()
    creature = Creature.Creature(exp, source)
    creature.loadConfig()
    creature.id = destination
    changeSources(creature, source_map)
    print "Generatiing..."
    creature.saveConfig()
    creature.run()
    return creature.getInfo()
    

def changeSources(creature, source_map):
    if not source_map:
        return
    changeSourcesInner(creature.head, source_map)
    
    
def changeSourcesInner(xform, source_map):
    if xform.is_non_transformer:
        srcimg = xform.getSrcImage()
        old_path = srcimg.getPath()
        (dir, fname) = os.path.split(old_path)
        fname = source_map.get(fname, fname)
        new_path = os.path.join(dir, fname)
        if (new_path != old_path):
            srcimg.setPath(new_path)
            print "Changed %s to %s." % (old_path, new_path)
    else:
        for input in xform.inputs:
            changeSourcesInner(input, source_map)
    xform.resetCache()
    
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:s:d:m:", ["help", "debug"] )
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
    if not odict.has_key("d"):
        usage()
        
    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()

    if odict.has_key("m"):
        source_map = json.load(open(odict["m"]))
        if (type(source_map) != type({})):
            usage("JSON file not a map")
    else:
        source_map = {}
    odict["m"] = source_map
        
    return (odict, args)


if __name__ == '__main__':
    main()
