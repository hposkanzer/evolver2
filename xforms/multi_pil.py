import math

import _xformer
from PIL import ImageChops
from PIL import ImageDraw
import random
from PIL import Image


#############################################################################
class _Combiner(_xformer._Transformer):
    
    def getExpectedInputCount(self):
        return 2

#############################################################################
#class PasteSection(_Combiner):
#    
#    max_tweak = 0.3
#    
#    def __init__(self):
#        _Combiner.__init__(self)
#        self.args["srcbox"] = []
#        self.args["dstbox"] = []
#        self.args["mask"] = random.randint(0, 255)
#
#    # We have to set our params here instead of __init__
#    # so we can know the size of the input image.    
#    def addInput(self, xform):
#        _Combiner.addInput(self, xform)
#        if not self.args["dstbox"]:
#            self.args["dstbox"] = self.getRandomBox()
#            self.args["srcbox"] = self.translateBox(self.args["dstbox"])
#            
#    def getArgsString(self):
#        return "(%s->%s, %s)" % (tuple(self.args["srcbox"]), tuple(self.args["dstbox"]), self.args["mask"])
#
#    def transformInner(self, imgs):
#        dst = imgs[0].copy()
#        srcbox = self.args["srcbox"]
#        dstbox = self.args["dstbox"]
#        size = self.boxToSize(srcbox)
#        src = imgs[1].crop(srcbox)
#        mask = Image.new("L", size, self.args["mask"])
#        dst.paste(src, dstbox, mask)
#        return dst
#
#    def tweakInner(self):
#        self.args["dstbox"] = self.tweakBox(self.args["dstbox"], self.max_tweak)
#        self.args["srcbox"] = self.translateBox(self.args["dstbox"])
#        self.args["mask"] = random.randint(0, 255)
#
#    def getExamplesInner(self, imgs):
#        exs = []
#        self.args["dstbox"] = [50, 50, 600, 300]
#        self.args["srcbox"] = self.translateBox(self.args["dstbox"])
#        for mask in [64, 128, 192]:
#            self.args["mask"] = mask
#            print "%s..." % (self)
#            exs.append(self.getExampleImage(imgs))
#        return exs

    
#############################################################################
class _StaticCombiner(_Combiner):    
    
    def getArgsString(self):
        return "(ON)"

    def tweakInner(self):
        pass

    def getExamplesInner(self, imgs):
        print "%s..." % (self)
        return [self.getExampleImage(imgs)]


class Lighter(_StaticCombiner):
    
    def transformInner(self, imgs):
        return apply(ImageChops.lighter, imgs)
    
class Darker(_StaticCombiner):
    
    def transformInner(self, imgs):
        return apply(ImageChops.darker, imgs)
    
class Multiply(_StaticCombiner):
    
    def transformInner(self, imgs):
        return apply(ImageChops.multiply, imgs)
    
class Difference(_StaticCombiner):
    
    def transformInner(self, imgs):
        return apply(ImageChops.difference, imgs)

class Screen(_StaticCombiner):
    
    def transformInner(self, imgs):
        return apply(ImageChops.screen, imgs)
    
    
#############################################################################
class Blend(_Combiner):
    
    def __init__(self):
        _Combiner.__init__(self)
        self.args["alpha"] = random.uniform(0.0, 1.0)

    def getArgsString(self):
        return "(%.2f)" % (self.args["alpha"])
    
    def transformInner(self, imgs):
        return ImageChops.blend(imgs[0], imgs[1], self.args["alpha"])
        
    def tweakInner(self):
        self.args["alpha"] = random.uniform(0.0, 1.0)
        
    def getExamplesInner(self, imgs):
        exs = []
        for alpha in [0.1, 0.5, 0.9]:
            self.args["alpha"] = alpha
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    
    
#############################################################################
class _AddSubtractChops(_Combiner):
    
    def __init__(self):
        _Combiner.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%.2f, %d)" % (self.args["scale"], self.args["offset"])

    def tweakInner(self):
        self.args["scale"] = random.uniform(0.3, 3.0)
        offsetRange = self.getOffsetRange(self.args["scale"])
        self.args["offset"] = random.randint(offsetRange[0], offsetRange[1])

    def getOffsetRange(self, scale):
        return [-64, 64]
    
    def getExamplesInner(self, imgs):
        exs = []
        for scale in [0.5, 1.0, 2.8]:
            self.args["scale"] = scale
            offsetRange = self.getOffsetRange(scale)
            for offset in [offsetRange[0], int(round(sum(offsetRange)/2.0)), offsetRange[1]]:
                self.args["offset"] = offset
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs


class Add(_AddSubtractChops):
    
    def getOffsetRange(self, scale):
        return [-64, int(round(128/2.7 * scale - 128.0/2.7*0.3 - 64))]
    
    def transformInner(self, imgs):
        return ImageChops.add(imgs[0], imgs[1], self.args["scale"], self.args["offset"])
    
class Subtract(_AddSubtractChops):
    
    def getOffsetRange(self, scale):
        return [int(round(128/2.7 * scale - 128.0/2.7*0.3 - 64)), 64]

    def transformInner(self, imgs):
        return ImageChops.subtract(imgs[0], imgs[1], self.args["scale"], self.args["offset"])


