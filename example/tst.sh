#!/bin/bash -eu

rm -f index.db;
sqlite3 index.db < ../db_init.sql;
mv index.db ~/.local/share/ppaml/

ENG=`peval register engine 1 engine`
echo ${ENG}
exit
SOL=`peval register solution ${ENG} 0-0-0 solution solution/one`
DAT=`peval register dataset 0-0-0 dataset/input/ dataset/eval/`

# test registration of new configuration file
peval register configuration ${SOL} solution/five
peval register configuration ${SOL} ten
peval run ${ENG} ${SOL} ${DAT} #  Integrator   0

