# If I ran every decision both ways, would I ship different products?

I left the last chapter with a synthesizing question. Throughout this book, the frequentist and Bayesian frameworks have run in parallel. They sometimes agree, sometimes disagree on borderline cases. In a real shipping decision pipeline (the kind a tech company runs hundreds of times per quarter, the kind a drug company runs at much higher stakes a few times per year), would the two frameworks produce different ship-or-no-ship decisions? On which kinds of cases? With what cost?

This is the capstone question of the book. The answer turns out to be: mostly the same decisions, with a small but consequential set of cases where the frameworks diverge. The shape of the divergence is itself informative about which framework to use when.

Real-world stage first.

Several large tech companies have published comparisons of frequentist and Bayesian decision rules running in parallel. Microsoft Excel's experimentation platform, in their 2017 paper, found that Bayesian and frequentist rules agreed on ship/no-ship decisions about 95 percent of the time across a corpus of A/B tests, with the disagreements concentrated in borderline cases at the 5-percent threshold.

Booking.com publishes some of the most detailed accounts of their A/B testing infrastructure. They have used Bayesian methods for some applications (sequential testing, hierarchical priors on metric drift) and frequentist methods for others (regulatory-style locked-in tests). The choice is contextual: Bayesian where peeking is necessary or the prior is informative, frequentist where the audit trail matters more.

Drug regulatory agencies (FDA, EMA) have moved toward accepting Bayesian methods for some applications (rare diseases, adaptive trials, pediatric extrapolation) while still requiring frequentist primary analyses for most phase 3 approvals. The hybrid is pragmatic: Bayesian for cases where the prior is real and the audit can handle it, frequentist for cases where the procedure has to be transparent and pre-specified.

In each of these places, the choice between frameworks is not theological. It is operational. Which framework's strengths line up with this particular decision's structure?

Back to the simulator.

Imagine I run a thousand simulated A/B tests on a tech-platform-style problem. Each test has a true effect that varies across tests (some tests have no real effect, some have small effects, some have large effects). For each test, I run both a frequentist decision rule (ship if p < 0.05 and direction is positive) and a Bayesian decision rule (ship if posterior probability of positive effect exceeds 0.95).

The two rules agree on a vast majority of the tests. The disagreements are concentrated where the data is borderline: small effects with sample sizes near the detection threshold. On these cases, the two rules can give different answers, and the answer depends on how confident the prior is.

If I impose a "minimum meaningful uplift" (MMU) on top of both rules, the Bayesian framework handles it more naturally. The MMU enters as a threshold the posterior must exceed: ship if P(effect > MMU) > 0.95. The frequentist version requires a one-sided non-inferiority test, which is more elaborate. With both rules using the same MMU and the same confidence level, the divergence shrinks even further.

The takeaway from these simulations is that the framework choice is often less consequential than people think. Two well-implemented frameworks pointing at the same question with comparable thresholds reach the same answer 90+ percent of the time. The remaining 10 percent are concentrated in cases where the data is genuinely insufficient to be confident, and where the framework's defaults effectively flip the call.

The cost of disagreement matters. In a tech context where the cost of a wrong ship is small (revert the change) and the cost of running the framework is real (engineering, reporting, training), the simpler framework usually wins. In a pharmaceutical context where the cost of a wrong approval is enormous (patient harm, regulatory backlash) and the framework's audit trail matters, the more transparent framework (frequentist with pre-specified rules) often wins.

There is another dimension. Frequentist analyses are easy to misinterpret (the p-value is widely misunderstood as the probability the null is true), while Bayesian analyses require the analyst to commit to a prior. Both frameworks can be done badly. The mature programs use both, and the choice between them is contextual.

Now look up from the simulator.

A tech company runs a thousand A/B tests in a quarter. Most of them are easy calls (clearly positive or clearly negative), and the framework choice does not matter. A few dozen are borderline calls where the framework choice matters. The aggregate effect of those few dozen on the year's product trajectory is small, but each individual case is a real decision that the framework had to make.

A drug regulator approves a few hundred drugs in a year. Most of the approvals are clear (effect size large relative to safety). A few are borderline (small effect, uncertain safety). The framework choice on those few is consequential because the cost of being wrong is patient harm. Both frameworks can give the right answer. the more conservative one is usually preferred.

An education researcher evaluating a pilot program has small samples (one school district, a few hundred students) and high stakes (decisions about scaling). Bayesian methods with informative priors (drawn from the broader literature on similar interventions) can give more useful posteriors than frequentist methods with the same data. The cost is the prior must be defended.

In each of these places, the framework choice is a tool selection problem. What is the data like? What is the cost of error? What is the audit trail? Different answers point to different frameworks.

The book has been about a single shape of question (is this thing real or chance, given some data?), with two frameworks for answering it. The last few chapters showed where the framework matters and where it does not. The frameworks agree on most cases. They disagree on some, and the disagreement is informative about the data more than about the frameworks.

The deeper takeaway is that the question is the thing. Picking the right question is harder and more important than picking the right framework. A wrong question answered well with either framework is still a wrong answer. A right question answered with a slightly imperfect framework still mostly works. The book has spent more pages on identifying the right question than on the framework wars, and that is the right balance.

There is a forward question that opens the next chapter, though it is the last one. Most of this book has assumed I can run a randomized experiment. Pick users, randomly assign half to treatment, half to control, watch what happens. This is the gold standard of inference. But many real questions cannot be answered by experiment. I cannot randomize people to smoke. I cannot randomize countries to have policies. I cannot randomize children to have particular parents. For these questions, the framework I have been using does not directly apply, and a different framework, called causal inference, takes over.

What do I do when I cannot run the experiment?
