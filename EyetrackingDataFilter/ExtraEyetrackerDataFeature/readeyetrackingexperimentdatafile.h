#pragma once
#include <string>
#include <map>
#include <vector>
#include <list>
#include "readfile.h"

class readeyetrackingexperimentdatafile :public readfile
{
	public:
		readeyetrackingexperimentdatafile(const std::string &filename,eyeOption eye);
		~readeyetrackingexperimentdatafile(void);
		ReturnData getProcessedData();
		std::vector<std::vector<int>> getFixationPoints();
		std::map<int,GazePointType> getGazePointType();
		int getBlinkCount();
		void readCsvFile(const std::string &filename);
		void writeDataToFile(const std::string &filesavename);
	private:
		void stringtofloat(const std::vector<std::string> &source,std::vector<float> &destination);
		void processEyetrackerData();
		void writeEyetrackerDataToFile(std::stringstream &stream,const std::vector<float> &pureeyetrackingdata,std::map<int,GazePointType> &gazePointType,int index);
		
		void saveFilteredEyetrackingDataToFile(const std::string &filesavename);
		void writeHeader(std::stringstream &stream);
		
	private:
		std::vector<std::vector<float>> m_eyetrackerdatacontainer;
		std::list<std::vector<float>> m_eyetrackerPreProcessed;
		std::vector<std::vector<int>> m_fixationPoints;
		std::map<int,GazePointType> m_gazePointType;
		int m_blinkCount;
		eyeOption m_eye;
};

