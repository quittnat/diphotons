#!/bin/bash

set -x
##fudge=4.5
fudge=1.4

version=v11
##output=full_analysis_spring15_7415v2_sync_v11_EBEE_0_630
##cutleadEE='( mass <630 && abs(leadScEta) > 1.5 )'
##cutsubleadEE='( mass <630 && abs(subleadScEta) > 1.5 )'
##cutleadEB='( mass <630 && abs(leadScEta) <= 1.5 )'
##cutsubleadEB='( mass <630 && abs(subleadScEta) <= 1.5 )'
output=full_analysis_spring15_7415v2_sync_v11_EBEE_500_630
cutleadEE='( mass> 500. && mass <630 && abs(leadScEta) > 1.5 )'
cutsubleadEE='( mass > 500 && mass <630 && abs(subleadScEta) > 1.5 )'
cutleadEB='(mass > 500 &&  mass <630 && abs(leadScEta) <= 1.5 )'
cutsubleadEB='(mass > 500 &&  mass <630 && abs(subleadScEta) <= 1.5 )'
##output=full_analysis_spring15_7415v2_sync_v11_EBEE_630_790
##cutleadEE='( mass> 630. && mass <790 && abs(leadScEta) > 1.5 )'
##cutsubleadEE='( mass > 630 && mass <790 && abs(subleadScEta) > 1.5 )'
##cutleadEB='(mass > 630 &&  mass <790 && abs(leadScEta) <= 1.5 )'
##cutsubleadEB='(mass > 630 &&  mass < 790 && abs(subleadScEta) <= 1.5 )'
ptmax1=2000.
ptmax2=2000.
##output=full_analysis_spring15_7415v2_sync_v11_EBEE_790_Inf
##cutleadEE='( mass > 790 && abs(leadScEta) > 1.5 )'
##cutsubleadEE='( mass > 790 && abs(subleadScEta) > 1.5 )'
##cutleadEB='( mass > 790 && abs(leadScEta) <= 1.5 )'
##cutsubleadEB='( mass > 790 && abs(subleadScEta) <= 1.5 )'
mkdir $output

## merge MC
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EB\* \
    --process GJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EB\*:10 \
	--cut "$cutleadEB" \
    --histograms "leadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "leadEta>>Eta(50,-2.5,2.5)" \
    --histograms "leadPhi>>Phi(64,-3.2,3.2)" \
    --output $output/output_mc_leadEB.root 

  ##data merge in Data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   --process Data\*EB\* \
	--cut "$cutleadEB"\
    --histograms "leadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "leadEta>>Eta(50,-2.5,2.5)" \
    --histograms "leadPhi>>Phi(64,-3.2,3.2)" \
   --output $output/output_data_leadEB.root 

   ./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EB\* \
    --process GJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EB\*:10 \
	--cut "$cutsubleadEB" \
    --histograms "subleadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "subleadEta>>Eta(50,-2.5,2.5)" \
    --histograms "subleadPhi>>Phi(64,-3.2,3.2)" \
    --output $output/output_mc_subleadEB.root 

  ##data merge in Data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   --process Data\*EB\* \
	--cut "$cutsubleadEB"\
    --histograms "subleadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "subleadEta>>Eta(50,-2.5,2.5)" \
    --histograms "subleadPhi>>Phi(64,-3.2,3.2)" \
   --output $output/output_data_subleadEB.root 

   ./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EE\* \
    --process GJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EE\*:10 \
	--cut "$cutleadEE" \
    --histograms "leadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "leadEta>>Eta(50,-2.5,2.5)" \
    --histograms "leadPhi>>Phi(64,-3.2,3.2)" \
    --output $output/output_mc_leadEE.root 

  ##data merge in Data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   --process Data\*EE\* \
	--cut "$cutleadEE"\
    --histograms "leadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "leadEta>>Eta(50,-2.5,2.5)" \
    --histograms "leadPhi>>Phi(64,-3.2,3.2)" \
   --output $output/output_data_leadEE.root 

   ./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EE\* \
    --process GJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EE\*:10 \
	--cut "$cutsubleadEE" \
    --histograms "subleadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "subleadEta>>Eta(50,-2.5,2.5)" \
    --histograms "subleadPhi>>Phi(64,-3.2,3.2)" \
    --output $output/output_mc_subleadEE.root 

  ##data merge in Data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   --process Data\*EE\* \
	--cut "$cutsubleadEE"\
    --histograms "subleadPt>>Pt(100,75.,$ptmax1)" \
    --histograms "subleadEta>>Eta(50,-2.5,2.5)" \
    --histograms "subleadPhi>>Phi(64,-3.2,3.2)" \
   --output $output/output_data_subleadEE.root 

hadd -f $output/output.root $output/output_data_leadEB.root $output/output_mc_leadEB.root $output/output_data_subleadEB.root $output/output_mc_subleadEB.root $output/output_data_leadEE.root $output/output_mc_leadEE.root $output/output_data_subleadEE.root $output/output_mc_subleadEE.root 
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/$output/ --input-dir $output  --fudge $fudge --lumi 2.44 

