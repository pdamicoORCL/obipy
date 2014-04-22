#!/bin/bash
# Batch file to document an Oracle BI Repository
echo $1
echo "Press any key to continue [$1] [$2]"
read theDir
python -E ./printCPools.py $1 | tee $2.pools.txt
python -E ./printVars.py $1 | tee $2.vars.txt
python -E ./printInitBlocks.py $1 | tee $2.init.txt
python -E ./printJoins_04.py $1 | tee $2.joins.txt
python -E ./printComplexJoins.py $1 | tee $2.complex.joins.txt
python -E ./printLts.py $1 | tee $2.lts.txt

