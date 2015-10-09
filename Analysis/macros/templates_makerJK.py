#!/bin/env python

from diphotons.Utils.pyrapp import *
from optparse import OptionParser, make_option
from copy import deepcopy as copy
import os, json
from pprint import pprint
import array
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
class rooImport:

    def __init__(self,target):
        self.import_ = getattr(target,"import")
        
    def __call__(self,*args):
        if len(args) == 1:
            try:
                # workaround for https://sft.its.cern.ch/jira/browse/ROOT-6785
                self.import_(args[0],ROOT.RooCmdArg())
            except:
                # for actual TObjects
                self.import_(args[0])
        else:
            self.import_(*args)
            
## ----------------------------------------------------------------------------------------------------------------------------------------
class LookUp:
    def __init__(self,target,method):
        self.method_ = method
        self.container_ = target.container_

    def __call__(self,*args):
        for ws in self.container_:
            obj = getattr(ws,self.method_)(*args)
            if obj: return obj
        return None

## ----------------------------------------------------------------------------------------------------------------------------------------
class WsList:
    
    def __init__(self,init=None):
        self.container_ = []
        if init:
            self.append(init)
        
    def append(self,what):
        self.container_.append(what)
    
    def Print(self,opt=""):
        for w in self.container_:
            w.Print(opt)
        
    def __getattr__(self,method):
        return LookUp(self,method)
    
    ### def data(self,what):
    ###     return self.lookup(what,"var")
    ### 
    ### def var(self,what):
    ###     return self.lookup(what,"var")
    ### 
    ### def pdf(self,what):
    ###     return self.lookup(what,"pdf")
    ### 
    ### def set(self,what):
    ###     return self.lookup(what,"set")
    ### 
    ### def func(self,what):
    ###     return self.lookup(what,"func")
    ### 
    ### def lookup(self,what,method):
    ###     for ws in self.container_:
    ###         obj = getattr(ws,method)(what)
    ###         if obj: return obj
    ###     return None



## ----------------------------------------------------------------------------------------------------------------------------------------
## TemplatesApp class
## ----------------------------------------------------------------------------------------------------------------------------------------

