#!/bin/bash

set -x 

src=$1 && shift
if [[ $(whoami) == "mquittna" ]]; then
#	src=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15v825ns_sync_v3/ && shift
	src=/shome/mquittna/CMSSW/EXO_7_4_6_patch2/src/diphotons/Analysis/config/output && shift
	src=/shome/mquittna/CMSSW/EXO_7_4_6_patch2/src/diphotons/Analysis/macros/full_analysis_spring15_7412v2_runD_v2 && shift
#	src=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15v825ns_sync_v3/ && shift
fi

www=~/www/exo/spring15_v850ns
if [[ $(whoami) == "mquittna" ]]; then
    www=/afs/cern.ch/user/m/mquittna/www/diphoton/basic_plots_spring15_7412v2_runD_v2/
##   www=/afs/cern.ch/user/m/mquittna/www/diphoton/basic_plots_QCD_HT100ToInf_spring1550ns/
fi
echo $1
[ -n "$1" ] && www=$1 && shift

target=$(basename $src)

[[ ! -d $www ]] && mkdir  $www/
mkdir  $www/$target/

./basic_plots.py --load basic_plots.json  -O $www/$target/selection  --input-dir $src  
# ./basic_plots.py --load purity_plots.json -O $www/$target/purity     --input-dir $src 
## ./eff_plots.py --load eff_plots.json      -O $www/$target/efficiency --input-dir $src 

## ./eff_plots.py --load singlepho_eff_plots.json      -O $www/$target/signlepho_efficiency --input-dir $src 
## ./eff_plots.py --load singlepho_eff_plots.json      -O $www/$target/signlepho_efficiency_grav15  --template "%(sample)s/histograms/RSGravToGG_kMpl_001_M_1500_13TeV_%(cat)s%(name)s"  --input-dir $src 
## ./eff_plots.py --load singlepho_eff_plots.json      -O $www/$target/signlepho_efficiency_grav50  --template "%(sample)s/histograms/RSGravToGG_kMpl_001_M_5000_13TeV_%(cat)s%(name)s"  --input-dir $src 

