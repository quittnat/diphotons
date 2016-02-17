#################prepare templates####################################
#./templates_maker.py --input-dir=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v2_data/  -o  templates_moriond16v1_sync_v2_data.root --prepare-data --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json
#./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws templates_moriond16v1_sync_v2_data.root,templatesdataMCv3.root --mix-templates --mix-mc  --store-new-only -o mixdataMCv3.root

################ compare templates#################################


./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws templates_moriond16v1_sync_v2_data.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/ -o compared_moriond16v1_sync_v2_data.root --compare-templates --fixed-massbins --template-binning="0.0,0.1,5.0,15.0" --store-new-only --lumi 2.56

#./templates_fitter.py --load templates_fitter.json,lumi.json --fit-mc --read-ws fb24/templatesdataMCv3.root,fb24/mixdataMCv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_24fb/fullmassrange_9b/ -o fitv3_fullmassrange_9b.root --compare-templates --fit-massbins 1,1,0 --template-binning="0.0,0.1,5.0,15.0" --store-new-only --lumi 2.56
####study mixing parameters####################################
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,mixdataMCv3_pt100.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt100/ -o fitv3_fixedmb_9b_pt100.root --compare-templates --fixed-massbins --template-binning="0.0,0.1,5.0,15.0" --store-new-only

#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatch2up.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch2up/ -o fitv3_fixedmb_9b_pt75_RndMatch2up.root --compare-templates --fixed-massbins --template-binning="0.0,0.1,5.0,15.0" --store-new-only



#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3_2.root,mixdataMCv3_2.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_2_26fb/fit_fullmassrange_9b_200_300/ -o fitv3_2_9b_fullmassrange.root --compare-templates --fit-massbins 1,1,0 --template-binning="0.0,0.1,5.0,15.0" --store-new-only --saveas pdf,convert_png,root

#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws fb24_1612/templatesdataMCv11.root,mixdataMCv11.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v11_26fb/fit_fullmassrange/ -o fitv11_fixedmb_fullmassrange.root --compare-templates --fit-massbins 1,1,0 --template-binning="0.0,0.1,5.0,15.0" --store-new-only --saveas pdf,convert_png,root
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws fb24/templatesdataMCv3.root,fb24/mixdataMCv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_24fb/test_760EBEB_700_800/ -o fitv3_760EBEB_700_800.root --compare-templates --fixed-massbins --template-binning="0.0,0.1,5.0,15.0" --store-new-only 







#################fits##################

###################3comp########################################

#./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_3comp_datapp_MCpf_toData/  --purity-sigregion --fit-mc -o fittedv3_fixedmb_9b_3comp_datapp_MCpf_toData.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 


#./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws fb24/templatesdataMCv3.root,fb24/mixdataMCv3.root,fb24/fitv3_fixedmb_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_24fb/fixedmb_9b_3comp/  --purity-sigregion -o fittedv3_fixedmb_9b_3comp_data.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only  --lumi 2.56
#./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws fb24/templatesdataMCv3.root,fb24/mixdataMCv3.root,fitv3_760EBEB_700_800.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_24fb/test_760EBEB_700_800/  --purity-sigregion -o fittedv3_data_760EBEB_700_800.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only  --lumi 2.56


#.c/templates_fitter.py --load templates_fitter.json,lumi.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_3comp_mc/ --fit-mc  --purity-sigregion -o fittedv3_fixedmb_9b_3comp_mc.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --lumi 2.56
#./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b/  --purity-sigregion -o fittedv3_fixedmb_9b_data.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --lumi 2.56
#./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b/ --fit-mc --purity-sigregion -o fittedv3_fixedmb_9b_mc.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --lumi 2.56 

#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_2comp_mc/ --fit-mc --purity-sigregion -o fittedv3_fixedmb_9b_mctruth.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_mctruth --store-new-only --lumi 2.56

