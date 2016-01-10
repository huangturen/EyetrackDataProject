#!/usr/bin/python
# -*- coding: utf-8 -*-
# "This programe is used to process eyetracker data"
#Author : Mabaoyan
#Time: 2015/11/04

import os
import sys
from EyetrackerData import EyetrackerData
from SubjectAssessmentData import SubjectAssessmentData
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats.stats as statstool
from math import *
from sklearn import svm
from sklearn.metrics import mean_squared_error
import corestats
from UserInfo import UserInfo
import csv
from EyetrackingDataBlinkFeatures import EyetrackingDataBlinkFeaturesFactory
import exceptions
featuresfilesavename = ''

class Eyetrack_Subject_Analysis(object):
    """docstring for Eyetrack_Subject_Analysis"""

    def __init__(self, eyetrackfolder,subjectassessmentfilename,userfilename):
        super(Eyetrack_Subject_Analysis, self).__init__()
        self.subject_processor = SubjectAssessmentData(subjectassessmentfilename)
        self.curEyetrackDataFolder = eyetrackfolder
        self.eyetrackDataFeature = np.array([])
        self.mosForEachImage = {}
        self.meanFeatureValueForEachImage = {}
        self.pupilDiameterset = {}
        self.individualPupilFeature = {}
        self.meanvalueforpupilsize = {}
        self.userinfofilename = userfilename
        self.userInfo = {}


    def getUserInfo(self):
        userinfoprocessor = UserInfo(self.userinfofilename)
        self.userInfo = userinfoprocessor.readUserInfoFile()

    def getDisparityAngularFile(self,disparityfilesavepath):
        files = os.listdir(self.curEyetrackDataFolder)
        featureSet = []
        index = 0
        for file in files:
            print index,file
            index = index+1
            if os.path.splitext(file)[1] == ".csv":
                curfile = self.curEyetrackDataFolder+'/'+file
                curEyetrackDataProcessor = EyetrackerData(curfile)
                curEyetrackDataProcessor.getDisparityAngularFile(disparityfilesavepath)


    def extrackEyetrackFeatures(self,basicEye):
        self.getUserInfo()
        files = os.listdir(self.curEyetrackDataFolder)
        featureSet = []
        index = 0
        for file in files:
            print index,file
            index = index+1
            if os.path.splitext(file)[1] == ".csv":
                curRecord = []
                splitresult = file.split('_')
                if len(splitresult) == 4:
                    imgName = splitresult[3][:-4]+'.jpg'
                    userName = splitresult[2]
                else:
                    imgName = splitresult[4][:-4]+'.jpg'
                    userName = splitresult[2]+'_'+splitresult[3]
                curRecord.append(imgName)
                if basicEye == 'left' or basicEye == 'right':
                    curfile = self.curEyetrackDataFolder+'/'+file
                elif basicEye == 'main' or basicEye == 'nomain':
                    print "Please Modify the folder for your eyetracker data"
                    if self.userInfo[userName] == -1:#-1 means you choose the main eye and 1 means you choose the Auxiliary eye
                        curfile = "Your left eye folder"+'/'+file
                    else:
                        curfile = "Your right eye folder"+file
                else:
                    print "Wrong choosed for the basic eye!";
                    return
                curEyetrackDataProcessor = EyetrackerData(curfile)
                curEyetrackFeatures = curEyetrackDataProcessor.getFixationFeatures()
                curRecord.extend(curEyetrackFeatures)
                featureSet.append(curRecord)
                print curRecord
        self.eyetrackDataFeature = np.array(featureSet)

    def getRelationBetweenEyetrackFeaturesAndSubjectScore(self,basicEye):
        """验证总体特征与主观评分之间的相关性"""
        self.extrackEyetrackFeatures(basicEye)
        self.mosForEachImage = self.subject_processor.getAvgMosForEachImage()
        #self.getPupilFeature()
        if len(self.meanFeatureValueForEachImage) == 0:
            self.getMeanFeatureValueForEachImage(basicEye)

        #self.svmTrain()
        # w,h = self.eyetrackDataFeature.shape
        # print w,h
        # percent=range(5,60,5)
        # plccset=np.array([])
        # for i in range(h-1):
        #     curPlcc = self.getRelationBetweenEyetrackFeatureAndSubjectScore(i)
        #     plccset = np.append(plccset,curPlcc)
        # plt.xlabel('Disparity Percent in front of the sorted serial')
        # plt.ylabel('LCC')
        # xmajorLocator = plt.MultipleLocator(5)
        # ymajorLocator = plt.MultipleLocator(0.1)
        # ax = plt.subplot(111)
        # plt.plot(percent,plccset,'-r*')
        # ax.xaxis.set_major_locator(xmajorLocator)
        # ax.yaxis.set_major_locator(ymajorLocator)
        # plt.grid()
        # plt.title('Relationship between the percentage we choosed and mos')
        #
        # plt.show()
        # self.getRelationBetweenEyetrackFeatureAndSubjectScore(6)

    def getRelationBetweenEyetrackFeatureAndSubjectScore(self,featureindex):
        """验证各特征与主观评分之间的相关性"""
        if len(self.mosForEachImage) != len(self.meanFeatureValueForEachImage):
            raise ValueError('the number of mos and feature is not equal,please check it')
        else:
            feature_score_pairlist = []
            for key in self.mosForEachImage:
                curList = [key,self.mosForEachImage[key],self.meanFeatureValueForEachImage[key][featureindex]]
                feature_score_pairlist.append(curList)
            feature_score_pairlist = np.array(feature_score_pairlist)
            feature_score_pairarray = np.array(feature_score_pairlist[:,1:], dtype=float)
            x = feature_score_pairarray[:,0]
            y = feature_score_pairarray[:,1]
            plcc,pval = statstool.pearsonr(x,y)
            srocc,pval = statstool.spearmanr(x,y)
            print "feature %d,%f,%f" %(featureindex,plcc,srocc)
            return plcc
            #plt.plot(x,'b-')
            #plt.plot(y,'r-')
            #plt.show()

    def getMeanFeatureValueForEachImage(self,basicEye):
        """获取针对每幅图像的平均特征值"""
        if len(self.eyetrackDataFeature) == 0:
            self.extrackEyetrackFeatures(basicEye)
        classific = {}
        index = 0
        for item in self.eyetrackDataFeature:
            imgName = item[0]
            if imgName not in classific:
                classific[imgName] = set([index])
            else:
                classific[imgName].add(index)
            index += 1
        # blinkfeaturesprocessor = EyetrackingDataBlinkFeaturesFactory()
        # blinkfeatures = blinkfeaturesprocessor.getEyeBlinkFeatures()
        for key in classific:
            serial = list(classific[key])
            tmp2 = self.eyetrackDataFeature[serial,1:]
            tmp = np.array(tmp2,dtype=float)
            self.meanFeatureValueForEachImage[key] = np.mean(tmp,axis = 0)
            # tmp3 = np.mean(blinkfeatures[key],axis=0)
            # self.meanFeatureValueForEachImage[key] = np.hstack((tmp3,self.meanFeatureValueForEachImage[key]))
            #self.meanFeatureValueForEachImage[key] = np.append(self.meanFeatureValueForEachImage[key],self.meanvalueforpupilsize[key])
    def getPupilFeature(self):
        individualpupilsize = self.calAvgPupilDiameter()
        averagepupilsizeforrecord = self.calAvgPupilForRecord()
        meanvalueforpupilsize = {}
        for key in averagepupilsizeforrecord:
            splitResult = key.split('_')
            imgName = splitResult[-1]
            if len(splitResult) == 2:
                userName = splitResult[0]
            else:
                userName = splitResult[0]+'_'+splitResult[1]
            curpupilsize = averagepupilsizeforrecord[key]/individualpupilsize[userName]
            if imgName not in meanvalueforpupilsize:
                meanvalueforpupilsize[imgName] = curpupilsize
            else:
                meanvalueforpupilsize[imgName] = np.append(meanvalueforpupilsize[imgName],curpupilsize)

        for key in meanvalueforpupilsize:
            meanvalueforpupilsize[key] = meanvalueforpupilsize[key].reshape(len(meanvalueforpupilsize[key])/2,2)
            meanvalueforpupilsize[key] = np.mean(meanvalueforpupilsize[key],axis=0)

        self.meanvalueforpupilsize = meanvalueforpupilsize


    def calAvgPupilDiameter(self):
        avgpupilsize = {}
        for key in self.pupilDiameterset:
            avgpupilsize[key] = np.mean(self.pupilDiameterset[key],axis=0)
        return avgpupilsize

    def calAvgPupilForRecord(self):
        avgpupilsizeForRecord = {}
        for key in self.individualPupilFeature:
            avgpupilsizeForRecord[key] = np.mean(self.individualPupilFeature[key],axis=0)
        return avgpupilsizeForRecord

    def getEyetrackerDataFeatures(self,basicEye,featuresfilesavename):
        """svm 学习训练 """
        self.getRelationBetweenEyetrackFeaturesAndSubjectScore(basicEye)
        feature_mos_set = np.array([])
        num = 0
        for key in self.mosForEachImage:
            cur_set = np.array(self.mosForEachImage[key])
            cur_set = np.append(cur_set,self.meanFeatureValueForEachImage[key])
            length = len(cur_set)
            feature_mos_set = np.append(feature_mos_set,cur_set)
            num += 1
        feature_mos_set = feature_mos_set.reshape(num,length)
        csvfile=file(featuresfilesavename,'a+')
        writer=csv.writer(csvfile)
        writer.writerows(feature_mos_set)
        csvfile.close()
        # w,h = feature_mos_set.shape
        #
        #
        # kernels = ['linear','poly','rbf']
        # for j in range(len(kernels)):
        #     LCC_rbf = [];SROCC_rbf = [];RMSE_rbf = []
        #     for i in range(1000):
        #         print i
        #         randlist = range(w)
        #         np.random.shuffle(randlist)
        #
        #         trainindex = randlist[0:60]
        #         testindex = randlist[60:w]
        #
        #         train_feature = list(feature_mos_set[trainindex,1:])
        #         train_label = list(feature_mos_set[trainindex,0])
        #
        #         test_feature = list(feature_mos_set[testindex,1:])
        #         test_label = feature_mos_set[testindex,0]
        #
        #         '''============= train and predict by svr with rbf kernel ==============='''
        #         # rbf kernel
        #         clf = svm.SVR(kernel=kernels[j], C=1000,gamma=0.1)
        #         pred = clf.fit(train_feature, train_label).predict(test_feature)
        #
        #         # rbf metrics
        #         srocc,p1 =  statstool.spearmanr(pred,test_label)
        #         plcc,p2 =  statstool.pearsonr(pred,test_label)
        #         rmse = sqrt(mean_squared_error(pred,test_label))
        #         LCC_rbf.append(plcc);SROCC_rbf.append(srocc);RMSE_rbf.append(rmse)
        #
        #
        #     sts_lcc = corestats.Stats(LCC_rbf)
        #     sts_srocc = corestats.Stats(SROCC_rbf)
        #     sts_rmse = corestats.Stats(RMSE_rbf)
        #     print "all_feature metrics %s:plcc:%f,srocc:%f,rmse:%f " %(kernels[j],sts_lcc.avg(),sts_srocc.avg(),sts_rmse.avg())

