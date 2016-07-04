#!/bin/env python

from diphotons.Utils.pyrapp import *
from optparse import OptionParser, make_option
from copy import deepcopy as copy
import os, json
from pprint import pprint
import array
from getpass import getuser
from templates_maker import TemplatesApp

from getpass import getuser
import random

from math import sqrt

# ----------------------------------------------------------------------------------------------------
def computeShapeWithUnc(histo,extraerr=None):
    histo.Scale(1./histo.Integral())
    if not extraerr:
        return
    for xb in range(histo.GetNbinsX()+1):
        for yb in range(histo.GetNbinsX()+1):
            ib = histo.GetBin(xb,yb)            
            err = histo.GetBinError(ib)
            bbyb = extraerr*histo.GetBinContent(ib)
            err = sqrt( err*err + bbyb*bbyb )
            histo.SetBinError(ib,err)

    return
    denom = histo.Clone("temp")
    denom.Reset("ICE")
    error = ROOT.Double(0.)
    entries = histo.GetEntries()
    try:
        integral = histo.IntegralAndError(-1,-1,error) 
    except:
        integral = histo.IntegralAndError(-1,-1,-1,-1,error) 
    for xb in range(denom.GetNbinsX()+1):
        for yb in range(denom.GetNbinsX()+1):
            ib = histo.GetBin(xb,yb)            
            denom.SetBinContent(ib,integral)
            denom.SetBinError(ib,error)
    histo.Divide(histo,denom,1.,1.,"B")
    del denom
    


## ----------------------------------------------------------------------------------------------------------------------------------------
## TemplatesApp class
## ----------------------------------------------------------------------------------------------------------------------------------------

