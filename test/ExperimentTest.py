import unittest
import tempfile
import os
import Experiment

class TestAllExperiments(unittest.TestCase):


    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.fnames = []

    def tearDown(self):
        self.fnames.reverse()
        for fname in self.fnames:
            path = os.path.join(self.dir, fname)
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
        os.rmdir(self.dir)


    def test01EmptyDir(self):
        l = Experiment.getAllExperiments(self.dir)
        self.assertEquals(l, [], "Found experiments in empty directory")
        
    def test02NoExperiments(self):
        self.makeFile("foo.txt")
        l = Experiment.getAllExperiments(self.dir)
        self.assertEquals(l, [], "Found experiments in directory with no experiments")
        
    def test03Experiments(self):
        self.makeDir("1234")
        self.makeDir("exp0001")
        l = Experiment.getAllExperiments(self.dir)
        self.assertEquals(l, ["1234", "exp0001"])
        
    def test03Mixed(self):
        self.makeDir("1234")
        self.makeFile("foo.txt")
        self.makeDir("exp0001")
        l = Experiment.getAllExperiments(self.dir)
        self.assertEquals(l, ["1234", "exp0001"])
        
    def test04HiddenDir(self):
        self.makeDir(".foo")
        self.makeDir("1234")
        l = Experiment.getAllExperiments(self.dir)
        self.assertEquals(l, ["1234"])
        
    def test05LoadConfig(self):
        self.makeDir("test")
        fname = os.path.join(self.dir, "test", "config.json")
        f = open(fname, "w")
        self.fnames.append(fname)
        f.write('{"key1":1, "key2":2}\n' )
        f.close()
        exp = Experiment.Experiment("test", self.dir)
        exp.loadConfig()
        conf = exp.getConfig()
        self.assertEquals(conf, {"key1":1, "key2":2})


    def makeFile(self, fname):
        open(os.path.join(self.dir, fname), "w").close()
        self.fnames.append(fname)

    def makeDir(self, dname):
        os.mkdir(os.path.join(self.dir, dname))
        self.fnames.append(dname)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test01LatestExperiment']
    unittest.main()