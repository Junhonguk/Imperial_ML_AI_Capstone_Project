# Literature behind each component

Each entry below is a method used in this project, with the code that uses
it and its reference.

**Gaussian-process regression, Matérn 5/2 kernel, ARD**
- Used in: `src/bbo/surrogates.py` (`fit_gp`).
- Reference: Rasmussen, C. E. & Williams, C. K. I. (2006). *Gaussian Processes
  for Machine Learning*. MIT Press. Ch. 4–5 (Matérn kernels, automatic
  relevance determination, marginal-likelihood fitting).

**Bayesian optimisation with a GP surrogate**
- Used in: `scripts/weekly_run.py` (overall loop).
- References:
  - Snoek, J., Larochelle, H. & Adams, R. P. (2012). Practical Bayesian
    optimization of machine learning algorithms. *NeurIPS*. Argues for
    Matérn 5/2 over the squared-exponential kernel.
  - Shahriari, B., Swersky, K., Wang, Z., Adams, R. P. & de Freitas, N.
    (2016). Taking the human out of the loop: a review of Bayesian
    optimization. *Proc. IEEE* 104(1).

**Expected Improvement and the exploration margin ξ**
- Used in: `src/bbo/acquisition.py` (`expected_improvement`, `propose`).
- References:
  - Močkus, J. (1975/1978). On Bayesian methods for seeking the extremum.
  - Jones, D. R., Schonlau, M. & Welch, W. J. (1998). Efficient global
    optimization of expensive black-box functions. *J. Global Optimization*
    13. The closed-form EI used here.
  - Lizotte, D. (2008). *Practical Bayesian Optimization* (PhD thesis). The
    effect of ξ.

**Trust regions in place of global acquisition**
- Used in: the `trust_region` regime in `config.py`; the box arguments of
  `propose`.
- Reference: Eriksson, D., Pearce, M., Gardner, J., Turner, R. D. &
  Poloczek, M. (2019). Scalable global optimization via local Bayesian
  optimization (TuRBO). *NeurIPS*. This project uses a simplified version:
  one box per function, ×1.5 on a record and ×0.5 on a miss, with the box
  sizes kept by hand rather than by counters.

**Output transforms for heavy-tailed objectives**
- Used in: `surrogates.transform` (`log`, `logabs`).
- Reference: Snelson, E., Ghahramani, Z. & Rasmussen, C. (2004). Warped
  Gaussian processes. *NeurIPS*. A fixed log warp is the simplest case.

**Local quadratic and response-surface models**
- Used in: `src/bbo/triangulation.py` (`isotropic_fit`, `consensus_centre`).
- References:
  - Box, G. E. P. & Wilson, K. B. (1951). On the experimental attainment of
    optimum conditions. *JRSS B* 13. Second-order response surfaces near an
    optimum.
  - Powell, M. J. D. (2002). UOBYQA: unconstrained optimization by quadratic
    approximation. *Math. Programming* 92. Model-based derivative-free steps.

**Calibration of predictive uncertainty**
- Used in: `results/calibration.md` (weekly hit rate against stated ranges).
- Reference: Gneiting, T., Balabdaoui, F. & Raftery, A. E. (2007).
  Probabilistic forecasts, calibration and sharpness. *JRSS B* 69.

**Documentation templates**
- Used in: `model_card.md`, `datasheets/`.
- References:
  - Mitchell, M. et al. (2019). Model cards for model reporting. *FAT\**.
  - Gebru, T. et al. (2021). Datasheets for datasets. *CACM* 64(12).
