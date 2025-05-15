import yasp
import cppyy

headers = [
	"eec/ecorrel.hh",
	"fjutil/fjutil.hh",
	"fjext/fjtools.hh",
	"groom/GroomerShop.hh",
	"pythiaext/PythiaExt.hh",
	"pythiafjext/pyfjtools.hh",
	"hybridutil/readhybrid.hh",
	"hybridutil/hybridNegaRecombiner.hh"
 ]
packs = ['heppyy']
libs = ['heppyy_eec', 'heppyy_fjutil', 'heppyy_fjext', 'heppyy_groom', 'heppyy_pythiafjext', 'heppyy_pythiaext', 'heppyy_hybridutil']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
if yasp.debug:
	print('[heppyy-i] cppyy loaded packages:', YaspCppyyHelper().loaded_packages)
	print('[heppyy-i] cppyy loaded libs:', YaspCppyyHelper().loaded_libs)
	print(YaspCppyyHelper())

