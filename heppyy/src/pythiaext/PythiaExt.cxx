#include "PythiaExt.hh"

namespace Pythia8
{
	const Info &getInfo(const Pythia &p)
	{
		return p.info;
	}

	const HIInfo *getHIInfo(const Pythia &p)
	{
		return p.info.hiInfo;
	}
}
