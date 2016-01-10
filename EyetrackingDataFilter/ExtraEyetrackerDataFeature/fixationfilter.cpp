#include "StdAfx.h"
#include "fixationfilter.h"
#include <iostream>
#include <utility>
#include <cmath>
using namespace std;

const double epsle = 1.0e-6;
const int windowWidth = 4;
const int imgWidth = 1920;
const int imgHeight = 1080;
const float peakThreshold = 40.0;

fixationfilter::fixationfilter(const list<vector<float>> &eyetrackdatacontainer,eyeOption eye)
	:m_eyetrackDataContainer(eyetrackdatacontainer),m_eye(eye),x_cordinary(-1),y_cordinary(-1)
{
}

fixationfilter::~fixationfilter(void)
{
	m_peakIndex.clear();
	m_peakVector.clear();
	m_fixationPoints.clear();
	m_gazePointType.clear();
}

std::vector<std::vector<int>> fixationfilter::getFixationPoints()
{
	if (m_peakIndex.empty())
	{
		getPeakIndex(m_eyetrackDataContainer,m_peakVector,m_peakIndex,m_eye);
	}
	else if (m_fixationPoints.empty())
	{
		getFixationPoints(m_eyetrackDataContainer,m_fixationPoints,m_peakIndex,m_eye);
	}
	return m_fixationPoints;
}
std::map<int,GazePointType> fixationfilter::getGazePointType()
{
	if (m_peakIndex.empty())
	{
		getPeakIndex(m_eyetrackDataContainer,m_peakVector,m_peakIndex,m_eye);
	}
	if (m_fixationPoints.empty())
	{
		getFixationPoints(m_eyetrackDataContainer,m_fixationPoints,m_peakIndex,m_eye);
	}
	getGazePointType(m_eyetrackDataContainer,m_fixationPoints,m_peakIndex,m_gazePointType);
	return m_gazePointType;
}
std::vector<float> fixationfilter::getPeakVector()
{
	if (m_peakVector.empty())
	{
		getPeakIndex(m_eyetrackDataContainer,m_peakVector,m_peakIndex,m_eye);
	}
	return m_peakVector;
}
std::vector<int> fixationfilter::getPeakIndex()
{
	if (m_peakIndex.empty())
	{
		getPeakIndex(m_eyetrackDataContainer,m_peakVector,m_peakIndex,m_eye);
	}
	return m_peakIndex;
}

void fixationfilter::getPeakIndex(const list<vector<float>> &pureEyetrackdataSet,vector<float> &peakVector, vector<int> &peakIndex,eyeOption eye)
{
	if (pureEyetrackdataSet.size()<11)
	{
		return;
	}
	peakIndex.clear();
	peakVector.clear();
	size_t start = 0;
	while(start++ < pureEyetrackdataSet.size())
	{
		peakVector.push_back(0);
	}
	vector<float> distancevector = calculateAdjacentWindowDistance(pureEyetrackdataSet,windowWidth,eye);
	for (vector<int>::size_type i=1;i<distancevector.size()-1;i++)
	{
		if (distancevector.at(i)>distancevector.at(i-1) && distancevector.at(i)>distancevector.at(i+1))
		{
			peakVector.at(i+windowWidth)=distancevector.at(i);
		}
	}

	for (int i=windowWidth;i<peakVector.size()-windowWidth;i++)
	{
		if (peakVector.at(i) > epsle)
		{
			for (int k=i-windowWidth;k<i;k++)
			{
				if (peakVector.at(i)>peakVector.at(k))
				{
					peakVector.at(k)=0;
				}
			}
			for (int k=i+1;k<=i+windowWidth;k++)
			{
				if (peakVector.at(i)>peakVector.at(k))
				{
					peakVector.at(k)=0;
				}
			}
		}
	}
	//peakIndex.push_back(0);/*方便后面处理*/
	for (unsigned int k = 0; k<peakVector.size(); k++)
	{
		if (peakVector.at(k)>peakThreshold)
		{
			peakIndex.push_back(k);
		}
	}

	int index = -1;
	int shortestDistance = INT_MIN;
	const int distance = 10;//we expect the length between two peak is bigger than 10
	while(shortestDistance<distance)
	{
		shortestDistance = INT_MAX;
		for (unsigned int k = 1; k<peakIndex.size(); k++)
		{
			int currentDistance = peakIndex.at(k)-peakIndex.at(k-1);
			if (currentDistance <shortestDistance)
			{
				shortestDistance = currentDistance;
				index = (peakVector.at(peakIndex.at(k))>peakVector.at(peakIndex.at(k-1))? k-1:k);
			}

		}
		if (shortestDistance<distance)
		{
			vector<int>::iterator iter = peakIndex.begin();
			int m = 0;
			while(m++<index)++iter;
			peakIndex.erase(iter);
		}
	}
	
	peakIndex.push_back(pureEyetrackdataSet.size());//方便后面处理
}
std::vector<float> fixationfilter::calculateAdjacentWindowDistance(const list<vector<float>> &pureEyetrackdataSet, int windowWidth, eyeOption eye)
{
	setBasicEye(eye);
	vector<float> distanceVector;
	if (pureEyetrackdataSet.empty())
	{
		return distanceVector;
	}
	list<vector<float>>::const_iterator iter = pureEyetrackdataSet.begin();
	list<vector<float>>::const_iterator end = pureEyetrackdataSet.end();
	for (int i=0;i<windowWidth;i++)
	{
		iter++;
		end--;
	}
	while(iter != end)
	{
		float m_before_x = 0,m_before_y = 0,m_after_x = 0,m_after_y = 0;
		list<vector<float>>::const_iterator precur = iter,nextcur = iter;
		for(int i=0;i<windowWidth;i++)
		{
			switch(eye)
			{
				case lefteye:
					m_before_x += (*(--precur))[x_cordinary]/windowWidth;
					m_before_y += (*precur)[y_cordinary]/windowWidth;
					m_after_x += (*(++nextcur))[x_cordinary]/windowWidth;
					m_after_y += (*nextcur)[y_cordinary]/windowWidth;
					break;
				case righteye:
					m_before_x += (*(--precur))[x_cordinary]/windowWidth;
					m_before_y += (*precur)[y_cordinary]/windowWidth;
					m_after_x += (*(++nextcur))[x_cordinary]/windowWidth;
					m_after_y += (*nextcur)[y_cordinary]/windowWidth;
					break;
				case doubleeyes:
					m_before_x += ((*(--precur))[1]+(*precur)[3])/(2*windowWidth);
					m_before_y += ((*precur)[2]+(*precur)[4])/(2*windowWidth);
					m_after_x += ((*(++nextcur))[1]+(*nextcur)[3])/(2*windowWidth);
					m_after_y += ((*nextcur)[2]+(*nextcur)[4])/(2*windowWidth);
					break;
				default:
					break;
			}
		}
		++iter;

		float curDistance = sqrt(pow((m_before_x-m_after_x)*imgWidth,2)+pow((m_before_y-m_after_y)*imgHeight,2));
		distanceVector.push_back(curDistance);
	}
	return distanceVector;
}

