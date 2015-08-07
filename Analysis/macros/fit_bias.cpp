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
	const int nsampling=500;
    //const int nbins=191;
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
			//cout << " intBin " << intBin << " divided by intRange " << intBin/intSig << endl;
		 	intPdfs[r][bin]=intBin/intSig;
		}
	}
//plot result
	gStyle->SetOptStat(111111);
//	std::vector< TH1F * > histVec;
	Double_t quant28[nbins] ;	
	Double_t quant41[nbins] ;	
	Double_t quant50[nbins] ;	
	Double_t quant59[nbins] ;	
	Double_t quant73[nbins] ;	
	for(int bin=0;bin< nbins;bin++)
	{
		cout << "---------- plot result ----------" << endl;
	//	TCanvas* c1= new TCanvas("c1","c1");
			//get max min values from array
			//throw toys to see if works
			//
		int nbin=100;
		Double_t xmin=0.0;
		Double_t xmax=1.0;
		TH1F* hist=new TH1F("hist","hist",nbin,xmin, xmax);
  		TH1F *cum = new TH1F("cum","cum", nbin, xmin, xmax);
		for(int samp=0; samp< nsampling; samp++)
		{
			hist->Fill(intPdfs[samp][bin]);

		}
  	//	c1->Divide(1,2);
  	//	c1->cd(1);
	//	hist->GetXaxis()->SetLimits(hist->GetXaxis()->GetXmin(), hist->GetXaxis()->GetXmax()  );
	//	hist->Draw();
	//	hist->GetXaxis()->SetLimits((hist->GetMean())-(hist->GetMean()*0.9), (hist->GetMean())+(hist->GetMean()*0.9)  );
		for(int samp=0; samp< nsampling; samp++)
		{
			if(intPdfs[samp][bin] < fabs(hist->GetMean()*0.05))
			{
	    		TCanvas * canvi = new TCanvas("check","check");
	    		canvi->SetLogy();
	    		canvi->SetLogx();
	    		randPdf->plotOn(framei,LineColor(kBlack));
	    		framei->Draw();
		  		canvi->SaveAs(Form("/afs/cern.ch/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_samp%i_bin%i.png",samp,bin));
			}
		}		
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
  	//	c1->cd(2);
  //	cum->Draw();
//compute 68 and 85 percent
		const int qn=5;
		Double_t quant[qn] ;	
		Double_t nquant[qn] ;	
		Double_t prob[qn]={0.275,0.41,0.5,0.59,0.725};
        for (Int_t q =0;q<qn;q++){ 
			cum->GetQuantiles(qn,quant,prob);
		}
		quant28[bin]=quant[0];	
		quant41[bin]=quant[1];	
		quant50[bin]=quant[2];	
		quant59[bin]=quant[3];	
		quant73[bin]=quant[4];	
		cout << quant[0] << " " << quant[1] << " " quant[2] << " " << quant[3] << " " <<  quant[4] << endl;
//		canvi->SaveAs(Form("/afs/cern.ch/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_bin%i.png",bin));
	//	histVec->push_back(hist);
		delete hist;
		delete cum;
		
	}
	//plot 68 and 95 percent 	
	TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
	//get mass bins, set legend
	TGraph *gr28 = new TGraph(nbins,massbins,quant28);
	TGraph *gr41 = new TGraph(nbins,massbins,quant41);
	TGraph *gr50 = new TGraph(nbins,massbins,quant50);
	TGraph *gr59 = new TGraph(nbins,massbins,quant59);
	TGraph *gr73 = new TGraph(nbins,massbins,quant73);
	gr28->SetMarkerStyle(21);
	gr41->SetMarkerStyle(21);
	gr50->SetMarkerStyle(21);
	gr59->SetMarkerStyle(21);
	gr73->SetMarkerStyle(21);
	gr28->SetMarkerColor(kBlue);
	gr41->SetMarkerColor(kRed);
	gr50->SetMarkerColor(kBlack);
	gr59->SetMarkerColor(kRed);
	gr73->SetMarkerColor(kBlue);
	gr28->Draw("ap"); 
	gr41->Draw("p SAME"); 
	gr50->Draw("p SAME"); 
	gr59->Draw("p SAME"); 
	gr73->Draw("p SAME"); 
    gr28->GetXaxis()->SetTitle("mass (GeV)");
    TLegend* leg = new TLegend(0.55, 0.85, .9, .95);
    leg->SetFillColor(0);
	leg->SetHeader("uncertainty");
    leg->AddEntry(gr28,"minus 95%" ,"p");
    leg->AddEntry(gr73,"plus 95%" ,"p");
    leg->AddEntry(gr50,"minus 68%" ,"p");
    leg->AddEntry(gr59,"plus 68%" ,"p");
    leg->AddEntry(gr50,"50 %" ,"p");
	leg->Draw();
	cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_pp_EBEB.png"));
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
