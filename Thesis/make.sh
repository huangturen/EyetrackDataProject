make clean
xelatex -no-pdf thesis
biber --debug thesis
xelatex thesis
