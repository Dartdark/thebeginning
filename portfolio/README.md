# Systematic futures research: a work sample

I'm an independent trader building a systematic research process for CME futures (equity index, energy, metals, rates,
FX), run live on prop-firm evaluation accounts. I direct the research and review; AI coding agents write most of the
implementation. This sample shows how I decide whether a result is real.

It follows the three pieces of evidence a quant firm can actually check:

| | What | File |
|---|---|---|
| **Replication** | A published overnight-return effect, rebuilt with realistic costs and judged on data the rule never saw. Verdict: real in 2017-22, gone since 2024. | [`replication/`](replication/) |
| **Failure log** | Ideas that didn't work and exactly why, including the mistakes in my own process. | [`FAILURE_LOG.md`](FAILURE_LOG.md) |
| **One system** | The research loop: queue → pre-registration → staged gates → ledger, with the rules enforced in code. | [`SYSTEM.md`](SYSTEM.md) |

**How I filter ideas before testing:** *who is paying, and why do they keep paying?* Every idea must name its source:
risk premium, behavioral, structural (someone forced to trade at a bad price), or information/speed. "No one I can name"
is noise and isn't tested.

**What isn't here:** the strategies I trade, and the market data (vendor licence). The replication script runs on any
1-minute NQ CSV and includes a synthetic self-test.

Contact: (add)
