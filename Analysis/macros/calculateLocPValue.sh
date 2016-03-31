#!/bin/bash
set -e
set -x
name=_spin2_k001_520GeV_13TeV_freezeenergyscalecorr
inname=_spin2_k001_520GeV_13TeV
mass="520"
datacard_file="datacard_combined_spin2_wnuis_unblind_grav_001_520.txt"
##name=_spin2_k001_600GeV_13TeV
#inname=_spin2_k001_600GeV_13TeV
#name=_spin2_k001_600GeV_13TeV_freezeenergyscalecorr
#mass="600"
#datacard_file="datacard_combined_spin2_wnuis_unblind_grav_001_600.txt"
##datacard_file="datacard_combined_spin2_wnuis_unblind_grav_001_760.txt"
#mass="760"
#name=_spin2_k001_760GeV_13TeV
##name=_spin2_k001_750GeV_8_13TeV
##mass="750"
##datacard_file="datacard_combined_813_spin2_unblind_grav_001_750.txt"
infolder="/shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/localPVal$inname"
JOBDIR=sgejob-$JOB_ID
echo $JOB_ID
mkdir -p /scratch/mquittna/$JOBDIR
outfolder=/scratch/mquittna/$JOBDIR
cp $infolder/$datacard_file $outfolder/.
datacard="$outfolder/$datacard_file"
replaceNames=1
#start all q with 100 jobs per coupling
#$ -q all.q
ntoys=450
njobs=100
#short q only for jobs above 100 150 each
###$ -q short.q
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
#gfal-ls $toysFile 
for job in $(seq 0 $njobs);do 
job_new=$JOB_ID$job
echo $job_new
combine -M ProfileLikelihood  -L libdiphotonsUtils  -m $mass -t $ntoys -n $name -s $job_new --pvalue --significance --freezeNuisances energyScaleEBEEeig1,energyScaleEBEEeig2,energyScaleEBEBeig1,energyScaleEBEBeig2,energyScaleZeroT $datacard
##combine -M ProfileLikelihood  -L libdiphotonsUtils  -m $mass -t $ntoys -n $name -s $1 --pvalue --significance $datacard
gfal-copy file:///$outfolder/higgsCombine$name.ProfileLikelihood.mH$mass.$job_new.root srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/localPVal$name/higgsCombine$name.mH$mass.$job_new.root
done



