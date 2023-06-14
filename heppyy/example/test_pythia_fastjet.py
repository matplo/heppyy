#!/usr/bin/env python3

from __future__ import print_function
import cppyy

import tqdm
import argparse
import os
import numpy as np
import sys
import yasp

def cppyy_add_include_paths_files(files=[], *packages):
	dirs = yasp.yasp_find_files_dirnames_in_packages(files, packages)
	for d in dirs:	
		print(f'[i] adding include path {d}')
		cppyy.add_include_path(f"{d}")

def cppyy_add_paths(*packages):
	for pfix in yasp.features('prefix', *packages):
		_include_path = os.path.join(pfix, 'include')
		_lib_path = os.path.join(pfix, 'lib')
		_lib64_path = os.path.join(pfix, 'lib')
		if os.path.isdir(_include_path):
			cppyy.add_include_path(_include_path)
		if os.path.isdir(_lib_path):
			cppyy.add_library_path(_lib_path)
		if os.path.isdir(_lib64_path):
			cppyy.add_library_path(_lib64_path)
 
files = [
    "fastjet/PseudoJet.hh",
    "fastjet/JetDefinition.hh",
    "fastjet/ClusterSequence.hh",
    "fastjet/Selector.hh",

    "fastjet/contrib/LundGenerator.hh",

    "Pythia8/Pythia.h",
    "Pythia8/Event.h"]

cppyy_add_paths('fastjet', 'pythia8')

cppyy.load_library("fastjet")
cppyy.load_library("pythia8")
cppyy.load_library("LundPlane")

for fn in files:
    cppyy.include(fn)

print(cppyy.gbl.__dict__)

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8

print(cppyy.gbl.__dict__)

import sys
_heppyy_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(_heppyy_dir)
from heppyy.pythia_util import configuration as pyconf

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
	if args.nev < 10:
		args.nev = 10
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
