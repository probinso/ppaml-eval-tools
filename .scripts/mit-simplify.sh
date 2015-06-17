#!/bin/bash

for pattern in pcfg;
    rm -f $( ls -t | grep ${pattern} | tail -n +3);
done


for pattern in graphs hmm homophily lda lifted qmr recursion regression cp5 venture-0.3;
    rm -f $( ls -t | grep ${pattern} | tail -n +2);
done

for i in $(ls -t *.tar.bz2); do 
    label=${i%%.tar.bz2};
    label=${label##venture-};
    echo `md5sum $i | awk '{print $1}' ` $label `date -r "$i" +"%F"` "(4.x)"; 
done | column -t
