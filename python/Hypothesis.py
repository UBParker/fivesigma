#!bin/env python

from __future__ import division
import os
import collections
import array
import ROOT
import numpy as np
import math

class BinningError(Exception):
    def __init__(self, name, newbin, oldbin):
        self.name, self.newbin, self.oldbin = name, newbin, oldbin
    def __str__(self):
        return "BinningError in histogram " + self.name + ": New bin: " + self.newbin + " and old bin: " + self.oldbin

class Hypothesis:
    def __init__(self):
        self._name=None
        self._cardfilename=None
        self._rootfilename=None
        self.parameters=dict
        self.uncertainties=collections.defaultdict(dict)
        self.scalar_uncertainties=collections.defaultdict(dict)
        self.bg_hist=collections.OrderedDict()
        self.luminosity = 1
        self.sg_hist=None
        self.data_hist=None
        self.directory=None
        self.width=None
        self.factor=None
        self.vector=None
        self.xmin=None
        self.xmax=None
        self._rmax=None
    def _set_alt_name(self, hist):
        hist.SetName(hist.GetName().replace("Signal", "Signal_ALT"))
    def _prepare_hist(self,hist,name):
        binning_vector=[]
        if self.xmin is None:
            self.xmin=hist.GetBinLowEdge(1)
        if self.xmax is None:
            self.xmax=hist.GetBinLowEdge(hist.GetNbinsX())
        if self.width is not None:
            #self.factor=int(hist.GetBinWidth(1)/self.width)
            binning_vector=np.arange(self.xmin,self.xmax,self.width)
        elif self.factor is not None:
            binning_vector=np.arange(self.xmin,self.xmax,hist.GetBinWidth(1)*self.factor)
        elif self.vector is not None:
            binning_vector=[x for x in self.vector if x>=self.xmin and x<=self.xmax]
        arrayBinning = array.array('d',binning_vector)
        newhist = ROOT.TH1F(name, "", len(binning_vector)-1,arrayBinning)
        self._unique_name(newhist)
        oldbin = hist.FindBin(binning_vector[0]+1E-5)
        for newbin in range(1,newhist.GetNbinsX()+1):
            binContent, binError, n = 0, 0, 0
            while hist.GetXaxis().GetBinLowEdge(oldbin) < newhist.GetXaxis().GetBinUpEdge(newbin):
                if hist.GetXaxis().GetBinUpEdge(oldbin) > newhist.GetXaxis().GetBinUpEdge(newbin):
                    print name, newbin, oldbin
                    hist.Draw()
                    newhist.Draw("same")
                    raw_input()
                    raise BinningError(name, newbin, oldbin)
                binContent += hist.GetBinContent(oldbin)
                binError += (hist.GetBinError(oldbin))**2
                oldbin += 1
                n += 1
            newhist.SetBinContent(newbin,binContent)
            newhist.SetBinError(newbin,math.sqrt(binError))
        return newhist
    def _get_name(self):
        if self._name is not None:
            return self._name
        else:
            name=""
            for par in self.parameters:
                name+="%s_%s_"%(par,self.parameters[par])
            name+="lumi_%s"%(self.luminosity)
            self._name=name
        return self.name
    def _get_card_name(self):
        if self._cardfilename is not None:
            return self._cardfilename
        else:
            self._cardfilename=os.path.join(self.directory, "datacard_"+self.name+".txt")
        return self._cardfilename
    def _get_root_name(self):
        if self._rootfilename is not None:
            return self._rootfilename
        else:
            self._rootfilename=os.path.join(self.directory, "histograms_"+self.name+".root")
        return self._rootfilename
    def _get_rmax(self):
        if self._rmax is not None:
            return self._rmax
        else:
            n_bg_ev=sum([self.bg_hist[b].Integral() for b in self.bg_hist])
            n_sig_ev=self.sg_hist.Integral()
            #good estimate for most cases
            self._rmax=5.*( 2. *math.sqrt(n_bg_ev+1.)+2.)/n_sig_ev
            return self._rmax
    def _set_rmax(self,rmax):
        self._rmax=rmax
    def _unique_name(self,hist):
        hist.SetName(hist.GetName()+"__"+str(id(hist)))
    def _write_clean_name(self,hist,name=None):
        if name is None:
            hist.Write(str(hist.GetName()).split("__")[0])
        else:
            hist.Write(name)

    def add_bg(self,name,hist):
        self._unique_name(hist)
        self.bg_hist[name]=hist
    def add_sg(self,hist):
        self._unique_name(hist)
        self.sg_hist=hist
    def add_data(self,hist):
        self._unique_name(hist)
        self.data_hist=hist
    def add_bg_uncertainty_up_down(self,bgname, name, histup, histdown):
        self._unique_name(histup)
        self._unique_name(histdown)
        self.uncertainties[name][bgname]=[histup,histdown]
    def add_sg_uncertainty_up_down(self, name, histup, histdown):
        self._unique_name(histup)
        self._unique_name(histdown)
        self.uncertainties[name]["Signal"]=[histup,histdown]
    def add_sg_uncertainty_scalar(self,name,value):
        self.scalar_uncertainties[name]["Signal"]=value
    def add_bg_uncertainty_scalar(self,bgname,name,value):
        self.scalar_uncertainties[name][bgname]=value
    def add_uncertainty_scalar(self,name,value):
        self.add_sg_uncertainty_scalar(name,value)
        for bgname in self.bg_hist:
            self.add_bg_uncertainty_scalar(bgname,name,value)
    def set_bining(self, width=None, factor=None, vector=None, xmin=None, xmax=None):
        self.width=width
        self.factor=factor
        self.vector=vector
        self.xmin=xmin
        self.xmax=xmax
    def set_parameters(self,parameters):
        self.parameters=parameters
