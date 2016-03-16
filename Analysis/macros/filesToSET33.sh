#!/bin/bash
njobs=100
for mass in $(seq 0 $njobs); do
#	if [ `echo "$mass % 2" | bc` -eq 0 ] ; then
		gfal-copy  file:////shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spinall_wnuis_unblind_m_2000/higgsCombineLEE_kall.ProfileLikelihood.$mass.root   srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/combined_spinall_wnuis_unblind_m_2000/higgsCombineLEE_kall.ProfileLikelihood.$mass.root
		gfal-copy  file:////shome/mquittna/CMSSW/CMSSW_7_1_5/src/diphotons/Analysis/macros/combined_spinall_wnuis_unblind_m_3000/higgsCombineLEE_kall.ProfileLikelihood.$mass.root   srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/mquittna/combined_spinall_wnuis_unblind_m_3000/higgsCombineLEE_kall.ProfileLikelihood.$mass.root
#	fi
done
