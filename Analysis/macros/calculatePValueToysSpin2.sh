#!/bin/bash
set -e
set -x
#combineall loops over masse
#for short queue loop over all masses
#for all q sepeartely
infolder="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin2_wnuis_unblind_all/"
JOBDIR=sgejob-$JOB_ID
echo $JOB_ID
wait
ls -la /scratch/mquittna
wait
mkdir -p /scratch/mquittna/$JOBDIR
ls -l /scratch/mquittna/$JOBDIR
outfolder=/scratch/mquittna/$JOBDIR
cp $infolder/datacard*.txt $outfolder/.
datacard_bkg="$outfolder/datacard_combined_spin2_wnuis_unblind_grav_001_950.txt"
toysFile="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin2_wnuis_unblind_all/higgsCombine_bkgLEE.GenerateOnly.mH0.$1.root"
replaceNames=1
ntoys=10
#short q only for jobs above 100 150 each
#$ -q short.q
#$-e /dev/null 
#$-o /dev/null
CMSSW_DIR=/shome/mquittna/CMSSW/CMSSW_7_1_5


source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
	  
cd $outfolder
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  02 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEESpin2 -s $1 --pvalue --significance  --hadd 
cp $outfolder/higgsCombineLEESpin2_k02*.root $infolder/. 


