#!/bin/bash
set -e
set -x
#combineall loops over masses
coup=$2
spin=$3
datacard_bkg="datacard_combined_spin0_wnuis_unblind_grav_$2_950.txt"
infolder="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin$3_wnuis_unblind_all/"
JOBDIR=sgejob-$JOB_ID
ls -l /scratch/mquittna
mkdir -p /scratch/mquittna/$JOBDIR
outfolder=/scratch/mquittna/$JOBDIR
cp $infolder/datacard*.txt $outfolder/.
ls -al $outfolder
toysFile="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin$3_wnuis_unblind_all/higgsCombine_bkgLEE.GenerateOnly.mH0.$1.root"
ntoys=100
replaceNames=1
#$ -q all.q
####$ -cwd
CMSSW_DIR=/shome/mquittna/CMSSW/CMSSW_7_1_5

source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
	  
mkdir -p /scratch/mquittna/$JOBDIR
cd $outfolder
#but take datacards input from folder in shome
if [ $replaceNames == 0 ] ; then
		sed -e 's#/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros#srm://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/mquittna#g' -i $outfolder/datacard*.txt 
fi

#wait
#combine -M GenerateOnly $infolder $datacard_bkg  -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils -s $1 -m 0 --cont 
#wait

ls -al $toysFile
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  $coup -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEE -s $1 --pvalue --significance --cont --hadd 
ls -al $outfolder
hadd $outfolder/higgsCombineLEE_kall.ProfileLikelihood.$s.root $outfolder/higgsCombineLEE_k*.ProfileLikelihood.$s.root 
cp $outfolder/higgsCombineLEE_k*.root $infolder/.


