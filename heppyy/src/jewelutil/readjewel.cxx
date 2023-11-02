#include "readjewel.hh"

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <limits>
#include <cmath>

#include <fastjet/PseudoJet.hh>

namespace HeppyyJewelUtil
{
	ReadJewelHepMC2File::ReadJewelHepMC2File(const char *fname) 
		: HeppyyHepMCUtil::ReadHepMCFile(fname)
	{
		;
	}

	ReadJewelHepMC2File::~ReadJewelHepMC2File()
	{
		;
	}

	std::vector<fastjet::PseudoJet> ReadJewelHepMC2File::fjParticles(bool only_final)
	{
		std::vector<fastjet::PseudoJet> rv;
		const auto& hep_parts = HepMCParticles(only_final);
		for (std::size_t i = 0; i < hep_parts.size(); ++i)
		{
			auto &part = hep_parts[i];
			auto psj = fastjet::PseudoJet(part->momentum().px(), part->momentum().py(), part->momentum().pz(), part->momentum().e());
			psj.set_user_index(i);
			rv.push_back(psj);
		}
		return rv;
	}

	std::vector<fastjet::PseudoJet> ReadJewelHepMC2File::fjParticlesWithStatus(int status)
	{
		std::vector<fastjet::PseudoJet> rv;
		const auto& hep_parts = HepMCParticlesWithStatus(status);
		for (std::size_t i = 0; i < hep_parts.size(); ++i)
		{
			auto &part = hep_parts[i];
			auto psj = fastjet::PseudoJet(part->momentum().px(), part->momentum().py(), part->momentum().pz(), part->momentum().e());
			psj.set_user_index(i);
			rv.push_back(psj);
		}
		return rv;
	}

	std::pair<std::size_t, std::size_t> minimum_distance(std::vector<fastjet::PseudoJet> &v1, std::vector<fastjet::PseudoJet> &v2)
	{
		int iret = -1;
		int jret = -1;
		double mind = std::numeric_limits<double>::max();
		for (std::size_t i = 0; i < v1.size(); ++i)
		{
			for (std::size_t j = 0; j < v2.size(); ++j)
			{
				auto d = v1[i].delta_R(v2[j]);
				if (d < mind)
				{
					mind = d;
					iret = i;
					jret = j;
				}
			}
		}
		return {iret, jret};
	}

	/// @brief return the list of pseudojets after the subtraction of the thermal particles - status 3
	/// @return std::vector<fastjet::PseudoJet>
	std::vector<fastjet::PseudoJet> ReadJewelHepMC2File::fjFinalParticlesSubtractedThermal()
	{
		std::vector<fastjet::PseudoJet> rv;
		std::vector<fastjet::PseudoJet> ps1 = fjParticlesWithStatus(1);
		std::vector<fastjet::PseudoJet> ps3 = fjParticlesWithStatus(3);
		std::vector<fastjet::PseudoJet> ps4 = fjParticlesWithStatus(4);
		// it looks like we need only one iteration on the distances...
		// pay attention to some mass things... not just the pT subtraction
		// - this indeed may need an additional intermediate particle structure (?)
		// - mdelta is defined as part.mdelta = sqrt(partmom.mass2() + sqr(partmom.pT())) - partmom.pT();
		// the end result is a mixture of particles subtracted thermal particles + remaining thermal particles

		// actually not sure the algo makes sense - it is not iterative in the pair building
		// find the pairs
		// subtract one from the other - the momenta are updated after each pair is evaluated (?)
		while (ps3.size() > 0)
		{
			auto mpair = minimum_distance(ps1, ps3);
			if (ps1[mpair.first].perp() > ps3[mpair.second].perp())
			{
				;
			}
			else
			{
				;
			}
			ps3.erase(ps3.begin() + mpair.second);
		}
		return rv;
	}

	// from rivet routine
	std::vector<fastjet::PseudoJet> ReadJewelHepMC2File::fjFinalParticlesSubtractedThermalRivet()
	{
		std::vector<fastjet::PseudoJet> rv;

		return rv;
	}
}
