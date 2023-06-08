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

import pyhepmc
import particle
import ROOT
import math
import array
import eech

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
	parser = argparse.ArgumentParser(description='read hepmc and analyze eecs', prog=os.path.basename(__file__))
	parser.add_argument('-i', '--input', help='input file', default='low', type=str, required=True)
	parser.add_argument('--hepmc', help='what format 2 or 3', default=2, type=int)
	parser.add_argument('--nev', help='number of events', default=10, type=int)
	parser.add_argument('--ncorrel', help='max n correlator', type=int, default=2)
	parser.add_argument('-o','--output', help='root output filename', default='eec.root', type=str)
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
	jet_selector = fj.SelectorPtMin(20.0) * fj.SelectorPtMax(500.0) * fj.SelectorAbsEtaMax(1 - jet_R0 * 1.05)

	# from FJ contrib - not clear how to use this
	# eec = fj.contrib.EnergyCorrelator(2, 1) # default is measure pt_R
	# print(eec.description())
 
	h = eech.EEChistograms(args=args)
	print(h)
 
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
				if particle.Particle.from_pdgid(p.pid).charge == 0:
					continue
				psj = fj.PseudoJet(p.momentum.px, p.momentum.py, p.momentum.pz, p.momentum.e)
				psj.set_user_index(i)
				fjparts.push_back(psj)

		# print('- number of particles in the event:', fjparts.size())
		# print('  leading particle pT:', fj.sorted_by_pt(fjparts)[0].perp())
		jets = jet_selector(jet_def(fjparts))

		njets += len(jets)
		if jets.size() > 0:
			# print('[i] found jets...', len(jets))
			for j in jets:
				# _reec = eec.result(j) #this is from FJ.contrib
				# print ('- jet pT={0:5.2f} eta={1:5.2f} eec={2:5.2f}'.format(j.perp(), j.eta(), _reec))
				# myeec = EnergyCorrelators.CorrelatorBuilder(j.constituents(), j.perp(), 2)
				# print(myeec.correlator(2).rs())
				h.fill_jet(j, j.constituents(), j.perp())

		pbar.update()
		if pbar.n >= args.nev:
			break

	print('[i] number of jets:', njets)

if __name__ == '__main__':
	main()
