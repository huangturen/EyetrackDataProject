#pragma once
#include <list>
#include <vector>
#include <sstream>
#include <fstream>
#include <memory>
class eyetrackFeatureFactory
{
public:
	eyetrackFeatureFactory(const std::list<std::vector<float>>& eyetrackerdata,const std::vector<std::vector<int>> &fixationPoints,
		const std::map<int,GazePointType>& gazePointType,int blinkCount);
	DataFeture getEyetrackerDataFetures();
	void writeEyetrackerDataFeature(const std::string& outputFileName,featureFileType type);
	void setDisparityFeature(const DisparityFeature& dispfeature);
	void setSubjectAssessmentScore(int score);
	~eyetrackFeatureFactory(void);
private:
	void gazePointFeatureProcess(DataFeture &datafeature, const std::vector<std::vector<int>>& fixationPoints);
	void fixationFeatureProcess(DataFeture &datafeature,const std::map<int,GazePointType>& gazepointtype);
	float getDistanceBetweenTwoFixations(const std::vector<int>& p1,const std::vector<int>& p2);
	void writeEyetrackerDataStreamCommon(std::stringstream &stream);
	void writeEyetrackerDataStreamStandard(std::stringstream &stream);
	void writeStreamToFile(std::shared_ptr<std::ofstream> &fileSaveName, std::stringstream &stream);
    float getDistanceBetweenTwoFixationsInDisparityAngular(const std::list<std::vector<float>>& eyetrackdata, const std::map<int,GazePointType>& gazepointType);
private:
	std::list<std::vector<float>> m_eyetrackerdata;
	int m_subjectAssessmentScore;
	std::vector<std::vector<int>> m_fixationPoints;
	std::map<int,GazePointType> m_gazePointType;
	std::shared_ptr<std::ofstream> m_savefile;
	DataFeture m_datafeture;
	DisparityFeature m_disparityFeature;
	int m_blinkCount;
	static const char splitSymbols = ' ';
};

