{

	
TFile *f = TFile::Open("full_analysis_anv1_v19_2D_final_ws.root");
gStyle->SetOptStat(1111111);
TString dir="/afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/checksForFit/";
const int mbins=6;
const int mbin=50;
Double_t mstart=300.;
double massbins[mbins]={300.,322.,352.,396.,481.,7000.};
int nbins=10;
double sEB=0.012;
TH1::SetDefaultSumw2();

TCanvas* ccomp=new TCanvas("ccomp_EBEB","ccomp_EBEB",1000,500);
//TH1D* pfmctruth=new TH1D("pfmctruth","pfmctruth",5,massbins);
//TH1D* ratio=new TH1D("ratio","ratio",5,massbins);
TH1D* ratio=new TH1D("ratio","ratio",mbin,mstart,7000.);
ratio->SetLineColor(kRed);
ratio->SetLineWidth(2);
TH1D* pfmctruth=new TH1D("pfmctruth","pfmctruth",mbin,mstart,7000.);
pfmctruth->SetLineColor(kRed);
pfmctruth->SetLineWidth(2);
//TH1D* pftemplate0=new TH1D("pftemplate0","pftemplate0",5,massbins);
TH1D* pftemplate0=new TH1D("pftemplate0","pftemplate0",mbin,mstart,7000.);
pftemplate0->SetLineColor(kBlue);
pftemplate0->SetLineStyle(2);
pftemplate0->SetLineWidth(2);
//TH1D* pftemplate1=new TH1D("pftemplate1","pftemplate1",5,massbins);
TH1D* pftemplate01=new TH1D("pftemplate1","pftemplate1",mbin,mstart,7000.);
pftemplate1->SetLineColor(kGreen+2);
pftemplate1->SetLineWidth(2);
//TH1D* pftemplate2=new TH1D("pftemplate2","pftemplate2",5,massbins);
TH1D* pftemplate2=new TH1D("pftemplate2","pftemplate2",mbin,mstart,7000.);
pftemplate2->SetLineColor(kYellow+1);
pftemplate2->SetLineWidth(2);
/*
TH1D* pftemplatemix0=new TH1D("pftemplatemix0","pftemplatemix0",5,massbins);
pftemplatemix0->SetLineColor(kGreen);
pftemplatemix0->SetLineStyle(2);
TH1D* pftemplatemix1=new TH1D("pftemplatemix1","pftemplatemix1",5,massbins);
pftemplatemix1->SetLineColor(kGreen+1);
TH1D* pftemplatemix2=new TH1D("pftemplatemix2","pftemplatemix2",5,massbins);
pftemplatemix2->SetLineColor(kGreen+3);
*/
ccomp->Divide(2,1);
ccomp->cd(1);
gPad->SetLogx();
gPad->SetLogy();

tree_mctruth_pf_2D_EBEB->Draw("mgg>>pfmctruth","weight","  norm  ");
//pfmctruth->GetXaxis()->SetRangeUser(10.,7000.);
//pfmctruth->GetYaxis()->SetRangeUser(0.001,0.6);
tree_template_pf_2D_EBEB->Draw("mgg>>pftemplate1","weight*(leadSigmaIeIe >= 0.017 || subleadSigmaIeIe >= 0.017)"," same norm  ");
tree_template_pf_2D_EBEB->Draw("mgg>>pftemplate2","weight*(leadSigmaIeIe < 0.017  &&  subleadSigmaIeIe < 0.017)"," same norm  ");
tree_template_pf_2D_EBEB->Draw("mgg>>pftemplate0","weight","same norm");
//tree_template_mix_pf_kDSinglePho2D_EBEB->Draw("mgg>>pftemplatemix1","weight"," same norm ");
//tree_template_mix_pf_kDSinglePho2D_EBEB->Draw("mgg>>pftemplatemix2","weight*(leg1SigmaIeIe < 0.017 && leg2SigmaIeIe < 0.017)","same norm ");
//tree_template_mix_pf_kDSinglePho2D_EBEB->Draw("mgg>>pftemplatemix0","weight","same norm ");

TLegend* leg = new TLegend(0.45, 0.75, .7, .9);
leg->SetFillColor(0);
leg->AddEntry(pfmctruth,"pf mctruth" ,"l");
leg->AddEntry(pftemplate0,"pf template all sieie" ,"l");
//leg->AddEntry(pftemplatemix0,"pf template_mix all sieie" ,"l");
leg->AddEntry(pftemplate1,"pf template f > 0.017" ,"l");
leg->AddEntry(pftemplate2,"pf template f < 0.017" ,"l");
//leg->AddEntry(pftemplatemix1,"pf template_mix all f > 0.017" ,"l");
//leg->AddEntry(pftemplatemix2,"pf template_mix all f < 0.017" ,"l");
leg->Draw();
ccomp->cd(2);
gPad->SetLogx();
ratio->Divide(pftemplate0,pfmctruth);
ratio->GetYaxis()->SetRangeUser(-0.01,2.);
ratio->GetYaxis()->SetTitle("pftemplate/pfmctruth");
ratio->Draw();
ccomp->SaveAs(Form("%ssanity_plots/ccomptemp%f_EBEB.png",dir.Data(),mstart));
ccomp->SaveAs(Form("%ssanity_plots/ccomptemp%f_EBEB.root",dir.Data(),mstart));




TCanvas* c1=new TCanvas("ctemplatepf_EBEB","ctemplatepf_EBEB",1000,500);
TH2D* pflead=new TH2D("pflead","pflead",5,massbins,nbins,0.012,0.022);
TH2D* pfsublead=new TH2D("pfsublead","pfsublead",5,massbins,nbins,0.012,0.022);
TH1D* pflead_py=NULL;
TH1D* pfsublead_py=NULL;

c1->Divide(2,3);
c1->cd(1);
gPad->SetLogx();
tree_template_pf_2D_EBEB->Draw("leadSigmaIeIe:mgg>>pflead","weight*(leadSigmaIeIe> 0.012)","colz");
c1->cd(2);
gPad->SetLogx();
tree_template_pf_2D_EBEB->Draw("subleadSigmaIeIe:mgg>>pfsublead","weight*(subleadSigmaIeIe> 0.012)","colz");
c1->cd(3);
gPad->SetLogy();
pflead_py=pflead->ProfileY();
pflead_py->GetYaxis()->SetRangeUser(200.,7000.);
pflead_py->Draw();
c1->cd(4);
gPad->SetLogx();
pflead->ProfileX("pflead_px",0,mbins,"")->Draw();
c1->cd(5);
gPad->SetLogy();
pfsublead_py=pfsublead->ProfileY();
pflead_py->GetYaxis()->SetRangeUser(200.,7000.);
pfsublead_py->Draw();
c1->cd(6);
gPad->SetLogx();
pfsublead->ProfileX("pfsublead_px",0,mbins,"")->Draw();

c1->SaveAs(Form("%ssanity_plots/ctemplatepf_EBEB.png",dir.Data()));
c1->SaveAs(Form("%ssanity_plots/ctemplatepf_EBEB.root",dir.Data()));



TCanvas* c2=new TCanvas("ctemplatepf_EBEE","ctemplatepf_EBEE",1000,500);
double massbins[]={300.,339.,382.,448.,565.,7000.};
TH2D* pflead2=new TH2D("pflead2","pflead2",5,massbins,nbins,0.035,0.06);
TH2D* pfsublead2=new TH2D("pfsublead2","pfsublead2",5,massbins,nbins,0.035,0.06);
TH1D* pflead2_py=NULL;
TH1D* pfsublead2_py=NULL;
c2->Divide(2,3);
c2->cd(1);
gPad->SetLogx();
tree_template_pf_2D_EBEE->Draw("leadSigmaIeIe:mgg>>pflead2","weight*(leadSigmaIeIe>= 0.035)","colz");
c2->cd(2);
gPad->SetLogx();
tree_template_pf_2D_EBEE->Draw("subleadSigmaIeIe:mgg>>pfsublead2","weight*(subleadSigmaIeIe>= 0.035)","colz");
c2->cd(3);
gPad->SetLogy();
pflead2_py=pflead2->ProfileY();
pflead2_py->GetYaxis()->SetRangeUser(200.,7000.);
pflead2_py->Draw();
c2->cd(4);
gPad->SetLogx();
pflead2->ProfileX("pflead2_px",0,mbins,"")->Draw();
c2->cd(5);
gPad->SetLogy();
pfsublead2_py=pfsublead2->ProfileY();
pfsublead2_py->GetYaxis()->SetRangeUser(200.,7000.);
pfsublead2_py->Draw();
c2->cd(6);
gPad->SetLogx();
pfsublead2->ProfileX("pfsublead2_px",0,mbins,"")->Draw();

c2->SaveAs(Form("%ssanity_plots/ctemplatepf_EBEE.png",dir.Data()));
c2->SaveAs(Form("%ssanity_plots/ctemplatepf_EBEE.root",dir.Data()));

}	
