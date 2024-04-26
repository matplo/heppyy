#ifndef HEPPYY_NegaRecombinerHYBRID_HH
#define HEPPYY_NegaRecombinerHYBRID_HH

#include <vector>
#include <list>
#include <fstream>
#include <string>

#include <fastjet/JetDefinition.hh>

namespace heppyy
{

  typedef fastjet::JetDefinition::Recombiner Recombiner;

  /// from Dani Pablos
  /// Recombiner class that propagates the user index and arranges the
  /// recombination accordingly

  class NegativeEnergyRecombiner : public Recombiner
  {
  public:
    NegativeEnergyRecombiner(const int ui);
    virtual std::string description() const;
    /// recombine pa and pb and put result into pab
    virtual void recombine(const fastjet::PseudoJet &pa,
                           const fastjet::PseudoJet &pb,
                           fastjet::PseudoJet &pab) const;
  private:
    const int _ui;
  };
};

#endif