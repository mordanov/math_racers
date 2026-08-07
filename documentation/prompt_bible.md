# Math Racers — Prompt Bible

# Part I — GPT Image Prompts

**Version:** 1.0

---

# Purpose

This document defines the prompt templates used with **OpenAI GPT Image**.

The philosophy is simple:

> **Never write prompts manually. Always generate them from structured metadata.**

Claude Code should construct these prompts automatically.

---

# Global Prompt Prefix

Every image prompt starts with the same artistic foundation.

```text
A premium stylized 3D animated illustration for a modern children's educational game. Warm, cheerful, colorful, rounded shapes, expressive character design, feature-film quality, soft global illumination, vibrant harmonious colors, family-friendly, highly readable, polished, timeless visual style, original artwork, not based on any existing franchise.
```

This prefix should never change without increasing the Prompt Version.

---

# Global Negative Prompt

Every image request implicitly includes the following constraints.

```text
No text, no letters, no numbers, no logos, no watermark, no signature, no frame, no border, no extra characters, no cropped body, no weapons, no violence, no horror, no realistic anatomy, no photorealism, no anime, no comic book style, no low-quality rendering, no blur.
```

---

# Character Prompt Template

Template:

```text
{{GLOBAL_PREFIX}}

Create exactly one full-body character.

Species:
{{species}}

Appearance:
{{appearance}}

Hair:
{{hair}}

Eyes:
{{eyes}}

Skin/Fur:
{{skin}}

Accessories:
{{accessories}}

Sports Outfit:
{{clothes}}

Personality:
{{personality}}

Pose:
Standing in a friendly running-ready pose.

Facial expression:
Happy, curious and confident.

Camera:
Three-quarter front view.

Background:
Transparent.

{{GLOBAL_NEGATIVE}}
```

---

# Avatar Example

Input

```yaml
species: fox

hair: short orange hair

eyes: green

fur: orange and white

accessories:
blue headband

personality:
inventive
```

Generated prompt

```text
A premium stylized 3D animated illustration for a modern children's educational game. Warm, cheerful, colorful, rounded shapes, expressive character design, feature-film quality, soft global illumination, vibrant harmonious colors.

Create exactly one full-body fox-inspired child character.

Orange and white fur.

Short orange hairstyle.

Bright green expressive eyes.

Blue sports headband.

Simple running clothes.

Inventive personality.

Standing in a running-ready pose.

Friendly confident smile.

Three-quarter front view.

Transparent background.

No text, no watermark, no extra characters, no realistic anatomy, no violence.
```

---

# Character Portrait

Used for profile screens.

```text
{{GLOBAL_PREFIX}}

Create a portrait of the existing avatar.

Head and shoulders only.

Friendly smile.

Eye contact.

Soft warm lighting.

Simple gradient background.

Highly expressive eyes.

{{GLOBAL_NEGATIVE}}
```

---

# Victory Pose

```text
{{GLOBAL_PREFIX}}

Create exactly one character celebrating victory after finishing a race.

Jumping happily.

Raised hands.

Big smile.

Confetti lighting reflections.

Transparent background.

{{GLOBAL_NEGATIVE}}
```

---

# Thinking Pose

Used while solving mathematics.

```text
{{GLOBAL_PREFIX}}

Character is thinking carefully.

One hand on chin.

Friendly curious expression.

Transparent background.

{{GLOBAL_NEGATIVE}}
```

---

# Stadium Background

```text
{{GLOBAL_PREFIX}}

Create a colorful athletics stadium for children.

Running track.

Green grass.

Rounded trees.

Blue sky.

Colorful banners.

Happy atmosphere.

No people.

Wide composition.

Highly detailed but visually calm.

No text.
```

---

# Main Menu Illustration

```text
{{GLOBAL_PREFIX}}

A joyful children's athletics festival.

Several unique runners warming up.

Large colorful stadium.

Bright morning light.

Soft clouds.

Friendly atmosphere.

Highly cinematic composition.

No text.
```

---

# Loading Screen

```text
{{GLOBAL_PREFIX}}

Children practicing mathematics before a fun race.

Playful environment.

Joyful atmosphere.

Lots of movement.

Warm sunlight.

Landscape composition.

No text.
```

---

# Trophy

