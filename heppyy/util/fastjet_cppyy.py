import yasp
import cppyy

headers = [
    "fastjet/PseudoJet.hh",
    "fastjet/JetDefinition.hh",
    "fastjet/ClusterSequence.hh",
    "fastjet/ClusterSequenceArea.hh",
    "fastjet/ClusterSequenceActiveArea.hh",
    "fastjet/Selector.hh",
    "fastjet/AreaDefinition.hh",
    "fastjet/GhostedAreaSpec.hh",
    "fastjet/tools/GridMedianBackgroundEstimator.hh",

    "fastjet/contrib/LundGenerator.hh",
    "fastjet/contrib/Recluster.hh",
    "fastjet/contrib/SoftDrop.hh",

    "fastjet/contrib/ConstituentSubtractor.hh",
    "fastjet/contrib/IterativeConstituentSubtractor.hh",
    
	"fastjet/contrib/EnergyCorrelator.hh"
 ]

packs = ['fastjet']
libs = ['fastjet', 'LundPlane', 'EnergyCorrelator', 'ConstituentSubtractor']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())
