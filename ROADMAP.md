# Roadmap: improving experimentation

- Status: 19 chapters built end-to-end, 17 expkit submodules in place, 42 tests passing. The repo is at "Beta" stage. This roadmap is the punch list to take it from "complete" to "polished".
- Each item below has a Why, a How, and an Owner-effort estimate (S = under an hour, M = a few hours, L = a day or more).
- Items are grouped by area, not by execution order. The "Suggested execution order" section at the bottom proposes a sequence.

# Area 1: library test coverage

- Why
  - Phase-1 modules (sim.coin, inference.binomial, inference.bayes, plot, io) are well-tested. Most modules added in chapters 7-17 have no direct unit tests. Without tests, narrative-driven changes can silently break the library.
- How
  - Add a tests/test_<module>.py file per untested module. Each test file should cover:
    - happy path (typical inputs, expected outputs)
    - shape/type invariants
    - one or two edge cases (empty input, boundary values, deterministic-with-fixed-seed)
    - cross-check against scipy/statsmodels where applicable
- Modules still missing direct tests
  - expkit/sim/die.py
  - expkit/sim/abtest.py
  - expkit/sim/user_segments.py
  - expkit/sim/novelty.py
  - expkit/sim/dilution.py
  - expkit/segments/behavioral.py
  - expkit/novelty/measure.py
  - expkit/metrics/quality.py
  - expkit/metrics/variance.py
  - expkit/metrics/delta.py
  - expkit/attribution/touch.py
- Effort
  - M (a few hours, ~10-15 tests per module + cross-checks)

# Area 2: Bayesian engine -- canonical PyMC usage

- Why
  - The plan declared PyMC the canonical Bayesian engine, with closed-form alongside for didactic comparison. In practice, most chapters use only the closed-form Beta math because it runs in milliseconds and ships clean charts. PyMC traces appear only in Chapters 1 and 6.
- How
  - For each chapter where the Bayesian flavor is non-trivial, add a PyMC model in generate.py, save the InferenceData to data/, and reference it from chapter.log/notebook. Closed-form remains the daily-driver in the notebooks; PyMC is the "see how this generalizes" companion.
- Specific chapters to extend
  - Ch.8 -- two-arm A/B test as a Beta-Beta hierarchical model in PyMC; show the posterior over (treatment - control).
  - Ch.11 -- segmented A/B as a hierarchical model with partial pooling. Each segment gets its own treatment effect drawn from a population-level distribution.
  - Ch.12 -- Simpson's-paradox example as a PyMC hierarchical fit. The hierarchical posterior should recover the per-segment effect even when the aggregate is misleading.
  - Ch.17 -- Bayesian multi-touch attribution as a logistic regression over channel coefficients in PyMC. Compare the posterior over channel coefficients to the four heuristic schemes.
- Effort
  - L total (each chapter is M, but the four together exercise four different model shapes)

# Area 3: notebook depth

- Why
  - Chapter 1's notebook walks the loops with code cells that mirror each step. Most other chapters have 2-4 sparse cells. A reader running the notebook should be able to retrace the inquiry, not just see static numbers.
- How
  - For each chapter, expand the notebook to mirror its loops. Each loop gets 1-2 code cells: one to compute, one to plot. Avoid duplicating generate.py's heavy work; the notebook should be fast and exploratory.
- Priority chapters (most reward)
  - Ch.5 -- comparing five interval methods deserves a side-by-side numeric printout AND an inline plot.
  - Ch.6 -- demonstrate priors-that-argue with a slider-friendly cell (one prior changed at a time).
  - Ch.8 -- A/B mechanics deserve a "look at the same data through both lenses" cell.
  - Ch.12 -- Simpson's paradox: build the toy table inline so the reader can change the segment sizes and watch the sign flip.
  - Ch.18 -- the capstone needs richer cells: read the CSV, compute the four cost regimes from arbitrary (C1, C2), explore the joint rule.
- Effort
  - M per chapter, L total

