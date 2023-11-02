#ifndef HEPPYY_RIVET_SubtractedJewelEvent_HH
#define HEPPYY_RIVET_SubtractedJewelEvent_HH

#include <HepMC/IO_GenEvent.h>
#include <HepMC/GenEvent.h>

#include <vector>

namespace HeppyyRivet {

    struct My4Mom {
	    double pt;
	    double mdelta;
	    double phi;
	    double y;
    } ;

    struct MyPart {
	    double pt;
	    double mdelta;
	    double phi;
	    double y;
	    int    id;
    } ;

    struct MyDist {
	    double dR;
	    size_t ipart;
	    size_t itherm;
    } ;
    
    inline bool MyDistComp (const MyDist& dist1, const MyDist& dist2) {
	    return dist1.dR < dist2.dR; 
    }

	class SubtractedJewelEvent 
	{
		public:
		void project(HepMC::GenEvent *e);

		SubtractedJewelEvent(double dRmax) : _dRmax(dRmax)
		{
			;
		}

		const std::vector<HepMC::GenParticle> &subtractedEvent() const { return _subtrevent; }

		protected:

		void clear();
		void translateParticles(HepMC::GenEvent *e); 
		std::vector<MyDist> buildPairs();
		void doSubtraction(std::vector<MyDist> & dist);
		void collectResult();
		
		double _dRmax;
		std::vector<HepMC::GenParticle> _subtrevent;
		std::vector<MyPart>       _myparticles;
		std::vector<My4Mom>       _mythermals;

	};

}

#endif
