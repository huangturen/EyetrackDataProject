This is main class to process 'train', you can use this project in the follow situations

Usage:featuresTrainAndAnalysis.py [options] [file]

 options-command :
 -c get the correlation
     --dm disparity and mos
    file   multilevel different level [5%,10%,....45%,50%] which percentage have the highest correlation between disparity and mos
     --g the gain of each feature except the basic features
    file   the basic eye ,should choosed from [right, left , main, nomain]
 -t get the train result
     --fm all features and mos
     file   the train file label by basic eye [right, left , main, nomain]
 -mt get the train result for modified features
     file   the train file label by basic eye [right, left , main, nomain]
 -cm get the comparision result between models before and after modified

e.g

$:python featuresTrainAndAnalysis.py -t --fm right 

it means you excute the script featuresTrainAndAnalysis.py with python to get the train results on all features based on the file from right eye features
