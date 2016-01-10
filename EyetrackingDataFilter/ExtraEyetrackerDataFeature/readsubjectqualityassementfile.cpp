#include "StdAfx.h"
#include "readsubjectqualityassementfile.h"
#include <float.h>
#include <algorithm>

using namespace std;
struct confidenceIntervalStruct{
	string imgname;
	int isInConfidenceInterval;// 1 is in, 0 is out;
	confidenceIntervalStruct(){}
	confidenceIntervalStruct(string imgName,int confidenceState=0):imgname(imgName),isInConfidenceInterval(confidenceState){}
};

readsubjectqualityassementfile::readsubjectqualityassementfile(const string &filename)
	:readfile(filename)
{
}


readsubjectqualityassementfile::~readsubjectqualityassementfile(void)
{
}

ReturnData readsubjectqualityassementfile::getProcessedData()
{
	readCsvFile(m_filename);
	ReturnData r;
	r.subjectQualityAssessment  = m_classifierbasedonimage;
	return r;
}
void readsubjectqualityassementfile::readCsvFile(const std::string &filename)
{
	ifstream infile(filename);
	if (!infile)
	{
		cerr << "Can't open csv file " << filename <<endl;
		return;
	}

	string line;
	cout << "start process file:" <<endl
		<< filename << endl;
	//m_eyetrackerdatacontainer.clear();
	vector<string> splitresult;
	vector<float> currentassessmentdata;
	SubjectAssessment curItem;
	while(getline(infile,line))
	{
		splitresult.clear();
		currentassessmentdata.clear();
		splitstring(line,",",splitresult);
		stringtofloat(splitresult,currentassessmentdata);

		if (splitresult.at(0) == "ParticipantName")
		{
			curItem.user = splitresult.at(1);
			m_userNameVector.push_back(curItem.user);
		}
		if (*currentassessmentdata.begin()>0)
		{
			string filename = splitresult.at(1);
			curItem.assessmentscore = currentassessmentdata.at(5);
			insertToClassifierBasedOnImage(m_classifierbasedonimage,filename,curItem);
			insertToClassifierBasedOnUser(m_classifierbasedonuser,curItem.user,curItem.assessmentscore);
		}		
	}	
}

void readsubjectqualityassementfile::writeDataToFile(const std::string &filesavename)
{
    fstream infile(filesavename);
	if (infile)
	{
		cout << filesavename << "is existed!" << endl;
		return;
	}
	m_saveFileName = make_shared<ofstream> (filesavename,ios_base::app);
	if (!m_saveFileName->is_open())
	{
		cout << "Can't open the save file correctly!" << endl;
		return;
	}
	stringstream stream;
	writeHeader(filesavename,stream,m_userNameVector);
	for (SubjectAssessmentMap::const_iterator iter = m_classifierbasedonimage.begin(); iter != m_classifierbasedonimage.end(); ++iter)
	{
		stringstream stream;
		stream << iter->first << splitsymbol;
		writeDataToFile(filesavename,stream,iter->second);
	}
	
}


void readsubjectqualityassementfile::writeDataToFile(const string &filesavename,stringstream &stream,const vector<SubjectAssessment> &classifier)
{
	vector<SubjectAssessment>::size_type i=0;
	for (; i<classifier.size()-1;++i)
	{
		stream << classifier.at(i).assessmentscore << splitsymbol;
	}
	stream << classifier.at(i).assessmentscore << endl;
	writeStreamToFile(m_saveFileName,stream);

}
void readsubjectqualityassementfile::writeHeader(const string &filesavename,stringstream &stream,const vector<string> &imgNameVector)
{
	stream << "ImageName" << splitsymbol;
	vector<string>::size_type i = 0;
	for (; i < imgNameVector.size()-1; ++i)
	{
		stream << imgNameVector.at(i) << splitsymbol;
	}
	stream << imgNameVector.at(i) << endl;
	writeStreamToFile(m_saveFileName,stream);
}
map<string,vector<float>> readsubjectqualityassementfile::getEffectiveAssessment()
{
	return m_classifierbasedonuser;
}
void readsubjectqualityassementfile::stringtofloat(const vector<string> &source,vector<float> &destination)
{
	if (source.empty())
	{
		return;
	}
	typedef vector<string>::const_iterator iterator;
	for(iterator iter = source.begin();iter != source.end(); iter++)
	{
		destination.push_back(atof((*iter).c_str()));
	}
}

