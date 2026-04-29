# Chapter 4: The family of tests

- Carried from Chapter 3
  - Same data, multiple tests. When do they tell the same story? When do they diverge?
- Five tests we will use through the rest of the book
  - Exact binomial test. Compute the actual probability under H0 of a result this extreme. No approximation. The gold standard for proportions.
  - Normal-approximation z-test. Treat the binomial as approximately normal. Fast and easy. Lies in the small-N or extreme-fraction corners.
  - Chi-square goodness-of-fit. Compare observed (heads, tails) to expected (n/2, n/2). Asymptotic.
  - Fisher exact test. Treat our 2x2 (observed vs an "ideal fair" reference of equal size) as a contingency table.
  - One-sample t-test on the 0/1 sequence. Treats each toss as a continuous draw. Wrong-shape model on purpose; useful for comparison.
  - Plus a Bayesian counterpart for each (the conjugate Beta posterior on p, with PyMC available for harder problems).

# Loop A: same data, every test

- Try
  - Five tests, four scenarios: 6/10, 60/100, 600/1000, 6000/10000. All test H0: p = 0.5.
- Observe
  - At 6/10 the tests all agree: nothing to see (p-values 0.50 to 0.85). Eyeball the chart -- the bars are above the alpha line in every test.
  - At 60/100 the tests start to disagree on degree. Exact binomial says 0.057 (just barely doesn't reject). Normal-approx says 0.046 (reject). Chi-square says 0.046. Fisher says 0.157 (because the reference 50/50 has variance too). t-test says 0.045.
  - At 600/1000, every test rejects strongly (p well below 1e-9). They are now indistinguishable in their conclusion.
  - At 6000/10000 every test rejects to numerical zero.
  - ![p-value grid](images/pvalue_grid.png)
- Hunch
  - Tests can disagree about *whether* to reject right at the boundary. They almost never disagree about *clear* signals or *clear* nulls.

# Loop B: where does normal-approximation lie?

- Try
  - Compute the absolute difference between exact-binomial and normal-approx p-values across (k, n) for n = 10, 25, 50, 100, 250, 500, 1000.
- Observe
  - At n = 10, normal-approx and exact diverge by up to 0.2 in p-value at the extremes. Useless near the boundary.
  - At n = 50, they agree to within 0.05 except at the very ends. Borderline.
  - At n = 250 and beyond, they agree to within 0.01 across the whole range. Essentially interchangeable.
  - ![Normal vs exact](images/normal_vs_exact.png)
- Rule of thumb
  - The textbook rule "use normal-approx when n*p > 5 and n*(1-p) > 5" is a decent approximation of where this plot becomes flat. For automated tooling, prefer exact when feasible -- modern computers do not care.

# Loop C: edge cases

- Try
  - 0/10. 10/10. 1/1. 0/100. 100/100. Run all five tests on each. See what breaks.
- Observe
  - 1/1: t-test breaks (zero variance, NaN). The other four still produce sensible numbers.
  - 0/10 and 10/10: every test reports a small p-value (extreme observations are extreme). But the magnitudes vary wildly. Exact binomial says ~0.002. Normal-approx says ~0 (incorrectly extreme). t-test breaks (zero variance again).
  - 0/100 and 100/100: same shape, exact and chi-square both correctly tiny, normal-approx underestimates the p-value (it thinks the data is more extreme than it is).
  - ![Edge cases](images/edge_cases.png)
- Hunch
  - When in doubt, prefer the exact test. Use the approximations when speed matters and N is large enough that they have caught up.

# Loop D: the Bayesian view of the same data

- Try
  - For each of 6/10, 60/100, 600/1000, 6000/10000, compute the Beta posterior under a flat Beta(1,1) prior. Plot the posterior, mark the 95% credible interval, mark p = 0.5.
- Observe
  - At 6/10: posterior Beta(7, 5), wide, centred at 0.58. The 95% CI ranges from about 0.32 to 0.81. p = 0.5 is comfortably inside.
  - At 60/100: posterior Beta(61, 41), centred at 0.598, 95% CI [0.50, 0.69]. p = 0.5 is right on the boundary -- echoing the borderline frequentist result.
  - At 600/1000: posterior Beta(601, 401), narrow, centred at 0.60, 95% CI [0.57, 0.63]. p = 0.5 is far outside.
  - At 6000/10000: vanishingly narrow around 0.60.
  - ![Bayesian view](images/bayes_alongside.png)
- Compare
  - The frequentist tests asked "is the data surprising under p = 0.5?" The Bayesian asks "is p = 0.5 plausible given the data?" The answers track each other closely, especially at large N. The disagreement at 60/100 is not a flaw in either lens; it is a genuinely borderline case where reasonable analysts might disagree.

# The big question that opens Chapter 5

- Tests answer "can I reject this specific H0?". They tell us about a single point. But what we often want is a range: not "can I rule out 0.5?" but "what range of p values can I rule out, and what range is plausible?"
- That's the dual move: from a test to an interval.
- Big question: instead of asking "rejected or not", what's the full set of values the data is consistent with?

# Notebook and data

- Companion notebook: [`notebook.ipynb`](notebook.ipynb)
- Generation script: [`generate.py`](generate.py)
