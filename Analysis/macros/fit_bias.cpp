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
	std::string compList[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE"}; 
//	std::string compList[]={"pp_EBEB"}; 
	std::list<std::string> components(compList,compList+sizeof(compList)/sizeof(std::string)); 

	//const int nbins=135;
	const int nbins=70;
	const int nsampling=100;
	
	for(std::list<std::string>::iterator it = components.begin(); it != components.end(); ++it) {
		TString comp=*it;
		TString fitShapeName=Form("shapeBkg_%s", comp.Data());
		TString fitNormName=Form("shapeBkg_%s__norm", comp.Data());
		
		//load truth pdf

		truthpdffile->cd();
		w->exportToCint("wTruth");
		//RooArgSet & obsTruth=RooArgSet(wTruth::mgg);
		RooArgSet  obsTruth=RooArgSet(wTruth::mgg, wTruth::templateNdim2_unroll);
		wTruth::templateNdim2_unroll.setRange("sigTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		wTruth::templateNdim2_unroll.setRange("binTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		RooProdPdf* fittruthShape=w->pdf(fitShapeName.Data());
		RooProduct* fittruthNorm=w->function(fitNormName.Data());
		cout << "----------- component " << comp.Data() << "----------------------" << endl;
	//	fittruthShape->Print();
	//	fittruthNorm->Print();
		wTruth::mgg.setRange("sigTruth_region",wTruth::mgg.getMin(),wTruth::mgg.getMax());
		RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		fittruthPdf.Print();
		Double_t inttruthSig=fittruthPdf.createIntegral(obsTruth,"sigTruth_region").getVal()  ;
		//load nominal pdf
		nompdffile->cd();
		w->loadSnapshot("MultiDimFit");
		w->exportToCint("wNom");
		//RooArgSet & obsNom=RooArgSet(wNom::mgg);
		RooArgSet obsNom=RooArgSet(wNom::mgg, wNom::templateNdim2_unroll);
		wNom::mgg.setRange("sig_region",wNom::mgg.getMin(),wNom::mgg.getMax());
		wNom::templateNdim2_unroll.setRange("sig_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		wNom::templateNdim2_unroll.setRange("bin_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		RooPlot * framei = wNom::mgg.frame(Title("check"),Bins(nbins),Range("sigTruth_region"));
		RooProdPdf* fitnomShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomNorm=w->function(fitNormName.Data());
		//fitnomShape->Print();
		//fitnomNorm->Print();	
		RooExtendPdf* fitnomPdf=new RooExtendPdf("fitnomPdf","fitnomPdf",*fitnomShape,*fitnomNorm);
		Double_t exptruthEvents= fittruthPdf->expectedEvents(obsTruth);
		fitnomPdf.Print();
		Double_t intnomSig=0. ;
		intnomSig=fitnomPdf.createIntegral(obsNom,"sig_region").getVal()  ;
		cout << "truth expEvent " << fittruthPdf->expectedEvents(obsTruth) << " inttruthSig " << inttruthSig << "nom expEvent " << fitnomPdf->expectedEvents(obsNom) <<" intnomSig " << intnomSig << endl;
		fitnomPdf->plotOn(framei,LineColor(kBlue));
		fittruthPdf->plotOn(framei,LineColor(kRed));
		w->loadSnapshot("MultiDimFit");
		RooProdPdf* randShape=w->pdf(fitShapeName.Data());
		RooProduct* randNorm=w->function(fitNormName.Data());
		RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",*randShape,*randNorm);
		Double_t expnomEvents= fitnomPdf->expectedEvents(obsNom);
		RooArgSet* pdfParams = randPdf->getParameters(obsNom) ;
		//pdfParams.Print("v");	
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
			//	Double_t intnomShape=((fitnomShape.createIntegral(obsNom,"bin_region").getVal())/intnomSig)  ;
			//	intnomBin[bin]=fitnomNorm*intnomShape ;
				Double_t intnomPdf=((fitnomPdf.createIntegral(obsNom,"bin_region").getVal())/intnomSig)  ;
				intnomBin[bin]=expnomEvents*intnomPdf ;
				wTruth::mgg.setRange("binTruth_region",min[bin],max[bin]);
			//	Double_t inttruthShape=((fittruthShape.createIntegral(obsTruth,"binTruth_region").getVal())/inttruthSig) ;
			//	inttruthBin[bin]=fittruthNorm*inttruthShape ;
				Double_t inttruthPdf=((fittruthPdf.createIntegral(obsTruth,"binTruth_region").getVal())/inttruthSig)  ;
				inttruthBin[bin]=exptruthEvents*inttruthPdf ;
		//			cout <<" intnomBin "<<intnomBin[bin] << " inttruthBin "<<inttruthBin[bin] << endl; 
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
		//	*NormParams = randParams ;
			Double_t intSig=0., exprandEvents=0.;
			//Double_t intSig=randShape.createIntegral(obsNom,"sig_region").getVal()  ;
			Double_t intSig=randPdf.createIntegral(obsNom,"sig_region").getVal()  ;
			Double_t exprandEvents= randPdf->expectedEvents(obsNom);
			wNom::templateNdim2_unroll.setRange("binRand_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
			
			for(int bin=0; bin <nbins;++bin){
				wNom::mgg.setRange("binRand_region",min[bin],max[bin]);
				//intBin=fitnomNorm*(randShape.createIntegral(obsNom,"binRand_region").getVal())  ;
				intBin=randShape.createIntegral(obsNom,"binRand_region").getVal()  ;
				intPdfs[r][bin]=exprandEvents*(intBin/intSig);
				//if( r==4 && (inttruthBin[bin] > intnomBin[bin])){
				if( r==4 ){
					cout <<bin << " : " <<  intPdfs[r][bin]  << " truth "<< inttruthBin[bin] <<"  nom "<< intnomBin[bin]<< endl;
				}
			}
			if( r==4 ){
					TCanvas * canvi = new TCanvas("check","check");
					canvi->SetLogy();
				//	canvi->SetLogx();
					randPdf->plotOn(framei,LineColor(kBlack));
	    			framei->GetYaxis()->SetRangeUser(1e-7,1000);
					framei->Draw();
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_%s__samp_4.png",comp.Data()));
			}
		}
		cout << "finished randomizing + integration " << endl;
		//plot result histo per bin for integral values from randomized pdfs
		gStyle->SetOptStat(111111);
		Double_t diff[nbins] ;	
		Double_t quant68[nbins] ;	
		Double_t quant95[nbins] ;	
		Double_t quant68m[nbins] ;	
		Double_t quant95m[nbins] ;	
		Double_t pull68[nbins] ;	
		Double_t errPlus[nbins] ;	
		Double_t errMin[nbins] ;	
		Double_t difffrac[nbins] ;	
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
			TH1D* hist=new TH1D("hist","hist",nbin,xmin, xmax);
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
				c1->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_%s_bin%i.png",comp.Data(),bin));
			}
			//compute 68 and 95 percent
			const int qn=5;
			Double_t quant[qn] ;	
			Double_t prob[qn]={0.025,0.16,0.5,0.84,0.975};
			hist->GetQuantiles(qn,quant,prob);
			diff[bin]= intnomBin[bin]-inttruthBin[bin];	
			difffrac[bin]= diff[bin]/intnomBin[bin];	
			quant68[bin]= quant[3]+intnomBin[bin];	
			quant95[bin]= quant[4]+intnomBin[bin];	
			quant68m[bin]=intnomBin[bin]-quant[1];	
			quant95m[bin]=intnomBin[bin]-quant[0];	

			errPlus[bin]= quant[3]-intnomBin[bin];	
			errMin[bin]= intnomBin[bin]-quant[1];	
			
			//pull function if diff positiv, take positv value
			if (intnomBin[bin]>= inttruthBin[bin]){
				pull68[bin]=diff[bin]/errPlus[bin];
			//cout << " diff " << diff[bin] << " quant68[bin] "<< quant68[bin]<< " quant95[bin] "<< quant95[bin] <<"  pull68[bin] "<< pull68[bin]<< "  pull95[bin] "<< pull95[bin] << endl;
			}
			else {
				pull68[bin]=diff[bin]/(errMin[bin]);
			//cout << " diff " << diff[bin] << " quantm68[bin] "<< quant68m[bin]<< " quantm95[bin] "<< quant95m[bin] <<"  pull68[bin] "<< pull68[bin]<< "  pull95[bin] "<< pull95[bin] << endl;
			}
			delete hist;
			
		}
		//plot 68 and 95 percent 	
		TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
		//get mass bins, set legend
		cbias->SetLogy();
		TGraph *gr68 = new TGraph(nbins,massbins,quant68);
		TGraph *gr95 = new TGraph(nbins,massbins,quant95);
		TGraph *grmean = new TGraph(nbins,massbins,intnomBin);
		TGraph *grmeanTruth = new TGraph(nbins,massbins,inttruthBin);
		gr68->SetMarkerStyle(21);
		gr95->SetMarkerStyle(21);
		grmean->SetMarkerStyle(21);
		grmean->SetMarkerColor(kRed+1);
		grmeanTruth->SetMarkerStyle(21);
		grmeanTruth->SetMarkerColor(kCyan+1);
		grmeanTruth->SetLineColor(grmeanTruth->GetMarkerColor());
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
		grmeanTruth->Draw("pC SAME"); 
		gr95->Draw("pC SAME"); 
		gr68->Draw("pC SAME"); 
		gr95m->Draw("pC SAME"); 
		gr68m->Draw("pC SAME"); 
		grmean->GetXaxis()->SetTitle("mass (GeV)");
		TLegend* leg = new TLegend(0.55, 0.8, .9, .9);
		leg->SetFillColor(0);
		leg->SetHeader("uncertainty");
		leg->AddEntry(grmean,"# exp Events nominal fit" ,"l");
		leg->AddEntry(grmeanTruth,"# exp Events truth fit" ,"l");
		leg->AddEntry(gr68,"68%" ,"l");
		leg->AddEntry(gr95,"95%" ,"l");
		leg->Draw();
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_%s.png",comp.Data()));
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cbias_%s.root",comp.Data()));
		//pull distribution
		TCanvas *cpull = new TCanvas("cpull","bias on model",10,10,700,900);
		cpull.cd();
		TGraph *grpull68 = new TGraph(nbins,massbins,pull68);
		grpull68->SetMarkerStyle(21);
		grpull68->SetMarkerColor(kYellow+1);
		grpull68->Draw("p a"); 
		grpull68->GetXaxis()->SetTitle("mass (GeV)");
		grpull68->GetYaxis()->SetTitle("pull");
		cpull->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cpull_%s.png",comp.Data()),"png");
		
		
		TCanvas *cfrac = new TCanvas("cfrac","bias on model",10,10,700,900);
		cfrac.cd();
		TGraph *grfrac = new TGraph(nbins,massbins,difffrac);
		grfrac->SetMarkerStyle(21);
		grfrac->SetMarkerColor(kYellow+1);
		grfrac->Draw("p a"); 
		grfrac->GetXaxis()->SetTitle("mass (GeV)");
		grfrac->GetYaxis()->SetTitle("pull");
		cfrac->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cfrac_%s.png",comp.Data()),"png");

		delete fittruthPdf;
		delete fittruthShape;
		delete fittruthNorm;
		delete randPdf;
		delete randShape;
		delete randNorm;
		delete fitnomPdf;
		delete fitnomShape;
		delete fitnomNorm;
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
