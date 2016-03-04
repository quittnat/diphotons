#!/bin/bash
#combineall loops over masses
datacard_bkg="datacard_combined_spin0_wnuis_unblind_grav_001_950.txt"
infolder="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind_test2/"
#outfolder="/scratch/mquittna/CMSSW_7_1_5/combined_spin0_wnuis_unblind_test2"
JOBDIR=sgejob-$JOB_ID
outfolder=/scratch/mquittna/$JOBDIR
#outfolder="/scratch/mquittna/"
toysFile="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind_test2/higgsCombine_bkgLEE.GenerateOnly.mH0.$1.root"
#ntoys=100
ntoys=3
replaceNames=false
#$ -q all.q
##$ -o combined_spin0_wnuis_unblind_test2
##$ -e combined_spin0_wnuis_unblind_test2
##$ -cwd
CMSSW_DIR=/shome/mquittna/CMSSW/CMSSW_7_1_5/

source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
	  
#cd $CMSSW_DIR/src/diphotons/Analysis/macros/
mkdir -p /scratch/mquittna/$JOBDIR
cd $outfolder
#if all on SE read root files from there
#but take datacards input from folder in shome
#if [ $replaceNames ] ; then
#		sed -e 's#/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros#srm://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/mquittna#g' $datacard_bkg > $datacard_bkg.tmp && mv $datacard_bkg.tmp $datacard_bkg
#fi

#wait
#combine -M GenerateOnly $infolder$datacard_bkg  -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils -s $1 -m 0 
#wait

ls -al $toysFile
#./combineall.sh $infolder  02 -M ProfileLikelihood --toysFile $toysFile  -t $ntoys -n LEE  -s $1 --pvalue --significance
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  01 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEE -s $1 --pvalue --significance --hadd --cont
ls -al $outfolder
wait
gfal-copy file:///$outfolder/higgsCombineLEE_k01.ProfileLikelihood.$1.root srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/combined_spin0_wnuis_unblind/higgsCombineLEE_k01.ProfileLikelihood.$1.root
#wait
#$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  001 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEE -s $1 --pvalue --significance --hadd --cont
#wait
#gfal-copy  file:///$outfolder/higgsCombineLEE_k001.ProfileLikelihood.$1.root srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/combined_spin0_wnuis_unblind/higgsCombineLEE_k001.ProfileLikelihood.$1.root
#fix hadd combineall and implement sed in combineall correcty



