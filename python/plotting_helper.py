#!/usr/bin/env python
import array
import ROOT
import csv
import math
import glob
import os
from collections import defaultdict
from collections import OrderedDict
import re
import numpy

def getLimitFromRootFile(filename):
   f=ROOT.TFile(filename,"r")
   tree = f.Get("limit")

   x = array.array('d',[0])
   tree.SetBranchAddress( "limit", x )
   alist, i = [], 0
   while tree.GetEntry(i):
      i += 1
      alist.append( x[0] )
   alist=sorted(alist)
   l=len(alist)
   median=alist[int(0.5*l)]
   l68=alist[int(0.158655254*l)]
   u68=alist[int(0.841344746*l)]
   l95=alist[int(0.022750132*l)]
   u95=alist[int(0.977249868*l)]
   return l95,l68,median,u68,u95
   #mean=sum(alist)/len(alist)
   #return mean,mean,median,mean,mean
class Table:
    """
    Creates a table from a file and provides method to access elements from that table.
    """
    def __init__(self,filename):
        f=open(filename,"r")
        for line in f:
            if line.strip()=="": continue
            if line[0]=="#": continue
            self.header=line.split()
            nlines=len(self.header)
            break
        i=0
        self.content=dict()
        for line in f:
            i+=1
            if line.strip()=="": continue
            if line[0]=="#": continue
            linelist=line.split()
            if len(linelist)!=nlines: raise NameError("Wrong number of columns in file "+filename+" line "+str(i))
            self.content[linelist[0]]=linelist
    def get(self,row,col):
        return self.content[row][self.header.index(col)]
    def getFloat(self,row,col):
        return float(self.get(row,col))
    def getCols(self):
        return self.header
    def getRows(self):
        b=list()
        for a in self.content.iterkeys():
            b.append(a)
        return b
    def getColDictFloat(self,col):
        b=dict()
        for a in self.content.iterkeys():
            b[a]=(float(self.content[a][self.header.index(col)]))
        return b
    cols = property(getCols)
    rows = property(getRows)

class ExpectedLimit:
   def __init__(self, filename, asymptotic=False):

      self.median=-1
      self.l68=-1
      self.h68=-1
      self.l95=-1
      self.h95=-1


      f=ROOT.TFile(filename,"r")
      tree = f.Get("limit")
      alist=[]
      if asymptotic:
         for l in tree:
            if math.fabs(l.quantileExpected -0.025)<0.001:
                self.l95 = l.limit
            if math.fabs(l.quantileExpected -0.16)<0.001:
                self.l68 = l.limit
            if math.fabs(l.quantileExpected -0.5)<0.001:
                self.median = l.limit
            if math.fabs(l.quantileExpected -0.84)<0.001:
                self.h68 = l.limit
            if math.fabs(l.quantileExpected -0.975)<0.001:
                self.h95 = l.limit
      else:
         #print filename
         x = array.array('d',[0])
         tree.SetBranchAddress( "limit", x )
         alist, i = [], 0
         while tree.GetEntry(i):
            i += 1
            alist.append( x[0] )
         alist=sorted(alist)
         l=len(alist)
         self.median=alist[int(0.5*l)]
         self.l68=alist[int(0.158655254*l)]
         self.h68=alist[int(0.841344746*l)]
         self.l95=alist[int(0.022750132*l)]
         self.h95=alist[int(0.977249868*l)]

#def readTreesAsymptotic(directory, veto):
    #d_CLs = defaultdict(lambda : defaultdict(dict))
    ##Read Trees
    #for path in sorted(glob.glob(directory+'/result*.root')):
        #filename = os.path.split(path)[1]
        #print "Read",filename
        #params = filename[14:-19].split('lumi')
        #lumi = float(params[1])
        #mass, coupling = params[0].split("_g")
        #mass, coupling = int(mass), float(coupling)
        #if lumi in veto:
            #continue
        ##name = params[0]
        #file = ROOT.TFile(path,"READ")
        #t = file.Get("limit")
        #d=dict()
        #for l in t:
            ##print l.quantileExpected, l.limit
            #if l.quantileExpected == -1.0:
                #d['mediancls'] = l.limit
        ##original
        #d_CLs[lumi][mass][coupling] = d
        ##anders
        ##d_CLs[name.split("vs")[0]+" vs. "+name.split("vs")[1]][lumi] = d
    #print "xxx",d_CLs
    #return d_CLs

