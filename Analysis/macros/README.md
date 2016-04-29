# Wild notes to keep track of command line options needed for the different analysis tasks

## Control plots

### Event selection monitoring
`./control_plots.sh full_analysis_anv1_v19 ~/www/exo/phys_14_anv1`

## Templates generation for Moriond 16 analysis

### Preparing input: merge trees and fill template variables
`./templates_maker.py --input-dir=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_moriond16v1_sync_v5_extra_vars_data/  -o  templates_moriond16v1_sync_v5.root --prepare-nosignal --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json`
- json files:
	- `templates_maker.json` contains datsets and aliases
	- `templates_maker_prepare.json` contains specifications for templates creation
- options: 
	- `--prepare-nosignal` if no signal MC templates wanted
	- `--prepare-data` if no MC templates wanted
	- `--only-subset` "2D" for templates, refering to final "2D" fit, has extended ChIso region for 3.8 T. See also specifications in templates_maker_prepare.json. For the following event mixing the creation of single photon templates is also necessary "singlePho"

### Event mixing
`./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws templates_moriond16v1_sync_v5_singlephoton.root,templates_moriond16v1_sync_v5.root  --mix-mc --mix-templates  --store-new-only -o mix_moriond16v1_sync_v5.root`

- options: 
	- `--mix-mc` if MC templates for mixed pf and ff templates wanted
	- `--store-new-only` possible as it saves time. Just read all inputs afterwards via `--read-ws` afterwards.


### Comparison plots for templates
There are two options. Either running over the full mass range for comparison plots, or to run with fixed mass bins to prepare the input for the final purity vs mass comparison.

`./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws templates_moriond16v1_sync_v5.root,mix_moriond16v1_sync_v5.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/moriond16/bkg_decomposition_moriond16v1_sync_v5/ -o compared_moriond16v1_sync_v5_fullmass.root --compare-templates --fit-massbins 1,1,0 --template-binning="0.0,0.1,5.0,15.0" --fit-mc  --store-new-only --lumi 2.7`
- options: 
	- `--lumi` puts lumi on plots if lumi.json file loaded
	- `--fit-mc` if also comparison plots for MC templates needed
    - `--no-mctruth` if not event MCtruth is needed
	- `fit-massbins`: "x,y,z" translates to x massbins on the whole,y massbins we want to run over now, starting from bin z. "1,1,0" corresponds to full mass range
	- `fixed-massbins` looks for an array, given in the `templates_fitter.json`

### 2d fit with unrolled histograms
./templates_fitter.py --load templates_fitter.json,lumi.json --read-ws compared_moriond16v1_sync_v5.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/moriond16/bkg_decomposition_moriond16v1_sync_v5/  --purity-sigregion -o fitted_moriond16v1_sync_v5_data.root  --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only --lumi  2.7 --saveas pdf,convert_png,root |tee output_fit_moriond_v5_verbose.txt
- options:
	- fit-template can be "unrolled_mctruth" or "unrolled_template_mix" + optional `--fit-mc`. Please be aware that the QCD statistics are too low to have a 3-components with for mctruth, such that for this option only the 2-component fit works. This can be specified in `templates_fitter.json`
	- optional: `--saveas pdf,convert_png,root` if problems with png figures
	- optional: `|tee output_fit_moriond_v5.txt` prints out log file on screen and saves as a txt file

### plots for purity vs massbins in full charged iso range and signal region
 `./templates_fitter.py --load templates_fitter.json,lumi.json --saveas pdf,convert_png,root --read-ws templates_moriond16v1_sync_v5.root,compared_moriond16v1_sync_v5.root,fitted_moriond16v1_sync_v5_data.root,fitted_moriond16v1_sync_v5_mc.root,fitted_moriond16v1_sync_v5_mctruth.root  -O /afs/cern.ch/user/m/mquittna/www/diphoton/moriond16/bkg_decomposition_moriond16v1_sync_v5/ --plot-purity --plot-closure template_mix --plot-purityvalue fraction  --lumi 2.7 --full-error -o purity_moriond16v1_sync_v5.root --store-new-only |tee output_fullregion_purity_moriond_v5.txt`

