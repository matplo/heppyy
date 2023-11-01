import yasp
import heppyy.util.hepmc2util_cppyy
from cppyy.gbl import HeppyyHepMCUtil
import tqdm

print(HeppyyHepMCUtil.statfile)
print(HeppyyHepMCUtil.ReadHepMCFile)

import sys
fname = "/rstorage/ploskon/jewel/ptmin100/job0/eventfiles/out_lhc10cent_0.hepmc"
if len(sys.argv) > 1:
    fname = sys.argv[1]
fin = HeppyyHepMCUtil.ReadHepMCFile(fname)
nev = HeppyyHepMCUtil.get_n_events(fname)
pbar = tqdm.tqdm(total=nev)
while fin.NextEvent():
    fin.GetEvent()
    pbar.update(1)
pbar.close()
