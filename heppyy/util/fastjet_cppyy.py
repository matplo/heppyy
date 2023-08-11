import yasp
import cppyy

headers = [
    "fastjet/PseudoJet.hh",
    "fastjet/JetDefinition.hh",
    "fastjet/ClusterSequence.hh",
    "fastjet/Selector.hh",

    "fastjet/contrib/LundGenerator.hh",
    "fastjet/contrib/Recluster.hh",
    "fastjet/contrib/SoftDrop.hh",
    
	"fastjet/contrib/EnergyCorrelator.hh"
 ]

packs = ['fastjet']
libs = ['fastjet', 'LundPlane', 'EnergyCorrelator']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())
