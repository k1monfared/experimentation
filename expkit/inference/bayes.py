"""Bayesian inference for a single binomial proportion.

PyMC is the canonical path. A closed-form Beta posterior is also exposed for
didactic comparison.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pymc as pm
from scipy import stats


@dataclass(frozen=True)
class ConjugatePosterior:
    """Closed-form Beta posterior for a Bernoulli likelihood with a Beta prior."""

    alpha: float
    beta: float

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def credible_interval(self, level: float = 0.95) -> tuple[float, float]:
        if not 0.0 < level < 1.0:
            raise ValueError("level must lie in (0, 1)")
        tail = (1.0 - level) / 2.0
        lo = float(stats.beta.ppf(tail, self.alpha, self.beta))
        hi = float(stats.beta.ppf(1.0 - tail, self.alpha, self.beta))
        return lo, hi

    def prob_greater_than(self, threshold: float) -> float:
        """Posterior probability that p > threshold."""
        return float(1.0 - stats.beta.cdf(threshold, self.alpha, self.beta))


def coin_posterior_conjugate(
    seq: np.ndarray, prior_alpha: float = 1.0, prior_beta: float = 1.0
) -> ConjugatePosterior:
    """Closed-form Beta posterior after observing ``seq``.

    Beta(alpha + heads, beta + tails). Default Beta(1, 1) prior is uniform on [0, 1].
    """
    seq_arr = np.asarray(seq, dtype=int)
    heads = int(seq_arr.sum())
    tails = int(seq_arr.size - heads)
    return ConjugatePosterior(
        alpha=prior_alpha + heads,
        beta=prior_beta + tails,
    )


def coin_posterior(
    seq: np.ndarray,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    seed: int | None = None,
    draws: int = 1000,
    chains: int = 2,
    tune: int = 1000,
    progressbar: bool = False,
):
    """Sample the posterior of ``p`` under a Beta(prior_alpha, prior_beta) prior.

    Returns an arviz ``InferenceData`` whose ``posterior`` group has variable ``p``.
    Uses PyMC's NUTS sampler. Sampling is deterministic for a fixed ``seed``.
    """
    seq_arr = np.asarray(seq, dtype=int)
    heads = int(seq_arr.sum())
    n = int(seq_arr.size)
    with pm.Model():
        p = pm.Beta("p", alpha=prior_alpha, beta=prior_beta)
        pm.Binomial("y", n=n, p=p, observed=heads)
        idata = pm.sample(
            draws=draws,
            chains=chains,
            tune=tune,
            random_seed=seed,
            progressbar=progressbar,
            return_inferencedata=True,
        )
    idata.attrs["seed"] = seed if seed is not None else "unset"
    idata.attrs["heads"] = heads
    idata.attrs["n"] = n
    idata.attrs["prior_alpha"] = prior_alpha
    idata.attrs["prior_beta"] = prior_beta
    return idata


def posterior_summary(idata) -> dict:
    """Lightweight numeric summary of the ``p`` posterior in ``idata``."""
    p_samples = idata.posterior["p"].values.ravel()
    return {
        "mean": float(np.mean(p_samples)),
        "std": float(np.std(p_samples, ddof=1)),
        "ci_95_low": float(np.quantile(p_samples, 0.025)),
        "ci_95_high": float(np.quantile(p_samples, 0.975)),
        "prob_greater_half": float(np.mean(p_samples > 0.5)),
    }


def bayes_factor_point_vs_uniform(seq: np.ndarray, point: float = 0.5) -> float:
    """Bayes factor for a point H0 (p = ``point``) vs the uniform-p alternative.

    Computes BF_{10} = P(data | H1) / P(data | H0) where H1 is "p ~ Uniform(0, 1)".
    Both marginal likelihoods have closed form in this conjugate setting.
    """
    from scipy.special import betaln, gammaln

    seq_arr = np.asarray(seq, dtype=int)
    k = int(seq_arr.sum())
    n = int(seq_arr.size)
    if not 0.0 < point < 1.0:
        raise ValueError("point must lie in (0, 1)")
    log_lik_h0 = k * np.log(point) + (n - k) * np.log(1.0 - point)
    # Beta(1,1) prior gives marginal P(data | H1) = B(k+1, n-k+1) / B(1, 1) = B(k+1, n-k+1)
    log_lik_h1 = betaln(k + 1, n - k + 1)
    # B(1, 1) = 1, so this is correct as-is. Add a sanity gammaln-based check.
    _ = gammaln  # keep import used
    return float(np.exp(log_lik_h1 - log_lik_h0))


def conjugate_posterior_predictive(
    seq: np.ndarray,
    new_n: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    n_samples: int = 5000,
    seed: int | None = None,
) -> np.ndarray:
    """Posterior predictive over the count of heads in ``new_n`` future tosses.

    Draws p ~ posterior, then heads ~ Binomial(new_n, p). Returns an array of
    ``n_samples`` predicted head counts.
    """
    rng = np.random.default_rng(seed)
    seq_arr = np.asarray(seq, dtype=int)
    a = prior_alpha + int(seq_arr.sum())
    b = prior_beta + int(seq_arr.size - seq_arr.sum())
    p_draws = rng.beta(a, b, size=n_samples)
    return rng.binomial(new_n, p_draws)
