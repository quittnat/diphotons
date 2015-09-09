{

	
TFile *f = TFile::Open("full_analysis_anv1_v19_2D_final_ws.root");
gStyle->SetOptStat(1111111);
TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/fakerate_studies/";
const int mbins=6;
const int mbin=25;
Double_t mstart=100.;
Double_t mend=5000.;
//double ptbins[mbins]={100.,150.,200.,250.,300.,400.,500.,700.,1000.,3000.,8000.};
double ptbins[mbins]={100.,300.,500.,1000.,3000.,8000.};
int nbins=10;
double sEB=0.012;
TH1::SetDefaultSumw2();

TCanvas* ccomp=new TCanvas("ccomp_EB","ccomp_EB",1000,500);
//TH1D* ratio=new TH1D("ratio","ratio",mbin,mstart,mend);
TH1D* ratio=new TH1D("ratio","ratio",mbins-1,ptbins);
ratio->SetLineColor(kRed);
ratio->SetLineWidth(2);
//TH1D* pfmctruth=new TH1D("pfmctruth","pfmctruth",mbin,mstart,mend);
TH1D* pfmctruth=new TH1D("pfmctruth","pfmctruth",mbins-1,ptbins);
pfmctruth->SetLineColor(kRed);
pfmctruth->SetLineWidth(2);
TH1D* pftemplate0=new TH1D("pftemplate0","pftemplate0",mbins-1,ptbins);
//TH1D* pftemplate0=new TH1D("pftemplate0","pftemplate0",mbin,mstart,mend);
pftemplate0->SetLineColor(kBlue);
pftemplate0->SetLineWidth(2);
ccomp->Divide(2,1);
ccomp->cd(1);
gPad->SetLogx();
gPad->SetLogy();

tree_mctruth_f_singlePho_EB->Draw("phoPt>>pfmctruth","weight","  norm  ");
//pfmctruth->GetXaxis()->SetRangeUser(10.,7000.);
//pfmctruth->GetYaxis()->SetRangeUser(0.001,0.6);
tree_template_f_singlePho_EB->Draw("phoPt>>pftemplate0","weight"," same norm  ");

TLegend* leg = new TLegend(0.45, 0.75, .7, .9);
leg->SetFillColor(0);
leg->AddEntry(pfmctruth,"f mctruth" ,"l");
leg->AddEntry(pftemplate0,"f sideband" ,"l");
leg->Draw();
ccomp->cd(2);
gPad->SetLogx();
TH1::SetDefaultSumw2();
ratio->Divide(pftemplate0,pfmctruth);
ratio->GetYaxis()->SetRangeUser(-0.1,3.);
ratio->GetYaxis()->SetTitle("fsb/fmctruth");
ratio->Draw();
ccomp->SaveAs(Form("%sccomp5b_EB.png",dir.Data()));
ccomp->SaveAs(Form("%sccomp5b_EB.root",dir.Data()));

TCanvas* ccomp2=new TCanvas("ccomp_EE","ccomp_EE",1000,500);
//TH1D* ratio=new TH1D("ratio","ratio",mbin,mstart,mend);
TH1D* ratio2=new TH1D("ratio2","ratio2",mbins-1,ptbins);
ratio2->SetLineColor(kRed);
ratio2->SetLineWidth(2);
//TH1D* pfmctruth=new TH1D("pfmctruth","pfmctruth",mbin,mstart,mend);
TH1D* pfmctruth2=new TH1D("pfmctruth2","pfmctruth2",mbins-1,ptbins);
pfmctruth2->SetLineColor(kRed);
pfmctruth2->SetLineWidth(2);
TH1D* pftemplate02=new TH1D("pftemplate02","pftemplate02",mbins-1,ptbins);
//TH1D* pftemplate0=new TH1D("pftemplate0","pftemplate0",mbin,mstart,mend);
pftemplate02->SetLineColor(kBlue);
pftemplate02->SetLineWidth(2);
ccomp2->Divide(2,1);
ccomp2->cd(1);
gPad->SetLogx();
gPad->SetLogy(); 

tree_mctruth_f_singlePho_EE->Draw("phoPt>>pfmctruth2","weight","  norm  ");
//pfmctruth->GetXaxis()->SetRangeUser(10.,7000.);
//pfmctruth->GetYaxis()->SetRangeUser(0.001,0.6);
tree_template_f_singlePho_EE->Draw("phoPt>>pftemplate02","weight"," same norm  ");

TLegend* leg2 = new TLegend(0.45, 0.75, .7, .9);
leg2->SetFillColor(0);
leg2->AddEntry(pfmctruth2,"f mctruth" ,"l");
leg2->AddEntry(pftemplate02,"f sideband" ,"l");
leg2->Draw();
ccomp2->cd(2);
gPad->SetLogx();
ratio2->Divide(pftemplate02,pfmctruth2);
ratio2->GetYaxis()->SetRangeUser(-0.1,3.);
ratio2->GetYaxis()->SetTitle("fsb/fmctruth");
ratio2->Draw();
ccomp2->SaveAs(Form("%sccomp5b_EE.png",dir.Data()));
ccomp2->SaveAs(Form("%sccomp5b_EE.root",dir.Data()));

TCanvas* ccomp3=new TCanvas("ccomp_pf_EE","ccomp_pf_EE",1000,500);
gPad->SetLogx();
gPad->SetLogy();
TH1D* fsubleadPt=new TH1D("fsubleadPt","fsubleadPt",mbins-1,ptbins);
fsubleadPt->SetLineColor(kRed);
TH1D* fleadPt=new TH1D("fleadPt","fleadPt",mbins-1,ptbins);
fleadPt->SetLineColor(kBlue);
TH1D* diphoPt=new TH1D("diphoPt","diphoPt",mbins-1,ptbins);
diphoPt->SetLineColor(kGreen+1);
TH1D* fsubleadPtTruth=new TH1D("fsubleadPtTruth","fsubleadPtTruth",mbins-1,ptbins);
fsubleadPtTruth->SetLineColor(kRed);
fsubleadPtTruth->SetLineStyle(2);
TH1D* fleadPtTruth=new TH1D("fleadPtTruth","fleadPtTruth",mbins-1,ptbins);
fleadPtTruth->SetLineColor(kBlue);
fleadPtTruth->SetLineStyle(2);
TH1D* diphoPtTruth=new TH1D("diphoPtTruth","diphoPtTruth",mbins-1,ptbins);
diphoPtTruth->SetLineColor(kGreen+1);
diphoPtTruth->SetLineStyle(2);
tree_template_pf_2D_EBEE->Draw("subleadPt>>fsubleadPt","weight*(subleadSigmaIeIe>= 0.035)","norm");
tree_template_pf_2D_EBEE->Draw("leadPt>>fleadPt","weight*(leadSigmaIeIe>= 0.035)","same norm");
tree_template_pf_2D_EBEE->Draw("mgg>>diphoPt","weight","same norm");
tree_mctruth_pf_2D_EBEE->Draw("leadPt>>fleadPtTruth","weight","same norm");
tree_mctruth_pf_2D_EBEE->Draw("subleadPt>>fsubleadPtTruth","weight*(subleadMatchType>0)","same norm");
tree_mctruth_pf_2D_EBEE->Draw("mgg>>diphoPtTruth","weight","same norm");
TLegend* leg3 = new TLegend(0.45, 0.75, .7, .9);
leg3->SetFillColor(0);
leg3->AddEntry(fsubleadPtTruth,"f sublead mctruth" ,"l");
leg3->AddEntry(fleadPtTruth,"f lead mctruth" ,"l");
leg3->AddEntry(fsubleadPt,"f sublead" ,"l");
leg3->AddEntry(fleadPt,"f lead" ,"l");
leg3->AddEntry(diphoPtTruth,"mgg mctruth" ,"l");
leg3->AddEntry(diphoPt,"mgg" ,"l");
leg3->Draw();
ccomp3->SaveAs(Form("%sccomppf_EBEE.png",dir.Data()));
ccomp3->SaveAs(Form("%sccomppf_EBEE.root",dir.Data()));

}	
