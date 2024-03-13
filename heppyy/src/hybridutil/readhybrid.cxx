#include "readhybrid.hh"

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <limits>
#include <cmath>

#include <fastjet/PseudoJet.hh>

namespace heppyy
{
	bool HybridFile::verbose = false;

	HybridFile::HybridFile(const char *fname)
		: _PDG(new TDatabasePDG())
		, _particles()
		, _sparticles()
		, _spartons()
		, _sevent()
		, _file(fname)
	{
		if (_file.is_open())
		{
			std::cerr << "HybridFile::HybridFile - file " << fname << " is open" << std::endl;
		}
	}

	HybridFile::~HybridFile()
	{
		if (_file.is_open())
		{
			_file.close();
		}
	}

	bool HybridFile::nextEvent()
	{
		_particles.clear();
		_sparticles.clear();
		_spartons.clear();
		std::string line;
		_sevent = "";
		bool _reading_particles 	= false;
		bool _reading_partons 		= false;
		if (!_file.is_open())
			return false;
		if (_file.eof())
			return false;
		while (std::getline(_file, line))
		{
			if (line.find("end") != std::string::npos)
			{
				if (verbose)
					std::cout << "HybridFile::nextEvent - end of event reached - " << line << std::endl;
				break;
			}
			if (line.find("# event") == 0)
			{
				if (verbose)
					std::cout << "HybridFile::nextEvent - start of event reached - " << line << std::endl;
				_sevent = line;
				continue;
			}
			if (line.find("weight") == 0)
			{
				if (verbose)
					std::cout << "HybridFile::nextEvent - - part of event - " << line << std::endl;
				_sevent += line;
				_reading_partons = true;
				continue;
			}
			if (_reading_partons)
			{
				_spartons.push_back(line);
				if (verbose)
					std::cout << "HybridFile::nextEvent - - parton - " << line << " count:" << _spartons.size() << std::endl;
				if (_spartons.size() == 2)
				{
					_reading_partons = false;
					_reading_particles = true;
					if (verbose)
						std::cout << "HybridFile::nextEvent - - number of partons 2 - " << _reading_partons << " -> " << _reading_particles << std::endl;
				}
				continue;
			}
			if (_reading_particles)
			{
				_sparticles.push_back(line);
				continue;
			}
		}
		if (_sparticles.size() > 0)
		{
			return true;
		}
		else
		{
			if (_file.eof())
			{
				if (verbose)
					std::cout << "HybridFile::nextEvent - end of file." << std::endl;
			}
			else
			{
				std::cerr << "HybridFile::nextEvent - no particles." << std::endl;
			}
		}		
		return false;
	}

	double HybridFile::eventInfo(EventInfo info)
	{
		return 0.0;
	}

	double HybridFile::particleInfo(ParticleInfo info)
	{
		return 0.0;
	}

	std::vector<fastjet::PseudoJet> HybridFile::getPseudoJets(bool charged_only)
	{
		std::vector<fastjet::PseudoJet> rv;
		unsigned int i = 0;
		for (auto &p : _sparticles)
		{
			std::istringstream iss(p);
			int pid;
			int status;
			double px, py, pz, e;
			iss >> px >> py >> pz >> e >> pid >> status;
			TParticlePDG *pPDG = _PDG->GetParticle(pid);
			if (charged_only && pPDG->Charge() == 0)
				continue;
			fastjet::PseudoJet psj(px, py, pz, e);
			psj.set_user_index(i++);
			rv.push_back(psj);
		}
		return rv;
	}
	
	const std::vector<std::string> HybridFile::getParticlesStr()
	{
		return _sparticles;
	}

	const std::vector<std::string> HybridFile::getPartonsStr()
	{
		return _spartons;
	}

	const std::string HybridFile::getEventStr()
	{
		return _sevent;
	}

};
