#!/bin/env python

import Calculator
import Hypothesis

import ROOT
import glob
import re

calc=Calculator.Calculator("DMLimits")
calc.outputdir="/home/home1/institut_3a/padeken/net/Wprime/NEWLimitTOOL/test7"

calc.method="asymptotic"
signalFileNames=glob.glob("/home/home1/institut_3a/padeken/MUSiC/SmallPy/eventWeighter/out/*.root")
signalNames=[ sg.split("/")[-1].replace(".root","") for sg in signalFileNames]
signalFiles={}
for sgName,sgFile in zip(signalNames,signalFileNames):
    signalFiles[sgName]=ROOT.TFile(sgFile,"READ")
bgFile=ROOT.TFile("/home/home1/institut_3a/padeken/MUSiC/SmallPy/systematics/bg_for_limit.root","READ")
scanLumi=[1,30,300,3000]

for lumi in scanLumi:
    for sample in signalFiles:
        if "DM_AV_Mxi_" not in sample:
            continue
        print "preparing %s"%sample
        hypo=Hypothesis.Hypothesis()
        syst_part=      ["Ele", "Muon", "Tau", "met", "Jet"]
        syst_type=      ["Scale", "Resolution"]
        syst_updown=    ["Up", "Down"]

        baseHistName="Ele/h1_3_Ele_mt"

        hypo.add_bg("background",bgFile.Get(baseHistName+"_Main"))
        hypo.add_sg(signalFiles[sample].Get(baseHistName))
        counter=signalFiles[sample].Get("h_counters")
        try:
            #counter=signalFiles[sample].Get("hcounter")
            #signal_n_ev_sample=1.
            signal_n_ev_sample= max(counter.GetBinContent(1),counter.GetBinContent(2))
        except:
            print "------------------------------------------------------------"
            print "WARNING:          Did not find a hcounter setting nev=1"
            print "------------------------------------------------------------"
            signal_n_ev_sample=1.

        for part in syst_part:
            for itype in syst_type:
                histup=bgFile.Get(baseHistName+"_syst_%s%s%s"%(part,itype,syst_updown[0]))
                histdown=bgFile.Get(baseHistName+"_syst_%s%s%s"%(part,itype,syst_updown[1]))
                try:
                    histup.Integral()>1.
                except:
                    continue
                if histup.Integral()>1. and histdown.Integral()>1.:
                    hypo.add_bg_uncertainty_up_down("background","%s%s"%(part,itype),histup,histdown)

                    histup=signalFiles[sample].Get(baseHistName+"_syst_%s%s%s"%(part,itype,syst_updown[0]))
                    histdown=signalFiles[sample].Get(baseHistName+"_syst_%s%s%s"%(part,itype,syst_updown[1]))
                    hypo.add_sg_uncertainty_up_down("%s%s"%(part,itype),histup,histdown)
        hypo.set_luminosity(lumi)

        hypo.add_uncertainty_scalar("lumi",0.026)
        hypo.add_uncertainty_scalar("eff",0.02)
        hypo.set_bining(width=10,xmin=200,xmax=4000)
        hypo.rescale_signal(1000./signal_n_ev_sample)
        mxi= re.search('Mxi_\d*', sample)
        mxi=mxi.group()
        mxi=mxi.replace("_","").replace("Mxi","")
        xi= re.search('g_\w\d', sample)
        xi=xi.group()
        xi=xi.replace("_","").replace("g","")
        hypo.set_parameters({"gxi":xi,"mxi":mxi})
        calc.add_hypothesis(hypo)
print "Write output..."
calc.write()
print "Done"
