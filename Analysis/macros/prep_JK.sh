
#./templates_maker.py --input-dir=full_analysis_spring15_7412v2_sync_v3/  -o  templatesdatav3_JK.root --prepare-data --only-subset="2D" --load templates_maker.json,templates_maker_prepare.json



#./templates_maker.py --load templates_maker_prepare.json,templates_maker.json --read-ws templatesdataMCSinglePhov3.root,fb24/templatesdataMCv3.root --mix-templates  --store-new-only -o mixdatav3_JK.root

#./templates_fitter.py --load templates_fitter.json  --read-ws mixdataMCv3.root,templatesdatav3_JK.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpp/  -o JKppv3.root --jackknife --fixed-massbins --template-binning="0.,0.1,5.0,15.0" --store-new-only 
./templates_fitter.py --load templates_fitter.json  --read-ws mixdatav3_JK.root,templatesdataMCv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpf/  -o JKpfv3.root --jackknife --fixed-massbins --template-binning="0.,0.1,5.0,15.0" --store-new-only 

#./templates_fitter.py --load templates_fitter.json  --read-ws templatesdatav3_JK.root,mixdataMCv3.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_3comp_data.root,JKppv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpp/  -o fittedJKppv3.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only

#./templates_fitter.py --load templates_fitter.json  --read-ws templatesdataMCv3.root,mixdatav3_JK.root,fitv3_fixedmb_9b.root,fittedv3_fixedmb_9b_3comp_data.root,JKpfv3.root -O /afs/cern.ch/user/m/mquittna/www/diphoton/template_studies_v3/fixedmb_9b_JKpf/  -o fittedJKpfv3.root --nominal-fit --fixed-massbins  --template-binning="0.0,0.1,5.0,15.0" --fit-template unrolled_template_mix --store-new-only




