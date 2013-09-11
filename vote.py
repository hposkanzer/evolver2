#!/usr/local/bin/python
import re
import urlparse

import sys
import os
import string
import traceback
import time

base_dir = "/h/hmp/fun/best/htdocs/evolver"
if not os.path.isdir(base_dir):
    base_dir = "/usr/home/harold/www/htdocs/evolver"
    
    
def main():

    try:

        odict = os.environ
        content_type = "text/plain"
        data = getPage( odict )

    except:
        l = apply( traceback.format_exception, sys.exc_info() )
        data = "Huh?\n%s" % (string.join(l, ""))
        content_type = "text/plain"

    print "Content-type: %s" % (content_type)
    print "Content-length: %s" % (len(data))
    print
    print data
    if (data != "OK"):
        logError(data)
    
    
def logError(msg):
    f = open(os.path.join(base_dir, "vote.log"), "a")
    f.write("%s: %s\n" % (time.ctime(time.time()), msg))
    f.close()


def getPage( odict ):
    
    # http://kipple.cup.hp.com/fun/best/htdocs/evolver/exp000/g0000/c00.html
    ref = odict.get("HTTP_REFERER")
    if not ref:
        return "FAIL:  no referer"
    
    parts = urlparse.urlparse(ref)
    if (len(parts) < 3):
        return "FAIL:  %s" % (ref)
    path = parts[2]

    parts = string.split(path, "/")
    if (len(parts) < 3):
        return "FAIL:  %s" % (parts)
    exp = parts[-3]
    gen = parts[-2]
    cre = parts[-1]
    
    match = re.match("c(\d+)\.html", cre)
    if not match:
        return "FAIL:  %s" % (cre)
    cid = int(match.group(1))
    
    dir = os.path.join(base_dir, exp, gen)
    if not os.path.isdir(dir):
        return "FAIL:  dir not found"
    
    vote = "%s: %d\n" % (time.ctime(time.time()), cid)
    f = open(os.path.join(dir, "votes.txt"), "a")
    f.write(vote)
    f.close()
    
    return "OK"


##############################################################################################
if __name__ == "__main__":
    main()
