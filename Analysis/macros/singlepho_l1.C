{
TFile *_file0 = TFile::Open("templates_spring16v1_singlepho_l1match.root");
TNtuple* tree=tree_data_singlePho_EB;
Float_t phoPt=0.;
Float_t phoL1EgmMatch=0.;
Float_t phoL1EgmPt=0.;
Float_t phoL1EgmDr=0.;
tree->SetBranchAddress("phoPt",&phoPt);
tree->SetBranchAddress("phoL1EgmMatch",&phoL1EgmMatch);
tree->SetBranchAddress("phoL1EgmPt",&phoL1EgmPt);
tree->SetBranchAddress("phoL1EgmDr",&phoL1EgmDr);
int n=tree->GetEntries();
double bins[17]={0.,50.,100.,150.,200.,250.,300.,350.,400.,450.,500.,550.,600.,700.,800.,1000.,1500.};
TEfficiency* eff = new TEfficiency("histo","L1 Egm efficiency for EB",16,bins);
int i=0;
for(int ev=0;ev< n;ev++){
	tree->GetEntry(ev);
	double passed=0.;
	if (phoL1EgmMatch == 1.){
		i++;	
	}
	passed= (phoL1EgmMatch == 1.);
	eff->Fill(passed,phoPt);
}

std::cout << "eff " << i/double(n) << std::endl;
//cout << "error low " << eff->GetEfficiencyErrorLow(1) << endl;
//cout << "error high " << eff->GetEfficiencyErrorUp(1) << endl;
TCanvas* c1 = new TCanvas("c1","c1",200,10,700,500);
c1->cd();
eff->SetLineColor(kRed);
eff->Draw("AP");
eff->SetTitle("L1 EgmMatch EB");
eff->SetMarkerColor(kBlue);
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/spring16/singlePho/l1EgmMatch_pt_EB.png");
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/spring16/singlePho/l1EgmMatch_pt_EB.root");
}
