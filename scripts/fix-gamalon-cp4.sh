#!/bin/bash

# Run this after a raw export of the databases to a scratch space,
# and run it in a scratch space ... not your repo working directory.
#
# After doing extract-from-db.sh, Gamalon 4.1, 4.5, 4.10 will be in seconds.
# Here we just convert those to milliseconds, modifying the files in place.
# Only run this once!
# In the repo working directory, delete the entire cp4/ directory.
# Then move this modified cp4 directory over to the repo working directory.
#
# git will recognize that most of the files match what's in the repo, except
# for any new exports you did.

if ! [ -d cp4 ]
then
	echo "There should be a cp4/ directory from an export. Exiting"
	exit 1
fi

find cp4/Gamalon -name problem-1-query-1-metric-1.csv -exec perl sec-to-ms.pl {} 1 \;
find cp4/Gamalon -name problem-1-query-1-metric-2.csv -exec perl sec-to-ms.pl {} 1 \;
find cp4/Gamalon -name problem-5-query-1-metric-1.csv -exec perl sec-to-ms.pl {} 1 \;
find cp4/Gamalon -name problem-5-query-2-metric-1.csv -exec perl sec-to-ms.pl {} 1 \;
find cp4/Gamalon -name problem-10-metrics.csv -exec perl sec-to-ms.pl {} 3 \;

echo "Files have been fixed up. DO NOT RUN THIS AGAIN."

