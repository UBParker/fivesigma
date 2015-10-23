#!bin/env python

import collections
import os
import shutil
import cPickle

class Calculator:
    def __init__(self,name):
        self.hypothesis=list()
        self.cross_sections=list()
        self.outputdir=os.path.join(os.getcwd(),name)
        self.name=name
        self.executable=None
        self.method=None
        self.nqueue=5
        self.executable={
                "bayesian":"runMultibin.py",
                "asymptotic":"runMultibin.py",
        }
        self.path=os.path.join(os.environ.get('FIVESIGMA'),"python")


    def add_hypothesis(self,hypo):
        hypo.directory=self.outputdir
        self.hypothesis.append(hypo)
    def set_method(self,method):
        self.method=method
    def write(self):
        if os.path.exists(self.outputdir):
                shutil.rmtree(self.outputdir)
        os.makedirs(os.path.join(self.outputdir,"expected"))
        os.makedirs(os.path.join(self.outputdir,"observed"))
        os.chdir(self.outputdir)

        for hypo in self.hypothesis:
            print "preparing ",hypo.name
            hypo.prepare_histograms()
            hypo.write_root(self.outputdir)
            hypo.write_card(self.outputdir)
            print hypo.name,"finished"
        self._makeJdl()
        f = open(os.path.join(self.outputdir, "calculator.pkl"), 'wb')
        cPickle.dump(self, f)
        f.close()


    def _makeJdl(self):
    #path, executable, limits, outputdir, name, options, bayesian=False):
        for limittype in ["expected", "observed"]:
            f = open(os.path.join(self.outputdir,limittype+"/multibinlimit_"+self.name+"_lumi"+str(self.hypothesis[0].luminosity)+".jdl"), 'w')
            print >>f, "executable   = "+os.path.join(self.path, self.executable[self.method])
            print >>f, "universe     = vanilla"
            print >>f, "getenv       = true"
            print >>f, "Error        = err.$(Process)_$(Cluster)"
            print >>f, "Output       = out.$(Process)_$(Cluster)"
            print >>f, "Log          = condor_$(Cluster).log"
            #print >>f, "request_memory = 2.5 GB"
            print >>f, "notification = Error"
            print >>f, ""

            nqueue=self.nqueue
            if limittype == "expected":
                limarguments = "--exp "
            else:
                limarguments = "--obs "
                nqueue=1

            if self.method=="bayesian":
                for hypo in self.hypothesis:
                     print >>f, "arguments =",hypo.cardfilename, hypo.name, "-o",os.path.join(self.outputdir, limittype), limarguments + "--bayesian --rmax "+str(hypo.rmax)
                     print >>f, "queue " + str(nqueue)
            if self.method=="asymptotic":
                for hypo in self.hypothesis:
                     print >>f, "arguments =",hypo.cardfilename, hypo.name, "-o",os.path.join(self.outputdir, limittype), limarguments + "--asymptotic"
                     print >>f, "queue 1"
            f.close()

    #def makeJdl(path, executable, limits, outputdir, name, options, bayesian=False):
        #f = open(os.path.join(self.outputdir,"expected/multibinlimit_"+name+"_lumi"+str(limits[0].luminosity)+".jdl"), 'w')
        #print >>f, "executable   = "+os.path.join(path, executable)
        #print >>f, "universe     = vanilla"
        #print >>f, "getenv       = true"
        #print >>f, "Error        = err.$(Process)_$(Cluster)"
        #print >>f, "Output       = out.$(Process)_$(Cluster)"
        #print >>f, "Log          = condor_$(Cluster).log"
        #print >>f, "notification = Error"
        #print >>f, ""
        #nqueue, asymptotic ="5", ""
        #if options.asymptotic:
            #asymptotic = "--asymptotic"
            #nqueue = "1"

        #for limit in limits:
            #pleaseadd=""
            #if bayesian:
                #print limit.rmaxs
                #pleaseadd="--bayesian --rmax "+str(limit.rmaxs[limit.luminosity])
            #print >>f, "arguments =",limit.cardfilename, limit.name, limit.luminosity, asymptotic, "-o",os.path.join(outputdir,"expected"), pleaseadd
            ##"--mcmcexp", "--rMax",str(limit.rmaxs[limit.luminosity]),
            #print >>f, "queue " + nqueue
        #f.close()
        ##makeJdlLongRun(path, executable, limits, outputdir, name, options)

    #def makeJdlCrossection(path, executable, limits, outputdir, name, crosssections):
        #f = open(os.path.join(outputdir,"expected/multibinlimit_"+name+"_lumi"+str(limits[0].luminosity)+".jdl"), 'w')
        #print >>f, "executable   = "+os.path.join(path, executable)
        #print >>f, "universe     = vanilla"
        #print >>f, "getenv       = true"
        #print >>f, "Error        = err.$(Process)_$(Cluster)"
        #print >>f, "Output       = out.$(Process)_$(Cluster)"
        #print >>f, "Log          = condor_$(Cluster).log"
        #print >>f, "notification = Error"
        #print >>f, ""

        #for limit in limits:
            #for cs in crosssections:
                #print >>f, "arguments =",limit.cardfilename, limit.name, limit.luminosity, "--expectSignal", str(cs), "--asymptotic", "-o",os.path.join(outputdir,"expected")
                #print >>f, "queue "
        #f.close()


    #def makeJdlLongRun(path, executable, limits, outputdir, name, options):
        #f = open(os.path.join(outputdir,"expected/multibinlimit_"+name+"_lumi"+str(limits[0].luminosity)+".longrun.jdl"), 'w')
        #print >>f, "executable   = "+os.path.join(path, executable)
        #print >>f, "universe     = vanilla"
        #print >>f, "getenv       = true"
        #print >>f, "Error        = err.$(Process)_$(Cluster)"
        #print >>f, "Output       = out.$(Process)_$(Cluster)"
        #print >>f, "Log          = condor_$(Cluster).log"
        #print >>f, "notification = Error"
        #print >>f, ""
        #nqueue = "10"
        #for limit in limits:
            #print >>f, "arguments =",limit.cardfilename, limit.name, limit.luminosity, "--longrun", "-o",os.path.join(outputdir,"expected")
            #print >>f, "queue " + nqueue
        #f.close()

