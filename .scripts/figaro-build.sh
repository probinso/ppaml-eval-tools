#!/bin/bash 

set -x

ename=figaro-3.2.0-1
rm -rf $ename
tar -vxjf $ename.tar.bz2
export ENGROOT=$(readlink -m $ename/lib/)

fname=figaro-CP04-2.0.0-0b4
rm -rf $fname/
tar -vxjf $fname.tar.bz2
cd $fname/

rm -rf lib;
ln -s $ENGROOT lib;
sbt clean; 
sbt compile;


ENGHASH=$(peval register engine 12 $ENGROOT 2>&1 | tail -n 1)

#special cases
for i in $(ls problem-8-files/); do
  cp problem-8-files/$i prob08/data/;
done;

for i in {1..5} {7..8}; do
  prob=prob0$i;
  ldir=./$prob/classes/com/cra/appril;
  rdir=./target/scala-2.11/classes/com/cra/appril;
  mkdir -p $ldir;
  cp -r $rdir/metrics $ldir;
  cp -r $rdir/$prob   $ldir;

  cd $prob;
    CPID=04-0$i-00
    peval register dataset $CPID ./data ./data;
    rm -rf data;
    sed -i -- 's/..\/lib\/\*:..\/target\/scala-2.11\/classes/.\/classes/g' ./run.sh;
    peval register solution $ENGHASH $CPID $(readlink -m .) solution-smoketest solution-evaluation;
  cd -;

done;

echo "
  CP-4.6 CP-4.9 are expressiveness
  CP-4.10 is not included in Figaro
";
