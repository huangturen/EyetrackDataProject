#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'baoyanma'

from EyetrackerData import EyetrackerData
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

class EyetrackingDataBlinkFeatures(object):
    """docstring for Eyetrackdata
	This class can be used to process Eyetrackdata"""

    def __init__(self, filename):
        super(EyetrackingDataBlinkFeatures, self).__init__()
        self.filename = filename
        self.eyestate = []
        self.blinkcount = 0
        self.blinktime = 0
        self.readRawEyetrackingData()

    def readRawEyetrackingData(self):
        numData = [];
        data = open(self.filename)
        s = data.readlines()
        index = 0
        for line in s:
            line = line.split(",");
            if index < 10:
                index += 1
                continue
            eyestate = map(float,line[18:20])
            numData.append(eyestate)
        self.eyestate = numData

    def getCurFileBlinkFeatures(self):
        index = 0
        count = 0
        blinktime = 0
        blinkmoment = 0
        for index in range(len(self.eyestate)-1):
            if self.eyestate[index] == [4.0,4.0]:
                blinktime = blinktime+1
                blinkmoment = blinkmoment+1
            else:
                if blinkmoment>4:
                    count = count+1
                blinkmoment = 0
            index = index+1
        return np.array([count,blinktime])



class EyetrackingDataBlinkFeaturesFactory(object):
    def __init__(self):
        super(EyetrackingDataBlinkFeaturesFactory, self).__init__()
        self.filepath = ''
    def getEyeBlinkFeatures(self):
        self.filepath = './Eyetrackdata/csv/task26'
        files = os.listdir(self.filepath)
        eyeblinkfeatures = {}
        for item in files:
            if os.path.splitext(item)[1] == ".csv":
                curImgName = item.split('_')[-1][:-4]+'.jpg'
                curfilename = self.filepath+'/'+item
                blinkprocessor = EyetrackingDataBlinkFeatures(curfilename)
                filtereddata = blinkprocessor.getCurFileBlinkFeatures()
                if eyeblinkfeatures.has_key(curImgName):
                    eyeblinkfeatures[curImgName] = np.vstack((eyeblinkfeatures[curImgName],filtereddata))
                else:
                    eyeblinkfeatures[curImgName] = filtereddata
        return eyeblinkfeatures


