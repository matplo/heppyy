import yasp
import cppyy

headers = [
	"eec/ecorrel.hh"
 ]
packs = ['heppyy']
libs = ['heppyy_eec']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())

