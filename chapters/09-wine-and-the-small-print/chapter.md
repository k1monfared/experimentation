# Chapter 9: Wine, coffee, and the small print

## Carried from Chapter 8

- The mechanics work. Now we ask: who was studied? what counts as "good"? what got measured? what got ignored?
## Inquiry loops planned

- Loop A: simulate a study where wine's "effect on health" is measured only on 22-year-old male college students. The estimated treatment effect is real for that subgroup. Then resample as if the same effect applied to a broader population (older people, women, pregnant women, kids). It doesn't. Show the gap.
- Loop B: define "good". A 5% reduction in resting heart rate isn't the same as "lives longer". Many studies measure proxies. Walk through three different operationalizations and which ones a 5% effect would hold for.
- Loop C: side effects. Run the same simulation but track three outcomes (target metric, secondary outcomes, harms). Treatment helps the headline metric and hurts a side metric. Both lenses agree on the data; the *decision* depends on weighting.
- Loop D: tradeoff analysis. Build a tiny utility function with knobs. Show that "ship/don't ship" flips depending on stakeholder priorities, even with the same posterior.
- Big question: how do real industry teams actually decide? Spoiler: they look at clicks and unsubscribes. That has its own pathologies.
## expkit modules used

- expkit.sim.user_segments (NEW): heterogeneous treatment effects across populations
- expkit.metrics.delta (eventually) for ratio outcomes
