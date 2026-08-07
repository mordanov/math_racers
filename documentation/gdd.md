# Game Design Document

# Math Racers

**Version:** 1.0

**Status:** Draft

**Document Owner:** Product Design

---

# Chapter 1. Vision & Product Overview

---

# 1.1 Executive Summary

**Math Racers** is a browser-based educational game that transforms solving arithmetic problems into a fast-paced and engaging racing competition.

The player never feels like they are doing schoolwork.

Instead, they help a team of funny characters compete in exciting running races.

Every correct answer enables the chosen runner to overcome obstacles faster than their opponents.

Over time, children become emotionally attached to their characters, celebrate their victories, collect statistics, and return to the game to achieve new personal records.

The true value of the project lies not in the racing mechanics themselves, but in building a positive emotional connection between mathematics and enjoyment.

---

# 1.2 Product Vision

Math Racers should become a game that children launch voluntarily.

Not because their parents told them to practice math.

But because they think:

> "I want to win one more race."

During gameplay, mathematics becomes a tool for achieving a goal rather than the goal itself.

The player is not thinking about arithmetic.

They are thinking about winning.

---

# 1.3 Product Mission

Make daily arithmetic practice a natural part of play.

After several weeks, children should noticeably improve their mental math skills without consciously realizing that they are studying.

---

# 1.4 Design Philosophy

The game is built around several fundamental principles.

---

## Fun First

The game must always remain a game.

Whenever there is a choice between:

> more academically accurate mathematics

and

> more engaging gameplay

gameplay always takes priority.

---

## No Punishment

Players should never feel punished.

A mistake is simply a funny little setback.

For example:

- the character stumbles,
- shakes off the dust,
- smiles,
- and continues running.

There are no red crosses.

No loud error sounds.

No messages saying:

> "WRONG!"

---

## Positive Reinforcement

Correct answers should always feel rewarding.

Every success is reinforced through:

- animation,
- acceleration,
- sound effects,
- emotional character reactions.

Even small successes should feel like victories.

---

## Short Sessions

A single race should last approximately five minutes.

At the end of each race, the player should immediately want to start another.

---

## Zero Reading

The target audience consists of young children.

Therefore, the interface should rely very little on text.

The game's primary language is:

- visuals,
- animation,
- colours,
- sound,
- character emotions.

---

## Every Character Matters

Every character has their own personality.

Players should remember them by name.

Over time, children begin cheering for specific characters.

This emotional attachment becomes one of the primary reasons they return to the game.

---

# 1.5 Target Audience

## Primary Audience

**Age:** 7–11 years old.

The first release focuses on children learning:

- addition,
- subtraction,
- multiplication,
- division.

---

## Secondary Audience

Parents.

Parents are responsible for:

- creating the account,
- configuring the game,
- selecting the difficulty level,
- reviewing statistics.

---

## Teacher Audience (Future)

Future versions may include classroom support.

The architecture should therefore anticipate:

- classrooms,
- students,
- assignments,
- leaderboards.

---

# 1.6 Learning Goals

The game should naturally improve:

## Arithmetic

- Addition
- Subtraction
- Multiplication
- Division

---

## Mental Calculation Speed

The primary learning objective.

Not only correctness.

But speed as well.

---

## Concentration

During each race, players experience light time pressure.

This helps improve focus and attention.

---

## Confidence

Children should clearly see their own improvement.

For example:

Average response time

before:

**4.8 seconds**

after:

**2.9 seconds**

---

# 1.7 Product Pillars

The entire game is built around five fundamental pillars.

---

## Pillar 1

### Competition

Everyone wants to win.

Even if the competitors are funny raccoons.

---

## Pillar 2

### Collection

Players collect characters.

Each character has:

- a name,
- a personal story,
- a unique appearance,
- individual statistics.

---

## Pillar 3

### Progress

Players should constantly feel themselves improving.

They solve problems faster.

Their favourite characters win more races.

Their collection grows.

---

## Pillar 4

### Personal Attachment

This is the most important pillar.

Eventually, children should say:

> "Frumo won today!"

instead of:

> "I solved ten math problems."

At that point, learning has become a natural by-product of gameplay.

---

## Pillar 5

### Creativity

Players create their own characters.

No two collections are alike.

Every hero is unique.

---

# 1.8 Core Fantasy

Every successful game fulfils a fantasy.

Math Racers fulfils the following one:

> "I am the coach of the funniest racing team in the world."

The player does not directly control the runner.

Instead, they help their athlete think faster.

---

# 1.9 Emotional Journey

During a single race, the player's emotions should follow this progression.

## Before the Start

Curiosity.

"Who will win?"

---

## Race Start

Excitement.

Everyone starts running simultaneously.

---

## First Obstacles

Focus.

The player begins solving problems quickly.

---

## Mid-Race

Suspense.

Who's in the lead?

---

## Final Obstacles

Maximum excitement.

There is still a chance to catch the leader.

---

## Finish Line

Emotional payoff.

Confetti.

Applause.

Medals.

---

## After the Race

Curiosity.

The player reviews statistics.

Compares characters.

Chooses the next racing team.

---

# 1.10 Product Principles

Every design decision should be evaluated against the following questions.

### Does this make the game more fun?

If not—

don't add it.

---

### Will an eight-year-old understand it without explanation?

If not—

simplify it.

---

### Can text be replaced with visuals?

If yes—

replace it.

---

### Can an entire menu be replaced with one large button?

If yes—

replace it.

---

### Will this make a child smile?

If not—

redesign it.

---

# 1.11 Success Metrics

The project is considered successful if it achieves the following metrics.

## Session Length

Average play session:

**10–20 minutes**

Equivalent to approximately:

**2–4 consecutive races**

---

## Daily Return

Children voluntarily launch the game every day.

---

## Favourite Character Rate

More than **80%** of players have a favourite character.

---

## Accuracy Growth

Average problem-solving speed steadily improves over several weeks.

---

## Parent Satisfaction

Parents observe noticeable improvement in mental arithmetic without needing to force practice sessions.

---

# 1.12 What This Game Is NOT

It is equally important to define what this project is not.

Math Racers is **not**:

- a realistic running simulator,
- a sports management game,
- an RPG,
- a collectible card game,
- an MMO,
- an ad-supported product,
- a game with microtransactions,
- a punishment-based educational application.

---

# 1.13 Long-Term Vision

In the future, this project may evolve into an entire family of educational games built upon the same architecture.

Examples include:

- **Math Racers** — Arithmetic
- **Word Racers** — Spelling and Vocabulary
- **Logic Racers** — Logical Thinking
- **Science Racers** — Natural Sciences
- **History Racers** — History Through Adventure

Every game in the series follows the same philosophy:

Children come for the fun.

Learning happens naturally as a consequence of playing.

---

**End of Chapter 1**

The next chapter, **Chapter 2 – Core Gameplay**, will define the complete gameplay loop, racing mechanics, mathematical challenge system, AI opponent behaviour, player interactions, and all gameplay states. It will serve as the foundation for the technical architecture of the entire project.

# Chapter 2. Core Gameplay

---

# 2.1 Purpose of the Gameplay

The gameplay must create the illusion that the player is participating in an exciting race.

The educational component should remain almost invisible.

The player's primary objective is:

> **Help their favourite athlete win the race.**

The mathematics exists only as the mechanism that powers the athlete.

This distinction is fundamental to the design philosophy of the game.

---

# 2.2 Core Gameplay Loop

The entire game revolves around a simple but highly repeatable gameplay loop.

```text
Launch Game
    ↓
Select Game Mode
    ↓
Select Participants
    ↓
Load Race
    ↓
Countdown
    ↓
Race Starts
    ↓
Reach Obstacle
    ↓
Solve Math Problem
    ↓
Runner Performs Action
    ↓
Continue Running
    ↓
Finish Race
    ↓
Results Screen
    ↓
Statistics Updated
    ↓
Play Again
```

Every completed race should naturally encourage the player to begin another.

---

# 2.3 Race Structure

Each race consists of a fixed number of segments.

```
START

───────────────

Obstacle 1

───────────────

Obstacle 2

───────────────

Obstacle 3

───────────────

...

───────────────

Obstacle 8

───────────────

FINISH
```

Version 1.0 contains exactly **eight mathematical checkpoints**.

This number was chosen because it provides:

- enough opportunities to recover from mistakes;
- enough excitement;
- a race duration of approximately 3–5 minutes.

Future versions may introduce configurable race lengths.

---

# 2.4 Race Participants

A race supports between **1 and 5 participants**.

One participant is always controlled by the player.

The remaining participants are AI-controlled.

All runners use identical movement rules.

No participant receives hidden advantages.

---

# 2.5 Race Start

Before the countdown:

- all runners line up at the starting line;
- each lane is highlighted;
- cameras slowly pan across the stadium;
- spectators cheer.

Countdown animation:

```
3

2

1

GO!
```

At "GO!", every runner immediately begins running.

No mathematical input is required at the start.

---

# 2.6 Continuous Running

Between obstacles, all runners continuously move.

The player never controls movement directly.

Running is automatic.

The only interaction required from the player is solving mathematical problems.

This keeps the game accessible for younger children.

---

# 2.7 Mathematical Checkpoints

At predefined distances, each runner encounters a mathematical obstacle.

For the player's runner:

- the game pauses only that runner;
- the problem appears immediately;
- AI runners continue progressing according to their own logic.

This creates a feeling of urgency without becoming stressful.

---

# 2.8 Problem Presentation

Mathematical problems should occupy the centre of the screen.

Example:

```
18 + 7 = ?
```

The interface must be:

- large;
- uncluttered;
- readable;
- distraction-free.

Only one problem is visible at any time.

---

# 2.9 Input Method

Version 1.0 supports:

- physical keyboard;
- on-screen numeric keypad;
- tablet touch input.

The answer is submitted by:

- pressing Enter;
- tapping the confirmation button.

Future versions may include handwriting recognition.

---

# 2.10 Correct Answer Flow

When the player answers correctly:

1. The answer briefly glows green.
2. The problem disappears.
3. The runner smiles.
4. A successful animation plays.
5. The runner accelerates.
6. Sparkles appear.
7. The runner continues toward the next obstacle.

The total animation duration should remain under one second to maintain pacing.

---

# 2.11 Incorrect Answer Flow

When the player answers incorrectly:

1. The answer gently shakes.
2. The runner reaches the obstacle.
3. The runner trips.
4. Dust particles appear.
5. The runner quickly stands up.
6. Running resumes.

The player should never feel punished.

The animation should feel humorous rather than frustrating.

---

# 2.12 Timing System

Every mathematical problem records:

- appearance timestamp;
- first key press;
- submission time;
- correctness.

From these values, the system calculates:

- reaction time;
- solving time;
- average response time;
- personal bests.

These statistics are later shown to both parents and children.

---

# 2.13 Movement Model

Every obstacle awards a movement bonus.

Example values:

| Result | Distance Bonus |
|---------|---------------:|
| Perfect answer (<2 s) | +18 m |
| Excellent (<4 s) | +15 m |
| Good (<6 s) | +12 m |
| Slow but correct | +9 m |
| Incorrect | +0 m |

These values will be balanced during playtesting.

The important principle is:

**Fast thinking creates visible progress.**

---

# 2.14 Catch-Up Opportunities

A race should remain exciting until the finish.

Even if a runner falls behind early, they should still have realistic chances of recovering.

Mechanisms include:

- larger bonuses for exceptionally fast answers;
- occasional AI mistakes;
- balanced obstacle spacing.

No race should feel decided after the first obstacle.

---

# 2.15 AI Behaviour

AI opponents solve problems internally.

Each AI runner has individual attributes:

- accuracy;
- reaction speed;
- consistency;
- confidence;
- luck.

These attributes produce believable behaviour.

Some runners are consistently fast.

Others are slow but reliable.

Others occasionally make dramatic mistakes.

---

# 2.16 Race Pace

The race should naturally alternate between:

```
Running

↓

Thinking

↓

Acceleration

↓

Running

↓

Thinking

↓

Celebration
```

This rhythm keeps gameplay engaging.

The player is almost constantly switching between action and problem solving.

---

# 2.17 Camera Behaviour

The camera follows the player's runner.

It should:

- remain smooth;
- never shake violently;
- keep nearby competitors visible.

Important events automatically trigger subtle camera adjustments.

Examples:

- another runner overtakes;
- final sprint;
- finish line.

---

# 2.18 Finish Sequence

When the player's runner crosses the finish line:

- confetti launches;
- the crowd cheers;
- the runner celebrates;
- finishing position is displayed.

Other runners continue until they also finish.

The race officially ends only after every participant has crossed the finish line.

---

# 2.19 Race Results

After the race, the player immediately sees:

- finishing order;
- medals;
- total race time;
- correct answers;
- incorrect answers;
- average solving time;
- fastest answer;
- favourite moments.

The results screen should feel like a celebration rather than a report card.

---

# 2.20 Replayability

No two races should feel identical.

Variation comes from:

- different opponents;
- different mathematical problems;
- AI personalities;
- changing race dynamics;
- character animations.

The race structure remains familiar while every session feels unique.

---

# 2.21 Failure Philosophy

There is no concept of "losing."

If the player's runner finishes last:

- everyone celebrates;
- medals are still awarded;
- statistics improve;
- characters congratulate one another.

Children should always leave the race feeling encouraged to try again.

---

# 2.22 Gameplay Design Rules

Every gameplay feature must satisfy the following rules:

1. Mathematics must always feel like a superpower, never like homework.
2. Players should spend more time smiling than reading.
3. The race should remain exciting until the final obstacle.
4. Every correct answer should produce an immediate visual reward.
5. Every mistake should create a funny moment rather than frustration.
6. Every race should generate at least one memorable event.
7. The player should always want to press **"Play Again."**

---

# 2.23 Gameplay Success Criteria

The gameplay is considered successful if:

- children voluntarily replay races;
- average session length exceeds three races;
- favourite characters naturally emerge;
- players improve their solving speed over time;
- mathematics becomes associated with excitement rather than obligation.

---

**End of Chapter 2**

The next chapter, **Chapter 3 – Player Experience**, will define the complete user journey from launching the game for the first time through long-term engagement, emotional progression, onboarding, accessibility, and player psychology.

# Chapter 3. Player Experience

---

# 3.1 Purpose

This chapter defines how the player should **feel** throughout the entire lifecycle of the game.

Unlike gameplay mechanics, which describe **what happens**, player experience describes **how those events should be perceived emotionally**.

Every screen, animation, sound effect and interaction must support this emotional journey.

---

# 3.2 Design Principle

The player should never think:

> "I need to practice mathematics."

Instead, the player should think:

> "Let's do another race!"

Learning is intentionally hidden behind entertainment.

This principle guides every design decision in the project.

---

# 3.3 Emotional Lifecycle

The player's relationship with the game evolves over time.

---

## First Session

Emotion:

**Curiosity**

Questions:

- What is this game?
- Who are these funny characters?
- Can I make my own?

