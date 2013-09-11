'''
Created on Aug 4, 2010

@author: hmp
'''
import Image
import ImageLoader
import UsageError
import os
import tempfile
import unittest


class Test(unittest.TestCase):

    loader = None

    def setUp(self):
        self.loader = ImageLoader.ImageLoader()
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

    def test005SupportedNames(self):
        fname = self.makeTestImage()
        try:
            l = self.loader.loadNames(self.dir)
            self.failUnless(len(l) == 1, "Load of directory returned list with length not equal to 1:  %s" % (l))
            self.failUnless(l[0] == fname, "Loaded filename is not %s:  %s" % (fname, l[0]))
        finally:
            os.remove(fname)


    def test006SupportedTypes(self):
        fname = self.makeTestImage()
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(len(l) == 1, "Load of directory returned list with length not equal to 1:  %s" % (l))
            self.failUnless(l[0].format == "JPEG", "Loaded image is not a JPEG:  %s" % (l[0].format))
            self.failUnless(l[0].mode == "RGB", "Loaded image is not RGB:  %s" % (l[0].mode))
            self.failUnless(l[0].size == (2,2), "Loaded image is not 2x2:  %s" % (str(l[0].size)))
        finally:
            os.remove(fname)


    def test007Thumbnail(self):
        f = tempfile.NamedTemporaryFile(dir=self.dir, suffix=".t.jpg")
        try:
            l = self.loader.loadAll(self.dir)
            self.failUnless(l == [], "Load of directory returned thumbnails:  %s" % (l))
        finally:
            f.close()


    def makeTestImage(self):
        # We have to use mkstemp here so that we can close it
        # so that we can delete it on Windows.  Feh.
        fd, fname = tempfile.mkstemp(dir=self.dir, suffix=".jpg")
        try:
            i = Image.new("RGB", (2, 2))
            i.save(fname)
        finally:
            os.close(fd)
        return fname
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testNotADir']
    unittest.main()