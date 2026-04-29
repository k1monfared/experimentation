# Chapter 13: The metric tree

## Carried from Chapter 12

- You can't even ask "did the parts agree with the whole?" until you decide what "the whole" is. That's the metric tree.
## Inquiry loops planned

- Loop A: draw the tree. Top-level company outcome (e.g. annual revenue, retention). First-layer proxies (DAU, conversion). Lower-layer (CTR, page-load time). Bottom-layer (clicks, scrolls). Each layer is a noisier, faster proxy.
- Loop B: noise vs signal trade-off per layer. Simulate measurement at each level. The top-level metric needs months and is the truth. Bottom-level metrics tick by the minute but don't predict the truth.
- Loop C: predictivity. Run 200 simulated experiments. For each one, record the short-term metric change AND the long-term metric change. Plot the correlation. It's noisy but real for some metrics, near-zero for others.
- Loop D: when does a proxy lie to you? Walk through three concrete simulated cases. (clickbait link from Chapter 10 reappears.)
- Big question: a proxy can lie. How does this lie evolve over time? Does the lie get smaller, or bigger, or change shape?
## expkit modules used

- expkit.metrics.quality (NEW)
- expkit.sim.abtest with multi-metric outputs