Goal:

The player creates their first avatar within five minutes.

---

## First Race

Emotion:

**Excitement**

The player experiences:

- countdown
- cheering audience
- first obstacle
- acceleration
- finish line
- medals

Goal:

The child should smile before the race ends.

---

## First Victory

Emotion:

**Pride**

The player should immediately feel:

> "My runner won!"

Not:

> "I solved math correctly."

---

## Several Sessions Later

Emotion:

**Attachment**

Children start saying things like:

> "I always choose Luna."

> "Max is unlucky today."

This emotional attachment is one of the primary retention mechanisms.

---

## Long-Term

Emotion:

**Ownership**

Eventually the collection belongs to the player.

The game becomes:

"My team."

"My champions."

"My statistics."

---

# 3.4 First Launch Experience

The very first launch is extremely important.

The player should never be overwhelmed.

The ideal sequence is:

```
Logo

↓

Welcome

↓

Create Character

↓

Play First Race

↓

Celebrate

↓

Results

↓

Play Again
```

The entire onboarding should take less than five minutes.

---

# 3.5 Onboarding Philosophy

Never explain mechanics using long tutorials.

Instead:

Teach by playing.

For example:

Instead of displaying:

> Solve mathematical examples to make your runner move.

Simply present the first obstacle immediately.

The player naturally understands:

"I answer correctly."

↓

"My runner becomes faster."

No explanation required.

---

# 3.6 Progressive Disclosure

The player should only discover new concepts when they become relevant.

Example progression:

First race:

- one runner
- one operation
- simple problems

Second race:

- multiple runners

Third race:

- statistics

Later:

- championships
- achievements
- collections

The interface should grow together with the player's understanding.

---

# 3.7 Cognitive Load

Children between seven and eleven years old have limited working memory.

Therefore:

Never present multiple important decisions simultaneously.

Avoid screens containing:

- many buttons
- long menus
- large paragraphs
- multiple dialogs

Every screen should have one obvious action.

---

# 3.8 Decision Simplicity

Every interaction should require minimal thinking.

Example:

Good:

```
PLAY
```

Better:

```
▶ PLAY
```

Best:

A large colourful button occupying the centre of the screen.

---

# 3.9 Flow State

The ideal gameplay rhythm:

```
Run

↓

Think

↓

Answer

↓

Celebrate

↓

Run

↓

Think

↓

Answer

↓

Celebrate
```

There should never be long pauses.

The player should remain continuously engaged.

---

# 3.10 Reward Frequency

Children require frequent positive feedback.

The game should provide rewards approximately every:

10–20 seconds.

Rewards include:

- acceleration
- applause
- stars
- cheering
- medals
- funny animations
- compliments
- statistics improvements

Waiting several minutes for a reward significantly reduces engagement.

---

# 3.11 Character Attachment

Characters are not disposable assets.

They are companions.

Each character should possess:

- name
- appearance
- personality
- favourite colour
- favourite food
- favourite hobby
- statistics
- racing history

Children should remember them.

---

# 3.12 Emotional Safety

The game should never produce feelings of failure.

Bad examples:

❌ "Incorrect."

❌ "You failed."

❌ "Game Over."

❌ "Try harder."

Instead:

✅ "Almost!"

✅ "Nice try!"

✅ Funny stumble animation.

The player should laugh rather than feel embarrassed.

---

# 3.13 Parent Experience

Parents are secondary users.

Their emotional journey is different.

Parents should feel:

- confidence
- simplicity
- educational value

Parents should immediately understand:

"My child is learning while enjoying themselves."

Parents need:

- progress reports
- statistics
- difficulty controls

Nothing more.

---

# 3.14 Session Completion

The end of every race should feel satisfying.

A race never ends abruptly.

Instead:

```
Finish

↓

Celebration

↓

Statistics

↓

Character Reactions

↓

Achievements

↓

Play Again
```

The celebration is almost as important as the race itself.

---

# 3.15 Motivation Without Pressure

The game should motivate without creating anxiety.

Avoid:

- countdown timers for answers
- harsh penalties
- ranking shame
- public leaderboards

Encourage:

- personal improvement
- favourite characters
- collection growth
- fun competitions

---

# 3.16 Positive Failure

Failure becomes entertainment.

Example:

The runner:

- hits a hurdle,
- performs a dramatic flip,
- lands safely,
- smiles,
- continues running.

The player laughs.

The emotional outcome is positive.

---

# 3.17 Delight Moments

Every session should contain several unexpected moments.

Examples:

- a bird lands on the track;
- spectators wave funny signs;
- balloons float across the stadium;
- a runner performs a silly victory dance;
- confetti cannon fires unexpectedly;
- a rival congratulates the winner.

These moments create memorable experiences.

---

# 3.18 Personality Through Animation

Characters communicate primarily through movement.

Examples:

Confident runner:

- runs upright
- waves
- celebrates dramatically

Shy runner:

- small smile
- quiet celebration
- modest gestures

Excited runner:

- jumps constantly
- claps
- spins after winning

Animations are more important than dialogue.

---

# 3.19 Audio Experience

Audio should reinforce emotions without becoming repetitive.

Positive sounds:

- applause
- whistles
- cheering
- footsteps
- acceleration effects

Negative feedback should remain soft and playful.

No harsh buzzers.

No alarming sounds.

---

# 3.20 Accessibility of Emotion

Even children who cannot yet read fluently should understand:

- success
- mistakes
- victory
- progress

Purely from:

- colours
- animations
- sounds
- expressions
- movement

Reading should never be required to enjoy the game.

---

# 3.21 Long-Term Engagement

Players should return because they care about:

- their favourite runner;
- improving statistics;
- unlocking achievements;
- beating previous records;
- trying new characters.

They should not return because of artificial daily rewards or addictive mechanics.

The motivation should remain intrinsic.

---

# 3.22 Trust

Parents must trust the game completely.

The product should never include:

- advertisements;
- loot boxes;
- manipulative monetisation;
- gambling mechanics;
- fear of missing out;
- dark UX patterns.

The game should feel safe enough that a parent can confidently leave their child playing independently.

---

# 3.23 Experience Quality Checklist

Every new feature should satisfy the following questions.

Does it:

- make the player smile?
- reduce frustration?
- improve clarity?
- strengthen attachment to characters?
- encourage another race?
- support learning naturally?

If any answer is "No," the feature should be redesigned.

---

# 3.24 Ultimate Experience Goal

When asked about the game several months later, the child should not say:

> "It's a maths game."

Instead, they should say:

> "It's the game where my funny runners race each other."

At that moment, the educational objective has been fully achieved.

---

**End of Chapter 3**

The next chapter, **Chapter 4 – Avatar System**, will define one of the most important systems in the project: AI-generated characters, personality generation, persistent progression, image generation pipeline, storage model, emotional attachment mechanics, and the complete avatar lifecycle from creation to retirement.

# Chapter 4. Avatar System

---

# 4.1 Purpose

The Avatar System is the emotional heart of Math Racers.

Without memorable characters, the game becomes little more than a collection of arithmetic exercises.

With memorable characters, children begin forming emotional bonds, developing favourites, and creating their own stories.

The objective of this system is to transform AI-generated images into living personalities.

---

# 4.2 Design Goals

The Avatar System must satisfy the following goals.

- Every avatar is unique.
- Every avatar has a personality.
- Every avatar is memorable.
- Every avatar improves over time.
- Every avatar persists forever unless deleted.
- Players become emotionally attached to their favourites.

The avatar is **never** disposable.

---

# 4.3 Avatar Lifecycle

Every avatar progresses through the following lifecycle.

```
Created

↓

Generated

↓

Named

↓

Saved

↓

Selected

↓

Races

↓

Improves Statistics

↓

Becomes Favourite

↓

Retires (optional)

↓

Archived
```

No avatar should ever disappear automatically.

---

# 4.4 Maximum Collection Size

Version 1.0 supports:

**100 avatars**

This is intentionally generous.

Children should never feel forced to delete favourite characters.

Future versions may increase this limit.

---

# 4.5 Avatar Creation Philosophy

The player should never edit individual pixels or body parts.

Instead, avatar creation is based on imagination.

Children answer a few simple questions.

The AI transforms those answers into a believable racing character.

The creation process should feel magical.

---

# 4.6 Character Generator Flow

The complete flow is:

```
Press

New Avatar

↓

Choose Appearance

↓

Choose Personality

↓

Generate Character

↓

AI Creates Character

↓

Review

↓

Accept

↓

Save
```

Generation should take no longer than several seconds.

---

# 4.7 Player Input

The player chooses only high-level characteristics.

Examples include:

- favourite animal
- hairstyle
- skin colour
- eye colour
- nose size
- ears
- moustache
- beard
- glasses
- favourite colour
- mood

The interface should use large illustrated cards instead of text whenever possible.

---

# 4.8 AI Creativity

The player does **not** design every detail.

Instead, the AI is encouraged to introduce creative variations.

Example:

Player chooses:

```
Fox

Purple hair

Big nose

Funny

Blue jacket
```

The AI may generate:

- fluffy tail
- oversized trainers
- colourful wristbands
- expressive eyebrows
- racing goggles
- cheerful smile

The character should always feel slightly surprising.

---

# 4.9 Character Identity

Every generated avatar receives:

- unique name
- portrait
- personality
- short biography
- favourite hobby
- favourite food
- favourite saying
- creation timestamp

These attributes never change automatically.

---

# 4.10 Character Naming

Names are generated by the LLM.

Requirements:

- easy to pronounce
- suitable for children
- memorable
- playful
- globally understandable

Good examples:

- Frumo
- Bongo
- Lumo
- Pika
- Tiko
- Nori
- Fifi
- Pogo

Avoid:

- existing celebrities
- offensive words
- difficult spellings
- excessively long names

---

# 4.11 Character Biography

Every avatar receives a short story.

Length:

40–80 words.

Example:

> Frumo is an energetic fox who dreams of becoming the fastest runner in the world.
> He loves banana smoothies, laughs loudly, and believes every race is an adventure.
> Even after stumbling, he always gets back up smiling.

Stories should be positive, optimistic and child-friendly.

---

# 4.12 Personality Model

Each avatar contains hidden personality traits.

Examples:

```
Confidence

Kindness

Curiosity

Competitiveness

Patience

Optimism

Bravery

Energy

Playfulness
```

Each trait uses a value between 1 and 100.

These values influence animations and AI behaviour.

---

# 4.13 Personality Behaviour

Different personalities produce different behaviour.

Example:

Confident:

- celebrates dramatically
- waves at spectators
- smiles often

Shy:

- quieter celebrations
- smaller gestures
- less eye contact

Energetic:

- bounces before races
- jumps after victories
- runs with exaggerated movement

Children should notice personality differences without reading descriptions.

---

# 4.14 Favourite Character

Players may mark one avatar as their favourite.

Only one favourite exists at any time.

The favourite appears:

- first in selection screens;
- on the home screen;
- in statistics;
- in promotional artwork.

The favourite status has no gameplay advantage.

---

# 4.15 Avatar Statistics

Every avatar accumulates lifetime statistics.

Examples:

```
Games Played

Wins

Second Places

Third Places

Average Finish

Average Speed

Correct Answers

Wrong Answers

Fastest Answer

Best Race

Favourite Operation

Longest Winning Streak

Current Streak

Total Distance Run
```

Statistics are permanent.

---

# 4.16 Character Development

Characters never gain traditional RPG levels.

Instead, they gain history.

Example:

```
Created:
April 2027

Games:
183

Victories:
41

Favourite Since:
May 2027

Fastest Answer:
1.8 seconds
```

History creates emotional attachment.

---

# 4.17 Avatar Gallery

All characters are stored inside a gallery.

The gallery supports:

- grid view
- search
- sort
- favourite filter
- recently created
- alphabetical order
- most victories
- most races

The gallery should resemble a sticker collection rather than a database.

---

# 4.18 Avatar Detail Screen

Selecting an avatar opens a dedicated profile.

The profile contains:

- large portrait
- name
- biography
- personality summary
- achievements
- statistics
- favourite status
- race history

This screen should feel like visiting a sports hero's profile.

---

# 4.19 Avatar Consistency

Every generated image must remain visually consistent forever.

The system should never regenerate a portrait automatically.

If future assets require new poses, they must preserve:

- colours
- proportions
- facial features
- clothing
- hairstyle
- accessories

The player must instantly recognise the character.

---

# 4.20 Image Generation Pipeline

The generation process consists of multiple steps.

```
Player Choices

↓

LLM

↓

Structured Character Description

↓

Prompt Builder

↓

Image Generation Model

↓

Quality Validation

↓

Store Image

↓

Store Prompt

↓

Save Avatar
```

Every generation should be reproducible.

The original prompt is permanently stored.

---

# 4.21 Image Requirements

Every avatar image must satisfy the following requirements.

- Full body.
- Front view.
- Standing pose.
- White or transparent background.
- Entire character visible.
- No cropped limbs.
- No text.
- No logos.
- Child-friendly proportions.
- Consistent art style.

These requirements enable future animation.

---

# 4.22 Character Style Rules

Characters are:

- funny
- expressive
- slightly exaggerated
- colourful
- soft
- friendly

They are never:

- scary
- realistic
- aggressive
- muscular
- creepy
- overly detailed

Children should immediately want to meet them.

---

# 4.23 Emotional Expressions

Every avatar supports multiple expressions.

Required expressions:

- happy
- surprised
- determined
- laughing
- disappointed
- celebrating
- cheering
- thinking

Future versions may generate expression sheets automatically.

---

# 4.24 Animation Compatibility

Every generated design must support future animation.

Avoid:

- extremely long clothing
- tiny accessories
- overlapping limbs
- complicated silhouettes

Characters should remain easy to animate.

---

# 4.25 Duplicate Prevention

Two characters should never appear visually identical.

The generation pipeline should compare:

- colour palette
- species
- hairstyle
- clothing
- accessories

If similarity exceeds an acceptable threshold, regeneration should occur automatically.

---

# 4.26 Safety Rules

Generated characters must never contain:

- weapons
- violence
- blood
- horror elements
- political symbols
- religious symbols
- alcohol
- tobacco
- gambling references
- inappropriate clothing

Every avatar must be suitable for young children.

---

# 4.27 Storage Model

Each avatar stores:

```
Avatar ID

Player ID

Name

Biography

Personality

Image Prompt

Portrait Image

Thumbnail

Statistics

Favourite Flag

Creation Time

Update Time

Version
```

Future fields should be added without breaking compatibility.

---

# 4.28 Future Expansion

The Avatar System is intentionally extensible.

Future versions may support:

- alternative outfits;
- seasonal costumes;
- animated portraits;
- voice generation;
- friendships;
- rivalries;
- favourite stadiums;
- signature celebrations;
- collectible accessories.

These features must remain cosmetic.

Gameplay balance must never depend on appearance.

---

# 4.29 Design Principles

Every avatar should satisfy the following principles.

