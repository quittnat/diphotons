#!/bin/bash
##do for spin0 and spin2 and all masses
#combineall loops over masses
datacard_bkg="datacard_combined_spin0_wnuis_unblind_grav_02_500.txt"
folder="combined_spin0_wnuis_unblind_all"
toysFile="higgsCombine_bkgLEE.GenerateOnly.mH0.$1.root"
ntoys=100
#$ -q all.q
#$ -o combined_spin0_wnuis_unblind_all
#$ -e combined_spin0_wnuis_unblind_all
#$ -cwd
CMSSW_DIR=/shome/mquittna/CMSSW/CMSSW_7_1_5/

source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
	  
cd $CMSSW_DIR/src/diphotons/Analysis/macros/
cd $folder

#sed -e  's:/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v4_data_cic2_default_shapes_spin0_wnuis_lumi_2.69:/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/full_analysis_moriond16v1_sync_v4_data_cic2_default_shapes_spin0_wnuis_lumi_2.69:g' $datacard_bkg > $datacard_bkg.tmp && mv $datacard_bkg.tmp $datacard_bkg
#sed -e 's:/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_0T_sync_v6_data_cic0T_default_shapes_spin0_wnuis_lumi_0.59:/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/full_analysis_moriond16v1_0T_sync_v6_data_cic0T_default_shapes_spin0_wnuis_lumi_0.59:g' $datacard_bkg > $datacard_bkg.tmp && mv $datacard_bkg.tmp $datacard_bkg
wait
combine -M GenerateOnly $datacard_bkg -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils -s $1 -m 0 
wait
cd ..
./combineall.sh $folder  02 -M ProfileLikelihood --toysFile $toysFile  -t $ntoys -n LEE  -s $1 --pvalue --significance
wait
./combineall.sh $folder  01 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEE -s $1 --pvalue --significance
wait
./combineall.sh $folder  001 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEE -s $1 --pvalue --significance

#fix hadd combineall and implement sed in combineall correcty



