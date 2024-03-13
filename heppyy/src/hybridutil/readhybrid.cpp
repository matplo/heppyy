#include "readhybrid.hh"

namespace Heppyy
{

HybridFile::HybridFile(const char *fname)
{
}

bool HybridFile::nextEvent()
{
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

std::vector<fastjet::PseudoJet> HybridFile::getPseudoJets(bool charged_only = false);
{
	return std::vector<fastjet::PseudoJet>();
}

};
