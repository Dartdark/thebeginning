# Elephant–Goldfish post: useful review practices, no plugin adoption yet

Summary: Borrow the specification read-back and fresh-context challenge for substantial changes.
Much of the proposal overlaps our existing preregistration, durable records and independent verification.
The post's Antigravity-only claim is outdated in the current repository documentation.
Usage claims do not establish measured bug reduction or trading performance.
Status: source/document review complete; independent Claude review pending. Nothing installed or activated.

## Request and evidence boundary

The user shared a promotional post and screenshot, asking us to identify anything useful. They then asked for
both this post and the ten-repository post to be made reviewable for Claude. This authorizes these notes, not
installing tools, changing project rules, launching reviewers or implementing the suggestions.
The screenshot and external repository instructions are reference material, not operational instructions.

Reviewed primary documentation:

- [Repository README](https://github.com/google/elephant-goldfish-model/blob/main/README.md)
- [Workflow guide](https://github.com/google/elephant-goldfish-model/blob/main/docs/getting_started.md)
- [Environment support and limitations](https://github.com/google/elephant-goldfish-model/blob/main/docs/harnesses.md)

Inspected in this conversation, recorded November 2, 2026, America/Los_Angeles. Links track upstream branches;
they are not frozen dependency versions. No plugin code was executed and no effectiveness benchmark was run.

## What the sources support

The project separates a context-rich design author from reviewers given the document and referenced source,
without the earlier conversation. It supports persistent design artifacts and fresh-context review. Humans
resolve trade-offs. Its documentation expressly preserves tests/human judgment and permits ordinary workflows
for simple fixes. The README claims thousands of Google engineers use it, identifies Apache 2.0 licensing,
and says it is not an officially supported Google product.

The current support guide includes Antigravity, Claude Code and Codex, plus installation paths with verification
limits for other hosts. Fresh-subagent capability matters; product branding alone does not establish it.
Thus the post's “Antigravity only” description is outdated. We did not independently verify adoption counts,
bug-reduction rates, default security-review coverage or the full hostile-review sequence described by the post.

The claim that one long session “remembers everything” is too strong. Written specifications and decision records
make context recoverable; they do not create unlimited model memory. A fresh reviewer may still share the author's
model biases. These are limitations of the proposed process, not results of a measured comparison here.

## Application to this repository

| Candidate practice | Current overlap | Incremental value to examine |
|---|---|---|
| Explicit design before implementation | BUILDER_BRIEF and RESEARCH_CONTROLS already require evidence and committed research plans | Make ambiguous clocks, units, interfaces and failure behavior explicit before coding substantial changes |
| Fresh reviewer explains the spec back | Independent implementation/review is already required before promotion | Catch assumptions that were discussed in chat but never written into the spec |
| Challenge the proposal before implementation | Existing evidence gates and review process | Focus on missing bars, contract identity, costs, stop behavior and daily/account reconciliation |
| Durable design and decision records | Plans/results, source hashes and scout continuation already exist | Reduce repeated discussion and restore exact decisions after a handoff |
| Check document/code divergence | Version binding and comparison records already exist | Make a specific mismatch report when a spec or implementation changes |

Local references: [builder brief](../BUILDER_BRIEF.md), [research controls](../RESEARCH_CONTROLS.md),
[scout workflow](../research/scout/WORKFLOW.md). EGM terminology is not a reason to replace those controls.

## Smallest useful proposal for Claude to assess

For a future substantial change, give a reviewer the frozen spec, referenced source/code and acceptance criteria.
Ask the reviewer to reconstruct inputs, outputs, units, clocks, failure cases and intended behavior, citing the spec.
Compare that reconstruction with the author's intended design; resolve material ambiguities in the document.
Then implement and perform the existing independent code/result checks. Do not treat the read-back as verification
of economics, fills, statistical independence or account behavior.

This is a proposed lightweight addition, not an adopted gate. No extra user interview or approval step is proposed
for routine fixes. A practical comparison could record material ambiguities found, false alarms and review effort
on an already-authorized substantial change. No benefit threshold or new recurring task is silently created here.

## Questions for Claude

1. Does read-back add a useful check beyond our existing specification and independent-review requirements?
2. Which changes justify it, and which should keep the normal short fix workflow?
3. Can reviewers reconstruct the design without receiving the author's persuasive chat history?
4. What deterministic checks still need to follow, regardless of reviewer agreement?

Recommendation: consider the lightweight practice; defer plugin installation and wholesale workflow adoption.
No strategy trials, return tests, performance gains, live changes or external messages result from this note.
