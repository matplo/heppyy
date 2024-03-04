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
# ./yasp.py -i yasp -m
# module load yasp

# Install some packages: can use --define version=x.xx.xx to set custom versions
python -m pip install numpy
yasp -mi HepMC2/2.06.11
module load HepMC2/2.06.11
yasp -mi HepMC3/3.2.7
module load HepMC3/3.2.7
yasp -mi LHAPDF6/6.5.4
module load HepMC3/3.2.7
yasp -mi fastjet/3.4.2
module load fastjet/3.4.2
yasp -i fjcontrib/1.053-custom  # Builds into fastjet
yasp -i IFNPlugin/jetflav         # Builds into fastjet
# yasp -i jetflav/default         # Builds into fastjet
yasp -mi root/6.28.12
module load root/6.28.12
yasp -mi roounfold/default
module load roounfold/default
yasp -mi pythia8/8310
module load pythia8/8310
yasp -mi sherpa/2.2.15 --define extra_opt=--disable-pyext
# you may need to use a cxx flag on a mac
# yasp -mi sherpa/2.2.15 --define cxx14=true
```

- then one can do (starting with a fresh shell below)

```
cd ${workdir}
source yasp/venvyasp/bin/activate  # Load the virtualenv
module use yasp/software/modules   # Tell module where to look
module load root roounfold HepMC2 LHAPDF6 HepMC3 pythia8 sherpa fastjet
git clone https://github.com/matplo/heppyy.git
./heppyy/install_with_yasp.sh
```

- test
```
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

# test

- run `./example/test_pythia_fastjet.py`

