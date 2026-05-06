# Real-life examples bank for the story track

Comprehensive set of real-world situations the book can pull from when illustrating a statistical concept. Each entry is genuinely distinct from the others (different domain, different mechanics, different reader entry point). Sub-variations are listed under their parent.

## How to use this bank

When drafting a chapter:

1. Identify the concepts the chapter develops (effect size, multiple testing, Simpson's paradox, etc.).
2. Skim the concept-to-example index at the bottom of this file.
3. Pick one example for the chapter's main throughline. Pick a second one, from a different domain, for the closing real-stakes connection.
4. Read the "specific stories" lines on the chosen example to find the texture-rich version. Reach for the stories that have stakes the reader can feel (per Intent 4 in `STORY_LEARNINGS.md`).
5. Stay in the chosen example's vocabulary throughout the chapter (per Intent 6 in `STORY_LEARNINGS.md`). If switching between examples, name the switch.
6. If you reach for an example and the math does not match cleanly, do not bend the math. Either pick a different example or build a clean variation under the parent example.

When a new chapter generates a new useful example or an unexpected variation, add it to this file before drafting the next chapter.

The "concepts illuminated" line for each example is the set of concepts where the example is *clean* and *anchoring*, not a list of every concept it might touch. The concept-to-example index lists examples in order of how clean they are for that concept.

## Examples bank

### 1. The coin

The foundational example. Pick up a coin, ask "is it fair?", toss it, watch the running fraction of heads.

- **Why it works**: small, embodied, anyone can do it, lets a single thread carry every concept that matters in the rest of the book.
- **Concepts illuminated**: hypothesis testing (is the coin fair?), sample size and power (how many tosses to detect a small bias?), confidence intervals and credible intervals (the band of plausible biases), Bayesian updating (how my belief shifts toss by toss), p-values and surprise zones, the imagined-population framing (10,000 people each tossing).
- **Specific stories and texture**:
  - Persi Diaconis's research on the physics of coin flipping showed that flipped coins are weirdly resistant to physical bias. Even substantially weighted coins flip almost evenly.
  - Football referees use ceremonial coins for kickoffs. Nobody has ever publicly checked whether the ceremonial coins are more fair than the pocket version.
  - The European Football Championship 1968 between Italy and the Soviet Union was decided by a coin toss after a 0-0 semifinal.
  - A bent coin (cup-shaped, rim curled inward by a few degrees) lands on the convex side noticeably more often. Pliers and a quarter is enough.
  - A coin spun on its edge is much more sensitive to physical asymmetry than a flipped coin.
- **Variations under this parent**:
  - Six-sided die: extends to multinomial distribution and chi-square.
  - Two-headed magic-shop coin: bias = 1, used for "obvious cheating" framing.
  - Roulette wheel: an industrial-scale, high-revolution version of the same physics question.

### 2. Clinical drug trial

A pharmaceutical company tests whether a new drug works. Some patients get the drug, some get a placebo, results are compared.

- **Why it works**: the math has tangible life-and-death stakes, the regulatory framework is rich, the failure modes are well-documented.
- **Concepts illuminated**: hypothesis testing with controls, sample size determination (FDA-style), power calculations, randomization, intent-to-treat vs per-protocol analysis (compliance), one-sided vs two-sided tests, replication, publication bias, conflict of interest in funding.
- **Specific stories and texture**:
  - The MRC streptomycin trial (1948), the first major randomized clinical trial, established the framework.
  - Vioxx withdrawal (2004): a drug approved on RCT evidence that turned out to cause excess cardiovascular events. About 88,000 to 140,000 cases of serious heart disease attributable.
  - The Phase III COVID vaccine trials (Pfizer-BioNTech enrolled 43,448 participants, Moderna 30,420). The "95% effective" headline came from the trial arithmetic of cases-in-vaccine vs cases-in-placebo.
  - Lipitor and the original CARE/4S trials. Statins as a category have hundreds of RCTs.
  - The replication crisis in biomedical research: Begley and Ellis (2012) reported they could replicate only 6 of 53 landmark cancer studies.
  - Pharma-funded trials show outcomes favorable to the funder more often than independently funded ones (the "funding effect", Lexchin et al. 2003).
- **Variations under this parent**:
  - Medical device trial (different regulatory path, often smaller N).
  - Vaccine trial (efficacy in event terms, base rate matters).
  - Surgery trial (often unblindable, different protocol shapes).
  - Lifestyle intervention trial (exercise, diet, sleep).
- **Sources**: David Spiegelhalter, *The Art of Statistics* chapter on causation; Ben Goldacre, *Bad Pharma*; the ICH E9 statistical guideline.

### 3. Political polling

Before an election, surveyors call a sample of voters to estimate how the full electorate is likely to vote.

- **Why it works**: every reader sees these numbers, "margin of error" is in the public vocabulary, the failure modes are visible (2016 US, 2015 UK, 2017 UK).
- **Concepts illuminated**: sample size and margin of error, confidence intervals, weighting and stratification, sampling bias (who answers polls), survey design, polling aggregation.
- **Specific stories and texture**:
  - The 1936 Literary Digest poll (2.4 million returned ballots) predicted Landon would beat Roosevelt; Roosevelt won 46 states. The sample was huge but biased: drawn from car registrations and phone books in a Depression-era US where poorer Roosevelt voters did not own cars or phones.
  - The 1948 Truman-Dewey "Dewey Defeats Truman" Chicago Tribune headline; Gallup had Truman at 44.5%, real result 49.6%.
  - The 2016 US presidential polls predicted Clinton would win; Trump won. State-level polls in WI, MI, PA were inside their margins, but the joint probability was not. Nate Silver's 538 model gave Trump about 29%, the others gave him 1-15%.
  - The 1992 UK general election where polls predicted a Labour win; Conservatives won. The "shy Tory" effect.
  - Pollsters started using mixed-mode (calls plus internet panels) after the 2010s as response rates collapsed.
- **Variations under this parent**:
  - Approval rating tracking (continuous vs election-day).
  - Exit polling (different sampling problem).
  - Census enumeration (no sampling, but undercount of certain populations).
  - Marketing surveys (commercial polling).

### 4. A/B testing in tech

A web product or app shows different versions of something to different users and measures who clicks more, buys more, comes back.

- **Why it works**: the reader interacts with these tests every day without knowing it; modern tech companies run thousands per month; the math forces the discussion of detection power for tiny effects.
- **Concepts illuminated**: comparison-based decisions, sample size needed for tiny effects, sequential testing and peeking, multiple comparisons (testing many features simultaneously), Bayesian decision-making, ship/no-ship rules, MMU (minimum meaningful uplift), engineering cost vs statistical cost.
- **Specific stories and texture**:
  - Google's "41 shades of blue" link color test (2009). A test famously sneered at by Marissa Mayer's design team but won the company an estimated $200M/year in additional ad revenue.
  - Microsoft Office Online's Bing Ads sorting experiment that flipped a sign and lost $10M in revenue before being caught.
  - Amazon's homepage A/B tests; CEO Bezos's famous quote about not running tests on most decisions.
  - Booking.com runs ~1000 A/B tests at any given moment (their published engineering posts).
  - Netflix A/B tests every recommendation algorithm change; their landing-page personalization experiments.
- **Variations under this parent**:
  - Multi-armed bandit (continuous allocation rather than fixed split).
  - Switchback experiment (alternating periods rather than user-level random).
  - Geo-experiment (different cities get different versions).
  - Surrogate-metric experiment (when the real metric is too slow).
- **Sources**: Ron Kohavi's blog and *Trustworthy Online Controlled Experiments*; the Microsoft ExP team papers; Booking.com engineering blog.

### 5. Diagnostic medical test

A patient takes a test for a disease. The test reports positive. Should they be worried?

- **Why it works**: this is the cleanest entry point to base-rate reasoning and Bayesian inversion. The prior probability of disease shapes the meaning of a test result.
- **Concepts illuminated**: Bayesian inversion (P(disease | positive test) is not P(positive test | disease)), base rates, sensitivity and specificity, positive predictive value, false positives in rare-event detection.
- **Specific stories and texture**:
  - The classic mammography problem (Eddy 1982): 95 of 100 doctors gave the wrong answer. Disease prevalence 1%, sensitivity 80%, specificity 90.4%. Posterior probability of cancer given positive test: about 7.5%, not 75%. (See *Reckoning with Risk* by Gigerenzer.)
  - HIV testing in low-prevalence populations: high sensitivity does not save you from base-rate-dominated false positive rates.
  - Cancer screening recommendations changing: PSA tests for prostate cancer dropped from "routine" to "case by case" because of base-rate-driven false positive cascades.
  - COVID rapid antigen tests at low community prevalence: most positives during low-spread periods were false positives.
  - Down syndrome screening in early pregnancy: combined NT scan plus blood markers vs amniocentesis; the reason invasive testing exists at all.
- **Variations under this parent**:
  - Pregnancy test (very high sensitivity and specificity, but reading-instruction errors).
  - Drug test in employment (workplace screening).
  - Polygraph / lie detector (high false positive rate; admissibility debate).
  - Forensic toolmark or hair analysis (long-running false-match problems).
- **Sources**: *Reckoning with Risk* by Gerd Gigerenzer; *Calculated Risks*; the BMJ "Bayes' theorem in the clinic" series.

### 6. Criminal trial verdict

A jury hears evidence and decides whether the defendant is guilty beyond reasonable doubt.

- **Why it works**: the legal framework is the cleanest real-world version of "burden of proof" the reader has seen. The asymmetric costs (false conviction vs false acquittal) make the threshold question concrete.
- **Concepts illuminated**: hypothesis testing as decision under uncertainty, asymmetric costs, type I and type II errors, presumption (innocent until proven guilty maps directly to "fair until proven biased"), the misuse of probability in court.
- **Specific stories and texture**:
  - The Sally Clark case (UK, 1999): convicted of murdering her two infant sons after a pediatrician testified the chance of two SIDS deaths was "1 in 73 million" by squaring 1/8500. The independence assumption was wrong; conviction was overturned in 2003.
  - The People v. Collins (1968): a couple was convicted because the prosecutor multiplied "subjective" probabilities of each visible feature (yellow car, ponytail) to get 1/12 million, then said this was the chance of innocence. Conviction reversed.
  - The OJ Simpson trial (1994): Alan Dershowitz argued that domestic violence rarely leads to murder (something like 1 in 2500), missing the conditional that the wife was already dead.
  - The Lucia de Berk case (Netherlands): a nurse convicted of multiple patient murders based on flawed probability arguments. Conviction reversed in 2010.
  - DNA evidence "match probabilities" being misinterpreted as "probability of innocence" (the "prosecutor's fallacy").
- **Variations under this parent**:
  - Civil trials (preponderance of evidence, lower threshold).
  - Tribunal hearings (administrative law, balance of probabilities).
- **Sources**: *The Theory That Would Not Die* by Sharon McGrayne (probability in court chapters); the Court of Appeal opinions on Sally Clark and Lucia de Berk.

### 7. Weather forecasting

Tomorrow's weather is reported as a probability ("70% chance of rain").

- **Why it works**: it is the most familiar example of a real probabilistic prediction; the reader uses these numbers without knowing what they mean.
- **Concepts illuminated**: probabilistic prediction, ensemble methods, calibration, probabilistic vs deterministic forecasts, the meaning of "X percent chance".
- **Specific stories and texture**:
  - "70% chance of rain tomorrow" is typically the fraction of model ensemble runs (each with slightly perturbed initial conditions) that produced rain at that location and time. It is not a fraction of historical similar days, although that interpretation is also defensible.
  - The 2012 Hurricane Sandy forecasts: ECMWF (European model) predicted the New Jersey landfall track 7-8 days out; American GFS only 3-4 days out. The European model was right.
  - Calibration evaluation: forecasts of "60% chance of rain" should rain about 60% of the time. Most national weather services calibrate this way (Brier score), and they are quite well calibrated.
  - The Brier score and the reliability diagram (forecast probability vs observed frequency).
  - The "polar vortex" forecasts of the 2010s: longer-range forecasting via teleconnections.
- **Variations under this parent**:
  - Hurricane track forecasting (cone of uncertainty).
  - Climate prediction vs weather prediction (very different time scales).
  - Sports betting odds (similar machinery in different clothes).

### 8. Smoking and lung cancer

Did smoking cause the dramatic rise in lung cancer in the 20th century? You cannot run the obvious experiment.

- **Why it works**: the foundational example of inference about causation when randomized experiments are impossible. The full debate is well documented, the resolution took decades, the public health stakes were enormous.
- **Concepts illuminated**: causal inference from observational data, Bradford Hill criteria, confounding, conflict of interest in research, dose-response relationships, when correlations are enough to act on.
- **Specific stories and texture**:
  - Doll and Hill's 1950 case-control study showed lung-cancer patients smoked more than matched controls. Their 1956 prospective cohort of British doctors removed the recall-bias question.
  - Tobacco industry's "Doubt is our product" memo (1969, Brown & Williamson). Decades of manufactured uncertainty.
  - The Bradford Hill criteria (1965) emerged as the framework: strength, consistency, specificity, temporality, biological gradient, plausibility, coherence, experiment, analogy.
  - R.A. Fisher (the same Fisher of Fisher exact test) argued for years that smoking was correlated with cancer due to a shared genetic cause. He was wrong, and the genetic cause hypothesis is now mostly forgotten.
  - The Surgeon General's 1964 report.
- **Variations under this parent**:
  - Asbestos and mesothelioma.
  - Lead and IQ (Clair Patterson and Alice Hamilton's work).
  - Air pollution and cardiovascular disease (Six Cities study, 1993).
  - Radon and lung cancer.
- **Sources**: *The Cigarette Century* by Allan Brandt; *Smoke and Mirrors* by Stanton Glantz; the Doll & Hill papers in BMJ.

### 9. Sports analytics

Was that hitter actually good, or just lucky? Should the manager bench the hot streak?

- **Why it works**: small sample sizes, regression to the mean, talent-vs-luck decomposition all show up cleanly. The reader knows the names.
- **Concepts illuminated**: regression to the mean, small-sample noise, batting average vs true ability, the hot hand fallacy (and its rehabilitation), Sabermetrics, base rates of streaks.
- **Specific stories and texture**:
  - Joe DiMaggio's 56-game hitting streak (1941). The math says streaks of 56 are extremely rare even for a hitter of DiMaggio's quality, but possible.
  - The Sports Illustrated jinx: athletes appearing on the cover often perform worse afterward. Pure regression to the mean.
  - Moneyball (Michael Lewis, 2003): Billy Beane's Oakland A's used Sabermetric statistics (on-base percentage instead of batting average) to identify undervalued players.
  - Tversky and Gilovich's 1985 paper "The Hot Hand in Basketball" claimed the hot hand was an illusion. Miller and Sanjurjo's 2018 reanalysis found a small but real effect.
  - Wilt Chamberlain's 100-point game (1962) and Kobe Bryant's 81-point game (2006). Both freak events conditional on talent.
  - The replication crisis hits sports too: many "clutch" findings do not replicate.
- **Variations under this parent**:
  - Tennis serve speeds and player rankings.
  - Football (American) draft pick value.
  - Soccer expected-goals (xG) models.
  - Chess Elo ratings.
- **Sources**: *Moneyball*; *The Numbers Game* by Anderson and Sally; Tom Tango's *The Book*; FiveThirtyEight's sports archives.

### 10. Stock market and the efficient market hypothesis

Can a fund manager beat the market on skill, or is most of the market a random walk?

- **Why it works**: the reader hears about market predictions every day; the failure of most active managers to beat the market is the largest natural experiment in pseudo-skill in human history.
- **Concepts illuminated**: random walks, alpha vs beta, survivorship bias in fund tracking, multiple testing across thousands of strategies, the Sharpe ratio, p-hacking in finance.
- **Specific stories and texture**:
  - Burton Malkiel's *A Random Walk Down Wall Street* and the "monkey throwing darts at the WSJ" experiment.
  - The S&P 500 vs hedge fund performance over decades. The "SPIVA" report from S&P Global tracks how few active funds beat their benchmark.
  - Renaissance Technologies' Medallion Fund: an apparent counter-example, with returns that are statistically extraordinary. Closed to outside investors.
  - The "January effect", "low-volatility anomaly", and other published market anomalies, most of which weakened or disappeared after publication. Harvey, Liu, and Zhu (2016) argued that the t-statistic threshold for genuine financial discovery should be 3.0, not 2.0, because of the multiple-testing problem across thousands of investigated strategies.
  - LTCM's 1998 collapse: 16-sigma events that turned out to happen.
- **Variations under this parent**:
  - Cryptocurrency price patterns (similar but younger).
  - Real estate price predictions.
  - Sports betting markets (semi-efficient).
- **Sources**: *A Random Walk Down Wall Street*; *The Misbehavior of Markets* by Mandelbrot; the SPIVA reports.

### 11. Casino games and the house edge

Slot machines, roulette, blackjack. Each has a tiny house edge that adds up reliably.

- **Why it works**: the casino is where probability is honest. The numbers are exact, the long run is real, the gambler's fallacy is on display.
- **Concepts illuminated**: expected value, the law of large numbers, gambler's fallacy, ruin theory, the Kelly criterion, why casinos are profitable.
- **Specific stories and texture**:
  - American roulette: 18 black, 18 red, 2 green (0 and 00). The house edge on a red/black bet is 2/38 = 5.26%. Long-run, the player loses 5.26 cents per dollar bet.
  - European roulette: 18/18/1, house edge 2.7%. Better game, same idea.
  - Blackjack with optimal basic strategy: house edge 0.5-1%, the closest casino game to a fair coin.
  - Card counting in blackjack: real, mathematically defensible, and casino-banned. MIT Blackjack Team (Bringing Down the House).
  - The Monte Carlo casino's 1913 streak: 26 reds in a row at the roulette wheel. The chance of 26 reds is (18/37)^26 ≈ 1 in 137 million. This is not so rare given enough wheels and enough hours.
  - The gambler's fallacy: thinking past results affect the next spin. They do not.
- **Variations under this parent**:
  - Lottery (large prizes, near-zero return per ticket).
  - Sports betting parlay (multiplicative house edge).
  - High-frequency stock trading (similar mathematics, much faster).
- **Sources**: *The Theory of Gambling and Statistical Logic* by Richard Epstein; *Beat the Dealer* by Edward Thorp.

### 12. Lottery and rare events

A lottery jackpot has expected value far below the ticket price. People play anyway. Why?

- **Why it works**: rare events stretch intuition. Probabilities like 1 in 300 million do not parse natively; analogies are needed.
- **Concepts illuminated**: very small probabilities, expected value, utility (the personal value of money is not linear), birthdate paradoxes, the law of small numbers, multiple comparisons (how many lottery winners are there?).
- **Specific stories and texture**:
  - Powerball: 1 in 292 million per ticket for the jackpot. Driving 1 mile to buy the ticket is more dangerous than the entire chance of winning.
  - Joan Ginther won the Texas lottery four times between 1993 and 2010, total winnings about $20 million. The chance of her winning each draw separately was tiny, but she bought thousands of tickets and was a former math professor.
  - Romanian-Australian Stefan Mandel bought every possible Virginia lottery combination in 1992, won $27 million.
  - The birthday paradox: 23 people in a room, more likely than not that two share a birthday.
  - "Someone wins the lottery every week, so it could be me" is the inverse of multiple-testing: there are many opportunities, so rare events happen.
- **Variations under this parent**:
  - Plane crash probability (very rare per flight, scary in feel).
  - Asteroid impact (extremely rare, civilization-ending stakes).
  - Striking it rich on a startup (rare conditional on starting one).

### 13. DNA forensic match

A crime-scene DNA sample matches the suspect's profile. Match probability is given as "1 in 50 million". What does that number mean?

- **Why it works**: clean entry to the prosecutor's fallacy, base rate reasoning, the difference between a random-match probability and a probability of guilt.
- **Concepts illuminated**: prosecutor's fallacy, conditional probabilities, false positives at scale (CODIS database searches), independence assumptions in forensic science, the rebuttal expert problem.
- **Specific stories and texture**:
  - The OJ Simpson trial: DNA match probabilities from blood evidence were stated as 1 in 170 million. Cochran's "if it doesn't fit, you must acquit" sidestepped the math.
  - The People v. Puckett (California, 2008): a cold-hit DNA match in a 30-year-old murder case. Match probability quoted to jury was 1 in 1.1 million; the actual database search probability was much higher.
  - The 2010 case of Lukis Anderson, San Jose, charged with murder based on a DNA match. He was in the hospital at the time. Cross-contamination from EMT equipment.
  - "Random match probability" vs "ID probability" debate in forensic genetics.
  - Mitochondrial DNA (less powerful than nuclear) and Y-STR markers (relevant for paternity-style matches).
- **Variations under this parent**:
  - Fingerprint matching (much less rigorous statistical foundation; PCAST 2016 report).
  - Bite-mark analysis (similar issues, largely discredited).
  - Hair analysis (FBI admitted in 2015 that 96% of pre-2000 hair-match testimony was flawed).

### 14. Education research

Does smaller class size help learning? Does a particular reading curriculum work?

- **Why it works**: the reader sees policy debates about education constantly. RCTs are difficult here, so the methodology questions are vivid.
- **Concepts illuminated**: randomized trials in social settings, contamination and spillover, intent-to-treat analysis (kids assigned to the new curriculum may not actually use it), long-term outcome measurement, multiple testing across districts.
- **Specific stories and texture**:
  - Project STAR (Tennessee Student/Teacher Achievement Ratio, 1985-1989): a real RCT on class size, ~11,600 students. Found a positive effect on test scores from smaller classes (13-17 vs 22-25), with effects persisting through high school graduation (Krueger and Whitmore).
  - Perry Preschool Project (1962-67) and the long-term economic returns (Heckman et al.) of early childhood education.
  - The "Hawthorne effect" in industrial productivity research at Western Electric (1924-32). The original study has been heavily reanalyzed.
  - The "growth mindset" intervention literature: large RCTs (Sisk et al. meta-analysis) showed effects far smaller than the original Carol Dweck claims.
  - Charter school RCTs (lottery designs leveraging oversubscription).
- **Variations under this parent**:
  - Job training programs (workforce development).
  - Microfinance impact studies (Esther Duflo et al.).
  - Mental health interventions in schools.
- **Sources**: *Poor Economics* by Banerjee and Duflo; *Mostly Harmless Econometrics* by Angrist and Pischke.

### 15. Hospital and surgeon outcome comparison

Which hospital has better mortality rates? Should I prefer the surgeon with the lower complication rate?

- **Why it works**: the cleanest entry to Simpson's paradox and risk adjustment. Simple rate comparisons can mislead in obvious ways.
- **Concepts illuminated**: Simpson's paradox, risk adjustment, case-mix differences, observational comparison vs counterfactual, outcome metrics that capture the wrong thing.
- **Specific stories and texture**:
  - The 2015 New York Times piece on the surgeon scorecards. ProPublica's "Surgeon Scorecard" project led to debate about the validity of unadjusted complication rates.
  - The British Bristol Royal Infirmary scandal (1990s): pediatric heart surgery mortality was much higher than other UK centers. Took years of statistical analysis (Spiegelhalter and others) to surface.
  - The Cleveland Clinic publishes its own outcomes; some hospitals will not.
  - Risk-adjustment methods (Charlson index, APACHE-II, ICU scoring).
  - The "best hospitals get the worst patients" pattern: top-tier centers attract sicker patients, raw mortality looks worse, risk-adjusted mortality is better.
- **Variations under this parent**:
  - Airline safety records.
  - University ranking systems.
  - Restaurant inspection scores.
- **Sources**: *The Risk-Adjusted Mortality* literature; the Bristol Inquiry final report (2001).

### 16. Manufacturing quality control

A factory makes thousands of widgets per day. How many can be defective before the line is shut down?

- **Why it works**: the cleanest source of statistical thinking in industry. Shewhart and Deming literally invented modern statistical quality control here.
- **Concepts illuminated**: control charts, six-sigma, special-cause vs common-cause variation, sampling-based inspection, type I and type II errors in process control, the cost of false alarms vs missed defects.
- **Specific stories and texture**:
  - Walter Shewhart at Bell Labs in the 1920s invented the control chart (the original "p-chart" for proportion defective).
  - W. Edwards Deming brought SPC to Japan in the 1950s; his 14 points became a management framework.
  - Motorola coined "Six Sigma" in 1986. The name refers to the goal of process variation being so small that the spec limits are 6 standard deviations away. Real Six Sigma processes target about 3.4 defects per million opportunities.
  - The Toyota Production System and andon cords (any worker can stop the line).
  - The 2009-10 Toyota unintended acceleration recalls. The actual cause turned out to be primarily mechanical (sticky pedals, floor mats), not software.
- **Variations under this parent**:
  - Software bug rates (less mature SPC tradition).
  - Restaurant kitchen inspections.
  - Surgical checklists (Atul Gawande, Peter Pronovost).

### 17. Spam and fraud detection

A bank's software flags some transactions as fraudulent. A spam filter classifies emails. The base rate of fraud or spam is low, the cost of false positives is real.

- **Why it works**: the asymmetric-cost framing is concrete (false positive = legit charge declined, vs false negative = stolen money). Base rate fallacy is unavoidable.
- **Concepts illuminated**: precision and recall (and why both matter), base rates dominating false-positive rates in rare-event detection, ROC curves, threshold tuning, cost-sensitive classification.
- **Specific stories and texture**:
  - Credit card fraud detection systems are tuned per merchant category. Stolen cards are often first tested on small merchants (gas stations, online subscriptions) before larger purchases.
  - Spam filtering: at the SpamAssassin / Bayesian filter era (Paul Graham's "A Plan for Spam", 2002), naive Bayes was the standard. Modern filters are deep neural nets; the math is different but the precision/recall problem is the same.
  - Synthetic identity fraud is the fastest-growing fraud category in the US. The base rate is low but the loss per case is large.
  - Anti-money-laundering (AML) systems generate enormous false positive rates. SARs (Suspicious Activity Reports) cost banks billions in compliance costs.
- **Variations under this parent**:
  - Insurance fraud detection.
  - Cybersecurity intrusion detection.
  - Counterfeit detection (currency, products).

### 18. Selection effects in online reviews

A restaurant has 4.6 stars on average. How biased is that average toward people who had memorable (good or bad) experiences?

- **Why it works**: every reader uses online ratings; the selection bias is strong, well-documented, and easy to feel.
- **Concepts illuminated**: selection bias, the U-shaped review distribution (very good or very bad people review, mediocre experiences are silent), survivorship bias generally, weighting by reviewer reliability.
- **Specific stories and texture**:
  - Amazon's review distribution is strongly bimodal: many 5-star and 1-star ratings, fewer 2/3/4. Different from the bell-curve assumption many people have.
  - The 2014 Yelp study: review-conditional probability of leaving a review correlates with extreme experiences.
  - Selection bias in sports: top performers in a season are often regression-to-mean candidates next season (Sports Illustrated jinx, again).
  - The military aircraft survival bias story (Abraham Wald, WWII): adding armor to the parts of returning planes that were NOT shot, because the planes that were shot in those places never came back to be observed.
- **Variations under this parent**:
  - Hiring data: top performers selected, talent pool truncated.
  - Movie ratings (IMDb's vote weighting).
  - Academic publication bias.
  - Customer satisfaction surveys.

### 19. Vaccine effectiveness

A vaccine is "95% effective" against a disease. What does that number mean, and how do you calculate it?

- **Why it works**: the COVID era made these numbers public-facing for two years. Most people heard "95% effective" without knowing the formula.
- **Concepts illuminated**: relative risk reduction vs absolute risk reduction, person-time, conditional probability, primary endpoints in trials.
- **Specific stories and texture**:
  - Pfizer COVID vaccine Phase III: 8 cases in vaccine arm vs 162 in placebo arm. Relative risk: 8/162 = 5%. Vaccine effectiveness: 1 - 5% = 95%.
  - The same trial: about 21,720 vaccine recipients and 21,728 placebo. So the absolute risk reduction was (162 - 8) / 21,728 = 0.71%, or about 1 case per 140 vaccinated people in the trial period.
  - Ebola vaccine ring trials in Guinea (2015) used a different design (cluster randomization to break transmission chains).
  - Influenza vaccine effectiveness: typically reported in the 40-60% range, varies by strain match and year.
  - The shingles vaccine (Shingrix): 97% effective in adults 50-69; the RCT enrolled 14,759 adults over a 4-year follow-up.
- **Variations under this parent**:
  - Antibiotic effectiveness (much harder to RCT for resistant strains).
  - Cancer screening "saves lives" claims (lead-time bias and length-time bias).
- **Sources**: NEJM publications of vaccine trials; David Spiegelhalter's COVID coverage in *The Guardian*.

### 20. Climate attribution

Has the climate warmed faster than natural variability would explain? Is hurricane X attributable to climate change?

- **Why it works**: the largest natural experiment in inference from observation that humanity has ever conducted. The mechanics are subtle and the politics intense.
- **Concepts illuminated**: trend detection in noisy time series, attribution via counterfactual climate simulations, base rates of extreme events, the difference between detection (warming is real) and attribution (X event is caused by warming).
- **Specific stories and texture**:
  - Hansen et al.'s 1988 Senate testimony was the first widely covered climate science statement. The numbers have held up; the attribution debate is now a separate research field.
  - The IPCC AR6 (2021) report's "unequivocal" attribution language emerged from decades of detection-and-attribution work.
  - Hurricane Harvey (2017): Risser & Wehner found about 19% of the rainfall was attributable to climate change.
  - Australian bushfire 2020 attribution studies: estimates of 30% increase in fire weather conditions due to anthropogenic warming.
  - The 2003 European heatwave: attribution studies estimated about 70,000 excess deaths and identified the heatwave's likelihood as 2-4x increased due to climate change.
- **Variations under this parent**:
  - Sea level rise attribution (different mechanisms, similar inference shape).
  - Air pollution and mortality (epidemiological inference).
  - Ocean acidification (chemistry plus statistics).
- **Sources**: IPCC AR6 Working Group I report; *The Discovery of Global Warming* by Spencer Weart.

### 21. Twin and adoption studies

Identical twins reared apart, fraternal twins, adopted siblings. The closest natural experiment in human behavioral genetics.

- **Why it works**: a real-world equivalent of randomization (the random assignment is genetic vs environmental). The mechanics are clean, the controversies are interesting.
- **Concepts illuminated**: heritability estimation (h^2), the equal environments assumption, gene-environment interaction, effect sizes in behavioral genetics.
- **Specific stories and texture**:
  - The Minnesota Study of Twins Reared Apart (1979-2010, Bouchard et al.). About 138 pairs of twins separated near birth, reunited as adults.
  - The "Jim twins" anecdote (Jim Lewis and Jim Springer, separated at 4 weeks, reunited at 39, eerily similar).
  - The Colorado Adoption Project (1976-): 245 adoptive families, longitudinal IQ measurements.
  - The "missing heritability" puzzle: GWAS studies find common variants explain only a small fraction of expected heritability (Yang et al. 2010 partly resolved this).
  - The flynn effect: IQ scores rose ~3 points per decade in many countries through the 20th century. Heritability is high but the population mean shifted dramatically.
- **Variations under this parent**:
  - Cross-fostering experiments in animal genetics (cleaner randomization).
  - Sibling-pair fixed-effects studies.

### 22. Multiple testing in genome-wide association studies

A GWAS scans hundreds of thousands of genetic markers for association with a trait. Most associations found by chance.

- **Why it works**: it is the cleanest large-scale demonstration that "p < 0.05" is meaningless when you do a million tests.
- **Concepts illuminated**: family-wise error rate, Bonferroni correction, false discovery rate (Benjamini-Hochberg), the "winner's curse" in effect sizes among the top hits, replication.
- **Specific stories and texture**:
  - GWAS significance threshold of 5×10^-8 (genome-wide significant) comes from approximately Bonferroni correcting 1 million independent tests at alpha 0.05.
  - The first major GWAS hits for common diseases (~2007) replicated cleanly. Earlier candidate-gene studies had failed to replicate.
  - "Missing heritability" partly resolved by realizing that thousands of small-effect loci, each with effect sizes too small to clear genome-wide significance, collectively explain variance.
  - Polygenic risk scores: combining hundreds of small effects into individual-level predictions.
  - Bem's 2011 ESP studies in *JPSP*: a high-profile non-genetics example of how multiple-testing-style problems can produce "significant" results that fail to replicate.
- **Variations under this parent**:
  - Brain imaging (fMRI multi-voxel testing).
  - Mass spectrometry proteomics.
  - High-throughput drug screens.
- **Sources**: *Statistics Done Wrong* by Alex Reinhart; the "Reproducible Research in Psychology" Open Science Framework reports.

### 23. Insurance and actuarial estimation

What is a fair premium for a life insurance policy on a 45-year-old non-smoking male in Ohio?

- **Why it works**: the original quantitative use of mortality data, the cleanest example of large-N estimation paying off.
- **Concepts illuminated**: large-N estimation (the law of large numbers in industry form), risk pooling, conditional probability, mortality tables, adverse selection.
- **Specific stories and texture**:
  - The 1693 Halley life table from Breslau (Wroclaw) was the first systematic mortality estimate.
  - The 1762 founding of the Equitable Life Assurance Society in London used Edmund Halley's tables to price annuities scientifically.
  - Modern US mortality tables (the 2017 CSO table) are based on millions of insurance deaths over decades.
  - Adverse selection: people who buy life insurance tend to have private information about their health that the insurer does not. Pricing has to account for this.
  - The 2001-2007 catastrophe insurance market post-Hurricane Andrew: actuaries had been using historical hurricane data, but the warming trend changed the base rate.
- **Variations under this parent**:
  - Health insurance pricing (much shorter time horizons).
  - Credit risk scoring (Fair Isaac / FICO, Vantage).
  - Catastrophe modeling (RMS, AIR).

### 24. Self-driving car safety

When can an autonomous vehicle be considered safer than a human driver?

- **Why it works**: a huge sample size required to show even small safety differences. The math is current and unsolved in the public discourse.
- **Concepts illuminated**: rare-event estimation, the reference-class problem (compared to which humans?), miles per disengagement as a metric, Texas-sharpshooter problems in safety claims.
- **Specific stories and texture**:
  - US human driving: about 1.1 fatalities per 100 million vehicle-miles. To show an autonomous system is "safer" with 95% confidence requires hundreds of millions of test miles.
  - The 2018 Uber self-driving fatality (Elaine Herzberg, Tempe AZ): the first known autonomous vehicle pedestrian fatality.
  - The 2016 Tesla autopilot fatality (Joshua Brown, Florida).
  - California DMV "miles per disengagement" reports show enormous variance between manufacturers, but disengagement criteria are not standardized.
  - Waymo's published safety reports: by 2024 they claimed lower-than-human accident rates with millions of miles, but the reference class debate continued.
- **Variations under this parent**:
  - Aviation safety statistics (very mature methodology).
  - Drug device safety (post-market surveillance).

### 25. Marketing attribution

A customer saw an ad on YouTube, then on Instagram, then bought the product through a Google search. Which ad gets credit?

- **Why it works**: the credit assignment problem is unsolvable in the strict sense, and yet enormous money rides on the answer.
- **Concepts illuminated**: attribution models (last-touch, first-touch, linear, time-decay, position-based), the futility of single-attribute attribution, the difference between correlation and causation in marketing data, the role of randomized holdout tests.
- **Specific stories and texture**:
  - Last-click attribution dominated digital advertising spend allocation for two decades. Famously credits the cheapest, highest-intent click (Google search) for sales that were primed by expensive top-of-funnel ads.
  - Google Analytics' Multi-Channel Funnels (2011) was an early move away from last-click.
  - The eBay 2013 study (Blake, Nosko, Tadelis): found that branded search ads, which had been credited with substantial sales, contributed essentially nothing in a randomized holdout.
  - Marketing mix modeling (MMM) returned to fashion in the 2020s after Apple's iOS privacy changes broke individual-level attribution.
- **Variations under this parent**:
  - Sales attribution in B2B (long sales cycles, multiple touchpoints).
  - Public health intervention attribution (multiple co-occurring policies).

### 26. Cancer screening and lead-time bias

A new screening test catches cancer earlier. Patients diagnosed by the new test live longer after diagnosis. Did the test save lives?

- **Why it works**: a clean and counterintuitive lesson about why "5-year survival" can be misleading.
- **Concepts illuminated**: lead-time bias, length-time bias, overdiagnosis, the importance of mortality (not "survival") as the endpoint, randomized screening trials.
- **Specific stories and texture**:
  - PSA (prostate-specific antigen) screening: caught cancers earlier, 5-year survival rates rose, but disease-specific mortality changed little. The 2009 PLCO and ERSPC trials reframed routine PSA testing.
  - Mammography for women under 50: a long-running debate over whether the false positive cascade (biopsies, anxiety, unnecessary treatment) outweighs the small mortality benefit.
  - Lung cancer CT screening for high-risk smokers: NLST trial (2011) showed about 20% mortality reduction.
  - The "thyroid cancer epidemic" in South Korea after 1999: incidence rose 15-fold, mortality unchanged. Massive overdiagnosis from ultrasound screening.
- **Variations under this parent**:
  - Diabetic retinopathy screening.
  - Colonoscopy screening.
- **Sources**: H. Gilbert Welch's *Overdiagnosed*; *Should I Be Tested for Cancer?* by Welch.

### 27. Restaurant tipping and natural experiments

Does telling diners that "everyone tips at least 18%" increase tips? Real natural experiments and field experiments here.

- **Why it works**: the mechanics are simple, the variations are diverse, and behavioral economics has used these for decades.
- **Concepts illuminated**: behavioral nudges, anchoring, suggestion-effect studies, field experiments, p-hacking and replication problems in behavioral econ.
- **Specific stories and texture**:
  - Strohmetz et al. (2002): putting a small candy on the tray with the bill increased tips by ~3-21% across studies.
  - Lynn and McCall's tip-related papers (touched, smiley face on bill, color of waitress's clothing).
  - The Ariely et al. studies on suggested tip amounts on credit card screens (anchoring).
  - The 2019 Bohren et al. paper raising statistical concerns about a chunk of the original tipping literature.
- **Variations under this parent**:
  - Default opt-in vs opt-out for organ donation, retirement contributions (Sunstein and Thaler).
  - Public-restroom hand-washing studies.
  - Posted speed-limit changes.

### 28. The hot hand fallacy and its rehabilitation

Basketball announcers say a player is "on fire" after several made shots in a row. Are they really?

- **Why it works**: a famous published-science reversal. The "hot hand is an illusion" was textbook orthodoxy from 1985 to 2018, then a subtle conditional-probability error was found in the original analysis.
- **Concepts illuminated**: conditional probability, sampling-without-replacement biases, when a result is a real phenomenon vs an artifact of the analysis, what it means to "control for" something subtly.
- **Specific stories and texture**:
  - Tversky, Gilovich, and Vallone (1985) "The Hot Hand in Basketball": the original paper, examined Cornell shooters, NBA shooters, free throws. Concluded the hot hand was an illusion, sequences were random.
  - Miller and Sanjurjo (2018): showed that "the proportion of hits after a streak of hits" is, in finite samples, biased downward as an estimator. The 1985 analysis was inadvertently controlling for a real phenomenon.
  - Replication of basketball shot data with the corrected analysis: hot hand effects of 3-5 percentage points are real and consistent with informed observers' intuitions.
- **Variations under this parent**:
  - Streakiness in baseball (DiMaggio's 56-game streak).
  - Streakiness in stock returns (some momentum effects).
  - Streakiness in coin flips? (No real effect, but psychological streak detection is robust.)

### 29. Astrology, psychic claims, and clinical trials of alternative medicine

How do you test claims that contradict known mechanisms?

- **Why it works**: forces clarity on what an experimental result means, what it would take to overturn a strong prior, and the relation between effect size and Bayesian updating.
- **Concepts illuminated**: extraordinary claims and prior probability, the file-drawer problem (publication bias), the placebo effect, double-blinding, why high-prior-improbability claims demand more evidence.
- **Specific stories and texture**:
  - Daryl Bem's 2011 *JPSP* paper claiming to find ESP via priming experiments. Used standard p-value methodology, p < 0.05 in 8 of 9 studies. Triggered the early replication crisis discussions.
  - Homeopathy clinical trials and meta-analyses: Linde 1997 (positive meta-analysis) vs Shang 2005 (null after addressing biases). The pattern of "trials get less positive as quality goes up" is itself diagnostic.
  - The CSICOP / James Randi tests of psychic claimants (1970s-2000s): all failed under controlled conditions.
  - Acupuncture sham trials: real acupuncture and "fake" acupuncture (random points, retracted needles) often produce indistinguishable improvement, larger than no-treatment controls.
- **Variations under this parent**:
  - Effects of prayer on patient recovery (STEP trial, 2006: no effect on recovery).
  - Subliminal advertising (largely overstated).

### 30. Search engine ranking and click-through

Google's search results are ordered. A new ranking algorithm is being tested. Did the new order help?

- **Why it works**: enormous traffic, tiny effects, very modern.
- **Concepts illuminated**: position bias (top results get more clicks regardless of relevance), counterfactual evaluation, interleaving experiments, online metric tradeoffs.
- **Specific stories and texture**:
  - Joachims' 2002 paper on click data from search engines: clicks cannot be naively interpreted as relevance because position dominates.
  - Interleaving experiments (Radlinski, Kurup, Joachims 2008): show two ranking algorithms' results interleaved in one list, see which one's clicks dominate. More sensitive than A/B tests for ranking.
  - Google's "Hummingbird" 2013 ranking update; the long-term experimental rollouts of large changes.
  - Bing's 2009 "RankNet to LambdaRank" change: small but reliable improvements in NDCG.

## Concept-to-example index

For each major concept in the book, the examples that illuminate it most cleanly. The first listed is the canonical anchor; later ones are alternatives if the chapter wants a different domain.

- **Hypothesis testing (is it real or chance?)**: coin (1), drug trial (2), criminal trial (6), election fraud claims (subset of polling/election work).
- **Sample size and power**: drug trial (2), polling (3), A/B testing (4), GWAS (22).
- **Confidence and credible intervals**: polling (3), insurance/actuarial (23), weather forecasting (7).
- **A/B testing structure**: A/B testing in tech (4), drug trial (2), education research (14).
- **Bayesian inversion (P(A|B) vs P(B|A))**: medical test (5), DNA forensic match (13), spam/fraud detection (17).
- **Base rate fallacy**: medical test (5), DNA match (13), spam/fraud (17), polygraph (under medical test variations).
- **Prosecutor's fallacy**: criminal trial (6), DNA forensic match (13).
- **Multiple testing**: GWAS (22), stock market anomalies (10), spam filtering (17).
- **Selection bias**: polling (3, especially the 1936 Literary Digest), online reviews (18), survival of WWII bombers (under reviews), academic publication bias.
- **Survivorship bias**: stock market fund tracking (10), online reviews (18), military aircraft (under reviews).
- **Simpson's paradox**: hospital outcomes (15), Berkeley admissions (often quoted, see Bickel 1975 - could become its own example).
- **Regression to the mean**: sports analytics (9), Sports Illustrated jinx, online reviews (18), hot hand (28).
- **Causal inference without RCT**: smoking and cancer (8), climate attribution (20), twin studies (21).
- **Replication crisis and publication bias**: drug trial (2 - Begley & Ellis), Bem's ESP (29), behavioral economics (27 - tipping reanalyses), GWAS replications (22).
- **Effect size and meaningful effects**: drug trial (2), A/B testing (4), education research (14), self-driving cars (24, what counts as meaningful safety improvement).
- **Random walks**: stock market (10), coin running fraction (1), sports streaks (9, 28).
- **Lead-time bias and length-time bias**: cancer screening (26).
- **Conditional probability misuse**: criminal trial (6 - Sally Clark), DNA match (13), hot hand fallacy (28).
- **Burden of proof and decision under uncertainty**: criminal trial (6), regulatory drug approval (under drug trial 2), hypothesis testing in general.
- **Probabilistic prediction (what does X% mean?)**: weather forecasting (7), vaccine efficacy (19), sports betting odds (under casino 11).
- **Attribution problem**: marketing attribution (25), climate attribution (20).
- **Rare events**: lottery (12), DNA match (13), self-driving car safety (24), insurance catastrophes (23).
- **Quality control and process monitoring**: manufacturing (16), hospital outcomes (15).

## Patterns I notice across examples

These are observations rather than rules; they help me pick the right example for a given concept.

- The cleanest examples for any concept are the ones where the math is exact: coin tosses, casino games, lotteries. The trade-off is that these can feel like toy problems.
- The most stakes-rich examples are biomedical and social: clinical trials, criminal trials, election polling. These are where the math meets real consequences.
- The most counterintuitive examples force the reader to slow down: Simpson's paradox in hospitals, lead-time bias in cancer screening, the prosecutor's fallacy. These are good for chapters where the goal is to disrupt the reader's instinct.
- The most visually rich examples produce arresting charts: weather forecasting (probability cones), sports analytics (player decompositions), GWAS (Manhattan plots, but those may be too technical).
- Some examples have a real "did you know" twist: the hot hand fallacy reversal, Wald's bullet-hole bombers, the 1936 Literary Digest poll. These are great for closing a chapter on a memorable note.

## Source library

The books and resources I mine when developing an example. Listed here so a future me does not have to re-discover them.

- David Spiegelhalter, *The Art of Statistics* — chapters on causation, probability, false positives.
- Persi Diaconis writings on coin physics (*The Statistical Mechanics of Coin Tossing*, with Holmes and Montgomery, 2007).
- Sharon McGrayne, *The Theory That Would Not Die* — Bayes' rule history, including its courtroom applications.
- Gerd Gigerenzer, *Reckoning with Risk* / *Calculated Risks* — base rates in medicine.
- Ben Goldacre, *Bad Pharma*, *Bad Science* — pharma trials, replication.
- Tim Harford, *The Data Detective* (US title: *How to Make the World Add Up*) — public-facing examples.
- Nate Silver, *The Signal and the Noise* — forecasting, weather, elections.
- Jordan Ellenberg, *How Not to Be Wrong* — counterintuitive examples.
- Tyler Vigen, *Spurious Correlations* — visual examples of multiple-comparison artifacts.
- Cathy O'Neil, *Weapons of Math Destruction* — algorithmic decision examples (insurance, hiring, criminal justice).
- Andrew Gelman's blog (statmodeling.stat.columbia.edu) — running commentary on contemporary statistical issues.
- Hadley Wickham's R tidy data writing — for cleaner versions of dataset stories.
- Tom Tango's *The Book* — sabermetric statistics done carefully.
- Allan Brandt, *The Cigarette Century* — the smoking-cancer history.
- Spencer Weart, *The Discovery of Global Warming* — climate inference history.
- The Cochrane reviews — gold standard for clinical evidence synthesis.
- IPCC reports (especially AR6 WGI) — climate attribution at the source.
- The original GWAS papers (the WTCCC 2007 paper is the canonical first hit).
- Ron Kohavi, Diane Tang, Ya Xu, *Trustworthy Online Controlled Experiments* — A/B testing canon.

## Process for me

- Add new examples here as they come up in feedback or in chapter writing.
- When the user mentions an example I have not catalogued, add it to this file before continuing.
- When I find that two entries in the bank are really the same example with different framings, merge them under the simpler parent.
- When I identify a clean pairing of "concept X is best demonstrated by example Y", add it to the concept-to-example index.
- This file is supposed to grow. The current version is a starting catalog, not an exhaustive one.

## Changelog

- 2026-05-05: Initial bank with 30 distinct core examples, organized by domain. Concept-to-example index, cross-cutting patterns, and source library at the bottom.
