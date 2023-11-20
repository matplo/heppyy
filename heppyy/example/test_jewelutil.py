import yasp
import heppyy.util.jewelutil_cppyy
from cppyy.gbl import HeppyyJewelUtil
from cppyy.gbl import HeppyyHepMCUtil
import tqdm

import sys
fname = "/rstorage/ploskon/jewel/ptmin100/job0/eventfiles/out_lhc10cent_0.hepmc"
# fname = "/rstorage/ploskon/jewel/ptmin100/job0/eventfiles/out_lhcvac_0.hepmc"
fname = "/rstorage/ploskon/jewel/output_v2.4.0/ptmin100/job0/eventfiles/out_lhc10cent_0.hepmc"
if len(sys.argv) > 1:
    fname = sys.argv[1]
fin = HeppyyJewelUtil.ReadJewelHepMC2File(fname)
nev = HeppyyHepMCUtil.get_n_events(fname)
pbar = tqdm.tqdm(total=nev)
while fin.NextEvent():
    # fin.GetEvent()
    fjp1 = fin.fjParticlesWithStatus(1)
    fjp3 = fin.fjParticlesWithStatus(3)
    # print(f'number of particles with status 1 : {len(fjp1)} - with 3 : {len(fjp3)}')
    fjp4 = fin.fjParticlesWithStatus(4)
    print(f'number of particles with status 1 : {len(fjp1)} - with 3 : {len(fjp3)} - with 4 : {len(fjp4)}')
    # fjsubtr = fin.fjFinalParticlesSubtractedThermal()
    fjsubtr = fin.fjFinalParticlesSubtractedThermalRivet()
    pbar.update(1)
pbar.close()