void readsubjectqualityassementfile::insertToClassifierBasedOnImage(map<string,vector<SubjectAssessment>> &distinationClassifierBasedOnImage,const string &filename, const SubjectAssessment &assessmentItem)
{
	if (distinationClassifierBasedOnImage.find(filename) == distinationClassifierBasedOnImage.end())
	{
		vector<SubjectAssessment> currentAssementPoint;
		currentAssementPoint.push_back(assessmentItem);
		auto tmp = make_pair(filename,currentAssementPoint);
		distinationClassifierBasedOnImage.insert(tmp);
	}
	else
	{
		distinationClassifierBasedOnImage.at(filename).push_back(assessmentItem);
	}
}

void readsubjectqualityassementfile::insertToClassifierBasedOnUser(map<string,vector<float>> &distinationClassifierBasedOnUser, const string &username, float score)
{
	if (distinationClassifierBasedOnUser.find(username) == distinationClassifierBasedOnUser.end())
	{
		vector<float> currentAssementPoint;
		currentAssementPoint.push_back(score);
		auto tmp = make_pair(username,currentAssementPoint);
		distinationClassifierBasedOnUser.insert(tmp);
	}
	else
	{
		distinationClassifierBasedOnUser.at(username).push_back(score);
	}
}

void readsubjectqualityassementfile::eliminateIneffectiveAssessmentBasedOnCorrelation(map<string,vector<float>> &classifer)
{
	const unsigned long numOfUser = classifer.size();
	if (0 == numOfUser)
	{
		return;
	}
	float leastCorrectiveCofficient = FLT_MIN, threshold = 0.5;
	while(leastCorrectiveCofficient < threshold)
	{
		vector<float> result = calculateMeanSujectAssessmentSocore(classifer);
		auto pivot = normalizeVector(result);
		leastCorrectiveCofficient = FLT_MAX;
		string willEraseUser;
		map<string,float> correlationCofficient;
		for (map<string,vector<float>>::iterator iter=classifer.begin(); iter != classifer.end(); ++iter)
		{
			vector<float> tmp = normalizeVector(iter->second);
			float correlativeCofficient = pearsonCorrelationCoefficient(tmp,pivot);
			correlationCofficient.insert(make_pair(iter->first,correlativeCofficient));

			if (leastCorrectiveCofficient>correlativeCofficient)
			{
				leastCorrectiveCofficient = correlativeCofficient;
				willEraseUser = iter->first;
			}
		}

		if (leastCorrectiveCofficient<threshold)
		{
			classifer.erase(classifer.find(willEraseUser));
		}

	}
	
}
bool compare(const PAIR &p,const PAIR &q)
{
	return p.second>q.second;
}
void readsubjectqualityassementfile::eliminateIneffectiveAssessmentBasedOnMeanAndVariance(map<string,vector<float>> &classifer)
{
	unsigned long numOfUser = classifer.size();
	if (0 == numOfUser)
	{
		return;
	}
	vector<float> result = calculateMeanSujectAssessmentSocore(classifer);
	map<string,float> varianceResult;
	for (map<string,vector<float>>::iterator iter=classifer.begin(); iter != classifer.end(); ++iter)
	{
		float variance = sumOfVariance(normalizeVector(iter->second),result);
		varianceResult.insert(make_pair(iter->first,variance));
	}
	vector<PAIR> varianceVector(varianceResult.begin(),varianceResult.end());
	sort(varianceVector.begin(),varianceVector.end(),compare);
	float maxVariance = FLT_MAX,threshold = 7;

	while(threshold < maxVariance)
	{
		for(vector<PAIR>::iterator iter = varianceVector.begin(); iter != varianceVector.end(); ++iter)
		{
			maxVariance = iter->second;
			if (maxVariance>threshold)
			{
				classifer.erase(classifer.find(iter->first));
			}
		}
	}
}

