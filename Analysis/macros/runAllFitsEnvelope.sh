# coups="001 005 007 01 015 02"
##coups="001 01 02"
coups=001
file=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_final_ws.root
file2="full_analysis_spring15_7415v2_sync_v5"
folder="full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes"
##bkg file must be in folder
##bkgfile="multipdf_gofToys_dijet5.root"
##bkgfile="full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_default_shapes_pas_lumi_2.56_grav_001_750.root"
bkgfile="multipdf_dijet2.root"
##bkgfile="for_envelope_bkg_ws.root"
##parallel when several signal models
##luminosity one for plot and one for scaling
##parallel --ungroup -j 1 './combine_maker.sh full_analysis_spring15_7415v2_sync_v6 --data-file `pwd`/full_analysis_spring15_7415v2_sync_v5_data_ecorr/output.root --lumi 2.56 --fit-name cic2 --plot-fit-bands --rescale-signal-to 1e-3  --parametric-signal ~/eos/cms/store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k{}_m1000to4900.root --parametric-signal ~/eos/cms/store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k{}_m500to998.root  --parametric-signal-xsection xsections.json --parametric-signal-acceptance  acceptance_pu.json --load lumi.json  --compute-fwhm --generate-ws-bkgnbias --only-coups {} --label pas --minos-bands' ::: $coups
##./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --fit-name cic2 --generate-signal --generate-datacard  --cardname datacard.txt  --rescale-signal-to 1e-3 --parametric-signal root://xrootd-cms.infn.it//store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json


./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --generate-signal --fit-name cic2 --generate-datacard --rescale-signal-to 1e-3 --parametric-signal WSdiphotonConSmearings_nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json --background-root-file $bkgfile --use-envelope
##./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --generate-signal --fit-name cic2 --generate-datacard --rescale-signal-to 1e-3 --parametric-signal WSdiphotonConSmearings_nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json --background-root-file $bkgfile 
wait
./combineall.sh $folder $coups -t -1 -M ProfileLikelihood --pvalue --significance --expectSignal 7 --hadd --rMax 60 --cont  


wait
./combineall.sh $folder $coups  -M Asymptotic --run expected --hadd --cont --rMax 60 
#to plot fit
wait
#combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k001 -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB --saveToys --freezeNuisances pdfindex_EBEB --setPhysicsModelParameters pdfindex_EBEB=0,r=0 datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_001_750.txt |tee output_freezeallbut1.txt
wait
#scan likelihood limit->Draw(deltaNll:r)
#combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k001 -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB --freezeNuisances pdfindex_EBEB --setPhysicsModelParameters pdfindex_EBEB=1 --rMin=0 --rMax=30 --algo=grid --points=100 --saveToys datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_001_750.txt |tee output_freeze_scan.txt



 

