#!/bin/bash 

set -x

ename=figaro-3.1.0-0
rm -rf $ename
tar -vxjf $ename.tar.bz2
export ENGROOT=$(readlink -m $ename/lib/)

fname=figaro-CP04-2.0.0-0b2
rm -rf $fname/
tar -vxjf $fname.tar.bz2
cd $fname/

rm -rf lib;
ln -s $ENGROOT lib;
sbt clean; 
sbt compile;

