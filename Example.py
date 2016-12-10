import os
import Picklable
import glob
import Thumbnailer


class ExampleSet(Picklable.Picklable):

    def __init__(self, experiment, xform):
        Picklable.Picklable.__init__(self)
        self.experiment = experiment
        self.xform = xform
        self.img_glob = "%s??.jpg" % (self.getBaseName())
        
    def getBaseName(self):
        return self.xform.__class__.__name__
        
    def imageExists(self):
        # Check if at least one example image exists.
        return (self.getExampleCount() > 0)
    
    def getExampleCount(self):
        return len(glob.glob(os.path.join(self.getDir(), self.img_glob)))
        
    def getDir(self, abs=True):
        return self.experiment.getExamplesDir(abs)
    
    def getPageName(self, i):
        return "%s%02d.html" % (self.getBaseName(), i)

    def getImageName(self, i):
        return "%s%02d.jpg" % (self.getBaseName(), i)

    def getThumbName(self, i):
        return "%s%02d.t.jpg" % (self.getBaseName(), i) 


    def writeImages(self, inputs):
        if self.imageExists():
            return
        self.logger.debug("Creating example images for %s..." % (self.getBaseName()))
        imgs = self.xform.getExamples(inputs)
        for i in range(len(imgs)):
            img = imgs[i]
            img.save(os.path.join(self.getDir(), self.getImageName(i)))
            Thumbnailer.getInstance(self.experiment).makeThumb(img, os.path.join(self.getDir(), self.getThumbName(i)))


    def writePages(self):
        
        dims = self.experiment.getDims()
        
        # We're going to assume that all existing images are contiguously numbered.
        count = len(glob.glob(os.path.join(self.getDir(), self.img_glob)))
        for i in range(count):
            
            fname = os.path.join(self.getDir(), self.getPageName(i))
            if os.path.exists(fname):
                break
            
            if (i == 0):
                self.logger.debug("Creating example pages for %s..." % (self.getBaseName()))
            
            f = open(fname, "w")
            f.write("<html>\n<head><title>%s Example #%d</title></head>\n<body>\n" % (self.getBaseName(), i+1))
            f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../../index.html'>Photo Evolver 2</a> &gt; <a href='../index.html'>Experiment</a> &gt; <a href='index.html'>Filter Examples</a></font>\n")
            f.write("<center>\n<h2>%s Example #%d</h2>\n" % (self.getBaseName(), i+1))
            f.write("<table><tr valign='center'>\n")
            f.write("<td width='%d'>%s</td>\n" % (self.experiment.getConfig()["thumbnail_size"], self.getExampleThumb(i-1, count)))
            f.write("<td><img src='%s' border=1 width=%d height=%d></td>\n" % (self.getImageName(i), dims[0], dims[1]))
            f.write("<td width='%d'>%s</td>\n" % (self.experiment.getConfig()["thumbnail_size"], self.getExampleThumb(i+1, count)))
            f.write("</tr></table></center>\n")
            f.write("</body>\n</html>\n")
            f.close()
            
        return count
            
        
    def getExampleThumb(self, i, count):
        if ((i < 0) or (i >= count)):
            return ""
        else:
            fname = os.path.join(self.getDir(False), self.getThumbName(i))
            url = Thumbnailer.getInstance(self.experiment).getURL(fname)
            return "<a href='%s'><img src='%s' border=1></a>" % (self.getPageName(i), url)

        
    def __str__(self):
        return "%s examples" % (self.getBaseName())