# Area 4: narrative polish

- Why
  - Chapter 1's prose is the most developed. Chapters 2-19 are tight but a second pass would reward them: cleaner sentences, tighter transitions, more memorable section headers. Some claims have approximate numbers ("about 25%") that should be replaced with exact computed numbers from the generators.
- How
  - For each chapter:
    - Re-read end-to-end aloud. Note any awkward sentence.
    - Replace any "about X" claim with the exact number computed by generate.py and cited in a footnote or inline.
    - Tighten the "Big question" line so it reads as a literal one-sentence question.
    - Verify the carried-over question at the top of chapter N+1 matches chapter N's "big question" verbatim.
- Effort
  - S per chapter, M total

# Area 5: reproducibility and infrastructure

- Why
  - The repo claims reproducibility (manifest + checksums) but does not enforce it automatically. There is no CI workflow, no pre-commit hook, no automated privacy check.
- How
  - Add .github/workflows/ci.yml that:
    - sets up Python 3.11+ in a fresh runner
    - installs the package via pip install -e ".[dev]"
    - runs pytest -m "not slow"
    - optionally runs python scripts/regenerate_all.py and asserts manifest checksums match (this is slower; could be a separate workflow)
  - Add .github/workflows/privacy.yml or a pre-commit hook that runs the existing grep guards (the privacy-policy strings listed in the local instructions) on staged content, fails the commit if any match in tracked files.
  - Add a Makefile or simple shell helpers for the common tasks: make test, make regen, make render, make notebooks.
- Effort
  - M total

# Area 6: documentation

- Why
  - A new contributor lands on the repo and has to reverse-engineer the venv + kernel + loglog dance. The README is mostly story-arc; it does not walk setup in enough detail.
- How
  - Add CONTRIBUTING.md (or expand README) with:
    - the venv + ipykernel registration steps explicitly
    - the loglog-to-markdown render command
    - the regeneration workflow and how to interpret data/manifest.yaml
    - the privacy-policy expectations for any committed file
  - Add an inline link from each chapter.md back to the README (or the previous/next chapter) so navigation is one click.
- Effort
  - S to M

# Area 7: cross-chapter coherence

- Why
  - The carried-over questions and big questions form the backbone of the inquiry-based flow. A few of them drift slightly in wording from chapter to chapter.
- How
  - Build a quick check: a small script that extracts each chapter's "big question" line (or a known-tag) and the next chapter's "carried from" line, and prints them paired. Walk the list, fix the drift.
- Effort
  - S

# Area 8: deduplication and refactor

- Why
  - Some generate.py files re-implement helpers (a hand-rolled bootstrap loop, a chi-square computation) instead of using the corresponding expkit module. This makes the chapter examples and the library drift independently.
- How
  - Audit each generate.py for hand-rolled stats. Replace with expkit imports.
  - Specifically: chapters/08-from-dice-to-ab/generate.py uses a hand-rolled bootstrap; can use expkit.inference.bootstrap.bootstrap_ci.
- Effort
  - S

# Area 9: stretch goals

- Companion exercises per chapter [DONE 2026-04-29]
  - Each chapter has an `exercises.log` (and rendered `exercises.md`) with 5 to 7 inquiry-shaped exercises tied to that chapter's loops, two-lens, and citing specific expkit functions.