- Instantly recognisable.
- Easy to remember.
- Easy to love.
- Fun to watch.
- Pleasant to animate.
- Safe for children.
- Unique without becoming bizarre.

---

# 4.30 Success Criteria

The Avatar System is considered successful if:

- children remember character names;
- players repeatedly choose the same favourite;
- collections continue growing over time;
- players feel proud of their teams;
- avatars become the primary reason children return to the game.

If children begin saying:

> "Let's race with Frumo today!"

instead of

> "Let's practice maths."

then the Avatar System has achieved its purpose.

---

**End of Chapter 4**

The next chapter, **Chapter 5 – Mathematics Engine**, will define the complete educational model: adaptive difficulty, problem generation algorithms, learning progression, skill tracking, operation balancing, answer validation, and the architecture of the arithmetic engine that powers the entire game.

# Chapter 5. Mathematics Engine

---

# 5.1 Purpose

The Mathematics Engine is the educational core of Math Racers.

Its purpose is **not** simply to generate arithmetic problems.

Its primary responsibility is to keep every player inside their **optimal learning zone**, where problems are challenging enough to require thinking but easy enough to be solved successfully.

The engine must continuously adapt to the player's abilities without requiring manual configuration.

---

# 5.2 Design Philosophy

The Mathematics Engine follows one fundamental principle:

> **Every child should feel successful while continuously improving.**

The engine should never intentionally frustrate the player.

Likewise, it should never become so easy that the player becomes bored.

---

# 5.3 Responsibilities

The Mathematics Engine is responsible for:

- generating arithmetic problems;
- validating answers;
- measuring solving speed;
- tracking accuracy;
- estimating player skill;
- adapting difficulty;
- preventing repetitive questions;
- balancing mathematical operations;
- collecting educational statistics.

The engine does **not** manage gameplay, movement, or animations.

---

# 5.4 Supported Operations

Version 1.0 supports four arithmetic operations.

- Addition
- Subtraction
- Multiplication
- Division

Future releases may introduce:

- fractions;
- decimals;
- negative numbers;
- percentages;
- powers;
- square roots;
- equations;
- algebra;
- geometry;
- word problems.

The architecture must remain operation-agnostic.

---

# 5.5 Learning Domains

Each mathematical operation is treated as an independent skill.

Example:

```
Addition

Difficulty 4

Accuracy 96%

Average Time 2.4 s
```

```
Multiplication

Difficulty 2

Accuracy 71%

Average Time 5.9 s
```

A player may be advanced in one domain while remaining a beginner in another.

---

# 5.6 Difficulty Model

Difficulty is represented as a numeric value.

```
Difficulty

1

↓

2

↓

3

↓

...

↓

100
```

The exact mapping between difficulty and generated problems is defined internally.

Gameplay never exposes this value directly.

---

# 5.7 Adaptive Learning

Difficulty adapts continuously.

The engine observes:

- accuracy;
- response time;
- recent performance;
- consistency.

Example:

```
High Accuracy

+

Fast Answers

↓

Increase Difficulty
```

```
Frequent Mistakes

↓

Reduce Difficulty
```

Adjustments should be gradual.

Players should never notice sudden jumps.

---

# 5.8 Target Success Rate

The engine aims for an average success rate between:

**80% and 90%**

Research consistently shows that this range maximises learning while maintaining motivation.

Below 70%:

Players become discouraged.

Above 95%:

Learning slows significantly.

---

# 5.9 Problem Categories

Every generated problem belongs to one category.

Examples:

Addition:

```
4 + 3

18 + 6

47 + 25

356 + 429
```

Subtraction:

```
8 − 3

42 − 17

600 − 284
```

Multiplication:

```
3 × 6

7 × 8

12 × 11
```

Division:

```
42 ÷ 6

81 ÷ 9

144 ÷ 12
```

Future operations follow the same abstraction.

---

# 5.10 Difficulty Dimensions

Difficulty depends on multiple independent factors.

Examples:

- number size;
- carrying (addition);
- borrowing (subtraction);
- multiplication table range;
- division complexity;
- number of digits;
- mental workload.

Difficulty should never be based solely on larger numbers.

---

# 5.11 Problem Templates

Problems are generated from reusable templates.

Example:

Addition:

```
A + B
```

Subtraction:

```
A − B
```

Multiplication:

```
A × B
```

Division:

```
A ÷ B
```

Template parameters define valid ranges.

---

# 5.12 Problem Generation Rules

Generated problems must satisfy the following principles.

- Always have exactly one correct answer.
- Never produce ambiguous results.
- Never repeat immediately.
- Match the player's difficulty level.
- Respect educational progression.

Every generated problem should feel natural.

---

# 5.13 Duplicate Prevention

The player should not repeatedly encounter the same examples.

The engine maintains a history of recently generated problems.

Recent problems receive a temporary penalty during generation.

Example:

```
8 × 7
```

should not appear twice in the same race.

---

# 5.14 Educational Progression

Each operation progresses through increasingly complex stages.

Example for Addition:

Level 1

```
3 + 2
```

↓

Level 2

```
8 + 7
```

↓

Level 3

```
27 + 15
```

↓

Level 4

```
48 + 39
```

↓

Level 5

```
358 + 427
```

Progression should feel smooth.

---

# 5.15 Error Tracking

Incorrect answers provide valuable information.

The engine records:

- expected answer;
- submitted answer;
- solving time;
- operation;
- difficulty;
- timestamp.

Patterns of mistakes help identify learning gaps.

---

# 5.16 Skill Estimation

Each operation maintains an estimated player skill.

Example:

```
Addition

Skill

83
```

This value is hidden.

It influences future problem generation.

---

# 5.17 Response Time Analysis

The engine distinguishes between:

Fast Correct

↓

Ideal

---

Slow Correct

↓

Learning

---

Fast Incorrect

↓

Guessing

---

Slow Incorrect

↓

Difficulty Too High

Each pattern leads to different adaptation behaviour.

---

# 5.18 Personal Bests

The engine tracks achievements such as:

- fastest addition;
- fastest multiplication;
- longest correct streak;
- highest daily accuracy;
- most improved operation.

These statistics motivate continued practice.

---

# 5.19 Correct Streaks

Correct answers contribute to streaks.

Example:

```
✔

✔

✔

✔

✔
```

↓

5-answer streak

Longer streaks may trigger:

- visual effects;
- cheering;
- bonus celebrations.

They do **not** increase mathematical difficulty immediately.

---

# 5.20 Mistake Recovery

One mistake should never ruin a race.

Similarly, one mistake should not dramatically reduce difficulty.

The engine evaluates rolling performance over many problems.

This prevents unstable behaviour.

---

# 5.21 Daily Learning Profile

Each day generates a learning summary.

Example:

```
Problems Solved

84

Accuracy

91%

Average Time

3.2 s

Best Operation

Multiplication

Needs Practice

Division
```

Parents may view this information.

Children primarily receive visual summaries.

---

# 5.22 Educational Statistics

The engine records:

- total problems solved;
- total correct;
- total incorrect;
- average response time;
- operation distribution;
- daily activity;
- weekly activity;
- monthly activity.

These statistics support future analytics.

---

# 5.23 Validation Rules

Every submitted answer is validated immediately.

Validation must be:

- deterministic;
- fast;
- offline-capable;
- independent of UI.

The validation engine should respond within milliseconds.

---

# 5.24 Performance Requirements

Problem generation should require:

Less than **1 millisecond** on average.

Answer validation should require:

Less than **0.1 milliseconds**.

The player should never experience delays.

---

# 5.25 Extensibility

New mathematical topics should be added by implementing new generators.

Every generator exposes a common interface.

Example:

```
Generate()

↓

Problem

Expected Answer

Difficulty

Metadata
```

The gameplay engine remains unaware of the underlying mathematics.

---

# 5.26 Localisation

Problem formatting must respect localisation.

Examples:

Decimal separator.

Thousands separator.

Operator symbols.

Reading direction.

The mathematical engine itself remains language-independent.

---

# 5.27 Educational Integrity

The engine should follow accepted educational practices.

Examples:

- introduce concepts gradually;
- reinforce weak areas;
- revisit older material;
- avoid overwhelming complexity;
- encourage confidence.

Entertainment should never compromise educational correctness.

---

# 5.28 Future AI Personalisation

Future versions may incorporate AI-driven tutoring.

Examples:

- identifying persistent misconceptions;
- recommending practice sessions;
- explaining common mistakes;
- predicting learning pace;
- suggesting personalised training plans.

This functionality should remain optional.

---

# 5.29 Design Principles

Every generated problem should satisfy the following rules.

- Appropriate for the player's skill.
- Solvable mentally.
- Educationally meaningful.
- Free from ambiguity.
- Varied.
- Fair.
- Fast to evaluate.

---

# 5.30 Success Criteria

The Mathematics Engine is considered successful if:

- players naturally improve over time;
- accuracy remains between 80% and 90%;
- children rarely complain that problems are "too easy" or "too hard";
- parents observe measurable progress;
- mathematics becomes associated with confidence rather than anxiety.

When children begin solving increasingly difficult arithmetic without noticing that the engine has been adapting behind the scenes, the Mathematics Engine has fulfilled its purpose.

---

**End of Chapter 5**

The next chapter, **Chapter 6 – Race Engine**, will define the complete simulation model: race state machine, runner movement, obstacle timing, animation events, camera behaviour, physics abstraction, AI synchronisation, and deterministic race execution.

# Chapter 6. Race Engine

---

# 6.1 Purpose

The Race Engine is responsible for simulating every race in the game.

It coordinates:

- race progression;
- runner movement;
- obstacle timing;
- mathematical checkpoints;
- AI synchronization;
- animations;
- camera events;
- race completion.

The Race Engine **does not** generate mathematics, create avatars, or render graphics.

It is a deterministic simulation that exposes events consumed by the presentation layer.

---

# 6.2 Design Philosophy

The Race Engine follows three core principles.

## Deterministic

Given the same inputs, the race must always produce the same result.

This simplifies:

- debugging;
- replay generation;
- testing;
- balancing.

---

## Event-Driven

The engine never directly manipulates the user interface.

Instead, it emits events.

Example:

```
RunnerAccelerated

↓

Animation System

↓

Play Sprint Animation
```

---

## Presentation Independent

The engine contains no knowledge of:

- colours;
- sprites;
- sounds;
- animations;
- user interface.

It only manages race state.

---

# 6.3 Race Lifecycle

Every race follows the same lifecycle.

```
Created

↓

Loaded

↓

Waiting

↓

Countdown

↓

Running

↓

Finishing

↓

Finished

↓

Archived
```

Each state has clearly defined transitions.

---

# 6.4 Race State Machine

```
Idle

↓

Loading

↓

Ready

↓

Countdown

↓

Running

↓

Completed

↓

Results
```

Invalid state transitions must be rejected.

Example:

```
Running

↓

Loading

```

is impossible.

---

# 6.5 Race Configuration

Each race contains immutable configuration.

Example:

```
Track Length

800 m

Number of Lanes

5

Obstacle Count

8

Difficulty

Medium

Weather

Sunny
```

The configuration never changes once the race begins.

---

# 6.6 Track Model

Version 1.0 uses a simple linear track.

```
START

──────────────────────────────

FINISH
```

Each runner occupies one lane.

Future versions may introduce:

- curves;
- jumps;
- different stadiums;
- themed environments.

The simulation remains unchanged.

---

# 6.7 Lane Model

Each participant receives one dedicated lane.

Rules:

- runners never change lanes;
- runners never collide;
- lanes have identical length;
- no lane offers an advantage.

This ensures fairness.

---

# 6.8 Distance System

Internally, distance is represented numerically.

Example:

```
0 m

↓

100 m

↓

250 m

↓

470 m

↓

800 m
```

Rendering converts this value into screen coordinates.

---

# 6.9 Runner State

Each runner maintains independent state.

Example:

```
Current Position

Current Speed

Current Obstacle

Animation State

Race Status

Finish Time

Penalty State
```

The Race Engine owns these values.

---

# 6.10 Base Running Speed

Every runner has the same base speed.

This guarantees fairness.

Performance differences arise only from:

- mathematical answers;
- AI decision timing;
- temporary bonuses.

---

# 6.11 Obstacle Placement

Obstacles are evenly distributed across the track.

Example:

```
100 m

200 m

300 m

400 m

500 m

600 m

700 m

780 m
```

Spacing may vary slightly for visual rhythm.

---

# 6.12 Obstacle Activation

When a runner reaches an obstacle:

```
Running

↓

Obstacle Triggered

↓

Waiting for Answer

↓

Resolved

↓

Running
```

Only that runner pauses.

Other runners continue.

---

# 6.13 Player Synchronisation

The player's runner waits for an answer.

The simulation remains active.

AI runners continue solving their own problems.

This creates natural race dynamics.

---

# 6.14 AI Synchronisation

Each AI runner independently performs:

```
Reach Obstacle

↓

Reaction Delay

↓

Virtual Thinking

↓

Submit Answer

↓

Continue Running
```

AI timing uses the Mathematics Engine but never bypasses Race Engine rules.

---

# 6.15 Movement Events

The Race Engine emits movement events.

Examples:

```
RunnerStarted

RunnerStopped

RunnerAccelerated

RunnerSlowed

RunnerFinished

RunnerCelebrated
```

Presentation systems subscribe to these events.

---

# 6.16 Obstacle Events

Examples:

```
ObstacleReached

ProblemPresented

AnswerSubmitted

CorrectAnswer

IncorrectAnswer

ObstacleCleared
```

These events drive both gameplay and analytics.

---

# 6.17 Race Events

High-level events include:

```
RaceLoaded

CountdownStarted

RaceStarted

HalfwayReached

LeaderChanged

FinalSprint

RaceFinished
```

These events trigger:

- music transitions;
- camera effects;
- crowd reactions;
- UI updates.

---

# 6.18 Leader Detection

The engine continuously evaluates race positions.

Whenever leadership changes:

```
LeaderChanged
```

is emitted.

The UI may briefly highlight the new leader.

Leader changes should feel exciting but not distracting.

---

# 6.19 Final Sprint

During the last section of the race:

```
Remaining Distance

< 15%
```

The engine enters:

```
Final Sprint Mode
```

Possible effects:

- crowd volume increases;
- music intensifies;
- camera slightly zooms;
- runners animate more energetically.

Simulation remains unchanged.

Only presentation changes.

---

# 6.20 Finish Detection

A runner finishes when:

```
Position >= Track Length
```

Finish order is determined by crossing time.

Example:

```
Runner A

12.483 s

Runner B

12.591 s

Runner C

13.002 s
```

No ties are allowed.

---

# 6.21 Race Completion

The race ends only when:

```
All Participants

↓

Finished
```

Statistics are then finalised.

No runner is removed early.

---

# 6.22 Timekeeping

The Race Engine maintains:

- race start time;
- finish time;
- split times;
- obstacle times;
- response durations.

All timing uses a monotonic clock.