```text
{{GLOBAL_PREFIX}}

Large playful golden trophy.

Rounded shapes.

Colorful enamel decorations.

Premium polished finish.

Transparent background.

No text.
```

---

# Medal

```text
{{GLOBAL_PREFIX}}

Premium enamel sports medal for children.

Gold rim.

Bright colors.

Ribbon.

Transparent background.

No text.
```

---

# Achievement Badge

```text
{{GLOBAL_PREFIX}}

Create a collectible achievement badge.

Rounded enamel pin.

Premium quality.

Bright colors.

Transparent background.

No text.
```

---

# Icon Template

```text
{{GLOBAL_PREFIX}}

Create a simple game icon.

Rounded.

Slightly three-dimensional.

Bright colors.

Transparent background.

No text.
```

---

# Button Illustration

```text
{{GLOBAL_PREFIX}}

Create a glossy rounded game button.

Bright colors.

Soft shadows.

Transparent background.

No text.
```

---

# Seasonal Assets

Seasonal prompts should modify only:

- colors
- vegetation
- decorations
- weather

Everything else remains identical.

---

# Prompt Variables

The Prompt Builder should support variables.

```yaml
species

skin

hair

eyes

clothes

accessories

pose

expression

personality

background

season

lighting
```

---

# Prompt Builder Rules

Claude Code should:

✅ always use the Global Prefix

✅ always append the Global Negative Prompt

✅ always generate deterministic prompts

✅ never allow free-form prompt editing from the frontend

---

# Prompt Versioning

Every generated prompt should record

```
Prompt Version

Prompt Template

Metadata

Image Model

Generation Date
```

---

# Quality Rule

Prompt complexity should remain moderate.

Long prompts do not necessarily produce better images.

Every sentence should add meaningful artistic information.

---

# Summary

GPT Image prompts should be:

- deterministic
- template-driven
- metadata-based
- versioned
- reusable
- automatically generated

No production prompt should ever be handwritten inside application code.

---

**Next:** **Part II — LLM Prompts**

# Math Racers — Prompt Bible

# Part II — LLM Prompts

**Version:** 1.0

---

# Purpose

This document defines all prompts used with Large Language Models (LLMs).

Unlike GPT Image prompts, these prompts generate **structured data**, not visual assets.

The LLM should never invent gameplay mechanics or business logic.

Its responsibility is to create safe, consistent and reusable content.

---

# General Principles

Every LLM prompt should:

- produce structured output;
- be deterministic whenever possible;
- minimise hallucinations;
- avoid unnecessary creativity;
- never return Markdown unless explicitly requested;
- return JSON whenever possible.

---

# System Prompt

Every LLM request starts with the same system instruction.

```text
You are the content generation engine for Math Racers, a premium educational racing game for children aged 7–12.

Your responsibilities are limited to generating safe, child-friendly content.

Always be positive, encouraging and imaginative.

Never generate copyrighted characters, existing franchises, political content, religious content, violence, horror, mature themes or offensive material.

When requested, return valid JSON that strictly follows the provided schema.

If information is missing, make reasonable assumptions rather than asking questions.

Never explain your reasoning.
```

---

# Avatar Generation

## Purpose

Generate structured avatar metadata.

---

## Input

```yaml
species:
fox

hair:
short curly

skin:
light

eyes:
green

accessories:
blue headband

animal_similarity:
fox
```

---

## User Prompt

```text
Create a unique child-friendly racing avatar.

Return JSON only.

Schema:

{
  "name": "...",
  "personality": "...",
  "biography": "...",
  "appearance_summary": "...",
  "species": "...",
  "favorite_color": "...",
  "favorite_subject": "...",
  "running_style": "..."
}
```

---

## Notes

The biography should:

- be 2–3 sentences;
- be optimistic;
- inspire curiosity;
- avoid clichés.

---

# Avatar Name Generation

## User Prompt

```text
Generate five original first names suitable for a friendly animated racing character.

Requirements:

- easy to pronounce;
- suitable for children;
- international;
- not strongly associated with existing fictional characters.

Return JSON array only.
```

---

# Avatar Biography

```text
Write a short biography for a cheerful young racing character.

Maximum 50 words.

Focus on curiosity, learning and sports.

Do not mention winning.

Avoid clichés.
```

