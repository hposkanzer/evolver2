#!/usr/local/bin/python

import cgi
import os
import sys
import getopt
import traceback
import string
import logging

import Location
import Picklable
import Experiment

from twython import Twython


def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s [--debug] [--s3] [--no-op] [name]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  s3:  Keep thumbnails on S3.\n")
    sys.stderr.write( "  no-op:  Do not generate creatures or preserve state.\n")
    sys.stderr.write( "  name:  Create this experiment name.  If not provided, a name is generated.\n")
    sys.exit(-1)
    
    
def main():
    
    try:

        Experiment.initLogging(False)
        
        # Command line.  All the output is still CGI-ish, though.  Sorry.
        (odict, args) = getOptions()
        (odict, args) = processOptions(odict, args)
            
        if args:
            exp = newExperiment(odict, args[0])
        else:
            exp = newExperiment(odict)
        creature = newCreature(odict, exp)
        tweet(creature)

    except:
        msg = string.join(apply( traceback.format_exception, sys.exc_info() ), "")
        if (msg[-1] == "\n"):
            msg = msg[:-1]
        logging.getLogger().warning(msg)
        data = "Huh?\n%s" % (msg)
        print data


def newExperiment(odict, name=None):
    
    exp = Experiment.Experiment(name)
    exp.initialize(not odict.get("s3", False), 
                   odict.get("no-op", False), 
                   odict.get("debug", False), 
                   odict.get("tile-mode", False), 
                   odict.get("reflect-mode", False), 
                   odict.get("grid-mode", False))
    return exp


def newCreature(odict, exp):
    
    creature = exp.newCreature(None)
    return creature
    

def tweet(creature):
    
    logging.getLogger().info("Posting %s as %s..." % (creature.getImagePath(), creature.getFullPageURL()))
    f = open(Location.getInstance().toAbsolutePath(".twitter.json"))
    creds = Location.getJsonModule().load(f)
    f.close()
    twitter = Twython(creds["app"], creds["app_secret"], creds["token"], creds["token_secret"])
    photo = open(creature.getImagePath(), 'rb')
    response = twitter.upload_media(media=photo)
    response = twitter.update_status(status=creature.getFullPageURL(), media_ids=[response['media_id']])
    logging.getLogger().info("Posted as %s." % (response["id_str"]))
    

def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help", "debug", "s3", "no-op"] )
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
        
    if odict.has_key("s3"):
        odict["s3"] = True
        
    if odict.has_key("no-op"):
        odict["no-op"] = True

    return (odict, args)


def processOptions(odict, args):

    if (len(args) > 1):
        usage()
        
    if ((len(args) > 0) and not Picklable.isValidID(args[0])):
        raise Picklable.InvalidID(args[0])
    
    if odict.has_key("debug"):
        logging.getLogger().setLevel(logging.DEBUG)
        
    odict["grid-mode"] = True
        
    return (odict, args)


if __name__ == '__main__':
    main()
