import yasp
import ROOT
import numpy as np
import array


headers = [
    "fastjet/PseudoJet.hh",     
	"eec/ecorrel.hh"
	]

packs = ['fastjet', 'heppyy']
libs = ['fastjet', 'heppyy_eec']

from yasp.cppyyhelper import YaspCppyyHelper
ycppyy = YaspCppyyHelper()
print(ycppyy)
YaspCppyyHelper().load(packs, libs, headers)

from cppyy.gbl import fastjet as fj
from cppyy.gbl.std import vector
from cppyy.gbl import EnergyCorrelators


def logbins(xmin, xmax, nbins):
        lspace = np.logspace(np.log10(xmin), np.log10(xmax), nbins+1)
        arr = array.array('f', lspace)
        return arr


class EEChistograms(yasp.GenericObject):
	def __init__(self, **kwargs):
		super(EEChistograms, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug        
		self.fout = ROOT.TFile(self.output, 'recreate')
		self.fout.cd()

		self.histograms = {}
		self.tn = ROOT.TNtuple('tn', 'tneec', 'n:ptpartcut:RL:w:jetpt')
		self.tnjet = ROOT.TNtuple('tnjet', 'tnjet', 'pt:eta:phi:nc')
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
				h = ROOT.TH1F(hname, hname, self.nbins, self.lbins)
				self.histograms[ptcut].append(h)

		return self.histograms[ptcut]

	# scale is the jet pt
	def fill_jet(self, j, parts, scale, pt_cuts=[0, 1.]):
		self.tnjet.Fill(j.perp(), j.eta(), j.phi(), len(j.constituents()))
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
    
	def __del__(self):
		print('[i] writing', self.fout.GetName())
		self.fout.Write()
		self.fout.Close()