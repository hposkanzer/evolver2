#!/usr/bin/python

import os
import sys
import getopt
import random
import logging
import time

import ImageLoader
import TransformLoader
import Experiment
import SrcImage
import Thumbnailer
import Picklable


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--s3] [-s srcimg_dir] [-e examples_dir] [xform ...]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  -s:  Use this dir for source images.  Defaults to './srcimgs'.\n")
    sys.stderr.write( "  -e:  Use this dir for the output.  Defaults to './examples'.\n")
    sys.stderr.write( "  xform:  Only execute these transformers.\n")
    sys.exit(-1)


def main():
    
    Experiment.initLogging()
    (odict, args) = getOptions()
    eg = ExampleGenerator(odict, args)
    eg.generateExamples()
    
    
class ExampleGenerator(Picklable.Picklable):

    srcimgs = []
    xforms = []
    non_transformer = None
    
    def __init__(self, odict, xformNames=None):
        Picklable.Picklable.__init__(self)
        self.odict = odict
        self.xformNames = xformNames
        
        
    def generateExamples(self):
        t0 = time.time()
        self.logger.info("Generating filter examples...")
        self.config = self.loadConfig()
        self.tn = Thumbnailer.Thumbnailer(self.config["thumbnail_size"], not self.odict.get("s3", False))
        self.loadSrcImages()
        self.loadTransforms()
        sets = self.writeExamplePages()
        self.writeExampleIndex(sets)
        t1 = time.time()
        self.logger.info("Generation complete in %.2f seconds." % (t1-t0))
        
        
    def writeExamplePages(self):

        inputs = []
        for img in self.srcimgs:
            inputs.append(self.non_transformer(img))

        sets = []
        for xform_cls in self.xforms:
            
            if self.xformNames and xform_cls.__name__ not in self.xformNames:
                continue
            
            xform = xform_cls()
            ex = ExampleSet(self, xform)
            count = ex.writeImages(inputs)
            ex.writePages(count, inputs)
            sets.append((ex, count))
            
        return sets
            
            
    def writeExampleIndex(self, sets):
        
        fname = os.path.join(self.getDir(), "index.html")
        
        self.logger.debug("Writing example index...")
        
        cols = [  # (counts-up-through-here, get-this-many-columns)
                (5, 1000),
                (7, 3),
                (8, 4),
                (10, 3),
                (1000, 4),
                ]
        
        f = open(fname, "w")
        f.write("<html>\n<head><title>Filter Examples</title></head>\n<body>\n")
        f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../../index.html'>Photo Evolver 2</a> &gt; <a href='../index.html'>Experiment</a></font>\n")
        f.write("<center>\n<h2>Filter Examples</h2>\n" )
        f.write("<i>These are examples of the transformations that can be applied to the source images.  Each group below is a filter type, and each image is an example of what the filter can do with different parameters.</i><p>\n")
        for (ex, count) in sets:
            f.write("<a name='%s'>%s</a>\n" % (ex.getBaseName(), ex.getBaseName()))
            f.write("<table><tr>\n")
            for (x, columns) in cols:
                if (count <= x):
                    break
            for i in range(count):
                if not i % columns:
                    if i:
                        f.write("</tr>\n")
                    f.write("<tr>\n") 
                # Example thumbnails are always served from the base srcimg dir.
                url = self.tn.getURL(os.path.join(self.getDir(), ex.getThumbName(i)))
                f.write("<td><a href='%s'><img src='%s' border=1 width=%d height=%d></a></td>\n" % (ex.getPageName(i), url, self.config["thumb_width"], self.config["thumb_height"]))
            f.write("</tr>\n</table><p>\n")
        f.write("</center>\n")
        f.write("</body>\n</html>\n")
        f.close()

    
    def loadSrcImages(self):
        self.logger.debug("Loading source images...")
        il = ImageLoader.ImageLoader()
        for fpath in il.loadNames(self.odict["s"]):
            self.srcimgs.append(SrcImage.SrcImage(fpath))
        random.shuffle(self.srcimgs)

    def loadTransforms(self):
        self.logger.debug("Loading transformers...")
        xl = TransformLoader.TransformLoader()
        self.xforms = xl.loadAll(Experiment.Experiment.xforms_dir)
        self.xforms.sort(byName)
        self.non_transformer = xl.getNonTransformer()
        
        
    def getDir(self):
        return self.odict["e"]
    
    def getSrcDir(self):
        return self.odict["s"]