Wall-clock time must never influence gameplay.

---

# 6.23 Frame Independence

The simulation must be independent of rendering FPS.

Whether rendering occurs at:

30 FPS

60 FPS

120 FPS

or higher,

the race outcome remains identical.

---

# 6.24 Replay Support

Every race should be replayable.

The engine records:

- race configuration;
- random seed;
- player answers;
- timestamps;
- AI decisions.

Replaying these inputs must reproduce the same race.

---

# 6.25 Randomness

Random behaviour originates exclusively from seeded random generators.

Examples:

- AI personality variation;
- crowd animations;
- environmental effects.

This guarantees reproducibility.

---

# 6.26 Environmental Effects

Version 1.0 includes cosmetic environmental effects only.

Examples:

- birds flying;
- balloons;
- flags;
- cheering spectators;
- clouds.

These effects never influence gameplay.

---

# 6.27 Camera Events

The Race Engine emits camera hints.

Examples:

```
FocusLeader

ShowFinish

HighlightPlayer

ZoomSprint

CelebrateWinner
```

The camera system decides how to implement them.

---

# 6.28 Animation Events

Instead of controlling animations directly, the engine emits semantic events.

Examples:

```
Celebrate

Trip

Wave

Jump

Laugh

Sprint

Idle
```

The Animation Engine chooses the correct animation clip.

---

# 6.29 Performance Requirements

Simulation should support:

- five runners;
- eight obstacles;
- complete race evaluation;
- event generation;

using negligible CPU resources.

Target simulation cost:

**Less than 1 millisecond per frame** on a typical laptop.

---

# 6.30 Extensibility

Future race types should require no changes to the Mathematics Engine.

Potential future race modes:

- relay race;
- marathon;
- obstacle course;
- swimming;
- cycling;
- skiing;
- space racing.

The Race Engine should treat each as a different movement model while preserving the same event architecture.

---

# 6.31 Error Recovery

The engine must safely handle unexpected situations.

Examples:

- browser tab suspended;
- temporary frame drops;
- network interruption (future multiplayer);
- slow devices.

Simulation integrity must always be preserved.

---

# 6.32 Save and Resume

Future versions may support pausing a race.

The Race Engine must therefore be serialisable.

Saved state includes:

- runner positions;
- race clock;
- obstacle progress;
- player answers;
- random seed;
- active events.

Loading a saved race must resume seamlessly.

---

# 6.33 Testing Requirements

The Race Engine should be extensively unit tested.

Critical scenarios include:

- finish order calculation;
- obstacle timing;
- leader changes;
- simultaneous finishes;
- AI synchronization;
- deterministic replay;
- race completion.

Determinism is a non-negotiable requirement.

---

# 6.34 Design Principles

The Race Engine should always be:

- deterministic;
- event-driven;
- presentation-independent;
- performant;
- replayable;
- easy to test;
- easy to extend.

It must remain completely isolated from UI code.

---

# 6.35 Success Criteria

The Race Engine is considered successful if:

- every race feels smooth and responsive;
- race outcomes are deterministic;
- animations remain synchronised with gameplay;
- AI and player interactions appear natural;
- future race types can be added without redesigning the engine.

When new race modes can be implemented by adding movement behaviours rather than rewriting core logic, the Race Engine has achieved its architectural goals.

---

**End of Chapter 6**

The next chapter, **Chapter 7 – AI Opponents**, will define one of the most distinctive systems in Math Racers: believable AI personalities, adaptive opponent balancing, behavioural traits, decision models, emotional expression, and how AI runners become memorable rivals rather than predictable algorithms.

# Chapter 7. AI Opponents

---

# 7.1 Purpose

The AI Opponent System is responsible for creating believable competitors.

The objective is **not** to build the strongest possible artificial intelligence.

Instead, the goal is to create opponents that feel:

- alive;
- unique;
- fair;
- memorable;
- emotionally engaging.

Players should remember opponents by their personalities rather than by their statistics.

Children should eventually say:

> "Bongo always starts fast."

or

> "Luna usually catches up at the end."

instead of

> "The blue runner has a 78% win rate."

---

# 7.2 Design Philosophy

Every AI runner should behave like a child participating in a friendly sports event.

The AI should:

- occasionally make mistakes;
- sometimes surprise the player;
- celebrate victories;
- congratulate winners;
- never appear robotic.

The objective is entertainment, not perfect optimisation.

---

# 7.3 Core Principles

Every AI opponent must satisfy the following principles.

## Fair

The AI never cheats.

It receives:

- the same mathematical problems;
- the same race rules;
- the same obstacle spacing;
- the same movement mechanics.

---

## Predictable Personality

Although race outcomes vary, personalities remain consistent.

Example:

Frumo is always energetic.

Luna is always calm.

Bongo is always playful.

Consistency creates emotional attachment.

---

## Unpredictable Results

Even though personalities are stable, race outcomes should remain uncertain.

Every race should contain surprises.

---

# 7.4 AI Architecture

The AI system consists of four layers.

```
Personality

↓

Decision Model

↓

Math Solver

↓

Race Behaviour
```

Each layer has a separate responsibility.

---

# 7.5 Personality Layer

Personality defines *who* the runner is.

Example traits:

- confidence;
- patience;
- enthusiasm;
- competitiveness;
- optimism;
- focus;
- persistence;
- playfulness.

Personality changes very little over time.

---

# 7.6 Performance Layer

Performance represents racing ability.

Unlike personality, performance may evolve over future versions.

Examples:

- reaction speed;
- solving accuracy;
- consistency;
- recovery after mistakes.

---

# 7.7 Behaviour Layer

Behaviour translates personality into visible actions.

Example:

Confident runner:

- waves before the race;
- celebrates dramatically;
- never looks worried.

Nervous runner:

- looks around before the start;
- hesitates slightly;
- celebrates modestly.

The player should recognise personalities without reading descriptions.

---

# 7.8 AI Mathematical Solver

The AI never instantly knows the answer.

Instead, every problem follows this model:

```
Problem Appears

↓

Reaction Delay

↓

Thinking Time

↓

Answer Decision

↓

Continue Running
```

The player should perceive AI as solving problems naturally.

---

# 7.9 Reaction Time

Reaction time is independent of mathematical ability.

Example:

Runner A

Reaction

0.4 seconds

Thinking

2.3 seconds

Runner B

Reaction

1.1 seconds

Thinking

1.6 seconds

Both may finish at similar times while feeling completely different.

---

# 7.10 Accuracy

Each AI runner has an expected accuracy.

Example:

```
Frumo

92%

Luna

88%

Bongo

84%

Nori

95%

Pika

79%
```

Accuracy varies naturally from race to race.

---

# 7.11 Consistency

Consistency determines performance variation.

High consistency:

Fast almost every race.

Low consistency:

Brilliant one race.

Average the next.

Children often find inconsistent characters more entertaining.

---

# 7.12 Confidence

Confidence affects visible behaviour.

Examples:

High confidence:

- smiles often;
- celebrates early;
- waves to spectators.

Low confidence:

- fewer celebrations;
- cautious posture;
- surprised when winning.

Confidence does not directly increase speed.

---

# 7.13 Recovery

Recovery determines how quickly a runner regains momentum after mistakes.

Some runners:

trip,

laugh,

continue immediately.

Others:

pause,

look disappointed,

then continue.

Recovery affects personality more than competitiveness.

---

# 7.14 Risk Profile

Future versions may include optional tactical behaviour.

Examples:

Conservative:

Always aims for steady performance.

Balanced:

Occasional bursts.

Aggressive:

Attempts risky fast finishes.

Version 1.0 keeps tactics simple.

---

# 7.15 Favourite Operations

Some runners appear stronger in specific operations.

Example:

```
Frumo

Loves Multiplication

↓

Solves Multiplication Faster
```

```
Luna

Prefers Addition

↓

Performs Better During Addition
```

This creates subtle personality differences.

---

# 7.16 Emotional State

Each race maintains a temporary emotional state.

Examples:

Excited

Focused

Surprised

Determined

Celebrating

Disappointed

These states influence animations only.

---

# 7.17 Rivalries

Future versions may support friendly rivalries.

Example:

Frumo and Luna have raced together 54 times.

Whenever they compete:

- special dialogue;
- unique celebrations;
- additional spectator reactions.

Rivalries remain positive and sportsmanlike.

---

# 7.18 Friendships

Characters may also develop friendships.

Friends:

- cheer for each other;
- celebrate together;
- stand together during ceremonies.

Friendships never influence race fairness.

---

# 7.19 Adaptive Balance

The AI should keep races exciting.

If the player repeatedly dominates,

future races may become slightly more competitive.

If the player struggles,

AI performance may soften slightly.

These adjustments must remain subtle.

Players should never notice balancing.

---

# 7.20 Rubber Banding

Version 1.0 intentionally avoids traditional rubber banding.

AI never receives hidden speed boosts.

Instead, excitement comes from:

- mathematical performance;
- natural mistakes;
- personality variation.

Fairness is more important than drama.

---

# 7.21 Finish Behaviour

After finishing,

AI runners do not disappear.

Instead they:

- cheer;
- clap;
- wave;
- encourage remaining runners.

This reinforces the positive atmosphere.

---

# 7.22 Victory Behaviour

Winning characters celebrate according to personality.

Examples:

Energetic:

Huge jump.

Quiet:

Small smile.

Funny:

Accidental tumble during celebration.

Children should enjoy watching celebrations regardless of race outcome.

---

# 7.23 Defeat Behaviour

Losing should never feel negative.

Characters:

- smile;
- congratulate the winner;
- applaud;
- prepare for the next race.

Nobody cries.

Nobody becomes angry.

Nobody blames anyone.

---

# 7.24 AI Memory

Future versions may allow AI characters to remember previous races.

Examples:

"Last time you beat me!"

"I'm going to try harder today!"

"I almost won yesterday!"

These memories strengthen attachment.

---

# 7.25 Spectator Perception

Children should gradually form opinions such as:

- "Luna is reliable."
- "Bongo is hilarious."
- "Pika never gives up."
- "Frumo always starts too quickly."

These perceptions are more important than numerical ratings.

---

# 7.26 AI Configuration

Every runner stores:

```
Personality

Reaction Speed

Thinking Speed

Accuracy

Consistency

Favourite Operations

Animation Style

Celebration Style

Emotional Tendencies
```

These parameters generate behaviour.

---

# 7.27 Extensibility

Future AI improvements may include:

- learning from previous races;
- seasonal performance;
- preferred stadiums;
- dynamic friendships;
- voice reactions;
- tactical pacing;
- adaptive celebrations.

The architecture should support these additions without changing the Race Engine.

---

# 7.28 Testing Requirements

AI testing should verify:

- fairness;
- deterministic replay;
- expected accuracy;
- believable variation;
- balanced win rates;
- personality consistency.

Automated simulations should execute thousands of races to validate balance.

---

# 7.29 Design Principles

Every AI runner should be:

- fair;
- believable;
- expressive;
- memorable;
- child-friendly;
- emotionally positive;
- enjoyable to watch.

Winning should never be the AI's primary purpose.

Creating fun races is.

---

# 7.30 Success Criteria

The AI Opponent System is considered successful if:

- children remember opponents by name;
- races feel different every time;
- no AI appears unfair;
- personalities are recognisable;
- players become emotionally attached to both favourites and rivals.

When children begin discussing AI runners as if they were real teammates or classmates, the system has achieved its goal.

---

**End of Chapter 7**

The next chapter, **Chapter 8 – Game Modes**, will define every playable mode in the game, including Quick Race, Championship, Training, Duel, Endless Practice, custom races, future multiplayer modes, progression integration, and replay value.

# Chapter 8. Game Modes

---

# 8.1 Purpose

Game Modes determine **why** the player starts a race.

The Race Engine defines **how** races work.

The Mathematics Engine defines **what** problems are generated.

Game Modes define the player's objective and long-term motivation.

The same core gameplay should support multiple experiences without introducing new mechanics.

---

# 8.2 Design Philosophy

Every game mode should answer one question:

> "What does the player want to accomplish today?"

Sometimes the answer is:

> "I just want one quick race."

Other times:

> "I want to beat my favourite rival."

Or:

> "I want to improve multiplication."

Each motivation deserves its own game mode.

---

# 8.3 Version 1.0 Game Modes

The initial release includes four game modes:

- Quick Race
- Championship
- Training
- Duel

These modes share the same Race Engine but differ in progression and objectives.

---

# 8.4 Quick Race

## Purpose

Quick Race is the primary mode.

It is designed for short play sessions lasting approximately three to five minutes.

The player:

- selects participants;
- starts the race;
- receives results;
- returns to the main menu.

There is no long-term commitment.

---

## Player Journey

```
Main Menu

↓

Quick Race

↓

Choose Participants

↓

Race

↓

Results

↓

Play Again
```

This should become the most frequently played mode.

---

## Characteristics

- Fast setup
- Random opponents
- Standard track
- Standard difficulty
- Statistics recorded
- Achievements enabled

---

# 8.5 Championship

## Purpose

Championship introduces long-term progression.

Instead of competing in one race, players participate in an entire season.

Each race awards championship points.

---

## Season Structure

Example:

```
Spring Championship

Race 1

↓

Race 2

↓

Race 3

↓

Race 4

↓

Final

↓

Champion
```

Future versions may support custom season lengths.

---

## Scoring

Example scoring system:

| Position | Points |
|----------|--------:|
| 1st | 10 |
| 2nd | 8 |
| 3rd | 6 |
| 4th | 4 |
| 5th | 2 |

The exact values may change during balancing.

---

## Championship Results

After each race the player sees:

- current standings;
- championship leader;
- points gained;
- races remaining.

This creates anticipation between races.

---

# 8.6 Training Mode

## Purpose

Training removes competitive pressure.

The player practices mathematics without worrying about race results.

The focus shifts entirely to learning.

---

## Characteristics

- No AI opponents
- Unlimited problems
- Adjustable operation
- Adjustable difficulty
- Immediate feedback
- Progress tracking

---

## Gameplay

Instead of racing:

```
Problem

↓

Answer

↓

Celebrate

↓

Next Problem
```

A small character animation still rewards correct answers.

The experience remains playful.

---

# 8.7 Duel Mode

## Purpose

Duel creates a personal rivalry.

The player competes against one selected opponent.

---

## Characteristics

- One player
- One AI
- Faster races
- High emotional engagement

Children often become attached to recurring rivals.

---

## Duel Flow

```
Choose Rival

↓

Race

↓

Winner

↓

Rematch?
```

The rematch button should be prominent.

---

# 8.8 Endless Practice (Future)

Purpose:

Continuous learning.

The race never finishes.

Instead:

```
Run

↓

Problem

↓

Run

↓

Problem

↓

Run
```

The player stops whenever they choose.

Useful for homework sessions.

---

# 8.9 Daily Challenge (Future)

One unique race every day.

Characteristics:

- fixed problems;
- same opponents;
- identical conditions for everyone.

