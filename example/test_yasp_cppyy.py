#!/usr/bin/env python3

from yasp.cppyyhelper import YaspCppyyHelper

import cppyy

yy = YaspCppyyHelper()
yy.load(['fastjet'], ['fastjet'], ['fastjet/ClusterSequence.hh'])
yy.load(['pythia8'], ['pythia8'], ['Pythia8/Pythia.h'])

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8

yx = YaspCppyyHelper()

print(yy)
print(yx)

print(cppyy.gbl.__dict__)


print(cppyy.gbl.__dict__)

fj.ClusterSequence.print_banner()
_ = Pythia8.Pythia()