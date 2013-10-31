'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import string
import _xformer
import random
import _Distortions


#############################################################################
class Speckle(_xformer._MonoTransformer):
    
    maxBlockSize = 50
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%s, %.2f)" % (self.args["blockSize"], self.args["sigma"])

    def transformImage(self, img):
        ret = img.copy()
        d = _Distortions.WigglyBlocks(self.args["blockSize"], self.args["sigma"], 1000)
        d.render(ret)
        return ret
    
    def tweakInner(self):
        self.args["blockSize"] = random.randint(0, self.maxBlockSize)
        self.args["sigma"] = random.uniform(0, 10)
        
    def getExamplesInner(self, imgs):
        exs = []
        for b in (10, 50):
            for s in (0.1, 5, 10):
                self.args["blockSize"] = b
                self.args["sigma"] = s
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs


class Sine(_xformer._MonoTransformer):
    
    maxAmplitude = 40
    maxPeriod = 0.1
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%.2f, %.2f)" % (self.args["amplitude"], self.args["period"])

    def transformImage(self, img):
        d = _Distortions.SineWarp(self.args["amplitude"], self.args["period"])
        return d.render(img)
    
    def tweakInner(self):
        self.args["amplitude"] = random.uniform(0, self.maxAmplitude)
        self.args["period"] = random.uniform(0, self.maxPeriod)
        
    def getExamplesInner(self, imgs):
        exs = []
        for a in (10, 20, 40):
            for p in (0.01, 0.05, 0.1):
                self.args["amplitude"] = a
                self.args["period"] = p
                print "%s..." % (self)
                exs.append(self.getExampleImage(imgs))
        return exs

