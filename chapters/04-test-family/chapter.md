# Chapter 4: The family of tests

## Carried from Chapter 3

- Same coin, same data: when do different tests agree? When do they tell different stories, and why?
## Inquiry loops planned

- Loop A: 6/10 in five different machines. Exact binomial test, normal-approximation z-test, chi-square goodness-of-fit, Fisher exact (vs an "ideal" 50/50), one-sample t-test on the fraction. Side-by-side p-values.
- Loop B: scale up. Same five tests at N = 100, 1000, 10000. Where does the normal approximation start to lie? Where does Fisher exact stop being feasible?
- Loop C: edge probe. Tiny N (3). Asymmetric counts (9/10). What breaks?
- Loop D: Bayesian counterparts. Beta-binomial conjugate; PyMC for the Bernoulli model directly. Same data, same answer (modulo prior choice).
- Big question: under the hood these all carve up the same evidence. What if instead of asking "is it surprising?" we ask "what values of p are plausible?"
## expkit modules used

- expkit.inference.binomial (existing), expkit.inference.normal (NEW), expkit.inference.chi2 (NEW), expkit.inference.fisher (NEW)
- expkit.inference.bayes (existing)
