#!/usr/bin/python
# -*- coding: utf-8 -*-
# "This programe is used to process eyetracker data"
#Author : Mabaoyan
#Time: 2015/11/04

import os,sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series
from math import sqrt
# import scipy.stats.stats import stat


"""----------------------------------------这个类是为了处理主观评价的分数--------------------------------------------"""


class SubjectAssessmentData(object):
    """docstring for SubjectAssessmentData"""

    def __init__(self, filename):
        super(SubjectAssessmentData, self).__init__()
        self.fileName = filename
        self.subjectAssessmentData = np.array([])
        self.title = np.array([])
        self.readSubjectAssessmentFile()


    """----------------------------------------------读取主观评价文件------------------------------------------------"""

    def readSubjectAssessmentFile(self):
        numData = [];
        data = open(self.fileName)
        s = data.readlines()
        index = 0
        for line in s:
            line = line.split(",");
            if index is 0:
                index += 1
                line[-1] = line[-1].replace('\r\n', '')
                self.title = np.array(line)
                continue
            line[1:25] = map(float, line[1:25])
            numData.append(line)
        self.subjectAssessmentData = np.array(numData)

    # for item in self.subjectAssessmentData:
    # 	print item
    """-----------------------------------------------获取已处理的主观评分数据-----------------------------------------"""
    def getSubjectAssessmentData(self):
        return self.subjectAssessmentData


    """-----------------------------------------------获取参与被试的姓名-----------------------------------------"""
    def getParticipantNameList(self):
        return self.title


    """-------------------------------------------------验证主观评价--------------------------------------------------"""

    def validSubjectAssessment(self, subjectassessment, title):
        assessment = np.array(subjectassessment[:, 1:25], dtype=float)
        assessment_avg = np.mean(assessment, axis=1)
        assessment_std = np.std(assessment, axis=1)
        confidenceIntervalUpper = assessment_avg + assessment_std
        confidenceIntervalLower = assessment_avg - assessment_std

        exceptionCountUpper = np.zeros((1, 24))
        exceptionCountLower = np.zeros((1, 24))
        index = 0
        for item in assessment:
            exceptionCountLower += item < confidenceIntervalLower[index]
            exceptionCountUpper += item > confidenceIntervalUpper[index]
            index += 1

        m, n = assessment.shape
        exceptionDegree = (exceptionCountUpper + exceptionCountLower) / (m * n)
        exceptionDegreeRelative = np.abs(exceptionCountUpper - exceptionCountLower) / (
            exceptionCountUpper + exceptionCountLower)

        exceptionPersonCount = 0
        exceptionThroldAb = 0.05
        exceptionThroldRl = 0.3

        exceptionDegreeHandle = exceptionDegree[0]
        exceptionDegreeRelativeHandle = exceptionDegreeRelative[0]

        for i in range(24):
            isException = exceptionDegreeHandle[i] > exceptionThroldAb and exceptionDegreeRelativeHandle[
                                                                               i] < exceptionThroldRl
            exceptionPersonCount += isException

        ablevel = [0.05 for i in range(24)]
        rllevel = [0.3 for i in range(24)]
        plt.plot(ablevel, 'bo', exceptionDegreeHandle, 'r-')
        plt.plot(rllevel, 'bo', exceptionDegreeRelativeHandle, 'r-')
        # plt.savefig('./validResult.jpg')
        plt.show()

    """-------------------------------------------------计算每个被试对每个视差下11副图像的均值--------------------------------------------------"""
    def performanceBasicOnDisparity(self):

        """将主观评分按照不同视差进行分类，共分为7类，对应的视差值分别为0，11，-11，22，-22，34，-34"""
        classficDic = {}
        index = 0
        for item in self.subjectAssessmentData:
            disparity = int(item[0][:-4].split('s')[1])
            assert isinstance(disparity, object)

            if disparity not in classficDic:
                classficDic[disparity] = set([index])
            else:
                classficDic[disparity].add(index)
            index += 1
        basecolors = ['red','green','indigo','blue','black','cyan','magenta']
        baselines = ['-','--']

        """分视差作图，横轴范围0：23，分别对应24个被试，纵轴范围为1：5，表示针对同一视差"""
        i=0
        sorted(classficDic.items(),key = lambda d:d[0])
        keylist = [34,22,11,0,-11,-22,-34]
        fig,ax = plt.subplots()
        for key in keylist:
            subscoreset = np.array(self.subjectAssessmentData[list(classficDic[key]), 1:],dtype = float)
            mos_eachdisparity = np.mean(subscoreset,axis = 0)
            if i>3:
                baseline = '--'
            else:
                baseline = '-'
            plt.plot(mos_eachdisparity,color = basecolors[i],label = str(key),linestyle = baseline)
            i += 1
        ind = range(24)
        ax.set_xticks(ind)
        ax.set_xticklabels(ind)
        plt.legend()
        # plt.title('Performance of subject assessment under different disparity')
        plt.xlabel(u"被试者序号",fontsize = 16)
        plt.ylabel(u"不同视差调整分组的MOS值",fontsize = 16)
        # plt.savefig('./Images/subjectScoreAnalysis/mos_perdisparity1.jpg')
        plt.show()


        """-------------------------------------------------计算每个被试对每个视差下11副图像的均值--------------------------------------------------"""
    def performanceBasicOnImage(self):
        """将主观评分按照不同视差进行分类，共分为7类，对应的视差值分别为0，11，-11，22，-22，34，-34"""
        classficDic = {}
        index = 0
        for item in self.subjectAssessmentData:
            imgName = int(item[0][:-4].split('s')[0])
            assert isinstance(imgName, object)

            if imgName not in classficDic:
                classficDic[imgName] = set([index])
            else:
                classficDic[imgName].add(index)
            index += 1
        basecolors = ['red','green','indigo','blue','black','cyan','magenta']
        baselines = ['-','--']

        """分视差作图，横轴范围0：23，分别对应24个被试，纵轴范围为1：5，表示针对同一视差"""
        i=0
        for key in classficDic:
            subscoreset = np.array(self.subjectAssessmentData[list(classficDic[key]), 1:],dtype = float)
            mos_eachdisparity = np.mean(subscoreset,axis = 0)
            plt.plot(mos_eachdisparity,color = basecolors[i%7],label = str(key),linestyle = baselines[i%2])
            i += 1
        plt.legend()
        plt.title('Performance of subject assessment under different disparity')
        plt.xlabel('number of Subjects/unit(1)')
        plt.ylabel('mos of each disparity')
        # plt.savefig('./Images/subjectScoreAnalysis/mos_image.jpg')
        plt.show()

    def getAvgMosForEachImage(self):
        """获得每幅图想得平均评分"""
        classicDic = {}
        index = 0
        for item in self.subjectAssessmentData:
            imgName = item[0]
            tmp = np.array(item[1:],dtype=float)
            classicDic[imgName] = np.mean(tmp)
        return classicDic

    def getStdForEachImage(self):
        classicDic = {}
        index = 0
        for item in self.subjectAssessmentData:
            imgName = item[0]
            tmp = np.array(item[1:],dtype=float)
            classicDic[imgName] = np.std(tmp)
        return classicDic

    def calkurtcoefficient(self,scoreforcurrentimage):
        scores = scoreforcurrentimage[1:]
        scores = Series(scores,dtype=float)
        kurtcoef = scores.kurt()+3
        return kurtcoef

    def getKurtosisCoefSet(self):
        print self.getKurtosisCoef()

    def getKurtosisCoef(self):
        kurtSet={}
        for item in self.subjectAssessmentData:
            kurtSet[item[0]]= self.calkurtcoefficient(item)
        return kurtSet

    def drawKurtCurve(self):
        kurtset = self.getKurtosisCoef()
        plt.plot(kurtset.values(),'r-o',label=u"kurtosis 系数",linewidth=1)
        plt.xlabel(u"立体图像序号",fontsize=18)
        plt.ylabel(u"kurtosis 系数",fontsize=18)
        # plt.title('Kurtosis coeficient of subject assessment scores for each image')
        plt.axhline(y=2,linestyle='-.',color='b',label='kurtosis=2',linewidth=3)
        plt.axhline(y=4,linestyle='-.',color='g',label='kurtosis=4',linewidth=3)
        plt.legend()
        # plt.savefig('./Images/subjectScoreAnalysis/kurtosis.jpg')
        plt.show()

    def getBoundMosForEachImage(self):
        mos_bound = {}
        avg_mos = self.getAvgMosForEachImage()
        std_mos = self.getStdForEachImage()
        kurtcoef_mos = self.getKurtosisCoef()
        for item in avg_mos:
            imgName = item
            if kurtcoef_mos[imgName]>=2 and kurtcoef_mos[imgName]<=4:
                mos_bound[imgName]=[avg_mos[imgName]-2*std_mos[imgName],avg_mos[imgName]+2*std_mos[imgName]]
            else:
                mos_bound[imgName]=[avg_mos[imgName]-sqrt(20)*std_mos[imgName],avg_mos[imgName]+sqrt(20)*std_mos[imgName]]
        return mos_bound

    def getExceptionCountUnder95Confident(self):
        avg_mos = self.getAvgMosForEachImage()
        std_mos = self.getStdForEachImage()
        fig, axes = plt.subplots()
        axes.errorbar(range(77), avg_mos.values(), yerr=[1.96*item/sqrt(24) for item in std_mos.values()], ecolor='b',fmt="ro",linestyle = ':', label=u"95%置信区间")
        # axes.set_xticks(range(77))
        # axes.set_xticklabels(tuple(avg_mos.keys()),rotation=80)
        plt.xlabel(u"立体图像序号",fontsize = 18)
        plt.ylabel(u'MOS值',fontsize = 18)
        axes.legend()
        # plt.savefig('./Images/subjectScoreAnalysis/mosandconfidence.jpg')
        plt.show()

    def drawMosDistributionForEachPerson(self):
        mos_bound = self.getBoundMosForEachImage()
        for i in range(self.title.size-1):
            plt.plot(np.array(mos_bound.values())[:,0],'g-^',label = u'异常值下界')
            plt.plot(np.array(mos_bound.values())[:,1],'b-v',label = u'异常值上界')
            plt.plot(self.subjectAssessmentData[:,i+1],'r--o',label = u'%s的评分' %(self.title[i+1]))
            plt.xlabel(u'立体图像序号',fontsize=18)
            plt.ylabel(u'主观评分',fontsize=18)
            # plt.title('The subject assessment score distribution of %s' %(self.title[i+1]))
            plt.legend()
            # plt.savefig('./Images/subjectScoreAnalysis/validwithmethod1/validresultfor%s' %(self.title[i+1]))
            plt.show()

    def getBiasForEachPerson(self):
        mos_bound = self.getBoundMosForEachImage()
        exceptionIndex = {}

        for i in range(self.title.size-1):
            curUpperCount = 0
            curLowerCount = 0
            for j in range(77):
                x = float(self.subjectAssessmentData[j,i+1])
                y = mos_bound[self.subjectAssessmentData[j,0]][1]
                if x>=y:
                    curUpperCount = curUpperCount+1
                elif self.subjectAssessmentData[j,i+1]<= mos_bound[self.subjectAssessmentData[j,0]][0]:
                    curLowerCount = curLowerCount+1
            if curLowerCount == 0:
                curLowerCount = 0.1
            exceptionIndex[self.title[i+1]]=[curUpperCount,curLowerCount]
        abexception = {}
        relativeexception={}
        upperexception = {}
        lowerexception = {}
        for key in exceptionIndex:
            upperexception[key]=exceptionIndex[key][0]
            lowerexception[key]=exceptionIndex[key][1]
            exceptionsum = float(np.sum(np.array(exceptionIndex[key])))
            abexception[key] = exceptionsum/77.0
            if exceptionsum == 0:
                relativeexception[key]=0
            else:
                relativeexception[key]= abs(exceptionIndex[key][0]-exceptionIndex[key][1])/exceptionsum
        return (abexception,relativeexception,upperexception,lowerexception)

    def drawBiasToOneSide(self):
        biasToOneSide = self.getBiasForEachPerson()[2:] #if the range is[0:2],then draw the abs and relative bias;if range is [2:],then draw local bias
        N = 24
        ind = np.arange(N)  # the x locations for the groups
        width = 0.3      # the width of the bars
        PLCC=[0.731489,0.745379]
        SROCC=[0.668282,0.673779]
        RMSE=[0.40558,0.387686]
        fig, ax = plt.subplots()
        a = map(float,biasToOneSide[0].values())
        b = biasToOneSide[1].values()
        rects1 = ax.bar(ind, tuple(a), width, color='r')
        rects2 = ax.bar(ind+width, tuple(b), width, color='b')
        # rects3 = ax.bar(ind+2*width, tuple(RMSE), width, color='g')
        # add some
        # ax.set_xlabel('Subjects\' Nickname of our expriment',fontsize=18)
        # ax.set_ylabel('Out of bounds Count',fontsize=18)
        ax.set_xlabel(u'实验中被试者昵称',fontsize=18)
        ax.set_ylabel(u'评分中偏差个数',fontsize=18)
        # ax.set_title('The performance of modified model')
        ax.set_xticks(ind+0.5*width)
        ax.set_xticklabels(('609lab', 'zhd_1225', 'zhili1', 'sunmin', 'dsfgjig', 'joe w', 'chen', 'Frank', 'wizard', 'fjz1124',\
                'zjzz123', 'Knight', 'cjlumei', 'leery24', 'shenshihui', 'pesuidemeng', 'cxqjiafeimao', '123123', '3dvqa', 'wzxsjdt',\
                'mrfranken', 'whk990', 'Jenna', 'suchen'),rotation=80)

        # ax.legend( (rects1[0], rects2[0]), ('Out of upper bounds', 'Out of lower bounds') )
        ax.legend( (rects1[0], rects2[0]), (u'绝对偏差', u'相对偏差') )
        # plt.ylim((0,1.2))
        plt.show()

    def drawAbsandRelativeBiasRatios(self):
        biasToOneSide = self.getBiasForEachPerson()[:2] #if the range is[0:2],then draw the abs and relative bias;if range is [2:],then draw local bias
        N = 24
        ind = np.arange(N)  # the x locations for the groups
        width = 0.3      # the width of the bars
        PLCC=[0.731489,0.745379]
        SROCC=[0.668282,0.673779]
        RMSE=[0.40558,0.387686]
        fig, ax = plt.subplots()
        a = map(float,biasToOneSide[0].values())
        b = biasToOneSide[1].values()
        rects1 = ax.bar(ind, tuple(a), width, color='r')
        rects2 = ax.bar(ind+width, tuple(b), width, color='b')
        # rects3 = ax.bar(ind+2*width, tuple(RMSE), width, color='g')
        # add some
        # ax.set_xlabel('Subjects\' Nickname of our expriment',fontsize=18)
        # ax.set_ylabel('Out of bounds Count',fontsize=18)
        ax.set_xlabel(u'实验中被试者昵称',fontsize=18)
        ax.set_ylabel(u'偏差比',fontsize=18)
        # ax.set_title('The performance of modified model')
        ax.set_xticks(ind+0.5*width)
        ax.set_xticklabels(('609lab', 'zhd_1225', 'zhili1', 'sunmin', 'dsfgjig', 'joe w', 'chen', 'Frank', 'wizard', 'fjz1124',\
                'zjzz123', 'Knight', 'cjlumei', 'leery24', 'shenshihui', 'pesuidemeng', 'cxqjiafeimao', '123123', '3dvqa', 'wzxsjdt',\
                'mrfranken', 'whk990', 'Jenna', 'suchen'),rotation=80)

        # ax.legend( (rects1[0], rects2[0]), ('Out of upper bounds', 'Out of lower bounds') )
        ax.legend( (rects1[0], rects2[0]), (u'绝对偏差比', u'相对偏差比') )
        # plt.ylim((0,1.2))
        plt.show()




