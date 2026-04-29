# Chapter 16: Metric quality -- noise, variance, stability, predictivity

## Carried from Chapter 15

- We want metrics that move when the world moves and stay still when it doesn't.
## Inquiry loops planned

- Loop A: variance. Three candidate metrics for the same underlying user value. Their variance differs by 10x. Simulate the same true effect; the high-variance metric requires 10x more users to detect.
- Loop B: variance reduction with CUPED. Use a pre-experiment covariate (last week's behavior) to soak up variance. Re-do the same detection task. Watch sample-size requirements drop.
- Loop C: stability. Run a series of A/A tests (no real treatment). The spread of "effects" we see by chance tells us our floor.
- Loop D: predictivity. Pair short-term and long-term metric changes from many simulated experiments. Some short-term metrics correlate with long-term outcomes. Most don't. Build a small predictivity scorer.
- Loop E: Bayesian flavor. A hierarchical model that treats short-term reads as noisy measurements of a long-term effect.
- Big question: my user clicks today and converts in 30 days. Who deserves the credit? (Attribution.)
## expkit modules used

- expkit.metrics.variance (NEW): CUPED, stratified estimators
- expkit.metrics.quality (NEW): predictivity diagnostics
