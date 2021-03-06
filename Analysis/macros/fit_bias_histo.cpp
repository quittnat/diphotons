{
# include <list>	
	using namespace RooFit;
	gSystem->Load("libHiggsAnalysisCombinedLimit");
	gSystem->Load("libdiphotonsUtils");
	bool check= false;
	TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/plots_300";
	//TODO includes etc
 	TFile* nomfitresfile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_300_lumi_5/multidimfit_fitnoweightcut_truth.root");
	TFile* nompdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_300_lumi_5/higgsCombine_fitnoweightcut_truth.MultiDimFit.mH0.123456.root");
	TFile* truthpdffile = new TFile("higgsCombine_300noweightcut_truth.GenerateOnly.mH0.123456.root");
//	TFile* nompdffile = new TFile("full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_self.MultiDimFit.mH0.root");
// 	TFile* nomfitresfile = new TFile("PasqualeFitOldf/full_analysis_anv1_v19_2D_split_shapes_semiparam_test_lumi_5/multidimfit_fit_truth.root");
//	TFile* truthpdffile =  new TFile("PasqualeFitOldf/higgsCombine_truth.GenerateOnly.mH0.123456.root ");
//	TFile* truthpdffile =  new TFile("PasqualeFitOldf/full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_lumi_5/higgsCombine_truth.GenerateOnly.mH0.123456.root ");
//	TFile* nompdffile =  new TFile("PasqualeFitOldf/full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5/higgsCombine_fit_truth.MultiDimFit.mH0.root");

	//bkg only
//	std::string components[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE"}; 
	//std::string comp[]={"pp_EBEB", "pf_EBEB", "ff_EBEB", "pp_EBEE","pf_EBEE","ff_EBEE"}; 
//	std::vector<std::string> components;
//	std::vector<std::string> components(comp, end(comp));
	
	/*
	for (int j=0; j< comp.size(); j++)
	{
		components.push_back(comp[j]);
	}
	components.push_back("pp_EBEB");
	components.push_back("pp_EBEE");
	components.push_back("pf_EBEB");
	components.push_back("pf_EBEE");
	components.push_back("ff_EBEB");
	components.push_back("ff_EBEE");
	cout << components[1] << endl;
	*/
	std::string compList[]={"pf_EBEB"}; 
	std::list<std::string> components(compList,compList+sizeof(compList)/sizeof(std::string)); 

	const int nsampling=300;
	int nbins=0;
	double binning =50.;
	
	//for(int it=0; it < components.size(); it++) {
	//for(std::vector<std::string>::iterator it = components.begin(); it != components.end(); ++it) {
	for(std::list<std::string>::iterator it = components.begin(); it != components.end(); ++it) {
		TString comp=*it;
	
		//TString comp(*it);
		cout << "----------- component " << comp.Data() << "----------------------" << endl;
		TString fitShapeName=Form("shapeBkg_%s", comp.Data());
		TString fitNormName=Form("shapeBkg_%s__norm", comp.Data());
		
		//load truth pdf

		truthpdffile->cd();
		w->exportToCint("wTruth");
		w->loadSnapshot("clean");
		RooArgSet  obsTruth=RooArgSet(wTruth::mgg, wTruth::templateNdim2_unroll);
		wTruth::templateNdim2_unroll.setRange("sigTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		wTruth::templateNdim2_unroll.setRange("binTruth_region",wTruth::templateNdim2_unroll.getMin(),wTruth::templateNdim2_unroll.getMax());
		wTruth::mgg.setRange("sigTruth_region",wTruth::mgg.getMin(),wTruth::mgg.getMax());
		RooProdPdf* fittruthShape=w->pdf(fitShapeName.Data());
		RooProduct* fittruthNorm=w->function(fitNormName.Data());
		RooExtendPdf* fittruthPdf=new RooExtendPdf("fittruthPdf","fittruthPdf",*fittruthShape,*fittruthNorm);
		RooArgSet* truthParams = fittruthPdf->getParameters(obsTruth) ;
		truthParams.Print();	
		//fittruthPdf.Print();
		Double_t inttruthSig=fittruthPdf.createIntegral(obsTruth,"sigTruth_region").getVal()  ;
		if(inttruthSig==0){cout << "integral for " << comp.Data() << " is zero" << endl; continue;}
		
		//variable binning
		const int binning1=50;
		const double mggThres=4000.;
		const int binning2=1000;
		const int nbins=(mggThres-wTruth::mgg.getMin())/binning1 +(wTruth::mgg.getMax()-mggThres)/binning2;
		const int nbins=(mggThres-wTruth::mgg.getMin())/binning1 +(wTruth::mgg.getMax()-mggThres)/binning2;
		const int nbinsP1=nbins+1;
		Double_t xbins[nbinsP1];
    	xbins[0]=wTruth::mgg.getMin();
		const double mggMax= wTruth::mgg.getMax();
    	for(int i=0 ; i <nbins ; i++)
		{
        	if (xbins[i] < mggThres)  xbins[i+1]= xbins[i]+binning1;
        	else if ( (mggThres <= xbins[i]) && (xbins[i]< mggMax))  xbins[i+1]=xbins[i]+binning2;
		}
		xbins[nbins]=mggMax;
		cout << nbins << endl;
	//	nbins=(wTruth::mgg.getMax()-wTruth::mgg.getMin())/binning;
		RooPlot * framei = wTruth::mgg.frame(Title("check"),Bins(nbins),Range("sigTruth_region"));
		fittruthPdf->plotOn(framei,LineColor(kBlack),Project(wTruth::templateNdim2_unroll));
		
		//RooArgList fitPdfs=RooArgList() 
//		RooExtendedPdf* fitAllPdf= new RooExtendedPdf("fitAllPdf","fitAllPdf",)
		
		//load nominal pdf
		nompdffile->cd();
		w->loadSnapshot("MultiDimFit");
		w->exportToCint("wNom");
		RooArgSet obsNom=RooArgSet(wNom::mgg, wNom::templateNdim2_unroll);
		wNom::mgg.setRange("sig_region",wNom::mgg.getMin(),wNom::mgg.getMax());
		wNom::templateNdim2_unroll.setRange("sig_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		wNom::templateNdim2_unroll.setRange("bin_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
		
		RooProdPdf* fitnomShape=w->pdf(fitShapeName.Data());
		RooProduct* fitnomNorm=w->function(fitNormName.Data());
		RooExtendPdf* fitnomPdf=new RooExtendPdf("fitnomPdf","fitnomPdf",*fitnomShape,*fitnomNorm);
		Double_t exptruthEvents= fittruthPdf->expectedEvents(obsTruth);
		fitnomPdf.Print();
		Double_t intnomSig=0. ;
		intnomSig=fitnomPdf.createIntegral(obsNom,"sig_region").getVal()  ;
		if(intnomSig==0){cout << "integral for " << comp.Data() << " is zero" << endl; continue;}
//		cout << "truth expEvent " << fittruthPdf->expectedEvents(obsTruth) << " inttruthSig " << inttruthSig << "nom expEvent " << fitnomPdf->expectedEvents(obsNom) <<" intnomSig " << intnomSig << endl;
		fitnomPdf->plotOn(framei,LineColor(kBlue),Project(wNom::templateNdim2_unroll));
		
		//w->loadSnapshot("MultiDimFit");
		RooProdPdf* randShape=w->pdf(fitShapeName.Data());
		RooProduct* randNorm=w->function(fitNormName.Data());
		RooExtendPdf* randPdf=new RooExtendPdf("randPdf","randPdf",*randShape,*randNorm);
		Double_t expnomEvents= fitnomPdf->expectedEvents(obsNom);
		RooArgSet* pdfParams = randPdf->getParameters(obsNom) ;
		pdfParams.Print("v");	
		
		//get fitresult and randomize parameters in covariance matrix
		nomfitresfile->cd();
		fit.Print("v");
		//const TMatrixDSym & cov=fit->covarianceMatrix();
		Double_t intPdfs[nsampling][nbins];
		
		Double_t inttruthBin[nbins];
		Double_t intnomBin[nbins];
		Double_t massbins[nbins];
		Double_t masserr[nbins];
		Double_t binwidth[nbins];
		Double_t min[nbins];
		Double_t max[nbins];
		for(int bin=0; bin <nbins;++bin){
				Double_t intBin=0.;
				//max[bin]= wNom::mgg.getMin() + binning*bin +binning;
				//min[bin]= wNom::mgg.getMin() + binning*bin;
				//TODO clean up max mix, just xbins
				max[bin]= xbins[bin+1];
				min[bin]= xbins[bin];
				massbins[bin]=(max[bin]+min[bin])/2.;
				masserr[bin]=(max[bin]-min[bin])/2.;
				binwidth[bin]=(max[bin]-min[bin]);
				wNom::mgg.setRange("bin_region",min[bin],max[bin]);
				Double_t intnomPdf=((fitnomPdf.createIntegral(obsNom,"bin_region").getVal())/intnomSig)  ;
				//intnomBin[bin]=expnomEvents*intnomPdf ;
				intnomBin[bin]=expnomEvents*intnomPdf/binwidth[bin] ;
				wTruth::mgg.setRange("binTruth_region",min[bin],max[bin]);
				Double_t inttruthPdf=((fittruthPdf.createIntegral(obsTruth,"binTruth_region").getVal())/inttruthSig)  ;
				inttruthBin[bin]=exptruthEvents*inttruthPdf/binwidth[bin] ;
				//inttruthBin[bin]=exptruthEvents*inttruthPdf ;
		//			cout <<" intnomBin "<<intnomBin[bin] << " inttruthBin "<<inttruthBin[bin] << endl; 
		}
		for(int r=0;r< nsampling;++r){	
			if(r==10 || r==40 ||r==100 || r==300 || r==450){
				cout << "---------------------------------  sampling" << r << "----------" << endl;
//				pdfParams.Print("v");
//				NormParams.Print("v");
			}
		//square root method for decomposition automatically applied
		//	pdfParams.Print("v");
			const RooArgList & randParams=fit.randomizePars();
			*pdfParams = randParams ;
		//	*NormParams = randParams ;
			Double_t intSig=0., exprandEvents=0.;
			wNom::mgg.setRange("sigRand_region",wNom::mgg.getMin(),wNom::mgg.getMax());
			wNom::templateNdim2_unroll.setRange("sigRand_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
			Double_t intSig=randPdf.createIntegral(obsNom,"sigRand_region").getVal()  ;
			Double_t exprandEvents= randPdf->expectedEvents(obsNom);
			wNom::templateNdim2_unroll.setRange("binRand_region",wNom::templateNdim2_unroll.getMin(),wNom::templateNdim2_unroll.getMax());
			
			for(int bin=0; bin <nbins;++bin){
				wNom::mgg.setRange("binRand_region",min[bin],max[bin]);
				//intBin=fitnomNorm*(randShape.createIntegral(obsNom,"binRand_region").getVal())  ;
				intBin=randShape.createIntegral(obsNom,"binRand_region").getVal()  ;
				//intPdfs[r][bin]=exprandEvents*(intBin/intSig);
				intPdfs[r][bin]=exprandEvents*(intBin/intSig)/binwidth[bin];
				if(check && r==4 ){
					cout <<bin << " : " <<  intPdfs[r][bin]  << " truth "<< inttruthBin[bin] <<"  nom "<< intnomBin[bin]<< endl;
				}
			}
			/*
			if( r==4 ){
					TCanvas * canvi = new TCanvas("ccheck","ccheck");
					canvi->SetLogy();
					canvi->SetGridy();
					canvi->SetGridx();
				//	canvi->SetLogx();
					randPdf->plotOn(framei,LineColor(kGreen+1),Project(wNom::templateNdim2_unroll));
	    			framei->GetYaxis()->SetRangeUser(1e-7,1000);
					framei->Draw();
					canvi->SaveAs(Form("%scheckDiff_%s__samp_4.png",dir.Data(),comp.Data()));
					delete canvi;
			}
			*/
		}
			randPdf=NULL;
			randShape=NULL;
			randNorm=NULL;
			
			delete randPdf;
			delete randShape;
			delete randNorm;
		
		cout << "finished randomizing + integration " << endl;
		//plot result histo per bin for integral values from randomized pdfs
		gStyle->SetOptStat(111111);
		Double_t diff[nbins] ;	
		Double_t err2Plus[nbins] ;	
		Double_t err2Min[nbins] ;	
		
		Double_t pull[nbins] ;	
		Double_t errPlus[nbins] ;	
		Double_t errMin[nbins] ;	
		Double_t difffrac[nbins] ;	
		Double_t histmean[nbins] ;	
		
		for(int bin=0;bin< nbins;bin++)
		{
			double xmin=0.;
			double xmax=0.;
			//get min and max element for histo
			for(unsigned int j=0; j<nsampling; ++j){
					if(intPdfs[j][bin] > xmax){
						xmax = intPdfs[j][bin];
					}
					if(intPdfs[j][bin] < xmin){
						xmin = intPdfs[j][bin];
					}
			  }
			
			//compute 68 and 95 percent 
			const int qn=5;
			Double_t quant[qn] ;	
			Double_t prob[qn]={0.025,0.16,0.5,0.84,0.975};
			TH1D* hist=new TH1D("hist","hist",100,xmin, xmax);
			for(int samp=0; samp< nsampling; samp++){hist->Fill(intPdfs[samp][bin]);}
			histmean[bin]=hist->GetMean();
			hist->GetQuantiles(qn,quant,prob);
			diff[bin]= intnomBin[bin]-inttruthBin[bin];	
			difffrac[bin]= diff[bin]/intnomBin[bin];	
			errPlus[bin]= quant[3]-intnomBin[bin];	
			errMin[bin]= intnomBin[bin]-quant[1];	
			err2Plus[bin]= quant[4]-intnomBin[bin];	
			err2Min[bin]=intnomBin[bin]-quant[0];	
			/*errPlus[bin]= quant[3]-intnomBin[bin];	
			errMin[bin]= intnomBin[bin]-quant[1];	
			err2Plus[bin]= quant[4]-intnomBin[bin];	
			err2Min[bin]=intnomBin[bin]-quant[0];	
			*/
			
			
			//pull function if diff positiv, take positv value
			if (intnomBin[bin]>= inttruthBin[bin]){
				pull[bin]=diff[bin]/errMin[bin];
			}
			else {
				pull[bin]=diff[bin]/errPlus[bin];
			}
			
			if(bin > 10)
			{
				TCanvas* chisto= new TCanvas("chisto","chisto");
				chisto->cd(1);
				gStyle->SetOptStat(111);
				
				hist->Draw();
				TLine *lmean = new TLine(intnomBin[bin],0.,intnomBin[bin], hist->GetBinContent(hist->GetMaximumBin()));
				lmean->SetLineColor(kGreen+1);
				lmean->SetLineWidth(3);
				lmean->SetLineStyle(4);
				TLine *lmeanTruth = new TLine(inttruthBin[bin],0.,inttruthBin[bin],hist->GetBinContent(hist->GetMaximumBin()));
				lmeanTruth->SetLineColor(kYellow+1);
				lmeanTruth->SetLineWidth(3);
				lmeanTruth->SetLineStyle(4);
				TLine *lm2s = new TLine(quant[0],0.,quant[0],hist->GetBinContent(hist->GetMaximumBin()));
				lm2s->SetLineColor(kMagenta);
				lm2s->SetLineWidth(3);
				TLine *lm1s = new TLine(quant[1],0.,quant[1],hist->GetBinContent(hist->GetMaximumBin()));
				lm1s->SetLineColor(kMagenta+1);
				lm1s->SetLineWidth(3);
				TLine *lm = new TLine(quant[2],0.,quant[2],hist->GetBinContent(hist->GetMaximumBin()));
				lm->SetLineColor(kMagenta+2);
				lm->SetLineWidth(3);
				TLine *l1s = new TLine(quant[3],0.,quant[3],hist->GetBinContent(hist->GetMaximumBin()));
				l1s->SetLineColor(kMagenta+3);
				l1s->SetLineWidth(3);
				TLine *l2s = new TLine(quant[4],0.,quant[4],hist->GetBinContent(hist->GetMaximumBin()));
				l2s->SetLineColor(kMagenta+4);
				l2s->SetLineWidth(3);
				lm2s->Draw("SAME");
				lm1s->Draw("SAME");
				lm->Draw("SAME");
				l1s->Draw("SAME");
				l2s->Draw("SAME");
				lmean->Draw("SAME");
				lmeanTruth->Draw("SAME");
				TLegend* leg3 = new TLegend(0.45, 0.7, .7, .9);
				leg3->SetFillColor(0);
				leg3->AddEntry(lmeanTruth,"mean truth" ,"l");
				leg3->AddEntry(lmean,"mean nominal start fit" ,"l");
				leg3->AddEntry(lm2s,"2.5 %" ,"l");
				leg3->AddEntry(lm1s,"16 %" ,"l");
				leg3->AddEntry(lm,"50 %" ,"l");
				leg3->AddEntry(l1s,"84 %" ,"l");
				leg3->AddEntry(l2s,"97.5 %" ,"l");
				leg3->Draw();
				chisto->SaveAs(Form("%s/Histo_%s_bin%i.png",dir.Data(),comp.Data(),bin));
				delete chisto;
				delete lm2s;
				delete lm1s;
				delete lm;
				delete l1s;
				delete l2s;
			
			}
			delete hist;
			//delete [] quant;
			//delete [] prob;
		}
		/*
		for(int b=0; b< nbins; b++){
			for(int sa=0; sa< nsampling; sa++){
				if(fabs(intPdfs[sa][b]) <histmean[b]*0.05)
				{
				TCanvas * canv = new TCanvas("ccheck2","ccheck2");
				canv->SetLogy();
				canv->SetGridy();
				canv->SetGridx();
			//	canv->SetLogx();
				randPdf->plotOn(framei,LineColor(kGreen+1),Project(wNom::templateNdim2_unroll));
	    		framei->GetYaxis()->SetRangeUser(1e-7,1000);
				framei->Draw();
				canv->SaveAs(Form("%scheckDiff_%s__samp%i_bin%i.png",dir.Data(),comp.Data(),sa,b));
				delete canvi;
				}
			}
		}
		*/
		//plot 68 and 95 percent 	
		TCanvas *cbias = new TCanvas("cbias","bias on model",10,10,700,900);
		//get mass bins, set legend
		cbias->cd();
		cbias->SetLogy();
		cbias->SetLogx();
		cbias->SetGridy();
		cbias->SetGridx();
		TGraphAsymmErrors *gr1sigma = new TGraphAsymmErrors(nbins,massbins,intnomBin,masserr,masserr,errMin,errPlus);
		TGraphAsymmErrors *gr2sigma = new TGraphAsymmErrors(nbins,massbins,intnomBin,masserr,masserr,err2Min,err2Plus);
		TGraph *grmean = new TGraph(nbins,massbins,intnomBin);

		TGraph *grmeanTruth = new TGraph(nbins,massbins,inttruthBin);
		gr1sigma->SetTitle("uncertainty of model");
	
		grmeanTruth->SetLineWidth(3);
		grmeanTruth->SetLineColor(kBlack);
		grmean->SetLineColor(kBlue);
		grmean->SetLineWidth(3);
	
		gr1sigma->SetFillColor(kYellow+1);
		gr1sigma->SetLineColor(kBlue);
		gr1sigma->SetLineWidth(3);
		gr2sigma->SetMarkerColor(kBlue);
		gr2sigma->SetLineColor(kBlue);
		gr2sigma->SetLineWidth(3);
		gr2sigma->SetFillColor(kGreen+1);
		
		gr2sigma->Draw("a l C E3"); 
		gr1sigma->Draw("C  E3 SAME"); 
		grmean->Draw("C l SAME"); 
		grmeanTruth->Draw("C l SAME"); 
		
		gr2sigma->GetXaxis()->SetTitle("mass [GeV]");
	//	gr2sigma->GetXaxis()->SetRangeUser(wTruth::mgg.getMin(),4000.);
		TLegend* leg = new TLegend(0.55, 0.75, .9, .9);
		leg->SetFillColor(0);
		leg->AddEntry(grmeanTruth,"true distribution" ,"l");
		leg->AddEntry(grmean,"fit projection" ,"l");
		leg->AddEntry(gr1sigma,"68%" ,"f");
		leg->AddEntry(gr2sigma,"95%" ,"f");
		leg->Draw();
		cbias->SaveAs(Form("%scbias_%s.png",dir.Data(),comp.Data()));
		cbias->SaveAs(Form("%scbias_%s.eps",dir.Data(),comp.Data()));
		cbias->SaveAs(Form("%scbias_%s.root",dir.Data(),comp.Data()));
		
		//pull distribution
		TCanvas *cpull = new TCanvas("cpull","pull distribution",10,10,700,900);
		cpull->cd();
		cpull->SetLogx();
		cpull->SetGridx();
		cpull->SetGridy();
		TGraph *grpull = new TGraph(nbins,massbins,pull);
		grpull->SetLineWidth(3);
		grpull->SetTitle("pull function");
		grpull->SetLineColor(kBlue+1);
		grpull->Draw("C a "); 
		grpull->GetXaxis()->SetTitle("mass [GeV]");
		//grpull->GetXaxis()->SetRangeUser(wTruth::mgg.getMin(),4000.);
		grpull->GetYaxis()->SetTitle("pull");
		cpull->SaveAs(Form("%scpull_%s.png",dir.Data(),comp.Data()));
		cpull->SaveAs(Form("%scpull_%s.root",dir.Data(),comp.Data()));
		cpull->SaveAs(Form("%scpull_%s.eps",dir.Data(),comp.Data()));
		
		
		TCanvas *cfrac = new TCanvas("cfrac","bias on model",10,10,700,900);
		cfrac->cd();
		cfrac->SetLogx();
		
		cfrac->SetGridx();
		cfrac->SetGridy();
		TGraph *grfrac = new TGraph(nbins,massbins,difffrac);
		grfrac->SetMarkerStyle(21);
		grfrac->SetTitle("fraction");
		grfrac->SetMarkerColor(kCyan+1);
		grfrac->Draw("p a"); 
		grfrac->GetXaxis()->SetTitle("mass [GeV]");
		grfrac->GetYaxis()->SetTitle("(Nnom-Ntruth)/Nnom");
	//	grfrac->GetXaxis()->SetRangeUser(wTruth::mgg.getMin(),4000.);
		cfrac->SaveAs(Form("%scfrac_%s.png",dir.Data(),comp.Data()));
		
		fittruthPdf=NULL;
		fittruthShape=NULL;
		fittruthNorm=NULL;
		fitnomPdf=NULL;
		fitnomShape=NULL;
		fitnomNorm=NULL;

		delete fittruthPdf;
		delete fittruthShape;
		delete fittruthNorm;
		delete fitnomPdf;
		delete fitnomShape;
		delete fitnomNorm;
		delete cfrac;
		delete cbias;
		delete cpull;
	}
	
}

/*
void PrintProgress(Long64_t entry)
{
    int step = 10; 
    // Adapt step in powers of 10 (every 10 below 100, every 100 below 1000, etc.)
// Method that prints the progress at reasonable frequency
    Long64_t power = 1;
    for ( size_t i=1; i<10; ++i )
   	{ // up to 10^10...
        power *= 10; 
        if ( !(entry/power) ) break;
        step = power;
    }   
*/



