# Steel fabricator - waste visibility & remnant reuse (FDE case study prototype)

Small, synthetic-data prototypes backing the case study. **No client data or client notes are in this repo.**

| File | What it shows |
|---|---|
| `prototype/remnant_matcher.py` | 2D plates: checking offcut stock before buying fresh plate. Sensitivity to how accurate the stock records are. |
| `prototype/profile_matcher.py` | 1D profiles (beams/columns): same idea for cut-length offcuts. |
| `prototype/benchmark.py` | The evaluation harness we would run on real data: paired manual-vs-auto yield comparison with a pre-agreed GO / EXTEND / STOP rule. |
| `prototype/packer.py` | Deliberately simple shelf packer. Not a production nester. |
| `docs/prototype_output.txt` | Output of the three scripts. |

Run: `cd prototype && python3 remnant_matcher.py && python3 profile_matcher.py && python3 benchmark.py` (Python 3, no dependencies).

## What this proves, and what it does not
- **Proves:** the reuse logic works mechanically, and the saving collapses as stock-record accuracy falls (synthetic: ~13% -> ~9% -> ~4% fewer fresh plate tonnes at 100% / 70% / 40% accuracy). That is why the pilot audits physical offcuts before trusting the digital stock.
- **Also shows:** a greedy matcher can occasionally make things worse (negative minimum in some runs) by fragmenting the remaining parts. That is why a nester signs off every proposal and why we measure outcomes, not just matches.
- **Does not prove:** any real saving for the client. Stock sizes, part mix and the packer are invented. The `benchmark.py` demo compares two toy packers only to show the harness runs; it says nothing about the client's nesting team.
