{
	using namespace RooFit;

	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/test_asimovi_splitshapes/";
//	TFile* _file0 = new TFile("higgsCombine_truth270.GenerateOnly.mH0.123456.root");
//	TFile* _file1 = new TFile("higgsCombine_fixtruth270.GenerateOnly.mH0.123456.root");
	TFile* _file0 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5/higgsCombine_truth.GenerateOnly.mH0.123456.root");
	TFile* _file1 = new TFile("full_analysis_anv1_v19_2D_split_shapes_asimovfixtruthpfEBEB270_lumi_5/higgsCombine_truth.GenerateOnly.mH0.123456.root");
//	TFile* _file1 = new TFile("higgsCombine_fixtruth270.GenerateOnly.mH0.123456.root");
	_file0->cd();
	
	RooAbsData * fakes = toys->Get("toy_asimov");
	// fakes = fakes->reduce("templateNdim2_unroll<4");	
	_file1->cd();
	RooAbsData * data = toys->Get("toy_asimov");
	// data = data->reduce("templateNdim2_unroll<4");	
	
	w->exportToCint("ws");
	RooCategory & cat = ws::CMS_channel;

	
        TList *datasets = data->split(cat, true);
        TIter next(datasets);

	_file0->cd();
        TList *fdatasets = fakes->split(cat, true);
	TIter fnext(fdatasets);
	_file1->cd();
	
        for (RooAbsData *ds = (RooAbsData *) next(); ds != 0; ds = (RooAbsData *) next()) {
	    
	    RooAbsData *fds = (RooAbsData *) fnext();
	    ws::mgg.setRange("sig_region",ws::mgg.getMin(),ws::mgg.getMax());
		    
	    RooPlot * framei = ws::mgg.frame(Title(ds->GetName()),Bins(134));
		TLegend* leg = new TLegend(0.55, 0.75, .9, .9);
	    
		    fds->plotOn(framei,MarkerStyle(kOpenCircle),Name("redBkg"),MarkerColor(kRed-1));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
	    ds->plotOn(framei,Name("totBkg"),MarkerStyle(kOpenTriangleUp));
	    
	    TCanvas * canvi = new TCanvas(ds->GetName(),ds->GetName());
	    
	    canvi->SetLogy();
	    canvi->SetLogx();
	    
	    framei->GetYaxis()->SetRangeUser(1e-5,700);
	    
	    framei->Draw();
		leg->SetFillColor(0);
		leg->AddEntry(totBkg,"fixedtruth270" ,"p");
		leg->AddEntry(redBkg,"truth270" ,"p");
		leg->Draw();
	    
	    canvi->SaveAs(Form("%s%s.png", dir.Data(),canvi->GetName()));
	    /// canvi->SaveAs(Form("template_%s.png", canvi->GetName()));
		//
/*
	    RooPlot * framej = ws::templateNdim2_unroll.frame(Title(Form("template%s",ds->GetName())),Bins(9));
	    ws::templateNdim2_unroll.setRange("full_region",0.,9.);
	    ws::mgg.setRange("full_region",ws::mgg.getMin(),ws::mgg.getMax());
	    
		    fds->plotOn(framej,MarkerStyle(kOpenCircle));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
	    ds->plotOn(framej,DataError(RooAbsData::Poisson),MarkerStyle(kOpenTriangleUp));
	    
	    TCanvas * canvj = new TCanvas(Form("template%s",ds->GetName()),Form("template%s",ds->GetName()));
	    
	    framej->Draw();
		leg->Draw();
	    
	    canvj->SaveAs(Form("%s%s.png", dir.Data(),canvj->GetName()));
	*/
		}
}

	    