#############################################################################
class _NonCommutativeChops(_Combiner):
    
    def tweakInner(self):
        random.shuffle(self.inputs)

    def getExamplesInner(self, imgs):
        exs = []
        print "%s..." % (self)
        exs.append(self.getExampleImage(imgs))
        self.inputs.reverse()
        print "%s..." % (self)
        exs.append(self.getExampleImage(imgs))
        return exs
    

#############################################################################
class _TripleInput(_xformer._Transformer):
    
    def getExpectedInputCount(self):
        return 3

#############################################################################
class Composite(_TripleInput):

    modes = ["L", "RGB"]
    
    def __init__(self):
        _TripleInput.__init__(self)
        self.args["cutoff"] = random.randint(0, 255)
        self.args["mode"] = random.choice(self.modes)

    def getArgsString(self):
        return "(%s, %d)" % (self.args["mode"], self.args["cutoff"])

    def transformInner(self, imgs):
        mask = imgs[2].convert(self.args["mode"]).point(self.transformFunc).convert("L")
        return ImageChops.composite(imgs[0], imgs[1], mask)
    
    def transformFunc(self, x):
        return (x+self.args["cutoff"])/255*255

    def tweakInner(self):
        self.args["cutoff"] = random.randint(0, 255)
        self.args["mode"] = random.choice(self.modes)

    def getExamplesInner(self, imgs):
        exs = []
        for mode in self.modes:
            for cutoff in [30, 127, 225]:
                self.args["mode"] = mode
                self.args["cutoff"] = cutoff
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs
    

#############################################################################
class Merge(_TripleInput):

    orders = [
              (0, 1, 2),
              (0, 2, 1),
              (1, 0, 2),
              (1, 2, 0),
              (2, 0, 1),
              (2, 1, 0),
              ]
    
    def __init__(self):
        _TripleInput.__init__(self)
        self.args["order"] = random.choice(self.orders)

    def getArgsString(self):
        l = [""] * 3
        for i in range(len(self.args["order"])):
            j = self.args["order"][i]
            l[j] = "RGB"[i]
        return "(%s%s%s)" % tuple(l)

    def transformInner(self, imgs):
        channels = []
        for i in self.args["order"]:
            channels.append(imgs[i].convert("L"))
        return Image.merge("RGB", channels)
    
    def tweakInner(self):
        self.args["order"] = random.choice(self.orders)

    def getExamplesInner(self, imgs):
        exs = []
        for order in self.orders:
            self.args["order"] = order
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    

#############################################################################
#class PasteSectionMask(_TripleInput):
#    
#    max_tweak = 0.3
#    
#    def __init__(self):
#        _TripleInput.__init__(self)
#        self.args["srcbox"] = []
#        self.args["dstbox"] = []
#        self.args["maskbox"] = []
#
#    # We have to set our params here instead of __init__
#    # so we can know the size of the input image.    
#    def addInput(self, xform):
#        _TripleInput.addInput(self, xform)
#        if not self.args["dstbox"]:
#            self.args["dstbox"] = self.getRandomBox()
#            self.args["srcbox"] = self.translateBox(self.args["dstbox"])
#            self.args["maskbox"] = self.translateBox(self.args["dstbox"])
#
#    def getArgsString(self):
#        return "(%s->%s, %s)" % (tuple(self.args["srcbox"]), tuple(self.args["dstbox"]), tuple(self.args["maskbox"]))
#
#    def transformInner(self, imgs):
#        dst = imgs[0].copy()
#        srcbox = self.args["srcbox"]
#        dstbox = self.args["dstbox"]
#        maskbox = self.args["maskbox"]
#        size = self.boxToSize(srcbox)
#        src = imgs[1].crop(srcbox)
#        mask = imgs[2].crop(maskbox).convert("L")
#        dst.paste(src, dstbox, mask)
#        return dst
#
#    def tweakInner(self):
#        self.args["dstbox"] = self.tweakBox(self.args["dstbox"], self.max_tweak)
#        self.args["srcbox"] = self.translateBox(self.args["dstbox"])
#        self.args["maskbox"] = self.translateBox(self.args["dstbox"])
#        
#    def getExamplesInner(self, imgs):
#        exs = []
#        self.args["dstbox"] = [50, 50, 600, 300]
#        for i in range(3):
#            self.args["srcbox"] = self.translateBox(self.args["dstbox"])
#            self.args["maskbox"] = self.translateBox(self.args["dstbox"])
#            print "%s..." % (self)
#            exs.append(self.getExampleImage(imgs))
#        return exs


############################################################################
class PasteMask(_TripleInput):
    
    modes = ["1", "L"]
    
    def __init__(self):
        _TripleInput.__init__(self)
        self.args["mode"] = random.choice(self.modes)

    def getArgsString(self):
        return "(%s)" % (self.args["mode"])

    def transformInner(self, imgs):
        dst = imgs[0].copy()
        src = imgs[1]
        mask = imgs[2].convert(self.args["mode"])
        dst.paste(src, (0, 0), mask)
        return dst

    def tweakInner(self):
        self.args["mode"] = random.choice(self.modes)

    def getExamplesInner(self, imgs):
        exs = []
        for mode in self.modes:
            self.args["mode"] = mode
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    

