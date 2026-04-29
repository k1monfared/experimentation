# Chapter 2: How sure can I be?

## Carried from Chapter 1

- We saw 6 heads in 10 tosses. The frequentist said "p-value is 0.75, not rare". The Bayesian said "posterior probability of bias is 0.73". Two different answers to almost the same question. We hand-waved past it. Now we make it precise.
## Inquiry loops planned

- Loop A: define the null. Toss a fair coin many times. Plot the sampling distribution of head counts under H0. Mark the rejection region for alpha = 0.05.
  - Frequentist: type I error, p-value, two-sided vs one-sided.
  - Bayesian: posterior P(p > 0.5), credible interval, ROPE (region of practical equivalence).
- Loop B: probe a slightly biased coin. What fraction of experiments would catch it? What fraction would miss?
  - Frequentist: type II error, the cost of being too strict.
  - Bayesian: probability that the true coin sits inside the ROPE.
- Loop C: vary alpha (0.1, 0.05, 0.01). Watch the rejection region grow and shrink. Same for credible-interval level.
- Loop D: simulate 10,000 experiments. Count how often each lens declares "rigged" when the coin is actually fair (false positives) and when the coin is biased (true positives).
- Big question: how many tosses does it take to reliably catch a small bias?
## expkit modules used

- expkit.sim.coin (already exists)
- expkit.inference.binomial (already exists, exact + normal-approx)
- expkit.inference.bayes (already exists; PyMC + closed form)
- new: a small simulation harness for repeated experiments under a given truth, returning rejection rate / posterior summary aggregates
