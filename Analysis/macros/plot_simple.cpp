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
	TFile* truthpdffile = new TFile("full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/datacard_truth.root");
 	TFile* nomasfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_self.GenerateOnly.mH0.123456.root");
	nomasfile->cd();
	RooAbsData * dataNom = toys->Get("toy_asimov");
 	TFile* truthasfile = new TFile("full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/higgsCombine_truth.GenerateOnly.mH0.123456.root");
	truthasfile->cd();
	RooAbsData * dataTruth = toys->Get("toy_asimov");
	TFile* nompdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.root");

	//bkg only
//	std::string compList[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE"}; 
	std::string compList[]={"pp_EBEB"}; 
	std::list<std::string> components(compList,compList+sizeof(compList)/sizeof(std::string)); 

	const int nsampling=1;
	
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
		//wTruth::templateNdim2_unroll.setRange(wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		wTruth::templateNdim2_unroll.setRange(0.,4.);
		RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		Double_t inttruthSig=fittruthPdf.createIntegral(obsTruth,"sigTruth_region").getVal()  ;
		fittruthPdf->Print();

		//load nominal pdf
		nompdffile->cd();
		w->loadSnapshot("MultiDimFit");
		w->exportToCint("wNom");
		RooArgSet & obsNom=RooArgSet(wNom::mgg,wNom::templateNdim2_unroll);
		wNom::mgg.setRange("sig_region",wNom::mgg.getMin(),wNom::mgg.getMax());
	//	wNom::templateNdim2_unroll.setRange(wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		wNom::templateNdim2_unroll.setRange(0.,4.);
		RooProdPdf* fitnomShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomNorm=w->function(fitNormName.Data());
		fitnomShape->Print();
		fitnomNorm->Print();	
		RooExtendPdf* fitnomPdf=new RooExtendPdf("fitnomPdf","fitnomPdf",*fitnomShape,*fitnomNorm);
		Double_t intnomSig=0. ;
		intnomSig=fitnomPdf.createIntegral(obsNom,"sig_region").getVal()  ;
		fitnomPdf->Print();
		w->loadSnapshot("MultiDimFit");
		RooProdPdf* randShape=w->pdf(fitShapeName.Data());
		RooProduct* randNorm=w->function(fitNormName.Data());
		RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",*randShape,*randNorm);
		RooArgSet* pdfParams = randPdf->getParameters(obsNom) ;
		pdfParams.Print();	
		//get fitresult and randomize parameters in covariance matrix
		nomfitresfile->cd();
		//const TMatrixDSym & cov=fit->covarianceMatrix();
			for(int samp=0; samp< nsampling; samp++)
			{
					RooArgList & randParams=fit.randomizePars();
					*pdfParams = randParams ;
					TCanvas * canvi = new TCanvas("check","check");
					canvi->SetLogy();
					canvi->SetLogx();
					RooPlot * framei = wTruth::mgg.frame(Title("check"),Bins(140),Range("sigTruth_region"));
					fitnomPdf->plotOn(framei,LineColor(kBlue));
					fittruthPdf->plotOn(framei,LineColor(kRed));
	   				dataNom->plotOn(framei,MarkerColor(kBlue-1));
	    			dataTruth->plotOn(framei,MarkerColor(kRed+1));
					framei->Draw();
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiff_%s__samp_%i.png",comp.Data(),samp));
					TCanvas * canvPdf = new TCanvas("checkPdf","checkPdf");
					canvPdf->SetLogy();
					canvPdf->SetLogx();
					RooPlot * framePdf = wTruth::mgg.frame(Title("check pdf"),Bins(140),Range("sigTruth_region"));
					randPdf->plotOn(framePdf,LineColor(kGreen));
					fitnomPdf->plotOn(framePdf,LineColor(kBlue));
					fittruthPdf->plotOn(framePdf,LineColor(kRed));
					framePdf->Draw();
					canvPdf->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/checkDiffPdf_%s__samp_%i.png",comp.Data(),samp));
			}
			}
	}
}	
