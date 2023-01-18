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
conda install -c conda-forge root hepmc2 hepmc3
# you can install pythia8 also from conda but it will be pybind11 not cppyy
# so use yasp to install pythia - heppyy is yasp aware...
conda install numpy tqdm ...
```

# test

- run `test_pythia_fastjet.py` from `util` directory

