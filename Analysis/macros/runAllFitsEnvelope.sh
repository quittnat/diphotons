# coups="001 005 007 01 015 02"
##coups="001 01 02"
coups=001
file=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_final_ws.root
file2="full_analysis_spring15_7415v2_sync_v5"
folder="full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes"
##bkg file must be in folder
bkgfile="multipdf_gofToys_dijet3.root"
##bkgfile="for_envelope_bkg_ws.root"
##parallel when several signal models
##luminosity one for plot and one for scaling
##parallel --ungroup -j 1 './combine_maker.sh full_analysis_spring15_7415v2_sync_v6 --data-file `pwd`/full_analysis_spring15_7415v2_sync_v5_data_ecorr/output.root --lumi 2.56 --fit-name cic2 --plot-fit-bands --rescale-signal-to 1e-3  --parametric-signal ~/eos/cms/store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k{}_m1000to4900.root --parametric-signal ~/eos/cms/store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k{}_m500to998.root  --parametric-signal-xsection xsections.json --parametric-signal-acceptance  acceptance_pu.json --load lumi.json  --compute-fwhm --generate-ws-bkgnbias --only-coups {} --label pas --minos-bands' ::: $coups
##./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --fit-name cic2 --generate-signal --generate-datacard  --cardname datacard.txt  --rescale-signal-to 1e-3 --parametric-signal root://xrootd-cms.infn.it//store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json
##./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --generate-signal --fit-name cic2 --generate-datacard --rescale-signal-to 1e-3 --parametric-signal WSdiphotonConSmearings_nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json --background-root-file $bkgfile --use-envelope
##-t -1 use Asimov dataset
wait
./combineall.sh $folder $coups -t -1 -M ProfileLikelihood --pvalue --significance --expectSignal 7  --plots --hadd --rMax 60 --cont 
#./combineall.sh $folder/EBEE $coups -t -1 -M ProfileLikelihood --pvalue --significance  --expectSignal 7 --hadd --rMax 60 -n EBEE --cont
#./combineall.sh $folder/EBEB $coups -t -1 -M ProfileLikelihood --pvalue --significance  --expectSignal 7 --hadd --rMax 60 -n EBEB --cont


wait
## both is expected and observed
##expectSignal is the simulated signal strength which is now 7 fb, rMax->signal range to consider
##parallel --ungroup './combineall.sh CMS-multipdf-EXO 001 -M Asymptotic --expectedSignal=7 --hadd --cont --rMax 60'
##./combineall.sh $folder/EBEB $coups -M Asymptotic --run expected --hadd --cont --rMax 60 -n EBEB
#./combineall.sh $folder/EBEE $coups -M Asymptotic --run expected --hadd --cont --rMax 60 -n EBEE
./combineall.sh $folder $coups  -M Asymptotic --run expected --hadd --cont --rMax 60 --minimizerStrategy 2 
