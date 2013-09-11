import Image
import UsageError
import os
import Picklable
import re

# Wrapper class to preserve file name, provide a better str(), etc.
class XImage(Picklable.Picklable):
    
    fpath = ""
    img = None
    loaded = 0
    
    def __init__(self, fpath):
        Picklable.Picklable.__init__(self)
        self.fpath = fpath
    
    def load(self):
        if self.loaded:
            return
        self.logger.debug("Loading %s..." % (self.fpath))
        # We open, load, and close the file explicitly so that we can
        # do stuff like delete the file later.
        f = open( self.fpath, "rb" )
        self.img = Image.open( f )
        self.img.load()
        f.close()
        self.loaded = 1
        
    def getFilename(self):
        return os.path.split(self.fpath)[-1]
        
    def __str__(self):
        return "Image(%s)" % (self.getFilename())
    
    def __getattr__(self, attr):
        return getattr(self.img, attr)
    

class ImageLoader(Picklable.Picklable):

    filetypes = [
                 ".jpg",
                 ".JPG",
                 ]
    thumb_pats = [
                  "\.t\.jpg$",
                  "\.t\.JPG$",
                  ]
    
    def __init__(self):
        Picklable.Picklable.__init__(self)


    # Load all image names in the given directory.
    # Only files that match one of the filetypes are loaded.
    # Files that match one of the thumbnail patterns are omitted.
    # Returns a list of file paths.
    def loadNames( self, dir ):
        
        if not os.path.isdir(dir):
            raise UsageError.UsageError( "%s is not a directory" % (dir) )
                              
        self.logger.debug("Reading %s..." % (dir))
            
        imgs = []
        for fname in os.listdir( dir ):
            
            if os.path.splitext( fname )[1] not in self.filetypes:
                continue
            
            if self.isThumbnail(fname):
                continue
            
            imgs.append(os.path.join(dir, fname))
            
        self.logger.debug("Loaded %s" % (map(os.path.basename, imgs)))
        return imgs
    
    
    # Load all images in the given directory.
    # Only files that match one of the filetypes are loaded.
    # Files that match one of the thumbnail patterns are omitted.
    # Returns a list of Image instances.
    def loadAll( self, dir ):
        imgs = []
        for fpath in self.loadNames( dir ):
            imgs.append(self.loadImage(fpath))
        return imgs
    
    
    # Load an image from a file name.
    def loadImage(self, fpath):
        
        img = Image.open(fpath)
        img.load()
        self.logger.debug("Loaded %s" % (img))
            
        return img


    def isThumbnail(self, fname):
        for pat in self.thumb_pats:
            if re.search(pat, fname):
                return 1
        return 0