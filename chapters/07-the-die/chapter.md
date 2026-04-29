# Chapter 7: The six-sided die

- Carried from Chapter 6
  - Two outcomes was cramped. Six gives us more interesting failure modes -- including a brand new headache called "multiple comparisons".

# Loop A: face counts wobble

- Try
  - Roll a fair die 60, 600, and 6000 times. Count each face. The expected count is N/6. The actual counts wobble.
- Observe
  - At N = 60 some faces appear 7 times, others 14. The wobble is huge as a fraction of the expected (10).
  - At N = 600 every face is in the 80-120 range. Still visible wobble; not enough to spook anyone.
  - At N = 6000 every face is within 1-2% of 1000.
  - ![Face counts wobble](images/count_wobble.png)
- Hunch
  - The same regression-to-mean we saw with the coin, only across six categories. Variance per face is approximately N * (1/6) * (5/6).

# Loop B: chi-square goodness-of-fit

- Try
  - We need a test that asks "is the whole vector of face frequencies consistent with uniform 1/6?". That's chi-square goodness-of-fit. Apply it to a fair die and to a loaded die (face 6 has p = 1/3, the others share 2/3) at increasing N.
- Observe
  - For the fair die, p-values bounce around above 0.05. They do dip below 0.05 occasionally -- that's our 5% type-I rate doing its job.
  - For the loaded die, p-values start above 0.05 (small N can't see it) but drop steadily as N grows. By N ~ 200 the test reliably rejects.
  - ![Chi-square p-values](images/chi2_pvalues.png)

# Loop C: Dirichlet-multinomial, the Bayesian counterpart

- Try
  - The conjugate analogue of Beta-binomial in the multinomial world is Dirichlet-multinomial. With a Dirichlet(1, 1, 1, 1, 1, 1) prior and observed counts, the posterior is Dirichlet(1 + c1, 1 + c2, ..., 1 + c6).
  - Plot the posterior marginal for each face on the same axes for the loaded-die data with N = 600.
- Observe
  - Faces 1-5 each have posterior marginals concentrated near 0.13 (slightly below 1/6 because face 6 ate the mass). The face-6 posterior is concentrated near 0.33.
  - The fair line at 1/6 sits inside the posteriors for faces 1-5 and well outside the face-6 posterior.
  - ![Dirichlet posterior](images/dirichlet_posterior.png)
- Compare
  - The Bayesian view answers "what's plausible for each face?" directly. The frequentist chi-square answers "is the whole vector consistent with fair?". Different questions, both useful. The Bayesian view also avoids the pitfall in the next loop.

# Loop D: multiple comparisons -- a frequentist trap

- Try
  - Suppose we test each face individually, using a binomial test against H0: p = 1/6. We test six hypotheses, each at alpha = 0.05. Run this 1,000 times on simulated *fair* dice and count how often at least one face gets falsely flagged.
- Observe
  - Naive: about 21-23% of the time at least one face is falsely flagged. We expected 5%. We got over 4x that.
  - Bonferroni-corrected (each test at 0.05/6 = 0.0083): about 4% of the time, right around the nominal 5% bound.
  - ![Multiple comparisons](images/multiple_comparisons.png)
- Bayesian counterpart
  - The Dirichlet posterior is a single joint object. Asking "is face 6 unusually high?" is reading a marginal of that joint. The marginal credible intervals already account for the others. There's no separate multiple-comparisons knob to turn -- the prior + likelihood machinery handles the joint correctly by construction.
- Probe an edge case
  - Bonferroni is conservative. At 100 tests, alpha/100 = 0.0005 per test, which kills power. Real-world multiple-testing strategies (Holm, Benjamini-Hochberg) trade some of this conservatism for power. The Bayesian view sidesteps it differently.

# The big question that opens Chapter 8

- We tested whether one die is fair. The next move: two dice (or two coins, or two website variants). Is variant B different from variant A? That's an A/B test.
- Big question: how do we go from "is this one thing fair?" to "is this thing different from that thing?"

# Notebook and data

- Companion notebook: [`notebook.ipynb`](notebook.ipynb)
- Generation script: [`generate.py`](generate.py)
