# How do many sub-effects share information without becoming one effect?

This appendix picks up a thread the segmentation chapter dropped: hierarchical Bayesian models. They were the right answer to the multiple-comparisons-in-segments problem, but I deferred a careful treatment to here because the right context was not yet built.

The problem hierarchical models solve is easy to state. Suppose I have a treatment that I believe affects different segments of a population differently. I run an experiment, segment the data, and compute the per-segment treatment effects. Some segments are large (lots of users, low noise on the segment-level estimate). Some are small (few users, high noise). The naive thing is to report each segment-level estimate at face value. The smart thing is to recognize that the segment effects probably come from a population distribution: most are similar, with a few outliers, and small noisy segments should be pulled toward the population center because their data alone is unreliable.

This is the partial-pooling idea. It is the Bayesian-flavored alternative to multiple-comparisons correction, and it shows up in many forms in modern statistics.

Real-world stage first.

The Stein paradox (Charles Stein, 1956) showed that when estimating three or more means simultaneously, the joint estimator that shrinks each mean toward the grand mean is uniformly better than estimating each mean independently. The math is striking: shrinkage is mathematically guaranteed to do better, even though shrinking each mean toward the grand mean seems like it should be worse. This was a foundational result for what became hierarchical modeling.

Educational-testing studies routinely use hierarchical models to estimate per-school or per-classroom effects. A small school with 20 students has noisy per-school estimates. a large school with 1000 students has more precise ones. The hierarchical model gives the small school an estimate that is partly its own data and partly the average across schools, with the weight depending on how informative its own data is.

In sports, the modern era of player evaluation uses hierarchical models routinely. A pitcher's "true" ERA after 50 innings has a wide credible interval. after 500 innings, narrow. The hierarchical estimator does not just report 50-inning ERA. it reports a posterior that is partly the player's data and partly the league average, weighted by how much data the player has.

In genomics, hierarchical models are the workhorse of estimating effects of thousands of genetic variants on a trait simultaneously. Most variants have no effect. a few have meaningful effects. the hierarchical model shrinks the noisy small-effect estimates toward zero and lets the genuinely meaningful ones stand out.

In each of these places, the structure is the same. Many parallel estimates, of varying precision, drawn from a population that is itself learnable. The hierarchical model learns the population and the per-unit estimates simultaneously, shrinks the noisy ones, and reports a more honest picture than the per-unit naive analysis.

Back to the simulator.

Imagine I am running an A/B test in a product with 50 segments (say, 50 cities). Each segment has its own treatment effect, which I believe come from a population distribution: most cities have effects near zero, a few have larger positive effects, a few have larger negative effects. I do not know the population distribution. I want to learn it from data.

The naive analysis: run a per-city z-test, report each city's effect with its CI. With 50 segments, multiple comparisons inflate the false-alarm rate. some cities will look "significant" by chance. The Bonferroni-corrected analysis is conservative.

The hierarchical analysis: model each city's effect as drawn from a population Normal(mu, tau), with mu and tau themselves having priors. The model jointly estimates mu (population average effect), tau (between-city variation), and per-city effects. Each per-city effect is shrunk toward mu by an amount that depends on tau (large tau means cities really differ, so less shrinkage. small tau means the cities are similar, so heavy shrinkage).

The hierarchical estimates are more accurate on average than the naive per-city estimates, because they incorporate information across cities. Cities with little data are pulled toward the mean. cities with lots of data dominate their own posterior. The shrinkage is automatic and calibrated.

The cost of the hierarchical model is computational and conceptual. It requires more sophisticated software (PyMC, Stan), and the analyst has to think about the prior on tau (the between-segment variability). A tight prior on tau forces heavy shrinkage. a loose prior allows the data to determine the shrinkage. In practice, weakly-informative priors (like a half-normal on tau with a sensibly-chosen scale) work well for most applications.

Hierarchical models extend naturally to many parallel estimands. Per-segment effects in an A/B test. Per-school effects in education. Per-clinic effects in a multi-site clinical trial. Per-country effects in an international study. Per-gene effects in a genome-wide study. The structure is the same: many parallel estimates, shared population structure, partial pooling.

The Bayesian framework makes hierarchical modeling natural. The posterior is one consistent object over (mu, tau, segment effects), and any quantity I want to compute from it is a query against the posterior. The frequentist version (random-effects models, mixed-effects models) gets to similar places by different routes, but the conceptual structure is recognizable as the same idea: pool when the data tells you to pool, separate when it tells you to separate.

This is the answer I deferred from the segmentation chapter. When I said "hierarchical Bayes is the right tool for multiple-comparisons in segments", I meant exactly the model in this appendix. The math is more involved than per-segment z-testing-with-Bonferroni, but the result is more honest and more useful for decision-making.

The book has now picked up its threads. The Bayesian framework, introduced in Chapter 6, generalized through Chapters 7-15 to many situations, and pulled together in this appendix as the natural answer to multi-segment, multi-site, multi-everything problems where partial pooling is the right discipline.

The reader who wants to apply the framework in real settings should plan to spend time with PyMC and Stan, and should use hierarchical models whenever the data has natural groupings that the analysis should respect.
