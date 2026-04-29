# Chapter 3: What if it's biased? (Power and sample size)

## Carried from Chapter 2

- We figured out how strict our threshold should be. But strictness alone doesn't tell us if we'll detect a real bias. How many tosses does it take?
## Inquiry loops planned

- Loop A: simulate detecting p = 0.55 vs the null at increasing N. Plot the detection rate (1 - beta).
- Loop B: try smaller effects (0.51, 0.52, 0.53). Watch the curve flatten. Sample size scales like 1/effect^2.
- Loop C: pose the inverse: "what effect size can I detect with N = 1000 at 80% power?" Build the minimum-detectable-effect (MDE) tool.
- Loop D: Bayesian-flavored stopping rule. Run experiments until the posterior credible interval is narrower than some target, OR until the posterior probability of "p > some threshold" is decisive. How many tosses does that take on average vs the fixed-N frequentist approach?
- Big question: when these tests disagree, what do they actually disagree about?
## expkit modules used

- expkit.sim.coin
- expkit.power.binomial (NEW): power_for_proportion, mde_for_proportion
- expkit.inference.binomial, expkit.inference.bayes
