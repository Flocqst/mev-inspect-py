#!/bin/bash
# This is a script to analyze MEV profits
# Input the pool Id of mev-inspect (can be found on your TILT interface)
# TODO: How to extract the mev-inspect pool id to copy the csv files?
mevInspectPoolId="mev-inspect-7746b4d64-btrjp"
# Input the starting and ending blocks you want to run the profit analysis for
blockFrom=$((34500000))
blockTo=$((34800000))
window=$((100))
reps=$(((${blockTo}-${blockFrom})/${window}))
reps=-1
echo "${reps}"
for i in $(seq 0 1 $reps)
do
    from=$(($blockFrom + $i*$window))
    to=$(($blockFrom + ($i+1)*$window))
    echo "--"
    echo "rep= $i/$reps"
    echo "from= $from"
    echo "to= $to"
    ./mev inspect-many $from $to
done
./mev analyze-profit $blockFrom $blockTo True
declare -a file_names=("profit_by_date.csv" "profit_by_block_number.csv" "profit_by_category.csv")
for fname in "${file_names[@]}"
do
  kubectl cp $mevInspectPoolId:resources/$fname $fname;
done