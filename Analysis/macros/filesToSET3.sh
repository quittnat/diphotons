#!/bin/bash
njobs=$1
for mass in $(seq 500 $njobs); do
	if [ `echo "$mass % 2" | bc` -eq 0 ] ; then
		gfal-copy  file:////shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/full_analysis_moriond16v1_sync_v4_data_cic2_default_shapes_spin2_wnuis_lumi_2.69/full_analysis_moriond16v1_sync_v4_data_cic2_default_shapes_spin2_wnuis_lumi_2.69_bkgnbias_grav_01_$mass.root   srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/full_analysis_moriond16v1_sync_v4_data_cic2_default_shapes_spin2_wnuis_lumi_2.69/full_analysis_moriond16v1_sync_v4_data_cic2_default_shapes_spin2_wnuis_lumi_2.69_bkgnbias_grav_01_$mass.root 
	fi
done
