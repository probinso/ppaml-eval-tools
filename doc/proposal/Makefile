default: cases.pdf

erd.pdf: erd.dot
	dot -Tpdf erd.dot -o erd.pdf

cases.pdf: cases.tex
	pdflatex cases.tex

docs.pdf: peval.png docs.tex
	pdflatex docs.tex

peval.png: peval.dot
	circo -Tpng peval.dot -o peval.png
