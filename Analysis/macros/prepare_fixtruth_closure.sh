#!/bin/bash

set -x 

# generate MC truth model for 2D fit
combineCards.py --xc .*EBE[BE]$ \
full_analysis_anv1_v19_2D_split_shapes_asimovfixtruthpfEBEB300_lumi_5/datacard_full_analysis_anv1_v19_2D_split_shapes_asimovfixtruthpfEBEB300_lumi_5_grav_02_5000.txt \
    | grep -v group > full_analysis_anv1_v19_2D_split_shapes_semiparam_fixtruth300_lumi_5_control.txt

combineCards.py \
    full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_fixtruth300_lumi_5/datacard_full_analysis_anv1_v19_2D_truth_shapes_truth_templates_semiparam_fixtruth300_lumi_5_grav_02_5000.txt\
    full_analysis_anv1_v19_2D_split_shapes_semiparam_fixtruth300_lumi_5_control.txt \
    | grep -v group | sed 's%ch[12]_%%g' > full_analysis_anv1_v19_2D_split_shapes_semiparam_fixtruth300_lumi_5_truth.txt
combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_semiparam_fixtruth300_lumi_5_truth.txt -n _fixtruth300 -m 0 -t -1 --saveToys --saveWorkspace -L libdiphotonsUtils 

##combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth.txt -n _truth_r0009 -m 0 -t -1 --saveToys -L libdiphotonsUtils --expectSignal 0.009

##sed 's%rate.*%rate 1 1 0 1 1 1 0 1 1 1%' full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth.txt | grep -v 'group' > full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth_nopp.txt

##combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth_nopp.txt -n _truth_nopp -m 0 -t -1 --saveToys -L libdiphotonsUtils
cd  full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog300_lumi_5 
combine -L libdiphotonsUtils datacard_full_analysis_anv1_v19_2D_split_shapes_semiparam_adhocnormlog300_lumi_5_grav_02_5000.txt -M MultiDimFit --redefineSignalPOIs pf_EBEB_frac,pf_EBEE_frac,pp_EBEE_frac,pp_EBEB_frac --freezeNuisances r --setPhysicsModelParameters r=0 -n _fit_fixtruth -t -1 -m 0 --toysFile ../higgsCombine_fixtruth300.GenerateOnly.mH0.123456.root --saveWorkspace --saveToys
##root fit_bias.cpp