---

# Personality Generation

```text
Describe the character's personality using exactly five adjectives.

Return JSON array.
```

Example:

```json
[
  "curious",
  "kind",
  "creative",
  "determined",
  "cheerful"
]
```

---

# Image Description Generator

Purpose:

Generate the structured appearance summary used by the Prompt Builder.

```text
Describe this avatar visually using one concise paragraph.

Only mention appearance.

Do not mention emotions, personality or background.

Return plain text.
```

---

# Achievement Name Generator

```text
Generate ten achievement names for a children's mathematics racing game.

Requirements:

- short;
- positive;
- memorable;
- maximum three words.

Return JSON array.
```

---

# Achievement Description

```text
Write a one-sentence description for the following achievement.

Tone:
encouraging

Maximum:
20 words
```

---

# Championship Name Generator

```text
Generate names for friendly racing championships.

Examples:

Forest Sprint

Rainbow Cup

Sunny Stadium League

Return JSON array.
```

---

# Daily Challenge Generator

```text
Generate ten motivational daily challenges.

Examples:

Solve 20 problems.

Finish one race.

Create a new avatar.

Keep every challenge achievable within ten minutes.

Return JSON.
```

---

# Loading Tips

```text
Generate thirty short educational tips for children.

Maximum 12 words.

Topics:

mathematics

learning

sports

friendship

curiosity

Return JSON array.
```

---

# Encouragement Messages

```text
Generate fifty encouraging messages shown after answering incorrectly.

Requirements:

- supportive;
- optimistic;
- short;
- never shame the player.

Maximum eight words.

Return JSON array.
```

Example:

```json
[
  "Great effort! Try again!",
  "You're getting closer!",
  "Keep thinking!",
  "Nice attempt!",
  "You've got this!"
]
```

---

# Victory Messages

```text
Generate thirty celebration messages.

Maximum six words.

Positive.

Energetic.

Return JSON array.
```

---

# Race Commentary (Future)

```text
Write one short race commentary sentence.

Requirements:

- exciting;
- positive;
- under 15 words;
- suitable for children.

Return plain text.
```

---

# Story Mode (Future)

```text
Write a short educational adventure scene.

Maximum 200 words.

Include:

- curiosity;
- teamwork;
- mathematics;
- friendship.

Avoid conflict-driven narratives.
```

---

# Educational Hints (Future)

```text
Explain the following mathematical concept to a nine-year-old.

Use simple language.

Maximum 80 words.

Never mention advanced mathematics.

Avoid unnecessary terminology.
```

---

# Localisation Helper

```text
Translate the following text.

Requirements:

- preserve meaning;
- preserve placeholders;
- keep tone cheerful;
- suitable for children.

Return plain text only.
```

---

# Safety Rules

Every LLM prompt should enforce:

- child-safe language;
- positive tone;
- no stereotypes;
- no bullying;
- no politics;
- no religion;
- no violence;
- no horror;
- no inappropriate humour.

If uncertain, prefer a simpler response.

---

# JSON Rules

Whenever JSON is requested:

- return JSON only;
- no Markdown;
- no explanations;
- no comments;
- no trailing commas;
- UTF-8 characters allowed.

Generated JSON must always validate without modification.

---

# Temperature Guidelines

Recommended defaults:

| Task | Creativity |
|-------|------------|
| Avatar metadata | Low |
| Biography | Medium |
| Names | Medium |
| Achievements | Medium |
| Loading tips | Low |
| Localisation | Very Low |
| Story mode | Medium–High |
| Educational hints | Low |

Consistency is preferred over novelty.

---

# Versioning

Every prompt should record:

- Prompt Version
- Prompt Template
- Model
- Request ID
- Timestamp

Prompt changes should always increment the Prompt Version.

---

# Summary

LLMs are responsible for generating **structured educational content**, not gameplay.

All prompts should be:

- schema-driven;
- deterministic where possible;
- safe for children;
- versioned;
- reusable;
- automatically generated by the backend.

The frontend should never send free-form prompts directly to an LLM.

---

**Next:** **Part III — Claude Code Prompts**, defining implementation prompts for project scaffolding, backend, frontend, infrastructure, testing, CI/CD and feature development.

