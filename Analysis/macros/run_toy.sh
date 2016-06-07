#!/bin/bash

set -e
#$-e /dev/null 
#$-o /dev/null
set -x
JOBDIR=sgejob-$JOB_ID
echo $JOB_ID
mkdir -p /scratch/mquittna/$JOBDIR
mydir=/scratch/mquittna/$JOBDIR
##mydir=$(dirname $(which $0))

CMSSW_DIR=/mnt/t3nfs01/data01/shome/mquittna/CMSSW/CMSSW_7_6_3
LOC_PATH=src/diphotons/Analysis/macros
source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_DIR/src/
eval `scramv1 runtime -sh`
if test $? -ne 0; then
	   echo "ERROR: Failed to source scram environment" >&2
	      exit 1
	  fi
cd $mydir

## full_analysis_anv1_v13/bias_study_toys_from_fit_unbinned.root
input=$1 && shift
output=$1 && shift
toy=$1 && shift
ntoys=$1 && shift
#     --fit-name 2D \
cp $input $mydir/.
outname=$(basename $output)
outdir=$(dirname $output)
echo $outname
echo $outdir
$CMSSW_DIR/$LOC_PATH/bkg_bias.py --n-toys $ntoys \
    --store-new-only \
    --components pp --models dijet \
    --read-ws $input  -o $mydir/$outname \
    --fit-toys \
    --fit-name cic2 \
    --saveas root,png \
    --test-range 950,1000 --test-range 1000,1100 --test-range 1100,1200 --test-range 1200,1800 --test-range 1800,2500 --test-range 2500,3500 --test-range 3500,4500 --test-range 500,550 --test-range 550,600 --test-range 600,650 --test-range 650,700 --test-range 700,750 --test-range 750,800 --test-range 800,900 --test-range 900,950 --test-range 4500,5500 --first-toy $toy \
    $@


##     --fit-range 300,3000 --saveas png --test-range 1000,3000 --test-range 500,550 --test-range 550,600 --test-range 600,650 --test-range 650,700 --test-range 700,750 --test-range 750,800 --test-range 800,900 --test-range 900,1000 --first-toy $toy \

##    --test-range 1000,1200 --test-range 1200,1800 --test-range 1800,2500 --test-range 2500,3500 --test-range 3500,4500 --test-range 500,550 --test-range 550,600 --test-range 600,650 --test-range 650,700 --test-range 700,750 --test-range 750,800 --test-range 800,900 --test-range 900,1000 --test-range 4500,5500 --first-toy $toy \

#mkdir -p $outdir
cp -p $mydir/$outname $outdir/$outname
#cp -p $mydir/*.png $outdir 
#cp -p $mydir/*.root $outdir 
