#################prepare templates####################################
#old but maybe useful
###./templates_maker.py --input-dir=./full_analysis_spring15v2_7415_v1MC_v5data/  -o   full_analysis_spring15v2_7415_v1MC_v5dataMC.root  --prepare-nosignal --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json
###./templates_maker.py --input-dir=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v2_data/  -o  templates_moriond16v1_sync_v2_data.root --prepare-data --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json
###./templates_maker.py --input-dir=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v5_data/  -o  templates_7415v2_v5_data_ecorr_pas.root --prepare-data --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json
###./templates_maker.py --input-dir=/afs/cern.ch/user/m/musella/public/workspace/exo/single_photon_spring15_7415v2_sync_v1_data/  -o  templates_single_photon_7415v2_v1_data.root --prepare-data --only-subset="singlePho" --load templates_maker.json,templates_maker_prepare.json
#./templates_maker.py --input-dir=/shome/mquittna/CMSSW/CMSSW_7_6_3/src/diphotons/Analysis/config/singlePhoton_data_76_4/  -o  templates_moriond16v1_sync_v2_data_singlephoton.root --prepare-data  --only-subset="singlePho" --load templates_maker.json,templates_maker_prepare.json

#./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws  templates_moriond16v1_sync_v2_data_singlephoton.root,templates_moriond16v1_sync_v2_data.root --mix-templates  --store-new-only -o mix_moriond16v1_sync_v2_data.root

##./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws templates_single_photon_7415v2_v1_data.root,templates_7415v2_v5_data_ecorr_pas.root --mix-templates  --store-new-only -o mix_7415v2_v5_data_ecorr_pas.root

###./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws full_analysis_spring15v2_7415_v1MC_v1dataMC_singlephoton.root,full_analysis_spring15v2_7415_v1MC_v5dataMC.root --mix-templates --mix-mc --store-new-only -o mix_7415v2_v5_dataMC_ecorr_pas.root

################ compare templates#################################

##full mass range
./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws templates_moriond16v1_sync_v2_data.root,mix_moriond16v1_sync_v2_data.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/ -o compared_moriond16v1_sync_v2_data_fullmass.root --compare-templates --fit-massbins 1,1,0 --template-binning="0.0,0.1,5.0,15.0" --no-mctruth --store-new-only --lumi 2.7
#./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws templates_7415v2_v5_data_ecorr_pas.root,mix_7415v2_v5_data_ecorr_pas.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_templates_7415v2_v5_data_ecorr_pas/  -o compared_templates_7415v2_v5_data_ecorr_pas_fullmass.root  --compare-templates --fit-massbins 1,1,0 --template-binning="0.0,0.1,5.0,15.0" --no-mctruth --store-new-only --lumi 2.7

##fixed mass bins

./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws templates_moriond16v1_sync_v2_data.root,mix_moriond16v1_sync_v2_data.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/ -o compared_moriond16v1_sync_v2_data.root --compare-templates --fixed-massbins --template-binning="0.0,0.1,5.0,15.0" --no-mctruth --store-new-only --lumi 2.7 --blind |tee output_comp_moriond.txt
#./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws templates_7415v2_v5_data_ecorr_pas.root,mix_7415v2_v5_data_ecorr_pas.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_templates_7415v2_v5_data_ecorr_pas/  -o compared_templates_7415v2_v5_data_ecorr_pas.root  --compare-templates --fixed-massbins --template-binning="0.0,0.1,5.0,15.0" --no-mctruth --store-new-only --lumi 2.7 --blind |tee output_comp_7415_v5.txt


#################fits##################

###################3comp########################################

./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws compared_moriond16v1_sync_v2_data.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/  --purity-sigregion -o fitted_moriond16v1_sync_v2_data.root  --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --lumi 2.7 --saveas pdf,convert_png,root |tee output_fit_moriond.txt

#./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --read-ws compared_templates_7415v2_v5_data_ecorr_pas.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_templates_7415v2_v5_data_ecorr_pas/  --purity-sigregion -o fitted_7415v2_v5_data_ecorr_pas.root  --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --lumi 2.7 --saveas pdf,convert_png,root |tee output_fit_7415_v5.txt


############plot purity closure########################
#./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --saveas pdf,convert_png,root --read-ws templates_7415v2_v5_data_ecorr_pas.root,compared_templates_7415v2_v5_data_ecorr_pas.root,fitted_7415v2_v5_data_ecorr_pas.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_templates_7415v2_v5_data_ecorr_pas/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction --no-mctruth --lumi 2.7 --full-error -o purity_7415v2_v5_data_ecorr_pas.root --store-new-only --blind

./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --saveas pdf,convert_png,root --read-ws templates_moriond16v1_sync_v2_data.root,compared_moriond16v1_sync_v2_data.root,fitted_moriond16v1_sync_v2_data.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction --no-mctruth --lumi 2.7 --full-error -o purity_moriond16v1_sync_v2_data.root --store-new-only --blind
#sigregion
#./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --saveas pdf,convert_png,root --read-ws templates_7415v2_v5_data_ecorr_pas.root,compared_templates_7415v2_v5_data_ecorr_pas.root,fitted_7415v2_v5_data_ecorr_pas.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_templates_7415v2_v5_data_ecorr_pas/ --plot-purity --plot-closure template_mix --purity-sigregion --plot-purityvalue fraction --no-mctruth --lumi 2.7 --full-error -o purity_sigregion_7415v2_v5_data_ecorr_pas.root --store-new-only --blind

./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --saveas pdf,convert_png,root --read-ws templates_moriond16v1_sync_v2_data.root,compared_moriond16v1_sync_v2_data.root,fitted_moriond16v1_sync_v2_data.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_moriond16v1_sync_v2_data/ --plot-purity --plot-closure template_mix --purity-sigregion --plot-purityvalue fraction --no-mctruth --lumi 2.7 --full-error -o purity_sigregion_moriond16v1_sync_v2_data.root --store-new-only --blind

wait
root  plot_chargediso_comp_cmssw.C 

