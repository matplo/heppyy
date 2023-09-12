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

import heppyy.util.fastjet_cppyy
import heppyy.util.pythia8_cppyy
import heppyy.util.heppyy_cppyy

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8
from cppyy.gbl.std import vector
from cppyy.gbl import EnergyCorrelators

from heppyy.pythia_util import configuration as pyconf

import ROOT
import math
import array
import eech

import pickle

class RecursiveJetTree(object):
	def __init__(self, j):
		self.j = j
		self.tree = []
		for n in range(len(j.constituents()) + 2):
			self.tree.append([])
		self.fill_parents(j, 0)

	def fill_parents(self, sj, parent, lvl):
		self.tree[lvl].append([sj, parent])
		p1 = fj.PseudoJet()
		p2 = fj.PseudoJet()
		if sj.has_parents(p1, p2):
			self.fill_parents(p1, sj, lvl+1)
			self.fill_parents(p2, sj, lvl+1)

	def dump(self):
		print('[i] jet', self.j.perp(), 'with', len(self.j.constituents()), 'constituents', [p.perp() for p in self.j.constituents()])
		s = ' '
		for i,lvl in enumerate(self.tree):
			s = s + ' '
			for e in lvl:
				print(i, s, e[0].perp())

	def dump_arrays(self):
		nodes = {}
		nodes['points'] = []
		for c in self.j.constituents():
			nodes['points'].append((c.px(), c.py(), c.pz()))
			nodes['type'].append('blue')
		nodes['lines'] = {}
		nodes['lines']['x'] = []
		nodes['lines']['y'] = []
		nodes['lines']['z'] = []
		for i, lvl in enumerate(self.tree):
			for e in lvl:
				p = (e[0].px(), e[0].py(), e[0].pz())
				if i > 0:					
					nodes['lines']['x'].append([e[1].px(), e[0].px()])
				if e in self.j.constituents():
					continue
				nodes['points'].append(p)
				nodes['type'].append('red')

		print('', self.j.perp(), 'with', len(self.j.constituents()), 'constituents', [p.perp() for p in self.j.constituents()])
		s = ' '
		for i,lvl in enumerate(self.tree):
			s = s + ' '
			for e in lvl:
				print(i, s, e.perp())


import networkx as nx
class JetGraph(object):
	def __init__(self, j):
		self.j = j
		self.G = nx.Graph()
		self.n = 0
		self.max_depth = 0
		self.max_depth = self.get_max_depth(j, 0)
		self.add_sj(j, -1, self.max_depth)
  
	def get_max_depth(self, sj, depth):
		p1 = fj.PseudoJet()
		p2 = fj.PseudoJet()
		depth = depth + 1
		if sj.has_parents(p1, p2):
			_ = self.get_max_depth(p1, depth)
			_ = self.get_max_depth(p2, depth)
		if depth > self.max_depth:	
			self.max_depth = depth
		return self.max_depth
   
	def add_sj(self, sj, parent_n, depth):
		p1 = fj.PseudoJet()
		p2 = fj.PseudoJet()
		self.n = self.n + 1
		this_n = self.n
		dphi = self.j.delta_phi_to(sj)
		deta = self.j.eta() - sj.eta()
		# z = sj.perp()/self.j.perp()
		z = sj.perp()
		if sj.has_parents(p1, p2):
			# self.G.add_node(this_n, color='red', p=(sj.px(), sj.py(), sj.pz()))
			# self.G.add_node(this_n, color='red', p=(sj.phi(), sj.eta(), sj.perp()))
			self.G.add_node(this_n, color='green', p=(dphi, deta, z), symbol='square-open', size=15)
			if parent_n > 0:
				self.G.add_edge(this_n, parent_n, color='green')
			self.add_sj(p1, this_n, depth)
			self.add_sj(p2, this_n, depth)
		else:
			if sj.user_index() < 10000:
				self.G.add_node(this_n, color='blue', p=(dphi, deta, z), symbol='circle', size=15)
			else:
				self.G.add_node(this_n, color='red', p=(dphi, deta, z), symbol='circle', size=15)
			if parent_n > 0:
				self.G.add_edge(this_n, parent_n, color='green')

import random
def add_random_parts(j, bgmult=10):
    v = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in j.constituents()])
    max_pt = max([p.perp() for p in j.constituents()])
    max_deta = max([j.eta() - p.eta() for p in j.constituents()])
    max_dphi = max([j.delta_phi_to(p) for p in j.constituents()])
    for i in range(bgmult):
        _pt = random.uniform(0, max_pt / 3.)
        _eta = j.eta() + random.uniform(-1, 1.) * max_deta
        _phi = j.phi() + random.uniform(-1, 1.) * max_dphi
        psj = fj.PseudoJet()
        psj.reset_PtYPhiM(_pt, _eta, _phi, 0)
        psj.set_user_index(10000)
        v.push_back(psj)
    return v

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
	parser.add_argument('--stable-charm', help="set some hadrons stable", default=False, action='store_true')
	parser.add_argument('--stable-beauty', help="set some hadrons stable", default=False, action='store_true')
	args = parser.parse_args()

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
	jet_graphs_akt = []
	jet_graphs_ca = []
	jet_graphs_cabg = []
	for i in tqdm.tqdm(range(args.nev)):
		if not pythia.next():
			continue
		# parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal() and p.isCharged()])
		parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal()])
		# parts = pythiafjext.vectorize(pythia, True, -1, 1, False)
		jets = fj.sorted_by_pt(jet_selector(jet_def(parts)))
		for j in jets:
			jg = JetGraph(j)
			jet_graphs_akt.append(jg.G)
			jca = jet_def_lund(j.constituents())[0]
			jgca = JetGraph(jca)
			jet_graphs_ca.append(jgca.G)

			_v = add_random_parts(j, 20)
			jcabg = jet_def_lund(_v)[0]
			jgcabg = JetGraph(jcabg)
			jet_graphs_cabg.append(jgcabg.G)

	pythia.stat()

	with open('graphs_akt.pkl', 'wb') as f:
		pickle.dump(jet_graphs_akt, f)

	with open('graphs_ca.pkl', 'wb') as f:
		pickle.dump(jet_graphs_ca, f)

	with open('graphs_cabg.pkl', 'wb') as f:
		pickle.dump(jet_graphs_cabg, f)


if __name__ == '__main__':
	main()
