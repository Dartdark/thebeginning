# Replication package for "Building Macroeconomically Relevant Climate Indices via the Assemblage VAR"

The Econometrics Journal, manuscript MS3837. Christophe Barrette, Philippe Goulet Coulombe and Tim
Reinicke. October 2026. Contact: Tim Reinicke, timreinicke@googlemail.com.

`ReadMe.pdf` is the official README. This file mirrors it.

**GitHub version.** This repository contains the published replication package (Zenodo,
https://doi.org/10.5281/zenodo.23976450) without the raw source files in `data/raw/`. The cleaned
data in `data/` are sufficient to reproduce all results. To rerun the optional data preparation,
obtain the raw files from the Zenodo record or from the sources listed in `data/raw/README.md`.

## 1. Overview

The package reproduces every figure (Figures 1-4, A.1-A.5, B.1, D.1-D.4), the two tables (Tables
C.1-C.2) and the numbers quoted in the text of the paper. All code
is in R. The master script `run_all.R` re-estimates the six Assemblage VAR specifications (ACI
national, ACI regional and NOAA panels, each in component and rank space) at the cross-validated
penalties stored in `config.R`, computes the impulse responses, draws all figures, writes the in-text
numbers and checks that all expected outputs are present, in 4-9 minutes on a laptop (Section 3.3). The computationally
expensive steps (penalty cross-validation, residual-bootstrap bands, pairs bootstrap and
expanding-window re-estimation) are supplied as results and can be recomputed with optional switches
(Section 5). An optional script rebuilds the analysis data in `data/` from the raw source files.
Section 4 lists the package contents.

## 2. Data availability and provenance

### 2.1 Statement about rights

- [x] I certify that the author(s) of the manuscript have legitimate access to and permission to use
  the data used in this manuscript.
- [ ] I certify that the author(s) of the manuscript have documented permission to
  redistribute/publish the data contained within this replication package. Appropriate permission
  are documented in the LICENSE.txt file (if applicable).

In this package the licence file is `LICENSE` in the package root.

### 2.2 Licence for data

The MIT licence in `LICENSE` covers the code only. The data files in `data/` and `data/raw/` remain
subject to the terms of their providers (Section 2.4).

### 2.3 Summary of availability

- [ ] All data **are** publicly available.
- [x] Some data **cannot be made** publicly available.
- [ ] **No data can be made** publicly available.

All source data can be obtained free of charge from their providers. Two raw files, the Actuaries
Climate Index workbook and the Macrobond export of the NOAA series, may not be redistributed under
their providers' terms. They are provided to the data editor confidentially in
`4-confidential-data-not-for-publication.zip` for the reproducibility checks only. The cleaned and
seasonally adjusted data derived from them, which are used for all results in the paper, are in
this package (`data/`); all other data, including the raw FRED-MD and Wu-Xia files, are included.

### 2.4 Data sources

| Source | Access and licence | Vintage | In package |
|---|---|---|---|
| 1. Actuaries Climate Index (ACI), U.S. monthly unstandardised components, national and 7 regions | https://actuariesclimateindex.org/data/; no registration; Terms of Use (https://actuariesclimateindex.org/terms-of-use/) accepted at download; derived series included for replication purposes | accessed 21 Jan 2026; data 1961:M1-2025:M5 | raw workbook: no; derived `data/aci_*.csv`, `data/labels_aci_*.csv`: yes |
| 2. NOAA NCEI, Climate at a Glance, regional time series (nClimDiv): 80 series, 9 regions and contiguous U.S. | https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/regional/time-series; no registration; U.S. Government work, public domain | retrieved via Macrobond, Feb 2026; data 1961:M1-2025:M12 | raw export: no; derived `data/noaa_*.csv`, `data/labels_noaa.csv`: yes |
| 3. NOAA GML, Mauna Loa CO2, monthly mean and trend | https://gml.noaa.gov/ccgg/trends/; no registration; public domain, cite the data providers | retrieved via Macrobond, Feb 2026 | as source 2 (two columns) |
| 4. Macrobond (platform used to retrieve 2-3 in one export) | https://www.macrobond.com; paid subscription, not needed for replication (2-3 are free); subscription terms | export of Feb 2026 | no |
| 5. FRED-MD (McCracken and Ng 2016): `INDPRO`, `PCEPI`, `UNRATE`, `EXUSUKx`, `HOUST`, `FEDFUNDS` | https://www.stlouisfed.org/research/economists/mccracken/fred-databases; no registration; published by the Federal Reserve Bank of St. Louis for research and replication | vintage 2025-12, downloaded 3 Oct 2026; data 1959:M1-2025:M10 | yes: `data/raw/2025-12-md.csv`, `data/macro_*.csv` |
| 6. Wu-Xia shadow federal funds rate (Wu and Xia 2016), Federal Reserve Bank of Atlanta | https://www.atlantafed.org/research-and-data/data/wu-xia-shadow-federal-funds-rate; no registration; public, cite Wu and Xia (2016) | downloaded 3 Oct 2026 (values identical to the paper's copy); last month 2022:M2 (updates suspended) | yes: `data/raw/WuXiaShadowRate.xlsx`; `SHADOWRATE` in `data/macro_*.csv` |
| 7. NBER business cycle dates (recession shading only) | https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions; permission to copy with attribution of source | accessed 1 Oct 2026 (latest trough 2020:M4) | yes: `data/nber_recessions.csv` |

Notes. The NOAA series (2-3) can be downloaded free of charge directly from NOAA; NOAA revises recent
values, so a new download can differ slightly. The FRED-MD and Wu-Xia files in `data/raw/` are the
original downloads, unchanged; `code/00_prepare_data.R` builds `SHADOWRATE` as the Wu-Xia rate from
1990:M4 to 2022:M2 and the FRED-MD `FEDFUNDS` in all other months. `data/raw/README.md` describes
each raw file and how to obtain it, and `data/raw/MANIFEST.csv` gives URL, download date, size and
SHA-256 of every raw file. `data/README.md` documents every column and transformation of the 14
analysis files.

## 3. Computational requirements

### 3.1 Software requirements

- R 4.3 or newer (verified with R 4.3.1 on Windows 11; paper results computed with R 4.5.2 on macOS); no other software for the
  main run. Versions of R and all packages used for the verified run: `sessionInfo.txt`.
- R packages (tested versions in `requirements.csv`; `install_packages.R` installs missing ones from
  CRAN and rejects older versions): NlcOptim 0.6, vars 1.6-1, ggplot2 3.5.1, ggthemes 5.2.0,
  zoo 1.8-12, scales 1.3.0, ggh4x 0.3.0, base R (parallel, stats, utils, grid, grDevices). Optional
  for figures: ragg 1.2.5, systemfonts 1.0.4 and the font STIX Two Text (otherwise R's default serif
  font).
- Optional, data preparation only: readxl 1.4.3, RJDemetra 0.2.8 and rJava 1.0-11 (not installed by
  `install_packages.R`; use `install.packages(c("readxl", "RJDemetra"))`); RJDemetra needs Java 8 or
  newer. Optional for step 3 on a cluster: SLURM (`code/slurm_helper/`).

### 3.2 Controlled randomness

- [x] The random seed is set in `config.R` (`SEED <- 123L`) and applied with `set.seed(SEED)` in
  `code/01_estimate_weights.R` and `code/02_irf_bands.R`. Step 3 (`code/03_bootstrap_weights.R`)
  uses `RNGkind("L'Ecuyer-CMRG")` with `set.seed(SEED)`, and `set.seed(SEED + o)` for
  expanding-window origin `o` (`code/funcs/pairs_bootstrap.R`).

### 3.3 Memory, runtime and storage

The default run takes **less than 10 minutes** and less than 2 GB of memory; a full recomputation of
all supplied results takes **1-3 days** on one machine. Storage: **25-250 MB** (the package is about
176 MB, of which 157 MB are the supplied bootstrap results). Reference machine for the runtimes below:
Lenovo laptop (model 20XL), AMD Ryzen 7 PRO 5850U (8 cores, 16 threads), 32 GB RAM, Windows 11
Education (10.0.26200), R 4.3.1. The supplied bootstrap archives were computed on a SLURM cluster
with `code/03_bootstrap_weights.R`.

| Route | Work | Time |
|---|---|---|
| `Rscript run_all.R` (default) | Six estimates at the stored penalties, point responses, 37 figures, in-text numbers, output check | 4-9 minutes (4.4 when the machine is otherwise idle) |
| `RUN_CV=TRUE` | Five-fold block cross-validation over 30 penalties | per specification: national about 2 min, regional 10-25 min, NOAA 45-75 min with nine workers |
| `RUN_IRF_BOOTSTRAP=TRUE` | Residual-bootstrap bands, 7 VARs | about 1 hour per VAR on one core |
| `RUN_BOOTSTRAP_WEIGHTS=TRUE` | Pairs bootstrap (1,000 draws) and 216 expanding-window origins, 6 specifications | 1-3 days sequentially; the SLURM launchers request 2 CPUs, 4 GB per CPU, up to 120 hours per job |
| `code/00_prepare_data.R` | Seasonal adjustment (X-13ARIMA-SEATS) and transformations | 5-10 minutes |

## 4. Package contents and code

Scripts are run from the package root; `run_all.R` runs steps 1-6 in order.

| Path | Contents |
|---|---|
| `ReadMe.pdf`, `README.md` | This document (the PDF is the official version; the Markdown file mirrors it). |
| `LICENSE` | MIT licence for the code; note on the terms of the data files. |
| `run_all.R`, `config.R` | Master script (steps 1-6 and the package check); all settings (sample, VAR, specifications, stored penalties, switches, seed, paths). |
| `install_packages.R`, `requirements.csv`, `sessionInfo.txt` | Package installer and checker; tested versions; R session of the verified run. |
| `code/00_prepare_data.R` | Optional, not run by `run_all.R`: rebuilds the files of `data/` from `data/raw/` into `data/_prepared/` and compares them with the shipped files. |
| `code/01_estimate_weights.R` | Step 1: weights of the six specifications (optional cross-validation); writes `results/point_estimates/`. |
| `code/02_irf_bands.R` | Step 2: point impulse responses; checks the supplied residual-bootstrap bands or recomputes them. |
| `code/03_bootstrap_weights.R` | Step 3, optional: pairs bootstrap (task 1) and expanding windows (task 2). |
| `code/04a_*.R`, `04b_*.R`, `05a_*.R`, `05b_*.R` | Steps 4-5: figures (Section 6). |
| `code/06_summary_numbers.R` | Step 6: in-text numbers, written to `results/summary_numbers.txt`. |
| `code/funcs/` | Functions; `validate_package.R` is the final check (data, settings, point estimates, archive dimensions and sizes, presence of all 38 figure files and the numbers file). |
| `code/slurm_helper/` | SLURM launchers for step 3, with their own `README.md`. |
| `data/`, `data/raw/` | 14 analysis files with the data dictionary `data/README.md`; raw inputs with `README.md` and `MANIFEST.csv`. |
| `results/` | `point_estimates/` (step 1); supplied `irf_bands/` (7 VARs) and `bootstrap/` (12 files, `manifest.csv` with sizes and SHA-256); `summary_numbers.txt` (step 6); formats in `results/README.md`. |
| `figures/` | The 37 figure files produced by the code; `static/Naming_ACI.png` is a hand-made legend. |

## 5. Instructions to replicators

1. Install R 4.3 or newer. Open a terminal in the package root (the folder that contains `config.R`).
2. Run `Rscript install_packages.R` once. Internet access is needed only if packages are missing.
3. Run `Rscript run_all.R`. The run ends with `PACKAGE VALIDATION PASSED` and the elapsed time.
   Figures are written to `figures/`, estimates to `results/point_estimates/` and the in-text numbers
   to `results/summary_numbers.txt`.

Without `Rscript` on the search path (common on Windows), run `source("install_packages.R")` and
`source("run_all.R")` in an R session whose working directory is the package root.

**Optional recomputation.** Switches are environment variables, all `FALSE` by default, e.g.
`RUN_CV=TRUE Rscript run_all.R` (bash) or `$env:RUN_CV="TRUE"; Rscript run_all.R` (PowerShell).
Supplied results are never overwritten.

| Switch | Effect |
|---|---|
| `RUN_CV=TRUE` | Re-selects the penalties by five-fold contiguous block cross-validation (paper protocol) instead of using `config.R`. |
| `RUN_IRF_BOOTSTRAP=TRUE` | Recomputes the residual-bootstrap bands into `results/irf_bands/_recomputed/`. |
| `RUN_BOOTSTRAP_WEIGHTS=TRUE` | Re-runs the pairs bootstrap and expanding windows into `results/bootstrap/_recomputed/` (cluster: `code/slurm_helper/`). |
| `USE_RECOMPUTED=TRUE` | Draws figures and numbers from the `_recomputed` directories only (requires a complete fresh set). |
| `N_CORES=k` | Workers for cross-validation (default: available cores minus one). |

Single scripts can be run from the package root, e.g. `Rscript code/04a_figures_irf.R`. A reduced
step 3, `Rscript code/03_bootstrap_weights.R comp_national 1 5`, writes five draws to
`results/bootstrap/_smoke/` in under a minute; they match the first five draws of
`results/bootstrap/comp_national_task1.rds` to about 1e-6.

**Platform sensitivity.** The paper's results were computed with R 4.5.2 on macOS. On other
platforms small numerical differences can occur: cross-validation can select a neighbouring penalty
where criterion values are nearly tied, the constrained optimizer can stop at slightly different
points, and X-13 can choose a different seasonal model (at most 0.75 standard deviations in the
rebuilt NOAA panel). Recomputing the
residual-bootstrap bands (`RUN_IRF_BOOTSTRAP=TRUE`) on another platform also gives bands that differ
from the supplied ones (in our Windows test by up to about a fifth of the band width) and may redraw a few explosive replications (procedure in Appendix A.1 of the paper). The
default run therefore uses the stored penalties, the supplied bootstrap archives and the shipped
data; remaining differences are small and mostly affect the appendix.

**Optional data preparation.** Install the data-preparation packages (Section 3.1). `data/raw/`
contains the FRED-MD and Wu-Xia files; save the ACI workbook and the Macrobond export (sources 1 and
4) there under the names given in `data/raw/README.md`. Then run `Rscript code/00_prepare_data.R`.
It writes the rebuilt files to `data/_prepared/`, compares them with the shipped files and never
modifies `data/`.

## 6. List of figures, tables and in-text numbers

Figure files are in `figures/`, scripts in `code/`; `<spec>` stands for `comp_national`,
`comp_regional`, `comp_noaa`, `rank_national`, `rank_regional` and `rank_noaa`. The impulse-response
figures (1, 2, A.3, A.4, D.1-D.4) are assembled in LaTeX from three PNG files (panels National,
Regional, NOAA) and a legend strip cropped from the static graphic `figures/static/Naming_ACI.png`.
Figures 1, 2, A.3 and A.4 show the rows for industrial production, unemployment and housing starts;
Figures D.1-D.4 show all seven variables of the same files.

| Paper object | Output file | Script |
|---|---|---|
| Figure 1 (a)-(c); Figure D.1 | `irf_comp_national.png`, `irf_comp_regional.png`, `irf_comp_noaa.png` | `04a_figures_irf.R` |
| Figure 2 (a)-(c); Figure D.2 | `irf_rank_national.png`, `irf_rank_regional.png`, `irf_rank_noaa.png` | `04a_figures_irf.R` |
| Figure 3, top panel (from 1965:M12) | `fitted_aci.png` | `04b_figures_series_weights.R` |
| Figure 3 (a), (b) | `weights_comp_aci.png`, `weights_rank_aci.png` | `04b_figures_series_weights.R` |
| Figure 4, top panel | `fitted_noaa.png` | `04b_figures_series_weights.R` |
| Figure 4 (a), (b) | `weights_comp_noaa.png`, `weights_rank_noaa.png` | `04b_figures_series_weights.R` |
| Figure A.1 | `boot_weights_<spec>.png` (one file per panel) | `05b_figures_bootstrap.R` |
| Figure A.2 | `boot_index_<spec>.png` (one file per panel) | `05b_figures_bootstrap.R` |
| Figure A.3 (a)-(c); Figure D.3 | `irfboot_comp_national.png`, `irfboot_comp_regional.png`, `irfboot_comp_noaa.png` | `05a_figures_irfboot.R` |
| Figure A.4 (a)-(c); Figure D.4 | `irfboot_rank_national.png`, `irfboot_rank_regional.png`, `irfboot_rank_noaa.png` | `05a_figures_irfboot.R` |
| Figure A.5 | `expanding_weights_<spec>.png` (one file per panel) | `05b_figures_bootstrap.R` |
| Figure B.1 | `rank_usage_noaa.png` | `05b_figures_bootstrap.R` |
| Table C.1; Table C.2 | `data/labels_noaa.csv`, columns `region_raw` -> `region_agg`; `variable_raw` -> `variable_agg` | supplied definition |
| In-text numbers | `results/summary_numbers.txt` | `06_summary_numbers.R` |

Inputs: Figures 1, 2, D.1 and D.2 take point responses and bands from the supplied
`results/irf_bands/`; Figures A.3, A.4, D.3 and D.4 take point responses from the same files and
bands from the pairs-bootstrap draws in `results/bootstrap/` (task 1). Figures A.1, A.2 and B.1 show
the point estimates of `results/point_estimates/` with the supplied bootstrap draws; Figure A.5 uses
the expanding windows (task 2).

## 7. References (data citations)

- American Academy of Actuaries, Canadian Institute of Actuaries, Casualty Actuarial Society and
  Society of Actuaries (2025). Actuaries Climate Index [dataset]. https://actuariesclimateindex.org
  (accessed 21 January 2026).
- NOAA National Centers for Environmental Information (2026). Climate at a Glance: Regional Time
  Series [dataset]. https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/regional/time-series
  (retrieved via Macrobond, February 2026).
- Vose, R. S., S. Applequist, M. Squires, I. Durre, M. J. Menne, C. N. Williams Jr., C. Fenimore,
  K. Gleason and D. Arndt (2014). NOAA Monthly U.S. Climate Divisional Database (NClimDiv) [dataset].
  NOAA National Climatic Data Center. https://doi.org/10.7289/V5M32STR.
- Lan, X. (NOAA Global Monitoring Laboratory) and R. Keeling (Scripps Institution of Oceanography)
  (2026). Monthly mean CO2 at Mauna Loa Observatory [dataset]. https://gml.noaa.gov/ccgg/trends/
  (retrieved via Macrobond, February 2026).
- Macrobond Financial AB (2026). Macrobond [database]. https://www.macrobond.com (accessed February
  2026).
- McCracken, M. W. and S. Ng (2016). FRED-MD: A monthly database for macroeconomic research. *Journal
  of Business & Economic Statistics* 34(4), 574-589. https://doi.org/10.1080/07350015.2015.1086655.
- Federal Reserve Bank of St. Louis (2025). FRED-MD, vintage 2025-12 [dataset].
  https://www.stlouisfed.org/research/economists/mccracken/fred-databases (accessed 3 October 2026).
- Wu, J. C. and F. D. Xia (2016). Measuring the macroeconomic impact of monetary policy at the zero
  lower bound. *Journal of Money, Credit and Banking* 48(2-3), 253-291.
  https://doi.org/10.1111/jmcb.12300.
- Federal Reserve Bank of Atlanta (2022). Wu-Xia Shadow Federal Funds Rate [dataset].
  https://www.atlantafed.org/research-and-data/data/wu-xia-shadow-federal-funds-rate (accessed
  3 October 2026).
- National Bureau of Economic Research (2026). US Business Cycle Expansions and Contractions
  [dataset]. https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions
  (accessed 1 October 2026).
