# Chapter 18: Frequentist vs Bayesian -- would we ship differently?

## Carried from Chapter 17

- We've shown both lenses on every problem. Now we ask: in practice, does the choice of lens change what we ship?
## Inquiry loops planned

- Loop A: simulator harness. Run 1,000 synthetic A/B tests where the true effect is drawn from a population (some null, some +0.1pp, some +1pp, some -0.5pp, ...). For each one, record:
  - frequentist decision: does p < 0.05 with the planned N?
  - Bayesian decision: is P(treatment - control > minimum-meaningful-effect) > some-threshold?
  - what was the true effect?
- Loop B: confusion matrix. For each lens, count (true positive ship, false positive ship, true negative pass, false negative pass). Visualize.
- Loop C: cost analysis. Each false-positive ship costs C1; each missed-win costs C2; each test takes time T. Compute expected-cost-per-decision under each lens. Vary the threshold and watch the front move.
- Loop D: dependence on prior. Sweep over Bayesian priors. For weakly informative ones, the two lenses ship near-identically. For strongly informative ones, they diverge sharply.
- Loop E: the case for both. Run as a joint decision rule: "ship only if frequentist passes AND Bayesian posterior probability of effect > 95%". Show the cost-and-error tradeoff vs single-lens rules.
- Big question: there are still questions experiments can't answer. Causality, long horizons, network effects, observational data. That's a different toolbox.
## expkit modules used

- all the above modules; this is the capstone
- expkit.sim.abtest (large batch generator), expkit.inference.* both lenses
