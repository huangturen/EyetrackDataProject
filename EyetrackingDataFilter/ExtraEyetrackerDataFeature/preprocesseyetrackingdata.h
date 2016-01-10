#pragma once
#include <list>
#include <vector>
class preprocesseyetrackingdata
{
	public:
		preprocesseyetrackingdata(const std::vector<std::vector<float>> &eyetrackdatacontainer);
		std::list<std::vector<float>> getEyetrackingDataAfterPreProcess();
		int getBlinkCount();
		~preprocesseyetrackingdata(void);
	private:
		void strimEyeBlink(std::list<std::vector<float>> &eyetrackdatacontainer);//remove the blink eye movement data;
		enum eyeOption{lefteye=0,righteye,doubleeyes};
		bool eyestateIsNormal(const std::vector<float> &currenteyetrackingdata);//judge whether the eye was catched by eyetracker correctly
	private:
		std::list<std::vector<float>> m_eyetrackdatacontainer;
		int blink_count;
};

