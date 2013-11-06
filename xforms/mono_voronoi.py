'''
Created on Aug 5, 2010

@author: hmp@drzeus.best.vwh.net
'''
import string
import _xformer
import random

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
        ret = img.copy()
        pts = []
        for i in range(self.args["points"]):
            pt = _voronoi.Site(random.randint(1, img.size[0]-1), random.randint(1, img.size[1]-1))
            pts.append(pt)
        context = _voronoi.computeVoronoiDiagram(pts)
        draw = ImageDraw.Draw(ret)
        for (pti, edges) in context.polygons.items():
            vchain = []
            i = 0
            while (len(edges) > 0 and i < 1000):
                (l, v1, v2) = edges.pop(0)
                if (v1 < 0 or v2 < 0):
                    continue
                i = i + 1
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
                        edges.append((l, v1, v2))
            vv = []
            for v in vchain:
                vv.append(context.vertices[v])
            pt = pts[pti]
            if (len(vv) > 2):
                draw.polygon(vv, outline=(0, 0, 0), fill=img.getpixel((pt.x, pt.y)))
            #draw.ellipse((pt.x-2, pt.y-2, pt.x+2, pt.y+2), fill=(255, 0, 0))
        return ret
    
    def tweakInner(self):
        self.args["points"] = random.randint(100, 2000)
        
    def getExamplesInner(self, imgs):
        exs = []
        for p in [100, 1000, 2000]:
            self.args["points"] = p
            print "%s..." % (self)
            exs.append(self.getExampleImage(imgs))
        return exs
    
