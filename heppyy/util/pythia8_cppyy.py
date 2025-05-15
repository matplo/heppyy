import yasp
import cppyy

headers = [
    "Pythia8/Pythia.h",
]

packs = ['pythia8']
libs = ['pythia8']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
if yasp.debug:
	print('[heppyy-i] cppyy loaded packages:', YaspCppyyHelper().loaded_packages)
	print('[heppyy-i] cppyy loaded libs:', YaspCppyyHelper().loaded_libs)
	print(YaspCppyyHelper())
