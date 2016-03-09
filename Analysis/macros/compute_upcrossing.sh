#!/bin/bash
njobs=100
###with script goes
### upcrossing_k001_l_0_5.txt
###plot_trials.C
###if toys

#for job in $(seq 0 $njobs); do
#	/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py -l 0.5 -o 0.0021451 /shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind_all/graphs_001_0_100.ProfileLikelihood.root  observed_001_$job  500 13000 >> upcrossing_k001_l_0_5.txt
#done

###else:
/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py -l 0.5  /afs/cern.ch/user/m/musella/public/workspace/exo/combined_spin0_wnuis_unblind/graphs_ProfileLikelihood.root  observed_001 500 3000  >> upcrossing_data_13TeV_k001_spin0_l_0_5.txt


/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py -l 0.5  /afs/cern.ch/user/m/musella/public/workspace/exo/combined_spin2_wnuis_unblind/graphs_ProfileLikelihood.root  observed_001 500 3000   >> upcrossing_data_13TeV_k001_spin2_l_0_5.txt
/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py -l 0.5  /afs/cern.ch/user/m/musella/public/workspace/exo/combined_813_spin0_unblind/graphs_ProfileLikelihood.root  observed_001 500 3000   >> upcrossing_data_8_13TeV_k001_spin0_l_0_5.txt
/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py -l 0.5  /afs/cern.ch/user/m/musella/public/workspace/exo/combined_813_spin2_unblind/graphs_ProfileLikelihood.root  observed_001 500 3000  >> upcrossing_data_8_13TeV_k001_spin2_l_0_5.txt
