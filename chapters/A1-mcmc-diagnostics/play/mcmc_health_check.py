"""Check the health of a PyMC MCMC run on a simple coin-bias model.

Run the sampler on coin-toss data and inspect R-hat, ESS, and divergences.
Try changing N_TOSSES to very small (10) to see the sampler struggle.

To play, run:

    python chapters/A1-mcmc-diagnostics/play/mcmc_health_check.py
"""

N_TOSSES = 100
N_HEADS = 60
N_DRAWS = 2000
N_TUNE = 1000
N_CHAINS = 4

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np


def main():
    try:
        import pymc as pm
        import arviz as az
    except ImportError:
        print("PyMC and arviz are required. Install with: pip install pymc arviz"); return

    print(f"\nFitting Beta(1,1) + Binomial model: {N_HEADS} heads in {N_TOSSES} tosses")
    with pm.Model():
        p = pm.Beta("p", alpha=1, beta=1)
        pm.Binomial("obs", n=N_TOSSES, p=p, observed=N_HEADS)
        idata = pm.sample(N_DRAWS, tune=N_TUNE, chains=N_CHAINS, random_seed=0,
                          progressbar=True, target_accept=0.9)
    summary = az.summary(idata, var_names=["p"])
    divs = int(idata.sample_stats["diverging"].sum().item())
    print(f"\nR-hat (p): {summary['r_hat'].values[0]:.4f}  (good if < 1.01)")
    print(f"ESS bulk (p): {summary['ess_bulk'].values[0]:.0f}  (good if > 400)")
    print(f"Divergences: {divs}  (good if 0)")
    if summary['r_hat'].values[0] > 1.01:
        print(f"\nWARNING: R-hat > 1.01. Chains have not converged. Results are unreliable.")
    else:
        print(f"\nChains healthy. Posterior mean: {float(idata.posterior['p'].mean()):.4f}")


if __name__ == "__main__":
    main()
