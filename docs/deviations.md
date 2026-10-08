# Departures from the pre-specified plan

Mirrors Table 11 of the paper. The dated record of each decision is in the addenda (Nachträge) of `docs/pap_history.md`; `docs/pap_v1.md` is the frozen plan.

| Planned | Implemented | Reason | Decided |
|---|---|---|---|
| Three-factor model for all firms | Market model on the S&P 500 for US-listed firms | European factors are not a benchmark for US equities | Before any abnormal return |
| Falsification test assigning the bank direction to non-euro banks (binary design) | Replaced by placebo dates | Collinear with event fixed effects in the binary design | After first estimation |
| F4: placebo dates from the same weeks as the events | Placebo dates from non-event trading days since January 2023, at least ten trading days from any event | Same-week days fall inside the exclusion band of the first stage and overlap the event windows | After first estimation |
| Continuous provider exposure (euro area revenue share) | Group indicator | Segment revenue data not assembled | Before estimation |
| Market-power split (deposit concentration) | Not implemented | Concentration data not assembled | Before estimation |
| Provider-role split (distributing vs acquiring) | Not implemented | Provider-level role and revenue data not assembled | Before estimation |
| Within-group test: selected vs non-selected pilot providers | Not implemented | Usable firm-level list of selected providers not available | Before estimation |
| Coding of the February 2024 draft and amendments as zero | Additionally excluded in a no-look-ahead specification | Original coding relied partly on the later fate of the draft | After review |
| Pooled design and implementation events | Additionally separated | Title question concerns design events | After review |
| One-day window with documented event days | Additionally release-time aligned | Publication time undocumented for 11 events (13 in an earlier version) | After review |
| Draft report dated by its document, 3 November 2025 | Additionally dated by its first press report, 31 October 2025; ECB release of 30 October 2025 timed during trading | Content reported after the close on 30 October (Bloomberg, 21:12 UTC); ECB release carried by news services by midday | After review, after the earlier result was known |
| Exposure measured in 2023 for all events | December 2019 exposure for the 2020–21 events | 2023 measure not predetermined for early events | After review, before estimation |
| Pre-specified first stage mixes local-currency returns with dollar factors | Additionally, a euro market factor with FF size and value, and a euro market model in excess returns | Fama–French European factors are computed in US dollars | After review |
| Two-day windows summed over available days | Windows require a return on every day | Coding error; two-day results recomputed | After review |
| Four-factor model with a European banks index | Not estimated | Index series could not be obtained | Before estimation |
| Romano–Wolf with permutation draws | Romano–Wolf with placebo-date draws | Permutation within a binary group is degenerate | After first estimation |