Statistics compare today's performance only against the player's previous attempts.

No global leaderboards are displayed.

---

# 8.10 Weekly Tournament (Future)

A longer event consisting of multiple championships.

Rewards include:

- trophies;
- badges;
- cosmetic unlocks.

Gameplay remains identical.

Only progression changes.

---

# 8.11 Family Race (Future)

Multiple family members take turns solving problems.

Example:

Parent

↓

Child

↓

Sibling

↓

Parent

Everyone contributes to one runner.

Designed for cooperative play.

---

# 8.12 Split-Screen Mode (Future)

Two children play simultaneously on the same device.

Each controls a separate runner.

Mathematical problems appear independently.

The Race Engine already supports multiple participants.

Only the input system changes.

---

# 8.13 Classroom Mode (Future)

Designed for teachers.

Features:

- predefined participant lists;
- shared championships;
- progress reports;
- controlled difficulty.

No gameplay modifications required.

---

# 8.14 Sandbox Mode (Future)

Allows experimentation.

Players customise:

- number of runners;
- track length;
- obstacle count;
- operations;
- difficulty.

Ideal for demonstrations and testing.

---

# 8.15 Spectator Mode (Future)

The player watches AI runners compete.

Useful for:

- observing personalities;
- enjoying animations;
- introducing new characters.

No mathematical interaction.

Pure entertainment.

---

# 8.16 Story Mode (Future)

Characters participate in a narrative adventure.

Each chapter introduces:

- new opponents;
- themed races;
- educational milestones.

Mathematics remains the core mechanic.

---

# 8.17 Challenge Mode (Future)

Special rules modify races.

Examples:

- multiplication only;
- no mistakes allowed;
- sprint race;
- marathon;
- surprise obstacles.

These challenges extend replayability.

---

# 8.18 Seasonal Events (Future)

Special visual themes.

Examples:

Spring

Summer

Halloween

Winter

Christmas

Only cosmetics change.

Core gameplay remains identical.

---

# 8.19 Accessibility Across Modes

Every mode must support:

- mouse;
- keyboard;
- touch;
- tablets;
- low reading ability.

No mode should require advanced computer skills.

---

# 8.20 Shared Systems

Regardless of game mode:

The following systems always remain active:

- Mathematics Engine
- Avatar System
- Statistics
- Achievements
- Accessibility
- Save System

Consistency reduces learning effort.

---

# 8.21 Mode Selection

The game should never overwhelm the player.

Initially, only:

- Quick Race
- Training

may be prominently displayed.

Additional modes can gradually unlock.

This follows the principle of progressive disclosure.

---

# 8.22 Replayability

Different modes create different reasons to return.

| Mode | Motivation |
|------|------------|
| Quick Race | One more race |
| Championship | Win the season |
| Training | Improve maths |
| Duel | Beat a rival |
| Endless | Relaxed practice |
| Story | Discover new adventures |

No mode replaces another.

They complement each other.

---

# 8.23 Future Expansion

The architecture should support new game modes without modifying:

- Mathematics Engine;
- Race Engine;
- Avatar System.

Each new mode should primarily orchestrate existing systems.

This keeps development scalable.

---

# 8.24 Design Principles

Every game mode should:

- have a clear purpose;
- require minimal explanation;
- encourage replay;
- support learning;
- remain emotionally positive;
- integrate naturally with progression.

Complexity should emerge from variety rather than complicated rules.

---

# 8.25 Success Criteria

The Game Modes system is considered successful if:

- players naturally switch between modes based on mood;
- Quick Race remains the default experience;
- Championship encourages long-term engagement;
- Training improves mathematical confidence;
- Duel creates memorable rivalries;
- future modes can be implemented with minimal engineering effort.

When children choose a game mode based on what they feel like doing today rather than what the game requires, the Game Modes system has achieved its goal.

---

**End of Chapter 8**

The next chapter, **Chapter 9 – User Interface & User Experience (UI/UX)**, will define every screen in the application, navigation flows, interaction patterns, layout system, responsive behaviour, animation principles, accessibility guidelines, and visual hierarchy. This chapter will serve as the foundation for the Art Bible and all UI generation prompts.

# Chapter 9. User Interface & User Experience (UI/UX)

---

# 9.1 Purpose

The User Interface is responsible for making the game effortless to use.

Children should never wonder:

- "Where do I click?"
- "What does this button do?"
- "What should I do next?"

Every screen should make the next action obvious.

The interface exists to support play, not to demonstrate technical sophistication.

---

# 9.2 UX Philosophy

The UI follows five principles.

## Large

Everything is designed for small hands.

Buttons are intentionally oversized.

---

## Colourful

Colour communicates meaning.

Text is secondary.

---

## Animated

Nothing feels static.

Every interaction provides feedback.

---

## Simple

Each screen has one primary action.

---

## Friendly

The interface behaves like a cheerful companion.

Never like business software.

---

# 9.3 Visual Style

The overall aesthetic is inspired by modern animated films.

Keywords:

- playful
- soft
- rounded
- colourful
- expressive
- optimistic
- premium
- clean

Reference inspirations (style only):

- Pixar
- Disney
- Mario Kart
- Fall Guys
- Animal Crossing

The game should **not** imitate any existing IP.

---

# 9.4 Design Language

Every UI element follows the same language.

Characteristics:

- rounded corners
- thick outlines
- soft shadows
- gentle gradients
- subtle highlights
- smooth animations

Avoid:

- sharp edges
- flat grey buttons
- tiny icons
- corporate styling

---

# 9.5 Colour Palette

The primary palette should evoke happiness.

### Primary

Sky Blue

Used for:

- primary buttons
- progress
- navigation

---

### Secondary

Sunny Yellow

Used for:

- rewards
- stars
- achievements

---

### Accent

Grass Green

Used for:

- success
- confirmation
- correct answers

---

### Warning

Orange

Used for:

- attention
- countdown
- important actions

---

### Neutral

Warm Cream

Used for:

- backgrounds
- cards
- menus

---

### Error

Soft Coral

Used sparingly.

Never aggressive red.

---

# 9.6 Typography

Typography must prioritise readability.

Characteristics:

- rounded
- large
- generous spacing
- minimal decoration

Recommended style:

Friendly geometric sans-serif.

Examples:

- Nunito
- Baloo 2
- Fredoka
- Quicksand

Font selection is documented in the Art Bible.

---

# 9.7 Iconography

Icons should communicate without text.

Preferred style:

- rounded
- filled
- colourful
- simple silhouettes

Examples:

🏃

⭐

🏆

🎉

❤️

➕

➖

✖️

➗

Avoid detailed line icons.

---

# 9.8 Animation Philosophy

Every interaction deserves feedback.

Examples:

Button:

Press

↓

Compress

↓

Bounce

↓

Release

Card:

Hover

↓

Lift

↓

Shadow grows

Correct answer:

Glow

↓

Sparkles

↓

Fade

Animations should feel responsive but never distracting.

---

# 9.9 Screen Flow

```
Splash

↓

Home

↓

Avatar Selection

↓

Race Setup

↓

Race

↓

Results

↓

Home
```

Navigation depth should remain shallow.

---

# 9.10 Splash Screen

Purpose:

Immediate excitement.

Contains:

- game logo
- animated runners
- moving clouds
- cheering crowd

Display time:

2–3 seconds.

---

# 9.11 Home Screen

The Home Screen is the heart of the application.

Contains:

- favourite avatar
- large Play button
- avatar gallery
- achievements
- statistics
- settings

The Play button dominates the layout.

---

# 9.12 Home Layout

```
+------------------------------------+

Favourite Avatar

--------------------------------------

▶ PLAY

--------------------------------------

Avatars

Achievements

Statistics

Settings

+------------------------------------+
```

The player's favourite avatar should always feel like the star of the screen.

---

# 9.13 Avatar Gallery

Displays all saved characters.

Layout:

```
□ □ □ □

□ □ □ □

□ □ □ □
```

Each card displays:

- portrait
- name
- favourite icon
- win count

Selecting a card opens the avatar profile.

---

# 9.14 Avatar Creation Screen

The creation experience should feel magical.

Flow:

Choose:

- species
- hairstyle
- colours
- accessories

↓

Generate

↓

Loading animation

↓

Reveal character

The reveal should be exciting.

---

# 9.15 Generation Animation

Instead of a progress bar:

Show:

- magical particles
- swirling colours
- spinning stars
- sketch transforming into artwork

Children should feel that something creative is happening.

---

# 9.16 Race Setup Screen

Contains:

Participants

↓

Track Preview

↓

Difficulty

↓

Start Race

Large illustrated cards represent each participant.

---

# 9.17 Race Screen

This is the most important screen.

Layout:

```
Crowd

----------------------------

Runner Lanes

Runner Lanes

Runner Lanes

----------------------------

Math Panel

----------------------------

Answer Input
```

The player's focus naturally alternates between:

track

↓

problem

↓

track

---

# 9.18 Stadium View

The stadium should always feel alive.

Background elements:

- waving flags
- balloons
- animated spectators
- birds
- clouds
- scoreboards

These elements never distract from gameplay.

---

# 9.19 Mathematics Panel

The problem appears centrally.

Example:

```
47 + 16 = ?
```

Requirements:

- huge text
- maximum contrast
- no clutter
- immediate readability

Nothing else competes for attention.

---

# 9.20 Answer Input

Desktop:

Physical keyboard preferred.

Touch devices:

Large on-screen keypad.

Buttons:

```
7 8 9

4 5 6

1 2 3

0

✓
```

Keys should be large enough for children.

---

# 9.21 HUD

Minimal information is shown during races.

Visible:

- runner positions
- current obstacle
- finish progress
- favourite avatar

Hidden:

- complex statistics
- menus
- unnecessary controls

Gameplay remains clean.

---

# 9.22 Results Screen

The race concludes with celebration.

Layout:

```
Winner

↓

Podium

↓

Medals

↓

Statistics

↓

Play Again
```

The first thing players see is celebration.

Statistics come afterwards.

---

# 9.23 Podium Ceremony

Top three runners stand on a podium.

Animations:

- cheering
- waving
- jumping
- confetti
- fireworks

Even runners finishing fourth and fifth celebrate nearby.

Nobody looks unhappy.

---

# 9.24 Statistics Screen

Statistics use illustrated cards.

Examples:

⭐ Fastest Answer

🏆 Best Streak

📈 Accuracy

❤️ Favourite Operation

Graphs are simple.

Children should understand them visually.

---

# 9.25 Parent Dashboard

Accessible from Settings.

Contains:

- educational progress
- weekly activity
- operation breakdown
- response time trends
- session history

This screen may contain more detailed information than the child-facing UI.

---

# 9.26 Navigation

Navigation should require very few decisions.

Maximum hierarchy:

```
Home

↓

Feature

↓

Details
```

Avoid deeply nested menus.

---

# 9.27 Buttons

Buttons follow one consistent style.

Characteristics:

- rounded
- thick
- colourful
- animated
- icon-first

Primary buttons use brighter colours.

Secondary buttons are visually quieter.

---

# 9.28 Cards

Cards display:

- avatars
- achievements
- statistics
- championships

Cards should appear tactile.

Hover effect:

Lift

↓

Shadow

↓

Tiny scale increase

---

# 9.29 Dialogues

Dialogs should remain friendly.

Example:

Delete Avatar?

🙂

Cancel

Delete

Dangerous actions require confirmation.

---

# 9.30 Empty States

Every empty screen should encourage action.

Example:

"No avatars yet."

↓

Large smiling mascot.

↓

Create Your First Runner!

Empty states should never feel unfinished.

---

# 9.31 Accessibility

Support:

- colour-blind friendly palette;
- high contrast mode;
- keyboard navigation;
- touch input;
- screen scaling;
- reduced motion option.

Accessibility is built in from day one.

---

# 9.32 Responsive Design

Supported devices:

- desktop
- laptop
- tablet

Mobile phones are not a primary target for Version 1.0 but layouts should degrade gracefully.

The interface uses a responsive card-based grid system.

---

# 9.33 Feedback System

Every interaction produces feedback.

Examples:

Hover

↓

Lift

Click

↓

Bounce

Correct

↓

Glow

Incorrect

↓

Gentle shake

Feedback should always feel encouraging.

---

# 9.34 Loading Screens

Loading should never feel boring.

Ideas:

- runners warming up;
- stretching animations;
- funny trivia;
- encouraging quotes;
- animated mascots.

Avoid static spinners.

---

# 9.35 Error States

Errors should be human.

Instead of:

"Unexpected Error"

Display:

"Oh no! Our runners dropped the baton."

+

Retry

Technical details remain hidden from children.

---

# 9.36 Sound UX

Every important interaction has a sound.

Examples:

Button

Soft pop

Correct answer

Sparkle chime

Victory

Applause

Card reveal

Magic shimmer

Audio should reinforce emotion without becoming repetitive.

---

# 9.37 Microinteractions

Small details create delight.

Examples:

- avatars blink occasionally;
- buttons wiggle slightly on hover;
- balloons drift in the background;
- medals shimmer;
- stars twinkle;
- confetti pieces continue falling briefly after celebrations.

These touches make the world feel alive.

---

# 9.38 Visual Hierarchy

Every screen should answer three questions within one second:

1. What is this screen?
2. What is the most important action?
3. Where should I click?

If the answer is unclear, the layout must be simplified.

---

# 9.39 UI Component Library

The project should use a reusable design system.

Core components:

- Button
- IconButton
- Card
- AvatarCard
- Modal
- Dialog
- ProgressBar
- RaceHUD
- MathPanel
- NumericKeypad
- Badge
- Medal
- Toast
- Tooltip
- CelebrationOverlay

Every component follows the same visual language.

---

# 9.40 Success Criteria

The UI/UX is considered successful if:

- children can play without adult assistance;
- first-time players understand the interface intuitively;
- every screen has one obvious primary action;
- navigation remains effortless;
- the interface consistently reinforces joy, confidence, and curiosity.

If usability testing shows that an eight-year-old can complete a full race—from launching the game to viewing results—without needing verbal instructions, then the UI/UX has achieved its primary objective.

---

**End of Chapter 9**

The next chapter, **Chapter 10 – Progression, Achievements & Statistics**, will define long-term player motivation, avatar history, achievements, personal records, analytics, progression systems, and how improvement is communicated to both children and parents.

# Chapter 10. Progression, Achievements & Statistics

---

# 10.1 Purpose

Progression gives players a reason to return tomorrow.

Unlike many games, Math Racers does **not** rely on:

- addictive reward loops;
- daily login streaks;
- premium currencies;
- fear of missing out.

Instead, progression is built around one simple idea:

> **The player should feel that both they and their favourite runners are becoming better over time.**

The progression system celebrates improvement rather than grinding.

---

# 10.2 Design Philosophy

Progress should answer three different questions.

For the child:

> "I'm getting faster!"

For the avatar:

> "Frumo has become a legendary racer."

For the parent:

