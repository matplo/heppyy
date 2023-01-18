# heppyy
HEP soft with python using cppyy 

# recommendation

- use conda
```
conda create -n heppyy
conda activate heppyy
conda install python
# install cppyy supporting c++11 - for fastjet
STDCXX=11 python -m pip install cppyy
# some more packages
conda install -c conda-forge root
conda install numpy tqdm 
```

# test

- run `test_pythia_fastjet.py` from `util` directory

