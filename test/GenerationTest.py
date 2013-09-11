'''
Created on Aug 10, 2010

@author: hmp@drzeus.best.vwh.net
'''
import unittest
import tempfile
import os
import Generation

class _TestBase(unittest.TestCase):
    
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.dirnames = []
        self.fnames = []
        

    def tearDown(self):
        for fname in self.fnames:
            os.remove(os.path.join(self.dir, fname))
        for dirname in self.dirnames:
            os.rmdir(os.path.join(self.dir, dirname))
        os.rmdir(self.dir)


    def makeDir(self, dirname, with_pkl=0):
        os.mkdir(os.path.join(self.dir, dirname))
        if with_pkl:
            self.makeFile(os.path.join(dirname, Generation.pickle_name))
        self.dirnames.append(dirname)

    def makeFile(self, fname):
        open(os.path.join(self.dir, fname), "w").close()
        self.fnames.append(fname)

    
class TestLatestGenerationName(_TestBase):


    def test01EmptyDir(self):
        gen_dir = Generation.getLatestGenerationName(self.dir)
        self.failUnlessEqual(gen_dir, None, "Empty directory did not return None")
        
    def test02NoGenerations(self):
        self.makeFile("foo.txt")
        gen_dir = Generation.getLatestGenerationName(self.dir)
        self.failUnlessEqual(gen_dir, None, "Directory with no Generations did not return None")
        
    def test03FalseGenerations(self):
        self.makeFile("galileo")
        gen_dir = Generation.getLatestGenerationName(self.dir)
        self.failUnlessEqual(gen_dir, None, "Directory with false Generation did not return None")
        
    def test04FailedDir(self):
        self.makeDir("g0001")
        gen_dir = Generation.getLatestGenerationName(self.dir)
        self.failUnlessEqual(gen_dir, None, "Directory with failed Generation did not return None")

    def test05Ordering(self):
        self.makeDir("g0001", with_pkl=1)
        self.makeDir("g0002", with_pkl=1)
        gen_dir = Generation.getLatestGenerationName(self.dir)
        self.failUnless(gen_dir == "g0002", "Generation found was not the latest:  %s" % (gen_dir))

    def test06Fallback(self):
        self.makeDir("g0001", with_pkl=1)
        self.makeDir("g0002")
        gen_dir = Generation.getLatestGenerationName(self.dir)
        self.failUnless(gen_dir == "g0001", "Generation found was not the latest successfull one:  %s" % (gen_dir))


class TestLatestGenerationID(_TestBase):

    def test01EmptyDir(self):
        gen_id = Generation.getLatestGenerationID(self.dir)
        self.failUnlessEqual(gen_id, None, "Empty directory did not return None")
        
    def test02NoGenerations(self):
        self.makeFile("foo.txt")
        gen_id = Generation.getLatestGenerationID(self.dir)
        self.failUnlessEqual(gen_id, None, "Directory with no Generations did not return None")
        
    def test03FalseGenerations(self):
        self.makeFile("galileo")
        gen_id = Generation.getLatestGenerationID(self.dir)
        self.failUnlessEqual(gen_id, None, "Directory with false Generation did not return None")
        
    def test04FailedDir(self):
        self.makeDir("g0001")
        gen_id = Generation.getLatestGenerationID(self.dir)
        self.failUnlessEqual(gen_id, None, "Directory with failed Generation did not return None")

    def test05Ordering(self):
        self.makeDir("g0001", with_pkl=1)
        self.makeDir("g0002", with_pkl=1)
        gen_id = Generation.getLatestGenerationID(self.dir)
        self.failUnless(gen_id == 2, "Generation found was not the latest:  %s" % (gen_id))

    def test06Fallback(self):
        self.makeDir("g0001", with_pkl=1)
        self.makeDir("g0002")
        gen_id = Generation.getLatestGenerationID(self.dir)
        self.failUnless(gen_id == 1, "Generation found was not the latest successfull one:  %s" % (gen_id))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test01LatestGeneration']
    unittest.main()