#pragma once

#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
//#include <cv.h>
//#include <highgui.h>
class readfile
{
	public:
		readfile(const std::string &filename);
		virtual ~readfile(void);
		virtual ReturnData getProcessedData();
		virtual void readCsvFile(const std::string &filename) = 0;
		virtual void writeDataToFile(const std::string &filesavename) = 0;

		void writeStreamToFile(std::shared_ptr<std::ofstream> &fileSaveName,std::stringstream &stream);
		
	protected:
		void splitstring(const std::string &line,const std::string &symbol,std::vector<std::string> & ret);//将一列string以“，”为界分割开来！
		virtual void stringtofloat(const std::vector<std::string> &source,std::vector<float> &destination);
	protected:
		std::string m_filename;
		std::shared_ptr<std::ofstream> m_saveFileName; 
		static const char splitsymbol = ',';
};

