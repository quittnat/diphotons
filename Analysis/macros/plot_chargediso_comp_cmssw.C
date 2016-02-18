{
//if necessary also normal projections and looip over massbins
	using namespace RooFit;
	TFile *_file0 = TFile::Open("compared_templates_7415v2_v5_data_ecorr_pas_fullmass.root");
 TFile *_file1 = TFile::Open("compared_moriond16v1_sync_v2_data_fullmass.root");
 	_file0->cd();	
//	wtemplates->exportToCint("ws");
	RooDataHist* ppEBEB_old= (RooDataHist*)(wtemplates->data("unrolled_template_pp_2D_EBEB_mb_230_12999"));
	RooDataHist* ppEBEE_old= (RooDataHist*)(wtemplates->data("unrolled_template_pp_2D_EBEE_mb_320_12999"));
 	_file1->cd();	
//	wtemplates->exportToCint("ws_new");
	RooDataHist* ppEBEB_new= (RooDataHist*)(wtemplates->data("unrolled_template_pp_2D_EBEB_mb_230_12999"));
	RooDataHist* ppEBEE_new= (RooDataHist*)(wtemplates->data("unrolled_template_pp_2D_EBEE_mb_320_12999"));
 	_file0->cd();	
		    
	RooPlot * frameEBEB = wtemplates->var("templateNdim2d_unroll")->frame();
	TLegend* leg= new TLegend(0.5,0.8,0.9,0.9);
	ppEBEB_new->plotOn(frameEBEB,LineColor(kBlack));
	ppEBEB_old->plotOn(frameEBEB,DrawOption("E2"),FillColor(kRed),FillStyle(3002));	
	
	TCanvas * canvEBEB = new TCanvas("ppEBEB","ppEBEB");
	canvEBEB->SetLogy();
	frameEBEB->GetYaxis()->SetRangeUser(0.5,1e4);
    leg->AddEntry(ppEBEB_new,"#gamma #gamma CMSSW 7_6 rereco (black)","lp")  ;
    leg->AddEntry(ppEBEB_old,"#gamma #gamma CMSSW 7_4 prompt (red)","f") ;
	frameEBEB->Draw(); 
	leg->Draw();
	canvEBEB->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%s.png", canvEBEB->GetName()));
	RooPlot * frameEBEE = wtemplates->var("templateNdim2d_unroll")->frame();
	ppEBEE_new->plotOn(frameEBEE,LineColor(kBlack));
	ppEBEE_old->plotOn(frameEBEE,DrawOption("E2"),FillColor(kRed),FillStyle(3002));	
	TCanvas * canvEBEE = new TCanvas("ppEBEE","ppEBEE");
	canvEBEE->SetLogy();
	frameEBEE->GetYaxis()->SetRangeUser(0.5,1e4);
	frameEBEE->Draw(); 
	leg->Draw();
	canvEBEE->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%s.png", canvEBEE->GetName()));
}

	    
