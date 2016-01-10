Usage:eyetrackerDataProcess.py type_options InputFolder outputFolder [basicEye]
 
 type_options :
 -d get the disparity angular for each person by each image 
     InputFolder is the original eyetrackdata folder
     outputFolder is the folder where you want to save the disparity angular files.
 -f get the features and write them as a csv file 
    InputFolder is the original eyetracker data folder
    outputfile is the file path which you want to save the features in(filepath + filename).
    basicEye[left|right|main|nomain] one of the four basic eyes,and left means we use the eyetracker data which is filtered based on left eye.so do others

e.g $:python eyetrackerDataProcess.py -d eyetrackingdatafolder disparitysavefolder 

e.g $:python eyetrackerDataProcess.py -f eyetrackingdatafolder featuresavepath left
