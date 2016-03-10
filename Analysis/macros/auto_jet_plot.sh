#!/bin/bash

set -x
fudge=1.4
cuts=(0 1 2 3)



## merge MC
for cut in "${cuts[@]}" ;do
	echo $cut
	if [[ $cut -eq 0 ]]; then
		output=full_analysis_moriond16v1_sync_v4_0_730
		cut='(mass < 730.)'
	elif [[ $cut -eq 1 ]]; then
		output=full_analysis_moriond16v1_sync_v4_500_730
		cut='(mass > 500 && mass < 730.)'
	elif [[ $cut -eq 2 ]]; then
		output=full_analysis_moriond16v1_sync_v4_730_790
		cut='(mass > 730 && mass < 790)'
	elif [[ $cut -eq 3 ]]; then
		output=full_analysis_moriond16v1_sync_v4_790_Inf
		cut='(mass > 790.)'
	fi
	mkdir $output
	./auto_plotter.py --selection cic,cicGenIso,cicNonGenIso \
    	--load auto_plotter_histos_jet.json \
		--process GGJets\*\* \
    	--process GJets\*\* \
    	--file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v4/output.root \
		--move cicGenIso:cic,cicNonGenIso:cic \
		--prescale GGJets\*\*:10 \
		--cut "$cut" \
    	--output $output/output_mc.root 



  ##data merge in Data
	./auto_plotter.py --selection cic \
    	--load auto_plotter_histos_jet.json \
   		--file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v4_data/output.root \
   		--process Data\*\* \
		--cut "$cut"\
		--output $output/output_data.root 

	hadd -f $output/output.root $output/output_data.root $output/output_mc.root  
	./basic_plots.py --load basic_plots.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/moriond16/$output/ --input-dir $output  --fudge $fudge --lumi 2.69
done	
