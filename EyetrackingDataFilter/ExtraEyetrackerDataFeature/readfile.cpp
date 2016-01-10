#include "StdAfx.h"
#include "readfile.h"

using namespace std;

readfile::readfile(const string &filename)
	:m_filename(filename)
{
}
readfile::~readfile(void)
{
}
ReturnData readfile::getProcessedData()
{
	ReturnData r;
	return r;
}


void readfile::splitstring(const string &line,const string &symbol,vector<string> & ret)
{
	if (line.empty())
	{
		return;
	}
	size_t last = 0;
	size_t index = line.find_first_of(symbol,last);
	while(index != string::npos)
	{
		ret.push_back(line.substr(last,index-last));
		last = index+1;
		index = line.find_first_of(symbol,last);
	}
	if (index-last>0)
	{
		ret.push_back(line.substr(last,index-last));
	}
}

void readfile::stringtofloat(const vector<string> &source,vector<float> &destination)
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

void readfile::writeStreamToFile(std::shared_ptr<std::ofstream> &fileSaveName, stringstream &stream)
{
	unsigned long size = stream.str().size();
	char* container = new char[size];
	stream.read(container,size);
	const char* p = container;
	fileSaveName->write(p,size);
	stream.flush();
}

