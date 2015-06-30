'''
Created on Aug 8, 2010

@author: hmp@drzeus.best.vwh.net
'''
import _xformer
from PIL import Image

# A special class that's the head-point of transformer chains when in reflect mode.
class ReflectTransformer(_xformer._MonoTransformer):

    is_reflect_transformer = 1
    is_reserved_transformer = 1

    def getArgsString(self):
        return "()"

    def transformImage(self, img):
        dims = self.getDims()
        small = img.resize((dims[0]/2, dims[1]/2), Image.ANTIALIAS)
        img.paste(small, (0, 0))  # In-place edit!
        small = small.transpose(Image.FLIP_LEFT_RIGHT)
        img.paste(small, (dims[0]/2, 0))  # In-place edit!
        small = small.transpose(Image.FLIP_TOP_BOTTOM)
        img.paste(small, (dims[0]/2, dims[1]/2))  # In-place edit!
        small = small.transpose(Image.FLIP_LEFT_RIGHT)
        img.paste(small, (0, dims[1]/2))  # In-place edit!
        return img
    
    
    def tweakInner(self):
        pass
    
    def getPairs(self, prev=None):
        l = []
        for input in self.inputs:
            l.extend(input.getPairs(self))
        return l
