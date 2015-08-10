{
	#include <vector>
	#include "TH1.h"
	#include <algorithm>
	#include <list>
	
	using namespace RooFit;
	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	bool check= false;
	//TODO includes etc
 	TFile* nomfitresfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/multidimfit_fit_self.root");
	//TFile* truthpdffile = new TFile("full_analysis_anv0_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.root");
	TFile* truthpdffile = new TFile("full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/datacard_truth.root");
	TFile* nompdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.root");

	//bkg only
	std::string compList[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE"}; 
//	std::string compList[]={"pp_EBEB"}; 
	std::list<std::string> components(compList,compList+sizeof(compList)/sizeof(std::string)); 

	//const int nbins=135;
	const int nbins=5;
	const int nsampling=500;
	
	for(std::list<std::string>::iterator it = components.begin(); it != components.end(); ++it) {
		TString comp=*it;
		TString fitShapeName=Form("shapeBkg_%s", comp.Data());
		TString fitNormName=Form("shapeBkg_%s__norm", comp.Data());
		
		//load truth pdf

		truthpdffile->cd();
		w->exportToCint("wTruth");
		RooArgSet & obsTruth=RooArgSet(wTruth::mgg,wTruth::templateNdim2_unroll);
		RooProdPdf* fittruthShape=w->pdf(fitShapeName.Data());
		RooProduct* fittruthNorm=w->function(fitNormName.Data());
		cout << "----------- component " << comp.Data() << "----------------------" << endl;
		fittruthShape->Print();
		fittruthNorm->Print();
		wTruth::mgg.setRange("sigTruth_region",wTruth::mgg.getMin(),wTruth::mgg.getMax());
		RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		Double_t inttruthSig=fittruthPdf.createIntegral(obsTruth,"sigTruth_region").getVal()  ;
		fittruthPdf->Print();
		RooPlot * framei = wTruth::mgg.frame(Title("check"),Bins(nbins),Range("sigTruth_region"));
		fittruthPdf->plotOn(framei,LineColor(kRed));

		//load nominal pdf
		nompdffile->cd();
		w->getSnapshot("MultiDimFit");
		w->exportToCint("wNom");
		RooArgSet & obsNom=RooArgSet(wNom::mgg,wNom::templateNdim2_unroll);
		wNom::mgg.setRange("sig_region",wNom::mgg.getMin(),wNom::mgg.getMax());
		RooProdPdf* fitnomShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomNorm=w->function(fitNormName.Data());
		fitnomShape->Print();
		fitnomNorm->Print();	
		RooExtendPdf* fitnomPdf=new RooExtendPdf("fitnomPdf","fitnomPdf",*fitnomShape,*fitnomNorm);
		Double_t intnomSig=0. ;
		intnomSig=fitnomPdf.createIntegral(obsNom,"sig_region").getVal()  ;
		fitnomPdf->Print();
		fitnomPdf->plotOn(framei,LineColor(kBlue));
		cout << inttruthSig << " " << intnomSig << endl;
		w->loadSnapshot("MultiDimFit");
		RooProdPdf* randShape=w->pdf(fitShapeName.Data());
		RooProduct* randNorm=w->function(fitNormName.Data());
		RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",*randShape,*randNorm);
		RooArgSet* pdfParams = randPdf->getParameters(obsNom) ;
		pdfParams.Print();	
		//get fitresult and randomize parameters in covariance matrix
		nomfitresfile->cd();
		//const TMatrixDSym & cov=fit->covarianceMatrix();
		Double_t intPdfs[nsampling][nbins];
		
		Double_t inttruthBin[nbins];
		Double_t intnomBin[nbins];
		Double_t massbins[nbins];
		
		for(int r=0;r< nsampling;++r){	
			if(r==100 || r==300){cout << "---------------------------------  sampling" << r << "----------" << endl;}
		//square root method for decomposition automatically applied
		
			RooArgList & randParams=fit.randomizePars();
			*pdfParams = randParams ;
			Double_t intSig=0.;
			Double_t intSig=randPdf.createIntegral(obsNom,"sig_region").getVal()  ;
			
			double binning =50.;
			for(int bin=0; bin <nbins;++bin){
				Double_t intBin=0.;
				Double_t max= wNom::mgg.getMin() + binning*bin +binning;
				Double_t min= wNom::mgg.getMin() + binning*bin;
				if(bin==0){ massbins[bin]=(max+wNom::mgg.getMin())/2.;}
				else{massbins[bin]=(max+massbins[bin-1])/2.;}
				
				wNom::mgg.setRange("bin_region",min,max);
				wTruth::mgg.setRange("binTruth_region",min,max);
				intBin=randPdf.createIntegral(obsNom,"bin_region").getVal()  ;
				intPdfs[r][bin]=intBin/intSig;
			
				if(r==0)
				{
					inttruthBin[bin]=0.;
					inttruthBin[bin]=(fittruthPdf.createIntegral(obsTruth,"binTruth_region").getVal())/inttruthSig ;
					cout <<  " truth "<<inttruthBin[bin] <<" " << inttruthSig  << endl;
		
					intnomBin[bin]=0.;
					intnomBin[bin]=(fitnomPdf.createIntegral(obsNom,"bin_region").getVal())/intnomSig  ;
					cout << intPdfs[r][bin] << " "<< intSig << " truth "<<inttruthBin[bin] <<" " << inttruthSig <<"  nom "<< intnomBin[bin] << " "<< intnomSig << endl;
				
				}
			
			}
		}
		return;
		//plot result histo per bin for integral values from randomized pdfs
		gStyle->SetOptStat(111111);
		Double_t mean[nbins] ;	
		Double_t quant68[nbins] ;	
		Double_t quant95[nbins] ;	
		Double_t quant68m[nbins] ;	
		Double_t quant95m[nbins] ;	
		Double_t pull68[nbins] ;	
		Double_t pull95[nbins] ;	
		for(int bin=0;bin< nbins;bin++)
		{
			cout << "---------- plot result "<< bin << " ----------" << endl;
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
				//if(intPdfs[samp][bin] < fabs(hist->GetMean()*0.05))
				//if(check && (intPdfs[samp][bin] < fabs(hist->GetMean()*0.05)))
				if(check)
				{
					TCanvas * canvi = new TCanvas("check","check");
					canvi->SetLogy();
					canvi->SetLogx();
					randPdf->plotOn(framei,LineColor(kBlack));
					framei->Draw();
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_%s__samp_%i_bin%i.png",comp.Data(),samp,bin));
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
				c1->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_%s_bin%i.png",comp.Data(),bin));
			}
			//compute 68 and 95 percent
			const int qn=4;
			Double_t quant[qn] ;	
			Double_t prob[qn]={0.025,0.16,0.84,0.975};
			cum->GetQuantiles(qn,quant,prob);
			mean[bin]= inttruthBin[bin]-intnomBin[bin];	
			quant68[bin]= intnomBin[bin]+quant[2];	
			quant95[bin]= intnomBin[bin]+quant[3];	
			quant68m[bin]=intnomBin[bin]-quant[1];	
			quant95m[bin]=intnomBin[bin]-quant[0];	
			//pull function
			if (intnomBin[bin]<= inttruthBin[bin]){
				pull68[bin]=(inttruthBin[bin]-intnomBin[bin])/(intnomBin[bin]+quant[2]);
				pull95[bin]=(inttruthBin[bin]-intnomBin[bin])/(intnomBin[bin]+quant[3]);
			}
			else {
				pull68[bin]=(intnomBin[bin]-inttruthBin[bin])/(intnomBin[bin]-quant[1]);
				pull95[bin]=(intnomBin[bin]-inttruthBin[bin])/(intnomBin[bin]-quant[0]);
			}
			delete hist;
			delete cum;
			
		}
		//plot 68 and 95 percent 	
		TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
		//get mass bins, set legend
		TGraph *gr68 = new TGraph(nbins,massbins,quant68);
		TGraph *gr95 = new TGraph(nbins,massbins,quant95);
		TGraph *grmean = new TGraph(nbins,massbins,mean);
		gr68->SetMarkerStyle(21);
		gr95->SetMarkerStyle(21);
		gr68->SetMarkerColor(kYellow);
		gr68->SetLineColor(gr68->GetMarkerColor());
		gr68->SetFillColor(gr68->GetMarkerColor());
		gr68->SetFillStyle(3001);
		gr95->SetMarkerColor(kGreen+1);
		gr95->SetLineColor(gr95->GetMarkerColor());
		gr95->SetFillColor(gr95->GetMarkerColor());
		gr95->SetFillStyle(3001);
		
		TGraph *gr68m = new TGraph(nbins,massbins,quant68m);
		TGraph *gr95m = new TGraph(nbins,massbins,quant95m);
		gr68m->SetMarkerStyle(21);
		gr95m->SetMarkerStyle(21);
		gr68m->SetMarkerColor(gr68->GetMarkerColor());
		gr68m->SetLineColor(gr68->GetMarkerColor());
		gr68m->SetFillColor(gr68->GetMarkerColor());
		gr95m->SetMarkerColor(gr95->GetMarkerColor());
		gr95m->SetLineColor(gr95->GetMarkerColor());
		gr95m->SetFillColor(gr95->GetMarkerColor());
		grmean->Draw("pC a"); 
		
		gr95->Draw("pC SAME"); 
		gr68->Draw("pC SAME"); 
		gr95m->Draw("pC SAME"); 
		gr68m->Draw("pC SAME"); 
		gr68->GetXaxis()->SetTitle("mass (GeV)");
		TLegend* leg = new TLegend(0.55, 0.8, .9, .9);
		leg->SetFillColor(0);
		leg->SetHeader("uncertainty");
		leg->AddEntry(gr68,"68%" ,"l");
		leg->AddEntry(gr95,"95%" ,"l");
		leg->Draw();
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_%s.png",comp.Data()),"png");
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_%s.root",comp.Data()));
		//pull distribution
		TGraph *grpull68 = new TGraph(nbins,massbins,pull68);
		TGraph *grpull95 = new TGraph(nbins,massbins,pull95);
		grpull68->SetMarkerStyle(21);
		grpull95->SetMarkerStyle(21);
		grpull68->SetMarkerColor(kYellow+1);
		grpull95->SetMarkerColor(kGreen+1);
		grpull68->Draw("pC a"); 
		
		grpull95->Draw("pC SAME"); 
		grpull68->GetXaxis()->SetTitle("mass (GeV)");
		grpull68->GetYaxis()->SetTitle("pull");
		TLegend* leg = new TLegend(0.55, 0.8, .9, .9);
		leg->SetFillColor(0);
		leg->SetHeader("uncertainty");
		leg->AddEntry(grpull68,"68%" ,"l");
		leg->AddEntry(grpull95,"95%" ,"l");
		leg->Draw();
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cpull_%s.png",comp.Data()),"png");

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
