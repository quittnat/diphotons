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
 //	TFile* nomfitresfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/multidimfit_fit_self.root");
	//TFile* truthpdffile = new TFile("full_analysis_anv0_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.root");
//	TFile* truthpdffile = new TFile("full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/datacard_truth.root");
//	TFile* nompdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.root");
 	TFile* nomfitresfile = new TFile("PasqualeFit/full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/multidimfit_fit_self.root");
	TFile* truthpdffile = new TFile("PasqualeFit/full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/higgsCombine_truth.GenerateOnly.mH0.123456.root");
	TFile* nompdffile = new TFile("PasqualeFit/full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.root");

	//bkg only
//	std::string compList[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE"}; 
	std::string compList[]={"pp_EBEB"}; 
	std::list<std::string> components(compList,compList+sizeof(compList)/sizeof(std::string)); 

	//const int nbins=135;
	const int nbins=135;
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
		wTruth::templateNdim2_unroll.setRange("sigTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
	//	RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		Double_t inttruthSig=fittruthShape.createIntegral(obsTruth,"sigTruth_region").getVal()  ;
		//load nominal pdf
		nompdffile->cd();
		w->loadSnapshot("MultiDimFit");
		w->exportToCint("wNom");
		RooArgSet & obsNom=RooArgSet(wNom::mgg,wNom::templateNdim2_unroll);
		wNom::mgg.setRange("sig_region",wNom::mgg.getMin(),wNom::mgg.getMax());
		wNom::templateNdim2_unroll.setRange("sig_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		RooPlot * framei = wNom::mgg.frame(Title("check"),Bins(nbins),Range("sigTruth_region"));
		RooProdPdf* fitnomShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomNorm=w->function(fitNormName.Data());
		fitnomShape->Print();
		fitnomNorm->Print();	
	//	RooExtendPdf* fitnomPdf=new RooExtendPdf("fitnomPdf","fitnomPdf",*fitnomShape,*fitnomNorm);
		Double_t intnomSig=0. ;
		intnomSig=fitnomShape.createIntegral(obsNom,"sig_region").getVal()  ;
		cout << " inttruthSig " << inttruthSig <<" intnomSig " << intnomSig << endl;
		fitnomShape->plotOn(framei,LineColor(kBlue));
		fittruthShape->plotOn(framei,LineColor(kRed));
		w->loadSnapshot("MultiDimFit");
		RooProdPdf* randShape=w->pdf(fitShapeName.Data());
		RooProduct* randNorm=w->function(fitNormName.Data());
	//	RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",*randShape,*randNorm);
		//RooArgSet* pdfParams = randPdf->getParameters(obsNom) ;
		RooArgSet* pdfParams = randShape->getParameters(obsNom) ;
		RooArgSet* NormParams = randNorm->getParameters(obsNom) ;
//		pdfParams.Print("v");	
//		NormParams.Print("v");	
		//get fitresult and randomize parameters in covariance matrix
		nomfitresfile->cd();
		//const TMatrixDSym & cov=fit->covarianceMatrix();
		Double_t intPdfs[nsampling][nbins];
		
		Double_t inttruthBin[nbins];
		Double_t intnomBin[nbins];
		Double_t massbins[nbins];
		Double_t min[nbins];
		Double_t max[nbins];
		double binning =50.;
		for(int bin=0; bin <nbins;++bin){
				Double_t intBin=0.;
				max[bin]= wNom::mgg.getMin() + binning*bin +binning;
				min[bin]= wNom::mgg.getMin() + binning*bin;
				massbins[bin]=(max[bin]+min[bin])/2.;
				
				wNom::mgg.setRange("bin_region",min[bin],max[bin]);
				Double_t intnomShape=((fitnomShape.createIntegral(obsNom,"bin_region").getVal())/intnomSig)  ;
				intnomBin[bin]=fitnomNorm*intnomShape ;
				wTruth::mgg.setRange("binTruth_region",min[bin],max[bin]);
				Double_t inttruthShape=((fittruthShape.createIntegral(obsTruth,"binTruth_region").getVal())/inttruthSig) ;
				inttruthBin[bin]=fittruthNorm*inttruthShape ;
			//	if( inttruthShape[bin] < intnomShape[bin]){
			//		cout << "intnomShape " << intnomShape << " intnomBin "<<intnomBin[bin] << " inttruthShape " << inttruthShape << " inttruthBin "<<inttruthBin[bin] << endl; 
			//	}
		}
		for(int r=0;r< nsampling;++r){	
			if(r==10 || r==40 ||r==100 || r==300 || r==450){
				cout << "---------------------------------  sampling" << r << "----------" << endl;
//				pdfParams.Print("v");
//				NormParams.Print("v");
			}
		//square root method for decomposition automatically applied
			RooArgList & randParams=fit.randomizePars();
			*pdfParams = randParams ;
			*NormParams = randParams ;
			Double_t intSig=0.;
			Double_t intSig=randShape.createIntegral(obsNom,"sig_region").getVal()  ;
			
			for(int bin=0; bin <nbins;++bin){
				wNom::mgg.setRange("binRand_region",min[bin],max[bin]);
				intBin=fitnomNorm*(randShape.createIntegral(obsNom,"binRand_region").getVal())  ;
				intPdfs[r][bin]=intBin/intSig;
			//	if(check && r==0){cout << intPdfs[r][bin] << " "<< intSig << " truth "<<inttruthBin[bin] <<" " << inttruthSig <<"  nom "<< intnomBin[bin] << " "<< intnomSig << endl;}
				//if( r==4 && (inttruthBin[bin] > intnomBin[bin])){
				if( r==4 ){
					cout << "WOW "<<massbins[bin] << " : " <<  intPdfs[r][bin]  << " truth "<< inttruthBin[bin] <<"  nom "<< intnomBin[bin]<< endl;
				}
			}
		}
		cout << "finished randomizing + integration " << endl;
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
//			cout << "---------- plot result "<< bin << " ----------" << endl;
			double xmin=0.;
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
			if(check || bin==20|| bin==120)
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
			//	if(check)
				if(bin==0 && (samp==3 ||samp==50))
				{
					TCanvas * canvi = new TCanvas("check","check");
					canvi->SetLogy();
				//	canvi->SetLogx();
					randShape->plotOn(framei,LineColor(kBlack));
	    			framei->GetYaxis()->SetRangeUser(1e-10,2);
					framei->Draw();
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_%s__samp_%i.png",comp.Data(),samp));
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
			if(check || bin==20|| bin==120)
			{
				c1->cd(2);
				cum->Draw();
				c1->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_%s_bin%i.png",comp.Data(),bin));
			}
			//compute 68 and 95 percent
			const int qn=5;
			Double_t quant[qn] ;	
			Double_t prob[qn]={0.025,0.16,0.5,0.84,0.975};
			cum->GetQuantiles(qn,quant,prob);
			mean[bin]= intnomBin[bin]-inttruthBin[bin];	
			quant68[bin]= intnomBin[bin]+quant[3];	
			quant95[bin]= intnomBin[bin]+quant[4];	
			quant68m[bin]=intnomBin[bin]-quant[1];	
			quant95m[bin]=intnomBin[bin]-quant[0];	
		/*
			mean[bin]= inttruthBin[bin]-quant[2];	
			quant68[bin]= quant[2]+quant[3];	
			quant95[bin]= quant[2]+quant[4];	
			quant68m[bin]=quant[2]-quant[1];	
			quant95m[bin]=quant[2]-quant[0];	
		*/	
			//pull function if diff positiv, take positv value
			if (intnomBin[bin]>= inttruthBin[bin]){
				pull68[bin]=mean[bin]/quant68[bin];
				pull95[bin]=mean[bin]/quant95[bin];
			cout << " mean " << mean[bin] << " quant68[bin] "<< quant68[bin]<< " quant95[bin] "<< quant95[bin] <<"  pull68[bin] "<< pull68[bin]<< "  pull95[bin] "<< pull95[bin] << endl;
			}
			else {
				pull68[bin]=mean[bin]/(quant68m[bin]);
				pull95[bin]=mean[bin]/(quant95m[bin]);
				
			cout << " mean " << mean[bin] << " quantm68[bin] "<< quant68m[bin]<< " quantm95[bin] "<< quant95m[bin] <<"  pull68[bin] "<< pull68[bin]<< "  pull95[bin] "<< pull95[bin] << endl;
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
		grmean->SetMarkerStyle(21);
		grmean->SetMarkerColor(kRed+1);
		gr68->SetMarkerColor(kYellow+1);
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
		
		grmean->Draw("a pC"); 
		gr95->Draw("  pC SAME"); 
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
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_%s.png",comp.Data()));
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_%s.root",comp.Data()));
		//pull distribution
		TCanvas *cpull = new TCanvas("cpull","bias on model",10,10,700,900);
		cpull.cd();
		TGraph *grpull68 = new TGraph(nbins,massbins,pull68);
		TGraph *grpull95 = new TGraph(nbins,massbins,pull95);
		grpull68->SetMarkerStyle(21);
		grpull95->SetMarkerStyle(21);
		grpull68->SetMarkerColor(kYellow+1);
		grpull95->SetMarkerColor(kGreen+1);
		grpull95->Draw("p a"); 
		
		grpull68->Draw("p SAME"); 
		grpull95->GetXaxis()->SetTitle("mass (GeV)");
		grpull95->GetYaxis()->SetTitle("pull");
		TLegend* leg2 = new TLegend(0.55, 0.8, .9, .9);
		leg2->SetFillColor(0);
		leg2->SetHeader("uncertainty");
		leg2->AddEntry(grpull68,"68%" ,"p");
		leg2->AddEntry(grpull95,"95%" ,"p");
		leg2->Draw();
		cpull->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cpull_%s.png",comp.Data()),"png");

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
