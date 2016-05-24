
## makes datasets
##./templates_maker.py --load templates_maker.json,templates_maker_prepare.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data   -o full_analysis_moriond16v1_sync_v4_data/bias_study_input.root --only-subset cic2 --signals '{}'

## throw toys for EBEB
##lumi_factor is kfactor*lumi 1.5*10/fb
##EBEB and EBEE separate because of different fit ranges
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=10000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb   --observable 'mgg[4000,230,10000]' --test-categories EBEB &
wait
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=10000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb   --observable 'mgg[3400,320,10000]' --test-categories EBEE &
wait
## throw asimov toy to check fit
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB_asimov.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb --observable 'mgg[4000,230,10000]' --test-categories EBEB  &
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE_asimov.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb --observable 'mgg[3400,320,10000]' --test-categories EBEE  &


wait

## fit the toys 
./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_2 1000 2 --observable 'mgg[4000,230,10000]' --fit-range 230,10000 & 
./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEE_2 1000 2 --observable 'mgg[3400,320,10000]' --fit-range 320,10000 & 
##qsub system
#./submit_toys.sh 8nm full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned_EBEB.root  full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned/EBEB_2 500 2 --observable 'mgg[4000,230,10000]' --fit-range 230,10000 & 

## fit and plot asimov
#./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB_asimov.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_asimov 1 1  --observable 'mgg[4000,230,10000]' --fit-range 230,10000 --plot-toys-fits --n-toys -1 -O . --plot-fit-bands & 

#cp full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_asimov/*.png /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/. 
#cp full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_1/*.png /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/. 


wait
#./hadd_toys.sh full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_2
#./bkg_bias.py --analyze-bias --bias-files full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/toys.root --bias-labels fit -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/ 
#./bkg_bias.py --analyze-bias --bias-files full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/toys.root --bias-labels fit -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/ 
