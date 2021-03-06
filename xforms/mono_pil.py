import os
import string
import math
import _xformer
from PIL import Image
from PIL import ImageFilter
import random
from PIL import ImageOps
from PIL import ImageEnhance
from PIL import ImageChops
from PIL import ImageDraw
from PIL import ImageFont
import Location


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
        s = abs(math.sin(self.args["angle"]/360.0 * _xformer.TWOPI))
        c = abs(math.cos(self.args["angle"]/360.0 * _xformer.TWOPI))
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
        return "(%s)" % (self.args["filter"].__name__)

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


class Kernel(_xformer._MonoTransformer):
    
    maxValue = 4
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%s)" % (string.join(map(str, self.args["kernel"]), ","))

    def transformImage(self, img):
        return img.filter(ImageFilter.Kernel((5,5), self.args["kernel"]))
    
    def tweakInner(self):
        self.args["kernel"] = map(lambda x: random.randint(-self.maxValue, self.maxValue), range(25))
        
    def getExamplesInner(self, imgs):
        exs = []
        kk = []
        kk.append( [ 4, 3, 2, 1, 0,
                     3, 2, 1, 0,-1,
                     2, 1, 0,-1,-2,
                     1, 0,-1,-2,-3,
                     0,-1,-2,-3,-4] )
        kk.append( map( lambda x: -x, kk[-1]) )
        kk.append( [-2,-1, 0,-1,-2,
                    -1, 0, 1, 0,-1,
                     0, 1, 2, 1, 0,
                    -1, 0, 1, 0,-1,
                    -2,-1, 0,-1,-2] )
        kk.append(self.args["kernel"])
        for k in kk:
            self.args["kernel"] = k
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


class Quad(_xformer._MonoTransformer):
    
    max_tweak = 0.2

    def __init__(self):
        _xformer._MonoTransformer.__init__(self)

    # so we can know the size of the input image.    
    def addInput(self, xform):
        _xformer._MonoTransformer.addInput(self, xform)
        self.args["quad"] = self.getRandomQuad(True)

    def getArgsString(self):
        return "(%s)" % (string.join(map(str, self.args["quad"]), ","))

    def transformImage(self, img):
        ret = img.transform(self.getDims(), Image.QUAD, self.args["quad"])
        #draw = ImageDraw.Draw(ret)
        #draw.polygon(self.args["quad"], outline=(255,0,0))
        return ret

    def tweakInner(self):
        self.args["quad"] = self.tweakQuad(self.args["quad"], self.max_tweak)

    def getExamplesInner(self, imgs):
        exs = []
        for i in range(3):
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
            self.tweakInner()
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


class ShiftValues(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.args["shift"] = random.randint(0, 255)

    def getArgsString(self):
        return "(%d)" % (self.args["shift"])

    def transformImage(self, img):
        return img.point(lambda x: (x + self.args["shift"]) % 256)

    def tweakInner(self):
        self.args["shift"] = random.randint(0, 255)

    def getExamplesInner(self, imgs):
        exs = []
        for shift in [10, 63, 127, 181, 245]:
            self.args["shift"] = shift
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


class ShiftBands(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%d, %d, %d)" % (self.args["r"], self.args["g"], self.args["b"])

    def transformImage(self, img):
        s = range(256)
        r = s[self.args["r"]:] + s[:self.args["r"]]
        g = s[self.args["g"]:] + s[:self.args["g"]]
        b = s[self.args["b"]:] + s[:self.args["b"]]
        t = r + g + b
        return img.point(t)

    def tweakInner(self):
        self.args["r"] = random.randint(0, 255)
        self.args["g"] = random.randint(0, 255)
        self.args["b"] = random.randint(0, 255)

    def getExamplesInner(self, imgs):
        exs = []
        for r in [0, 127]:
            for g in [0, 127]:
                for b in [0, 127]:
                    self.args["r"] = r
                    self.args["g"] = g
                    self.args["b"] = b
                    print "%s..." % (self)
                    exs.append(self.getExampleImage(imgs))
        return exs


class InvertBands(_xformer._MonoTransformer):    
    
    band_options = ['', 'R', 'B', 'G', 'RB', 'RG', 'BG', 'RBG']
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%s)" % (self.args["bands"])

    def transformImage(self, img):
        s = range(256)
        r = range(256)
        r.reverse()
        l = []
        for band in "RGB":
            if (band in self.args["bands"]):
                l.extend(r)
            else:
                l.extend(s)
        return img.point(l)

    def tweakInner(self):
        self.args["bands"] = random.choice(self.band_options)
        
    def getExamplesInner(self, imgs):
        exs = []
        for bands in self.band_options:
            self.args["bands"] = bands
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


