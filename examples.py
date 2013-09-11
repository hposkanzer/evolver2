#!/usr/bin/env python
'''
Created on Aug 8, 2010

@author: hmp@drzeus.best.vwh.net
'''
import os
import ImageLoader
import TransformLoader
import SrcImage
import re
import random

examples_dir = "examples"
src_pat = re.compile("_src\d.jpg")

class ExampleGenerator:

    srcimgs = []
    xforms = []
    non_transformer = None
    
    def generateExamples(self):
        self.loadImages()
        self.loadTransforms()
        inputs = []
        for img in self.srcimgs:
            inputs.append(self.non_transformer(img))
        for i in range(len(self.xforms)):
            xform_cls = self.xforms[i]
            print "%d/%d:  %s..." % (i+1, len(self.xforms), xform_cls.__name__)
            xform = xform_cls()
            imgs = xform.getExamples(inputs)
            for j in range(len(imgs)):
                img = imgs[j]
                fname = os.path.join(examples_dir, "%s%02d.jpg" % (xform.__class__.__name__, j))
                img.save(fname)

    def loadImages(self):
        if not self.srcimgs:
            il = ImageLoader.ImageLoader()
            l = il.loadNames(examples_dir)
            l = filter(lambda x: src_pat.match(os.path.basename(x)), l)
            for fpath in l:
                self.srcimgs.append(SrcImage.SrcImage(fpath))
            random.shuffle(self.srcimgs)

    def loadTransforms(self):
        if not self.xforms:
            xl = TransformLoader.TransformLoader()
            self.xforms = xl.loadAll("xforms")
            self.non_transformer = xl.getNonTransformer()


def main():
    
    eg = ExampleGenerator()
    eg.generateExamples()
    

if __name__ == "__main__":
    main()