#!/bin/bash 

set -x

ename=figaro-3.1.0-1
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

for i in {1..9}; do
  prob=prob0$i;
  ldir=./$prob/classes/com/cra/appril;
  rdir=./target/scala-2.11/classes/com/cra/appril;
  mkdir -p $ldir;
  cp -r $rdir/metrics $ldir; ## include in all problems because it's not obvious which is owner
  cp -r $rdir/$prob   $ldir;

  cd $prob;
    CPID=04-0$i-00

    rm -rf data; ## insure solution isn't using local data directory
    sed -i -- 's/..\/lib\/\*:..\/target\/scala-2.11\/classes/.\/classes/g' ./run.sh;

  cd -;

done;