void readsubjectqualityassementfile::eliminateIneffectiveAssessment(SubjectAssessmentMap &classifierBasedOnImage)//95% Confidence interval
{
	map<string,vector<confidenceIntervalStruct>> confidenceResult;
	map<string,int> confidenceCount;
	const int N = 24;
	if (classifierBasedOnImage.size()==0)
	{
		return;
	}
	for (SubjectAssessmentMap::iterator iter = classifierBasedOnImage.begin(); iter != classifierBasedOnImage.end(); ++iter)
	{
		float curItemAverage = 0;
		const unsigned long assessmentNum = iter->second.size();
		for (vector<SubjectAssessment>::iterator subIter = iter->second.begin(); subIter != iter->second.end(); ++subIter)
		{
			curItemAverage += subIter->assessmentscore/assessmentNum;
		}
		float  dvt = 0;
		for (vector<SubjectAssessment>::iterator subIter = iter->second.begin(); subIter != iter->second.end(); ++subIter)
		{
			dvt += pow((subIter->assessmentscore-curItemAverage),2)/(N-1);
		}
		float stddvt = sqrt(dvt);
		float delta = 1.96*stddvt/sqrt(static_cast<double>(N));//method to calculate 95% confidence interval
		
		float confidenceIntervalUpper = curItemAverage+delta;
		float confidenceIntervalLower = curItemAverage-delta;

		for (vector<SubjectAssessment>::iterator subIter = iter->second.begin(); subIter != iter->second.end(); ++subIter)
		{
			confidenceIntervalStruct tmpCIS(iter->first,0);
			if (subIter->assessmentscore >= confidenceIntervalLower && subIter->assessmentscore <= confidenceIntervalUpper)
			{
				tmpCIS.isInConfidenceInterval = 1;
			}
			if (confidenceResult.find(subIter->user) == confidenceResult.end())
			{
				vector<confidenceIntervalStruct> tmpVect;tmpVect.push_back(tmpCIS);
				confidenceResult.insert(make_pair(subIter->user,tmpVect));
				confidenceCount.insert(make_pair(subIter->user,tmpCIS.isInConfidenceInterval));
			}
			else
			{
				confidenceResult.at(subIter->user).push_back(tmpCIS);
				confidenceCount.at(subIter->user) += tmpCIS.isInConfidenceInterval;
			}
		}
		
	}
}
vector<float> readsubjectqualityassementfile::calculateMeanSujectAssessmentSocore(const std::map<std::string,std::vector<float>> &classifer)
{
	const unsigned long numOfUser = classifer.size();
	const unsigned long numOfImage = classifer.begin()->second.size();
	vector<float> result(numOfImage,0);
	for (map<string,vector<float>>::const_iterator iter=classifer.begin(); iter != classifer.end(); ++iter)
	{
		vector<float> tmp2 = normalizeVector(iter->second);
		for(vector<float>::size_type i=0;i<tmp2.size();++i)
		{
			result.at(i) += tmp2.at(i)/numOfUser;
		}	
	}
	return result;
}
float readsubjectqualityassementfile::pearsonCorrelationCoefficient(const vector<float> vect1,const vector<float> vect2)
{
	if (vect1.size() != vect2.size() || 0 == vect1.size())
	{
		cout << "Invalid input" << endl;
		return 2;//The correlative coefficient is in [-1,1]
	}
	float average1 = sumOfVector(vect1)/vect1.size();
	float average2 = sumOfVector(vect2)/vect2.size();

	float numerator=0,denominator = 0,part1 = 0,part2 = 0;
	for (vector<float>::size_type i=0;i<vect1.size();i++)
	{
		numerator += (vect1.at(i)-average1)*(vect2.at(i)-average2);
		part1 += pow(vect1.at(i)-average1,2);
		part2 += pow(vect2.at(i)-average2,2);
	}
	denominator = sqrt(part1*part2);

	return denominator == 0? 2:numerator/denominator;//if the denominator is zero,return 2 to refer the wrong operator.
}


float readsubjectqualityassementfile::sumOfVector(const vector<float> &vect)
{
	if (vect.size()<=0)
	{
		return 0;
	}
	float Sum = 0;
	for(vector<float>::const_iterator iter = vect.begin(); iter != vect.end(); ++iter)
	{
		Sum += *iter;
	}
	return Sum;
}

float readsubjectqualityassementfile::sumOfVariance(const std::vector<float> vect1,const std::vector<float> vect2)
{
	if (vect1.size() != vect2.size() || 0 == vect1.size())
	{
		cout << "Invalid input" << endl;
		return -1;
	}
	float variance = 0;
	for (vector<float>::size_type i = 0;i<vect1.size();i++)
	{
		variance += pow(vect1.at(i)-vect2.at(i),2);
	}
	return variance;
}
vector<float> readsubjectqualityassementfile::normalizeVector(const vector<float> &vect)
{
	vector<float> result;
	if (vect.size() == 0)
	{
		return result;
	}
	float maxVal = FLT_MIN,minVal = FLT_MAX;
	for(vector<float>::const_iterator iter = vect.begin(); iter != vect.end(); iter++)
	{
		maxVal = *iter>maxVal? *iter:maxVal;
		minVal = *iter<minVal? *iter:minVal;
	}
	float eps = 1.0e-6;
	if (maxVal-minVal<eps)
	{
		vector<float>::const_iterator iter = vect.begin();
		while(iter != vect.end())
			result.push_back((*iter)/maxVal);
		return result;
	}
	for(vector<float>::const_iterator iter = vect.begin(); iter != vect.end(); iter++)
	{
		result.push_back(((*iter)-minVal)/(maxVal-minVal));
	}
	return result;
}

