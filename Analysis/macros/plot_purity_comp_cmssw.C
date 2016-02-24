{
//if necessary also normal projections and looip over massbins
	using namespace RooFit;
	TFile *_file0 = TFile::Open("purity_sigregion_7415v2_v5_data_ecorr_pas.root");
	TFile *_file1 = TFile::Open("purity_sigregion_moriond16v1_sync_v2_data.root");
//	TFile *_file0 = TFile::Open("purity_7415v2_v5_data_ecorr_pas.root");
//	TFile *_file1 = TFile::Open("purity_moriond16v1_sync_v2_data.root");


 _file0->cd();	
	TGraphErrors* ppEBEB_old= (TGraphErrors*)(wtemplates->genobj("g_ppEBEB"));
	TGraphErrors* ppEBEE_old= (TGraphErrors*)(wtemplates->genobj("g_ppEBEE"));
 	_file1->cd();	
	TGraphErrors* ppEBEB_new= (TGraphErrors*)(wtemplates->genobj("g_ppEBEB"));
	TGraphErrors* ppEBEE_new= (TGraphErrors*)(wtemplates->genobj("g_ppEBEE"));
	TGraphErrors* ratioppEBEB= new TGraphErrors();
	TGraphErrors* ratioppEBEE= new TGraphErrors();
	for(int mb=0; mb< ppEBEB_old->GetN();mb++){
		double x=0.,y=0.,xn=0.,yn=0.,err=0.,errX=0.;
		ppEBEB_old->GetPoint(mb,x,y);
		ppEBEB_new->GetPoint(mb,xn,yn);
		err=ppEBEB_new->GetErrorY(mb);
		errX=ppEBEB_new->GetErrorX(mb);
        ratioppEBEB->SetPoint(mb,x,(yn-y)/err);
        ratioppEBEB->SetPointError(mb,errX,0.);
	}
	for(int mb=0; mb< ppEBEE_old->GetN();mb++){
		double x=0.,y=0.,xn=0.,yn=0.,err=0.,errX=0.;
		ppEBEE_old->GetPoint(mb,x,y);
		ppEBEE_new->GetPoint(mb,xn,yn);
		err=ppEBEE_new->GetErrorY(mb);
		errX=ppEBEE_new->GetErrorX(mb);
        ratioppEBEE->SetPoint(mb,x,(yn-y)/err);
        ratioppEBEE->SetPointError(mb,errX,0.);
	
	}
	
	TCanvas * canvEBEB = new TCanvas("purity_ppEBEB","purity_ppEBEB");
    canvEBEB->Divide(1,2);
    canvEBEB->cd(1);
    gPad->SetPad(0., 0.3, 1., 1.0);
    canvEBEB->cd(2);
    gPad->SetPad(0., 0.0, 1.,0.3);
    canvEBEB->cd(1);
	TLegend* leg= new TLegend(0.5,0.8,0.9,0.9);
	ppEBEB_new->SetLineColor(kBlack);
	ppEBEB_new->SetMarkerColor(kBlack);
    ppEBEB_new->GetYaxis()->SetTitle("Fraction");
    ppEBEB_new->GetXaxis()->SetTitleSize( 0.8 *ppEBEB_new->GetXaxis()->GetTitleSize() );
    ppEBEB_new->GetYaxis()->SetTitleSize( 0.8 *ppEBEB_new->GetYaxis()->GetTitleSize() );
	ppEBEB_new->Draw("ap");
	ppEBEB_old->SetFillColor(kRed);
	ppEBEB_old->SetFillStyle(3002);
	ppEBEB_old->Draw("E2 same");
    leg->AddEntry(ppEBEB_new,"#gamma #gamma data CMSSW 7_6 rereco ","lp")  ;
    leg->AddEntry(ppEBEB_old,"#gamma #gamma data CMSSW 7_4 prompt ","f") ;
	leg->Draw();
    canvEBEB->cd(2);
	ratioppEBEB->SetTitle("");
	ratioppEBEB->SetLineColor(kBlack);
	ratioppEBEB->SetMarkerColor(kBlack);
    ratioppEBEB->GetXaxis()->SetTitle("m_{#gamma #gamma} (GeV)");
    ratioppEBEB->GetYaxis()->SetTitle("(rereco-prompt)/#sigma_{rereco}");
    ratioppEBEB->GetYaxis()->SetTitleSize(ppEBEB_new->GetYaxis()->GetTitleSize() * 5.0/3.0 );
    ratioppEBEB->GetYaxis()->SetLabelSize(ppEBEB_new->GetYaxis()->GetLabelSize() *  7.0/3.0 );
    ratioppEBEB->GetYaxis()->SetTitleOffset(ppEBEB_new->GetYaxis()->GetTitleOffset() *  4.0/7.0 );
    ratioppEBEB->GetXaxis()->SetTitleOffset(ratioppEBEB->GetXaxis()->GetTitleOffset() *7.8/7.0);
    ratioppEBEB->GetXaxis()->SetLabelSize(ratioppEBEB->GetXaxis()->GetLabelSize() *  7.0/3.0 );
    ratioppEBEB->GetXaxis()->SetTitleSize( ratioppEBEB->GetYaxis()->GetTitleSize() * 4.0/3.0 );
    ratioppEBEB->GetXaxis()->SetLabelSize( ratioppEBEB->GetYaxis()->GetLabelSize()  );
    ratioppEBEB->GetYaxis()->SetNdivisions(505);
    ratioppEBEB->GetXaxis()->SetLimits(200.,1600.);
    
	ratioppEBEB->Draw("ap");
    
	
	canvEBEB->cd(1);
    double margin = gPad->GetBottomMargin()+gPad->GetTopMargin();
    gPad->SetBottomMargin(0.2*margin);
    canvEBEB->cd(2);
    double margin2 = gPad->GetBottomMargin()+gPad->GetTopMargin();
    gPad->SetBottomMargin(1.8*margin2);
    gPad->SetTopMargin(0.25*margin2);
//	canvEBEB->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%s.png", canvEBEB->GetName()));
	canvEBEB->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%ssigregion.png", canvEBEB->GetName()));
	
	
	TCanvas * canvEBEE = new TCanvas("purity_ppEBEE","purity_ppEBEE");
    canvEBEE->Divide(1,2);
    canvEBEE->cd(1);
    gPad->SetPad(0., 0.3, 1., 1.0);
    canvEBEE->cd(2);
    gPad->SetPad(0., 0.0, 1.,0.3);
    canvEBEE->cd(1);
	ppEBEE_new->SetLineColor(kBlack);
	ppEBEE_new->SetMarkerColor(kBlack);
	ppEBEE_new->Draw("ap");
	ppEBEE_old->SetFillColor(kRed);
	ppEBEE_old->SetFillStyle(3002);
        ppEBEE_new->GetYaxis()->SetTitle("Fraction");
        ppEBEE_new->GetXaxis()->SetTitleSize( 0.8 *ppEBEE_new->GetXaxis()->GetTitleSize() );
        ppEBEE_new->GetYaxis()->SetTitleSize( 0.8 *ppEBEE_new->GetYaxis()->GetTitleSize() );
	ppEBEE_old->Draw("E2 same");
	leg->Draw();
    canvEBEE->cd(2);
	ratioppEBEE->SetTitle("");
	ratioppEBEE->SetLineColor(kBlack);
	ratioppEBEE->SetMarkerColor(kBlack);
    ratioppEBEE->GetXaxis()->SetTitle("m_{#gamma #gamma} (GeV)");
    ratioppEBEE->GetYaxis()->SetTitle("(rereco-prompt)/#sigma_{rereco}");
    ratioppEBEE->GetYaxis()->SetTitleSize(ppEBEE_new->GetYaxis()->GetTitleSize() * 5.0/3.0 );
    ratioppEBEE->GetYaxis()->SetLabelSize(ppEBEE_new->GetYaxis()->GetLabelSize() *  7.0/3.0 );
    ratioppEBEE->GetYaxis()->SetTitleOffset(ppEBEE_new->GetYaxis()->GetTitleOffset() *  4.0/7.0 );
    ratioppEBEE->GetXaxis()->SetTitleOffset(ratioppEBEE->GetXaxis()->GetTitleOffset() *7.8/7.0);
    ratioppEBEE->GetXaxis()->SetLabelSize(ratioppEBEE->GetXaxis()->GetLabelSize() *  7.0/3.0 );
    ratioppEBEE->GetXaxis()->SetTitleSize( ratioppEBEE->GetYaxis()->GetTitleSize() * 4.0/3.0 );
    ratioppEBEE->GetXaxis()->SetLabelSize( ratioppEBEE->GetYaxis()->GetLabelSize()  );
    ratioppEBEE->GetYaxis()->SetNdivisions(505);
    ratioppEBEE->GetXaxis()->SetLimits(200.,1600.);
	ratioppEBEE->Draw("ap");
	canvEBEE->cd(1);
    double margin3 = gPad->GetBottomMargin()+gPad->GetTopMargin();
    gPad->SetBottomMargin(0.2*margin3);
    canvEBEE->cd(2);
    double margin4 = gPad->GetBottomMargin()+gPad->GetTopMargin();
    gPad->SetBottomMargin(1.8*margin4);
    



//	canvEBEE->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%s.png", canvEBEE->GetName()));
	canvEBEE->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/%ssigregion.png", canvEBEE->GetName()));
}

	    
