#pragma once
#include "StdAfx.h"
#include <vector>
#include <list>
#include <memory>
#include <utility>
#include <map>
/*This class is used to filter the eye tracker data*/
class fixationfilter
{
	public:
		fixationfilter(const std::list<std::vector<float>> &eyetrackdatacontainer,eyeOption eye);//here is an eye tracker container after preprocessing
		std::vector<std::vector<int>> getFixationPoints();
		std::map<int,GazePointType> getGazePointType();
		std::vector<float> getPeakVector();
		std::vector<int> getPeakIndex();
		~fixationfilter(void);
	private:
		void getPeakIndex(const std::list<std::vector<float>> &pureEyetrackdataSet, std::vector<float> &peakVector, std::vector<int> &peakIndex, eyeOption eye);//get the index where the saccade eye movement appeared
		std::vector<float> calculateAdjacentWindowDistance(const std::list<std::vector<float>> &pureEyetrackdataSet,int windowWidth,eyeOption eye); //calculate the distance of two adjacent windows 
		void getFixationPoints(const std::list<std::vector<float>> &rawEyetrackerData, std::vector<std::vector<int>> &fixationPoints, std::vector<int> &peakIndex,eyeOption eye);//get the current fixaiton points based the eyeOption
		void setBasicEye(eyeOption eye);// set the basic eye,there are three options: lefteye,right, doubleeyes
		void getGazePointType(const std::list<std::vector<float>> &rawEyetrackerData,std::vector<std::vector<int>> &fixationPoints,const std::vector<int> &peakindex,std::map<int,GazePointType> &gazePointType);
	private:
		std::list<std::vector<float>> m_eyetrackDataContainer;
		std::vector<std::vector<int>> m_fixationPoints;
		std::map<int,GazePointType> m_gazePointType;
		std::vector<float> m_peakVector;
		std::vector<int> m_peakIndex;
		int x_cordinary;
		int y_cordinary;
		static const char splitSymbol = ',';
		eyeOption m_eye;

};

