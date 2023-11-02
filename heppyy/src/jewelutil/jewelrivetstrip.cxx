#include "jewelrivetstrip.hh"
#include <cmath>

namespace std
{
	double sqr(const double &v)
	{
		return std::pow(v, 2.);
	}
}

namespace HeppyyRivet
{

	bool fuzzyEquals(double a, double b, double epsilon = 1e-6)
	{
		return std::abs(a - b) < epsilon;
	}

	void SubtractedJewelEvent::project(HepMC::GenEvent *e)
	{
		clear();
		translateParticles(e);
		std::vector<MyDist> dists = buildPairs();
		doSubtraction(dists);
		collectResult();
		return;
	}

	void SubtractedJewelEvent::clear()
	{
		_subtrevent = std::vector<HepMC::GenParticle>();
		_myparticles.clear();
		_mythermals.clear();
	}

	HepMC::FourVector fMy4MomToHepMC4Vector(const My4Mom &v)
	{
		double px = v.pt * std::cos(v.phi);
		double py = v.pt * std::sin(v.phi);
		double pz = v.pt * std::sinh(v.y);
		double E = std::sqrt(v.pt * v.pt * std::cosh(v.y) * std::cosh(v.y) + v.mdelta * v.mdelta);
		return HepMC::FourVector(px, py, pz, E);
	};

	HepMC::FourVector fMyPartToHepMC4Vector(const MyPart &v)
	{
		double px = v.pt * std::cos(v.phi);
		double py = v.pt * std::sin(v.phi);
		double pz = v.pt * std::sinh(v.y);
		double E = std::sqrt(v.pt * v.pt * std::cosh(v.y) * std::cosh(v.y) + v.mdelta * v.mdelta);
		return HepMC::FourVector(px, py, pz, E);
	};

	double rapidity(const HepMC::FourVector &fourVec)
	{
		double E = fourVec.e();	  // Energy
		double pz = fourVec.pz(); // Longitudinal momentum component

		// Protect against division by zero and log of a negative number
		if (E == pz)
		{
			// Particle is moving at the speed of light along the beam axis.
			// Rapidity is infinite in this case.
			return std::numeric_limits<double>::infinity();
		}
		else if (E < pz)
		{
			// Unphysical, but to prevent taking the log of a negative number
			return std::numeric_limits<double>::quiet_NaN();
		}

		// Calculate rapidity
		return 0.5 * std::log((E + pz) / (E - pz));
	}

	void SubtractedJewelEvent::translateParticles(HepMC::GenEvent *e)
	{
		// translate Particle's and FourMomentum's into myPart's
		for (HepMC::GenEvent::particle_iterator piter = e->particles_begin();
			 piter != e->particles_end(); ++piter)
		{
			HepMC::GenParticle *p = *piter;
			if (p->end_vertex()) continue;

			if (p->status() == 1 || p->status() == 4)
			{
				HepMC::FourVector partmom = p->momentum();
				if (fuzzyEquals(partmom.e(), 1e-6))
					continue;
				if (partmom.e() - fabs(partmom.pz()) > 0.)
				{
					MyPart part;
					part.id = p->pdg_id();
					part.pt = partmom.perp();
					part.mdelta = std::sqrt(partmom.m2() + std::sqr(partmom.perp())) - partmom.perp();
					part.phi = partmom.phi();
					// part.y = partmom.rapidity();
					part.y = rapidity(partmom);
					_myparticles.push_back(part);
				}
				else
				{
					_subtrevent.push_back(*p);
				}
			}

			if (p->status() == 3)
			{
				HepMC::FourVector mom = p->momentum();
				My4Mom therm;
				if (mom.e() - fabs(mom.pz()) > 0.)
				{
					therm.pt = mom.perp();
					therm.mdelta = std::sqrt(mom.m2() + std::sqr(mom.perp())) - mom.perp();
					therm.phi = mom.phi();
					// therm.y = mom.rapidity();
					therm.y = rapidity(mom);
					_mythermals.push_back(therm);
				}
				else
				{
					int thermid;
					if (rand() / RAND_MAX < 1. / 3.)
						thermid = 211;
						// thermid = PID::PIPLUS;
					else if (rand() / RAND_MAX < 2. / 3.)
						thermid = -211;
						// thermid = PID::PIMINUS;
					else
						thermid = 111;
						// thermid = PID::PI0;

					// HepMC::GenParticle part(thermid, mom);
					HepMC::GenParticle part(mom, thermid, 1);
					_subtrevent.push_back(part);
				}
			}
		}
	}

