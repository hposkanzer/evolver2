import Creature
import random
import os
import re
import glob
import Picklable
import cPickle
import string
import stat
import Thumbnailer

prefix = "g"
name_pat = re.compile("%s(\d\d\d\d)" % (prefix))
pickle_name = "data.pkl"
votes_name = "votes.txt"
    
class NotEnoughVotes(Exception):  pass


def getLatestGenerationID(exp_dir):
    
    gen_dir = getLatestGenerationName(exp_dir)
    
    if gen_dir:
        match = name_pat.match(gen_dir)
        gen_id = int(match.group(1))
    else:
        gen_id = None
    
    return gen_id
    
    
def getLatestGenerationName(exp_dir):
    
    # Get the names that match our generation directory pattern.
    l = glob.glob(os.path.join(exp_dir, "%s*" % (prefix)))
    l = map(os.path.basename, l)
    l = filter(lambda x: name_pat.match(x), l)
    if not l:
        return None
    
    # Find the latest one that includes a pickle file.
    l.sort()
    gen_dir = l.pop()
    while not os.path.exists(os.path.join(exp_dir, gen_dir, pickle_name)):
        if not l:
            return None
        gen_dir = l.pop()
    return gen_dir


########################################################################
class Generation(Picklable.Picklable):

    def __init__(self, experiment, id=0):
        Picklable.Picklable.__init__(self)
        self.experiment = experiment
        self.id = id
        self.latest = True
        self.prev_generation = None
        self.creatures = []

    def __str__(self):
        return "Generation %04d" % (self.id)
        
    def getID(self):
        return self.id
    
    def getName(self):
        return "g%04d" % (self.getID())
    
    def getDir(self):
        return os.path.join(self.experiment.getName(), self.getName())
    
    def getConfig(self):
        return self.experiment.getConfig()
    
    def getExperiment(self):
        return self.experiment
    
    def isLatest(self):
        return self.latest
    
    
    ########################################################################
    def produce(self):
        self.logger.debug("Producing %s..." % (self))
        output_dir = self.getDir()
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        # Create a blank votes file.
        fname = os.path.join(output_dir, votes_name)
        f = open(fname, "w")
        f.close()
        os.chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
        # Produce the creatures.
        for i in range(len(self.creatures)):
            creature = self.creatures[i]
            creature.run(self, i)
        # Write the generation page.
        self.writePage()

        
    def writePage(self):
        fname = os.path.join(self.getDir(), "index.html")
        f = open(fname, "w")
        f.write("<html>\n<head><title>Generation %d</title></head>\n<body>\n" % (self.getID()))
        f.write("<font size='-1'><a href='/'>Chez Zeus</a> &gt; <a href='../../index.html'>Photo Evolver</a></font>\n")
        f.write("<center>\n<h2>\n")
        if self.prev_generation:
            f.write("<a href='../%s/index.html'><img src='../../back.jpg' border=0 style='{vertical-align: middle}'></a>\n" % (self.prev_generation.getName()))
        else:
            f.write("<img src='../../blank.jpg' style='{vertical-align: middle}'>\n")
        f.write("&nbsp;Generation %d&nbsp;\n" % (self.getID()))
        if not self.isLatest():
            f.write("<a href='../%s/index.html'><img src='../../forw.jpg' border=0 style='{vertical-align: middle}'></a>\n" % ("g%04d" % (self.getID()+1))) # XXX ugly
        else:
            f.write("<img src='../../blank.jpg' style='{vertical-align: middle}'>\n")
        f.write("</h2>\n")
        f.write("<a href='../index.html'>Experiment %d</a><p>\n" % (self.experiment.getID()))
        if self.isLatest():
            f.write("<i>This is the latest generation.  Browse through the creatures below and vote for your favorites.</i>\n")
        else:
            f.write("<i>This is an older generation.  Voting is closed, but you can still browse through the creatures.  The suvivors of this generation are highlighted below.</i>\n")
        f.write("<table>\n")
        columns = self.experiment.getConfig()["index_columns"]
        for i in range(len(self.creatures)):
            creature = self.creatures[i]
            if not i % columns:
                if i:
                    f.write("</tr>\n")
                f.write("<tr>\n") 
            fname = os.path.join(self.getDir(), creature.getThumbName())
            url = Thumbnailer.getInstance(self.getExperiment()).getURL(fname)
            style = "border: 1px solid black"
            if (not self.isLatest()and not creature.isSurvivor()):
                style = style + "; opacity:0.4;filter:alpha(opacity=40)"
            f.write("<td><a href='%s'><img src='%s' style='%s'></a></td>\n" % (creature.getPageName(), url, style))
        f.write("</tr>\n</table></center>")
        f.write("</body>\n</html>\n")
        f.close()
        
        
    def regenHTML(self):
        self.writePage()
        for i in range(len(self.creatures)):
            creature = self.creatures[i]
            creature.writePage(self, i)
         
         
    def getCreatureThumb(self, i):
        if ((i < 0) or (i >= len(self.creatures))):
            return ""
        else:
            creature = self.creatures[i]
            fname = os.path.join(self.getDir(), creature.getThumbName())
            url = Thumbnailer.getInstance(self.getExperiment()).getURL(fname)
            return "<a href='%s'><img src='%s' border=1></a>" % (creature.getPageName(), url)
            
            
    ########################################################################
    def conceive(self):
        self.logger.debug("Conceiving %s..." % (self))
        self.fillNewCreatures()
        

    def fillNewCreatures(self):
        for i in range(len(self.creatures), self.experiment.getConfig()["creatures"]):
            creature = Creature.Creature(self, i)
            creature.conceive(random.randint(self.experiment.getConfig()["min_depth"], self.experiment.getConfig()["max_depth"]))
            self.creatures.append(creature)


    ########################################################################
    def evolveFrom(self, gen_dir):
        
        self.prev_generation = self.depersist(gen_dir)
        self.prev_generation.latest = False
        self.id = self.prev_generation.getID() + 1
        self.creatures = []

        self.logger.debug("Evolving %s..." % (self.prev_generation))
        
        progeny_count = self.experiment.getConfig()["progeny"]
        survivors = self.prev_generation.getSurvivors(self.experiment.getConfig()["survivors"])
        for i in range(len(survivors)):
            creature = survivors[i]     
            self.logger.debug("Choosing %s.." % (creature))
            creature.setSurvivor()
            for j in range(progeny_count):
                child = creature.clone(self, (i*progeny_count)+j)
                child.evolve()
                self.creatures.append(child)
                
        self.fillNewCreatures()
                
            
    ########################################################################
    def getSurvivors(self, count):

        vote_counts = self.getVotes()
        rank = vote_counts.keys()
        rank.sort(lambda a, b, d=vote_counts: cmp(d[a], d[b]))
        
        survivors = []
        while (rank and (len(survivors) < count)):
            id = rank.pop()
            for creature in self.creatures:
                if (creature.getID() == id):
                    survivors.append(creature)
                    break
            else:
                self.logger.warning("No creature found for ID %d." % (id))
                
        if (len(survivors) < count):
            raise NotEnoughVotes, vote_counts
        
        survivors.sort(lambda a, b:  cmp(a.getID(), b.getID()))
        return survivors
        
    
    def getVotes(self):

        self.logger.debug("Reading votes...")
        fname = os.path.join(self.experiment.getName(), self.getName(), votes_name)
        f = open(fname)
        votes = filter(None, map(string.strip, f.readlines()))
        f.close()
        
        vote_counts = {}
        for vote in votes:
            vote = int(string.split(vote, ":")[-1])
            if not vote_counts.has_key(vote):
                vote_counts[vote] = 0
            vote_counts[vote] = vote_counts[vote] + 1
            
        vote_strs = []
        keys = vote_counts.keys()
        keys.sort()
        for key in keys:
            vote_strs.append("%d:%d" % (key, vote_counts[key]))
        self.logger.debug("Votes:  %s" % (string.join(vote_strs, ", ")))

        return vote_counts
        
        
    ########################################################################
    def persist(self):
        self.logger.debug("Persisting %s..." % (self))
        fname = os.path.join(self.experiment.getName(), self.getName(), pickle_name)
        f = open(fname, "w")
        cPickle.dump(self, f)
        f.close()
        
    
    def depersist(self, gen_dir):
        self.logger.debug("Depersisting %s..." % (gen_dir))
        fname = os.path.join(self.experiment.getName(), gen_dir, pickle_name)
        f = open(fname)
        gen = cPickle.load(f)
        f.close()
        return gen
        