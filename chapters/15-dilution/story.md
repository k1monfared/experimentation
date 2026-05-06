# What if some people in the trial did not actually get the treatment?

I left the last chapter with a question about who actually receives the treatment in a real trial. The math of two-arm comparison assumes the treatment arm got the treatment and the control arm did not. In reality, the assignment to a treatment arm and the actual delivery of treatment can differ. The gap matters.

Real-world stage first.

In the COVID vaccine trials, the treatment arm meant "received the vaccine". But the trial's primary analysis was by intent-to-treat: every participant counted in their assigned arm regardless of whether they completed both doses, missed appointments, or had concurrent illnesses. The intent-to-treat analysis dilutes the apparent effect (because some "vaccine-arm" people did not finish dosing) but is the right answer for "if I roll out this vaccine to a population, what effect should I expect?".

Drug compliance studies routinely show that 30 to 50 percent of patients prescribed a chronic medication stop taking it within six months. The trial's intent-to-treat analysis includes those non-compliers in the treatment arm. The trial's per-protocol analysis excludes them. The two analyses give different numbers and answer different questions.

The 1990s push to encourage HRT (hormone replacement therapy) for menopausal women was based on observational data showing reduced cardiovascular events in HRT users. The Women's Health Initiative randomized trial in 2002 tested it directly and found increased cardiovascular events. One major reason for the discrepancy: in the observational data, HRT users were also more likely to be health-conscious in other ways (diet, exercise, screening), and the apparent benefit was partly driven by these confounders. The randomization tested the actual prescription, not the user behavior.

In a tech A/B test, the "treatment" is often a feature that shows up only when the user takes some action (logs in, visits a particular page, performs a particular interaction). A user assigned to the treatment arm who never logs in during the test period received no actual treatment. The gap between assignment and exposure is what dilutes the test.

Back to the simulator.

Suppose I am running a trial of a settings-page change. Users assigned to treatment will see the new settings page if they visit it. About 30 percent of users visit the settings page during the trial period. The treatment helps the visitors by 10 percentage points. The non-visitors are not affected at all.

If I run the standard intent-to-treat analysis (every assigned user counts in their arm), the apparent treatment effect is roughly 30 percent of 10 percentage points, or 3 percentage points. A real effect, but smaller than the underlying mechanism.

If I run a per-protocol analysis (compare only treatment-arm visitors to control-arm visitors), the apparent treatment effect is closer to 10 percentage points, the actual underlying effect on the people who saw the new page.

These two analyses answer different questions. Intent-to-treat answers "if I roll out this change to all users, what effect should I expect?". Per-protocol answers "for users who actually visit the settings page, what is the effect of the new design?". The first is the right number for product roll-out. the second is the right number for understanding the mechanism. Both are honest. Conflating them is the trap.

Per-protocol analysis has a subtler problem. Comparing treatment-arm visitors to control-arm visitors is not really comparing the new design to the old design. It is comparing one population (treatment-arm users who visited the settings page) to another (control-arm users who visited the settings page). If the act of being assigned to treatment changes whether a user visits (maybe the new design's email notifications nudge more people in), then the two visitor populations are different in ways the analysis does not control for. The per-protocol effect is contaminated.

The discipline is to be explicit about which analysis is being reported and what question it answers. Most regulatory agencies require intent-to-treat as the primary analysis for exactly this reason: it is the most honest answer to "what happens if I deploy this?".

There is a related subtlety with continuous outcomes that ratio-shaped metrics expose particularly clearly. Suppose I am measuring revenue per session. Both the numerator (revenue) and the denominator (number of sessions) are random. The naive estimator (mean of revenue divided by mean of sessions, or alternatively mean of per-session revenue) has a known bias and a non-trivial standard error. The "delta method" is a standard tool for getting the standard error right. it linearizes the ratio around the expected values. The math is more elaborate than simple difference of means.

Anyone running A/B tests on ratio metrics will eventually trip on this. The two arms can have noticeably different mean-of-ratios versus ratio-of-means, and which one to report is again a question about which analysis matches the question being asked.

Now look up from the simulator.

A vaccine trial reports both intent-to-treat efficacy (the headline number, useful for public health planning) and per-protocol efficacy (closer to the biological effect). Both numbers are true. They answer different questions.

A school-voucher experiment offers vouchers to a randomly selected subset of families. Some accept, some do not. The intent-to-treat effect is the average outcome of the offered group versus the not-offered group. The per-protocol effect (or the more sophisticated "compliers average causal effect") is the effect on the families who actually used the voucher. The first answers "what happens if I offer this to everyone?". The second answers "what does this voucher do for the people who use it?". Policymakers usually want the first. Researchers often want the second.

A drug trial in chronic depression has high non-compliance rates. The intent-to-treat result is what FDA cares about for approval (do prescriptions help on average?). The per-protocol result is what doctors think about for individual patients (does this drug work in people who actually take it?). Both numbers go into the package insert. Conflating them in news reports is common.

In each of these places, the gap between "assigned to treatment" and "actually treated" is real and consequential. The math handles it (intent-to-treat, per-protocol, instrumental variables for the more sophisticated cases), but the choice of which analysis to lead with determines what the result means in practice.

There is a forward question that opens the next chapter. The dilution problem is one kind of problem with the metric the trial reports. There is a much broader category: the metric itself is noisy in ways that can be reduced. Some of that noise reduction is a free lunch, in the sense that it does not require more data, just smarter analysis. The most famous tool for this is called CUPED.

How do I make my A/B tests more sensitive without enrolling more users?
