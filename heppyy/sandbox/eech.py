import yasp
import ROOT
import numpy as np
import array


import heppyy.util.fastjet_cppyy
import heppyy.util.heppyy_cppyy

from cppyy.gbl import fastjet as fj
from cppyy.gbl.std import vector
from cppyy.gbl import EnergyCorrelators

from heppyy.util.mputils import logbins

class EEChistograms(yasp.GenericObject):
	def __init__(self, **kwargs):
		super(EEChistograms, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug
		if self.output_fname:
			self.output = self.output_fname
		self.fout = ROOT.TFile(self.output, 'recreate')
		print('[i] will write to', self.fout.GetName())
		self.fout.cd()

		self.histograms = {}
		self.tn = ROOT.TNtuple('tn', 'tneec', 'n:ptpartcut:RL:w:jetpt:sigmaGen:weight')
		self.tnjet = ROOT.TNtuple('tnjet', 'tnjet', 'pt:eta:phi:nc:sigmaGen:weight')
		self.tnjetFF = ROOT.TNtuple('tnjetFF', 'tnjetFF', 'pt:eta:phi:nc:z:zphi:zeta:ptcut:sigmaGen:weight')
		self.nbins = int(18.)
		self.lbins = logbins(1.e-3, 1., self.nbins)

		if self.ncorrel < 2:
			self.ncorrel = 2
		if self.ncorrel > 5:
			self.ncorrel = 5
		print('[i] n correl up to', self.ncorrel)

	# these are the eec histograms
	# ptcut is the pt cut on particles
	def get_histograms(self, ptcut):
		try:
			if self.histograms[ptcut]:
				return self.histograms[ptcut]
		except:
			self.histograms[ptcut] = []
			for i in range(self.ncorrel - 1):
				hname = 'hec_{}_ptcut_{}'.format(i+2, ptcut)
				self.fout.cd()
				h = ROOT.TH1F(hname, hname, self.nbins, self.lbins)
				self.histograms[ptcut].append(h)

		return self.histograms[ptcut]

	# scale is the jet pt
	def fill_jet(self, j, parts, scale, pt_cuts=[0.15, 1.], sigmaGen=1., weight=1.):
		self.tnjet.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()), sigmaGen, weight)
		_ = [self.tnjetFF.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()), _p.perp()/j.perp(), _p.phi(), _p.eta(), _p.perp()) for _p in j.constituents()]
		for pt_cut in pt_cuts:
			_parts = vector[fj.PseudoJet]()
			_ = [_parts.push_back(p) for p in parts if p.perp() > pt_cut]
			_cb = EnergyCorrelators.CorrelatorBuilder(_parts, scale, self.ncorrel)
			for i in range(self.ncorrel - 1):
				_hl = self.get_histograms(pt_cut)
				_hl[i].FillN(_cb.correlator(i+2).rs().size(), 
							array.array('d', _cb.correlator(i+2).rs()), 
							array.array('d', _cb.correlator(i+2).weights()) )
				_ = [self.tn.Fill(	i+2, 
                      				pt_cut, 
                          			_cb.correlator(i+2).rs()[_i], 
                             		_cb.correlator(i+2).weights()[_i], scale, sigmaGen, weight) 
         			for _i in range(0, _cb.correlator(i+2).rs().size())]
    
	def __del__(self):
		if self.fout:
			print('[i] writing', self.fout.GetName())
			self.fout.Write()
			self.fout.Close()

	def write(self):
		if self.fout:
			print('[i] writing', self.fout.GetName())
			self.fout.Write()
			self.fout.Close()