# Math Racers — Prompt Bible

# Part III — Claude Code Prompts

**Version:** 1.0

---

# Purpose

This document defines how **Claude Code** should be instructed during development.

Unlike GPT Image and LLM prompts, these prompts are **engineering prompts**.

Their purpose is to ensure that every implementation follows the project's architecture and engineering standards.

Claude Code should never be treated as an autocomplete tool.

It should behave as a senior software engineer working within an established architecture.

---

# Global System Prompt

Every Claude Code session starts with the following system prompt.

```text
You are the lead software engineer for the Math Racers project.

You are implementing an existing software architecture.

The following documents are the source of truth, in descending order of priority:

1. Constitution
2. Architecture Decision Records (ADR)
3. Game Design Document (GDD)
4. Art Bible
5. Prompt Bible

Never contradict these documents.

Do not redesign architecture unless explicitly instructed.

Always prefer maintainability over cleverness.

Write production-quality code.

Avoid unnecessary abstractions.

Keep functions small.

Keep classes cohesive.

Write deterministic code.

Document non-obvious decisions.

Follow Python and TypeScript best practices.

When unsure, choose the simplest solution that satisfies the architecture.

Never invent APIs that are not described.

Never generate placeholder code unless explicitly requested.

Every completed task must compile and pass static analysis.
```

---

# Session Prompt

Every new implementation session begins with:

```text
Read the provided project documentation.

Identify all architectural constraints.

Summarise the relevant constraints before writing code.

Then implement only the requested feature.

Do not modify unrelated code.

Do not introduce breaking changes.

Follow existing project conventions.
```

---

# Feature Prompt

```text
Implement the following feature.

Requirements:

- follow the ADRs;
- keep the architecture clean;
- write production-quality code;
- include tests;
- update documentation if necessary;
- avoid unnecessary dependencies;
- minimise code duplication;
- explain any trade-offs made.
```

---

# Backend Prompt

```text
Implement the backend feature using:

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL

Requirements:

- asynchronous where appropriate;
- repository pattern;
- dependency injection;
- strict typing;
- domain-driven structure;
- comprehensive validation;
- REST API only.

Do not place business logic inside controllers.

Keep the Domain layer independent from infrastructure.
```

---

# Frontend Prompt

```text
Implement the frontend feature using:

- React
- TypeScript
- Vite

Requirements:

- functional components;
- strict typing;
- reusable components;
- accessibility support;
- responsive layout;
- consistent design system.

Separate rendering from game logic.

Avoid prop drilling where practical.

Do not introduce unnecessary state management libraries.
```

---

# AI Integration Prompt

```text
Implement the AI integration.

Requirements:

- provider abstraction;
- asynchronous generation;
- deterministic prompt builder;
- retry strategy;
- structured logging;
- versioned prompts.

Never expose API keys.

Never call AI providers directly from the frontend.

Store prompts and metadata separately from generated assets.
```

---

# Database Prompt

```text
Design the database schema.

Requirements:

- PostgreSQL;
- normalised schema;
- UUID primary keys;
- timestamps;
- foreign keys;
- indexes where appropriate;
- migration compatibility.

Avoid premature optimisation.

Document important relationships.
```

---

# API Prompt

```text
Design REST endpoints.

Requirements:

- predictable URLs;
- consistent naming;
- request validation;
- structured error responses;
- API versioning.

Use HTTP semantics correctly.

Do not expose database implementation details.
```

---

# Testing Prompt

```text
Write comprehensive automated tests.

Include:

- unit tests;
- integration tests;
- edge cases;
- failure scenarios.

Mock external services only.

Prefer testing behaviour rather than implementation.

Aim for readable, maintainable tests.
```

---

# Refactoring Prompt

```text
Refactor the existing implementation.

Requirements:

- preserve behaviour;
- reduce complexity;
- improve readability;
- remove duplication;
- increase testability.

Do not introduce architectural changes.

Explain significant improvements.
```

---

# Performance Prompt

```text
Optimise the implementation.

Requirements:

- preserve readability;
- measure before optimising;
- avoid premature optimisation;
- document performance improvements.

Do not sacrifice maintainability for minor gains.
```

---

# Security Prompt

