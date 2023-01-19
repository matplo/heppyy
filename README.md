# heppyy
HEP soft with python using cppyy 

# recommendation

- use conda
```
conda create -n heppyy
conda activate heppyy
conda install python
conda install -c conda-forge compilers
# install cppyy supporting c++11 - for fastjet
STDCXX=11 python -m pip install cppyy
# some more packages
conda install -c conda-forge root hepmc2 hepmc3 lhapdf6
conda install numpy tqdm ...
# you can install pythia8 also from conda but it will be pybind11 not cppyy we so use yasp (https://github.com/matplo/yasp) to install pythia - heppyy is yasp aware...
git clone https://github.com/matplo/yasp
# we will install those locally here ./external but we could also point to the conda dir or anywhere else in the system
./yasp/yasp.py --configure --prefix $PWD/external --workdir $PWD/build
./yasp/yasp.py --install fastjet fjcontrib pythia8
```

# test

- run `test_pythia_fastjet.py` from `util` directory

