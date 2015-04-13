#!/bin/bash

rm -f index.db;
sqlite3 index.db < ../db_init.sql;
mv index.db ~/.local/share/ppaml/

ENG=$(peval register engine 1 engine 2>&1)
SOL=$(peval register solution ${ENG} 0-0-0 solution solution/one 2>&1)
DAT=$(peval register dataset 0-0-0 dataset/input/ dataset/eval/ 2>&1)

# test registration of new configuration file
peval register configuration ${SOL} solution/five
peval register configuration ${SOL} ten
peval run ${ENG} ${SOL} ${DAT} #  Integrator   0

