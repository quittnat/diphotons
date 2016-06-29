#!/bin/bash


target=$1 && shift

args="-U --fixed-x-section 1.e-3 --use-fb --load lumi_limits.json --lumi 10 --saveas pdf,convert_png,root"

www=$(echo $target | sed 's%_cic.*%%')


#./limit_plots.py --do-limits -M Asymptotic  $args --input-dir $target/bias_term_in_scan -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1/bias_study_default/bias_in
wait
#./limit_plots.py --do-limits -M Asymptotic  $args --input-dir $target/bias_term_out_scan -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1/bias_study_default/bias_out
wait
### 
### ./limit_plots.py --do-pvalues -M ProfileLikelihood $args --input-dir $target -O ~/www/exo/spring15_7415/$www/$target/limits
### ###  
### ### for cat in EBEB EBEE; do
### ###     ./limit_plots.py --do-pvalues -M ProfileLikelihood $args --input-dir $target/$cat -O ~/www/exo/spring15_7415/$www/$target/limits/$cat --label $cat
### ### done 
### ### 
### ### 
./limit_plots.py $args --do-comparison --compare-files $target/bias_term_in_scan/saved_2/graphs_Asymptotic.root,$target/bias_term_out_scan/graphs_Asymptotic.root --compare-expected --load lumi_limits.json --lumi 10 -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1/bias_study_default/  -k 02 --plot-average
### 
### ### for cat in EBEB EBEE; do
### ###     ./limit_plots.py --do-limits -M Asymptotic $args --input-dir $target/$cat -O ~/www/exo/spring15_7415/$www/$target/limits/$cat --label $cat
### ### done 


## ./limit_plots.py $args --do-comparison --compare-files $target/graphs_Asymptotic.root,$target/EBEB/graphs_Asymptotic.root,$target/EBEE/graphs_Asymptotic.root --load lumi_limits.json --lumi 2.56 -O  ~/www/exo/spring15_7415/$www/$target/limits/comparison --compare-expected -k 001,01,02
