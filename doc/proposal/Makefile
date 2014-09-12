default: cases.pdf

requirements.pdf: requirements.tex
	pdflatex requirements.tex

notes.pdf: notes.tex
	pdflatex notes.tex

erd.pdf: erd.dot
	dot -Tpdf erd.dot -o erd.pdf

cases.pdf: cases.tex
	pdflatex cases.tex

docs.pdf: peval.png docs.tex
	pdflatex docs.tex

peval.png: peval.dot
	circo -Tpng peval.dot -o peval.png