#./templates_fitter.py --load templates_fitter.json,lumi2.json --read-ws fb24/templatesdataMCv3.root,fb24/mixdataMCv3.root,fitv3_fixedmb_9b.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_2_26fb/fixedmb_9b_3comp/  --purity-sigregion -o fittedv3_data_fixedmb_9b.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only  --lumi 2.56  --saveas pdf,convert_png,root
#./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws fb24_1612/templatesdataMCv11.root,mixdataMCv11.root,fitv11_fixedmb_fullmassrange.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v11_26fb/fit_fullmassrange/  --purity-sigregion -o fittedv11_data_fullmassrange_9b.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only  --lumi 2.56  --saveas pdf,convert_png,root

####study mixing parameters####################################
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatch2up.root,fitv3_fixedmb_9b_pt75_RndMatch2up.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch2up/  -o fittedv3_fixedmb_9b_data_pt75_RndMatch2up.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatch2up.root,fitv3_fixedmb_9b_pt75_RndMatch2up.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch2up/ -o fittedv3_fixedmb_9b_mc_pt75_RndMatch2up.root --fit-mc --nominal-fit --fixed-massbins   --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatch2up.root,fitv3_fixedmb_9b_pt75_RndMatch2up.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch2up/ -o fittedv3_fixedmb_9b_mctruth_pt75_RndMatch2up.root --fit-mc  --nominal-fit --fixed-massbins   --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_mctruth --store-new-only 

#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatchlow.root,fitv3_fixedmb_9b_pt75_RndMatch1low.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch1low/   -o fittedv3_fixedmb_9b_data_pt75_RndMatch1low.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatchlow.root,fitv3_fixedmb_9b_pt75_RndMatch1low.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch1low/ --purity-sigregion -o fittedv3_fixedmb_9b_mc_pt75_RndMatch1low.root --fit-mc --nominal-fit --fixed-massbins   --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt75_RndMatchlow.root,fitv3_fixedmb_9b_pt75_RndMatch1low.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt75_RndMatch1low/ -o fittedv3_fixedmb_9b_mctruth_pt75_RndMatch1low.root --fit-mc --purity-sigregion --nominal-fit --fixed-massbins   --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_mctruth --store-new-only 

#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt100.root,fitv3_fixedmb_9b_pt100.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt100/ --purity-sigregion  -o fittedv3_fixedmb_9b_data_pt100.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt100.root,fitv3_fixedmb_9b_pt100.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt100/ --purity-sigregion -o fittedv3_fixedmb_9b_mc_pt100.root --fit-mc --nominal-fit --fixed-massbins   --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3_pt100.root,fitv3_fixedmb_9b_pt100.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_pt100/ -o fittedv3_fixedmb_9b_mctruth_pt100.root --fit-mc --purity-sigregion --nominal-fit --fixed-massbins   --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_mctruth --store-new-only 

##############4bins##########################
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,mixdataMCv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_4b/ -o fitv3_fixedmb_4b.root --compare-templates --fixed-massbins --template-binning="0.0,5.0,15.0" --store-new-only
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_4b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_4b/ -o fittedv3_fixedmb_4b_data.root --nominal-fit --fixed-massbins  --template-binning="0.0,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_4b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_4b/ -o fittedv3_fixedmb_4b_mc.root  --fit-mc --nominal-fit --fixed-massbins  --template-binning="0.0,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCv3.root,mixdataMCv3.root,fitv3_fixedmb_4b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_4b/ -o fittedv3_fixedmb_4b_mctruth.root  --fit-mc --nominal-fit --fixed-massbins  --template-binning="0.0,5.0,15.0" --fit-template unrolled_mctruth --store-new-only 



#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_3comp_mc.root,fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb2_9b_3comp_sigRegion_closure/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction --lumi 2.56

############plot purity closure########################
#standard
#./templates_fitter.py --load templates_fitter.json  --read-ws templatesdataMCv3.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_data.root,fittedv3_fixedmb_9b_mc.root,fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction

#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws fb24/templatesdataMCv3.root,fb24/fitv3_fixedmb_9b.root,fb24/fittedv3_fixedmb_9b_3comp_mc.root,fb24/fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_24fb/fixedmb_9b/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction

