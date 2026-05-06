# What do I do when I cannot run the experiment?

I left the last chapter on a forward note about questions that cannot be answered by randomized experiment. This chapter is the handoff. The book has been about experiments where I, as the analyst, control the assignment and can compare arms by clean math. Many of the most important questions in the world are not like this.

Real-world stage first.

The smoking-causes-cancer question, raised in Chapter 8, took decades to settle and was never settled by an experiment. You cannot randomize humans to smoke. The case was built from observational evidence (Doll and Hill's case-control study, 1950, and prospective cohort study, 1956), Bradford Hill's nine criteria for causation (1965), and Surgeon General's reports through the 1960s. The R.A. Fisher counter-argument (smokers and lung-cancer patients might share a common genetic cause) took years to refute, with evidence drawn from multiple distinct study designs. The conclusion is now overwhelming, but no single experiment did it.

Climate attribution is a similar shape. You cannot randomize the planet to have or not have CO2. The case for human-caused climate change is built from observational data, climate models, paleo-records, and counterfactual simulations. The IPCC reports synthesize these strands into "very likely" and "extremely likely" probabilistic statements. The framework is causal inference applied to a single planet over multiple decades.

Educational policy questions like "does going to college cause higher earnings?" are messy because people who go to college differ from people who do not in many ways before they ever start. The naive comparison (graduates earn more than non-graduates) is contaminated by selection. Modern econometric work uses techniques like instrumental variables (e.g., proximity to a college as an instrument for attending) and natural experiments (e.g., compulsory schooling laws as a discontinuity) to isolate the causal effect. The effect is real but smaller than the naive comparison suggests.

Medical interventions that cannot be randomized for ethical reasons (e.g., child-rearing practices, exposure to traumatic events, dietary patterns over decades) face the same problem. The data is observational, the comparisons are contaminated, and the causal structure has to be reasoned about explicitly.

Back to the simulator. Or rather, away from it, because the simulator does not save me here.

The simulator I have been using has a feature that real life rarely has: I controlled the assignment. I knew which users got treatment and which did not, because I assigned them. The mathematics of A/B testing rests on this control. When I lose control of assignment, the same math gives wrong answers, and I need different machinery.

The simplest version of the problem is selection bias. Suppose I observe data on a population: who got the treatment, who did not, what happened. The treatment was not randomly assigned. people chose it. The people who chose it are different in many ways from the people who did not. Comparing the two groups gives a naive effect that is partly the treatment and partly the differences between the groups.

The HRT case I mentioned in the dilution chapter is an example. Observational data showed HRT users had fewer cardiovascular events than non-users. The naive interpretation: HRT prevents cardiovascular disease. The randomized trial showed the opposite: HRT increases cardiovascular events. The discrepancy was that HRT users were systematically healthier, more affluent, and more health-conscious in ways that confounded the comparison.

The first tool of causal inference is to think about the data-generating process explicitly. What variables affect whether someone got the treatment? What variables affect the outcome? Are the two sets correlated? If so, those variables are confounders, and they need to be controlled for.

Statisticians and epidemiologists call this drawing the DAG (directed acyclic graph) of the data-generating process. The DAG specifies which variables cause which others. With the DAG in hand, there are rules for which adjustments make the comparison valid (controlling for confounders) and which adjustments make it worse (controlling for variables on the causal path, which blocks the very effect being measured).

The second tool is the natural experiment. Sometimes the world has, by accident, performed something that looks enough like a randomized experiment that the comparison is valid. The classic example is John Snow's 1854 cholera study in London: the Broad Street pump was contaminated, two water companies served different parts of the same neighborhood, the residents were similar across the boundary, and the cholera death rates differed by water company. The comparison was as-good-as-random because the water company assignment was decided by an old contract rather than by the residents' health.

Natural experiments are everywhere if you look. Vietnam draft lottery as an instrument for military service. Twin studies as a way to control for genetics. Same-sex sibling studies as a way to control for family environment. School cutoff dates as a discontinuity in age-at-entry. These designs are the heart of empirical economics and modern epidemiology.

The third tool is the instrumental variable. Suppose I cannot randomize directly, but I have a variable that is randomly distributed and that affects only the treatment, not the outcome directly. Then the variation in the instrument can be used to estimate the causal effect, even though the treatment itself is not random. Compulsory schooling laws as an instrument for years of education is the textbook case.

The fourth tool is the matched study. For each treated subject, find an untreated subject with similar pre-treatment characteristics. Compare the matched pairs. If the matching is based on all the relevant confounders, the comparison is valid. The catch: I have to know all the relevant confounders, which I rarely do.

These tools (and many more) form the field of causal inference. The math is more involved than randomized A/B testing because the assumptions about the data-generating process are explicit and the analyst has to defend them.

This is the territory the book hands off to. There is a parallel book in this series specifically about causal inference, with the same kind of inquiry-driven walkthrough but starting from the question of how to extract causal claims from observational data. The reader who has followed this book has the foundation: the surprise rule, the belief curve, the framework for combining prior with data, the appreciation for how data design shapes what the math can say. The causal inference book picks up where this one ends, with the harder problems where the experiment is impossible.

There is one more thing worth saying. The framework of this book (test, interval, posterior, decision rule) is built for situations where I control the assignment. When I do not, the framework still has parts that work. Confidence intervals around an estimated quantity remain meaningful, conditional on the model being right. Bayesian posteriors can be computed for any model, including causal-inference models. The pieces of machinery are reusable. What changes is the modeling: I have to specify the data-generating process, defend the assumptions, and own the consequences.

Now look up from the simulator.

The smoking-cancer question will never be answered by experiment. The case is built. The framework is causal inference, and the framework took fifty years and many researchers to deploy.

The climate-change question is in the same shape. The framework is observational, multiple lines of evidence, counterfactual modeling. The case is now overwhelming, and the framework is the standard one.

The "does this policy work?" questions in economics, education, public health, and criminal justice are dominated by observational data with various clever designs (regression discontinuity, instrumental variables, matched panels, difference-in-differences). The math of A/B testing does not apply directly, but the underlying intuitions (effect size, sample size, power, the difference between an estimate and a confidence interval, the role of priors) all carry over.

In each of these places, the question is the same shape as the questions this book has been about. Is this thing real or noise? How sure can I be? But the answer requires more careful thought about the data-generating process and the assumptions the analysis depends on. Causal inference is the right framework for these questions, and the parallel book in this series picks them up.

This is the end of the experimentation book. The coin has been a good companion. The simplest possible decision under uncertainty (is this coin fair?) has stood in for everything that comes after, because the structure of the question turns out to be universal. Drugs, polls, A/B tests, court verdicts, climate attribution: each has its own vocabulary and its own quirks, but each lives inside the same machinery. The reader who has followed the chapters has the lens. Whether the next question is one I can experiment on or one that has to be reasoned about from the data the world happens to have, the lens helps me ask the right question.

If I can stay honest with the coin in my hand, I have a chance of staying honest about the things that actually matter.
