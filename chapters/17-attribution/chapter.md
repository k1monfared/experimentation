# Chapter 17: Attribution

## Carried from Chapter 16

- A user touches the product five times before converting. Which touch gets credit? Different answers, different decisions.
## Inquiry loops planned

- Loop A: simulate user journeys with five touchpoints. Apply first-touch, last-touch, linear, time-decay attribution. Compute "value per channel" under each scheme.
- Loop B: introduce an experiment that boosts touch #3 specifically. Which attribution scheme catches the lift? Which one misses it? Which one mis-allocates it to the wrong channel?
- Loop C: shifted-time perspective. The same touches at different lags. Which scheme is most stable to the lag distribution?
- Loop D: Bayesian attribution as a multi-touch model. Each channel has a true coefficient; the data partially identifies them. Posteriors over coefficients vs naive last-touch.
- Big question: we've been running experiments for 17 chapters. When do experiments fail? When do we have to do something else?
## expkit modules used

- expkit.attribution.touch (NEW)
