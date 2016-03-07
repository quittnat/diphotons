{
 ifstream infiletau("upcrossing_k001_l_0_5.txt",ios::in);
 if(!infiletau.is_open()){
   cout<<"No upcrossing_k001_l_0_5.txt file to open!"<<endl;
   return -1;
 }

 double dum;
 double entries=100.;
 char sline[100];
 TH1D* trials=new TH1D("trials","trials",15,40.,140.);
 for (i=0;i<entries;i++){
 	infiletau.getline(sline,256);
 	sscanf(sline, "%lf",&dum);
//	cout << dum << endl;
	trials->Fill(dum);
 }
	TCanvas * ctrials = new TCanvas("ctrials","ctrials");
	ctrials->cd(1);
	gStyle->SetOptStat(1111111);
	TLegend* leg= new TLegend(0.5,0.8,0.9,0.9);
    trials->GetYaxis()->SetTitle("#");
	trials->Draw("HIST");
    trials->GetXaxis()->SetTitle("trial number");
    trials->SetTitle("trial number for k001 and level for upcrossings 0.5");
//leg->Draw();

	ctrials->SaveAs(Form("/afs/cern.ch/user/m/mquittna/www/diphoton/LEE/trial_k001_l_0_5.png"));
	
}

	    
