#!/bin/bash

set -x
##fudge=4.5
fudge=1.4

version=v11
##output=full_analysis_spring15_7415v2_sync_v11_0_730
##cut='(mass < 730.)'
##output=full_analysis_spring15_7415v2_sync_v11_500_730
##cut='(mass > 500 && mass < 730.)'
output=full_analysis_spring15_7415v2_sync_v11_730_790
cut='(mass > 730 && mass < 790)'
ptmax1=2000.
ptmax2=2000.
##output=full_analysis_spring15_7415v2_sync_v11_790_Inf
##cut='(mass > 790.)'
mkdir $output



## merge MC
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EB\* \
    --process GJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EB\*:10 \
	--cut "$cut" \
    --histograms "mht30Mass>>mht30Mass(300,0.,3000.)" \
    --histograms "mht60Mass>>mht60Mass(300,0.,3000.)" \
    --histograms "nJets30>>nJets30(6,-0.5,5.5)" \
    --histograms "nJets60>>nJets60(6,-0.5,5.5)" \
    --histograms "leadPt>>leadPt(100,75.,$ptmax1)" \
    --histograms "leadEta>>leadEta(50,-2.5,2.5)" \
    --histograms "leadPhi>>leadPhi(64,-3.2,3.2)" \
    --histograms "subleadPt>>subleadPt(100,0.,$ptmax2)" \
    --histograms "subleadEta>>subleadEta(50,-2.5,2.5)" \
    --histograms "subleadPhi>>subleadPhi(64,-3.2,3.2)" \
    --output $output/output_mc_EBEB.root 



  ##data merge in Data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   --process Data\*EB\* \
	--cut "$cut"\
   --histograms "mht30Mass>>mht30Mass(300,0.,3000.)" \
   --histograms "mht60Mass>>mht60Mass(300,0.,3000.)" \
   --histograms "nJets30>>nJets30(6,-0.5,5.5)" \
   --histograms "nJets60>>nJets60(6,-0.5,5.5)" \
   --histograms "leadPt>>leadPt(100,75.,$ptmax1)" \
   --histograms "leadEta>>leadEta(50,-2.5,2.5)" \
   --histograms "leadPhi>>leadPhi(64,-3.2,3.2)" \
   --histograms "subleadPt>>subleadPt(100,0.,$ptmax2)" \
   --histograms "subleadEta>>subleadEta(50,-2.5,2.5)" \
   --histograms "subleadPhi>>subleadPhi(64,-3.2,3.2)" \
   --output $output/output_data_EBEB.root 

hadd -f $output/output.root $output/output_data_EBEB.root $output/output_mc_EBEB.root  
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/$output/ --input-dir $output  --fudge $fudge --lumi 2.44 