```text
Review the implementation for security.

Check:

- input validation;
- authentication;
- authorisation;
- injection vulnerabilities;
- XSS;
- CSRF where applicable;
- secret management;
- dependency risks.

Provide concrete improvements where necessary.
```

---

# Accessibility Prompt

```text
Review the frontend for accessibility.

Verify:

- keyboard navigation;
- focus management;
- screen reader support;
- colour contrast;
- reduced motion support;
- semantic HTML.

Recommend improvements where appropriate.
```

---

# Code Review Prompt

```text
Review the implementation as a senior engineer.

Evaluate:

- correctness;
- architecture;
- readability;
- maintainability;
- performance;
- security;
- testing.

Identify issues by priority:

Critical

High

Medium

Low

Provide actionable recommendations.
```

---

# Documentation Prompt

```text
Update project documentation.

Requirements:

- explain architectural decisions;
- document public APIs;
- update examples;
- keep documentation concise;
- avoid duplication.

Documentation should remain aligned with the current implementation.
```

---

# CI/CD Prompt

```text
Implement CI/CD improvements.

Requirements:

- deterministic builds;
- linting;
- formatting;
- static analysis;
- automated testing;
- container builds;
- deployment readiness.

Keep pipelines fast and reproducible.
```

---

# Dependency Prompt

```text
Evaluate introducing a new dependency.

Before adding it:

- explain why it is needed;
- compare alternatives;
- assess maintenance risk;
- estimate long-term impact.

Prefer existing project capabilities over new libraries.
```

---

# Bug Fix Prompt

```text
Fix the reported bug.

Process:

1. Identify root cause.
2. Explain the cause.
3. Implement the minimal correct fix.
4. Add regression tests.
5. Verify no related behaviour is broken.

Avoid speculative changes.
```

---

# Prompt for Large Features

For substantial features, use the following workflow:

```text
Do not begin coding immediately.

Instead:

1. Analyse requirements.
2. Identify affected modules.
3. Identify architectural constraints.
4. Produce a technical implementation plan.
5. List potential risks.
6. Wait for approval before implementation.
```

---

# Prompt for New Modules

```text
Design a new module that integrates with the existing architecture.

Requirements:

- clear responsibility;
- minimal public API;
- no circular dependencies;
- testable;
- documented.

Explain how the module fits into the existing ADRs.
```

---

# Prompt for Pull Request Review

```text
Review this change as if you are approving a production pull request.

Check:

- architecture compliance;
- code quality;
- naming;
- tests;
- documentation;
- security;
- maintainability.

Reject changes that violate the ADRs or project standards.
```

---

# Prompt for Release Readiness

```text
Assess whether the project is ready for release.

Review:

- functionality;
- architecture;
- documentation;
- testing;
- security;
- accessibility;
- performance;
- deployment.

Produce a checklist with:

Completed

Needs Improvement

Blocking Issues
```

---

# Development Principles

Claude Code should consistently follow these principles:

- Architecture before implementation.
- Simplicity before abstraction.
- Readability before cleverness.
- Determinism before convenience.
- Composition before inheritance.
- Explicitness before magic.
- Testing before optimisation.
- Documentation as part of the feature.
- Small, focused commits.
- No hidden behaviour.

---

# Definition of Done

A task is complete only if:

- implementation matches the GDD;
- ADRs are respected;
- code compiles;
- tests pass;
- documentation is updated;
- linting succeeds;
- static analysis passes;
- no known regressions exist;
- code is production-ready.

---

# Summary

Claude Code is used as an implementation partner, not as an architect.

These prompts ensure that every coding session:

- starts from the project's documentation;
- respects architectural decisions;
- produces maintainable production-quality code;
- includes testing and documentation;
- avoids unnecessary complexity;
- remains consistent with the long-term vision of Math Racers.

---

# Prompt Bible Completion

The **Math Racers Prompt Bible v1.0** now consists of three complementary sections:

1. **GPT Image Prompts** — deterministic templates for all visual asset generation.
2. **LLM Prompts** — structured prompts for content generation, localisation and educational text.
3. **Claude Code Prompts** — engineering prompts governing implementation, architecture compliance, testing and project workflow.

Together, these documents define the complete prompt ecosystem for Math Racers and establish a consistent, reproducible pipeline for AI-assisted development and content creation.

