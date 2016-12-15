#!/usr/bin/python

import os
import sys
import getopt
import shutil

import find_favs
import evolve_frames
import progress


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-m freq] fav [...]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  freq:  Mutate every freq frames. Defaults to 0 (never).\n")
    sys.stderr.write( "  fav:  One or more gallery files on which to call evolve_frames.py.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)

    tups = find_favs.findFavs(args).items()
    for i in range(len(tups)):
        (fav, exp) = tups[i]
        print "[%d/%d] Evolving %s/%s..." % (i + 1, len(tups), exp, fav)
        evolve_frames.evolveFrames(exp, fav, odict["m"])
        i = i + 1
        
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hm:", ["help"] )
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

    return odict, args


def processOptions(odict, args):

    if (len(args) <= 0):
        usage()
        
    return (odict, args)


if __name__ == '__main__':
    main()
