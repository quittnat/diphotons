#!/bin/bash
set -e
set -x
#combineall loops over masses
coup=001
infolder="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind_all/"
JOBDIR=sgejob-$JOB_ID
echo $JOB_ID
wait
ls -la /scratch/mquittna
wait
if ( ! mkdir -p /scratch/mquittna/$JOBDIR ); 
	#$ -e $infolder/
 	then exit; 
fi
mkdir -p /scratch/mquittna/$JOBDIR
ls -l /scratch/mquittna/$JOBDIR
outfolder=/scratch/mquittna/$JOBDIR
cp $infolder/datacard*.txt $outfolder/.
datacard_bkg="$outfolder/datacard_combined_spin0_wnuis_unblind_grav_001_950.txt"
ls -al $outfolder
toysFile="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spin0_wnuis_unblind_all/higgsCombine_bkgLEE.GenerateOnly.mH0.$1.root"
ntoys=1
replaceNames=1
#$ -q all.q
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

combine -M GenerateOnly $datacard_bkg  -n _bkgLEE -t $ntoys --saveToys -L libdiphotonsUtils -s $1 -m 0  

###ls -al $toysFile
####$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  $coup -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEE -s $1 --pvalue --significance  --hadd --cont 
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  001 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEESpin0 -s $1 --pvalue --significance  --hadd 
ls -al $outfolder
hadd -f $outfolder/higgsCombineLEE_k001.ProfileLikelihood.$s.root $outfolder/higgsCombineLEE_k001.ProfileLikelihood.mH*.$s.root 
wait
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  01 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEESpin0 -s $1 --pvalue --significance  --hadd 
hadd -f $outfolder/higgsCombineLEE_k01.ProfileLikelihood.$s.root $outfolder/higgsCombineLEE_k01.ProfileLikelihood.mH*.$s.root 
wait
$CMSSW_DIR/src/diphotons/Analysis/macros/combineall.sh $outfolder  02 -M ProfileLikelihood  --toysFile $toysFile  -t $ntoys -n LEESpin0 -s $1 --pvalue --significance  --hadd 
hadd -f $outfolder/higgsCombineLEE_k02.ProfileLikelihood.$s.root $outfolder/higgsCombineLEE_k02.ProfileLikelihood.mH*.$s.root 
wait
hadd -f $outfolder/higgsCombineLEE_kall.ProfileLikelihood.$s.root $outfolder/higgsCombineLEE_k*.ProfileLikelihood.$s.root 
cp $outfolder/higgsCombineLEE_k*.root $infolder/. 


