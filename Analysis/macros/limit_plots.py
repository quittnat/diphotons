#!/bin/env python

from diphotons.Utils.pyrapp import *
from optparse import OptionParser, make_option
from copy import deepcopy as copy
import os, sys, glob, json

from auto_plotter import getObjects

def guessLabel(name):
    if "EBEB" in name: return "EBEB"
    elif "EBEE" in name: return "EBEE"
    elif "8TeV" in name: return "8TeV"
    elif "13TeV" in name: return "13TeV"
    else: return "Combined"
    

def scaleGraph(graph,scale):
    graph = graph.Clone()
    graph.GetListOfFunctions().Clear()
    ## graph.Print()
    
    xvals = graph.GetX()
    yvals = graph.GetY()
    yerrl = graph.GetEYlow()
    yerrh = graph.GetEYhigh()
    for ip in xrange(graph.GetN()):
        scl = scale(xvals[ip]) 
        ## print scl
        graph.SetPoint( ip, xvals[ip], yvals[ip]*scl )
        try:
            graph.SetPointEYlow( ip, yerrl[ip]*scl )
            graph.SetPointEYhigh( ip, yerrh[ip]*scl )
        except:
            pass
    
    ## graph.Print()
    
    return graph

def fitFunc(graph,func):
    
    ## func = func.Clone()
    graph.Fit(func)
    return func.Clone()