- options:
	- `--plot-closure` :template_mix or template
	- `--plot-purityvalue`: either fraction or number of events
	- `--plot-closure`: for mctruth or template
	- `--full-error`: full error as statistical + jack-knife (see below) +systematic error computed
	- `--no-mctruth`: not even mctruth wanted, data only
	- `--fit-mc`: MC plots


for the signal region you have for example:
 `./templates_fitter.py --load templates_fitter_cmsswcomparison.json,lumi.json --saveas pdf,convert_png,root --read-ws templates_7415v2_v5_data_ecorr_pas.root,compared_templates_7415v2_v5_data_ecorr_pas.root,fitted_7415v2_v5_data_ecorr_pas.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/bkg_decomposition_templates_7415v2_v5_data_ecorr_pas/ --plot-purity --plot-closure template_mix --purity-sigregion --plot-purityvalue fraction --no-mctruth --lumi 2.7 --full-error -o purity_sigregion_7415v2_v5_data_ecorr_pas.root --store-new-only |tee output_sigregion_purity_74.txt` 
- options:
	- `--purity-sigregion`: to plot the purity in the signal region
 
### getting Jack-knife uncertainty on templates
You have to enable the different options in the respective json files for each step
 `./templates_maker.py --input-dir=full_analysis_spring15_7412v2_sync_v3/  -o  templatesdatav3_JK.root --prepare-data --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json`
 `./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws templatesdataMCSinglePhov3.root,fb24/templatesdataMCv3.root --mix-templates  --store-new-only -o mixdatav3_JK.root`

 `./templates_fitter.py --load templates_fitter.json  --read-ws mixdataMCv3.root,templatesdatav3_JK.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpp/  -o JKppv3.root --jackknife --fixed-massbins --template-binning="0.,0.1,5.0,15.0" --store-new-only` 

 `./templates_fitter.py --load templates_fitter.json  --read-ws mixdatav3_JK.root,templatesdataMCv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpf/  -o JKpfv3.root --jackknife --fixed-massbins --template-binning="0.,0.1,5.0,15.0" --store-new-only` 

 `./templates_fitter.py --load templates_fitter.json  --read-ws templatesdatav3_JK.root,mixdataMCv3.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_3comp_data.root,JKppv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpp/  -o fittedJKppv3.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only`

#./templates_fitter.py --load templates_fitter.json  --read-ws templatesdataMCv3.root,mixdatav3_JK.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_3comp_data.root,JKpfv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpf/  -o fittedJKpfv3.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only


## Compare data with MC for irreducible background
 - `./auto_mass_plot.sh`
 - `./basic_plots.py --load basic_plots.json --bkg-file=full_analysis_spring15_7415v2_sync_v3_compare_2/output_mc.root --data-file=full_analysis_spring15_7415v2_sync_v3_compare_2/output_data.root --lumi 2.4 --fudge 621 -O /afs/cern.ch/user/m/mquittna/www/diphoton/comparison_24fb`



### Throwing toys
- `./bkg_bias.py --throw-toys --throw-from-model --lumi-factor=10. --n-toys=1000 --components pp --models dijet --fit-name 2D --store-new-only --read-ws full_analysis_anv1_v19/bias_study_input.root -o full_analysis_anv1_v19/bias_study_toys_from_fit_unbinned_10fb.root  -O ~/www/exo/phys_14_anv1/full_analysis_v19/bkg_model_v0/ --observable mass[1140,300,6000]`
- `./bkg_bias.py --throw-toys --lumi-factor=10. --n-toys=1000 --components pp --models dijet --fit-name 2D --store-new-only --read-ws full_analysis_anv1_v19/bias_study_input.root -o full_analysis_anv1_v19/bias_study_toys_from_mc_unbinned_10fb.root  -O ~/www/exo/phys_14_anv1/full_analysis_v19/bkg_model_v0/ --observable mass[1140,300,6000]`

### Fitting toys
- `./submit_toys.sh 8nm full_analysis_anv1_v19/bias_study_toys_from_fit_unbinned_10fb.root bias_study_toys_from_fit_cmp_to_gen_10fb_1000 1000 2`
- `./submit_toys.sh 8nm full_analysis_anv1_v19/bias_study_toys_from_mc_unbinned_10fb.root  bias_study_toys_from_mc_cmp_to_gen_10fb_1000 1000 2`

