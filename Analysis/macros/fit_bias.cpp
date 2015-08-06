{
	#include <vector>
	#include "TH1.h"
	using namespace RooFit;
 
	//TODO includes etc
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
	//TODO get integral
	// RooAddPdf & fitPdf=ws::pdf_binEBEE_nuis;
	 RooAddPdf & randPdf=ws::pdf_binEBEB_nuis;
	 //cout << randPdf.createIntegral(ws::mgg,"sig_region").getVal()  << endl;
	 RooAddPdf* fitPdf=new RooAddPdf(randPdf,"fitPdf");
//	RooAddPdf* randPdf=fitPdf->clone("randPdf");
	//cout << randPdf->getVal(ws::pp_EBEB_frac) << endl;
//	double test=ws::n_exp_final_binEBEB_proc_pf.getVal();
 //   cout << test << endl; 
 	RooArgSet & obs=RooArgSet(ws::mgg,ws::templateNdim2_unroll);
	RooArgSet* pdfParams = randPdf.getParameters(obs) ;
//	pdfParams.Print("v");
	//get fitresult and randomize parameters in covariance matrix
	nomfitresfile->cd();
	const TMatrixDSym & cov=fit->covarianceMatrix();
	
	const int nsampling=4;
	//TODO loop to create arrrays
    //const int nbins=191;
    const int nbins=191;
	Double_t intPdfs[nsampling][nbins];
	for(int r=0;r< nsampling;++r){	
	//square root method for decomposition automatically applied
		RooArgList & randParams=fit.randomizePars();
		*pdfParams = randParams ;
//		pdfParams.Print("v");
	//  plot vs mass
	  	double start=270.;
	  //get from dataset nbins
	  	double binning =50.;
	  	for(int bin=0; bin <nbins;++bin){
			Double_t integral=0.;
			Double_t max= ws::mgg.getMin() + binning*bin +binning;
	     	ws::mgg.setRange("sig_region",ws::mgg.getMin(),max);
			integral=randPdf.createIntegral(ws::mgg,"sig_region").getVal()  ;
			cout << fitPdf->createIntegral(ws::mgg,"sig_region").getVal()  ;
			cout << integral << endl;
		 	intPdfs[r][bin]=integral;
			
		}

	}
//plot result
 	
	ws::mgg.setRange("sig_region",ws::mgg.getMin(),ws::mgg.getMax());
	gStyle->SetOptStat(0);
	std::vector< TH1F * > histVec;
	int nbins=2;
	for(int bin=0;bin< nbins;bin++)
	{
		TCanvas* c1= new TCanvas("c1","c1");
			//get max min values from array
			//throw toys to see if works
			//
		int nbin=100;
		Double_t xmin=1e15;
		Double_t xmax=5e16;
		TH1F* hist=new TH1F("hist","hist",nbin,xmin, xmax);
  		TH1F *cum = new TH1F("cum","cum", nbin, xmin, xmax);
			
		for(int samp=0; samp< nsampling; samp++)
		{
			hist->Fill(intPdfs[samp][bin]);
		}

  		c1->Divide(1,2);

  		//TH1F *gau = new TH1F("gau","", nbbin, xmin, xmax);
  		//gau->FillRandom("gaus",10000);
  		c1->cd(1);
	  	//gau->Draw();
		hist->Draw();

  		// We compute the cumulative version of "gau"
  		int total = 0;
  		for (int i=0;i<nbin;i++)
    	{
     		total += hist->GetBinContent(i);
     	for (int k=0;k<total;k++)
       		{
        		cum->AddBinContent(i);
       		}
    	}
  		double norme = 1/hist->Integral();
  		cout << norme << endl;
 		cum->Scale(norme);
  		c1->cd(2);
  		cum->Draw();
}	
		//TH1* cum=hist->GetCumulative();
		//cum->Draw("SAME");
	//	histVec->push_back(hist);
	//	delete hist;
		
		//do check plots
	}
	
}

