// stdafx.h : 标准系统包含文件的包含文件，
// 或是经常使用但不常更改的
// 特定于项目的包含文件
//

#pragma once

#include <string>
#include <stdio.h>
#include <vector>
#include <map>
#include <list>
#include <math.h>
struct eyetrackingdata
{
	std::string time;
	int timestamp;
	int leftgazepointx;
};
struct GazePointType{
	std::string pointType;
	int point_x;
	int point_y;
	GazePointType(std::string type,int x=-1,int y=-1):pointType(type),point_x(x),point_y(y){}
};

struct SubjectAssessment{
	std::string user;
	float assessmentscore;
	SubjectAssessment(){}
	SubjectAssessment(std::string &username,float score = -1.0):user(username),assessmentscore(score){}
};

struct ReturnData{
	std::list<std::vector<float>> eyetrackerdata;
	std::map<std::string,std::vector<SubjectAssessment>> subjectQualityAssessment;
};
struct DataFeture{
	int blinkCount;
	int fixationNum;
	float fixationAreaRatio;
	float maxLenFixationTime;
	float averageFixationTime;
	float maxSaccadeDistance;
	float averageSaccadeDistance;
	DataFeture():blinkCount(0),fixationNum(0),fixationAreaRatio(0.0f),maxLenFixationTime(0.0f),averageFixationTime(0.0f),maxSaccadeDistance(0.0f),averageSaccadeDistance(0.0f){}
};
struct DisparityFeature{
	int shiftValue;
	int maxDisparity;
	int minDisparity;
	float averageDisparity;
	DisparityFeature():shiftValue(0),maxDisparity(0),minDisparity(0),averageDisparity(0.0f){}
};
enum eyeOption{lefteye=1,righteye,doubleeyes};
enum featureFileType{standard = 0,common};
typedef std::pair<std::string,float> PAIR;
// TODO: 在此处引用程序需要的其他头文件
