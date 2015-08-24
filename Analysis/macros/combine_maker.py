#!/bin/env python

from diphotons.Utils.pyrapp import *
from optparse import OptionParser, make_option
from copy import deepcopy as copy
import os, json

from pprint import pprint

import array

from getpass import getuser

from templates_maker import TemplatesApp

import random

from math import sqrt

## ----------------------------------------------------------------------------------------------------------------------------------------
class CombineApp(TemplatesApp):
    """
    Class to handle template fitting.
    Takes care of preparing templates starting from TTrees.
    Inherith from PyRapp and PlotApp classes.
    """
    
    ## ------------------------------------------------------------------------------------------------------------
    def __init__(self,option_list=[],option_groups=[]):
        
        super(CombineApp,self).__init__(
            option_groups=[
                ("Combine workspace options", [
                        make_option("--fit-name",dest="fit_name",action="store",type="string",
                                    default="cic",
                                    help="Fit to consider"),
                        make_option("--observable",dest="observable",action="store",type="string",
                                   ## default="mgg[3350,300,7000]",
                                    default="mgg[3350,270,7000]",
                                    help="Observable used in the fit default : [%default]",
                                    ),
                        make_option("--fit-background",dest="fit_background",action="store_true",default=False,
                                    help="Fit background",
                                    ),                        
                        make_option("--use-custom-pdfs",dest="use_custom_pdfs",action="store_true",default=True,
                                    help="Use custom pdfs from diphotons/Utils",
                                    ),                        
                        make_option("--no-use-custom-pdfs",dest="use_custom_pdfs",action="store_false",
                                    help="Do not use custom pdfs from diphotons/Utils",
                                    ),                        
                        make_option("--use-templates",dest="use_templates",action="store_true",default=False,
                                    help="Use hybrid fit",
                                    ),                        
                        make_option("--template-comp-sig",dest="template_comp_sig",action="store_true",default="pp",
                                    help="Use this template for signal modeling",
                                    ),                        
                        make_option("--obs-template-binning",dest="obs_template_binning",action="callback",callback=optpars_utils.Load(scratch=True),
                                    default={ 
                                             "EBEB" : [270.,295.,325.,370.,450.,7000.],
                                             "EBEE" : [270.,310.,355.,420.,535.,7000.]
                                  ##           "EBEB" : [300.,322.,352.,396.,481.,7000.],
                                   ##          "EBEE" : [300.,339.,382.,448.,565.,7000.]
                                             },
                                    help="Binning of the parametric observable to be used for templates",
                                    ),                        
                        make_option("--template-binning",dest="template_binning",action="callback",callback=optpars_utils.ScratchAppend(float),
                                    type="string",
                                    default=[],
                                    help="Binning of the parametric observable to be used for templates",
                                    ),                        
                        make_option("--fit-asimov",dest="fit_asimov",action="callback",callback=optpars_utils.ScratchAppend(float),
                                    type="string",default=[],
                                    help="Do background fit on asimov dataset (thrown from fit to extended mass range)",
                                    metavar="FIT_RANGE"
                                    ),                        
                        make_option("--plot-binning",dest="plot_binning",action="callback",callback=optpars_utils.ScratchAppend(float),
                                    ## type="string",default=[114,300,6000],
                                   ##type="string",default=[134,300,7000],
                                    type="string",default=[136,270,7000],
                                    help="Binning to be used for plots",
                                    ),
                        make_option("--plot-signal-binning",dest="plot_signal_binning",action="callback",callback=optpars_utils.ScratchAppend(float),
                                    type="string",default=[50,0.2],
                                    help="Number of bins and width of observable for signal model plots",
                                    ),
                        make_option("--plot-fit-bands",dest="plot_fit_bands",action="store_true",default=False,
                                    help="Add error bands to plots",
                                    ),                        
                        make_option("--fast-bands",dest="fast_bands",action="store_true",default=True,
                                    help="Use hesse bands computation",
                                    ),                        
                        make_option("--minos-bands",dest="fast_bands",action="store_false",
                                    help="Use minos for bands computation",
                                    ),      
                        make_option("--plot-asimov-dataset",dest="plot_asimov_dataset",action="store_true",
                                    default=True,
                                    help="Use minos for bands computation",
                                    ),      
                        make_option("--no-plot-asimov-dataset",dest="plot_asimov_dataset",action="store_false",
                                    help="Use minos for bands computation",
                                    ),
                        make_option("--plot-norm-dataset",dest="plot_norm_dataset",action="store_true",
                                    default=False,
                                    help="Use minos for bands computation",
                                    ),      
                        make_option("--freeze-params",dest="freeze_params",action="store_true",default=False,
                                    help="Freeze background parameters after fitting",
                                    ),                        
                        make_option("--norm-as-fractions",dest="norm_as_fractions",action="store_true",default=False,
                                    help="Parametrize background components normalization as fractions",
                                    ),
                        make_option("--nuisance-fractions",dest="nuisance_fractions",action="store_true",default=False,
                                    help="Add nuisance parameters for component fractions",
                                    ),
                        make_option("--nuisance-fractions-covariance",dest="nuisance_fractions_covariance",
                                    action="callback",callback=optpars_utils.Load(scratch=True), type="string",
                                    default=None,
                                    help="correlation matrix between nuisance parameters",
                                    ),
                        ## make_option("--select-components",dest="select_components",action="callback",callback=optpars_utils.ScratchAppend(),
                        ##             default=[],
                        ##             help="only consider subset of background components"
                        ##             ),
                        make_option("--bkg-shapes",dest="bkg_shapes",action="callback",callback=optpars_utils.Load(scratch=True),
                                    type="string",
                                    default={ "bkg" : {
                                    "shape" : "data", "norm" : "data"
                                    }  },
                                    help="Background shapes",
                                    ),
                        make_option("--default-model",dest="default_model",action="store",type="string",
                                    default="dijet",
                                    help="Default background mode : [%default]",
                                    ),
                        make_option("--data-source",dest="data_source",action="store",type="string",
                                    default="data",
                                    help="Dataset to be used as 'data' default : [%default]",
                                    ),
                        make_option("--generate-signal-dataset",dest="generate_signal_dataset",action="store_true",default=False,
                                    help="Generate signal dataset",
                                    ),
                        make_option("--signal-name",dest="signal_name",action="store",type="string",
                                    default=None,
                                    help="Signal name to generate the dataset and/or datacard"),            
                        make_option("--generate-datacard",dest="generate_datacard",action="store_true",default=False,
                                    help="Generate datacard",
                                    ),
                        make_option("--include-flat-params-in-groups",dest="include_flat_params_in_groups",action="store_true",default=False,
                                    help="Include flat parameters in nuisance groups. (requires combine PR #225)",
                                    ),
                        make_option("--use-signal-datahist",dest="use_signal_datahist",action="store_true",default=False,
                                    help="Give RooDataHist to combine instead of RooHistPdf",
                                    ),
                        make_option("--binned-data-in-datacard",dest="binned_data_in_datacard",action="store_true",default=False,
                                    help="Use binned data dataset in datacard",
                                    ),
                        make_option("--unbinned-data-in-datacard",dest="binned_data_in_datacard",action="store_false",
                                    help="Use unbinned data dataset in datacard",
                                    ),
                        make_option("--background-root-file",dest="background_root_file",action="store",type="string",
                                    default=None,
                                    help="Output file from the background fit",
                                    ),
                        make_option("--signal-root-file",dest="signal_root_file",action="store",type="string",
                                    default=None,
                                    help="Output file from the signal model",
                                    ),
                        make_option("--cardname",dest="cardname",action="store",type="string",
                                    default=None,
                                    help="Name of generated card",
                                    ),
                        make_option("--compute-fwhm",dest="compute_fwhm",action="store_true",default=False,
                                    help="Compute the Full Width Half Maximum (FWHM) when generating signals",
                                    ),
                        make_option("--generate-ws-bkgnbias",dest="generate_ws_bkgnbias",action="store_true",default=False,
                                    help="Read signal and background workspaces and generate background+bias model",
                                    ),
                        make_option("--bkgnbias-components",dest="bkgnbias_components",action="callback",default=["bkg","pp"],
                                    type="string",callback=optpars_utils.ScratchAppend(),
                                    help="List of background components to which bias term is applied",
                                    ),
                        make_option("--bias-func",dest="bias_func",action="callback",callback=optpars_utils.Load(scratch=True),
                                    type="string",
                                    default={} ,
                                    help="Bias as a function of diphoton mass to compute the bias uncertainty values inside the datacard",
                                    ),
                        make_option("--fwhm-input-file",dest="fwhm_input_file",action="callback",callback=optpars_utils.Load(scratch=True),
                                    type="string",
                                    default={} ,
                                    help="Full Width Half Maximum (FWHM) values for different graviton masses used to compute the bias uncertainty values inside the datacard",
                                    ),
                        make_option("--datacard-bkg-rate",dest="datacard_bkg_rate",action="store",type="string",
                                    default="1",
                                    help="To increase bkg rate in datacard, for signal: call option --expectSignal when running combine tool",
                                    ),
                        make_option("--set-bins-fwhm",dest="set_bins_fwhm",action="callback",callback=optpars_utils.Load(scratch=True),
                                    type="string",
                                    default={},
                                    help="File containing best binning of histograms to compute the FWHM, best binning depends on the graviton mass and coupling",
                                    ),
                        make_option("--fwhm-output-file",dest="fwhm_output_file",action="store",type="string",
                                    default={},
                                    help="File where to write fwhm values",
                                    ), 
                        make_option("--luminosity",dest="luminosity",action="store",type="string",
                                    default="1",
                                    help="Specify luminosity for generating data, background and signal workspaces",
                                    ),
                        make_option("--signal-scalefactor-forpdf",dest="signal_scalefactor_forpdf",action="store",type="string",
                                    default="100",
                                    help="Specify luminosity for generating data, background and signal workspaces",
                                    ),
                        ]
                 )
                ]+option_groups,option_list=option_list
            )
        
        ## load ROOT (and libraries)
        global ROOT, style_utils, RooFit
        import ROOT
        from ROOT import RooFit
        
        import diphotons.Utils.pyrapp.style_utils as style_utils
        ROOT.gSystem.Load("libdiphotonsUtils")
        if ROOT.gROOT.GetVersionInt() >= 60000:
            ROOT.gSystem.Load("libdiphotonsRooUtils")
        
        self.pdfPars_ = ROOT.RooArgSet()

    def __call__(self,options,args):
        

        ## load ROOT style
        self.loadRootStyle()
        ROOT.TGaxis.SetMaxDigits(3)
        from ROOT import RooFit
        from ROOT import TH1D, TCanvas, TAxis
        
        printLevel = ROOT.RooMsgService.instance().globalKillBelow()
        ROOT.RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)
        ROOT.TH1D.SetDefaultSumw2(True)
        
        options.only_subset = [options.fit_name]
        options.store_new_only=True
        options.components = options.bkg_shapes.keys()
        ### if options.select_components:
        ###     options.components = [ comp for comp in options.components if comp in options.select_components ]
        self.use_custom_pdfs_ = options.use_custom_pdfs
        #self.save_params_.append("luminosity")

        # make sure that relevant 
        #  config parameters are read/written to the workspace
        self.save_params_.append("signals")
        if options.fit_background or options.generate_datacard:
            self.save_params_.append("components")
        self.save_params_.append("fit_name")

        self.setup(options,args)
        
        if options.fit_background:
            self.fitBackground(options,args)
            
        if options.generate_signal_dataset:
            self.generateSignalDataset(options,args)
            
        if options.generate_ws_bkgnbias:
            self.generateWsBkgnbias(options,args)
        
        if options.generate_datacard:
            self.generateDatacard(options,args)


    ## ------------------------------------------------------------------------------------------------------------
    def generateDatacard(self,options,args):
        """Generate a datacard with name: signal_name.txt if signal_root_file not provided.
        
        Generates datacard for signal_name or loop over the list of signals if signal_name not provided.
        If read_ws then bkg.root file = read_ws file.
        
        """
        print "--------------------------------------------------------------------------------------------------------------------------"
        print "generating datacard(s)"
        print "--------------------------------------------------------------------------------------------------------------------------"

        fitname = options.fit_name
        fit = options.fits[fitname]
        sidebands = list(fit.get("sidebands",{}).keys())
        categories = list(fit["categories"].keys())
        ### if (options.read_ws):
        ###     options.background_root_file = options.read_ws

        bkname_prefix = None
        if not options.background_root_file:
            options.background_root_file = options.read_ws
        elif not ".root" in options.background_root_file:
            bkname_prefix = options.background_root_file

        ## isNameProvided = False
        if (options.signal_name != None):
            signals = [options.signal_name]
            fname_prefix = None
        else:
            signals = options.signals.keys()
            fname_prefix = options.signal_root_file.replace(".root","_") if options.signal_root_file else ""

        ##for signame,trees in options.signals.iteritems():
        for signame in signals:
            
            ### if (options.signal_name != None):
            ###     isNameProvided = True
            ###     signame = options.signal_name
            ### 
            ### if (not isNameProvided or (isNameProvided and options.signal_root_file == None)):
            ###     options.signal_root_file = signame+".root" 

            if fname_prefix:
                options.signal_root_file = "%s%s.root" % ( fname_prefix, signame )
            elif not options.signal_root_file:
                options.signal_root_file = signame+".root" 
            if bkname_prefix:
                bkgfile = "%s%s.root" % ( bkname_prefix, signame )
            else:
                bkgfile = options.background_root_file
                
            ### if(options.cardname != None):    
            ###     datacard = self.open(options.cardname,"w+")
            ### else:
            ###     datacard = self.open("dataCard_"+signame+".txt","w+")

            cardname = "dataCard_"+signame+".txt"
            if options.cardname:
                if options.signal_name:
                    cardname = options.cardname
                else:
                    cardname = "%s_%s.txt" % ( options.cardname.replace(".txt",""), signame )
            datacard = self.open(cardname,"w+",folder=options.ws_dir)

            print 
            print "signal        : %s" % signame
            print "background ws : %s" % bkgfile
            print "signal     ws : %s" % options.signal_root_file
            print "datacard      : %s" % cardname
            print 
                            
            datacard.write("""
## Signal: %s - 13TeV
##
----------------------------------------------------------------------------------------------------------------------------------
imax * number of channels
jmax * number of backgrounds
kmax * number of nuisance parameters (source of systematic uncertainties)
----------------------------------------------------------------------------------------------------------------------------------\n""" % signame)
                        
            for cat in categories:
                datacard.write("shapes sig".ljust(20))
                datacard.write((" %s  %s" % (cat,options.signal_root_file)).ljust(50))
                if options.use_signal_datahist:
                    datacard.write(" wtemplates:signal_%s_%s\n"% (signame,cat))
                else:
                    datacard.write(" wtemplates:model_signal_%s_%s\n"% (signame,cat))
                
                for comp in options.components:
                    datacard.write(("shapes %s" % comp).ljust(20))
                    datacard.write((" %s  %s" % (cat,bkgfile)).ljust(50))
                    datacard.write(" wtemplates:model_%s_%s\n" % (comp,cat) ) 
                datacard.write("shapes data_obs".ljust(20))
                datacard.write((" %s  %s" % (cat,bkgfile)).ljust(50))
                if options.binned_data_in_datacard:
                    datacard.write(" wtemplates:binned_data_%s\n" % cat) 
                else:
                    datacard.write(" wtemplates:data_%s\n" % cat) 
            
            for cat in sidebands:                
                for comp in  fit["sidebands"][cat]:
                    datacard.write(("shapes %s" % comp).ljust(20))
                    datacard.write((" %s  %s" % (cat,bkgfile)).ljust(50))
                    datacard.write(" wtemplates:model_%s_%s\n" % (comp,cat) )  
                datacard.write("shapes data_obs".ljust(20))
                datacard.write((" %s  %s" % (cat,bkgfile)).ljust(50))
                if options.binned_data_in_datacard:
                    datacard.write(" wtemplates:binned_data_%s\n" % cat)                 
                else:
                    datacard.write(" wtemplates:data_%s\n" % cat)                 

            datacard.write("----------------------------------------------------------------------------------------------------------------------------------\n")
            datacard.write("bin".ljust(20))
            for cat in categories+sidebands:
                datacard.write((" %s".ljust(15) % cat))
            datacard.write("\n")

            datacard.write("observation".ljust(20))
            for cat in categories+sidebands:
                  datacard.write(" -1".ljust(15) )
            datacard.write("\n")
            
            datacard.write("----------------------------------------------------------------------------------------------------------------------------------\n")
            
            datacard.write("bin".ljust(20))
            for cat in categories:
                datacard.write((" %s" % cat).ljust(15) )
                for comp in options.components:
                    datacard.write((" %s" % cat).ljust(15) )
            for cat in sidebands:                
                for comp in  fit["sidebands"][cat]:
                    datacard.write((" %s" % cat).ljust(15) )                    
            datacard.write("\n")


            datacard.write("process".ljust(20))
            for cat in categories:
                datacard.write(" sig".ljust(15) )
                for comp in options.components:
                    datacard.write((" %s" % comp).ljust(15) )
            for cat in sidebands:                
                for comp in  fit["sidebands"][cat]:
                    datacard.write((" %s" % comp).ljust(15) )                    
            datacard.write("\n")
            
            datacard.write("process".ljust(20))
            icomp = {}
            i = 0
            for cat in categories:
                datacard.write(" 0".ljust(15) )
                
                for comp in options.components:
                    if comp in icomp:
                        j = icomp[comp]
                    else:
                        i+=1
                        j = i
                        icomp[comp] = i 
                    datacard.write((" %d" % j).ljust(15) )
            for cat in sidebands:                
                for comp in  fit["sidebands"][cat]:
                    if comp in icomp:
                        j = icomp[comp]
                    else:
                        i+=1
                        j = i
                        icomp[comp] = i 
                    datacard.write((" %d" % j).ljust(15) )
            datacard.write("\n")
            
            datacard.write("rate".ljust(20))
            for cat in categories:
                if options.use_signal_datahist:
                    datacard.write(" -1".ljust(15) )
                else:
                    datacard.write("  1".ljust(15) )
                for comp in options.components:
                    datacard.write((" %s" % options.datacard_bkg_rate).ljust(15))
            for cat in sidebands:                
                for comp in  fit["sidebands"][cat]:                    
                    datacard.write((" %s" % options.datacard_bkg_rate).ljust(15) )
            datacard.write("\n")
            
            datacard.write("----------------------------------------------------------------------------------------------------------------------------------\n")
            
            # normalization nuisances
            datacard.write("lumi  lnN".ljust(20))
            for cat in categories:
                datacard.write(" 1.04".ljust(15) )
                for comp in options.components:
                    datacard.write(" -".ljust(15) )
            for cat in sidebands:                
                for comp in  fit["sidebands"][cat]:                    
                    datacard.write(" -".ljust(15) )
            datacard.write("\n")
            
            # other nuisance parameters
            datacard.write("\n")
            for param in fit.get("params",[]) + fit.get("sig_params",{}).get(signame,[]):
                if (param[-1] == 0):
                    datacard.write("# ")
                datacard.write("%s param %1.3g %1.3g\n" % tuple(param) )            
            
            # flat parameters
            datacard.write("\n")
            for param in fit.get("flat_params",[]):
                if (param[-1] == 0):
                    datacard.write("# ")
                datacard.write("%s flatParam\n" % param )
            
            # groups of nuisances
            datacard.write("\n")
            for group,params in fit.get("groups",{}).iteritems():
                if len(params) == 0: continue
                if not options.include_flat_params_in_groups:
                    flatp = fit.get("flat_params",[])
                    ## remove flat parameters from group
                    flat_params = [ p for p in params if not p in flatp ]
                    if len(flat_params) != 0:
                        pars = " ".join( set(flat_params) )
                        datacard.write("%s group = %s\n" % (group,pars ))
                    datacard.write("# "); ## leave full group definition in datacard, but commented
                pars = " ".join( set(params) )
                datacard.write("%s group = %s\n" % (group,pars ))
                
            datacard.write("----------------------------------------------------------------------------------------------------------------------------------\n\n")
            
            
            ## if isNameProvided:
            ##     break
        print "--------------------------------------------------------------------------------------------------------------------------"
                
    ## ------------------------------------------------------------------------------------------------------------        
    def generateWsBkgnbias(self,options,args):

        print "--------------------------------------------------------------------------------------------------------------------------"
        print "including bias term in the background"
        print "--------------------------------------------------------------------------------------------------------------------------"
        
        fit = options.fits[options.fit_name]
        
        ### signame = options.signal_name
        ### if (options.signal_name == None or options.fit_name == None):
        ###     print "Please provide --signal-name and --fit-name"
        ###     return

        # build observable variable
        roobs = self.buildRooVar(*(self.getVar(options.observable)), recycle=True, importToWs=True)
        roobs.setRange("fullRange",roobs.getMin(),roobs.getMax()) 
        roowe = self.buildRooVar("weight",[])        
        rooset = ROOT.RooArgSet(roobs,roowe)
        
        if not "params" in fit:
            fit["params"] = []
        if not "sig_params" in fit:
            fit["sig_params"] = {}
            
        if options.signal_name:
            signals = [options.signal_name]
        else:
            signals = options.signals.keys()
            
        if (len(signals) == 0 or options.fit_name == None):
            print "Please provide --signal-name and --fit-name"
            return
        
        if len(signals) > 1:
            options.background_root_file = options.background_root_file.replace(".root","_bkgnbias_") ## change this for generateDatacard
        
        for signame in signals:
            if not signame in fit["sig_params"]:
                fit["sig_params"][signame] = []

            for cat in fit["categories"]:
                
                dataBinned = self.rooData("binned_data_%s" % cat)
                data = self.rooData("data_%s" % cat)
                if options.use_signal_datahist:
                    signalDataHist = self.rooData("signal_%s_%s" % (signame,cat))
                    signalPdf = ROOT.RooHistPdf("signal_model_%s_%s"% (signame,cat),"signalPdf_%s_%s"% (signame,cat),ROOT.RooArgSet(roobs),signalDataHist)
                else:
                    signalPdf = self.rooPdf("model_signal_%s_%s"% (signame,cat))
                self.workspace_.rooImport(data)
                self.workspace_.rooImport(dataBinned)
                
                for comp in options.components :
                
                    ## # import source datasets too
                    ## dset = self.rooData("source_dataset_%s%s"% (comp,cat))
                    ## self.workspace_.rooImport(dset)

                    bkgPdf = self.rooPdf("model_%s_%s" % (comp,cat))
                   
                    roopdflist = ROOT.RooArgList()
                    roopdflist.add(bkgPdf)
                    roopdflist.add(signalPdf)
                    
                    ## retrieve norm of pdf 
                    rooNdata = self.buildRooVar("%s_norm" % (bkgPdf.GetName()),[],recycle=True,importToWs=False)

                    ## add bias term only to some background components
                    ##     important in the case of the semi-parametric fit
                    if not comp in options.bkgnbias_components:
                        self.workspace_.rooImport(bkgPdf)
                        self.workspace_.rooImport(rooNdata)
                        continue
                
                    bkgPdf.SetName("bkgOnly_model_%s_%s" % (comp,cat) )
                    rooNdata.SetName("%s_norm" % bkgPdf.GetName())
                    ## build list of coefficients 
                    roolist = ROOT.RooArgList()
                    nBias = self.buildRooVar("nBias_%s_%s" % (comp,cat), [], importToWs=False )
                    nBias.setVal(0.)
                    nBias.setConstant(True)
                    
                    # compute the nuisance values if bias_func and fwhm_input_file are provided 
                    nB = 0.
                    if(len(options.bias_func) != 0 and len(options.fwhm_input_file) != 0):
                        bias_name = "%s_%s_%d_%d" % (cat,options.default_model,int(roobs.getMin()),int(roobs.getMax()))
                        if (not bias_name in options.bias_func.keys()):
                            print
                            print("Cannot compute the bias values: bias function for %s not provided" % bias_name)
                            print
                        else:
                            bias_func = ROOT.TF1(bias_name, options.bias_func[bias_name],roobs.getMin(),roobs.getMax())
                            # get value of grav mass
                            substr = signame[signame.index("_")+1:]
                            grav_mass = float(substr[substr.index("_")+1:])
                            fwhm_val = float(options.fwhm_input_file[signame][cat])
                            nB = bias_func.Eval(grav_mass) * fwhm_val * float(options.luminosity) 
                            #print "%f" % nB
                    fit["sig_params"][signame].append( (nBias.GetName(), nBias.getVal(), nB) )
                    pdfSum_norm = ROOT.RooFormulaVar("model_%s_%s_norm" % (comp,cat),"model_%s_%s_norm" % (comp,cat),"@0",ROOT.RooArgList(rooNdata)) 
                
                    fracsignuis = ROOT.RooFormulaVar("signal_%s_%s_nuisanced_frac" % (comp,cat),"signal_%s_%s_nuisanced_frac" % (comp,cat),"@0*1./@1",ROOT.RooArgList(nBias,pdfSum_norm) )
                    fracbkg = ROOT.RooFormulaVar("background_%s_%s_frac" % (comp,cat), "background_%s_%s_frac" % (comp,cat), "1.-@0",ROOT.RooArgList(fracsignuis))
                    roolist.add(fracbkg)
                    roolist.add(fracsignuis)
                    
                    
                    ## summing pdfs
                    pdfSum = ROOT.RooAddPdf("model_%s_%s" % (comp,cat),"model_%s_%s" % (comp,cat), roopdflist, roolist)
                    self.workspace_.rooImport(pdfSum_norm)
                    self.workspace_.rooImport(pdfSum,RooFit.RecycleConflictNodes())
                    
            # import pdfs for the sidebands
            for cat,comps in fit.get("sidebands",{}).iteritems():
                for comp in comps:
                    dataBinned = self.rooData("binned_data_%s" % cat)
                    data = self.rooData("data_%s" % cat)
                    self.workspace_.rooImport(data)
                    self.workspace_.rooImport(dataBinned)
                    
                    sbPdf = self.rooPdf("model_%s_%s" % (comp,cat))
                    sbNorm  = self.rooVar("%s_norm" % sbPdf.GetName())
                    self.workspace_.rooImport(sbNorm)
                    self.workspace_.rooImport(sbPdf,RooFit.RecycleConflictNodes())
                
            if len(signals) > 1:
                options.output_file = "%s%s.root" % (options.background_root_file,signame)
            self.saveWs(options)

    ## ------------------------------------------------------------------------------------------------------------  
    def fitBackground(self,options,args):

        print "--------------------------------------------------------------------------------------------------------------------------"
        print "runnning background fit"
        print 
        
        ROOT.RooMsgService.instance().addStream(RooFit.DEBUG,RooFit.Topic(RooFit.Eval),RooFit.ClassName("RooProdPdf")) 
        fitname = options.fit_name
        fit = options.fits[fitname]
        
        options.background_root_file = options.output_file # set name for datacard generation
        
        roobs = self.buildRooVar(*(self.getVar(options.observable)), recycle=False, importToWs=False)
        #roobs.setBins(5000,"cache")
        roobs.setRange("fullRange",roobs.getMin(),roobs.getMax()) 
        roowe = self.buildRooVar("weight",[])        
        rooset = ROOT.RooArgSet(roobs,roowe)
        roobs.getBinning("fullRange").Print()        
        extset = ROOT.RooArgSet(rooset)

        useAsimov = False
        if len(options.fit_asimov) > 0 :
            obsvar,obsbinning = self.getVar(options.observable)
            nbins = float(len(obsbinning)-1)*(options.fit_asimov[1] - options.fit_asimov[0])/(obsbinning[-1]-obsbinning[0])
            asimbinning = self.getVar("%s[%d,%f,%f]" % ( obsvar,nbins,options.fit_asimov[0],options.fit_asimov[1] ) )[1]
            asimobs = self.buildRooVar(obsvar,asimbinning, recycle=False, importToWs=False)
            useAsimov = True
            asimobs.setRange("asimRange",asimobs.getMin(),asimobs.getMax())
            asimobs.setRange("fullRange",roobs.getMin(),roobs.getMax())
            
        
        ## build and import data dataset
        ndata = {}
        rooNdata = {}
        sidebands = {}

        if len(options.template_binning) > 0:
            fit["template_binning"] = options.template_binning
        # add extra observable for hybrid fit
        if options.use_templates:
            ndim = fit["ndim"]
            rootempls = ROOT.RooArgSet()
            for idim in range(ndim):
                rootempls.add( self.buildRooVar("templateNdim%dDim%d" %(ndim,idim), fit["template_binning"]) )
                nb = len(fit["template_binning"])-1
                nb *= nb
            templfunc,unrol_widths = self.histounroll_book(fit["template_binning"],rootempls,importToWs=False,buildHistFunc="templateNdim%d_unroll" % ndim)            
            unrol_binning = array.array( 'd', [ float(bound) for bound in range(nb+1) ] )
            unrol_widths = array.array( 'd', [ 1. for bound in range(nb) ] )
            assert( len(unrol_binning) == len(unrol_widths)+1 )
            rootempl = self.buildRooVar(templfunc.GetName() , unrol_binning)
            # make sure binnings are consistently defined later on
            roobs = rooset[roobs.GetName()]
            for cat in fit["categories"]:
                obs_binning = array.array('d',options.obs_template_binning[cat])
                roobs.setBinning(ROOT.RooBinning(len(obs_binning)-1,obs_binning),"templateBinning%s" % cat)
                rootempl.setBinning(ROOT.RooBinning(len(unrol_binning)-1,unrol_binning),"templateBinning%s" % cat)
                
            extset.add(rootempl)
            extset.add(rootempls)
            rooset.add(rootempls)
                        
        self.workspace_.rooImport(roobs)
        # import data dataset
        for cat in fit["categories"]:
            treename = "%s_%s_%s" % (options.data_source,options.fit_name,cat)
            
            print "importing %s as data for cat %s" % (treename, cat)

            dset = self.rooData(treename, weight="%s * weight" % options.luminosity)

            if options.use_templates:
                dset.addColumn(templfunc)
            reduced = dset.reduce(RooFit.SelectVars(extset),RooFit.Range("fullRange"))

            reduced.SetName("data_%s"% (cat))
            
            ## keep track of numbef of events in data
            ndata[cat] = reduced.sumEntries()
            rooNdata[cat] = self.buildRooVar("%s_norm" % cat,[],recycle=False,importToWs=False)
            rooNdata[cat].setVal(ndata[cat])
            
            self.workspace_.rooImport(reduced)
            
            binned = reduced.binnedClone("binned_data_%s" % cat)
            self.workspace_.rooImport(binned)

        fitops = [ RooFit.PrintLevel(-1),RooFit.Warnings(False),RooFit.Minimizer("Minuit2"),RooFit.Offset(True) ]
        if options.verbose:
            fitops[0] = RooFit.PrintLevel(2)

        ## prepare background fit components
        print
        fit["params"] = fit.get("params",[])
        fit["flat_params"] = fit.get("flat_params",[])
        fit["groups"] = fit.get("groups",{})
        if not "bkg_shape" in fit["groups"]:
            fit["groups"]["bkg_shape"] = []
        if not "bkg_shape_control" in fit["groups"]:
            fit["groups"]["bkg_shape_control"] = []
            
        ## loop over categories to fit background
        for cat in fit["categories"]:
            
            print
            print "fitting category : ", cat
            print
            
            importme = []
            fractions = {}
            setme = []
            # use purity fractions to define components normalization
            if options.norm_as_fractions:
                tot = 0.
                roolist = ROOT.RooArgList()
                rooformula = []
                if not "bkg_fractions" in fit["groups"]:
                    fit["groups"]["bkg_fractions"] = []
                # read covariance matrix for purities
                if options.nuisance_fractions_covariance:
                    ## FIXME: covariance per-category
                    if not options.nuisance_fractions:
                        print "You specified a covariance matrix for the component fraction, but did not set the nuisance-fractions options"
                        print "   I will act as if you did it"
                        options.nuisance_fractions = True
                    cov_components = options.nuisance_fractions_covariance["components"]
                    # make sure we have the right number of items in the covariance
                    assert(len(cov_components) == len(options.components) - 1)
                    # one of purities is a linear combination of the others.
                    #     find out which one
                    dependent = None
                    for comp in options.components:
                        if not comp in cov_components:
                            dependent = comp
                            break
                    assert(dependent)
                    # now build the covariance matrix
                    errors = options.nuisance_fractions_covariance["errors"]
                    correlations = options.nuisance_fractions_covariance["correlations"]
                    covariance = ROOT.TMatrixDSym(len(errors))
                    for ii,ierr in enumerate(errors):
                        for jj,jerr in enumerate(errors):
                            covariance[ii][jj] = correlations[ii][jj]*ierr*jerr
                    # and find eigenvectors
                    eigen = ROOT.TMatrixDSymEigen(covariance)
                    vectors = eigen.GetEigenVectors();
                    values  = eigen.GetEigenValues();                    
                    # create unit gaussians per eigen-vector
                    eigvVars = ROOT.RooArgList()
                    for ii in range(len(errors)):
                        eigNuis = self.buildRooVar("%s_eig%d_frac_nuis" % (cat,ii), [0.,-5.,5.], importToWs=False )
                        eigNuis.Print()
                        eigNuis.setConstant(True)
                        eigvVars.add(eigNuis)
                        fit["params"].append( (eigNuis.GetName(), eigNuis.getVal(), 1.) )
                        fit["groups"]["bkg_fractions"].append(eigNuis.GetName())
                else:
                    cov_components = options.components[:-1]
                    dependent      = options.components[-1]
                    
                ## for icomp,comp in enumerate(options.components[:-1]):
                for icomp,comp in enumerate(cov_components):
                    if comp != "":
                        comp = "%s_" % comp
                    # FIXME: optionally read central value as input
                    frac = self.buildRooVar("%s%s_frac" % (comp,cat), [0.5,0.,1.], importToWs=False )
                    # set purity fraction according to normalization dataset
                    setme.append(comp)
                    fractions[comp] = frac
                    # build rooformula var for depdendent coefficient
                    rooformula.append("@%d"%icomp)
                    if options.nuisance_fractions:
                        if options.nuisance_fractions_covariance:
                            # now create the linear combinations
                            # each is equal to the transpose matrx times the square root of the eigenvalue (so that we get unit gaussians)
                            coeffs = ROOT.RooArgList()                                    
                            for jcomp in range(len(cov_components)):
                                coeff = self.buildRooVar("%s%s_coeff%d_frac" % (comp,cat,jcomp), [vectors(icomp,jcomp)*sqrt(values(jcomp))], importToWs=False )
                                coeff.setConstant(True)
                                coeff.Print()
                                coeffs.add(coeff)
                            nuis = ROOT.RooAddition("%s%s_frac_nuis" % (comp,cat), "%s%s_frac_nuis" % (comp,cat), eigvVars, coeffs )                            
                        else:
                            nuis = self.buildRooVar("%s%s_frac_nuis" % (comp,cat), [0.,-5,5], importToWs=False )
                            nuis.setConstant(True)
                            fit["params"].append( (nuis.GetName(), nuis.getVal(), 0.) )
                            
                        frac.setConstant(True)
                        nuisfrac = ROOT.RooAddition("%s%s_nuisanced_frac" % (comp,cat),"%s%s_nuisanced_frac" % (comp,cat),ROOT.RooArgList(frac,nuis) )
                        roolist.add(nuisfrac)                        
                        self.keep( [nuis,nuisfrac] )
                    else:
                        frac.setConstant(False)
                        roolist.add(frac)
                        fit["flat_params"].append(frac.GetName())
                        fit["groups"]["bkg_fractions"].append(frac.GetName())

                # now build the dependent coefficient as 1 - sum frac_j
                comp = dependent
                if comp != "":
                    comp = "%s_" % comp
                frac = ROOT.RooFormulaVar("%s%s_frac" % (comp,cat),"%s%s_frac" % (comp,cat),"1.-%s" % "-".join(rooformula),roolist )
                fractions[comp] = frac
                # all purity fractions built

            # fit the observable
            for comp,opts in options.bkg_shapes.iteritems():                
                # fit options
                model = opts.get("model",options.default_model) # functional form
                model_cats = opts.get("model_cats",{})          #  may also be specified per-category
                model   = model_cats.get(cat,model)             #  
                source  = opts["shape"]                         # dataset used to fit shape
                nsource = opts["norm"]                          # dataset used to set normalization
                source_cats = opts.get("shape_cats",{})         # potentially take shape from different category
                nsource_cats = opts.get("norm_cats",{})         # ... or normalization
                add_sideband = opts.get("add_sideband",False)   # add shape dataset as control region
                weight_cut = opts.get("weight_cut",None)        # for convenience: remove MC event with high weight
                tsource = opts.get("template",None)
                assert( tsource or not options.use_templates )
                
                # options read
                print "component : " , comp
                print "model :", model
                if comp != "":
                    comp = "%s_" % comp
                    
                # dataset used to determine shape
                catsource = source_cats.get(cat,cat)
                treename = "%s_%s_%s" % (source,options.fit_name,catsource)
                # and normalization
                catnsource = nsource_cats.get(cat,cat)
                ntreename = "%s_%s_%s" % (nsource,options.fit_name,catnsource)

                if add_sideband and not catsource in sidebands:
                    sidebands[catsource] = set()

                dset     = self.rooData(treename,weight="%s * weight" % options.luminosity)
                ndset    = self.rooData(ntreename,weight="%s * weight" % options.luminosity)
                pldset   = dset if not options.plot_norm_dataset else ndset
                                
                ## if needed replace dataset with asimov
                if useAsimov:
                    print 
                    print "Will use asimov dataset"                    
                    print "enlarged fit range : %1.4g-%1.4g" % ( asimobs.getMin(), asimobs.getMax() )
                    print "final    fit range : %1.4g-%1.4g" % ( roobs.getMin(), roobs.getMax() )
                    if weight_cut:
                        adset = self.reducedRooData(treename,rooset,sel=weight_cut,redo=True,importToWs=False)
                    else:
                        adset = dset
                    ## fit pdf to asimov dataset
                    aset = ROOT.RooArgSet(asimobs,roowe)
                    adset = adset.reduce(RooFit.SelectVars(aset),RooFit.Range("asimRange")) 
                    apdf = self.buildPdf(model,"asimov_model_%s%s" % (comp,cat), asimobs )
                    apdf.fitTo(adset,*fitops)
                    snap = ("asimov_model_%s%s" % (comp,cat), apdf.getDependents( self.pdfPars_ ).snapshot())                    
                    ## now compute number of expected events in "fullRange"                    
                    ndset = ndset.reduce(RooFit.SelectVars(aset),RooFit.Range("asimRange"))
                    nexp = ndset.sumEntries()
                    nexp *= apdf.createIntegral(ROOT.RooArgSet(asimobs),"fullRange").getVal()/apdf.createIntegral(ROOT.RooArgSet(asimobs),"asimRange").getVal()
                    print "throwing asimov dataset for %1.4g expected events (computed from %1.4g events in enlarged range)" % ( nexp, ndset.sumEntries() )
                    ## build a new pdf which depends on roobs instead of asimobs and use it to throw the asimov dataset
                    tpdf = self.buildPdf(model,"extra_asimov_model_%s%s" % (comp,cat), roobs, load=snap )
                    dset = ROOT.DataSetFiller.throwAsimov(nexp,tpdf,roobs)
                    ndset = dset
                    print
                else:
                    snap = None
                    
                ## if needed cut away high weight events for the fit, but keep the uncut dataset
                if weight_cut:                    
                    uncut        = dset.reduce(RooFit.SelectVars(rooset),RooFit.Range("fullRange"))
                    binned_uncut = uncut.binnedClone() if not useAsimov else uncut
                    if useAsimov:
                        dset = uncut
                    else:
                        dset = self.reducedRooData(treename,rooset,weight="%s * weight" % options.luminosity,sel=weight_cut,redo=True,importToWs=False)                    

                ## reduce datasets to required range
                reduced  = dset.reduce(RooFit.SelectVars(rooset),RooFit.Range("fullRange"))
                if useAsimov and options.plot_asimov_dataset:
                    plreduced = reduced
                else:
                    plreduced = pldset.reduce(RooFit.SelectVars(rooset),RooFit.Range("fullRange"))
                    if options.use_templates:
                        plreduced.addColumn(templfunc)
                nreduced = ndset.reduce(RooFit.SelectVars(rooset),RooFit.Range("fullRange"))
                reduced.SetName("source_dataset_%s%s"% (comp,cat))
                binned = reduced.binnedClone() if not useAsimov else reduced               
                
                print "shape source :", treename, reduced.sumEntries(), dset.sumEntries(), 
                if weight_cut:
                    print uncut.sumEntries()
                else:
                    print
                print "normalization source: ", ntreename, nreduced.sumEntries()

                ## build pdf
                if add_sideband: 
                    ## if we want to take background shape from sideband in data, book 
                    ##    the pdf such that coefficients are the same for the signal region and sideband shapes
                    pdf = self.buildPdf(model,"model_%s_%s_control" % (add_sideband,catsource), roobs, load=snap )
                    sbpdf = self.buildPdf(model,"model_%s_%s_control" % (add_sideband,catsource), roobs, load=snap )
                    sbpdf.SetName("model_%s_%s_control" % (add_sideband,catsource))
                    sidebands[catsource].add(add_sideband)
                else:
                    ## else book fully independet shape
                    pdf = self.buildPdf(model,"model_%s%s" % (comp,cat), roobs, load=snap )                    
                if options.use_templates:
                    pdf.SetName("model_%s_%s%s" % (roobs.GetName(),comp,cat))
                else:
                    pdf.SetName("model_%s%s" % (comp,cat))
                    
                if add_sideband:
                    ## build normalization variable for sideband
                    sbnorm = self.buildRooVar("%s_norm" %  (sbpdf.GetName()), [], importToWs=False )
                    ## sideband normalization accounts also for the high weight events
                    if weight_cut or useAsimov:
                        sbnorm.setVal(uncut.sumEntries())
                    else:
                        sbnorm.setVal(reduced.sumEntries())
                        
                # fit
                if not useAsimov:
                    # no need to refit if we used asimov dataset
                    pdf.fitTo(binned,RooFit.Strategy(2),*fitops)
                    
                ## template pdfs
                if options.use_templates:
                    ## get dataset for templates building
                    tfitnam = options.fit_name                    
                    if ":" in tsource:
                        tsource, tfitnam = tsource.split(":")
                    ttreename = "%s_%s_%s" % ( tsource, tfitnam, cat )
                    templset = self.reducedRooData(ttreename, rooset, weight="%s * weight" % options.luminosity, sel=weight_cut, redo=True, importToWs=False )
                    templset = templset.reduce(RooFit.Range("fullRange"))
                    templset.addColumn(templfunc)
                    
                    ## fill TH2 of template vs observable
                    xb = roobs.getBinning("templateBinning%s"%cat)
                    yb = rootempl.getBinning("templateBinning%s"%cat)
                    templhist = ROOT.TH2F("hist_template_%s%s" % (comp,cat), "hist_template_%s%s" % (comp,cat), xb.numBins(), xb.array(), yb.numBins(), yb.array() )
                    templset.fillHistogram(templhist, ROOT.RooArgList(roobs,rootempl) )
                    ## make slice pdf out of TH2
                    self.keep(pdf)
                    templpdf = ROOT.RooSlicePdf("model_%s_%s%s" % (rootempl.GetName(),comp,cat),"model_%s_%s%s" % (rootempl.GetName(),comp,cat),
                                                templhist,unrol_widths,rootempl,roobs)
                    self.keep(templpdf)
                    if options.verbose:
                        print "Integral templpdf     :", templpdf.createIntegral(ROOT.RooArgSet(rootempl,roobs),"templateBinning%s"%cat).getVal()
                        print "Integral param pdf    :", pdf.createIntegral(ROOT.RooArgSet(roobs),"templateBinning%s"%cat).getVal()
                    
                    ## and finally the conditional pdf. 
                    ## note: not telling RooFit to build the conditional pdf 
                    ##       since it is already done by the RooSlicePdf                        
                    pdf = ROOT.RooProdPdf("model_%s%s" % (comp,cat), "model_%s%s" % (comp,cat), 
                                          pdf, templpdf )
                                          ## ROOT.RooArgSet(pdf), RooFit.Conditional(ROOT.RooArgSet(templpdf),ROOT.RooArgSet(rootempl)) )
                    if options.verbose:
                        print "Integral combined pdf :", pdf.createIntegral(ROOT.RooArgSet(rootempl,roobs),"templateBinning%s"%cat).getVal()
                    
                    plbinned = ROOT.RooDataHist("%s_binned_tmp" % plreduced.GetName(), "%s_binned_tmp" % plreduced.GetName(), ROOT.RooArgSet(roobs,rootempl),"templateBinning%s"%cat )
                    plbinned.add(plreduced)
                    self.plotBkgFit(options,plbinned,templpdf,rootempl,"template_proj_%s%s" % (comp,cat),poissonErrs=True,logy=False,logx=False,
                                    plot_binning=list(unrol_binning),
                                    opts=[RooFit.ProjWData(ROOT.RooArgSet(roobs),plbinned)], bias_funcs={}, forceSkipBands=True )
                    
                    self.plotBkgFit(options,plbinned,pdf,rootempl,"template_cond_%s%s" % (comp,cat),poissonErrs=True,logy=False,logx=False,
                                    plot_binning=list(unrol_binning), bias_funcs={} )
                    
                ## plot the fit result
                self.plotBkgFit(options,plreduced,pdf,roobs,"%s%s" % (comp,cat),poissonErrs=True)

                ## normalization has to be called <pdfname>_norm or combine won't find it
                if options.norm_as_fractions:
                    # normalization is n_tot * frac_comp
                    norm = ROOT.RooProduct("%s_norm" %  (pdf.GetName()),"%s_norm" %  (pdf.GetName()),
                                              ROOT.RooArgList(rooNdata[cat],fractions[comp]))
                else:
                    # otherwise just n_comp
                    norm = self.buildRooVar("%s_norm" %  (pdf.GetName()), [], importToWs=False ) 
                ## set normalization to expected number of events in normalization region
                if options.norm_as_fractions:
                    if comp in setme:
                        fractions[comp].setVal(nreduced.sumEntries()/ndata[cat])
                        ## fractions[comp].setConstant(True) # set constant by default
                else:
                    norm.setVal(nreduced.sumEntries()) 
                
                ## define groups of parameters and set them constant if requested
                params = pdf.getDependents(self.pdfPars_)
                itr = params.createIterator()
                var = itr.Next()
                while var:
                    if not var.isConstant(): # skip the variables which were set constant
                        fit["flat_params"].append( var.GetName() )
                        fit["groups"]["bkg_shape"].append( var.GetName() )
                        if "control" in var.GetName():
                            fit["groups"]["bkg_shape_control"].append( var.GetName() )
                    if options.freeze_params:
                        var.setConstant(True)
                    var = itr.Next()
                    
                # import pdf to the workspace
                self.workspace_.rooImport(pdf,RooFit.RecycleConflictNodes())
                importme.append([norm]) ## import this only after we run on all components, to make sure that all fractions are properly set
                self.workspace_.rooImport(reduced)
                
                # import pdf and data for sidebands
                if add_sideband:
                    if weight_cut or useAsimov:
                        reduced = uncut
                        binned  = binned_uncut
                    reduced.SetName("data_%s_control" % catsource)
                    self.workspace_.rooImport(reduced)
                    binned.SetName("binned_data_%s_control" % catsource)
                    self.workspace_.rooImport(binned)
                    self.workspace_.rooImport(sbnorm)
                    self.workspace_.rooImport(sbpdf,RooFit.RecycleConflictNodes())
            
                print
                
            if options.norm_as_fractions:
                for comp in setme:
                    me = fractions[comp]
                    print "fraction %s : %1.3g" % ( me.GetName(), me.getVal() )
            # import all variables
            for me in importme:
                self.workspace_.rooImport(*me)
                
                
        # keep track of nuisance parameters
        fit["sidebands"] = {}
        for nam,val in sidebands.iteritems():
            fit["sidebands"]["%s_control" % nam] = list(val)
        
        if options.use_templates:
            templfunc.Print()
            templfunc.SetNameTitle("func_%s"% templfunc.GetName(),"func_%s"% templfunc.GetName())
            self.workspace_.rooImport(templfunc)
            self.workspace_.rooImport(rootempl)
        
        if options.verbose:
            self.workspace_.Print()
        # done
        self.saveWs(options)
       
 ## ------------------------------------------------------------------------------------------------------------
    def generateSignalDataset(self,options,args):
        
        print "--------------------------------------------------------------------------------------------------------------------------"
        print "generating signal dataset"
        print 
        
        fitname = options.fit_name
        fit = options.fits[fitname] 
        isNameProvided = False
        list_fwhm = {}
        isPrefix = False
        if (options.signal_name != None):
                isNameProvided = True
        
        if (not isNameProvided and options.output_file != None):
            isPrefix = True
            prefix_output = options.output_file.replace(".root","")
            options.signal_root_file = options.output_file ## copy this in case we want to run --generate-datacard at the same time
            if not options.cardname:
                options.cardname = "dacard_%s.txt" % prefix_output
        
        ## book roo observable
        roobs = self.buildRooVar(*(self.getVar(options.observable)), recycle=False, importToWs=True)
        roobs.setRange("fullRange",roobs.getMin(),roobs.getMax())
        roowe = self.buildRooVar("weight",[])        
        weightMod = ROOT.RooFormulaVar("weightMod" ,"weightMod","@0*100", ROOT.RooArgList(roowe) )
                
        rooset = ROOT.RooArgSet(roobs,roowe)
        ## read back template roovariable and map
        if options.use_templates:
            ndim = fit["ndim"]
            rootemplname="templateNdim%s_unroll" % ndim
            rootempl = self.buildRooVar(*(self.getVar(rootemplname)), recycle=True)
            rootempls = ROOT.RooArgSet()
            for idim in range(ndim):
                rootempls.add(self.buildRooVar(*(self.getVar(rootemplname)), recycle=False)) 
            rooset.add(rootempls)
            templfunc = self.rooFunc("func_%s" % rootemplname)
            templfunc.SetName(rootemplname)
            options.use_signal_datahist = False ## make sure that in the datacard we point to the pdf for signal, not to the roodatahist
            
        for signame,trees in options.signals.iteritems():
            self.bookNewWs()
            
            if(isNameProvided):
                signame = options.signal_name
        
            # In case nothing specified about the output file, set: output_file = signame.root
            if ( options.output_file == None ):
                options.output_file = "%s.root" % (signame)

            # In case we loop over all signals, we can give inside options.output_file the prefix
            # ... for all generated signal files (e.g. a common directory)
            elif (isPrefix):
                options.output_file = "%s_%s.root" % (prefix_output,signame)
            nameFileOutput = options.output_file
           
            sublist_fwhm = {}
            ## build and import signal dataset
            for cat in fit["categories"]:
                treename = "%s_%s_%s" % (signame,options.fit_name,cat)
                print treename
                ## dset = self.rooData(treename)
                dset = self.rooData(treename,weight="%s * weight" % options.luminosity)
                if options.signal_scalefactor_forpdf!=1:
                    dsetPdf = self.rooData(treename,weight="%s * weight" %options.signal_scalefactor_forpdf,redo=True)
                    dsetPdf.SetName("ForPdf_%s" %treename)
                else: dsetPdf=dset
                
                if options.verbose: 
                    dsetPdf.Print()
                    dset.Print()

                roobsArg=ROOT.RooArgSet(roobs)
                if options.use_templates:
                    rootempl_binning= rootempl.getBinning("templateBinning%s" % cat)
                    dset.addColumn(templfunc)
                    rootemps=ROOT.RooArgSet(roobs,rootempl)
                else:
                    rootemps=ROOT.RooArgSet(roobs)
                
                reduced = dset.reduce(RooFit.SelectVars(rootemps),RooFit.Range("fullRange"))
                reduced.SetName("signal_%s_%s"% (signame,cat))
                reducedPdf = dsetPdf.reduce(RooFit.SelectVars(roobsArg),RooFit.Range("fullRange"))
                reducedPdf.SetName("signalforPdf_%s_%s"% (signame,cat))
                
                if options.verbose: 
                    reduced.Print()
                    reducedPdf.Print()
                binned = reduced.binnedClone()
                binned.SetName("signal_%s_%s"% (signame,cat))
                binnedPdf = reducedPdf.binnedClone()
                binnedPdf.SetName("signalforPdf_%s_%s"% (signame,cat))
                if options.verbose: 
                    binned.Print()
                    binnedPdf.Print()
                self.workspace_.rooImport(binned)
                self.workspace_.rooImport(binnedPdf)

                if options.compute_fwhm:
                    if len(options.fwhm_output_file) != 0:
                        file_fwhm = self.open(options.fwhm_output_file,"a",folder=options.ws_dir)
                    else:
                        file_fwhm = self.open("fwhm_%s.json" % fitname,"a",folder=options.ws_dir)
                    # plot signal histogram and compute FWHM
                    canv = ROOT.TCanvas("signal_%s" % (cat),"signal" )
                    nBins = 1000
                    if (options.set_bins_fwhm != None):
                        if (signame in options.set_bins_fwhm.keys()):
                            nBins = int(options.set_bins_fwhm[signame])
                    roobs.setBins(nBins)
                    hist = binned.createHistogram("sigHist",roobs)
                    halfMaxVal = 0.5*hist.GetMaximum()
                    maxBin = hist.GetMaximumBin()
                  
                    binLeft=binRight=xWidth=xLeft=xRight=0

                    for ibin in range(1,maxBin):
                        binVal = hist.GetBinContent(ibin)
                        if (binVal >= halfMaxVal):
                            binLeft = ibin
                            break;
                    for ibin in range(maxBin+1,hist.GetXaxis().GetNbins()+1):
                        binVal = hist.GetBinContent(ibin)
                        if (binVal < halfMaxVal):
                            binRight = ibin-1
                            break;
                    if (binLeft > 0 and binRight > 0 ):
                        xLeft = hist.GetXaxis().GetBinCenter(binLeft)
                        xRight = hist.GetXaxis().GetBinCenter(binRight)
                        xWidth = xRight-xLeft
                        print ("FWHM = %f" % (xWidth))
                        hist.GetXaxis().SetRangeUser(hist.GetXaxis().GetBinCenter(maxBin)-5*xWidth,hist.GetXaxis().GetBinCenter(maxBin)+5*xWidth)
                        hist.Draw("HIST")
                        #canv.SaveAs(options.output_file.replace(".root","_%s_hist.png" % (cat))
                        canv.SaveAs(nameFileOutput.replace(".root",("%s_hist.png" % cat)))
                        sublist_fwhm[cat] = "%f" % xWidth
                    else:
                        print
                        print("Did not succeed to compute the FWHM")
                        print

                ## build RooHistPdf in roobs
                ##pdfDataHist = binned if not options.use_templates else binned.reduce(ROOT.RooArgSet(roobs))
                pdfDataHist = binnedPdf
                pdf=ROOT.RooHistPdf("model_signal_%s_%s"% (signame, cat),"model_signal_%s_%s"% (signame, cat),ROOT.RooArgSet(roobs),pdfDataHist)
                if options.verbose:
                    print "Integral signal pdf    :", pdf.createIntegral(ROOT.RooArgSet(roobs),"templateBinning%s"%cat).getVal()
                print "Integral signal pdf    :", pdf.createIntegral(ROOT.RooArgSet(roobs),"templateBinning%s"%cat).getVal()
                    
                ## prepare binnning: doing it here as it is faster than on the 2D pdf
                plot_signal_binning = None
                if options.plot_signal_binning:
                    nbins, width = options.plot_signal_binning
                    obsmean = pdf.mean(roobs).getVal()
                    width = max(width,pdf.sigma(roobs).getVal()/obsmean*4.)
                    omin, omax = obsmean*(1.-0.5*width), obsmean*(1.+0.5*width)
                    if options.verbose:  print obsmean, omin, omax
                    omin = max(roobs.getMin(),omin)
                    omax = min(roobs.getMax(),omax)
                    if options.verbose: print omin, omax
                    step = (omax-omin)/nbins
                    plot_signal_binnning = []
                    while omin<omax:
                        plot_signal_binnning.append(omin)
                        omin += step                    
                    
                ## prepare semi-parametric model if neded
                if options.use_templates:
                    pdf.SetName("model_signal_%s_%s_%s"% (roobs.GetName(),signame, cat))
                    ppPdf=self.rooPdf( "model_%s_%s_%s" %(rootempl.GetName(),options.template_comp_sig,cat))
                    self.keep([pdf,ppPdf])
                    pdf = ROOT.RooProdPdf("model_signal_%s_%s"% (signame, cat), "model_signal_%s_%s"% (signame, cat),pdf, ppPdf )
                    if options.verbose:
                        print
                        ppPdf.Print()
                        pdf.Print()
                        print "Integral templpdf     :", ppPdf.createIntegral(ROOT.RooArgSet(rootempl,roobs),"templateBinning%s"%cat).getVal()
                        print "Integral templpdf only mgg    :", ppPdf.createIntegral(ROOT.RooArgSet(roobs),"templateBinning%s"%cat).getVal()
                        print "Integral templpdf only templateNdim2_unroll    :", ppPdf.createIntegral(ROOT.RooArgSet(rootempl),"templateBinning%s"%cat).getVal()
                        print "Integral combined pdf    :", pdf.createIntegral(ROOT.RooArgSet(rootempl,roobs),"templateBinning%s"%cat).getVal()
                        print
                    self.plotBkgFit(options,binned,pdf,rootempl,"signal_%s_%s_%s" % (signame,rootempl.GetName(),cat),poissonErrs=True,logy=False,logx=False,plot_binning=rootempl_binning,opts=[RooFit.ProjWData(ROOT.RooArgSet(roobs),binned)], bias_funcs={},sig=True)
                
                self.plotBkgFit(options,reduced,pdf,roobs,"signal_%s_%s_%s" % (signame,roobs.GetName(),cat),poissonErrs=False,sig=True,logx=False,logy=False,
                                plot_binning=plot_signal_binnning)

                ## normalization has to be called <pdfname>_norm or combine won't find it
                norm = self.buildRooVar("%s_norm" %  (pdf.GetName()), [], importToWs=False ) 
                norm.setConstant(True)
                norm.setVal(reduced.sumEntries()) 
                
                ## import pdf and normalization
                self.workspace_.rooImport(pdf,RooFit.RecycleConflictNodes())
                self.workspace_.rooImport(norm)
           
            list_fwhm[signame] = sublist_fwhm
            self.saveWs(options)
                        
            # if signame provided then stop
            if isNameProvided :
                break
        if options.compute_fwhm:
            json_output = json.dumps(list_fwhm, indent=4)
            file_fwhm.write("%s\n" % json_output)            
            options.fwhm_input_file=list_fwhm # in case we run also generateWsBkgnbias
  
        
    ## ------------------------------------------------------------------------------------------------------------
    def plotBkgFit(self,options,dset,pdf,obs,label,blabel=None,extra=None,bias_funcs=None,poissonErrs=True,plot_binning=None,logx=True,logy=True,
                       opts=[],forceSkipBands=False,sig=False):
        ## plot the fit result
        print "Plotting  model ", label, obs.GetName()
        ROOT.TH1D.SetDefaultSumw2(True)
        obsname = obs.GetName()
        if obsname == "mass" or obsname == "mgg":
            obs.SetTitle("m_{#gamma #gamma}")
            obs.setUnit("GeV")
        elif "templateNdim" in obsname:
            subname = obsname.replace("templateNdim","")
            ndim = int(subname[0])
            if "unroll" in obsname:
                obs.SetTitle("template_{%dD}" % ndim)
            else:
                idim = int(subname[-1])
                obs.SetTitle("template^{%d}_{%dD}" % (idim,ndim) )

        invisible = []
        ## dataopts = [,RooFit.MarkerSize(1)]
        dataopts = [RooFit.MarkerSize(1)]+opts
        if poissonErrs:
            dataopts.append(RooFit.DataError(ROOT.RooAbsData.Poisson))
        curveopts = [RooFit.LineColor(ROOT.kBlue)]
        
        if not plot_binning:
            plot_binning = options.plot_binning

        binning = None
        if type(plot_binning) == list:
            if len(plot_binning) > 0:
                if len(plot_binning) == 3:
                    plot_binning[0] = int(plot_binning[0])
                    binning = ROOT.RooBinning(*plot_binning)
                else:
                    binning = ROOT.RooBinning(len(plot_binning)-1,array.array('d',plot_binning))
                obs.setBinning(binning,"plotBinning")
                dset.get()[obs.GetName()].setBinning(binning,"plotBinning")
                binning = "plotBinning"
        elif type(plot_binning) == ROOT.RooBinning:
            obs.setBinning(plot_binning,"plotBinning")
            dset.get()[obs.GetName()].setBinning(plot_binning,"plotBinning")
            binning = "plotBinning"
    #    if options.verbose and binning:
   #         print "Plot binning: ",
  #          dset.get()[obs.GetName()].getBinning(binning).Print()
        doBands = options.plot_fit_bands and not forceSkipBands
        if doBands:
            invisible.append(RooFit.Invisible())
            
        if binning:
            dataopts.append(RooFit.Binning(binning))                        
            frame = obs.frame(RooFit.Range("plotBinning"))
            resid  = obs.frame(RooFit.Range("plotBinning"))
        else:
            frame = obs.frame()
            resid  = obs.frame()
        
        print "Plotting dataset"
        dset.plotOn(frame,*(dataopts+invisible))
        print "Plotting pdf....",
        pdf.plotOn(frame,*(curveopts+invisible))
        print "done"
        pdf.Print()
        dset.Print()
        hist   = frame.getObject(int(frame.numItems()-2))
        fitc   = frame.getObject(int(frame.numItems()-1))
        print hist, fitc
        if extra:
            extra.plotOn(frame,RooFit.LineColor(ROOT.kGreen))
            
        if doBands:
            print "Making fit error bands...",
            onesigma,twosigma = self.plotFitBands(options,frame,dset,pdf,obs,fitc,binning,blabel,bias_funcs)
            pdf.plotOn(frame,*curveopts)
            dset.plotOn(frame,*dataopts)
            
            ronesigma = onesigma.Clone()
            rtwosigma = twosigma.Clone()
            self.keep( [onesigma,twosigma,ronesigma,rtwosigma] )
            for ip in range(ronesigma.GetN()):
                px = ronesigma.GetX()[ip]
                py = ronesigma.GetY()[ip]
                ronesigma.SetPoint(ip,px,0.)
                rtwosigma.SetPoint(ip,px,0.)
                hx = hist.GetX()[ip]
                hy = hist.GetY()[ip]
                
                oerrp, oerrm = ronesigma.GetErrorYhigh(ip), ronesigma.GetErrorYhigh(ip)
                terrp, terrm = rtwosigma.GetErrorYhigh(ip), rtwosigma.GetErrorYhigh(ip)
                herrp, herrm = hist.GetErrorYhigh(ip), hist.GetErrorYhigh(ip)
                ## print oerrp, oerrm, herrp, herrm
                if py > hy:
                    oerrp /= herrm
                    terrp /= herrm
                    oerrm /= herrm
                    terrm /= herrm
                else:
                    oerrp /= herrp
                    terrp /= herrp
                    oerrm /= herrp
                    terrm /= herrp
                ## print oerrp, oerrm, herrp, herrm
                ronesigma.SetPointEYhigh(ip,oerrp),ronesigma.SetPointEYlow(ip,oerrm)
                rtwosigma.SetPointEYhigh(ip,terrp),rtwosigma.SetPointEYlow(ip,terrm)
                
            resid.addObject(rtwosigma,"E3")
            resid.addObject(ronesigma,"E3")
            print "done"
        hresid = frame.residHist(hist.GetName(),fitc.GetName(),True)
        resid.addPlotable(hresid,"PE")
        
        if sig: canv = ROOT.TCanvas("sig_fit_%s" % label, "sig_fit_%s" % label)
        else:canv = ROOT.TCanvas("bkg_fit_%s" % label, "bkg_fit_%s" % label)
        canv.Divide(1,2)
        
        canv.cd(1)
        ROOT.gPad.SetPad(0.,0.35,1.,1.)
        ROOT.gPad.SetLogy(logy)
        ROOT.gPad.SetLogx(logx)
        ROOT.gPad.SetFillStyle(0)
        ROOT.gPad.SetTickx()
        ROOT.gPad.SetTicky()
        
        canv.cd(2)
        ROOT.gPad.SetPad(0.,0.,1.,0.35)
        ROOT.gPad.SetFillStyle(0)
        ROOT.gPad.SetTickx()
        ROOT.gPad.SetTicky()

        canv.cd(1)
        if sig:
            ymin = fitc.GetMinimum()
            ymax = fitc.GetMaximum()
        else:
            ymax = fitc.interpolate(frame.GetXaxis().GetXmin())*2.
            ymin = fitc.interpolate(frame.GetXaxis().GetXmax())*0.25
        if not logx:
            ymin = min(0,ymin)
        frame.GetYaxis().SetRangeUser(ymin,ymax)
        frame.GetXaxis().SetMoreLogLabels()
        frame.GetYaxis().SetLabelSize( frame.GetYaxis().GetLabelSize() * canv.GetWh() / ROOT.gPad.GetWh() )
        frame.Draw()
        canv.cd(2)
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetLogx(logx)
        resid.GetXaxis().SetMoreLogLabels()
        resid.GetYaxis().SetNdivisions(505)
        resid.GetYaxis().SetTitleSize( frame.GetYaxis().GetTitleSize() * 6.5/3.5 )
        resid.GetYaxis().SetTitleOffset( frame.GetYaxis().GetTitleOffset() * 3.5/6.5 ) # not clear why the ratio should be upside down, but it does
        resid.GetYaxis().SetLabelSize( frame.GetYaxis().GetLabelSize() * 6.5/3.5 )
        resid.GetXaxis().SetTitleSize( frame.GetXaxis().GetTitleSize() * 6.5/3.5 )
        resid.GetXaxis().SetLabelSize( frame.GetXaxis().GetLabelSize() * 6.5/3.5 )
        resid.GetYaxis().SetTitle("(data - model) / #sigma_{data}")
        resid.GetYaxis().SetRangeUser( -5., 5. )
        resid.Draw()

        canv.cd(1)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
        ROOT.gPad.SetTopMargin(0.1*margin)
        ROOT.gPad.SetBottomMargin(0.1*margin)

        canv.cd(2)
        margin = ROOT.gPad.GetBottomMargin()+ROOT.gPad.GetTopMargin()
        ROOT.gPad.SetBottomMargin(margin)
        ROOT.gPad.SetTopMargin(0.1*margin)
                
        frame.GetXaxis().SetTitle("")
        frame.GetXaxis().SetLabelSize(0.)
        
        # this will actually save the plots
        self.keep(canv)
        self.autosave(True)


    ## ------------------------------------------------------------------------------------------------------------
    def plotFitBands(self,options,frame,dset,pdf,obs,roocurve,binning=None,slabel=None,bias_funcs=None):
        
        wd = ROOT.gDirectory
        params = pdf.getDependents( self.pdfPars_ )
        snap = params.snapshot()

        onesigma = ROOT.TGraphAsymmErrors()
        twosigma = ROOT.TGraphAsymmErrors()
        bias     = ROOT.TGraphAsymmErrors()

        bands  =  [onesigma,twosigma,bias]
        styles = [ [(style_utils.colors,ROOT.kYellow)],  [(style_utils.colors,ROOT.kGreen+1)], 
                   [(style_utils.colors,ROOT.kOrange)]
                   ]
        for band in bands:
            style_utils.apply( band, styles.pop(0) )
            
        self.keep(bands)
        
        bins = []
        if binning:
            roobins = obs.getBinning(binning)
            for ibin in range(roobins.numBins()):
                bins.append(  (roobins.binCenter(ibin), roobins.binLow(ibin), roobins.binHigh(ibin)) )
        else:
            for ibin in range(1,frame.GetXaxis().GetNbins()+1):
                lowedge = frame.GetXaxis().GetBinLowEdge(ibin)
                upedge  = frame.GetXaxis().GetBinUpEdge(ibin)
                center  = frame.GetXaxis().GetBinCenter(ibin)
                bins.append(  (center,lowedge,upedge) )

        if not bias_funcs: bias_funcs = options.bias_func
        bias_func=None
        if slabel in bias_funcs:
            bias_func = ROOT.TF1("err_correction",bias_funcs[slabel],0,2e+6)        

        for ibin,bin in enumerate(bins):
            center,lowedge,upedge = bin

            nombkg = roocurve.interpolate(center)
            largeNum = nombkg*50.
            largeNum = max(0.1,largeNum)

            if bias_func:
                nombias = bias_func.Integral(lowedge,upedge)
                ## largeNum = max(largeNum,nombias*50.)
            else:
                nombias = 0.

            nlim = ROOT.RooRealVar("nlim%s" % dset.GetName(),"",0.0,-largeNum,largeNum)
            nbias = ROOT.RooRealVar("nbias%s" % dset.GetName(),"",0.0,-largeNum,largeNum)
            biaspdf = ROOT.RooGaussian("nbiasPdf%s" % dset.GetName(),"",nbias,RooFit.RooConst(0.),RooFit.RooConst(nombias))
            nsum = ROOT.RooAddition("nsum%s"%dset.GetName(),"",ROOT.RooArgList(nlim,nbias))
            
            onesigma.SetPoint(ibin,center,nombkg)
            twosigma.SetPoint(ibin,center,nombkg)
            
            nlim.setVal(nombkg)
            if options.verbose or ibin % 10 == 0:
                print "computing error band ", ibin, lowedge, upedge, nombkg,                

            ## if nombkg < 5e-4:
            ##     print
            ##     continue

            obs.setRange("errRange",lowedge,upedge)
            if bias_func and nombias > 0.:
                epdf = ROOT.RooExtendPdf("epdf","",pdf,nsum,"errRange")
                nll = epdf.createNLL(dset,RooFit.Extended(),RooFit.ExternalConstraints( ROOT.RooArgSet(biaspdf) ))
            else:
                epdf = ROOT.RooExtendPdf("epdf","",pdf,nlim,"errRange")
                nll = epdf.createNLL(dset,RooFit.Extended())
            minim = ROOT.RooMinimizer(nll)
            minim.setMinimizerType("Minuit2")
            minim.setStrategy(2)
            minim.setPrintLevel( -1 if not options.verbose else 2)
            minim.migrad()

            if not options.fast_bands:
                minim.setStrategy(0)
                minim.minos(ROOT.RooArgSet(nlim))
                errm, errp = -nlim.getErrorLo(),nlim.getErrorHi()
            else:
                minim.hesse()
                result = minim.lastMinuitFit()
                errm = nlim.getPropagatedError(result)
                errp = errm
                
            onesigma.SetPointError(ibin,center-lowedge,upedge-center,errm,errp)
            
            if options.verbose or ibin % 10 == 0:
                print errp, errm
                
            if not options.fast_bands:
                minim.setErrorLevel(2.)
                minim.migrad()
                minim.minos(ROOT.RooArgSet(nlim))
                errm, errp = -nlim.getErrorLo(),nlim.getErrorHi()
            else:
                result = minim.lastMinuitFit()
                errm = 2.*nlim.getError()
                errp = errm
                
            twosigma.SetPointError(ibin,center-lowedge,upedge-center,errm,errp)
            
            del minim
            del nll

        ### smoothErrors(onesigma)
        ### smoothErrors(twosigma)
        
        frame.addObject(twosigma,"E2")
        frame.addObject(onesigma,"E2")

        itr = snap.createIterator()
        var = itr.Next()
        while var:
            params[var.GetName()].setVal(var.getVal())
            var = itr.Next()
            
        wd.cd()    
        
        return onesigma,twosigma
    
    ## ------------------------------------------------------------------------------------------------------------
    def buildPdf(self,model,name,xvar,order=0,label=None,load=None):
        
        pdf = None
        if not label:
            label = model
        if model == "dijet":                
            pname = "dijet_%s" % name
            linc = self.buildRooVar("%s_lin" % pname,[-100.0,100.0], importToWs=False)
            logc = self.buildRooVar("%s_log" % pname,[-100.0,100.0], importToWs=False)
            linc.setVal(5.)
            logc.setVal(-1.)
            
            self.pdfPars_.add(linc)
            self.pdfPars_.add(logc)
            
            if self.use_custom_pdfs_:
                print "Using custom pdf RooPowLogPdf"
                pdf = ROOT.RooPowLogPdf( pname, pname, xvar, linc, logc)
            else:
                print "Using RooGenericPdf"
                roolist = ROOT.RooArgList( xvar, linc, logc)
                pdf = ROOT.RooGenericPdf( pname, pname, "TMath::Max(1e-50,pow(@0,@1+@2*log(@0)))", roolist )
            
            
            self.keep( [pdf,linc,logc] )
            
        if model == "maxdijet":
            pname = "maxdijet_%s" % name
            linc = self.buildRooVar("%s_lin" % pname,[-100.0,100.0], importToWs=False)
            logc = self.buildRooVar("%s_log" % pname,[-100.0,100.0], importToWs=False)
            linc.setVal(2.)
            logc.setVal(-10.)
            
            self.pdfPars_.add(linc)
            self.pdfPars_.add(logc)
            
            roolist = ROOT.RooArgList( xvar, linc, logc )
            pdf = ROOT.RooGenericPdf( pname, pname, "TMath::Max(1e-30,pow(@0,@1+@2*log(@0)))", roolist )
            
            self.keep( [pdf,linc,logc] )
            
        elif model == "moddijet":
            pname = "moddijet_%s" % name
            lina = self.buildRooVar("%s_lina" % pname,[-100,10], importToWs=False)
            loga = self.buildRooVar("%s_loga" % pname,[-100,10], importToWs=False)
            linb = self.buildRooVar("%s_linb" % pname,[-100,10], importToWs=False)
            sqrb = self.buildRooVar("%s_sqrb" % pname,[], importToWs=False)
            lina.setVal(5.)
            loga.setVal(-1.)
            linb.setVal(-0.1)
            sqrb.setVal(1./13.e+3)
            sqrb.setConstant(1)
            
            
            self.pdfPars_.add(lina)
            self.pdfPars_.add(loga)
            self.pdfPars_.add(linb)
            self.pdfPars_.add(sqrb)
            
            roolist = ROOT.RooArgList( xvar, lina, loga, linb, sqrb )
            pdf = ROOT.RooGenericPdf( pname, pname, "TMath::Max(1e-50,pow(@0,@1+@2*log(@0))*pow(1.-@0*@4,@3))", roolist )
            
            self.keep( [pdf,lina,loga, linb, sqrb] )
        elif model == "expow":
            
            pname = "expow_%s" % name
            lam = self.buildRooVar("%s_lambda" % pname,[], importToWs=False)
            alp = self.buildRooVar("%s_alpha"  % pname,[], importToWs=False)
            lam.setVal(0.)
            alp.setVal(-4.)
            
            self.pdfPars_.add(alp)
            self.pdfPars_.add(lam)
            
            roolist = ROOT.RooArgList( xvar, lam, alp )
            pdf = ROOT.RooGenericPdf( pname, pname, "exp(@1*@0)*pow(@0,@2)", roolist )
            
            self.keep( [pdf,lam,alp] )

        elif model == "expow2":
            
            pname = "expow2_%s" % name
            lam0 = self.buildRooVar("%s_lambda0" % pname,[], importToWs=False)
            lam1 = self.buildRooVar("%s_lambda1" % pname,[], importToWs=False)
            alp = self.buildRooVar("%s_alpha"  % pname,[], importToWs=False)
            lam0.setVal(0.)
            lam1.setVal(0.)
            alp.setVal(2.)
            
            self.pdfPars_.add(alp)
            self.pdfPars_.add(lam0)
            self.pdfPars_.add(lam1)
            
            bla = ROOT.RooArgList(lam0,lam1)
            hmax = ROOT.RooFormulaVar("%s_hmax" %pname,"( @1 != 0. ? (-@0/(4.*@1)>300. && -@0/(4.*@1)<3500. ? @0*@0/(4.*@1+@1) : TMath::Max(@0*3500+2*@1*3500.*3500,@0*3500+2*@1*300.*300)) : @0*3500.)", bla )
            roolist = ROOT.RooArgList( xvar, lam0, lam1, alp, hmax )
            pdf = ROOT.RooGenericPdf( pname, pname, "exp( @1*@0+@2*@0*@0   )*pow(@0, -@3*@3 + @4  )", roolist )
            
            self.keep( [pdf,lam0,lam1,alp,hmax] )

        elif model == "invpow":
            
            pname = "invpow_%s" % name
            slo = self.buildRooVar("%s_slo" % pname,[], importToWs=False)
            alp = self.buildRooVar("%s_alp" % pname,[], importToWs=False)
            slo.setVal(2.e-3)
            alp.setVal(-7.)
            
            self.pdfPars_.add(slo)
            self.pdfPars_.add(alp)
            
            roolist = ROOT.RooArgList( xvar, slo, alp )
            pdf = ROOT.RooGenericPdf( pname, pname, "pow(1+@0*@1,@2)", roolist )
            
            self.keep( [pdf,slo,alp] )

        elif model == "invpowlog":
            
            pname = "invpowlog_%s" % name
            slo = self.buildRooVar("%s_slo" % pname,[], importToWs=False)
            alp = self.buildRooVar("%s_alp" % pname,[], importToWs=False)
            bet = self.buildRooVar("%s_bet" % pname,[], importToWs=False)
            slo.setVal(1.e-3)
            alp.setVal(-4.)
            bet.setVal(0.)
            
            self.pdfPars_.add(slo)
            self.pdfPars_.add(alp)
            self.pdfPars_.add(bet)
            
            roolist = ROOT.RooArgList( xvar, slo, alp, bet )
            pdf = ROOT.RooGenericPdf( pname, pname, "pow(1+@0*@1,@2+@3*log(@0))", roolist )
            
            self.keep( [pdf,slo,alp,bet] )

        elif model == "invpowlin":
            
            pname = "invpowlin_%s" % name
            slo = self.buildRooVar("%s_slo" % pname,[], importToWs=False)
            alp = self.buildRooVar("%s_alp" % pname,[], importToWs=False)
            bet = self.buildRooVar("%s_bet" % pname,[], importToWs=False)
            slo.setVal(1.e-3)
            alp.setVal(-4.)
            bet.setVal(0.)
            
            self.pdfPars_.add(slo)
            self.pdfPars_.add(alp)
            self.pdfPars_.add(bet)
            
            roolist = ROOT.RooArgList( xvar, slo, alp, bet )
            pdf = ROOT.RooGenericPdf( pname, pname, "pow(1+@0*@1,@2+@3*@0)", roolist )
            
            self.keep( [pdf,slo,alp,bet] )

        elif model == "invpow2":
            
            pname = "invpow2_%s" % name
            slo = self.buildRooVar("%s_slo" % pname,[], importToWs=False)
            qua = self.buildRooVar("%s_qua" % pname,[], importToWs=False)
            alp = self.buildRooVar("%s_alp" % pname,[], importToWs=False)
            slo.setVal(1.e-4)
            qua.setVal(1.e-6)
            alp.setVal(-4.)
            
            self.pdfPars_.add(slo)
            self.pdfPars_.add(qua)
            self.pdfPars_.add(alp)
            
            roolist = ROOT.RooArgList( xvar, slo, qua, alp )
            pdf = ROOT.RooGenericPdf( pname, pname, "pow(1+@1*@0+@2*@0*@0,@3)", roolist )
            
            self.keep( [pdf,slo,qua,alp] )
        elif model== "adhoclognorm":
            pname = "adhoclognorm_%s" % name
            mu = self.buildRooVar("%s_mu" % pname,[], importToWs=False)
            twovar = self.buildRooVar("%s_twovar" % pname,[], importToWs=False)
            mu.setVal(5.44)
            twovar.setVal(0.517)
            mu.setConstant(True)
            twovar.setConstant(True)

            self.pdfPars_.add(mu)
            self.pdfPars_.add(twovar)
            
            roolist = ROOT.RooArgList( xvar, mu, twovar )
            pdf = ROOT.RooGenericPdf( pname, pname, "exp(-pow(log(@0)-@1,2)/@2)", roolist )
            self.keep( [pdf,mu,twovar] )
        
        elif model== "fixtruth270":
            pname = "fixtruth270_%s" % name
            linc = self.buildRooVar("%s_lin" % pname,[-100.0,100.0], importToWs=False)
            logc = self.buildRooVar("%s_log" % pname,[-100.0,100.0], importToWs=False)
            linc.setVal(14.7202)
            logc.setVal(-1.59571)
            linc.setConstant(True)
            logc.setConstant(True)

            self.pdfPars_.add(linc)
            self.pdfPars_.add(logc)
            
            roolist = ROOT.RooArgList( xvar, linc, logc )
            pdf = ROOT.RooGenericPdf( pname, pname, "TMath::Max(1e-50,pow(@0,@1+@2*log(@0)))", roolist )
            self.keep( [pdf,linc,logc] )



        if load:
            sname,snap = load
            params = pdf.getDependents(self.pdfPars_)
            itr = snap.createIterator()
            var = itr.Next()
            while var:
                parname = var.GetName().replace(sname,name)
                params[parname].setVal(var.getVal())
                var = itr.Next()
            

        return pdf
      
    
# -----------------------------------------------------------------------------------------------------------
# actual main
if __name__ == "__main__":
    app = CombineApp()
    app.run()
