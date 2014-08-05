default: docs.pdf

docs.pdf: peval.png docs.tex
	pdflatex docs.tex

peval.png: peval.dot
	circo -Tpng peval.dot -o peval.png
