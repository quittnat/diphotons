#!/bin/bash

set -x

version=v11
#######for jets
##output=full_analysis_spring15_7415v2_sync_v11_730_790_min2Jets
##cut30='(nJets30 >1 && mass > 730 && mass < 790)'
##cut60='(nJets60 >1 && mass > 730. && mass < 790.)'
##cut301='(nJets30 >0 && mass > 730. && mass < 790.)'

fudge=1.4
minmass=30.
maxmass=340.
maxmass2=3000.
ptmax1=2000.
ptmax2=200.
#output=full_analysis_spring15_7415v2_sync_v11_790_Inf_min2Jets
#cut30='(nJets30 >1 && mass > 790.)'
#cut60='(nJets60 >1 && mass > 790.)'
#cut301='(nJets30 >0 && mass > 790.)'

output=full_analysis_spring15_7415v2_sync_v11_0_730_min2Jets
cut30='(nJets30 >1 && mass < 730.)'
cut60='(nJets60 >1 && mass < 730.)'
cut301='(nJets30 >0 && mass < 730.)'
#output=full_analysis_spring15_7415v2_sync_v11_500_730_min2Jets
#cut30='(nJets30 >1 && mass > 500. && mass < 730.)'
#cut60='(nJets60 >1 && mass > 500. && mass < 730.)'
mkdir $output

##./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
##    --process GGJets\*EB\* \
##    --process GJets\*EB\* \
##    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
##	--prescale GGJets\*EB\*:10 \
##	--cut "$cut30" \
##  	--histograms "abs(jet2Eta-jet1Eta)>>deltaEta(8,0.0,4.0)" \
 ##   --histograms "mht30CleanMass>>mht30CleanMass(10,$minmass,$maxmass)" \
 ##   --histograms "dijet30CleanMass>>dijet30CleanMass(5,$minmass,$maxmass)" \
 ##   --histograms "mht30Mass>>mht30Mass(10,0.,$maxmass2)" \
 ##   --histograms "(rapidity-(jet2Eta+jet1Eta)/2.)>>diffrap(6,-3.,3.)" \
 ##   --histograms "jet2Pt>>jet2Pt(5,0.,$ptmax2)" \
 ##   --histograms "jet2Eta>>jet2Eta(5,-2.5,2.5)" \
 ##   --histograms "jet2Phi>>jet2Phi(5,-3.2,3.2)" \
  ##  --output $output/output_mc30_EBEB.root 
  ##
  ##  
  ##  ./auto_plotter.py --selection cic \
  ## --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
  ## --process Data\*EB\* \
  ##  --cut "$cut30"\
 ## 	--histograms "abs(jet2Eta-jet1Eta)>>deltaEta(8,0.0,4.0)" \
 ##   --histograms "mht30CleanMass>>mht30CleanMass(10,$minmass,$maxmass)" \
 ##   --histograms "dijet30CleanMass>>dijet30CleanMass(5,$minmass,$maxmass)" \
 ##   --histograms "mht30Mass>>mht30Mass(10,0.,$maxmass2)" \
 ##   --histograms "(rapidity-(jet2Eta+jet1Eta)/2.)>>diffrap(6,-3.,3.)" \
 ##   --histograms "jet2Pt>>jet2Pt(5,0.,$ptmax2)" \
 ##   --histograms "jet2Eta>>jet2Eta(5,-2.5,2.5)" \
##    --histograms "jet2Phi>>jet2Phi(5,-3.2,3.2)" \
##    --output $output/output_data30_EBEB.root 

	./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EB\* \
    --process GJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EB\*:10 \
	--cut "$cut301" \
    --histograms "jet1Pt>>jet1Pt(100,0.,$ptmax1)" \
    --histograms "jet1Eta>>jet1Eta(25,-2.5,2.5)" \
    --histograms "jet1Phi>>jet1Phi(5,-3.2,3.2)" \
    --output $output/output_mc30_1_EBEB.root 
	
	./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   --process Data\*EB\* \
	--cut "$cut301"\
    --histograms "jet1Pt>>jet1Pt(100,0.,$ptmax1)" \
    --histograms "jet1Eta>>jet1Eta(25,-2.5,2.5)" \
    --histograms "jet1Phi>>jet1Phi(5,-3.2,3.2)" \
    --output $output/output_data30_1_EBEB.root 


 ##./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
 ##   --process GGJets\*EB\* \
 ##   --process GJets\*EB\* \
 ##   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicGenIso:cic,cicNonGenIso:cic \
 ##   --prescale GGJets\*EB\*:10 \
 ##   --cut "$cut60" \
 ##   --histograms "mht60CleanMass>>mht60CleanMass(10,$minmass,$maxmass)" \
  ##  --histograms "dijet60CleanMass>>dijet60CleanMass(5,$minmass,$maxmass)" \
  ##  --histograms "mht60Mass>>mht60Mass(10,0.,$maxmass2)" \
  ##  --output $output/output_mc60_EBEB.root 
  ##
  ##  
  ##  ./auto_plotter.py --selection cic \
  ## --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11_data/output.root \
   ##--process Data\*EB\* \
   ## --cut "$cut60"\
   ## --histograms "mht60CleanMass>>mht60CleanMass(10,$minmass,$maxmass)" \
   ## --histograms "dijet60CleanMass>>dijet60CleanMass(5,$minmass,$maxmass)" \
   ## --histograms "mht60Mass>>mht60Mass(10,0.,$maxmass2)" \
   ## --output $output/output_data60_EBEB.root 
   ##


#hadd -f $output/output.root $output/output_data30_1_EBEB.root $output/output_mc30_1_EBEB.root  $output/output_data30_EBEB.root $output/output_mc30_EBEB.root  $output/output_data60_EBEB.root $output/output_mc60_EBEB.root 
hadd -f $output/output.root $output/output_data30_1_EBEB.root $output/output_mc30_1_EBEB.root  
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/$output/ --input-dir $output --fudge $fudge 
