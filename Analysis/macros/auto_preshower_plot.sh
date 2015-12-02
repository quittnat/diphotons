#!/bin/bash

set -x

##output=full_analysis_spring15_7415v2_sync_v9_preshower_fullmass
##cut='(mass > 730 && mass < 790)'
##output=full_analysis_spring15_7415v2_sync_v9_preshower_630_790
##cutlead='(mass > 630 && mass < 790 && abs(leadScEta) > 1.5 )'
##cutsublead='(mass > 630 && mass < 790 && abs(subleadScEta) > 1.5 )'
##output=full_analysis_spring15_7415v2_sync_v9_preshower_0_630
##cutlead='(mass < 630 && abs(leadScEta) > 1.5 )'
##cutsublead='( mass < 630 && abs(subleadScEta) > 1.5 )'
fudge=1.4
output=full_analysis_spring15_7415v2_sync_v9_preshower_780_Inf
cutlead='(mass > 780 && abs(leadScEta) > 1.5 )'
cutsublead='( mass > 780 && abs(subleadScEta) > 1.5 )'

mkdir $output



## merge MC
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EE\* \
    --process GJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EE\*:10 \
	--cut "$cutlead" \
    --histograms "leadcPreshowerEnergyPlane1>>PreshowerEnergyPlane1(50,0.,50.)" \
    --histograms "leadcPreshowerEnergyPlane2>>PreshowerEnergyPlane2(50,0.,50.)" \
    --histograms "leadcPreshowerEnergy>>PreshowerEnergy(50,0.,50.)" \
    --histograms "leadEnergy>>Energy(100,0.,7000.)" \
    --histograms "(leadcPreshowerEnergy/leadEnergy)>>ESEnergy_Energy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergyPlane1/leadEnergy)>>ESEnergyPlane1_Energy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergyPlane2/leadEnergy)>>ESEnergyPlane2_Energy(20,0.,0.04)" \
    --output $output/output_mc_leadEE.root 

  ##data merge in Data
./auto_plotter.py --selection cic \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9_data/output.root \
    --process Data\*EE\* \
	--cut "$cutlead"\
    --histograms "leadcPreshowerEnergyPlane1>>PreshowerEnergyPlane1(50,0.,50.)" \
    --histograms "leadcPreshowerEnergyPlane2>>PreshowerEnergyPlane2(50,0.,50.)" \
    --histograms "leadcPreshowerEnergy>>PreshowerEnergy(50,0.,50.)" \
    --histograms "leadcRawEnergy>>ScRawEnergy(50,0.,1500.)" \
    --histograms "leadEnergy>>Energy(100,0.,7000.)" \
    --histograms "(leadcRawEnergy/leadEnergy)>>RawEnergy_Energy(20,0.8,1.0)" \
    --histograms "(leadcPreshowerEnergyPlane1/leadcRawEnergy)>>ESEnergyPlane1_RawEnergy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergyPlane2/leadcRawEnergy)>>ESEnergyPlane2_RawEnergy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergy/leadEnergy)>>ESEnergy_Energy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergy/leadcRawEnergy)>>ESEnergy_RawEnergy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergyPlane1/leadEnergy)>>ESEnergyPlane1_Energy(20,0.,0.04)" \
    --histograms "(leadcPreshowerEnergyPlane2/leadEnergy)>>ESEnergyPlane2_Energy(20,0.,0.04)" \
   --output $output/output_data_leadEE.root 

  ##sublead   
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    --process GGJets\*EE\* \
    --process GJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9/output.root --move cicGenIso:cic,cicNonGenIso:cic \
	--prescale GGJets\*EE\*:10 \
	--cut "$cutsublead" \
    --histograms "subleadreshowerEnergyPlane1>>PreshowerEnergyPlane1(50,0.,50.)" \
    --histograms "subleadreshowerEnergyPlane2>>PreshowerEnergyPlane2(50,0.,50.)" \
    --histograms "subleadcPreshowerEnergy>>PreshowerEnergy(50,0.,50.)" \
    --histograms "subLeadEnergy>>Energy(100,0.,7000.)" \
    --histograms "(subleadcPreshowerEnergy/subLeadEnergy)>>ESEnergy_Energy(20,0.,0.04)" \
    --histograms "(subleadreshowerEnergyPlane1/subLeadEnergy)>>ESEnergyPlane1_Energy(20,0.,0.04)" \
    --histograms "(subleadreshowerEnergyPlane2/subLeadEnergy)>>ESEnergyPlane2_Energy(20,0.,0.04)" \
    --output $output/output_mc_subleadEE.root 

  ##data merge in Data
./auto_plotter.py --selection cic \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v9_data/output.root \
    --process Data\*EE\* \
	--cut "$cutsublead"\
    --histograms "subleadreshowerEnergyPlane1>>PreshowerEnergyPlane1(50,0.,50.)" \
    --histograms "subleadreshowerEnergyPlane2>>PreshowerEnergyPlane2(50,0.,50.)" \
    --histograms "subleadcPreshowerEnergy>>PreshowerEnergy(50,0.,50.)" \
    --histograms "subleadcRawEnergy>>ScRawEnergy(50,0.,1500.)" \
    --histograms "subLeadEnergy>>Energy(100,0.,7000.)" \
    --histograms "(subleadcPreshowerEnergy/subLeadEnergy)>>ESEnergy_Energy(20,0.,0.04)" \
    --histograms "(subleadcPreshowerEnergy/subleadcRawEnergy)>>ESEnergy_RawEnergy(20,0.,0.04)" \
    --histograms "(subleadreshowerEnergyPlane1/subLeadEnergy)>>ESEnergyPlane1_Energy(20,0.,0.04)" \
    --histograms "(subleadreshowerEnergyPlane2/subLeadEnergy)>>ESEnergyPlane2_Energy(20,0.,0.04)" \
    --histograms "(subleadcRawEnergy/subLeadEnergy)>>RawEnergy_Energy(20,0.8,1.)" \
    --histograms "(subleadreshowerEnergyPlane1/subleadcRawEnergy)>>ESEnergyPlane1_RawEnergy(20,0.,0.04)" \
    --histograms "(subleadreshowerEnergyPlane2/subleadcRawEnergy)>>ESEnergyPlane2_RawEnergy(20,0.,0.04)" \
    --output $output/output_data_subleadEE.root 

hadd -f $output/output_leadEE.root $output/output_data_leadEE.root $output/output_mc_leadEE.root  
hadd -f $output/output_subleadEE.root $output/output_data_subleadEE.root $output/output_mc_subleadEE.root  
hadd -f $output/output.root $output/output_leadEE.root $output/output_subleadEE.root  
hadd -f $output/output_data.root $output/output_data_leadEE.root $output/output_data_subleadEE.root  
./basic_plots.py --load basic_plots_preshower.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/$output/ --input-dir $output --lumi 2.45 --fudge $fudge 


