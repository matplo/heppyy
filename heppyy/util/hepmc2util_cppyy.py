import yasp
import cppyy

headers = [
	"hepmc2util/readfile.hh",
	"hepmc2util/statfile.hh"
 ]
packs = ['heppyy', 'HepMC2/2.06.11']
libs = ['heppyy_hepmc2util', 'HepMC']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())