	std::vector<MyDist> SubtractedJewelEvent::buildPairs()
	{
		// create list with all particle-ghosts distances and sort it
		std::vector<MyDist> dists;
		for (size_t i = 0; i < _myparticles.size(); ++i)
		{
			for (size_t j = 0; j < _mythermals.size(); ++j)
			{
				// cout<<"i, j = "<<i<<" "<<j<<endl;
				MyDist dist;
				double Deltaphi(abs(_myparticles[i].phi - _mythermals[j].phi));
				if (Deltaphi > M_PI)
					Deltaphi = 2. * M_PI - Deltaphi;
				dist.dR = std::sqrt(std::sqr(Deltaphi) + std::sqr(_myparticles[i].y - _mythermals[j].y));
				dist.ipart = i;
				dist.itherm = j;
				// cout<<"distance: "<<dist.dR<<endl;
				dists.push_back(dist);
			}
		}
		// dists.sort(MyDistComp);
		std::sort(dists.begin(), dists.end(), MyDistComp);
		return dists;
	}

	void SubtractedJewelEvent::doSubtraction(std::vector<MyDist> &dists)
	{
		// go through all particle-ghost pairs and re-distribute momentum and mass
		for (std::vector<MyDist>::iterator liter = dists.begin(); liter != dists.end(); ++liter)
		{
			// cout<<"dealing with dist "<<liter->dR<<endl;
			if (liter->dR > _dRmax)
				break;
			size_t pnum = liter->ipart;
			size_t tnum = liter->itherm;
			double ptp = _myparticles[pnum].pt;
			double ptt = _mythermals[tnum].pt;
			// cout<<"pts: "<<ptp<<" vs "<<ptg<<endl;
			if (ptp > ptt)
			{
				_myparticles[pnum].pt -= ptt;
				_mythermals[tnum].pt = 0.;
			}
			else
			{
				_mythermals[tnum].pt -= ptp;
				_myparticles[pnum].pt = 0.;
			}
			double mdp = _myparticles[pnum].mdelta;
			double mdt = _mythermals[tnum].mdelta;
			// cout<<"masses: "<<mdp<<" vs "<<mdg<<endl;
			if (mdp > mdt)
			{
				_myparticles[pnum].mdelta -= mdt;
				_mythermals[tnum].mdelta = 0.;
			}
			else
			{
				_mythermals[tnum].mdelta -= mdp;
				_myparticles[pnum].mdelta = 0.;
			}
		}
		return;
	}

	void SubtractedJewelEvent::collectResult()
	{
		// collect resulting 4-momenta to get subtracted event
		for (size_t i = 0; i < _myparticles.size(); ++i)
		{
			if (_myparticles[i].pt > 0.)
			{
				// HepMC::FourVector mom((_myparticles[i].pt + _myparticles[i].mdelta) * cosh(_myparticles[i].y),
				// 				 _myparticles[i].pt * cos(_myparticles[i].phi),
				// 				 _myparticles[i].pt * sin(_myparticles[i].phi),
				// 				 (_myparticles[i].pt + _myparticles[i].mdelta) * sinh(_myparticles[i].y));
				const HepMC::FourVector mom = fMyPartToHepMC4Vector(_myparticles[i]);
				HepMC::GenParticle outpart(mom, _myparticles[i].id, 1);
				_subtrevent.push_back(outpart);
			}
		}
		for (size_t i = 0; i < _mythermals.size(); ++i)
		{
			if (_mythermals[i].pt > 0.)
			{
				// HepMC::FourVector mom((_mythermals[i].pt + _mythermals[i].mdelta) * cosh(_mythermals[i].y),
				// 						_mythermals[i].pt * cos(_mythermals[i].phi),
				// 						_mythermals[i].pt * sin(_mythermals[i].phi),
				// 						(_mythermals[i].pt + _mythermals[i].mdelta) * sinh(_mythermals[i].y));
				const HepMC::FourVector mom = fMy4MomToHepMC4Vector(_mythermals[i]);
				int thermid = 0;
				if (rand() / RAND_MAX < 1. / 3.)
					thermid = 211;
					// thermid = PID::PIPLUS;
				else if (rand() / RAND_MAX < 2. / 3.)
					thermid = -211;
					// thermid = PID::PIMINUS;
				else
					thermid = 111;
				// thermid = PID::PI0;
				// HepMC::GenParticle outpart(thermid, mom);
				HepMC::GenParticle outpart(mom, thermid, 1);
				_subtrevent.push_back(outpart);
			}
		}
        return;
}

}
