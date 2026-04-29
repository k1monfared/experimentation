# Chapter 6: The Bayesian view, formalized

## Carried from Chapter 5

- We have been using "posterior" intuitively for five chapters. Time to formalize.
## Inquiry loops planned

- Loop A: prior + likelihood -> posterior, using PyMC explicitly. Show the model code. Inspect the trace with arviz.
- Loop B: priors that argue. Beta(1,1) flat, Beta(50,50) skeptical, Beta(2,8) "I expect tails", Beta(8,2) "I expect heads". Same 6/10 data. Plot four posteriors on one chart.
- Loop C: when does the prior stop mattering? Re-run Loop B with N = 1000. Posteriors collapse onto each other.
- Loop D: Bayes factor. Fair-vs-biased model comparison. What does it mean? Compare to p-value side-by-side.
- Loop E: probe edge cases. What if my prior is wrong? Show a worst-case mismatched prior under tiny N -- it can mislead.
- Big question: every chapter so far had two outcomes (heads/tails). What changes if we have six? Or fifty?
## expkit modules used

- expkit.inference.bayes (existing); expanded with bayes_factor, model comparison helpers
- arviz for diagnostics