### Analyze results
- `./hadd_toys.sh bias_study_toys_from_mc_cmp_to_gen_10fb_1000/`
- `./hadd_toys.sh bias_study_toys_from_fit_cmp_to_gen_10fb_1000/`
- `./bkg_bias.py --analyze-bias --bias-files bias_study_toys_from_mc_cmp_to_gen_10fb_1000/toys.root --bias-labels mc --bias-files bias_study_toys_from_fit_cmp_to_gen_5fb_1000/toys.root --bias-labels fit -O ~/www/exo/phys_14_anv1/bkg_model_v0/5fb`


## Preparing combine inputs

### Shell script wrapper

- `./combine_maker.sh <analysis_version> <list-of-options>`
  - runs template_maker.py to generate the input workspace from the analysis trees
  - runs background model, signal model and datacard creation according to the options
  - all the outuput goes to a dedicate folder named `<analysis_version>_<fitname>_lumi_<luminosity>_<background_model>[_bias][_use_templates][_<extra_label>]`
    the extra label can be specified through the `--label` option

### Background model
- `./combine_maker.py --load templates_maker.json,templates_maker_prepare.json --fit-name cic --input-dir ~musella/public/workspace/exo/full_analysis_anv1_v14  -o full_analysis_anv1_v14_final_ws.root`
- `./combine_maker.py --fit-name cic  --fit-background --read-ws full_analysis_anv1_v14_final_ws.root -O ~/www/test_bkg_fit -o full_analysis_anv1_v14_bkg_ws.root`
- `./combine_maker.py --generate-signal-dataset --read-ws full_analysis_anv1_v14_final_ws.root --fit-name cic --load templates_maker.json --signal-name grav_001_1500 -o grav_001_1500.root`
- `/combine_maker.py --generate-signal-dataset --read-ws bkg_037.root --read-ws full_analysis_anv1_v19_final_ws_semiparam_037.root --fit-name 2D --load templates_maker.json --signal-name grav_02_1500 -o grav_02_1
500.root --use-templates -O /afs/cern.ch/user/m/mquittna/www/diphoton/Phys14/full_analysis_anv1_v19/test_bkg_fit_semiparam_truth_shapes  --plot-binning 50,500.,6000 --verbose`
- `./combine_maker.py --generate-datacard --read-ws full_analysis_anv1_v14_bkg_ws.root --fit-name cic --load templates_maker_prepare.json --signal-name grav_001_1500 --signal-root-file grav_001_1500.root --background-root-file full_analysis_anv1_v14_bkg_ws.root`


### Per-component background model
- `./combine_maker.py --fit-name cic  --fit-background   --observable mgg[5700,300,6000] --read-ws full_analysis_anv1_v19_final_ws.root -O ~/www/test_bkg_fit -o full_analysis_anv1_v19_bkg_ws.root  --bkg-shapes bkg_model/split_shapes.json`

### Per-component background model with constrained purities
- `./combine_maker.py --fit-name cic  --fit-background   --observable mgg[5700,300,6000] --read-ws full_analysis_anv1_v19_final_ws.root -O ~/www/test_bkg_fit -o full_analysis_anv1_v19_bkg_ws.root   --norm-as-fractions --nuisance-fractions-covariance bkg_model/split_covariance.json --bkg-shapes bkg_model/split_shapes.json`

### Semi-parametric templates vs isolation
- `./templates_maker.py --load templates_maker.json,templates_maker_prepare.json --mix-templates --input-dir  ~musella/public/workspace/exo/full_analysis_anv1_v19  -o full_analysis_anv1_v19_final_ws_semiparam.root --only-subset 2D,singlePho`

