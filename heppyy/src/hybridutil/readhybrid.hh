#ifndef HEPPYY_READHYBRID_HH
#define HEPPYY_READHYBRID_HH

#include <vector>
#include <list>
#include <fstream>
#include <string>

#include<fastjet/PseudoJet.hh>
#include <TDatabasePDG.h>

namespace heppyy
{
	class HybridFile
	{
	public:
		enum ParticleInfo {kPID = 1, kStatus};
		enum EventInfo {kWeight = 1, kCross, kX, kY};

		HybridFile(const char *fname);
		virtual ~HybridFile();

		std::vector<fastjet::PseudoJet> getPseudoJets(bool charged_only = false);

		TDatabasePDG *getPDG() {return _PDG;}
		bool 		nextEvent();
		double 	eventInfo(EventInfo info);
		double 	particleInfo(ParticleInfo info);

		static bool verbose;
	private: 
		TDatabasePDG *_PDG;
		std::vector<fastjet::PseudoJet> _particles;
		std::vector<std::string> _sparticles;
		std::vector<std::string> _spartons;
		std::string _sevent;
		std::ifstream _file;
	};
};
#endif
