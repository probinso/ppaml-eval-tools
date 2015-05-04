#!/bin/bash

set -x

fname=figaro-CP04-2.0.0-0b2
cd $fname

sqlite3 ~/.local/share/ppaml/index.db \
  "pragma foreign_keys = ON;
   delete from engine;
   delete from solution;
   delete from dataset;"

rm -rf /tmp/ppaml*

ENGHASH=$(peval register engine 12 $ENGROOT 2>&1 | tail -n 1)

for i in {1..9}; do
  prob=prob0$i;
  ldir=./$prob/classes/com/cra/appril;
  rdir=./target/scala-2.11/classes/com/cra/appril;
  mkdir -p $ldir;
  cp -r $rdir/metrics $ldir;
  cp -r $rdir/$prob   $ldir;

  cd $prob;
    CPID=04-0$i-00
    mkdir -p data/forcework
    peval register dataset $CPID ./data ./data;
    rm -rf data;
    sed -i -- 's/..\/lib\/\*:..\/target\/scala-2.11\/classes/.\/classes/g' ./run.sh;
    peval register solution $ENGHASH $CPID $(readlink -m .) solution-smoketest solution-evaluation;
  cd -;

done;

