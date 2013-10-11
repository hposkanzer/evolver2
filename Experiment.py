import glob
import os
import random
import shutil
import time
import sys
import logging.handlers
import ConfigParser

sys.path.append(os.path.expanduser("~/lib/python/PIL/"))
sys.path.append("/usr/lib64/python2.3/site-packages/PIL")

import Location
import Creature
import ImageLoader
import Picklable
import SrcImage
import Thumbnailer
import TransformLoader

exps_dir = "exps"
abs_dir = Location.getInstance().toAbsolutePath(exps_dir)

class NoSuchExperiment(Exception):
    def __init__(self, exp):
        Exception.__init__(self)
        self.exp = exp
    def __str__(self):
        return str(self.exp)


################################################################
def initLogging(cgi=False):
    
    conf = ConfigParser.RawConfigParser()
    conf.read(Location.getInstance().toAbsolutePath("logging.conf"))
    
    logger = logging.getLogger()
    logger.setLevel(logging._levelNames[conf.get("logger_root", "level")]) # Weirdly, there's no supported method to get a level from a name...
    
    if cgi:
        # Make sure all created files are writable.
        os.umask(0)
    else:
        # Set up the console logger.
        formatter_name = conf.get("handler_consoleHandler", "formatter")
        format = conf.get("formatter_%s" % (formatter_name), "format")
        formatter = logging.Formatter(format)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set up the file logger.
    filename = Location.getInstance().toAbsolutePath(os.path.join("logs", conf.get("handler_logfileHandler", "filename")))
    max_bytes = conf.getint("handler_logfileHandler", "max_bytes")
    backup_count = conf.getint("handler_logfileHandler", "backup_count")
    formatter_name = conf.get("handler_logfileHandler", "formatter")
    format = conf.get("formatter_%s" % (formatter_name), "format")
    formatter = logging.Formatter(format)
    handler = logging.handlers.RotatingFileHandler(filename, "a", max_bytes, backup_count)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


################################################################
def getAllExperiments(dir=abs_dir):
    
    l = os.listdir(dir)
    l = filter(lambda x: os.path.isdir(os.path.join(dir,x)), l)
    l = filter(lambda x: x[0] != ".", l)
    l = map(os.path.basename, l)
    l.sort()
    return l


