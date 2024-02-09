#!/usr/bin/env python3


from __future__ import print_function
import tqdm
import argparse
import os
import numpy as np
import sys
import yasp
import cppyy
import pickle

import sys
#_heppyy_dir = os.path.join(os.path.dirname(__file__), '..')
#sys.path.append(_heppyy_dir)

import heppyy.util.fastjet_cppyy
import heppyy.util.pythia8_cppyy
import heppyy.util.heppyy_cppyy

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8
from cppyy.gbl.std import vector
# from cppyy.gbl import EnergyCorrelators

from heppyy.pythia_util import configuration as pyconf

import ROOT
import math
import array
import pandas as pd

def jet_to_dict(j):
	d = {}
	d['pt'] = j.perp()
	d['eta'] = j.eta()
	d['phi'] = j.phi()
	return d

def lund_split_to_dict(l, nsplit):
	d = {}
	d['nsplit'] = nsplit
	d['kt'] = l.kt()
	d['kappa'] = l.kappa()
	d['z'] = l.z()
	d['m'] = l.m()
	d['psi'] = l.psi()
	d['delta'] = l.Delta()    
	return d

# aa = 0
# ab = 1
# bb = 2
from itertools import combinations
# use the one below for auto corelations
# from itertools import combinations_with_replacement
def eec_pairs_from_parts(parts, w, ptcut=1.):
	d = {}
	_parts = [ p for p in parts if p.perp() > 1.]
	_combs = combinations(_parts)
	d['weights'] = [(x[0].perp() * x[1].perp())/(w*w) for x in _comb]
	d['RL'] = [x[0].delta_R(x[1]) for x in _combs]
	return d

def eec_from_lsplit_to_dict(l, w, pt_cut):
	d = {}
	_parts1 = [ p for p in l.harder().constituents() if p.perp() > 1.]
	_ = [ p.set_user_index(0) for p in _parts1]
	for p in _parts1:
		print(p.user_index())

	_parts2 = [ p for p in l.softer().constituents() if p.perp() > 1.]
	_ = [ p.set_user_index(1) for p in _parts2]
	for p in _parts2:
		print(p.user_index())

	_combs = combinations(_parts1, 2)
	d['weights'] = [(x[0].perp() * x[1].perp())/(w*w) for x in _combs]
	d['RL'] = [x[0].delta_R(x[1]) for x in _combs]
	d['type'] = [x[0].user_index() + x[1].user_index() for x in _combs]
	return d

def main():
	parser = argparse.ArgumentParser(description='pythia8 fastjet on the fly', prog=os.path.basename(__file__))
	pyconf.add_standard_pythia_args(parser)
	parser.add_argument('--ignore-mycfg', help="ignore some settings hardcoded here", default=False, action='store_true')
	parser.add_argument('-v', '--verbose', help="be verbose", default=False, action='store_true')
	parser.add_argument('--ncorrel', help='max n correlator', type=int, default=2)
	parser.add_argument('-o','--output', help='root output filename', default='eec_pythia.root', type=str)
	parser.add_argument('--jet-ptmin', help='minimum jet pt', default=20, type=float)
	parser.add_argument('--jet-ptmax', help='maximum jet pt', default=1e5, type=float)
	parser.add_argument('--jet-etamax', help='maximum jet eta', default=3.0, type=float)
	parser.add_argument('--use-lundpt', help="use lund radiator pt for scaling", default=False, action='store_true')
	parser.add_argument('--stable-beauty', help="set some hadrons stable", default=False, action='store_true')
	parser.add_argument('--ptcut', help="pt cut for particles for EEC", default=1.0, type=float)
	parser.add_argument('--stable-charm', help="set some hadrons stable", default=False, action='store_true')
	args = parser.parse_args()

	pt_cut = args.ptcut
	if pt_cut <= 0:
		pt_cut = 1.0
		print(f'[w] reverting ptcut for EECs to {pt_cut}')

	pythia = Pythia8.Pythia()

	# jet finder
	# print the banner first
	fj.ClusterSequence.print_banner()
	print()
	jet_R0 = 0.4
	hadron_etamax = args.jet_etamax + jet_R0 * 1.05
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	jet_selector = fj.SelectorPtMin(args.jet_ptmin)
	jet_selector = fj.SelectorPtMin(args.jet_ptmin) * fj.SelectorPtMax(args.jet_ptmax) * fj.SelectorAbsEtaMax(hadron_etamax - jet_R0 * 1.05)

	# from FJ contrib - not clear how to use this
	# eec = fj.contrib.EnergyCorrelator(2, 1) # default is measure pt_R
	# print(eec.description())

	jet_def_lund = fj.JetDefinition(fj.cambridge_algorithm, 1.0)
	lund_gen = fj.contrib.LundGenerator(jet_def_lund)
	print('making lund diagram for all jets...')
	print(f' {lund_gen.description()}')

	mycfg = ['PhaseSpace:pThatMin = {}'.format(args.jet_ptmin)]
	if args.ignore_mycfg:
		mycfg = []
	if args.stable_charm:
		for c in [411,413,421,423,431,433]:
			mycfg.append(f'{c}:mayDecay=false')
			mycfg.append(f'-{c}:mayDecay=false')
	if args.stable_beauty:
		for c in [511,513,521,523,531,533]:
			mycfg.append(f'{c}:mayDecay=false')
			mycfg.append(f'-{c}:mayDecay=false')
	pythia = pyconf.create_and_init_pythia_from_args(args, mycfg)
	if not pythia:
		print("[e] pythia initialization failed.")
		return
	if args.nev < 10:
		args.nev = 10
	jets = []
	jdicts = []
	for i in tqdm.tqdm(range(args.nev)):
		if not pythia.next():
			continue
		# parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal() and p.isCharged()])
		parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal()])
		# parts = pythiafjext.vectorize(pythia, True, -1, 1, False)
		jets = jet_selector(jet_def(parts))
		for j in jets:
			jdict = jet_to_dict(j)
			lunds = lund_gen.result(j)
			nsplits = len(lunds)
			ldicts = []
			for il, l in enumerate(lunds):
				ldict = lund_split_to_dict(l, il)
				# def eec_pairs_from_parts(parts, w, ptcut=1.):
				ldict['eecs'] = eec_from_lsplit_to_dict(l, j.perp(), pt_cut)
				# _parts = vector[fj.PseudoJet]()
				# _ = [_parts.push_back(p) for p in l.pair().constituents() if p.perp() > pt_cut]
				ldicts.append(ldict)
			jdict['lunds'] = ldicts
			jdicts.append(jdict)

	df = pd.DataFrame.from_dict(jdicts)
	# print(df)   
	df.to_parquet('eec_lund.parquet', compression='snappy')

	with open('eec_lund.pkl', 'wb') as file:
		pickle.dump(df, file)

	df.to_csv('eec_lund.csv', index=False)  # Set index=False to exclude the DataFrame index from the CSV file     

	pythia.stat()
	pythia.settings.writeFile('eec_lund.cmnd')

if __name__ == '__main__':
	main()
