#!/usr/bin/env python3


from __future__ import print_function
import tqdm
import argparse
import os
import numpy as np
import sys
import yasp
import cppyy

import sys
#_heppyy_dir = os.path.join(os.path.dirname(__file__), '..')
#sys.path.append(_heppyy_dir)

headers = [
    "fastjet/PseudoJet.hh",
    "fastjet/JetDefinition.hh",
    "fastjet/ClusterSequence.hh",
    "fastjet/Selector.hh",

    "fastjet/contrib/LundGenerator.hh",
    "fastjet/contrib/Recluster.hh",
    "fastjet/contrib/SoftDrop.hh",
    
	"fastjet/contrib/EnergyCorrelator.hh",
 
	"eec/ecorrel.hh",

    "Pythia8/Pythia.h",
    "Pythia8/Event.h"]

packs = ['fastjet', 'pythia8', 'heppyy']
libs = ['fastjet', 'pythia8', 'LundPlane', 'EnergyCorrelator', 'heppyy_eec']

from yasp.cppyyhelper import YaspCppyyHelper
ycppyy = YaspCppyyHelper().load(packs, libs, headers)
print(ycppyy)

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8
from cppyy.gbl.std import vector
from cppyy.gbl import EnergyCorrelators
print(sys.path)
from heppyy.pythia_util import configuration as pyconf

print(cppyy.gbl.__dict__)

import ROOT
import math
import array
import eech

def main():
	parser = argparse.ArgumentParser(description='pythia8 fastjet on the fly', prog=os.path.basename(__file__))
	pyconf.add_standard_pythia_args(parser)
	parser.add_argument('--ignore-mycfg', help="ignore some settings hardcoded here", default=False, action='store_true')
	parser.add_argument('-v', '--verbose', help="be verbose", default=False, action='store_true')
	parser.add_argument('--ncorrel', help='max n correlator', type=int, default=2)
	parser.add_argument('-o','--output', help='root output filename', default='eec_pythia.root', type=str)
	args = parser.parse_args()

	pythia = Pythia8.Pythia()

	# jet finder
	# print the banner first
	fj.ClusterSequence.print_banner()
	print()
	jet_R0 = 0.4
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	jet_selector = fj.SelectorPtMin(20.0)
	jet_selector = fj.SelectorPtMin(20.0) * fj.SelectorPtMax(500.0) * fj.SelectorAbsEtaMax(1 - jet_R0 * 1.05)

	# from FJ contrib - not clear how to use this
	# eec = fj.contrib.EnergyCorrelator(2, 1) # default is measure pt_R
	# print(eec.description())
 
	h = eech.EEChistograms(args=args)
	print(h)

	mycfg = ['PhaseSpace:pThatMin = 20']
	if args.ignore_mycfg:
		mycfg = []
	pythia = pyconf.create_and_init_pythia_from_args(args, mycfg)
	if not pythia:
		print("[e] pythia initialization failed.")
		return
	if args.nev < 10:
		args.nev = 10
	for i in tqdm.tqdm(range(args.nev)):
		if not pythia.next():
			continue
		parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal() and p.isCharged()])
		# parts = pythiafjext.vectorize(pythia, True, -1, 1, False)
		jets = jet_selector(jet_def(parts))
		for j in jets:
			h.fill_jet(j, j.constituents(), j.perp())


	pythia.stat()

	print(type(pythia))


if __name__ == '__main__':
	main()