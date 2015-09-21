{
	#include <vector>
	#include "TH1.h"
	#include <algorithm>
	#include <list>
	
	using namespace RooFit;
	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	//TODO includes etc
// 	TFile* nompdffile = new TFile("PasqualeFit/full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.root");
	TFile* truthpdffile = new TFile("PasqualeFit/full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.root");
 	//TFile* nomasfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_self.GenerateOnly.mH0.123456.root");
//	nomasfile->cd();
	//RooAbsData * dataTruth = toys->Get("toy_asimov");
 	TFile* truthasfile = new TFile("PasqualeFit/full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/higgsCombine_truth.GenerateOnly.mH0.123456.root");
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
		w->loadSnapshot("clean");
		RooArgSet  obsTruth=RooArgSet(wTruth::templateNdim2_unroll,wTruth::templateNdim2_unroll);
		RooProdPdf* fittruthShape=w->pdf(fitShapeName.Data());
		RooProduct* fittruthNorm=w->function(fitNormName.Data());
		wTruth::mgg.setRange("sigTruth_region",wTruth::mgg.getMin(),wTruth::mgg.getMax());
		wTruth::templateNdim2_unroll.setRange(wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		RooArgSet* truthParams = fittruthPdf->getParameters(obsTruth) ;
		truthParams->Print("v");
		RooPlot * framei = wTruth::mgg.frame(Title("check"),Bins(134),Range("sigTruth_region"));
//	   	dataTruth->plotOn(framei,MarkerColor(kRed+1));
		fittruthShape->plotOn(framei,LineColor(kRed),LineStyle(1),LineWidth(3),Project(obsTruth));
		RooPlot * framePdf = wTruth::mgg.frame(Title("check pdf"),Bins(134),Range("sigTruth_region"));
		fittruthPdf->plotOn(framePdf,LineColor(kRed),LineStyle(1),LineWidth(3),Project(obsTruth));

		RooProdPdf* fittruthSShape=w->pdf(fitShapeName.Data());
		RooProduct* fittruthSNorm=w->function(fitNormName.Data());
		wTruth::mgg.setRange("sig_region",wTruth::mgg.getMin(),wTruth::mgg.getMax());
		RooExtendPdf* fittruthSPdf=new RooExtendPdf("fittruthSPdf","fittruthSPdf",*fittruthSShape,*fittruthSNorm);
		fittruthSShape->plotOn(framei,LineColor(kYellow+1),LineStyle(4),LineWidth(2),Project(wTruth::templateNdim2_unroll));
		fittruthSShape->plotOn(framei,LineColor(kYellow+4),LineStyle(4),LineWidth(5),Project(wTruth::mgg));
		fittruthSPdf->plotOn(framePdf,LineColor(kYellow+1),LineStyle(4),LineWidth(1),Project(wTruth::templateNdim2_unroll));

		//load nominal pdf
		w->loadSnapshot("MultiDimFit");
		RooProdPdf* fitnomShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomNorm=w->function(fitNormName.Data());
		RooExtendPdf* fitnomPdf=new RooExtendPdf("fitnomPdf","fitnomPdf",*fitnomShape,*fitnomNorm);
		RooArgSet* nomParams = fitnomPdf->getParameters(obsTruth) ;
		nomParams->Print("v");
		fitnomShape->plotOn(framei,LineColor(kBlue),LineStyle(3),LineWidth(3),Project(obsTruth));
		fitnomPdf->plotOn(framePdf,LineColor(kBlue),LineStyle(3),LineWidth(3), Project(obsTruth));
	//	fitnomShape->plotOn(framei,LineColor(kBlue),LineStyle(3),LineWidth(3));
	//	fitnomPdf->plotOn(framePdf,LineColor(kBlue),LineStyle(3),LineWidth(3));
		RooProdPdf* fitnomSShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomSNorm=w->function(fitNormName.Data());
		RooExtendPdf* fitnomSPdf=new RooExtendPdf("fitnomSPdf","fitnomSPdf",*fitnomSShape,*fitnomSNorm);
		fitnomSShape->plotOn(framei,LineColor(kGreen+1),LineStyle(10),LineWidth(2),Project(wTruth::templateNdim2_unroll));
		fitnomSShape->plotOn(framei,LineColor(kGreen+4),LineStyle(5),LineWidth(1),Project(wTruth::mgg));
		fitnomSPdf->plotOn(framePdf,LineColor(kGreen+1),LineStyle(10),LineWidth(5),Project(wTruth::templateNdim2_unroll));
		//intnomSig=fitnomPdf.createIntegral(obsTruth,"sig_region").getVal()  ;
		//fitnomPdf->Print();
					TCanvas * canvi = new TCanvas("check","check");
					canvi->SetLogy();
					canvi->SetLogx();
	   			//	dataNom->plotOn(framei,MarkerColor(kBlue-1));
	    			framei->GetYaxis()->SetRangeUser(1e-7,1000);
					TLegend* leg3 = new TLegend(0.45, 0.6, .9, .9);
					framei->Draw();
					leg3->SetFillColor(0);
					leg3->AddEntry(fittruthShape,"truth both variables" ,"lp");
					leg3->AddEntry(fittruthSShape,"truth one variable" ,"lp");
					leg3->AddEntry(fitnomShape,"nom both variables" ,"lp");
					leg3->AddEntry(fitnomSShape,"nom one variable" ,"lp");
					leg3.Draw();
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/plotDiffFit_%s.png",comp.Data()));
					canvi->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/plotDiffFit_%s.root",comp.Data()));
		
					TCanvas * canvPdf = new TCanvas("checkPdf","checkPdf");
					canvPdf->SetLogy();
					canvPdf->SetLogx();
					leg3.Draw();
					framePdf->Draw();
	    			framePdf->GetYaxis()->SetRangeUser(1e-7,1000);
					canvPdf->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/plotDiffFitExtPdf_%s.png",comp.Data()));
					canvPdf->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_fit_bias/plotDiffFitExtPdf_%s.root",comp.Data()));
			
					}
}	
