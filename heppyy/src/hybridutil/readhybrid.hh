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
	class EventInfo
	{
	public:
		EventInfo();
		EventInfo(const std::string &line);
		void set(const std::string &line);
		virtual ~EventInfo() {;}
		double weight() const {return _weight;}
		double cross() const {return _cross;}
		double sigmaGen() const { return _cross; }
		double x() const { return _x; }
		double y() const {return _y;}
	private:
		double _weight;
		double _cross;
		double _x;
		double _y;
	};

	class HybridFile
	{
	public:
		// enum ParticleInfo {kPID = 1, kStatus};
		// enum EventInfo {kWeight = 1, kCross, kX, kY};

		HybridFile(const char *fname, int medium_offset = 1001);
		virtual ~HybridFile();

		std::vector<fastjet::PseudoJet> getParticles(bool include_wake = false, bool charged_only = false);
		const std::vector<std::string> getParticlesStr();

		std::vector<fastjet::PseudoJet> getPartons();
		const std::vector<std::string> getPartonsStr();
		const std::string getEventStr();

		TDatabasePDG *getPDG() {return _PDG;}

		bool 		nextEvent();

		const EventInfo & info() {return _info;}

		static bool verbose;
	private: 
		TDatabasePDG *_PDG;
		std::vector<fastjet::PseudoJet> _particles;
		std::vector<std::string> _sparticles;
		std::vector<std::string> _spartons;
		std::string _sevent;
		std::ifstream _file;
		EventInfo _info;
		int _medium_offset;
	};
};
#endif