## ----------------------------------------------------------------------------------------------------------------------------------------
class TemplatesFitApp(TemplatesApp):
    """
    Class to handle template fitting.
    Takes care of preparing templates starting from TTrees.
    Inherith from PyRapp and PlotApp classes and Template Maker App class.
    """
    
    ## ------------------------------------------------------------------------------------------------------------
    def __init__(self,option_list=[],option_groups=[]):
        super(TemplatesFitApp,self).__init__(option_groups=[
                ("General templates preparation options", [
                        make_option("--compare-templates",dest="compare_templates",action="store_true",default=False,
                                    help="Make templates comparison plots",
                                    ),
                        make_option("--input-envelope",dest="input_envelope",action="store_true",default=False,
                                    help="roodataset for envelope",
                                    ),
                        make_option("--nominal-fit",dest="nominal_fit",action="store_true",default=False,
                                    help="do fit templates",
                                    ),
                        make_option("--fit-mc",dest="fit_mc",action="store_true",default=False,
                                    help="do fit with mc ",
                                    ),
                        make_option("--build-3dtemplates",dest="build_3dtemplates",action="store_true",
                                    default=False,
                                     help="build 3d templates with unrolled variable and mass",
                                    ), 
                        make_option("--corr-singlePho",dest="corr_singlePho",action="store_true",
                                    default=False,
                                     help="correlation sieie and chiso single fake photon",
                                    ),
                        make_option("--jackknife",dest="jack_knife",action="store_true",default=False,
                                    help="Plot RMS etc from jk pseudosamples",
                                    ),
                        make_option("--purity-sigregion",dest="pu_sigregion",action="store_true",default=False,
                        
                                    help="get also purity values for sig region, can be done on top of fit over full range",
                                    ),
                        make_option("--fixed-massbins",dest="fixed_massbins",action="store_true",default=False,
                                    help="if you want to fix the massbins otherwise --fit-massbins",
                                    ),
                        make_option("--no-mctruth",dest="no_mctruth",action="store_true",default=False,
                                    help="if you only run on data",
                                    ),
                        make_option("--blind",dest="blind",action="store_true",default=False,
                                    help="blind",
                                    ),
                        make_option("--full-error",dest="full_error",action="store_true",default=False,
                                    help="if purity plotted with sys+stat error",
                                    ),
                        
                        
                        make_option("--extra-shape-unc",dest="extra_shape_unc",action="store",type="float",
                                    default=None,
                                    help="Add extra uncertainty to template shapes (implemented only for plotting)",
                                    ),
                        ]
                      )
            ]+option_groups,option_list=option_list)
        

        ## load ROOT (and libraries)
        global ROOT, style_utils, RooFit
        import ROOT
        from ROOT import RooFit
        import diphotons.Utils.pyrapp.style_utils as style_utils
        ROOT.gSystem.Load("libdiphotonsUtils")
        if ROOT.gROOT.GetVersionInt() >= 60000:
            ROOT.gSystem.Load("libdiphotonsRooUtils")

        ROOT.gStyle.SetOptStat(111111)

    ## ------------------------------------------------------------------------------------------------------------
    def __call__(self,options,args):
        """ 
        Main method. Called automatically by PyRoot class.
        """
        ## load ROOT style
        self.loadRootStyle()
        from ROOT import RooFit
        from ROOT import TH1D, TCanvas, TAxis
        ROOT.gStyle.SetOptStat(111111)
        printLevel = ROOT.RooMsgService.instance().globalKillBelow()
        ROOT.RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)
        ROOT.TH1D.SetDefaultSumw2(True)
        
        self.setup(options,args)
        
        if options.compare_templates:
            self.compareTemplates(options,args)
        if options.input_envelope:
            self.inputEnvelope(options,args)
            
        if options.nominal_fit:
            self.nominalFit(options,args)
        if options.plot_purity:
            self.plotPurity(options,args)
        if options.corr_singlePho:
            self.corrSinglePho(options,args)
        if options.build_3dtemplates:
            self.build3dTemplates(options,args)
        if options.jack_knife:
            self.Jackknife(options,args)
        

    ## ------------------------------------------------------------------------------------------------------------
    def inputEnvelope(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        weight_cut=options.inputEnvelope["weight_cut"] 
        fitname=options.inputEnvelope["fit"]
        components=options.inputEnvelope.get("components")
        print fitname, components
        for comp in components:
            if type(comp) == str or type(comp)==unicode:
                compname = comp
                templatesls= comparison["templates"]
            else:
                compname, templatesls = comp
            for cat in options.inputEnvelope.get("categories"):
                print cat, compname
                templates = []
                massargs=ROOT.RooArgSet("massargs")
                mass_var,mass_b=self.getVar(options.inputEnvelope.get("mass_binning"))
                mass=self.buildRooVar(mass_var,mass_b,recycle=True)
                massargs.add(mass)
                setargs=ROOT.RooArgSet(massargs)
                rooweight=self.buildRooVar("weight",[],recycle=True)
                setargs.add(rooweight)
                setargs.Print()
                truthname= "mctruth_%s_%s_%s" % (compname,fitname,cat)
                print truthname
                print
                truth = self.reducedRooData(truthname,setargs,False,sel=weight_cut,redo=False)
                truth.Print()
        self.saveWs(options,fout)
    
    ## ------------------------------------------------------------------------------------------------------------
    def compareTemplates(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        self.doCompareTemplates(options,args)
        self.saveWs(options,fout)
    
    ## ------------------------------------------------------------------------------------------------------------
    #MQ compare truth templates with rcone and sideband templates
    def doCompareTemplates(self,options,args):
        print "Compare truth templates with rcone and sideband templates"
        ROOT.TH1F.SetDefaultSumw2(True)
        for name, comparison in options.comparisons.iteritems():
            if name.startswith("_"): continue
            print "Comparison %s" % name
            prepfit=comparison["prepfit"] 
            ReDo=comparison.get("redo",True)
            weight_cut=comparison["weight_cut"] 
            fitname=comparison["fit"]
            if fitname=="2D" : d2=True
            else: d2=False
            fit=options.fits[fitname]
            components=comparison.get("components",fit["components"])
            print components
            for comp in components:
                if type(comp) == str or type(comp)==unicode:
                    compname = comp
                    templatesls= comparison["templates"]
                else:
                    compname, templatesls = comp
                for cat in comparison.get("categories",fit["categories"]):
                    print
                    print cat, compname
                    isoargs=ROOT.RooArgSet("isoargs")
                    massargs=ROOT.RooArgSet("massargs")
                    mass_var,mass_b=self.getVar(comparison.get("mass_binning"))
                    mass=self.buildRooVar(mass_var,mass_b,recycle=True)
                    massargs.add(mass)
                    if len(options.template_binning) > 0:
                        template_binning = array.array('d',options.template_binning)
                    else:
                        template_binning = array.array('d',comparison.get("template_binning"))
                    templatebins=ROOT.RooBinning(len(template_binning)-1,template_binning,"templatebins" )
### list to store templates for each category
                    templates = []
                    for idim in range(fit["ndim"]):
                        isoargs.add(self.buildRooVar("templateNdim%dDim%d" % ( fit["ndim"],idim),template_binning,recycle=True))
                    if d2:
                        setargs=ROOT.RooArgSet(massargs,isoargs)
                        sigRegionlow2D=float(comparison.get("lowerLimitSigRegion2D"))
                        sigRegionup2D=float(comparison.get("upperLimitSigRegion2D"))
                        sigRegionup1D=float(comparison.get("upperLimitSigRegion1D"))
                    else: setargs=ROOT.RooArgSet(isoargs)
                   # setargs.add(self.buildRooVar("weight",[],recycle=True))
                    rooweight=self.buildRooVar("weight",[],recycle=True)
                    setargs.add(rooweight)
                    setargs.Print()
                    #needed to estimate true purity for alter 2dfit
                    if not options.no_mctruth:
                        truthname= "mctruth_%s_%s_%s" % (compname,fitname,cat)
                        print truthname
                        print
                        truth = self.reducedRooData(truthname,setargs,False,sel=weight_cut,redo=ReDo)
                        truth.Print()
                        templates.append(truth)
### loop over templates
                    tempdatals=self.buildTemplates(templatesls,setargs,weight_cut,compname,cat) 
                    for temp in tempdatals:
                        templates.append(temp)
###------------------- split in massbins
                    masserror = array.array('d',[])
                     
                    if cat=="EEEB": catd="EBEE"#TODO implement in json file
                    else: catd=cat
                    setargs.add(massargs)
                    setargs.Print()
                    dset_data = self.reducedRooData("data_%s_%s" % (fitname,catd),setargs,False,sel=weight_cut,redo=ReDo)
                    if not options.no_mctruth:
                        dset_mc = self.reducedRooData("mc_%s_%s" % (fitname,catd),setargs,False,sel=weight_cut,redo=ReDo)
                    if not options.fixed_massbins:
                        mass_split= [int(x) for x in options.fit_massbins]
                        print mass_split
                        diphomass=self.massquantiles(dset_data,massargs,mass_b,mass_split)
                        if cat=="EBEB":
                            diphomass=[230.0,12999.]
                        if cat=="EBEE":
                            diphomass=[320.0,12999.]
                        massrange=[mass_split[2],mass_split[1]]
                    elif options.fixed_massbins and cat=="EBEB":
                        if not options.blind: diphomass = array.array('d',comparison.get("diphomassEBEB_binning"))
                        else:diphomass = array.array('d',comparison.get("diphomassEBEBblind_binning"))
                        massrange=[0,len(diphomass)-1]
                    elif options.fixed_massbins and cat=="EBEE":
                        if not options.blind: diphomass = array.array('d',comparison.get("diphomassEBEE_binning"))
                        else:diphomass = array.array('d',comparison.get("diphomassEBEEblind_binning"))
                        massrange=[0,len(diphomass)-1]
                    if not options.no_mctruth:
                        truth_pp= "mctruth_%s_%s_%s" % (compname,fitname,cat)
                        if d2:
                            tp_mcpu = ROOT.TNtuple("tree_truth_fraction_all_%s_%s_%s" % (compname,fitname,cat),"tree_truth_fraction_%s_%s_%s" % (compname,fitname,cat),"number_pu:frac_pu:massbin:masserror" )
                            ntp_mcpu = ROOT.TNtuple("tree_truth_fraction_signalregion_%s_%s_%s" % (compname,fitname,cat),"tree_truth_fraction_signalrange_%s_%s_%s" % (compname,fitname,cat),"number_pu:frac_pu:massbin:masserror" )
                    else:
                        if d2:
                            tp_mcpu = ROOT.TNtuple("tree_truth_fraction_all_%s_%s_%s" % (compname,fitname,cat),"tree_truth_fraction_%s_%s_%s" % (compname,fitname,cat),"number_pu:frac_pu:massbin:masserror" )
                            ntp_mcpu = ROOT.TNtuple("tree_truth_fraction_signalregion_%s_%s_%s" % (compname,fitname,cat),"tree_truth_fraction_signalrange_%s_%s_%s" % (compname,fitname,cat),"number_pu:frac_pu:massbin:masserror" )

                    self.store_[tp_mcpu.GetName()] =tp_mcpu
                    self.store_[ntp_mcpu.GetName()] =ntp_mcpu

                 
                    for mb in range(massrange[0],massrange[1]):
                        massbin=(diphomass[mb]+diphomass[mb+1])/2.
                        masserror=(diphomass[mb+1]-diphomass[mb])/2.
                        cut=ROOT.TCut("mass>%f && mass<%f"% (diphomass[mb],diphomass[mb+1]))
                        cut_s= "%1.0f_%2.0f"% (diphomass[mb],diphomass[mb+1])
                        print cut.GetTitle()
                        if d2:
                            cut_sigregion=ROOT.TCut("templateNdim2Dim0< %f && templateNdim2Dim1< %f" %(sigRegionup1D,sigRegionup1D))
                            dset_massc=self.masscutTemplates(dset_data,cut,cut_s)
                            if not options.no_mctruth:
                                dset_massc_mc=self.masscutTemplates(dset_mc,cut,cut_s)
                                temp_massc_truth=self.masscutTemplates(templates[0],cut,cut_s,"temp_truthinformation")
                                number_pu=temp_massc_truth.sumEntries()
                                if dset_massc_mc.sumEntries() !=0:
                                    frac_pu=number_pu/dset_massc_mc.sumEntries()
                                else: frac_pu=0.
                                tempSig_massc_truth=temp_massc_truth.Clone("tempSig_truthinformation")
                            templates_massc=[]
                            for temp_m in templates:
                                temp_massc=self.masscutTemplates(temp_m,cut,cut_s)
                                if temp_massc.sumEntries() ==0:
                                    print "!!!!!!!!!!!! attention dataset ", temp_massc, " has no entries !!!!!!!!!!!!!!!!!"
                                ##
                                else:templates_massc.append(temp_massc)
###---------------get truth information per massbin and in signal range
                            if not options.no_mctruth:
                                data_massc_truth = dset_massc_mc.Clone("data_truthinformation")
                                data_massc_truth=data_massc_truth.reduce(cut_sigregion.GetTitle())
                                tempSig_massc_truth=tempSig_massc_truth.reduce(cut_sigregion.GetTitle())
                                number_pu_sigrange=tempSig_massc_truth.sumEntries()
                                if data_massc_truth.sumEntries() !=0:
                                    frac_pu_sigrange=number_pu_sigrange/data_massc_truth.sumEntries()
                                else: frac_pu_sigrange=0.
                                tp_mcpu.Fill(number_pu,frac_pu,massbin, masserror)
                                ntp_mcpu.Fill(number_pu_sigrange,frac_pu_sigrange,massbin, masserror)
                            else:
                                tp_mcpu.Fill(0,0,massbin, masserror)
                                ntp_mcpu.Fill(0,0,massbin, masserror)
                        elif not d2:
                            templates_massc=templates[:]
###----------------------- loop over 2 legs
                        for id in range(fit["ndim"]):
                            histls=[]
                            isoarg1d=ROOT.RooArgList("isoarg")
                            isoarg1d.add(self.buildRooVar("templateNdim%dDim%d" % ( fit["ndim"],id),template_binning,recycle=True))                
                            tit = "compiso_%s_%s_%s_mb_%s_templateNdim%dDim%d" % (fitname,compname,cat,cut_s,fit["ndim"],id)
                            numEntries_s=""
                            for tm in templates_massc:
                                tempHisto=ROOT.TH1F("%s_dim%d_%d" % (tm.GetName(),fit["ndim"],id),
                                                    "%s_dim%d_%d" % (tm.GetName(),fit["ndim"],id),len(template_binning)-1,template_binning)
                                tm.fillHistogram(tempHisto,isoarg1d)
                                numEntries_s+= (" %f " % tempHisto.Integral())
                                if "truth" in tempHisto.GetName():
                                    computeShapeWithUnc(tempHisto)
                                else:
                                    computeShapeWithUnc(tempHisto,options.extra_shape_unc)
                                for bin in range(1,len(template_binning) ):
                                    tempHisto.SetBinContent(bin,tempHisto.GetBinContent(bin)/(tempHisto.GetBinWidth(bin)))
                                    tempHisto.SetBinError(bin,tempHisto.GetBinError(bin)/(tempHisto.GetBinWidth(bin)))
                                histls.append(tempHisto)
                      #     if not prepfit: 
                            print "plot 1d histos"
                            self.plotHistos(histls,tit,template_binning,False,logx=False,logy=True,numEntries=numEntries_s,ID=id)
                        

                        ## roll out for combine tool per category
                        if fit["ndim"]>1:
                            self.histounroll(templates_massc,template_binning,isoargs,compname,cat,cut_s,prepfit,sigRegionlow2D,sigRegionup2D,extra_shape_unc=options.extra_shape_unc)
                            self.histounroll_book(template_binning,isoargs)

    ## ------------------------------------------------------------------------------------------------------------
    def buildTemplates(self,templatesls,setargs, weight_cut=None,compname="pf",cat="EBEB"):
        templs=[]
        for template,mapping in templatesls.iteritems():
            print template, mapping
            if "mix" in template:
                mixname = template.split(":")[-1]
                print "template_mix_%s_%s_%s" % (compname,mixname,mapping.get(cat,cat))
                templatename= "template_mix_%s_%s_%s" % (compname,mixname,mapping.get(cat,cat))
            elif "template_mc" in template:
                tempname = template.split(":")[-1]
                print "template_mc_%s_%s_%s" % (compname,tempname,mapping.get(cat,cat))
                templatename= "template_mc_%s_%s_%s" % (compname,tempname,mapping.get(cat,cat))
            else:
                print "template_%s_%s_%s" % (compname,template,mapping.get(cat,cat))
                templatename= "template_%s_%s_%s" % (compname,template,mapping.get(cat,cat))
            tempdata = self.reducedRooData(templatename,setargs,False,sel=weight_cut,redo=True)

            if "mix" in template:
                mixname=mixname[11:]
                templatename=( "reduced_template_mix_%s_%s_%s" % (compname,mixname,mapping.get(cat,cat)))
                print templatename
                tempdata.SetName(templatename)
            tempdata.Print()
            if tempdata.sumEntries() ==0:
                print "!!!!!!!!!!!! attention dataset ", templatename, " has no entries !!!!!!!!!!!!!!!!!"
            else:
                templs.append(tempdata)
        return templs
    ## ------------------------------------------------------------------------------------------------------------
    def masscutTemplates(self,dset,cut,cut_s,name=None):
        if name==None:
            name=dset.GetName()[8:]
        dset_massc = dset.Clone("%s_mb_%s"%(name,cut_s))
        dset_massc=dset_massc.reduce(cut.GetTitle())
        dset_massc.Print()
        return dset_massc
    ## ------------------------------------------------------------------------------------------------------------


    def histounroll(self,templatelist,template_binning,isoargs,comp,cat,mcut_s,prepfit,sigRegionlow,sigRegionup,extra_shape_unc=None,plot=True):
        pad_it=0
        c1=ROOT.TCanvas("d2hist_%s" % cat,"2d hists per category",1400,1000) 
        c1.Divide(1,2)
        histlistunroll=[]
        print
        print "roll out" 
        tempunroll_binning = array.array('d',[])
        histlsY=[]
        histlsX=[]
    #    print"len(template_binning)", len(template_binning)
   #     print"template_binning", template_binning
        for tempur in templatelist:
            pad_it+=1
            temp2d=ROOT.TH2F("d2%s" % (tempur.GetName()),"d2%s" % (tempur.GetName()),len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
            tempur.fillHistogram(temp2d,ROOT.RooArgList(isoargs))
            print "integral 2d  histo", temp2d.Integral()
            temp2dx=temp2d.ProjectionX("%s_X" %tempur.GetName())
            if plot:
                if "truth" in temp2dx.GetName():
                    computeShapeWithUnc(temp2dx)
                else:
                    computeShapeWithUnc(temp2dx,extra_shape_unc)
                temp2dx.SetTitle("%s_X" %tempur.GetName())
                temp2dy=temp2d.ProjectionY("%s_Y" %tempur.GetName())
                if "truth" in temp2dy.GetName():
                    computeShapeWithUnc(temp2dy)
                else:
                    computeShapeWithUnc(temp2dy,extra_shape_unc)
                ## draw projections as a check
                histlsX.append(temp2dx)
                temp2dy.SetTitle("%s_Y" %tempur.GetName())
                histlsY.append(temp2dy)
            if  plot:
                if "truth" in temp2d.GetName():
                    computeShapeWithUnc(temp2d)
                else:
                    computeShapeWithUnc(temp2d,extra_shape_unc)
            tempunroll_binning = array.array('d',[])
            tempunroll_binning.append(0.0)
            sum=0.
            bin=0
            binslist=[]
            #binslist=array.array('i',(0,0))
            for b in range(1,len(template_binning)):
                for x in range(1,b+1):
                    bin+=1
                    binslist.append((x,b))
                for y in range (b-1,0,-1):
                    bin+=1
                    binslist.append((b,y))
            for bin1, bin2 in binslist:
                binErr=0.
                area=0.
                binCont=0.
                binCont= temp2d.GetBinContent(bin1,bin2)
                binErr=temp2d.GetBinError(bin1,bin2)
                area=(temp2d.GetXaxis().GetBinWidth(bin1))*(temp2d.GetYaxis().GetBinWidth(bin2))
                if not prepfit:
                    sum+=1
                    temp2d.SetBinContent(bin1,bin2,binCont/area)
                    temp2d.SetBinError(bin1,bin2,binErr/area)
                else:
                   # sum+=area
                    sum+=1
                    temp2d.SetBinContent(bin1,bin2,binCont)
                    temp2d.SetBinError(bin1,bin2,binErr)
                tempunroll_binning.append(sum)
            if prepfit:
                templateNdim2d_unroll=self.buildRooVar("templateNdim2d_unroll",tempunroll_binning,importToWs=True)
                templateNdim2d_unroll.setRange("sigRegion",sigRegionup,sigRegionlow)
                rootemplate_binning=ROOT.RooBinning(len(template_binning),template_binning,"rootemplate_binning")
                unrollvar=ROOT.RooArgList(templateNdim2d_unroll) 
              #  templateNdim2d_unroll.setBinning(rootemplate_binning)
            if plot and "template_pp" in tempur.GetTitle():
                c1.cd(pad_it)
                ROOT.gPad.SetLogz()
                temp2d.Draw("COLZ")
                temp2d.GetZaxis().SetRangeUser(1e-8,1)
            bin=0
            temp1dunroll=ROOT.TH1F("hist_%s" % (tempur.GetName()),"hist_%s"% (tempur.GetName()),len(tempunroll_binning)-1,tempunroll_binning)
            for bin1, bin2 in binslist:
                #  to loop up to inclu sively b
                bin+=1
                binC= temp2d.GetBinContent(bin1,bin2)
                binE= temp2d.GetBinError(bin1,bin2)
                temp1dunroll.SetBinContent(bin,binC)
                temp1dunroll.SetBinError(bin,binE)
            histlistunroll.append(temp1dunroll)
            fail=0
            if prepfit:
                for b in range(1,temp1dunroll.GetNbinsX()+1):
                    if temp1dunroll.GetBinContent(b) ==0:
                            temp1dunroll.SetBinContent(b,0.)
                            print "ui, the bin content is zero"
                            fail=fail+1
                roodatahist_1dunroll=ROOT.RooDataHist("unrolled_%s" % (tempur.GetName()),"unrolled_%s_zerobins%u" %(tempur.GetName(),fail),unrollvar, temp1dunroll)
                print "unrolled roodata hist:"
                roodatahist_1dunroll.Print()
                self.workspace_.rooImport(roodatahist_1dunroll,ROOT.RooFit.RecycleConflictNodes())
        print "histlistunroll ", histlistunroll
        if plot:
            title="histo_%s_%s_%s" %(comp,cat,mcut_s)
       #     self.plotHistos(histlsX,"%s_X" %title,template_binning,False,logx=True,logy=True)
        #    self.plotHistos(histlsY,"%s_Y" %title,template_binning,False,logx=True,logy=True)
            self.plotHistos(histlistunroll,"%s_unrolled" % (title),tempunroll_binning,False,False,True)
            self.keep( [c1] )
            self.format(c1,self.options.postproc)
            self.autosave(True)
        else: return histlistunroll 


    ## ------------------------------------------------------------------------------------------------------------
    def histounroll_book(self,template_binning,args,importToWs=True,buildHistFunc=False):
        print args
        template_binning = array.array('d',template_binning)
        th2d=ROOT.TH2F("th2d","th2d",len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
        bin=0
        binslist=[]
        isoargs=ROOT.RooArgList(args)
        #booking binslist
        for b in range(1,len(template_binning)):
            for x in range(1,b+1):
                bin+=1
                binslist.append((x,b))                
            for y in range (b-1,0,-1):
                bin+=1
                binslist.append((b,y))
        unroll_widths=array.array('d',[])
        for bin1,bin2 in binslist:
            area = th2d.GetXaxis().GetBinWidth(bin1)*th2d.GetYaxis().GetBinWidth(bin2)
            unroll_widths.append(area)
        for ibin,bins in enumerate(binslist):
            bin1,bin2=bins
            th2d.SetBinContent(bin1,bin2,
                               ## (unroll_binning[ibin]+unroll_binning[ibin+1])*0.5)
                               ibin+0.5)
        hist2d_forUnrolled=ROOT.RooDataHist("hist2d_forUnrolled","hist2d_forUnrolled",ROOT.RooArgList(isoargs), th2d)
        self.keep(hist2d_forUnrolled)
        #ct=ROOT.TCanvas("ct","ct",1000,1000) 
        #ct.cd()
        #ROOT.gStyle.SetPaintTextFormat("1.1f")
        #th2d.SetMarkerSize(3.)
        #th2d.GetXaxis().SetTitle("templateNdim2Dim0")
        #th2d.GetYaxis().SetTitle("templateNdim2Dim1")
        #th2d.Draw("TEXT")
        #self.keep( [th2d,ct] )
        #self.autosave(True)
        ret=hist2d_forUnrolled
        if buildHistFunc:
            ret=ROOT.RooHistFunc(buildHistFunc,buildHistFunc,args,hist2d_forUnrolled)
            self.keep(ret)
            
        if importToWs:
            self.workspace_.rooImport(ret,ROOT.RooFit.RecycleConflictNodes())
            
        return ret,unroll_widths

    ## ------------------------------------------------------------------------------------------------------------
    def massquantiles(self,dataset,massargs,mass_binning,mass_split):
        #print "splitByBin for dataset", dataset.GetName()
        #massH=ROOT.TH1F("%s_massH" % dataset.GetName()[-17:],"%s_massH" % dataset.GetName()[-17:],len(mass_binning)-1,mass_binning)
        massargs.Print()

        massH=ROOT.TH1F("%s_massH" % dataset.GetName(),"%s_massH" % dataset.GetName(),len(mass_binning)-1,mass_binning)
        print massH,len(mass_binning)-1
        dataset.fillHistogram(massH,ROOT.RooArgList(massargs)) 
       # print "define mass bins 0 
        massH.Scale(1.0/massH.Integral())
        prob = array.array('d',[])
        dpmq = array.array('d',[0.0 for i in range((mass_split[1]+1))])
        for i in range(0,mass_split[1]+1):
            prob.append((i+float(mass_split[2]))/mass_split[0])
            print dpmq
        massH.GetQuantiles(mass_split[1]+1,dpmq,prob)
        #show the original histogram in the top pad
        massHC=ROOT.TH1F("%s_massHC" % dataset.GetName(),"%s_massHC" % dataset.GetName(),len(dpmq)-1,dpmq)
        dataset.fillHistogram(massHC,ROOT.RooArgList(massargs)) 
        cq=ROOT.TCanvas("cq_%s" %dataset.GetName()[-20:],"mass quantiles",10,10,700,900)
        cq.Divide(1,2)
        cq.cd(1)
        ROOT.gPad.SetLogx()
        massHC.Draw()
        #show the quantiles in the bottom pad
        cq.cd(2)
        gr =ROOT.TGraph(mass_split[1]+1,prob,dpmq)
        ROOT.gPad.SetLogy()
        gr.SetMarkerStyle(21)
        gr.GetXaxis().SetTitle("quantiles")
        gr.GetYaxis().SetTitle("diphoton mass [GeV]")
        gr.Draw("alp")
        self.keep( [cq] )
        self.autosave(True)
        #
        for  k in range(0,len(dpmq)):
            print "prob " ,prob[k] ," diphomass " , dpmq[k]  
        return dpmq
 
    ## ------------------------------------------------------------------------------------------------------------
    #MQ compare truth templates with rcone and sideband templates
    def corrSinglePho(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        ROOT.TH1F.SetDefaultSumw2(True)
        setargs=ROOT.RooArgSet("setargs")
        iso,isob=self.getVar("templateNdim1Dim0")
        isovar=self.buildRooVar(iso,isob,recycle=True)
        setargs.add(isovar)
        sigma_var,sigma_b=self.getVar("phoSigmaIeIe")
        template_binning=array.array('d',[])
        for i in range(0,16):
            i=i*1.
            template_binning.append(i)
        sieievar=self.buildRooVar(sigma_var,sigma_b,recycle=True)
        setargs.add(sieievar)
        rooweight=self.buildRooVar("weight",[],recycle=True)
        setargs.add(rooweight)
        setargs.Print()
        prob = array.array('d',[])
        #n=10
        #sieieb = array.array('d',[0.0 for i in range(n+1)])
       # for i in range(0,n+1):
        #    prob.append(i/float(n))
        for cat in options.corrPlot.get("categories"):
            if cat=="EB":
                sieielow=0.007
                sieieup=0.014
                sieieb = array.array('d',[sieielow,0.0105,0.0112,0.012,sieieup])
                ymax=12e3
            elif cat =="EE":
                sieielow=0.02
                sieieup=0.04
                sieieb = array.array('d',[sieielow,0.028,0.030,0.035,sieieup])
                ymax=4.5e3
            sieievar.setRange(sieielow,sieieup)
            truth = self.reducedRooData("mctruth_f_singlePho_%s"% cat,setargs,False,weight="weight < 1000.",redo=True)
            truth.Print()
            tempdata = self.reducedRooData("template_f_singlePho_%s" %cat,setargs,False,weight="weight < 1000.",redo=True)
            tempdata.Print()
            tempdata.append(truth)
            tempCombined=tempdata
            tempCombined.SetName("template_allsieie_f_singlePho_%s" %cat)
            tempCombined.Print()
            histo_sieie=ROOT.TH1F("histo_sieie_%s" %cat,"histo_sieie_%s"%cat,40,sieielow,sieieup)
            tempCombined.fillHistogram(histo_sieie,ROOT.RooArgList(sieievar)) 
            histo_sieie2=histo_sieie.Clone()
            histo_sieie.Scale(1.0/histo_sieie.Integral())
        #    histo_sieie.GetQuantiles(n+1,sieieb,prob)
            sieiebins=ROOT.RooBinning(len(sieieb)-1,sieieb,"sieiebins" )
            sieievar.setBinning(sieiebins)
            histo2_sieie=ROOT.TH2F("histo2_sieie_%s" %cat,"histo2_sieie_%s"%cat,len(sieieb)-1,sieieb,len(template_binning)-1,template_binning)
            tempCombined.fillHistogram(histo2_sieie,ROOT.RooArgList(sieievar,isovar)) 
            histo2_sieie.GetXaxis().SetNdivisions(4,3,0) 
            self.workspace_.rooImport(tempCombined)
            prb = array.array('d',[0.99,0.8,0.7,0.6,0.5,0.3,0.1])
            graphs=[]
            graphs=getQuantilesGraphs(histo2_sieie,prb)
            self.keep([graphs,histo2_sieie])
            self.plotQuantileGraphs(histo2_sieie,graphs,cat)
            #TODO fix numbers x axis
            truthp = self.reducedRooData("mctruth_p_singlePho_%s"% cat,setargs,False,redo=True)
            #works only if json file modified accordingly
            tempdatap = self.reducedRooData("template_p_singlePho_%s" %cat,setargs,False,redo=True)
            tempdatap.append(truthp)
            tempCombinedp=tempdatap
            tempCombinedp.SetName("template_allsieie_p_singlePho_%s" %cat)
            tempCombinedp.Print()
            histop_sieie=ROOT.TH1F("histop_sieie_%s" %cat,"histop_sieie_%s"%cat,40,sieielow,sieieup)
            tempCombinedp.fillHistogram(histop_sieie,ROOT.RooArgList(sieievar)) 
            #histop_sieie.Scale(1.0/histop_sieie.Integral())
            cSide=ROOT.TCanvas("cSide_%s" %cat,"cSide_%s" %cat)
            cSide.cd()
            sieiebins=ROOT.RooBinning(len(sieieb)-1,sieieb,"sieiebins" )
            lineSR=ROOT.TLine(sieieb[1],0.,sieieb[1],ymax)
            lineSB=ROOT.TLine(sieieb[2],0.,sieieb[2],ymax)
            histo_sieie2.SetLineColor(ROOT.kRed)
            histo_sieie2.SetLineWidth(2)
            histop_sieie.SetLineWidth(2)
            histop_sieie.Draw("HIST E1")
            lineSR.Draw("SAME")
            lineSB.Draw("SAME")
            histo_sieie2.Draw(" same HIST E1")
            leg =ROOT.TLegend(0.65,0.4,0.9,0.6)
            leg.SetTextSize(0.03)
            leg.SetTextFont(42);
            leg.SetFillColor(ROOT.kWhite)
            leg.AddEntry(histop_sieie,"prompt single photons","l")
            leg.AddEntry(histo_sieie2,"fake single photons","l")
            leg.Draw()
            histop_sieie.GetXaxis().SetTitle("#sigma_{i#etai#eta}") 
         #   histop_sieie.GetXaxis().SetNdivisions(4,3,0) 
            self.keep([cSide])
            self.autosave(True)
        self.saveWs(options,fout)

    ## ------------------------------------------------------------------------------------------------------------
    def plotQuantileGraphs(self,histo,graphs,cat):
        
        c=ROOT.TCanvas("cCorrelation2d_%s"%cat ,"cCorrelation2d_%s"%cat,10,10,700,900)
        c.cd()
        histo.GetXaxis().SetTitle("#sigma_{i#etai#eta}")
        histo.GetYaxis().SetTitle("Charged PF Isolation [GeV]")
        histo.Draw("colz")
        c.Update()
        ps = c.GetPrimitive("stats")
        ps.SetX2(0.99)
        histo.SetStats(0)
        c.Modified()
        c2=ROOT.TCanvas("cCorrelation1d_%s"%cat ,"cCorrelation1d_%s"%cat,10,10,700,900)
        c2.Divide(1,2)
        c2.cd(1)
        histo.ProjectionX().Draw()
        c2.cd(2)
        histo.ProjectionY().Draw()
        
        cQ=ROOT.TCanvas("cCorrelation_%s"%cat ,"corr chIso mass %s"% cat,10,10,700,900)
        cQ.cd()
        i=0
        leg =ROOT.TLegend(0.55,0.65,0.85,0.9)
        leg.SetTextSize(0.03)
        leg.SetTextFont(42);
        leg.SetFillColor(ROOT.kWhite)
        for gr in graphs:
            gr.SetMarkerStyle(21)
            gr.SetMarkerColor(ROOT.kRed-i)
            gr.SetLineColor(ROOT.kRed-i)
            if i==0:
                gr.GetXaxis().SetTitle("#sigma_{i#etai#eta}")
                gr.GetXaxis().SetNdivisions(4,3,0) 
                gr.GetYaxis().SetTitle("Charged PF Isolation [GeV]")
                gr.GetYaxis().SetRangeUser(0.,24.)
                gr.Draw("AP")
            if i>0:
                gr.Draw("P SAME")
            leg.AddEntry(gr,gr.GetName()[-14:],"ple")
            i=i+1
        leg.Draw()
        self.keep( [c,c2,cQ] )
        self.autosave(True)
        #

    ## ------------------------------------------------------------------------------------------------------------

    def plotHistos(self,histlist,title,template_bins,dim1,logx=False,logy=False,numEntries=None,ID=99.):
        b=ROOT.TLatex()
        b.SetNDC()
        b.SetTextSize(0.035)
        b.SetTextColor(ROOT.kBlack)
        denominator=0
        if not "ff" in histlist[0].GetName():
                if "unroll" in title:
                        leg = ROOT.TLegend(0.2,0.2,0.6,0.4)
                else:leg = ROOT.TLegend(0.65,0.65,0.85,0.9  )
        else:
                if "unroll" in title:
                        leg = ROOT.TLegend(0.3,0.3,0.5,0.5)
                else:leg = ROOT.TLegend(0.2,0.2,0.35,0.4  )
        leg.SetFillColor(ROOT.kWhite)
       # leg.SetHeader("#%s " % numEntries)
        canv = ROOT.TCanvas(title,title,1400,1000)
        canv.Divide(1,2)
        canv.cd(1)
        ROOT.gPad.SetPad(0., 0.3, 1., 1.0)
        ROOT.gPad.SetLogy()
        if logx:
            ROOT.gPad.SetLogx()
        canv.cd(2)
        ROOT.gPad.SetPad(0., 0.0, 1., 0.3)
        ROOT.gPad.SetGridy()
        canv.cd(1)
        # for dataMc plot MC as filled and data as points
        histstart=0
        ymin=5e-5
        ymax = 5.
        histlist[histstart].GetYaxis().SetLabelSize( histlist[histstart].GetYaxis().GetLabelSize() * canv.GetWh() / ROOT.gPad.GetWh() )
        k=0
        minX=-0.5
        if dim1:histlist[histstart].GetXaxis().SetTitle(title[-17:])
        histlist[histstart].GetYaxis().SetLabelSize( 1.5*histlist[histstart].GetYaxis().GetLabelSize() * canv.GetWh() / ROOT.gPad.GetWh() )
        histlist[histstart].GetYaxis().SetTitleSize(1.2*histlist[histstart].GetYaxis().GetTitleSize() * canv.GetWh() / ROOT.gPad.GetWh() )
        histlist[histstart].GetXaxis().SetTitle("")
        histlist[histstart].GetXaxis().SetLabelSize(0.)
        histlist[histstart].GetYaxis().SetTitle("arbitary units")
        for i in range(histstart,len(histlist)):
            if "pp" in histlist[histstart].GetName():
                comp="#gamma #gamma"
            if "pf" in histlist[histstart].GetName():comp="#gamma j"
            if "ff" in histlist[histstart].GetName():comp="j j"
           # if histlist[i].GetMinimum() != 0.:   ymin = min(ymin,histlist[histstart].GetMinimum()-histlist[histstart].GetMinimum()*0.5)
            mctruth_expectedStyle =  [["SetFillStyle",3004],["SetFillColorAlpha",(ROOT.kRed,0.0)],["SetLineColor",ROOT.kRed]]
            mc_expectedStyle =[["SetFillStyle",3004],["SetFillColorAlpha",(ROOT.kAzure+2,0.0)],["SetLineColor",ROOT.kAzure+2]]
            data_expectedStyle =[["SetLineWidth",3],["SetMarkerStyle",20],["SetMarkerSize",2.0],["SetMarkerColor",ROOT.kBlack],["SetLineColor",ROOT.kBlack]]
            ratio_expectedStyle =[["SetLineWidth",3],["SetMarkerStyle",34],["SetMarkerSize",1.3],["SetMarkerColor",ROOT.kAzure+2],["SetLineColor",ROOT.kAzure+2]]
            if "mctruth" in histlist[i].GetName():
                style_utils.apply(histlist[i],mctruth_expectedStyle)
                if i==histstart:histlist[i].Draw("E2")
                else: histlist[i].Draw("E2 SAME")
                leg.AddEntry(histlist[i],"%s MC truth"%comp,"f")  
                denominator=histlist[i].Clone("denominator")

            elif ("mix" and "MC" in histlist[i].GetName()) or ("mc_pp" in histlist[i].GetName()):
                style_utils.apply(histlist[i],mc_expectedStyle)
                if i==histstart:histlist[i].Draw("E2")
                else: histlist[i].Draw("E2 SAME")
                leg.AddEntry(histlist[i],"%s MC"%comp,"f")  
                ratios=histlist[i].Clone("ratio") 
            elif not ("mc" or "MC") in histlist[i].GetName():
                style_utils.apply(histlist[i],data_expectedStyle)
                if i==histstart:histlist[i].Draw("E")
                else: histlist[i].Draw("E SAME")
                leg.AddEntry(histlist[i],"%s data"%comp,"lp")  
               # ratios=histlist[i].Clone("ratio") 
            #leg.AddEntry(histlist[i],histlist[i].GetName(),"l")  
          #  ymax = max(ymax,histlist[histstart].GetMaximum())
            #histlist[i].GetYaxis().SetRangeUser(1e-4,ymax*2.)
            histlist[i].GetXaxis().SetRangeUser(minX,15.)
          #  b.DrawLatex(0.45,.94,"#int L dt=1.7 /fb  CMS PRELIMINARY")
        if "unroll" in title:
            ymin = 1.e-5
            histlist[i].GetXaxis().SetRangeUser(minX,9.)
            histlist[histstart].GetYaxis().SetRangeUser(ymin,ymax)
         #   histlist[histstart].GetYaxis().SetLimits(ymin*0.5,ymax)
        leg.Draw()
        #change for data mc comparison 
        canv.cd(2)
        if denominator !=0:
            style_utils.apply(ratios,ratio_expectedStyle)
            ratios.Divide(denominator)
            ratios.Draw()        
            ratios.GetYaxis().SetTitleSize(histlist[histstart].GetYaxis().GetTitleSize() * 5.0/3.0 )
            ratios.GetYaxis().SetLabelSize(histlist[histstart].GetYaxis().GetLabelSize() *  7.0/3.0 )
            ratios.GetYaxis().SetTitleOffset(histlist[histstart].GetYaxis().GetTitleOffset() *  4.0/7.0 )
            ratios.GetXaxis().SetTitleOffset(ratios.GetXaxis().GetTitleOffset() *7.8/7.0)
            ratios.GetXaxis().SetLabelSize(ratios.GetXaxis().GetLabelSize() *  7.0/3.0 )
            ratios.GetXaxis().SetTitleSize( ratios.GetYaxis().GetTitleSize() * 4.0/3.0 )
            ratios.GetXaxis().SetLabelSize( ratios.GetYaxis().GetLabelSize()  )
            ratios.GetYaxis().SetTitle("MC_{temp}/MC_{truth}")
            ratios.GetYaxis().SetNdivisions(505)
            ratios.GetXaxis().SetRangeUser(minX,15.)
            ratios.GetYaxis().SetRangeUser(0.,3.5)
            if not  "unroll" in title:
                ID=ID+1
                ratios.GetXaxis().SetTitle("I_{Ch}(#gamma^{%d}) (GeV)" %ID)
            else: 
                ratios.GetXaxis().SetTitle("(I_{Ch}(#gamma^{1}),I_{Ch}(#gamma^{2})) bin")
            ROOT.gStyle.SetOptStat(0)
        canv.cd(1)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
       #B ROOT.gPad.SetTopMargin(0.1*margin)
        ROOT.gPad.SetBottomMargin(0.2*margin)
        ROOT.gPad.Modified()
        ROOT.gPad.Update()

        canv.cd(2)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
        ROOT.gPad.SetBottomMargin(1.8*margin)
        ROOT.gPad.SetTopMargin(0.25*margin)
        ROOT.gPad.Modified()
        ROOT.gPad.Update()
        self.keep( [canv] )
        self.format(canv,self.options.postproc)
        self.autosave(True)
            


    ## ------------------------------------------------------------------------------------------------------------
    def build3dTemplates(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        ROOT.TH1F.SetDefaultSumw2(True)
        weight_cut=options.build3d.get("weight_cut") 
        var,var_b=self.getVar("templateNdim2d_unroll")
        unrolledIso=self.buildRooVar(var,var_b,recycle=True)
        unrolledIso.Print()
        isoargs=ROOT.RooArgSet("isoargs")
        for idim in range(int(options.build3d["ndim"])):
            iso,biniso=self.getVar("templateNdim2Dim%d" % (idim))
            isoargs.add(self.buildRooVar(iso,biniso,recycle=True))
        template_binning=array.array('d',[0.0,0.1,5.,15.])
         
        self.histounroll_book(template_binning,isoargs)
        return
        components=options.build3d.get("components")
        dim=options.build3d.get("dimensions")
        mass_var,mass_b=self.getVar("mass")
        mass=self.buildRooVar(mass_var,mass_b,recycle=True)
        mass.Print()
        setargs=ROOT.RooArgSet(isoargs)
        setargs.add(mass)
        categories = options.build3d.get("categories")
        components = options.build3d.get("components")
        for catd in categories:
            print "-----------------------------------------------------------------"
            catd=="EBEE"
            cat=="EBEE"
            if catd=="EEEB": cat="EBEE" 
            else:cat=catd
            data_book=self.rooData("hist2d_forUnrolled")
            data_book.Print()
            #get dataset and add column (actually filling values in) 
            unrolledVar=ROOT.RooHistFunc(unrolledIso.GetName(),unrolledIso.GetName(),isoargs,data_book)
            data = self.reducedRooData("data_2D_%s" %cat,setargs,False,sel=weight_cut, redo=False)
            data.addColumn(unrolledVar)
            dataCombine=data.reduce(ROOT.RooArgSet(mass,unrolledIso))
            dataCombine.SetName("data_3D_%s" %cat)
            dataCombine.Print()
            self.workspace_.rooImport(dataCombine,ROOT.RooFit.RenameVariable("mass","mgg"))
          #  for temp in tempname=options.build3d.get("tempname"):
          #TODO grab template names from json file
            for comp in components:
                print cat, comp 
                histo_book=self.rooData("hist2d_forUnrolled")
                if comp=="pp":
                    histo_temp = self.reducedRooData("template_%s_2D_%s" %(comp,cat),setargs,False,sel=weight_cut,redo=False)
                else:
                    histo_temp = self.reducedRooData("template_mix_%s_kDSinglePho2D_%s" %(comp,cat),setargs,False,sel=weight_cut,redo=False)
                
                histo_temp.addColumn(unrolledVar)
                histoCombine_temp=histo_temp.reduce(ROOT.RooArgSet(mass,unrolledIso))
                histoCombine_temp.SetNameTitle("template_%s_3D_%s" %(comp,cat),"template_%s_3D_%s" %(comp,cat))
                histoCombine_temp.Print()
                self.workspace_.rooImport(histoCombine_temp,ROOT.RooFit.RenameVariable("mass","mgg"))
                histo_mctruth = self.reducedRooData("mctruth_%s_2D_%s" %(comp,cat),setargs,False,sel=weight_cut,redo=False)
                histo_mctruth.addColumn(unrolledVar)
                histoCombine_mctruth=histo_mctruth.reduce(ROOT.RooArgSet(mass,unrolledIso))
                histoCombine_mctruth.SetNameTitle("mctruth_%s_3D_%s" %(comp,cat),"mctruth_%s_3D_%s" %(comp,cat))
                histoCombine_mctruth.Print()
                self.workspace_.rooImport(histoCombine_mctruth,ROOT.RooFit.RenameVariable("mass","mgg"))
        self.saveWs(options,fout)
    ## ------------------------------------------------------------------------------------------------------------
    def nominalFit(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        self.doNominalFit(options,args)
        self.saveWs(options,fout)

## ------------------------------------------------------------------------------------------------------------
    def doNominalFit(self,options,args):
        ROOT.TH1F.SetDefaultSumw2(True)
        for name, nomFit in options.nominalFit.iteritems():
            if name.startswith("_"): continue
            isoargs=ROOT.RooArgSet("isoargs")
            iso1,biniso1=self.getVar("templateNdim2Dim0")
            iso2,biniso2=self.getVar("templateNdim2Dim1")
            if len(options.template_binning) > 0:
                biniso = array.array('d',options.template_binning)
            else:
                biniso = array.array('d',options.comparisons.get("template_binning"))
            isoargs.add(self.buildRooVar(iso1,biniso,recycle=True))
            isoargs.add(self.buildRooVar(iso2,biniso,recycle=True))
            obsls=ROOT.RooArgList("obsls")
            weight_cut=nomFit.get("weight_cut") 
            var,var_b=self.getVar(nomFit.get("observable"))
            lowsigRegion=float(nomFit.get("lowerLimitSigRegion"))
            upsigRegion=float(nomFit.get("upperLimitSigRegion"))
            observable=self.buildRooVar(var,var_b,recycle=True)
            observable.setRange("sigRegion",lowsigRegion,upsigRegion)
            obsls.add(observable)
            components=nomFit.get("components")
            print "nominal fit with: ", name, " observable : ", nomFit.get("observable")
            tempname=options.fit_templates[0]
            dim=nomFit.get("dimensions")
            mass_var,mass_b=self.getVar(nomFit.get("mass_binning"))
            mass=self.buildRooVar(mass_var,mass_b,recycle=True)
            setargs=ROOT.RooArgSet(isoargs)
            setargs.add(mass)
            hist_Eta=[]
            categories = options.fit_categories
            mass_split= [int(x) for x in options.fit_massbins]
            jkpf=nomFit.get("jackknife_pf",False)
            jkpp=nomFit.get("jackknife_pp",False)
            jkID="non existing"

            if jkpf:
                jkID="jkpf"
                jks=int(options.jackknife.get("jk_source"))
                jkt=int(options.jackknife.get("jk_target"))
                num=jks+jkt
            elif jkpp:
                jkID="jkpp"
                num=int(options.jackknife.get("jk_pp"))
            else:num=1
            for cat in categories:
                print "-----------------------------------------------------------------"
                if cat=="EEEB": catd="EBEE" 
                else:catd=cat
                data_book=self.rooData("hist2d_forUnrolled")
                unrolledVar=ROOT.RooHistFunc(observable.GetName(),observable.GetName(),isoargs,data_book)
                if not options.fit_mc: dodata=True
                else: dodata=False
                if dodata:
                    dset="_"
                else:
                    dset="_mc_"
                if dodata:
                    data = self.reducedRooData("data_2D_%s" % (catd),setargs,False,sel=weight_cut, redo=False)
                else:
                    data = self.reducedRooData("mc_2D_%s" % (catd),setargs,False,sel=weight_cut, redo=False)
              #  data = self.reducedRooData("data_2D_%s" % (catd),setargs,False,sel=weight_cut, redo=False)
                data.addColumn(unrolledVar)
                data=data.reduce(ROOT.RooArgSet(mass,observable))
                tree_mass=self.treeData("%s_pp_2D_%s"%(options.plotPurity["treetruth"], cat))
                tps=[]
                massTuple = ROOT.TNtuple("tree_massbins_%s_%s" % (dim,cat),"tree_massbins_%s_%s" % (dim,cat),"massbin:masserror" )
                self.store_[massTuple.GetName()] = massTuple
                for i in range(num):
                    if not (jkpf or jkpp):tpi = ROOT.TNtuple("tree_fitresult_fraction%s%s_%s_%s" % (dset,tempname,dim,cat),"tree_fitresult_fraction_%s_%s_%s" % (tempname,dim,cat),"purity_pp:err_pplow:err_pphigh:purity_pf:err_pflow:err_pfhigh:purity_ff:err_fflow:err_ffhigh" )
                    elif jkpf: tpi = ROOT.TNtuple("tree_fitresult_fraction%s%s_jkpf%i_%s_%s" % (dset,tempname,i,dim,cat),"tree_fitresult_fraction_%s_jk%i_%s_%s" % (tempname,i,dim,cat),"purity_pp:error_pp:purity_pf:error_pf" )

                    elif jkpp: tpi = ROOT.TNtuple("tree_fitresult_fraction%s%s_jkpp%i_%s_%s" % (dset,tempname,i,dim,cat),"tree_fitresult_fraction_%s_jk%i_%s_%s" % (tempname,i,dim,cat),"purity_pp:error_pp:purity_pf:error_pf" )
                    self.store_[tpi.GetName()] = tpi
                    tps.append(tpi)
                if options.pu_sigregion:
                    tpSig = ROOT.TNtuple("tree_fitresult_fraction_sigRegion%s%s_%s_%s" % (dset,tempname,dim,cat),"tree_fitresult_fraction_sigRegion%s%s_%s_%s" % (dset,tempname,dim,cat),"purity_pp:err_pplow:err_pphigh:purity_pf:err_pflow:err_pfhigh:purity_ff:err_fflow:err_ffhigh" )

                    tpRatSig = ROOT.TNtuple("tree_fitresult_fraction_ratio_of_uncertainties_forsigregion%s%s_%s_%s" % (dset,tempname,dim,cat),"tree_fitresult_fraction_ratio_of_uncertainties_forsigregion%s%s_%s_%s" % (dset,tempname,dim,cat),"ratSig_pplow:ratSig_pphigh:ratSig_pflow:ratSig_pfhigh:ratSig_fflow:ratSig_ffhigh" )
                    self.store_[tpSig.GetName()] = tpSig
                    self.store_[tpRatSig.GetName()] = tpRatSig
                massrange= range(0,tree_mass.GetEntries())
                if not options.fixed_massbins and len(mass_split)== 3:
                    massrange=range(mass_split[2],mass_split[1])
                for mb in massrange:
                    print "---------------------------------------------------" 
                    tree_mass.GetEntry(mb)
                    cut=ROOT.TCut("mass>%f && mass<%f"% (tree_mass.massbin-tree_mass.masserror,tree_mass.massbin+tree_mass.masserror))
                    cut_s= "%1.0f_%1.0f"%  (tree_mass.massbin-tree_mass.masserror,tree_mass.massbin+tree_mass.masserror)
                    print cut.GetTitle()
                    data_massc=data.reduce(cut.GetTitle())
                    #define fit parameters
                    jpp = ROOT.RooRealVar("jpp","jpp",float(nomFit.get("jppstart")),0.,1.)
                    jpf = ROOT.RooRealVar("jpf","jpf",float(nomFit.get("jpfstart")),0.,1.)
                    fpp= ROOT.RooFormulaVar("fpp_%s"%cut_s,"fpp_%s"%cut_s,"jpp",ROOT.RooArgList(jpp))
                    pu_estimates=ROOT.RooArgList(fpp)
                    pu_estimates_roopdf=ROOT.RooArgList(fpp)
                    if len(components)>2: 
                        fpf= ROOT.RooFormulaVar("fpf_%s"%cut_s,"fpf_%s"%cut_s,"jpf ",ROOT.RooArgList(jpf))
                        pu_estimates.add(fpf)
                    pdf_collections=[ ]
                    i=0
                    if not (jkpf or jkpp):
                        pdf_set=ROOT.RooArgList() 
                        for comp in nomFit["components"]:
                            if tempname=="unrolled_template_mix" and not dodata:
                                dim_new="2DMC"
                                dset="_"
                            else:dim_new=dim
                            if tempname=="unrolled_mctruth": dset="_"
                            if i==0 and  tempname=="unrolled_template_mix":
                                tempname_new="unrolled_template"
                                if dodata:
                                    dset="_"
                                else: 
                                    dset="_mc_"
                                    dim_new="2D"
                            else: tempname_new=tempname
                            
                            print "%s%s%s_%s_%s_mb_%s"%(tempname_new,dset,comp, dim_new,cat,cut_s)
                            histo = self.rooData("%s%s%s_%s_%s_mb_%s"%(tempname_new,dset,comp, dim_new,cat,cut_s))
                            rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetTitle(),ROOT.RooArgSet(obsls),histo)
                         
                            self.keep([rooHistPdf])
                            pdf_set.add(rooHistPdf)
                            i=i+1

                        pdf_collections.append(pdf_set)
                    else:
                        for i in range(num):
                            pdf_set=ROOT.RooArgList()
                            for comp in nomFit["components"]:
                                if jkpf:
                                    if comp=="pp":
                                        histo = self.rooData("unrolled_template_pp_2D_%s_mb_%s"%(cat,cut_s))
                                        rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetName(),ROOT.RooArgSet(obsls),histo)
                                    elif comp=="pf":
                                        if i < jks: name= "unrolled_template_mix_pf_2D_%i_%s_mb_%s"%(i,cat,cut_s)
                                        elif i>= jks:name= "unrolled_template_mix_pf_%i_2D_%s_mb_%s"%(i-jks,cat,cut_s)
                                        histo = self.rooData(name)
                                        rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetName(),ROOT.RooArgSet(obsls),histo)
                                else:
                                    if comp=="pp":
                                        histo = self.rooData("unrolled_template_pp_%i_2D_%s_mb_%s"%(i,cat,cut_s))
                                        rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetName(),ROOT.RooArgSet(obsls),histo)
                                    elif comp=="pf":
                                        histo = self.rooData("unrolled_template_mix_pf_2D_%s_mb_%s"%(cat,cut_s))
                                        rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetName(),ROOT.RooArgSet(obsls),histo)
                                if comp=="ff":
                                    histo = self.rooData("unrolled_template_mix_ff_2D_%s_mb_%s"%(cat,cut_s))
                                    rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetName(),ROOT.RooArgSet(obsls),histo)
                                self.keep([rooHistPdf])
                                pdf_set.add(rooHistPdf)
                            pdf_collections.append(pdf_set)
                    for k in range(num):
                        ArgListPdf=None
                        jpp.setVal(float(nomFit.get("jppstart")))
                        jpf.setVal(float(nomFit.get("jpfstart")))
                        ArgListPdf=pdf_collections[k]
                        fitUnrolledPdf=ROOT.RooAddPdf("fitPdfs_%s%s%s_%s_mb_%s" % (tempname,dset,cat,dim,cut_s),"fitPdfs_%s%s%s_%s_mb_%s" % (tempname,dset,cat,dim,cut_s),ArgListPdf,pu_estimates,True )
              #save roofitresult in outputfile
                        #recursive definition: fpp*pdf_pp+(1-fpp)*(fpf*pdf_pf+(1-fpf)*fff*pdf_fff)
                        #fraction for pp = fpp.getVal()=jpp
                        #fraction for pf=fpu_pf.getVal()=(1-fpp)*fpf
                        #fraction for ff=fpu_ff.getVal()=(1-fpp)*(1-fpf)
                        #sum of all fractions is 1
                        fit_studies = fitUnrolledPdf.fitTo(data_massc, RooFit.NumCPU(8),RooFit.Strategy(2),RooFit.SumW2Error(True),RooFit.Save(True),RooFit.Minos(True),RooFit.PrintLevel(1))
                        pu_pp=fpp.getParameter("jpp").getVal()
                        if len(components)>2: 
                            fpu_pf= ROOT.RooFormulaVar("fpu_pf","fpu_pf","(1-@0)*@1",ROOT.RooArgList(fpp.getParameter("jpp"),fpf.getParameter("jpf")))
                            pu_pf=fpu_pf.getVal()
                            fpu_ff= ROOT.RooFormulaVar("fpu_ff","fpu_ff","(1-@0)*(1-@1)",ROOT.RooArgList(fpp.getParameter("jpp"),fpf.getParameter("jpf")))
                            print "[INFO] fraction values %.3f, %.3f, %.3f"%(fpp.getVal(), fpu_pf.getVal(), fpu_ff.getVal())
                            err_jpfhigh=fpf.getParameter("jpf").getAsymErrorHi()
                            err_jpflow=abs(fpf.getParameter("jpf").getAsymErrorLo())
                            pu_ff=fpu_ff.getVal()
                            self.buildRooVar("fpf_%s"%cut_s,[fpf.getParameter("jpf").getVal(),0.,1.])
                        else:
                            pu_pf=1-pu_pp
                        #use MINOS error except if one of the parameters is at the limit
                        limit_minos=float(nomFit.get("limit_to_use_minos"))
                        databin_entries=data_massc.sumEntries()
                        if( (pu_pp < limit_minos) and not ((fpp.getParameter("jpp").getAsymErrorHi()==0 or fpp.getParameter("jpp").getAsymErrorLo()==0) or (len(components) >2 and (err_jpfhigh==0 or err_jpflow==0)))):
                            err_pphigh=fpp.getParameter("jpp").getAsymErrorHi()
                            err_pplow=abs(fpp.getParameter("jpp").getAsymErrorLo())
                        else: 
                            print "[INFO] take Clopper Pearson uncertainty as MINOS failed"
                            print "[INFO] data points",databin_entries, ", events pp: %.3f - integer"%(databin_entries*pu_pp), int(round(databin_entries*pu_pp)), ", events pf: %.3f - integer"%(databin_entries*pu_pf), int(round(databin_entries*pu_pf)),", events ff: %.3f -integer"%(databin_entries*pu_ff),int(round(databin_entries*pu_ff))
                            err_pphigh=ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_pp*databin_entries)),0.68,True)-pu_pp
                            if err_pphigh<0: err_pphigh=0.
                            err_pplow=(pu_pp-ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_pp*databin_entries)),0.68,False))
                        self.buildRooVar("fpp_%s"%cut_s,[fpp.getParameter("jpp").getVal(),0.,1.])
                        self.workspace_.rooImport(fitUnrolledPdf,ROOT.RooFit.RecycleConflictNodes())
                        if len(components)>2: 
                            if (pu_pp < limit_minos) and not (err_pphigh==0 or err_pplow==0 or err_jpfhigh==0 or err_jpflow==0): 
                                fpu_pf_errlow= ROOT.RooFormulaVar("fpu_pf_errlow","fpu_pf_errlow","sqrt(pow(@0*%f,2)+pow(1-@1,2)*pow(%f,2))"%(err_pplow,err_jpflow),ROOT.RooArgList(fpf.getParameter("jpf"),fpp.getParameter("jpp")))
                                fpu_pf_errhigh=  ROOT.RooFormulaVar("fpu_pf_errhigh","fpu_pf_errhigh","sqrt(pow(@0,2)*pow(%f,2)+pow(1-@1,2)*pow(%f,2))"%(err_pphigh,err_jpfhigh),ROOT.RooArgList(fpf.getParameter("jpf"),fpp.getParameter("jpp")))
                                err_pflow=fpu_pf_errlow.getVal()
                                err_pfhigh=fpu_pf_errhigh.getVal()
                                fpu_ff_errlow= ROOT.RooFormulaVar("fpu_ff_errlow","fpu_ff_errlow","sqrt(pow((1-@0)*%f,2)+pow((1-@1)*%f,2))"%(err_pplow,err_jpflow),ROOT.RooArgList(fpf.getParameter("jpf"),fpp.getParameter("jpp")))
                                fpu_ff_errhigh= ROOT.RooFormulaVar("fpu_ff_errhigh","fpu_ff_errhigh","sqrt(pow((1-@0)*%f,2)+pow((1-@1)*%f,2))"%(err_pphigh,err_jpfhigh),ROOT.RooArgList(fpf.getParameter("jpf"),fpp.getParameter("jpp")))

                                err_fflow=fpu_ff_errlow.getVal()
                                err_ffhigh=fpu_ff_errhigh.getVal()
                            else: 
                                print "[INFO] take Clopper Pearson uncertainty as MINOS failed"
                                err_pfhigh=ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_pf*databin_entries)),0.68,True)-pu_pf
                                err_pflow=(pu_pf-ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_pf*databin_entries)),0.68,False))
                                err_ffhigh=ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_ff*databin_entries)),0.68,True)-pu_ff
                                err_fflow=(pu_ff-ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_ff*databin_entries)),0.68,False))
                            self.workspace_.rooImport(fit_studies.covarianceMatrix(), "covariance_studies%i_%s"%(k,cut_s))
                            self.workspace_.rooImport(fit_studies.correlationMatrix(),"correlation_studies%i_%s"%(k,cut_s))
                            self.workspace_.rooImport(fit_studies,"fit_studies%i_%s" %(k,cut_s))
                            print "[INFO] fraction errors: err_pplow %.3f"%err_pplow, ", err_pplow/purity_pp*100 %.3f"%(err_pplow*100/pu_pp),", err_pphigh %.3f" %err_pphigh,", err_pphigh/purity_pp*100 %.3f"%(err_pphigh*100/pu_pp)
                            print "[INFO] fraction errors: err_pflow %.3f"%err_pflow, ", err_pflow/purity_pf*100 %.3f"%(err_pflow*100/pu_pf),", err_pfhigh %.3f" %err_pfhigh,", err_pfhigh/purity_pf*100 %.3f"%(err_pfhigh*100/pu_pf)
                            print "[INFO] fraction errors: err_fflow %.3f"%err_fflow, ", err_fflow/purity_ff*100 %.3f"%(err_fflow*100/pu_ff),", err_ffhigh %.3f" %err_ffhigh,", err_ffhigh/purity_ff*100 %.3f"%(err_ffhigh*100/pu_ff)
                        else:
                            pu_pf=1-pu_pp
                            pu_ff=0.
                            err_fflow=0.
                            err_ffhigh=0.
                            if (pu_pp < limit_minos) and not (err_pphigh==0 or err_pplow==0): 
                                err_pflow=err_pplow
                                err_pfhigh=err_pphigh
                            else: 
                                err_pfhigh=ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_pf*databin_entries)),0.68,True)-pu_pf
                                err_pflow=(pu_pf-ROOT.TEfficiency.ClopperPearson(int(round(databin_entries)),int(round(pu_pf*databin_entries)),0.68,False))
                        tps[k].Fill(pu_pp,err_pplow,err_pphigh,pu_pf,err_pflow,err_pfhigh,pu_ff,err_fflow,err_ffhigh)
                        massTuple.Fill(tree_mass.massbin,tree_mass.masserror)
                       # if dodata and not (jkpp or jkpf):
                        self.plotFit(observable,fitUnrolledPdf,ArgListPdf,data_massc,components,cat,log=False,i=k)


