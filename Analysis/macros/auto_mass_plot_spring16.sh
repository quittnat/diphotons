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

  ./auto_plotter.py \
      --process GGJets\*EB\* \
      --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root \
      --selection cic,cicGenIso,cicNonGenIso \
      --move cicGenIso:cic,cicNonGenIso:cic \
       --merge "LowR9","HighR9"\
      --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
      --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
      --cut "$cut" \
      --output $output/output_mc_EBEB.root 
  
   ./auto_plotter.py \
      --selection cic,cicGenIso,cicNonGenIso \
      --move cicGenIso:cic,cicNonGenIso:cic \
       --process GGJets\*EE\* \
       --merge "LowR9","HighR9"\
       --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root \
       --move cicGenIso:cic,cicNonGenIso:cic \
       --weight "weight*((max(abs(leadScEta),abs(subleadScEta))<1.5)*(1.408 + 1.014e-4*genMass) + (max(abs(leadScEta),abs(subleadScEta))>1.5)*(1.367 + 1.647e-4*genMass)) " \
       --histograms "mass>>mass[320,355,444,500,600,800,1600]"\
       --cut "$cut" \
       --output $output/output_mc_EBEE.root 
   
   hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root 
   
 #   cross-ceck w/o k-factor
   ./auto_plotter.py \
       --selection cic,cicGenIso,cicNonGenIso \
       --move cicGenIso:cic,cicNonGenIso:cic \
       --merge "LowR9","HighR9"\
       --process GGJets\*EB\* \
       --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root  \
       --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
       --cut "$cut" \
       --output $output/output_mc_nok_EBEB.root 
   
   
   ./auto_plotter.py \
       --selection cic,cicGenIso,cicNonGenIso \
      --move cicGenIso:cic,cicNonGenIso:cic \
       --process GGJets\*EE\* \
       --merge "LowR9","HighR9"\
       --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$mcfilename/output.root \
       --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
       --cut "$cut" \
       --output $output/output_mc_nok_EBEE.root 
   
   hadd -f $output/output_mc_nok.root  $output/output_mc_nok_EBEB.root  $output/output_mc_nok_EBEE.root 
 
# mpute pp in data
    ./auto_plotter.py --selection cic \
       --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root\
       --process Data\*EB\* \
       --merge "LowR9","HighR9"\
       --histograms "mass>>mass[230,253,282,295,332,409,500,600,800,1600]" \
       --cut "$cut" \
       --scale '{"mass":[ [0.864568531513 ,-1],[   0.863343477249 ,-1],[   0.886201381683 ,-1],[  0.892993330956 ,-1],[ 0.884906589985 ,-1],[ 0.91299790144 ,-1],[ 0.953488171101 ,-1],[ 0.995400071144 ,-1],[ 1.0 ,-1]]}' \
       --output $output/output_data_EBEB.root 
    
      
     ./auto_plotter.py --selection cic \
        --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root\
        --process Data\*EB\* \
        --histograms "mass>>mass_up[230,253,282,295,332,409,500,600,800,1600]" \
        --histograms "mass>>mass_low[230,253,282,295,332,409,500,600,800,1600]" \
        --cut "$cut" \
        --merge "LowR9","HighR9"\
        --rename "Data_err" \
        --asymError \
        --scale '{"mass_up":[
   	 [ 0.86503395677 , 0.119140386255 ],
 	 [ 0.86380973558 , 0.120553538393 ],
 	 [ 0.886402459398 , 0.130053372886 ],
 	 [ 0.893558226793 , 0.120653529171 ],
 	 [ 0.885590680886 , 0.11952128868 ],
 	 [ 0.911906431054 , 0.133301907298 ],
 	 [ 0.954715162497 , 0.141996408146 ],
 	 [ 1.04538859234 , 0.162438495996 ],
 	 [ 0.977350770026 , 0.0950301799023 ]
 	   
 	   
 	   ]}' \
        --scale '{"mass_low":[
 [ 0.86503395677 , 0.118674960999 ],
 [ 0.86380973558 , 0.120087280063 ],
 [ 0.886402459398 , 0.129852295172 ],
 [ 0.893558226793 , 0.120088633334 ],
 [ 0.885590680886 , 0.118837197779 ],
 [ 0.911906431054 , 0.134393377684 ],
 [ 0.954715162497 , 0.14076941675 ],
 [ 1.04538859234 , 0.1124499748 ],
 [ 0.977350770026 , 0.117679409877 ]
 	   ]}' \
        --output $output/output_data_err_EBEB.root 
     
   
   ./auto_plotter.py --selection cic \
       --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root \
       --process Data\*EE\* \
       --histograms "mass>>mass[320,355,444,500,600,800,1600]" \
       --cut "$cut" \
       --merge "LowR9","HighR9"\
       --scale '{"mass":[ [0.878596544266 ,-1],[0.763974845409 ,-1],[0.731936454773 ,-1],[0.835289299488 ,-1],[0.735968589783 ,-1],[0.83046746254 ,-1]]}'\
       --output $output/output_data_EBEE.root 
  
   ./auto_plotter.py --selection cic \
       --file  /afs/cern.ch/user/m/musella/public/workspace/exo/$output/output.root \
       --process Data\*EE\* \
       --histograms "mass>>mass_up[320,355,444,500,600,800,1600]" \
       --histograms "mass>>mass_low[320,355,444,500,600,800,1600]" \
       --asymError \
       --cut "$cut" \
       --merge "LowR9","HighR9"\
       --rename "Data_err" \
       --scale '{"mass_up":[
  	 [ 0.879547515462 , 0.168679905152 ],
	 [ 0.764295776537 , 0.167905144336 ],
	 [ 0.731353749719 , 0.188470767628 ],
	 [ 0.835762302747 , 0.179296595656 ],
	 [ 0.73505377571 , 0.188832621284 ],
	 [ 0.82062740122 , 0.209642966355 ]
	   ]}' \
      --scale '{"mass_low":[
  [ 0.879547515462 , 0.167728933955 ],
  [ 0.764295776537 , 0.167584213209 ],
  [ 0.731353749719 , 0.189053472681 ],
  [ 0.835762302747 , 0.178823592397 ],
  [ 0.73505377571 , 0.189747435356 ],
  [ 0.82062740122 , 0.219483027675 ]
	  ]}' \
       --output $output/output_data_err_EBEE.root 
   
   hadd -f $output/output_data_err.root  $output/output_data_err_EBEB.root  $output/output_data_err_EBEE.root
   hadd -f $output/output_data.root $output/output_data_EBEB.root $output/output_data_EBEE.root
   ### hadd -f $output/output_mc.root  $output/output_mc_EBEB.root  $output/output_mc_EBEE.root
   hadd -f $output/output.root  $output/output_mc.root  $output/output_data.root $output/output_data_err.root
   ./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/"$output" --input-dir $output --lumi 4.0
