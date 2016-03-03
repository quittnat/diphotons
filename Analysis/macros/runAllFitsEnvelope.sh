# coups="001 005 007 01 015 02"
##coups="001 01 02"
coups=001
#bkgfile=/afs/cern.ch/user/m/musella/public/workspace/exo/full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_default_shapes_pas_lumi_2.56/full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_default_shapes_pas_lumi_2.56_grav_001_750.root
#bkgfile=full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_default_shapes_pas_lumi_2.56_bkgnbias_grav_001_750.root
file2="full_analysis_spring15_7415v2_sync_v5"
folder="full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes"
##bkg file must be in folder
##bkgfile="multipdf_gofToys_dijet5.root"
##bkgfile="full_analysis_spring15_7415v2_sync_v5_data_ecorr_cic2_default_shapes_pas_lumi_2.56_grav_001_750.root"
bkgfile="/afs/cern.ch/user/m/mquittna/public/envelope_EXO/output_flashggFinalFit/multipdf_all_ho_dijetstart.root"
###parallel when several signal models
###luminosity one for plot and one for scaling
###parallel --ungroup -j 1 './combine_maker.sh full_analysis_spring15_7415v2_sync_v6 --data-file `pwd`/full_analysis_spring15_7415v2_sync_v5_data_ecorr/output.root --lumi 2.56 --fit-name cic2 --plot-fit-bands --rescale-signal-to 1e-3  --parametric-signal ~/eos/cms/store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k{}_m1000to4900.root --parametric-signal ~/eos/cms/store/user/crovelli/WSdiphotonConSmearings/nominalWSwithSmear_k{}_m500to998.root  --parametric-signal-xsection xsections.json --parametric-signal-acceptance  acceptance_pu.json --load lumi.json  --compute-fwhm --generate-ws-bkgnbias --only-coups {} --label pas --minos-bands' ::: $coups
###mkdir $folder

cp $bkgfile $folder/.
./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --generate-signal --fit-name cic2 --generate-datacard --rescale-signal-to 1e-3 --parametric-signal nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json --background-root-file $bkgfile --use-envelope
##./combine_maker.sh $file2 --luminosity 2.56 --lumi 2.56 --generate-signal --fit-name cic2 --generate-datacard --rescale-signal-to 1e-3 --parametric-signal nominalWSwithSmear_k001_m500to998.root --parametric-signal-acceptance acceptance_pu.json --background-root-file $bkgfile 
wait
cd $folder
###combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k001fit -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB --saveToys --freezeNuisances pdfindex_EBEB --setPhysicsModelParameters pdfindex_EBEB=0,r=0 datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_001_750.txt |tee output_MultiDimFit.txt

###combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k01fittoysFreq -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB,pdfindex_EBEE --toysFrequentist --saveToys --setPhysicsModelParameters r=0 datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_01_750.txt |tee output_MultiDimFit_toysFrequentist.txt
combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k001fit -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB,pdfindex_EBEE --saveToys --setPhysicsModelParameters r=0 datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_001_750.txt |tee output_MultiDimFit.txt

wait
cd ..
###./combineall.sh $folder $coups -t -1 -M ProfileLikelihood --pvalue --significance --expectSignal 7 --hadd --rMax 60 --toysFrequentist -n toysFreq --cont
##wait
./combineall.sh $folder $coups -t -1 -M ProfileLikelihood --pvalue --significance --expectSignal 7 --hadd --rMax 60 --cont
wait
./combineall.sh $folder $coups  -M Asymptotic --run expected --hadd --cont --rMax 60 
###wait
###./combineall.sh $folder $coups  -M Asymptotic --run expected --hadd --cont -n toysFreq --toysFrequentist --rMax 60 
#to plot fit
###wait
#scan likelihood limit->Draw(deltaNll:r)
##cd $folder
##combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k001scan -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB --freezeNuisances pdfindex_EBEB --setPhysicsModelParameters pdfindex_EBEB=1 --rMin=0 --rMax=30 --algo=grid --points=100 --saveToys datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_001_750.txt |tee output_freeze_scan.txt
##combine -L libdiphotonsUtils -t -1 -M MultiDimFit --expectSignal 7 -n _k001scan -m 750 -v 3 --saveWorkspace --saveSpecifiedIndex pdfindex_EBEB,pdfindex_EBEE --rMin=0 --rMax=30 --algo=grid --points=100 --saveToys datacard_full_analysis_spring15_7415v2_sync_v5_cic2_default_shapes_grav_001_750.txt |tee output_freeze_scan.txt



 

