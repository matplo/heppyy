import yasp
import cppyy

headers = [
	"eec/ecorrel.hh",
	"fjutil/fjutil.hh"
 ]
packs = ['heppyy']
libs = ['heppyy_eec', 'heppyy_fjutil']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())

