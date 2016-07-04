#!/bin/bash

set -x

output=full_analysis_spring16v1_sync_v4_cert_275125
cut='(mass > 230 && max(abs(leadScEta),abs(subleadScEta))<1.5) || mass > 320'
mcfilename=full_analysis_spring16v1_sync_v1_2705_cert
mkdir $output
##non approved k-factor (new)
##--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*( 1.582 + 0.0001136 *genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.523 + 0.0001607*genMass)) " \
##old k-factors
##	--weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
## scale MC by k-factor

# ./auto_plotter.py \
#     --process GGJets\*EB\* \
#     --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root \
#     --selection cic,cicGenIso,cicNonGenIso \
#     --move cicGenIso:cic,cicNonGenIso:cic \
#     --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
#     --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
#     --cut "$cut" \
#     --merge "LowR9","HighR9"\
#     --output $output/output_mc_EBEB.root 
 
 ## 
 ## ./auto_plotter.py \ 
 ##     --selection cic,cicGenIso,cicNonGenIso \
 ##    --move cicGenIso:cic,cicNonGenIso:cic \
 ##     --process GGJets\*EE\* \
 ##     --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root \
 ##     --move cicGenIso:cic,cicNonGenIso:cic \
 ##     --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
 ##     --histograms "mass>>mass[320,355,444,500,600,800,1600]"\
 ##     --cut "$cut" \
 ##     --merge "LowR9","HighR9"\
 ##     --output $output/output_mc_EBEE.root 
 ## 
 ## hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root 
 ## 
 ##  cross-ceck w/o k-factor
 ## ./auto_plotter.py \ 
 ##     --selection cic,cicGenIso,cicNonGenIso \
 ##    --move cicGenIso:cic,cicNonGenIso:cic \
 ##     --process GGJets\*EB\* \
 ##     --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root  \
 ##     --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
 ##     --cut "$cut" \
 ##     --merge "LowR9","HighR9"\
 ##     --output $output/output_mc_nok_EBEB.root 
 ## 
 ## 
 ## ./auto_plotter.py \ 
 ##     --selection cic,cicGenIso,cicNonGenIso \
 ##    --move cicGenIso:cic,cicNonGenIso:cic \
 ##     --process GGJets\*EE\* \
 ##     --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root \
 ##     --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
 ## 	--cut "$cut" \
 ##     --merge "LowR9","HighR9"\
 ##     --output $output/output_mc_nok_EBEE.root 
 ## 
 ## hadd -f $output/output_mc_nok.root  $output/output_mc_nok_EBEB.root  $output/output_mc_nok_EBEE.root 
 ##
 ###ompute pp in data
   ./auto_plotter.py --selection cic \
      --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root\
      --process Data\*EB\* \
      --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
      --cut "$cut" \
      --merge "LowR9","HighR9"\
      --scale '{"mass":[ [0.864568531513 ,-1],[   0.863343477249 ,-1],[   0.886201381683 ,-1],[  0.892993330956 ,-1],[ 0.884906589985 ,-1],[ 0.91299790144 ,-1],[ 0.953488171101 ,-1],[ 0.995400071144 ,-1],[ 1.0 ,-1]]}' \
      --output $output/output_data_EBEB.root 
 ##  
 ##    
 ##   ./auto_plotter.py --selection cic \
 ##      --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root\
 ##      --process Data\*EB\* \
 ##      --histograms "mass>>mass_up[230,253,282,295,332,409,500,600,800,1600]" \
 ##      --histograms "mass>>mass_low[230,253,282,295,332,409,500,600,800,1600]" \
 ##      --cut "$cut" \
 ##      --merge "LowR9","HighR9"\
 ##      --rename "Data_err" \
 ##      --asymError \
 ##      --scale '{"mass_up":[
 ##  [ 0.864861614256 , 0.104634288957 ],
 ##  [ 0.863609455442 , 0.10592606147 ],
 ##  [ 0.885911757639 , 0.118518307545 ],
 ##  [ 0.893317611275 , 0.109704792842 ],
 ##  [ 0.885348868331 , 0.107507700532 ],
 ##  [ 0.912054700296 , 0.1236882405 ],
 ##  [ 0.954576440191 , 0.13768134879 ],
 ##  [ 1.04504864793 , 0.161731128375 ],
 ##  [ 0.977350770026 , 0.0950301799023 ]
 ## 	 ]}' \
 ##      --scale '{"mass_low":[
 ##  [ 0.864861614256 , 0.104341206214 ],
 ##  [ 0.863609455442 , 0.105660083278 ],
 ##  [ 0.885911757639 , 0.118807931589 ],
 ##  [ 0.893317611275 , 0.109380512523 ],
 ##  [ 0.885348868331 , 0.107065422186 ],
 ##  [ 0.912054700296 , 0.124631441644 ],
 ##  [ 0.954576440191 , 0.1365930797 ],
 ##  [ 1.04504864793 , 0.112082551593 ],
 ##  [ 0.977350770026 , 0.117679409877 ]
 ##  ]}' \
 ##      --output $output/output_data_err_EBEB.root 
 ##   
 ## 
 ## ./auto_plotter.py --selection cic \
 ##     --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root \
 ##     --process Data\*EE\* \
 ##     --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
 ##     --cut "$cut" \
 ##     --merge "LowR9","HighR9"\
 ##     --scale '{"mass":[ [0.878596544266 ,-1],[0.763974845409 ,-1],[0.731936454773 ,-1],[0.835289299488 ,-1],[0.735968589783 ,-1],[0.83046746254 ,-1]]}'\
 ##     --output $output/output_data_EBEE.root 
 ## 
 ##  ./auto_plotter.py --selection cic \
 ##      --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root \
 ##      --process Data\*EE\* \
 ##      --histograms "mass>>mass_up[320,355,444,500,600,800,1600]" \
 ##      --histograms "mass>>mass_low[320,355,444,500,600,800,1600]" \
 ##      --asymError \
 ##      --cut "$cut" \
 ##      --merge "LowR9","HighR9"\
 ##      --rename "Data_err" \
 ##      --scale '{"mass_up":[
 ## 	 [ 0.879072249012 , 0.151606643635 ],
 ## 	 [ 0.764033558701 , 0.133609621322 ],
 ## 	 [ 0.730879876138 , 0.15617532655 ],
 ## 	 [ 0.835193940606 , 0.15551955299 ],
 ## 	 [ 0.734357639884 , 0.154622269765 ],
 ## 	 [ 0.819502485259 , 0.194455710621 ]
 ## 	 ]}' \
 ##     --scale '{"mass_low":[
 ##     [ 0.879072249012 , 0.151130938889 ],
 ## 	[ 0.764033558701 , 0.13355090803 ],
 ## 	[ 0.730879876138 , 0.157231905185 ],
 ## 	[ 0.835193940606 , 0.155614911872 ],
 ## 	[ 0.734357639884 , 0.156233219664 ],
 ## 	[ 0.819502485259 , 0.205420687901 ]
 ## 	]}' \
 ##      --output $output/output_data_err_EBEE.root 
 ##  
 ##  hadd -f $output/output_data_err.root  $output/output_data_err_EBEB.root  $output/output_data_err_EBEE.root
 ##  hadd -f $output/output_data.root $output/output_data_EBEB.root $output/output_data_EBEE.root
 ##  ### hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root
 ##  hadd -f $output/output.root  $output/output_mc.root  $output/output_data.root $output/output_data_err.root
 ##  ./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/"$output" --input-dir $output --lumi 4.0