#############################################Extrapolation to Signal region#########################################################

                        if options.pu_sigregion:
                            #formula to extrapolate back to signal region
                            fpuSig_pp= ROOT.RooFormulaVar("fpuSig_pp","fpuSig_pp","(@0*@1)/(@2)",ROOT.RooArgList(fpp,fitUnrolledPdf.pdfList()[0].createIntegral(ROOT.RooArgSet(observable),"sigRegion"),fitUnrolledPdf.createIntegral(ROOT.RooArgSet(observable),"sigRegion")))
                            #do extra because interested in error on ratio of the two integrals, not the individual error
                            integralratio_pp= ROOT.RooFormulaVar("integralratio_pp","integralratio_pp","(@0)/(@1)",ROOT.RooArgList(fitUnrolledPdf.pdfList()[0].createIntegral(ROOT.RooArgSet(observable),"sigRegion"),fitUnrolledPdf.createIntegral(ROOT.RooArgSet(observable),"sigRegion")))
                            puSig_pp=fpuSig_pp.getVal()
                            errSig_pplow= ROOT.RooFormulaVar("errSig_pplow","errSig_pplow","sqrt(pow(%f*@0,2)+pow(%f*@1,2))"%(err_pplow,integralratio_pp.getPropagatedError(fit_studies)),ROOT.RooArgList(integralratio_pp,fpp)).getVal()
                            errSig_pphigh= ROOT.RooFormulaVar("errSig_pphigh","errSig_pphigh","sqrt(pow(%f*@0,2)+pow(%f*@1,2))"%(err_pphigh,integralratio_pp.getPropagatedError(fit_studies)),ROOT.RooArgList(integralratio_pp,fpp)).getVal()
                            #store ratio of both errors for scaling of systematic and jack knife uncertainty
                            #fix to not divide by zero
                            if err_pphigh < 1e-5:
                                ratSig_pphigh=1.
                                print "[WARNING] error pphigh is zero"
                            else:ratSig_pphigh=errSig_pphigh/err_pphigh
                           
                            ratSig_pplow=errSig_pplow/abs(err_pplow)
                            if len(components)==2:
                                puSig_pf=1-puSig_pp
                                errSig_pflow=errSig_pplow 
                                errSig_pfhigh=errSig_pphigh
                                ratSig_pfhigh=errSig_pfhigh/err_pfhigh
                                ratSig_pflow=errSig_pflow/abs(err_pflow)
                                puSig_ff=0.
                                errSig_fflow=0.
                                errSig_ffhigh=0.
                                ratSig_fflow=0.
                                ratSig_ffhigh=0.

                            elif len(components)>2:
                                fpuSig_pf= ROOT.RooFormulaVar("fpuSig_pf","fpuSig_pf","(@0*@1)/@2",ROOT.RooArgList(fpu_pf,fitUnrolledPdf.pdfList()[1].createIntegral(ROOT.RooArgSet(observable),"sigRegion"),fitUnrolledPdf.createIntegral(ROOT.RooArgSet(observable),"sigRegion")))
                                integralratio_pf= ROOT.RooFormulaVar("integralratio_pf","integralratio_pf","(@0)/(@1)",ROOT.RooArgList(fitUnrolledPdf.pdfList()[1].createIntegral(ROOT.RooArgSet(observable),"sigRegion"),fitUnrolledPdf.createIntegral(ROOT.RooArgSet(observable),"sigRegion")))
                                errSig_pflow= ROOT.RooFormulaVar("errSig_pflow","errSig_pflow","sqrt(pow(%f*@0,2)+pow(%f*@1,2))"%(err_pflow,integralratio_pf.getPropagatedError(fit_studies)),ROOT.RooArgList(integralratio_pf,fpu_pf)).getVal()
                                errSig_pfhigh= ROOT.RooFormulaVar("errSig_pfhigh","errSig_pfhigh","sqrt(pow(%f*@0,2)+pow(%f*@1,2))"%(err_pfhigh,integralratio_pf.getPropagatedError(fit_studies)),ROOT.RooArgList(integralratio_pf,fpu_pf)).getVal()

                                puSig_pf=fpuSig_pf.getVal()
                                ratSig_pfhigh=errSig_pfhigh/err_pfhigh
                                ratSig_pflow=errSig_pflow/abs(err_pflow)
                                fpuSig_ff= ROOT.RooFormulaVar("fpuSig_ff","fpuSig_ff","(@0*@1)/@2",ROOT.RooArgList(fpu_ff,fitUnrolledPdf.pdfList()[2].createIntegral(ROOT.RooArgSet(observable),"sigRegion"),fitUnrolledPdf.createIntegral(ROOT.RooArgSet(observable),"sigRegion")))
                                puSig_ff=fpuSig_ff.getVal()
                                integralratio_ff= ROOT.RooFormulaVar("integralratio_ff","integralratio_ff","(@0)/(@1)",ROOT.RooArgList(fitUnrolledPdf.pdfList()[2].createIntegral(ROOT.RooArgSet(observable),"sigRegion"),fitUnrolledPdf.createIntegral(ROOT.RooArgSet(observable),"sigRegion")))
                                errSig_fflow= ROOT.RooFormulaVar("errSig_fflow","errSig_fflow","sqrt(pow(%f*@0,2)+pow(%f*@1,2))"%(err_fflow,integralratio_ff.getPropagatedError(fit_studies)),ROOT.RooArgList(integralratio_ff,fpu_ff)).getVal()
                                errSig_ffhigh= ROOT.RooFormulaVar("errSig_ffhigh","errSig_ffhigh","sqrt(pow(%f*@0,2)+pow(%f*@1,2))"%(err_ffhigh,integralratio_ff.getPropagatedError(fit_studies)),ROOT.RooArgList(integralratio_ff,fpu_ff)).getVal()
                                ratSig_ffhigh=errSig_ffhigh/err_ffhigh
                                ratSig_fflow=errSig_fflow/abs(err_fflow)
                                print "[INFO] fraction errors signalregion: ratios error pplow %.3f, ratio errors pphigh %.3f, err_pplow %.3f"%(ratSig_pplow,ratSig_pphigh,errSig_pplow), ", err_pplow*purity_pp*100 %.3f"%(errSig_pplow*100/puSig_pp),", err_pphigh %.3f" %errSig_pphigh,", err_pphigh*purity_pp*100 %.3f"%(errSig_pphigh*100/puSig_pp)
                                print "[INFO] fraction errors signalregion: ratios error pflow %.3f, ratio errors pfhigh %.3f, err_pflow %.3f"%(ratSig_pflow,ratSig_pfhigh,errSig_pflow), ", err_pflow*purity_pf*100 %.3f"%(errSig_pflow*100/puSig_pf),", err_pfhigh %.3f" %errSig_pfhigh,", err_pfhigh*purity_pf*100 %.3f"%(errSig_pfhigh*100/puSig_pf)
                                print "[INFO] fraction errors signalregion:ratios error fflow %.3f, ratio errors ffhigh %.3f,  err_fflow %.3f"%(ratSig_fflow, ratSig_ffhigh,errSig_fflow), ", err_fflow*purity_ff*100 %.3f"%(errSig_fflow*100/puSig_ff),", err_ffhigh %.3f" %errSig_ffhigh,", err_ffhigh*purity_ff*100 %.3f"%(errSig_ffhigh*100/puSig_ff)
                            
                            tpSig.Fill(puSig_pp,errSig_pplow,errSig_pphigh,puSig_pf,errSig_pflow,errSig_pfhigh,puSig_ff,errSig_fflow,errSig_ffhigh)
                            tpRatSig.Fill(ratSig_pplow,ratSig_pphigh,ratSig_pflow,ratSig_pfhigh,ratSig_fflow,ratSig_ffhigh,tree_mass.massbin,tree_mass.masserror)
    #ML fit to weighted dataset: SumW2Error takes statistics of dataset into account, scales with number of events in datasetif ON good for MC comparison, takes limited statistics of MC dataset into account
  #  if OUT treated as if it would be data- for data MC comparison
                if jkpf or jkpp:
                    self.plotJKpurity(options,cat,dim,tps,jkID)
                print "done fit ...."
                print
    ## ---------------#--------------------------------------------------------------------------------------------
    def histunrollback(self,dataset,observable,cat,cut,template_binning,pu_pp,pu_pf,pu_ff):
        leg = ROOT.TLegend(0.6,0.5,0.85,0.9  )
        fit_expectedStyle =  [["SetLineWidth",2],["SetLineColor",ROOT.kBlue]]
        pdf_expectedStyle =  [["SetLineWidth",3],["SetLineStyle",ROOT.kDashed]]
        data_expectedStyle =[["SetLineWidth",3],["SetMarkerStyle",20],["SetMarkerSize",2.0],["SetMarkerColor",ROOT.kBlack],["SetLineColor",ROOT.kBlack]]
        ratio_expectedStyle =[["SetLineWidth",3],["SetMarkerStyle",20],["SetMarkerSize",2.0],["SetMarkerColor",ROOT.kBlack],["SetLineColor",ROOT.kBlack]]
        template_binning = array.array('d',template_binning)
        pppdf=self.rooPdf("pdf_unrolled_template_pp_2D_%s_mb_%s" %(cat,cut))
        pppdf.Print()
        pp1d=pppdf.createHistogram("pdf%s" %pppdf.GetName(),observable, RooFit.Binning(9,0.,9))
        pp2d=ROOT.TH2D("d2%s" % (pppdf.GetName()),"d2%s" % (pppdf.GetName()),len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
        pfpdf=self.rooPdf("pdf_unrolled_template_mix_pf_2D_%s_mb_%s" %(cat,cut))
         
        pf1d=pfpdf.createHistogram("pdf%s" %pfpdf.GetName(),observable, RooFit.Binning(9,0.,9))
        pf2d=ROOT.TH2D("d2%s" % (pfpdf.GetName()),"d2%s" % (pfpdf.GetName()),len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
        ffpdf=self.rooPdf("pdf_unrolled_template_mix_ff_2D_%s_mb_%s" %(cat,cut))
        ff1d=pfpdf.createHistogram("pdf%s" %pfpdf.GetName(),observable, RooFit.Binning(9,0.,9))
        ff2d=ROOT.TH2D("d2%s" % (ffpdf.GetName()),"d2%s" % (ffpdf.GetName()),len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
        fitpdf=self.rooPdf("fitPdfs_unrolled_template_mix_%s_2D_mb_%s" %(cat,cut))
        fit1d=fitpdf.createHistogram("pdf%s" %fitpdf.GetName(),observable, RooFit.Binning(9,0.,9))
        fit2d=ROOT.TH2D("d2%s" % (fitpdf.GetName()),"d2%s" % (fitpdf.GetName()),len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
        fitpdf.Print()
        dataset=self.rooData("reduced_data_2D_%s"%cat)
        entries=dataset.sumEntries()
        print entries
        data2d=ROOT.TH2D("d2%s" % (dataset.GetName()),"d2%s" % (dataset.GetName()),len(template_binning)-1,template_binning,len(template_binning)-1,template_binning)
        dataset.fillHistogram(data2d,ROOT.RooArgList(self.rooVar("templateNdim2Dim0"),self.rooVar("templateNdim2Dim1")))
        dataset=self.fill2d(data2d,template_binning)
        fit2d=self.fill2d(fit2d,template_binning,fit1d)
        fit2d.Scale(entries)
        pp2d=self.fill2d(pp2d,template_binning,pp1d)
        pf2d=self.fill2d(pf2d,template_binning,pf1d)
        ff2d=self.fill2d(ff2d,template_binning,ff1d)
        pp2d.Scale(entries*pu_pp)
        pf2d.Scale(entries*pu_pf)
        ff2d.Scale(entries*pu_ff)
        
        c1=ROOT.TCanvas("d2hist_%s" % cat,"2d hists per category") 
        data2d.Draw("COLZ") 
        
        cfitx=ROOT.TCanvas("cfitxproj_%s" % cat,"projection of the fit") 
        cfitx.Divide(1,2)
        cfitx.cd(1)
        ROOT.gPad.SetPad(0., 0.3, 1., 1.0)
        ROOT.gPad.SetLogy()
        cfitx.cd(2)
        ROOT.gPad.SetPad(0., 0.0, 1., 0.3)
        ROOT.gPad.SetGridy()
        cfitx.cd(1)
        # for dataMc plot MC as filled and data as points
        pt=ROOT.TPaveText(0.2,0.8,0.28,0.95,"nbNDC")
        pt.SetFillStyle(0)
        pt.SetLineColor(ROOT.kWhite)
        pt.AddText("%s" % cat)
        ROOT.gStyle.SetOptStat(0)
        data2dx=data2d.ProjectionX("%s_X" %dataset.GetName())
        style_utils.apply(data2dx,data_expectedStyle)
        fit2dx=fit2d.ProjectionX("%s_X" %fitpdf.GetName())
        style_utils.apply(fit2dx,fit_expectedStyle)
        pp2dx=pp2d.ProjectionX("%s_X" %pppdf.GetName())
        style_utils.apply(pp2dx,pdf_expectedStyle)
        pp2dx.SetLineColor(ROOT.kRed)
        pf2dx=pf2d.ProjectionX("%s_X" %pfpdf.GetName())
        style_utils.apply(pf2dx,pdf_expectedStyle)
        pf2dx.SetLineColor(ROOT.kCyan+2)
        ff2dx=ff2d.ProjectionX("%s_X" %ffpdf.GetName())
        style_utils.apply(ff2dx,pdf_expectedStyle)
        ff2dx.SetLineColor(ROOT.kBlack)
        
        data2dx.Draw()
        data2dx.GetXaxis().SetTitle("I_{Ch}(#gamma^{1}) (GeV)")
        data2dx.GetYaxis().SetTitle("Events / (GeV)")
        fit2dx.Draw("same")
        pp2dx.Draw("same")
        pf2dx.Draw("same")
        ff2dx.Draw("same")

        data2dx.GetXaxis().SetRangeUser(-0.1,15.)
      #  data2dx.GetXaxis().SetLimits(-2,15.)
        data2dx.GetYaxis().SetRangeUser(1e1,1e5)
     #   data2dx.GetXaxis().SetLabelSize( 1.1*data2dx.GetXaxis().GetLabelSize() )
      #  data2dx.GetXaxis().SetTitleSize( 0.75 *data2dx.GetXaxis().GetTitleSize() )
    #    data2dx.GetXaxis().SetTitleOffset( 1.02 )
        data2dx.GetXaxis().SetTitle("")
        data2dx.GetXaxis().SetLabelSize(0.)
        data2dx.GetYaxis().SetLabelSize( 1.5*data2dx.GetYaxis().GetLabelSize() * cfitx.GetWh() / ROOT.gPad.GetWh() )
        data2dx.GetYaxis().SetTitleSize(1.2*data2dx.GetYaxis().GetTitleSize() * cfitx.GetWh() / ROOT.gPad.GetWh() )
        data2dx.GetYaxis().SetTitleOffset(1.0 )
        leg.AddEntry(data2dx,"Data","pl")
        leg.AddEntry(fit2dx,"Fit","l")
        leg.AddEntry(pp2dx,"#gamma #gamma ","l")
        leg.AddEntry(pf2dx,"#gamma j ","l")
        leg.AddEntry(ff2dx,"j j ","l")
        leg.Draw()
        pt.Draw("same")
       

        residualx=ROOT.TGraphErrors(data2dx.GetNbinsX())
        for bn in range(1,data2dx.GetNbinsX()+1):
            residualP=(data2dx.GetBinContent(bn)-fit2dx.GetBinContent(bn))/data2dx.GetBinError(bn)
            mass=data2dx.GetXaxis().GetBinCenter(bn) 
            residualx.SetPoint(bn-1,mass,residualP)
            residualx.SetPointError(bn-1,(mass-data2dx.GetBinLowEdge(bn)),1.)
        cfitx.cd(2)
        style_utils.apply(residualx,ratio_expectedStyle)
        residualx.Draw("AP")        
        #residualx.GetYaxis().SetTitleSize( data2dx.GetYaxis().GetTitleSize() * 7.0/3.0 )
        residualx.GetYaxis().SetTitleSize( data2dx.GetYaxis().GetTitleSize() *5.5/3.0 )
        residualx.GetYaxis().SetTitleOffset(data2dx.GetYaxis().GetTitleOffset() *3.5/7.0)
        residualx.GetYaxis().SetLabelSize( data2dx.GetYaxis().GetLabelSize() *  7.0/3.0 )
       # residualx.GetXaxis().SetLabelSize(residualx.GetXaxis().GetLabelSize() )
      #  residualx.GetXaxis().SetTitleOffset(data2dx.GetXaxis().GetTitleOffset() *  3.0/7.0 )
        residualx.GetXaxis().SetTitleOffset(residualx.GetXaxis().GetTitleOffset() *  7.8/7.0 )
       # residualx.GetXaxis().SetLabelSize(data2dx.GetXaxis().GetLabelSize() *  7.0/3.0 )
        #residualx.GetYaxis().SetLabelSize( data2dx.GetYaxis().GetLabelSize() *  7.0/3.0 )
       # residualx.GetXaxis().SetTitleSize( data5dx.GetYaxis().GetTitleSize() * 7.0/3.0 )
        residualx.GetXaxis().SetTitleSize( data2dx.GetYaxis().GetTitleSize() * 7.0/3.0 )
        residualx.GetXaxis().SetLabelSize( residualx.GetYaxis().GetLabelSize()  )
        residualx.GetYaxis().SetNdivisions(505)
        residualx.GetYaxis().SetTitle("(Data-Fit)/#sigma_{stat}")
        residualx.GetXaxis().SetTitle("I_{Ch}(#gamma^{1}) (GeV)")
        ######residualx.GetXaxis().SetRangeUser(-5,15.)
        residualx.GetXaxis().SetLimits(-5,15.)
        residualx.GetYaxis().SetRangeUser(-2.,2.)
        cfitx.cd(1)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
       #B ROOT.gPad.SetTopMargin(0.1*margin)
        ROOT.gPad.SetBottomMargin(0.1*margin)

        cfitx.cd(2)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
        ROOT.gPad.SetBottomMargin(1.8*margin)
        ROOT.gPad.SetTopMargin(0.25*margin)
                
        
        cfity=ROOT.TCanvas("cfityproj_%s" % cat,"projection of the fit") 
        cfity.Divide(1,2)
        cfity.cd(1)
        ROOT.gPad.SetPad(0., 0.3, 1., 1.0)
        ROOT.gPad.SetLogy()
        cfity.cd(2)
        ROOT.gPad.SetPad(0., 0.0, 1., 0.3)
        ROOT.gPad.SetGridy()
        cfity.cd(1)
        data2dy=data2d.ProjectionY("%s_Y" %dataset.GetName())
        style_utils.apply(data2dy,data_expectedStyle)
        fit2dy=fit2d.ProjectionX("%s_Y" %fitpdf.GetName())
        style_utils.apply(fit2dy,fit_expectedStyle)
        pp2dy=pp2d.ProjectionY("%s_Y" %pppdf.GetName())
        style_utils.apply(pp2dy,pdf_expectedStyle)
        pp2dy.SetLineColor(ROOT.kRed)
        pf2dy=pf2d.ProjectionY("%s_Y" %pfpdf.GetName())
        style_utils.apply(pf2dy,pdf_expectedStyle)
        pf2dy.SetLineColor(ROOT.kCyan+2)
        ff2dy=ff2d.ProjectionX("%s_Y" %ffpdf.GetName())
        style_utils.apply(ff2dy,pdf_expectedStyle)
        ff2dy.SetLineColor(ROOT.kBlack)
        
        data2dy.Draw()
        data2dy.GetXaxis().SetRangeUser(-0.1,15.)
        data2dy.GetYaxis().SetRangeUser(1e1,1e5)
        data2dy.GetXaxis().SetTitle("")
        data2dy.GetXaxis().SetLabelSize(0.)
        data2dy.GetYaxis().SetLabelSize( 1.5*data2dy.GetYaxis().GetLabelSize() * cfity.GetWh() / ROOT.gPad.GetWh() )
        data2dy.GetYaxis().SetTitleSize(1.2*data2dy.GetYaxis().GetTitleSize() * cfity.GetWh() / ROOT.gPad.GetWh() )
        data2dy.GetYaxis().SetTitleOffset(1.0 )
        data2dy.GetYaxis().SetTitle("Events / (GeV)")
        fit2dy.Draw("same")
        pp2dy.Draw("same")
        pf2dy.Draw("same")
        ff2dy.Draw("same")
        leg.Draw()
        pt.Draw("same")
        residualy=ROOT.TGraphErrors(data2dy.GetNbinsX())
        print data2dy.GetNbinsX()
        for bn in range(1,data2dy.GetNbinsX()+1):
            residualP=(data2dy.GetBinContent(bn)-fit2dy.GetBinContent(bn))/data2dy.GetBinError(bn)
            mass=data2dy.GetXaxis().GetBinCenter(bn) 
            residualy.SetPoint(bn-1,mass,residualP)
            residualy.SetPointError(bn-1,(mass-data2dy.GetBinLowEdge(bn)),1.)
        cfity.cd(2)
        style_utils.apply(residualy,ratio_expectedStyle)
        residualy.Draw("AP")        
  #      residualy.GetYaxis().SetTitleSize( data2dy.GetYaxis().GetTitleSize() * 7.0/3.0 )
  #      residualy.GetYaxis().SetLabelSize( data2dy.GetYaxis().GetLabelSize() *  7.0/3.0 )
        residualy.GetYaxis().SetTitleSize( data2dy.GetYaxis().GetTitleSize() *5.5/3.0 )
        residualy.GetYaxis().SetTitleOffset(data2dy.GetYaxis().GetTitleOffset() *3.5/7.0)
        residualy.GetYaxis().SetLabelSize( data2dy.GetYaxis().GetLabelSize() *  7.0/3.0 )
        residualy.GetXaxis().SetTitleOffset(residualy.GetXaxis().GetTitleOffset() *  7.8/7.0 )
        #residualy.GetXaxis().SetTitleOffset(data2dy.GetXaxis().GetTitleOffset() *  5.5/7.0 )
        #residualy.GetXaxis().SetLabelSize(data2dy.GetXaxis().GetLabelSize() *  7.0/3.0 )
        #residualy.GetXaxis().SetTitleSize( data2dy.GetXaxis().GetTitleSize() * 7.0/3.0 )
        residualy.GetXaxis().SetTitleSize( data2dy.GetYaxis().GetTitleSize() * 7.0/3.0 )
        residualy.GetXaxis().SetLabelSize( residualy.GetYaxis().GetLabelSize()  )
        residualy.GetYaxis().SetNdivisions(505)
        residualy.GetYaxis().SetTitle("(Data-Fit)/#sigma_{stat}")
        residualy.GetXaxis().SetTitle("I_{Ch}(#gamma^{2}) (GeV)")
        #residualy.GetXaxis().SetRangeUser(-5,15.)
        residualy.GetXaxis().SetLimits(-5,15.)
        residualy.GetYaxis().SetRangeUser(-5.,2.)
        cfity.cd(1)
        margin =  ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
   #     ROOT.gPad.SetTopMargin(0.1*margin)
        ROOT.gPad.SetBottomMargin(0.1*margin)

        cfity.cd(2)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
        ROOT.gPad.SetBottomMargin(1.8*margin)
        ROOT.gPad.SetTopMargin(0.25*margin)
                
            
            
        ROOT.gStyle.SetOptStat(0)
        self.keep( [cfitx,c1,cfity] )
        self.format(cfitx,self.options.postproc)
        self.format(cfity,self.options.postproc)
        self.autosave(True)
            


    ## ------------------------------------------------------------------------------------------------------------
    def build3dTemplates(self,options,args):
        fout = self.openOut(options)
        self.format(cfitx,self.options.postproc)
        self.format(cfity,self.options.postproc)
        self.keep( [c1,cfitx,cfity] )
        self.autosave(True)
    
##############################---------------------------------------------------    

    def fill2d(self,temp2d,template_binning,temp1d=None):
        sum=0.
        bin=0
        binslist=[]
        #book bin list
        for b in range(1,len(template_binning)):
            for x in range(1,b+1):
                bin+=1
                binslist.append((x,b))
            for y in range (b-1,0,-1):
                bin+=1
                binslist.append((b,y))
        # fill bin list
        b=0
        for bin1, bin2 in binslist:
            b=b+1
            binErr=0.
            area=0.
            binCont=0.
            area=(temp2d.GetXaxis().GetBinWidth(bin1))*(temp2d.GetYaxis().GetBinWidth(bin2))
            sum+=1
            if temp1d:
                temp2d.SetBinContent(bin1,bin2,temp1d.GetBinContent(b)/area)
                temp2d.SetBinError(bin1,bin2,temp1d.GetBinError(b)/area)
            else:
                temp2d.SetBinContent(bin1,bin2,temp2d.GetBinContent(bin1,bin2)/area)
                temp2d.SetBinError(bin1,bin2,temp2d.GetBinError(bin1,bin2)/area)

         ##   temp2d.SetBinContent(bin1,bin2,temp1d.GetBinContent(b))
        ##    temp2d.SetBinError(bin1,bin2,temp1d.GetBinError(b))
        return temp2d 
    
    ## ---------------#--------------------------------------------------------------------------------------------
    def plotFit(self,roovar,rooaddpdf,roopdfs,data,components,cat,log,i=None):
        ROOT.TH1F.SetDefaultSumw2(True)
        if "mc" in data.GetName():
            cFit = ROOT.TCanvas("c%s_%u_%s_mc_%i" %(rooaddpdf.GetName(),len(components),log,i),"cFit")
        else:cFit = ROOT.TCanvas("c%s_%u_%s_%i" %(rooaddpdf.GetName(),len(components),log,i),"cFit")
        if not log: leg =ROOT.TLegend(0.7,0.5,0.88,0.9)
        else: leg =ROOT.TLegend(0.2,0.2,0.4,0.4)
        leg.SetFillColor(ROOT.kWhite)
        cFit.cd(1)
        if log:
            cFit.SetLogy()
        frame = roovar.frame(RooFit.Title("1d fit for category %s and %u components"% (cat,len(components))))
        data.plotOn(frame,RooFit.Name("data"))
    #    print "data has sigRegion ? ", data.get()[roovar.GetName()].hasRange("sigRegion")
    #    dataVar = data.get()[roovar.GetName()]
     #   dataVar.setRange("sigRegion",roovar.getBinning("sigRegion").lowBound(),roovar.getBinning("sigRegion").highBound())
    #     data.plotOn(frame,RooFit.Name("datasigRegion"),RooFit.Range("sigRegion"),RooFit.LineColor(ROOT.kCyan+1))
        rooaddpdf.plotOn(frame,RooFit.Name("fit"))
        rooaddpdf.plotOn(frame,RooFit.Components(roopdfs[0].GetName()),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kRed),RooFit.Name("pp"))
        rooaddpdf.plotOn(frame,RooFit.Components(roopdfs[1].GetName()),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kCyan+2),RooFit.Name("pf"))
        if len(components)>2:
            rooaddpdf.plotOn(frame,RooFit.Components(roopdfs[2].GetName()),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kBlack),RooFit.Name("ff"))
        frame.Draw()
        frame.GetXaxis().SetLabelSize( 1.1*frame.GetXaxis().GetLabelSize() )
        frame.GetXaxis().SetTitle("(I_{Ch}(#gamma^{1}),I_{Ch}(#gamma^{2})) bin")
        frame.GetYaxis().SetTitle("Events / bin")
        frame.GetXaxis().SetTitleSize( 0.75 *frame.GetXaxis().GetTitleSize() )
        frame.GetXaxis().SetTitleOffset( 1.02 )
        frame.GetYaxis().SetLabelSize( 1*frame.GetXaxis().GetLabelSize() * cFit.GetWh() / ROOT.gPad.GetWh() )
        frame.GetYaxis().SetTitleSize(1.2*frame.GetXaxis().GetTitleSize() * cFit.GetWh() / ROOT.gPad.GetWh() )
        frame.GetYaxis().SetTitleOffset(1.0 )
        
        leg.AddEntry("data","Data","pl")
        leg.AddEntry("fit","Fit","l")
        leg.AddEntry("pp","#gamma #gamma ","l")
        leg.AddEntry("pf","#gamma j ","l")
        if len(components)>2:
            leg.AddEntry("ff","j j ","l")
        leg.Draw()
        pt=ROOT.TPaveText(0.25,0.8,0.33,0.95,"nbNDC")
        pt.SetFillStyle(0)
        pt.SetLineColor(ROOT.kWhite)
        pt.AddText("%s" % cat)
        pt.Draw("same")
        self.format(cFit,self.options.postproc)
        self.keep([cFit])
        self.autosave(True)

    ## ------------------------------------------------------------------------------------------------------------
    ## ------------------------------------------------------------------------------------------------------------
    def plotPurity(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        
        comp=3
        treetruthname=options.plotPurity["treetruth"]
        dim=options.plotPurity["dimensions"]
        categories = options.plotPurity["categories"]
        closure = options.plot_closure
        if options.fit_mc:data=False
        else:data=True
        purity_values = options.plot_purityvalue
        for opt,pu_val in zip(closure,purity_values):
            for cat in categories:
                print cat
                tree_massbins=self.treeData("massbins_%s_%s"%(dim, cat))
                if data:
                    if options.pu_sigregion:
                        tree_template=self.treeData("fitresult_fraction_sigRegion_unrolled_%s_%s_%s"%(opt,dim, cat))
                        tree_templateRat=self.treeData("fitresult_fraction_ratio_of_uncertainties_forsigregion_unrolled_%s_%s_%s"%(opt,dim, cat))
                        if not options.no_mctruth:
                            tree_mctruth=self.treeData("fitresult_fraction_sigRegion_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                            tree_mctruthInt=self.treeData("fitresult_fraction_ratio_of_uncertainties_forsigregion_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                    else:
                        tree_template=self.treeData("fitresult_fraction_unrolled_%s_%s_%s"%(opt,dim, cat))
                        tree_mctruth=self.treeData("fitresult_fraction_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                    g_templatepp=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    g_templatepf=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    g_templateff=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    g_ratiopp=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    g_syspp=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    g_syspf=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    g_sysff=ROOT.TGraphAsymmErrors(tree_template.GetEntries())
                    nentries=tree_template.GetEntries()
                else:
                    if options.pu_sigregion:
                        tree_templatemc=self.treeData("fitresult_fraction_sigRegion_mc_unrolled_%s_%s_%s"%(opt,dim, cat))
                        tree_templatemcInt=self.treeData("fitresult_fraction_ratio_of_uncertainties_forsigregion_mc_unrolled_%s_%s_%s"%(opt,dim, cat))
                        tree_mctruth=self.treeData("fitresult_fraction_sigRegion_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                        tree_mctruthInt=self.treeData("fitresult_fraction_ratio_of_uncertainties_forsigregion_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                    
                    else:
                        tree_templatemc=self.treeData("fitresult_fraction_mc_unrolled_%s_%s_%s"%(opt,dim, cat))
                        tree_mctruth=self.treeData("fitresult_fraction_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                    g_templateppmc=ROOT.TGraphAsymmErrors(tree_templatemc.GetEntries())
                    g_templatepfmc=ROOT.TGraphAsymmErrors(tree_templatemc.GetEntries())
                    g_templateffmc=ROOT.TGraphAsymmErrors(tree_templatemc.GetEntries())
                    nentries=tree_templatemc.GetEntries()
                    #for MCtruth one can take either the counted truth entries or the fit, here we are using the counted ones
                if options.pu_sigregion:
                        treetruthSigname="truth_fraction_signalregion"
                        tree_truthpp=self.treeData("%s_pp_%s_%s"%(treetruthSigname, dim, cat))
                        tree_truthpf=self.treeData("%s_pf_%s_%s"%(treetruthSigname,dim, cat))
                        tree_truthff=self.treeData("%s_ff_%s_%s"%(treetruthSigname,dim, cat))
                else:
                    tree_truthpp=self.treeData("%s_pp_%s_%s"%(treetruthname, dim, cat))
                    tree_truthpf=self.treeData("%s_pf_%s_%s"%(treetruthname,dim, cat))
                    tree_truthff=self.treeData("%s_ff_%s_%s"%(treetruthname,dim, cat))
                if tree_truthff!=None:
                    g_truthff=ROOT.TGraphErrors(tree_truthff.GetEntries())
                else:
                    g_truthff=ROOT.TGraphErrors()
                    print "no truth ff component"
                g_truthpp=ROOT.TGraphErrors(tree_truthpp.GetEntries())
                g_truthpf=ROOT.TGraphErrors(tree_truthpf.GetEntries())
                if not options.no_mctruth:
                    g_mctruthpp=ROOT.TGraphAsymmErrors(tree_mctruth.GetEntries())
                    g_mctruthpf=ROOT.TGraphAsymmErrors(tree_mctruth.GetEntries())
                    g_mctruthff=ROOT.TGraphAsymmErrors(tree_mctruth.GetEntries())
                if not data:
                    g_pullpp=ROOT.TGraphAsymmErrors(nentries)
                    g_cicpullpp=ROOT.TGraphAsymmErrors(nentries)
                    g_mctruthpullpp=ROOT.TGraphAsymmErrors(nentries)
                    h_pullpp=ROOT.TH1F("h_pullpp_%s" % cat,"h_pullpp_%s"% cat,10*tree_mctruth.GetEntries(),-2.,2.)
            #        if ((tree_truthpp.GetEntries()!=nentries)):
            #            print "number of entries in trees dont agree"
                if options.full_error:tot_err=True
                else: tot_err=False
                if data and tot_err:
                    if options.blind:
                        if cat=="EBEB":JK = array.array('d',options.plotPurity.get("JK_EBEB_blind"))
                        elif cat=="EBEE":JK = array.array('d',options.plotPurity.get("JK_EBEE_blind"))
                    else:
                        if cat=="EBEB":JK = array.array('d',options.plotPurity.get("JK_EBEB"))
                        elif cat=="EBEE":JK = array.array('d',options.plotPurity.get("JK_EBEE"))
                    if (len(JK)!= nentries):print "error JK uncertainty has not the same number of entries as mass bins"
                for mb in range(0,nentries):
                    if mb==(nentries-1):
                        if options.blind:
                            massbin=(options.plotPurity.get("blindingpoint")+options.plotPurity.get("upperend_lastbin"))/2.
                            masserror=(options.plotPurity.get("upperend_lastbin")-options.plotPurity.get("blindingpoint"))/2.
                        else:
                            massbin=(options.plotPurity.get("lowerend_lastbin")+options.plotPurity.get("upperend_lastbin"))/2.
                            masserror=(options.plotPurity.get("upperend_lastbin")-options.plotPurity.get("lowerend_lastbin"))/2.
                    else:
                        tree_massbins.GetEntry(mb)
                        massbin=tree_massbins.massbin
                        masserror=tree_massbins.masserror
                    if not options.no_mctruth:
                        tree_mctruth.GetEntry(mb)
                    if data:
                        tree_template.GetEntry(mb)
                        pf_p=tree_template.purity_pf
                        pp_p=tree_template.purity_pp
                        ff_p=tree_template.purity_ff
                        if not tot_err:
                            pp_errlow=tree_template.err_pplow
                            pp_errhigh=tree_template.err_pphigh
                            pf_errlow=tree_template.err_pflow
                            pf_errhigh=tree_template.err_pfhigh
                            ff_errlow=tree_template.err_fflow
                            ff_errhigh=tree_template.err_ffhigh
                        elif tot_err and cat=="EBEB":
                        #this error is the percentage and has thus to be multiplied by the purity
                            sys=options.plotPurity.get("syserrorEBEB")
                        elif tot_err and cat=="EBEE":
                            sys=options.plotPurity.get("syserrorEBEE")
                        if tot_err:
                            if not options.pu_sigregion:
                                stat_pplow=sqrt(JK[mb]**2+tree_template.err_pplow**2)
                                stat_pphigh=sqrt(JK[mb]**2+tree_template.err_pphigh**2)
                                pp_sys=sys**2*pp_p**2
                                pp_errlow=sqrt(pp_sys+stat_pplow**2)
                                pp_errhigh=sqrt(pp_sys+stat_pphigh**2)
                                stat_pflow=sqrt(JK[mb]**2+tree_template.err_pflow**2)
                                stat_pfhigh=sqrt(JK[mb]**2+tree_template.err_pfhigh**2)
                                pf_sys=sys**2*pf_p**2
                                pf_errlow=sqrt(pf_sys+stat_pflow**2)
                                pf_errhigh=sqrt(pf_sys+stat_pfhigh**2)
                                stat_fflow=sqrt(JK[mb]**2+tree_template.err_fflow**2)
                                stat_ffhigh=sqrt(JK[mb]**2+tree_template.err_ffhigh**2)
                                ff_sys=sys**2*ff_p**2
                                ff_errlow=sqrt(ff_sys+stat_fflow**2)
                                ff_errhigh=sqrt(ff_sys+stat_ffhigh**2)
                                pp_syslow=pp_sys
                                pp_syshigh=pp_sys
                                pf_syslow=pf_sys
                                pf_syshigh=pf_sys
                                ff_syslow=ff_sys
                                ff_syshigh=ff_sys
                            #    print "[INFO] fullregion for pp component:  purity pp %.2f"% pp_p," JK (absolute) %.3f"% JK[mb], "stat error from fit: low %.3f"% tree_template.err_pplow, "high %3.f" %tree_template.err_pphigh,"final stat error low %.3f" % stat_pplow, "high %.3f"%stat_pphigh ,"sys error*purity_pp %.3f" % sqrt(pp_sys),"total error low %.3f"%pp_errlow, "high %.3f" %pp_errhigh
                            else:
                                tree_templateRat.GetEntry(mb)
                                stat_pplow=sqrt(JK[mb]**2*tree_templateRat.ratSig_pplow**2+tree_template.err_pplow**2)
                                stat_pphigh=sqrt(JK[mb]**2*tree_templateRat.ratSig_pplow**2+tree_template.err_pphigh**2)
                                pp_syslow=sys**2*tree_templateRat.ratSig_pplow**2*pp_p**2 
                                pp_syshigh=sys**2*tree_templateRat.ratSig_pphigh**2*pp_p**2 
                                stat_pflow=sqrt(JK[mb]**2*tree_templateRat.ratSig_pflow**2+tree_template.err_pflow**2)
                                stat_pfhigh=sqrt(JK[mb]**2*tree_templateRat.ratSig_pfhigh**2+tree_template.err_pfhigh**2)
                                pf_syslow=sys**2*tree_templateRat.ratSig_pflow**2*pf_p**2 
                                pf_syshigh=sys**2*tree_templateRat.ratSig_pfhigh**2*pf_p**2 
                                stat_fflow=sqrt(JK[mb]**2*tree_templateRat.ratSig_fflow**2+tree_template.err_fflow**2)
                                stat_ffhigh=sqrt(JK[mb]**2*tree_templateRat.ratSig_ffhigh**2+tree_template.err_ffhigh**2)
                                ff_syslow=sys**2*tree_templateRat.ratSig_fflow**2*ff_p**2 
                                ff_syshigh=sys**2*tree_templateRat.ratSig_ffhigh**2*ff_p**2 
                                
                                pp_errlow=sqrt(pp_syslow+stat_pplow**2)
                                pf_errlow=sqrt(pf_syslow+stat_pflow**2)
                                ff_errlow=sqrt(ff_syslow+stat_fflow**2)
                                pp_errhigh=sqrt(pp_syshigh+stat_pphigh**2)
                                pf_errhigh=sqrt(pf_syshigh+stat_pfhigh**2)
                                ff_errhigh=sqrt(ff_syshigh+stat_ffhigh**2)

                            #    print "[INFO] sigregion for pp component: "," purity pp %.2f"%pp_p," JK (absolute for fullregion) %.3f"%JK[mb], "stat error from fit: low %.3f"%tree_template.err_pplow, "high %.3f"% tree_template.err_pphigh,"final stat error low %.3f" % stat_pplow, "high %.3f"%stat_pphigh ,"sys error*purity_pp low %.3f"% sqrt(pp_syslow),"high %.3f"%sqrt(pp_syshigh),"total error low %.3f"% pp_errlow, "high % .3f"%pp_errhigh
                           ##print outs for auto_mass_plot.sh
                         #   print "[",pp_p,",-1],"
                            print "[",(-pp_errlow+pp_errhigh+pp_p) ,"," , pp_errhigh  ,"],"
                          #  print "[",(-pp_errlow+pp_errhigh+pp_p) ,",",  pp_errlow  ,"],"
                            g_syspf.SetPoint(mb,massbin,pf_p)
                            g_syspp.SetPoint(mb,massbin,pp_p)
                            g_sysff.SetPoint(mb,massbin,ff_p)
                            g_syspf.SetPointError(mb,masserror,masserror,sqrt(pf_syslow),sqrt(pf_syshigh))
                            if pp_p+sqrt(pp_syshigh)>1:
                                new_error=1-pp_p
                                g_syspp.SetPointError(mb,masserror,masserror,sqrt(pp_syslow),new_error)
                            else:
                                g_syspp.SetPointError(mb,masserror,masserror,sqrt(pp_syslow),sqrt(pp_syshigh))
                            g_sysff.SetPointError(mb,masserror,masserror, sqrt(ff_syslow),sqrt(ff_syshigh))
                        g_templatepf.SetPoint(mb,massbin,pf_p)
                        g_templatepf.SetPointError(mb,masserror,masserror,pf_errlow,pf_errhigh)
                        g_templatepp.SetPoint(mb,massbin,pp_p)
                        if (pp_p+pp_errhigh>1):
                            new_error=1-pp_p
                            g_templatepp.SetPointError(mb,masserror,masserror,pp_errlow,new_error)
                        else:
                            g_templatepp.SetPointError(mb,masserror,masserror,pp_errlow,pp_errhigh)
                        g_templateff.SetPoint(mb,massbin,ff_p)
                        g_templateff.SetPointError(mb,masserror,masserror,ff_errlow,ff_errhigh)
                    else:
                        tree_templatemc.GetEntry(mb)
                        g_templatepfmc.SetPoint(mb,massbin,tree_templatemc.purity_pf)
                        g_templatepfmc.SetPointError(mb,masserror,masserror,tree_templatemc.err_pflow, tree_templatemc.err_pfhigh)
                        g_templateffmc.SetPoint(mb,massbin,tree_templatemc.purity_ff)
                        g_templateffmc.SetPointError(mb,masserror,masserror,tree_templatemc.err_fflow,tree_templatemc.err_ffhigh)
                        g_templateppmc.SetPoint(mb,massbin,tree_templatemc.purity_pp)
                        if( tree_templatemc.purity_pp+tree_templatemc.err_pphigh)>1:
                            new_error=1-tree_templatemc.purity_pp
                            g_templateppmc.SetPointError(mb,masserror,masserror,tree_templatemc.err_pplow,new_error)
                        else:
                            g_templateppmc.SetPointError(mb,masserror,masserror,tree_templatemc.err_pplow,tree_templatemc.err_pphigh)
                    if not options.no_mctruth:
                        g_mctruthpp.SetPoint(mb,massbin,tree_mctruth.purity_pp)
                        if (tree_mctruth.purity_pp+tree_mctruth.err_pphigh)>1:
                            new_error=1-tree_mctruth.purity_pp
                            g_mctruthpp.SetPointError(mb,masserror,masserror,tree_mctruth.err_pplow,new_error)
                        else:
                            g_mctruthpp.SetPointError(mb,masserror,masserror,tree_mctruth.err_pplow,tree_mctruth.err_pphigh)
                        tree_truthpp.GetEntry(mb)
                        tree_truthpf.GetEntry(mb)
                        if tree_truthff!=None:
                            tree_truthff.GetEntry(mb)
                        g_truthpp.SetPoint(mb,massbin,tree_truthpp.frac_pu)
                        g_truthpp.SetPointError(mb,masserror,0.)
                        g_truthpf.SetPoint(mb,massbin,tree_truthpf.frac_pu)
                        g_truthff.SetPoint(mb,massbin,tree_truthff.frac_pu)
                        g_truthpf.SetPointError(mb,masserror,0.)
                        g_truthff.SetPointError(mb,masserror,0.)
                        tree_mctruth.GetEntry(mb)
                        if data:
                  #      g_ratiopp.SetPoint(mb,massbin,(pp_p-tree_truthpp.frac_pu)/pp_err)
                            g_ratiopp.SetPoint(mb,massbin,(pp_p-tree_mctruth.purity_pp)/(sqrt(pp_errlow**2+pp_errhigh**2)))
                            g_ratiopp.SetPointError(mb,0.,0.,pp_errlow,pp_errhigh)
                        if not data:
                            pullpp=(tree_templatemc.purity_pp-tree_mctruth.purity_pp)/sqrt(tree_templatemc.err_pplow**2+tree_templatemc.err_pphigh**2)
                            mctruthpullpp=(tree_truthpp.frac_pu-tree_mctruth.purity_pp)/sqrt(tree_mctruth.err_pplow**2+tree_mctruth.err_pphigh**2)
                            cicpullpp=(tree_templatemc.purity_pp-tree_truthpp.frac_pu)/sqrt(tree_templatemc.err_pplow**2+tree_templatemc.err_pphigh**2)
                            g_pullpp.SetPoint(mb,massbin,pullpp)
                            g_cicpullpp.SetPoint(mb,massbin,cicpullpp)
                            g_mctruthpullpp.SetPoint(mb,massbin,mctruthpullpp)
                            h_pullpp.Fill(pullpp)
                        g_mctruthpf.SetPoint(mb,massbin,tree_mctruth.purity_pf)
                        g_mctruthff.SetPoint(mb,massbin,tree_mctruth.purity_ff)
                        g_mctruthpf.SetPointError(mb,masserror,masserror,tree_mctruth.err_pflow,tree_mctruth.err_pfhigh)
                        g_mctruthff.SetPointError(mb,masserror,masserror,tree_mctruth.err_fflow,tree_mctruth.err_ffhigh)
 ##                if not data:
 ##                    if options.pu_sigregion:  self.plotClosure(cat,pu_val,opt,"sigRegion_MC_MCtruthtemp",g_templateppmc,g_templatepfmc,g_templateffmc,g_pullpp,g_mctruthpp,g_mctruthpf,g_mctruthff)
 ##                    else: self.plotClosure(cat,pu_val,opt,"fullRegion_MC_MCtruthtemp",g_templateppmc,g_templatepfmc,g_templateffmc,g_pullpp,g_mctruthpp,g_mctruthpf,g_mctruthff)
 ##                    if options.pu_sigregion:  self.plotClosure(cat,pu_val,opt,"sigRegion_MC_MCtruthcic",g_templateppmc,g_templatepfmc,g_templateffmc,g_cicpullpp,g_truthpp,g_truthpf,g_truthff)
 ##                    else: self.plotClosure(cat,pu_val,opt,"fullRegion_MC_MCtruthcic",g_templateppmc,g_templatepfmc,g_templateffmc,g_cicpullpp,g_truthpp,g_truthpf,g_truthff)
 ##                    if options.pu_sigregion:  self.plotClosure(cat,pu_val,opt,"sigRegion_MCtruth_closure",g_truthpp,g_truthpf,g_truthff,g_mctruthpullpp,g_mctruthpp,g_mctruthpf,g_mctruthff)
 ##                    else: self.plotClosure(cat,pu_val,opt,"fullRegion_MCtruth_closure",g_truthpp,g_truthpf,g_truthff,g_mctruthpullpp,g_mctruthpp,g_mctruthpf,g_mctruthff)
 ##                else:
 ##                    if options.pu_sigregion:
 ##                        self.plotPurityMassbins(cat,pu_val,opt,"sigRegion_data_syserror",g_templatepp,g_templatepf,g_templateff,g_syspp,g_syspf,g_sysff)
 ##                        if not options.no_mctruth:
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"sigRegion_data_MCtruthtemp_nosyserror",g_templatepp,g_templatepf,g_templateff,g_mctruthpp=g_mctruthpp,g_mctruthpf=g_mctruthpf,g_mctruthff=g_mctruthff,g_ratiopp=g_ratiopp)
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"sigRegion_data_MCtruthtemp_syserror",g_templatepp,g_templatepf,g_templateff,g_syspp,g_syspf,g_sysff,g_mctruthpp,g_mctruthpf,g_mctruthff,g_ratiopp)
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"sigRegion_data_MCtruthcic_nosyserror",g_templatepp,g_templatepf,g_templateff,g_mctruthpp=g_truthpp,g_mctruthpf=g_truthpf,g_mctruthff=g_truthff,g_ratiopp=g_ratiopp)
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"sigRegion_data_MCtruthcic_syserror",g_templatepp,g_templatepf,g_templateff,g_syspp,g_syspf,g_sysff,g_truthpp,g_truthpf,g_truthff,g_ratiopp)
 ##
 ##                    else: 
 ##                        self.plotPurityMassbins(cat,pu_val,opt,"data_syserror",g_templatepp,g_templatepf,g_templateff,g_syspp,g_syspf,g_sysff)
 ##                        if not options.no_mctruth:
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"data_MCtruthtemp_nosyserror",g_templatepp,g_templatepf,g_templateff,g_mctruthpp=g_mctruthpp,g_mctruthpf=g_mctruthpf,g_mctruthff=g_mctruthff,g_ratiopp=g_ratiopp)
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"data_MCtruthtemp_syserror",g_templatepp,g_templatepf,g_templateff,g_syspp,g_syspf,g_sysff,g_mctruthpp,g_mctruthpf,g_mctruthff,g_ratiopp)
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"data_MCtruthcic_nosyserror",g_templatepp,g_templatepf,g_templateff,g_mctruthpp=g_truthpp,g_mctruthpf=g_truthpf,g_mctruthff=g_truthff,g_ratiopp=g_ratiopp)
 ##                            self.plotPurityMassbins(cat,pu_val,opt,"data_MCtruthcic_syserror",g_templatepp,g_templatepf,g_templateff,g_syspp,g_syspf,g_sysff,g_truthpp,g_truthpf,g_truthff,g_ratiopp)
        self.saveWs(options,fout)
            ## ------------------------------------------------------------------------------------------------------------
    def pullFunction(self,g_pull,h_pull,cat,comp,opt,pu_val):
        leg = ROOT.TLegend(0.5,0.8,0.9,0.9)
        print "cpull_%s_%s" % (comp,cat)
        cpull = ROOT.TCanvas("cpull_for%s_%s_%s_%s" % (opt,comp,cat,pu_val),"cpull_for%s_%s_%s_%s" % (opt,comp,cat,pu_val))
        cpull.Divide(1,2)
        cpull.cd(1)
        ROOT.gPad.SetPad(0., 0.5, 1., 1.0)
        ROOT.gStyle.SetOptFit(1)
        cpull.cd(2)
        ROOT.gPad.SetPad(0.,  0., 1., 0.5)
        #ROOT.gPad.SetGridx()
        #ROOT.gPad.SetGridy()
        ROOT.gPad.SetLogx()
        cpull.cd(1)
        fitgauss=ROOT.TF1("fitgauss","gaus",-5.,5.)
        h_pull.GetXaxis().SetTitle("(pu_tp-pu_mctruth)/pu_tperr")
        h_pull.Fit("fitgauss","L ");
        h_pull.Draw("HIST") 
        fitgauss.Draw("SAME")
        cpull.cd(2)
        g_pull.SetMarkerStyle(20)
        g_pull.GetYaxis().SetRangeUser(-5.,5.)
        g_pull.GetXaxis().SetRangeUser(0.,13000.)
        g_pull.GetXaxis().SetTitle("Diphoton mass [GeV]")
        g_pull.GetYaxis().SetTitle("(pu_tp-pu_mctruth)/pu_tperr")
        g_pull.Draw("AP")
        self.keep( [cpull] )
        self.autosave(True)
    ## ------------------------------------------------------------------------------------------------------------
    def addCmsLumi(canv,period,pos,extraText=None):
        if extraText:
                ROOT.writeExtraText = True
                if type(extraText) == str and extraText != "":
                        ROOT.extraText = extraText
                ROOT.CMS_lumi(canv,period,pos)

    ## ------------------------------------------------------------------------------------------------------------
    def plotClosure(self,cat,pu_val,opt,name,g_templatepp=None,g_templatepf=None,g_templateff=None,g_ratiopp=None,g_mctruthpp=None,g_mctruthpf=None,g_mctruthff=None):
        leg = ROOT.TLegend(0.4,0.7,0.8,0.9)
        leg.SetNColumns(2)
        basicStyle = [["SetMarkerSize",1.3],["SetLineWidth",2],["SetLineStyle",1]]
        mc_expectedStyle = basicStyle+ [["SetMarkerStyle",ROOT.kFullTriangleUp],["SetTitle",";m_{#gamma #gamma} (GeV);Fraction"]]
        ratio_expectedStyle =  [["SetMarkerStyle",ROOT.kFullTriangleUp]]
        mctruth_expectedStyle = basicStyle+ [["SetMarkerStyle",ROOT.kOpenCircle],["SetLineStyle",ROOT.kDashed],["SetTitle",";m_{#gamma #gamma} (GeV);Fraction"]]
        cpu = ROOT.TCanvas("cpu_%s_%s_%s_%s" % (opt,cat,pu_val,name),"cpu_%s_%s_%s_%s" %(opt,cat,pu_val,name),1400,1000)
        cpu.Divide(1,2)
        cpu.cd(1)
        ROOT.gPad.SetPad(0., 0.3, 1., 1.0)
        ROOT.gPad.SetLogx()
       # ROOT.gPad.SetGridx()
        #ROOT.gPad.SetTicky()
       # ROOT.gPad.SetGridy()
        cpu.cd(2)
        ROOT.gPad.SetPad(0., 0., 1., 0.3)
       # ROOT.gPad.SetTicky()
       # ROOT.gPad.SetGridx()
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetLogx()
        cpu.cd(1)
        g_templatepp.GetYaxis().SetLabelSize( g_templatepp.GetYaxis().GetLabelSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
        style_utils.apply(g_templatepp, [["colors",ROOT.kRed]]+mc_expectedStyle)
        style_utils.apply(g_mctruthpp, [["colors",ROOT.kRed]]+mctruth_expectedStyle )
        style_utils.apply(g_templatepf, [["colors",ROOT.kBlue]]+mc_expectedStyle )
        style_utils.apply(g_mctruthpf, [["colors",ROOT.kBlue]]+mctruth_expectedStyle )
        if g_templateff:style_utils.apply(g_templateff, [["colors",ROOT.kBlack]]+mc_expectedStyle )
        if g_mctruthff:style_utils.apply(g_mctruthff, [["colors",ROOT.kBlack]]+mctruth_expectedStyle )
        g_templatepp.GetXaxis().SetLabelSize( 1.05*g_templatepp.GetXaxis().GetLabelSize() )
        g_templatepp.GetXaxis().SetTitleSize( 1. *g_templatepp.GetXaxis().GetTitleSize() )
        g_templatepp.GetXaxis().SetTitleOffset( 0.8 )
        g_templatepp.GetYaxis().SetLabelSize( g_templatepp.GetXaxis().GetLabelSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
        g_templatepp.GetYaxis().SetTitleSize(1* g_templatepp.GetXaxis().GetTitleSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
        g_templatepp.GetYaxis().SetTitleOffset( 0.8 )
        g_templatepp.GetYaxis().SetRangeUser(0.,1.5)
        g_templatepp.GetXaxis().SetMoreLogLabels()
        g_templatepp.GetYaxis().SetNdivisions(505)
        if cat=="EBEB":g_templatepp.GetXaxis().SetLimits(200.,1600.)
        if cat=="EBEE":g_templatepp.GetXaxis().SetLimits(300.,1600.)
        g_templatepp.Draw("AP")
        g_templatepf.Draw("P SAME")
        if g_templateff:g_templateff.Draw("P SAME")
        g_mctruthpf.Draw("P SAME")
        g_mctruthpp.Draw("P SAME")
        if g_mctruthff:g_mctruthff.Draw("P SAME")
        
        if "closure" in name:
            leg.AddEntry(g_templatepp,"#gamma #gamma  MC truth count","lp")  
            leg.AddEntry(g_templatepf,"#gamma j  MC truth count","lp")
            if g_templateff:leg.AddEntry(g_templateff,"j j  MC truth count","lp")
        else:
            leg.AddEntry(g_templatepp,"#gamma #gamma  MC","lp")  
            leg.AddEntry(g_templatepf,"#gamma j  MC","lp")
            if g_templateff:leg.AddEntry(g_templateff,"j j  MC","lp")
        if "MCcic" in name:
            leg.AddEntry(g_mctruthpp,"#gamma #gamma  MC truth count","lp")  
            leg.AddEntry(g_mctruthpf,"#gamma j  MC truth count","lp")
            if g_mctruthff:leg.AddEntry(g_mctruthff,"j j  MC truth count","lp")
        else:
            leg.AddEntry(g_mctruthpp,"#gamma #gamma MC truth","lp")  
            leg.AddEntry(g_mctruthpf,"#gamma j MC truth","lp")
            if g_mctruthff:leg.AddEntry(g_mctruthff,"j j MC truth","lp")

        leg.Draw()
        g_ratiopp.SetMarkerStyle(20)
        cpu.cd(2)
        style_utils.apply(g_ratiopp, [["colors",ROOT.kRed]]+ratio_expectedStyle )
        if "closure" in name: g_ratiopp.GetYaxis().SetTitle("(MC-MC_{tr})/#sigma_{MC}")
        else: g_ratiopp.GetYaxis().SetTitle("(MC-MC_{tr})/#sigma_{MC}")
        g_ratiopp.GetYaxis().SetRangeUser(-1.3,1.3)
        g_ratiopp.GetYaxis().SetTitleSize( g_templatepp.GetYaxis().GetTitleSize() *6./3. )
        g_ratiopp.GetYaxis().SetLabelSize( g_templatepp.GetYaxis().GetLabelSize()*7./3.  )
        g_ratiopp.GetXaxis().SetTitleSize(  g_templatepp.GetXaxis().GetTitleSize() * 7/3. )
        g_ratiopp.GetYaxis().SetTitleOffset(g_templatepp.GetYaxis().GetTitleOffset()*3./7. )
        g_ratiopp.GetXaxis().SetTitleOffset(g_templatepp.GetXaxis().GetTitleOffset() )
        g_ratiopp.GetXaxis().SetLabelSize( g_templatepp.GetXaxis().GetLabelSize()*6./3. )
        g_ratiopp.GetXaxis().SetLimits(200.,5000.)
        g_ratiopp.GetXaxis().SetMoreLogLabels()
     #   g_ratiopp.Draw("A")
        g_ratiopp.Draw("AP")
        if cat=="EBEB":
            g_ratiopp.GetXaxis().SetLimits(200.,1600.)
        if cat=="EBEE":
            g_ratiopp.GetXaxis().SetLimits(300.,1600.)
        self.keep( [g_mctruthpp,g_ratiopp] )
        self.keep( [g_mctruthpp,g_mctruthpf] )
        if g_mctruthff:self.keep( [g_mctruthff] )
        self.keep( [cpu,g_templatepp,g_templatepf] )
        if g_templateff:self.keep( [g_templateff] )
        self.format(cpu,self.options.postproc)
        self.autosave(True)

    ## ------------------------------------------------------------------------------------------------------------
    def plotPurityMassbins(self,cat,pu_val,opt,name,g_templatepp=None,g_templatepf=None,g_templateff=None,g_syspp=None,g_syspf=None,g_sysff=None,g_mctruthpp=None,g_mctruthpf=None,g_mctruthff=None,g_ratiopp=None):
        basicStyle = [["SetMarkerSize",1.3],["SetLineWidth",4]]
        data_expectedStyle = basicStyle+ [["SetMarkerStyle",ROOT.kFullTriangleUp],["SetLineStyle",1],["SetTitle",";#it{m}_{#gamma#gamma} (GeV);Fraction"]]
        ratio_expectedStyle = [["SetMarkerStyle",ROOT.kFullTriangleUp]]
        mctruth_expectedStyle = basicStyle+ [["SetMarkerStyle",ROOT.kOpenCircle],["SetLineStyle",ROOT.kDashed],["SetTitle",";m_{#gamma#gamma} (GeV);Fraction"]]
        if g_mctruthpp:
            leg = ROOT.TLegend(0.4,0.7,0.8,0.9)
            cpu = ROOT.TCanvas("cpu_%s_%s_%s_%s" % (opt,cat,pu_val,name),"cpu_%s_%s_%s_%s" %(opt,cat,pu_val,name),1400,1000)
        else: 
            leg = ROOT.TLegend(0.7,0.7,0.8,0.9)
            #cpu = ROOT.TCanvas("cpu_%s_%s_%s_%s" % (opt,cat,pu_val,name),"cpu_%s_%s_%s_%s" %(opt,cat,pu_val,name),1400,700)
            cpu = ROOT.TCanvas("cpu_%s_%s_%s_%s" % (opt,cat,pu_val,name),"cpu_%s_%s_%s_%s" %(opt,cat,pu_val,name))
        if g_mctruthpp:
                leg.SetNColumns(2)
                cpu.Divide(1,2)
                cpu.cd(1)
                ROOT.gPad.SetPad(0., 0.3, 1., 1.0)
                cpu.cd(2)
                ROOT.gPad.SetPad(0., 0., 1., 0.3)
             #   ROOT.gPad.SetTicky()
             #   ROOT.gPad.SetGridx()
                ROOT.gPad.SetGridy()
                ROOT.gPad.SetLogx()
        cpu.cd(1)
     #   ROOT.gPad.SetTicky()
     #   ROOT.gPad.SetGridx()
    #    ROOT.gPad.SetGridy()
    ##    ROOT.gPad.SetLogx()
        
        if not g_mctruthpp:
                g_templatepp.GetXaxis().SetLabelSize( 0.95*g_templatepp.GetXaxis().GetLabelSize() )
                g_templatepp.GetXaxis().SetTitleSize( 0.9 *g_templatepp.GetXaxis().GetTitleSize() )
                g_templatepp.GetXaxis().SetTitleOffset( 0.8 )
                g_templatepp.GetYaxis().SetLabelSize( 0.95*g_templatepp.GetXaxis().GetLabelSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
                g_templatepp.GetYaxis().SetTitleSize(1* g_templatepp.GetXaxis().GetTitleSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
                g_templatepp.GetYaxis().SetTitleOffset(1.0 )
                g_templatepp.GetYaxis().SetRangeUser(0.,1.4)
        else:
                g_templatepp.GetXaxis().SetLabelSize( 1.05*g_templatepp.GetXaxis().GetLabelSize() )
                g_templatepp.GetXaxis().SetTitleSize( 1. *g_templatepp.GetXaxis().GetTitleSize() )
                g_templatepp.GetXaxis().SetTitleOffset( 0.8 )
                g_templatepp.GetYaxis().SetLabelSize( g_templatepp.GetXaxis().GetLabelSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
                g_templatepp.GetYaxis().SetTitleSize(1* g_templatepp.GetXaxis().GetTitleSize() * cpu.GetWh() / ROOT.gPad.GetWh() )
                g_templatepp.GetYaxis().SetTitleOffset( 0.8 )
                g_templatepp.GetYaxis().SetRangeUser(0.,1.5)
        g_templatepp.GetXaxis().SetMoreLogLabels()
        if cat=="EBEB":
            g_templatepp.GetXaxis().SetLimits(200.,1600.)
        if cat=="EBEE":
            g_templatepp.GetXaxis().SetLimits(300.,1600.)
        g_templatepp.GetYaxis().SetNdivisions(505)
        style_utils.apply(g_templatepp, [["colors",ROOT.kRed]]+data_expectedStyle)
        style_utils.apply(g_templatepf, [["colors",ROOT.kBlue]]+data_expectedStyle )
        style_utils.apply(g_templateff, [["colors",ROOT.kBlack]]+data_expectedStyle )
        if g_mctruthpp:
                style_utils.apply(g_mctruthpp, [["colors",ROOT.kRed+2]]+mctruth_expectedStyle)
                style_utils.apply(g_mctruthpf, [["colors",ROOT.kBlue+2]]+mctruth_expectedStyle )
                style_utils.apply(g_mctruthff, [["colors",ROOT.kBlack]]+mctruth_expectedStyle )
        if g_syspp:
            style_utils.apply(g_syspp, [["SetFillStyle",3002],["colors",ROOT.kRed]]+data_expectedStyle )
            style_utils.apply(g_syspf, [["SetFillStyle",3002],["colors",ROOT.kBlue]]+data_expectedStyle )
            style_utils.apply(g_sysff, [["SetFillStyle",3002],["colors",ROOT.kBlack]]+data_expectedStyle )
        g_templatepp.Draw("AP")
        g_templatepf.Draw("P SAME")
        g_templateff.Draw("P SAME")
        if g_syspp:
            g_syspp.Draw("E2 SAME")
            g_syspf.Draw("E2 SAME")
            g_sysff.Draw("E2 SAME")
        if g_mctruthpp:
            g_mctruthpp.Draw("p SAME")
            g_mctruthpf.Draw("p SAME")
            g_mctruthff.Draw("p SAME")
            leg.AddEntry(g_mctruthpp,"#gamma #gamma MC truth","lp")  
            leg.AddEntry(g_templatepp,"#gamma #gamma data","lp")  
            leg.AddEntry(g_mctruthpf,"#gamma j MC truth","lp")
            leg.AddEntry(g_templatepf,"#gamma j data","lp")
            leg.AddEntry(g_mctruthff,"j j MC truth","lp")
            leg.AddEntry(g_templateff,"j j data","lp")
        else:
            leg.AddEntry(g_templatepp,"#gamma #gamma","lp")  
            leg.AddEntry(g_templatepf,"#gamma j","lp")
            leg.AddEntry(g_templateff,"j j","lp")
        g_templatepp.GetXaxis().SetMoreLogLabels()
        leg.Draw()
       # pt=ROOT.TPaveText(0.19,0.81,0.26,0.92,"nbNDC")
        pt=ROOT.TPaveText(0.19,0.84,0.28,0.91,"nbNDC")
        #pt=ROOT.TPaveText(0.19,0.8,0.29,0.92,"nbNDC")
        pt.SetFillStyle(0)
        pt.SetLineColor(ROOT.kWhite)
        pt.AddText("%s" % cat)
        pt.Draw("same")
        #b.DrawLatex(0.45,.94,"#int L dt=1.7 /fb  CMS PRELIMINARY")
        if g_ratiopp:
                cpu.cd(2)
                style_utils.apply(g_ratiopp, [["colors",ROOT.kRed]]+ratio_expectedStyle )
                g_ratiopp.GetYaxis().SetTitle("(data-MC)/#sigma_{data}")
                g_ratiopp.GetYaxis().SetRangeUser(-1.3,1.3)
                g_ratiopp.GetYaxis().SetTitleSize(  g_templatepp.GetYaxis().GetTitleSize() * 6/3. )
                g_ratiopp.GetYaxis().SetTitleOffset(  g_templatepp.GetYaxis().GetTitleOffset() * 3/7. ) # not clear why the ratio should be upside down, but it does
                g_ratiopp.GetYaxis().SetLabelSize(  g_templatepp.GetYaxis().GetLabelSize() * 7/3. )
                g_ratiopp.GetXaxis().SetTitleSize(  g_templatepp.GetXaxis().GetTitleSize() * 7/3. )
                g_ratiopp.GetXaxis().SetTitleOffset(  g_templatepp.GetXaxis().GetTitleOffset() )
                g_ratiopp.GetXaxis().SetLabelSize(  g_templatepp.GetXaxis().GetLabelSize() * 6/3. )
                if cat=="EBEB":
                    g_ratiopp.GetXaxis().SetLimits(200.,1600.)
                if cat=="EBEE":
                    g_ratiopp.GetXaxis().SetLimits(300.,1600.)
                g_ratiopp.GetXaxis().SetMoreLogLabels()
                g_ratiopp.Draw("AP")
                self.keep( [g_ratiopp] )
        self.workspace_.rooImport(g_templatepp,"g_pp%s" %cat)
        self.workspace_.rooImport(g_templatepf,"g_pf%s" %cat)
        self.workspace_.rooImport(g_templateff,"g_ff%s" %cat)
        self.format(cpu,self.options.postproc)
        self.keep( [cpu,g_templatepp,g_templatepf,g_templateff] )
        self.autosave(True)

    ## ------------------------------------------------------------------------------------------------------------
    
    
    def Jackknife(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        fit=options.fits["2D"]
        for cat in options.jackknife.get("categories", fit["categories"]):
            isoargs=ROOT.RooArgSet("isoargs")
            setargs=ROOT.RooArgSet("setargs")
            massargs=ROOT.RooArgSet("massargs")
            mass_var,mass_b=self.getVar(options.jackknife.get("mass_binning"))
            mass=self.buildRooVar(mass_var,mass_b,recycle=True)
            massargs.add(mass)
            if len(options.template_binning) > 0:
                template_binning = array.array('d',options.template_binning)
            else:
                template_binning = array.array('d',options.jackknife.get("template_binning"))
            templatebins=ROOT.RooBinning(len(template_binning)-1,template_binning,"templatebins" )
            for idim in range(fit["ndim"]):
                isoargs.add(self.buildRooVar("templateNdim%dDim%d" % ( fit["ndim"],idim),template_binning,recycle=True))
            setargs.add(isoargs)
            setargs.add(massargs)
            dset_data = self.reducedRooData("data_2D_%s" % (cat),massargs)
            dset_data.Print()
            if not options.fixed_massbins:
                mass_split= [int(x) for x in options.fit_massbins]
                diphomass=self.massquantiles(dset_data,massargs,mass_b,mass_split)
                massrange=[mass_split[2],mass_split[1]]
            elif options.fixed_massbins and cat=="EBEB":
                diphomass = array.array('d',comparison.get("diphomassEBEB_binning"))
                massrange=[0,len(diphomass)-1]
            elif options.fixed_massbins and cat=="EBEE":
                diphomass = array.array('d',comparison.get("diphomassEBEE_binning"))
                
                massrange=[0,len(diphomass)-1]
            for mb in range(massrange[0],massrange[1]):
                massbin=(diphomass[mb]+diphomass[mb+1])/2.
                masserror=(diphomass[mb+1]-diphomass[mb])/2. 
                cut=ROOT.TCut("mass>%f && mass<%f"% (diphomass[mb],diphomass[mb+1]))
                cut_s= "%1.0f_%2.0f"% (diphomass[mb],diphomass[mb+1])
                print cut.GetTitle()
                for comp in options.jackknife.get("components",fit["components"]) :
                    name="%s_%s_%s" %(comp,cat,cut_s)
                    print name
                    #if comp=="pf"
                    #    full_temp = self.reducedRooData( "template_mix_%s_kDSinglePho2D_%s" % (comp,cat),setargs,redo=True)
                    #    full_temp.SetName("template_mix_%s_2D_%s" % (comp,cat))
                    #    full_template =self.masscutTemplates(full_temp,cut,cut_s,"%s"% (full_temp.GetName()))
                    
                   # print full_template
                   # full_hist=self.histounroll([full_template],template_binning,isoargs,comp,cat,cut_s,True,min(template_binning),max(template_binning),extra_shape_unc=options.extra_shape_unc,plot=False)

                    #TODO get number of pseudosamples more elegant
                    #if options.verbose:
                    #    c1=ROOT.TCanvas("c1_%s"%name,"c1_%s"%name)
                    #    full_hist[0].Draw()
                    #    self.keep(c1)

                    temps_all = []
                    temps = []
                    if not comp=="pp":
                        jks=int(options.jackknife.get("jk_source"))
                        jkt=int(options.jackknife.get("jk_target"))
                        print "jks ",jks, " jkt ", jkt
                        for s in range(jks):
                            temp = self.reducedRooData( "template_mix_%s_%i_kDSinglePho2D_%s" % (comp,s,cat),setargs,redo=True)
                            temp.SetName("template_mix_%s_%i_2D_%s" % (comp,s,cat))
                            temps_all.append(temp)
                        for t in range(jkt):
                            temp = self.reducedRooData( "template_mix_%s_kDSinglePho2D_%i_%s" % (comp,t,cat),setargs,redo=True)
                            temp.SetName("template_mix_%s_2D_%i_%s" % (comp,t,cat))
                            temps_all.append(temp)
                        print temp
                    else:
                        jkp=int(options.jackknife.get("jk_pp"))
                        for s in range(jkp):
                            temp = self.reducedRooData( "template_%s_%i_2D_%s" % (comp,s,cat),setargs,redo=True)
                            temp.SetName("template_%s_%i_2D_%s" % (comp,s,cat))
                            temps_all.append(temp)
                    print temps_all
                    for template in temps_all:
                        template_massc =self.masscutTemplates(template,cut,cut_s,"%s"% (template.GetName()))
                        temps.append(template_massc)
                    print "number of pseudo samples", len(temps)
                    print temps
                    hists=self.histounroll(temps,template_binning,isoargs,comp,cat,cut_s,True,min(template_binning),max(template_binning),extra_shape_unc=options.extra_shape_unc,plot=False)
                    if options.verbose:
                        c12=ROOT.TCanvas("c12_1%s"%name,"c12_1%s"%name)
                        hists[1].Draw()
                        self.keep(c12)
                        self.autosave(True)
                    #self.varJK(self.options,full_hist,hists,name)
        self.saveWs(options,fout)
    
    ## ------------------------------------------------------------------------------------------------------------
    def plotJKpurity(self,options,cat,dim,tps,jkID="jk"):
        jks=int(options.jackknife.get("jk_source"))
        jkt=int(options.jackknife.get("jk_target"))
      #   tree_fitresult_purity_unrolled_template_mix_2D_EBEB
        nom_tree =self.treeData("fitresult_purity_unrolled_template_mix_2D_%s" % (cat))
        nentries= nom_tree.GetEntries()
        g_purity=ROOT.TGraphErrors(nentries*len(tps))
        g_purity=ROOT.TGraphErrors(nentries)
        g_puerr=ROOT.TGraphErrors(nentries)
        g_puratio=ROOT.TGraphErrors(nentries)
        histos=[]
        for mb in range(nentries):
            h_p=ROOT.TH1D("h_p%s_%s_%i"%(jkID,cat,mb),"h_p%s_%s_%i"%(jkID,cat,mb),50*len(tps),.3,1.)
            histos.append(h_p)
        g_purity.GetXaxis().SetTitle("Diphoton mass [GeV]")
        g_purity.GetYaxis().SetTitle("Fraction")
        i=1
        for tree_template in tps:
            for mb in range(nentries):
                tree_template.GetEntry(mb)
                histos[mb].Fill(tree_template.purity_pp)
                massbin=tree_template.massbin
                masserror=tree_template.masserror
                if mb==nentries-1:
                    massbin=5500/2.
                    masserror=1950.
                else:
                    massbin=tree_template.massbin
                    masserror=tree_template.masserror
                g_purity.SetPoint(mb+i,massbin,tree_template.purity_pp)
                g_purity.SetPointError(mb+i,masserror,tree_template.error_pp)
            i=i+nentries
        
        for mb in range(nentries):
            cmb = ROOT.TCanvas("cJK%s_%s_%i" % (jkID,cat,mb),"cJK%s_%s_%i" % (jkID,cat,mb))
            cmb.cd()
            histos[mb].Draw("HIST E2")
            rms=histos[mb].GetRMS()*(len(tps)-1)/sqrt(len(tps))
            histos[mb].GetXaxis().SetTitle("Diphoton mass %i"%mb)
            histos[mb].GetXaxis().SetLimits( histos[mb].GetMean()-3*histos[mb].GetRMS(),histos[mb].GetMean()+3*histos[mb].GetRMS())
            self.keep( [cmb,histos[mb]] )
            nom_tree.GetEntry(mb)
            if mb==nentries-1:
                massbin=5500/2.
                masserror=1950.
            else:
                massbin=nom_tree.massbin
                masserror=nom_tree.masserror
            g_ratio.SetPoint(mb+1,massbin,nom_tree.purity_pp)
            g_ratio.SetPointError(mb+1,masserror,rms)
            g_puratio.SetPoint(mb+1,massbin,0.)
            g_puerr.SetPoint(mb+1,massbin,nom_tree.purity_pp)
            err=sqrt(pow(rms,2)+pow(nom_tree.error_pp,2) )
            print mb, "rms", rms, "tot err",err
            g_puerr.SetPointError(mb+1,masserror,err)
            g_puratio.SetPointError(mb+1,masserror,err/nom_tree.purity_pp)
        cpurity = ROOT.TCanvas("cpurity%s_%s" % (jkID,cat),"cpurity%s_%s" % (jkID,cat))
        cpurity.Divide(1,2)
        cpurity.cd(1)
      #  ROOT.gPad.SetGridx()
      #  ROOT.gPad.SetGridy()
        ROOT.gPad.SetPad(0., 0.5, 1., 1.0)
        ROOT.gPad.SetLogx()
        g_purity.SetMarkerSize(1.3)
        g_purity.SetMarkerStyle(20)
        g_purity.GetYaxis().SetTitle("JK puritys")
        g_purity.Draw("AP")
        g_purity.GetXaxis().SetLimits(200.,5000.)
        cpurity.cd(2)
        ROOT.gPad.SetPad(0., 0., 1., 0.5)
        ROOT.gPad.SetLogx()
       # ROOT.gPad.SetGridy()
        g_ratio.SetMarkerSize(1.0)
        g_ratio.SetMarkerStyle(20)
        g_ratio.Draw("AP" )
        #g_ratio.GetXaxis().SetTitle("Diphoton mass [GeV]")
        g_ratio.GetYaxis().SetTitleSize( g_purity.GetYaxis().GetTitleSize() )
        g_ratio.GetYaxis().SetLabelSize( g_purity.GetYaxis().GetLabelSize()  )
        g_ratio.GetYaxis().SetTitleOffset(g_purity.GetYaxis().GetTitleOffset() )
        g_ratio.GetXaxis().SetTitleSize( g_purity.GetXaxis().GetTitleSize()  )
        g_ratio.GetXaxis().SetLabelSize( g_purity.GetXaxis().GetLabelSize() )
        g_ratio.GetYaxis().SetTitle("Fraction + JK stat error")
        g_ratio.GetXaxis().SetLimits(200.,5000.)
        g_ratio.GetYaxis().SetRangeUser(0.4,1.)
        
        #draw whole nominal purity with JK
        cpu = ROOT.TCanvas("cpurity_%s" % (cat),"cpurity_%s" % (cat))
        cpu.Divide(1,2)
        cpu.cd(1)
       # ROOT.gPad.SetGridx()
       # ROOT.gPad.SetGridy()
        leg =ROOT.TLegend(0.4,0.2,0.7,0.5)
        leg.SetFillColor(ROOT.kWhite)
        leg.AddEntry(g_puerr,"full stat. error","l")
        leg.AddEntry(g_ratio,"JK error","l")
        ROOT.gPad.SetPad(0., 0.4, 1., 1.0)
        ROOT.gPad.SetLogx()
        g_puerr.SetMarkerSize(1.3)
        g_puerr.SetMarkerStyle(20)
        g_puerr.SetLineWidth(2)
        g_ratio.SetLineWidth(2)
        g_ratio.SetMarkerColor(ROOT.kRed+1)
        g_ratio.SetLineColor(g_ratio.GetMarkerColor())
        g_puerr.Draw("AP")
        g_puerr.GetXaxis().SetTitle("Diphoton mass [GeV]")
        g_ratio.Draw("P SAME")
        leg.Draw()
        g_puerr.GetXaxis().SetLimits(200.,5000.)
        cpu.cd(2)
        #ROOT.gPad.SetGridy()
        ROOT.gPad.SetPad(0., 0., 1., 0.4)
        ROOT.gPad.SetLogx()
        g_puratio.SetMarkerSize(1.3)
        g_puratio.SetMarkerStyle(20)
        g_puratio.Draw("AP")
        #g_puratio.GetXaxis().SetTitle("Diphoton mass [GeV]")
        g_puratio.GetYaxis().SetTitle("fullerr/purity")
        g_puratio.GetXaxis().SetLimits(200.,5000.)
        g_puratio.GetYaxis().SetRangeUser(-0.3,0.3)
        g_puratio.GetYaxis().SetTitleSize( g_puratio.GetYaxis().GetTitleSize() *6./4. )
        g_puratio.GetYaxis().SetLabelSize( g_puratio.GetYaxis().GetLabelSize()*6./4.  )
        g_puratio.GetYaxis().SetTitleOffset(g_puratio.GetYaxis().GetTitleOffset()*4./6. )
        g_puratio.GetXaxis().SetTitleSize( g_puratio.GetXaxis().GetTitleSize() *6./4. )
        g_puratio.GetXaxis().SetLabelSize( g_puratio.GetXaxis().GetLabelSize()*6./4. )
        
       #TODO new function for last plot to add JKpp and JKpf error 
        self.keep( [cpu,cpurity,g_purity,g_ratio] )
        self.autosave(True)
        
    ## ------------------------------------------------------------------------------------------------------------
    def varJK(self,options,full_hist,hists,name):
        ROOT.TH1D.SetDefaultSumw2(True)
        num_bins=full_hist[0].GetNbinsX()
        ntuple_rms = ROOT.TNtuple("tree_rms_%s" % (name),"tree_rms_%s" % (name),"rms_bin" )
        self.store_[ntuple_rms.GetName()] =ntuple_rms
        hist_diffHigh=ROOT.TH2D("hdiffHigh_%s"% (name),"Variance for %s of the difference of # entries between two bins, bin_{X-(X+1)}"%name,num_bins,0.,num_bins,num_bins,0.,num_bins)
        hist_var=ROOT.TH1D("hvar_%s"% (name),"hvar_%s"% (name),num_bins,0.0,num_bins)
        var_bins=[] #goal to have all differences in an array
        bincont_bins=[]
        #2d array with:y columns,x rows
        diffHigh = [ [  [] for col in range(num_bins)] for row in range(num_bins)]
        mean_dHigh = [ [ 0. for col in range(num_bins)] for row in range(num_bins)]
        for bin in range(1,num_bins+1):
           #get #of entries for current bin
            mean_bin=0
            for hist in hists:
                if full_hist[0].GetBinContent(bin)!=0:
                    bincont=hist.GetBinContent(bin)/full_hist[0].GetBinContent(bin)
                    mean_bin=mean_bin+bincont
                    bincont_bins.append(bincont)
                else:
                    bincont_bins.append()
                #get difference of # entries between current and next bin to calculate RMS for this value (diffHigh)
                for i in range (1,num_bins+1):
                    if full_hist[0].GetBinContent(i) >0.:
                        diffHigh[bin-1][i-1].append(bincont - hist.GetBinContent(i)/full_hist[0].GetBinContent(i))
            #get variance for #of entries for each bin
            #get rms for #of entries for current bin
            mean_bin=mean_bin/len(hists)
            n=0
            for j in range(len(hists)):
                n=n+pow((mean_bin-bincont_bins[j]),2)
            var_rmsbin=(len(hists)-1)/float(len(hists))*n
            hist_var.SetBinContent(bin,var_rmsbin)
            ntuple_rms.Fill(var_rmsbin)
        #draw variance of #of entries for each bin
        canv = ROOT.TCanvas("cvar_%s" % (name),"cvar_%s"% (name) )
        canv.cd()
        hist_var.Draw("HIST E2")
        ROOT.gStyle.SetOptStat(111111)
        hist_var.GetXaxis().SetTitle("bin_{JK}/bin_{full_dataset}") 
        hist_var.GetYaxis().SetTitle("variance of # entries per bin") 
        hist_var.SetTitle("Var for %s ChIso" %(name) )
        self.keep( [canv] )



       #get mean for diffHigh of each bin difference
        for row in range(num_bins):
            for col in range(num_bins):
                add_hists=0
                for j in diffHigh[row][col]:
                    add_hists=j+add_hists
                mean_dHigh[row][col]=add_hists/len(hists)

        #calculate variance for this diffHigh~ (RMS-currentdiffHigh)
        for row in range(num_bins):
            for col in range(num_bins):
                var_diff=0
                for j in range(len(hists)):
                   var_diff=var_diff+pow((mean_dHigh[row][col]-diffHigh[row][col][j]),2)
                var_rmsbin=(len(hists)-1)/float(len(hists))*var_diff
                print "mean ", mean_dHigh[row][col], "var_diff", var_diff, "row",row+1 ,"col", col+1
                hist_diffHigh.SetBinContent(row+1,col+1,var_diff)
       #plot variance for each bin difference from bin1 - binX
        cHigh=ROOT.TCanvas("chigh_%s"% name,"chigh_%s"% name)
        hist_diffHigh.GetXaxis().SetTitle("bin X") 
        hist_diffHigh.GetYaxis().SetTitle("bin X+1") 
        cHigh.cd()
        hist_diffHigh.Draw("colz")
        hist_diffHigh.SetTitle("Variance for %s difference of # entries between two bins, bin_{X-(X+1)}" %(name) )
        self.keep([cHigh])
        self.autosave(True)


    ## ------------------------------------------------------------------------------------------------------------
    

# -----------------------------------------------------------------------------------------------------------
# actual main
if __name__ == "__main__":
    app = TemplatesFitApp()
    app.run()



