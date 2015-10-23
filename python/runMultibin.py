#!/usr/bin/env python
from __future__ import division
import os
import optparse
import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for x in range(size))


parser = optparse.OptionParser( description='Wrapper for combine limit (Higgs tool).', usage='usage: %prog parameter_of_interest')
parser.add_option("--rmax", action="store", dest="rmax", help="maximum value for signal strength modifier",default="20")
parser.add_option("-o", "--outputdir", action="store", type="string", dest="outputdir", help="Outputdir for root files, this is needed for CLs expected limit")
parser.add_option("--asymptotic", action="store_true", dest="asymptotic", help="Make a asymptotic limit",default=False)
parser.add_option("--bayesian", action="store_true", dest="bayesian", help="Make a bayesian limit",default=False)
parser.add_option("--frequentist", action="store_true", dest="frequentist", help="Make a frequentist limit",default=False)
parser.add_option("--exp","--expmcmc", action="store_true", dest="mcmcexp", help="Use Bayesian MCMC for expected limit",default=True)
parser.add_option("--obs", "--obsmcmc",action="store_true", dest="mcmcobs", help="Use Bayesian MCMC for observed limit",default=False)
(options, args ) = parser.parse_args()

datafile = args[0]
poi = args[1]

#print "poi:",poi
rundir="/tmp/limit-multibin-"+id_generator()
os.system("export RANDFILE=/tmp/.rnd")
os.makedirs(rundir)
os.chdir(rundir)
if options.mcmcobs:
   if options.bayesian:
      print "thisis observed MCMC"
      #os.system("combine -M MarkovChainMC -H ProfileLikelihood "+datafile+" --tries 30 -s -1 --compile --rMax "+options.rmax )
      os.system("combine -M MarkovChainMC -H Asymptotic "+datafile+" --tries 30 -s -1 --compile --rMax "+options.rmax )
      os.system("cp higgsCombineTest.* "+options.outputdir+"/poi_"+poi+"--shape_"+id_generator()+".root")
   if options.asymptotic:
      print "this is observed asymptotic"
      os.system("combine -M Asymptotic "+datafile+ " --run observed" )
      os.system("cp higgsCombineTest.* "+options.outputdir+"/poi_"+poi+"--shape_"+id_generator()+".root")
   #if options.frequentist:
      #print "this is observed frequentist"
      #os.system("combine -M HybridNew "+datafile+ " --run observed" )
      #os.system("cp higgsCombineTest.* "+options.outputdir+"/poi_"+poi+"--shape_"+id_generator()+".root")
elif options.mcmcexp:
   if options.bayesian:
      print "thisis expected MCMC"
      #os.system("combine -M MarkovChainMC -H ProfileLikelihood "+datafile+" --tries 10 -t 400 -s -1 --rMax "+options.rmax )
      os.system("combine -M MarkovChainMC -H Asymptotic "+datafile+" --tries 10 -t 400 -s -1 --compile --rMax "+options.rmax )
      os.system("cp higgsCombineTest.* "+options.outputdir+"/poi_"+poi+"--shape_"+id_generator()+".root")
   if options.asymptotic:
      print "this is expected asymptotic"
      os.system("combine -M Asymptotic "+datafile+ " --run expected" )
      os.system("cp higgsCombineTest.* "+options.outputdir+"/poi_"+poi+"--shape_"+id_generator()+".root")
   #if options.frequentist:
      #print "this is observed frequentist"
      #os.system("combine -M HybridNew "+datafile+ " --run expected" )
      #os.system("cp higgsCombineTest.* "+options.outputdir+"/poi_"+poi+"--shape_"+id_generator()+".root")

print "poi:",poi
os.chdir("/tmp")
os.system("rm -rf "+rundir)
print "finished"



#def makeJdl(limitcfg,listMasses, listDatacards, listRMax, modus, outputdir):
   #f = open(limitcfg, 'w')
   #print >>f, "executable   = "+config.get("Limit","script_dir")+"singlebin.py"
   #print >>f, "universe     = vanilla"
   #print >>f, "getenv       = true"
   #print >>f, "Error        = err.$(Process)_$(Cluster)"
   #print >>f, "Output       = out.$(Process)_$(Cluster)"
   #print >>f, "Log          = singlebin_$(Cluster).log"
   #print >>f, "notification = Error"
   #print >>f, ""
   #for mW,datacard,rMax in zip(listMasses, listDatacards, listRMax):
      #print >>f, "arguments =",datacard, str(mW),"--"+modus, "--rMax",rMax, "-o",outputdir
      #print >>f, "queue"
   #f.close()
