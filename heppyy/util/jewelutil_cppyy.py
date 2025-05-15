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
if yasp.debug:
	print('[heppyy-i] cppyy loaded packages:', YaspCppyyHelper().loaded_packages)
	print('[heppyy-i] cppyy loaded libs:', YaspCppyyHelper().loaded_libs)
	print(YaspCppyyHelper())

