import string
import _xformer
import random
import math

import _Distortions


#############################################################################
class Speckle(_xformer._MonoTransformer):
    
    maxBlockSize = 50
    modes = ["RANDOM", "OUT", "ANGLE"]
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        if (self.args["mode"] == "ANGLE"):
            return "(%s, %d, %.2f, %.2f)" % (self.args["mode"], self.args["blockSize"], self.args["sigma"], self.args["angle"])
        else:
            return "(%s, %d, %.2f)" % (self.args["mode"], self.args["blockSize"], self.args["sigma"])

    def transformImage(self, img):
        if (self.args["mode"] == "ANGLE"):
            angle = self.args["angle"]
        elif (self.args["mode"] == "RANDOM"):
            angle = -1
        else:
            angle = -2
        d = _Distortions.WigglyBlocks(self.args["blockSize"], self.args["sigma"], angle, self.args["iters"])
        return d.render(img)
    
    def tweakInner(self):
        self.args["mode"] = random.choice(self.modes)
        self.args["blockSize"] = random.randint(0, self.maxBlockSize)
        self.args["sigma"] = random.uniform(0, 10)
        self.args["angle"] = random.uniform(0, math.pi * 2)
        self.args["iters"] = self.getIterations()
        
    def getExamplesInner(self, imgs):
        exs = []
        for m in self.modes:
            for b in (10, 50):
                for s in (2, 10):
                    self.args["mode"] = m
                    self.args["blockSize"] = b
                    self.args["sigma"] = s
                    self.args["iters"] = self.getIterations()
                    if (m == "ANGLE"):
                        for a in [0.0, math.pi/2]:
                            self.args["angle"] = a
                            print "%s..." % (self)
                            exs.append(self.getExampleImage(imgs))
                    else:
                        print "%s..." % (self)
                        exs.append(self.getExampleImage(imgs))
        return exs
    
    def getIterations(self):
        # From 10000 down to 1000
        return -180 * self.args["blockSize"] + 20000


class Sine(_xformer._MonoTransformer):
    
    maxAmplitude = 40
    maxPeriod = 0.1
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%.2f, %.2f, [%.2f,%.2f])" % (self.args["amplitude"], self.args["period"], self.args["offset"][0], self.args["offset"][1])

    def transformImage(self, img):
        d = _Distortions.SineWarp(self.args["amplitude"], self.args["period"], self.args["offset"])
        return d.render(img)
    
    def tweakInner(self):
        self.args["amplitude"] = random.uniform(0, self.maxAmplitude)
        self.args["period"] = random.uniform(0, self.maxPeriod)
        self.args["offset"] = (random.uniform(0, math.pi * 2 / self.args["period"]),
                               random.uniform(0, math.pi * 2 / self.args["period"]))
        
    def getExamplesInner(self, imgs):
        exs = []
        for a in (10, 40):
            for p in (0.01, 0.05, 0.1):
                self.args["amplitude"] = a
                self.args["period"] = p
                for o in ((0,0), (math.pi/p,math.pi/p)):
                    self.args["offset"] = o
                    print "%s..." % (self)
                    exs.append(self.getExampleImage(imgs))
        return exs


class Wave(_xformer._MonoTransformer):
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)

    def getArgsString(self):
        return "(%.2f, %.2f)" % (self.args["wavelength"], self.args["amplitude"])

    def addInput(self, xform):
        _xformer._MonoTransformer.addInput(self, xform)
        self.tweakInner()

    def transformImage(self, img):
        d = _Distortions.DomeWarp(self.args["amplitude"], self.args["wavelength"])
        return d.render(img)
    
    def tweakInner(self):
        self.args["wavelength"] = random.uniform(30, min(self.getDims())/2.0)
        self.args["amplitude"] = random.uniform(-self.getMaxAmplitude(), self.getMaxAmplitude())
        
    def getMaxAmplitude(self):
        return self.args["wavelength"]/4.0
        
    def getExamplesInner(self, imgs):
        exs = []
        for w in (30, 150, 300):
            self.args["wavelength"] = w
            for a in (-self.getMaxAmplitude(), self.getMaxAmplitude()):
                self.args["amplitude"] = a
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs


class BentleyWarp(_xformer._Transformer):    
    
    debug = False
    
    def __init__(self):
        _xformer._Transformer.__init__(self)
        self.tweakInner()

    def getExpectedInputCount(self):
        return 2

    def getArgsString(self):
        return "(%.2f, %.2f)" % (self.args["sigma"], self.args["angle"])

    def transformInner(self, imgs):
        d = _Distortions.BentleyWarp(imgs[1], self.args["sigma"], self.args["angle"])
        return d.render(imgs[0])

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
    