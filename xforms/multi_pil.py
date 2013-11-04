'''
Created on Aug 12, 2010

@author: hmp@drzeus.best.vwh.net
'''
import _xformer
import ImageChops
import random
import Image


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
        self.args["scale"] = random.uniform(0.3, 3.0)
        self.args["offset"] = random.randint(-64, 64)

    def getArgsString(self):
        return "(%.2f, %d)" % (self.args["scale"], self.args["offset"])

    def tweakInner(self):
        self.args["scale"] = random.uniform(0.3, 3.0)
        self.args["offset"] = random.randint(-64, 64)

    def getExamplesInner(self, imgs):
        exs = []
        for scale in [0.3, 1.0, 3.0]:
            for offset in [-64, 0, 64]:
                self.args["scale"] = scale
                self.args["offset"] = offset
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs


class Add(_AddSubtractChops):
    
    def transformInner(self, imgs):
        return ImageChops.add(imgs[0], imgs[1], self.args["scale"], self.args["offset"])
    
class Subtract(_AddSubtractChops):
    
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
    

