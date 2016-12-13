#!/usr/bin/python

import os
import sys
import getopt
import shutil

def usage( msg=None ):
    if msg:
        sys.stderr.write( "ERROR:  %s\n" % (msg) )
    sys.stderr.write( "Usage:  %s fav [...]\n" % (os.path.basename(sys.argv[0])) )
    sys.stderr.write( "  fav:  One or more gallery files to dereference.\n")
    sys.exit(-1)
    
    
def main():
    
    (odict, args) = getOptions()
    (odict, args) = processOptions(odict, args)
        
    result = findFavs(args)
    ll = []
    for (creature, exp) in result.items():
        ll.append(os.path.join("exps", exp, "creatures", creature))
    ll.sort()
    print "\n".join(ll)


def findFavs(favs):
    result = {}
    for fav in favs:
        exp = findExp(os.path.splitext(os.path.basename(fav))[0])
        if exp != None:
            result[fav] = exp
    return result

    
def findExp(fav):
    for exp in os.listdir("exps"):
        creatures = os.listdir(os.path.join("exps", exp, "creatures"))
        creatures = filter(lambda x: x.endswith(".pkl"), creatures)
        creatures = map(lambda x: os.path.splitext(x)[0], creatures)
        if fav in creatures:
            return exp
    else:
        return None
            
    
def getOptions():
    
    try:
        (tt, args) = getopt.getopt( sys.argv[1:], "h", ["help"] )
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

    if (len(args) <= 0):
        usage()
        
    return (odict, args)


if __name__ == '__main__':
    main()
