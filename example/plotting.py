#!/bin/env python
from __future__ import division
#~ import plotting_helper
import python.plotting_helper as plotting_helper
import os
import optparse
import cPickle
import glob
import collections
import ROOT
import itertools

def unit(x):
    return "("+x+")"
    return "["+x+"]"
    return "/ "+x


def find_parmeter_in_limit(mdictlist,parameters,parameter_names):
    for entry in mdictlist:
        found=0
        for i in range(len(parameter_names)):
            if entry[parameter_names[i]]==parameters[i]:
                found+=1
        if found==len(parameter_names):
            return entry
    return None

def write_table(name,pois,par,variable_pois,combi,expected_limit):
    f=open(name+".txt","w")
    outstring=""
    for i in expected_limit:
        outstring +=i+"  "
    outstring+="\n"
    for i in expected_limit:
        outstring += "%s  "%expected_limit[i].median
    outstring+="\n"
    for i in expected_limit:
        outstring += "%s  "%expected_limit[i].l68
    outstring+="\n"
    for i in expected_limit:
        outstring += "%s  "%expected_limit[i].h68
    outstring+="\n"
    for i in expected_limit:
        outstring += "%s  "%expected_limit[i].l95
    outstring+="\n"
    for i in expected_limit:
        outstring += "%s  "%expected_limit[i].h95
    outstring+="\n"
    f.write(outstring)




