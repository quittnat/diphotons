#!/bin/bash
set -x
fudge=1.4
cuts=(0 1 2)
#cuts=(0)

for cut in "${cuts[@]}" ;do
	echo $cut
	if [[ $cut -eq 0 ]]; then
		output=full_analysis_moriond16v1_0T_sync_v6_230_or_320_500
		cut='(mass < 500.)'

	elif [[ $cut -eq 1 ]]; then
		output=full_analysis_moriond16v1_0T_sync_v6_500_Inf
		cut='(mass > 500.)'
	elif [[ $cut -eq 2 ]]; then
		output=full_analysis_moriond16v1_0T_sync_v6_700_Inf
		cut='(mass > 700.)'
	fi
	mkdir $output
	
	./auto_plotter.py --load auto_plotter_histos.json \
		--selection cic,cicGenIso,cicNonGenIso \
    	--process GGJets\*\* \
    	--process GJets\*\* \
		--file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_0T_sync_v6_data/output.root \
		--move cicGenIso:cic,cicNonGenIso:cic \
		--prescale GGJets\*\*:10 \
		--cut "$cut" \
    	--output $output/output_mc.root 

 ## merge in Data
	./auto_plotter.py --load auto_plotter_histos.json \
		--selection cic \
		--file  /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_0T_sync_v6_data/output.root \
  		--process DoubleEG\*\* \
   		--cut "$cut"\
   		--output $output/output_data.root 

	hadd -f $output/output.root $output/output_data.root $output/output_mc.root  
	./basic_plots.py --load basic_plots_0T.json -O /afs/cern.ch/user/m/mquittna/www/diphoton/moriond16/$output/ --input-dir $output  --fudge $fudge --lumi 0.6 
done