class _ContrastBands(_xformer._MonoTransformer):    
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%s, %s, %s)" % (self.args["r"], self.args["g"], self.args["b"])

    def transformImage(self, img):
        r = map(lambda x, y=self.args["r"]: x/255.0 * (y[1] - y[0]) + y[0], range(256))
        b = map(lambda x, y=self.args["b"]: x/255.0 * (y[1] - y[0]) + y[0], range(256))
        g = map(lambda x, y=self.args["g"]: x/255.0 * (y[1] - y[0]) + y[0], range(256))
        t = r + g + b
        return img.point(t)

    def tweakInner(self):
        self.args["r"] = (random.randint(0, 255), random.randint(0, 255))
        self.args["g"] = (random.randint(0, 255), random.randint(0, 255))
        self.args["b"] = (random.randint(0, 255), random.randint(0, 255))

    def getExamplesInner(self, imgs):
        exs = []
        for r in range(5):
            self.tweakInner()
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs


#############################################################################
class _Enhancer(_xformer._MonoTransformer):
    
    enhancer = None
    min_factor = 0.0
    max_factor = 4.0

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
        for i in range(3):
            self.args["factor"] = factor
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
            factor = factor + (self.max_factor - self.min_factor - 0.4)/2.0
        return exs


class ColorEnhancer(_Enhancer):  enhancer = ImageEnhance.Color
class BrightnessEnhancer(_Enhancer):  enhancer = ImageEnhance.Brightness
class ContrastEnhancer(_Enhancer):  enhancer = ImageEnhance.Contrast
class SharpnessEnhancer(_Enhancer):  enhancer = ImageEnhance.Sharpness


#############################################################################
class Dots(_xformer._MonoTransformer):    
    
    modes = ["SCALE", "GRID"]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%d, %s)" % (self.args["sample"], self.args["mode"])

    def transformImage(self, img):
        ret = Image.new('RGB', self.getDims())
        draw = ImageDraw.Draw(ret)
        sample = self.args["sample"]
        values = img.filter(ImageFilter.MedianFilter(5))
        for x in xrange(0, self.getDims()[0], sample):
            for y in xrange(0, self.getDims()[1], sample):
                if (self.args["mode"] == "SCALE"):
                    diameter = (sum(values.getpixel((x,y))) / (255.0 * 3))**0.5
                else:
                    diameter = 0.9
                edge = 0.5*(1-diameter)*sample
                x_pos, y_pos = (x+edge), (y+edge)
                box_edge = sample*diameter
                draw.ellipse((x_pos, y_pos, x_pos + box_edge, y_pos + box_edge), fill=values.getpixel((x,y)))
        return ret

    def tweakInner(self):
        self.args["sample"] = random.randint(2, 50)
        self.args["mode"] = random.choice(self.modes)

    def getExamplesInner(self, imgs):
        exs = []
        for mode in self.modes:
            for sample in [10, 30]:
                self.args["sample"] = sample
                self.args["mode"] = mode
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs



