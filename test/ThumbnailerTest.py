import unittest
import Thumbnailer
import Location

class LocalTest(unittest.TestCase):

    def setUp(self):
        self.loc = Location.Location()
        self.tn = Thumbnailer.Thumbnailer(150, True)

    def tearDown(self):
        self.tn = None

    def testRelative(self):
        url = self.tn.getURL("foo")
        self.assertEqual(url, self.loc.base_url + "/foo")

    def testAbsolute(self):
        url = self.tn.getURL(self.loc.base_dir + "/foo")
        self.assertEqual(url, self.loc.base_url + "/foo")

    def testRelativeBackslash(self):
        url = self.tn.getURL("foo\\bar")
        self.assertEqual(url, self.loc.base_url + "/foo/bar")

    def testAbsoluteBackslash(self):
        url = self.tn.getURL(self.loc.base_dir + "\\foo\\bar")
        self.assertEqual(url, self.loc.base_url + "/foo/bar")


class RemoteTest(unittest.TestCase):

    def setUp(self):
        self.loc = Location.Location()
        self.tn = Thumbnailer.Thumbnailer(150, False)

    def tearDown(self):
        self.tn = None

    def testRelative(self):
        url = self.tn.getURL("foo")
        self.assertEqual(url, self.loc.s3_base_url + "/foo")

    def testAbsolute(self):
        url = self.tn.getURL(self.loc.base_dir + "/foo")
        self.assertEqual(url, self.loc.s3_base_url + "/foo")

    def testRelativeBackslash(self):
        url = self.tn.getURL("foo\\bar")
        self.assertEqual(url, self.loc.s3_base_url + "/foo/bar")

    def testAbsoluteBackslash(self):
        url = self.tn.getURL(self.loc.base_dir + "\\foo\\bar")
        self.assertEqual(url, self.loc.s3_base_url + "/foo/bar")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()