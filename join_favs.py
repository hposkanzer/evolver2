#!/usr/bin/python

import os
import sys
import getopt
import shutil

import find_favs
import join_frames
import progress


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-r rate] fav [...]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  fav:  One or more gallery files on which to call join_frames.py.\n")
    sys.stderr.write( "  rate:  The number of frames per second to capture. Defaults to 10.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)

    tups = find_favs.findFavs(args).items()
    def wrapper(i):
        (fav, exp) = tups[i]
        print "[%d/%d] Joining %s/%s..." % (i + 1, len(tups), exp, fav)
        join_frames.joinFrames(exp, fav, odict["r"])
    progress.ProgressBar(range(len(tups)), wrapper, newlines=1).start()
        
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hr:", ["help"] )
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

    if (len(args) <= 0):
        usage()
        
    if (not odict.has_key("r")):
        odict["r"] = "10"
    odict["r"] = int(odict["r"])

    return (odict, args)


if __name__ == '__main__':
    main()
