# Chapter 10: Industry experimentation -- clicks, unsubs, and the average

## Carried from Chapter 9

- Studies pick narrow outcomes and narrow samples. Industry has the opposite problem: huge samples, but the metric you can measure in 1-2 weeks is rarely the metric you want to optimize.
## Inquiry loops planned

- Loop A: simulate a feature launch where click-through rate is up 4% (highly significant by every test we have built so far). Now show that 7-day retention is flat. Both can be true. Which is the real signal?
- Loop B: clickbait. Generate user behavior where the user clicks (positive short-term signal), then either feels misled and unsubscribes, or learns to ignore the source over time. Track 1-day, 7-day, and 30-day metrics. Watch the sign flip.
- Loop C: "averages hide structure". The average user's click rate goes up 4%; the most-engaged 10%'s rate goes down 2% while a long tail's rate goes up 15%. Same headline, different stories.
- Loop D: guardrail tests (frequentist) vs Bayesian decision frameworks. When metrics conflict, a single p-value can't tell you what to do. A Bayesian utility-weighted decision can.
- Big question: averages hide structure. What kind of structure?
## expkit modules used

- expkit.sim.abtest, expkit.sim.user_segments
- expkit.metrics.* (existing + new), expkit.inference.* both lenses
