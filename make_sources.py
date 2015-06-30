#!/usr/bin/python

import os
import sys
import getopt
import logging
import time

sys.path.append(os.path.expanduser("~/lib/python/PIL/"))
sys.path.append("/usr/lib64/python2.3/site-packages/PIL")

from PIL import Image
import ImageLoader
import Experiment
import SrcImage
import Thumbnailer
import Picklable


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--local-only] [-s srcimg_dir]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  -s:  Use this dir for source images.  Defaults to './srcimgs'.\n")
    sys.exit(-1)


def main():
    
    Experiment.initLogging()
    (odict, args) = getOptions()
    g = SourceGenerator(odict)
    g.generateSources()


class SourceGenerator(Picklable.Picklable):

    srcimgs = []
    
    def __init__(self, odict):
        Picklable.Picklable.__init__(self)
        self.odict = odict
        
    
    def generateSources(self):
        t0 = time.time()
        self.logger.info("Generating source images...")
        self.config = self.loadConfig()
        self.tn = Thumbnailer.Thumbnailer(self.config["thumbnail_size"], self.odict.get("local-only", False))
        self.loadSrcImages()
        self.scaleImages()
        self.makeSrcImageThumbs()
        self.writeSrcImageIndex()
        self.writeSrcImagePages()
        self.saveConfig(self.config) # Write all the discovered dimensions back to config.json.
        t1 = time.time()
        self.logger.info("Generation complete in %.2f seconds." % (t1-t0))

    
    def loadSrcImages(self):
        self.logger.debug("Loading source images...")
        il = ImageLoader.ImageLoader()
        for fpath in il.loadNames(self.getDir()):
            self.srcimgs.append(SrcImage.SrcImage(fpath))


    def scaleImages(self):
        # Scale everything to the size of the first image.
        dims = (self.config["img_width"], self.config["img_height"])
        for srcimg in self.srcimgs:
            img = srcimg.getImage()
            if (img.size != dims):
                self.logger.debug("Resizing %s from %s to %s..." % (srcimg, img.size, dims))
                img = img.resize(dims, Image.BICUBIC)
                img.save(srcimg.getPath())
                
                
    def makeSrcImageThumbs(self):
        self.logger.debug("Making source thumbnails...")
        for srcimg in self.srcimgs:
            fpath = srcimg.getThumbPath()
            self.tn.makeThumb(srcimg.getImage(), fpath)
        if self.srcimgs:
            srcimg = self.srcimgs[0]
            dims = Image.open(srcimg.getThumbPath()).size
            self.config["thumb_width"] = dims[0]
            self.config["thumb_height"] = dims[1]
            self.logger.debug("Source image thumbnails are %dx%d." % (dims[0], dims[1]))
            
            
    def writeSrcImageIndex(self):
        fname = os.path.join(self.getDir(), "index.html")
        self.logger.debug("Creating source image index...")
        f = open(fname, "w")
        f.write("<html>\n<head><title>Source Images</title></head>\n<body>\n")
        f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../../index.html'>Photo Evolver 2</a> &gt; <a href='../index.html'>Experiment</a></font>\n")
        f.write("<center>\n<h2>Source Images</h2>\n" )
        f.write("<i>These are the source images used as input to create the creatures for this experiment.  They're combined using the filters to create the creatures.</i><p>\n")
        f.write("<table>\n")
        columns = self.config["index_columns"]
        for i in range(len(self.srcimgs)):
            if not i % columns:
                if i:
                    f.write("</tr>\n")
                f.write("<tr>\n") 
            f.write("<td>%s</td>\n" % (self.getSrcImageThumb(i)))
        f.write("</tr>\n</table>\n")
        f.write("</center>\n")
        f.write("</body>\n</html>\n")
        f.close()
        
        
    def writeSrcImagePages(self):
        for i in range(len(self.srcimgs)):
            srcimg = self.srcimgs[i]
            fname = os.path.join(self.getDir(), srcimg.getPageName())
            self.logger.debug("Creating page for %s..." % (srcimg))
            f = open(fname, "w")
            f.write("<html>\n<head><title>Source Image %s</title></head>\n<body>\n" % (srcimg.getFilename()))
            f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../../index.html'>Photo Evolver 2</a> &gt; <a href='../index.html'>Experiment</a> &gt; <a href='index.html'>Source Images</a></font>\n")
            f.write("<center>\n<h2>Source Image %s</h2>\n" % (srcimg.getFilename()))
            f.write("<table><tr valign='center'>\n")
            f.write("<td width='%d'>%s</td>\n" % (self.config["thumbnail_size"], self.getSrcImageThumb(i-1)))
            f.write("<td><img src='%s' border=1 width=%d height=%d></td>\n" % (srcimg.getFilename(), self.config["img_width"], self.config["img_height"]))
            f.write("<td width='%d'>%s</td>\n" % (self.config["thumbnail_size"], self.getSrcImageThumb(i+1)))
            f.write("</tr></table></center>\n")
            f.write("</body>\n</html>\n")
            f.close()
            
            
    def getSrcImageThumb(self, i):
        if ((i < 0) or (i >= len(self.srcimgs))):
            return ""
        else:
            srcimg = self.srcimgs[i]
            # Source image thumbnails are always served from the base srcimg dir.
            src = self.tn.getURL(os.path.join(self.getDir(), srcimg.getThumbName()))
            return "<a href='%s'><img src='%s' border=1 width=%d height=%d></a>" % (srcimg.getPageName(), src, self.config["thumb_width"], self.config["thumb_height"])
            
            
    def getDir(self):
        return self.odict["s"]
             
            
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hs:", ["help", "debug", "local-only"] )
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

    if (len(args) > 0):
        usage()
        
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    if odict.has_key("local-only"):
        odict["local-only"] = True
        
    if not odict.has_key("s"):
        odict["s"] = Experiment.Experiment.srcimg_dir

    return odict, args



if __name__ == "__main__":
    main()