
## makes datasets
./templates_maker.py --load templates_maker.json,templates_maker_prepare.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v4_data   -o full_analysis_moriond16v1_sync_v4_data/bias_study_input.root --only-subset cic2 --signals '{}'

## throw toys for EBEB
##lumi_factor is kfactor*lumi 1.5*10/fb
##EBEB and EBEE separate because of different fit ranges
./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=1000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB.root  -O ~/www/exo/moriond16/full_analysis_moriond16v1_sync_v4_data/bias_study --observable 'mgg[4000,230,10000]' --test-categories EBEB &

## throw asimov toy to check fit
## ./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_0T_sync_v6_data/bias_study_input.root -o full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned_EBEB_asimov.root  -O ~/www/exo/moriond16/full_analysis_moriond16v1_0T_sync_v6_data/bias_study --observable 'mgg[4000,230,10000]' --test-categories EBEB  &


wait

## fit the toys 
./submit_toys.sh all.q full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned_EBEB.root  full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned/EBEB_2 500 2 --observable 'mgg[4000,230,10000]' --fit-range 230,10000 & 

## fit and plot asimov
## ./submit_toys.sh 8nm full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned_wslope_EBEB_asimov.root  full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned/EBEB_wslope 1 1 --observable 'mgg[4000,230,10000]' --fit-range 230,10000 --plot-toys-fits --n-toys -1 -O . --plot-fit-bands & 


## ./submit_toys.sh 8nm full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned_EBEE.root  full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned/EBEE 500 2 --observable 'mgg[3400,330,10000]' --fit-range 330,10000 &

wait
