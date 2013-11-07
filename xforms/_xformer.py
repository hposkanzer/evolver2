'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import Picklable
import random
import copy
import ImageDraw
import ImageFont
import os
import string
import sha  # Server runs on Python 2.4.

import Image

# It takes up a lot of disk space and doesn't improve performance that much.
# It would allow me to show the product of every step of the transformation, though.
cachingEnabled = False


class _Transformer(Picklable.Picklable):
    
    is_non_transformer = 0
    is_reserved_transformer = 0
    
    def __init__(self):
        Picklable.Picklable.__init__(self)
        self.inputs = []
        self.args = {}
        self.dims = (800, 600) # Hardcoding this for now.
        self.resetCache()
    
    def __str__(self):
        return self.__class__.__name__ + self.getArgsString()
    
    def getArgsString(self):
        return "()"
    
    def getLoggerName(self):
        return "Transformer"

    def setDebug(self, debug):
        self.debug = debug
        
    def resetCache(self):
        self.genome = None
        self.digest = ""
        self.width = -1
        self.depth = -1

        
    def getGenome(self):
        if not self.genome:
            self.genome = {"class" : str(self.__class__),
                           "args" : self.args,
                           "inputs" : self.getInputGenomes()}
        return self.genome
        
    def getInputGenomes(self):
        gg = []
        for input in self.inputs:
            gg.append(input.getGenome())
        return gg
    
    
    def getDigest(self):
        if not self.digest:
            h = sha.new()
            h.update(self.getDigestInput())
            self.digest = h.hexdigest()
        return self.digest
    
    def getDigestInput(self):
        return str(self.getGenome())
    
    
    def getWidth(self):
        if (self.width < 0):
            self.width = 0
            for input in self.inputs:
                self.width = self.width + input.getWidth()
        return self.width
    
    def getDepth(self):
        if (self.depth < 0):
            idepth = 0
            for input in self.inputs:
                idepth = max(idepth, input.getDepth())
            self.depth = idepth + 1
        return self.depth
        
    

    def toString(self, i=0):
        l = []
        l.append("  " * i + "%d: %s (%s)" % (i, self, self.getDigest()))
        for input in self.inputs:
            l.append(input.toString(i+1))
        return string.join(l, "\n")
    

    #########################################################################
    # Call transform on the inputs, perform a transformation on the result, return an Image.
    def transform(self, experiment):
        # Do we have this image cached?
        img = self.getCachedImage(experiment)
        if not img:
            imgs = self.transformInputs(experiment)
            self.logger.debug("%s..." % (self))
            img = self.transformInner(imgs)
            self.cacheImage(experiment, img)
            self.saveThumbnail(experiment, img)
        return img
    
    def transformInputs(self, experiment):
        imgs = []
        for input in self.inputs:
            imgs.append(input.transform(experiment))
        return imgs

    def transformInner(self, imgs):
        raise NotImplementedError
    

    def getCachePath(self, experiment):
        return os.path.join(experiment.getCreaturesDir(), "%s.jpg" % (self.getDigest()))
    
    def getThumbPath(self, experiment):
        return os.path.join(experiment.getCreaturesDir(), self.getThumbName())
    
    def getThumbName(self):
        return "%s.t.jpg" % (self.getDigest())

    
    def getCachedImage(self, experiment):
        if not cachingEnabled:
            return None
        fpath = self.getCachePath(experiment)
        if os.path.exists(fpath):
            self.logger.debug("Cache hit on %s (%s)." % (self, self.getDigest()))
            return Image.open(fpath)
        else:
            self.logger.debug("Cache miss on %s (%s)." % (self, self.getDigest()))
            return None
        
    def cacheImage(self, experiment, img):
        if cachingEnabled:
            fpath = self.getCachePath(experiment)
            img.save(fpath)
            
            
    def saveThumbnail(self, experiment, img):
        fname = self.getThumbPath(experiment)
        if os.path.exists(fname):
            self.logger.debug("Thumbnail for %s (%s) already exists." % (self, self.getDigest()))
        else:
            self.logger.debug("Saving thumbnail for %s (%s)..." % (self, self.getDigest()))
            experiment.tn.makeThumb(img, fname)
        
            
    #########################################################################
    def getExamples(self, inputs):
        
        # Set all the inputs we need.
        # All of the inputs should be NonTransformers at this point.
        for j in range(self.getExpectedInputCount()):
            self.addInput(inputs[j])
        
        # Get the images from our inputs.
        imgs = []
        for input in self.inputs:
            imgs.append(input.getImage())

        return self.getExamplesInner(imgs)
    

    def getExamplesInner(self, imgs):
        raise NotImplementedError
    
    def getExampleImage(self, imgs):
        img = self.transformInner(imgs)
        # Now put a label on it.
        draw = ImageDraw.Draw(img)
        font = ImageFont.load(os.path.join("fonts", "courB12.pil"))
        text = str(self)
        (w,h) = draw.textsize(text, font)
        draw.rectangle((0,0,w+10,h+10), (255,255,255))
        draw.text((5, 5), text, font=font, fill=(0,0,0))
        return img
    
    
    #########################################################################
    def clone(self):
        new = self.__class__()
        for input in self.inputs:
            new.inputs.append(input.clone())
        new.args = copy.deepcopy(self.args)
        return new

    
    # Tweak the parameters of this and all inputs.
    def tweak(self, tweak_rate):
        self.tweakInputs(tweak_rate)
        if (random.random() <= tweak_rate):
            old = str(self)
            self.tweakInner()
            new = str(self)
            self.logger.debug("%s -> %s" % (old, new))
        else:
            self.logger.debug("%s did not tweak." % (self))
        self.resetCache()
    
    def tweakInputs(self, tweak_rate):
        for input in self.inputs:
            input.tweak(tweak_rate)

    def tweakInner(self):
        raise NotImplementedError

    
    #########################################################################
    # Get the number of expected inputs to this transformer.
    def getExpectedInputCount(self):
        raise NotImplementedError

    def getInputCount(self):
        return len(self.inputs)
    
    def getInputs(self):
        return copy.copy(self.inputs)
            
    def setInputs(self, xforms):
        self.inputs = []
        for xform in xforms:
            self.addInput(xform)
        
    def addInput(self, xform):
        self.inputs.append(xform)
        self.resetCache()
        
    def getDims(self):
        if not self.dims:
            # We assume all images are the same size for now.
            self.dims = self.inputs[0].getDims()
        return self.dims

        
    #########################################################################
    def getPairs(self, prev=None):
        l = []
        l.append((prev, self))
        for input in self.inputs:
            l.extend(input.getPairs(self))
        return l
        
        
    #########################################################################
    # Common, useful utilties.
    def getRandomColor(self):
        l = []
        for i in range(3):
            l.append("%02x" % (random.randint(0, 255)))
        return string.upper("#%s" % ("".join(l)))


    def swapInputs(self, i, j):
        x = self.inputs[i]
        self.inputs[i] = self.inputs[j]
        self.inputs[j] = x


    def boxToSize(self, box):
        return (box[2] - box[0], box[3] - box[1])


    def getRandomBox(self):
        dims = self.getDims()
        box = [0] * 4
        box[0] = random.randint(0, dims[0])
        box[1] = random.randint(0, dims[1])
        box[2] = random.randint(box[0], dims[0])
        box[3] = random.randint(box[1], dims[1])
        return box
        
    def tweakBox(self, box, max_tweak):
        dims = self.getDims()
        max_changes = map(int, map(round, [dims[0] * self.max_tweak, dims[1] * self.max_tweak]))
        box[0] = self.newBoundary(box[0], max_changes[0], 0, dims[0])
        box[1] = self.newBoundary(box[1], max_changes[1], 0, dims[1])
        box[2] = self.newBoundary(box[2], max_changes[0], box[0], dims[0])
        box[3] = self.newBoundary(box[3], max_changes[1], box[1], dims[1])
        return box
    
    
    def getRandomQuad(self, constrain=False):
        dims = self.getDims()
        box = [0] * 8
        if constrain:
            box[0] = random.randint(0, dims[0]/2)
            box[1] = random.randint(0, dims[1]/2)
            box[2] = random.randint(0, dims[0]/2)
            box[3] = random.randint(dims[1]/2, dims[1])
            box[4] = random.randint(dims[0]/2, dims[0])
            box[5] = random.randint(dims[1]/2, dims[1])
            box[6] = random.randint(dims[0]/2, dims[0])
            box[7] = random.randint(0, dims[1]/2)
        else:
            box[0] = random.randint(0, dims[0])
            box[1] = random.randint(0, dims[1])
            box[2] = random.randint(0, dims[0])
            box[3] = random.randint(0, dims[1])
            box[4] = random.randint(0, dims[0])
            box[5] = random.randint(0, dims[1])
            box[6] = random.randint(0, dims[0])
            box[7] = random.randint(0, dims[1])
        return box
        
    def tweakQuad(self, quad, max_tweak):
        dims = self.getDims()
        max_changes = map(int, map(round, [dims[0] * self.max_tweak, dims[1] * self.max_tweak]))
        quad[0] = self.newBoundary(quad[0], max_changes[0], 0, dims[0])
        quad[1] = self.newBoundary(quad[1], max_changes[1], 0, dims[1])
        quad[2] = self.newBoundary(quad[2], max_changes[0], 0, dims[0])
        quad[3] = self.newBoundary(quad[3], max_changes[1], 0, dims[1])
        quad[4] = self.newBoundary(quad[4], max_changes[0], 0, dims[0])
        quad[5] = self.newBoundary(quad[5], max_changes[1], 0, dims[1])
        quad[6] = self.newBoundary(quad[6], max_changes[0], 0, dims[0])
        quad[7] = self.newBoundary(quad[7], max_changes[1], 0, dims[1])
        return quad
    
    
    def newBoundary(self, boundary, max_change, min_boundary, max_boundary):
        min_boundary = max(boundary - max_change, min_boundary)
        max_boundary = min(boundary + max_change, max_boundary)
        return int(round(random.uniform(min_boundary, max_boundary)))
    
    
    def translateBox(self, box):
        dims = self.getDims()
        size = self.boxToSize(box)
        x = random.randint(0, dims[0] - size[0])
        y = random.randint(0, dims[1] - size[1])
        return (x, y, x + size[0], y + size[1])
    
        
# A transformer that takes a single transformer as input.
class _MonoTransformer(_Transformer):
    
    def getExpectedInputCount(self):
        return 1
    
    def transformInner(self, imgs):
        return self.transformImage(imgs[0])

    def transformImage(self, img):
        raise NotImplementedError
    
        
