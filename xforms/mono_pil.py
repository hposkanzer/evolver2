'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import string
import math
import _xformer
import Image
import ImageFilter
import random
import ImageOps
import ImageEnhance
import ImageChops
import ImageDraw


#############################################################################
class Transpose(_xformer._MonoTransformer):
    
    methods = [Image.FLIP_LEFT_RIGHT, Image.FLIP_TOP_BOTTOM, Image.ROTATE_180]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["method"] = random.choice(self.methods)

    def getArgsString(self):
        return "(%s)" % (self.args["method"])

    def transformImage(self, img):
        return img.transpose(self.args["method"])
    
    def tweakInner(self):
        self.args["method"] = random.choice(self.methods)
        
    def getExamplesInner(self, imgs):
        exs = []
        for method in self.methods:
            self.args["method"] = method
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Colorize(_xformer._MonoTransformer):
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["black"] = self.getRandomColor()
        self.args["white"] = self.getRandomColor()

    def getArgsString(self):
        return "(%s, %s)" % (self.args["black"], self.args["white"])

    def transformImage(self, img):
        return ImageOps.colorize(ImageOps.grayscale(img), self.args["black"], self.args["white"])
    
    def tweakInner(self):
        self.args["black"] = self.getRandomColor()
        self.args["white"] = self.getRandomColor()
        
    def getExamplesInner(self, imgs):
        exs = []
        for i in range(3):
            self.tweakInner()
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    

#############################################################################
class ColorSwap(_xformer._MonoTransformer):
    
    orders = [
              (0, 1, 2),
              (0, 2, 1),
              (1, 0, 2),
              (1, 2, 0),
              (2, 0, 1),
              (2, 1, 0),
              ]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["order"] = random.choice(self.orders)

    def getArgsString(self):
        l = [""] * 3
        for i in range(len(self.args["order"])):
            j = self.args["order"][i]
            l[j] = "RGB"[i]
        return "(%s%s%s)" % tuple(l)

    def transformImage(self, img):
        rgb = img.split()
        channels = []
        for i in self.args["order"]:
            channels.append(rgb[i])
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
class Rotate(_xformer._MonoTransformer):
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["angle"] = random.randint(0, 360)

    def getArgsString(self):
        return "(%s)" % (self.args["angle"])

    def transformImage(self, img):
        img = img.rotate(self.args["angle"], Image.BILINEAR, 1)
        # We now want to zoom in on the largest rectangle fully within the rotated image.
        # The math here is way too hard.  We're just going to approximate it.
        s = abs(math.sin(self.args["angle"]/360.0 * 2 * math.pi))
        c = abs(math.cos(self.args["angle"]/360.0 * 2 * math.pi))
        (ow, oh) = self.getDims()
        w = ow - ((ow-oh) * s) - ((ow-oh) * s * c * 2)
        h = float(oh)/ow * w
        coords = map(int, ((img.size[0]-w)/2, (img.size[1]-h)/2, (img.size[0]+w)/2, (img.size[1]+h)/2))
        return img.crop(coords).resize(self.getDims(), Image.BILINEAR)
    
    def tweakInner(self):
        self.args["angle"] = random.randint(0, 360)
        
    def getExamplesInner(self, imgs):
        exs = []
        for angle in range(0, 360, 30):
            self.args["angle"] = angle
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class _BuiltInDegreeFilter(_xformer._MonoTransformer):
    
    filters = []
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["filter"] = random.choice(self.filters)

    def getArgsString(self):
        return "(%s)" % (str(self.args["filter"]).split(".")[-1])

    def transformImage(self, img):
        return img.filter(self.args["filter"])
    
    def tweakInner(self):
        self.args["filter"] = random.choice(self.filters)

    def getExamplesInner(self, imgs):
        exs = []
        for filter in self.filters:
            self.args["filter"] = filter
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs

    
class EmbossFilter(_BuiltInDegreeFilter):
    filters = [
               ImageFilter.CONTOUR, 
               ImageFilter.EMBOSS, 
               ImageFilter.FIND_EDGES,
               ]
    
class SharpenFilter(_BuiltInDegreeFilter):
    filters = [
               ImageFilter.SHARPEN,
               ImageFilter.DETAIL,
               ImageFilter.EDGE_ENHANCE,
               ImageFilter.EDGE_ENHANCE_MORE,
               ]
    
class BlurFilter(_BuiltInDegreeFilter):
    filters = [
               ImageFilter.BLUR,
               ImageFilter.SMOOTH,
               ImageFilter.SMOOTH_MORE,
               ]


