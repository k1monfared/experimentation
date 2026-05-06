# Story track learnings

This is my running notes from the user's feedback across Ch.1, Ch.2, Ch.3 of the story track. I refer to it before drafting any new story chapter and update it as the user gives me more feedback.

The story track is the parallel non-technical narrative to the experimentation book. It uses "I" voice, present tense, embodied wandering, real-stakes anchored. Each chapter is a real question anyone can connect to.

## Working title (private)

The working title is "When in doubt, toss a coin". This is a private reference and must not appear, explicitly or implicitly, in any chapter content. The title may surface in the introduction or conclusion of the book if the user chooses, but the body of the book should not play into it. The arc is: the coin toss is a lens for thinking about whether a thing is real or chance, and that lens carries through to drugs, elections, climate, and the rest of life. Treat the title as the goal of the book's structure, not a phrase to repeat.

## Companion file: examples bank

The companion file `chapters/STORY_EXAMPLES.md` holds the bank of real-world examples (drug trials, A/B testing, fluoride, polling, etc.) with concept pointers. Before starting a chapter, look there for the right anchor example. Add to that file whenever a chapter generates a new useful example.

## Process for using this doc

- Before drafting a new chapter, read this file end to end.
- The first section ("Intents") is the spine. The intents are the user's underlying goals; the specifics that follow each intent are examples, not literal rules. When I face a new situation, I work from the intent, not the example.
- The second section ("Mechanical rules") covers voice, punctuation, and other low-level rules where the intent is a single bright line. These are literal.
- After every round of user feedback, find the intent behind the feedback and put it in this file. If I cannot tell what the intent is, I keep the surface feedback as-is and flag it as ambiguous.
- If a rule turns out to apply to a chapter I have already drafted, go back and apply it.
- This doc lives at `chapters/STORY_LEARNINGS.md` so a future me can reliably find it.

## Intents

These are the underlying goals I have inferred from the user's feedback. The examples under each are specific instances the user has called out. The example is not the rule. The intent is the rule.

### Intent 1: Natural progression of a curious mind

Write as a person actually figuring things out, not as a teacher who already knows the answer. The reader should follow my live thinking, including detours and changes of direction, not consume my conclusions.

The example the user gave most explicitly: log-scale charts. Nobody draws a log-scale chart from scratch. A real scientist draws the linear chart, notices the structure is hidden, realizes log scale would expose the structure, and then redraws. The chapter should mirror that progression. Show the linear chart, sit with the reader to notice what is hidden, then say "let me try a log scale" and show the new version.

This generalizes to most technical moves in the chapter.

- Threshold conventions: don't say "I will use 5%". Try 80% in the middle, see it is too aggressive, try 90%, hear from a friend that 95% is the convention, hear from another friend that physics demands 99.9999%, settle on 95% but stay tentative. The number is found, not given.
- Naming concepts: don't introduce "effect size" then explain. Use the gap between the bias and 0.5 several times, see the pattern in the gap, then casually mention "people who do this work call this an effect size".
- Hierarchical machinery: don't drop posteriors out of nowhere. Imagine 1000 different-bias coins. Ask which one most likely produced the data. The Bayesian-flavored answer is now grounded.
- Test machinery: don't list tests upfront. Run into a situation where the rule needs a different shape, then build the new shape.

The general rule: if I am about to introduce a technical move, ask whether a curious person would have arrived at it themselves, given what they know so far. If not, back up and add the steps.

### Intent 2: Every move is motivated by what came before

Each thought, paragraph, observation, or technical move has to come naturally from the previous one. The chapter is a chain, not a list. If the reader could re-arrange paragraphs without noticing, the motivation is missing.

Examples the user has called out:

- The opening of Ch.1: weighing the coin came out of nowhere. The user pointed out: why would I weigh the coin? Because I just got HHH and I am suspicious, so I check the physical coin first, find nothing, and only then escalate. The chain has to be visible.
- The 3-heads observation in Ch.1: the user explicitly noted this should be the first escalation in a question already on the table, not the trigger for the question. The setup paragraphs (coins are not built to be fair, my brother and I, gas station dice) build the question; HHH lands inside it.
- The 5% threshold in Ch.2: it "came out of blue" because it was not connected to anything. Each step has to be motivated by the previous one.

The general rule: before any chart, technical move, or new section, ask "what is the previous beat that makes this one inevitable?". If I cannot point to that beat, the chain is broken, and I need to insert the missing beat.

### Intent 3: Sit with interesting observations, do not rush past

When something genuinely curious surfaces, the narrative dwells on it and develops it. It does not flag-and-move-on. The user notices when I have collapsed a big idea into a passing line.

