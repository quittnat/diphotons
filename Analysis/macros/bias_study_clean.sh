
## makes datasets
#./templates_maker.py --load templates_maker.json,templates_maker_prepare.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring16v1_sync_v1_2705_cert   -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input.root --only-subset cic2 --signals '{}'
./templates_maker.py --load templates_maker.json,templates_maker_prepare.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/   -o full_analysis_moriond16v1_sync_v5_extra_vars_data//bias_study_input.root --only-subset cic2 --signals '{}'
##apply one cut to truth pp in cic2, rest is as before
##(mass<550 && weight < 0.02) || (mass < 1100 && weight < 0.001) || (mass < 2200 && weight < 2.e-4) || (mass < 4400 && weight < 1e-5) ||( mass >= 4400)
#./templates_maker.py --load templates_maker.json,templates_maker_prepare.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring16v1_sync_v1_2705_cert   -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input_weightcut.root --only-subset cic2 --signals '{}'
wait
## throw toys for EBEB
##lumi_factor is kfactor*lumi 1.5*10/fb
##EBEB and EBEE separate because of different fit ranges
##./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=1000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input_weightcut.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_weightcut_EBEB.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb_withweightcut   --observable 'mgg[4000,230,10000]' --test-categories EBEB &
wait
##./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=1000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input_weightcut.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_weightcut_EBEE.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb_withweightcut   --observable 'mgg[3400,320,10000]' --test-categories EBEE &
wait

##### throw asimov toy to check fit
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input_weightcut.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB_asimov_weightcut.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/weight_studies --observable 'mgg[4000,230,10000]' --test-categories EBEB  &
wait
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input_weightcut.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE_asimov_weightcut.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/weight_studies --observable 'mgg[3400,320,10000]' --test-categories EBEE  &
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_input.root -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE_asimov.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/ --observable 'mgg[3400,320,10000]' --test-categories EBEE  &

wait

#### fit the toys 
##./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_weightcut_EBEB.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_2 1000 20 --observable 'mgg[4000,230,10000]' --fit-range 230,10000 & 
##./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_weightcut_EBEE.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEE_2 1000 20 --observable 'mgg[3400,320,10000]' --fit-range 320,10000 & 
##qsub system
#./submit_toys.sh 8nm full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned_EBEB.root  full_analysis_moriond16v1_0T_sync_v6_data/bias_study_toys_from_mc_unbinned/EBEB_2 500 2 --observable 'mgg[4000,230,10000]' --fit-range 230,10000 & 

## fit and plot asimov
#./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB_asimov_weightcut.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_asimov_weightcut 1 0  --observable 'mgg[4000,230,10000]' --fit-range 230,10000 --plot-toys-fits --n-toys -1 -O . --plot-fit-bands &

##./submit_toys.sh all.q full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEB_asimov.root  full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_asimov 1 1  --observable 'mgg[4000,230,10000]' --fit-range 230,10000 --plot-toys-fits --n-toys -1 -O . --plot-fit-bands & 
##wait
#./bkg_bias.py --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE_asimov.root  -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEE_asimov/test.root --observable 'mgg[3400,320,10000]' --plot-toys-fits --n-toys -1 -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/ --plot-fit-bands --fit-range 320,10000 --store-new-only --components pp --models dijet --fit-toys --fit-name cic2 --saveas root,png
wait
#./bkg_bias.py --read-ws full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned_EBEE_asimov_weightcut.root  -o full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEE_asimov_weightcut/test.root --observable 'mgg[3400,320,10000]' --plot-toys-fits --n-toys -1 -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/weight_studies/ --plot-fit-bands --fit-range 320,10000 --store-new-only --components pp --models dijet --fit-toys --fit-name cic2 --saveas root,png
##need to copy plots by hand because no access to /afs via scratch
#cp full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_asimov/*.png /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/. 
#cp full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEE_asimov/*.png /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/. 
#cp full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_asimov_weightcut/*.png /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/. 
#cp full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEE_asimov_weightcut/*.png /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/. 

##if you need to tune bias: look at profile_bias.root 
##define TF1 for fit with SetParameters according to old function
## see if fit defines bias well, for tail addition of constant can be usefu;
##if tail is overcorrected -lower order in power law
## try also two different function for both ends and try to interpolate

wait
#./hadd_toys.sh full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/EBEB_2

#./bkg_bias.py --analyze-bias --bias-files full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/toys.root --scale-bias 10 --bias-labels 10fb -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb_withweightcut/ 
#./bkg_bias.py --analyze-bias --bias-files full_analysis_moriond16v1_sync_v4_data/bias_study_toys_from_mc_unbinned/toys.root --bias-labels fit -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_moriond16v1_sync_v4_data/bias_study_10fb/ 
