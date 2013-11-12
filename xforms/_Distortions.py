""" Captcha.Visual.Distortions

Distortion layers for visual CAPTCHAs
"""
#
# PyCAPTCHA Package
# Copyright (C) 2004 Micah Dowty <micah@navi.cx>
#

import ImageDraw, Image
import random, math


class WigglyBlocks:
    """Randomly select and shift blocks of the image"""
    def __init__(self, blockSize=16, sigma=0.01, angle=-1, iterations=300):
        self.blockSize = blockSize
        self.sigma = sigma
        self.angle = angle
        self.iterations = iterations
        self.seed = random.random()

    def render(self, image):
        r = random.Random(self.seed)
        for i in xrange(self.iterations):
            # Select a block
            bx = int(r.uniform(0, image.size[0]-self.blockSize))
            by = int(r.uniform(0, image.size[1]-self.blockSize))
            block = image.crop((bx, by, bx+self.blockSize-1, by+self.blockSize-1))

            # Figure out how much to move it.
            # The call to floor() is important so we always round toward
            # 0 rather than to -inf. Just int() would bias the block motion.
            if (self.angle >= 0):
                m = r.normalvariate(0, self.sigma)
                mx = int(math.floor(math.cos(self.angle) * m))
                my = int(math.floor(math.sin(self.angle) * m))
            elif (self.angle == -1):
                mx = int(math.floor(r.normalvariate(0, self.sigma)))
                my = int(math.floor(r.normalvariate(0, self.sigma)))
            else:
                m = r.normalvariate(0, self.sigma)
                if ((bx - image.size[0]/2.0) == 0):
                    continue
                angle = math.atan((by - image.size[1]/2.0)/(bx - image.size[0]/2.0))
                mx = int(math.floor(math.cos(angle) * m))
                my = int(math.floor(math.sin(angle) * m))

            # Now actually move the block
            image.paste(block, (bx+mx, by+my))


class WarpBase:
    """Abstract base class for image warping. Subclasses define a
       function that maps points in the output image to points in the input image.
       This warping engine runs a grid of points through this transform and uses
       PIL's mesh transform to warp the image.
       """
    filtering = Image.BILINEAR
    resolution = 10
    debug = False

    def getTransform(self, image):
        """Return a transformation function, subclasses should override this"""
        return lambda x, y: (x, y)

    def render(self, image):
        
        r = self.resolution
        xPoints = image.size[0] / r + 2
        yPoints = image.size[1] / r + 2
        f = self.getTransform(image)
        
        # Overlay a grid
        if self.debug:
            draw = ImageDraw.Draw(image)
            for i in xrange(xPoints):
                draw.line((i*r,0,i*r,image.size[1]), (255,0,0))
            for i in xrange(yPoints):
                draw.line((0,i*r,image.size[0],i*r), (255,0,0))

        # Create a list of arrays with transformed points
        xRows = []
        yRows = []
        for j in xrange(yPoints):
            xRow = []
            yRow = []
            for i in xrange(xPoints):
                x, y = f(i*r, j*r)

                # Clamp the edges so we don't get black undefined areas
                x = max(0, min(image.size[0]-1, x))
                y = max(0, min(image.size[1]-1, y))

                xRow.append(x)
                yRow.append(y)
            xRows.append(xRow)
            yRows.append(yRow)

        # Create the mesh list, with a transformation for
        # each square between points on the grid
        mesh = []
        for j in xrange(yPoints-1):
            for i in xrange(xPoints-1):
                mesh.append((
                    # Destination rectangle
                    (i*r, j*r,
                     (i+1)*r, (j+1)*r),
                    # Source quadrilateral
                    (xRows[j  ][i  ], yRows[j  ][i  ],
                     xRows[j+1][i  ], yRows[j+1][i  ],
                     xRows[j+1][i+1], yRows[j+1][i+1],
                     xRows[j  ][i+1], yRows[j  ][i+1]),
                    ))

        return image.transform(image.size, Image.MESH, mesh, self.filtering)


class SineWarp(WarpBase):
    """Warp the image using a random composition of sine waves"""

    def __init__(self,
                 amplitude,
                 period,
                 offset
                 ):
        self.amplitude = amplitude
        self.period = period
        self.offset = offset

    def getTransform(self, image):
        return (lambda x, y,
                a = self.amplitude,
                p = self.period,
                o = self.offset:
                (math.sin( (y+o[0])*p )*a + x,
                 math.sin( (x+o[1])*p )*a + y))


class DomeWarp(WarpBase):
    """Warp the image using a dome"""

    def __init__(self,
                 amplitude,
                 wavelength
                 ):
        self.amplitude = amplitude
        self.wavelength = wavelength

    def getTransform(self, image):
        self.halfdims = (image.size[0]/2.0, image.size[1]/2.0)
        return self.transform
        
    def transform(self, x, y):
        a = self.amplitude
        h = self.halfdims
        w = self.wavelength
        d = math.hypot(x - h[0], y - h[1])
        return (x - a * math.sin(math.pi * (x - h[0]) / w) * abs(math.sin(math.pi * d / w)),
                y - a * math.cos(math.pi * (y - h[0]) / w) * abs(math.sin(math.pi * d / w)))
        

### The End ###
