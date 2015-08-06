{
	using namespace RooFit;
 	TFile* nomfitresfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/multidimfit_fit_self.root");
	TFile* fitpdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH120.root");
	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	fitpdffile->cd();
	//implement also control region and EBEE category like plot_fit.C
	
//    RooArgSet* snap = w->getSnapshot("MultiDimFit");
	w->loadSnapshot("MultiDimFit");
	w->exportToCint("ws");
	//get address of pdfs
	RooAddPdf & fitPdf=ws::pdf_binEBEB_nuis;
	RooAddPdf* randPdf=fitPdf->Clone("randPdf");
	//cout << randPdf->getVal(ws::pp_EBEB_frac) << endl;
//	double test=ws::n_exp_final_binEBEB_proc_pf.getVal();
 //   cout << test << endl; 
 	RooArgSet & obs=RooArgSet(ws::mgg,ws::templateNdim2_unroll);
	RooArgSet* pdfParams = randPdf.getParameters(obs) ;
	pdfParams.Print("v");
	//get fitresult and randomize parameters in covariance matrix
	nomfitresfile->cd();
	const TMatrixDSym & cov=fit->covarianceMatrix();
	
	int nsampling=2;
	for(int bin=0;bin< nsampling;bin++){	
	//square root method for decomposition automatically applied
		RooArgList & randParams=fit.randomizePars();
		*pdfParams = randParams ;
		pdfParams.Print("v");
		//cout << randPdf.getVal(ws::pp_EBEB_frac) << endl;
	
//	double test2=ws::n_exp_final_binEBEB_proc_pf.getVal();
//	cout << test2 << endl;
	//check if really randomized, plot the two pdfs an look at values and parameters


		
		
		
		
		
		
		
		/*	
	TIterator* itr = randParams->createIterator();
	TObject* var = itr->Next();
    
	while (var>0):{
    //RooRealVar &var_r = dynamic_cast<TObject &>( var);
    RooAbsArg &var_r = dynamic_cast<TObject &>( var);
	// TString parname = var.GetName().replace(snap.GetName(),"try");
                //eventually replace name because same for fit tru
 	TString parname= var_r->GetName();
	Double_t varVal=0.;
//	varVal=var_r->getVal();
	RooAbsArg& var_old=pdfParams.find(parname);
	pdfParams.replace(var_old,var_r);
	//((RooRealVar*)(pdfParams->find(parname))).setVal(0.0);
//	RooAbsArg&  varPdf= pdfParams[parname];
  //  RooRealVar&  var_Pdfr = dynamic_cast<RooAbsArg & >( varPdf);
	//varPdf.setVal(varVal);
	//cout << var_Pdfr << endl;
    var = itr->Next();
	}
*/

	//  plot vs mass
	  double start=270.;
	  //get from dataset nbins
	  //int nbins=191;
	  int nbins=5;
	  double binning =50.;
	  for(int bin=0; bin <=nbins;bin++){
		 Double_t intTruth=0.;
		 Double_t intRand=0.;
		 Double_t max= ws::mgg.getMin() + binning*bin;
	     ws::mgg.setRange("sig_region",ws::mgg.getMin(),max);
		 intTruth=fitPdf.createIntegral(ws::mgg,"sig_region").getVal()  ; 
		 intRand=randPdf.createIntegral(ws::mgg,"sig_region").getVal()  ; 
		 Double_t diff= intTruth-intRand;
		 cout << "intTruth "<< intTruth << " intRand "<< intRand << " diff " << diff << endl;
		}

	}
	
}