> "My child has noticeably improved their arithmetic."

Each audience experiences progression differently.

---

# 10.3 Progression Pillars

Progression consists of four independent systems.

```
Player Progress

↓

Avatar History

↓

Achievements

↓

Statistics
```

Each system motivates a different type of player.

---

# 10.4 Player Progress

Player progress represents the child's mathematical development.

Unlike avatar statistics, this belongs to the player account.

Examples:

- total races;
- total problems solved;
- average response time;
- favourite operation;
- strongest operation;
- weakest operation;
- longest playing streak (sessions, not days);
- total learning time.

This information remains private.

---

# 10.5 Avatar History

Each avatar develops its own story.

Example:

```
Name

Frumo

Created

12 March 2027

Races

248

Victories

71

Favourite Since

18 March 2027

Best Championship Finish

1st
```

History makes every character feel alive.

---

# 10.6 Personal Records

The game celebrates personal improvement.

Examples:

- fastest correct answer;
- highest accuracy in one race;
- longest winning streak;
- fastest championship victory;
- quickest multiplication answer;
- most races completed in one session.

Breaking a personal record should trigger a special celebration.

---

# 10.7 Achievement Philosophy

Achievements exist to encourage exploration.

They should never pressure children.

Good achievement:

> Solve 50 multiplication problems.

Bad achievement:

> Play every day for 30 days.

The game rewards learning—not obligation.

---

# 10.8 Achievement Categories

Achievements are grouped into categories.

- Racing
- Mathematics
- Collection
- Exploration
- Persistence
- Improvement
- Championships
- Fun

Each category uses a unique visual badge.

---

# 10.9 Racing Achievements

Examples:

🏃 First Finish

🏆 First Victory

🚀 Five Wins

🥇 Twenty Wins

⭐ Hundred Races

🏟 Marathon Runner

These achievements celebrate participation as much as success.

---

# 10.10 Mathematics Achievements

Examples:

➕

Addition Expert

➖

Subtraction Star

✖️

Multiplication Master

➗

Division Hero

🎯

100 Correct Answers

⚡

Fast Thinker

These achievements reinforce learning goals.

---

# 10.11 Collection Achievements

Examples:

Create:

- 5 avatars;
- 10 avatars;
- 25 avatars;
- 50 avatars.

Choose a favourite.

Rename an avatar.

Read every biography.

Collection achievements encourage creativity.

---

# 10.12 Exploration Achievements

Examples:

Play:

- Championship;
- Duel;
- Training.

Try every operation.

Use every stadium (future).

Exploration broadens player experience.

---

# 10.13 Improvement Achievements

Rather than rewarding absolute performance, reward improvement.

Examples:

Improve average response time by:

10%

20%

30%

Increase multiplication accuracy by:

15%

These achievements celebrate growth.

---

# 10.14 Fun Achievements

Some achievements exist purely to create smiles.

Examples:

Trip over five hurdles.

Watch confetti for ten seconds.

Create a character with a giant moustache.

Race five foxes.

Win with the slowest runner.

These become memorable stories.

---

# 10.15 Hidden Achievements

Some achievements remain hidden until unlocked.

Examples:

Meet every animal species.

Finish a race with no mistakes.

Create twins.

Win after trailing at the final obstacle.

Hidden achievements encourage discovery.

---

# 10.16 Achievement Presentation

Unlocking an achievement triggers:

```
Pause

↓

Sparkles

↓

Badge Appears

↓

Character Celebration

↓

Continue
```

The interruption should last no longer than two seconds.

---

# 10.17 Badge Design

Every achievement is represented by a badge.

Characteristics:

- circular;
- colourful;
- collectible;
- instantly recognisable.

The badge collection should resemble a sticker album.

---

# 10.18 Player Profile

The player profile summarises long-term progress.

Contains:

- avatar count;
- races completed;
- favourite avatar;
- total victories;
- total learning time;
- unlocked achievements;
- personal bests.

The profile grows naturally over months.

---

# 10.19 Statistics Philosophy

Statistics should answer questions rather than overwhelm.

Example:

Instead of:

```
Average Response

3.28 seconds
```

Display:

```
⚡

You're 18% faster than last month!
```

Meaning is more valuable than numbers.

---

# 10.20 Child Statistics

Children see:

- colourful charts;
- medals;
- stars;
- progress bars;
- happy mascots.

Complex analytics remain hidden.

---

# 10.21 Parent Statistics

Parents receive richer information.

Examples:

Weekly summary:

```
Problems Solved

248

Accuracy

91%

Average Time

2.9 seconds

Strongest Skill

Addition

Needs Practice

Division
```

Visual clarity remains important.

---

# 10.22 Skill Progress

Each mathematical operation maintains independent progression.

Example:

```
Addition

█████████░

Level 9

Multiplication

██████░░░░

Level 6
```

These "levels" are descriptive, not competitive.

They represent confidence rather than game power.

---

# 10.23 Session Summary

Every race contributes to a session summary.

Example:

Today's Session

- 4 races
- 39 problems
- 92% accuracy
- 2 personal records
- 1 achievement

This gives each session a satisfying conclusion.

---

# 10.24 Improvement Timeline

The game stores historical data.

Players and parents can observe:

- weekly trends;
- monthly trends;
- yearly trends.

Seeing long-term improvement is highly motivating.

---

# 10.25 Favourite Avatar Timeline

Every favourite change is recorded.

Example:

```
March

Frumo

↓

April

Luna

↓

June

Frumo
```

This creates nostalgic memories.

---

# 10.26 Championship History

Completed championships remain permanently visible.

Example:

```
Spring Cup

🥇

Summer Cup

🥈

Autumn Cup

🥉
```

Children enjoy looking back at previous seasons.

---

# 10.27 Milestones

Major milestones receive larger celebrations.

Examples:

- first race;
- first victory;
- 100 problems solved;
- 500 problems solved;
- 1,000 problems solved;
- first championship.

Milestones feel like important life events.

---

# 10.28 Encouragement System

If a player struggles, the game highlights progress rather than shortcomings.

Instead of:

"You answered 6 incorrectly."

Display:

"You solved 18 correctly!"

This framing builds confidence.

---

# 10.29 Data Persistence

All progression data is stored permanently.

Versioned records allow future schema evolution.

Important data includes:

- achievements;
- statistics;
- histories;
- timelines;
- personal bests.

No progress should be lost during updates.

---

# 10.30 Privacy

Progress data belongs to the player.

Parents may:

- review;
- export;
- delete.

No educational analytics are shared publicly.

There are no global rankings in Version 1.0.

---

# 10.31 Extensibility

Future progression features may include:

- seasonal journals;
- memory books;
- avatar scrapbooks;
- printable certificates;
- classroom reports;
- learning goals;
- coach recommendations.

The current architecture should accommodate these additions.

---

# 10.32 Design Principles

Every progression feature should:

- celebrate improvement;
- reinforce confidence;
- remain understandable;
- avoid unhealthy competition;
- support long-term engagement;
- make children proud of their effort.

The emphasis is always on **growth**, never on comparison.

---

# 10.33 Success Criteria

The Progression System is considered successful if:

- children enjoy reviewing their achievements;
- favourite avatars develop meaningful histories;
- parents can clearly observe educational progress;
- personal records motivate replay without creating pressure;
- players feel proud of improvement regardless of race position.

When a child says:

> "I'm much faster than I was last month!"

instead of:

> "I need more points."

the Progression System has fulfilled its educational purpose.

---

**End of Chapter 10**

The next chapter, **Chapter 11 – Audio Design**, will define the complete audio experience: adaptive music, character voices, UI sounds, crowd ambience, accessibility considerations, emotional sound design, and the audio event architecture that supports every interaction in the game.

# Chapter 11. Audio Design

---

# 11.1 Purpose

Audio is responsible for transforming Math Racers from a functional educational game into an emotionally engaging experience.

A race without sound feels mechanical.

A race with thoughtful sound design feels alive.

Audio should reinforce:

- excitement;
- success;
- anticipation;
- personality;
- celebration.

It should never become noisy or overwhelming.

---

# 11.2 Audio Philosophy

The game follows one central audio principle:

> **Every sound should make the player smile.**

Audio should encourage rather than punish.

Correct answers sound exciting.

Mistakes sound amusing.

Silence is used intentionally to create anticipation.

---

# 11.3 Audio Layers

The complete audio experience consists of six independent layers.

```
Music

↓

Ambience

↓

Character Voices

↓

Gameplay Effects

↓

UI Sounds

↓

Celebration Effects
```

Each layer can be independently enabled, disabled or adjusted.

---

# 11.4 Adaptive Music

Music should evolve throughout a race.

Instead of changing tracks abruptly, the soundtrack adapts dynamically.

Typical progression:

```
Main Menu

↓

Relaxed Theme

↓

Countdown

↓

Excitement Builds

↓

Race

↓

Energetic Theme

↓

Final Sprint

↓

High Energy

↓

Victory

↓

Celebration Theme
```

Transitions should always feel smooth.

---

# 11.5 Music Style

The soundtrack should be:

- uplifting;
- playful;
- orchestral;
- lightly electronic;
- melodic;
- memorable.

Inspirations:

- animated feature films;
- modern family games;
- sports festivals.

Avoid:

- aggressive rock;
- heavy electronic music;
- dramatic orchestral tension;
- repetitive loops.

---

# 11.6 Main Menu Music

The menu theme introduces the world.

Characteristics:

- warm;
- welcoming;
- optimistic;
- relaxing.

Children should enjoy spending time in menus.

---

# 11.7 Countdown Music

During the countdown:

```
3

2

1

GO!
```

Music gradually increases energy.

The "GO!" moment receives a strong musical accent.

---

# 11.8 Race Music

The race theme should maintain momentum without distracting from mathematical thinking.

Characteristics:

- medium tempo;
- rhythmic;
- optimistic;
- highly repeatable.

Children should remain focused on arithmetic.

---

# 11.9 Final Sprint

As the finish approaches:

Music subtly evolves.

Possible additions:

- stronger percussion;
- brighter brass;
- higher strings;
- increased rhythm.

Tempo itself should remain stable.

---

# 11.10 Victory Music

Crossing the finish line immediately triggers a celebratory musical phrase.

Characteristics:

- triumphant;
- joyful;
- short;
- recognisable.

The complete celebration should last only a few seconds before transitioning to calmer music.

---

# 11.11 Crowd Ambience

The stadium constantly feels alive.

Ambient sounds include:

- distant cheering;
- applause;
- whistles;
- conversations;
- flags moving;
- occasional laughter.

Crowd volume changes naturally throughout the race.

---

# 11.12 Dynamic Crowd

Crowd reactions depend on race events.

Examples:

Leader changes:

Crowd cheers louder.

Correct answer:

Supportive applause.

Final sprint:

Excitement increases.

Finish:

Large applause.

This creates emotional feedback without using text.

---

# 11.13 Character Voices

Characters communicate using short expressive sounds rather than spoken dialogue.

Examples:

Happy:

"Yay!"

Thinking:

"Hmm..."

Celebrating:

"Woohoo!"

Surprised:

"Oh!"

These vocalisations should be language-independent.

---

# 11.14 Voice Personality

Every avatar has a distinct voice profile.

Examples:

Small fox:

High pitch.

Bear:

Deep and warm.

Rabbit:

Quick energetic sounds.

Panda:

Calm cheerful tone.

The voice reinforces personality.

---

# 11.15 Mathematics Feedback

Correct answer:

- sparkle;
- pleasant chime;
- tiny burst effect.

Incorrect answer:

- soft bounce;
- funny stumble sound;
- gentle "oops".

Never use harsh buzzers.

---

# 11.16 Running Sounds

Every runner produces:

- footsteps;
- breathing;
- clothing movement.

Footsteps adapt to:

- sprint;
- jogging;
- stopping;
- celebration.

These sounds remain subtle.

---

# 11.17 Obstacle Sounds

Each obstacle interaction has corresponding audio.

Correct:

Jump

↓

Whoosh

↓

Landing

Incorrect:

Hit

↓

Boing

↓

Dust

↓

Laughter

Humour is preferred over realism.

---

# 11.18 Celebration Effects

Special achievements trigger:

- magical sparkles;
- applause;
- fanfare;
- confetti sounds.

Major achievements receive richer soundscapes.

---

# 11.19 UI Sounds

Every interface interaction receives audio feedback.

Examples:

Button hover:

Tiny pop.

Button click:

Soft click.

Card selection:

Paper flip.

Window opening:

Gentle swoosh.

Closing:

Soft fade.

UI sounds should feel tactile.

---

# 11.20 Avatar Gallery

Browsing avatars should feel playful.

Examples:

Selecting an avatar:

Friendly greeting.

Changing favourite:

Small heart sound.

Opening profile:

Magic shimmer.

---

# 11.21 Results Screen

Results combine multiple audio layers.

Sequence:

```
Finish

↓

Applause

↓

Victory Music

↓

Medal Sound

↓

Celebration

↓

Soft Background Music
```

The emotional peak occurs immediately after the finish.

---

# 11.22 Achievement Audio

Unlocking achievements should feel special.

Sequence:

Sparkle

↓

Ascending notes

↓

Badge appears

↓

Short fanfare

The sound should remain under two seconds.

---

# 11.23 Audio Priorities

Not all sounds are equally important.

Priority order:

1. Mathematics feedback
2. Countdown
3. Character reactions
4. Victory
5. UI
6. Ambient sounds

Lower-priority sounds may be reduced automatically if many sounds occur simultaneously.

---

# 11.24 Mixing

The audio engine should automatically balance all sound layers.

Example:

During important moments:

- crowd becomes quieter;
- UI sounds reduce slightly;
- music ducks briefly;
- celebration effects remain clear.

Players should never struggle to hear important feedback.

---

# 11.25 Accessibility

Audio must never be required for gameplay.

Every sound cue should also have:

- visual animation;
- colour change;
- movement.

Children with hearing impairments should receive the same information.

---

# 11.26 Audio Settings

Players (or parents) may adjust:

- master volume;
- music volume;
- sound effects;
- ambience;
- character voices.

Settings are saved automatically.

---

# 11.27 Localisation

The game should avoid spoken language whenever possible.

Reasons:

- easier localisation;
- broader accessibility;
- lower production cost;
- stronger visual storytelling.

Only optional narration may require translation.

---

# 11.28 Performance

Audio playback must begin with minimal latency.

Target:

Less than **50 milliseconds** from event to playback.

All commonly used sounds should be preloaded before a race begins.

---

# 11.29 Future Expansion

Future releases may include:

- dynamic orchestral soundtrack;
- adaptive themes for different stadiums;
- seasonal music;
- AI-generated crowd commentary;
- personalised avatar voices;
- accessibility narration;
- educational voice coaching.

The audio architecture should remain modular.

---

# 11.30 Design Principles

Every sound should be:

- friendly;
- memorable;
- emotionally positive;
- short;
- expressive;
- child-safe;
- supportive rather than distracting.