#pdf uncertainties
    def set_alt_names(self):
        self._set_alt_name(self.sg_hist)
        for uncertainty in self.uncertainties:
            for hist in self.uncertainties[uncertainty]["Signal"]:
                self._set_alt_name(hist)
    def set_zero(self):
        self.sg_hist.Scale(0)
        for uncertainty in self.uncertainties:
            for sb in self.uncertainties[uncertainty]:
                for hist in self.uncertainties[uncertainty]["Signal"]:
                    hist.Scale(0)
    def set_luminosity_and_scale_all(self, luminosity):
        for hist in self.bg_hist.values()+[self.sg_hist]:
            hist.Scale(luminosity/self.luminosity)
        for uncertainty in self.uncertainties:
            #sb =all signal and backgrounds
            for sb in self.uncertainties[uncertainty]:
                if sb in self.uncertainties[uncertainty]:
                    for hist in self.uncertainties[uncertainty][sb]:
                        hist.Scale(luminosity/self.luminosity)
        self.luminosity = luminosity

    def set_luminosity_and_scale_signal(self, luminosity):
        self.sg_hist.Scale(luminosity/self.luminosity)
        for uncertainty in self.uncertainties:
            if "Signal" in self.uncertainties[uncertainty]:
                for hist in self.uncertainties[uncertainty]["Signal"]:
                    hist.Scale(luminosity/self.luminosity)
        self.luminosity = luminosity

    def rescale_signal(self, scalefactor):
        self.sg_hist.Scale(scalefactor)
        for uncertainty in self.uncertainties:
            if "Signal" in self.uncertainties[uncertainty]:
                for hist in self.uncertainties[uncertainty]["Signal"]:
                    hist.Scale(scalefactor)
    def set_rmax(self,rmax):
        self.rmax=rmax
    def prepare_histograms(self):
        #signal_scalefactor = float((lumi*signal_xs)/signal_n_ev_sample)
        #signal_hist.Scale(signal_scalefactor)
        self.sg_hist=self._prepare_hist(self.sg_hist,"Signal")
        for bg in self.bg_hist:
            self.bg_hist[bg]=self._prepare_hist(self.bg_hist[bg],bg)
        for uncertainty in self.uncertainties:
            for sb in self.uncertainties[uncertainty]:
                self.uncertainties[uncertainty][sb][0]=self._prepare_hist(self.uncertainties[uncertainty][sb][0],sb+"_"+uncertainty+"_Up")
                self.uncertainties[uncertainty][sb][1]=self._prepare_hist(self.uncertainties[uncertainty][sb][1],sb+"_"+uncertainty+"_Down")
                #for ihins=hist in enumerate(self.uncertainties[uncertainty][sb]):
                    ##print hist,uncertainty,sb
                    #hist=self._prepare_hist(hist,sb+"_"+uncertainty)
        if self.data_hist is not None:
            self.data_hist=self._prepare_hist(self.data_hist,"data_obs")
        else:
            self.data_hist=self.bg_hist.values()[0].Clone()
            self._unique_name(self.data_hist)
    def write_card(self,directory):
        n_sig_ev = self.sg_hist.Integral()
        n_bg_ev=dict()
        for bg in self.bg_hist:
            n_bg_ev[bg]=self.bg_hist[bg].Integral()
        f=open(self.cardfilename,"w")
        f.write("# channels\n")
        f.write("imax *\n")
        f.write("# backgrounds\n")
        f.write("jmax *\n")
        f.write("# nuisance\n")
        f.write("kmax *\n")
        f.write("---------------\n")
        f.write("shapes * * " + self.rootfilename + " $PROCESS $PROCESS_$SYSTEMATIC\n")
        f.write("---------------\n")
        f.write("bin channel\n")
        if self.data_hist is not None:
            f.write("observation "+str(self.data_hist.Integral())+"\n")
        else:
            #just put in a random number
            f.write("observation 1\n")
        f.write("---------------\n")
        f.write("bin    "+"channel"+"".join([ " channel" for i in range(len(self.bg_hist))])+"\n")
        f.write("process"+" Signal "+" ".join(self.bg_hist.keys())+"\n")
        f.write("process"+" 0"+"".join([ " %d"%(i+1) for i in range(len(self.bg_hist))])+"\n")
        f.write("rate   "+" "+str(n_sig_ev)+" "+"".join([ " %f"%(n_bg_ev[i]) for i in self.bg_hist])+"\n")
        f.write("---------------\n")
        all_sg_bgs=["Signal"]+self.bg_hist.keys()
        for unc in self.uncertainties:
            tmp_string=unc+"_ shape"
            for sb in all_sg_bgs:
                tmp_string+=" %i"%(sb in self.uncertainties[unc])
            tmp_string+="\n"
            f.write(tmp_string)
            #tmp_string=unc+"_Down shape"
            #for sb in all_sg_bgs:
                #tmp_string+=" %i"%(sb in self.uncertainties[unc])
            #tmp_string+="\n"
            #f.write(tmp_string)
        for unc in self.scalar_uncertainties:
            tmp_string=unc+" lnN"
            for sb in all_sg_bgs:
                tmp_string+=" %i"%(sb in self.scalar_uncertainties[unc])
            tmp_string+="\n"
            f.write(tmp_string)
        f.close()
    def write_root(self,directory):
        outfile = ROOT.TFile(self.rootfilename,"RECREATE")
        for name in self.bg_hist:
            self._write_clean_name(self.bg_hist[name])
            #outfile.WriteTObject(self.bg_hist[name])
        #outfile.WriteTObject(self.sg_hist)
        self._write_clean_name(self.sg_hist)
        self._write_clean_name(self.data_hist,name="data_obs")
        #outfile.WriteTObject(self.data_hist)
        for uncertainty in self.uncertainties:
            for sb in self.uncertainties[uncertainty]:
                for hist in self.uncertainties[uncertainty][sb]:
                    #outfile.WriteTObject(hist)
                    self._write_clean_name(hist)
    def __deepcopy__(self, book):
        new = Limit()
        new.__dict__=copy.deepcopy(self.__dict__, book)
        try: new.sg_hist = new.sg_hist.Clone()
        except AttributeError: pass
        try: new.data_hist = new.data_hist.Clone()
        except AttributeError: pass
        try: new.bg_hist = new.bg_hist.Clone()
        except AttributeError: pass
        for uncertainty in new.uncertainties:
            for sb in new.uncertainties[uncertainty]:
                for hist in new.uncertainties[uncertainty][sb]:
                    hist = hist.Clone()
        return new
    name = property(_get_name)
    cardfilename = property(_get_card_name)
    rootfilename = property(_get_root_name)
    rmax = property(_get_rmax,_set_rmax)