void fixationfilter::getFixationPoints(const list<std::vector<float>> &rawEyetrackerData,vector<vector<int>> &fixationPoints, vector<int> &peakIndex,eyeOption eye)
{
	fixationPoints.clear();
	setBasicEye(eye);
	int shortestdistance = INT_MIN;
	int radius = 60;
	
	while(shortestdistance<radius)
	{
		fixationPoints.clear();
		int index = -1;
		list<vector<float>>::const_iterator iter = rawEyetrackerData.begin(); 
		int j = 0;
		for (unsigned int i=0;i<peakIndex.size();i++)
		{
			float fixation_x = 0;
			float fixation_y = 0;
			int fixationlength = 0;
			vector<int> curFixationPoint;
			if (j != 0)
			{
				for (int m=0;m<windowWidth;++m)
				{
					++iter;
					++j;
				}
			}
			while(iter != rawEyetrackerData.end() && j++<peakIndex.at(i))
			{
				fixation_x += (*iter).at(x_cordinary);
				fixation_y += (*iter).at(y_cordinary);
				++fixationlength;
				++iter;
			}
			curFixationPoint.push_back(fixation_x*imgWidth/fixationlength);
			curFixationPoint.push_back(fixation_y*imgHeight/fixationlength);
			fixationPoints.push_back(curFixationPoint);
		}

		//remove the index that relative two fixation points are too closed!
		shortestdistance = INT_MAX;
		for (unsigned int k=1;k<fixationPoints.size();++k)
		{
			float distance = sqrt(pow(float(fixationPoints.at(k).at(0)-fixationPoints.at(k-1).at(0)),2)+pow(float(fixationPoints.at(k).at(1)-fixationPoints.at(k-1).at(1)),2));
			if (distance<shortestdistance)
			{
				shortestdistance = distance;
				index = k-1;
			}	
		}
		
		if (shortestdistance < radius && index >= 0)
		{
			vector<int>::iterator iter = peakIndex.begin();
			for (int i=0;i<index && iter != peakIndex.end();i++)
			{
				++iter;
			}
			if (iter != peakIndex.end())
			{
				peakIndex.erase(iter);
			}
		}
	}
}

void fixationfilter::getGazePointType(const list<vector<float>> &rawEyetrackerData,vector<vector<int>> &fixationPoints,const vector<int> &peakindex,map<int,GazePointType> &gazePointType)
{
	size_t i = 0,j = 0;
	/*vector<int>::size_type j=0;*/
	while(i<rawEyetrackerData.size() && j<peakindex.size())
	{
		if (j != 0)
		{
			for(int m=0; m<windowWidth; ++m)
			{
				GazePointType gazepoint(string("Saccade"));
				auto currentType = make_pair(i,gazepoint);
				gazePointType.insert(currentType);
				i++;
			}
		}
		for( ;i<peakindex.at(j) && i<rawEyetrackerData.size(); i++)
		{
			GazePointType gazepoint("Fixation",fixationPoints.at(j).at(0),fixationPoints.at(j).at(1));
			auto currentType = make_pair(i,gazepoint);
			gazePointType.insert(currentType);
		}
		j++;
	}
}
void fixationfilter::setBasicEye(eyeOption eye)
{
	switch(eye)
	{
		case lefteye:
			x_cordinary = 1;
			y_cordinary = 2;
			break;
		case righteye:
			x_cordinary = 3;
			y_cordinary = 4;
			break;
	}
}

