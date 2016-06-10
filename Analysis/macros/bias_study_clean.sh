
## makes datasets
##./templates_maker.py --load templates_maker_bias.json,templates_maker_prepare_bias.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring16v1_sync_v1_2705_cert   -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input.root --only-subset cic2 --signals '{}'
##./templates_maker.py --load templates_maker_bias.json,templates_maker_prepare_bias.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring16v1_sync_v1_2705_cert   -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input_nopuweight_200_1000mccorr.root --only-subset cic2 --signals '{}'
#./templates_maker.py --load templates_maker_bias.json,templates_maker_prepare_bias.json --selection cic --input-dir /afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring16v1_sync_v1_2705_cert   -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input.root --only-subset cic2 --signals '{}'
##--reweight-variables "(1+ (2.286/(2.047)-1-0.03)*(mggGen>200 && mggGen<500))" --do-reweight

##lumi_factor is kfactor*lumi 1.5*10/fb

##EBEB and EBEE separate because of different fit ranges
##### throw asimov toy to check fit
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --models dijet --components pp  --fit-name cic2 --store-new-only --read-ws full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input_nopuweight_200_1000mccorr.root -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_EBEB_asimov_nopuweight_200_1000mccorr.root --observable 'mgg[1954,230,10000]' --test-categories EBEB  &
wait
##./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=-1 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input_nopuweight_200_1000mccorr.root -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_EBEE_asimov_nopuweight_200_1000mccorr.root --observable 'mgg[1936,320,10000]' --test-categories EBEE  &
wait
#./bkg_bias.py --read-ws full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_EBEB_asimov_nopuweight_200_1000mccorr.root  -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_EBEB_asimov_fit_nopuweight_200_1000mccorr.root --observable 'mgg[1954,230,10000]' --plot-toys-fits --n-toys -1 -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1/bias_study_10fb_nopuweight_200_1000mccorr/  --fit-range 230,10000 --store-new-only --components pp --models dijet --fit-toys --fit-name cic2 --plot-binning 94,230,2110  --saveas root,png
#94,2110
#189,4010
wait
#./bkg_bias.py --read-ws full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_EBEE_asimov_nopuweight_200_1000mccorr.root  -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_EBEE_asimov_fit_nopuweight_200_1000mccorr.root --observable 'mgg[1936,320,10000]' --plot-toys-fits --n-toys -1 -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1/bias_study_10fb_nopuweight_200_1000mccorr/  --fit-range 320,10000 --store-new-only --components pp --models dijet --fit-toys --fit-name cic2 --plot-binning 89,320,2100  --saveas root,png
## throw toys for EBEB
#89,2100
#184,4000
wait
#create toys
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=10000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input_nopuweight_200_1000mccorr.root -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_nopuweight_200_1000mccorr_EBEB.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1_2705_cert/bias_study_10fb_nopuweight_200_1000mccorr   --observable 'mgg[4000,230,10000]' --test-categories EBEB &
wait
#./bkg_bias.py --throw-toys --lumi-factor=15. --n-toys=10000 --components pp --models dijet --fit-name cic2 --store-new-only --read-ws full_analysis_spring16v1_sync_v1_2705_cert/bias_study_input_nopuweight_200_1000mccorr.root -o full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_nopuweight_200_1000mccorr_EBEE.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1_2705_cert/bias_study_10fb_nopuweight_200_1000mccorr   --observable 'mgg[3400,320,10000]' --test-categories EBEE &


#### fit the toys
wait
./submit_toys.sh short.q full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_nopuweight_200_1000mccorr_EBEB.root  full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_dijet/EBEB 1000 20 --observable 'mgg[1954,230,10000]' --fit-range 230,10000 & 
./submit_toys.sh short.q full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_nopuweight_200_1000mccorr_EBEE.root  full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned_dijet/EBEE 1000 20 --observable 'mgg[1936,320,10000]' --fit-range 320,10000 & 
#wait
wait


##if you need to tune bias: look at profile_bias.root 
##define TF1 for fit with SetParameters according to old function
## see if fit defines bias well, for tail addition of constant can be usefu;
##if tail is overcorrected -lower order in power law
## try also two different function for both ends and try to interpolate

wait
##./hadd_toys.sh full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned/EBEB
wait
##./hadd_toys.sh full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned/EBEE
#hadd full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned/toys.root full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned/EBEE/* full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned/EBEB/*
#./bkg_bias.py --analyze-bias --bias-files full_analysis_spring16v1_sync_v1_2705_cert/bias_study_toys_from_mc_unbinned/toys.root --scale-bias 10 --bias-labels 10fb -O /afs/cern.ch/user/m/mquittna/www/diphoton/spring16/full_analysis_spring16v1_sync_v1/bias_study_10fb_punopuweight_200_1000mccorr_addbin/ 

