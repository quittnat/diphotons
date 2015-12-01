{
//TNtuple* tree=tree_grav_01_750_cic2_EBEB;
TNtuple* tree=tree_grav_01_allmasses_cic2_EBEB;


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
double bins[17]={0.,50.,100.,150.,200.,250.,300.,350.,400.,450.,500.,550.,600.,700.,800.,1000.,1500.};
// TEfficiency*eff = new TEfficiency("histo","vtx efficiency for grav k=01, 750 GeV, EBEB;p_{t,#gamma#gamma} (GeV);fraction of |z_{reco}-z_{gen}| < 1 cm",16,bins);
 TEfficiency*eff = new TEfficiency("histo","vtx efficiency for grav k=01, 750 -5000 GeV , EBEB;p_{t,#gamma#gamma} (GeV);fraction of |z_{reco}-z_{gen}| < 1 cm",16,bins);
//TH1D* histo=new TH1D("signal_vtx","signal_vtx",n*0.1, 0.,1500.);
for(int ev=0;ev< n;ev++){
	tree->GetEntry(ev);
	TLorentzVector p1;
	TLorentzVector p2;
	p1.SetPtEtaPhiM(leadPt,leadEta,leadPhi,0.);
	p2.SetPtEtaPhiM(subleadPt,subleadEta,subleadPhi,0.);
	diphopt=(p1+p2).Pt();
	double diff=abs(recoVtx-genVtxZ);
	double passed=0.;
//	if (diff < 1.){
	//	histo->Fill(diphopt);		
//	}
	passed= diff < 1.;
	eff->Fill(passed,diphopt);
}
TCanvas* c1 = new TCanvas("c1","c1",200,10,700,500);
c1->cd();
eff->SetLineColor(kRed);
eff->Draw("AP");
eff->SetMarkerColor(kRed);
//c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_750_EBEB.png");
//c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_750_EBEB.root");
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_allmasses_EBEB.png");
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/vtxeff_grav01_allmasses_EBEB.root");
}
