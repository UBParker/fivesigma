#!/bin/env python

import Calculator
import Hypothesis

import ROOT
import glob
import re

isverbose = True

calc=Calculator.Calculator("DMLimits")
calc.outputdir="/afs/cern.ch/user/a/asparker/public/limitSetting/fivesigma/example/output"

calc.method="asymptotic"
signalFileNames=glob.glob("/eos/cms/store/user/jingyan/2017_Matrix_BestZmass_Final_noTrigMatch_30GeV/haddedFiles/2017_LFVStVecU.root")
signalNames=[ sg.split("/")[-1].replace(".root","") for sg in signalFileNames]
signalFiles={}

if isverbose : 
    print signalNames

for sgName,sgFile in zip(signalNames,signalFileNames):
    signalFiles[sgName]=ROOT.TFile(sgFile,"READ")
bgFile=ROOT.TFile("/eos/cms/store/user/jingyan/2017_Matrix_BestZmass_Final_noTrigMatch_30GeV/haddedFiles/2017_TX.root","READ")
scanLumi=[1,30,300,3000]

for lumi in scanLumi:
    for sample in signalFiles:
        if "LFV" not in sample:
            continue
        print "preparing %s"%sample
        hypo=Hypothesis.Hypothesis()
        syst_part=      ["jes"]
        syst_type=      ["Scale"] #, "Resolution"]
        syst_updown=    ["Up", "Down"]
        # _jes_Up 
        baseHistName= "AR_emul_lllOffZMetg20Jetgeq1Bleq1_BDT_ST" #"Ele/h1_3_Ele_mt"
        #VR_emul_lllOffZMetg20Jetgeq1Bleq1_BDT_ST
        if isverbose:
            print "baseHistName is below:"
            print baseHistName


        #hypo.add_bg(bgFile.Get(baseHistName))
        
        hypo.add_sg(signalFiles[sample].Get(baseHistName))
        #counter=signalFiles[sample].Get("h_counters")
        #try:
        #    #counter=signalFiles[sample].Get("hcounter")
        #    #signal_n_ev_sample=1.
        #    signal_n_ev_sample= max(counter.GetBinContent(1),counter.GetBinContent(2))
        #except:
        #    print "------------------------------------------------------------"
        #    print "WARNING:          Did not find a hcounter setting nev=1"
        #    print "------------------------------------------------------------"
        signal_n_ev_sample=1.

        for part in syst_part:
            for itype in syst_type:
                if isverbose :
                   print baseHistName+"_%s_%s"%(part,syst_updown[0])

                histup=bgFile.Get(baseHistName+"_%s_%s"%(part,syst_updown[0]))
                histdown=bgFile.Get(baseHistName+"_%s_%s"%(part,syst_updown[1]))
                try:
                    histup.Integral()>1.
                except:
                    continue
                if histup.Integral()>1. and histdown.Integral()>1.:
                    hypo.add_bg_uncertainty_up_down("background","%s"%(part),histup,histdown)

                    histup=signalFiles[sample].Get(baseHistName+"_%s_%s"%(part,syst_updown[0]))
                    histdown=signalFiles[sample].Get(baseHistName+"_%s_%s"%(part,syst_updown[1]))
                    hypo.add_sg_uncertainty_up_down("%s%s"%(part,itype),histup,histdown)
        hypo.set_luminosity_and_scale_all(lumi)

        hypo.add_uncertainty_scalar("lumi",0.026)
        #hypo.add_uncertainty_scalar("eff",0.02)
        hypo.set_bining(width=10)
        hypo.rescale_signal(1./signal_n_ev_sample)
        mxi= re.search('2017_LFV\d*', sample)
        if isverbose :
            print "mxi :"
            print mxi
            print "sample:"
            print sample 

        mxi=mxi.group()
        mxi=mxi.replace("_","")#.replace("Mxi","")
        #xi= re.search('g_\w\d', sample)
        #xi=xi.group()
        #xi=xi.replace("_","").replace("g","")
        hypo.set_parameters({"mxi":mxi})#{"gxi":xi,"mxi":mxi})
        calc.add_hypothesis(hypo)
print "Write output..."
calc.write()
print "Done"
