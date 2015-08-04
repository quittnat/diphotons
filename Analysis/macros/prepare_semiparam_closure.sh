#!/bin/bash

set -x 

# generate MC truth model for 2D fit
combineCards.py --xc .*EBE[BE]$ \
full_analysis_anv1_v19_0_0_mgg_split_shapes_lumi5/datacard_full_analysis_anv1_v19_mgg_split_shapes_lumi5_grav_02_5000.txt \
| grep -v group > full_analysis_anv1_v19_0_0_mgg_semiparam_split_shapes_lumi5_control.txt
 
combineCards.py \
full_analysis_anv1_v19_0_0_mgg_truth_shapes_truth_templates_lumi5/datacard_full_analysis_anv1_v19_mgg_truth_shapes_truth_templates_lumi5_grav_02_5000.txt \
full_analysis_anv1_v19_0_0_mgg_semiparam_split_shapes_lumi5_control.txt \
     | grep -v group | sed 's%ch[12]_%%g' > full_analysis_anv1_v19_0_0_mgg_semiparam_split_shapes_lumi5_truth.txt

combine -M GenerateOnly full_analysis_anv1_v19_0_0_mgg_semiparam_split_shapes_lumi5_truth.txt -n _truth -m 0 -t -1 --saveToys -L libdiphotonsUtils

##combine -M GenerateOnly full_analysis_anv1_v19_2D_split_shapes_lumi_5_truth.txt -n _truth_r0009 -m 0 -t -1 --saveToys -L libdiphotonsUtils --expectSignal 0.009

sed 's%rate.*%rate 1 1 0 1 1 1 0 1 1 1%' full_analysis_anv1_v19_0_0_mgg_semiparam_split_shapes_lumi5_truth.txt | grep -v 'group' > full_analysis_anv1_v19_0_0_mgg_split_shapes_lumi5_truth_nopp.txt \

combine -M GenerateOnly full_analysis_anv1_v19_0_0_mgg_split_shapes_lumi5_truth_nopp.txt -n _truth_nopp -m 0 -t -1 --saveToys -L libdiphotonsUtils