################################################################
class Experiment(Picklable.Picklable):
    
    question_mark = "qm.jpg"
    loading = "loading.gif"
    broken = "broken.jpg"
    more = "plus.png"
    delete_img = "delete.gif"
    mutate_img = "mutate.jpg"
    empty_img = "empty.gif"
    srcimg_dir = "srcimgs"
    xforms_dir = "xforms"
    creatures_dir = "creatures"
    examples_dir = "examples"
    
    def __init__(self, name, dir=abs_dir):
        Picklable.Picklable.__init__(self)
        self.name = name or self.generateID()
        self.dir = os.path.join(dir, self.name)
        self.config = {}
        self.srcimgs = []
        self.xforms = []
        self.non_transformer = None
        self.tile_transformer = None
        self.reflect_transformer = None
        self.tn = None
        

    ##############################################################
    def initialize(self, local_only=False, no_op=False, debug=False, tile_mode=False, reflect_mode=False):
        
        t0 = time.time()
        self.logger.info("Initializing %s..." % (self))
        os.mkdir(self.dir)
        
        # Grab the common stuff from the top dir.
        self.linkOrCopy(os.path.join(self.loc.base_dir, "evolver.html"), os.path.join(self.dir, "index.html"))
        self.copyFromBase(self.question_mark)
        self.copyFromBase(self.loading)
        self.copyFromBase(self.broken)
        self.copyFromBase(self.more)
        self.copyFromBase(self.delete_img)
        self.copyFromBase(self.mutate_img)
        self.copyFromBase(self.empty_img)
        # For now we're going to use the same set of images & xforms for every experiment.
        self.copyFromBase(self.srcimg_dir)
        self.copyFromBase(self.xforms_dir)
        self.copyFromBase(self.examples_dir)
        # Create the directory for all the creatures.
        os.mkdir(self.getCreaturesDir())
        # Generate the initial conf file.
        self.initConfig(local_only, no_op, debug, tile_mode, reflect_mode)
        
        t1 = time.time()
        self.logger.debug("%s complete in %.2f seconds." % (self, t1-t0))
        
        
    ##############################################################
    def reset(self):
        self.logger.info( "Resetting %s..." % (self) )
        if os.path.exists(self.getCreaturesDir()):
            self.logger.debug( "Removing %s/%s..." % (self.name, self.getCreaturesDir(False)) )
            shutil.rmtree(self.getCreaturesDir())
            os.mkdir(self.getCreaturesDir())
        
        
    ##############################################################
    def getCreatureState(self):
        t0 = time.time()
        self.logger.debug("Gathering creature state for %s..." % (self))
        self.loadConfig()
        if self.config["no_op"]:
            data = []
        else:
            self.loadTransforms()
            data = []
            for creature in self.getAllCreatures():
                creature.loadConfig()
                data.append(creature.getInfo())
        t1 = time.time()
        self.logger.debug("%s complete in %.2f seconds." % (self, t1-t0))
        return data
    
    
    def getAllCreatures(self):
        l = []
        fnames = glob.glob(os.path.join(self.getCreaturesDir(), "*.pkl"))
        fnames.sort()
        for fname in fnames:
            name = os.path.splitext(os.path.basename(fname))[0]
            l.append(Creature.Creature(self, name))
        return l
    
        
    ##############################################################
    def regenHTML(self):
        t0 = time.time()
        self.logger.info("Regenerating HTML for %s..." % (self))
        self.loadConfig()
        self.loadTransforms()
        for creature in self.getAllCreatures():
            creature.loadConfig()
            creature.writePage()
        t1 = time.time()
        self.logger.debug("%s complete in %.2f seconds." % (self, t1-t0))
        
        
    ##############################################################
    def newCreature(self, parentName=None):
        t0 = time.time()
        self.loadConfig()
        self.loadImages()
        self.loadTransforms()
        if parentName:
            parent = self.getCreature(parentName)
            self.logger.info("Evolving %s in %s..." % (parent, self))
            parent.loadConfig()
            creature = parent.clone()
            creature.evolve()
        else:
            self.logger.info("Creating new creature in %s..." % (self))
            creature = Creature.Creature(self)
            creature.conceive(random.randint(self.getConfig()["min_depth"], self.getConfig()["max_depth"]))
        creature.run()
        t1 = time.time()
        self.logger.info("%s in %s complete in %.2f seconds." % (creature, self, t1-t0))
        return creature


    def getCreature(self, name):
        return Creature.Creature(self, name)
    
    ##############################################################
    def hideCreature(self, creatureName):
        t0 = time.time()
        self.loadConfig()
        self.loadImages()
        self.loadTransforms()
        creature = self.getCreature(creatureName)
        self.logger.info("Hiding %s in %s..." % (creature, self))
        creature.loadConfig()
        creature.hide()
        t1 = time.time()
        self.logger.info("%s in %s complete in %.2f seconds." % (creature, self, t1-t0))
        return creature


    ##############################################################
    def loadImages(self):
        if self.srcimgs:
            return
        il = ImageLoader.ImageLoader()
        for fpath in il.loadNames(self.getSrcImageDir()):
            self.srcimgs.append(SrcImage.SrcImage(fpath))
            
            
    ##############################################################
    def loadTransforms(self):
        if self.xforms:
            return
        xl = TransformLoader.TransformLoader()
        xl.loadAll(os.path.join(self.dir, self.xforms_dir))
        self.xforms = xl.getTransforms()
        self.xforms.sort(lambda a, b: cmp(a.__name__, b.__name__))
        self.non_transformer = xl.getNonTransformer()
        self.tile_transformer = xl.getTileTransformer()
        self.reflect_transformer = xl.getReflectTransformer()
        
        
    ##############################################################
    def getName(self):
        return self.name
    
    def getID(self):
        return self.getName()
    
    def getURL(self):
        return self.loc.toAbsoluteURL(self.getURLPath())
    
    def getURLPath(self):
        return "%s/%s" % (exps_dir, self.name)

    def getDir(self):
        return self.dir
    
    def getSrcImageDir(self, abs=True):
        if abs:
            return os.path.join(self.dir, self.srcimg_dir)
        else:
            return self.srcimg_dir 

    def getSrcImages(self):
        return self.srcimgs
    
    def getRandomSrcImage(self):
        return random.choice(self.srcimgs)
    
    def getTransforms(self):
        return self.xforms
    
    def getRandomTransform(self):
        xform = random.choice(self.xforms)()
        return xform
    
    def getNonTransformer(self):
        xform = self.non_transformer()
        return xform
    
    def getTileTransformer(self):
        xform = self.tile_transformer()
        return xform
    
    def getReflectTransformer(self):
        xform = self.reflect_transformer()
        return xform
    
    def getCreaturesDir(self, abs=True):
        if abs:
            return os.path.join(self.dir, self.creatures_dir)
        else:
            return self.creatures_dir
    
    def getExamplesDir(self, abs=True):
        if abs:
            return os.path.join(self.dir, self.examples_dir)
        else:
            return self.examples_dir

    
    def __str__(self):
        return "Experiment(%s)" % (self.name)
    
    
    ##############################################################
    def initConfig(self, local_only=False, no_op=False, debug=False, tile_mode=False, reflect_mode=False):
        # For now, we'll copy the default values.
        src = self.loc.toAbsolutePath(self.conf_file)
        dst = os.path.join(self.dir, self.conf_file)
        self.logger.debug("Copying %s to %s..." % (src, dst))
        shutil.copy(src, dst)
        self.loadConfig()
        # Insert the Experiment-specific stuff.
        self.config["name"] = self.name
        self.config["local_only"] = local_only
        self.config["no_op"] = no_op
        self.config["debug"] = debug
        self.config["tile_mode"] = tile_mode
        self.config["reflect_mode"] = reflect_mode
        # Write the config back to disk.
        self.saveConfig()
        
    def loadConfig(self):
        fname = os.path.join(self.dir, self.conf_file)
        if not os.path.exists(fname):
            raise NoSuchExperiment(self)
        self.config = Picklable.Picklable.loadConfig(self, fname)
        self.config["local_only"] = self.config.get("local_only", False)
        self.config["no_op"] = self.config.get("no_op", False)
        self.tn = Thumbnailer.Thumbnailer(self.config["thumbnail_size"], self.config["local_only"])

    def saveConfig(self):
        Picklable.Picklable.saveConfig(self, self.config, os.path.join(self.dir, self.conf_file))

    def getConfig(self):
        return self.config
    
    
    ##############################################################
    def copyFromBase(self, fname):
        self.linkOrCopy(os.path.join(self.loc.base_dir, fname), os.path.join(self.dir, fname))
    
    # src and dst are absolute paths.
    def linkOrCopy(self, src, dst):
        if (os.name == "nt"):
            self.logger.debug("Copying %s to %s..." % (src, dst))
            if (os.path.isfile(src)):
                shutil.copy(src, dst)
            else:
                # Only copy one level deep and ignore .* files (e.g., .svn).
                os.mkdir(dst)
                for fname in os.listdir(src):
                    if (fname[0] != "."):
                        shutil.copy(os.path.join(src, fname), dst)
        else:
            self.logger.debug("Linking %s to %s..." % (src, dst))
            os.symlink(src, dst) #@UndefinedVariable

