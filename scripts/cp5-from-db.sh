#!/bin/bash

# XXX: Fix these names
substitute_names () {
    sed -i 's/9a203d6d55114f9a57bf31df59235a300b9d33ad.tar.bz2/micro/' \
        $1;
    sed -i 's/171e652bed17b9507de7517f0aa9db7d84e61084.tar.bz2/quarter/' \
        $1;
    sed -i 's/d6415049ec71976150c53957d7dca443729a07ad.tar.bz2/half/' \
        $1;
    sed -i 's/b404cc7ecf1b7f35e36e1e919b5cbcbeae3cebf4.tar.bz2/full/' \
        $1;
    sed -i 's/dd8b8cc5794d303cc3c2a67ae830c235203a8489.tar.bz2/eighth/' \
        $1;
    sed -i 's/266203773911e7304c9470473ba96679133713b9.tar.bz2/sixteenth/' \
        $1;
}


MAC=`ifconfig eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | tail -c 3`

BASEDIR=`mktemp -d /tmp/cp5_extract_XXX`/;

DATADIR=~/.local/share/peval/;
DATABASE=${DATADIR}/index.db;

RUN_IDS=`sqlite3 $DATABASE "SELECT r.id FROM Run r, configured_solution \
    csln, solution sln WHERE r.configured_solution_id = csln.id AND \
    r.configured_solution_solution = csln.solution AND \
    csln.solution = sln.id AND sln.challenge_problem_id = 5"`;

: << 'COMMENT'
for ARUN in $RUN_IDS; do
  peval evaluate run $ARUN;
done;
COMMENT

RESULTS_FILE=${BASEDIR}/results.csv;
echo "RUN_ID, DATASET, DURATION, LOAD_AVERAGE, LOAD_MAX, RAM_AVERAGE, \
      RAM_MAX, TEAM, F1, STATES, NUM_NONTERMINALS" > ${RESULTS_FILE};

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

        SCORE=`cat ${DIRNAME}/f1.txt`;
        echo -n ", ${TEAM}, ${SCORE}" >> ${RESULTS_FILE}

        # HACK: This totals up the number of states
        STATESDIR=`mktemp -d`/;
        RUN_OUTPUT=`sqlite3 ${DATABASE} "select output from run where id='${ARUN}'"`;
        cp ${DATADIR}/${RUN_OUTPUT} ${STATESDIR}
        cd ${STATESDIR}
        tar xjf ${RUN_OUTPUT}
        STATES=`cat pcfgla.states | cut -f2 | paste -sd+ | bc`
        NUM_NONTERMINALS=`wc -l pcfgla.states | cut -d' ' -f1`
        cd - > /dev/null;
        rm -r ${STATESDIR}
        echo ", ${STATES}, ${NUM_NONTERMINALS}" >> ${RESULTS_FILE}

    else
        echo "No file for run ${ARUN}";
    fi;
done;

# Clean up single results file
substitute_names ${RESULTS_FILE};

cd ${BASEDIR}
ARCHIVE=results-${MAC}.tar
tar -c -f ${ARCHIVE} ./*
pbzip2 ${ARCHIVE}
mv ${ARCHIVE}.bz2 ~/
cd - > /dev/null

echo "Temp dir: $BASEDIR"
# rm -rf ${BASEDIR}
exit