#############################################################################
class _QuadrupleInput(_xformer._Transformer):
    
    def getExpectedInputCount(self):
        return 4


#############################################################################
class MergeCMYK(_QuadrupleInput):

    orders = [(0, 1, 2, 3), 
              (0, 1, 3, 2), 
              (0, 2, 1, 3), 
              (0, 2, 3, 1), 
              (0, 3, 1, 2), 
              (0, 3, 2, 1), 
              (1, 0, 2, 3), 
              (1, 0, 3, 2), 
              (1, 2, 0, 3), 
              (1, 2, 3, 0), 
              (1, 3, 0, 2), 
              (1, 3, 2, 0), 
              (2, 0, 1, 3), 
              (2, 0, 3, 1), 
              (2, 1, 0, 3), 
              (2, 1, 3, 0), 
              (2, 3, 0, 1), 
              (2, 3, 1, 0), 
              (3, 0, 1, 2), 
              (3, 0, 2, 1), 
              (3, 1, 0, 2), 
              (3, 1, 2, 0), 
              (3, 2, 0, 1), 
              (3, 2, 1, 0)]
    
    def __init__(self):
        _QuadrupleInput.__init__(self)
        self.args["order"] = random.choice(self.orders)

    def getArgsString(self):
        l = [""] * 4
        for i in range(len(self.args["order"])):
            j = self.args["order"][i]
            l[j] = "CMYK"[i]
        return "(%s%s%s%s)" % tuple(l)

    def transformInner(self, imgs):
        channels = []
        for i in self.args["order"]:
            channels.append(imgs[i].convert("L"))
        return Image.merge("CMYK", channels).convert("RGB")
    
    def tweakInner(self):
        self.args["order"] = random.choice(self.orders)

    def getExamplesInner(self, imgs):
        exs = []
        for order in self.orders:
            self.args["order"] = order
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    


#############################################################################
class BentleyMerge(_Combiner):    
    
    debug = False
    
    def __init__(self):
        _Combiner.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%.2f, %.2f)" % (self.args["sigma"], self.args["angle"])

    def transformInner(self, imgs):
        ret = imgs[0].copy()
        dims = self.getDims()
        rload = ret.load()
        img0 = imgs[0]
        if self.debug:
            img0 = img0.copy()
            draw = ImageDraw.Draw(img0)
            for i in xrange(0, dims[0], 10):
                draw.line((i,0,i,dims[1]), (255,0,0))
            for i in xrange(0, dims[1], 10):
                draw.line((0,i,dims[0],i), (255,0,0))
        iload0 = img0.load()
        iload1 = imgs[1].load()
        sigma = self.args["sigma"]
        angle = self.args["angle"]
        for x in xrange(0, dims[0]):
            for y in xrange(0, dims[1]):
                m = round(sum(iload1[x,y])/765.0 * sigma)
                mx = int(math.floor(math.cos(angle) * m))
                my = int(math.floor(math.sin(angle) * m))
                rload[x,y] = iload0[(x+mx)%dims[0], (y+my)%dims[1]]
        return ret

    def tweakInner(self):
        self.args["sigma"] = random.uniform(10, 200)
        self.args["angle"] = random.uniform(0, _xformer.TWOPI)

    def getExamplesInner(self, imgs):
        exs = []
        for a in (0.0, math.pi/2):
            for s in (10, 200):
                self.args["sigma"] = s
                self.args["angle"] = a
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs
    
    

#############################################################################
class Strips(_Combiner):    
    
    dirs = ["H", "V"]
    
    def __init__(self):
        _Combiner.__init__(self)

    def addInput(self, xform):
        _Combiner.addInput(self, xform)
        self.tweakInner()

    def getArgsString(self):
        return "(%d, %s)" % (self.args["rows"], self.args["dir"])

    def transformInner(self, imgs):
        ret = imgs[0].copy()
        dims = self.getDims()
        rows = self.args["rows"]
        if self.args["dir"] == "H":
            for i in range(0, dims[1], rows*2):
                coords = (0,i,dims[0],i+rows)
                ret.paste(imgs[1].crop(coords), coords)
        else:
            for i in range(0, dims[0], rows*2):
                coords = (i,0,i+rows,dims[1])
                ret.paste(imgs[1].crop(coords), coords)
        return ret

    def tweakInner(self):
        self.args["dir"] = random.choice(self.dirs)
        self.args["rows"] = random.randint(1, self.getMaxRows())

    def getMaxRows(self):
        if self.args["dir"] == "H":
            maxRows = self.getDims()[1]
        else:
            maxRows = self.getDims()[0]
        return int(round(maxRows/4.0))
    
    def getExamplesInner(self, imgs):
        exs = []
        for d in self.dirs:
            self.args["dir"] = d
            for r in (1, 10, self.getMaxRows()):
                self.args["rows"] = r
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs    