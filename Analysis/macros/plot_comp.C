{
	using namespace RooFit;

	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/fit_frozenShapes/";
	//TFile* _file1 = new TFile("old_fullan049/full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_noweightcuts_300_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.123456.root");
	TFile* _file1 = new TFile("full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_adhocpf_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.123456.root");
//	TFile* _file0 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_fittest_lumi_5/higgsCombine_self.GenerateOnly.mH0.123456.root");
	TFile* _file0 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocpf_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.123456.root");
	_file0->cd();
	
	RooAbsData * fakes = toys->Get("toy_asimov");
	w->loadSnapshot("MultiDimFit");
//	w->loadSnapshot("clean");
	w->exportToCint("ws2");
	_file1->cd();
	RooAbsData * data = toys->Get("toy_asimov");
	
	w->loadSnapshot("MultiDimFit");
	//w->loadSnapshot("clean");
	w->exportToCint("ws");
	RooCategory & cat = ws::CMS_channel;
	RooSimultaneousOpt & sim = ws::model_s;
	
        TList *datasets = data->split(cat, true);
        TIter next(datasets);

	_file0->cd();
        TList *fdatasets = fakes->split(cat, true);
	RooSimultaneousOpt & fsim = ws2::model_s;
	TIter fnext(fdatasets);
	_file1->cd();
	
        for (RooAbsData *ds = (RooAbsData *) next(); ds != 0; ds = (RooAbsData *) next()) {
            RooAbsPdf *pdfi  = sim->getPdf(ds->GetName());
	    
	    RooAbsData *fds = (RooAbsData *) fnext();
            RooAbsPdf *pdff  = fsim->getPdf(fds->GetName());
	    ws::templateNdim2_unroll.setRange("sig_region",0,9.);
	    ws::mgg.setRange("sig_region",ws::mgg.getMin(),ws::mgg.getMax());
		    
	    RooPlot * framei = ws::mgg.frame(Title(ds->GetName()),Bins(134),Range("sig_region"));
		TLegend* leg = new TLegend(0.55, 0.75, .9, .9);
	    
		fds->plotOn(framei,MarkerStyle(kOpenCircle),Name("totNom"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
		pdff->plotOn(framei,LineColor(kRed),LineWidth(5),Components("*pf*"),Name("redNom"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
		
		ds->plotOn(framei,Name("totBkg"));
	    pdfi->plotOn(framei,LineColor(kBlue),LineStyle(2),Name("total"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framei,LineColor(kYellow+1),LineStyle(2),Components("*pf*"),Name("pf"));//,ProjectionRange("sig_region"));

	    pdfi->plotOn(framei,LineColor(kOrange),LineStyle(2),Components("*ff*"),Name("ff"));//,ProjectionRange("sig_region"));
	    
	    TCanvas * canvi = new TCanvas(ds->GetName(),ds->GetName());
	    
	    canvi->SetLogy();
	    canvi->SetLogx();
	    canvi->SetGridy();
	    canvi->SetGridx();
	    
	    framei->GetYaxis()->SetRangeUser(1e-7,700);
	    
	    framei->Draw();
		leg->SetFillColor(0);
		leg->AddEntry(totBkg,"truth " ,"p");
		leg->AddEntry(totNom," nominal model" ,"p");
		leg->AddEntry(redNom,"pf nominal model" ,"l");
		leg->AddEntry(total,"total truth self fit" ,"l");
		leg->AddEntry(pf,"pf component truth" ,"l");
		leg->AddEntry(ff,"ff component truth" ,"l");
		leg->Draw();
	    
	    canvi->SaveAs(Form("%stn%s.png", dir.Data(),canvi->GetName()));
		//


	    RooPlot * framej = ws::templateNdim2_unroll.frame(Title(Form("template%s",ds->GetName())),Bins(9));
	    ws::templateNdim2_unroll.setRange("full_region",0.,9.);
	    ws::mgg.setRange("full_region",ws::mgg.getMin(),ws::mgg.getMax());
		fds->plotOn(framej,MarkerStyle(kOpenCircle),DataError(RooAbsData::Poisson),Range("full_region"),Name("totNom2"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
		pdff->plotOn(framej,LineColor(kRed),Components("*pf*"),Name("redNom2"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
		pdff->plotOn(framej,LineColor(kGreen),Components("*pp*"),Name("ppNom2"));//,DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
	    
	    ds->plotOn(framej,DataError(RooAbsData::Poisson),Name("totBkg2"));
	    pdfi->plotOn(framej,LineStyle(2),LineColor(kBlue),Name("total2"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framej,LineColor(kYellow+3),LineStyle(2),Components("*pp*"),Name("pp2"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framej,LineColor(kYellow+1),LineStyle(2),Components("*pf*"),Name("pf2"));//,ProjectionRange("sig_region"));
	    pdfi->plotOn(framej,LineColor(kOrange),LineStyle(2),Components("*ff*"),Name("ff2"));//,ProjectionRange("sig_region"));
	    
	    TCanvas * canvj = new TCanvas(Form("template%s",ds->GetName()),Form("template%s",ds->GetName()));
	    
	    framej->Draw();
		TLegend* leg2 = new TLegend(0.55, 0.75, .9, .9);
		leg2->SetFillColor(0);
		leg2->AddEntry(totNom2," nominal model" ,"p");
		leg2->AddEntry(ppNom2," pp nominal model" ,"l");
		leg2->AddEntry(redNom2,"pf nominal model" ,"l");
		leg2->AddEntry(totBkg2,"truth " ,"p");
		leg2->AddEntry(total2,"total truth self fit" ,"l");
		leg2->AddEntry(pp2,"pp component truth" ,"l");
		leg2->AddEntry(pf2,"pf component truth" ,"l");
		leg2->AddEntry(ff2,"ff component truth" ,"l");
		leg2->Draw();
	    
	    
	    canvj->SaveAs(Form("%stn%s.png", dir.Data(),canvj->GetName()));
		
	}
	
}

	    
