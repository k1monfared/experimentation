# When something good happens, who gets the credit?

I left the last chapter with a different shape of question. Not "is the effect real?" but "given an outcome, which input deserves credit?". The question shows up in marketing, in healthcare, in education, in any setting where the decision is among several inputs that could plausibly have produced the outcome.

Real-world stage first.

In digital marketing, the canonical attribution problem: a user sees an ad on YouTube, then a sponsored Instagram post, then comes back to a Google search and clicks a paid ad, then makes a purchase. Which ad gets the credit? The marketing budget for next quarter depends on the answer. Different attribution rules give wildly different answers.

In medicine, a patient takes three medications and recovers. Which one helped? In some cases each medication is targeting a separate symptom. in others they are alternative paths to the same outcome and only one is doing the work. Discontinuing one medication to find out the answer is sometimes possible (a clinical "rechallenge") and sometimes not.

In sports, a basketball player is on the court for a string of points. Which players deserve credit for the points? The simple "plus-minus" statistic gives equal credit to everyone on the court. More sophisticated adjustments use regression to disentangle individual contributions from team context.

In each of these places, the data shows that a positive outcome happened in the presence of multiple potential causes. The math has to assign credit somehow, and the choice of credit-assignment rule determines the answer.

Back to the simulator.

Imagine a user who converts after a sequence of touches. Touch 1: saw a YouTube ad. Touch 2: saw an Instagram post. Touch 3: clicked a Google paid search result. Touch 4: opened a marketing email. Touch 5: visited the website organically and bought.

The conversion happened. How much credit goes to each touch?

Last-touch attribution: 100 percent of credit to the last interaction (the organic visit). The earlier touches get nothing. This is the dominant model in much of digital marketing because it is easy to implement: the touch that closed the deal is in the same session as the conversion, easy to track. The criticism is that it gives no credit to top-of-funnel work that built awareness and intent.

First-touch attribution: 100 percent of credit to the first interaction (the YouTube ad). Useful for measuring "how did people first hear about the brand", essentially useless for measuring which subsequent touches mattered.

Linear attribution: equal credit to every touch. Simple, but treats every touch as equally important, which is rarely true.

Time-decay attribution: more credit to touches closer to the conversion. Compromise between first and last touch. The "decay rate" is a tunable parameter that determines how much weight goes to early vs late touches.

Position-based (often "U-shaped"): typically 40 percent to first touch, 40 percent to last, 20 percent split among middle. Captures the idea that first and last touches are particularly important.

Algorithmic / data-driven attribution: trains a model on conversion sequences to estimate the marginal contribution of each touch. More principled, requires more data and more sophisticated infrastructure.

These are all rules. Each one gives a different breakdown of credit for the same conversion sequence. Which rule is "right" depends on what question is being asked.

The fundamental problem is that attribution requires a counterfactual. To know how much credit a touch deserves, I need to know what would have happened without that touch. Real conversion data does not contain the counterfactuals. each user converts or does not, with their actual touch sequence. Attribution rules are heuristics for assigning credit in the absence of the counterfactual.

The 2013 eBay study by Blake, Nosko, and Tadelis is the classic demonstration of how attribution can mislead. eBay was spending substantial money on branded paid search ads (people typing "ebay" into Google and seeing eBay's paid ad). Standard last-touch attribution credited those ads with a meaningful share of conversions. Then eBay ran an experiment: in some markets they turned off the branded paid search ads. The result: total conversions barely moved. The users who would have clicked the paid ad just clicked the organic result instead. The "attributed conversions" were almost entirely cannibalization of organic traffic. The paid search budget was largely wasted, but the attribution model said it was working.

This is the structural problem. Attribution rules report numbers that look like causal effects but are not. they are credit-assignment rules applied to observational data. The randomized holdout is what tests whether the touch is actually causal. Without the holdout, I am guessing.

Mature marketing programs use a mix: attribution models for day-to-day reporting (because randomized holdouts are expensive), and periodic geographic or temporal holdout experiments to calibrate the attribution model. The attribution model gives daily numbers. the holdouts give periodic ground truth. The two together are more honest than either alone.

Sophisticated approaches extend to Bayesian frameworks where each touch is given a posterior over its causal effect, and the posterior tightens as more data comes in. The Bayesian framing makes the credit-assignment uncertainty explicit, which is usually appropriate given how uncertain real attribution is.

Now look up from the simulator.

A presidential candidate has many touches with each voter (rallies, ads, mailers, debates, social media). Which touch flipped the vote? Campaign data scientists try to estimate marginal effects of each channel, often with regression adjustment and natural experiments (e.g., one media market got more ads than another because of TV scheduling quirks, allowing an instrumental variable analysis).

A pharmaceutical patient education program has multiple touchpoints (in-person counseling, mailed materials, follow-up calls). Which touchpoint drove adherence? Trials with factorial designs (some patients get one combination, some another) can disentangle the contributions, but factorial designs are expensive and rare.

A college student has many influences on their career path (a particular professor, a summer internship, a club, a mentor). Asking the student which one mattered most rarely gives a reliable answer because the influences are co-conspirators, not independent inputs. Career counseling programs that try to take credit for outcomes face this attribution problem in a hard form.

In each of these places, attribution is a question without a clean answer because the causal structure is intertwined. The math can produce credit-assignment numbers. whether those numbers reflect the actual causal contribution is a separate, harder question.

There is a forward question that opens the next chapter. So far in this book I have used both frequentist and Bayesian frameworks in parallel. In real-world shipping decisions, would the two frameworks actually disagree about what to ship? If so, how often, and on what kinds of cases? This is a capstone question that brings together the threads of the whole book.

If I ran every decision through both frameworks, would I ship different products?
