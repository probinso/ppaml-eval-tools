#!/bin/bash

set -x

rm -f index.db;
sqlite3 index.db < ../db_init.sql;
mv index.db ~/.local/share/ppaml/

ENG=$(peval register engine 1 engine 2>&1 | tail -n 1)
SOL=$(peval register solution ${ENG} 0-0-0 solution solution/one solution/five 2>&1 | tail -n 1)
DAT=$(peval register dataset 0-0-0 dataset/input/ dataset/eval/ 2>&1 | tail -n 1)

# test registration of new configuration file
peval register configuration ${SOL} solution/two_minus_one
peval register configuration ${SOL} ten
peval run ${ENG} ${SOL} ${DAT} #  Integrator   0

