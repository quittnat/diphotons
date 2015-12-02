#!/bin/bash

set -x

##output=full_analysis_spring15_7415v2_sync_v9_730_790
##cut='(mass > 730 && mass < 790)'
##fudge=4.5
fudge=1.4
##output=full_analysis_spring15_7415v2_sync_v9_790_Inf
##cut='(mass > 790.)'

output=full_analysis_spring15_7415v2_sync_v9_0_730
cut='(mass < 730.)'

mkdir $output



## merge MC
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EB\* \
    --process GJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EB\*:10 \
	--cut "$cut" \
    --histograms "dijet30CleanMass>>dijet30Mass(100,0.,3000.)" \
    --histograms "dijet60CleanMass>>dijet60Mass(100,0.,3000.)" \
    --histograms "mht30CleanMass>>mht30CleanMass(100,0.,3000.)" \
    --histograms "mht30Mass>>mht30Mass(100,0.,3000.)" \
    --histograms "mht60CleanMass>>mht60CleanMass(100,0.,3000.)" \
    --histograms "mht60Mass>>mht60Mass(100,0.,3000.)" \
    --histograms "nJets30-2>>nJets30(6,-0.5,5.5)" \
    --histograms "nJets60-2>>nJets60(6,-0.5,5.5)" \
    --output $output/output_mc_EBEB.root 



  ##data merge in Data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9_data/output.root \
   --process Data\*EB\* \
	--cut "$cut"\
   --histograms "dijet30CleanMass>>dijet30Mass(100,0.,3000.)" \
   --histograms "dijet60CleanMass>>dijet60Mass(100,0.,3000.)" \
   --histograms "mht30CleanMass>>mht30CleanMass(100,0.,3000.)" \
   --histograms "mht30Mass>>mht30Mass(100,0.,3000.)" \
   --histograms "mht60CleanMass>>mht60CleanMass(100,0.,3000.)" \
   --histograms "mht60Mass>>mht60Mass(100,0.,3000.)" \
   --histograms "nJets30-2>>nJets30(6,-0.5,5.5)" \
   --histograms "nJets60-2>>nJets60(6,-0.5,5.5)" \
   --output $output/output_data_EBEB.root 

hadd -f $output/output.root $output/output_data_EBEB.root $output/output_mc_EBEB.root  
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/$output/ --input-dir $output --lumi 2.45 --fudge $fudge 