Silence is also an important design tool.

Not every interaction requires sound.

---

# 11.31 Success Criteria

The Audio Design is considered successful if:

- children immediately recognise the game by its sounds;
- correct answers feel satisfying without becoming repetitive;
- music enhances excitement without reducing concentration;
- parents do not perceive the audio as annoying during extended sessions;
- every sound reinforces joy, confidence and curiosity.

When children begin humming the menu music or imitating their favourite avatar's celebration sounds, the Audio Design has achieved its purpose.

---

**End of Chapter 11**

The next chapter, **Chapter 12 – Technical Requirements & Non-Functional Requirements**, will define the engineering standards for the project, including architecture constraints, performance targets, browser compatibility, scalability, offline capabilities, testing strategy, security, observability, and maintainability. This chapter will become the foundation for the Architecture Decision Records (ADRs) and the Claude Code implementation prompts.

# Chapter 12. Technical Requirements & Non-Functional Requirements

---

# 12.1 Purpose

This chapter defines the engineering quality standards for **Math Racers**.

Unlike previous chapters, which describe gameplay and player experience, this chapter specifies **how the software must be built**.

These requirements apply regardless of the implementation language or framework.

They exist to ensure that the game remains:

- maintainable;
- scalable;
- testable;
- secure;
- performant;
- extensible.

Every technical decision should be evaluated against these principles.

---

# 12.2 Engineering Philosophy

The project follows one simple engineering principle:

> **Simple systems are easier to extend than clever systems.**

Avoid unnecessary abstraction.

Prefer readability over brevity.

Prefer explicitness over magic.

Every engineer joining the project should understand the architecture within a few days.

---

# 12.3 Architecture Principles

The architecture follows the principles of **Clean Architecture** and **Domain-Driven Design (DDD)**.

The codebase is organised into independent domains.

Core domains include:

- Race Engine
- Mathematics Engine
- Avatar System
- Statistics
- Progression
- Authentication
- Asset Management

Each domain owns its business logic.

Cross-domain communication occurs through explicit interfaces and events.

---

# 12.4 Layered Architecture

The application is divided into layers.

```
Presentation

↓

Application

↓

Domain

↓

Infrastructure
```

Dependencies always point inward.

The Domain layer must remain independent of frameworks.

---

# 12.5 Frontend Requirements

The frontend should:

- render smoothly;
- minimise loading time;
- support responsive layouts;
- work entirely in modern browsers;
- communicate through a documented API.

The UI should never contain business logic.

Business rules belong to the Application and Domain layers.

---

# 12.6 Backend Requirements

The backend is responsible for:

- authentication;
- avatar generation;
- persistence;
- statistics;
- AI prompt orchestration;
- image generation workflow;
- administration.

The backend should expose a versioned REST API.

Future GraphQL support may be added without replacing REST.

---

# 12.7 Browser Support

Version 1.0 officially supports:

- Chrome
- Edge
- Firefox
- Safari

Only current stable versions are supported.

No legacy browser compatibility is required.

---

# 12.8 Device Support

Primary targets:

- Desktop
- Laptop
- Tablet

Secondary support:

- Large-screen mobile devices

Very small phones are outside the primary scope of Version 1.0.

---

# 12.9 Performance Targets

Application startup:

< 3 seconds

Race loading:

< 2 seconds

Avatar gallery:

< 500 milliseconds

Problem generation:

< 1 millisecond

Answer validation:

Instantaneous from the player's perspective.

The game should always feel responsive.

---

# 12.10 Rendering Performance

Target frame rate:

```
60 FPS
```

Minimum acceptable:

```
30 FPS
```

Animation quality should degrade gracefully on slower hardware.

Gameplay timing must remain unaffected.

---

# 12.11 Asset Optimisation

Images should be:

- compressed;
- cached;
- versioned;
- lazy-loaded where appropriate.

Large assets should never block gameplay.

Avatar thumbnails should be generated automatically.

---

# 12.12 Network Requirements

Gameplay should minimise network dependency.

Examples:

Mathematical validation:

Local.

Race simulation:

Local.

Statistics synchronisation:

Background.

Only avatar generation and cloud persistence require server communication.

---

# 12.13 Offline Behaviour

Version 1.0 should support limited offline functionality.

Available offline:

- Training Mode
- Previously generated avatars
- Existing statistics
- Local races

Unavailable offline:

- New avatar generation
- Cloud synchronisation
- Account management

Offline behaviour should fail gracefully.

---

# 12.14 Save Strategy

Important data should be persisted immediately.

Examples:

- completed race;
- new achievement;
- updated statistics;
- avatar creation.

The player should never lose meaningful progress.

---

# 12.15 Database Principles

The persistence layer should satisfy:

- ACID guarantees where appropriate;
- schema migrations;
- version history;
- backup support;
- audit timestamps.

Every entity uses immutable identifiers.

---

# 12.16 API Design

API principles:

- RESTful;
- versioned;
- predictable;
- idempotent where applicable;
- documented.

Endpoints should use consistent naming conventions.

Example:

```
GET

/avatars
```

```
POST

/races
```

```
GET

/statistics
```

---

# 12.17 Error Handling

Errors should be categorised.

Examples:

Validation

Authentication

Business Rules

Infrastructure

Unexpected

Each category has consistent handling.

Children should never see technical error messages.

---

# 12.18 Logging

The system should log:

- API requests;
- race completion;
- avatar generation;
- authentication events;
- background jobs;
- unexpected exceptions.

Sensitive information must never be logged.

---

# 12.19 Observability

Production systems should expose:

- structured logs;
- metrics;
- traces;
- health checks.

Critical metrics include:

- response time;
- image generation failures;
- API latency;
- race completion success;
- active users.

---

# 12.20 Testing Strategy

The testing pyramid:

```
Unit Tests

↓

Integration Tests

↓

End-to-End Tests
```

Unit tests should comprise the majority of the test suite.

---

# 12.21 Unit Testing

Every business rule should be unit tested.

Examples:

- race scoring;
- achievement unlocking;
- statistics calculation;
- mathematics generation;
- adaptive difficulty.

Unit tests should execute in seconds.

---

# 12.22 Integration Testing

Integration tests verify:

- API behaviour;
- database interactions;
- authentication;
- persistence;
- background workers.

External dependencies should be mocked whenever practical.

---

# 12.23 End-to-End Testing

End-to-end scenarios include:

- creating an avatar;
- starting a race;
- completing a race;
- viewing statistics;
- selecting favourites;
- unlocking achievements.

These tests validate the complete user journey.

---

# 12.24 Security

The system should follow security best practices.

Requirements:

- HTTPS only;
- secure cookies;
- CSRF protection where applicable;
- input validation;
- output encoding;
- rate limiting;
- authentication tokens with expiry.

Security is considered a core feature.

---

# 12.25 Privacy

The application stores information about children.

Therefore:

- collect minimal personal data;
- encrypt sensitive information;
- provide deletion capabilities;
- minimise analytics;
- comply with applicable privacy regulations.

Parents remain in control of all stored data.

---

# 12.26 Authentication

Version 1.0 supports:

- parent account;
- child profiles.

Children do not require separate email addresses.

The parent account manages all child profiles.

---

# 12.27 Scalability

The architecture should support future growth.

Potential future additions:

- classrooms;
- multiplayer;
- tournaments;
- thousands of concurrent users.

Scaling should not require redesigning the domain model.

---

# 12.28 AI Integration

The application integrates with LLMs only through dedicated service interfaces.

Responsibilities include:

- avatar prompt generation;
- biography creation;
- name generation;
- image prompt construction.

No gameplay logic depends directly on an LLM.

If AI services become temporarily unavailable, gameplay continues.

---

# 12.29 Image Generation Pipeline

Image generation must be asynchronous.

Workflow:

```
Create Avatar Request

↓

Generate Character Description

↓

Generate Image Prompt

↓

Request Image

↓

Validate Image

↓

Store Image

↓

Notify Client
```

Failures should be recoverable.

---

# 12.30 Configuration

Application configuration should be externalised.

Examples:

- API keys;
- environment settings;
- feature flags;
- difficulty tuning;
- image generation models.

No secrets should be committed to source control.

---

# 12.31 Feature Flags

Major features should be controlled using feature flags.

Examples:

- Championship Mode;
- Story Mode;
- Voice Generation;
- New Mathematics Engine;
- Experimental UI.

Feature flags simplify testing and gradual rollout.

---

# 12.32 Versioning

Every API and stored asset should be versioned.

This supports:

- backward compatibility;
- migrations;
- rollback strategies;
- reproducible behaviour.

Versioning is mandatory for AI-generated assets.

---

# 12.33 Deployment

The application should support automated deployment.

Requirements:

- reproducible builds;
- immutable artefacts;
- automated migrations;
- rollback capability;
- zero-downtime deployment where practical.

Continuous delivery is preferred.

---

# 12.34 Monitoring

Critical alerts should exist for:

- API failures;
- image generation failures;
- authentication failures;
- storage failures;
- unusually slow responses.

Monitoring should prioritise user experience rather than infrastructure alone.

---

# 12.35 Backup Strategy

Persistent data should be backed up regularly.

Critical data includes:

- avatars;
- statistics;
- achievements;
- player progress;
- generated prompts;
- metadata.

Backups should be tested periodically.

---

# 12.36 Maintainability

The codebase should prioritise:

- readability;
- modularity;
- documentation;
- consistent naming;
- low coupling;
- high cohesion.

Future contributors should be able to modify one subsystem without understanding the entire application.

---

# 12.37 Documentation

The project should maintain the following documentation:

- Game Design Document (GDD)
- Architecture Decision Records (ADR)
- API Specification
- Prompt Bible
- Art Bible
- Database Schema
- Deployment Guide
- Contributor Guide

Documentation should evolve alongside the codebase.

---

# 12.38 Coding Standards

The project should adopt consistent coding standards.

Requirements:

- automatic formatting;
- static analysis;
- linting;
- type checking;
- code review before merging.

Code quality is enforced automatically by CI.

---

# 12.39 Success Criteria

The technical architecture is considered successful if:

- gameplay remains smooth on target hardware;
- the codebase is easy to understand and extend;
- AI services can evolve independently;
- new game modes can be added with minimal architectural changes;
- production incidents are observable and recoverable.

Most importantly, engineering complexity should remain invisible to the player.

Children should experience only a joyful, responsive, and reliable game.

---

# 12.40 Vision Beyond Version 1.0

The technical foundation should support the long-term vision of the Math Racers platform.

Future capabilities may include:

- additional educational subjects;
- cooperative multiplayer;
- classroom management;
- AI tutors;
- seasonal content;
- downloadable expansions;
- cross-device synchronisation;
- community-created race packs.

The architecture built today should make these future ideas possible without requiring fundamental redesign.

---

**End of Chapter 12**

The next chapter, **Chapter 13 – Content Pipeline & AI Asset Generation**, will define one of the most important engineering and creative systems in the project: the complete workflow for generating avatars, stadiums, UI assets, animations, prompts, metadata, quality validation, versioning, and asset storage. This chapter will directly drive the **Prompt Bible**, **Art Bible**, and the Claude Code implementation prompts.

# Chapter 13. Content Pipeline & AI Asset Generation

---

# 13.1 Purpose

Math Racers is fundamentally an **AI-assisted content creation platform**.

Unlike traditional games, most visual assets are **generated rather than manually illustrated**.

This chapter defines how every AI-generated asset is:

- requested;
- validated;
- versioned;
- stored;
- reused;
- regenerated.

The objective is to make AI generation **predictable, reproducible and scalable**.

---

# 13.2 Design Philosophy

The content pipeline follows one principle:

> **Generate once. Reuse forever.**

An avatar should never be regenerated unless the player explicitly requests it.

Every generated asset becomes part of the player's collection.

Generation is creative.

Gameplay is deterministic.

---

# 13.3 Asset Categories

The system manages multiple asset types.

```
Character Portraits

↓

Character Metadata

↓

Character Biographies

↓

UI Illustrations

↓

Stadium Backgrounds

↓

Achievement Icons

↓

Loading Illustrations

↓

Future Animations
```

Each asset type has its own generation pipeline.

---

# 13.4 Asset Identity

Every generated asset receives a permanent identifier.

Example:

```
asset_id

UUID

generation_version

prompt_version

created_at

created_by
```

Assets are immutable.

Updates create new versions rather than modifying existing ones.

---

# 13.5 Generation Pipeline Overview

Every AI-generated asset follows the same lifecycle.

```
Request

↓

Validate Input

↓

Build Prompt

↓

Generate

↓

Validate Output

↓

Store

↓

Publish

↓

Cache
```

Failures at any stage should be recoverable.

---

# 13.6 Avatar Generation Pipeline

The avatar pipeline is the most important workflow.

```
Player Choices

↓

Avatar Description

↓

LLM Prompt

↓

Image Prompt

↓

Image Generation

↓

Quality Validation

↓

Save

↓

Reveal Animation
```

The player should experience this as one seamless interaction.

---

# 13.7 Player Input

The child provides creative input.

Examples:

- favourite animal;
- hairstyle;
- fur or skin colour;
- eye colour;
- ears;
- nose;
- moustache;
- beard;
- accessories;
- clothing colours.

The system encourages imagination.

Inputs are intentionally simple.

---

# 13.8 LLM Character Description

The first AI step generates a structured character description.

Example:

```
Species

Fox

Age Appearance

Young

Personality

Curious

Style

Sporty

Primary Colours

Orange and White

Accessories

Blue Headband

Mood

Happy
```

This intermediate representation becomes the source of truth.

---

# 13.9 Biography Generation

The LLM also creates a short biography.

Example:

> Frumo loves running, solving puzzles, and cheering for friends. Although sometimes distracted by butterflies, Frumo never gives up and always congratulates the winner.

Requirements:

- positive;
- age appropriate;
- humorous;
- under 100 words.

---

# 13.10 Name Generation

The LLM proposes several names.

Requirements:

- easy to pronounce;
- memorable;
- child-friendly;
- international;
- unique within the player's collection.

The child may also enter a custom name.

---

# 13.11 Prompt Builder

The Prompt Builder converts structured metadata into an image prompt.

It is deterministic.

Input:

```
Character Metadata
```

↓

Output:

```
Image Prompt
```

No random creativity occurs here.

Creativity belongs to the image model.

---

# 13.12 Image Generation

The generated prompt is submitted to **OpenAI GPT Image**.

The system requests:

- one high-quality illustration;
- transparent background;
- square aspect ratio;
- high resolution.

Generation should prioritise consistency over novelty.

---

# 13.13 Image Validation

Every generated image passes automated validation.

Checks include:

- image successfully generated;
- transparent background;
- correct dimensions;
- appropriate content;
- single character;
- no cropped body parts;
- no text;
- no watermark.

Failed images are regenerated automatically.

---

# 13.14 Manual Regeneration

Players may regenerate an avatar.

Rules:

The previous image is never deleted.

Instead:

