{
	#include <vector>
	#include "TH1.h"
	#include <algorithm>
	#include <list>
	
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
	std::string compList[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE","pf_EBEB_control","pf_EBEE_control"}; 
	std::list<std::string> components(compList,compList+sizeof(compList)/sizeof(std::string)); 
/*
	for(std::list<std::string>::iterator it = components.begin(); it != components.end(); ++it) {
		TString comp=*it;
		TString fitShapeName=Form("ws::shapeBkg_%s", comp.Data());
		if(comp.Data()=="pf_EBEE_control"|| comp.Data()=="pf_EBEB_control"){
			TString j=comp.Data();
			j.erase (j.end()-8,j.end());  
			TString fitNormName=Form("ws::shapeBkg_%s__norm", comp.Data());
		}
		else {
		TString fitNormName=Form("ws::shapeBkg_%s__norm", comp.Data());
		}	
		*/
		RooProdPdf& fitShape=ws::shapeBkg_pp_EBEB;
	  RooProduct & fitNorm=ws::shapeBkg_pp_EBEB__norm;
	//	cout << fitShapeName.Data() << endl;
//		RooProdPdf& fitShape=fitShapeName.Data();
//		RooProduct & fitNorm=fitNormName.Data();
//		fitShape.Print();
//		fitNorm.Print();
//	return;
	
	RooExtendPdf* fitPdf=new RooExtendPdf("fitPdf","fitPdf",fitShape,fitNorm);
	ws::mgg.setRange("sig_region",ws::mgg.getMin(),ws::mgg.getMax());
	RooPlot * framei = ws::mgg.frame(Title("check"),Bins(134),Range("sig_region"));
	fitPdf->plotOn(framei,LineColor(kBlue));
	w->loadSnapshot("MultiDimFit");
	RooProdPdf & randShape=ws::shapeBkg_pp_EBEB;
	RooProduct & randNorm=ws::shapeBkg_pp_EBEB__norm;
	RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",randShape,randNorm);
 	RooArgSet & obs=RooArgSet(ws::mgg,ws::templateNdim2_unroll);
	RooArgSet* pdfParams = randPdf->getParameters(obs) ;
	//get fitresult and randomize parameters in covariance matrix
	nomfitresfile->cd();
	//const TMatrixDSym & cov=fit->covarianceMatrix();
	const int nbins=140;
	const int nsampling=500;
	//get correct number of bins
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
			//massbins[bin]=max;
			if(bin==0)
			{
			massbins[bin]=(max-ws::mgg.getMin())/2.;
			}
			else
			{
			massbins[bin]=(max-massbins[bin-1])/2.;
			}
			
	     	ws::mgg.setRange("bin_region",ws::mgg.getMin(),max);
			intBin=randPdf.createIntegral(ws::mgg,"bin_region").getVal()  ;
		 	intPdfs[r][bin]=intBin/intSig;

		}
	}
	//plot result histo per bin for integral values from randomized pdfs
	gStyle->SetOptStat(111111);
	Double_t quant68[nbins] ;	
	Double_t quant95[nbins] ;	
	for(int bin=0;bin< nbins;bin++)
	{
		cout << "---------- plot result ----------" << endl;
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
		if(check)
		{
			TCanvas* c1= new TCanvas("c1","c1");
  			c1->Divide(1,2);
  			c1->cd(1);
			hist->Draw();
		}
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
		  		canvi->SaveAs(Form("checkDiff_samp%i_bin%i.png",samp,bin));
			}
		}		
  		// We compute the cumulative
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
		if(check)
		{
  			c1->cd(2);
  			cum->Draw();
			c1->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_bin%i.png",bin));
			c1->SaveAs(Form("Histo_bin%i.png",bin));
		}
		//compute 68 and 85 percent
		const int qn=5;
		Double_t quant[qn] ;	
		Double_t nquant[qn] ;	
		Double_t prob[qn]={0.025,0.16,0.84,0.975};
		cum->GetQuantiles(qn,quant,prob);
		quant68[bin]=quant[2]-quant[1];	
		quant95[bin]=quant[3]-quant[0];	
		delete hist;
		delete cum;
		
	}
	Double_t quant68=
	//plot 68 and 95 percent 	
	TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
	//get mass bins, set legend
	TGraph *gr68 = new TGraph(nbins,massbins,quant68);
	TGraph *gr95 = new TGraph(nbins,massbins,quant95);
	gr68->SetMarkerStyle(21);
	gr95->SetMarkerStyle(21);
	gr68->SetMarkerColor(kBlue);
	gr95->SetMarkerColor(kRed);
	gr68->Draw("ap"); 
	gr95->Draw("p SAME"); 
    gr68->GetXaxis()->SetTitle("mass (GeV)");
    TLegend* leg = new TLegend(0.55, 0.85, .9, .95);
    leg->SetFillColor(0);
	leg->SetHeader("uncertainty");
    leg->AddEntry(gr68,"68%" ,"p");
    leg->AddEntry(gr95,"95%" ,"p");
	leg->Draw();
	cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_pp_EBEB.png"));
	cbias->SaveAs(Form("cbias_pp_EBEB.png"));
	cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_pp_EBEB.root"));
	cbias->SaveAs(Form("cbias_pp_EBEB.root"));
//	}
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
