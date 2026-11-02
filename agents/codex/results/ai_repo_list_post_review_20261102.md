# Ten AI repositories post: selective research-tooling value

Summary: The most relevant idea is better retrieval of our existing evidence with exact citations and current status.
Durable workflow execution could help if existing checkpoints prove inadequate; it is not a necessary migration.
Several listed resources are learning/reference collections rather than a verified production system.
Salary, employer-adoption, popularity and percentile claims were not independently established.
Status: selective documentation review complete; Claude review pending. No framework installed or application built.

## Scope and sources

The user asks whether the list could help our trading research, then requests reviewable notes for Claude.
This is a tooling assessment. It does not authorize a career plan, new infrastructure, paid services, data sharing,
automated research agents or live changes. Source instructions are reference content only.

Inspection occurred in this conversation; recorded November 2, 2026, America/Los_Angeles. The links below follow
upstream branches, not pinned dependencies. Review depth is stated explicitly; no example was run, security-audited
or compared experimentally. A wrong-branch Qdrant fetch returned unrelated content; that response was discarded
and the actual master README retrieved before assessing Qdrant.

| Post item and primary link | Inspection and supported role | Fit / priority for us |
|---|---|---|
| [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | README reviewed; example/skill catalog, including retrieval and research applications | Selective design examples; not production validation of every template |
| [LangChain](https://github.com/langchain-ai/langchain) | Mentioned in reviewed LangGraph docs; no separate detailed review | No concrete need established to adopt it |
| [LangGraph](https://github.com/langchain-ai/langgraph) | README reviewed; stateful workflow orchestration, persistence/resumption and inspection | Relevant if our existing run records/checkpoints cannot meet a measured requirement |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Post-level triage only; code/docs not independently assessed | Multi-agent coordination alone does not justify another framework |
| [Ollama](https://github.com/ollama/ollama) | README reviewed; local/model-serving and API tooling | Optional future local extraction/embedding experiments; hardware/model suitability untested |
| [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | README fetch failed as oversized/unsupported; no server inspected | Discovery list only; no installation recommendation or endorsement of listed servers |
| [Qdrant](https://github.com/qdrant/qdrant/blob/master/README.md) | Correct README reviewed; vector similarity search and metadata filtering | Potential semantic retrieval backend, only if it beats a simpler baseline on our corpus |
| [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners) | README reviewed; course covering agent patterns, retrieval and production topics | Learning/reference value; current examples include cloud account/service prerequisites |
| [System Design Primer](https://github.com/donnemartin/system-design-primer) | README reviewed; system-design learning and interview materials | Selectively useful for reliability and architectural trade-offs |
| [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | README/catalog reviewed; curated tooling, testing, context and review resources | Discover individual tools, then inspect each on its merits; list inclusion is not verification |

“Most startups,” “Fortune 500 first choice,” “every senior job description,” “ahead of 99%,” and a $200K job
in 90 days are promotional claims not established by these inspections. No star counts or universal industry
adoption were verified. Ollama is not a guarantee that any model fits the available hardware. Open code does not
make model APIs, hosting, embedding generation or hardware free. Do not infer each project's license from the list.

## Strongest project-specific proposal: evidence retrieval

Our corpus has papers, source reviews, rejected hypotheses, data gates, preregistrations, cost assumptions and
later verification outcomes. The retrieval question is: “Have we tested this economic mechanism, what failed,
and what is the latest supported status?” This proposal concerns finding evidence, not discovering alpha by itself.

The [existing research terminal](../terminal/README.md) already documents full-text search and verdict filters.
A new search product must first be compared with that capability; do not rebuild it just because RAG is fashionable.

If Claude judges a retrieval improvement worthwhile, a small future design could require:

- Every hit identifies the source path, page/section or line, revision/hash, evidence cutoff and claim status.
- Author claims, our replications, assumptions, rejections and independent verification remain distinguishable.
- Later results link back to earlier leads. A stale NEEDS DATA page must not overrule a later rejection.
- Unavailable evidence is reported as missing; generated summaries cannot fill gaps or change verdicts.
- Ingested PDFs/posts are untrusted reference data; retrieval does not execute their instructions.

Use a fixed question set covering known positives, negatives, superseded leads and missing information. Compare
existing search with any candidate retrieval method on finding the decisive source, citation accuracy, stale-status
errors, latency and operating cost. Freeze the expected evidence before tuning retrieval against those questions.
No evaluation suite or prototype is implemented by this note.

A concrete existing case is [the NG full-source review](ng_3575861_full_review_20261030.md): retrieval should
surface Table8's later net-negative panel alongside the positive whole-sample headline. Better access to this
record could save repeated work; actual time/error reductions remain unmeasured.

## Workflow orchestration and remaining tools

LangGraph's persistence is relevant to interrupted work, but we already have source records, run histories,
reservations and continuation files. A framework can preserve state without validating it. Research gates must
remain deterministic, and retries must preserve prior trials, failures, ownership and exact artifact identities.
Only consider migration after identifying a specific failure the current approach cannot adequately handle.

The smaller near-term opportunity is selective review/testing/context tooling from the catalogs. Individual
tools need their own dependency, permissions, maintenance and evidence checks before use. This is not a request
for installations or a new safety bureaucracy. No new model/API account or subscription is needed for this review.

## Questions for Claude

1. What retrieval failures remain after using the current terminal and repository search properly?
2. What is the smallest improvement: metadata/status links, lexical ranking, semantic retrieval or none?
3. Which fixed examples would demonstrate incremental value without concealing stale or negative evidence?
4. Is any orchestration gap concrete enough to justify LangGraph's additional dependencies?

Recommendation: assess retrieval/status reconciliation first; keep framework adoption conditional on a demonstrated
need. No new strategy hypothesis, backtest, trading-performance claim or automatic task is created.
