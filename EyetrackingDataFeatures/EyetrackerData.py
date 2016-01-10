#!/usr/bin/python
# -*- coding: utf-8 -*-
# "This programe is used to process eyetracker data"
#Author : Mabaoyan
#Time: 2015/11/04

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sg
import csv

class EyetrackerData(object):
    """docstring for Eyetrackdata
	This class can be used to process Eyetrackdata"""

    def __init__(self, filename):
        super(EyetrackerData, self).__init__()
        self.fileName = filename
        self.filteredData = np.array([])
        self.fixationData = np.array([])
        self.eyetrackdatafeature = np.array([])
        self.eyetrackdatacount = 0.0
        self.disparityset=np.array([])
        self.readEyetrackDataFile()

    """-----------------------------------加载数据-------------------------------------"""

    def readEyetrackDataFile(self):
        title = [];
        numData = [];
        data = open(self.fileName)
        s = data.readlines()
        index = 0
        for line in s:
            line = line.split(",");
            if index is 0:
                index += 1
                title = line
                continue
            numData.append(line)
        self.filteredData = np.array(numData)
        m,n = self.filteredData.shape
        self.eyetrackdatacount = m


    def setFileName(self,filename):
        """设置当前文件名称"""
        self.fileName = filename
        self.readEyetrackDataFile()


    def getFilteredData(self):
        """获取滤波后的数据"""
        return self.filteredData


    def getFixationData(self):
        """获取滤波后的数据"""
        self.calFixationData()
        return self.fixationData

    """-----------------------------------获取滤波后的点-------------------------------------"""

    def calFixationData(self):
        filtereddata = self.filteredData
        m, n = filtereddata.shape
        Fixation = np.array([])
        curFixation = np.array([])
        start = 0
        end = 0
        count = 0

        """ 将同一注视点的记录合并 """
        for i in range(m):
            if str(filtereddata[i, 1]) == 'Fixation':
                end += 1
                count += 1
            elif str(filtereddata[i, 1]) != str(filtereddata[i - 1, 1]):
                end = start + count - 1
                tmp = np.array(filtereddata[end, 0:4])
                a = np.array(filtereddata[start:end, 4:24], dtype=float)
                tmp2 = np.mean(a, axis=0)
                p = np.append(tmp, tmp2)
                if Fixation.size == 0:
                    Fixation = p
                else:
                    Fixation = np.vstack((Fixation, p))
                count = 0
            else:
                i += 1
                start = i
                continue
            i += 1

        self.fixationData = Fixation


    """-----------------------------------眼动数据的特征提取-------------------------------------"""
    def getEyetrackDataFeature(self):
        self.getFixationFeatures()

    def getFixationFeatures(self):
        """-----------------------------------获取眼动数据的静态特征-------------------------------------"""
        self.readEyetrackDataFile()
        self.getFixationData()
        fix_num = self.getFixationNum(self.fixationData)
        fix_maxlen = self.getFixationMaxLen(self.filteredData)
        fix_avglen = self.getFixationAvgLen(self.filteredData)
        pupilfeature = self.getRatioBetweenFixationAndOverall(self.filteredData)
        self.eyetrackdatafeature =[float(item)/self.eyetrackdatacount for item in [fix_num,fix_maxlen,fix_avglen]]
        self.eyetrackdatafeature = np.append(self.eyetrackdatafeature,pupilfeature)
        disparityFeature = self.getDisparityFeatures()
        self.eyetrackdatafeature = np.append(self.eyetrackdatafeature,disparityFeature)
        saccadefeatures = self.getSaccadeDisparityFeature()
        self.eyetrackdatafeature = np.append(self.eyetrackdatafeature,saccadefeatures)
        return  self.eyetrackdatafeature

    def getFixationNum(self, fixationdata):
        """获取当前文件中注视点个数"""
        try:
            m, n = fixationdata.shape
        except ValueError:
            m = 1
        return m

    def getFixationMaxLen(self, filtereddata):
        """获取最长注视点的长度"""
        w, h = filtereddata.shape
        maxLen = 0
        curLen = 0
        for i in range(w):
            if str(filtereddata[i, 1]) == 'Fixation':
                curLen += 1
            elif str(filtereddata[i, 1]) != str(filtereddata[i - 1, 1]):
                if curLen > maxLen:
                    maxLen = curLen
                curLen = 0
            else:
                i += 1
                continue
            i += 1
        return maxLen

    """-----------------------------------注视点平均长度-------------------------------------"""

    def getFixationAvgLen(self, filtereddata):
        """获取注视点的长度的均值"""
        w, h = filtereddata.shape
        sumLen = 0
        curLen = 0
        count = 0.0
        for i in range(w):
            if str(filtereddata[i, 1]) == 'Fixation':
                curLen += 1
            elif str(filtereddata[i, 1]) != str(filtereddata[i - 1, 1]):
                sumLen += curLen
                curLen = 0
                count += 1
            else:
                i += 1
                continue
            i += 1
        return sumLen / count

    def getPupilDiameter(self):
        """计算左右眼瞳孔的直径的均值"""
        pupilDiameterSet = np.array([])
        fixation_pupilDiameterset = np.array([])
        for item in self.filteredData:
            curItem = np.array(item[-2:],dtype=float)
            if pupilDiameterSet.size == 0:
                pupilDiameterSet = curItem
            else:
                pupilDiameterSet = np.vstack((pupilDiameterSet,curItem))
        return pupilDiameterSet

    def getRatioBetweenFixationAndOverall(self,filtereddata):
        curpupilset = np.array([])
        curfixationpupilset = np.array([])
        for item in filtereddata:
            tmp = np.array(item[-2:],dtype=float)
            if curpupilset.size == 0:
                curpupilset = tmp
            else:
                curpupilset = np.vstack((curpupilset,tmp))
            if item[1] == 'Fixation':
                if curfixationpupilset.size == 0:
                    curfixationpupilset = tmp
                else:
                    curfixationpupilset = np.vstack((curfixationpupilset,tmp))

        avgpupilsize_fixation = np.mean(curfixationpupilset,axis=0)
        avgpupilsize_overall = np.mean(curpupilset,axis=0)
        return avgpupilsize_fixation/avgpupilsize_overall

    def getPupilTopIndexRation(self,filtereddata):
        curpupilset = np.array([])
        for item in filtereddata:
            tmp = np.array(item[-2:],dtype=float)
            if curpupilset.size == 0:
                curpupilset = tmp
            else:
                curpupilset = np.vstack((curpupilset,tmp))
        fft_left = np.fft.rfft(curpupilset[:,0])/len(curpupilset)
        xfp_left = np.abs(fft_left)
        fft_right = np.fft.rfft(curpupilset[:,1])/len(curpupilset)
        xfp_rigth = np.abs(fft_right)
        pupilFeature = np.append(np.mean(xfp_left),np.mean(xfp_rigth))
        return pupilFeature
    """-----------------------------------视差值的计算-------------------------------------"""
    def getDisparityFeatures(self):
        disparitySet = self.getDisparitySet(self.filteredData)
        avg_disparity = self.getAvgDisparity(disparitySet)  #视差均值
        std_disparity = self.getStdDisparity(disparitySet) #视差方差
        avg_fixation_disparity = self.getFixationAvgDisparityFeatures(disparitySet)#注视点处视差均值
        avg_top4p_maxdisparity = self.getAvgTopFivePercentMaxDisparity(disparitySet)#最大值前45%的视差均值
        avg_top4p_mindisparity = self.getAvgTopFivePercentMinDisparity(disparitySet)#最小值前45%的视差均值
        disparityfeatures = np.array([avg_disparity,std_disparity,avg_fixation_disparity,avg_top4p_maxdisparity,avg_top4p_mindisparity])
        avg_fix_top4p_maxdisparity = self.getFixAvgTopFivePercentMaxDisparity(disparitySet,45)#注视区域最大值前45%的视差均值
        avg_fix_top4p_mindisparity = self.getFixAvgTopFivePercentMinDisparity(disparitySet,45)#注视区域最小值前45%的视差均值
        disparityfeatures = np.append(disparityfeatures,[avg_fix_top4p_maxdisparity,avg_fix_top4p_mindisparity])
        avg_vergence = self.getVergenceMeanValue(disparitySet) #扫视过程视差变化均值
        disparityfeatures = np.append(disparityfeatures,avg_vergence)
        return disparityfeatures

    def getDiffLevelDisparitySet(self):
        disparitySet = self.getDisparitySet(self.filteredData)
        diffLevelDisparitySet = self.getDifferentLevelDisparitySet(disparitySet)
        return diffLevelDisparitySet

    def getDisparitySet(self,filtereddata):
        curdisparityset = np.array([])
        for items in filtereddata:
            item = np.array(items[8:],dtype=float)
            lefteye = item[0:3]
            righteye = item[3:6]
            leftgaze = item[6:9]
            rightgaze = item[9:12]
            disparityangular = self.calculateDisparityAngular(lefteye,righteye,leftgaze,rightgaze)
            curItem = np.array([items[1],disparityangular])
            if curdisparityset.size == 0:
                curdisparityset = curItem
            else:
                curdisparityset = np.vstack((curdisparityset,curItem))
        disparityset = sg.wiener(np.array(curdisparityset[:,1],dtype=float))
        dispritysettmp = np.array([])
        for i in range(len(curdisparityset)):
            curitem = np.array([curdisparityset[i,0],disparityset[i]])
            if dispritysettmp.size ==0:
                dispritysettmp = curitem
            else:
                dispritysettmp = np.vstack((dispritysettmp,curitem))
        disparityset = dispritysettmp
        # plt.plot(map(float,curdisparityset[:,1]))
        # plt.xlabel(u'采样点',fontsize = 18)
        # plt.ylabel(u'视差角(rad)',fontsize = 18)
        # #plt.plot(disparityset)
        # plt.show()
        return disparityset

    def getDisparityAngularFile(self,disparityAngularSaveFolder):
        disparitySet = self.getDisparitySet(self.filteredData)
        disparitysavename = self.getDisparitySaveFileName(disparityAngularSaveFolder)
        if not disparitysavename == '':
            self.writeArrayToCsvFile(disparitysavename,disparitySet)
        else:
            exit(1)

    def writeArrayToCsvFile(self,filename,disparityset):
        csvfile=file(filename,'a+')
        writer=csv.writer(csvfile)
        writer.writerows(disparityset)
        csvfile.close()
    def getDisparitySaveFileName(self,disparityAngularSaveFolder):
        filepath = os.path.splitext(self.fileName)
        filename = filepath[0].split('/')
        if not os.path.exists(disparityAngularSaveFolder):
            os.mkdir(disparityAngularSaveFolder)
        disparityfilesavename = disparityAngularSaveFolder+'/'+filename[-1]+'_disparityset'+filepath[-1]
        if os.path.exists(disparityfilesavename):
            print 'the file is existed,if you want to regenerate this file ,please remove the older one!'
            return ''
        else:
            return disparityfilesavename

    def getAvgDisparity(self,disparityset):
        disparity = np.array(disparityset[:,1],dtype=float)
        avg_disparity = np.median(disparity)
        return avg_disparity

    def getStdDisparity(self,disparityset):
        disparity = np.array(disparityset[:,1],dtype=float)
        std_disparity = np.std(disparity)
        return std_disparity

    def getAvgTopFivePercentMaxDisparity(self,disparityset):
        disparitySet = np.array(disparityset[:,1],dtype=float)
        abs_disparity = np.abs(disparitySet)
        disparity_index = np.argsort(abs_disparity)
        sz = disparity_index.size
        topfiveMax = sz*0.45
        topMaxDisparityindex = filter(lambda x:x>=sz-topfiveMax,disparity_index)
        topFiveMaxAvgDisparity = np.mean(np.array(disparitySet[topMaxDisparityindex]))
        return topFiveMaxAvgDisparity

    def getAvgTopFivePercentMinDisparity(self,disparityset):
        disparitySet = np.array(disparityset[:,1],dtype=float)
        abs_disparity = np.abs(disparitySet)
        disparity_index = np.argsort(abs_disparity)
        sz = disparity_index.size
        topfiveMax = sz*0.45
        topMaxDisparityindex = filter(lambda x:x<=topfiveMax,disparity_index)
        topFiveMinAvgDisparity = np.mean(np.array(disparitySet[topMaxDisparityindex]))
        return topFiveMinAvgDisparity

    def getFixationAvgDisparityFeatures(self,disparityset):

        fixationSet = filter(lambda x:x[0] == 'Fixation',disparityset)
        curfixationdisparityset = np.array(fixationSet)
        curfixationdisparityset = np.array(curfixationdisparityset[:,1],dtype=float)
        avg_fixation_disparity = np.median(curfixationdisparityset)
        return avg_fixation_disparity

    def getFixAvgTopFivePercentMaxDisparity(self,disparityset,percent):
        disparityFixSet = filter(lambda x:x[0] == 'Fixation',disparityset)
        disparityFixSet = np.array(disparityFixSet)
        disparityFixSet = np.array(disparityFixSet[:,1],dtype=float)
        abs_disparity = np.abs(disparityFixSet)
        disparity_index = np.argsort(abs_disparity)
        sz = disparity_index.size
        topfiveMax = sz*0.01*percent
        topMaxDisparityindex = filter(lambda x:x>=sz-topfiveMax,disparity_index)
        topFiveMaxAvgDisparity = np.mean(np.array(disparityFixSet[topMaxDisparityindex]))
        return topFiveMaxAvgDisparity

    def getFixAvgTopFivePercentMinDisparity(self,disparityset,percent):
        disparityFixSet = filter(lambda x:x[0] == 'Fixation',disparityset)
        disparityFixSet = np.array(disparityFixSet)
        disparityFixSet = np.array(disparityFixSet[:,1],dtype=float)
        abs_disparity = np.abs(disparityFixSet)
        disparity_index = np.argsort(abs_disparity)
        sz = disparity_index.size
        topfiveMax = sz*0.01*percent
        topMaxDisparityindex = filter(lambda x:x<=topfiveMax,disparity_index)
        topFiveMinAvgDisparity = np.mean(np.array(disparityFixSet[topMaxDisparityindex]))
        return topFiveMinAvgDisparity

    def getVergenceMeanValue(self,disparityset):

        disparitySet = np.array(disparityset[:,1],dtype=float)
        vergence = np.array([])
        for i in range(disparitySet.size-1):
            curverge = disparitySet[i+1]-disparitySet[i]
            vergence = np.append(vergence,curverge)
        avg_verge = np.mean(vergence)
        return avg_verge

    def getSaccadeDisparityFeature(self):
        maxSaccadeDisparity = 0
        maxJumpDisparity = 0
        SaccadeDisparity = np.array([])
        if  self.fixationData.size == 24:
            item = np.array(self.fixationData[8:],dtype=float)
            lefteye = item[0:3]
            righteye = item[3:6]
            leftgaze = item[6:9]
            rightgaze = item[9:12]
            curDisparity = self.calculateDisparityAngular(lefteye,righteye,leftgaze,rightgaze)
            return np.array([curDisparity,curDisparity])

        for item in self.fixationData:
            try:
                item = np.array(item[8:],dtype=float)
                lefteye = item[0:3]
                righteye = item[3:6]
                leftgaze = item[6:9]
                rightgaze = item[9:12]
            except ValueError :
                print self.fixationData,self.fixationData.shape
                #print item
                continue
            curDisparity = self.calculateDisparityAngular(lefteye,righteye,leftgaze,rightgaze)
            SaccadeDisparity = np.append(SaccadeDisparity,curDisparity)
        maxSaccadeDisparity = (SaccadeDisparity.size>0 and np.max(SaccadeDisparity)) or 0

        fixationNum = SaccadeDisparity.size
        disparityDiffSum = 0
        for i in range(fixationNum-1):
            curDiff = SaccadeDisparity[i+1]-SaccadeDisparity[i]
            if np.abs(curDiff)>np.abs(maxJumpDisparity):
                maxJumpDisparity = curDiff
            disparityDiffSum += curDiff
        return map(float,[maxJumpDisparity,disparityDiffSum/(fixationNum-1)])
    # def getMaxSaccadeDisparity(self,filtereddata):
    #     curFixation = np.array([])
    #     for item in filtereddata:
    #         if item[1] == 'Fixation':
    #             curFixation = (curFixation.size == 0 and item[8:]) or np.vstack((curFixation,item[8:]))
    #         else:
    #             pass



    def calculateDisparityAngular(self, lefteye, righteye, leftgaze, rightgaze):
        """ 计算视差（以视差角来表示） """
        origcrossangle = self.calculateCrossAngle(lefteye, righteye, leftgaze, rightgaze)
        """ 计算屏幕上的汇聚角 """
        crosspoint = (leftgaze + rightgaze) / 2.0
        screenangle = self.calculateCrossAngle(lefteye, righteye, crosspoint, crosspoint)
        disparityangule = screenangle - origcrossangle
        return disparityangule


    def calculateCrossAngular(self, line1, line2):
        l1 = np.sqrt(line1.dot(line1))
        l2 = np.sqrt(line2.dot(line2))
        cos_angle = line1.dot(line2) / (l1 * l2)
        angle = np.arccos(cos_angle)
        return angle


    def calculateCrossAngle(self, lefteye, righteye, leftgaze, rightgaze):
        leftsightline = leftgaze - lefteye
        rightsightline = rightgaze - righteye
        angle = self.calculateCrossAngular(leftsightline, rightsightline)
        return angle



    """-----------------------------------视差值的计算-------------------------------------"""
    def getDifferentLevelDisparitySet(self,disparityset):
        difflevelset=np.array([])
        for percent in range(5,60,5):
            curTopAvgDisparity = self.getCurPercentMinDisparity(disparityset,percent)
            difflevelset = np.append(difflevelset,curTopAvgDisparity)
        return difflevelset



    def getCurPercentMinDisparity(self,disparityset,percent):
        disparitySet = np.array(disparityset[:,1],dtype=float)
        abs_disparity = np.abs(disparitySet)
        disparity_index = np.argsort(abs_disparity)
        sz = disparity_index.size
        topfiveMax = sz*percent/100.0
        topMaxDisparityindex = filter(lambda x:x<=topfiveMax,disparity_index)
        topFiveMinAvgDisparity = np.mean(np.array(disparitySet[topMaxDisparityindex]))
        return topFiveMinAvgDisparity
