{
	using namespace RooFit;

	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_300test/";
	TFile* _file1 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_300_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.123456.root");
	TFile* _file0 = new TFile("full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_noweightcuts_300_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.123456.root");
//	TFile* _file0 = new TFile("higgsCombine_300noweightcut_truth_nopp.GenerateOnly.mH0.123456.root ");
//	TFile* _file1 = new TFile("higgsCombine_fixtruth270.GenerateOnly.mH0.123456.root");
//	TFile* _file0 = new TFile("PasqualeFit/higgsCombine_truth.GenerateOnly.mH0.123456.root");
//	TFile* _file1 = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog300_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.123456.root");
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
	    TH1D*fhisto = new TH1D("fhisto","fhisto", 134,ws::mgg.getMin(),ws::mgg.getMax());
	    TH1D*dhisto = new TH1D("dhisto","dhisto", 134,ws::mgg.getMin(),ws::mgg.getMax());
		fds->fillHistogram(fhisto,RooArgList(ws::mgg));
		ds->fillHistogram(dhisto,RooArgList(ws::mgg));
	   	fhisto->Divide(dhisto); 
	 //   if( TString(ds->GetName()).Contains("control") ) {
		//fds->plotOn(framei,MarkerStyle(kOpenCircle),Name("redBkg"),MarkerColor(kRed),Rescale(1./fds->numEntries()));//Rescale(1./fds->numEntries()),DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
		//ds->plotOn(framei,Name("totBkg"),MarkerStyle(kOpenTriangleUp),Rescale(1./ds->numEntries()));
		ds->plotOn(framei,Name("totBkg"),MarkerStyle(kOpenTriangleUp));
		fds->plotOn(framei,MarkerStyle(kOpenCircle),Name("redBkg"),MarkerColor(kRed));//Rescale(1./fds->numEntries()),DataError(RooAbsData::Poisson),LineColor(kRed-1),MarkerColor(kRed-1));
	    
	    TCanvas * canvi = new TCanvas(Form("asimov%s",ds->GetName()),Form("asimov%s",ds->GetName()));
	    
	    canvi->SetLogy();
	    canvi->SetLogx();
	    canvi->SetGridy();
	    canvi->SetGridx();
	    
	    framei->GetYaxis()->SetRangeUser(1e-7,700);
	    
	     framei->Draw();
		leg->SetFillColor(0);
		leg->AddEntry(totBkg,"me split shapes self fit" ,"p");
		leg->AddEntry(redBkg,"me truth self fit" ,"p");
		leg->Draw();
	    
	    canvi->SaveAs(Form("%s%s.png", dir.Data(),canvi->GetName()));
	    /// canvi->SaveAs(Form("template_%s.png", canvi->GetName()));
		//

	    
	    TCanvas * canvj = new TCanvas(Form("asimov_ratio%s",ds->GetName()),Form("asimov_ratio%s",ds->GetName()));
		fhisto->Draw();
	    
	    
	    canvj->SaveAs(Form("%s%s.png", dir.Data(),canvj->GetName()));
	
	//	}
		}
}

	    
