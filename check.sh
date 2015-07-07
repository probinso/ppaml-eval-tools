for i in /tmp/peval*; do 
    var=${i%.*};
    var=${var#*.};
    for filename in `grep -l ${var} ~/slurm/stdouterr/*`; do
	echo "###################################################################"
	echo ${filename}
	tail ${filename}
    done
done
