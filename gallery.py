#!/usr/bin/python

import cgi
import os
import sys
import getopt
import traceback
import string
import logging
import shutil

import Location
import Experiment
import Thumbnailer
import Picklable
import Creature
import SrcImage
import UsageError


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--s3] ([-e exp -c creature] | [-c creature])\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  exp:  The name of the experiment in which the creature exists.\n")
    sys.stderr.write( "  creature:  The name of the creature to show in the gallery.\n")
    sys.exit(-1)
    
    
def main():
    
    try:

        Experiment.initLogging(os.environ.has_key("GATEWAY_INTERFACE"))
        
        if os.environ.has_key("GATEWAY_INTERFACE"):
            # CGI
            (odict, args) = getCGIOptions()
        else:
            # Command line.  All the output is still CGI-ish, though.  Sorry.
            (odict, args) = getOptions()
        (odict, args) = processOptions(odict, args)
            
        if odict.has_key("e") or not odict.has_key("c"):
            data = getGallery(odict, odict.get("e"), odict.get("c"))
        else:
            data = getPage(odict, odict["c"], odict.get("p"), odict.get("n"))
        
        print "Content-type: text/html"
        print "Content-length: %s" % (len(data))
        print
        print data

    except:
        msg = string.join(apply( traceback.format_exception, sys.exc_info() ), "")
        if (msg[-1] == "\n"):
            msg = msg[:-1]
        logging.getLogger().warning(msg)
        data = "Huh?\n%s" % (msg)
        print "Status: 500 Internal Server Error"
        print "Content-type: text/plain"
        print "Content-length: %s" % (len(data))
        print
        print data


def getGallery(odict, exp=None, creature=None):
    
    gallery = Gallery(odict)    
    return gallery.getHTML(exp, creature)
    
    
# prev & next are currently ignored.
def getPage(odict, creature, prev=None, next=None):
    
    page = Page(odict)    
    return page.getHTML(creature, prev, next)

    
class Common:
    
    loc = Location.getInstance()
    gallery_dir = "gallery"
    base_url = "%s/%s" % (loc.base_url, gallery_dir)
    cgi_url = "/cgi-bin/gallery.py"
    max_creatures = 1000
    dir = os.path.join(loc.base_dir, gallery_dir)
    odict = {}
    tn = None
    
    def __init__(self, odict):
        self.odict = odict
        self.tn = Thumbnailer.Thumbnailer(666, not odict.has_key("s3"))
        self.logger = logging.getLogger(self.__class__.__name__)


    def getCreatures(self):
        l = filter(lambda x: x.endswith(".jpg") and not x.endswith(".t.jpg") , os.listdir(self.dir))
        l.sort()
        l.reverse()
        return l
    
    
    def getThumbHTML(self, creatureName=None):
        if not creatureName:
            return ""
        img = self.toImage(creatureName)
        abspath = os.path.join(self.dir, img)
        url = self.getThumbURL(abspath)
        lo = ""
        if (self.odict.has_key("s3")):
            lo = "&s3=1"
        return "<a href='%s?c=%s%s'><img class='linkedthumb' src='%s'></a>" % (self.cgi_url, creatureName, lo, url)

    
    def getThumbURL(self, abspath):
        return self.tn.getURL(self.toThumb(abspath))
    

    def toImage(self, name):
        return name + ".jpg"
    
    def toThumb(self, img):
        (root, ext) = os.path.splitext(img)
        return root + ".t" + ext
        
    def toName(self, img):
        return os.path.splitext(img)[0]
    
    
