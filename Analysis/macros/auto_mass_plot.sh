#!/bin/bash

set -x

output=full_analysis_spring15_7415v2_sync_v3_compare
cut='(mass > 230 && max(abs(leadScEta),abs(subleadScEta))<1.5) || mass > 320'

mkdir $output
##non approved k-factor (new)
##--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*( 1.582 + 0.0001136 *genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.523 + 0.0001607*genMass)) " \
##old k-factors
## scale MC by k-factor
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root   --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
	--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
    --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_EBEB.root 


./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
	--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_EBEE.root 

hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root 

## cross-ceck w/o k-factor
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_nok_EBEB.root 


./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v11/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_nok_EBEE.root 

hadd -f $output/output_mc_nok.root  $output/output_mc_nok_EBEB.root  $output/output_mc_nok_EBEE.root 

## compute pp in data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
   --process Data\*EB\* \
   --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
   --scale '{ "mass": [[  0.8688402       ,0.0489556436876],[0.8800560, 0.0529053838468  ],[     0.9374606, 0.0469352125767],[0.8635201, 0.0526435782377],[      0.9074038, 0.0486617966005   ],[      0.8737227,  0.0604184704223  ],[      0.9882389,  0.030053515941   ],[      0.8754522,  0.0715876619642 ],[      0.9615517,0.0544461432163]] }' \
   --cut "$cut" \
   --output $output/output_data_EBEB.root 

##    --scale '{ "mass": [[0.8469712,0.0],[0.8716598,0.0],[0.9429578,0.0],[0.8808349,0.0],[0.9032798,0.0],[0.8949969,0.0],[0.9388431,0.0]], "massStatSys": [[0.8469712,-0.06119773],[0.8716598,-0.06144162],[0.9429578,-0.0526395],[0.8808349,-0.05801563],[0.9032798,-0.05530418],[0.8949969,-0.06584333],[0.9388431,-0.06267834]], "massSyst" : [[0.8284119,-0.05527019],[0.8877271,-0.05365184],[0.8469712,-0.05477732],[0.8716598,-0.0546952],[0.9429578,-0.04423841],[0.8808349,-0.04918167],[0.9032798,-0.04896716],[0.8949969,-0.04983432],[0.9388431,-0.05282998]] }' \

./auto_plotter.py --selection cic \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --process Data\*EE\* \
    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
    --scale '{ "mass": [[0.8215680,0.101605863439],[0.7518959,0.101540433831],[0.6698329, 0.115953902535],[0.7618178,0.113387601436],[0.8777796,0.0904766158086],[0.9365055, 0.070239429172]] }' \
	--cut "$cut" \
    --output $output/output_data_EBEE.root 

hadd -f $output/output_data.root  $output/output_data_EBEB.root  $output/output_data_EBEE.root
hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root
hadd -f $output/output.root  $output/output_mc.root  $output/output_data.root
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/"$output" --input-dir $output --lumi 2.56
