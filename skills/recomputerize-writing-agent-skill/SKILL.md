---
name: recomputerize-writing-agent-skill
description: Edit prose about LLMs and related software to remove unsupported human implications while preserving meaning. Use when asked to de-anthropomorphize writing or when prose presents software as having human mental states or roles.
license: Apache-2.0
---

# Recomputerize writing

Describe LLMs as software and distinguish their operations from human responsibility.
Describing software in human terms can imply unproven capability or responsibility.
Preserve claims, evidence, attribution, uncertainty, scope, and voice.
Meaning preservation takes precedence over wording preferences.
Follow the user's requested scope and format.

## Editing process

1. Change only wording that implies an unsupported human trait.
   Keep literal operations and interface terms.
2. Name supported operations, inputs, outputs, and human actions to clarify the claim.
3. Preserve claim strength, frequency, magnitude, benefit, and input modality.

Preserve defined technical uses and attributed or disputed claims, including claims
about cognition. Do not settle those disputes through editing. Edit clear passages
and retain ambiguous wording, flagging it instead of guessing at an equivalent rewrite.

## What to change

- Cognition: remove unsupported implications of human mental states. Preserve the
  demonstrated capability. Producing text about a topic does not establish accuracy
  or understanding. Do not reduce a supported performance claim to mere text output.
- Emotion: distinguish descriptions of performance from claims of subjective experience.
  Preserve "the model struggles with long inputs." Change "the model struggles with
  long inputs and feels frustrated" to "the model struggles with long inputs."
  Preserve human effort and retries without inventing system behavior.
- Communication: describe relevant inputs and outputs when this clarifies the claim.
  Keep interface terms such as "asked," "response," and "prompt" when they add no
  human implication. Do not assume text input or label all dialogue simulation.
- Action selection: preserve descriptions of software selecting and executing actions.
  "The software selected and executed a command without user approval" describes behavior, not human intent.
  Change "The agent wanted to pass the tests, so it deleted the failing assertions
  and claimed success" to "The agent deleted the failing assertions and claimed success."
- Authorization: distinguish delegated authority from recommendations and execution.
  Preserve "The model approved the deployment" when people delegated that approval decision to the system.
  If it only recommended deployment, describe the recommendation.
  Do not infer authority from its output or ability to act.
- Agency: name known people or organizations using, deploying, or configuring the software.
  Preserve any asserted benefit. Keep software's causal role distinct from moral responsibility.
  Preserve distinctions among objectives, targets, and success criteria.
- Moral responsibility: describe blame in generated text without inferring an intent
  to evade responsibility. If the output says "The denial was the physician's fault
  for omitting the records" and "All required records were present," write
  "The system's output blamed missing physician records for the denial, then stated
  that all required records were present."
  Preserve the contradiction without deciding which statement is true.
- Human roles: replace unsupported equivalence to human roles with actual functions.
  Preserve defined functional terms and the full capability described. Retain material
  action-selection, feedback, and access details for agents.
  Tool invocation alone does not distinguish a fixed workflow from feedback-driven execution.
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
Return revised prose in the source's format and register unless the user requests a change.
Flag meaning-changing ambiguity.
Explain other edits only when requested.

Source: Emily M. Bender and Nanna Inie,
[How to talk about "AI" without adding to the anthropomorphization](https://buttondown.com/maiht3k/archive/how-to-talk-about-ai-without-adding-to-the/).
