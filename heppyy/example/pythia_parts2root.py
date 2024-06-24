#!/usr/bin/env python3

from __future__ import print_function
import tqdm
import argparse
import os
import numpy as np
import sys
import yasp
import cppyy

#import heppyy.util.fastjet_cppyy
import heppyy.util.pythia8_cppyy
import heppyy.util.heppyy_cppyy

#from cppyy.gbl import fastjet as fj
from cppyy.gbl import Pythia8
from cppyy.gbl.std import vector

# from cppyy.gbl import pythiaext

from heppyy.pythia_util import configuration as pyconf

import ROOT

print(cppyy.gbl.__dict__)

def main():
	parser = argparse.ArgumentParser(description='pythia8 fastjet on the fly', prog=os.path.basename(__file__))
	pyconf.add_standard_pythia_args(parser)
	parser.add_argument('--ignore-mycfg', help="ignore some settings hardcoded here", default=False, action='store_true')
	parser.add_argument('--output', help="output file", default="pythia_parts.root")
	parser.add_argument('-v', '--verbose', help="be verbose", default=False, action='store_true')
	args = parser.parse_args()

	rfile = ROOT.TFile(args.output, "RECREATE")
	rfile.cd()
	tn = ROOT.TNtuple("parts", "parts", "pt:eta:y:phi:mass:pdg:charge:xsec:weight:process:nev")
	tn_ev = ROOT.TNtuple("event", "event", "xsec:weight:process:nev")
	pythia = Pythia8.Pythia()

	mycfg = ['']
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
		_info = Pythia8.getInfo(pythia)
		proc_number = _info.code()
		sigmaGen = _info.sigmaGen()
		weight = _info.weight()
		_ = [tn.Fill(p.pT(), p.eta(), p.y(), p.phi(), p.m0(), p.id(), p.charge(), sigmaGen, weight, proc_number, i) for p in pythia.event if p.isFinal()]
		tn_ev.Fill(sigmaGen, weight, proc_number, i)
		

	pythia.stat()

	print(type(pythia))
	# nev = _info.nAccepted()
	# ntrials = _info.nTried()

	rfile.Write()

if __name__ == '__main__':
	main()