Examples the user has called out:

- "What happens if I toss an unfair coin and it lands in the middle hump?" — I had a single sentence on this. The user said no, run the simulation, draw the overlap chart, sit with the implication.
- Bayesian thinking — I gave it two paragraphs in Ch.2. The user said it deserves more, build it slowly, give it room.
- Replication in Ch.3 — I had it in passing. The user said this needs its own substantive treatment with simulations and connection to the broader replication crisis.
- Peeking — I had alpha-budget as a passing technicality. The user said either treat it properly or defer it cleanly to a planned later place. Half-treating it is worse than either.

The general rule: when I notice a topic that the chapter is depending on but only mentioning, I have two options: spend the space to develop it now, or defer it explicitly to a future chapter with a promise about when it will land. I do not get to half-treat it in passing.

### Intent 4: Real stakes that touch the reader

Real-world examples have to be concrete enough that the reader feels them. Generic examples ("a drug company decides whether to ship") are textbook. Specific examples ("the drug helps a five-year-old breathe through the night, but the trial only enrolled forty patients") have stakes.

The user's explicit framing: "no dramatization, real world example". So I do not embellish. I find the genuine real-world detail and let it land.

Examples the user has called out:

- Election example: it should be the night before, the race is tight, my candidate is ahead within the margin of error, what does that mean for whether I should bother voting and which way. Not "a pollster decides how many people to call".
- A/B test example: contrast the cost of the change. Button color = one line of code, trivial. Payment provider = six months engineering, irreversible. Same machinery, very different stakes.
- The brother coin tosses: thirty years, sixty extra wins, neither of us would have noticed. Not "if a coin were biased a small amount, you might not notice".
- Fluoride in water: actual policy debate, real numbers (0.7 mg/L in US municipal water), the rhetorical structure of "studies show no harm" connected to the math.

The general rule: when I am about to write a real-world example, ask whether the reader can picture a specific moment in it. If the example is generic, find the specific version. If the specific version has fake drama, take the drama out but keep the texture.

### Intent 5: Trust through traceability

The reader should be able to verify everything. The narrator is showing work, not asserting. Numbers come from somewhere the reader could check.

Examples the user has called out:

- "Where does this curve come from? Can the reader independently create it?" - asked twice in Ch.3. The fix: explain the procedure (imagined experiments, simulator), link the play file, give the parameters.
- "Why a thousand and not a hundred or ten thousand? Let me figure that out as I go" - the user explicitly does not want appeals to authority. The narrator works it out, not invokes it.
- Drug trial numbers in the tech-company comparison - "double check the math". When the example uses concrete numbers, the numbers must be defensible.

The general rule: every quoted number, every chart, every claim about how something behaves, has to be traceable. Either I show the calculation, or I link the simulator that produces it, or I cite a real-world source. "The math says X" is the worst possible phrasing; it does the opposite of trust-building.

### Intent 6: Vocabulary discipline

The reader can only use vocabulary they have earned. Every term has to be either plain English, or introduced in this chapter, or already introduced in an earlier chapter and used since. Once introduced, it gets used (not introduced and abandoned).

Examples the user has called out:

- "Lift" used in Ch.3 while still in coin chapter - "lift" is A/B testing vocabulary, the reader was on coins. The user said: stay in coin language.
- "Alpha budget" dropped in Ch.3 without setup - the user said "way too ahead of ourselves". Defer or build first.
- "Posterior" used in Ch.2 closing examples - the user asked "what does this mean to the reader?". Either explain on first use or remove.
- "Bayesian" / "frequentist" used in Ch.3 without earning the names - if I am going to use the named tradition, I either introduce it or refer to it without the name.
- "N" instead of "number of tosses" - small but real. Stay in everyday language.
- A/B testing used twice in Ch.3 before being introduced - the user said go back to first use and add the introduction.

The general rule: scan every chapter draft for technical vocabulary. For each word, ask: is this plain English, or have I earned this with the reader? If neither, either introduce it or replace it. If I introduced a term and stopped using it, either drop the introduction or use it consistently.

### Intent 7: Honest about open caveats and tensions

When the math has a wrinkle, the narrative names the wrinkle. When two methods disagree on a particular case, the narrative shows the disagreement. The reader is treated as someone who can handle nuance.

Examples the user has called out:

- "Even tail outcomes are still possible from a fair coin" - in Ch.2, the user explicitly added this as a caveat. The original prose had over-implied that surprise-zone equals not-fair.
- "80% means 20% of the time we miss real biases" - the user noted that I was letting this slip out of view. Reiterate.
- "Where does Bayesian and frequentist match? Do they ever?" - the user noticed I was glossing past the natural reader question. Address it head-on.
- "2400 versus 780 is not the same ballpark" - the user caught me being imprecise about a comparison. Be exact.

