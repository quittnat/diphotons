#!/bin/bash
njobs=100
###with script goes
### upcrossing_k001_l_0_5.txt
###plot_trials.C
for job in $(seq 0 $njobs); do
	/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py -l 0.5 -o 0.0021451 /shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind_all/graphs_001_0_100.ProfileLikelihood.root  observed_001_$job  500 13000 >> upcrossing_k001_l_0_5.txt
done
