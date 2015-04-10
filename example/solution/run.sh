#!/bin/bash -eu

if (( $# != 4)); then
  printf "Usage: %s config_file input_dir output_path log_path\n" "$0" >&2 ;
  exit 1;
fi;

mkdir -p $3;

typeset -i variable=$(cat $1)
for i in `seq 0 $variable`; do
    sleep 5;
    $ENGROOT/enginefile >> $3/output;
done;