The general rule: if I am about to make a comparison, an estimate, or a claim, ask "what would a careful reader push back on?" and pre-empt it. The story is more trustworthy when the narrator is the one pointing out the caveats.

### Intent 8: Connect to mental frameworks the reader already has

When a technical structure has a familiar real-world counterpart, drop into the counterpart. The reader does not have to build everything from scratch. They have a life full of analogies.

Examples the user has called out:

- Burden of proof in court for the surprise rule - the user explicitly suggested this connection. "Innocent until proven guilty" is the same shape as "fair until proven biased".
- Grandma's glasses for MDE - the user gave me this analogy verbatim. Bigger differences need less precision to detect.
- Football referee with pocket coin vs ceremonial coin - the user gave this as the framing for "are coins fair?".
- News headlines (studies show, no evidence of harm) - the user explicitly wanted this connection.

The general rule: when I am about to explain something, ask whether the reader has seen a structurally similar thing in real life. If yes, lead with the analogy and let the technical move ride on it.

### Intent 9: Big concepts get the space they need

I do not get to compress a major shift in framing into a paragraph because I am running long. Either I give it the development it needs, or I defer it to where I can.

Examples the user has called out:

- Bayesian thinking in Ch.2 - the user said two paragraphs is too short for "a whole new question and its answer".
- Replication in Ch.3 - the user wrote a long comment listing what should be in this section: pooling vs replicating, independence, conflict of interest, "studies show" headlines, overwhelming evidence. They want the section to actually carry that weight.
- Peeking - the user said this is important enough that it needs its own proper treatment somewhere, not a passing line.

The general rule: when I notice I am compressing a major concept, decide between two options: develop it now, or defer it cleanly. If I defer, I make a specific promise about where it will land.

### Intent 10: The narrator is a thinking person, not an authority

The narrator is fallible, curious, embodied, and visibly working things out. The reader should never feel they are being addressed by a textbook or an expert.

Examples the user has called out:

- The eggplant story in Ch.2 (added by the user) - silly, personal, lived-in. It humanizes the narrator and makes the next paragraph land.
- "I am not going to take a number on faith" - the user wanted this stance. Numbers need work, not authority.
- "I" voice everywhere instead of "we". The we-voice carries authority; the I-voice carries inquiry.
- The narrator weighing the coin in their palm at the start of Ch.1 - embodied, present-tense, real action.
- "Honest moments of confusion" - the user OK'd these explicitly. The narrator is allowed to be tired or unsure when it is true.

The general rule: when I am about to write something with the rhythm of "this is true because the math says so" or "the rule is", stop. Replace with "I am working out X. Here is what I notice." The narrator and the reader are at the same table.

### Intent 11: Accuracy is not optional, even when prose is loose

The wandering, exploratory voice is not a license to be sloppy. When I make a numerical claim, it has to be defensible. When I describe what a chart shows, the description has to match the chart. When I say two numbers are "in the same ballpark", they actually have to be.

Examples the user has called out:

- "2400 versus 780 is not the same ballpark, it is 3x larger" - I was being lazy. Same ballpark means within a factor that the reader would tolerate, not a factor of three.
- "The variation is the coin? Not really. It is the same fair coin." - I had written something logically wrong. The variation is in the tossing, not the coin.
- "50 included or not in the band?" - I had said included; the math said excluded by less than half a percentage point. The user wanted me to be precise about it.
- "Read the bars from left to right" - the chart was symmetric, so the natural reading is from the center outward. The description was wrong.
- Tech company numbers in Ch.3 - the user said "double check the math". Real-world numbers have to survive scrutiny.

The general rule: every quantitative claim, every chart description, every comparison, has to be defensible. The wandering voice does not give me a pass. If I am unsure, I check.

### Intent 12: Consistent conventions across the book

When I set up a convention (a notation, a way of phrasing something, a rule of thumb), I keep using it consistently. Switching conventions mid-chapter or mid-book without warning confuses the reader.

Examples the user has called out:

- Heads if number > threshold. The user wanted this kept consistent. I had flipped to "heads if number < threshold" for the biased case, which was confusing because the same words now meant the opposite direction.
- "Lift" in coin chapter. The convention should be "bias" or "deviation from fair" while the chapter is on coins.
- "N" versus "number of tosses". Pick one and stick with it.

The general rule: at the start of a chapter, list the conventions I am using and stick to them. If I am about to introduce a new convention, name the change explicitly.