def getArraysFromDict(d,reverseD=None):
   xlist,ylist=[],[]
   for poi in sorted(d):
      try:
         xlist.append(float(poi))
      except:
         xlist.append(poi)
      ylist.append(d[poi])
   if reverseD != None:
      for poi in sorted(reverseD, reverse=True):
         try:
            xlist.append(float(poi))
         except:
            xlist.append(poi)
         ylist.append(reverseD[poi])
   return array.array("d",xlist),array.array("d",ylist)

def get_arrays_from_expected(expected,name,reverseName=None):
   xlist,ylist=[],[]
   for poi in expected:
      ylimit=expected[poi].__dict__.get(name,None)
      if ylimit is None:
         continue
      ylist.append(ylimit)
      try:
         xlist.append(float(poi))
      except:
         xlist.append(poi)

   if reverseName != None:
      for poi in expected.keys()[::-1]:
         ylimit=expected[poi].__dict__.get(reverseName,None)
         if ylimit is None:
            continue
         try:
            xlist.append(float(poi))
         except:
            xlist.append(poi)
         ylist.append(ylimit)
   try:
      return array.array("d",xlist),array.array("d",ylist)
   except:
      return array.array("d",[i for i in range(len(xlist))]),array.array("d",ylist)


def get_event_yield(MTlower, poi, lumi, tab_bg,tab_eff, tab_cs=None, printIt=False,events=False):
   result=dict()
   if tab_cs!=None:
      crossSection=tab_cs.getFloat(str(poi),"crossSection")*1000*tab_cs.getFloat(str(poi),"kFactor")
   else:
      crossSection=1
   eff=tab_eff.getFloat(str(MTlower),str(poi))
   err_eff=tab_eff.getFloat(str(MTlower),"e_"+str(poi))
   result['observed']=observed= int(tab_bg.getFloat(str(MTlower),"data"))
   result['mc']=mc=tab_bg.getFloat(str(MTlower),"MC")
   err_mc=tab_bg.getFloat(str(MTlower),"MCUncertainty")
   result['uncert_fit']=uncert_fit=(err_mc/mc+1)
   if events:
       result['signal']=signal=eff
       result['uncert_eff']=uncert_eff=(err_eff/eff+1)
   else:
       result['signal']=signal=(eff*lumi*crossSection)
       result['uncert_eff']=uncert_eff=(err_eff/eff+1)
   result['errUp_signal']=errUp_signal=signal*uncert_eff-signal
   result['errDown_signal']=errDown_signal=signal-signal/uncert_eff
   result['errUp_mc']=mc*uncert_fit-mc
   result['errDown_mc']=mc-mc/uncert_fit

   if printIt:
      print "Observed",observed
      print "mc",mc
      print "err_mc",err_mc
      print "err_mcUpDown","^{+"+str(mc*uncert_fit-mc)+"}_{-"+str(mc-mc/uncert_fit)+"}"
      print "uncert_fit",uncert_fit
      print "eff",eff
      print "err_eff",err_eff
      print "uncert_eff",uncert_eff
      print "signal",signal
      print "err_signal",errUp_signal,errDown_signal
      print "isevent",events
   return result

def get_event_yield2(MTlower, poi, lumi, tab_bg,tab_eff, tab_cs=None, printIt=False):
   result=dict()
   if tab_cs!=None:
      crossSection=tab_cs.getFloat(str(poi),"crossSection")*tab_cs.getFloat(str(poi),"kFactor")
   else:
      crossSection=1
   result['observed']=observed= int(tab_bg.getFloat(str(MTlower),"data"))
   result['mc']=mc=tab_bg.getFloat(str(MTlower),"MC")
   err_mc=tab_bg.getFloat(str(MTlower),"MCUncertainty")
   result['uncert_fit']=uncert_fit=(err_mc/mc+1)
   return result


