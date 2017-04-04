#!/bin/bash

# XXX: Fix these names
substitute_names () {
    sed -i 's/60ef23dbed04bcfca448d03544f4466f36815678.tar.bz2/micro/' \
        $1;
    sed -i 's/d0e46a3005bb8340e7316a6b55ca7354e592bf21.tar.bz2/sixteenth/' \
        $1;
    sed -i 's/53bcbf3db71d730ed00b3c551f95fe4dcbab3e13.tar.bz2/eighth/' \
        $1;
    sed -i 's/c1003f7c43e538be6773b2c793324808f5d23b84.tar.bz2/quarter/' \
        $1;
    sed -i 's/029b78f555a1ea7d313c74c10f3a2dadfb07439c.tar.bz2/half/' \
        $1;
    sed -i 's/607ea3ee812ce2d1f958e98f3848648a8c97aa02.tar.bz2/full/' \
        $1;
}


MAC=`ifconfig eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | tail -c 3`

BASEDIR=`mktemp -d /tmp/cp6_extract_XXX`/;

DATADIR=~/.local/share/peval/;
DATABASE=${DATADIR}/index.db;

RUN_IDS=`sqlite3 $DATABASE "SELECT r.id FROM Run r, configured_solution \
    csln, solution sln WHERE r.configured_solution_id = csln.id AND \
    r.configured_solution_solution = csln.solution AND \
    csln.solution = sln.id AND sln.challenge_problem_id = 6 \
    AND sln.challenge_problem_revision_major = 1"`;

: << 'COMMENT'
for ARUN in $RUN_IDS; do
  peval evaluate run $ARUN;
done;
COMMENT

RESULTS_FILE=${BASEDIR}/results.csv;
echo "RUN_ID, DATASET, DURATION, LOAD_AVERAGE, LOAD_MAX, RAM_AVERAGE, \
      RAM_MAX, TEAM, mAP" > ${RESULTS_FILE};

for ARUN in $RUN_IDS; do

    RESULT=`sqlite3 $DATABASE "select id from evaluation where run='$ARUN'"`
    UUID=${RESULT%%.*};

    TEAM=`sqlite3 $DATABASE "SELECT description FROM team t, engine e, \
        Run r WHERE r.engine = e.id AND e.team = t.id AND r.id = $ARUN;"`;

    if [[ "$TEAM" = "{CH,D}imple" ]]; then TEAM=Gamalon; fi;

    DIRNAME=${BASEDIR}/${TEAM}/${UUID};
    mkdir -p ${DIRNAME};

    RESULTARCHIVE=${DATADIR}/${RESULT};
    if [ -f ${RESULTARCHIVE} ]; then


    cd ${DIRNAME};
    tar -xjf ${RESULTARCHIVE};
    cd - > /dev/null;

###### THE MAX AND AVERAGE COLUMNS ARE STORED BACKWARDS #####
    ROW=`sqlite3 -separator ', ' ${DATABASE} "select id, dataset, duration, \
         load_max, load_average, ram_max, ram_average from run \
         where id='${ARUN}'"`;
    echo -n ${ROW} >> ${RESULTS_FILE};

    SCORE=`awk '$1=="Info:"&&$2=="mAP:"{print $3}' ${DIRNAME}/eval.log`
    if [[ ! -n "${SCORE}" ]]; then
      echo "XXX: No mAP for $ARUN";
    fi;
    echo ", ${TEAM}, ${SCORE}" >> ${RESULTS_FILE};

    else echo "No file for run ${ARUN}";
    fi;
done;

# Clean up single results file
substitute_names ${RESULTS_FILE};

cd ${BASEDIR}
ARCHIVE=results-${MAC}.tar
tar -c -f ${ARCHIVE} ./*
pbzip2 ${ARCHIVE}
mv ${ARCHIVE}.bz2 ~/
cd - > /dev/null;

echo "Temp dir: $BASEDIR"
# rm -rf ${BASEDIR}
exit
