'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
from PIL import Image

import mono_pil
import _halftone


#############################################################################
class Halftone(mono_pil._OnOffTransformer):
    
    def doTransform(self, img):
        h = _halftone.Halftone(None)
        cmyk = h.gcr(img, 0.0)
        dots = h.halftone(img, 0.0, cmyk, sample=5, scale=2, angles=h.default_angles)
        ret = Image.merge('CMYK', dots)
        ret = ret.resize(img.size, Image.ANTIALIAS)
        return ret.convert("RGB")


