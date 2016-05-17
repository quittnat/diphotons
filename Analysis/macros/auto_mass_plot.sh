#!/bin/bash

set -x

output=full_analysis_moriond16v1_sync_v5_extra_vars_data
cut='(mass > 230 && max(abs(leadScEta),abs(subleadScEta))<1.5) || mass > 320'

mkdir $output
##non approved k-factor (new)
##--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*( 1.582 + 0.0001136 *genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.523 + 0.0001607*genMass)) " \
##old k-factors
##	--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
## scale MC by k-factor

#./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
#    --process GGJets\*EB\* \
#    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root   --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
#    --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
#    --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
#    --cut "$cut" \
#    --output $output/output_mc_EBEB.root 


#./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
#    --process GGJets\*EE\* \
#    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
#    --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
#    --histograms "mass>>mass[320,355,444,500,600,800,1600]"\
#    --cut "$cut" \
#    --output $output/output_mc_EBEE.root 

#hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root 

## cross-ceck w/o k-factor
#./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
#    --process GGJets\*EB\* \
#    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
#    --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
#    --cut "$cut" \


#./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso,cicNoChIso,cicNoChIsoGenIso,cicNoChIsoNonGenIso, \
#    --process GGJets\*EE\* \
#    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
#    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
#	--cut "$cut" \
#    --output $output/output_mc_nok_EBEE.root 

#hadd -f $output/output_mc_nok.root  $output/output_mc_nok_EBEB.root  $output/output_mc_nok_EBEE.root 

## compute pp in data
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root\
   --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
   --process Data\*EB\* \
   --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
   --cut "$cut" \
   --scale '{"mass":[ [ 0.867308795452 ,-1],[ 0.858006477356 ,-1], [ 0.956895291805 ,-1], [ 0.865706264973 ,-1],[ 0.91312122345 ,-1], [ 0.861734449863 ,-1],[ 0.984739124775 ,-1], [ 0.865879058838 ,-1],[ 1.0 ,-1]]}' \
   --output $output/output_data_EBEB.root 

   
./auto_plotter.py --selection cic \
   --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root\
   --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic2,cicNonGenIso:cic2 \
   --process Data\*EB\* \
   --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
   --histograms "mass>>mass_up[230,253,282,295,332,409,500,600,800,1600]" \
   --histograms "mass>>mass_low[230,253,282,295,332,409,500,600,800,1600]" \
   --cut "$cut" \
   --asymError \
   --scale '{"mass_up":[
[ 0.867659845968 , 0.111947924482 ],
[ 0.857936370306 , 0.117919644603 ],
[ 0.960227495965 , 0.121093637658 ],
[ 0.86517050617 , 0.120378163693 ],
[ 0.913654333122 , 0.117803067518 ],
[ 0.858028756667 , 0.137707188021 ],
[ 0.991224486186 , 0.157647746003 ],
[ 0.866242568288 , 0.164139387566 ],
[ 0.945913740925 , 0.0961584278569 ]
   ]}' \
   --scale '{"mass_low":[
 [ 0.867659845968 , 0.111596873966 ],
[ 0.857936370306 , 0.117989751653 ],
[ 0.960227495965 , 0.117761433498 ],
[ 0.86517050617 , 0.120913922496 ],
[ 0.913654333122 , 0.117269957846 ],
[ 0.858028756667 , 0.141412881217 ],
[ 0.991224486186 , 0.151162384592 ],
[ 0.866242568288 , 0.163775878115 ],
[ 0.945913740925 , 0.150244686932 ]
   ]}' \
   --output $output/output_data_err_EBEB.root 


#./auto_plotter.py --selection cic \
#    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root \ 
#    --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
#    --process Data\*EE\* \
#    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
#    --cut "$cut" \
#    --scale '{"mass":[ [ 0.815133213997 ,-1],[ 0.783728480339 ,-1],[ 0.873058080673 ,-1], [0.617588639259 ,-1],[ 0.846991121769 ,-1],[ 0.887187361717 ,-1] ]}'\
#    --output $output/output_data_EBEE.root 
#./auto_plotter.py --selection cic \
#    --file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/output.root --move cicNoChIsoGenIso:cicNoChIso,cicNoChIsoNonGenIso:cicNoChIso,cicGenIso:cic,cicNonGenIso:cic \
#    --process Data\*EE\* \
#    --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
#    --cut "$cut" \
#    --scale '{"mass":[ [ 0.814722382193 , 0.173598550384 ],[ 0.78374533621 , 0.167441498496 ],[ 0.880818688629 , 0.235159625181 ],[ 0.616451103752 , 0.184942374811 ],[ 0.845125110616 , 0.206740676843 ],[ 0.887325959986 , 0.232328647348 ]]}'\
#    --output $output/output_data_err_EBEE.root 
##
#--scale '{ "mass": [[0.867308795452 , 0.0503222267649 ],[0.858006477356 ,0.0570716153544   ],[0.956895291805 ,0.0377916182429  ],[0.865706264973 ,0.056449121008   ],[0.91312122345 ,0.0448497023146   ],[0.861734449863 ,  ],[0.984739124775 ,0.0617819608643  ],[0.865879058838 ,0.0364356518461  ],[1.0 ,0.0747184808719  ]] }' \
#--scale '{ "mass": [[0.815133213997 , 0.101110477918  ],[0.783728480339 , 0.102836896568 ],[0.873058080673 ,0.12547682698   ],[0.617588639259 ,0.133731156241 ],[0.846991121769 , 0.112079713623  ],[0.887187361717 , 0.0928274604558  ]] }' \
cp $output/output_data_err_EBEB.root  $output/output_data_err.root
cp $output/output_data_EBEB.root  $output/output_data.root
#hadd -f $output/output_data.root  $output/output_data_EBEB.root  $output/output_data_EBEE.root
#hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root
#hadd -f $output/output.root  $output/output_mc.root  $output/output_data.root $output/output_data_err.root
./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/moriond16/"$output" --input-dir $output --lumi 2.69
