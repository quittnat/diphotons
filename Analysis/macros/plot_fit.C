{
	using namespace RooFit;

	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/full_analysis_anv1_v19/full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5/";
 	TFile* _file0 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5/higgsCombine_fit_truth_nopp.MultiDimFit.mH0.123456.root");
	TFile* _file1 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.123456.root");
// 	TFile* _file0 = new TFile("higgsCombine_truth_nopp.GenerateOnly.mH0.123456.root");
//	TFile* _file1 = new TFile("higgsCombine_truth.GenerateOnly.mH0.123456.root");
	_file0->cd();
	
	RooAbsData * fakes = toys->Get("toy_asimov");
	// fakes = fakes->reduce("templateNdim2_unroll<4");	
	_file1->cd();
	RooAbsData * data = toys->Get("toy_asimov");
	// data = data->reduce("templateNdim2_unroll<4");	
	
	w->loadSnapshot("MultiDimFit");
	w->exportToCint("ws");
	RooCategory & cat = ws::CMS_channel;

	RooSimultaneousOpt & sim = ws::model_s;
	
        TList *datasets = data->split(cat, true);
        TIter next(datasets);

	_file0->cd();
        TList *fdatasets = fakes->split(cat, true);
	TIter fnext(fdatasets);
	_file1->cd();
	
        for (RooAbsData *ds = (RooAbsData *) next(); ds != 0; ds = (RooAbsData *) next()) {
            RooAbsPdf *pdfi  = sim->getPdf(ds->GetName());
	    
	    RooAbsData *fds = (RooAbsData *) fnext();
	    ws::templateNdim2_unroll.setRange("sig_region",0,9.);
	    ws::mgg.setRange("sig_region",ws::mgg.getMin(),ws::mgg.getMax());
		    
	    RooPlot * framei = ws::mgg.frame(Title(ds->GetName()),Bins(134),Range("sig_region"));
		TLegend* leg = new TLegend(0.55, 0.75, .9, .9);
	    /// RooPlot * framei = ws::templateNdim2_unroll.frame(Title(ds->GetName()));
	    /// if( TString(ds->GetName()).Contains("control") ) {
	    /// 	    continue;
	    /// }
	    
	    if(! TString(ds->GetName()).Contains("control") ) {
		    fds->plotOn(framei,MarkerStyle(kOpenCircle),Name("redBkg"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
	    }
	    ds->plotOn(framei,Name("totBkg"));
	    pdfi->plotOn(framei,LineColor(kBlue),Name("total"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framei,LineColor(kRed),Components("*pf*"),Name("pf"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framei,LineColor(kOrange),Components("*ff*"),Name("ff"));//,ProjectionRange("sig_region"));
	    
	    TCanvas * canvi = new TCanvas(ds->GetName(),ds->GetName());
	    
	    canvi->SetLogy();
	    canvi->SetLogx();
	    
	    framei->GetYaxis()->SetRangeUser(1e-5,700);
	    
	    framei->Draw();
		leg->SetFillColor(0);
		leg->AddEntry(totBkg,"full background" ,"p");
		leg->AddEntry(redBkg,"reducible background" ,"p");
		leg->AddEntry(total,"total fit" ,"l");
		leg->AddEntry(pf,"pf component" ,"l");
		leg->AddEntry(ff,"ff component" ,"l");
		leg->Draw();
	    
	    canvi->SaveAs(Form("%s%s.png", dir.Data(),canvi->GetName()));
	    /// canvi->SaveAs(Form("template_%s.png", canvi->GetName()));
		//

	    RooPlot * framej = ws::templateNdim2_unroll.frame(Title(Form("template%s",ds->GetName())),Bins(9));
	    ws::templateNdim2_unroll.setRange("full_region",0.,9.);
	    ws::mgg.setRange("full_region",ws::mgg.getMin(),ws::mgg.getMax());
	    
	    if( TString(ds->GetName()).Contains("control") ) {
	     	    continue;
	    }
	    if(! TString(ds->GetName()).Contains("control") ) {
		    fds->plotOn(framej,MarkerStyle(kOpenCircle),Range("full_region"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
	    }
	    ds->plotOn(framej,DataError(RooAbsData::Poisson));
	    pdfi->plotOn(framej,LineColor(kBlue));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framej,LineColor(kRed),Components("*pf*"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framej,LineColor(kOrange),Components("*ff*"));//,ProjectionRange("sig_region"));
	    
	    TCanvas * canvj = new TCanvas(Form("template%s",ds->GetName()),Form("template%s",ds->GetName()));
	    
	    framej->Draw();
		leg->Draw();
	    
	    canvj->SaveAs(Form("%s%s.png", dir.Data(),canvj->GetName()));
	}
}

	    
