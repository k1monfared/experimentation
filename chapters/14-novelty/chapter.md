# Chapter 14: Novelty effects

- Carried from Chapter 13
  - The lie evolves over time. The most famous form: novelty.

# Loop A: three views of one event log

- Try
  - Simulate a treatment whose true long-run lift is 0. The first day a user sees the new feature, they over-engage by +6pp; this excitement decays with a 5-day half-life. Run for 40 days, 2,000 users with random arrival.
  - Now read the same event log three different ways:
    - by calendar day from launch
    - by per-user days since first exposure
    - by per-user exposure count
- Observe
  - Calendar day view: the early days show a treatment lift; the lift fades by day ~20 because by then most treatment users have been exposed for a while. By day 40 the curves cross.
  - Days-since-exposure view: starts at +6pp on day-1, decays to ~0 by day 20. The shape of the decay is visible directly.
  - Exposure-count view: 1st exposure shows the maximum lift; later exposures show progressively less. Same story, different x-axis.
  - ![Three views](images/three_views.png)
- Hunch
  - The same event log can support "treatment is great!" or "treatment did nothing" depending entirely on the chosen aggregation axis.

# Loop B: which view is "right"?

- Observe
  - Calendar-day is what dashboards typically show, but it confounds calendar effects with user-tenure effects.
  - Days-since-exposure is the cleanest read of what each individual user experiences. But it requires per-user start-date tracking.
  - Exposure-count cleans out time entirely. Useful for asking "do users habituate?".
- Hunch
  - There is no single right view. Different views answer different questions. Pretending one is the answer is the source of most novelty-related disagreements.

# Loop C: it's not always decay

- Try
  - Simulate three different shapes: decay (the classic novelty effect), primacy (a slow ramp-up as users learn the feature), and a U-shape (initial curiosity, then a confused dip, then recovery).
- Observe
  - All three are plausible. Real-world data often looks like a mixture.
  - ![Decay shapes](images/decay_shapes.png)
- Hunch
  - "Wait until novelty wears off" is fine if the truth is exhibit A. Catastrophic if the truth is exhibit B (you ship too early) or exhibit C (you give up too early).

# Two-lens commentary

- Frequentist: typically tries to estimate the asymptote by truncating the early days. Sensitive to where you cut.
- Bayesian: a hierarchical model where each user has a (latent) decay shape, with population-level priors on time-to-asymptote. Posterior over the asymptotic effect marginalizes over decay-shape uncertainty.
- Both work; the Bayesian version is more honest about uncertainty in the asymptote when the experiment is short.

# The big question that opens Chapter 15

- We just assumed every user actually saw the new feature. They don't. Most users in an experiment don't visit the page where the change happens.
- Big question: what happens when "in the experiment" doesn't mean "exposed to the change"?

# Notebook and data

- Companion notebook: [`notebook.ipynb`](notebook.ipynb)
- Generation script: [`generate.py`](generate.py)
