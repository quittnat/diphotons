coups="001 01 02"
## coups=001
##do for spin0 and spin2 and all masses
#combineall loops over masses
datacard_bkg="datacard_combined_spin0_wnuis_unblind_grav_001_600.txt"
folder="combined_spin0_wnuis_unblind"
toysFile="higgsCombine_bkgLEE.GenerateOnly.mH120.123456.root"
ntoys=3
minmass=500
maxmass=1600
cd $folder
combine -M GenerateOnly $datacard_bkg -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils 
wait
cd ..
parallel --gnu './combineall.sh combined_spin0_wnuis_unblind/ {} -M ProfileLikelihood --toysFile higgsCombine_bkgLEE.GenerateOnly.mH120.123456.root  -t 3 -n LEE --hadd --pvalue --significance --cont' ::: 001 01 02 
wait
./limit_plots.py --input-dir combined_spin0_wnuis_unblind/ -n LEE -k 001 -U --compute-upcrossings -M ProfileLikelihood --nToys $ntoys
wait
./limit_plots.py --input-dir combined_spin0_wnuis_unblind/ -n LEE -k 01 -U --compute-upcrossings -M ProfileLikelihood --nToys $ntoys
wait
./limit_plots.py --input-dir combined_spin0_wnuis_unblind/ -n LEE -k 02 -U --compute-upcrossings -M ProfileLikelihood --nToys $ntoys

wait
#comput upcrossings
/shome/mquittna/CMSSW/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py  -l 0.5 /shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind/graphs_001_ProfileLikelihood.root observed_001_ $minmass $maxmass