# -----------------------------------------------------------------------------------------------------------
class LimitPlot(PlotApp):

    def __init__(self):
        super(LimitPlot,self).__init__(option_list=[
                make_option("--do-limits",action="store_true", dest="do_limits", 
                            default=False),
                make_option("--do-pvalues",action="store_true", dest="do_pvalues", 
                            default=False),
                make_option("--compute-LEE",action="store_true", dest="compute_lee", 
                            default=False,help="for the computation of lee, creates trees etc from scratch"),
                make_option("--trial-factor",action="store_true", dest="trial_factor", 
                            default=False,help="fits trial factor on distribution of maximum pvalues"),
                make_option("--plot-LEE",action="store_true", dest="plot_lee", 
                            default=False,help="plots the maximum signficance if trees already exist"),
                make_option("--plot-locpval",action="store_true", dest="plot_locpval", 
                            default=False,help="plots the local p value "),
                make_option("--output-dir",action="store", dest="output_dir", 
                            default="./"),
                make_option("--do-comparison",action="store_true", dest="do_comparison", 
                            default=False),
                make_option("--compare-expected",action="store_true", dest="compare_expected", 
                            default=False),
                make_option("--compare-file","--compare-files",dest="compare_files",action="callback",type="string", callback=optpars_utils.ScratchAppend(str),
                            default=[]),
                make_option("--compare-label","--compare-labels",dest="compare_labels",action="callback",type="string", callback=optpars_utils.ScratchAppend(str),
                            default=[]),
                make_option("--asimov-expected",action="store_true", dest="asimov_expected", 
                            default=True),
                make_option("--toys-expected",action="store_false", dest="asimov_expected", 
                            ),
                make_option("--x-range",dest="x_range",action="callback",type="string", callback=optpars_utils.ScratchAppend(float),
                            default=[450.,5000.]),
                make_option("--legend",dest="legend",action="callback",type="string", callback=optpars_utils.ScratchAppend(float),
                            default=[0.56,0.51,0.86,0.76]),
                make_option("-n","--label",action="store", dest="label", 
                            default=""),                
                make_option("-M","--method",action="store", dest="method", 
                            default="Asymptotic"),                
                make_option("-U","--unblind",action="store_true", dest="unblind", 
                            default=False),                
                make_option("-B","--blind",action="store_false", dest="unblind", 
                            ),                
                make_option("-k","--couplings",action="callback", dest="couplings", type="string", callback=optpars_utils.ScratchAppend(str),
                            default=[]),                
                make_option("-x","--x-sections",action="callback", dest="x_sections", type="string", callback=optpars_utils.Load(),
                            default={}),                
                make_option("--fixed-x-section",action="store", dest="fixed_x_section", type="float", 
                            default=None), 
                make_option("--nToys",action="store", dest="nToys",type="int", 
                            default=None), 
                make_option("--nJobs",action="store", dest="nJobs",type="int", 
                            default=0), 
                make_option("--fixed-x-section-ratio",action="store", dest="fixed_x_section_ratio", type="string", 
                            default=None), 
                make_option("--use-fb",dest="use_fb", action="store_true", 
                            default=False), 
                
            ])
        
        global ROOT, style_utils, RooFit
        import ROOT
        from ROOT import RooFit
        from ROOT import RooAbsData
        import diphotons.Utils.pyrapp.style_utils as style_utils


    def __call__(self,options,args):
        self.loadRootStyle()
        
        ROOT.gStyle.SetTitleYOffset(1.)
        ROOT.gStyle.SetTitleXOffset(1.15)
        ROOT.gStyle.SetOptStat(111111)

        # ROOT.gSystem.AddIncludePath( "$ROOTSYS/include" )
        ROOT.gROOT.LoadMacro( "$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/plotting/bandUtils.cxx+" )
        
        self.loadXsections(options.x_sections)

        if options.do_comparison:
            if len(options.compare_labels) > 0: assert( len(options.compare_labels) == len(options.compare_files) )
            else: options.compare_labels = map(guessLabel, options.compare_files)
            self.compare = map(lambda x: (getObjects([self.open(x[0])]),x[1]), zip(options.compare_files,options.compare_labels) )
            self.plotComparisons(options)
            return

        print options.couplings
        if options.compute_lee or options.plot_lee or options.trial_factor:
            flist = [ "%s/higgsCombine%s_k%s.%s.%d.root" % (options.input_dir, options.label, options.couplings[0],options.method,job)  for job in range(0,options.nJobs+1) ]
        else:
            if len(options.couplings) == 0:
                flist = glob.glob("%s/higgsCombine%s_k*.%s.root" % (options.input_dir, options.label, options.method) )
            else:
                flist = [ "%s/higgsCombine%s_k%s.%s.root" % (options.input_dir, options.label, coup, options.method) for coup in options.couplings ]
        if options.plot_locpval:
            flist =["%s/higgsCombine_%s.%s.root" % (options.input_dir, options.label,options.method)]
        if not options.compute_lee: print options.input_dir, flist
            
        tflist = {}
        tflist_job = {}
        for fname in flist:
            bname = os.path.basename(fname)
            job = bname.replace(".root","").rsplit(".",1)[-1]
            dname =options.input_dir
            if options.compute_lee or options.plot_lee or options.trial_factor:
                spin = dname.replace("combined","").split("_",-1)[1].replace("spin","")
            else:
                print "[WARNING] assume spin2 for labels "
                spin=2
            coup = bname.split("_",1)
            coup = coup[1].split(".")
            coup = coup[0].replace("k","")
            
            if options.plot_locpval:
                sname = bname.rsplit("GeV",1)[1].split(".ProfileLikelihood",1)[0]
                mname = bname.rsplit("GeV",1)[0].rsplit("_",1)[1]
                print sname,mname
            tfin = self.open(fname)
            if not tfin: 
                print ("unable to open %s" % fname)
                sys.exit(-1)
            tree = tfin.Get("limit")
            if not tree: 
                print ("unable to find limit tree in %s" % fname)
                if options.compute_lee or options.plot_lee or options.trial_factor:
                    continue
                else:
                    sys.exit(-1)
        
            if options.compute_lee:
               # if (coup=="all" and (spin=="0" or spin=="2")):holynr=(1286)*options.nToys
                #elif (coup=="all" and (spin=="all")):holynr=(1286)*2*options.nToys
                #elif ((coup=="001" or  coup=="01" or coup =="02") and (spin=="0" or spin=="2")):holynr=(428)*options.nToys
                if (coup=="all" and (spin=="0" or spin=="2")):holynr=(404*3)*options.nToys
                elif (coup=="all" and (spin=="all")):holynr=(404*3)*2*options.nToys
                elif ((coup=="001" or  coup=="01" or coup =="02") and (spin=="0" or spin=="2")):holynr=(404)*options.nToys
                else: holynr=1e15
                if tree.GetEntries() < holynr:
                    print "[WARNING ] job ", job, ": tree has not expected number of entries "
                    continue
                else: tflist_job[job] = tfin
            else:
                tflist[coup] = tfin
        
        self.graphs = []
        for coup,tfile in tflist.iteritems():

            if options.do_limits:
                print coup, tfile
                self.plotLimit(options,coup,tfile)
            if options.do_pvalues:
                observed = ROOT.theBand( tfile, 1, 0, ROOT.Observed, 0.95 )
                self.plotPval(options,coup,spin,tfile,observed)
        for job,tfile in tflist_job.iteritems():
            if options.compute_lee: self.getPvalToys(options,coup,spin, job,tfile)
               
        self.autosave()
        if not (options.plot_lee or options.trial_factor or options.plot_locpval):
            if options.compute_lee:
                for job in range(0,options.nJobs+1):
                    graphs = self.open("%s/graphs_%s_%s_%s.%s.root" % (options.input_dir,"_".join(options.couplings),spin,job,options.method),"recreate")
            else:
                if len(options.couplings) == 0:
                    graphs = self.open("%s/graphs_%s.root" % (options.input_dir,options.method),"recreate") #makes one file with everyting
                else:
                    graphs = self.open("%s/graphs_%s_%s.root" % (options.input_dir,"_".join(options.couplings),options.method),"recreate")
            graphs.cd()
            for gr in self.graphs: gr.Write()
            graphs.Close()
        if (options.compute_lee or options.plot_lee or options.trial_factor) : self.plotLEE(options,coup,spin)
        if  options.plot_locpval: self.plotLocpval(options,coup,sname,mname)
        
    def plotLimit(self,options,coup,tfile):
        ## TGraphAsymmErrors *theBand(TFile *file, int doSyst, int whichChannel, BandType type, double width=0.68) {
        if options.asimov_expected:
            ROOT.use_precomputed_quantiles = True
            bandType = ROOT.Median 
        else:
            bandType = ROOT.Median
        expected68 = ROOT.theBand( tfile, 1, 0, bandType, 0.68 )
        expected95 = ROOT.theBand( tfile, 1, 0, bandType, 0.95 )
        observed = ROOT.theBand( tfile, 1, 0, ROOT.Observed, 0.95 )
        unit = "fb" if options.use_fb else "pb"
        basicStyle = [["SetMarkerSize",0.6],["SetLineWidth",3],
                       ["SetTitle",";m_{G} (GeV);95%% C.L. limit #sigma(pp#rightarrow G#rightarrow#gamma#gamma) (%s)" % unit]]
        commonStyle = [[self.scaleByXsec,coup],"Sort"]+basicStyle
        ## expectedStyle = commonStyle+[["SetMarkerStyle",ROOT.kOpenCircle]]
        expectedStyle = commonStyle+[["SetMarkerSize",0]]
        observedStyle = commonStyle+[["SetMarkerStyle",ROOT.kFullCircle]]
        
        style_utils.apply( expected68, [["colors",ROOT.kYellow],["SetName","expected68_%s"%coup]]+expectedStyle )
        style_utils.apply( expected95, [["colors",ROOT.kGreen],["SetName","expected95_%s"%coup]]+expectedStyle )
        
        expected = ROOT.TGraph(expected68)
        style_utils.apply( expected, [["colors",ROOT.kBlack],["SetLineStyle",7],["SetName","expected_%s"%coup]])
        
        style_utils.apply(observed,[["SetName","observed_%s"%coup]]+observedStyle)
      
        canv  = ROOT.TCanvas("limits_k%s"%coup,"limits_k%s"%coup)
        canv.SetLogx()
        legend = ROOT.TLegend(0.6,0.6,0.9,0.9)
        expected95.Draw("AE3")        
        expected95.GetXaxis().SetRangeUser(450,5500)
        expected95.GetXaxis().SetMoreLogLabels()
        expected68.Draw("E3L")
        expected.Draw("L")
        kappa = "0."+coup[1:]
        legend.AddEntry(None,"#tilde{#kappa} = %s" % kappa,"")
        legend.AddEntry(expected,"Expected limit","l")
        legend.AddEntry(expected68," \pm 1 \sigma","f")
        legend.AddEntry(expected95," \pm 2 \sigma","f")
        if options.unblind:
            observed.Draw("PL")
            ## observed.Draw("L")
            legend.AddEntry(observed,"Observed limit","l")
        if coup in self.xsections_:
            grav = self.xsections_[coup]
            style_utils.apply( grav, basicStyle+[["SetLineStyle",9],["colors",ROOT.myColorB2]] )
            grav.Draw("L")
            legend.AddEntry(grav,"G_{RS}#rightarrow#gamma#gamma (LO)","l").SetLineStyle(0)
            
        self.keep(legend,True)
        legend.Draw()
        
        self.graphs.extend([observed,expected,expected68,expected95])
        
        self.keep( [canv,observed,expected,expected68,expected95] )
        self.format(canv,options.postproc)

    def plotComparisons(self,options):
        if options.compare_expected:
            observed = map(lambda x: (filter(lambda y: "expected" in y.GetName(), x[0]),x[1]), self.compare)
            coups = set(map(lambda x: x.GetName().replace("expected_",""), reduce(lambda x,y: x+y, map(lambda z: z[0], observed), [])))
        else:
            observed = map(lambda x: (filter(lambda y: "observed" in y.GetName(), x[0]),x[1]), self.compare)
            coups = set(map(lambda x: x.GetName().replace("observed_",""), reduce(lambda x,y: x+y, map(lambda z: z[0], observed), [])))
        ## coups = ["001","01","02"]
        coups = ["001"]
        if len(options.couplings) > 0:
            coups = options.couplings

        map(lambda x: self.plotComparison(options,x,observed), coups)

    def plotComparison(self,options,coup,observed):
        
        cobserved = map(lambda x: (filter(lambda y: y.GetName().endswith("_%s" % coup), x[0])[0],x[1]), observed)
        print cobserved
        
        ## styles = [ [["colors",ROOT.kBlue]], [["colors",ROOT.kRed+1]], [["colors",ROOT.kMagenta-2]] ]
        styles = [ [["colors",ROOT.kBlack]], [["colors",ROOT.kBlue],["SetLineStyle",2]], [["colors",ROOT.kRed],["SetLineStyle",2]] ]
        map(lambda x: style_utils.apply(x[0],[["SetMarkerSize",0.3],["SetLineWidth",2]]+styles.pop(0)), cobserved)
    
        canv = ROOT.TCanvas("comparison_%s" % coup,"comparison_%s" % coup)
        legend = ROOT.TLegend(*options.legend)
        ## legend = ROOT.TLegend(0.56,0.51,0.86,0.76)
        ## legend = ROOT.TLegend(0.6,0.51,0.9,0.76)
        ## legend = ROOT.TLegend(0.6,0.2,0.9,0.42)
        ## legend = ROOT.TLegend(0.45,0.2,0.75,0.42)
        legend.SetFillStyle(0)
        kappa = "0."+coup[1:]
        legend.AddEntry(None,"#tilde{#kappa} = %s" % kappa,"")
        
        g0 = cobserved[0][0]
        g0.GetXaxis().SetTitle("m_{G} (GeV)")
        g0.Draw("apl")
        for gr,nam in cobserved:
            legend.AddEntry(gr,nam,"l")
        for gr,nam in reversed(cobserved):
            gr.Draw("pl")
        legend.Draw("same")
        
        xmin,xmax = options.x_range
        ## g0.GetXaxis().SetRangeUser(450,5000)
        ## g0.GetXaxis().SetRangeUser(500,3000)
        ## g0.GetXaxis().SetRangeUser(500,850)
        ## g0.GetXaxis().SetRangeUser(850,3000)
        g0.GetXaxis().SetRangeUser(xmin,xmax)
        g0.GetXaxis().SetMoreLogLabels()
        canv.SetLogx()
        if options.do_pvalues:
            canv.SetLogy()
            g0.GetYaxis().SetRangeUser(1e-3,0.55)
            self.drawLines(g0,xmin,xmax)
            ## self.drawLines(g0,450,5000)
            ## self.drawLines(g0,500,3000)
            ## self.drawLines(g0,500,850)
            ## self.drawLines(g0,850,3000)
        
        self.keep([canv,legend])
        self.format(canv,options.postproc)
        
    def drawLines(self,ref,xmin=450,xmax=5000):
        
        spots = filter(lambda x: x>ref.GetYaxis().GetXmin(),  map(lambda x: (x,ROOT.RooStats.SignificanceToPValue(x)), xrange(1,5) ) )
        
        lines = map( lambda y: ROOT.TLine(xmin,y[1],xmax,y[1]), spots )
        map( lambda x: style_utils.apply(x,[["SetLineColor",ROOT.kGray+3],["SetLineStyle",7]]), lines )
        
        labels = map( lambda y: ROOT.TLatex(xmax*1.01,y[1]*0.9,"#color[%d]{%d #sigma}" % (ROOT.kGray+2,y[0])), spots )
        map( lambda x: style_utils.apply(x,[["SetTextSize",0.05]]), labels )

        map( lambda x: x.Draw("same"), lines+labels )
        self.keep(lines+labels)

    def getPvalToys(self,options, coup,spin,ijob,tfile):
        tree = tfile.Get("limit")
        print "jobs ", ijob , " #toys ", options.nToys, "couplings", coup, " #masspoints " ,tree.GetEntries()/options.nToys
        tp = ROOT.TNtuple("tree_pval_k%s_s%s_t%s_j%s" % (coup,spin,options.nToys, ijob),"tree_pval_k%s_s%s_t%s_j%s" % (coup,spin,options.nToys, ijob),"toy:pval" )
        for itoy in range(1,options.nToys+1):
            observed = ROOT.theBand( tfile, 1, 0, ROOT.ToyObserved, 0.95,itoy )
            maxpval=ROOT.TMath.MinElement(observed.GetN(),observed.GetY())
            tp.Fill(itoy,maxpval)
           # print "itoy ", itoy , "max ", maxpval
            self.plotPval(options,coup,spin,tfile,observed,itoy,ijob)
        tp.SaveAs("%s/tree_pval_k%s_s%s_t%s_j%s.root" % (options.input_dir,coup,spin,options.nToys, ijob))

    def plotLEE(self,options, coup,spin):
        canv = ROOT.TCanvas("cqtoy","cqtoy")
        histo=ROOT.TH1D("qtoy","qtoy",300,1.,5.)
       # histo_pval=ROOT.TH1D("qtoy_pval","qtoy_pval",200,1e-4,0.5)
        pmin=1e-6
        pmax=0.08
        histo_pval=ROOT.TH1D("qtoy_pval","qtoy_pval",200,pmin,pmax)
        for ijob in range(0,options.nJobs):
            fname= "%s/tree_pval_k%s_s%s_t%s_j%s.root" % (options.input_dir,coup,spin,options.nToys, ijob)
            tfin = self.open(fname)
            if not tfin: 
                print ("unable to open %s" % fname)
                continue
            #tree = tfin.Get("tree_pval_k%s_s%s_t%s_j100" % (coup,spin,options.nToys))
            tree = tfin.Get("tree_pval_k%s_s%s_t%s_j%s" % (coup,spin,options.nToys,ijob))
            toyStyle = [["SetFillStyle",3004],["SetLineColor",ROOT.kRed]]
            style_utils.apply(histo,[["SetTitle",";Max Significance ;Entries (Toys)"],["SetName","max significance k%s s%s" %(coup,spin)]]+toyStyle)
            for toy in range(0,tree.GetEntries()):
                tree.GetEntry(toy)
                significance=ROOT.ROOT.Math.normal_quantile_c(tree.pval, 1.0)
                histo.Fill(significance)
                if options.trial_factor:
                    histo_pval.Fill(tree.pval)
        self.keep(histo_pval)
        if spin=="0":
            obsZ=2.856 
            obsP=0.0021451# @ 756 GeV
        elif (spin=="2" or spin== "all"):
            obsZ=2.93149
            obsP=0.00168668# @ 758 GeV
        else: print "no oberved "
        print "significance 2.9: pval: ", histo.Integral(histo.GetXaxis().FindBin(2.9),histo.GetXaxis().FindBin(histo.GetMaximumBin()))/histo.Integral()
        integral=histo.Integral(histo.GetXaxis().FindBin(obsZ),histo.GetXaxis().FindBin(histo.GetMaximumBin()))/histo.Integral()
        if options.trial_factor:
            cdf=self.cdf(histo_pval,histo.GetNbinsX(),pmin,pmax) 
            self.keep(cdf)
        
        canv.cd()
        histo.Rebin(5)
        histo.Draw("HIST E2")
        ROOT.gStyle.SetOptStat(111111)
        lineObs=ROOT.TLine(obsZ,0.,obsZ,histo.GetMaximum())
        lineObs.SetLineColor(ROOT.kBlack)
        lineObs.SetLineWidth(3)
        lineObs.Draw()
        b=ROOT.TLatex()
        b.SetNDC()
        b.SetTextSize(0.035)
        b.SetTextColor(ROOT.kBlack)
        b.DrawLatex(0.65,0.5,"global pval: %.2e" % integral)
        b.DrawLatex(0.65,0.4,"global Z: %4.2f" % ROOT.ROOT.Math.normal_quantile_c(integral,1.0))
        b.DrawLatex(0.65,0.3,"trial factor: %d " %( integral/obsP))

        canv.SaveAs("%s/LEE_k%s_s%s.root" % (options.output_dir,coup,spin))
        canv.SaveAs("%s/LEE_k%s_s%s.png" % (options.output_dir,coup,spin))
        canv.SaveAs("%s/LEE_k%s_s%s.pdf" % (options.output_dir,coup,spin))
        self.keep( [canv,histo] )

        if options.trial_factor:
            ccdf = ROOT.TCanvas("ccdf","ccdf")
            ccdf.cd()
            ROOT.gStyle.SetOptStat(0)
            pminfit=1e-5
            pmaxfit=0.006
            vsfit =ROOT.TF1("vsfit","[0]*x+[1]",pmin,pmax)
            vsfit.SetParameters(60, 0)
            cdf.Fit(vsfit,"R","",pminfit,pmaxfit)
            cdf.GetXaxis().SetRangeUser(pminfit,pmaxfit)
            cdf.GetXaxis().SetTitle("Min p-value")
            cdf.GetYaxis().SetTitle("CDF")
            cdf.Draw("HIST")
            c=ROOT.TLatex()
            c.SetNDC()
            c.SetTextSize(0.04)
            c.SetTextColor(ROOT.kBlack)
            c.DrawLatex(0.45,0.4,"fit range pmin: %.2e ( z= %4.2f )" % (pminfit,ROOT.ROOT.Math.normal_quantile_c(pminfit,1.0)))
            c.DrawLatex(0.55,0.3,"pmax: %.2e ( z= %4.2f )" % (pmaxfit,ROOT.ROOT.Math.normal_quantile_c(pmaxfit,1.0)))
            c.DrawLatex(0.55,0.2,"trial factor: %d" % (vsfit.GetParameter(0)))

            vsfit.Draw("SAME")
       #     self.keep( [ccdf,cdf] )
            ccdf.SaveAs("%s/cdf_pval_k%s_s%s.root" % (options.output_dir,coup,spin))
            ccdf.SaveAs("%s/cdf_pval_k%s_s%s.png" % (options.output_dir,coup,spin))
            ccdf.SaveAs("%s/cdf_pval_k%s_s%s.pdf" % (options.output_dir,coup,spin))
            cpval = ROOT.TCanvas("cpval","cpval")
            cpval.cd()
            cpval.SetLogx()
            ROOT.gStyle.SetOptStat(11111111)
            histo_pval.Draw("HIST")
            histo_pval.GetXaxis().SetTitle("Min p-value")
            histo_pval.GetYaxis().SetTitle("Entries (Toys)")
            cpval.SaveAs("%s/cpval_k%s_s%s.root" % (options.output_dir,coup,spin))
            cpval.SaveAs("%s/cpval_k%s_s%s.png" % (options.output_dir,coup,spin))
            cpval.SaveAs("%s/cpval_k%s_s%s.pdf" % (options.output_dir,coup,spin))
    
    def plotLocpval(self,options,coup, sname,mname):
        canv = ROOT.TCanvas("cqtoy","cqtoy")
        histo=ROOT.TH1D("qtoy","qtoy",5000,0.,6.)
        fname= "%s/higgsCombine_spin2_k001_%sGeV%s.ProfileLikelihood.root" % (options.input_dir,mname,sname)
        tfin = self.open(fname) #TODO difine mname and sname for input
        if not tfin: 
            print ("unable to open %s" % fname)
        tree = tfin.Get("limit")
        toyStyle = [["SetFillStyle",3004],["SetLineColor",ROOT.kRed]]
        style_utils.apply(histo,[["SetTitle",";Significance ;Entries (Toys)"],["SetName","k%s s2 %s %s" %(coup,mname,sname)]]+toyStyle)
        for toy in range(0,tree.GetEntries()):
            tree.GetEntry(toy)
           # if tree.limit !=0:

            significance=ROOT.RooStats.PValueToSignificance(tree.limit)
            histo.Fill(significance)
        if (sname=="_8_13TeV"):obsZ=3.35548#@750 GeV  p-value of background: 0.000396131  (Significance = 3.35548)
        elif (sname=="_13TeV" and mname=="760"):obsZ=2.92222# @ 760 GeV p-value of background: 0.00173774 (Significance = 2.92222)
        elif (sname=="_13TeV" and mname=="600"):obsZ=0.527256# @ 600 GeV  pvalue: 0.29900 Significance = 0.527256
     ##   elif (sname=="_13TeV"):obsZ=2.93# @ 760 GeV p-value of background: 0.00173774 (Significance = 2.92222)
        else: print "no oberved "
        integral=histo.Integral(histo.GetXaxis().FindBin(obsZ),-1)/histo.Integral()
        canv.cd()
        canv.SetLogy()
        histo.Rebin(50)
        histo.Draw("HIST E2")
        ROOT.gStyle.SetOptStat(111111)
        lineObs=ROOT.TLine(obsZ,0.,obsZ,histo.GetMaximum())
        lineObs.SetLineColor(ROOT.kBlack)
        lineObs.SetLineWidth(3)
        lineObs.Draw()
        b=ROOT.TLatex()
        b.SetNDC()
        b.SetTextSize(0.035)
        b.SetTextColor(ROOT.kBlack)
        b.DrawLatex(0.75,0.5,"pval: %.2e" % integral)
        b.DrawLatex(0.75,0.4,"Z: %4.2f" % ROOT.RooStats.PValueToSignificance(integral))

        canv.SaveAs("%s/LocPVal_k%s_spin2_%s%s.root" % (options.output_dir,coup,mname,sname))
        canv.SaveAs("%s/LocPVal_k%s_spin2_%s%s.png" % (options.output_dir,coup,mname,sname))
        canv.SaveAs("%s/LocPVal_k%s_spin2_%s%s.pdf" % (options.output_dir,coup,mname,sname))
        self.keep( [canv,histo] )


    def cdf(self,histo,bins,min,max):
        cdf=ROOT.TH1D("cdf","cdf",bins,min,max)
        total = 0
        for i in range(0,bins):
            total =int(total + histo.GetBinContent(i))
            for k in range(0,total):
                cdf.AddBinContent(i)
        norme = 1/histo.Integral()
        print norme
        cdf.Scale(norme)
        return cdf

    def plotPval(self,options,coup,spin,tfile,observed,itoy=0,ijob=0):
        basicStyle = [["SetMarkerSize",0.6],["SetLineWidth",3],
                       ["SetTitle",";m_{G} (GeV);p_{0}"]]
        commonStyle = ["Sort"]+basicStyle
        observedStyle = commonStyle+[["SetMarkerStyle",ROOT.kFullCircle],["colors",ROOT.kBlue]]
        if(itoy==0):style_utils.apply(observed,[["SetName","observed_%s"%coup]]+observedStyle)
        else:       style_utils.apply(observed,[["SetName","observed_%s_%s"%(coup,itoy)]]+observedStyle)
      
        
        xmin,xmax = options.x_range
        if(itoy==0):canv  = ROOT.TCanvas("pvalues_k%s_s%s"%(coup,spin),"pvalues_k%s_s%s"%(coup,spin))
        else:       canv  = ROOT.TCanvas("pvalues_k%s_s%s_t%s_j%s"%(coup,spin,itoy,ijob),"pvalues_k%s_s%s_t%s_j%s"%(coup,spin,itoy,ijob))
        canv.SetLogy()
        canv.SetLogx()
        ## legend = ROOT.TLegend(0.5,0.6,0.8,0.75)
        ## legend = ROOT.TLegend(0.6,0.6,0.9,0.75)
        legend = ROOT.TLegend(0.56,0.6,0.86,0.75)
        legend.SetFillStyle(0)
        kappa = "0."+coup[1:]
        observed.Draw("apl")
        ## observed.Draw("al")
        ## observed.GetYaxis().SetRangeUser(1e-5,0.55)
        observed.GetYaxis().SetRangeUser(1e-3,0.55)
        ## observed.GetXaxis().SetRangeUser(450,3000)
        ## observed.GetXaxis().SetRangeUser(450,5000)
        observed.GetXaxis().SetRangeUser(xmin,xmax)
        observed.GetXaxis().SetMoreLogLabels()
        
        ## xmin,xmax=observed.GetXaxis().GetXmin(),observed.GetXaxis().GetXmax()
        ## xmin,xmax=450,3000
        # xmin,xmax=450,5000
        spots = filter(lambda x: x>observed.GetYaxis().GetXmin(),  map(lambda x: (x,ROOT.RooStats.SignificanceToPValue(x)), xrange(1,5) ) )
        
        lines = map( lambda y: ROOT.TLine(xmin,y[1],xmax,y[1]), spots )
        map( lambda x: style_utils.apply(x,[["SetLineColor",ROOT.kGray+3],["SetLineStyle",7]]), lines )

        labels = map( lambda y: ROOT.TLatex(xmax*1.01,y[1]*0.9,"#color[%d]{%d #sigma}" % (ROOT.kGray+2,y[0])), spots )
        map( lambda x: style_utils.apply(x,[["SetTextSize",0.05]]), labels )

        map( lambda x: x.Draw("same"), lines+labels )
        self.keep(lines+labels)
        
        legend.AddEntry(None,"#tilde{#kappa} = %s" % kappa,"")
        legend.AddEntry(observed,"Observed p_{0}","l")
        
        self.keep(legend,True)
        legend.Draw()
        
        self.graphs.extend([observed])
        self.keep( [canv,observed] )
        self.format(canv,options.postproc)

    def scaleByXsec(self,graph,coup):
        if self.options.fixed_x_section:
            scale = self.options.fixed_x_section
            rescaleFunc = None
            if self.options.fixed_x_section_ratio:
                rescaleFunc = ROOT.TF1("rescale",self.options.fixed_x_section_ratio)
                print rescaleFunc
            if self.options.use_fb: scale *= 1e+3
        xvals = graph.GetX()
        yvals = graph.GetY()
        yerrl = graph.GetEYlow()
        yerrh = graph.GetEYhigh()
        if not self.options.fixed_x_section:
            if not coup in self.xsections_:
                print("Cross section for k = %s not found" % coup)
                sys.exit(-1)
            else:
                xsec = self.xsections_[coup]
        for ip in range(graph.GetN()):
            iscale = scale
            if not self.options.fixed_x_section:
                iscale = xsec.Eval(xvals[ip])
            elif rescaleFunc: 
                print xvals[ip],iscale,
                iscale *= rescaleFunc.Eval(xvals[ip])
                print iscale
            graph.SetPoint( ip, xvals[ip], yvals[ip]*iscale )
            graph.SetPointEYlow( ip, yerrl[ip]*iscale )
            graph.SetPointEYhigh( ip, yerrh[ip]*iscale )
        
    def loadXsections(self,inmap):
        self.xsections_ = {}
        scl = 1e+3 if self.options.use_fb else 1.
        for name,val in inmap.iteritems():
            if name.startswith("RSGravToGG") or name.startswith("RSGravitonToGG"):
                coup,mass = name.split("kMpl")[1].split("_Tune")[0].replace("_","").replace("-","").split("M")
                mass = float(mass)
                if not coup in self.xsections_:
                    self.xsections_[coup] = ROOT.TGraph()
                self.xsections_[coup].SetPoint(self.xsections_[coup].GetN(),mass,val["xs"]*scl)
        for name,val in self.xsections_.iteritems():
            val.Sort()

    def plotXsections(self):
        coups = sorted( map( lambda x: (float("0."+x[0][1:]),x[1]), self.xsections_.iteritems() ), key=lambda x: x[0] )
        ## minc = min( map( lambda x: x[0], coups) )
        refc = coups[-4]
        print refc, coups
        scaled = map( lambda x: (x[0],scaleGraph(x[1], lambda y: refc[0]*refc[0]/((x[0]*x[0])*refc[1].Eval(y)))), coups )
        
        mypol = ROOT.TF1("mypol","[0]+[1]*(x-[2])**2")
        fit = map( lambda x: (x[0],x[1],fitFunc(x[1],mypol)),  scaled )
        
        rescaled = map( lambda x: (x[0],scaleGraph(x[1], lambda y: 1./(x[2].Eval(y)) )), fit )

        canv = ROOT.TCanvas("xsections","xsections")
        scaled[0][1].Draw("apl")
        # scaled[0].GetYaxis().SetRange(0,5)
        for g in scaled[1:]: g[1].Draw("pl")
        print scaled
        self.keep( list(scaled) )
        self.keep(canv)

        recanv = ROOT.TCanvas("xsections_rescaled","xsections_rescaled")
        rescaled[0][1].Draw("apl")
        # scaled[0].GetYaxis().SetRange(0,5)
        for g in rescaled[1:]: g[1].Draw("pl")
        print rescaled
        self.keep( list(rescaled) )
        self.keep(recanv)

        params = map( lambda x: (x[0], x[2].GetParameter(0), x[2].GetParameter(1), x[2].GetParameter(2)), fit  )
        
        param_graphs = ROOT.TGraph(), ROOT.TGraph(), ROOT.TGraph()
        map( lambda x: (param_graphs[0].SetPoint(param_graphs[0].GetN(),x[0],x[1]),param_graphs[1].SetPoint(param_graphs[1].GetN(),x[0],x[2]),param_graphs[2].SetPoint(param_graphs[2].GetN(),x[0],x[3])), params )
        for ip, gr in enumerate(param_graphs):
            gr.Sort()
            pcanv = ROOT.TCanvas("p%d"%ip,"p%d"%ip)
            gr.Draw()
            self.keep( [gr,pcanv] )

        p0 = ROOT.TF1("p0","pol2")
        p0.SetParameters(1.09141,-0.0977154,-0.670345)

        p1 = ROOT.TF1("p1","pol2")
        p1.SetParameters(-3.44266e-08,5.194e-08,2.02169e-07)

        p2 = ROOT.TF1("p2","pol2")
        p2.SetParameters(2718.59,69.1401,-772.539)
        
        ## refc[0] = 3
        equalized = map( lambda x: (x[0],scaleGraph(x[1], lambda y: refc[0]*refc[0]/((x[0]*x[0])*(p0.Eval(x[0]) + p1.Eval(x[0])*(y-p2.Eval(x[0]))**2)) )), coups )        

        eqcanv = ROOT.TCanvas("xsections_equalized","xsections_equalized")
        ## equalized[0][1].Draw("apl")
        ## # scaled[0].GetYaxis().SetRange(0,5)
        ## for g in equalized[1:]: g[1].Draw("pl")
        ## self.keep( list(equalized) )
        ## self.keep(eqcanv)

        sumg = {}
        for gr in equalized:
            gr = gr[1]
            xvals = gr.GetX()
            yvals = gr.GetY()
            for ip in xrange(gr.GetN()):
                x,y = xvals[ip],yvals[ip]
                if not x in sumg: sumg[x] = [0.,0]
                sumg[x][0] += y
                sumg[x][1] += 1
        averaged = ROOT.TGraph()
        for x,y in sumg.iteritems():
            averaged.SetPoint(averaged.GetN(),x,y[0]/y[1])
        averaged.Sort()
        averaged.Draw("apl")
        self.keep(averaged)
        self.keep(eqcanv)
        
        xsec = {
            "ref" : refc[0],
            "p0"  : [ p0.GetParameter(0), p0.GetParameter(1), p0.GetParameter(2) ],
            "p1"  : [ p1.GetParameter(0), p1.GetParameter(1), p1.GetParameter(2) ],
            "p2"  : [ p2.GetParameter(0), p2.GetParameter(1), p2.GetParameter(2) ],
            "xsec" : [ (averaged.GetX()[i],averaged.GetY()[i]) for i in xrange(averaged.GetN()) ]
            }
        
        with open("xsecions.json","w+") as xsec_file:
            xsec_file.write(json.dumps(xsec))
            xsec_file.close()
        
        
        
# -----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app = LimitPlot()
    app.run()