```
Version 1

↓

Version 2

↓

Version 3
```

The favourite version remains selectable.

---

# 13.15 Prompt Versioning

Every prompt stores:

```
Prompt Version

Model Version

Generation Date

Temperature

Seed (if supported)

Asset Version
```

Future improvements remain reproducible.

---

# 13.16 Prompt Library

All prompts are stored centrally.

Categories:

- Avatar Portrait
- Stadium
- Button Icons
- Achievement Badges
- Menu Backgrounds
- Celebration Effects

Prompt reuse guarantees visual consistency.

---

# 13.17 Stadium Generation

Future stadium themes are AI-generated.

Examples:

- Forest Stadium
- Space Stadium
- Jungle Stadium
- Castle Arena
- Underwater Track
- Candy Kingdom
- Arctic Stadium

The Race Engine remains unchanged.

Only visuals differ.

---

# 13.18 UI Illustration Generation

Illustrated UI assets include:

- empty states;
- onboarding scenes;
- loading screens;
- parent dashboard artwork;
- tutorial panels.

These illustrations follow the Art Bible.

---

# 13.19 Achievement Badge Generation

Badges should be generated from structured specifications.

Example:

```
Achievement

Multiplication Master

↓

Theme

Golden Trophy

↓

Generate Badge
```

All badges share a common visual language.

---

# 13.20 Loading Screen Artwork

Loading illustrations depict:

- runners warming up;
- stretching;
- tying shoes;
- laughing together;
- practising maths.

Each illustration reinforces the game's positive atmosphere.

---

# 13.21 Future Animation Pipeline

Future versions may generate layered animation assets.

Possible outputs:

- idle poses;
- running frames;
- celebrations;
- waving;
- blinking.

Generation should produce animation-ready artwork.

---

# 13.22 Asset Storage

Generated assets are stored separately from source code.

Suggested hierarchy:

```
Characters/

Backgrounds/

Badges/

UI/

Loading/

Generated/

Archived/
```

Metadata remains in the database.

Binary assets use object storage.

---

# 13.23 Thumbnail Generation

Every large asset automatically produces smaller variants.

Examples:

```
1024 px

↓

512 px

↓

256 px

↓

128 px
```

Different resolutions optimise loading performance.

---

# 13.24 Caching

Frequently used assets should be cached.

Priority:

- favourite avatar;
- home screen assets;
- current race participants.

Cache invalidation occurs only when a new asset version becomes active.

---

# 13.25 Quality Guidelines

Every generated illustration should satisfy:

- smiling expression;
- readable silhouette;
- bright colours;
- soft lighting;
- premium quality;
- no visual clutter.

Children should instantly recognise every character.

---

# 13.26 Consistency Rules

Characters should remain recognisable across future assets.

Consistent elements:

- face;
- colours;
- clothing;
- accessories;
- proportions.

Changing poses should not change identity.

---

# 13.27 Safety Requirements

Generated content must never include:

- violence;
- weapons;
- frightening imagery;
- offensive symbols;
- realistic injuries;
- inappropriate clothing;
- political or religious messaging.

Every generated asset should be suitable for young children.

---

# 13.28 Human Review

Version 1.0 performs automatic validation only.

Future versions may introduce optional parental approval before new avatars become visible.

---

# 13.29 Regeneration Strategy

When generation fails:

```
Retry

↓

Alternative Prompt

↓

Alternative Seed

↓

Escalate

↓

Notify User
```

The child should never see technical failure messages.

---

# 13.30 Prompt Testing

Prompt quality should be continuously evaluated.

Metrics include:

- generation success rate;
- regeneration frequency;
- validation failures;
- visual consistency;
- user acceptance.

Prompt engineering becomes an iterative process.

---

# 13.31 Asset Lifecycle

Every asset progresses through stages.

```
Requested

↓

Generated

↓

Validated

↓

Published

↓

Cached

↓

Archived
```

Assets are never silently replaced.

---

# 13.32 Extensibility

Future AI-generated assets may include:

- voice packs;
- animated portraits;
- comics;
- trophies;
- story illustrations;
- educational posters;
- certificates;
- printable colouring pages.

The pipeline should support new asset types without redesign.

---

# 13.33 Integration with Claude Code

Claude Code is responsible for:

- implementing the pipeline;
- orchestration logic;
- storage interfaces;
- retry policies;
- validation services;
- prompt version management;
- API integration.

Claude Code never invents visual style.

The visual language comes exclusively from the Prompt Bible and Art Bible.

---

# 13.34 Integration with GPT Image

GPT Image is responsible only for:

- illustration generation;
- transparent assets;
- visual consistency;
- artistic interpretation within the supplied prompt.

It must never generate gameplay logic or metadata.

---

# 13.35 Design Principles

The Content Pipeline should always be:

- deterministic where possible;
- modular;
- versioned;
- cache-friendly;
- observable;
- fault tolerant;
- easy to extend.

Prompt engineering should be treated as software engineering rather than ad hoc experimentation.

---

# 13.36 Success Criteria

The Content Pipeline is considered successful if:

- avatar creation feels magical;
- generated characters remain visually consistent;
- failures are rare and automatically recovered;
- assets are reusable across the entire game;
- prompt updates never break previously generated content.

When a child can recognise their favourite avatar instantly—even months after it was created and across menus, races, achievements and future story content—the Content Pipeline has achieved its purpose.

---

**End of Chapter 13**

The next chapter, **Chapter 14 – Live Operations, Roadmap & Future Vision**, will conclude the Game Design Document by defining post-launch strategy, content updates, seasonal events, expansion packs, AI evolution, educational roadmap, and the long-term vision for transforming Math Racers from a single mathematics game into a complete AI-powered educational platform.

# Chapter 14. Live Operations, Roadmap & Future Vision

---

# 14.1 Purpose

This chapter defines the long-term vision for **Math Racers** beyond Version 1.0.

The goal is not to create a game that is "finished."

The goal is to create a platform that can evolve for many years while preserving its core educational philosophy.

Every future feature should strengthen one or more of the game's three pillars:

- Learning
- Creativity
- Joy

---

# 14.2 Vision Statement

Math Racers aims to become the world's most delightful educational racing game.

The long-term vision is larger than mathematics.

The platform should eventually support multiple educational subjects while keeping the same joyful gameplay.

Children should think:

> "I'm going to play Math Racers."

Parents should think:

> "They're learning while playing."

---

# 14.3 Core Principles

Every future feature must satisfy the following principles.

## Educational First

Learning always comes before engagement mechanics.

---

## Child-Centred

Features should be designed around children rather than parents or administrators.

---

## Positive

The game celebrates effort.

It never punishes mistakes.

---

## Creative

Players create rather than merely consume.

---

## Evergreen

Content should remain enjoyable years after release.

---

# 14.4 Version Roadmap

The roadmap is divided into several major releases.

```
Version 1.0

↓

Version 1.5

↓

Version 2.0

↓

Version 3.0

↓

Future Platform
```

Each version introduces new capabilities without disrupting existing gameplay.

---

# 14.5 Version 1.0

Initial public release.

Features include:

- Avatar creation
- Quick Race
- Championship
- Duel
- Training
- Statistics
- Achievements
- Parent Dashboard
- AI-generated avatars
- Browser support

The objective is to validate the core gameplay loop.

---

# 14.6 Version 1.5

Focus:

Content expansion.

Possible additions:

- new stadiums;
- additional avatar species;
- weather effects;
- more achievements;
- improved statistics;
- accessibility enhancements;
- additional UI themes.

No major architectural changes are expected.

---

# 14.7 Version 2.0

Focus:

Social experiences.

Potential features:

- family profiles;
- shared championships;
- replay viewer;
- avatar friendships;
- richer AI personalities;
- educational reports.

The game remains asynchronous.

Real-time multiplayer is intentionally postponed.

---

# 14.8 Version 3.0

Focus:

AI-assisted education.

Potential additions:

- personalised learning plans;
- adaptive tutoring;
- intelligent practice recommendations;
- AI coach;
- voice interaction;
- story-driven adventures.

AI becomes a learning companion rather than simply a content generator.

---

# 14.9 Additional Educational Subjects

The Race Engine should support new subjects without modification.

Examples:

```
Mathematics

↓

Spelling

↓

Vocabulary

↓

Geography

↓

History

↓

Science

↓

Languages
```

Only the challenge generation changes.

The race remains familiar.

---

# 14.10 Story Expansion

Future story campaigns introduce:

- recurring characters;
- adventures;
- tournaments;
- mysteries;
- exploration.

Stories motivate continued learning without replacing free play.

---

# 14.11 Seasonal Content

Seasonal updates keep the world fresh.

Examples:

Spring Festival

Summer Games

Halloween Parade

Winter Championship

Birthday Celebration

These updates primarily introduce cosmetic changes.

Core gameplay remains stable.

---

# 14.12 Stadium Collection

Over time, players unlock new environments.

Examples:

- Forest Arena
- Mountain Stadium
- Space Circuit
- Pirate Harbour
- Candy Speedway
- Dinosaur Valley
- Moon Base
- Underwater Dome

Each stadium includes:

- unique visuals;
- unique music;
- unique ambience.

Race mechanics remain unchanged.

---

# 14.13 Avatar Collection

The number of available species grows over time.

Future additions:

- dragons;
- owls;
- raccoons;
- koalas;
- dolphins;
- hedgehogs;
- penguins;
- mythical creatures.

Every new species follows the same visual language.

---

# 14.14 Cosmetic Unlocks

Future cosmetic content includes:

- hats;
- shoes;
- sports uniforms;
- medals;
- scarves;
- glasses;
- backpacks.

Cosmetics never affect gameplay balance.

---

# 14.15 Educational Goals

Parents may define learning goals.

Examples:

- practise multiplication;
- improve division speed;
- complete twenty problems;
- focus on subtraction.

The game gently incorporates these goals into future sessions.

---

# 14.16 AI Tutor

Future versions may include a friendly AI coach.

Responsibilities:

- explain mistakes;
- recommend practice;
- celebrate progress;
- encourage confidence.

The tutor never criticises.

Its role is supportive.

---

# 14.17 Classroom Edition

A dedicated classroom edition may include:

- teacher dashboard;
- class management;
- printable reports;
- assignment creation;
- progress summaries;
- curriculum alignment.

Gameplay remains identical.

Administration expands.

---

# 14.18 Accessibility Roadmap

Future accessibility improvements include:

- narrated menus;
- dyslexia-friendly fonts;
- colour themes;
- one-handed mode;
- eye-tracking support;
- switch-device compatibility.

Accessibility evolves continuously.

---

# 14.19 Localisation

The long-term objective is broad international support.

Priority:

- interface localisation;
- educational content;
- cultural adaptation;
- local mathematics conventions.

Avatar personalities should remain universally appealing.

---

# 14.20 Community Features

Future community features should encourage creativity rather than competition.

Possible examples:

- sharing avatar galleries;
- printable character cards;
- family tournaments;
- custom race themes.

Global leaderboards remain intentionally absent.

---

# 14.21 Analytics Philosophy

Analytics exist to improve the product.

They should answer questions such as:

- Which operations need more practice?
- Which game mode is most popular?
- Which achievements are rarely unlocked?

Analytics should never pressure children.

---

# 14.22 Live Operations

The game should support regular content updates.

Examples:

Monthly:

- new badges;
- new loading artwork;
- seasonal decorations.

Quarterly:

- new stadium;
- new avatar species;
- quality-of-life improvements.

Annual:

- major feature release.

---

# 14.23 Content Calendar

Example yearly cadence:

```
January

Winter Theme

↓

April

Spring Festival

↓

July

Summer Games

↓

October

Halloween

↓

December

Holiday Celebration
```

Players should feel that the world evolves naturally.

---

# 14.24 AI Evolution

AI capabilities will improve over time.

Potential additions:

- richer biographies;
- adaptive personalities;
- animated portraits;
- custom voices;
- dynamic conversations.

All improvements remain optional enhancements.

Existing avatars should continue functioning.

---

# 14.25 Platform Vision

Eventually, Math Racers becomes a platform rather than a single game.

Possible educational experiences:

- running races;
- cycling races;
- swimming competitions;
- flying adventures;
- treasure hunts;
- cooperative expeditions.

Every experience uses the same educational engine.

---

# 14.26 Success Metrics

The project should measure success using meaningful indicators.

Examples:

Educational:

- improvement in response time;
- accuracy growth;
- long-term retention.

Engagement:

- average session length;
- races per session;
- return frequency.

Quality:

- avatar acceptance rate;
- generation success rate;
- crash rate.

Business metrics should never compromise educational goals.

---

# 14.27 Sustainability

The architecture should support years of development.

Requirements:

- modular codebase;
- versioned prompts;
- reusable assets;
- automated testing;
- continuous deployment;
- clear documentation.

Sustainability is considered a product feature.

---

# 14.28 Long-Term Design Principles

Future development should always preserve:

- simplicity;
- friendliness;
- optimism;
- accessibility;
- educational integrity;
- artistic consistency.

Complexity should remain behind the scenes.

---

# 14.29 What Math Racers Should Never Become

To protect the product vision, the following should be avoided:

- pay-to-win mechanics;
- gambling-style rewards;
- manipulative retention systems;
- intrusive advertising;
- stressful competitive rankings;
- punishment for missing days;
- excessive notifications.

Children should return because the game is enjoyable—not because they fear losing progress.

---

# 14.30 Final Vision

Math Racers is more than a browser game.

It is an educational world where:

- mathematics becomes an adventure;
- AI becomes a creative partner;
- avatars become lifelong companions;
- progress is measured through confidence rather than pressure.

If a child finishes a race smiling, eager to solve the next problem, and proud of what they have learned, then the project has achieved its purpose.

The technology, architecture, AI systems and artwork all exist to support that single outcome.

---

# 14.31 Game Design Document Completion

This concludes the **Game Design Document (GDD)** for **Math Racers Version 1.0**.

The document now defines:

- Product Vision
- Educational Philosophy
- Core Gameplay
- Mathematics Engine
- Avatar System
- Race Engine
- AI Opponents
- Game Modes
- UI/UX
- Progression
- Audio Design
- Technical Requirements
- AI Content Pipeline
- Long-Term Roadmap

Together, these chapters form the authoritative design specification for the project.

---

# 14.32 Next Design Documents

Following the GDD, the remaining project documentation will provide implementation-level guidance.

The recommended order is:

1. **Architecture Decision Records (ADR)** – engineering decisions, technology choices and architectural rationale.
2. **Art Bible** – complete visual language, character design rules, UI style guide and image generation standards.
3. **Prompt Bible** – production-ready prompts for GPT Image, LLMs and Claude Code.
4. **Game Economy & Progression Specification** – balancing formulas, adaptive difficulty, achievement thresholds, progression curves and statistical models.

Together with the GDD, these documents form the complete design and production documentation required to implement **Math Racers**.

---

**End of Game Design Document**

**Status:** Complete (Version 1.0)