- MCMC diagnostics mini-chapter [DONE 2026-04-29 as Appendix A1]
  - chapters/A1-mcmc-diagnostics/ has Loop A (a healthy sampler), Loop B (Neal's funnel: centered vs non-centered parameterization), Loop C (R-hat and ESS sweep across run lengths), with PyMC traces saved to data/.
- Hierarchical Bayesian deep-dive [DONE 2026-04-29 as Appendix A2]
  - chapters/A2-hierarchical/ walks no/complete/partial pooling, the learned tau, and the effect of the prior on tau when N per segment is small.
- Interactive playground
  - Inspiration: Nicky Case's interactive explainers (ncase.me). Patterns to steal:
    - Text -> small focused widget -> reflection text, repeated with increasing complexity (Parable of the Polygons).
    - One concept per widget, isolated. The central parameter gets a slider; everything else is fixed.
    - Live simulation that re-runs as the slider moves (Loopy, Emoji Simulator).
    - "Step" button to add one event at a time so the reader builds intuition (one coin toss, one user enters the experiment, one channel is touched).
    - Sandbox mode at the end of the chapter where multiple knobs are unlocked at once.
    - Branching/scenario shifts where the reader steps INTO the role being studied (Adventures with Anxiety, We Become What We Behold).
  - Anchor pieces (one widget per chapter, ordered by leverage)
    - Ch.1 -- single-coin sandbox: "step" button to toss once, "toss 100" button, slider on the true bias, the running fraction and posterior update in lockstep.
    - Ch.2 -- p-value visualizer: fixed coin, step a toss at a time, watch the p-value rise and fall as the count moves.
    - Ch.3 -- power slider: drag the true effect, drag the N, watch the detection rate (out of N simulated runs) update in real time.
    - Ch.5 -- CI sweeper: same data, slider on alpha, four interval methods animate side by side.
    - Ch.6 -- prior tuner: drag a Beta prior shape, watch the posterior with fixed observed data update.
    - Ch.12 -- Simpson sandbox: drag segment sizes and per-segment treatment shares; the aggregate sign flips visibly. The "I made the paradox happen" moment.
    - Ch.14 -- novelty triple-view: a single event log, three aggregation buttons (calendar / since-exposure / count); reader toggles to see the same data tell different stories.
    - Ch.18 -- capstone shipping simulator: drag the cost ratio (FP cost / miss cost), drag the threshold, watch which lens "wins" for that cost regime.
  - Tech notes
    - Single-file HTML + JS (no build step) so each widget is self-contained and embeddable.
    - Re-implement the relevant tiny piece of expkit logic in JS (binomial sampler, beta CDF, etc.). Keep the JS small; the canonical Python lives in expkit and the JS widgets cross-validate against the Python notebooks.
    - Each widget links back to the chapter and forward to the source code.
  - Effort: L (per widget M, across 8 widgets that's L+)
- Blog-form publication
  - Each chapter.md is already self-contained. Wrap them in a Jekyll/Hugo/MkDocs site, syndicate to k1monfared.github.io. Add a TOC, search, and per-chapter dates.
  - Effort: L
- Hierarchical Bayesian deep-dive companion
  - Ch.6 introduces PyMC; the meaty hierarchical models live in the segmentation chapters. A standalone companion file (or appendix) walking through one full hierarchical fit -- model spec, sampling, posterior diagnostics, predictive checks -- would cement the technique.
  - Effort: M
- Power and sample size for non-binomial outcomes
  - Currently power.binomial covers proportions. A power.continuous module for t-tests and a power.ratio for ratio metrics would round out the toolkit.
  - Effort: M

# Suggested execution order

- Phase A (low-risk infrastructure first; catches regressions during everything else)
  - Area 1 -- library test coverage
  - Area 5 -- CI + pre-commit
  - Area 6 -- contributing/setup docs
- Phase B (deepens the deliverable)
  - Area 8 -- deduplicate generators against the library
  - Area 3 -- notebook depth on priority chapters (5, 6, 8, 12, 18)
  - Area 7 -- cross-chapter coherence pass
  - Area 4 -- narrative polish
- Phase C (delivers on the canonical-PyMC promise)
  - Area 2 -- PyMC versions in chapters 8, 11, 12, 17
- Phase D (stretch)
  - Stretch goals from Area 9, in any order

# Notes

- Each phase produces commits that are independently shippable.
- Phase A is conservative: it changes nothing the reader sees but tightens the floor.
- Phase B is reader-facing polish.
- Phase C is the canonical-engine commitment from the original plan.
- Phase D is optional and only worth doing if the project graduates from "Beta" to a published reference.
