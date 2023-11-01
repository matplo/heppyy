#ifndef HEPPYY_READJEWEL_HH
#define HEPPYY_READJEWEL_HH

#include <hepmc2util/readfile.hh>

#include <HepMC/IO_GenEvent.h>
#include <HepMC/GenEvent.h>

#include <vector>
#include <list>

#include<fastjet/PseudoJet.hh>

namespace HeppyyJewelUtil
{
	class ReadJewelHepMC2File : public HeppyyHepMCUtil::ReadHepMCFile
	{
	public:
		ReadJewelHepMC2File(const char *fname);
		virtual ~ReadJewelHepMC2File();

        std::vector<fastjet::PseudoJet> fjParticles(bool only_final = true);
        std::vector<fastjet::PseudoJet> fjParticlesWithStatus(int status = -1);
        std::vector<fastjet::PseudoJet> fjFinalParticlesSubtractedThermal();
        
	private:
        ;
	};
};
#endif