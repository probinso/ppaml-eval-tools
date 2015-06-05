#!/bin/bash 

set -x

if (( $# != 1 )); then
    printf "Usage: %s <figaro_challenge_problem_four.tar.bz2>" "$0" >&2
    printf "Also please remember to set environment variable ENGROOT" >&2
    exit 1
fi

if [ -z $ENGROOT ]; then
  echo "Please set ENGROOT environment variable" >&2
  exit -1
fi

fname=$1 # set filenmae to input variable 1

if [ ! -e $fname ]; then
  echo "Input filename does not exist" >&2
  exit -1
fi

if [ ! $fname == *".tar.bz2" ]; then
  echo "Input filename is incorrect file extension, please use .tar.bz2" >&2
  exit -1;
fi

dname=${fname%%.tar.bz2} # set directory name of output, this is a figaro convention

rm -rf $dname    # clean up previous instance of dname
tar -vxjf $fname # extract $fname, should create $dname directory by convention

cd $dname/

# Remove lib, and replace with engroot 
rm -rf lib;
ln -s $ENGROOT lib;

# build figaro cp4
sbt clean; 
sbt compile;


#special cases problem8 data is stored differently in the figaro submission
for i in $(ls problem-8-files/); do
  cp problem-8-files/$i prob08/data/;
done;

for i in {1..5} {7..8}; do # other problems are missing or expressivity
  prob=prob0$i;
  ldir=./$prob/classes/com/cra/appril;
  rdir=./target/scala-2.11/classes/com/cra/appril;

  # restructuring submission to conform to peval tool
  mkdir -p $ldir;
  cp -r $rdir/metrics $ldir;
  cp -r $rdir/$prob   $ldir;


  cd $prob;
    # move datasets to obvious location
    mv  ./data ../data_for_$prob ;
    sed -i -- 's/..\/lib\/\*:..\/target\/scala-2.11\/classes/.\/classes/g' ./run.sh;
  cd -;

done;

echo "
  CP-4.6 CP-4.9 are expressiveness
  CP-4.10 is not included in Figaro
";
