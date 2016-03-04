coups="001 01 02"
## coups=001
##do for spin0 and spin2 and all masses
#combineall loops over masses
datacard_bkg="datacard_combined_spin0_wnuis_unblind_grav_001_600.txt"
folder="combined_spin0_wnuis_unblind_all"
toysFile="higgsCombine_bkgLEE.GenerateOnly.mH120.123456.root"
ntoys=50
cd $folder
combine -M GenerateOnly $datacard_bkg -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils 
wait
cd ..
parallel --gnu './combineall.sh combined_spin0_wnuis_unblind_all/ {} -M ProfileLikelihood --toysFile higgsCombine_bkgLEE.GenerateOnly.mH120.123456.root  -t 50 -n LEE --hadd --pvalue --significance --cont' ::: 001 01 02 




