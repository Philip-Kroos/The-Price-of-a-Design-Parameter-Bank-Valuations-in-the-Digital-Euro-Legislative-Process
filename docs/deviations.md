# Deviations from the pre-specified plan

This file mirrors the deviations reported in Appendix E / Table 11 of the paper. The frozen plan itself is preserved in `pap_v1.md`; later chronological notes are in `pap_history.md`.

| Planned | Implemented | Reason | Decision timing |
|---|---|---|---|
| Three-factor model for all firms | S&P 500 market model for US-listed firms | European factors are not an appropriate benchmark for US equities | Before any abnormal return |
| Binary falsification assigning bank direction to non-euro banks | Replaced by placebo dates | Collinear with event fixed effects in the binary design | After first estimation |
| Continuous provider exposure (euro-area revenue share) | Group indicator | Segment revenue data not assembled | Before estimation |
| Market-power split using deposit concentration | Not implemented | Concentration data not assembled | Before estimation |
| Provider-role split (distributing vs acquiring) | Not implemented | Provider-level role and revenue data not assembled | Before estimation |
| Selected vs non-selected pilot providers | Not implemented | Usable firm-level list of selected providers not available | Before estimation |
| February 2024 draft and amendments coded zero | Also excluded in a no-look-ahead specification | Original coding relied partly on the later fate of the draft | After review |
| Pooled design and implementation events | Also separated | The title question concerns design events | After review |
| One-day window on documented event dates | Also release-time aligned | Publication time undocumented for 13 events | After review |
| 2023 exposure for all events | December 2019 exposure for the 2020–21 extension | 2023 exposure is not predetermined for early events | After review, before estimation |
| Pre-specified first stage uses local-currency returns with USD European factors | Added EUR-market-factor and fully euro-denominated excess-return checks | Fama–French Europe factors are computed in US dollars | After review |
| Two-day windows summed over available days | Require a return on every day in the window | Coding error; two-day results recomputed | After review |
| Four-factor model with a European banks index | Not estimated | Index series could not be obtained | Before estimation |
| Romano–Wolf adjustment using permutation draws | Placebo-date draws | Permutation within a binary group is degenerate | After first estimation |
