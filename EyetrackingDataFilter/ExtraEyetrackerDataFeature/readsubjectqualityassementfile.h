#pragma once
#include "StdAfx.h"
#include "readfile.h"
#include <string>
#include <map>
#include <sstream>
#include <fstream>

class readsubjectqualityassementfile :public readfile
{
public:
	readsubjectqualityassementfile(const std::string &filename);
	~readsubjectqualityassementfile(void);
	ReturnData getProcessedData();
	void readCsvFile(const std::string &filename);
	std::map<std::string,std::vector<float>> getEffectiveAssessment();
	void writeDataToFile(const std::string &filesavename);
private:
	typedef std::map<std::string,std::vector<SubjectAssessment>> SubjectAssessmentMap;
	void stringtofloat(const std::vector<std::string> &source,std::vector<float> &destination);
	void insertToClassifierBasedOnImage(std::map<std::string,std::vector<SubjectAssessment>> &distinationClassifierBasedOnImage, const std::string &filename, const SubjectAssessment &assessmentItem);
	void insertToClassifierBasedOnUser(std::map<std::string,std::vector<float>> &distinationClassifierBasedOnUser, const std::string &username, float score);
	void writeDataToFile(const std::string &filesavename,std::stringstream &stream,const std::vector<SubjectAssessment> &classifier);
	void writeHeader(const std::string &filesavename,std::stringstream &stream,const std::vector<std::string> &imgNameVector);

	void eliminateIneffectiveAssessmentBasedOnCorrelation(std::map<std::string,std::vector<float>> &classifer);
	void eliminateIneffectiveAssessmentBasedOnMeanAndVariance(std::map<std::string,std::vector<float>> &classifer);
	void eliminateIneffectiveAssessment(std::map<std::string,std::vector<SubjectAssessment>> &classifierBasedOnImage);//95% Confidence interval
	std::vector<float> calculateMeanSujectAssessmentSocore(const std::map<std::string,std::vector<float>> &classifer);
	float sumOfVector(const std::vector<float> &vect);
	float pearsonCorrelationCoefficient(const std::vector<float> vect1,const std::vector<float> vect2);
	float sumOfVariance(const std::vector<float> vect1,const std::vector<float> vect2);
	std::vector<float> normalizeVector(const std::vector<float> &vect);

	/*bool compare(const PAIR &p,const PAIR &q);*/
private:
	std::map<std::string,std::vector<SubjectAssessment>> m_classifierbasedonimage;
	std::map<std::string,std::vector<float>> m_classifierbasedonuser;
	std::vector<std::string> m_userNameVector;
};

