#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats.stats as statstool
from math import *
from sklearn import svm
from sklearn.metrics import mean_squared_error
import corestats


class FeatureTrainAndAnalysis(object):
    def __init__(self, filename):
        super(FeatureTrainAndAnalysis, self).__init__()
        self.fileName = filename
        self.datafortrain = np.array([])
        self.featureFileReader()

    def featureFileReader(self):
        # 数据读取
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

        datafortrain = np.array([])
        for item in numData:
            curitem = np.array(item, dtype=float)
            if datafortrain.size == 0:
                datafortrain = curitem
            else:
                datafortrain = np.vstack((datafortrain, curitem))
        self.datafortrain = datafortrain

    # def getRelationBetweenEyetrackFeatureAndSubjectScore(self,featureindex):
    # """验证各特征与主观评分之间的相关性"""
    #         if len(self.mosForEachImage) != len(self.meanFeatureValueForEachImage):
    #             raise ValueError('the number of mos and feature is not equal,please check it')
    #         else:
    #             feature_score_pairlist = []
    #             for key in self.mosForEachImage:
    #                 curList = [key,self.mosForEachImage[key],self.meanFeatureValueForEachImage[key][featureindex]]
    #                 feature_score_pairlist.append(curList)
    #             feature_score_pairlist = np.array(feature_score_pairlist)
    #             feature_score_pairarray = np.array(feature_score_pairlist[:,1:3], dtype=float)
    #             x = feature_score_pairarray[:,0]
    #             y = feature_score_pairarray[:,1]
    #             plcc,pval = statstool.pearsonr(x,y)
    #             srocc,pval = statstool.spearmanr(x,y)
    #             print "feature 1,%f,%f" %(plcc,srocc)
    #             return plcc


    def plccBetweenDifferentPercentOfDisparityAngular(self):
        w, h = self.datafortrain.shape
        ########################################################################
        #获取45%的结果
        ########################################################################
        percent = range(5, 60, 5)
        plccset = np.array([])
        maxplcc = 0
        for i in range(11):
            curPlcc, p = statstool.pearsonr(self.datafortrain[:, 0], self.datafortrain[:, i + 1])
            if maxplcc < curPlcc:
                maxplcc = curPlcc
            plccset = np.append(plccset, curPlcc)
        plt.xlabel(u'排序后视差角的前百分比（%）', fontsize=18)
        plt.ylabel(u'与MOS值的PLCC', fontsize=18)
        xmajorLocator = plt.MultipleLocator(5)
        ymajorLocator = plt.MultipleLocator(0.1)
        ax = plt.subplot(111)
        plt.plot(percent, plccset, 'g--^', label='PLCC', linewidth=1, mfc='r')
        ax.xaxis.set_major_locator(xmajorLocator)
        ax.yaxis.set_major_locator(ymajorLocator)
        plt.axhline(y=maxplcc, linestyle='-.', color='b', label=u'PLCC最大值', linewidth=3, animated=False, lod=True)
        plt.grid()
        plt.text(0, maxplcc, np.float16(maxplcc))
        plt.legend(loc='center right')
        # plt.title('Relationship between the percentage we choosed and mos')

        plt.show()


    #########################################################################
    #########################################################################





    #########################################################################
    #用来画模型修正前后的效果对比图
    #########################################################################
    def correlationBetweenAllFeaturesAndMOS(self):
        w, h = self.datafortrain.shape
        PLCC = []
        SROCC = []
        for i in range(h - 1):
            x = self.datafortrain[:, 0]
            y = self.datafortrain[:, i + 1]
            plcc, pval = statstool.pearsonr(x, y)
            srocc, pval = statstool.spearmanr(x, y)
            PLCC.append(plcc), SROCC.append(srocc)
        N = 15

        ind = np.arange(N)  # the x locations for the groups
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()

        # add some
        ax.set_xlabel(u'特征序号', fontsize=18)
        ax.set_ylabel(u'相关系数', fontsize=18)
        # ax.set_title('The Correlation between features and mos')

        rects1 = ax.bar(ind, tuple(PLCC), width, color='r')
        rects2 = ax.bar(ind + width, tuple(SROCC), width, color='b')
        ax.set_xticks(ind)
        ax.set_xticklabels(
            ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15'))
        ax.legend((rects1[0], rects2[0]), ('PLCC', 'SROCC'))
        plt.legend(loc='center right')
        plt.show()

    #########################################################################
    #########################################################################

    def lowgaininthebasicfeatures(self):
        w, h = self.datafortrain.shape
        kernels = ['linear', 'poly', 'rbf']
        LCC = [];
        SROCC = [];
        RMSE = [];
        baseplcc = 0;
        basesrocc = 0;
        basermse = 0
        for j in [0, 1, 2, 3, 4, 5, 7, 13, 14, 15]:
            print j
            LCC_rbf = [];
            SROCC_rbf = [];
            RMSE_rbf = []
            for i in range(2000):
                randlist = range(w)
                np.random.shuffle(randlist)

                trainindex = randlist[0:60]
                testindex = randlist[60:w]
                basecolumn = [6, 7, 8, 9, 10, 11, 12, 13, 15, 14]

                if j not in basecolumn:
                    basecolumn.append(j)
                if j == 0:
                    basecolumn.remove(j)
                train_feature = self.datafortrain[trainindex, :]
                train_feature = train_feature[:, basecolumn]
                train_label = self.datafortrain[trainindex, 0]

                test_feature = self.datafortrain[testindex, :]
                test_feature = test_feature[:, basecolumn]
                test_label = self.datafortrain[testindex, 0]

                '''============= train and predict by svr with rbf kernel ==============='''
                # rbf kernel
                clf = svm.SVR(kernel='rbf', C=1000, gamma=1 / 77)
                pred = clf.fit(train_feature, train_label).predict(test_feature)

                # rbf metrics
                srocc, p1 = statstool.spearmanr(pred, test_label)
                plcc, p2 = statstool.pearsonr(pred, test_label)
                rmse = sqrt(mean_squared_error(pred, test_label))
                LCC_rbf.append(plcc);
                SROCC_rbf.append(srocc);
                RMSE_rbf.append(rmse)

            sts_lcc = corestats.Stats(LCC_rbf)
            sts_srocc = corestats.Stats(SROCC_rbf)
            sts_rmse = corestats.Stats(RMSE_rbf)
            LCC.append(sts_lcc.avg());
            SROCC.append(sts_srocc.avg());
            RMSE.append(sts_rmse.avg())
            if j == 0:
                baseplcc = sts_lcc.avg();
                basesrocc = sts_srocc.avg();
                basermse = sts_rmse.avg()
            else:
                basecolumn.remove(j)
        #print "all_feature metrics %s:plcc:%f,srocc:%f,rmse:%f " %(kernels[2],sts_lcc.avg(),sts_srocc.avg(),sts_rmse.avg())

        # LCC_r = [(item-baseplcc)/baseplcc for item in LCC]
        # SROCC_r = [(item-basesrocc)/basesrocc for item in SROCC]
        # RMSE_r = [(item-basermse)/basermse for item in RMSE]

        N = 15

        ind = np.arange(N)  # the x locations for the groups
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()

        # add some
        ax.set_xlabel(u'特征序号', fontsize=18)
        ax.set_ylabel(u'相关系数和均方差', fontsize=18)
        # ax.set_title('The Correlation between features and mos')
        ax.set_xticks(ind)
        ax.set_xticklabels(('Orig', 'f1', 'f2', 'f3', 'f4', 'f5', 'f7', 'f13', 'f14', 'f15'))
        plt.axhline(y=baseplcc)
        plt.axhline(y=basesrocc)
        plt.axhline(y=basermse)
        plt.plot(LCC, 'b--*', label='PLCC')
        plt.plot(SROCC, 'g--+', label='SROCC')
        plt.plot(RMSE, 'r--o', label='RMSE')
        plt.legend(loc='center right')
        plt.show()

    def trainForModifiedFeaturesExceptLowGainFeatures(self):
        #此函数是用来检验去掉低增益的特征后模型的效果，因此在使用前务必将main（）函数中的fileName选为'./features_nomain.csv'（辅眼为准的滤波）
        w, h = self.datafortrain.shape
        kernels = ['linear', 'poly', 'rbf']
        for j in range(3):
            LCC_rbf = [];
            SROCC_rbf = [];
            RMSE_rbf = []
            for i in range(2000):
                randlist = range(w)
                np.random.shuffle(randlist)

                trainindex = randlist[0:60]
                testindex = randlist[60:w]
                basecolumn = [6, 7, 8, 9, 10, 11, 12, 13, 15, 14]

                # if j not in basecolumn:
                #     basecolumn.append(j)
                # if j==0:
                #     basecolumn.remove(j)
                train_feature = self.datafortrain[trainindex, :]
                train_feature = train_feature[:, basecolumn]
                train_label = self.datafortrain[trainindex, 0]

                test_feature = self.datafortrain[testindex, :]
                test_feature = test_feature[:, basecolumn]
                test_label = self.datafortrain[testindex, 0]

                '''============= train and predict by svr with rbf kernel ==============='''
                # rbf kernel
                clf = svm.SVR(kernel=kernels[j], C=1000, gamma=0.1)
                pred = clf.fit(train_feature, train_label).predict(test_feature)

                # rbf metrics
                srocc, p1 = statstool.spearmanr(pred, test_label)
                plcc, p2 = statstool.pearsonr(pred, test_label)
                rmse = sqrt(mean_squared_error(pred, test_label))
                LCC_rbf.append(plcc);
                SROCC_rbf.append(srocc);
                RMSE_rbf.append(rmse)

            sts_lcc = corestats.Stats(LCC_rbf)
            sts_srocc = corestats.Stats(SROCC_rbf)
            sts_rmse = corestats.Stats(RMSE_rbf)
            print "all_feature metrics %s:plcc:%f,srocc:%f,rmse:%f " % (
                kernels[j], sts_lcc.avg(), sts_srocc.avg(), sts_rmse.avg())

    def trainForAllFeatures(self):
        #此函数是用来检验去掉低增益的特征后模型的效果，因此在使用前务必将main（）函数中的fileName选为'./features_nomain.csv'（辅眼为准的滤波）
        w, h = self.datafortrain.shape
        kernels = ['linear', 'poly', 'rbf']
        for j in range(3):
            LCC_rbf = [];
            SROCC_rbf = [];
            RMSE_rbf = []
            for i in range(2000):
                print u"第%d次训练" % i
                randlist = range(w)
                np.random.shuffle(randlist)

                trainindex = randlist[0:60]
                testindex = randlist[60:w]

                # if j not in basecolumn:
                #     basecolumn.append(j)
                # if j==0:
                #     basecolumn.remove(j)
                train_feature = self.datafortrain[trainindex, :]
                train_feature = train_feature[:, 1:]
                train_label = self.datafortrain[trainindex, 0]

                test_feature = self.datafortrain[testindex, :]
                test_feature = test_feature[:, 1:]
                test_label = self.datafortrain[testindex, 0]

                '''============= train and predict by svr with rbf kernel ==============='''
                # rbf kernel
                clf = svm.SVR(kernel=kernels[j], C=1000, gamma=0.1)
                pred = clf.fit(train_feature, train_label).predict(test_feature)

                # rbf metrics
                srocc, p1 = statstool.spearmanr(pred, test_label)
                plcc, p2 = statstool.pearsonr(pred, test_label)
                rmse = sqrt(mean_squared_error(pred, test_label))
                LCC_rbf.append(plcc);
                SROCC_rbf.append(srocc);
                RMSE_rbf.append(rmse)

            sts_lcc = corestats.Stats(LCC_rbf)
            sts_srocc = corestats.Stats(SROCC_rbf)
            sts_rmse = corestats.Stats(RMSE_rbf)
            print "all_feature metrics %s:plcc:%f,srocc:%f,rmse:%f " % (
                kernels[j], sts_lcc.avg(), sts_srocc.avg(), sts_rmse.avg())
    @staticmethod
    def drawComparisionResultBeforeAndAfterModified():
        N = 2
        ind = np.arange(N)  # the x locations for the groups
        width = 0.25  # the width of the bars
        # 这里的数据都是真实测量值，方便起见人工敲上去的，可以通过函数trainForModifiedFeaturesExceptLowGainFeatures来验证
        PLCC = [0.731489, 0.745379]
        SROCC = [0.668282, 0.673779]
        RMSE = [0.40558, 0.387686]
        fig, ax = plt.subplots()
        a = tuple(PLCC)
        rects1 = ax.bar(ind, tuple(PLCC), width, color='r')
        rects2 = ax.bar(ind + width, tuple(SROCC), width, color='b')
        rects3 = ax.bar(ind + 2 * width, tuple(RMSE), width, color='g')
        # add some
        ax.set_xlabel(u'PLCC,SROCC,RMSE对比', fontsize=18)
        ax.set_ylabel(u'相关系数与均方差', fontsize=18)
        # ax.set_title('The performance of modified model')
        ax.set_xticks(ind + width)
        ax.set_xticklabels((u'修正前', u'修正后'), fontsize=16)

        ax.legend((rects1[0], rects2[0], rects3[0]), ('PLCC', 'SROCC', 'RMSE'))

        plt.axhline(y=PLCC[0], linestyle='--', color='black')
        plt.axhline(y=SROCC[0], linestyle='--', color='black')
        plt.axhline(y=RMSE[0], linestyle='--', color='black')
        plt.show()

    #########################################################################
    #########################################################################

def main():
    print 'here'
    filterBase = ['./Features/features_left.csv', './Features/features_right.csv', './Features/features_main.csv',
                  './Features/features_nomain.csv', './Features/features_multilevel.csv', ]

    if sys.argv.__len__() < 2:
        exit_with_help()

    if sys.argv[1] == '-c' and sys.argv[2] == '--dm' and sys.argv[3] == 'multilevel':
        fileName = filterBase[3]
        featuresProcessor = FeatureTrainAndAnalysis(fileName)
        featuresProcessor.correlationBetweenAllFeaturesAndMOS()
    elif sys.argv[1] == '-c' and sys.argv[2] == '--g':
        if sys.argv[3] == 'left':
            fileName = filterBase[0]
        elif sys.argv[3] == 'right':
            fileName = filterBase[1]
        elif sys.argv[3] == 'main':
            fileName = filterBase[2]
        elif sys.argv[3] == 'nomain':
            fileName = filterBase[3]
        else:
            print "features file is not existed,you should choose one from [left,right,main,nomain]"
        fileName = filterBase[3]
        featuresProcessor = FeatureTrainAndAnalysis(fileName)
        featuresProcessor.lowgaininthebasicfeatures()
    elif sys.argv[1] == '-t' and sys.argv[2] == '--fm':
        print 'here'
        if sys.argv[3] == 'left':
            fileName = filterBase[0]
        elif sys.argv[3] == 'right':
            fileName = filterBase[1]
        elif sys.argv[3] == 'main':
            fileName = filterBase[2]
        elif sys.argv[3] == 'nomain':
            fileName = filterBase[3]
        else:
            print "features file is not existed,you should choose one from [left,right,main,nomain]"
        featuresProcessor = FeatureTrainAndAnalysis(fileName)
        featuresProcessor.trainForAllFeatures()
    elif sys.argv[1] == '-mt':
        if sys.argv[2] == 'left':
            fileName = filterBase[0]
        elif sys.argv[2] == 'right':
            fileName = filterBase[1]
        elif sys.argv[2] == 'main':
            fileName = filterBase[2]
        elif sys.argv[2] == 'nomain':
            fileName = filterBase[3]
        else:
            print "features file is not existed,you should choose one from [left,right,main,nomain]"
        featuresProcessor = FeatureTrainAndAnalysis(fileName)
        featuresProcessor.trainForModifiedFeaturesExceptLowGainFeatures()
    elif sys.argv[1] == '-cm':
        FeatureTrainAndAnalysis.drawComparisionResultBeforeAndAfterModified()
    else:
        exit_with_help()

if __name__ == "__main__":

    def exit_with_help():
        print ("""\
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
 """)

        sys.exit(1)
    main()