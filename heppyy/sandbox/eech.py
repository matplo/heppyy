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
from heppyy.util.treewriter import RTreeWriter

class EEChistograms(yasp.GenericObject):
	def __init__(self, **kwargs):
		super(EEChistograms, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug
		if self.output_fname:
			self.output = self.output_fname
		self.fout = ROOT.TFile(self.output, 'recreate')
		self.fout.cd()

		self.histograms = {}
		self.tn = ROOT.TNtuple('tn', 'tneec', 'n:ptpartcut:RL:w:jetpt')
		self.tnjet = ROOT.TNtuple('tnjet', 'tnjet', 'pt:eta:phi:nc')
		self.tnjetFF = ROOT.TNtuple('tnjetFF', 'tnjetFF', 'pt:eta:phi:nc:z:zphi:zeta:ptcut')
		self.nbins = int(18.)
		self.lbins = logbins(1.e-3, 1., self.nbins)

		self.tw = RTreeWriter(fout=self.fout, tree_name='teec')
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
	def fill_jet_old(self, j, parts, scale, pt_cuts=[0, 1.]):
		self.tnjet.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()))
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
                             		_cb.correlator(i+2).weights()[_i], scale) 
         			for _i in range(0, _cb.correlator(i+2).rs().size())]
    
	def fill_jet(self, j, scale=None, pt_cut=1.0):
		self.tnjet.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()))
		_ = [self.tnjetFF.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()), _p.perp()/j.perp(), _p.phi(), _p.eta(), _p.perp()) for _p in j.constituents()]
		_data = {}
		_data['j'] = j
		_data['pt_cut'] = pt_cut
		_parts = vector[fj.PseudoJet]()
		_ = [_parts.push_back(p) for p in j.constituents() if p.perp() > pt_cut]
		_scale = scale
		if scale is None:
			_scale = j.perp()
		_cb = EnergyCorrelators.CorrelatorBuilder(_parts, _scale, self.ncorrel)
		for i in range(self.ncorrel - 1):
			_data['rs'] = [_rs for _rs in _cb.correlator(i+2).rs()]
			_data['w'] = [_w for _w in _cb.correlator(i+2).weights()]
			_data['scale'] = _scale
			self.tw.fill_branch('eec_{}'.format(i+2), _data)
		self.tw.fill_tree()

	def fill_lund_jet(self, j, lund_gen=None, scale=None, pt_cut=1.0):
		if lund_gen is None:
			self.fill_jet(j, scale=scale, pt_cut=pt_cut)
			return
		self.tnjet.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()))
		_ = [self.tnjetFF.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()), _p.perp()/j.perp(), _p.phi(), _p.eta(), _p.perp()) for _p in j.constituents()]
		lunds = lund_gen.result(j)
		nsplits = len(lunds)
		for il, l in enumerate(lunds):
			_parts = vector[fj.PseudoJet]()
			_ = [_parts.push_back(p) for p in l.pair().constituents() if p.perp() > pt_cut]
			_scale = scale
			if scale is None:
				_scale = j.perp()
			if scale == 'lund':
				_scale = l.perp()
			_data = {}
			_data['j'] = j
			_data['l'] = l.pair()
			_data['l_nsplits'] = nsplits
			_data['l_nsplit'] = il
			_data['l_kt'] = l.kt()
			_data['l_kappa'] = l.kappa()
			_data['l_z'] = l.z()
			_data['l_m'] = l.m()
			_data['l_psi'] = l.psi()
			_data['l_delta'] = l.Delta()
			_data['l_pt_cut'] = pt_cut
			_data['l_scale'] = _scale
			_cb = EnergyCorrelators.CorrelatorBuilder(_parts, _scale, self.ncorrel)
			for i in range(self.ncorrel - 1):
				_rs = _cb.correlator(i+2).rs()
				_ws = _cb.correlator(i+2).weights()
				for ic in range(_rs.size()):
					_data['l_rs'] = _rs[ic]
					_data['l_w'] = _ws[ic]
					self.tw.fill_branch('eec{}'.format(i+2), _data)
					self.tw.fill_tree()
    
	def __del__(self):
		print('[i] writing', self.fout.GetName())
		self.fout.Write()
		self.fout.Close()