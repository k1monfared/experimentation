# Chapter 8: From dice to A/B tests

## Carried from Chapter 7

- Two coins, two dice, two website variants. Same problem: are these from the same underlying distribution, or different?
## Inquiry loops planned

- Loop A: two-proportion test on conversion rates. 5% vs 5.5% with 1000 users per arm. What does each lens say?
- Loop B: scale up: 10000 users per arm. The same effect becomes detectable.
- Loop C: continuous outcomes -- average revenue per user. Two-sample t-test, Mann-Whitney U, posterior on the difference of means with weakly informative priors via PyMC.
- Loop D: stratification. Same population, but split by region. Within-stratum effects can be different. Pooled vs stratified analysis.
- Loop E: Bayesian decision rule. "Ship if P(treatment > control + minimum-meaningful-effect) > 0.95". Compare to "p < 0.05".
- Big question: experiments work in the lab, but real studies make claims like "wine is good for your heart". What's different about that claim?
## expkit modules used

- expkit.sim.abtest (NEW): two-arm experiment generator (binary + continuous outcomes)
- expkit.inference.normal (NEW: two-proportion z, two-sample t)
- expkit.inference.bayes (PyMC two-arm model)
