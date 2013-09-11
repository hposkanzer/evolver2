'''
Created on Aug 10, 2010

@author: hmp@drzeus.best.vwh.net
'''
import os
import string

import Image


class SrcImage(object):

    def __init__(self, fpath):
        self.fpath = fpath
    
    def getPath(self):
        return self.fpath
    
    def getThumbPath(self):
        return self.getThumbName(self.getPath())
    
    def getFilename(self):
        return os.path.split(self.fpath)[-1]
    
    def getThumbName(self, s=None):
        if (s == None):
            s = self.getFilename()
        l = list(os.path.splitext(s))
        l.insert(1, ".t")
        return string.join(l, "")
    
    def getPageName(self):
        return os.path.splitext(self.getFilename())[0] + ".html"
    
    def getImage(self):
        # I tried saving the image in self, but I kept getting memory errors.
        # So we just re-load it every time.
        img = Image.open(self.fpath)
        img.load() # A bug in Image.split() requires this.
        return img
    
    def getDims(self):
        return self.getImage().size
        
    def __str__(self):
        return "Image(%s)" % (self.getFilename())
    

