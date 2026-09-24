---
name: recomputerize-writing-agent-skill
description: Edit prose about LLMs and related software to remove unsupported human implications while preserving meaning. Use when asked to de-anthropomorphize writing or when prose presents software as having human mental states or roles.
license: Apache-2.0
---

# Recomputerize writing

Describe LLMs as software and distinguish their operations from human responsibility.
Describing software in human terms can imply unproven capability or responsibility.
Preserve claims, evidence, attribution, uncertainty, scope, and voice.
Meaning preservation takes precedence over wording preferences. Follow the user's requested scope and format.

## Editing process

1. Change only wording that implies an unsupported human trait. Keep literal operations and interface terms.
2. Name supported operations, inputs, outputs, and human actions to clarify the claim.
3. Preserve claim strength, frequency, magnitude, benefit, and input modality.

Preserve defined technical uses and attributed or disputed claims, including claims
about cognition. Do not settle those disputes through editing. Edit clear passages
and retain ambiguous wording, flagging it instead of guessing at an equivalent rewrite.
For example, when a log shows a retry, change "the system wanted another try" to
"the system retried."

## What to change

- Cognition: remove unsupported implications of human mental states. Preserve the
  demonstrated capability. Producing text about a topic does not establish accuracy
  or understanding. Do not reduce a supported performance claim to mere text output.
- Emotion: describe observed performance and the person's actions.
  Preserve effort and repeated attempts. "Struggles" need not imply feelings or
  incorrect output. Describe generated emotional language without assigning feelings.
- Communication: describe relevant inputs and outputs when this clarifies the claim.
  Keep interface terms such as "asked," "response," and "prompt" when they add no
  human implication. Do not assume text input or label all dialogue simulation.
- Agency: name known people or organizations using, deploying, or configuring the
  software. Preserve any asserted benefit. Describe automated actions without
  implying per-action approval. Keep software's causal role distinct from moral
  responsibility. Preserve distinctions among objectives, targets, and success criteria.
- Human roles: replace unsupported equivalence to human roles with actual functions.
  Preserve defined functional terms and the full capability described. For agents,
  retain material action-selection, feedback, and access details. Tool invocation
  alone does not distinguish a fixed workflow from feedback-driven execution.
- Names and pronouns: use "it" for a system. Name people and systems separately
  when collective pronouns obscure responsibility. Retain identifying product names.
- Biological metaphors: explain computation when a metaphor implies living tissue.
  Keep conventional resource descriptions such as "consumes memory" when accurate.
  Distinguish training from inference. Data use does not always adjust model weights.

## Preserve precision

Prefer a product, model type, or function when it matches the intended scope.
Keep "AI" for an umbrella category or discussion of the term, industry, or ideology.
Choose familiar, accurate language for the audience. Avoid mocking labels, slogans,
and cumbersome euphemisms such as "probabilistic automation" for every system.

Name specific defects when known: false claims, nonexistent citations, or contradictions
with the supplied source. Otherwise preserve the defined error term or flag ambiguity.
Do not broaden "hallucination" to "undesirable output" or invent a generation mechanism.
Describe observed bias without implying its origin unless the evidence supports it.

Preserve quotations, titles, code, API names, and exact interface labels. Keep established
technical terms when replacement would obscure meaning. Explain them for the audience.
Do not infer human traits from labels such as "attention," "memory," or "neural network."

Do not invent motives, consciousness claims, capabilities, actors, or verification status.
Do not claim these wording choices improve trust or accountability without evidence.
Compare each change with the source for actors, operations, claim strength, and scope.
Return revised prose in the source's format and register unless the user requests a change. Flag meaning-changing ambiguity.
Explain other edits only when requested.

Source: Emily M. Bender and Nanna Inie,
[How to talk about "AI" without adding to the anthropomorphization](https://buttondown.com/maiht3k/archive/how-to-talk-about-ai-without-adding-to-the/).
