# Why does the new thing always look great at first?

I left the last chapter with a particular kind of metric problem: the new feature wins on day one, then the win fades. The pattern is so common in product launches that it has a name: novelty effects. The user encounters something new, interacts with it more (curiosity, exploration, sometimes confusion), and the metrics spike. Once the novelty wears off, the metrics return to baseline.

Real-world stage first.

Every gym in January gets new memberships. Most of those new members are gone by April. The "post-resolution gym wave" is a famous case of behavior that responds to a stimulus then fades. Aggregate gym attendance in mid-February looks great. By March it does not.

A new song on the radio gets played in heavy rotation. Audience metrics spike. Two months later the same song is in light rotation and the metrics have settled. The novelty was real and limited.

A redesigned homepage on a website gets more clicks for the first week. Users are exploring. Two weeks in, click-through rates have settled back to where they were before the redesign. The redesign did not change long-run engagement.

Apple released the iPhone in 2007 and a small fraction of users were obsessed for the first weeks. By month six the obsession had stabilized into normal use. Whatever the launch's "engagement metrics" looked like in the first week, they were not the steady-state numbers.

In each of these places, the early metrics are real but transient. The product team that ships based on day-one numbers has not measured the steady state.

Back to the simulator.

Imagine I run an A/B test on a new feature. The feature genuinely changes nothing about long-run user value. Users see something new, are curious, click around, and the click metric spikes. After a month the click metric returns to baseline. The feature has zero true effect.

A typical 7-day A/B test, run on this feature, would catch the spike. The team would ship. Two months later, the click metric is unchanged from the original baseline, but by then the experimentation team has moved on to other things and the lift has been written into the books as a win that did not happen.

The fix is to design tests that distinguish novelty effects from real effects. There are three standard tools.

The first is to extend the time horizon. Run the test for 30 or 60 days instead of 7. The novelty curve has time to bend. The cost is real: long-running tests tie up traffic and slow down the team's ability to iterate.

The second is to look at user-level engagement curves rather than population-level rates. A real treatment effect should be visible across many users on day 30, when the novelty has worn off. A novelty effect should be visible mostly in users encountering the feature for the first time, with the effect decaying as those users have repeated exposures. If I plot per-user click rate against "days since first exposure", a real effect plateaus and a novelty effect decays.

The third is to use long-running holdout groups. Some fraction of users (maybe 10 percent) are kept on the original version forever, even after the new version is shipped. The metric difference between the holdout and the launched-to population is the steady-state effect. The first-week launch numbers are mostly novelty. the long-running holdout difference is the real signal.

Mature programs use all three. The cost of running a long-horizon experiment with holdout groups is real (traffic, complexity, organizational overhead), and many programs cut corners. The corners they cut are exactly where novelty effects hide.

There is a sister problem: primacy effects. Some treatments show small effects on day one and grow over time, because users need to learn to use the new feature. The opposite of a novelty effect. Both effects are non-stationary, both confuse a 7-day test, and both require longer horizons or holdout groups to characterize.

Now look up from the simulator.

A streaming service runs an A/B test on a new "skip intro" button. Click rates on the button are huge in the first week. By month two, the button is rarely used because users have figured out which shows have intros and which do not. The day-one number was not predictive of steady-state behavior.

A retail site adds a "buy now with one click" feature. Conversion lifts by 5 percent in week one. By month three the lift is 1 percent and stable. The week-one number was a mix of novelty and real effect. The team that shipped on the week-one number is now claiming credit for a 5 percent lift that was actually 1 percent.

A pharmaceutical study of a new headache drug measures pain relief at 1 hour and 24 hours after administration. The 1-hour effect is large. The 24-hour effect is small. The drug works fast and wears off fast. Reporting the 1-hour effect alone (which is common in marketing) overstates how much help patients get from the drug.

In each of these places, the time horizon of measurement is part of the question. Cheap fast metrics catch transient effects that decay. The expensive long-horizon measurement catches the steady-state truth. Choosing the time horizon is choosing which kind of effect to measure.

There is a forward question that opens the next chapter. So far I have been assuming the people in my treatment arm are all actually receiving the treatment. In reality, some fraction of the treatment arm does not engage with the treatment (for any number of reasons: they did not log in during the test, they did not see the feature, they actively opted out). The math has to handle this gap, and it has consequences.

If some people in the treatment group are not actually getting the treatment, what does the comparison even mean?