def main():
    if sys.argv.__len__() < 3:
        exit_with_help()
    print sys.argv
    subjectfilename = './ss_subjectAssessmentScore_aferProcessed.csv'
    subjectprocessor = SubjectAssessmentData(subjectfilename)
    if sys.argv[1] == '-p' and sys.argv[2] == '--Disparity':
        subjectprocessor.performanceBasicOnDisparity()
    elif sys.argv[1] == '-p' and sys.argv[2] == '--Image':
        subjectprocessor.performanceBasicOnImage()
    elif sys.argv[1] == '-k' and sys.argv[2] == '--s':
        subjectprocessor.getKurtosisCoefSet()
    elif sys.argv[1] == '-k' and sys.argv[2] == '--f':
        subjectprocessor.drawKurtCurve()
    elif sys.argv[1] == '-c' and sys.argv[2] == '--f':
        subjectprocessor.getExceptionCountUnder95Confident()
    elif sys.argv[1] == '-m' and sys.argv[2] == '--f':
        subjectprocessor.drawMosDistributionForEachPerson()
    elif sys.argv[1] == '-b' and sys.argv[2] == '--a':
        subjectprocessor.drawAbsandRelativeBiasRatios()
    elif sys.argv[1] == '-b' and sys.argv[2] == '--r':
        subjectprocessor.drawBiasToOneSide()
    else:
        exit_with_help()

if __name__ == '__main__':
    def exit_with_help():


        print ("""\
 Usage:SubjectAssessmentData.py options command

 options-command :
 -p get the performance of subject score
     --Disparity  based on the shift disparity value
     --Image   based on the image
 -k get the kurtosis value
     --s get kurtosis set and print
     --f show kurtosis result as a fig
 -c get 95% confident interval
     --f show fig of confident interval
 -m get distribution of MOS
     --f show mos distribution as a fig
 -b get bias of subject scores
     --a show absolute bias
     --r show relative bias
 """)
        sys.exit(1)
    main()