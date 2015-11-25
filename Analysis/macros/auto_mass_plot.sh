#!/bin/bash

set -x

output=full_analysis_spring15_7415v2_sync_v3_compare_2
cut='(mass > 230 && max(abs(leadScEta),abs(subleadScEta))<1.5) || mass > 320'

mkdir $output

## scale MC by k-factor
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
    --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_EBEB.root 


./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_EBEE.root 

hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root 

## cross-ceck w/o k-factor
./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EB\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_nok_EBEB.root 


./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
    --process GGJets\*EE\* \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
    --cut "$cut" \
    --output $output/output_mc_nok_EBEE.root 

hadd -f $output/output_mc_nok.root  $output/output_mc_nok_EBEB.root  $output/output_mc_nok_EBEE.root 

## compute pp in data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
   --process Data\*EB\* \
   --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
   --scale '{ "mass": [[0.8622998,0.0201538],[0.8801798,0.0243933],[0.9383431,0.0245097],[0.8658863,0.0263364],[0.9053993,0.0225588],[0.8699184,0.0414392],[0.9601336,0.0300307],[0.8897305,0.0498550],[0.9419215,0.0598091]] }' \
   --cut "$cut" \
   --output $output/output_data_EBEB.root 


##    --scale '{ "mass": [[0.8469712,0.0],[0.8716598,0.0],[0.9429578,0.0],[0.8808349,0.0],[0.9032798,0.0],[0.8949969,0.0],[0.9388431,0.0]], "massStatSys": [[0.8469712,-0.06119773],[0.8716598,-0.06144162],[0.9429578,-0.0526395],[0.8808349,-0.05801563],[0.9032798,-0.05530418],[0.8949969,-0.06584333],[0.9388431,-0.06267834]], "massSyst" : [[0.8284119,-0.05527019],[0.8877271,-0.05365184],[0.8469712,-0.05477732],[0.8716598,-0.0546952],[0.9429578,-0.04423841],[0.8808349,-0.04918167],[0.9032798,-0.04896716],[0.8949969,-0.04983432],[0.9388431,-0.05282998]] }' \

./auto_plotter.py --selection cic \
    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v3_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
    --process Data\*EE\* \
    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
    --scale '{ "mass": [[0.8343765,0.0523237],[0.7932588,0.0426967],[0.7179751,0.0973470],[0.7900301,0.0772637],[0.9425252,0.0295486],[0.9687680,0.0319608]] }' \
    --cut "$cut" \
    --output $output/output_data_EBEE.root 

hadd -f $output/output_data.root  $output/output_data_EBEB.root  $output/output_data_EBEE.root
