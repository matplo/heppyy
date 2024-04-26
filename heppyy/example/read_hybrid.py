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
	parser.add_argument('-w', '--wake', help='include wake particles', action='store_true', default=False)
	parser.add_argument('-v', '--verbose', help="be verbose", default=False, action='store_true')
	args = parser.parse_args()
 
	fj.ClusterSequence.print_banner()
	print()

	# use the energy recombiner
	ner = heppyy.NegativeEnergyRecombiner(1001)
	print(ner.description())

	# set up our jet definition and a jet selector
	jet_R0 = 0.4
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	if args.wake:
		jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0, ner)
	jet_selector = fj.SelectorPtMin(100.0) * fj.SelectorAbsEtaMax(1)
	# jet_selector = fj.SelectorPtMin(300.0) * fj.SelectorAbsEtaMax(1.)
	print(jet_def)

	# jet_def_lund = fj.JetDefinition(fj.cambridge_algorithm, 1.0)
	# lund_gen = fj.contrib.LundGenerator(jet_def_lund)
	# print('making lund diagram for all jets...')
	# print(f' {lund_gen.description()}')
 
	input = heppyy.HybridFile(args.input)

	if args.nev < 10:
		args.nev = 10
	for i in tqdm.tqdm(range(args.nev)):
		if not input.nextEvent():
			break
		parts = input.getParticles(include_wake=args.wake)
		partons = input.getPartons()
		sparts = input.getParticlesStr()
		spartons = input.getPartonsStr()
		ev_info = input.info()
		print(f'ev_info.weight: {ev_info.weight()}, ev_info.cross: {ev_info.cross()}, ev_info.x: {ev_info.x()}, ev_info.y: {ev_info.y()}')
		if args.verbose:
			print(f'event {i} has {len(partons)} partons')
			for np in range(len(partons)):
				print(f'- from psj: px={partons[np].px()}, py={partons[np].py()}, pz={partons[np].pz()}, E={partons[np].E()}, m={partons[np].m()}, ui={partons[np].user_index()}')
				print(f'- from str: {spartons[np]}')
			print(f'event {i} has {len(parts)} particles')
			for np in range(len(parts)):
				print(f'- from psj: px={parts[np].px()}, py={parts[np].py()}, pz={parts[np].pz()}, E={parts[np].E()}, m={parts[np].m()}, ui={parts[np].user_index()}')
				print(f'- from str: {sparts[np]}')
		jets = fj.sorted_by_pt(jet_selector(jet_def(parts)))
		if len(jets) == 0:
			continue

		# match partons to jets
		print(f'number of accepted jets: {len(jets)}')
		for j in jets:
			print(f'jet pt: {j.pt()} eta: {j.eta()}')
			for np in range(len(partons)):
				p = partons[np]
				if j.delta_R(p) < 0.4:
					print(f' - matched parton {np} with pt: {p.perp()} eta: {p.eta()}')

if __name__ == '__main__':
	main()
