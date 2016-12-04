import os
import sys
import string

instance = None
home_base = "/Users/hmp/Documents/best/www/evolver2"
prod_base = "/home/drzeus/www/evolver2"

sys.path.append(home_base)
sys.path.append(prod_base)

def getInstance():
    global instance
    if not instance:
        instance = Location()
    return instance


def getJsonModule():
    try:
        import json
        return json
    except ImportError:
        sys.path.append(os.path.expanduser("~/lib/simplejson-2.1.3"))
        import simplejson
        return simplejson


class Location:
    
    def __init__(self):
    
        self.project_name = "evolver2"

        # Home Mac
        self.base_dir = home_base
        self.base_url = "http://localhost:8080/%s" % (self.project_name)
        if not os.path.isdir(self.base_dir):
            # Production
            self.base_dir = prod_base
            self.base_url = "http://drze.us/%s" % (self.project_name)
        # Amazon S3
        self.s3_base_url = "http://drzeus.s3.amazonaws.com/%s" % (self.project_name)
    
    
    def toRelativePath(self, abspath):
        relpath = string.replace(abspath, self.base_dir, "")
        if (relpath[0] in ["/", "\\"]):
            relpath = relpath[1:]
        return relpath
    
    def toAbsolutePath(self, relpath):
        return os.path.join(self.base_dir, relpath)
    
    def toRelativeURL(self, path):
        path = self.toRelativePath(path)
        path = string.replace(path, os.path.sep, "/")
        return path

    def toAbsoluteURL(self, path, local=True):
        path = self.toRelativeURL(path)
        if local:
            base_url = self.base_url
        else:
            base_url = self.s3_base_url
        return "%s/%s" % (base_url, path)
    


        
