'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import inspect
import os
import sys

import Picklable
import UsageError


class TransformLoader(Picklable.Picklable):
    
    def __init__(self):
        Picklable.Picklable.__init__(self)
        self.classes = []
        self.non_transformer = None
        self.tile_transformer = None


    def getTransforms(self):
        return self.classes
    
    def getNonTransformer(self):
        return self.non_transformer
    
    def getTileTransformer(self):
        return self.tile_transformer
    
    
    # Import all .py files in the given directory and return all classes found therein.
    # Files and classes starting with "_" are skipped.
    # Modules with the same name as already-imported modules will not import.
    def loadAll(self, dir):
        
        if not os.path.isdir(dir):
            raise UsageError.UsageError( "%s is not a directory" % (dir) )
                              
        self.logger.debug("Reading %s..." % (dir))
            
        if dir not in sys.path:
            sys.path.append(dir)
            
        for fname in os.listdir( dir ):
            if (fname[0] == "_"):
                continue
            if (os.path.splitext(fname)[1] != ".py"):
                continue
            self.loadModule(fname)
            
        return self.classes
            
  
    # Import the module corresponding to a file name.
    # Classes starting with "_" are skipped.
    # Modules with the same name as already-imported modules will not import.
    # PYTHONPATH is assumed to be correct for the import to succeed.
    def loadModule(self, fname):
        
        modname, ext = os.path.splitext(fname)
        
        self.logger.debug("Importing %s..." % (modname))
        mod = __import__(modname)
        
        self.loadClasses(mod)
  
    
    # Find all the classes in a module.
    # Classes starting with "_" are skipped.
    def loadClasses(self, mod):
        
        cc = []
        
        members = inspect.getmembers(mod, inspect.isclass)
        for (name, obj) in members:

            if (hasattr(obj, "is_non_transformer") and obj.is_non_transformer):
                self.non_transformer = obj
                self.logger.debug("Found NonTransformer:  %s" % (obj))
                continue
                
            if (hasattr(obj, "is_tile_transformer") and obj.is_tile_transformer):
                self.tile_transformer = obj
                self.logger.debug("Found TileTransformer:  %s" % (obj))
                continue
                
            if (obj.__name__[0] == "_"):
                continue

            cc.append(obj)
            
        self.logger.debug("Loaded %s" % (cc))
        self.classes.extend(cc)
