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

    "Pythia8/Pythia.h",
    "Pythia8/Event.h"]

packs = ['fastjet', 'pythia8']
libs = ['fastjet', 'pythia8', 'LundPlane']

from yasp.cppyyhelper import YaspCppyyHelper
ycppyy = YaspCppyyHelper().load(packs, libs, headers)
print(ycppyy)

from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8
from cppyy.gbl.std import vector

print(sys.path)
from heppyy.pythia_util import configuration as pyconf

print(cppyy.gbl.__dict__)

import pyhepmc
import ROOT
import math
import array

def logbins(xmin, xmax, nbins):
        lspace = np.logspace(np.log10(xmin), np.log10(xmax), nbins+1)
        arr = array.array('f', lspace)
        return arr


def find_jets_hepmc(jet_def, jet_selector, hepmc_event):
	fjparts = []
	# parts = vector[fj.PseudoJet]([fj.PseudoJet(p.px(), p.py(), p.pz(), p.e()) for p in pythia.event if p.isFinal()])
	for i,p in enumerate(hepmc_event.particles):
		if p.status == 1 and not p.end_vertex:
			psj = fj.PseudoJet(p.momentum.px, p.momentum.py, p.momentum.pz, p.momentum.e)
			# psj.set_user_index(i)
			fjparts.append(psj)
	fjparts = vector[fj.PseudoJet](fjparts)
	print('- number of particles in the event:', fjparts.size())
	print('  leading particle pT:', fj.sorted_by_pt(fjparts)[0].perp())
	jets = jet_selector(jet_def(fjparts))
	return jets


def main():
	parser = argparse.ArgumentParser(description='pythia8 in python', prog=os.path.basename(__file__))
	parser.add_argument('-i', '--input', help='input file', default='low', type=str, required=True)
	parser.add_argument('--hepmc', help='what format 2 or 3', default=2, type=int)
	parser.add_argument('--nev', help='number of events', default=10, type=int)
	args = parser.parse_args()	

	###
	# now lets read the HEPMC file and do some jet finding
	if args.hepmc == 3:
		input_hepmc = pyhepmc.io.ReaderAscii(args.input)
	if args.hepmc == 2:
		input_hepmc = pyhepmc.io.ReaderAsciiHepMC2(args.input)

	if input_hepmc.failed():
		print ("[error] unable to read from {}".format(args.input))
		sys.exit(1)

	# jet finder
	# print the banner first
	fj.ClusterSequence.print_banner()
	print()
	jet_R0 = 0.4
	jet_def = fj.JetDefinition(fj.antikt_algorithm, jet_R0)
	jet_selector = fj.SelectorPtMin(20.0)
	jet_selector = fj.SelectorPtMin(20.0) * fj.SelectorPtMax(500.0) * fj.SelectorAbsEtaMax(2)

	event_hepmc = pyhepmc.GenEvent()
	pbar = tqdm.tqdm(range(args.nev))
	njets = 0
	while not input_hepmc.failed():
		ev = input_hepmc.read_event(event_hepmc)
		if input_hepmc.failed():
			break
		fjparts = vector[fj.PseudoJet]()
		for i,p in enumerate(event_hepmc.particles):
			if p.status == 1 and not p.end_vertex:
				psj = fj.PseudoJet(p.momentum.px, p.momentum.py, p.momentum.pz, p.momentum.e)
				psj.set_user_index(i)
				fjparts.push_back(psj)

		print('- number of particles in the event:', fjparts.size())
		print('  leading particle pT:', fj.sorted_by_pt(fjparts)[0].perp())
		jets = jet_selector(jet_def(fjparts))

		njets += len(jets)
		if jets.size() > 0:
			print('[i] found jets...', len(jets))
			for j in jets:
				print ('- jet pT={0:5.2f} eta={1:5.2f}'.format(j.perp(), j.eta()))

		pbar.update()
		if pbar.n >= args.nev:
			break

	print('[i] number of jets:', njets)

if __name__ == '__main__':
	main()
