{
int n=8;
double mass[8]={750.,1000.,1250.,2000.,2750.,3000.,4000.,5000.};
//double mass[8]={750./2,1000./2,1250./2,2000./2,2750./2,3000./2,4000./2,5000./2};
double masserr[8]={0.,0.,0.,0.,0.,0.,0.,0.};
//EBEB
//double efficiency[8]={0.883823, 0.885289,0.882275,0.875332,0.86184  ,0.857412  ,0.834641 ,0.805769    };
//double errLow[8]={0.00256831 ,0.00171941 ,0.00166167 ,0.0017804 ,0.00150539 ,0.00151185 ,0.0015159 ,0.0015615     };
//double errHigh[8]={0.0025205 ,0.00169745 ,0.00164174 ,0.00175903 ,0.00149183 ,0.00149868 ,0.0015049 ,0.00155208  };
//EBEE
double efficiency[8]={0.900259,0.902868  ,0.903249 ,0.907958  ,0.917386 ,0.910481 ,0.906623 ,0.892919  };
double errLow[8]={0.0029139 ,0.00207321 ,0.00208992 ,0.00274934 ,0.00267839 ,0.00294537 ,0.00366892 ,0.00473816  };
double errHigh[8]={0.00284123 ,0.00203489 ,0.00205082 ,0.00267857 ,0.00260289,0.00286191,0.00354646 ,0.0045645   };

TGraphAsymmErrors* eff=new TGraphAsymmErrors(n,mass,efficiency,masserr,masserr,errLow,errHigh);
TCanvas* c1 = new TCanvas("c1","c1",200,10,700,500);
c1->cd();
eff->SetLineColor(kRed);
eff->SetLineWidth(2);
eff->SetMarkerColor(kRed);
eff->SetMarkerStyle(1);
eff->Draw("AP");
eff->SetTitle("vtx efficiency for graviton k=01, EBEE");
eff->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
eff->GetYaxis()->SetTitle("fraction of |z_{reco}-z_{gen}| < 1 cm");
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/overall_eff_vs_mass_grav01_EBEE.png");
c1->SaveAs("/afs/cern.ch/user/m/mquittna/www/diphoton/signalvtxEfficiency/overall_eff_vs_mass_grav01_EBEE.root");
}
