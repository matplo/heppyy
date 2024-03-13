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

import heppyy.util.fastjet_cppyy
import heppyy.util.heppyy_cppyy

from cppyy.gbl import fastjet as fj
from cppyy.gbl.std import vector

from cppyy.gbl import heppyy

print(cppyy.gbl.__dict__)

def main():
	parser = argparse.ArgumentParser(description='analyze hybrid with fastjet on the fly', prog=os.path.basename(__file__))
	parser.add_argument('-i', '--input', help='input file', default='', required=True)
	parser.add_argument('-n', '--nev', help='number of events', default=10, type=int)
	parser.add_argument('-v', '--verbose', help="be verbose", default=False, action='store_true')
	args = parser.parse_args()
 
	fj.ClusterSequence.print_banner()
	print()
	# set up our jet definition and a jet selector
	jet_R0 = 0.4
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	# jet_selector = fj.SelectorPtMin(100.0) * fj.SelectorAbsEtaMax(1)
	jet_selector = fj.SelectorPtMin(300.0) * fj.SelectorAbsEtaMax(1.)
	print(jet_def)

	jet_def_lund = fj.JetDefinition(fj.cambridge_algorithm, 1.0)
	lund_gen = fj.contrib.LundGenerator(jet_def_lund)
	print('making lund diagram for all jets...')
	print(f' {lund_gen.description()}')
 
	input = heppyy.HybridFile(args.input)

	if args.nev < 10:
		args.nev = 10
	for i in tqdm.tqdm(range(args.nev)):
		if not input.nextEvent():
			break
		parts = input.getPseudoJets()
		sparts = input.getParticlesStr()
		spartons = input.getPartonsStr()
		if args.verbose:
			print(f'event {i} has {len(parts)} particles')
			print(f'- from psj: px={parts[0].px()}, py={parts[0].py()}, pz={parts[0].pz()}, E={parts[0].E()}')
			print(f'- from str: {sparts[0]}')
		jets = fj.sorted_by_pt(jet_selector(jet_def(parts)))
		if len(jets) == 0:
			continue
		print(f'number of accepted jets: {len(jets)} - leading jet pt: {jets[0].pt()} eta: {jets[0].eta()}')
		print(f' - parton 0: {spartons[0]}')
		print(f' - parton 1: {spartons[1]}')
		for j in jets:
			lunds = lund_gen.result(j)

if __name__ == '__main__':
	main()
