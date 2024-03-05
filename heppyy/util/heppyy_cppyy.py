import yasp
import cppyy

headers = [
	"eec/ecorrel.hh",
	"fjutil/fjutil.hh",
	"fjext/fjtools.hh",
	"groom/GroomerShop.hh"
 ]
packs = ['heppyy']
libs = ['heppyy_eec', 'heppyy_fjutil', 'heppyy_fjext', 'heppyy_groom']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())

