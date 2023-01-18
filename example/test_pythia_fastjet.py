#!/usr/bin/env python3

from __future__ import print_function
import cppyy

import tqdm
import argparse
import os
import numpy as np

prefix = os.path.expandvars('$HOME/softbuild')
cppyy.add_include_path(f"{prefix}/include")
cppyy.add_library_path(f"{prefix}/lib")

files = [
    "fastjet/PseudoJet.hh",
    "fastjet/JetDefinition.hh",
    "fastjet/ClusterSequence.hh",
    "fastjet/Selector.hh",

    "fastjet/contrib/LundGenerator.hh",

    "Pythia8/Pythia.h",
    "Pythia8/Event.h"]

for fn in files:
    cppyy.include(fn)

cppyy.load_library("fastjet")
cppyy.load_library("pythia8")
cppyy.load_library("LundPlane")

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8

import sys
_heppyy_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(_heppyy_dir)
from util import configuration as pyconf

from cppyy.gbl.std import vector

def main():
	parser = argparse.ArgumentParser(description='pythia8 fastjet on the fly', prog=os.path.basename(__file__))
	pyconf.add_standard_pythia_args(parser)
	parser.add_argument('--ignore-mycfg', help="ignore some settings hardcoded here", default=False, action='store_true')
	args = parser.parse_args()
 
	pythia = Pythia8.Pythia()

	fj.ClusterSequence.print_banner()
	print()
	# set up our jet definition and a jet selector
	jet_R0 = 0.4
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	jet_selector = fj.SelectorPtMin(100.0) * fj.SelectorAbsEtaMax(1)
	print(jet_def)

	jet_def_lund = fj.JetDefinition(fj.cambridge_algorithm, 1.0)
	lund_gen = fj.contrib.LundGenerator(jet_def_lund)
	print('making lund diagram for all jets...')
	print(f' {lund_gen.description()}')

	mycfg = ['PhaseSpace:pThatMin = 100']
	if args.ignore_mycfg:
		mycfg = []
	pythia = pyconf.create_and_init_pythia_from_args(args, mycfg)
	if not pythia:
		print("[e] pythia initialization failed.")
		return
	if args.nev < 100:
		args.nev = 100
	for i in tqdm.tqdm(range(args.nev)):
		if not pythia.next():
			continue
		parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal()])
		# parts = pythiafjext.vectorize(pythia, True, -1, 1, False)
		jets = jet_selector(jet_def(parts))
		for j in jets:
			lunds = lund_gen.result(j)
			print(f'jet pT={j.perp()}')
			for i, l in enumerate(lunds):
				print('- L {} pT={:5.2f} eta={:5.2f}'.format(i, l.pair().perp(), l.pair().eta()))
				print('  Deltas={}'.format(l.Delta()))
				print('  kts={}'.format(l.kt()))
				print()


	pythia.stat()

	print(type(pythia))


if __name__ == '__main__':
	main()