## ----------------------------------------------------------------------------------------------------------------------------------------
class TemplatesApp(PlotApp):
    """
    Class to handle template fitting.
    Takes care of preparing templates starting from TTrees.
    Inherith from PyRapp and PlotApp classes.
    """
    
    ## ------------------------------------------------------------------------------------------------------------
    def __init__(self,option_list=[],option_groups=[]):
        """ 
        Constructor
        """
        super(TemplatesApp,self).__init__(option_groups=[
                ( "Fit definition options. Usually specified through JSON configuration (see templates_maker.json for details)", [
                        make_option("--preselection",dest="preselection",action="store",type="string",
                                    default="",
                                    help="Preselection cuts to be applied."),
                        make_option("--selection",dest="selection",action="store",type="string",
                                    help="(Di-)Photon selection to be used for analysis. In dataset definition it replaces '%(sel)s'."),                
                        make_option("--fit-categories",dest="fit_categories",action="callback",type="string",callback=optpars_utils.ScratchAppend(),help="sets specific category for fit, e.g. EBEB or EBEE",default=["EBEB","EBEE"]),
                        make_option("--fit-massbins",dest="fit_massbins",action="callback",type="string",callback=optpars_utils.ScratchAppend(),help="sets massbins for fit or templates comparison: first integer is total number of massbins, 2. how many bins we want to run over, 3. startbin",default=["1","1","0"]),
                        make_option("--fit-templates",dest="fit_templates",action="callback",type="string",callback=optpars_utils.ScratchAppend(),help="get templates for fit: either unrolled_template,unrolled_template_mix or unrolled_mctruth",default=["unrolled_template"]),
                        make_option("--plot-closure",dest="plot_closure",action="callback",callback=optpars_utils.ScratchAppend(),type="string",
                                    default=["template"],
                                    help="choose template or mctruth."),
                        make_option("--plot-purityvalue",dest="plot_purityvalue",action="callback",callback=optpars_utils.ScratchAppend(),type="string",
                                    default=["fraction"],
                                    help="purity either as fraction or as number of events in signalregion.Choose 'fraction' or 'events'"),
                        make_option("--plot-mctruth",dest="plotMCtruth",action="callback",callback=optpars_utils.ScratchAppend(),type="string",
                                    default=["mctruth"]),
                        make_option("--aliases",dest="aliases",action="callback",type="string",callback=optpars_utils.ScratchAppend(),
                                    default=[],
                                    help="List of aliases to be defined for each tree. They can be used for selection or variable definition"),
                        make_option("--plot-purity",dest="plot_purity",action="store_true",default=False,
                                    help="Plot purities, purity vs massbin and pull function",
                                    ),
                        make_option("--jackknife",dest="jackknife",action="store_true",default=False,
                                    help="Plot RMS etc from jk pseudosamples",
                                    ),
                        make_option("--fits",dest="fits",action="callback",callback=optpars_utils.Load(),type="string",
                                    default={},help="List of templates fits to be performed. Categories, componentd and templates can be specified."),
                        make_option("--mix",dest="mix",action="callback",callback=optpars_utils.Load(),type="string",
                                    default={},help="Configuration for event mixing."),
                        make_option("--template-binning",dest="template_binning",action="callback",callback=optpars_utils.ScratchAppend(float),
                                    type="string",
                                    default=[],
                                    help="Binning of the parametric observable to be used for templates",
                                    ),                        
                        make_option("--comparisons",dest="comparisons",action="callback",callback=optpars_utils.Load(),type="string",
                                    default={},help="Configuration for templates comparison."),
                        make_option("--skip-templates",dest="skip_templates",action="store_true",
                                    default=False,help="Skip templates generation (even if not reading back from ws)"),
                        make_option("--dataset-variables",dest="dataset_variables",action="callback",callback=optpars_utils.ScratchAppend(),type="string",
                                    default=[],help="List of variables to be added to dataets."),
                        make_option("--weight-expression",dest="weight_expression",action="store",type="string",
                                    default="",help="Expression used to define datasets weight."),
                        ]
                  ), ("General templates preparation options", [
                        make_option("--compare-templates",dest="compare_templates",action="store_true",default=False,
                                    help="Make templates comparison plots",
                                    ),
                        make_option("--nominal-fit",dest="nominal_fit",action="store_true",default=False,
                                    help="do fit templates",
                                    ),
                        make_option("--build-3dtemplates",dest="build_3dtemplates",action="store_true",
                                    default=False,
                                     help="build 3d templates with unrolled variable and mass",
                                    ), 
                        make_option("--corr-singlePho",dest="corr_singlePho",action="store_true",
                                    default=False,
                                     help="correlation sieie and chiso single fake photon",
                                    ), 
                        make_option("--do-reweight",dest="do_reweight",action="store_true",default=False,
                                    help="Reweight templates to data.",
                                    ),
                        make_option("--reweight-variables",dest="reweight_variables",action="callback",callback=optpars_utils.ScratchAppend(),
                                    default=[],
                                    help="List of variables to be used for reweighting.",
                                    ),
                        make_option("--mix-templates",dest="mix_templates",action="store_true",
                                    default=False,
                                    help="Mix templates.",
                                    ),
                        make_option("--extra-shape-unc",dest="extra_shape_unc",action="store",type="float",
                                    default=None,
                                    help="Add extra uncertainty to template shapes (implemented only for plotting)",
                                    ),
                        make_option("--read-ws","-r",dest="read_ws",type="string",
                                    default=[],action="callback",callback=optpars_utils.ScratchAppend(),
                                    help="workspace input file.",
                                    ),
                        make_option("--ws-dir","-w",dest="ws_dir",action="store",type="string",
                                    default=None,
                                    help="Folder to be used to read and write workspaces"
                                    ),
                        make_option("--output-file","-o",dest="output_file",action="store",type="string",
                                    default=None,
                                    help="Output file.",
                                    ),
                        make_option("--store-new-only",dest="store_new_only",action="store_true",
                                    default=False,
                                    help="Only store new objects in output file.",
                                    ),
                        make_option("--store-inputs",dest="store_inputs",action="store_true",
                                    default=False,
                                    help="Store all used input datasets.",
                                    ),
                        make_option("--mc-file",dest="mc_file",action="store",type="string",
                                    default=None,help="default: %default"),
                        make_option("--prepare-data",dest="prep_data",action="store_true",
                                    default=False,help="prepare templates only with data, no mc, signals, or templatesMC,mctruth)"),
                        make_option("--prepare-nosignal",dest="prep_nosig",action="store_true",
                                    default=False,help="prepare templates without signals"),
                        make_option("--only-subset",dest="only_subset",action="callback",type="string", callback=optpars_utils.ScratchAppend(),
                    default=[],help="default: %default"),
                        ]
                      )
            ]+option_groups,option_list=option_list)
        
        ## initialize data members
        self.trees_ = {}
        self.datasets_ = {}
        self.aliases_ = {}
        self.variables_ = {}
        self.cache_ = {}
        self.store_ = {}
        self.rename_ = False
        self.store_new_ = False
        self.save_params_ = []
        self.workspace_ = None

        self.save_params_.append("signals")
        self.save_params_.append("aliases")
        
        ## load ROOT (and libraries)
        global ROOT, style_utils, RooFit
        import ROOT
        from ROOT import RooFit
        from ROOT import RooAbsData
        import diphotons.Utils.pyrapp.style_utils as style_utils
        ROOT.gSystem.Load("libdiphotonsUtils")
        if ROOT.gROOT.GetVersionInt() >= 60000:
            ROOT.gSystem.Load("libdiphotonsRooUtils")
            ROOT.gSystem.AddIncludePath("-I$CMSSW_BASE/include")
            ROOT.gROOT.ProcessLine('#include "diphotons/Utils/interface/DataSetFiller.h"')
            ROOT.gROOT.ProcessLine('#include "diphotons/Utils/interface/DataSetMixer.h"')

        ROOT.gStyle.SetOptStat(111111)

    ## ------------------------------------------------------------------------------------------------------------
    def setup(self,options,args):
        """ 
        Read input trees and generate new datasets/trees if required
        """

        if len(options.only_subset)>0:
            subset = {}
            for name,fit in options.fits.iteritems():
                if not name in options.only_subset:
                    continue
                subset[name] = fit
            options.fits = subset
        
        if options.store_new_only:
            self.store_new_ = True
            self.store_inputs_ = options.store_inputs
        
        if len(options.read_ws) > 0:
            options.read_ws_list = options.read_ws
            options.read_ws = options.read_ws_list[0]
        else:
            options.read_ws = False
            
        if not options.output_file:
            if options.read_ws: 
                options.output_file = options.read_ws
                if options.store_new_only:
                    options.output_file = options.output_file.replace(".root","_new.root")
            else : 
                options.output_file = "templates.root"
        
        if options.read_ws:
            self.readWs(options,args)
        elif not options.skip_templates:
            self.prepareTemplates(options,args)
            
        if options.verbose:
            print "Read workspace"

    ## ------------------------------------------------------------------------------------------------------------
    def __call__(self,options,args):
        """ 
        Main method. Called automatically by PyRoot class.
        """
        ## load ROOT style
        self.loadRootStyle()
        from ROOT import RooFit
        ROOT.gStyle.SetOptStat(111111)
        printLevel = ROOT.RooMsgService.instance().globalKillBelow()
        ROOT.RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)
        
        self.setup(options,args)
        
        if options.mix_templates:
            if options.verbose:
                print "calling mix templates"
            self.mixTemplates(options,args)
            
        if options.compare_templates:
            self.compareTemplates(options,args)
            
        if options.nominal_fit:
            self.nominalFit(options,args)
        if options.plot_purity:
            self.plotPurity(options,args)
        if options.jackknife:
            self.Jackknife(options,args)
        if options.corr_singlePho:
            self.corrSinglePho(options,args)
        if options.build_3dtemplates:
            self.build3dTemplates(options,args)
     #   if options.plotMCtruth:
      #      self.plotMCtruth(options,args)
        

    ## ------------------------------------------------------------------------------------------------------------
    def openOut(self,options):
        if options.read_ws and options.output_file == options.read_ws:
            name    = options.output_file
            tmpname = name.replace(".root","_tmp.root")
            fout    = self.open(tmpname,"recreate",folder=options.ws_dir)
            self.rename_  = (tmpname,name)
        else:
            fout = self.open(options.output_file,"recreate",folder=options.ws_dir)
        return fout

    ## ------------------------------------------------------------------------------------------------------------
    def saveWs(self,options,fout=None):            
        if not fout:
            fout = self.openOut(options)
        fout.cd()
        cfg = { "fits"   : options.fits,
                "mix"    : options.mix,
                "comparisons"    : options.comparisons,
                "stored" : self.store_.keys(),
                }
        for name in self.save_params_:
            val = getattr(options,name,None)
            if val:
                cfg[name] = val

        print "--------------------------------------------------------------------------------------------------------------------------"
        print "saving output"
        print 
        ROOT.TObjString( json.dumps( cfg,indent=4,sort_keys=True) ).Write("cfg")
        
        nobjs = len(self.store_.keys())
        nprint = int(nobjs/20)
        if nprint == 0:
            nprint = 1
        iobj  = 0
        for key,val in self.store_.iteritems():
            val.CloneTree().Write(key,ROOT.TObject.kWriteDelete)
            iobj += 1
            if iobj % nprint == 1:
                print "written %d / %d trees" % ( iobj, nobjs )
        print "writing workspace ...",
        self.workspace_.Write()
        print "done"
        fout.Close()
        
        if self.rename_:
            os.rename( *self.rename_ )
        print "--------------------------------------------------------------------------------------------------------------------------"
        print

    ## ------------------------------------------------------------------------------------------------------------
    def rooImportItr(self,coll,verbose=False):        
        itr = coll.createIterator()
        if verbose:
            print "Importing collection to workspace"
            coll.Print()
        obj = itr.Next()
        while obj:
            if type(obj) == ROOT.TObject:
                ## FIXME: for some reason, instead of a null pointer, at the end of the iteration
                ##        a bare TObject is returned.... looks like a plain ROOT bug
                break          
            self.workspace_.rooImport(obj,ROOT.RooFit.RecycleConflictNodes(),ROOT.RooFit.Silence(not verbose))
            obj = itr.Next()
        
    ## ------------------------------------------------------------------------------------------------------------
    def mergeWs(self,options,read_ws):
        
        if os.path.dirname(read_ws) == "" and not os.path.exists(read_ws):
            print "Warning: %s does not exist. I will look for it in %s" % ( read_ws, options.ws_dir )
            fin = self.open(read_ws,folder=options.ws_dir)
        else:
            fin = self.open(read_ws)
        cfg = json.loads( str(fin.Get("cfg").GetString()) )
        for name,val in cfg["fits"].iteritems():
            options.fits[name] = val
        ws = fin.Get("wtemplates")

        if not self.workspace_:
            self.workspace_ = ws
            ## self.workspace_.rooImport = getattr(self.workspace_,"import")
            self.workspace_.rooImport = rooImport(self.workspace_)
        else:
            self.rooImportItr( ws.allVars(), verbose=options.verbose )
            self.rooImportItr( ws.allFunctions(), verbose=options.verbose )
            self.rooImportItr( ws.allPdfs(), verbose=options.verbose )
            
            alldata = ws.allData()
            for data in alldata:
                self.workspace_.rooImport(data)
            
        for name in cfg["stored"]:
            self.store_[name]=fin.Get(name)
            
        if not options.mix_templates:
            options.mix = cfg.get("mix",{})
        if not options.compare_templates:
            options.comparisons = cfg.get("comparisons",{})

        for name in self.save_params_:
            val = cfg.get(name,None)
            if val:
                print "Reading back saved parameter ", name, val
                setattr(options,name,val)
    
    ## ------------------------------------------------------------------------------------------------------------
    def readWs(self,options,args):
        print
        print "--------------------------------------------------------------------------------------------------------------------------"
        print "Reading back workspace from %s " % options.read_ws
        print 
        ### fin = self.open(options.read_ws)
        ### cfg = json.loads( str(fin.Get("cfg").GetString()) )
        ### options.fits = cfg["fits"]
        ### self.workspace_ = fin.Get("wtemplates")
        ### self.workspace_.rooImport = getattr(self.workspace_,"import")
        ### for name in cfg["stored"]:
        ###     self.store_[name]=fin.Get(name)
        ###     
        ### if not options.mix_templates:
        ###     options.mix = cfg.get("mix",{})
        ### if not options.compare_templates:
        ###     options.comparisons = cfg.get("comparisons",{})
        ### 
        ### for name in self.save_params_:
        ###     val = cfg.get(name,None)
        ###     print name, val
        ###     if val:
        ###         setattr(options,name,val)
        
        for ws in options.read_ws_list:
            self.mergeWs(options,ws)
            
        
        print "Fits :"
        print "---------------------------------------------------------"
        for key,val in options.fits.iteritems():
            print "- %s \n  ndim : %d \n  components : %s" % ( key, val["ndim"], ",".join(val["components"]) )
            print
        
        print "TTrees :"
        print "---------------------------------------------------------"
        for key,val in self.store_.iteritems():
            print key.ljust(30), ":", ("%d" % val.GetEntries()).rjust(8)
        print
        
        print "Datasets :"
        print "---------------------------------------------------------"
        alldata = self.workspace_.allData()
        ntoys = 0
        for dset in alldata:
            name = dset.GetName()
            if name.startswith("toy"):
                ntoys += 1
            else:
                print name.ljust(30), ":", ("%d" % dset.sumEntries()).rjust(8)
        print 
        print "Number of toys : %d"         % ntoys
        print    
        print "--------------------------------------------------------------------------------------------------------------------------"

        if self.store_new_:
            self.store_input_ = self.store_
            self.store_ = {}
            
            self.workspace_input_ = WsList(self.workspace_)
            self.workspace_ = ROOT.RooWorkspace("wtemplates","wtemplates")
            ## self.workspace_.rooImport = getattr(self.workspace_,"import")
            self.workspace_.rooImport = rooImport(self.workspace_)
            
    
    ## ------------------------------------------------------------------------------------------------------------
    
    def Jackknife(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        fit=options.fits["2D"]
        for cat in options.jackknife.get("categories", fit["categories"]):
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
                setargs.add(self.buildRooVar("templateNdim%dDim%d" % ( fit["ndim"],idim),template_binning,recycle=True))
            dset_data = self.reducedRooData("data_2D_%s" % (cat),massargs)
            dset_data.Print()
            mass_split= [int(x) for x in options.fit_massbins]
            diphomass=self.massquantiles(dset_data,massargs,mass_b,mass_split)
            for mb in range(mass_split[2],mass_split[1]):
                massbin=(diphomass[mb]+diphomass[mb+1])/2.
                masserror=(diphomass[mb+1]-diphomass[mb])/2. 
                cut=ROOT.TCut("mass>%f && mass<%f"% (diphomass[mb],diphomass[mb+1]))
                cut_s= "%1.0f_%2.0f"% (diphomass[mb],diphomass[mb+1])
                print cut.GetTitle()
                for comp in options.jackknife.get("components",fit["components"]) :
                    print cat, comp
                    full_template = self.reducedRooData( "template_mix_%s_kDSinglePho2D_%s" % (comp,cat),setargs)
                    print full_template
                    #TODO get number of pseudosamples more elegant
                    mix=options.mix.get("kDSinglePho2D")
                    jks=mix.get("jk_source",10)
                    jkt=mix.get("jk_target",10)
                    print "jks ",jks, " jkt ", jkt
                    temps = []
                    for s in range(jks):
                        temp = self.reducedRooData( "template_mix_%s_%i_kDSinglePho2D_%s" % (comp,s,cat),setargs)
                        temps.append(temp)
                    for t in range(jkt):
                        temp = self.reducedRooData( "template_mix_%s_kDSinglePho2D_%si_%i" % (comp,cat,t),setargs)
                        temps.append(temp)
                    print "number of pseudo samples", len(temps)
                    self.plotJK(full_template,temps)
        self.saveWs(options,fout)
    
    ## ------------------------------------------------------------------------------------------------------------
    
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
            doDataMc=comparison.get("doDataMc",True)
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
                        if len(template_binning)==4:
                            sigRegionup2D=9.
                        elif len(template_binning)==3:
                            sigRegionup2D=4.
                        else:
                            sigRegionup2D=float(comparison.get("upperLimitSigRegion2D"))
                        sigRegionup1D=float(comparison.get("upperLimitSigRegion1D"))
                    else: setargs=ROOT.RooArgSet(isoargs)
                   # setargs.add(self.buildRooVar("weight",[],recycle=True))
                    rooweight=self.buildRooVar("weight",[],recycle=True)
                    setargs.add(rooweight)
                    setargs.Print()
                    #needed to estimate true purity for alter 2dfit
                  
                    truthname= "mctruth_%s_%s_%s" % (compname,fitname,cat)
                    truth = self.reducedRooData(truthname,setargs,False,sel=weight_cut,redo=ReDo)
                    truth.Print()
                    #if not doDataMc:
                    templates.append(truth)
### loop over templates
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
                        tempdata = self.reducedRooData(templatename,setargs,False,sel=weight_cut,redo=ReDo)

                        #if "mix" in template and not prepfit:
                        if "mix" in template:
                            mixname=mixname[11:]
                            templatename=( "reduced_template_mix_%s_%s_%s" % (compname,mixname,mapping.get(cat,cat)))
                            print templatename
                            tempdata.SetName(templatename)
                        tempdata.Print()
                        if tempdata.sumEntries() ==0:
                            print "!!!!!!!!!!!! attention dataset ", templatename, " has no entries !!!!!!!!!!!!!!!!!"
                        else:
                            templates.append(tempdata)
###------------------- split in massbins
                    masserror = array.array('d',[])
                    
                    if cat=="EEEB": catd="EBEE"#TODO implement in json file
                    else: catd=cat
                    setargs.add(massargs)
                    setargs.Print()
                    dset_data = self.reducedRooData("data_%s_%s" % (fitname,catd),setargs,False,sel=weight_cut,redo=ReDo)
                    dset_mc = self.reducedRooData("mc_%s_%s" % (fitname,catd),setargs,False,sel=weight_cut,redo=ReDo)
                   # dset_data = self.reducedRooData("data_%s_%s" % (fitname,catd),setargs,False,redo=ReDo)
                    print "number of entries after reduced"
                    dset_data.Print()
                    mass_split= [int(x) for x in options.fit_massbins]
                    diphomass=self.massquantiles(dset_data,massargs,mass_b,mass_split)
                   # if not doDataMc:
                    truth_pp= "mctruth_%s_%s_%s" % (compname,fitname,cat)
                    if d2:
                        tp_mcpu = ROOT.TNtuple("tree_truth_purity_all_%s_%s_%s" % (compname,fitname,cat),"tree_truth_purity_%s_%s_%s" % (compname,fitname,cat),"number_pu:frac_pu:massbin:masserror" )
                      #  ntp_mcpu = ROOT.TNtuple("tree_truth_purity_signalregion_%s_%s_%s" % (compname,fitname,cat),"tree_truth_purity_signalrange_%s_%s_%s" % (compname,fitname,cat),"number_pu:frac_pu:massbin:masserror" )
                      #  self.store_[ntp_mcpu.GetName()] =ntp_mcpu
                        self.store_[tp_mcpu.GetName()] =tp_mcpu
                    for mb in range(mass_split[2],mass_split[1]):
                        massbin=(diphomass[mb]+diphomass[mb+1])/2.
                        masserror=(diphomass[mb+1]-diphomass[mb])/2.
                        
                        cut=ROOT.TCut("mass>%f && mass<%f"% (diphomass[mb],diphomass[mb+1]))
                        cut_s= "%1.0f_%2.0f"% (diphomass[mb],diphomass[mb+1])
                        print cut.GetTitle()
                        if d2:
                            cut_sigregion=ROOT.TCut("templateNdim2Dim0< %f && templateNdim2Dim1< %f" %(sigRegionup1D,sigRegionup1D))
                            dset_massc = dset_data.Clone("%s_mb_%s"%(dset_data.GetName()[8:],cut_s))
                            dset_massc=dset_massc.reduce(cut.GetTitle())
                            dset_massc.Print()
                            dset_massc_mc = dset_mc.Clone("%s_mb_%s"%(dset_mc.GetName()[8:],cut_s))
                            dset_massc_mc=dset_massc_mc.reduce(cut.GetTitle())
                            dset_massc_mc.Print()
                            temp_massc_truth = templates[0].Clone("temp_truthinformation")
                            temp_massc_truth=temp_massc_truth.reduce(cut.GetTitle())
                            number_pu=temp_massc_truth.sumEntries()
                            frac_pu=number_pu/dset_massc_mc.sumEntries()
                            templates_massc=[]
                            for temp_m in templates:
                                temp_massc = temp_m.Clone("%s_mb_%s"%(temp_m.GetName()[8:],cut_s))
                                temp_massc=temp_massc.reduce(cut.GetTitle())
                                temp_massc.Print()
                                if temp_massc.sumEntries() ==0:
                                    print "!!!!!!!!!!!! attention dataset ", temp_massc, " has no entries !!!!!!!!!!!!!!!!!"
                                else:
                                    templates_massc.append(temp_massc)
###---------------get truth information per massbin and in signal range
                            #data_massc_truth = dset_massc.Clone("data_truthinformation")
                            #data_massc_truth=data_massc_truth.reduce(cut_sigregion.GetTitle())
                            print number_pu, " ", dset_massc_mc.sumEntries() , " ", frac_pu
                          #  number_pu_sigrange=temp_massc_truth.sumEntries()
                          #  frac_pu_sigrange=number_pu_sigrange/data_massc_truth.sumEntries()
                            tp_mcpu.Fill(number_pu, frac_pu,massbin, masserror)
                          #  ntp_mcpu.Fill(number_pu_sigrange, frac_pu_sigrange,massbin, masserror)
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
                           # if not prepfit: 
                           # print "plot 1d histos"
                      #      self.plotHistos(histls,tit,template_binning,True,True,numEntries_s)
                        

                        ## roll out for combine tool per category
                        if fit["ndim"]>1:
                            self.histounroll(templates_massc,template_binning,isoargs,compname,cat,cut_s,prepfit,sigRegionlow2D,sigRegionup2D,extra_shape_unc=options.extra_shape_unc)
                            self.histounroll_book(template_binning,isoargs)

    ## ------------------------------------------------------------------------------------------------------------

    def histounroll(self,templatelist, template_binning,isoargs,comp,cat,mcut_s,prepfit,sigRegionlow,sigRegionup,extra_shape_unc=None):
        pad_it=0
        c1=ROOT.TCanvas("d2hist_%s" % cat,"2d hists per category",1000,1000) 
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
           # print "integral 2d  histo", temp2d.Integral()
            temp2dx=temp2d.ProjectionX("%s_X" %tempur.GetName())
            ## temp2dx.Scale(1./temp2dx.Integral())
            if "truth" in temp2dx.GetName():
                computeShapeWithUnc(temp2dx)
            else:
                computeShapeWithUnc(temp2dx,extra_shape_unc)
            temp2dx.SetTitle("%s_X" %tempur.GetName())
            temp2dy=temp2d.ProjectionY("%s_Y" %tempur.GetName())
            ## temp2dy.Scale(1./temp2dy.Integral())
            if "truth" in temp2dy.GetName():
                computeShapeWithUnc(temp2dy)
            else:
                computeShapeWithUnc(temp2dy,extra_shape_unc)
            ## draw projections as a check
            histlsX.append(temp2dx)
            temp2dy.SetTitle("%s_Y" %tempur.GetName())
            histlsY.append(temp2dy)
            if len(templatelist) >1:
                ## temp2d.Scale(1./temp2d.Integral())
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
                            temp1dunroll.SetBinContent(b,0.0001)
                            print "ui, the bin content is zero"
                            fail=fail+1
                roodatahist_1dunroll=ROOT.RooDataHist("unrolled_%s" % (tempur.GetName()),"unrolled_%s_zerobins%u" %(tempur.GetName(),fail),unrollvar, temp1dunroll)
                roodatahist_1dunroll.Print()
                self.workspace_.rooImport(roodatahist_1dunroll,ROOT.RooFit.RecycleConflictNodes())
        if len(histlistunroll) >1:
            title="histo_%s_%s_%s" %(comp,cat,mcut_s)
            self.plotHistos(histlsX,"%s_X" %title,"charged isolation_X",template_binning,False,True,False,True)
            self.plotHistos(histlsY,"%s_Y" %title,"charged isolation_Y",template_binning,False,True,False,True)
            self.plotHistos(histlistunroll,"%s_unrolled" % (title),"charged isolation",tempunroll_binning,False,True,False,True)
            self.keep( [c1] )
            self.autosave(True)


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
        dataset.fillHistogram(massH,ROOT.RooArgList(massargs)) 
       # print "define mass bins 0 
        massH.Scale(1.0/massH.Integral())
        prob = array.array('d',[])
        dpmq = array.array('d',[0.0 for i in range((mass_split[1]+1))])
        for i in range(0,mass_split[1]+1):
            prob.append((i+float(mass_split[2]))/mass_split[0])
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
                sieieup=0.02
                sieieb = array.array('d',[sieielow,0.0105,0.012,sieieup])
                ymax=0.22e6
            elif cat =="EE":
                sieielow=0.015
                sieieup=0.045
                sieieb = array.array('d',[sieielow,0.028,0.035,sieieup])
                ymax=90e3
            sieievar.setRange(sieielow,sieieup)
            truth = self.reducedRooData("mctruth_f_singlePho_%s"% cat,setargs,False,weight="weight < 1000.",redo=True)
            truth.Print()
            tempdata = self.reducedRooData("template_f_singlePho_%s" %cat,setargs,False,weight="weight < 1000.",redo=True)
            tempdata.Print()
            tempdata.append(truth)
            tempCombined=tempdata
            tempCombined.SetName("template_allsieie_f_singlePho_%s" %cat)
            tempCombined.Print()
            histo_sieie=ROOT.TH1F("histo_sieie_%s" %cat,"histo_sieie_%s"%cat,30,sieielow,sieieup)
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
            histop_sieie=ROOT.TH1F("histop_sieie_%s" %cat,"histop_sieie_%s"%cat,30,sieielow,sieieup)
            tempCombinedp.fillHistogram(histop_sieie,ROOT.RooArgList(sieievar)) 
            #histop_sieie.Scale(1.0/histop_sieie.Integral())
            cSide=ROOT.TCanvas("cSide_%s" %cat,"cSide_%s" %cat)
            cSide.cd()
            cSide.SetLogy()
        #    histo_sieie.GetQuantiles(n+1,sieieb,prob)
            sieiebins=ROOT.RooBinning(len(sieieb)-1,sieieb,"sieiebins" )
            lineSR=ROOT.TLine(sieieb[1],0.,sieieb[1],ymax)
            lineSB=ROOT.TLine(sieieb[2],0.,sieieb[2],ymax)
            histo_sieie2.SetLineColor(ROOT.kRed)
            histo_sieie2.SetLineWidth(2)
            histop_sieie.SetLineWidth(2)
            histop_sieie.Draw("HIST")
            lineSR.Draw("SAME")
            lineSB.Draw("SAME")
            histo_sieie2.Draw(" same HIST")
            leg =ROOT.TLegend(0.55,0.4,0.85,0.6)
            leg.SetTextSize(0.03)
            leg.SetTextFont(42);
            leg.SetFillColor(ROOT.kWhite)
            leg.AddEntry(histop_sieie,"prompt single photons","l")
            leg.AddEntry(histo_sieie2,"fake single photons","l")
            leg.Draw()
            histop_sieie.GetXaxis().SetTitle("#sigma_{i#etai#eta}") 
            histop_sieie.GetXaxis().SetNdivisions(4,3,0) 
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

    def plotHistos(self,histlist,title,titlex,template_bins,dim1,doDataMc,logx=False,logy=False,numEntries=None):
        leg = ROOT.TLegend(0.334,0.7,0.75,0.9  )
        leg.SetTextSize(0.03)
        leg.SetTextFont(42);
        leg.SetFillColor(ROOT.kWhite)
       # leg.SetHeader("#%s " % numEntries)
        canv = ROOT.TCanvas(title,title)
        if not doDataMc:
            canv.Divide(1,2)
            canv.cd(1)
            ROOT.gPad.SetPad(0., 0.35, 1., 1.0)
            canv.cd(2)
            ROOT.gPad.SetPad(0., 0., 1., 0.35)
            ROOT.gPad.SetGridy()
        if logy:
            ROOT.gPad.SetLogy()
        if logx:
            ROOT.gPad.SetLogx()
        canv.cd(1)
        # for dataMc plot MC as filled and data as points
        if doDataMc:
            histstart=0
        else:
            histstart=0
        ymax = 0.
        ymin = 1.e+5
        histlist[histstart].GetYaxis().SetLabelSize( histlist[histstart].GetYaxis().GetLabelSize() * canv.GetWh() / ROOT.gPad.GetWh() )
        histlist[histstart].GetXaxis().SetTitle(titlex)
        k=0
        for i in range(histstart,len(histlist)):
            if "mc" in histlist[i].GetName()  or "MC" in histlist[i].GetName():
                histlist[i].SetFillColor(ROOT.kRed+k)
                k+=2
                histlist[i].SetFillStyle(3004)
                histlist[i].SetLineColor(histlist[i].GetFillColor())
                if i==histstart:
                    histlist[i].Draw("E2")
                else:
                    histlist[i].Draw("E2 SAME")
            else:
                histlist[i].SetLineColor(ROOT.kAzure+i)
                histlist[i].SetLineWidth(2)
                histlist[i].SetMarkerColor(ROOT.kAzure+i)
                histlist[i].SetMarkerStyle(20)
                histlist[i].SetMarkerSize(2)
                if i==histstart:
                    histlist[i].Draw("E")
                else:
                    histlist[i].Draw("E SAME")
            leg.AddEntry(histlist[i],histlist[i].GetName(),"l")  
            ymax = max(ymax,histlist[i].GetMaximum())
            if histlist[i].GetMinimum() != 0.:
                ymin = min(ymin,histlist[i].GetMinimum())
            if min(template_bins)==0.: minX=-0.1
            else: minX=min(template_bins)
        histlist[histstart].GetXaxis().SetLimits(minX,max(template_bins))
        histlist[histstart].GetYaxis().SetRangeUser(ymin*0.5,ymax*2.)
        if "unroll" in title:
           histlist[histstart].GetYaxis().SetRangeUser(ymin*0.5,ymax*30.)
        leg.Draw()
        #change for data mc comparison 
        if not doDataMc:
            ratios = []
            canv.cd(2)
            for ihsit,hist in enumerate(histlist[1:]):
                ratios.append( hist.Clone("ratio_%d" % ihsit) )
                ratios[-1].Divide(histlist[0])
            
            ratios[0].GetYaxis().SetTitleSize( histlist[0].GetYaxis().GetTitleSize() * 3.5/3.5 )
            ratios[0].GetYaxis().SetLabelSize( histlist[0].GetYaxis().GetLabelSize() * 6.5/3.5 )
            ratios[0].GetYaxis().SetTitleOffset( histlist[0].GetYaxis().GetTitleOffset() * 6.5/3.5 )
            ratios[0].GetXaxis().SetTitleSize( histlist[0].GetXaxis().GetTitleSize() * 4.5/3.5 )
            ratios[0].GetXaxis().SetLabelSize( histlist[0].GetXaxis().GetLabelSize() * 6.5/3.5 )
            if dim1:
                ratios[0].GetXaxis().SetTitle(title[-17:])
            else:
                ratios[0].GetXaxis().SetTitle("charged isolation")
            ratios[0].Draw()        
            ratios[0].GetYaxis().SetTitle("ratio")
            ratios[0].GetXaxis().SetLimits(-0.1,max(template_bins))
            ratios[0].GetYaxis().SetRangeUser(0.2,1.8)
            for r in ratios[1:]:
                r.Draw("same")
        ROOT.gStyle.SetOptStat(0)
            #  ROOT.gStyle.SetOptTitle(0)
        self.keep( [canv] )
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
            weight_cut="weight < 5." 
            var,var_b=self.getVar(nomFit.get("observable"))
            lowsigRegion=float(nomFit.get("lowerLimitSigRegion"))
            if len(biniso)==4:
                upsigRegion=9.
            elif len(biniso)==3:
                upsigRegion=4.
            else:
                upsigRegion=float(nomFit.get("upperLimitSigRegion"))
            extended_fit=nomFit.get("extended_fit",False)
            observable=self.buildRooVar(var,var_b,recycle=True)
            observable.setRange("sigRegion",lowsigRegion,upsigRegion)
            observable.Print() 
            obsls.add(observable)
             
            #you want to keep bins from 0 to 3
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
            for cat in categories:
                print "-----------------------------------------------------------------"
                if cat=="EEEB": catd="EBEE" 
                else:catd=cat
                data_book=self.rooData("hist2d_forUnrolled")
                data_book.Print()
                unrolledVar=ROOT.RooHistFunc(observable.GetName(),observable.GetName(),isoargs,data_book)
                dodata=nomFit.get("data")
                if dodata:
                    dset="_"
                else:
                    dset="_mc_"
              #get dataset and add column (actually filling values in)
                if dodata:
                    data = self.reducedRooData("data_2D_%s" % (catd),setargs,False,sel=weight_cut, redo=False)
                else:
                    data = self.reducedRooData("mc_2D_%s" % (catd),setargs,False,sel=weight_cut, redo=False)
                data.addColumn(unrolledVar)
                data=data.reduce(ROOT.RooArgSet(mass,observable))
              #  data=data.binnedClone()
                data.Print()
                tree_mass=self.treeData("%s_pp_2D_%s"%(options.plotPurity["treetruth"], cat))
                if not dodata:
                    tp = ROOT.TNtuple("tree_fitresult_fraction%s%s_%s_%s" % (dset,tempname,dim,cat),"tree_fitresult_fraction_%s_%s_%s" % (tempname,dim,cat),"purity_pp:error_pp_sumw2on:error_pp:purity_pf:error_pf_sumw2on:error_pf:massbin:masserror" )
                else:
                    tp = ROOT.TNtuple("tree_fitresult_fraction%s%s_%s_%s" % (dset,tempname,dim,cat),"tree_fitresult_fraction_%s_%s_%s" % (tempname,dim,cat),"purity_pp:error_pp:purity_pf:error_pf:massbin:masserror" )
                self.store_[tp.GetName()] = tp
                if extended_fit:
                    ntp = ROOT.TNtuple("tree_fitresult_events%s%s_%s_%s" % (dset,tempname,dim,cat),"tree_fitresult_events_%s_%s_%s" % (tempname,dim,cat),"norm:purity_pp:error_pp_sumw2off:error_pp_sumw2on:purity_pf:error_pf_sumw2off:error_pf_sumw2on:massbin:masserror" )
                    self.store_[ntp.GetName()] = ntp
                rng= range(0,tree_mass.GetEntries())
                if len(mass_split)== 3:
                    rng=range(mass_split[2],mass_split[1])
                for mb in rng:
                    print "---------------------------------------------------" 
                    tree_mass.GetEntry(mb)
                    cut=ROOT.TCut("mass>%f && mass<%f"% (tree_mass.massbin-tree_mass.masserror,tree_mass.massbin+tree_mass.masserror))
                    cut_s= "%1.0f_%2.0f"%  (tree_mass.massbin-tree_mass.masserror,tree_mass.massbin+tree_mass.masserror)
                    print cut.GetTitle()
                    data_massc=data.reduce(cut.GetTitle())
                    data_massc.Print()
                    #define fit parameters
                    jpp = ROOT.RooRealVar("jpp","jpp",0.6,0.,1.)
                    jpf = ROOT.RooRealVar("jpf","jpf",0.4,0.,1.)
                    if extended_fit:
                        entries= data_massc.sumEntries("templateNdim2d_unroll <= 4.")
                        jnorm = ROOT.RooRealVar("jnorm","jnorm",entries,0.,2.*entries)
                        fpp= ROOT.RooFormulaVar("fpp","fpp","@0*@1 ",ROOT.RooArgList(jnorm,jpp))
                    else:
                        fpp= ROOT.RooFormulaVar("fpp","fpp","jpp ",ROOT.RooArgList(jpp))
                    pu_estimates=ROOT.RooArgList(fpp)
                    pu_estimates_roopdf=ROOT.RooArgList(fpp)
                    if len(components)>2 and not extended_fit: 
                        fpf= ROOT.RooFormulaVar("fpf","fpf","jpf ",ROOT.RooArgList(jpf))
                        pu_estimates.add(fpf)
                    elif extended_fit:
                        if len(components)>2:
                            fpf= ROOT.RooFormulaVar("fpf","fpf","@0*@1 ",ROOT.RooArgList(jnorm,jpf))
                            fff= ROOT.RooFormulaVar("fff","fff","(@0*TMath::Max(0.,(1-@1-@2))) ",ROOT.RooArgList(jnorm,jpp,jpf))
                            pu_estimates_roopdf.add(fpf)
                            pu_estimates_roopdf.add(fff)
                        elif len(components)<3:
                            fpf= ROOT.RooFormulaVar("fpf","fpf","(@0*(1-@1)) ",ROOT.RooArgList(jnorm,jpp))
                            pu_estimates_roopdf.add(fpf)
                    rooPdfs=[]
                    ArgListPdf=ROOT.RooArgList()
                    i=0
                    for comp in nomFit["components"]:
                        print "%s%s%s_%s_%s_mb_%s"%(tempname,dset,comp, dim,cat,cut_s)
                        tempname_new=None
                        dim_new=None
                        if tempname=="unrolled_template_mix" and not dodata:
                            dim_new="2DMC"
                            dset="_"
                        else:
                            dim_new=dim
                        if tempname=="unrolled_mctruth":
                            dset="_"
                        if i==0 and  tempname=="unrolled_template_mix":
                            tempname_new="unrolled_template"
                            dim_new="2D"
                        else: tempname_new=tempname
                        #print "%s%s%s_%s_%s_mb_%s"%(tempname_new,dset,comp, dim_new,cat,cut_s)
                        #return
                        histo = self.rooData("%s%s%s_%s_%s_mb_%s"%(tempname_new,dset,comp, dim_new,cat,cut_s))
                        rooHistPdf=ROOT.RooHistPdf("pdf_%s"% histo.GetName(),"pdf_%s"% histo.GetTitle(),ROOT.RooArgSet(obsls),histo)
                        
                        if options.verbose:
                            histo.Print("v")
                            rooHistPdf.Print()
                        if extended_fit:
                            self.keep([rooHistPdf])
                            rooExtPdf=ROOT.RooExtendPdf("extpdf_%s"% histo.GetName(),"extpdf_%s"% histo.GetTitle(),rooHistPdf,pu_estimates_roopdf[i],"sigRegion")
                            rooExtPdf.Print()
                            rooPdfs.append(rooExtPdf)
                            ArgListPdf.add(rooExtPdf)
                        else:
                            rooPdfs.append(rooHistPdf)
                            ArgListPdf.add(rooHistPdf)
                        i=i+1
                    if options.verbose:
                        ArgListPdf.Print()
                    if extended_fit:
                        fitUnrolledPdf=ROOT.RooAddPdf("fitPdfs_%s%s%s_%s_mb_%s" % (tempname_new,dset,cat,dim_new,cut_s),"fitPdfs_%s_%s_%s_mb_%s" % (tempname_new,cat,dim_new,cut_s),ArgListPdf  )
                    else:
                        fitUnrolledPdf=ROOT.RooAddPdf("fitPdfs_%s%s%s_%s_mb_%s" % (tempname_new,dset,cat,dim_new,cut_s),"fitPdfs_%s_%s_%s_mb_%s" % (tempname_new,cat,dim_new,cut_s),ArgListPdf,pu_estimates  )
                    self.workspace_.rooImport(fitUnrolledPdf)
              #save roofitresult in outputfile
                    fit_studies = fitUnrolledPdf.fitTo(data_massc, RooFit.NumCPU(8),RooFit.Strategy(2),RooFit.Extended(extended_fit),RooFit.SumW2Error(False),RooFit.Save(True))
                    pu_pp=fpp.getParameter("jpp").getVal()
                    err_pp=fpp.getParameter("jpp").getError()
                    if extended_fit:
                        norm=fpp.getParameter("jnorm").getVal()
                        norm_err=fpp.getParameter("jnorm").getError()
                        pu_npp=fpp.getVal()
                        err_npp=fpp.getPropagatedError(fit_mcstudies)
                    if len(components)>2:
                        pu_pf=fpf.getParameter("jpf").getVal()
                        err_pf=fpf.getParameter("jpf").getError()
                        if extended_fit:
                            pu_npf=fpf.getVal()
                            err_npf=fpf.getPropagatedError(fit_mcstudies)
                        covariance_studies=fit_studies.covarianceMatrix()
                        correlation_studies=fit_studies.correlationMatrix()
                        self.workspace_.rooImport(covariance_studies, "covariance_studies")
                        self.workspace_.rooImport(correlation_studies,"correlation_studies")
                        self.workspace_.rooImport(fit_studies,"fit_studies")
                    else: 
                        pu_pf=1-pu_pp
                        print "pu_pf ", pu_pf
                        if extended_fit:
                            pu_npf=1-pu_npp
                            err_npf=0.
                        err_pf=0.
                    print "err_pp " ,err_pp, " err_pf " ,err_pf
                    print
                    self.plotFit(observable,fitUnrolledPdf,rooPdfs,data_massc,components,cat,log=True) 
                    self.plotFit(observable,fitUnrolledPdf,rooPdfs,data_massc,components,cat,log=False)
    #ML fit to weighted dataset: SumW2Error takes statistics of dataset into account, scales with number of events in datasetif ON good for MC comparison, takes limited statistics of MC dataset into account
  #  if OUT treated as if it would be data- for data MC comparison
                    print "-------------------------------------------------------------------------"
                    if not dodata:
                        jpp.setVal(0.8)
                        jpf.setVal(0.2)
                        fit_mcstudies = fitUnrolledPdf.fitTo(data_massc, RooFit.NumCPU(8),RooFit.Strategy(2),RooFit.Extended(extended_fit),RooFit.SumW2Error(True),RooFit.Save(True))
                        if extended_fit: 
                            jnorm.setVal(entries)
                            puerr_npp=fpp.getPropagatedError(fit_mcstudies)
                        puerr_pp=fpp.getParameter("jpp").getError()
                        if len(components)>2:
                            if extended_fit:
                               puerr_npf=fpf.getPropagatedError(fit_mcstudies)
                            puerr_pf=fpf.getParameter("jpf").getError()
                            covariance_mcstudies=fit_mcstudies.covarianceMatrix()
                            correlation_mcstudies=fit_mcstudies.correlationMatrix()
                            self.workspace_.rooImport(covariance_mcstudies,"covariance_mcstudies")
                            self.workspace_.rooImport(correlation_mcstudies,"correlation_mcstudies")
                            self.workspace_.rooImport(fit_mcstudies,"fit_mcstudies")
                        else: 
                            if extended_fit:
                                puerr_npf=0.
                            puerr_pf=0.
                        print "puerr_pp " ,puerr_pp, " puerr_pf " ,puerr_pf
                    if extended_fit:
                        ntp.Fill(norm,pu_npp,puerr_npp,err_npp,pu_npf,puerr_npf,err_npf,tree_mass.massbin,tree_mass.masserror )
                    if not dodata:
                        tp.Fill(pu_pp,puerr_pp,err_pp,pu_pf,puerr_pf,err_pf,tree_mass.massbin,tree_mass.masserror )
                    else:
                        tp.Fill(pu_pp,err_pp,pu_pf,err_pf,tree_mass.massbin,tree_mass.masserror )
                print "done fit ...."
                print 
    ## ---------------#--------------------------------------------------------------------------------------------
    def plotFit(self,roovar,rooaddpdf,roopdfs,data,components,cat,log):
        ROOT.TH1F.SetDefaultSumw2(True)
        b=ROOT.TLatex()
        b.SetNDC()
        b.SetTextSize(0.06)
        b.SetTextColor(ROOT.kRed)
        cFit = ROOT.TCanvas("c%s_%u_%s" %(rooaddpdf.GetName(),len(components),log),"cFit",1200,800)
        leg =ROOT.TLegend(0.5,0.8,0.35,0.9)
        leg.SetTextSize(0.03)
        leg.SetTextFont(42);
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
        rooaddpdf.plotOn(frame,RooFit.Components(roopdfs[1].GetName()),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kCyan+1),RooFit.Name("pf"))
        if len(components)>2:
            rooaddpdf.plotOn(frame,RooFit.Components(roopdfs[2].GetName()),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kBlack),RooFit.Name("ff"))
        frame.Draw()
        leg.AddEntry("fit","fit","l")
        leg.AddEntry("data","data","l")
        leg.AddEntry("pp","prompt-prompt ","l")
        leg.AddEntry("pf","prompt-fake ","l")
        if len(components)>2:
            leg.AddEntry("ff","fake-fake ","l")
        leg.Draw()
        #b.DrawLatex(0.55,0.7,"PRELIMINARY")
        self.keep([cFit])
        self.autosave(True)

    ## ------------------------------------------------------------------------------------------------------------
    def plotPurity(self,options,args):
        
        comp=3
        treetruthname=options.plotPurity["treetruth"]
        dim=options.plotPurity["dimensions"]
        categories = options.plotPurity["categories"]
        closure = options.plot_closure
        data=options.plotPurity.get("data",True)
        purity_values = options.plot_purityvalue
        for opt,pu_val in zip(closure,purity_values):
            for cat in categories:
                print cat
                if not opt=="mctruth":
                    tree_template=self.treeData("fitresult_fraction_unrolled_%s_%s_%s"%(opt,dim, cat))
                    g_templatepp=ROOT.TGraphErrors(tree_template.GetEntries())
                    g_templatepf=ROOT.TGraphErrors(tree_template.GetEntries())
                    nentries=tree_template.GetEntries()
                if not data:
                    if not opt=="mctruth":
                        tree_templatemc=self.treeData("fitresult_fraction_mc_unrolled_%s_%s_%s"%(opt,dim, cat))
                        g_templatemcpp=ROOT.TGraphErrors(tree_templatemc.GetEntries())
                        g_templatemcpf=ROOT.TGraphErrors(tree_templatemc.GetEntries())
                    tree_mctruth=self.treeData("fitresult_fraction_mc_unrolled_mctruth_%s_%s"%( dim, cat))
                    nentries=tree_mctruth.GetEntries()
                    tree_truthpp=self.treeData("%s_pp_%s_%s"%(treetruthname, dim, cat))
                    tree_truthpf=self.treeData("%s_pf_%s_%s"%(treetruthname,dim, cat))
                    tree_truthff=self.treeData("%s_ff_%s_%s"%(treetruthname,dim, cat))
                    if tree_truthff!=None:
                        g_truthff=ROOT.TGraphErrors(tree_truthff.GetEntries())
                    else:
                        g_truthff=ROOT.TGraphErrors()
                        print "no truth ff component"
                    g_mctruthpp=ROOT.TGraphErrors(tree_mctruth.GetEntries())
                    g_mctruthpp_sumw2on=ROOT.TGraphErrors(tree_mctruth.GetEntries())
                    g_truthpp=ROOT.TGraphErrors(tree_truthpp.GetEntries())
                    g_truthpf=ROOT.TGraphErrors(tree_truthpf.GetEntries())
                    g_pullpp=ROOT.TGraphErrors(nentries)
                    g_mctruthpf=ROOT.TGraphErrors(tree_mctruth.GetEntries())
                    g_mctruthpf_sumw2on=ROOT.TGraphErrors(tree_mctruth.GetEntries())
                    g_pullpf=ROOT.TGraphErrors(nentries)
                    h_pullpp=ROOT.TH1F("h_pullpp_%s" % cat,"h_pullpp_%s"% cat,10*tree_truthpp.GetEntries(),-2.,2.)
                    h_pullpf=ROOT.TH1F("h_pullpf_%s" % cat,"h_pullpf_%s" %cat,10*tree_truthpp.GetEntries(),-2.,2.)
                    if ((tree_truthpp.GetEntries()!=nentries)):
                        print "number of entries in trees dont agree"
                for mb in range(0,nentries):
                    if not opt=="mctruth":
                        tree_template.GetEntry(mb)
                        g_templatepf.SetPoint(mb,tree_template.massbin,tree_template.purity_pf)
                        g_templatepf.SetPointError(mb,tree_template.masserror,tree_template.error_pf)
                        g_templatepp.SetPoint(mb,tree_template.massbin,tree_template.purity_pp)
                        g_templatepp.SetPointError(mb,tree_template.masserror,tree_template.error_pp)
                    if not data:
                        if not opt=="mctruth":
                            tree_templatemc.GetEntry(mb)
                            g_templatepfmc.SetPoint(mb,tree_templatemc.massbin,tree_templatemc.purity_pf)
                            g_templatepfmc.SetPointError(mb,tree_templatemc.masserror,tree_templatemc.error_pf)
                            g_templateppmc.SetPoint(mb,tree_templatemc.massbin,tree_templatemc.purity_pp)
                            g_templateppmc.SetPointError(mb,tree_templatemc.masserror,tree_templatemc.error_pp)
                        tree_mctruth.GetEntry(mb)
                        tree_truthpp.GetEntry(mb)
                        tree_truthpf.GetEntry(mb)
                        if tree_truthff!=None:
                            tree_truthff.GetEntry(mb)
                        g_truthpp.SetPoint(mb,tree_truthpp.massbin,tree_truthpp.frac_pu)
                        g_truthpp.SetPointError(mb,tree_truthpp.masserror,0.)
                        g_truthpf.SetPoint(mb,tree_truthpf.massbin,tree_truthpf.frac_pu)
                        g_truthpf.SetPointError(mb,tree_truthpf.masserror,0.)
                        g_truthff.SetPoint(mb,tree_truthff.massbin,tree_truthff.frac_pu)
                        g_truthff.SetPointError(mb,tree_truthff.masserror,0.)
                    
                        g_mctruthpp.SetPoint(mb,tree_mctruth.massbin,tree_mctruth.purity_pp)
                        g_mctruthpp_sumw2on.SetPoint(mb,tree_mctruth.massbin,tree_mctruth.purity_pp)
                        g_mctruthpp.SetPointError(mb,tree_mctruth.masserror,tree_mctruth.error_pp)
                        g_mctruthpp_sumw2on.SetPointError(mb,tree_mctruth.masserror,tree_mctruth.error_pp_sumw2on)
                        if opt=="template" or opt=="template_mix":
                            pullpp=(tree_templatemc.purity_pp-tree_truthpp.frac_pu)/tree_templatemc.error_pp_sumw2on
                        elif opt=="mctruth":
                            pullpp=(tree_mctruth.purity_pp-tree_truthpp.frac_pu)/tree_mctruth.error_pp_sumw2on
                        else:print "dont know what to compare to truth"
                        print  "tree_mctruth.purity_pp ", tree_mctruth.purity_pp, "tree_mctruth.error_pp ", tree_mctruth.error_pp, "pull pp", pullpp
                        print "tree_mctruth.error_pp_sumw2on ", tree_mctruth.error_pp_sumw2on
                        g_pullpp.SetPoint(mb,tree_mctruth.massbin,pullpp)
                        h_pullpp.Fill(pullpp)
                        g_mctruthpf.SetPoint(mb,tree_mctruth.massbin,tree_mctruth.purity_pf)
                        g_mctruthpf_sumw2on.SetPoint(mb,tree_mctruth.massbin,tree_mctruth.purity_pf)
                        if tree_mctruth.error_pf_sumw2on ==0:
                            g_mctruthpf.SetPointError(mb,tree_mctruth.masserror,0.)
                            g_mctruthpf_sumw2on.SetPointError(mb,tree_mctruth.masserror,0.)

                        else: 
                            g_mctruthpf.SetPointError(mb,tree_mctruth.masserror,tree_mctruth.error_pf)
                            g_mctruthpf_sumw2on.SetPointError(mb,tree_mctruth.masserror,tree_mctruth.error_pf_sumw2on)
                            print  " tree_mctruth.purity_pf ",tree_mctruth.purity_pf, " tree_mctruth.error_pf_sumw2on ",tree_mctruth.error_pf_sumw2on
                            print " tree_mctruth.error_pf_sumw2on ",tree_mctruth.error_pf_sumw2on
                            if opt=="template" or opt=="template_mix":
                                pullpf=(tree_templatemc.purity_pf-tree_truthpf.frac_pu)/tree_templatemc.error_pf_sumw2on
                            elif opt=="mctruth":
                                pullpf=(tree_mctruth.purity_pf-tree_truthpf.frac_pu)/tree_mctruth.error_pf_sumw2on
                            g_pullpf.SetPoint(mb,tree_templatemc.massbin,pullpf)
                            h_pullpf.Fill(pullpf)
                    print "tree_truth fractions: ",  tree_truthff.frac_pu, tree_truthpf.frac_pu, tree_truthpp.frac_pu
                self.pullFunction(g_pullpp,h_pullpp,cat,"pp",opt,pu_val)
                if not data:
                    if tree_mctruth.error_pf_sumw2on !=0:
                        self.pullFunction(g_pullpf,h_pullpf,cat,"pf",opt,pu_val)
                    sumw2on="sumw2on"
                    if opt=="mctruth":
                        self.plotPurityMassbins(cat,pu_val,opt,sumw2on,None,None,g_pullpp,g_truthpp,g_truthpf,g_truthff,g_mctruthpp_sumw2on,g_mctruthpf_sumw2on)

                        sumw2off="sumw2off"
                        self.plotPurityMassbins(cat,pu_val,opt,sumw2off,None,None,None,g_truthpp,g_truthpf,g_truthff,g_mctruthpp,g_mctruthpf)
                else:
                    self.plotPurityMassbins(cat,pu_val,opt,"data",g_templatepp,g_templatepf)
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
        ROOT.gPad.SetPad(0., 0., 1., 0.5)
        ROOT.gPad.SetGridx()
        ROOT.gPad.SetGridy()
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
    def plotPurityMassbins(self,cat,pu_val,opt,opt2,g_templatepp=None,g_templatepf=None,g_ratiopp=None,g_truthpp=None,g_truthpf=None,g_truthff=None,g_mctruthpp=None,g_mctruthpf=None,g_ratiopf=None):
        leg = ROOT.TLegend(0.6,0.6,0.8,0.9)
        cpu = ROOT.TCanvas("cpu_%s_%s_%s_%s" % (opt,cat,pu_val,opt2),"cpu_%s_%s_%s_%s" %(opt,cat,pu_val,opt2))
        if not (opt2=="data" or opt2=="sumw2off") :
            cpu.Divide(1,2)
            cpu.cd(1)
            ROOT.gPad.SetPad(0., 0.4, 1., 1.0)
            ROOT.gPad.SetLogx()
            ROOT.gPad.SetGridx()
            ROOT.gPad.SetTicky()
            ROOT.gPad.SetGridy()
            cpu.cd(2)
            ROOT.gPad.SetPad(0., 0., 1., 0.4)
            
        ROOT.gPad.SetTicky()
        ROOT.gPad.SetGridx()
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetLogx()
        cpu.cd(1)
        if not opt=="mctruth":
            g_templatepp.SetMarkerColor(ROOT.kBlue+1)
            g_templatepp.SetLineColor(ROOT.kBlue+1)
            g_templatepp.SetMarkerSize(1.3)
            g_templatepp.SetMarkerStyle(20)
            g_templatepp.GetXaxis().SetTitle("Diphoton mass [GeV]")
            g_templatepp.GetYaxis().SetTitle("purity")
            g_templatepp.GetYaxis().SetRangeUser(0.,1.6)
            g_templatepp.GetXaxis().SetLimits(200.,15000.)
            g_templatepp.Draw("AP")
        if not opt2=="data":
            g_truthpp.SetMarkerColor(ROOT.kYellow+2)
            g_truthpp.SetLineColor(ROOT.kYellow+2)
            g_truthpf.SetMarkerColor(ROOT.kGreen+1)
            g_truthpf.SetLineColor(ROOT.kGreen+1)
            g_truthff.SetMarkerColor(ROOT.kGreen+3)
            g_truthff.SetLineColor(ROOT.kGreen+3)
            g_mctruthpp.SetMarkerColor(ROOT.kRed)
            g_mctruthpp.SetLineColor(ROOT.kRed)
            g_mctruthpp.SetMarkerStyle(20)
            g_truthpp.SetMarkerStyle(20)
            g_truthpf.SetMarkerStyle(20)
            g_truthff.SetMarkerStyle(20)
            g_mctruthpp.SetMarkerSize(1.3)
            if opt=="mctruth":
                g_mctruthpp.GetXaxis().SetTitle("Diphoton mass [GeV]")
                g_mctruthpp.GetYaxis().SetTitle("purity")
                g_mctruthpp.GetYaxis().SetRangeUser(0.,1.6)
                g_mctruthpp.GetXaxis().SetLimits(200.,15000.)
                g_mctruthpp.Draw("AP")
                leg.AddEntry(g_mctruthpp,"pp mctruth template","lp")  
                g_mctruthpf.Draw("P SAME")
                leg.AddEntry(g_mctruthpf,"pf mctruth template","lp")
            leg.AddEntry(g_truthpp,"pp truth","lp")  
            leg.AddEntry(g_truthpf,"pf truth","lp")  
            leg.AddEntry(g_truthff,"ff truth","lp")  
            g_truthpp.Draw("P SAME")
            g_truthpf.Draw("P SAME")
            g_truthff.Draw("P SAME")
            g_mctruthpf.SetMarkerColor(ROOT.kOrange+7)
            g_mctruthpf.SetLineColor(ROOT.kOrange+7)
            g_mctruthpf.SetMarkerStyle(20)
            g_mctruthpf.SetMarkerSize(1.3)
        if not opt=="mctruth":
            g_templatepf.Draw("P SAME")
            leg.AddEntry(g_templatepp,"pp template","lp")  
            leg.AddEntry(g_templatepf,"pf %s"% opt,"pl")  
            g_templatepf.SetMarkerColor(ROOT.kBlack)
            g_templatepf.SetLineColor(ROOT.kBlack)
            g_templatepf.SetMarkerStyle(20)
            g_templatepf.SetMarkerSize(1.3)  
            
        leg.Draw()
        if not (opt2=="data" or opt2=="sumw2off"):
            g_ratiopp.SetMarkerStyle(20)
            cpu.cd(2)
            if opt=="mctruth":
                g_ratiopp.SetMarkerColor(g_mctruthpp.GetMarkerColor())
                g_ratiopp.SetLineColor(g_mctruthpp.GetLineColor())
                if g_ratiopf!=None:
                    g_ratiopf.SetMarkerColor(g_mctruthpf.GetMarkerColor())
                    g_ratiopf.SetMarkerColor(g_mctruthpf.GetMarkerColor())
            else:
                g_ratiopp.SetMarkerColor(g_templatepp.GetMarkerColor())
                g_ratiopp.SetLineColor(g_templatepp.GetLineColor())
                if g_ratiopf!=None:
                    g_ratiopf.SetMarkerColor(g_templatepf.GetMarkerColor())
                    g_ratiopf.SetLineColor(g_templatepf.GetLineColor())
            g_ratiopp.GetXaxis().SetTitle("Diphoton mass [GeV]")
        #    g_ratiopp.GetYaxis().SetTitle("(pu_tp-pu_mctruth)/pu_tperr")
            g_ratiopp.GetYaxis().SetTitle("pull fct")
        
            g_ratiopp.GetYaxis().SetRangeUser(-3.,3.)
           # g_ratiopp.GetXaxis().SetLimits(g_mctruthpp.GetXaxis().GetBinLowEdge(g_mctruthpp.GetXaxis.GetFirst()),g_mctruthpp.GetXaxis().GetBinUpEdge(g_mctruthpp.GetXaxis(g_mctruthpp.GetXaxis.GetLast())))
            g_ratiopp.GetYaxis().SetTitleSize( g_mctruthpp.GetYaxis().GetTitleSize() *4.5/4. )
            g_ratiopp.GetYaxis().SetLabelSize( g_mctruthpp.GetYaxis().GetLabelSize()*6./4.  )
            g_ratiopp.GetYaxis().SetTitleOffset(g_mctruthpp.GetYaxis().GetTitleOffset()*4.5/4. )
            g_ratiopp.GetXaxis().SetTitleSize( g_mctruthpp.GetXaxis().GetTitleSize() *5./4. )
            g_ratiopp.GetXaxis().SetLabelSize( g_mctruthpp.GetXaxis().GetLabelSize()*6./4. )
            g_ratiopp.Draw("AP")
            g_ratiopp.GetXaxis().SetLimits(350.,15000.)
            g_ratiopp.Draw("AP")
            if g_ratiopf!=None:
                g_ratiopf.SetMarkerStyle(20)
                g_ratiopf.Draw("P SAME")
                self.keep( [g_mctruthpf,g_ratiopf] )
            self.keep( [g_mctruthpp,g_ratiopp] )
        self.keep( [cpu,g_templatepp,g_templatepf] )
        self.autosave(True)
        ## ------------------------------------------------------------------------------------------------------------
    def prepareTemplates(self,options,args):
        
        fout = self.openOut(options)
        self.workspace_ = ROOT.RooWorkspace("wtemplates","wtemplates")
        tmp = fout
        ## read input trees
        self.datasets_["data"] = self.openDataset(None,options.data_file,options.infile,options.data)
        self.datasets_["templates"]   = self.openDataset(None,options.data_file,options.infile,options.templates)
        if not options.prep_data:
            self.datasets_["mc"]   = self.openDataset(None,options.mc_file,options.infile,options.mc)
            self.datasets_["templatesMC"]   = self.openDataset(None,options.mc_file,options.infile,options.templatesMC)
       
        if not (options.prep_data or options.prep_nosig):
            for name,trees in options.signals.iteritems():
                self.datasets_[name] = self.openDataset(None,options.mc_file,options.infile,trees)        
            # used by parent class PlotApp to read in objects
        self.template_ = options.treeName
        
        self.groups = options.groups
        if options.groups:
            self.categories_ = options.groups.keys()
        else:
            self.categories_ = options.categories
            
        ## create output workspace
        ## self.workspace_.rooImport = getattr(self.workspace_,"import")
        self.workspace_.rooImport = rooImport(self.workspace_)

        ## read and store list of aliases. will be defined later in all trees
        for var in options.aliases:
            self.getVar(var)
        
        ## define list of variables for the dataset
        varlist = ROOT.RooArgList()
        weight  = self.getVar(options.weight_expression)[0]
        for var in options.dataset_variables+[weight]:
            name, binning = self.getVar(var)
            rooVar = self.buildRooVar(name,binning)
            varlist.add(rooVar)
            
        ## loop over configured fits
        for name, fit in options.fits.iteritems():
            if name.startswith("_"): continue
            print
            print "--------------------------------------------------------------------------------------------------------------------------"
            print "Preparing fit %s" % name
            print 
            
            ndim            = fit["ndim"]
            bins            = fit["bins"]
            components      = fit["components"]
            categories      = fit["categories"]
            if not options.prep_data:
                truth_selection = fit["truth_selection"]
                if not options.prep_nosig:
                    signals         = fit.get("signals",[])
                    if signals == "__all__":
                        signals = options.signals.keys()
                        fit["signals"] = signals
            template_binning = array.array('d',fit["template_binning"])
            templates       = fit["templates"]
            storeTrees      = fit.get("store_trees",False)
            selection       = fit.get("selection",options.selection)
            preselection    = fit.get("preselection",options.preselection)
            
            variables       = fit.get("dataset_variables",[])
            
            fulllist = varlist.Clone()
            for var in variables:
                vname, binning = self.getVar(var)
                rooVar = self.buildRooVar(vname,binning)
                fulllist.add(rooVar)
            
            for dim in range(ndim):
                dimVar = self.buildRooVar("templateNdim%dDim%d" % (ndim,dim),template_binning)
                fulllist.add( dimVar )
            print "Will put the following variables in the dataset : "
            fulllist.Print()
            
            print "Number of dimensions : %d" % ndim
            print "Components           : %s" % ",".join(components)
            print 
            
            tmp.cd()
            
            ## prepare data
            dataTrees = self.prepareTrees("data",selection,options.verbose,"Data trees")
            self.buildRooDataSet(dataTrees,"data",name,fit,categories,fulllist,weight,preselection,storeTrees)
            for cat in categories.keys():
                print "dataset - %s" % (cat), self.rooData("data_%s_%s" % (name,cat) ).sumEntries()
                print "number of entries data - %s" % (cat), self.rooData("data_%s_%s" % (name,cat) ).numEntries()
          ## prepare mc
            if not options.prep_data:
                mcTrees =  self.prepareTrees("mc",selection,options.verbose,"MC trees")
                self.buildRooDataSet(mcTrees,"mc",name,fit,categories,fulllist,weight,preselection,storeTrees)
          
          ## prepare signal
            if not (options.prep_data or options.prep_nosig):
                for sig in signals:
                    sigTrees =  self.prepareTrees(sig,selection,options.verbose,"Signal %s trees" % sig)
                    self.buildRooDataSet(sigTrees,sig,name,fit,categories,fulllist,weight,preselection,storeTrees)
            
          ## prepare truth templates
            if not options.prep_data:
                for truth,sel in truth_selection.iteritems():
                    cut = ROOT.TCut(preselection)
                    cut *= ROOT.TCut(sel)
                    legs = [""]
                    if "legs" in fit:
                        legs = fit["legs"]
                    self.buildRooDataSet(mcTrees,"mctruth_%s" % truth,name,fit,categories,fulllist,weight,cut.GetTitle(),storeTrees)
          
              
            print
          ## sanity check
            if not options.prep_data:
                for cat in categories.keys():
                    catCounts = {}
                    catCounts["tot"] = self.rooData("mc_%s_%s" % (name,cat) ).sumEntries()
                  
                    breakDown = 0.
                    for truth in truth_selection.keys():
                        count = self.rooData("mctruth_%s_%s_%s" % (truth,name,cat) ).sumEntries()
                        breakDown += count
                        catCounts[truth] = count
                    print "truth : ",cat, " ".join( "%s : %1.4g" % (key,val) for key,val in catCounts.iteritems() ),
                    if breakDown != catCounts["tot"]:
                        print "\n   Warning : total MC counts don't match sum of truths. Difference: ", catCounts["tot"]-breakDown
                    else:
                        print
                      
            ## prepare templates
            print 
            for component,cfg in fit["templates"].iteritems():
                if component.startswith("_"): continue
              #templates (data) is default one
                for dat in cfg.get("dataset","templates"):
                    print dat
                    trees = self.prepareTrees(dat,cfg["sel"],options.verbose,"Templates selection for %s %s" % (dat,component))
                    if dat=="data" or dat=="templates":
                        dat="_"
                    elif dat=="templatesMC" or dat=="mc":
                        dat="_mc_"
                    cats = {}
                    presel = cfg.get("presel",preselection)
                    for cat,fill in cfg["fill_categories"].iteritems():
                        if cat.startswith("_"): continue
                        config = { "src" : categories[cat]["src"],
                                   "fill": fill
                                   }
                        cats[cat] = config
                    self.buildRooDataSet(trees,"template%s%s" % (dat,component),name,fit,cats,fulllist,weight,presel,storeTrees)
                    
                    for cat in categories.keys():
                        tree=self.treeData("template%s%s_%s_%s" % (dat,component,name,cat) )
                        print "template -%s - %s" % (component,cat), self.rooData("template%s%s_%s_%s" % (dat,component,name,cat) ).sumEntries()
                        print "number of entries template %s - %s" % (component,cat), self.rooData("template%s%s_%s_%s" % (dat,component,name,cat) ).numEntries()
                    print 
                    print "--------------------------------------------------------------------------------------------------------------------------"
                    print
                

        if options.mix_templates:
            self.doMixTemplates(options,args)

        self.saveWs(options,fout)
    
    ## ------------------------------------------------------------------------------------------------------------
    def mixTemplates(self,options,args):
        fout = self.openOut(options)
        fout.Print()
        fout.cd()
        self.doMixTemplates(options,args)
        self.saveWs(options,fout)
    
    ## ------------------------------------------------------------------------------------------------------------
    def doMixTemplates(self,options,args):
        
        print
        print "--------------------------------------------------------------------------------------------------------------------------"
        print "Mixing templates "
        print 
        
        for name, mix in options.mix.iteritems():
            if name.startswith("_"): continue
            print
            print "--------------------------------------------------------------------------------------------------------------------------"
            print "Mixing %s" % name
            print 

            targetName      = mix["target"]
            targetSrc       = "data"
            jks              = mix.get("jk_source",0)
            if ":" in targetName:
                targetName, targetSrc = targetName.split(":")
            targetFit       = options.fits[targetName]
            ndim            = targetFit["ndim"]
            ## categories      = target["categories"]
            
            ptLeadMin       = mix["ptLeadMin"]
            ptSubleadMin    = mix["ptSubleadMin"]
            massMin         = mix["massMin"]
            mixType         = mix.get("type","simple") 

            pt              = mix["pt"]
            eta             = mix["eta"]
            phi             = mix["phi"]
            energy          = mix["energy"]
            replace         = mix["replace"]
            fill_categories = mix["fill_categories"]
            if mixType == "simple":
                matchVars = ROOT.RooArgList() # FIXME
                for var,thr in mix["match"].iteritems():
                    var = self.buildRooVar(var,[])
                    var.setVal(thr)
                    matchVars.add(var)

            elif mixType == "kdtree":
                pass
            else:
                sys.exit(-1,"Uknown event mixing type %s" % mixType)
  
            if ndim != 2:
                sys.exit(-1,"can only do event mixing with two objects")

            sources = {}
            print "Source templates: "            
            for comp,source in mix["sources"].iteritems():
                print comp, ":", " ".join(source)
                sources[comp] = [ s.split(":") for s in source ] 
            print

            for cat, fill in fill_categories.iteritems():
                if cat.startswith("_"): continue
                print
                print "Filling category :", cat
                for comp,source in sources.iteritems():
                    legs = []
                    legnams = []
                    print
                    print "Component :", comp
                    for leg,src in zip(fill["legs"],source):
                        if len(src) == 2:
                            sname,scomp = src
                            if "mc" in src:
                                stype = "template_mc"
                            else:
                                stype = "template"
                        else:
                            sname,stype,scomp = src
                        legname = "%s_%s_%s_%s" % (stype,scomp,sname,leg)
                        legnams.append( legname )
                        legs.append( (self.treeData(legname),ROOT.RooArgList(self.dsetVars(legname)) ) )
                        if jks !=0 and scomp!="p":
                            tree_all=self.treeData(legname)
                            n= int(tree_all.GetEntries())
                            d=jks*n
                            g=n/d
                            if n % d != 0:
                                g += 1
                            g=int(g)
                            print "computing partitions: n=%d d=%d g=%i" % (n,d,g)
                            all_events= range(n)
                            random.shuffle(all_events)
                            for j in range(g):
                                lo=int(1+d*j)
                                hi=int(d+d*j)
                                tree_temp=tree_all.CloneTree(0)
                                tree_temp.SetName("%s_%i" %(legname,j))
                                for k in all_events:
                                    if not(k>= lo and k < hi ): tree_temp.Fill(tree_all.GetEntry(k))
                                legnams.append( tree_temp.GetName() )
                                legs.append( ( tree_temp,ROOT.RooArgList(self.dsetVars(legname)) ) )
                    if len(legs) != ndim and jks==0:
                        sys.exit(-1,"number of legs does not match number of dimensions for dataset mixing")
                    rndswap     = fill.get("rndswap",False)
                    rndmatch     = fill.get("rndmatch",0.)
                    
                    print "legs  :", " ".join(legnams)
                    print "type  :", mixType
                    if jks==0: g=0
                    for j in range(g+1):
                        if j==0:
                            (tree1, vars1)= legs[0]
                            (tree2, vars2)  = legs[g+1]
                        if len(legs)==ndim*g+2:
                            (tree1, vars1)= legs[j]
                            (tree2, vars2)  = legs[g+1+j]
                        elif len(legs) <ndim*g+2:
                            (tree1, vars1)= legs[0]
                            (tree2, vars2)  = legs[j+1]
                        else: "legs not correctly assigned to trees"
                        print tree1, tree2
                        print "----------------"
                    for j in range(0,g+1):
                        #variables to keep from target after mixing
                        constVariables        = mix["transfer_variables"]
                        varsT=ROOT.RooArgList()
                        for element in constVariables:
                            el = self.buildRooVar(*(self.getVar(element)))
                            varsT.add(el)
                        
                        
                        if mixType == "simple":
                            maxEvents   = fill.get("maxEvents",-1)
                            matchEffMap = fill.get("matchEff",{})
                            matchEff    = matchEffMap.get(comp,1.)
                            print "maxEvents :", maxEvents, "rndswap :", rndswap, "mathcEffMap"
                            mixer.fillFromTree(tree1,tree2,pt,eta,phi,energy,pt,eta,phi,energy,matchVars,rndswap,maxEvents,matchEff)
                            
                        elif mixType == "kdtree":
                            targetCat           = fill.get("targetCat",cat)
                            targetFraction      = fill.get("targetFraction",0.)
                            jkt                 = mix.get("jk_target",0)
                            nNeigh              = fill.get("nNeigh",10)
                            nMinNeigh           = fill.get("nMinNeigh",nNeigh)
                            useCdfDistance      = fill.get("useCdfDistance",False)
                            matchWithThreshold  = fill.get("matchWithThreshold",False)
                            targetWeight        = fill.get("targetWeight","weight")
                            maxWeightTarget     = fill.get("maxWeightTarget",0.)
                            maxWeightCache      = fill.get("maxWeightCache",0.)
                            dataname            = "%s_%s_%s" % (targetSrc,targetName,targetCat)       
                            print dataname
                            targets     = []
                            # only if single photon datasets the full ones
                            targets.append(self.treeData(dataname))
                            if j==0 and jkt!=0:
                                target_all          = self.treeData(dataname)
                                nt= int(target_all.GetEntries())
                                dt=jkt*nt
                                gt=nt/dt
                                if nt % dt != 0:
                                    gt += 1
                                gt=int(gt)
                                print "computing partitions for target: nt=%d dt=%d gt=%i" % (nt,dt,gt)
                                all_eventst= range(nt)
                                random.shuffle(all_eventst)
                                for jt in range(gt):
                                    lot=int(1+dt*jt)
                                    hit=int(dt+dt*jt)
                                    tree_tempt=target_all.CloneTree(0)
                                    tree_tempt.SetName("%s_%i" %(dataname,jt))
                                    for kt in all_eventst:
                                        if not(kt>= lot and kt < hit ): tree_tempt.Fill(target_all.GetEntry(kt))
                                    targets.append( tree_tempt )

                                #  target          = self.treeData(dataname)
                        print targets
                        
                        matchVars1   = ROOT.RooArgList()
                        matchVars2   = ROOT.RooArgList()
                        targetMatch1 = ROOT.RooArgList()
                        targetMatch2 = ROOT.RooArgList()
                        for var in fill["match1"]:
                            var = self.buildRooVar(var,[])
                            matchVars1.add(var)
                        for var in fill["match2"]:
                            var = self.buildRooVar(var,[])
                            matchVars2.add(var)
                        for var in fill["target1"]:
                            var = self.buildRooVar(*(self.getVar(var)))
                            targetMatch1.add(var)
                        for var in fill["target2"]:
                            var = self.buildRooVar(*(self.getVar(var)))
                            targetMatch2.add(var)
                        axesWeights     = fill.get( "axesWeights", [1.]*len(fill["match1"]) )
                        print "rndswap :", rndswap, " rndmatch :", rndmatch," useCdfDistance :", useCdfDistance, "matchWithThreshold :", matchWithThreshold
                        print "nNeigh :", nNeigh, "nMinNeigh :", nMinNeigh
                        print "axesWeights :", axesWeights
                        m=0
                        for target in targets:

                            print "------------------------------------------"
                            print "target :", target.GetName()
                            if      m==0 and j==0:   mixername="template_mix_%s_%s_%s" % ( comp,name, cat)
                            elif    m>0 and j==0:    mixername="template_mix_%s_%s_%i_%s" % ( comp,name, m-1,cat)
                            elif    m==0 and j>0:    mixername="template_mix_%s_%i_%s_%s" % ( comp,j-1,name,cat)
                            mixer = ROOT.DataSetMixer( mixername,mixername,
                                                   vars1, vars2, varsT,replace, replace,
                                                   ptLeadMin, ptSubleadMin, massMin,
                                                   "weight", "weight", True,                                               
                                                   )
                            mixer.fillLikeTarget(target,targetMatch1,targetMatch2,targetWeight,tree1,tree2,
                                             pt,eta,phi,energy,pt,eta,phi,energy,
                                             matchVars1,matchVars2,rndswap,rndmatch,nNeigh,nMinNeigh,targetFraction,
                                             useCdfDistance,matchWithThreshold, maxWeightTarget,maxWeightCache,
                                             array.array('d',axesWeights))
                    
                            dataset = mixer.get()
                            dataset.GetName()
                            self.workspace_.rooImport(dataset,ROOT.RooFit.RecycleConflictNodes())
                            tree = mixer.getTree()
                            print tree.GetName()
                            print "------------------------------------------"
                            print "------------------------------------------"
                            self.store_[tree.GetName()] = tree
                            m=m+1

                print 
                print "--------------------------------------------------------------------------------------------------------------------------"
                print 


    ## ------------------------------------------------------------------------------------------------------------
    def bookNewWs(self,keepOld=True):
        if keepOld:
            self.workspace_input_.append(self.workspace_)
        self.workspace_ = ROOT.RooWorkspace("wtemplates","wtemplates")
        ## self.workspace_.rooImport = getattr(self.workspace_,"import")
        self.workspace_.rooImport = rooImport(self.workspace_)
        
    
    ## ------------------------------------------------------------------------------------------------------------
    def setAliases(self,tree):
        """ Define all aliases in tees
        """
        for var,vdef in self.aliases_.iteritems():
            tree.SetAlias(var,vdef)
    

    ## ------------------------------------------------------------------------------------------------------------
    def reducedRooData(self,name,rooset,binned=False,weight="weight",sel=None,redo=False,importToWs=True):
        data = self.rooData("reduced_%s" % name,quiet=True)
        if not data or redo:
            data = self.rooData(name,rooset=rooset,weight=weight,sel=sel,redo=redo)
            if binned:
                data = data.binnedClone("reduced_%s" % name,"reduced_%s" % name)
            else:
                data.SetName("reduced_%s" % name)
        if importToWs:
            self.workspace_.rooImport(data)
        return data

    ## ------------------------------------------------------------------------------------------------------------
    def rooPdf(self,name,importToWs=False):
        pdf = self.workspace_.pdf(name)
        if not pdf and self.store_new_:
            pdf = self.workspace_input_.pdf(name)            
        if importToWs:
            self.workspace_.rooImport(pdf)
        return pdf

    ## ------------------------------------------------------------------------------------------------------------
    def rooFunc(self,name):
        rooHistFunc = self.workspace_.function(name)
        if not rooHistFunc and self.store_new_:
            rooHistFunc = self.workspace_input_.function(name)            
        if not rooHistFunc:
            print "Warning failed to read %s" % name
            self.workspace_.Print()
            self.workspace_input_.Print()
        return rooHistFunc



    ## ------------------------------------------------------------------------------------------------------------
    def rooData(self,name,autofill=True,rooset=None,weight="weight",sel=None,redo=False,quiet=False):
        if name in self.cache_ and not redo:
            return self.cache_[name]        
        dataset = self.workspace_.data(name)
        if not dataset and self.store_new_:
            dataset = self.workspace_input_.data(name)
            if self.store_inputs_ and dataset:
                self.workspace_.rooImport(dataset)
                
        if not dataset:
            if not quiet:
                print "warning : dataset %s not found" % name
                self.workspace_.Print()
                self.workspace_input_.Print()
            return dataset

        if autofill and dataset.sumEntries() == 0.:
            tree = self.treeData(name)
            if not tree: 
                return dataset
            if rooset:
                dataset = dataset.reduce(RooFit.SelectVars(rooset))
            else:
                dataset = dataset.emptyClone()                
            if not redo:
                self.cache_[name] = dataset
            filler = ROOT.DataSetFiller(dataset)
            cut=ROOT.TCut(weight)
            if sel:
                cut *=sel
            filler.fillFromTree(tree,cut.GetTitle(),True)          
        elif sel or rooset:
            if rooset and sel:
                dataset = dataset.reduce(rooset,sel)
            elif rooset:
                dataset = dataset.reduce(rooset)
            elif sel:
                dataset = dataset.reduce(sel)
        
        return dataset

    ## ------------------------------------------------------------------------------------------------------------
    def treeData(self,name):
        if "tree_%s" % name in self.store_:
            return self.store_["tree_%s" % name]
        elif self.store_new_ and "tree_%s" % name in self.store_input_:
            rt = self.store_input_["tree_%s" % name]
            if self.store_inputs_:
                self.store_["tree_%s" % name] = rt
            return rt
        return None
        
    ## ------------------------------------------------------------------------------------------------------------
    def dsetVars(self,name):
        st = self.workspace_.set("variables_%s" %name)
        if not st and self.store_new_:
            st = self.workspace_input_.set("variables_%s" %name)
            if self.store_inputs_:
                self.workspace_.defineSet("variables_%s" %name,st)
        return st

    ## ------------------------------------------------------------------------------------------------------------
    def getVar(self,var):
        """ 
        Parse variable definition
        General form:
        'var := expression [binning]'
        ':= expression' can be omitted if the variable already exists in trees.
        '[binning]' is also optional and can be specified as [nbins,min,max] or list of boundaires.
        """
        if "[" in var:
            name,binning = var.rstrip("-").rstrip("]").rsplit("[",1)
            
            if "," in binning:
                binning = binning.split(",")
            else:
                binning = binning.split(":")
            if len(binning) == 3:
                nbins = int(binning[0])
                xmin = float(binning[1])
                xmax = float(binning[2])
                step = ( xmax - xmin ) / float(nbins)
                xbins = array.array('d',[xmin+step*float(ib) for ib in range(nbins+1)])
            else:
                xbins = array.array('d',[float(b) for b in binning])
        else:
            name,xbins = var.rstrip("-"),[]

        if ":=" in name:
            name,vdef = [ t.lstrip(" ").rstrip(" ").lstrip("\t").rstrip("\t") for t in name.split(":=",1) ]
            self.aliases_[name] = vdef
            
        name = name.lstrip(" ").rstrip(" ").lstrip("\t").rstrip("\t")
        if len(xbins) == 0 and name in self.variables_:
            xbins = self.variables_[name]
        else:
            self.variables_[name] = xbins
        return name,xbins

    ## ------------------------------------------------------------------------------------------------------------
    def rooVar(self,name):
        rooVar = self.workspace_.var(name)
        if not rooVar and self.store_new_:
            rooVar = self.workspace_input_.var(name)
        return rooVar
        
    ## ------------------------------------------------------------------------------------------------------------
    def buildRooVar(self,name,binning,importToWs=True,recycle=False):
        rooVar = None
        if recycle:
            rooVar = self.workspace_.var(name)
            if not rooVar and self.store_new_:
                rooVar = self.workspace_input_.var(name)
        if not rooVar:
            if name in self.aliases_:
                title = self.aliases_[name]
            else:
                title = name
            rooVar = ROOT.RooRealVar(name,title,0.)
            rooVar.setConstant(False)

        if len(binning) > 0:
            val = None
            if len(binning)==1 or len(binning)>2 and binning[0]>=min(binning[1:]):
                rooVar.setVal(binning[0])
                binning = binning[1:]
            else:
                rooVar.setVal(0.5*(binning[0]+binning[-1]))
            if len(binning) > 1:
                rooVar.setMin(binning[0])
                rooVar.setMax(binning[-1])

                rooVar.setBinning(ROOT.RooBinning(len(binning)-1,array.array('d',binning)))
        if importToWs:
            self.workspace_.rooImport(rooVar,ROOT.RooFit.RecycleConflictNodes())
        self.keep(rooVar) ## make sure the variable is not destroyed by the garbage collector
        return rooVar

    ## ------------------------------------------------------------------------------------------------------------
    def buildRooDataSet(self,trees,name,fitname,fit,categories,fulllist,weight,preselection,storeTrees):
        """ Build per-category RooDataSet starting from trees
        """
        # define loop over legs
        legs = [""]
        redef = []        
        if "legs" in fit:
            legs = fit["legs"]
            redef = [ fulllist[ivar].GetTitle()  for ivar in range(fulllist.getSize() ) ]

        ## fill datasets
        for catname,cfg in categories.iteritems():
            filler = ROOT.DataSetFiller( "%s_%s_%s" % (name,fitname,catname), "%s_%s_%s" % (name,fitname,catname), fulllist, weight, storeTrees )
            
            ## source category
            src = trees[cfg["src"]]
            
            ## filling directives
            fill  = cfg["fill"]

            ## loop over directives 
            for cut,variables in fill.iteritems():
                # assume template vars are at the end
                firstVar = fulllist.getSize()-len(variables)
                ## loop over all legs
                for leg in legs:
                    ## adapt the definition of all variables
                    for ired, red in enumerate(redef):
                        filler.vars()[ired].SetTitle(red % {"leg" : leg})
                    ## adapt the definition of the template variables
                    for ivar,var in enumerate(variables):
                        filler.vars()[firstVar+ivar].SetTitle(var % {"leg" : leg})
                
                    ## compute weight as preselection*cut*weight
                    wei  = ROOT.TCut(preselection)
                    wei *= ROOT.TCut(cut)
                    wei *= ROOT.TCut(weight)
                    ## fill dataset from source trees
                    for tree in src:
                        twei = wei.GetTitle() % {"leg" : leg}
                        ## this will actually discard all events with weight 0 
                        ##   or outside of the range of any variable in fulllist
                        filler.fillFromTree(tree,twei)
            
            # restore variables definition
            for ired, red in enumerate(redef):
                fulllist[ired].SetTitle(red)
                
            ## and we are done
            dataset = filler.get()
            self.workspace_.rooImport(dataset,ROOT.RooFit.RecycleConflictNodes())

            variables = ROOT.RooArgSet(filler.vars())
            self.workspace_.defineSet("variables_%s" % dataset.GetName(),variables)
            
            if storeTrees:
                tree = filler.getTree()
                self.store_[tree.GetName()] = tree
                

    ## ------------------------------------------------------------------------------------------------------------
    def prepareTrees(self,name,selection,doPrint=False,printHeader=""): 
        """ Read trees from input file(s) and set all aliases 
        """ 
        if doPrint:    
            print "%s :" % printHeader
        
        ## read trees for given selection
        allTrees = self.getTreesForSelection(name,selection)
        for cat,trees in allTrees.iteritems():
            treePaths = []
            ## set aliases
            for t in trees:
                self.setAliases(t)
                treePaths.append( "%s/%s" % (os.path.relpath(t.GetDirectory().GetPath()), t.GetName()) )
            if doPrint:
                print " %s : \n  %s" % (cat, "\n  ".join(treePaths) ) 

        if doPrint:    
            print 
           
        return allTrees

    ## ------------------------------------------------------------------------------------------------------------
    def getTreesForSelection(self,dataset,selection):
        """ Load trees used for datasets definition.
        """ 
        ret = {}
        
        ## keep track of already loaded datasets
        key = "%s:%s" % ( dataset, selection ) 
        if not key in self.trees_:
            infile,samplesTmpl = self.datasets_[dataset]
            
            ## replace %(sel)s keyword with choosen selection
            replacements = { "sel" : selection }
            samples = [ s % replacements for s in samplesTmpl ]
            ## initialize list of trees: one entry per category
            self.trees_[key] = {}
            
            ## loop over categories and read in trees
            for cat in self.categories_:
                if type(cat) == int: 
                    catname = "cat%d" % cat
                else:
                    catname = cat
                    group = None
                if self.groups:
                    group = self.groups[cat]
                
                # call PlotApp.readObjects to read trees
                self.trees_[key][catname] = self.readObjects(infile,"",samples=samples,cat=catname,group=group)
                
        ## done
        return self.trees_[key]

        
    ## ------------------------------------------------------------------------------------------------------------
    ## End of class definition
    ## ------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------
# actual main
if __name__ == "__main__":
    app = TemplatesApp()
    app.run()

#  LocalWords:  workspaces