def intersect(a,*p):
    for i in p:
        a=[val for val in a if val in i]
    return a

#still beta, has o be updated
def siground(x,e,digits=2):
    if (float(e)!=0 and float(x)!=0):
        sf=digits-int(math.floor (math.log(e,10)) - math.floor (math.log(x,10)   ))
    else: sf=0
    if sf<0: sf=0
    formatstr=str("{0:."+str(int(sf))+"G}")
    return latexformat(float(x), formatstr), latexformat(float(e), '{0:.'+str(digits)+'G}')

def latexformat(x,formatstr):
    rounded= float(formatstr.format(x))
    #if rounded>=0.0001 and rounded <0: return str(rounded)
    if rounded<10000 and rounded >=10: return str(int(rounded))

    if "E" in formatstr.format(x):
        m,e=formatstr.format(x).split("E")
        if "+" in e: e=e[1:]
        #if abs(int(e))<4: return str(x)
        return m+"\cdot 10^{"+e+"}"
    else: return formatstr.format(x)

def merge_root_files(directory):
   #print "#Merge .root files for expected limit"
   uniquefiles=set()
   for filename in glob.glob(directory+'/poi_*.root'):
      ipar=os.path.basename(filename)
      ipar=ipar.split("--")[0]
      uniquefiles.add(ipar)
   #print uniquefiles
   for i in uniquefiles:
      if not os.path.exists("%s/merged_%s.root"%(directory,i)):
         os.system("hadd -f %s/merged_%s.root %s/%s--*.root"%(directory,i,directory,i))
      #print "#.root file have been merged, don't worry to much about warnings above."

def get_from_expected_dir(directory ,asymptotic):
    limit = list()
    if os.path.isdir(directory):
        for path in glob.glob("%s/merged_*.root"%(directory)):
            filename=os.path.basename(path)
            lumi = filename.split("lumi_")[1].replace(".root","")
            parameters=filename.split("lumi_")[0]
            par=re.search("_\w*_\w*_",parameters)
            #try:
            par=par.group(0)

            #the structure is:
            #['', 'poi', 'par1', 'value1', 'par2', 'value2',...., '']
            parameters={}
            allpars=par.split("_")
            for i in range(2,len(allpars)-1,2):
               parameters[allpars[i]]=allpars[i+1]
            ipar=par.split("_")[1]
            parameters.update({"limit":ExpectedLimit(path,asymptotic),"lumi":lumi})
            limit.append(parameters)
            #except:
                #print "no limit in ", path
    return limit

# observed limit functions:

def read_output_file(filename):
	current_par, current_limit =  "", -1
	with open(filename, 'r') as f:
		for line in f:
			if "Limit" in line and not "tries" in line:
				current_limit = float(line.split(" ")[3])
			if "poi:" in line:
				current_par = line.split(" ")[1]
	return (current_par, current_limit)

def get_pois_value(pois, parameter):
    pois = pois.split("_")
    value = -1
    for i in range(len(pois)):
        if pois[i] == parameter:
            value = pois[i+1]
    return value 

def StringContainsAll(string, listcontains):
    
    # return True if string contains all list items.
    
    matches = 0
    for item in listcontains:
        if item in string:
            matches += 1
    if matches == len(listcontains) and matches != 0:
        return True
    return False

def get_observed_limit(directory, currentpar, fixed_parvalues):

    # read all limits from out* files from output directory:
    
    limits = {}
    if os.path.isdir(directory):
        for path in glob.glob("%s/out.*"%(directory)):
            filename=os.path.basename(path)
            pois, val = read_output_file(path)
            limits[pois.replace("\n","")] = val

    if len(limits) == 0:
        print "No observed limit found."
        return None

    # return xy list for plotting for current and fixed parameter(s):
    
    x, y = numpy.array([],'d'), numpy.array([],'d')
    
    for pois in limits:
        if StringContainsAll(pois, fixed_parvalues):
            parvalue = float(get_pois_value(pois, currentpar))
            limit = float(limits[pois])
            #xy[parvalue] = limit
            #x.append(parvalue)
            #y.append(limit)
            x=numpy.append(x, parvalue)
            y=numpy.append(y, limit)

    return x, y
