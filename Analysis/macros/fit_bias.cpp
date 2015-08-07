{
	#include <vector>
	#include "TH1.h"
	#include <algorithm> 
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
	
	const int nsampling=500;
//	const int nsampling=50;
    const int nbins=140;
	//get correct number of bins
    const int nbins=10;
	Double_t intPdfs[nsampling][nbins];
	Double_t massbins[nbins];
	massbins[0]=0.;
	for(int r=0;r< nsampling;++r){	
		if(r==100 || r==300){cout << "---------------------------------  sampling" << r << "----------" << endl;}
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
			massbins[bin]=max;
			/*if(bin==0)
			{
			massbins[bin]=(max-ws::mgg.getMin())/2.;
			}
			else
			{
			
			massbins[bin]=(max-massbins[bin-1])/2.;
			}
			*/
	     	ws::mgg.setRange("bin_region",ws::mgg.getMin(),max);
			intBin=randPdf.createIntegral(ws::mgg,"bin_region").getVal()  ;
//			cout << " intBin " << intBin << " divided by intRange " << intBin/intSig << endl;
		 	intPdfs[r][bin]=intBin/intSig;

		}
	}
//plot result
	gStyle->SetOptStat(111111);
//	std::vector< TH1F * > histVec;
	Double_t quant2p5[nbins] ;	
	Double_t quant16[nbins] ;	
	Double_t quant50[nbins] ;	
	Double_t quant84[nbins] ;	
	Double_t quant975[nbins] ;	
	for(int bin=0;bin< nbins;bin++)
	{
		cout << "---------- plot result ----------" << endl;
	//	TCanvas* c1= new TCanvas("c1","c1");
			//get max min values from array
			//throw toys to see if works
			//
		double xmin=1.;
		double xmax=0.;
		//get min and max element for histo
		for(unsigned int j=0; j<nsampling; ++j){
				if(intPdfs[j][bin] > xmax){
         			xmax = intPdfs[j][bin];
				}
				if(intPdfs[j][bin] < xmin){
         			xmin = intPdfs[j][bin];
				}
		  }
		int nbin=100;
		TH1F* hist=new TH1F("hist","hist",nbin,xmin, xmax);
  		TH1F *cum = new TH1F("cum","cum", nbin, xmin, xmax);
		for(int samp=0; samp< nsampling; samp++)
		{
			hist->Fill(intPdfs[samp][bin]);

		}
  	//	c1->Divide(1,2);
  	//	c1->cd(1);
	//	hist->Draw();
		for(int samp=0; samp< nsampling; samp++)
		{
			if(intPdfs[samp][bin] < fabs(hist->GetMean()*0.05))
			{
	    		TCanvas * canvi = new TCanvas("check","check");
	    		canvi->SetLogy();
	    		canvi->SetLogx();
	    		randPdf->plotOn(framei,LineColor(kBlack));
	    		framei->Draw();
		  		canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_samp%i_bin%i.png",samp,bin));
			}
		}		
  		// We compute the cumulative version of "gau"
  		int total = 0;
  		for (int i=0;i<nbin;i++)
    	{
     		total += hist->GetBinContent(i);
     		for (int m=0;m<total;m++)
       		{
        		cum->AddBinContent(i);
       		}
    	}
  		double norme = 1/hist->Integral();
 		cum->Scale(norme);
  	//	c1->cd(2);
  	//	cum->Draw();
	//	c1->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_bin%i.png",bin));
//compute 68 and 85 percent
		const int qn=5;
		Double_t quant[qn] ;	
		Double_t nquant[qn] ;	
		Double_t prob[qn]={0.025,0.16,0.5,0.84,0.975};
		cum->GetQuantiles(qn,quant,prob);
		quant2p5[bin]=quant[0];	
		quant16[bin]=quant[1];	
		quant50[bin]=quant[2];	
		quant84[bin]=quant[3];	
		quant975[bin]=quant[4];	
		delete hist;
		delete cum;
		
	}
	//plot 68 and 95 percent 	
	TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
	//get mass bins, set legend
	TGraph *gr2p5 = new TGraph(nbins,massbins,quant2p5);
	TGraph *gr16 = new TGraph(nbins,massbins,quant16);
	TGraph *gr50 = new TGraph(nbins,massbins,quant50);
	TGraph *gr84 = new TGraph(nbins,massbins,quant84);
	TGraph *gr975 = new TGraph(nbins,massbins,quant975);
	gr2p5->SetMarkerStyle(21);
	gr16->SetMarkerStyle(21);
	gr50->SetMarkerStyle(21);
	gr84->SetMarkerStyle(21);
	gr975->SetMarkerStyle(21);
	gr2p5->SetMarkerColor(kBlue);
	gr16->SetMarkerColor(kRed);
	gr50->SetMarkerColor(kBlack);
	gr84->SetMarkerColor(kRed);
	gr975->SetMarkerColor(kBlue);
	gr2p5->Draw("ap"); 
	gr16->Draw("p SAME"); 
	gr50->Draw("p SAME"); 
	gr84->Draw("p SAME"); 
	gr975->Draw("p SAME"); 
    gr2p5->GetXaxis()->SetTitle("mass (GeV)");
    TLegend* leg = new TLegend(0.55, 0.85, .9, .95);
    leg->SetFillColor(0);
	leg->SetHeader("uncertainty");
    leg->AddEntry(gr2p5,"minus 95%" ,"p");
    leg->AddEntry(gr975,"plus 95%" ,"p");
    leg->AddEntry(gr16,"minus 68%" ,"p");
    leg->AddEntry(gr84,"plus 68%" ,"p");
    leg->AddEntry(gr50,"50 %" ,"p");
	leg->Draw();
//	cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_pp_EBEB.png"));
	cbias->SaveAs(Form("cbias_pp_EBEB.png"));
}
/*
void max_min(int *a, int n, int *minn, int *maxx)  {
   int i;
   for(i = 0; i < n; i++ )  {
      if(a[i] > maxx)
         maxx = array[i];
 
      //add the if statement for minn, here
   }
}
*/

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
