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

	const int nsampling=300;
	int nbins=0;
	double binning =50.;
	
	for(std::list<std::string>::iterator it = components.begin(); it != components.end(); ++it) {
		TString comp=*it;
		cout << "----------- component " << comp.Data() << "----------------------" << endl;
		TString fitShapeName=Form("shapeBkg_%s", comp.Data());
		TString fitNormName=Form("shapeBkg_%s__norm", comp.Data());
		
		//load truth pdf

		truthpdffile->cd();
		w->exportToCint("wTruth");
		RooArgSet  obsTruth=RooArgSet(wTruth::mgg, wTruth::templateNdim2_unroll);
		wTruth::templateNdim2_unroll.setRange("sigTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		wTruth::templateNdim2_unroll.setRange("binTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		RooProdPdf* fittruthShape=w->pdf(fitShapeName.Data());
		RooProduct* fittruthNorm=w->function(fitNormName.Data());
		wTruth::mgg.setRange("sigTruth_region",wTruth::mgg.getMin(),wTruth::mgg.getMax());
		
		
		RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		fittruthPdf.Print();
		Double_t inttruthSig=fittruthPdf.createIntegral(obsTruth,"sigTruth_region").getVal()  ;
		
		//load nominal pdf
		nompdffile->cd();
		w->loadSnapshot("MultiDimFit");
		w->exportToCint("wNom");
		RooArgSet obsNom=RooArgSet(wNom::mgg, wNom::templateNdim2_unroll);
		wNom::mgg.setRange("sig_region",wNom::mgg.getMin(),wNom::mgg.getMax());
		wNom::templateNdim2_unroll.setRange("sig_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		wNom::templateNdim2_unroll.setRange("bin_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		nbins=(wNom::mgg.getMax()-wNom::mgg.getMin())/binning;
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
//		cout << "truth expEvent " << fittruthPdf->expectedEvents(obsTruth) << " inttruthSig " << inttruthSig << "nom expEvent " << fitnomPdf->expectedEvents(obsNom) <<" intnomSig " << intnomSig << endl;
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
		Double_t masserrl[nbins];
		Double_t masserrh[nbins];
		Double_t min[nbins];
		Double_t max[nbins];
		for(int bin=0; bin <nbins;++bin){
				Double_t intBin=0.;
				max[bin]= wNom::mgg.getMin() + binning*bin +binning;
				min[bin]= wNom::mgg.getMin() + binning*bin;
				massbins[bin]=(max[bin]+min[bin])/2.;
				masserrl[bin]=binning/2.;
				masserrh[bin]=binning/2.;
				
				wNom::mgg.setRange("bin_region",min[bin],max[bin]);
				Double_t intnomPdf=((fitnomPdf.createIntegral(obsNom,"bin_region").getVal())/intnomSig)  ;
				intnomBin[bin]=expnomEvents*intnomPdf ;
				wTruth::mgg.setRange("binTruth_region",min[bin],max[bin]);
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
			wNom::mgg.setRange("sigRand_region",wNom::mgg.getMin(),wNom::mgg.getMax());
			wNom::templateNdim2_unroll.setRange("sigRand_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
			Double_t intSig=randPdf.createIntegral(obsNom,"sigRand_region").getVal()  ;
			Double_t exprandEvents= randPdf->expectedEvents(obsNom);
			wNom::templateNdim2_unroll.setRange("binRand_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
			
			for(int bin=0; bin <nbins;++bin){
				wNom::mgg.setRange("binRand_region",min[bin],max[bin]);
				//intBin=fitnomNorm*(randShape.createIntegral(obsNom,"binRand_region").getVal())  ;
				intBin=randShape.createIntegral(obsNom,"binRand_region").getVal()  ;
				intPdfs[r][bin]=exprandEvents*(intBin/intSig);
				if(check && r==4 ){
					cout <<bin << " : " <<  intPdfs[r][bin]  << " truth "<< inttruthBin[bin] <<"  nom "<< intnomBin[bin]<< endl;
				}
			}
			if( r==4 ){
					TCanvas * canvi = new TCanvas("ccheck","ccheck");
					canvi->SetLogy();
					canvi->SetGridy();
					canvi->SetGridx();
				//	canvi->SetLogx();
					randPdf->plotOn(framei,LineColor(kBlack));
	    			framei->GetYaxis()->SetRangeUser(1e-7,1000);
					framei->Draw();
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_%s__samp_4.png",comp.Data()));
					delete canvi;
			}
		}
		cout << "finished randomizing + integration " << endl;
		//plot result histo per bin for integral values from randomized pdfs
		gStyle->SetOptStat(111111);
		Double_t diff[nbins] ;	
		Double_t quant68[nbins] ;	
		Double_t quant50[nbins] ;	
		Double_t quant95[nbins] ;	
		Double_t quant68m[nbins] ;	
		Double_t quant95m[nbins] ;	
		
		Double_t pull[nbins] ;	
		Double_t errPlus[nbins] ;	
		Double_t errMin[nbins] ;	
		Double_t difffrac[nbins] ;	
		Double_t quant68n[nbins] ;	
		
		for(int bin=0;bin< nbins;bin++)
		{
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
			
			//compute 68 and 95 percent 
			const int qn=5;
			Double_t quant[qn] ;	
			Double_t prob[qn]={0.025,0.16,0.5,0.84,0.975};
			TH1D* hist=new TH1D("hist","hist",100,xmin, xmax);
			for(int samp=0; samp< nsampling; samp++){hist->Fill(intPdfs[samp][bin]);}
			hist->GetQuantiles(qn,quant,prob);
			diff[bin]= intnomBin[bin]-inttruthBin[bin];	
			difffrac[bin]= diff[bin]/intnomBin[bin];	
			quant68[bin]= quant[3]+intnomBin[bin];	
			quant95[bin]= quant[4]+intnomBin[bin];	
			quant68n[bin]= 0.;	
			quant68m[bin]=intnomBin[bin]-quant[1];	
			quant95m[bin]=intnomBin[bin]-quant[0];	
			quant50[bin]=quant[2];
			errPlus[bin]= quant[3]-intnomBin[bin];	
			errMin[bin]= intnomBin[bin]-quant[1];	
			
			//pull function if diff positiv, take positv value
				cout << bin << " : diff " << diff[bin] << " quantm68 "<< quant68m[bin]<< "       quantm95  "<< quant95m[bin] << endl;
				cout << bin << " : diff " << diff[bin] << " quant68  "<< quant68[bin] << "       quant95   "<< quant95[bin] << endl;
			if (intnomBin[bin]>= inttruthBin[bin]){
				pull[bin]=diff[bin]/errPlus[bin];
				cout << bin << " : diff " << diff[bin] << " errPlus "<< errPlus[bin] <<  "       pull "<< pull[bin] << endl;
			}
			else {
				pull[bin]=diff[bin]/(errMin[bin]);
				cout << bin << " : diff " << diff[bin] << " errMin   "<< errMin[bin]  << "       pull "<< pull[bin] << endl;
			}
			cout << " "  << endl;
			
			if(check || bin>100)
			{
				TCanvas* chisto= new TCanvas("chisto","chisto");
				chisto->cd(1);
				hist->Draw();
				TLine *lmean = new TLine(intnomBin[bin],0.,intnomBin[bin],nsampling/10.);
				lmean->SetLineColor(kGreen+1);
				lmean->SetLineWidth(3);
			n->SetLineStyle(4);
				TLine *lmeanTruth = new TLine(inttruthBin[bin],0.,inttruthBin[bin],nsampling/10.);
				lmeanTruth->SetLineColor(kYellow+1);
				lmeanTruth->SetLineWidth(3);
				lmeanTruth->SetLineStyle(4);
				TLine *lm2s = new TLine(quant[0],0.,quant[0],nsampling/10.);
				lm2s->SetLineColor(kMagenta);
				lm2s->SetLineWidth(3);
				TLine *lm1s = new TLine(quant[1],0.,quant[1],nsampling/10.);
				lm1s->SetLineColor(kMagenta+1);
				lm1s->SetLineWidth(3);
				TLine *lm = new TLine(quant[2],0.,quant[2],nsampling/10.);
				lm->SetLineColor(kMagenta+2);
				lm->SetLineWidth(3);
				TLine *l1s = new TLine(quant[3],0.,quant[3],nsampling/10.);
				l1s->SetLineColor(kMagenta+3);
				l1s->SetLineWidth(3);
				TLine *l2s = new TLine(quant[4],0.,quant[4],nsampling/10.);
				l2s->SetLineColor(kMagenta+4);
				l2s->SetLineWidth(3);
				lm2s->Draw("SAME");
				lm1s->Draw("SAME");
				lm->Draw("SAME");
				l1s->Draw("SAME");
				l2s->Draw("SAME");
				lmean->Draw("SAME");
				lmeanTruth->Draw("SAME");
				TLegend* leg3 = new TLegend(0.45, 0.6, .9, .9);
				leg3->SetFillColor(0);
				leg3->AddEntry(lmeanTruth,"mean truth" ,"l");
				leg3->AddEntry(lmean,"mean nominal start fit" ,"l");
				leg3->AddEntry(lm2s,"2.5 %" ,"l");
				leg3->AddEntry(lm1s,"16 %" ,"l");
				leg3->AddEntry(lm,"50 %" ,"l");
				leg3->AddEntry(l1s,"84 %" ,"l");
				leg3->AddEntry(l2s,"97.5 %" ,"l");
				leg3->Draw();
				chisto->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/Histo_%s_bin%i.png",comp.Data(),bin));
				delete chisto;
				delete lm2s;
				delete lm1s;
				delete lm;
				delete l1s;
				delete l2s;
			
			}
			//delete [] quant;
			//delete [] prob;
			delete hist;
			randPdf=NULL;
			randShape=NULL;
			randNorm=NULL;
			
			delete randPdf;
			delete randShape;
			delete randNorm;
		}
		//plot 68 and 95 percent 	
		TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
		//get mass bins, set legend
		cbias->cd();
		cbias->SetLogy();
		cbias->SetGridy();
		cbias->SetGridx();
		//TGraphAsymmErrors *gr68 = new TGraphAsymmErrors(nbins,massbins,intnomBin,masserrl,masserrh,quant68m,quant68);
		//TGraphAsymmErrors *gr95 = new TGraphAsymmErrors(nbins,massbins,intnomBin,masserrl,masserrh,quant95m,quant95);
		TGraphAsymmErrors *gr68 = new TGraphAsymmErrors(nbins,massbins,intnomBin,masserrl,masserrh,quant68m,quant68m);
		TGraphAsymmErrors *gr95 = new TGraphAsymmErrors(nbins,massbins,intnomBin,masserrl,masserrh,quant95m,quant68n);
		TGraph *grmean = new TGraph(nbins,massbins,quant50);
		TGraph *grmeanTruth = new TGraph(nbins,massbins,inttruthBin);
		gr68->SetMarkerStyle(21);
		gr68->SetTitle("uncertainty of model");
		gr95->SetMarkerStyle(21);
		grmean->SetMarkerStyle(21);
		grmean->SetMarkerColor(kCyan+1);
	
		grmeanTruth->SetMarkerStyle(21);
		grmeanTruth->SetMarkerColor(kRed+1);
		grmeanTruth->SetLineColor(grmeanTruth->GetMarkerColor());
	
		gr68->SetMarkerColor(kBlack);
		gr68->SetFillColor(kYellow+1);
		gr68->SetLineColor(gr68->GetFillColor());
		gr68->SetFillStyle(3001);
		gr95->SetMarkerColor(kBlack);
		gr95->SetFillColor(kGreen+1);
		gr95->SetLineColor(gr95->GetFillColor());
		gr95->SetFillStyle(3001);
		
		gr95->Draw("a pC "); 
		grmeanTruth->Draw("pC SAME"); 
		grmean->Draw("pC SAME"); 
		gr68->Draw("pC  SAME"); 
		gr95->GetXaxis()->SetTitle("mass [GeV]");
		TLegend* leg = new TLegend(0.45, 0.6, .9, .9);
		leg->SetFillColor(0);
		leg->AddEntry(grmeanTruth,"# exp Events truth fit" ,"p");
		leg->AddEntry(grmean,"# median from randomized events" ,"p");
		leg->AddEntry(gr68,"# exp Events nominal fit" ,"p");
		leg->AddEntry(gr68,"68%" ,"l");
		leg->AddEntry(gr95,"95%" ,"l");
		leg->Draw();
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/testcbias_%s.png",comp.Data()));
		cbias->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/testcbias_%s.root",comp.Data()));
		
		//pull distribution
		TCanvas *cpull = new TCanvas("cpull","pull distribution",10,10,700,900);
		cpull->cd();
		cpull->SetGridx();
		cpull->SetGridy();
		TGraph *grpull = new TGraph(nbins,massbins,pull);
		grpull->SetMarkerStyle(21);
		grpull->SetTitle("pull function");
		grpull->SetMarkerColor(kBlue+1);
		grpull->Draw("p a "); 
		grpull->GetXaxis()->SetTitle("mass [GeV]");
		grpull->GetYaxis()->SetTitle("pull");
		cpull->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cpull_%s.png",comp.Data()),"png");
		
		
		TCanvas *cfrac = new TCanvas("cfrac","bias on model",10,10,700,900);
		cfrac->cd();
		
		cfrac->SetGridx();
		cfrac->SetGridy();
		TGraph *grfrac = new TGraph(nbins,massbins,difffrac);
		grfrac->SetMarkerStyle(21);
		grfrac->SetTitle("fraction");
		grfrac->SetMarkerColor(kCyan+1);
		grfrac->Draw("p a"); 
		grfrac->GetXaxis()->SetTitle("mass [GeV]");
		grfrac->GetYaxis()->SetTitle("(Nnom-Ntruth)/Nnom");
		cfrac->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/cfrac_%s.png",comp.Data()),"png");
		
		fittruthPdf=NULL;
		fittruthShape=NULL;
		fittruthNorm=NULL;
		fitnomPdf=NULL;
		fitnomShape=NULL;
		fitnomNorm=NULL;

		delete fittruthPdf;
		delete fittruthShape;
		delete fittruthNorm;
		delete fitnomPdf;
		delete fitnomShape;
		delete fitnomNorm;
		delete cfrac;
		delete cbias;
		delete cpull;
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
