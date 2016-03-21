#!/bin/bash
set -e
set -x
name=_spin2_k001_760GeV_13TeV
mass="760"
##datacard_file="datacard_combined_spin2_wnuis_unblind_grav_001_760.txt"
##name=_spin2_k001_750GeV_8_13TeV
##mass="750"
##datacard_file="datacard_combined_813_spin2_unblind_grav_001_750.txt"
infolder="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/localPVal$name"
JOBDIR=sgejob-$JOB_ID
echo $JOB_ID
mkdir -p /scratch/mquittna/$JOBDIR
outfolder=/scratch/mquittna/$JOBDIR
cp $infolder/$datacard_file $outfolder/.
datacard="$outfolder/$datacard_file"
replaceNames=1
#start all q with 100 jobs per coupling
###$ -q all.q
ntoys=400
#short q only for jobs above 100 150 each
#$ -q short.q
#$-e /dev/null 
#$-o /dev/null
####################$-cwd
CMSSW_DIR=/shome/mquittna/CMSSW/CMSSW_7_1_5


source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
	  
cd $outfolder
#gfal-ls $toysFileSE
combine -M ProfileLikelihood  -L libdiphotonsUtils  -m $mass -t $ntoys -n $name -s $1 --pvalue --significance $datacard

gfal-copy file:///$outfolder/higgsCombine$name.ProfileLikelihood.mH$mass.$1.root srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/localPVal$name/higgsCombine$name.ProfileLikelihood.mH$mass.$1.root


