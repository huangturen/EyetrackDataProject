#include "StdAfx.h"
#include "preprocesseyetrackingdata.h"
#include <iostream>
using namespace std;

const int lefteyestate = 17;
const int righteyestate = 18;
const double epsle = 1e-3;

preprocesseyetrackingdata::preprocesseyetrackingdata(const vector<vector<float>> &eyetrackdatacontainer)
	:blink_count(0),m_eyetrackdatacontainer(eyetrackdatacontainer.begin(),eyetrackdatacontainer.end())
{
}


preprocesseyetrackingdata::~preprocesseyetrackingdata(void)
{
}

list<vector<float>> preprocesseyetrackingdata::getEyetrackingDataAfterPreProcess()
{
	strimEyeBlink(m_eyetrackdatacontainer);
	return m_eyetrackdatacontainer;
}
int preprocesseyetrackingdata::getBlinkCount()
{
	return blink_count;
}
void preprocesseyetrackingdata::strimEyeBlink(list<vector<float>> &eyetrackdatacontainer)
{
	list<vector<float>>::iterator iter = eyetrackdatacontainer.begin();
	do{
		int blink_moment = 0;
		while (iter != eyetrackdatacontainer.end() && !eyestateIsNormal(*iter))
		{
			blink_moment++;
			list<vector<float>>::iterator p = iter;
			if (p != eyetrackdatacontainer.end())
			{
				iter++;
				eyetrackdatacontainer.erase(p);
			}			
		}
		if (blink_moment>4)
		{
			blink_count++;
		}
		blink_moment = 0;
		while (iter != eyetrackdatacontainer.end() && eyestateIsNormal(*iter))
		{
			++iter;
		}
	}while(iter != eyetrackdatacontainer.end());
}

bool preprocesseyetrackingdata::eyestateIsNormal(const std::vector<float> &currenteyetrackingdata)
{
	if (currenteyetrackingdata.empty())
	{
		return false;
	}
	if (currenteyetrackingdata[lefteyestate]>-epsle && currenteyetrackingdata[lefteyestate]< epsle && currenteyetrackingdata[righteyestate]>-epsle && currenteyetrackingdata[righteyestate]< epsle)
	{
		return true;
	}
	return false;
}