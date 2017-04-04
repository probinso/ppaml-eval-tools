#!/bin/bash

# XXX: Fix these names
substitute_names () {
    sed -i 's/d1f729650601f5f1b020fdc8f055c3c5bc71de2e.tar.bz2/Small/' \
        $1;
    sed -i 's/05b892c4fd24002b5227204d9e77ba222c56993e.tar.bz2/Mid/' \
        $1;
    sed -i 's/cb5d847e330fbb5a344c43602eaf9da0c084e9c0.tar.bz2/Full/' \
        $1;
}


MAC=`ifconfig eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | tail -c 3`

BASEDIR=`mktemp -d /tmp/cp7_extract_XXX`/;

DATADIR=~/.local/share/peval/;
DATABASE=${DATADIR}/index.db;

RUN_IDS=`sqlite3 $DATABASE "SELECT r.id FROM Run r, configured_solution \
    csln, solution sln WHERE r.configured_solution_id = csln.id AND \
    r.configured_solution_solution = csln.solution AND \
    csln.solution = sln.id AND sln.challenge_problem_id = 7 \
    AND sln.challenge_problem_revision_major = 0 \
    ORDER BY r.id"`;

: << 'COMMENT'
for ARUN in $RUN_IDS; do
  peval evaluate run $ARUN;
done;
COMMENT

RESULTS_FILE=${BASEDIR}/results.csv;
echo "RUN_ID, DATASET, DURATION, LOAD_AVERAGE, LOAD_MAX, RAM_AVERAGE, \
      RAM_MAX, TEAM, ROOT_MEAN_SQUARED_ERROR" > ${RESULTS_FILE};

# Directory for solution output to go in
mkdir ${BASEDIR}/solution_results

for RUN in $RUN_IDS; do

    RESULT=`sqlite3 $DATABASE "select id from evaluation where run='$RUN'"`

    TEAM=`sqlite3 $DATABASE "SELECT description FROM team t, engine e, \
        Run r WHERE r.engine = e.id AND e.team = t.id AND r.id = $RUN;"`;

    if [[ "$TEAM" = "{CH,D}imple" ]]; then TEAM=Gamalon; fi;

    DIRNAME=${BASEDIR}/${TEAM}/${RUN};
    mkdir -p ${DIRNAME};

    RESULTARCHIVE=${DATADIR}/${RESULT};
    if [[ ! -f ${RESULTARCHIVE} ]]; then
	echo "WARNING: No result for run ${RUN}: the run has not been evaluated.";
    else
	cd ${DIRNAME};
	tar -xjf ${RESULTARCHIVE};
	cd - > /dev/null;

	###### THE MAX AND AVERAGE COLUMNS ARE STORED BACKWARDS #####
	ROW=`sqlite3 -separator ', ' ${DATABASE} "select id, dataset, duration, \
         load_max, load_average, ram_max, ram_average from run \
         where id='${RUN}'"`;
	echo -n "${ROW}, $TEAM, " >> ${RESULTS_FILE};

	# Example of eval_metric.csv
	# Root mean squared error: 0.893553223785
	CSV="${DIRNAME}/eval_metric.csv"
	if [[ ! -f "$CSV" ]]; then
	    echo "INFO: No evaluation metric file '$CSV' found! Emitting empty score column."
	else
	    SCORE=`awk -F"[ ]" '{print $5}' ${DIRNAME}/eval_metric.csv`
	    if [[ ! -n "${SCORE}" ]]; then
		echo "ERROR: No sum-of-squared-errors for $RUN: Evaluator produced malformed output.";
	    fi;
	    echo -n "${SCORE}" >> ${RESULTS_FILE};
            echo "INFO: successfully added run $RUN."
	fi
	echo >> $RESULTS_FILE
    fi;

    # Here we copy the solution result into the results directory
    SOLUTION_OUTPUT_HASH=`sqlite3 ${DATABASE} "select output from run where id='${RUN}'"`;
    # `peval inspect` inpacks a directory into a tmp directory and returns the name
    # We then grab it and move it
    SOLUTION_OUTPUT_DIR=`peval inspect $SOLUTION_OUTPUT_HASH | tail -1 | awk -F"[ ]" '{print $4}'`
    mv $SOLUTION_OUTPUT_DIR ${BASEDIR}/solution_results/$RUN
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
