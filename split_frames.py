#!/usr/bin/python

import os
import sys
import getopt
import shutil

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [-r rate] [-o outdir] movie [...]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  movie:  One or more movie files to split into frames.\n")
    sys.stderr.write( "  rate:  The number of frames per second to capture. Defaults to 10.\n")
    sys.stderr.write( "  outdir:  The output directory. Defaults to ./frames.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    splitFrames(args, odict["o"], odict["r"])


def splitFrames(fnames, outdir, rate=10):
    tmpdir = os.path.join(outdir, "tmp")
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    for fname in fnames:
        basename = os.path.splitext(os.path.basename(fname))[0] + ".jpg"
        cmd = "/usr/local/bin/ffmpeg -i %s -r %d -vf rotate=PI -f image2 '%s/%s.%%04d'" % (fname, rate, tmpdir, basename)
        print "[%s/%d] Running %s..." % (fnames.index(fname) + 1, len(fnames), cmd)
        if (os.system(cmd)):
            raise "Error"
        shuffle(tmpdir, outdir)
        

def shuffle(tmpdir, outdir):
    print "Shuffling into frame dirs..."
    for fname in os.listdir(tmpdir):
        (basename, frame) = os.path.splitext(fname)
        frame = frame[1:]
        framedir = os.path.join(outdir, frame)
        if not os.path.exists(framedir):
            os.mkdir(framedir)
        shutil.move(os.path.join(tmpdir, fname), os.path.join(framedir, basename))
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hr:o:", ["help"] )
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
    
    if (not odict.has_key("o")):
        odict["o"] = "frames"

    return (odict, args)


if __name__ == '__main__':
    main()
