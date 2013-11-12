'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import string
import _xformer
import random
import math

import _Distortions


#############################################################################
class Speckle(_xformer._MonoTransformer):
    
    maxBlockSize = 50
    randomModePct = 0.2
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%s, %.2f, %.2f)" % (self.args["blockSize"], self.args["sigma"], self.args["angle"])

    def transformImage(self, img):
        ret = img.copy()
        d = _Distortions.WigglyBlocks(self.args["blockSize"], self.args["sigma"], self.args["angle"], self.args["iters"])
        d.render(ret)
        return ret
    
    def tweakInner(self):
        self.args["blockSize"] = random.randint(0, self.maxBlockSize)
        self.args["sigma"] = random.uniform(0, 10)
        if (random.uniform(0, 1.0) <= self.randomModePct):
            self.args["angle"] = -1
        else:
            self.args["angle"] = random.uniform(0, math.pi * 2)
        self.args["iters"] = self.getIterations()
        
    def getExamplesInner(self, imgs):
        exs = []
        for a in (-1, 0.0, math.pi/2):
            for b in (10, 50):
                for s in (0.1, 10):
                    self.args["blockSize"] = b
                    self.args["sigma"] = s
                    self.args["angle"] = a
                    self.args["iters"] = self.getIterations()
                    print "%s..." % (self)
                    exs.append(self.getExampleImage(imgs))
        return exs
    
    def getIterations(self):
        # From 10000 down to 1000
        return -180 * self.args["blockSize"] + 10000


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