class Gallery(Common):
    
    columns = 5
    
    def getHTML(self, expName=None, creatureName=None):
        if expName and creatureName:
            exp = Experiment.Experiment(expName)
            creature = exp.getCreature(creatureName)
            self.addCreature(creature)
        else:
            creature = None
        html = self.getHeader()
        imgs = self.getCreatures()
        html = html + self.getTable(imgs, creature)
        html = html + self.getFooter()
        return html
    
    
    def addCreature(self, creature):
        self.logger.info("Adding %s from %s..." % (creature, creature.experiment))
        # Won't work on Windows!
        src = os.path.join(creature.experiment.getCreaturesDir(), creature.getImageName())
        if not os.path.exists(src):
            raise Creature.NoSuchCreature(creature)
        dst = os.path.join(self.dir, creature.getImageName())
        if os.path.exists(dst):
            return
        shutil.copyfile(src, dst)
        
        
    def getTable(self, imgs, newCreature=None):
        html = []
        html.append("<center>")
        html.append("<table border=0 cellpadding=10>")
        html.append("<tr>")
        i = 0;
        for img in imgs:
            if ((i > 0) and (i % self.columns == 0)):
                html.append("</tr><tr>")
            idStr = ""
            if (newCreature and (img == newCreature.getImageName())):
                idStr = "id='newthumb'"
            html.append("<td %s>%s</td>" % (idStr, self.getThumbHTML(self.toName(img))))
            i = i + 1
        html.append("</tr>")  # Might end up with an empty row at the bottom.  Big deal.
        html.append("</table>")
        html.append("</center>")
        return "\n".join(html) + "\n"
    
    
    def getHeader(self):
        html = """<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml" />
<title>Evolver 2 Gallery</title>
<link rel="stylesheet" type="text/css" href="%s/gallery.css" />
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
<script type="text/javascript" src="%s/jquery.scrollTo-1.4.2-min.js"></script>
<script type="text/javascript">
$(document).ready(init);
function init() {
    $.scrollTo($('#newthumb'), 400);
}
</script>
</head>
<body>
<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='%s'>Photo Evolver 2</a> &gt; Gallery</font><p>
""" % (self.loc.base_url, self.loc.base_url, self.loc.base_url)
        return html

    def getFooter(self):
        html = """
</body>
</html>
"""
        return html
       
       
class Page(Common):
    
    # prev & next are currently ignored.
    def getHTML(self, creatureName, prevName=None, nextName=None):
        html = self.getHeader(creatureName)
        if (not prevName or not nextName):
            imgs = self.getCreatures()
            (prevName, nextName) = self.getNeighbors(creatureName, imgs)
        html = html + self.getTable(creatureName, prevName, nextName)
        html = html + self.getFooter()
        return html


    def getTable(self, creatureName, prevName=None, nextName=None):
        html = []
        html.append("<center><table><tr valign='center'>")
        html.append("<td width='150'>%s</td>" % (self.getThumbHTML(prevName))) 
        html.append("<td align='center'><img class='image' src='%s/%s'></td>" % (self.base_url, self.toImage(creatureName)))
        html.append("<td width='150'>%s</td>" % (self.getThumbHTML(nextName)))  
        html.append("</tr></table></center>")
        return "\n".join(html) + "\n"
    
    
    def getNeighbors(self, creatureName, imgs):
        (prev, next) = (None, None)
        img = self.toImage(creatureName)
        try:
            i = imgs.index(img)
        except ValueError:
            return (prev, next)
        prevI = i - 1
        if (prevI >= 0):
            prev = self.toName(imgs[prevI])
        nextI = i + 1
        if (nextI < len(imgs)):
            next = self.toName(imgs[nextI])
        return (prev, next)
    
        
    def getHeader(self, creatureName):
        lo = ""
        if (self.odict.has_key("s3")):
            lo = "?s3=1"
        html = """<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml" />
<title>Evolver 2 Gallery</title>
<link rel="stylesheet" type="text/css" href="%s/gallery.css" />
</head>
<body>
<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='%s'>Photo Evolver 2</a> &gt; <a href='%s%s'>Gallery</a> &gt; Creature %s</font><p>
""" % (self.loc.base_url, self.loc.base_url, self.cgi_url, lo, creatureName)
        return html

    def getFooter(self):
        html = """
</body>
</html>
"""
        return html
    
 
def getCGIOptions():
    
    odict = cgi.parse()
    args = []
    
    for opt in ["e", "c", "n", "p", "s3"]:
        if odict.has_key(opt):
            odict[opt] = odict[opt][0]
    
    return (odict, args)


def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "he:c:n:p:", ["help", "debug", "s3"] )
    except getopt.error:
        usage( str(sys.exc_info()[1]) )

    odict = {}
    for t in tt:
        s = t[0]
        while (s[0] == "-"):        # Strip leading '-'s
            s = s[1:]
        if not odict.has_key( s ):
            odict[s] = []
        odict[s] = t[1]

    if (odict.has_key("h") or odict.has_key("help")):
        usage()

    if odict.has_key("e") and not odict.has_key("c"):
        usage()
        
    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()
        
    for opt in ["e", "c", "n", "p"]:
        if odict.has_key(opt) and not Picklable.isValidID(odict[opt]):
            raise Picklable.InvalidID(odict[opt])
        
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    return (odict, args)


if __name__ == '__main__':
    main()