#./templates_fitter.py --load templates_fitter.json  --read-ws fb24/templatesdataMCv3.root,fb24/fitv3_fixedmb_9b.root,fb24/fittedv3_fixedmb_9b_3comp_data.root,fb24/fittedv3_fixedmb_9b_3comp_mc.root,fb24/fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_24fb/fixedmb_9b_3comp/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction --fit-mc 
#3 comp


#./templates_fitter.py --load templates_fitter.json,lumi.json  --read-ws fb24/templatesdataMCv3.root,fb24/fitv3_fixedmb_9b.root,fb24/fittedv3_fixedmb_9b_3comp_data.root,fb24/fittedv3_fixedmb_9b_3comp_mc.root,fb24/fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_2_26fb/fixedmb_9b_3comp/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction --fit-mc --lumi 2.56
#./templates_fitter.py --load templates_fitter.json,lumi.json --saveas png,root --read-ws fb24/templatesdataMCv3.root,fb24/fitv3_fixedmb_9b.root,fb24/fittedv3_fixedmb_9b_mctruth.root,fb24/fittedv3_fixedmb_9b_3comp_mc.root,fb24/fittedv3_fixedmb_9b_3comp_data.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_2_26fb/fixedmb_9b_3comp/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction  --lumi 2.56

#sigregion

#./templates_fitter.py --load templates_fitter.json,lumi.json  --read-ws fb24/templatesdataMCv3.root,fb24/fitv3_fixedmb_9b.root,fb24/fittedv3_fixedmb_9b_3comp_data.root,fb24/fittedv3_fixedmb_9b_3comp_mc.root,fb24/fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_2_26fb/fixedmb_9b_3comp/ --fit-mc --plot-purity --plot-closure template_mix --plot-purityvalue fraction --purity-sigregion --lumi 2.56  --saveas pdf,convert_png,root
#./templates_fitter.py --load templates_fitter.json,lumi.json --saveas png,root   --read-ws fb24/fitv3_fixedmb_9b.root,fb24/fittedv3_fixedmb_9b_3comp_data.root,fb24/fittedv3_fixedmb_9b_3comp_mc.root,fb24/fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3_2_26fb/fixedmb_9b_3comp/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction  --purity-sigregion --lumi 2.56 --saveas pdf,convert_png,root

############plot purity mctruth########################
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_mc.root,fittedv3_fixedmb_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b/  --plot-purity --plot-closure mctruth --plot-purityvalue fraction
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,fitv3_fixedmb_4b.root,fittedv3_fixedmb_4b_mc.root,fittedv3_fixedmb_4b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_4b/  --plot-purity --plot-closure mctruth --plot-purityvalue fraction
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesdataMCv3.root,fitv3_mb9_9b.root,fittedv3_mb9_9b_mc.root,fittedv3_mb9_9b_mctruth.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/notfixedyet/mb9_9b/ --plot-purity --plot-closure mctruth --plot-purityvalue fraction

####################################################
#./templates_fitter.py --load templates_fitter.json --read-ws templatesIDv2_selv2_00112003.root,mix25nsdataMCv2_selv2_00112003.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2_9b_00112003/ -o fitIDv2_selv2_9b_00112003.root --compare-templates --fit-massbins 15,15,0 --template-binning="0.0,0.1,5.0,15.0" --store-new-only
#./templates_fitter.py --load templates_fitter.json --read-ws templatesIDv2_selv2_00112003.root,mix25nsdataMCv2_selv2_00112003.root,fitIDv2_selv2_9b_00112003.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2_9b_00112003/ -o fittedmcIDv2_selv2_9b_00112003.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --fit-mc
#./templates_fitter.py --load templates_fitter.json --read-ws templatesIDv2_selv2_00112003.root,mix25nsdataMCv2_selv2_00112003.root,fitIDv2_selv2_9b_00112003.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2_9b_00112003_data/ -o fittedmcIDv2_selv2_9b_00112003_data.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only 

