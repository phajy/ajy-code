# PSD Table Model

The code `PSDTable.py` can be used to assemble an XSPEC table model of Power Spectral Densities (PSD).

## How to create a PSD table model

I will provide separate documentation on how to run this later.

You can find a pre-made table model on Typhon at `/data/typhon1/phajy/gx339-4/pwd.mod`.

## How to use the PSD table model in XSPEC

### Change the PSD format so it can be read into XSPEC

See instructions on using a (propagating fluctuations model)[https://heasarc.gsfc.nasa.gov/xanadu/xspec/models/propfluc.html] in XSPEC. Use `flx2xsp` to convert a PSD to a "pi" file and response. See Appendix A of Ingram & Done (2012) for how to do this.

As a test case let's use the power spectrum `xti3558010202_700-1500eV_ps_logrb.fits`.

I've created a text file from this called `my_psd.csv` (you can find this file in the `test` folder) with the following columns.

$f − df$, $f + df$, $2 P df$, $2 dP df$.

- $f$ is the frequency at the bin centre.
- $df$ is related to the bin width, which spans $f \pm df$ so the bin width is $2df$.
- $2 P df$ is the power, $P$, multiplied by the bin width $2 df$.
- $2 dP df$ is the error on the power, $dP$, multiplied by the bin widht $2 df$.

Note that columns should be separated by spaces not commas.

You can convert this to a "spectrum" and "response" using the following command (you'll need to have HEASOFT initialised).

`flx2xsp my_psd.csv my_psd.pha my_psd.rsp`

### Read the PSD into XSPEC and try to fit the data

```
xspec
data my_psd.pha
mo atable{psd.mod}
```

You can input some model parameters. I found the following values worked well for the example. These are the best fit values so perhaps don't start off with exactly these values. Note that I chose to freeze the normalisation at one here.

```
========================================================================
Model atable{psd.mod}<1> Source No.: 1   Active/On
Model Model Component  Parameter  Unit     Value
 par  comp
   1    1   psd        r_trc               18.0020      +/-  1.74275E-02  
   2    1   psd        r_sh                14.6994      +/-  6.45075E-02  
   3    1   psd        inc                 30.2127      +/-  1.51881E-02  
   4    1   psd        disc_par            8.54846E-03  +/-  3.00278E-04  
   5    1   psd        emiss               0.623116     +/-  0.133434     
   6    1   psd        norm                1.00000      frozen
________________________________________________________________________
```

```
cpd /xs
setplot energy
ignore 10.-**
fit
plot eufs del
```

The `ignore` command will, in this case, ignore the PSD above 10 Hz.

The plot command will plot the "unfolded spectrum" multiplied by energy and show the residuals. This should look like quite a good fit.

Note that `XSPEC` will plot this as a "spectrum" so the X-axis will be in "Hz" and the y-axis in "power" (or "frequency x power" if plotting when multiplied by "energy").

You can get confidence intervals on the parameters using the `err` command. E.g., `err 2` will give you the 90% confidence interval for parameter 2.
