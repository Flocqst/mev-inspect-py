#!/bin/bash
# This is a script to analyze MEV profits
# Run with:
# sleep(900); ./mev exec alembic upgrade head; sleep(60); nohup bash scripts/launch_analysis.sh > analysis.out 2>&1 &
# Input the pool Id of mev-inspect (can also be found on your TILT interface)
mevInspectPoolId=$(kubectl get pods | sed -n -e '/^mev-inspect-/p' | sed '/^mev-inspect-workers/d' | awk '{print $1}')
# Input the starting and ending blocks you want to run the profit analysis for
blockFrom=$((34500000))
nBlocks=500000
blockTo=$((blockFrom+nBlocks))
startDate=$(date +%s)
startDateFormatted=$(date +"%Y-%m-%d-%H:%M:%S.")$((startDate))
echo "Starting analysis from block=${blockFrom} for ${nBlocks} blocks on the ${startDateFormatted}"
./mev inspect-many $blockFrom $blockTo
./mev analyze-profit $blockFrom $blockTo True
endDate=$(date +%s)
endDateFormatted=$(date +"%Y-%m-%d-%H:%M:%S.")$(($endDate))
echo "Finished analysis of ${nBlocks} blocks on the ${endDateFormatted}. It took $(( (endDate - startDate)/60 )) minutes."
declare -a file_names=("profit_by_date.csv" "profit_by_block_number.csv" "profit_by_category.csv" "usd_profit.csv"  "profit_distribution.png" "analyze_profit_failures.csv")
for fname in "${file_names[@]}"
do
  kubectl cp $mevInspectPoolId:resources/$fname $fname;
done