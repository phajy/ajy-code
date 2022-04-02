# XSPEC walk through

XSPEC tutorial / walk through tutorial.

## Run XSPEC

I run [XSPEC](https://heasarc.gsfc.nasa.gov/xanadu/xspec/) in a [Docker](https://heasarc.gsfc.nasa.gov/docs/software/heasoft/docker.html) because I find it easier to keep all the libraries and dependencies working well.

```
/opt/X11/bin/xhost + 127.0.0.1
docker run --rm -it -e DISPLAY=host.docker.internal:0 -v /Volumes/ajy/research:/research heasoft:v6.29 tcsh
```

You can update this to share whatever folder you like (I have data on an external disk in `/Volumes/ajy/research`).

## Set up the local model

Download the source code and tables from the [RELXILL web site](http://www.sternwarte.uni-erlangen.de/~dauser/research/relxill/).

### Compile for the first time

Change the path to wherever your `relxill` model is.

```
cd /research/relxill_model
chmod u+r compile_relxill.sh
./compile_relxill.csh
```

### Load model into XSPEC (need to to do this each time)

```
setenv RELXILL_TABLE_PATH /research/relxill_model/
xspec
lmod relxill /research/relxill_model
```

You can put the `setenv` into your `.cshrc` or equivalent. There is an XSPEC initialisation file that can load the local model automatically each time you start XSPEC.

## Load and fit some data

These data sets are from MSci project students and are _XMM Newton_ observations of the AGN MCG-6-30-15. I've put the files in `/research/mcg-6-30-15` but you should `cd` to the appropriate directory.

The data files can be found in `files/spectra` which also includes an example fit file (`pgplot.pdf`).

```
xspec
lmod relxill /research/relxill_model
cd /research/mcg-6-30-15
data fabian_pn_source.ds
back fabian_pn_bkg.ds
resp fabian_pn_response.rmf
cpd /xs
setp e
ignore 0.-1.
ignore 10.-**
mo tbabs*(gaussian+relxill)
```

The spectrum file can include the name of the background file and response files in the header so you don't have to load them by hand.

You can then enter some model parameters. Here's an example save file that you can read in.

```
@ajy_relxill
fit
pl ld de
```
