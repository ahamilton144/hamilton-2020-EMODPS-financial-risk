# hamilton-2020-managing-financial-risk-tradeoffs-for-hydropower
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3627730.svg)](https://doi.org/10.5281/zenodo.3627730) 

This repository contains all code and data (included data for figures) for the following paper:

Hamilton, A.L., Characklis, G.W., &amp; Reed, P.M. (2020). Managing financial risk tradeoffs for hydropower generation using snowpack-based index contracts (submitted manuscript).

Licensed under the GNU General Public License v3.0. In building the multi-objective optimization (MOO) component of this code base, I borrowed and built upon sections of Julianne Quinn's [Lake Problem Direct Policy Search code](https://github.com/julianneq/Lake_Problem_DPS).

## Contents
* `code/` - directory with all code used to replicate paper
  * `synthetic_data_and_moea_plots/` - Python and bash scripts needed for (1) Generating all synthetic time series, (2) Plotting related to synthetic data, (3) Plotting related to MOO output
  * `optimization/` - C++ and bash scripts needed for MOO
  * `misc/` - directory for storing third-party software
    * `HypervolumeEval.class` - Class for calculating hypervolume with MOEAFramework, written by Dave Hadka, created following instructions [here](https://waterprogramming.wordpress.com/2015/08/26/moea-diagnostics-for-a-simple-test-case-part-23/)
    * `boostutil.h` - Utility functions for boost matrices/vectors, taken from [Lake Problem DPS](https://github.com/julianneq/Lake_Problem_DPS/blob/master/Optimization/boostutil.h) by Julianne Quinn.
* `data/` - directory with all data
  * `downloaded_inputs/` - original data (sources described in manuscript)
    * `ice_electric-*final.xls`, `NP15Hub.xls` - Historical electricity price data at NP15 hub in northern California
    * `SeriesReport-20190311141838_d27dd7.xlsx` - Historical consumer price index data
    * `SFPUC_Combined_Public.xlsx` - Historical hydropower generation and sales for SFPUC
    * `SFPUC_genMonthly.csv` - Historical hydropower generation for SFPUC (after manually aggregating across sources to monthly time step)
    * `swe_dana_meadows.csv` - Historical snow water equivalent depth at Dana Meadows snow station
  * `generated_inputs/` - data generated by user
    * `param_LHC_bounds.txt` - parameter file dictating bounds for Latin Hypercube Sample across parameter space for sensitivity analysis
    * Other files created by model itself, as described below
  * `optimization_output/` - outputs from MOO needed for furthur analysis
    * `baseline/` - results from MOO using baseline parameters(SFPUC October 2016 estimates)
    * `sensitivity_analysis/` - results from MOO for sensitivity analysis
* `figures/` - directory for storing figures

## Running the model
* Clone the model and install dependencies. 
  * Synthetic generation and all plotting is set up to run on my Windows laptop, using a linux bash shell (e.g., Cygwin), and Python 3.6.1, plus the Python libraries below. If using a different setup, you may have to make alterations to the bash scripts.
    * Python libraries: numpy, pandas, matplotlib, seaborn, importlib, datetime, statsmodels, math, scipy
  * Optimization set up to run on [THECUBE](https://www.cac.cornell.edu/wiki/index.php?title=THECUBE_Cluster), a cluster housed at Cornell University. THECUBE uses the slurm scheduler. Submission scripts and makefiles may need to be altered to accomodate different setups.
* Additional software
  * Download the [Borg MOEA](http://borgmoea.org/) source code
    * Create a new directory called `borg` within the `code/misc/` directory and place the source code here.
  * Download the "Compiled Binaries" from the [MOEAFramework](http://www.moeaframework.org/) website.
    * Copy the `moeaframework.c` &amp `moeaframework.h` files (from the `MOEAFramework-*/examples` directory of the packag) to `code/misc/borg` 
  * Download the "Demo Application" from the [MOEAFramework](http://www.moeaframework.org/) website.
    * Move `MOEAFramework-*-Demo.jar` to `code/misc`
  * Download `pareto.py` from [Github](https://github.com/matthewjwoodruff/pareto.py) 
    * Move to `code/misc`
* Create Latin Hypercube Sample for sensitivity analysis. 
  * From project home directory, navigate to the code directory for synthetic data generation (`cd code/synthetic_data_and_moea_plots`)
  * Now run LHC sample script (`sh get_sample_LHC.sh`)
  * Output (`data/generated_inputs/param_LHC_sample.txt`) will have five columns (one for each uncertain factor) and 151 rows. The first 150 are from the LHC sample, and the last is the baseline parameter values.
* Create synthetic time series and related plots
  * Run `make_synthetic_data_plots.py`, either in an IDE such as Pycharm, or in a bash shell (`python make_synthetic_data_plots.py` from `code/synthetic_data_and_moea_plots` directory)
    * This takes about 7 minutes on my laptop.
    * Outputs
      * `data/generated_inputs/synthetic_data.txt` - Synthetic time series of SWE, revenue, and CFD contract payouts (using baseline market price of risk (lambda) parameter value). Needed for MOO.
      * `data/generated_inputs/synthetic_data_monthly.txt` - Synthetic time series of monthly hydropower generation and power prices. Not needed for the present study, but stored here for a future study.
      * `data/generated_inputs/param_LHC_sample_withLamPremShift.txt` - Parameter sample file with a newly-calculated contract for differences (CFD) pricing shift based on sampled market price of risk (lambda) value. Used in sensitivity analysis MOOs.
      * Figures 2-6 from main text and S2-S3 from Supporting Information, in `figures` directory
  * Run `make_swe_copula_plot.py` 
    * Output - Figure S1 from Supporting Information, in `figures` directory
    * This takes ~2 hours on my laptop. Skip this step if you don't want to reproduce this plot.
* Transfer new files from `data/generated_inputs/` to cluster (skip this step if performing all analysis on same machine)
* Create baseline, sensitivity, & retest versions. Compile each C++ using MPI. All steps executed from directory `code/optimization`
  * `sh remake.sh`
  * Note: you may need to alter compiler, library/module locations, etc., in `remake.sh` and `makefile` based on your machine.
* Run MOO for baseline & sensitivity analysis, from `code/optimization/` directory, in bash shell.
  * `sbatch run_baseline_borgms.sh` - This will launch 50 instances of the MOO, each with a different seed given to Borg MOEA.
  * `sbatch run_sensitivity_borgms.sh` - This will launch 1500 instances of the MOO; 150 sets of parameters for the sensitivity analysis, with 10 Borg seeds each.
  * Note: May want to change the number of nodes (`--nodes`), number of processors per node (`--ntasks-per-node`), and wall time (`-t`) to match your resources. The default is 1 node of 16 processors for the baseline set (on THECUBE, this ran for ~1 real minute, or 16 user minutes, per seed, or ~50 real minutes total), and 5 nodes of 16 processors each for the sensitivity analysis (which ran for a total of ~5.1 real hours total, or ~411 user hours).
  * Outputs
    * `data/optimization_output/baseline/sets/param150_seedS1_seedB*.set`, for values of * in 1-50
    * `data/optimization_output/baseline/runtime/param150_seedS1_seedB*.runtime`, for values of * in 1-50
    * `data/optimization_output/sensitivity/sets/param@_seedS1_seedB*.set`, for values of * in 1-10, @ in 1-150
    * `data/optimization_output/sensitivity/runtime/param@_seedS1_seedB*.runtime`, for values of * in 1-10, @ in 1-150
* Run postprocessing script
  * `sh postprocess_output.sh`, from directory `code/optimization`
  * Outputs
    * `data/optimization_output/baseline/param150_borg.resultfile` - Reference set for baseline with 5 columns: 2 decision variables (max reserve size, cfd slope), 2 objectives (expected annualized cash flow, 95th percentile max fund), 1 constraint
    * `data/optimization_output/baseline/param150_borg.reference` - Same as resultfile, but only 2 objective columns
    * `data/optimization_output/baseline/param150_borg.hypervolume` - Hypervolume of reference set
    * `data/optimization_output/baseline/param150_borg_retest.resultfile` - Results from rerunning reference set on a new stochastic sample of 50,000 simulations. Adds 3 columns to end of resultfile - objectives & constraint values on rerun.
    * `data/optimization_output/baseline/metrics/param150_seedS1_seedB*.metrics`. - Indicators of performance throughout Borg MOEA run, for seed number * in 1-50. 50 rows give performance at function evaluations (200, 400, ..., 10000).
    * `data/optimization_output/sensitivity/param@_borg.resultfile` - Reference set for sensitivity analysis parameter set @ (0-149)
    * `data/optimization_output/sensitivity/param@_borg.reference` 
    * `data/optimization_output/sensitivity/param@_borg.hypervolume` 
    * `data/optimization_output/sensitivity/param@_borg_retest.resultfile`
    * `data/optimization_output/sensitivity/metrics/param@_seedS1_seedB*.metrics`. - Indicators of performance throughout Borg MOEA run, for seed number * in 1-10, for sensitivity analysis parameter set @ in 0-149. Note some will be missing, indicating (@,*) combinations for which fewer than two feasible solutions are found, and thus some performance indicators are undefined. We find that 1310 out of 1500 total (@,\*) combinations have feasible metrics files.
* Transfer important MOO outputs to appropriate directories on laptop for plotting (skip this step if performing the all analysis on a single machine)
  * `data/optimization_output/baseline/param150_borg.hypervolume`
  * `data/optimization_output/baseline/param150_borg_retest.resultfile`
  * `data/optimization_output/baseline/metrics/param150_seedS1_seedB*.metrics`, for * in 1-50
  * `data/optimization_output/sensitivity/param@_borg.hypervolume`, for @ in 0-149
  * `data/optimization_output/sensitivity/param@_borg_retest.resultfile`, for @ in 0-149
  * `data/optimization_output/sensitivity/metrics/param@_seedS1_seedB*.metrics`, for @ in 0-149, * in 1-10
* Create plots related to MOO results
  * Run `make_moea_output_plots.py`, from directory `code/synthetic_data_and_moea_plots.py`
  * This takes about 3 minutes on my laptop
  * Outputs
    * Figures 7-11 from main text and S4-S9 from Supporting Information, in `figures` directory
