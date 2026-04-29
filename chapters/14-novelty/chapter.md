# Chapter 14: Novelty effects

## Carried from Chapter 13

- The lie evolves over time. The most famous version: novelty.
## Inquiry loops planned

- Loop A: simulate a feature where the true long-run effect is +1%. But for the first week, exposed users explore the new thing and click 6% more. Then it decays.
- Loop B: three measurement schemes for the same data:
  - calendar time from launch (week 1, week 2, week 3 ...)
  - per-user time since exposure (day 1 since exposed, day 2 ...)
  - per-user exposure count (1st exposure, 2nd ...)
  - These three reframings of the same event stream tell different stories. Plot all three side by side.
- Loop C: probe the edge. What if instead of decay, we have a primacy effect that builds? Or a U-shape?
- Loop D: Bayesian: a hierarchical model where each user's response is exposure-time-shaped, with a population-level decay curve.
- Big question: some users were "in the experiment" but never actually saw the new feature. Does that change anything? (Yes.)
## expkit modules used

- expkit.sim.novelty (NEW)
- expkit.novelty.measure (NEW)
