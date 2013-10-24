import os
import random
import string
import cPickle
import time

import Picklable

##################################################################
class NoSuchCreature(Exception):
    def __init__(self, creature):
        Exception.__init__(self)
        self.creature = creature
    def __str__(self):
        return str(self.creature)

##################################################################
class Creature(Picklable.Picklable):

    def __init__(self, experiment, name=None):
        Picklable.Picklable.__init__(self)
        self.experiment = experiment
        self.id = name or self.generateID()
        self.head = None
        self.ancestorName = ""
        self.hidden = False

        
    def __str__(self):
        return "Creature(%s)" % (self.id)
    
    def getID(self):
        return self.id
    
    def getName(self):
        return self.getID()
    
    def getImageName(self):
        return "%s.jpg" % (self.getName())
    
    def getPageName(self):
        return "%s.html" % (self.getName())
    
    def getThumbName(self):
        return "%s.t.jpg" % (self.getName())
    
    def getPickleName(self):
        return "%s.pkl" % (self.getName())
    
    def getPageURL(self):
        return self.experiment.getCreaturesDir(False) + "/" + self.getPageName()

    def getImageURL(self):
        return self.experiment.getCreaturesDir(False) + "/" + self.getImageName()

    def getThumbURL(self):
        abspath = os.path.join(self.experiment.getCreaturesDir(), self.getThumbName())
        url = self.experiment.tn.getURL(abspath)
        return url
    
    def getGalleryURL(self):
        url = "/cgi-bin/gallery.py?e=%s&c=%s" % (self.experiment.getName(), self.getName())
        if self.experiment.getConfig()["local_only"]:
            url = url + "&local-only=1"
        return url
    
    def getInfo(self):
        ret = {
           "name" : self.getName(),
           "page_url" : self.getPageURL(),
           "image_url" : self.getImageURL(),
           "thumb_url" : self.getThumbURL(),
           "parent" : self.ancestorName or None,
           "gallery_url" : self.getGalleryURL(),
           "hidden" : self.hidden,
           }
        return ret


    #################################################################
    def conceive(self, depth):
        self.logger.debug("Conceiving %s..." % (self))
        self.head = self.makeGenome(depth)
        if (self.experiment.config["reflect_mode"]):
            reflect = self.experiment.getReflectTransformer()
            reflect.addInput(self.head)
            self.head = reflect
        
        
    #################################################################
    def hide(self):
        self.logger.debug("Hiding %s..." % (self))
        self.hidden = True
        self.saveConfig()

    
    #################################################################
    def evolve(self):
        self.logger.debug("Evolving %s..." % (self))
        self.mutate()
        self.tweak()
        
        
    #################################################################
    def mutate(self):
        if (random.random() <= self.experiment.getConfig()["mutation_rate"]):
            mutation_funcs = [
                              "insertTransformer",
                              "deleteTransformer",
                              "swapTransformers",
                              ]
            getattr(self, random.choice(mutation_funcs))()
        else:
            self.logger.debug("%s did not mutate." % (self))

        
    def insertTransformer(self):
        
        # Pick a transformer to insert after.
        l = self.getTransformerPairs()
        if (len(l) == 0):
            # Only the reserved transformers!
            # In this case, we'll actually insert the new transformer *after* the srcimg.
            (prev, xform) = (None, self.head)
        else:
            (prev, xform) = random.choice(l)
        
        # Pick an input to insert before.
        inputs = xform.getInputs()  # Returns a copy
        i = random.choice(range(len(inputs)))

        # Generate a new transformer.
        next = self.experiment.getRandomTransform()
        # Add the old input to it.
        if (len(l) == 0):
            next.addInput(xform)
        else:
            next.addInput(inputs[i])
        # Fill in any remaining inputs with new source images.
        for j in range(1, next.getExpectedInputCount()):
            next.addInput(self.getRandomSrcImage())
        
        # Insert the new transformer.
        if (len(l) == 0):
            self.head = next
            self.logger.debug("Inserted %s after %s." % (next, xform))
        else:
            inputs[i] = next
            xform.setInputs(inputs)
            # We say "before" because genomes are evaluated in bottom-up order.
            self.logger.debug("Inserted %s before %s." % (next, xform))
    
    
    def deleteTransformer(self):

        # Pick a transformer to delete.
        l = self.getTransformerPairs()
        if (len(l) == 0):
            # Only the reserved transformers!
            # Better abort
            return
        (prev, xform) = random.choice(l)
        
        # Pick one of its inputs to pop up.
        inputs = xform.getInputs()  # Returns a copy
        next = random.choice(inputs)

        # Replace the transformer in the previous transformer's inputs.
        self.replaceInput(prev, xform, next)
        
        self.logger.debug("Deleted %s, popped up %s." % (xform, next))
    
    
    def swapTransformers(self):
        
        # Pick two transformers to swap.
        l = self.getTransformerPairs()
        if (len(l) <= 1):
            return
        (prev1, xform1) = random.choice(l)
        xform2 = xform1
        while (xform2 == xform1):
            (prev2, xform2) = random.choice(l)
        
        # Swap the inputs.
        inputs1 = xform1.getInputs()  # Returns a copy
        inputs2 = xform2.getInputs()  # Returns a copy
        min_inputs = min(len(inputs1), len(inputs2))
        start = random.randint(0, min_inputs-1)
        for i in range(min_inputs):
            i1 = (start + i) % len(inputs1)
            i2 = (start + i) % len(inputs2)
            input1 = inputs1[i1]
            if (input1 == xform2):
                input1 = xform1
            input2 = inputs2[i2]
            if (input2 == xform1):
                input2 = xform2
            inputs1[i1] = input2
            inputs2[i2] = input1
        xform1.setInputs(inputs1)
        xform2.setInputs(inputs2)
 
        # Replace the transformers in the previous transformers' inputs.
        self.replaceInput(prev1, xform1, xform2)
        self.replaceInput(prev2, xform2, xform1)

        self.logger.debug("Swapped %s and %s." % (xform1, xform2))
    
    
    def replaceInput(self, prev, old_input, new_input):
        if (prev == None):
            self.head = new_input
        else:
            inputs = prev.getInputs()  # Returns a copy
            for i in range(len(inputs)):
                if (inputs[i] == old_input):
                    inputs[i] = new_input
                    break
            prev.setInputs(inputs)

    
    # Returns a list of (parent, child) pairs of transformers.
    # Parent will be None if Child is the head transformer.
    # NonTransformers, TileTransformers, and ReflectTransformers are not included.
    def getTransformerPairs(self):
        return self.head.getPairs()
        
    #################################################################
    def tweak(self):
        self.head.tweak(self.experiment.getConfig()["tweak_rate"])
    
    
    #################################################################
    def run(self):
        self.logger.debug("====> Running %s..." % (self))
        self.logger.debug("Genome:\n" + self.toString())
        if self.experiment.getConfig()["no_op"]:
            qm = os.path.join(self.experiment.getDir(), self.experiment.question_mark)
            imagepath = os.path.join(self.experiment.getCreaturesDir(), self.getImageName())
            thumbpath = os.path.join(self.experiment.getCreaturesDir(), self.getThumbName())
            self.experiment.linkOrCopy(qm, imagepath)
            self.experiment.linkOrCopy(qm, thumbpath)
            if not self.experiment.getConfig()["local_only"]:
                self.experiment.tn.uploadThumb(thumbpath)
            self.writeEmptyPage()
            #time.sleep(5)
        else:
            img = self.head.transform(self.experiment)
            self.writeImage(img)
            self.writeThumb(img)
            self.writePage()
        self.saveConfig()
    
    
    def writeImage(self, img):
        fname = os.path.join(self.experiment.getCreaturesDir(), self.getImageName())
        img.save(fname)
        
        
    def writeThumb(self, img):
        fname = os.path.join(self.experiment.getCreaturesDir(), self.getThumbName())
        self.experiment.tn.makeThumb(img, fname)

    
    def writePage(self):
        fname = os.path.join(self.experiment.getCreaturesDir(), self.getPageName())
        self.logger.debug("Creating page for %s..." % (self))
        f = open(fname, "w")
        f.write("<html>\n<head><title>Experiment %s, Creature %s</title>\n" % (self.experiment.getName(), self.getID()))
        f.write('<link rel="stylesheet" type="text/css" href="../../../gallery.css" />\n')
        f.write("</head>\n<body>\n")
        f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../../index.html'>Photo Evolver 2</a> &gt; <a href='../index.html'>Experiment</a></font>\n")
        f.write("<center>\n<h2>Creature %s</h2>\n" % (self.getID()))
        f.write("<table><tr valign='center'>\n")
        f.write("<td align='center'>\n")
        f.write("<img class='image' src='%s'>" % (self.getImageName()))
        f.write("\n</td>\n")
        f.write("</tr></table>\n")
        width = self.experiment.config["img_width"] / 2
        f.write("<p>\n")
        f.write("<center><b>Genome:</b>\n%s</center>\n" % (self.getGenomeFragment()))
        if self.ancestorName:
            f.write("<p><center><b>Ancestry:</b>\n%s\n</center>\n" % (self.getAncestorFragment()))
        f.write("</center>\n</body>\n</html>\n")
        f.close()


    def writeEmptyPage(self):
        fname = os.path.join(self.experiment.getCreaturesDir(), self.getPageName())
        self.logger.debug("Creating empty page for %s..." % (self))
        f = open(fname, "w")
        f.write("<html>\n<head><title>Experiment %s, Creature %s</title></head>\n<body></body></html>" % (self.experiment.getName(), self.getID()))
        f.close()


    def getGenomeFragment(self):
        l = []
        l.append("<table class='genomeTable'>")
        rows = map(lambda x: [], range(self.head.getDepth()))
        self.getGenomeFragmentInner(rows, self.head)
        for row in rows:
            l.append("<tr align='center'>")
            for td in row:
                l.append("%s" % (td))
            l.append("</tr>")
        l.append("</table>")
        return string.join(l, "\n")
    
    
    def getGenomeFragmentInner(self, rows, xform, i=0):
        if xform.is_non_transformer:
            srcimg = xform.getSrcImage()
            # Source image thumbnails are always served from the base srcimg dir.
            fpath = self.experiment.getSrcImageDir(False) + "/" + srcimg.getThumbName()
            src = self.experiment.tn.getURL(fpath)
            # And link to the local copy.
            href = "../%s/%s" % (self.experiment.getSrcImageDir(False), srcimg.getPageName())
            tdData = "<a href='%s'><img class='linkedthumb' src='%s'><br>%s</a>" % (href, src, srcimg.getFilename())
            tdClass = "genomeCell srcimgCell"
            # Fill below us to the bottom of the table with empty cells.
            for j in range(i+1, len(rows)):
                rows[j].append("<td></td>")
        else:
            name = xform.__class__.__name__
            # Thumbnails come from the local creatures dir.
            fpath = self.experiment.getCreaturesDir() + "/" + xform.getThumbName()
            src = self.experiment.tn.getURL(fpath)
            if xform.is_reserved_transformer:
                # No link.
                tdData = "<img class='thumb' src='%s'><br>%s%s" % (src, name, xform.getArgsString())
            else:
                # Link to the local copy of the filter example.
                href = "../%s/index.html#%s" % (self.experiment.examples_dir, name)
                tdData = "<img class='thumb' src='%s'><br><a href='%s'>%s</a>%s" % (src, href, name, xform.getArgsString())
            tdClass = "genomeCell"
            if (len(xform.inputs) > 1):
                # Add a line across the bottom.
                tdClass = tdClass + " srcimgCell"
            # Push all the children onto their rows.
            for input in xform.inputs:
                self.getGenomeFragmentInner(rows, input, i+1)
        # Push us onto our row.
        rows[i].append("<td class='%s' colspan=%d>%s</td>" % (tdClass, xform.getWidth(), tdData))


    def getAncestorFragment(self):
        l = []
        l.append("<table class='ancestorTable'>")
        ancestorName = self.ancestorName
        while (ancestorName):
            creature = self.__class__(self.experiment, ancestorName)
            creature.loadConfig()
            l.append("<tr><td class='ancestorCell'><a href='%s'><img class='linkedthumb' src='%s'></a></td></tr>" % (creature.getPageName(), creature.getThumbURL()))
            ancestorName = creature.ancestorName
        l.append("</table>")
        return string.join(l, "\n")
        

    #################################################################
    def clone(self):
        new = self.__class__(self.experiment)
        new.ancestorName = self.getName()
        new.head = self.head.clone()
        self.logger.debug("Cloned %s from %s." % (new, self))
        return new
    
            
    #################################################################
    def makeGenome(self, depth):
        if (depth == 0):
            # Return the non-transformer
            xform = self.getRandomSrcImage()
        else:
            # Return some random transfomer
            xform = self.experiment.getRandomTransform()
            for i in range(xform.getExpectedInputCount()):
                xform.addInput(self.makeGenome(depth - 1))
        return xform
    
    
    def getRandomSrcImage(self):
        src = self.experiment.getNonTransformer()
        src.addInput(self.experiment.getRandomSrcImage())
        if (self.experiment.config["tile_mode"]):
            tile = self.experiment.getTileTransformer()
            tile.addInput(src)
            src = tile
        return src


    #################################################################
    def getGenome(self):
        return self.head.getGenome()
    
    def toString(self):
        return self.head.toString()
    

    #################################################################
    def __getstate__(self):
        d = Picklable.Picklable.__getstate__(self)
        del d["experiment"]
        return d

    def saveConfig(self):
        self.logger.debug("Persisting %s..." % (self))
        fname = os.path.join(self.experiment.getCreaturesDir(), self.getPickleName())
        f = open(fname, "w")
        cPickle.dump(self, f)
        f.close()
        
    
    def loadConfig(self):
        self.logger.debug("Depersisting %s..." % (self))
        fname = os.path.join(self.experiment.getCreaturesDir(), self.getPickleName())
        if not os.path.exists(fname):
            raise NoSuchCreature(self)
        f = open(fname)
        creature = cPickle.load(f)
        f.close()
        self.head = creature.head
        self.ancestorName = creature.ancestorName
        self.hidden = creature.hidden
        
    