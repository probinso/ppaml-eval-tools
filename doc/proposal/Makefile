default: docs

docs: peval.png neval.png docs.tex
	pdflatex docs.tex

peval.png: peval.dot
	circo -Tpng peval.dot -o peval.png
