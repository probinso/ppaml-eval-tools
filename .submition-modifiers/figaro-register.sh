#!/bin/bash

set -x

ename=figaro-3.1.0-1
export ENGROOT=$(readlink -m $ename/lib/)

ENGHASH=$(peval register engine 12 $ENGROOT 2>&1 | tail -n 1)

fname=figaro-CP04-2.0.0-0b2
cd $fname

for i in {1..9}; do
  prob=prob0$i;
  cd $prob;
    CPID=04-0$i-00
    peval register solution $ENGHASH $CPID $(readlink -m .) solution-smoketest solution-evaluation;
  cd -;

done;
