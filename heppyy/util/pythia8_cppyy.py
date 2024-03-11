import yasp
import cppyy

headers = [
    "Pythia8/Pythia.h",
]

packs = ['pythia8']
libs = ['pythia8']

from yasp.cppyyhelper import YaspCppyyHelper
YaspCppyyHelper().load(packs, libs, headers)
print(YaspCppyyHelper())
