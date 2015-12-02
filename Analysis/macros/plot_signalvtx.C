{
TNtuple* tree=tree_grav_01_1250_cic2_EBEE;
//TNtuple* tree=tree_grav_01_allmasses_cic2_EBEE;


Float_t leadPt=0.;
Float_t subleadPt=0.;
Float_t diphopt=0.;
Float_t leadEta=0.;
Float_t subleadEta=0.;
Float_t leadPhi=0.;
Float_t subleadPhi=0.;
Float_t genVtxZ=0.;
Float_t recoVtx=0.;
Float_t nvtx=0.;
tree->SetBranchAddress("leadPt",&leadPt);
tree->SetBranchAddress("subleadPt",&subleadPt);
tree->SetBranchAddress("leadEta",&leadEta);
tree->SetBranchAddress("subleadEta",&subleadEta);
tree->SetBranchAddress("leadPhi",&leadPhi);
tree->SetBranchAddress("subleadPhi",&subleadPhi);
tree->SetBranchAddress("genVtxZ",&genVtxZ);
tree->SetBranchAddress("recoVtx",&recoVtx);
tree->SetBranchAddress("nvtx",&nvtx);
int n=tree->GetEntries();
//double bins[17]={0.,50.,100.,150.,200.,250.,300.,350.,400.,450.,500.,550.,600.,700.,800.,1000.,1500.};
double bins[2]={0.,13000.};
// TEfficiency*eff = new TEfficiency("histo","vtx efficiency for grav k=01, 750 GeV, EBEE;p_{t,#gamma#gamma} (GeV);fraction of |z_{reco}-z_{gen}| < 1 cm",16,bins);
 TEfficiency* eff = new TEfficiency("histo","vtx efficiency for grav k=01, EBEE;p_{t,#gamma#gamma} (GeV);fraction of |z_{reco}-z_{gen}| < 1 cm",1,bins);
 //TEfficiency* eff = new TEfficiency("histo","vtx efficiency for grav k=01, 750 -750 GeV , EBEE;p_{t,#gamma#gamma} (GeV);fraction of |z_{reco}-z_{gen}| < 1 cm",16,bins);
//TH1D* histo=new TH1D("signal_vtx","signal_vtx",n*0.1, 0.,1500.);
	int i=0;
for(int ev=0;ev< n;ev++){
	tree->GetEntry(ev);
	TLorentzVector p1;
	TLorentzVector p2;
	p1.SetPtEtaPhiM(leadPt,leadEta,leadPhi,0.);
	p2.SetPtEtaPhiM(subleadPt,subleadEta,subleadPhi,0.);
	diphopt=(p1+p2).Pt();
	double diff=abs(recoVtx-genVtxZ);
	double passed=0.;
	if (diff < 1.){
	//	histo->Fill(diphopt);	
		i++;	
	}
	passed= diff < 1.;
	eff->Fill(passed,diphopt);
}

std::cout << "eff " << i/double(n) << std::endl;
cout << "error low " << eff->GetEfficiencyErrorLow(1) << endl;
cout << "error high " << eff->GetEfficiencyErrorUp(1) << endl;
/*TCanvas* c1 = new TCanvas("c1","c1",200,10,700,500);
c1->cd();
eff->SetLineColor(kRed);
eff->Draw("AP");
eff->SetMarkerColor(kRed);
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_750_overall_EBEE.png");
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_750_overall_EBEE.root");
//c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_allmasses_EBEE.png");
//c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_allmasses_EBEE.root");
*/
}
