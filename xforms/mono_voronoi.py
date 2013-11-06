'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import string
import _xformer
import random
import math

import ImageDraw
import _voronoi


#############################################################################
class Voronoi(_xformer._MonoTransformer):
    
    def __init__(self):
        _xformer._MonoTransformer.__init__(self)
        self.tweakInner()

    def getArgsString(self):
        return "(%d)" % (self.args["points"])

    def transformImage(self, img):
        return self.transformViaTriangulation(img)
        #return self.transformViaBruteForce(img)
    
    
    # Wicked slow.
    def transformViaBruteForce(self, img):
        ret = img.copy()
        imgx, imgy = img.size
        nx = []
        ny = []
        nc = []
        for i in range(self.args["points"]):
            nx.append(random.randrange(imgx))
            ny.append(random.randrange(imgy))
            nc.append(img.getpixel((ny[-1], ny[-1])))
        for y in range(imgy):
            for x in range(imgx):
                dmin = math.hypot(imgx-1, imgy-1)
                j = -1
                for i in range(self.args["points"]):
                    d = math.hypot(nx[i]-x, ny[i]-y)
                    if d < dmin:
                        dmin = d
                        j = i
                ret.putpixel((x, y), nc[j])
        #draw = ImageDraw.Draw(ret)
        #for i in range(len(nx)):
        #    draw.ellipse((nx[i]-2, ny[i]-2, nx[i]+2, ny[i]+2), fill=(255, 0, 0))
        return ret
    
    
    def transformViaTriangulation(self, img):
        
        # Make some points and calculate the Voronoi.
        pts = {}
        while (len(pts) < self.args["points"]):
            pt = _voronoi.Site(random.randint(0, img.size[0]-1), random.randint(0, img.size[1]-1))
            pts[(pt.x, pt.y)] = pt
        pts = pts.values()
        context = _voronoi.computeVoronoiDiagram(pts)

        ret = img.copy()
        draw = ImageDraw.Draw(ret)
        incompletes = {}  # l => (v1, v2)
        vplus = context.vertices[:]  # This gets appended with the calculated incompletes.
        for (pti, edges) in context.polygons.items():
            
            # Construct a chain of vertices
            vchain = []
            while (len(edges) > 0):
                (l, v1, v2) = edges.pop(0)
                if (v1 < 0 or v2 < 0):
                    # One vertex is at infinity.  Construct something closer.
                    if not incompletes.has_key(l):
                        self.addIncomplete(incompletes, context.lines, vplus, l, v1, v2)
                    (v1, v2) = incompletes[l]
                if (len(vchain) == 0):
                    vchain.append(v1)
                    vchain.append(v2)
                else:
                    if (vchain[0] == v1):
                        vchain.insert(0, v2)
                    elif (vchain[0] == v2):
                        vchain.insert(0, v1)
                    elif (vchain[-1] == v1):
                        vchain.append(v2)
                    elif (vchain[-1] == v2):
                        vchain.append(v1)
                    else:
                        # Can't connect it yet.
                        edges.append((l, v1, v2))
                
            # Translate the indices into coordinates.        
            vv = []
            for v in vchain:
                vv.append(vplus[v])
                
            # Fill a polygon with the value of the input point.
            pt = pts[pti]
            if (len(vv) > 2):
                draw.polygon(vv, outline=(0, 0, 0), fill=img.getpixel((pt.x, pt.y)))
            #draw.ellipse((pt.x-2, pt.y-2, pt.x+2, pt.y+2), fill=(255, 0, 0))
            
        return ret
    
    
    def addIncomplete(self, incompletes, lines, vplus, l, v1, v2):
        
        # Which one is our known vertex?
        if (v1 < 0):
            vi = v2
        else:
            vi = v1
        v = vplus[vi]
        
        # The line direction is not consistent, so we need to 
        # guess the correct direction by which quadrant we're in.
        (a, b, c) = lines[l]
        if (v[0] < self.getDims()[0]/2):
            sb = -abs(b)
            if (v[1] < self.getDims()[1]/2):
                sa = -abs(a)
            else:
                sa = abs(a)
        else:
            sb = abs(b)
            if (v[1] < self.getDims()[1]/2):
                sa = -abs(a)
            else:
                sa = abs(a)
                
        # Make a point far away on this line.
        ab = (v[0] + 200*sb, v[1] + 200*sa)
        vplus.append(ab)
        incompletes[l] = (vi, len(vplus)-1)
        #print v1, v2, v, incompletes[l], ab
    
    
    def tweakInner(self):
        self.args["points"] = random.randint(100, 4000)
        
    def getExamplesInner(self, imgs):
        exs = []
        for p in [100, 2000, 4000]:
            self.args["points"] = p
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    
