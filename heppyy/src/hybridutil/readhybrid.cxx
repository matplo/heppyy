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

	EventInfo::EventInfo()
		: _weight(0.0)
		, _cross(0.0)
		, _x(0.0)
		, _y(0.0)
	{
	}

	EventInfo::EventInfo(const std::string &line)
		: _weight(0.0)
		, _cross(0.0)
		, _x(0.0)
		, _y(0.0)
	{
		set(line);
	}

	void EventInfo::set(const std::string &line)
	{
		std::istringstream iss(line);
		std::string keyword;
		// weight 0.00116132 cross 1.23074 X 0 Y 0
		iss >> keyword >> _weight >> keyword >> _cross >> keyword >> _x >> keyword >> _y;
	}

	double p_energy(double px, double py, double pz, double m)
	{
		return std::sqrt(px * px + py * py + pz * pz + m * m);
	}

	bool HybridFile::verbose = false;

	HybridFile::HybridFile(const char *fname, int medium_offset)
		: _PDG(new TDatabasePDG())
		, _particles()
		, _sparticles()
		, _spartons()
		, _sevent()
		, _file(fname)
		, _info()
		, _medium_offset(medium_offset)
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
				_info.set(line);
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

	std::vector<fastjet::PseudoJet> HybridFile::getParticles(bool include_wake, bool charged_only)
	{
		std::vector<fastjet::PseudoJet> rv;
		unsigned int i = 0;
		for (auto &p : _sparticles)
		{
			std::istringstream iss(p);
			int pid;
			int status;
			double px, py, pz, m;
			iss >> px >> py >> pz >> m >> pid >> status;

			// skip partons with status -2
			if (status == -2)
				continue;
			// skip hadrons with index 1 or 2
			if (include_wake == false && (status == 1 || status == 2))
				continue;
			// check if a charged hadron
			// note this may mess up the background subtraction (?)
			TParticlePDG *pPDG = _PDG->GetParticle(pid);
			if (charged_only && pPDG->Charge() == 0)
				continue;

			double e = p_energy(px, py, pz, m);
			fastjet::PseudoJet psj(px, py, pz, e);
			if (status == 2 || status == 1)
			{
				if (status == 2)
				{
					psj.set_user_index(-1 * _medium_offset - i);
				}
				else
				{
					psj.set_user_index(_medium_offset + i);
				}
			}
			else
			{
				psj.set_user_index(i);
			}
			rv.push_back(psj);

			i++;
		}
		return rv;
	}

	std::vector<fastjet::PseudoJet> HybridFile::getPartons()
	{
		std::vector<fastjet::PseudoJet> rv;
		unsigned int i = 0;
		for (auto &p : _spartons)
		{
			std::istringstream iss(p);
			int pid;
			int status;
			double px, py, pz, m;
			iss >> px >> py >> pz >> m >> pid >> status;
			if (status != -2)
				continue;
			TParticlePDG *pPDG = _PDG->GetParticle(pid);
			double e = p_energy(px, py, pz, m);
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
