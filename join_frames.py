#!/usr/bin/python

import os
import sys
import getopt
import shutil

import Experiment
import Creature
import change_sources
import progress


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-r rate] -e exp -c creature\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which to create the movie.\n")
    sys.stderr.write( "  creature:  The name of the creature.\n")
    sys.stderr.write( "  rate:  The number of frames per second to capture. Defaults to 10.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    joinFrames(odict["e"], odict["c"], odict["r"])


def joinFrames(expName, creatureName, rate=10):
    exp = Experiment.Experiment(expName)
    exp.loadConfig()
    exp.loadTransforms()
    creature = Creature.Creature(exp, creatureName)
    creature.loadConfig()
    outFile = os.path.join(exp.getCreaturesDir(), creature.getName() + ".mp4")
    if os.path.exists(outFile):
        return
    inDir = os.path.join(exp.getCreaturesDir(), creature.getName())
    tmpFile = os.path.join(exp.getCreaturesDir(), creature.getName() + ".tmp.mp4")
    cmd = "/usr/local/bin/ffmpeg -y -f image2 -pattern_type glob -framerate %d -i '%s/*.jpg' %s" % (rate, inDir, tmpFile)
    print "Running %s..." % (cmd)
    if (os.system(cmd)):
        raise "Error"
    shutil.move(tmpFile, outFile)
        
        
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:c:r:", ["help", "debug"] )
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

    if (not odict.has_key("r")):
        odict["r"] = "10"
    odict["r"] = int(odict["r"])

    return (odict, args)


if __name__ == '__main__':
    main()