#############################################################################
class Fuzz(_xformer._MonoTransformer):    
    
    modes = ["RANDOM", "OUT", "ANGLE"]

    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        if (self.args["mode"] == "ANGLE"):
            return "(%s, %.2f, %.2f)" % (self.args["mode"], self.args["sigma"], self.args["angle"])
        else:
            return "(%s, %.2f)" % (self.args["mode"], self.args["sigma"])
            

    def transformImage(self, img):
        ret = img.copy()
        rload = ret.load()
        iload = img.load()
        mode = self.args.get("mode")
        sigma = self.args["sigma"]
        dims = self.getDims()
        for x in xrange(0, dims[0]):
            for y in xrange(0, dims[1]):
                if (mode == "ANGLE"):
                    angle = self.args["angle"]
                elif (mode == "OUT"):
                    if ((x - dims[0]/2.0) == 0):
                        continue
                    angle = math.atan((y - dims[1]/2.0)/(x - dims[0]/2.0))
                else:
                    angle = random.uniform(0, _xformer.TWOPI)
                m = random.normalvariate(0, sigma)
                mx = int(math.floor(math.cos(angle) * m))
                my = int(math.floor(math.sin(angle) * m))
                rload[x,y] = iload[(x+mx)%dims[0], (y+my)%dims[1]]
        return ret

    def tweakInner(self):
        self.args["mode"] = random.choice(self.modes)
        self.args["sigma"] = random.uniform(0, 10)
        self.args["angle"] = random.uniform(0, _xformer.TWOPI)

    def getExamplesInner(self, imgs):
        exs = []
        for m in self.modes:
            for s in (2, 10):
                self.args["mode"] = m
                self.args["sigma"] = s
                if (m == "ANGLE"):
                    for a in [0.0, math.pi/2]:
                        self.args["angle"] = a
                        print "%s..." % (self)
                        exs.append(self.getExampleImage(imgs))
                else:
                    print "%s..." % (self)
                    exs.append(self.getExampleImage(imgs))
        return exs
    
    

#############################################################################
class TV(_xformer._MonoTransformer):    
    
    randomModePct = 0.2

    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%d, %.2f)" % (self.args["rows"], self.args["dim"])

    def transformImage(self, img):
        dims = self.getDims()
        rows = self.args["rows"]
        dim = self.args["dim"]
        overlay = Image.new("L", dims, "white")
        for i in range(0, dims[1], rows*2):
            overlay.paste(int(round(255 * dim)), (0,i,dims[0],i+rows))
        return ImageChops.multiply(img, overlay.convert("RGB"))

    def tweakInner(self):
        self.args["rows"] = random.randint(1, 2)
        self.args["dim"] = random.uniform(0.0, 1.0)

    def getExamplesInner(self, imgs):
        exs = []
        for r in (1, 2):
            for d in (0.0, 0.5):
                self.args["rows"] = r
                self.args["dim"] = d
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs
        

#############################################################################
class ASCII(_xformer._MonoTransformer):    
    
    chars1 = ['#', '@', '$', '=', '*', '!', ';', ':', '~', '-', ',', '.', ' ']
    chars2 = ["#", "A", "@", "M",  "$", "0", "e", "a", "o", "=", "+", ";", ":", ",", ".", " "]
    charsets = [chars1, chars2]
    modes = ["L", "RGB"]
    fonts = ["08", "10", "12", "14"]

    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%s, %d, %s)" % (self.args["font"], self.charsets.index(self.args["charset"]), self.args["mode"])

    def transformImage(self, img):
        dims = self.getDims()
        ret = Image.new("RGB", dims, "white")
        draw = ImageDraw.Draw(ret)
        font = "courR" + self.args["font"] + ".pil"
        path= Location.getInstance().toAbsolutePath(os.path.join("fonts", font))
        font = ImageFont.load(path)
        (w,h) = draw.textsize(self.args["charset"][-1], font)
        if self.args["mode"] == "L":
            # Convert to grayscale
            values = img.convert("L")
        else:
            # Saturate the color
            values = ImageEnhance.Color(img).enhance(4.0)
        values = values.filter(ImageFilter.MedianFilter(5))
        for y in range(0, dims[1], h):
            for x in range(0, dims[0], w):
                v = values.getpixel((x,y))
                if self.args["mode"] == "L":
                    pct =  v/255.0
                    fill = (0, 0, 0)
                else:
                    pct = sum(v)/765.0
                    fill = v
                vi = int(round(pct * (len(self.args["charset"])-1)))
                draw.text((x,y), self.args["charset"][vi], font=font, fill=fill)
        return ret

    def tweakInner(self):
        self.args["font"] = random.choice(self.fonts)
        self.args["charset"] = random.choice(self.charsets)
        self.args["mode"] = random.choice(self.modes)

    def getExamplesInner(self, imgs):
        exs = []
        for font in [self.fonts[0], self.fonts[-1]]:
            for mode in self.modes:
                for charset in self.charsets:
                    self.args["font"] = font
                    self.args["mode"] = mode
                    self.args["charset"]  = charset
                    print "%s..." % (self)
                    exs.append(self.getExampleImage(imgs))
        return exs