#############################################################################
class _StatsFilter(_xformer._MonoTransformer):
    
    sizes = [3, 5, 7, 9, 11]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["size"] = random.choice(self.sizes)

    def getArgsString(self):
        return "(%dx%d)" % (self.args["size"], self.args["size"])

    def transformImage(self, img):
        return img.filter(self.filter_class(self.args["size"]))
    
    def tweakInner(self):
        self.args["size"] = random.choice(self.sizes)

    def getExamplesInner(self, imgs):
        exs = []
        for size in [3, 7, 11]:
            self.args["size"] = size
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


class MinFilter(_StatsFilter):  filter_class = ImageFilter.MinFilter
class MedianFilter(_StatsFilter):  filter_class = ImageFilter.MedianFilter
class MaxFilter(_StatsFilter):  filter_class = ImageFilter.MaxFilter
class ModeFilter(_StatsFilter):  filter_class = ImageFilter.ModeFilter


class RankFilter(_StatsFilter):
    
    def __init__(self):
        _StatsFilter.__init__(self)
        self.args["rank"] = random.randint(0, (self.args["size"]*self.args["size"])-1)

    def getArgsString(self):
        return "(%dx%d, %d)" % (self.args["size"], self.args["size"], self.args["rank"])

    def transformImage(self, img):
        return img.filter(ImageFilter.RankFilter(self.args["size"], self.args["rank"]))
    
    def tweakInner(self):
        _StatsFilter.tweakInner(self)
        self.args["rank"] = random.randint(0, (self.args["size"]*self.args["size"])-1)

    def getExamplesInner(self, imgs):
        exs = []
        for size in [3, 7, 11]:
            for rank in range(1, size*size, size*size/3):
                self.args["size"] = size
                self.args["rank"] = rank
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Zoom(_xformer._MonoTransformer):
    
    max_tweak = 0.3
    filters = [
               Image.NEAREST, 
               Image.BILINEAR, 
               Image.BICUBIC,
               Image.ANTIALIAS,
               ]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["box"] = []
        self.args["filter"] = random.choice(self.filters)

    # We have to set our params here instead of __init__
    # so we can know the size of the input image.    
    def addInput(self, xform):
        _xformer._MonoTransformer.addInput(self, xform)
        self.args["box"] = self.getRandomBox()

    def getArgsString(self):
        return "(%s, %s)" % (tuple(self.args["box"]), self.args["filter"])

    def transformImage(self, img):
        return img.crop(tuple(self.args["box"])).resize(self.getDims(), self.args["filter"])

    def tweakInner(self):
        self.args["box"] = self.tweakBox(self.args["box"], self.max_tweak)
        self.args["filter"] = random.choice(self.filters)

    def getExamplesInner(self, imgs):
        exs = []
        for filter in self.filters:
            self.args["filter"] = filter
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Shift(_xformer._MonoTransformer):
    
    max_tweak = 0.3
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["xshift"] = 0
        self.args["yshift"] = 0

    # We have to set our params here instead of __init__
    # so we can know the size of the input image.    
    def addInput(self, xform):
        _xformer._MonoTransformer.addInput(self, xform)
        self.args["xshift"] = random.randint(0, self.getDims()[0])
        self.args["yshift"] = random.randint(0, self.getDims()[1])

    def getArgsString(self):
        return "(%s, %s)" % (self.args["xshift"], self.args["yshift"])

    def transformImage(self, img):
        return ImageChops.offset(img, self.args["xshift"], self.args["yshift"])

    def tweakInner(self):
        max_x = self.getDims()[0] * self.max_tweak / 2
        max_y = self.getDims()[1] * self.max_tweak / 2
        self.args["xshift"] = random.randint(self.args["xshift"] - max_x, self.args["xshift"] + max_x) % self.getDims()[0]
        self.args["yshift"] = random.randint(self.args["yshift"] - max_y, self.args["yshift"] + max_y) % self.getDims()[1]

    def getExamplesInner(self, imgs):
        exs = []
        self.args["xshift"] = self.getDims()[0] / 3
        self.args["yshift"] = self.getDims()[1] / 3
        print "%s..." % (self)
        exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Reflect(_xformer._MonoTransformer):
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["box"] = []

    # We have to set our params here instead of __init__
    # so we can know the size of the input image.    
    def addInput(self, xform):
        _xformer._MonoTransformer.addInput(self, xform)
        self.args["box"] = self.getBox()

    def getArgsString(self):
        return str(tuple(self.args["box"]))

    def transformImage(self, img):
        ret = img.copy()
        dims = self.getDims()
        small = img.crop(tuple(self.args["box"]))
        ret.paste(small, (0, 0))  # In-place edit!
        small = small.transpose(Image.FLIP_LEFT_RIGHT)
        ret.paste(small, (dims[0]/2, 0))  # In-place edit!
        small = small.transpose(Image.FLIP_TOP_BOTTOM)
        ret.paste(small, (dims[0]/2, dims[1]/2))  # In-place edit!
        small = small.transpose(Image.FLIP_LEFT_RIGHT)
        ret.paste(small, (0, dims[1]/2))  # In-place edit!
        return ret
    
    def tweakInner(self):
        self.args["box"] = self.getBox()

    def getBox(self):
        dims = self.getDims()
        box = [0] * 4
        box[0] = random.randint(0, dims[0]/2)
        box[1] = random.randint(0, dims[1]/2)
        box[2] = box[0] + dims[0]/2
        box[3] = box[1] + dims[1]/2
        return box

    def getExamplesInner(self, imgs):
        exs = []
        for i in range(1):
            self.tweakInner()
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Mirror(_xformer._MonoTransformer):
    
    portions = [
            "L",
            "R",
            "T",
            "B",
            ]
    modes = [
             "FLIP",
             "ROTATE",
             ]
    dests = [
             "BEFORE",
             "AFTER",
             ]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["portion"] = random.choice(self.portions)
        self.args["mode"] = random.choice(self.modes)
        self.args["dest"] = random.choice(self.dests)

    def getArgsString(self):
        return "(%s, %s, %s)" % (self.args["portion"], self.args["mode"], self.args["dest"])


    def transformImage(self, img):

        portion = self.args["portion"]
        mode = self.args["mode"]
        dest = self.args["dest"]
        dims = self.getDims()
       
        if (portion == "L"):
            box = (0, 0, dims[0]/2, dims[1])
            flip = Image.FLIP_LEFT_RIGHT
        elif (portion == "R"):
            box = (dims[0]/2, 0, dims[0], dims[1])
            flip = Image.FLIP_LEFT_RIGHT
        elif (portion == "T"):
            box = (0, 0, dims[0], dims[1]/2)
            flip = Image.FLIP_TOP_BOTTOM
        else: # "B"
            box = (0, dims[1]/2, dims[0], dims[1])
            flip = Image.FLIP_TOP_BOTTOM
        
        snip = img.crop(box)
        
        if (mode == "FLIP"):
            snip = snip.transpose(flip)
        else: # "ROTATE"
            snip = snip.transpose(Image.ROTATE_180)  
            
        if (dest == "BEFORE"):
            location = (0, 0)
            if (portion == "L"):
                offset = (dims[0]/2, 0)
            elif (portion == "T"):
                offset = (0, dims[1]/2)
            else: # "R", "B"
                offset = (0, 0)
        else: # "AFTER"
            if (portion == "L"):
                offset = (0, 0)
                location = (dims[0]/2, 0)
            elif (portion == "R"):
                offset = (dims[0]/2, 0)
                location = (dims[0]/2, 0)
            elif (portion == "T"):
                offset = (0, 0)
                location = (0, dims[1]/2)
            else: # "B"
                offset = (0, dims[1]/2)
                location = (0, dims[1]/2)
        
        img = ImageChops.offset(img, offset[0], offset[1])
        img.paste(snip, location)  # In-place edit!

        return img


    def tweakInner(self):
        self.args["portion"] = random.choice(self.portions)
        self.args["mode"] = random.choice(self.modes)
        self.args["dest"] = random.choice(self.dests)
        
    def getExamplesInner(self, imgs):
        exs = []
        for portion in self.portions:
            for mode in self.modes:
                for dest in self.dests:
                    self.args["portion"] = portion
                    self.args["mode"] = mode
                    self.args["dest"] = dest
                    print "%s..." % (self)
                    exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class AutoContrast(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["cutoff"] = random.randint(0, 40)

    def getArgsString(self):
        return "(%d)" % (self.args["cutoff"])

    def transformImage(self, img):
        return ImageOps.autocontrast(img, self.args["cutoff"])
    
    def tweakInner(self):
        self.args["cutoff"] = random.randint(0, 40)

    def getExamplesInner(self, imgs):
        exs = []
        for cutoff in [0, 20, 40]:
            self.args["cutoff"] = cutoff
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Threshold(_xformer._MonoTransformer):
    
    modes = ["L", "RGB"]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["cutoff"] = random.randint(0, 255)
        self.args["mode"] = random.choice(self.modes)

    def getArgsString(self):
        return "(%s, %d)" % (self.args["mode"], self.args["cutoff"])

    def transformImage(self, img):
        return img.convert(self.args["mode"]).point(self.transformFunc).convert("RGB")
    
    def transformFunc(self, x):
        return (x+self.args["cutoff"])/255*255
    
    def tweakInner(self):
        self.args["cutoff"] = random.randint(0, 255)
        self.args["mode"] = random.choice(self.modes)

    def getExamplesInner(self, imgs):
        exs = []
        for mode in self.modes:
            for cutoff in [30, 127, 225]:
                self.args["cutoff"] = cutoff
                self.args["mode"] = mode
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class Modulo(_xformer._MonoTransformer):
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["quants"] = random.randint(63, 213)

    def getArgsString(self):
        return "(%d)" % (self.args["quants"])

    def transformImage(self, img):
        return img.point(self.transformFunc).convert("RGB")
    
    def transformFunc(self, x):
        div = 255 / self.args["quants"]
        return (x % self.args["quants"]) * div
    
    def tweakInner(self):
        self.args["quants"] = random.randint(63, 213)

    def getExamplesInner(self, imgs):
        exs = []
        for quant in [63, 127, 181]:
            self.args["quants"] = quant
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class _OnOffTransformer(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["toggle"] = random.choice([True, False])

    def getArgsString(self):
        if self.args["toggle"]:
            return "(ON)"
        else:
            return "(OFF)"
        
    def getDigestInput(self):
        if self.args["toggle"]:
            return str(self.getGenome())
        else:
            return self.inputs[0].getDigestInput()


    def transformImage(self, img):
        if (self.args["toggle"]):
            return self.doTransform(img)
        else:
            return img
        
    def doTransform(self, img):
        raise NotImplementedError
            
    def tweakInner(self):
        self.args["toggle"] = random.choice([True, False])

    def getExamplesInner(self, imgs):
        self.args["toggle"] = True
        print "%s..." % (self)
        return [self.getExampleImage(imgs)]


class Equalize(_OnOffTransformer):
    
    def doTransform(self, img):
        return ImageOps.equalize(img)
    
class Grayscale(_OnOffTransformer):

    def doTransform(self, img):
        return ImageOps.grayscale(img).convert("RGB")
    
class Dither(_OnOffTransformer):

    def doTransform(self, img):
        return img.convert("1").convert("RGB")
    
class Invert(_OnOffTransformer):
    
    def doTransform(self, img):
        return ImageOps.invert(img)
    
    
#############################################################################
class Posterize(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["bits"] = random.randint(1, 2)

    def getArgsString(self):
        return "(%d)" % (self.args["bits"])

    def transformImage(self, img):
        return ImageOps.posterize(img, self.args["bits"])
    
    def tweakInner(self):
        self.args["bits"] = random.randint(1, 2)

    def getExamplesInner(self, imgs):
        exs = []
        for bits in [1, 2]:
            self.args["bits"] = bits
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    

#############################################################################
class Solarize(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["threshold"] = random.randint(0, 255)

    def getArgsString(self):
        return "(%d)" % (self.args["threshold"])

    def transformImage(self, img):
        return ImageOps.solarize(img, self.args["threshold"])

    def tweakInner(self):
        self.args["threshold"] = random.randint(0, 255)

    def getExamplesInner(self, imgs):
        exs = []
        for threshold in [0, 63, 127, 181, 255]:
            self.args["threshold"] = threshold
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class _Enhancer(_xformer._MonoTransformer):
    
    enhancer = None
    min_factor = 0.0
    max_factor = 1.0

    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["factor"] = random.uniform(self.min_factor, self.max_factor)
        
    def getArgsString(self):
        return "(%.2f)" % (self.args["factor"])

    def transformImage(self, img):
        return self.enhancer(img).enhance(self.args["factor"])
    
    def tweakInner(self):
        self.args["factor"] = random.uniform(self.min_factor, self.max_factor)
        
    def getExamplesInner(self, imgs):
        exs = []
        factor = 0.2
        while (factor <= self.max_factor):
            self.args["factor"] = factor
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
            factor = factor + (self.max_factor - self.min_factor)/3.0
        return exs


class ColorEnhancer(_Enhancer):  enhancer = ImageEnhance.Color
class BrightnessEnhancer(_Enhancer):  enhancer = ImageEnhance.Brightness
class ContrastEnhancer(_Enhancer):  enhancer = ImageEnhance.Contrast

class SharpnessEnhancer(_Enhancer):  

    enhancer = ImageEnhance.Sharpness
    min_factor = 0.0
    max_factor = 2.0
