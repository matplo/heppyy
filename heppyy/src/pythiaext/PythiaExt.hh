#ifndef Pythia8_Pythia_H_ext
#define Pythia8_Pythia_H_ext

#include <Pythia8/Pythia.h>
#include <Pythia8/Info.h>
#include <Pythia8/HIInfo.h>

namespace Pythia8
{
	const Info &getInfo(const Pythia &p);
	const HIInfo *getHIInfo(const Pythia &p);
}

#endif // Pythia8_Pythia_H_ext