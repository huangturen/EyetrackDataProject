#include "StdAfx.h"
#include "eyetrackFeatureFactory.h"
#include <iostream>

using namespace std;

eyetrackFeatureFactory::eyetrackFeatureFactory(const list<vector<float>>& eyetrackerdata,const std::vector<std::vector<int>> &fixationPoints,
	const std::map<int,GazePointType>& gazePointType,int blinkCount)
	:m_eyetrackerdata(eyetrackerdata),m_subjectAssessmentScore(0),m_fixationPoints(fixationPoints),m_gazePointType(gazePointType),m_blinkCount(blinkCount)
{
    cout << eyetrackerdata.size() << endl << gazePointType.size() << endl;
}

DataFeture eyetrackFeatureFactory::getEyetrackerDataFetures()
{
	m_datafeture.blinkCount = m_blinkCount;
	gazePointFeatureProcess(m_datafeture,m_fixationPoints);
	fixationFeatureProcess(m_datafeture,m_gazePointType);
	return m_datafeture;
}

eyetrackFeatureFactory::~eyetrackFeatureFactory(void)
{
}
void eyetrackFeatureFactory::setDisparityFeature(const DisparityFeature& dispfeature)
{
	m_disparityFeature = dispfeature;
}

void eyetrackFeatureFactory::setSubjectAssessmentScore(int score)
{
	m_subjectAssessmentScore = score;
}
void eyetrackFeatureFactory::gazePointFeatureProcess(DataFeture &datafeature, const vector<vector<int>>& fixationPoints)
{
	if (!fixationPoints.empty())
	{
		datafeature.fixationNum = int(fixationPoints.size());
		vector<vector<int>>::const_iterator iterpre = fixationPoints.begin();
		float maxSaccadeDistance = 0.0f;
		float saccadeDistanceSum = 0.0f;
		int saccadeCombinationCount = 0;
		int top_x = (*iterpre).at(0),top_y = (*iterpre).at(1), bottom_x = (*iterpre).at(0), bottom_y = (*iterpre).at(1);
		while (iterpre != fixationPoints.end()-1)
		{
			for (vector<vector<int>>::const_iterator iterpost = iterpre+1; iterpost != fixationPoints.end(); ++iterpost)
			{
				float curSaccadeDistance = getDistanceBetweenTwoFixations(*iterpre,*iterpost);
				saccadeDistanceSum += curSaccadeDistance;
				++saccadeCombinationCount;
				if (curSaccadeDistance>maxSaccadeDistance)
				{
					maxSaccadeDistance = curSaccadeDistance;
				}
			}
			
			++iterpre;
			if ((*iterpre).at(0)<top_x)
			{
				top_x = (*iterpre).at(0);
			}
			if ((*iterpre).at(1)<top_y)
			{
				top_y = (*iterpre).at(1);
			}
			if ((*iterpre).at(0)>bottom_x)
			{
				bottom_x = (*iterpre).at(0);
			}
			if ((*iterpre).at(1)>bottom_y)
			{
				bottom_y = (*iterpre).at(1);
			}
		}
		datafeature.maxSaccadeDistance = maxSaccadeDistance;
		datafeature.averageSaccadeDistance = saccadeDistanceSum/saccadeCombinationCount;
		datafeature.fixationAreaRatio = float(abs(bottom_x-top_x)*abs(bottom_y-top_y))/(1920*1080);
	}
}

void eyetrackFeatureFactory::fixationFeatureProcess(DataFeture &datafeature,const map<int,GazePointType>& gazepointtype)
{
	int index = 0;
	int maxLenFixationTime = 0;
	int curLen = 0;
	int fixationLenSum = 0;
	int fixaitonCount = 0;
	while(index < gazepointtype.size())
	{
		if (gazepointtype.at(index).pointType == "Fixation")
		{
			curLen++;
		} 
		else if(gazepointtype.at(index).pointType != gazepointtype.at(index-1).pointType)
		{
			if (maxLenFixationTime<curLen)
			{
				maxLenFixationTime = curLen;
			}
			fixationLenSum += curLen;
			curLen = 0;
			++fixaitonCount;
		}
		else
		{
			++index;
			continue;
		}
		++index;
	}
	datafeature.maxLenFixationTime = maxLenFixationTime;
	datafeature.averageFixationTime = fixationLenSum/fixaitonCount;
}
float eyetrackFeatureFactory::getDistanceBetweenTwoFixations(const std::vector<int>& p1,const std::vector<int>& p2)
{
	float r = 0;
	r = sqrt(pow(float(p1.at(0)-p2.at(0)),2)+pow(float(p1.at(1)-p2.at(1)),2));
	return r;
}

