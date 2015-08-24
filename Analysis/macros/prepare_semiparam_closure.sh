#!/bin/bash

set -x 

# generate MC truth model for 2D fit
combineCards.py --xc .*EBE[BE]$ \
	full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5/datacard_full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5_grav_02_1500.txt\
    | grep -v group > full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_control.txt

combineCards.py \
    full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_adhocnormlog270_lumi_5/datacard_full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_adhocnormlog270_lumi_5_grav_02_1500.txt \
    full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_control.txt \
    | grep -v group | sed 's%ch[12]_%%g' > full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_truth.txt
#combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_truth.txt -n _truth270 -m 0 -t -1 --saveToys --saveWorkspace -L libdiphotonsUtils 

##combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_truth.txt -n _truth_r0009 -m 0 -t -1 --saveToys -L libdiphotonsUtils --expectSignal 0.009

sed 's%rate.*%rate 1 1 0 1 1 1 0 1 1 1%' full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_truth.txt | grep -v 'group' > full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_truth_nopp.txt

combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_adhocnormlog270_lumi_5_truth_nopp.txt -n _truth_nopp -m 0 -t -1 --saveToys -L libdiphotonsUtils
##cd  full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5 
##combine -L libdiphotonsUtils datacard_full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog270_lumi_5_grav_02_5000.txt -M MultiDimFit --redefineSignalPOIs pf_EBEB_frac,pf_EBEE_frac,pp_EBEE_frac,pp_EBEB_frac --freezeNuisances r --setPhysicsModelParameters r=0 -n _fit_truth -t -1 -m 0 --toysFile ../higgsCombine_truth270.GenerateOnly.mH0.123456.root --saveWorkspace 
#root fit_bias.cpp