basicEye = ['left','right','main','nomain']
eye_feature = {'left':'features_left.csv','right':'features_right.csv','main':'features_main.csv','nomain':'features_nomain.csv'}
def main():
    if sys.argv.__len__()<4:
        print sys.argv
        exit_with_help()

    try:
        originalfilepath = sys.argv[2]
        filesavepath = sys.argv[3]
    except IndexError:
        print "Please Confirm your EyetrackData set path!"
        return
    finally:
        subjectfilename = './ss_subjectAssessmentScore_aferProcessed.csv'
        userInfoFile = './participantInfo.csv'
        print 'place 1'
    print sys.argv,sys.argv.__len__()
    if sys.argv.__len__() == 4 and sys.argv[1] == '-d':
        print "You want to get all disparity angular files."
        if not os.path.exists(filesavepath):
            os.mkdir(filesavepath)
        dprocessor = Eyetrack_Subject_Analysis(originalfilepath,subjectfilename,userInfoFile)
        dprocessor.getDisparityAngularFile(filesavepath)
    elif sys.argv.__len__() == 5 and sys.argv[1] == '-f' and sys.argv[4] in basicEye:
        print "You are try to get features of eyetracking data!"
        basiceye = sys.argv[4]
        if not os.path.exists(filesavepath):
            os.mkdir(filesavepath)
        featuresfilesavename = filesavepath+'/'+eye_feature[basiceye]
        if os.path.exists(featuresfilesavename):
            b = raw_input('The feature file %s is existed!Do you want to regenerate features file?(y/n):'%featuresfilesavename)
            if b == 'y':
                os.remove(featuresfilesavename)
            else:
                return
        fprocessor = Eyetrack_Subject_Analysis(originalfilepath,subjectfilename,userInfoFile)
        fprocessor.getEyetrackerDataFeatures(basiceye,featuresfilesavename)

    else:
        exit_with_help()



    # subjectfilename = './ss_subjectAssessmentScore_aferProcessed.csv'
    # filepath = './Eyetrackdata/csv/processed/task26'
    # userInfoFile = './participantInfo.csv'




if __name__ == '__main__':

    def exit_with_help():


        print ("""\
 Usage:eyetrackerDataProcess.py type_options InputFolder outputFolder [basicEye]
 
 type_options :
 -d get the disparity angular for each person by each image 
     InputFolder is the original eyetrackdata folder
     outputFolder is the folder where you want to save the disparity angular files.
 -f get the features and write them as a csv file 
    InputFolder is the original eyetracker data folder
    outputfile is the file path which you want to save the features in(filepath + filename).
    basicEye[left|right|main|nomain] one of the four basic eyes,and left means we use the eyetracker data which is filtered based on left eye.so do others.""")
        sys.exit(1)
    main()









