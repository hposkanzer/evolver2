'''
Created on Aug 4, 2010

@author: hmp
'''
import UsageError
import os
import tempfile
import unittest
import TransformLoader
import types
import random


class Test(unittest.TestCase):

    loader = None

    def setUp(self):
        self.loader = TransformLoader.TransformLoader()
        self.dir = tempfile.mkdtemp()


    def tearDown(self):
        self.loader = None
        os.rmdir(self.dir)


    def test001NotAPath(self):
        try:
            self.loader.loadAll("/x/y/z")
            self.fail("Load of non-existent path failed to raise UsageError")
        except UsageError.UsageError:
            pass
        
    def test002NotADir(self):
        f = tempfile.NamedTemporaryFile()
        try:
            self.loader.loadAll(f.name)
            self.fail("Load of non-directory failed to raise UsageError")
        except UsageError.UsageError:
            pass
        
    def test003EmptyDir(self):
        l = self.loader.loadAll(self.dir)
        self.failUnless(l == [], "Load of empty directory returned non-empty list:  %s" % (l))
        
    def test004UnsupportedTypes(self):
        f = tempfile.NamedTemporaryFile(dir=self.dir, suffix=".txt")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of directory returned unsupported types:  %s" % (l))
        finally:
            f.close()

    def test005PrivateNames(self):
        f = tempfile.NamedTemporaryFile(dir=self.dir, prefix="_", suffix=".py")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of directory returned private files:  %s" % (l))
        finally:
            f.close()

    def test006EmptyFile(self):
        mod = ModuleFile(self.dir)
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of empty file returned classes:  %s" % (l))
            non = self.loader.getNonTransformer()
            self.failIf(non != None, "Load of empty file returned non-transformer:  %s" % (non))
        finally:
            mod.remove()
            
    def test007NoClass(self):
        mod = ModuleFile(self.dir, "foo = 1\n")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of file without classes returned classes:  %s" % (l))
            non = self.loader.getNonTransformer()
            self.failIf(non != None, "Load of empty file returned non-transformer:  %s" % (non))
        finally:
            mod.remove()
            
    def test008PrivateClass(self):
        mod = ModuleFile(self.dir, "class _Foo: pass\n")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of file with private class returned classes:  %s" % (l))
            non = self.loader.getNonTransformer()
            self.failIf(non != None, "Load of empty file returned non-transformer:  %s" % (non))
        finally:
            mod.remove()
            
    def test009Class(self):
        mod = ModuleFile(self.dir, "class Foo: pass\n")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(len(l) == 1, "Load of directory returned list with length not equal to 1:  %s" % (l))
            self.failUnless(type(l[0]) == types.ClassType, "Loaded object is not a class:  %s" % (type(l[0])))
            non = self.loader.getNonTransformer()
            self.failIf(non != None, "Load of empty file returned non-transformer:  %s" % (non))
        finally:
            mod.remove()
            
    def test010NonTransformer(self):
        mod = ModuleFile(self.dir, "class NonTransformer: is_non_transformer = 1\n")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of file with private class returned classes:  %s" % (l))
            non = self.loader.getNonTransformer()
            self.failIf(non == None, "Load of file returned null non-transformer")
            self.failUnless(type(non) == types.ClassType, "Non-transformer is not a class:  %s" % (type(non)))
        finally:
            mod.remove()
            
        
class ModuleFile:
    
    dir = ""
    fpath = ""
    
    def __init__(self, dir, code=""):
        self.dir = dir
        # We can't use tempfile here because it'll create illegal module names.
        # We have to randomize the module name, too, otherwise the import command will
        # not re-load the module because the name is unchanged.
        self.fpath = os.path.join(self.dir, "p%dr%d.py" % (os.getpid(), random.randint(0, 10000)))
        f = open(self.fpath, "w")
        if code:
            f.write(code)
        f.close()
        
    def remove(self):
        os.remove(self.fpath)
        pyc = self.fpath + "c"
        if os.path.exists(pyc):
            os.remove(pyc)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testNotADir']
    unittest.main()