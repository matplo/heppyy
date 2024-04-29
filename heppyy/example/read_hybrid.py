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

# print(cppyy.gbl.__dict__)
from heppyy.util.logger import Logger

def main():
	parser = argparse.ArgumentParser(description='analyze hybrid with fastjet on the fly', prog=os.path.basename(__file__))
	parser.add_argument('-i', '--input', help='input file', default='', required=True)
	parser.add_argument('-n', '--nev', help='number of events', default=10, type=int)
	parser.add_argument('-w', '--wake', help='include wake particles', action='store_true', default=False)
	parser.add_argument('-v', '--verbose', help="be verbose", default=False, action='store_true')
	parser.add_argument('--jet-min-pt', help="minimum pT jet to accept", default=5., type=float)	
	parser.add_argument('--max-eta-jet', help="max eta of a jet to accept", default=2.5, type=float)	
	parser.add_argument('--jet-R', help="jet R", default=0.4, type=float)	
	parser.add_argument('-g', '--debug', help="write debug things", default=False, action='store_true')
	args = parser.parse_args()

	# set up logging - this uses singleton Logger
	log_level = 'DEBUG' if args.debug else 'WARNING'
	log = Logger(console=args.verbose, level=log_level)
	if args.verbose:
		log.set_level('INFO')
	if args.debug:
		log.set_level('DEBUG')
  
	log.critical(args)
  
	fj.ClusterSequence.print_banner()
	print()

	# use the energy recombiner
	ner = heppyy.NegativeEnergyRecombiner(1001)
	log.critical(ner.description())

	# set up our jet definition and a jet selector
	jet_R0 = args.jet_R
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	if args.wake:
		jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0, ner)
	jet_selector = fj.SelectorPtMin(args.jet_min_pt) * fj.SelectorAbsEtaMax(args.max_eta_jet)
	log.critical(jet_def.description())

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

		jets = fj.sorted_by_pt(jet_selector(jet_def(parts)))
		if len(jets) == 0:
			continue

		log.info(f'* event {i} has {len(partons)} partons')
		log.info(f'  ev_info.weight: {ev_info.weight()}, ev_info.cross: {ev_info.cross()}, ev_info.x: {ev_info.x()}, ev_info.y: {ev_info.y()}')
		for np in range(len(partons)):
			log.info(f'  parton pt: {partons[np].pt()} eta: {partons[np].eta()}')
			log.debug(f'- from psj: px={partons[np].px()}, py={partons[np].py()}, pz={partons[np].pz()}, E={partons[np].E()}, m={partons[np].m()}, ui={partons[np].user_index()}')
			log.debug(f'- from str: {spartons[np]}')
		log.debug(f'event {i} has {len(parts)} particles')
		for np in range(len(parts)):
			log.debug(f'- from psj: px={parts[np].px()}, py={parts[np].py()}, pz={parts[np].pz()}, E={parts[np].E()}, m={parts[np].m()}, ui={parts[np].user_index()}')
			log.debug(f'- from str: {sparts[np]}')

		log.info(f'-> event {i} has {len(jets)} jets')
		for j in jets:
			log.info(f'   - jet pt: {j.pt()} eta: {j.eta()}')
   
		log.disable_console()
		log.info('debugging... - this should not write to console but show up in the log file')
		log.enable_console()

		# match partons to jets
		for j in jets:
			log.debug(f'jet pt: {j.pt()} eta: {j.eta()}')
			for np in range(len(partons)):
				p = partons[np]
				if j.delta_R(p) < 0.4:
					log.debug(f' - matched parton {np} with pt: {p.perp()} eta: {p.eta()}')

if __name__ == '__main__':
	main()
