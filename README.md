# heppyy
HEP soft with python using cppyy 

# recommendation

## use yasp with virtualenv

```
workdir=<somewhere>
cd ${workdir}
git clone https://github.com/matplo/yasp
cd yasp
./yaspenv.sh
./yasp.py -i yasp -m
module load yasp

# install some packages
python -m pip install numpy
yasp -mi root/default --define version=6.28.06
module load root/default
yasp -mi HepMC2/2.06.11
module load HepMC2/2.06.11
yasp -mi LHAPDF6/6.5.3 --define version=6.5.4
module load LHAPDF6/6.5.3
yasp -mi HepMC3/3.2.5 --define version=3.2.6
module load HepMC3/3.2.5
yasp -mi fastjet/3.4.0
module load fastjet/3.4.0
yasp -i fjcontrib/1.051
yasp -mi pythia8/8308
module load pythia8/8308
./install_with_yasp.sh
yasp -mi sherpa/2.2.15 --define extra_opt=--disable-pyext
```

- then one can do (starting with a fresh shell below)

```
cd ${workdir}
./yasp/yaspenv.sh
module load root HepMC2 LHAPDF6 HepMC3 pythia8 sherpa fastjet
git clone https://github.com/matplo/heppyu.git
./heppyy/example/test_yaspcppyy_pythia_fastjet.py
```

- note yasp can make a collect module file

```
cd ${workdir}
./yasp/yaspenv.sh
module load root HepMC2 LHAPDF6 HepMC3 pythia8 sherpa fastjet heppyy
yasp --mm myheppyy
```

so next time "module load myheppyy" should work...

## try conda
```
conda create -n heppyy
conda activate heppyy
conda install python
conda install -c conda-forge compilers
# install cppyy supporting c++11 - for fastjet
STDCXX=11 python -m pip install cppyy==2.4.0
# some more packages
conda install -c conda-forge hepmc2 hepmc3 lhapdf pyyaml numpy tqdm
# you can also grab root from conda
# conda install -c conda-forge root but this on some systems does not always work nice with the new cppyy
# you can install pythia8 also from conda but it will be pybind11 not cppyy we so use yasp (https://github.com/matplo/yasp) to install pythia - heppyy is yasp aware...
git clone https://github.com/matplo/yasp
# we will install those locally here ./external but we could also point to the conda dir or anywhere else in the system
./yasp/yasp.py --configure --prefix $PWD/external --workdir $PWD/build
./yasp/yasp.py --install fastjet fjcontrib pythia8
```

# test

- run `./example/test_pythia_fastjet.py`