- `./combine_maker.py --fit-name 2D  --fit-background   --observable mgg[11460,270,6000] --read-ws full_analysis_anv1_v19_final_ws_semiparam.root -O ~/www/exo/full_analysis_anv1_v19/test_bkg_fit_semiparam_split_shapes -o full_analysis_anv1_v19_bkg_ws_semiparam_split_shapes.root  --use-templates  --bkg-shapes bkg_model/split_shapes.json --plot-norm-dataset --plot-binning '191,270,6000'`
- `./combine_maker.py --fit-name 2D  --fit-background   --observable mgg[11460,270,6000] --read-ws full_analysis_anv1_v19_final_ws_semiparam.root -O ~/www/exo/full_analysis_anv1_v19/test_bkg_fit_semiparam_truth_shapes -o full_analysis_anv1_v19_bkg_ws_semiparam_truth_shapes.root  --use-templates  --bkg-shapes bkg_model/truth_shapes.json --plot-norm-dataset --plot-binning '191,270,6000'`
- Notes
  - `bkg_model/truth_shapes.json` uses MC truth for mgg shape, but data-driven templates.
  - `bkg_model/split_shapes.json` takes mgg shape from control region and data-driven templates. 
     Control regions are then added to combine datacard.
  - adding `--norm-as-fractions` fits purties instead of absolute normaliztions.  
  - `--template-binnning <binning>` overwrites the default template binning
  - `--plot-fit-bands --fast-bands` adds uncertainties bands on the models

### All in one 
- `./combine_maker.py --fit-name 2D  --fit-background --observable mgg[11460,270,6000] --read-ws full_analysis_anv1_v19_final_ws_semiparam.root -O ~/www/exo/full_analysis_anv1_v19/test_bkg_fit_semiparam_split_shapes -o full_analysis_anv1_v19_mgg_split_shapes.root  --bkg-shapes bkg_model/truth_shapes.json --plot-norm-dataset --plot-binning '191,270,6000' --generate-signal --generate-datacard --ws-dir full_analysis_anv1_v19_mgg_split_shapes --cardname datacard_full_analysis_anv1_v19_mgg_split_shapes.txt`

### Running combine tool 

### Using custom pdfs
We have to run text2workspace.py by hand since combine forgets to pass the list of libraries to be loaded. eg:
- `text2workspace.py -L libdiphotonsUtils  -m 1500  -o dataCard_grav_001_1500.root  dataCard_grav_001_1500.txt`
- `combine -M ProfileLikelihood --expectSignal 1 --pvalue --significance -t -1  -m 1500 dataCard_grav_001_1500.root -L libdiphotonsUtils`

### Significance
- `combine -M ProfileLikelihood --expectSignal 1 --significance -t -1 dataCard_full_analysis_anv1_v14_bkg_ws.txt`
- `./combineall.sh full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5 02 --hadd -M ProfileLikelihood ProfileLikelihood --expectSignal 1 --significance -t -1`

### Limits
- `combine -M Asymptotic -t -1 --run expected dataCard_full_analysis_anv1_v14_bkg_ws.txt`
- `./combineall.sh full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5 02 --hadd -M Asymptotic -t -1 --run expected`

### Running closure 2D

- prepare models `prepare_all_models.sh`
- throw asymov datasets `prepare_semiparam_closure.sh`

- `combine -L libdiphotonsUtils datacard_full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5_grav_02_1500.txt -M MultiDimFit --redefineSignaPOIs pf_EBEB_frac,pf_EBEE_frac,pp_EBEE_frac,pp_EBEB_frac --freezeNuisance r --setPhysicsModelParameters r=0 -n _fit_self  -m 0 -t -1 --saveWorkspace`

- `combine -L libdiphotonsUtils datacard_full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5_grav_02_1500.txt -M MultiDimFit --redefineSignaPOIs pf_EBEB_frac,pf_EBEE_frac,pp_EBEE_frac,pp_EBEB_frac --freezeNuisance r --setPhysicsModelParameters r=0 -n _fit_truth -t -1 --toysFile ../higgsCombine_truth.GenerateOnly.mH0.123456.root --saveWorkspace`

- `combine -L libdiphotonsUtils datacard_full_analysis_anv1_v19_2D_split_shapes_semiparam_lumi_5_grav_02_1500.txt -M MultiDimFit --redefineSignaPOIs r,pf_EBEB_frac,pf_EBEE_frac,pp_EBEE_frac,pp_EBEB_frac  -m 1500 -n _fit_truth_r009 -t -1 --toysFile ../higgsCombine_truth_r0009.GenerateOnly.mH0.123456.root --saveWorkspace`

- additional options
  - run minos '--algo=singles'
  - different starting points --setPhysicsModelParameters pf_EBEB_frac=0.1,pf_EBEE_frac=0.1,pp_EBEE_frac=0.8,pp_EBEB_frac=0.8
