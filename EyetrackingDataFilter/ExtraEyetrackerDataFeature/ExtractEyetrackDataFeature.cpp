// ExtractEyetrackDataFeature.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "readeyetrackingexperimentdatafile.h"
#include "readsubjectqualityassementfile.h"
#include "eyetrackFeatureFactory.h"
#include <string>
#include <vector>
#include <iostream>
#include <memory>
#include <contrib/contrib.hpp>
#include <io.h>
#include <hash_map>
#include <videostab\stabilizer.hpp>
#include <exception>
#include <sstream>
using namespace std;

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

int _tmain(int argc, _TCHAR* argv[])
{
	cv::Directory dir;
	string filename = "C:\\Users\\biye\\Documents\\MATLAB\\3dvqa_Shifted_Image_Test.csv";
	shared_ptr<readfile> m_reader(new readsubjectqualityassementfile(filename));
	ReturnData subjectAssessment = m_reader->getProcessedData();
	m_reader.reset();

	vector<string> files = dir.GetListFiles("C:\\Users\\biye\\Documents\\MATLAB\\Eyetrackdata\\csv\\task26\\","*csv",true);

	for (vector<string>::size_type i = 0;i<files.size();++i)
	{
		string csvfilename = files.at(i);
		vector<string> tmp,result,disparity;
		splitstring(csvfilename.substr(0,csvfilename.size()-4),"\/",tmp);
		splitstring(tmp.at(1),"_",result);
		string imgName = result.at(3)+".jpg";

		shared_ptr<readeyetrackingexperimentdatafile> m_eyetrackerdatareader(new readeyetrackingexperimentdatafile(csvfilename,lefteye));
		ReturnData raweyetrackingdata = m_eyetrackerdatareader->getProcessedData();
		int blinkCount = m_eyetrackerdatareader->getBlinkCount();
		vector<vector<int>> fixationPoints = m_eyetrackerdatareader->getFixationPoints();
		map<int,GazePointType> gazePointType = m_eyetrackerdatareader->getGazePointType();
		int subjectAssessmentScore = 0;
		
		if(result.size() == 4)
		{
			subjectAssessmentScore = findScoreBasedOnUserNameVsImgName(subjectAssessment, imgName, result.at(2));
			splitstring(result.at(3),"s",disparity);
		}
		else
		{
			imgName = result.at(4)+".jpg";
			subjectAssessmentScore = findScoreBasedOnUserNameVsImgName(subjectAssessment,imgName , result.at(2)+"_"+result.at(3));
			splitstring(result.at(4),"s",disparity);
		}
		
		stringstream ss;
		ss << disparity.at(1);
		int shiftvalue;
		ss >> shiftvalue;
		eyetrackFeatureFactory eyetrackerDataFeatureProcessor(raweyetrackingdata.eyetrackerdata,fixationPoints,gazePointType,blinkCount);
		DisparityFeature disparityfeature;
		disparityfeature.shiftValue = shiftvalue;
		eyetrackerDataFeatureProcessor.setDisparityFeature(disparityfeature);
		eyetrackerDataFeatureProcessor.setSubjectAssessmentScore(subjectAssessmentScore);
		DataFeture datafeature = eyetrackerDataFeatureProcessor.getEyetrackerDataFetures();
		eyetrackerDataFeatureProcessor.writeEyetrackerDataFeature("eyetrackerdatafeatureCommon",common);
		eyetrackerDataFeatureProcessor.writeEyetrackerDataFeature("eyetrackerdatafeatureStandard",standard);
	}
	
	system("pause");
	return 0;
}

