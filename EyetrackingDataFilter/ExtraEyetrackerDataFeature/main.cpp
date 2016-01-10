    //
//  main.cpp
//  ExtraEyetrackerDataFeature
//
//  Created by BaoyanMa on 15/11/3.
//  Copyright (c) 2015年 BaoyanMa. All rights reserved.
//

#include "stdafx.h"
#include "readeyetrackingexperimentdatafile.h"
#include "readsubjectqualityassementfile.h"
#include "eyetrackFeatureFactory.h"
#include <string>
#include <vector>
#include <iostream>
#include <memory>
#include <opencv2/contrib/contrib.hpp>
#include <exception>
#include <sstream>
using namespace std;


const string eyetrackdatafolder = "/Users/baoyanma/Documents/EyetrackerProject/Eyetrackdata/csv/task26/";
void splitstring(const string &line,const string &symbol,vector<string> & ret)
{
    if (line.empty())
    {
        return;
    }
    size_t last = 0;
    size_t index = line.find_first_of(symbol,last);
    while(index != string::npos)
    {
        ret.push_back(line.substr(last,index-last));
        last = index+1;
        index = line.find_first_of(symbol,last);
    }
    if (index-last>0)
    {
        ret.push_back(line.substr(last,index-last));
    }
}

int findScoreBasedOnUserNameVsImgName(const ReturnData& subjectAssessment, const string& imgname, const string& username)
{
    vector<SubjectAssessment> subjectAssessmentVector = subjectAssessment.subjectQualityAssessment.at(imgname);
    cout << imgname << endl;
    int subjectAssessmentScore = 0;
    for (vector<SubjectAssessment>::const_iterator iter = subjectAssessmentVector.begin(); iter != subjectAssessmentVector.end(); ++iter)
    {
        if ((*iter).user == username)
        {
            subjectAssessmentScore = (*iter).assessmentscore;
            break;
        }
    }
    return subjectAssessmentScore;
}

int main()
{
    cv::Directory dir;
    string filename = "/Users/baoyanma/Documents/EyetrackerProject/3dvqa_Shifted_Image_Test.csv";
    shared_ptr<readfile> m_reader(new readsubjectqualityassementfile(filename));
    ReturnData subjectAssessment = m_reader->getProcessedData();
    m_reader->writeDataToFile("/tmp/tst.csv");
    m_reader.reset();
    
    vector<string> files = dir.GetListFiles("/Users/baoyanma/Documents/EyetrackerProject/Eyetrackdata/csv/task26");
  
    for (vector<string>::size_type i = 0;i<files.size();++i)
    {
        string csvfilename = files.at(i);
        string::size_type sz = csvfilename.size();
        if (csvfilename.substr(sz-4,sz) != ".csv") {
            continue;
        }
        cout << csvfilename << endl;
        vector<string> result,disparity;
        splitstring(csvfilename.substr(0,csvfilename.size()-4),"_",result);
        string imgName = result.at(3)+".jpg";
        
        shared_ptr<readeyetrackingexperimentdatafile> m_eyetrackerdatareader(new readeyetrackingexperimentdatafile(eyetrackdatafolder+csvfilename,lefteye));
        ReturnData raweyetrackingdata = m_eyetrackerdatareader->getProcessedData();
//        int blinkCount = m_eyetrackerdatareader->getBlinkCount();
        
        m_eyetrackerdatareader->writeDataToFile("/tmp/"+csvfilename);
//        vector<vector<int>> fixationPoints = m_eyetrackerdatareader->getFixationPoints();
//        map<int,GazePointType> gazePointType = m_eyetrackerdatareader->getGazePointType();
//        int subjectAssessmentScore = 0;
//        
//        if(result.size() == 4)
//        {
//            subjectAssessmentScore = findScoreBasedOnUserNameVsImgName(subjectAssessment, imgName, result.at(2));
//            splitstring(result.at(3),"s",disparity);
//        }
//        else
//        {
//            imgName = result.at(4)+".jpg";
//            subjectAssessmentScore = findScoreBasedOnUserNameVsImgName(subjectAssessment,imgName , result.at(2)+"_"+result.at(3));
//            splitstring(result.at(4),"s",disparity);
//        }
//        
//        stringstream ss;
//        ss << disparity.at(1);
//        int shiftvalue;
//        ss >> shiftvalue;
//        eyetrackFeatureFactory eyetrackerDataFeatureProcessor(raweyetrackingdata.eyetrackerdata,fixationPoints,gazePointType,blinkCount);
//        DisparityFeature disparityfeature;
//        disparityfeature.shiftValue = shiftvalue;
//        eyetrackerDataFeatureProcessor.setDisparityFeature(disparityfeature);
//        eyetrackerDataFeatureProcessor.setSubjectAssessmentScore(subjectAssessmentScore);
//        DataFeture datafeature = eyetrackerDataFeatureProcessor.getEyetrackerDataFetures();
//        eyetrackerDataFeatureProcessor.writeEyetrackerDataFeature("/Users/baoyanma/Documents/EyetrackerProject/eyetrackerdatafeatureCommon",common);
//        eyetrackerDataFeatureProcessor.writeEyetrackerDataFeature("/Users/baoyanma/Documents/EyetrackerProject/eyetrackerdatafeatureStandard",standard);
    }
    
    system("pause");
    return 0;
}

