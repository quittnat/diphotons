#!/bin/bash
#e.g ./submit_toysLEE.sh
njobs=$1
#differenr random seed for each job
for job in $(seq 0 $njobs); do
    qsub prepLEEtest.sh $job 
done
