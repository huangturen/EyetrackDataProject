#include "StdAfx.h"
#include "readeyetrackingexperimentdatafile.h"
#include "fixationfilter.h"
#include "preprocesseyetrackingdata.h"

using namespace std;

readeyetrackingexperimentdatafile::readeyetrackingexperimentdatafile(const string &filename,eyeOption eye)
	:readfile(filename),m_eye(eye)
{
}


readeyetrackingexperimentdatafile::~readeyetrackingexperimentdatafile(void)
{
}

ReturnData readeyetrackingexperimentdatafile::getProcessedData()
{
	readCsvFile(m_filename);
	ReturnData r;
	r.eyetrackerdata  = m_eyetrackerPreProcessed;
	return r;
}

std::vector<std::vector<int>> readeyetrackingexperimentdatafile::getFixationPoints()
{
	return m_fixationPoints;
}
std::map<int,GazePointType> readeyetrackingexperimentdatafile::getGazePointType()
{
	return m_gazePointType;
}

int readeyetrackingexperimentdatafile::getBlinkCount()
{
	return m_blinkCount;
}
void readeyetrackingexperimentdatafile::readCsvFile(const std::string &filename)
{
	ifstream infile(filename.c_str());
	if (!infile)
	{
		cerr << "Can't open csv file " << filename <<endl;
		return;
	}

	string line;
	cout << "start process file:" <<" "<< filename << endl;
	int count = 1;
	m_eyetrackerdatacontainer.clear();
	while(getline(infile,line))
	{
		if(count++<11)continue;
		vector<string> splitresult;
		splitstring(line,",",splitresult);
		vector<float> currenteyetrackdata;
		stringtofloat(splitresult,currenteyetrackdata);
		m_eyetrackerdatacontainer.push_back(currenteyetrackdata);
	}	
	processEyetrackerData();
}

void readeyetrackingexperimentdatafile::stringtofloat(const vector<string> &source,vector<float> &destination)
{
	if (source.empty())
	{
		return;
	}
	typedef vector<string>::const_iterator iterator;
	for(iterator iter = source.begin()+1;iter != source.end(); iter++)
	{
		destination.push_back(atof((*iter).c_str()));
	}
}

void readeyetrackingexperimentdatafile::processEyetrackerData()
{
	shared_ptr<preprocesseyetrackingdata> preProcessor(new preprocesseyetrackingdata(m_eyetrackerdatacontainer));
	m_eyetrackerPreProcessed = preProcessor->getEyetrackingDataAfterPreProcess();
	m_blinkCount = preProcessor->getBlinkCount();
	shared_ptr<fixationfilter> fixationFilter(new fixationfilter(m_eyetrackerPreProcessed,m_eye));
	m_gazePointType = fixationFilter->getGazePointType();
	m_fixationPoints = fixationFilter->getFixationPoints();

}

void readeyetrackingexperimentdatafile::writeDataToFile(const std::string &filesavename)
{
	saveFilteredEyetrackingDataToFile(filesavename);
}

void readeyetrackingexperimentdatafile::saveFilteredEyetrackingDataToFile(const string &filesavename)
{
    fstream infile;
    infile.open(filesavename,ios::in);
	if (infile)
	{
		cout << filesavename <<" is existed!" << endl;
		return;
	}

	m_saveFileName = make_shared<ofstream> (filesavename,ios_base::app);
	if (!m_saveFileName->is_open())
	{
		cout << "Can't open the save file correctly!" << endl;
		return;
	}
	
	stringstream stream;
	writeHeader(stream);
	
	int index = 0;
	for (list<vector<float>>::const_iterator iter = m_eyetrackerPreProcessed.begin();iter != m_eyetrackerPreProcessed.end();++iter,++index)
	{
		stringstream stream;
		writeEyetrackerDataToFile(stream,*iter,m_gazePointType,index);
	}
	m_saveFileName->close();
}

void readeyetrackingexperimentdatafile::writeEyetrackerDataToFile(stringstream &stream,const vector<float> &pureeyetrackingdata,map<int,GazePointType> &gazePointType,int index)
{
	stream << pureeyetrackingdata.at(0) << splitsymbol;
	stream << gazePointType.at(index).pointType<< splitsymbol;
	if (gazePointType.at(index).point_x == -1 && gazePointType.at(index).point_y == -1)
	{
		stream << " "<< splitsymbol;
		stream << " "<< splitsymbol;
	}
	else
	{
		stream << gazePointType.at(index).point_x<< splitsymbol;
		stream << gazePointType.at(index).point_y<< splitsymbol;
	}
	unsigned int i=1;
	for (; i<pureeyetrackingdata.size()-1; i++)
	{
		stream << pureeyetrackingdata.at(i)<< splitsymbol;
	}
	stream << pureeyetrackingdata.at(i)<< '\n';
	writeStreamToFile(m_saveFileName,stream);
}
void readeyetrackingexperimentdatafile::writeHeader(stringstream &stream)
{					
	stream << "time_stamp,GazePointType,FixationPointX,FixationPointY,LeftGazePoint2dX,LeftGazePoint2dY,"
		<<"RightGazePoint2dX,RightGazePoint2dY,LeftEyePositionX(UCSmm),LeftEyePositionY(UCSmm),LeftEyePositionZ(UCSmm),"
		<< "RightEyePositionX(UCSmm),RightEyePositionY(UCSmm),RightEyePositionZ(UCSmm),LeftGazePoint3DX(UCSmm),"
		<< "LeftGazePoint3DY(UCSmm),LeftGazePoint3DZ(UCSmm),rightGazePoint3DX(UCSmm),rightGazePoint3DY(UCSmm),"
		<< "rightGazePoint3DZ(UCSmm),left_validity,right_validity,left_pupil_diameter,right_pupil_diameter"
		<< endl;
	writeStreamToFile(m_saveFileName,stream);
}

