#!/usr/bin/python

import os
import sys
import getopt
import shutil

import Experiment
import Creature
import change_sources

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-m freq] -e exp -c creature\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  freq:  Mutate every freq frames. Defaults to 0 (never).\n")
    sys.stderr.write( "  exp:  The name of the experiment in which to create the creature.\n")
    sys.stderr.write( "  creature:  The name of the source creature.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    evolveFrames(odict, odict["e"], odict["c"], odict["m"])


def evolveFrames(odict, expName, sourceName, mutationFreq = 0):
    exp = Experiment.Experiment(expName)
    exp.loadConfig()
    exp.loadTransforms()
    outDir = os.path.join(exp.getCreaturesDir(), sourceName)
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    source = Creature.Creature(exp, sourceName)
    source.loadConfig()
    source_id = source.id
    for frame in range(1, 601):
        if (mutationFreq > 0 and frame % mutationFreq == 0):
            print "Evolving..."
            source.evolve()
        source.id = source_id + ".%04d" % (frame)
        print "Generating %s..." % (source.id)
        source.saveConfig()
        # Update the srcimgs symlink to the correct frame.
        os.remove(exp.getSrcImageDir())
        os.symlink(os.path.join(exp.loc.base_dir, "frames", "%04d" % (frame)), exp.getSrcImageDir())
        # Generate it.
        source.run()
        # Move it into the final location.
        src = os.path.join(exp.getCreaturesDir(), source.getImageName())
        dst = os.path.join(outDir, "%04d.jpg" % (frame))
        shutil.move(src, dst)
        # Delete the extraneous files.
        for fname in [source.getPageName(), source.getThumbName(), source.getPickleName()]:
            os.remove(os.path.join(exp.getCreaturesDir(), fname))
        
        
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hm:e:c:", ["help", "debug"] )
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
    if not odict.has_key("c"):
        usage()
        
    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()

    return (odict, args)


if __name__ == '__main__':
    main()
