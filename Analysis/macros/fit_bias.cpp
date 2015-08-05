{
gSystem->Load("libHiggsAnalysisCombinedLimit");
gSystem->Load("libdiphotonsUtils");
	using namespace RooFit;
	TFile* nomfitresfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/multidimfit_fit_self.root");
	TFile* fitpdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.root");
	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	fitpdffile->cd();
	//implement also control region and EBEE category like plot_fit.C
	

	RooArgSet* snap = w->getSnapshot("MultiDimFit");
	w->exportToCint("ws");
	RooAddPdf fitpdf=ws::pdf_binEBEB_nuis;
	fitpdf.Print();
	//double test=fitpdf.getVal(ws::pp_EBEB_frac);
    RooArgSet* pdfParams = fitpdf.getParameters(RooArgSet(ws::mgg,ws::templateNdim2_unroll)) ; 
	//get fitresult and randomize parameters in covariance matrix
	nomfitresfile->cd();
	const TMatrixDSym & cov=fit->covarianceMatrix();
	int nsampling=2;
	for(int bin=0;bin< nsampling;bin++){	
	//square root method for decomposition automatically applied
		RooArgList & ranParams=fit.randomizePars();
		*pdfParams = ranParams ;
		fitpdf.Print();
		//check if really randomized, plot the two pdfs an look at values and parameters
//    	TIterator* itr = snap.createIterator();
  //  	RooRealVar* var = itr.Next();
    //    while var:
                //parname = var.GetName().replace(snap.GetName(),)
                //eventually replace name because same for fit truth
	//		parname = var.GetName();
      //      pdfParams[parname].setVal(var.getVal());
        //    var = itr.Next()
              //      apdf = self.buildPdf(model,"asimov_model_%s%s" % (comp,cat), asimobs )
                //    apdf.fitTo(adset,*fitops)
                  //  snap = ("asimov_model_%s%s" % (comp,cat), apdf.getDependents( self.pdfPars_ ).snapshot())                    
		  
	}
}
