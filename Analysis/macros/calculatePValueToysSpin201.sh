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
##ls -al $outfolder
toysFile="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin2_wnuis_unblind_all/higgsCombine_bkgLEE.GenerateOnly.mH0.$1.root"
replaceNames=1
#start all q with 100 jobs per coupling
#$ -q all.q
#$-e /dev/null 
#$-o /dev/null
ntoys=100
#short q only for jobs above 100 150 each
###$ -q short.q
CMSSW_DIR=/shome/mquittna/CMSSW/CMSSW_7_1_5


source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
	  
cd $outfolder
#but take datacards input from folder in shome
if [ $replaceNames == 0 ] ; then
		sed -e 's#/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros#srm://t3se01.psi.ch//pnfs/psi.ch/cms/trivcat/store/user/mquittna#g' -i $outfolder/datacard*.txt 
fi

#combine -M GenerateOnly $datacard_bkg  -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils -s $1 -m 0  

###ls -al $toysFile
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  01 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEESpin2 -s $1 --pvalue --significance  --hadd 
###hadd $outfolder/higgsCombineLEE_k01.ProfileLikelihood.$1.root $outfolder/higgsCombineLEE_k01.ProfileLikelihood.mH*.$1.root 
cp $outfolder/higgsCombineLEESpin2_k01*.root $infolder/. 


