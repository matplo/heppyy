#!/usr/bin/env python3

from __future__ import print_function
import tqdm
import argparse
import os
import numpy as np
import sys
import yasp
import cppyy


import heppyy.util.fastjet_cppyy
import heppyy.util.pythia8_cppyy
import heppyy.util.heppyy_cppyy

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8
from cppyy.gbl.std import vector

# from cppyy.gbl import pythiaext

from heppyy.pythia_util import configuration as pyconf

import ROOT
import math
import array
import eech

def logbins(xmin, xmax, nbins):
        lspace = np.logspace(np.log10(xmin), np.log10(xmax), nbins+1)
        arr = array.array('f', lspace)
        return arr


def find_jets_pythia(jet_def, jet_selector, pythia):
	fjparts = []
	fjparts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal()])
	fjparts = vector[fj.PseudoJet](fjparts)
	print('- number of particles in the event:', fjparts.size())
	print('  leading particle pT:', fj.sorted_by_pt(fjparts)[0].perp())
	jets = jet_selector(jet_def(fjparts))
	return jets


def main():
	parser = argparse.ArgumentParser(description='read hepmc and analyze eecs', prog=os.path.basename(__file__))
	pyconf.add_standard_pythia_args(parser)
	parser.add_argument('--ncorrel', help='max n correlator', type=int, default=2)
	parser.add_argument('-o','--output', help='root output filename', default='eec_pythia8.root', type=str)
	args = parser.parse_args()	

	if args.output == 'eec_pythia8.root':
		if args.py_vincia:
			args.output = args.output.replace('.root', '_vincia.root')
		if args.py_dire:
			args.output = args.output.replace('.root', '_dire.root')
		print("[w] using [modified] default output file:", args.output)
	else:
		print("[w] using specified output file:", args.output)

	pythia = Pythia8.Pythia()

	# jet finder
	# print the banner first
	fj.ClusterSequence.print_banner()
	print()
	jet_R0 = 0.4
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	jet_selector = fj.SelectorPtMin(args.py_pthatmin)
	jet_selector = fj.SelectorPtMin(args.py_pthatmin) * fj.SelectorPtMax(args.py_pthatmin+20) * fj.SelectorAbsEtaMax(1 - jet_R0 * 1.05)
 
	h = eech.EEChistograms(args=args)
	print(h)

	mycfg = []
	pythia = pyconf.create_and_init_pythia_from_args(args, mycfg)
	if not pythia:
		print("[e] pythia initialization failed.")
		return

	_stop = False 
	pbar = tqdm.tqdm(range(args.nev))
	njets = 0
	while not _stop:
		if not pythia.next():
			continue
		fjparts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal() and p.isCharged()])
		# jets = fj.sorted_by_pt(jet_def(fjparts))
		jets = fj.sorted_by_pt(jet_selector(jet_def(fjparts)))
		njets += len(jets)
		# _info = Pythia8.pythia.info
		_info = Pythia8.getInfo(pythia)
		sigmaGen = _info.sigmaGen()
		ev_weight = _info.weight()
		if jets.size() > 0:
			for j in jets:
				h.fill_jet(j, j.constituents(), j.perp(), sigmaGen=sigmaGen, weight=ev_weight)
		else:
			continue
		pbar.update(jets.size())
		if pbar.n >= args.nev:
			_stop = True

	print('[i] number of jets:', njets)

if __name__ == '__main__':
	main()
