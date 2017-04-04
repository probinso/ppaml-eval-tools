#!/bin/bash

DBPATH=$HOME/.local/share/ppaml
DATABASE=$DBPATH/index.db

if (( $# != 2))
then
	echo "Run this on the Linux VM where the database lives."
	echo "Usage: $0 CPNUM MACHINE"
	echo "CPNUM is an integer and MACHINE is the name of the machine/database"
	exit 1
else
	CPNUM=$1
	MACHINE=$2
fi

if ! [ -r $DATABASE ]
then
	echo "Error: $DATABASE is not a readable file"
	exit 1
fi

# Get all run IDs for challenge problem CPNUM

RUN_IDS=`sqlite3 $DATABASE "SELECT r.id FROM Run r, configured_solution csln, solution sln WHERE \
	r.configured_solution_id = csln.id AND r.configured_solution_solution = csln.solution AND \
	csln.solution = sln.id AND \
	sln.challenge_problem_id = $CPNUM"`

# Dump for each run...

STARTDIR=`pwd`

for ARUN in $RUN_IDS
do
	TEAM=`sqlite3 $DATABASE "SELECT description FROM team t, engine e, Run r WHERE \
		r.engine = e.id AND e.team = t.id AND r.id = $ARUN;"`
	if [[ "$TEAM" = "{CH,D}imple" ]]; then TEAM=Gamalon; fi

	CONFIG=`sqlite3 $DATABASE "SELECT filename FROM Run r, configured_solution csln WHERE \
	r.configured_solution_id = csln.id AND r.configured_solution_solution = csln.solution AND \
	r.id = $ARUN"`

	OUTFILE=`sqlite3 $DATABASE "SELECT output FROM Run r WHERE r.id=$ARUN"`

	# directory we will export to
	RESULT="output/cp$CPNUM/$TEAM/$CONFIG/$MACHINE-$ARUN"

	if ! [ -r $DBPATH/$OUTFILE ]
	then
		echo "Error: database refers to $OUTFILE, which doesn't exist in $DBPATH"
		exit 1
	fi

	if [ -d "$STARTDIR/$RESULT" ]
	then
		echo "Error: $STARTDIR/$RESULT already exists, terminating"
		exit 1
	fi

	mkdir -p "$STARTDIR/$RESULT"
	cd "$STARTDIR/$RESULT"
	if [ $? != 0 ]
	then
		echo "Error: could not cd to $RESULT"
		exit 1
	fi

	echo "Extracting $RESULT"
	# For CP4, careful to only extract desired results
	if [[ $CPNUM == 4 ]]
	then
		tar -xf $DBPATH/$OUTFILE --wildcards "problem-*.csv"
	else
		tar xf $DBPATH/$OUTFILE
	fi

	if [ $? != 0 ]
	then
		echo "Error: un-tar problem, terminating"
		exit 1
	fi

done
