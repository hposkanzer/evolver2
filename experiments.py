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
    sys.stderr.write( "Usage:  %s [--debug]\n" % (os.path.basename(sys.argv[0])) )
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
            
        data = getGallery()
        
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


def getGallery():
    
    gallery = Gallery()    
    return gallery.getHTML()
    
    
class Gallery:
    
    columns = 10
    loc = Location.getInstance()
    dir = Experiment.abs_dir
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def getExperiments(self):
        l = filter(lambda x: os.path.isdir(os.path.join(self.dir, x)), os.listdir(self.dir))
        l.sort()
        l.reverse()
        self.logger.info("Found %d experiments in %s." % (len(l), self.dir))
        return l
    
    def getExpHTML(self, exp):
        abspath = os.path.join(self.dir, exp)
        url = self.loc.toAbsoluteURL(abspath)
        return "<a href='%s'>%s</a>" % (url, exp)

    def getHTML(self):
        html = self.getHeader()
        exps = self.getExperiments()
        html = html + self.getTable(exps)
        html = html + self.getFooter()
        return html
    
    
    def getTable(self, exps):
        html = []
        html.append("<center>")
        html.append("<table border=0 cellpadding=10>")
        html.append("<tr>")
        i = 0;
        for exp in exps:
            if ((i > 0) and (i % self.columns == 0)):
                html.append("</tr><tr>")
            html.append("<td>%s</td>" % (self.getExpHTML(exp)))
            i = i + 1
        html.append("</tr>")  # Might end up with an empty row at the bottom.  Big deal.
        html.append("</table>")
        html.append("</center>")
        return "\n".join(html) + "\n"
    
    
    def getHeader(self):
        html = """<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml" />
<title>Evolver 2 Experiments</title>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
<script type="text/javascript" src="%s/jquery.scrollTo-1.4.2-min.js"></script>
</head>
<body>
<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='%s'>Photo Evolver 2</a> &gt; Experiments</font><p>
""" % (self.loc.base_url, self.loc.base_url)
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
    
    for opt in []:
        if odict.has_key(opt):
            odict[opt] = odict[opt][0]
    
    return (odict, args)


def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h:", ["help", "debug"] )
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

    return odict, args


def processOptions(odict, args):

    if (len(args) > 0):
        usage()
        
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    return (odict, args)


if __name__ == '__main__':
    main()