def main():
    parser = optparse.OptionParser( description = 'Push Histos.', usage = 'usage: %prog cfgfile outfile.root')
    parser.add_option("-d", "--directory", action="store", dest="directory", help="base path to the limits", default=os.getcwd())
    parser.add_option("-c", "--calculator", action="store", dest="calculator", help="name of the calculator", default= glob.glob(os.getcwd()+"/*.pkl")[0] )
    parser.add_option("-o", "--observed", action="store", dest="observed", help="path to observed limit files", default="observed")
    parser.add_option("-x", "--expected", action="store", dest="expected", help="path to expected limit files", default="expected")
    parser.add_option("--veto", action="store", dest="veto", help="Veto these mass points (comma seperated list)", default="")
    parser.add_option("--crosssection", action="store", dest="crosssection", help="Cross Section file", default="/net/scratch_cms/institut_3a/olschewski/software/limit/SSMCrossSections8TeV.txt")
    parser.add_option("--xmin", action="store", type="int", dest="xmin", help="XMin", default=0)
    parser.add_option("--xmax", action="store", type="int", dest="xmax", help="xMax", default=6000)
    parser.add_option("--ymin", action="store", type="int", dest="ymin", help="yMin", default=0.1)
    parser.add_option("--ymax", action="store", type="int", dest="ymax", help="yMax", default=1000)
    parser.add_option("--s", action="store", type="string", dest="s", help="yMax", default="13 TeV")
    parser.add_option("--xs", action="store", type="string", dest="xs", help="yMax", default="41.82 pb^{-1}" )


    #parser.add_option("-t", "--tohiggs", action="store_true", dest="tohiggs", help="Recalculate non Higgs style to Higgs style", default=False)
    #parser.add_option("-f", "--fromhiggs", action="store_true", dest="fromhiggs", help="Recalculate Higgs style to non Higgs style", default=False)
    #parser.add_option("-g", "--higgs", action="store_true", dest="higgs", help="Plot is Higgs style", default=False)
    #parser.add_option("-p", "--plot", action="store", dest="plotfiles", help="Additional file to plot", default=None)
    #parser.add_option("--plotdir", action="store", dest="plotdir", help="Additional directory with files to plot", default=None)
    #parser.add_option("--lumi", action="store", dest="lumi", help="Lumi / fb-1", default=None)
    #parser.add_option("--dataset", action="store", dest="dataset", help="Dataset 20112012emu", default=None)
    #parser.add_option("--fromroot", action="store_true", dest="fromroot", help="From root (out of order)", default=False)

    #parser.add_option("--muonobsdir", action="store", dest="muonobsdir", help="Muon obs directory", default=None)
    #parser.add_option("--eleobsdir", action="store", dest="eleobsdir", help="Electron obs directory", default=None)
    #parser.add_option("--muonexpdir", action="store", dest="muonexpdir", help="Muon exp directory", default=None)
    #parser.add_option("--eleexpdir", action="store", dest="eleexpdir", help="Electron exp directory", default=None)


    #parser.add_option("--channel", action="store", type="string", dest="channel", help="channel only important for table")
    #parser.add_option("-k", "--config", action="store", type="string", dest="cfgfile", help="Full path to config file", default='/net/scratch_cms/institut_3a/olschewski/limit/singlebin.cfg')
    #parser.add_option("--text", action="store", type="string", dest="text", help="Additional line of text", default=None)
    #parser.add_option("--dm", action="store_true", dest="darkmatter", help="Dark matter", default=False)
    #parser.add_option("--lambda", action="store_true", dest="lamb", help="Dark matter", default=False)
    #parser.add_option("--wprime", action="store_true", dest="wprime", help="Wprime", default=False)

    (options, args ) = parser.parse_args()

    options.expected=os.path.join(options.directory,options.expected)
    veto = options.veto.split(",")

    f = open(os.path.join(options.directory,options.calculator),'rb')
    calculator = cPickle.load(f)
    f.close()

    plotting_helper.merge_root_files(options.expected)
    limits=plotting_helper.get_from_expected_dir(options.expected,calculator.method=="asymptotic")
    parameters={}

    for hypo in calculator.hypothesis:
        for par in hypo.parameters:
            if hypo.parameters[par] in veto:
                continue
            if par in parameters:
                parameters[par].append(hypo.parameters[par])
            else:
                parameters[par]=[]
                parameters[par].append(hypo.parameters[par])
    lumis=set()
    pois=dict()
    no_float_par=[]

    for par in parameters.keys()+["lumi"]:
        pois[par]=set()
        for limit in limits:
            pois[par].add(limit[par])

    for par in pois:
        pois[par]=list(pois[par])
        try:
            pois[par].sort(key=lambda x: float(x))
        except:
            pois[par].sort()


    c1 = ROOT.TCanvas("c1","",800,800)
    c1.SetLogx()
    c1.SetLogy()
    print pois


    #fixed_pois_lists=[pois[i] for i in pois]
    #combinations=itertools.product(*fixed_pois_lists)
    for par in pois:
        try:
            float(pois[par][0])
        except:
            continue
        variable_pois=filter(lambda x: x!=par ,pois)
        varible_pois_lists=[pois[i] for i in variable_pois]


        combinations=itertools.product(*varible_pois_lists)
        for combi in combinations:
            
            print "par", par, "combi", combi
            
            expected_limit=collections.OrderedDict()
            for ipar in pois[par]:
                reduced_limits=filter(lambda x: x[par]==ipar,limits)
                limit=find_parmeter_in_limit(reduced_limits,combi,variable_pois)
                if limit is not None:
                    expected_limit[ipar]=limit["limit"]
            if len(expected_limit)==0:
                continue
            c1.SetLogx(True)
            x95,y95=plotting_helper.get_arrays_from_expected(expected_limit,"l95","h95")
            f95 = ROOT.TGraph(len(x95),x95,y95);

            f95.SetFillColor(ROOT.kYellow)
            f95.SetTitle("")
            #~ if par=="Mmed" or par=="mxi": f95.GetXaxis().SetTitle(par +" [GeV]")
            if par=="Mmed": f95.GetXaxis().SetTitle("m_{Med}" +" (GeV)")
            elif par=="mxi": f95.GetXaxis().SetTitle("m_#xi" +" (GeV)")
            else: f95.GetXaxis().SetTitle(par)
            f95.GetYaxis().SetTitle("#sigma #times B "+unit("pb"))
            f95.GetXaxis().SetRangeUser(options.xmin,options.xmax)
            f95.GetYaxis().SetRangeUser(options.ymin,options.ymax)
            x68,y68=plotting_helper.get_arrays_from_expected(expected_limit,"l68","h68")
            f68 = ROOT.TGraph(len(x68),x68,y68);
            f68.SetFillColor(ROOT.kGreen)

            f95.Draw("af")
            f68.Draw("f")


            x50,y50=plotting_helper.get_arrays_from_expected(expected_limit,"median")
            lexpected = ROOT.TGraph(len(x50),x50,y50)
            lexpected.SetLineColor(1)
            lexpected.SetLineStyle(7)
            lexpected.SetLineWidth(3)
            lexpected.Draw("L")
            if min(x50)<=0:
                c1.SetLogx(False)
            c1.Update()

            try:
                # if present, plot observed limit:
                x50,y50=plotting_helper.get_observed_limit("observed", par, combi)
                lobserved = ROOT.TGraph(len(x50),x50,y50)
                lobserved.Sort()
                lobserved.SetLineColor(1)
                lobserved.SetLineStyle(1)
                lobserved.SetLineWidth(3)
                lobserved.Draw("L")
            except:
                print "Omitting observed limit."

            name="Limit"
            for i in range(len(variable_pois)):
                name+="_%s_%s"%(variable_pois[i],combi[i])
                name+="_"+os.getcwd().split("/")[-1]
            write_table(name,pois,par,variable_pois,combi,expected_limit)


            
            
            leg = ROOT.TLegend(0.65,0.75,0.89,0.89);
            leg.AddEntry(lexpected,"expected limit","l")
            leg.AddEntry(f68,"expected limit #pm 1 #sigma","f")
            leg.AddEntry(f95,"expected limit #pm 2 #sigma","f")
            leg.AddEntry(lobserved,"observed limits","l")
            leg.Draw()

            #~ gStyle.SetStatStyle(0);
            #~ gStyle.SetTitleStyle(0); 
            leg.SetFillColor(0);
            leg.SetBorderSize(0);
            
            
            tex= ROOT.TLatex(0.6,0.91,"#font[42]{#scale[0.8]{"+options.xs+" ("+options.s+")}}") #42pb
            tex.SetNDC()
            tex.SetTextSize(0.05)
            tex.Draw("same")
        
            
        
                
            c1.SaveAs(name+".root")
            c1.SaveAs(name+".pdf")
            c1.SaveAs(name+".png")

    



                #for limit in limits:
                    #found=0
                    #for p in range(len(variable_pois)):
                        #if limit[variable_pois[p]]==combi[p]:
                            #found+=1
                    #if found==len(variable_pois):
                        #break



                    #expected_limit[combi]=limits[




        #for ipar in pois[par]:
            #print par,ipar
            #expected_limit=collections.OrderedDict()


            #for combi in combinations:
                #if ipar in combi:
                    #expected_limit[






        #print par
        #fixed_pois=filter(lambda x: x!=par ,pois)
        #fixed_pois_lists=[pois[i] for i in pois]
        #print fixed_pois_lists

        #combinations=itertools.product(*fixed_pois_lists)
        #for combi in combinations:
            #print combi
        #print combinations
        ##for otherpar in limits:





            #expected_limit=collections.OrderedDict()
            #for i in parameters[par]:
                #expected_limit[i]=limits[par][i][lumi]

            #x95,y95=plotting_helper.get_arrays_from_expected(expected_limit,"l95","h95")
            #f95 = ROOT.TGraph(len(x95),x95,y95);

            #f95.SetFillColor(ROOT.kYellow)
            #f95.SetTitle("")
            #f95.GetXaxis().SetTitle(par)
            #f95.GetYaxis().SetTitle("#sigma #times B "+unit("fb"))
            #f95.GetXaxis().SetRangeUser(options.xmin,options.xmax)
            #x68,y68=plotting_helper.get_arrays_from_expected(expected_limit,"l68","h68")
            #f68 = ROOT.TGraph(len(x68),x68,y68);
            #f68.SetFillColor(ROOT.kGreen)

            #f95.Draw("af")
            #f68.Draw("f")


            #x50,y50=plotting_helper.get_arrays_from_expected(expected_limit,"median")
            #lexpected = ROOT.TGraph(len(x50),x50,y50)
            #lexpected.SetLineColor(1)
            #lexpected.SetLineStyle(7)
            #lexpected.SetLineWidth(3)
            #lexpected.Draw("L")
            #c1.Update()

            #print "-----------------------"
            #print "limit for:",par
            #for i in parameters[par]:
                #print i,"  ",
            #print
            #for i in parameters[par]:
                #print expected_limit[i].median,"  ",
            #c1.SaveAs("Limit_%s_lumi_%s.root"%(par,lumi))
            #c1.SaveAs("Limit_%s_lumi_%s.pdf"%(par,lumi))
            #c1.SaveAs("Limit_%s_lumi_%s.png"%(par,lumi))





        #if len(parameters[par])>1:
            #for lumi in lumis:


                ##c1.SetLogx()
                #expected_limit=collections.OrderedDict()
                #for i in parameters[par]:
                    #expected_limit[i]=limits[par][i][lumi]

                #x95,y95=plotting_helper.get_arrays_from_expected(expected_limit,"l95","h95")
                #f95 = ROOT.TGraph(len(x95),x95,y95);

                #f95.SetFillColor(ROOT.kYellow)
                #f95.SetTitle("")
                #f95.GetXaxis().SetTitle(par)
                #f95.GetYaxis().SetTitle("#sigma #times B "+unit("fb"))
                #f95.GetXaxis().SetRangeUser(options.xmin,options.xmax)
                #x68,y68=plotting_helper.get_arrays_from_expected(expected_limit,"l68","h68")
                #f68 = ROOT.TGraph(len(x68),x68,y68);
                #f68.SetFillColor(ROOT.kGreen)

                #f95.Draw("af")
                #f68.Draw("f")


                #x50,y50=plotting_helper.get_arrays_from_expected(expected_limit,"median")
                #lexpected = ROOT.TGraph(len(x50),x50,y50)
                #lexpected.SetLineColor(1)
                #lexpected.SetLineStyle(7)
                #lexpected.SetLineWidth(3)
                #lexpected.Draw("L")
                #c1.Update()

                #print "-----------------------"
                #print "limit for:",par
                #for i in parameters[par]:
                    #print i,"  ",
                #print
                #for i in parameters[par]:
                    #print expected_limit[i].median,"  ",
                #c1.SaveAs("Limit_%s_lumi_%s.root"%(par,lumi))
                #c1.SaveAs("Limit_%s_lumi_%s.pdf"%(par,lumi))
                #c1.SaveAs("Limit_%s_lumi_%s.png"%(par,lumi))

        #if len(lumis)>1:
            #for ipar in parameters[par]:

                #expected_limit=collections.OrderedDict()
                #for i in lumis:

                #f95.SetFillColor(ROOT.kYellow)
                #f95.SetTitle("")
                #f95.GetXaxis().SetTitle("lumi "+unit("fb^{-1}"))
                #f95.GetYaxis().SetTitle("#sigma #times B "+unit("fb"))
                #f95.GetXaxis().SetRangeUser(options.xmin,options.xmax)
                #x68,y68=plotting_helper.get_arrays_from_expected(expected_limit,"l68","h68")
                #f68 = ROOT.TGraph(len(x68),x68,y68);
                #f68.SetFillColor(ROOT.kGreen)

                #f95.Draw("af")
                #f68.Draw("f")


                #x50,y50=plotting_helper.get_arrays_from_expected(expected_limit,"median")
                #lexpected = ROOT.TGraph(len(x50),x50,y50)
                #lexpected.SetLineColor(1)
                #lexpected.SetLineStyle(7)
                #lexpected.SetLineWidth(3)
                #lexpected.Draw("L")
                #c1.Update()


                #print "-----------------------"
                #print "limit for:",par
                #for i in lumis:
                    #print i,"  ",
                #print
                #for i in lumis:
                    #print expected_limit[i].median,"  ",

                #c1.SaveAs("Limit_%s_for_%s.root"%(par,ipar))
                #c1.SaveAs("Limit_%s_for_%s.pdf"%(par,ipar))
                #c1.SaveAs("Limit_%s_for_%s.png"%(par,ipar))













if __name__=="__main__":
    main()
