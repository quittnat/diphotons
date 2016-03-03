coups="001 01 02"
## coups=001
##do for spin0 and spin2 and all masses
#combineall loops over masses
datacard_bkg="datacard_combined_spin0_wnuis_unblind_grav_001_600.txt"
folder="combined_spin0_wnuis_unblind"
toysFile="higgsCombine_bkgLEE.GenerateOnly.mH120.123456.root"
ntoys=3
cd $folder
combine -M GenerateOnly $datacard_bkg -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils 
wait
#to replace path in the datacards in case you have to copy it to t3 because too slow
#sed 's%rate.*%rate 1 1 0 1 1 1 0 1 1 1%' full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth.txt | grep -v 'group' > full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth_nopp.txt
wait
#do I need -t 1000 there as well or does it read all toys automatically?
cd ..
parallel --gnu './combineall.sh combined_spin0_wnuis_unblind/ {} -M ProfileLikelihood --toysFile higgsCombine_bkgLEE.GenerateOnly.mH120.123456.root  -t 3 -n LEE --hadd --pvalue --significance --cont' ::: 001 01 02 
#./combineall.sh $folder 001 -M ProfileLikelihood --toysFile $toysFile  -t $ntoys -n _LEE --hadd --pvalue --significance --cont




