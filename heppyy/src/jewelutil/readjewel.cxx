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
		, _se(new HeppyyRivet::SubtractedJewelEvent(0.5))
		, _PDG(new TDatabasePDG())
	{
		;
	}

	ReadJewelHepMC2File::~ReadJewelHepMC2File()
	{
		delete _se;
		delete _PDG;
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
	std::vector<fastjet::PseudoJet> ReadJewelHepMC2File::fjFinalParticlesSubtractedThermalTest()
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

	void ReadJewelHepMC2File::runSubstractionThermalRivet(double dmax);
	{
		_se->resetdRmax(dmax);
		_se->project(fEvent);
	}

		// from rivet routine
	std::vector<fastjet::PseudoJet> ReadJewelHepMC2File::getPseudoJets(bool charged_only = false);
	{
		std::vector<fastjet::PseudoJet> rv;
		//for (auto &p : se.subtractedEvent())
		const std::vector<HepMC::GenParticle> & vse = _se->subtractedEvent();
		for (std::size_t i = 0; i < vse.size(); ++i)
		{
			if (charged_only)
			{
				int pdg_id = vse[i].pdg_id();
				TParticlePDG *pPDG = _PDG->GetParticle(pdg_id);
				if (pPDG->Charge() == 0)
					continue;
			}
			fastjet::PseudoJet psj(vse[i].momentum().px(), vse[i].momentum().py(), vse[i].momentum().pz(), vse[i].momentum().e());
			psj.set_user_index(i);
			rv.push_back(psj);
		}
		return rv;
	}
}
