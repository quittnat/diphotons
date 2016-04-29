{
//if necessary also normal projections and looip over massbins
	using namespace RooFit;
//	TFile *_file0 = TFile::Open("purity_sigregion_7415v2_v5_data_ecorr_pas.root");
//	TFile *_file1 = TFile::Open("purity_sigregion_moriond16v1_sync_v5.root");
	TFile *_file0 = TFile::Open("purity_fullregion_7415v2_v5_data_ecorr_pas.root");
	TFile *_file1 = TFile::Open("moriondv5/purity_moriond16v1_sync_v5.root");

cout << __LINE__<< endl;
 _file0->cd();	
//	wtemplates->exportToCint("ws");
	TGraphAsymmErrors* ppEBEB_old= (TGraphAsymmErrors*)(wtemplates->genobj("g_ppEBEB"));
	TGraphAsymmErrors* ppEBEE_old= (TGraphAsymmErrors*)(wtemplates->genobj("g_ppEBEE"));
 	_file1->cd();	
cout << __LINE__<< endl;
//	wtemplates->exportToCint("ws_new");
	TGraphAsymmErrors* ppEBEB_new= (TGraphAsymmErrors*)(wtemplates->genobj("g_ppEBEB"));
cout << __LINE__<< endl;
	TGraphAsymmErrors* ppEBEE_new= (TGraphAsymmErrors*)(wtemplates->genobj("g_ppEBEE"));
cout << __LINE__<< endl;
	TCanvas* canvEBEB = new TCanvas("purity_ppEBEB","purity_ppEBEB");
cout << __LINE__<< endl;
	TLegend* leg= new TLegend(0.5,0.8,0.9,0.9);
cout << __LINE__<< endl;
	ppEBEB_new->SetLineColor(kBlack);
	ppEBEB_new->SetMarkerColor(kBlack);
    ppEBEB_new->GetXaxis()->SetTitle("m_{#gamma #gamma} (GeV)");
    ppEBEB_new->GetYaxis()->SetTitle("Fraction");
    ppEBEB_new->GetXaxis()->SetTitleSize( 0.8 *ppEBEB_new->GetXaxis()->GetTitleSize() );
    ppEBEB_new->GetYaxis()->SetTitleSize( 0.8 *ppEBEB_new->GetYaxis()->GetTitleSize() );
	ppEBEB_new->Draw("ap");
cout << __LINE__<< endl;
	ppEBEB_old->SetFillColor(kRed);
	ppEBEB_old->SetFillStyle(3002);
	ppEBEB_old->Draw("E2 same");
cout << __LINE__<< endl;
    leg->AddEntry(ppEBEB_new,"#gamma #gamma CMSSW 7_6 rereco ","lp")  ;
    leg->AddEntry(ppEBEB_old,"#gamma #gamma CMSSW 7_4 prompt ","f") ;
	leg->Draw();
	canvEBEB->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v5/%s.png", canvEBEB->GetName()));
//	canvEBEB->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v5/%ssigregion.png", canvEBEB->GetName()));
	
cout << __LINE__<< endl;
	TCanvas * canvEBEE = new TCanvas("purity_ppEBEE","purity_ppEBEE");
	ppEBEE_new->SetLineColor(kBlack);
	ppEBEE_new->SetMarkerColor(kBlack);
	ppEBEE_new->Draw("ap");
	ppEBEE_old->SetFillColor(kRed);
	ppEBEE_old->SetFillStyle(3002);
        ppEBEE_new->GetXaxis()->SetTitle("m_{#gamma #gamma} (GeV)");
        ppEBEE_new->GetYaxis()->SetTitle("Fraction");
        ppEBEE_new->GetXaxis()->SetTitleSize( 0.8 *ppEBEE_new->GetXaxis()->GetTitleSize() );
        ppEBEE_new->GetYaxis()->SetTitleSize( 0.8 *ppEBEE_new->GetYaxis()->GetTitleSize() );
	ppEBEE_old->Draw("E2 same");
	leg->Draw();
	canvEBEE->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v5/%s.png", canvEBEE->GetName()));
//	canvEBEE->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v5/%ssigregion.png", canvEBEE->GetName()));
	}

	    
