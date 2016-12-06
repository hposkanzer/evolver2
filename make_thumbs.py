#!/usr/bin/python

import sys
import os
import string
import getopt

import Picklable
import Experiment
import Thumbnailer
import ImageLoader


def main():
	(odict, args) = getOptions()
	config = Picklable.Picklable().loadConfig()
	tn = Thumbnailer.Thumbnailer(config["thumbnail_size"], not odict.get("s3", False))
	for imgfile in args:
		makeThumb(tn, imgfile)


def makeThumb(tn, imgfile):
	img = ImageLoader.ImageLoader().loadImage(imgfile)
	thumbfile = toThumb(imgfile)
	print "Thumbnailing %s..." % (imgfile)
	tn.makeThumb(img, thumbfile)
	
	
def toThumb(imgfile):
	(root, ext) = os.path.splitext(imgfile)
	return root + ".t" + ext
	

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help", "debug", "s3"] )
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

    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    if odict.has_key("s3"):
        odict["s3"] = True
        
    return odict, args


if __name__ == '__main__':
    main()