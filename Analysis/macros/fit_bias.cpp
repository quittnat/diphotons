{
	#include <vector>
	#include "TH1.h"
	using namespace RooFit;
	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
 
	//TODO includes etc
	//do each component per category + control
 	TFile* nomfitresfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/multidimfit_fit_self.root");
	TFile* fitpdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.root");
	fitpdffile->cd();
	w->getSnapshot("MultiDimFit");
	w->exportToCint("ws");
	RooProdPdf& fitShape=ws::shapeBkg_pp_EBEB;
	RooProduct & fitNorm=ws::shapeBkg_pp_EBEB__norm;
	RooExtendPdf* fitPdf=new RooExtendPdf("fitPdf","fitPdf",fitShape,fitNorm);
	ws::mgg.setRange("sig_region",ws::mgg.getMin(),ws::mgg.getMax());
	RooPlot * framei = ws::mgg.frame(Title("check"),Bins(134),Range("sig_region"));
	fitPdf->plotOn(framei,LineColor(kBlue));
//	fitPdf.Print();
	//get address of pdfs
	w->loadSnapshot("MultiDimFit");
	RooProdPdf & randShape=ws::shapeBkg_pp_EBEB;
	RooProduct & randNorm=ws::shapeBkg_pp_EBEB__norm;
	RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",randShape,randNorm);
 	RooArgSet & obs=RooArgSet(ws::mgg,ws::templateNdim2_unroll);
	RooArgSet* pdfParams = randPdf->getParameters(obs) ;
	//get fitresult and randomize parameters in covariance matrix
	nomfitresfile->cd();
	const TMatrixDSym & cov=fit->covarianceMatrix();
	
	//const int nsampling=500;
	const int nsampling=2;
    //const int nbins=191;
	//get correct number of bins
    const int nbins=2;
	Double_t intPdfs[nsampling][nbins];
	for(int r=0;r< nsampling;++r){	
	//square root method for decomposition automatically applied
		RooArgList & randParams=fit.randomizePars();
		*pdfParams = randParams ;
		Double_t intSig=0.;
		intSig=randPdf.createIntegral(ws::mgg,"sig_region").getVal()  ;
	//  plot vs mass
	  	double start=270.;
	  //get from dataset nbins
	  	double binning =50.;
	  	for(int bin=0; bin <nbins;++bin){
			Double_t intBin=0.;
			Double_t max= ws::mgg.getMin() + binning*bin +binning;
	     	ws::mgg.setRange("bin_region",ws::mgg.getMin(),max);
			intBin=randPdf.createIntegral(ws::mgg,"bin_region").getVal()  ;
			//cout << " intBin " << intBin << " divided by intRange " << intBin/intSig << endl;
		 	intPdfs[r][bin]=intBin/intSig;
			/*if(intPdfs[r][1] < 0.01)
			{
	    		TCanvas * canvi = new TCanvas("check","check");
	    		canvi->SetLogy();
	    		canvi->SetLogx();
	    		randPdf->plotOn(framei,LineColor(kBlack));
	    		framei->Draw();
			}	
			*/
		}
	}
//plot result
	gStyle->SetOptStat(111111);
	std::vector< TH1F * > histVec;
	for(int bin=0;bin< nbins;bin++)
	{
		TCanvas* c1= new TCanvas("c1","c1");
			//get max min values from array
			//throw toys to see if works
			//
		int nbin=100;
		Double_t xmin=0.0;
		Double_t xmax=1.;
		TH1F* hist=new TH1F("hist","hist",nbin,xmin, xmax);
  		TH1F *cum = new TH1F("cum","cum", nbin, xmin, xmax);
			
		for(int samp=0; samp< nsampling; samp++)
		{
			hist->Fill(intPdfs[samp][bin]);
		}
  		c1->Divide(1,2);
  		c1->cd(1);
		hist->Draw();
		hist->GetXaxis()->SetRangeUser(hist->GetMinimum(), hist->GetMaximum()  );
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
	//	histVec->push_back(hist);
	//	delete hist;
		
	}
	
}

/*
void PrintProgress(Long64_t entry)
{
    int step = 10; 
    // Adapt step in powers of 10 (every 10 below 100, every 100 below 1000, etc.)
// Method that prints the progress at reasonable frequency
    Long64_t power = 1;
    for ( size_t i=1; i<10; ++i )
   	{ // up to 10^10...
        power *= 10; 
        if ( !(entry/power) ) break;
        step = power;
    }   
*/
