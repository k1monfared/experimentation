# When the computer is doing the math, how do I know it is doing it right?

Most of the Bayesian results in the book have come out of computer simulations. I write down a model, hand it to a sampler, get back a histogram of the posterior, and read off the answer. The sampler does the work I cannot do by hand.

The catch: samplers can fail, and a failing sampler can give back a histogram that looks right but is not. The Bayesian framework is rigorous. The implementation has bugs. This appendix is about how to tell the two apart.

Real-world stage first.

In 2014, a published Bayesian analysis of a complex hierarchical psychology dataset used MCMC sampling that, on later inspection, had not converged. The original conclusions were partly wrong, and the reanalysis (with a corrected sampler) gave different numbers. The error was not in the model. it was in the implementation.

Bayesian software libraries (PyMC, Stan, JAGS) all build in convergence diagnostics that check for sampler health. These diagnostics catch most failures, but not all. A user who runs the sampler without checking the diagnostics is trusting that everything went right.

In each of these places, the diagnostics are the line between "the computer is producing reliable answers" and "the computer is producing answers that look reliable but are not".

The basic problem is that MCMC samplers approximate the posterior by drawing samples from a Markov chain that is supposed to converge to the target distribution. Convergence is not guaranteed in finite time. A chain that has not converged can produce histograms that drift, that have different shapes in different segments, or that miss parts of the distribution entirely.

The standard diagnostics are:

R-hat (potential scale reduction factor): a measure of whether multiple chains, started from different points, have converged to the same distribution. R-hat near 1.0 (typically below 1.01 or 1.05) is good. R-hat above 1.1 or so is a warning.

Effective sample size (ESS): a measure of how many independent samples the chain has effectively produced. If a chain has 4000 draws but is highly autocorrelated, the effective sample size might be 200, meaning the variance of any quantity computed from the chain is what 200 independent samples would give. ESS in the hundreds is usually fine for moderate-precision applications. ESS below 100 is a warning.

Divergences: in the specific case of Hamiltonian Monte Carlo (HMC) and its descendant the No-U-Turn Sampler (NUTS), the algorithm sometimes detects that the proposed step would have to integrate over high-curvature regions to be accurate. These detections are flagged as divergences. A small number of divergences is usually fine. many divergences are a warning that the model has a difficult geometry.

Trace plots: a plot of each parameter's value across the iterations. A healthy trace looks like a fuzzy caterpillar, mixing freely. An unhealthy trace shows long sticky regions, drift, or clear separation between chains.

The simplest thing to do is to print these diagnostics for every model. PyMC has a `summary` function that does this. If R-hat is fine, ESS is large enough, and divergences are zero or few, the inference can be trusted. If any of these is off, the model needs work.

What does "the model needs work" look like? Often the fix is to reparameterize. Hierarchical models with the "centered parameterization" (each lower-level parameter is expressed as a draw from a population distribution) are notoriously hard to sample. The "non-centered parameterization" (each lower-level parameter is expressed as a population-level mean plus a standardized deviation) often samples much better. The math is the same. the geometry is different.

Other fixes include longer warmup, tighter priors, simpler models, or moving from MCMC to variational inference for very high-dimensional cases.

This appendix is short because the practical advice is brief: check your diagnostics. PyMC, Stan, and similar tools make this easy. Don't trust a posterior you have not diagnosed.

The deeper takeaway: Bayesian inference is a framework. Running the framework on a computer requires implementation discipline. The framework is correct. the implementation has gotchas. The diagnostics are how I tell which is which.

There is no forward question for an appendix. The book ends with Chapter 19. The appendix is a tool for using the Bayesian machinery rigorously.