## Mechanical rules

These are the bright-line voice and punctuation rules. No interpretation needed.

- First-person singular "I" everywhere. Never "we", "us", "our", "ours", or "ourselves".
- The only allowed "you" is the opening hook of Chapter 1 ("Have you ever considered...") and friend dialogue.
- No em dashes (—), no en dashes (–), no semicolons. Use commas, colons, periods, or sentence breaks instead.
- Present tense, embodied. The narrator is doing the thinking right now, not summarizing past thinking.
- Every chapter starts with the carry-forward question from the previous chapter. The phrase "I left the last chapter with..." is good. Do not say "the next chapter".
- Charts go ABOVE their explanation. The explanation tells the reader what to see in the chart they just looked at, not what they are about to look at.
- Bar charts always start at zero on the y-axis. (Enforced by `expkit.plot.story.bars`.)
- No pie charts ever. Use bars.
- Every figure quoted in the prose has a play simulator linked at the moment the prose discusses it.
- Privacy guard must remain clean (no AI-tool attribution in any committed file).

## Pattern: imagined-people framing for distributions

This is a useful pattern that ties several intents together. When I introduce a distribution:

1. Imagine a crowd of people doing the same experiment under the same conditions.
2. Describe a few specific people's outcomes ("around 800 of them got 50 heads, around 9 got 35").
3. Show a raw-count chart with a few bars annotated.
4. Switch to percentage chart with a tongue-in-cheek transition.

This works because: it grounds the chart (Intent 5), it is the natural progression of someone trying to picture the answer (Intent 1), and it keeps the vocabulary plain (Intent 6).

## Pattern: chart progression (linear → log → log-log)

When the structure of a curve hides at one end of the axis:

1. Draw it linear.
2. Notice with the reader that something is hidden.
3. Switch to log on the relevant axis.
4. If both directions hide structure, walk to log-log in stages: linear, x-log, both-log.

This is the natural progression of a curious mind (Intent 1). The reader follows the discovery; they are not handed the conclusion.

## Pattern: simulator links

Every quoted number is reachable through a play file. The reader can rerun the experiment with different parameters. This builds traceability (Intent 5) and keeps the work open.

The link goes in parenthetical "([Try it yourself](play/foo.py))" form, inline at the moment in prose where the chart or number lands. The play file has parameters at the top, prints interesting numbers, and shows the chart.

## Pattern: defer with a promise

When a topic deserves more space than this chapter can give:

1. Name it.
2. Acknowledge it deserves more.
3. Promise where it will land.

Example from Ch.3: "The Bayesian rule has a subtle property worth flagging because it bites people in practice. It is allowed to peek... I will come back to this when the question matters more, in the context of designing real running experiments. For now I will set it aside."

This satisfies Intent 9 (big concepts get space) while keeping the chapter's pacing.

## Open questions / things I am not sure of

When I am uncertain about the intent behind specific feedback, I keep the surface feedback as-is rather than invent a higher-order rule. Items currently here:

- Where exactly does the formal Bayesian framing land? Currently teased in Ch.2 and Ch.3 but deferred to Ch.6. Make sure Ch.6 actually does the formal treatment cleanly, with the imagined-1000-coins framing carried over.
- The peeking / alpha-budget treatment needs a chapter home. Probably an appendix or a sequential-testing aside in Ch.3, but currently deferred without a specific landing.
- Replication crisis as its own thread: currently just landed in Ch.3. Whether it gets a longer treatment elsewhere is unclear.
- Effect size as a formally introduced concept: now lightly named in Ch.3 with caveat about the technical meaning. May need its own home.
- Fluoride / "is X bad for babies" type real-stakes example: now in Ch.3. The user wanted more like this in other chapters.

## Process for me

- Before drafting a new chapter, read the Intents section. Apply each one as a question I ask of every paragraph.
- Before claiming a chapter is done, scan it for: forbidden punctuation, "we/us/our", abandoned terms, charts without justification, "the math says" phrasing, missing simulator links.
- After user feedback, before applying the changes, find the intent behind each comment. Add it to this file, even if it is a refinement of an existing intent.
- If I cannot find the intent, keep the surface feedback in the "Open questions" section.
- Keep the file maintained: if an intent turns out to be stated wrong or refined by later feedback, update the intent itself, do not just add a new one alongside.

## Changelog

- 2026-05-05: Initial draft. Captured rules from feedback on Ch.1, Ch.2, Ch.3.
- 2026-05-05: Restructured around intents (the user's underlying goals) rather than surface rules. Specifics kept as examples. The intent is the rule; the example is just the shape of the rule in one situation.