def byName(a, b):
    return cmp(a.__name__, b.__name__)


class ExampleSet(Picklable.Picklable):

    def __init__(self, generator, xform):
        Picklable.Picklable.__init__(self)
        self.generator = generator
        self.xform = xform
        self.tn = generator.tn
        
    def getBaseName(self):
        return self.xform.__class__.__name__
        
    def getDir(self):
        return self.generator.getDir()
    
    def getPageName(self, i):
        return "%s%02d.html" % (self.getBaseName(), i)

    def getImageName(self, i):
        return "%s%02d.jpg" % (self.getBaseName(), i)

    def getThumbName(self, i):
        return "%s%02d.t.jpg" % (self.getBaseName(), i) 


    def writeImages(self, inputs):
        self.logger.debug("Creating example images for %s..." % (self.getBaseName()))
        imgs = self.xform.getExamples(inputs)
        for i in range(len(imgs)):
            img = imgs[i]
            img.save(os.path.join(self.getDir(), self.getImageName(i)))
            self.tn.makeThumb(img, os.path.join(self.getDir(), self.getThumbName(i)))
        return len(imgs)
            

    def writePages(self, count, inputs):
        
        srcCount = self.xform.getExpectedInputCount()
        srcs = []
        for src in inputs[:srcCount]:
            srcs.append(self.getSourceThumb(src.getSrcImage()))
        srcs = "".join(srcs)
        
        for i in range(count):
            
            fname = os.path.join(self.getDir(), self.getPageName(i))
            
            if (i == 0):
                self.logger.debug("Creating example pages for %s..." % (self.getBaseName()))
            
            f = open(fname, "w")
            f.write("<html>\n<head><title>%s Example #%d</title></head>\n<body>\n" % (self.getBaseName(), i+1))
            f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../../index.html'>Photo Evolver 2</a> &gt; <a href='../index.html'>Experiment</a> &gt; <a href='index.html'>Filter Examples</a></font>\n")
            f.write("<center>\n<h2>%s Example #%d</h2>\n" % (self.getBaseName(), i+1))
            f.write("<table>\n")
            f.write("<tr valign='center'>\n")
            f.write("<td width='%d'>%s</td>\n" % (self.generator.config["thumbnail_size"], self.getExampleThumb(i-1, count)))
            f.write("<td><img src='%s' border=1 width=%d height=%d></td>\n" % (self.getImageName(i), self.generator.config["img_width"], self.generator.config["img_height"]))
            f.write("<td width='%d'>%s</td>\n" % (self.generator.config["thumbnail_size"], self.getExampleThumb(i+1, count)))
            f.write("</tr><tr>\n")
            f.write("<td colspan=3 align='center'>%s</td>\n" % (srcs))
            f.write("</table></center>\n")
            f.write("</body>\n</html>\n")
            f.close()
            
            
    def getSourceThumb(self, srcimg):
        src = self.tn.getURL(os.path.join(self.generator.getSrcDir(), srcimg.getThumbName()))
        return "<a href='../srcimgs/%s'><img src='%s' border=1 width=%d height=%d hspace=10></a>" % (srcimg.getPageName(), src, self.generator.config["thumb_width"], self.generator.config["thumb_height"])
    
        
    def getExampleThumb(self, i, count):
        if ((i < 0) or (i >= count)):
            return ""
        else:
            # Example thumbnails are always served from the base srcimg dir.
            url = self.tn.getURL(os.path.join(self.getDir(), self.getThumbName(i)))
            return "<a href='%s'><img src='%s' border=1 width=%d height=%d></a>" % (self.getPageName(i), url, self.generator.config["thumb_width"], self.generator.config["thumb_height"])

        
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "hs:", ["help", "debug", "s3"] )
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
        
    if not odict.has_key("s"):
        odict["s"] = Experiment.Experiment.srcimg_dir

    return odict, args



if __name__ == "__main__":
    main()