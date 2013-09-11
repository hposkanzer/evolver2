'''
Created on Aug 10, 2010

@author: hmp@drzeus.best.vwh.net
'''
import unittest
import Picklable
import cPickle
import logging

class MyClass(Picklable.Picklable):
    
    def __init__(self):
        Picklable.Picklable.__init__(self)
        self.a = "a"
        
class Test(unittest.TestCase):


    def test01Picklable(self):
        obj1 = MyClass()
        s = cPickle.dumps(obj1)
        obj2 = cPickle.loads(s)
        self.failUnless(hasattr(obj2, "a"), "Unpickled object has no attribute 'a'")
        self.failUnless(obj2.a == "a", "Unpickled object.a is not 'a':  %s" % (obj2.a))
        self.failUnless(hasattr(obj2, "logger"), "Unpickled object has no attribute 'logger'")
        self.failUnless(isinstance(obj2.logger, logging.Logger), "Unpickled object.logger is not a Logger:  %s" % (obj2.logger))
        self.failUnless(obj2.logger.name == obj2.__class__.__name__, "Unpickled object.logger's name is not class name:  %s" % (obj2.logger.name))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test01Picklable']
    unittest.main()