#./templates_fitter.py --load templates_fitter.json --read-ws templatesIDv2_selv2_00112003.root,mix25nsdataMCv2_selv2_00112003.root,fitIDv2_selv2_9b_00112003.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2_9b_00112003/ -o fittedmcIDv2_selv2_9b_00112003_mctruth.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_mctruth --store-new-only --fit-mc
#./templates_fitter.py --load templates_fitter.json --fit-mc --read-ws templatesIDv2_selv2_00112003.root,fittedmcIDv2_selv2_9b_00112003.root,fittedmcIDv2_selv2_9b_00112003_mctruth.root,fitIDv2_selv2_9b_00112003.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2_9b_00112003/ -o purity_00112003.root --plot-purity --plot-closure template_mix --plot-purityvalue fraction

#./templates_maker.py --input-dir=outputSinglePhoIDv2_selv1/ -o templatesdataMCSinglePhoIDv2_selv1.root --prepare-nosignal --only-subset="singlePho" --load templates_maker.json,templates_maker_fits.json
#./templates_maker.py --input-dir=output2dIDv2_selv1/ -o templatesdataMCIDv2_selv1.root --prepare-nosignal --only-subset="2D" --load templates_maker.json,templates_maker_fits.jso
#./templates_maker.py --load templates_maker_fits.json,templates_maker.json --read-ws templatesdataMCSinglePhoIDv2_selv1.root,templatesdataMCIDv2_selv1.root --mix-templates --store-new-only -o mix25nsdatav2_selv1.root
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv2.root,mix25nsdataMCv2_selv2.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2.56b_mc/ -o fitdataIDv2_selv2.56b_mc.root --compare-templates --fit-massbins 15,15,0 --template-binning="0.0,5.0,15.0" --store-new-only
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv2.root,mix25nsdataMCv2_selv2.root,fitdataIDv2_selv2.56b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2.56b/ -o fitteddataIDv2_selv1_4b.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,5.0,15.0" --fit-template unrolled_template_mix --store-new-only
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv2.root,mix25nsdataMCv2_selv2.root,fitdataIDv2_selv2.56b_mc.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2.56b_mc/ -o fitteddataIDv2_selv1_4b_mctruth.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,5.0,15.0" --fit-template unrolled_mctruth --store-new-only
#./templates_maker.py --load templates_maker_fits.json --read-ws templatesdataMCIDv2_selv2.root,mix25nsdatav2_selv2.root,fitteddataIDv2_selv2.56b.root,fitdataIDv2_selv2.56b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv2.56b/ -o purity_dataIDv2_selv2_2comp_4b.root --plot-purity --plot-closure template_mix --plot-purityvalue fraction
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv1.root,mix25nsdataMCv2_selv1.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv1dataMC_9b/ -o fitdataMCIDv2_selv1_9b.root --compare-templates --fit-massbins 15,15,0 --template-binning="0.0,0.1,5.0,15.0" --store-new-only

#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv1.root,mix25nsdataMCv2_selv1.root,fitdataMCIDv2_selv1_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv1dataMC_9b/ -o fitteddataMCIDv2_selv1_9b.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv1.root,mix25nsdataMCv2_selv1.root,fitdataMCIDv2_selv1_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv1dataMC_9b/ -o fitteddataMCIDv2_selv1_9b2.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only
#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv1.root,mix25nsdataMCv2_selv1.root,fitdataMCIDv2_selv1_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv1dataMC_9b/ -o fitteddataMCIDv2_selv1_9b3.root --nominal-fit --fit-massbins 15,15,0  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_mctruth --store-new-only

#./templates_fitter.py --load templates_fitter.json --read-ws templatesdataMCIDv2_selv1.root,mix25nsdataMCv2_selv1.root,fitteddataMCIDv2_selv1_9b.root,fitteddataMCIDv2_selv1_9b2.root,fitteddataMCIDv2_selv1_9b3.root,fitdataMCIDv2_selv1_9b.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_runD_v2/selv1dataMC_9b/ -o purity_dataIDv2_selv1_2comp_9b_all.root --plot-purity --plot-closure template_mix --plot-purityvalue fraction




