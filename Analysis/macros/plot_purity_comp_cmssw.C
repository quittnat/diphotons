{
//if necessary also normal projections and looip over massbins
	using namespace RooFit;
	TFile *_file0 = TFile::Open("purity_7415v2_v5_data_ecorr_pas.root");
 TFile *_file1 = TFile::Open("purity_moriond16v1_sync_v2_data.root");
 	_file0->cd();	
//	wtemplates->exportToCint("ws");
	TGraphErrors* ppEBEB_old= (TGraphErrors*)(wtemplates->genobj("g_ppEBEB"));
	TGraphErrors* ppEBEE_old= (TGraphErrors*)(wtemplates->genobj("g_ppEBEE"));
 	_file1->cd();	
//	wtemplates->exportToCint("ws_new");
	TGraphErrors* ppEBEB_new= (TGraphErrors*)(wtemplates->genobj("g_ppEBEB"));
	TGraphErrors* ppEBEE_new= (TGraphErrors*)(wtemplates->genobj("g_ppEBEE"));
		    
	TCanvas * canvEBEB = new TCanvas("purity_ppEBEB","purity_ppEBEB");
	TLegend* leg= new TLegend(0.5,0.8,0.9,0.9);
	ppEBEB_new->SetLineColor(kBlack);
	ppEBEB_new->SetMarkerColor(kBlack);
	ppEBEB_new->Draw("ap");
	ppEBEB_old->SetFillColor(kRed);
	ppEBEB_old->SetFillStyle(3002);
	ppEBEB_old->Draw("E2 same");
    leg->AddEntry(ppEBEB_new,"#gamma #gamma CMSSW 7_6 rereco (black)","lp")  ;
    leg->AddEntry(ppEBEB_old,"#gamma #gamma CMSSW 7_4 prompt (red)","f") ;
	leg->Draw();
	canvEBEB->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%s.png", canvEBEB->GetName()));
	
	TCanvas * canvEBEE = new TCanvas("purity_ppEBEE","purity_ppEBEE");
	ppEBEE_new->SetLineColor(kBlack);
	ppEBEE_new->SetMarkerColor(kBlack);
	ppEBEE_new->Draw("ap");
	ppEBEE_old->SetFillColor(kRed);
	ppEBEE_old->SetFillStyle(3002);
	ppEBEE_old->Draw("E2 same");
	leg->Draw();
	canvEBEE->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%s.png", canvEBEE->GetName()));
	}

	    