float eyetrackFeatureFactory::getDistanceBetweenTwoFixationsInDisparityAngular(const list<vector<float>>& eyetrackdata, const map<int,GazePointType>& gazepointType)
{
    vector<vector<float> > fixationRelated;
    int index = 0;
    float angularDistance = 0.0f;
    if (eyetrackdata.empty() || gazepointType.empty()) {
        cout << "The eyetrackdata or gazepointType must be calculated!some one is empty! " << endl;
        return angularDistance;
    }
    int curFixationLen = 0;
    list<vector<float>>::const_iterator iter = eyetrackdata.begin();
    vector<float> curRecord(iter->size(),0.0f);
    while (index < gazepointType.size()) {
        if (gazepointType.at(index).pointType == "Fixation") {
            ++curFixationLen;
            for (int i=0; i<curRecord.size(); ++i) {
                curRecord.at(i) += (*iter).at(i);
            }
        }
        else if(gazepointType.at(index).pointType != gazepointType.at(index-1).pointType)
        {
            for (int i=0; i<curRecord.size(); ++i) {
                curRecord.at(i) /= curFixationLen;
            }
            fixationRelated.push_back(curRecord);
            for (int i=0; i<curRecord.size(); ++i) {
                curRecord.at(i) = 0;
            }
            curFixationLen = 0;
        }
        else
        {
            ++index;
            ++iter;
            continue;
        }
        ++index;
        ++iter;
    }
    return angularDistance;
}


void eyetrackFeatureFactory::writeEyetrackerDataFeature(const string& outputFileName, featureFileType type)
{

	m_savefile = make_shared<ofstream>(outputFileName,ios_base::app);
	if (!m_savefile->is_open())
	{
		cout <<"Can't open the file!" << endl;
		return;
	}
	stringstream stream;
	if(m_subjectAssessmentScore>0)
	{
		if (type == common)
		{
			writeEyetrackerDataStreamCommon(stream);
		}
		else
		{
			writeEyetrackerDataStreamStandard(stream);
		}
		
	}
	else
	{
		m_savefile->close();
		return;
	}
	
	writeStreamToFile(m_savefile,stream);
	m_savefile->close();
}

void eyetrackFeatureFactory::writeEyetrackerDataStreamCommon(stringstream &stream)
{
	//subject score
	stream << m_subjectAssessmentScore << splitSymbols;

	//int count = 0;
	// eyetrackerdata feature
	
	stream  << m_datafeture.blinkCount << splitSymbols;
	stream  << m_datafeture.fixationNum << splitSymbols;
	stream  << m_datafeture.maxSaccadeDistance << splitSymbols;
	stream  << m_datafeture.averageSaccadeDistance << splitSymbols;
	stream  << m_datafeture.fixationAreaRatio << splitSymbols;
	stream  << m_datafeture.maxLenFixationTime << splitSymbols;
	stream  << m_datafeture.averageFixationTime << splitSymbols;

	//disparity feature
	stream  << m_disparityFeature.shiftValue << splitSymbols;
	stream << "\n";
}
void eyetrackFeatureFactory::writeEyetrackerDataStreamStandard(stringstream &stream)
{
	stream << m_subjectAssessmentScore << splitSymbols;
	int count = 0;
	
	stream << ++count << ":" << m_datafeture.blinkCount << splitSymbols;
	stream << ++count << ":" << m_datafeture.fixationNum << splitSymbols;
	stream << ++count << ":" << m_datafeture.maxSaccadeDistance << splitSymbols;
	stream << ++count << ":" << m_datafeture.averageSaccadeDistance << splitSymbols;
	stream << ++count << ":" << m_datafeture.fixationAreaRatio << splitSymbols;
	stream << ++count << ":" << m_datafeture.maxLenFixationTime << splitSymbols;
	stream << ++count << ":" << m_datafeture.averageFixationTime << splitSymbols;
	stream << ++count << ":" << m_disparityFeature.shiftValue << splitSymbols;
	stream << "\n";
}

void eyetrackFeatureFactory::writeStreamToFile(shared_ptr<ofstream> &fileSaveName, stringstream &stream)
{
	unsigned long size = stream.str().size();
	char* container = new char[size];
	stream.read(container,size);
	const char* p = container;
	fileSaveName->write(p,size);
	stream.flush();
}



