import yasp
import cppyy

import heppyy.util.fastjet_cppyy
import heppyy.util.hepmc2util_cppyy

headers = [
	"jewelutil/readjewel.hh"
 ]
packs = ['heppyy']
libs = ['heppyy_jewelutil']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())

