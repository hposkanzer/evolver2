'''
Created on Aug 8, 2010

@author: hmp@drzeus.best.vwh.net
'''
import _xformer

# A special class that's the end-point of transformer chains.
# Input is a SrcImage, not another Transfomer.
# It does nothing but return the image.
class NonTransformer(_xformer._Transformer):

    is_non_transformer = 1

    def __init__(self, img=None):
        _xformer._Transformer.__init__(self)
        if img:
            self.addInput(img)
    
    
    def getFilename(self):
        if self.inputs:
            return self.inputs[0].getFilename()
        else:
            return "(empty)"
        
    def getInputGenomes(self):
        return [self.getFilename()]
        
        
    def getWidth(self):
        return 1
    
    def getDepth(self):
        return 1
    
        
    def toString(self, i=0):
        return "  " * i + "%d: %s" % (i, self.getFilename())


    def getExpectedInputCount(self):
        return 1
    
    def transform(self, experiment):
        self.logger.debug("%s..." % (self))
        return self.getImage()
    
    def getSrcImage(self):
        return self.inputs[0]
    
    def getImage(self):
        return self.inputs[0].getImage()

    def clone(self):
        new = self.__class__()
        if self.inputs:
            new.addInput(self.inputs[0])
        return new

    def tweak(self, tweak_rate):
        pass
    
    def getDims(self):
        if not self.dims:
            self.dims = self.inputs[0].getImage().size
        return self.dims
    
    def getPairs(self, prev=None):
        return []
        
    def __str__(self):
        if self.inputs:
            return str(self.inputs[0])
        else:
            return "(empty)"
