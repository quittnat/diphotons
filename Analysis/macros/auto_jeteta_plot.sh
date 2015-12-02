#!/bin/bash

set -x


#######for jets
##output=full_analysis_spring15_7415v2_sync_v9_730_790_deltaEta
##cut='(nJets30 >3 && mass > 730 && mass < 790)'
##fudge=4.5

fudge=1.4
##output=full_analysis_spring15_7415v2_sync_v9_790_Inf_deltaEta
##cut='(nJets30 >3 && mass > 790.)'

output=full_analysis_spring15_7415v2_sync_v9_0_730_deltaEta
cut='(nJets30 >3 && mass < 730.)'
mkdir $output



./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EB\* \
    --process GJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EB\*:10 \
	--cut "$cut" \
  	--histograms "abs(jet4Eta-jet3Eta)>>deltaEta(10,0.0,5.0)" \
  	--histograms "abs(jet1Eta-jet2Eta)-abs(jet4Eta-jet3Eta)>>diffdeltaEta(10,0.0,5.0)" \
    --output $output/output_mc_EBEB.root 

	
	./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9_data/output.root \
   --process Data\*EB\* \
	--cut "$cut"\
  	--histograms "abs(jet4Eta-jet3Eta)>>deltaEta(10,0.0,5.0)" \
  	--histograms "abs(jet1Eta-jet2Eta)-abs(jet4Eta-jet3Eta)>>diffdeltaEta(10,0.0,5.0)" \
    --output $output/output_data_EBEB.root 



hadd -f $output/output.root $output/output_data_EBEB.root $output/output_mc_EBEB.root  
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/$output/ --input-dir $output --lumi 2.45 --fudge $fudge 
