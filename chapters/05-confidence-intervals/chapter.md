# Chapter 5: Confidence intervals -- the dual of tests

## Carried from Chapter 4

- Tests answer "can I rule this out?". Intervals answer "what can't I rule out?". They are two sides of the same coin (the coin we have been tossing).
## Inquiry loops planned

- Loop A: compute Wald, Wilson, Clopper-Pearson, and bootstrap CIs at N = 10, 100, 1000 with 6/10, 60/100, 600/1000.
- Loop B: probe near boundaries. 0/10. 10/10. Where does Wald fail? Where does Clopper-Pearson over-cover?
- Loop C: Bayesian credible interval (uniform prior, then Jeffreys, then a strongly informative prior). Visualize the same data with three priors.
- Loop D: simulate 10,000 fair-coin experiments. Count how often each interval contains the truth. The good ones cover at least 95% of the time.
- Big question: instead of "ruling out", what if we want to update a belief?
## expkit modules used

- expkit.inference.binomial (existing): wilson, clopper_pearson
- expkit.inference.bootstrap (NEW)
- expkit.inference.bayes (existing)
