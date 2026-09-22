# The Price of a Design Parameter

## Bank Valuations in the Digital Euro Legislative Process

**Philip Kroos — September 2026**

[**Read the paper (PDF)**](paper/main.pdf) · [**One-page abstract**](paper/abstract.pdf) · [**Replication guide**](REPLICATION.md)

---

## Research question

**Do financial markets price the exact policy parameters that determine who gains and loses from a central bank digital currency?**

The digital euro is a useful laboratory because its economic incidence depends on concrete design choices: the holding limit determines the scope for deposit substitution, fee caps affect payment providers, and device-access rules affect platform gatekeepers. Between 2023 and 2026 these parameters moved through a visible legislative process, creating a sequence of dated policy events.

This paper combines those events with bank-level deposit exposure and equity-market reactions to ask whether the market valued the **design of the digital euro**, rather than simply news that the project existed.

---

## Findings at a glance

| Question | Evidence |
|---|---|
| Do more deposit-funded banks react more to bank-friendly digital-euro news? | **Only weakly.** The pre-specified estimate is **+0.051 pp per 1 SD of deposit exposure**; permutation *p* = **0.47**. |
| Does publication timing matter? | A conservative release-time alignment raises the estimate to roughly **+0.15 to +0.17 pp**. This is evidence of a small effect, but it is inference-sensitive and still economically modest. |
| What happens on events that actually set or signal a design parameter? | **No detectable valuation effect.** The design-only estimate is **−0.004 pp**, with a 95% interval of about **[−0.22, +0.21]**. |
| Can the design detect a large effect when one exists? | **Yes.** On the October 2020 Eurosystem-report day, strictly pre-event specifications produce a slope of about **+0.77 to +0.82 pp per SD**. |
| Were the design choices politically important? | **Yes.** The legislative transparency record contains **309 disclosed meetings** with banks, payment firms, retailers, technology firms and other stakeholders. |

> **Main takeaway:** markets appear to have reacted much more strongly to early news about whether a digital euro would exist than to the later legislative details of how it would be designed.

---

## Early project news vs. later design news

The figure below puts the central result in one picture. The left side shows the early 2020–2021 phase; the right side shows the 2023–2026 legislative phase. Points are exposure slopes signed so that a positive value agrees with the model prediction.

![Early project news versus later legislative design](assets/fig_event_slopes_all.jpg)

*Early project-existence news produced a much larger cross-sectional response than the later legislative design events. Red squares mark design-parameter events; black circles mark implementation/project events.*

The October 2020 Eurosystem report generates a response close to the magnitude documented in the earlier literature. By contrast, later parameter-setting events are smaller, mixed in sign, and jointly indistinguishable from zero.

---

## Identification

The main bank specification is:

**CAR(i,e) = firm FE + event FE + θ × Exposure(i) × Direction(e) + error.**

The identifying comparison is therefore **within the same event day**: does a bank with a larger pre-determined deposit exposure react more strongly when an event changes the digital-euro design in a bank-friendly or bank-unfriendly direction?

- **Events:** 22 event dates in the main estimation sample, constructed from European Parliament, Council and ECB documents.
- **Bank sample:** 29 euro-area banks in the continuous-exposure analysis, plus non-euro banks for comparison and placebo exercises.
- **Exposure:** pre-proposal bank deposit exposure from EBA supervisory data.
- **Outcome:** event-day abnormal equity returns.
- **Fixed effects:** firm and event fixed effects.
- **Inference:** leave-one-firm-out jackknife standard errors, exposure-permutation inference and null-imposed wild-cluster bootstrap checks.
- **Timing:** one-day baseline, wider windows and a conservative release-time-aligned specification.
- **Positive control:** the same design is extended back to 2020–2021 using predetermined 2019 exposure and strictly pre-event factor loadings.

Event fixed effects absorb news common to all firms on a date. The coefficient is identified from whether firms with different exposure react differently **to the same event**.

---

## Political contestation

The market response is modest, but the design parameters were not politically irrelevant. I transcribe the published transparency record for the digital-euro procedure: **309 disclosed meetings** between legislators and interest representatives.

![Negotiation record for the digital euro](assets/fig_lobby.jpg)

*Panel A shows who met the negotiators over time. Panel B shows the number of disclosed meetings in the 30 days before key events.*

Banks and banking associations account for the largest private-interest category. Payment providers, retailers, consumer organisations and large technology firms also appear repeatedly. I use this record **descriptively**, not as an instrument or source of exogenous variation: lobbying intensity is itself endogenous to expected exposure.

---

## What the result means

The paper does **not** claim that digital-euro design has literally zero value. The evidence supports a narrower conclusion:

- the pre-specified estimate is small and imprecise;
- the release-time specification allows a somewhat larger, but still modest, response;
- the cleanest design-parameter subset shows no detectable effect;
- effects of the size observed around the major 2020 project announcement are inconsistent with the later legislative evidence.

The result is therefore a **bounded null**: the later design process does not appear to have generated valuation effects remotely as large as the early project-existence news.

---

## Data

The analysis combines four public-data components:

| Component | Main use |
|---|---|
| European Parliament / Council / ECB documents | Event dates and coded design direction |
| EBA supervisory data | Predetermined bank deposit exposure |
| Daily equity prices and factor returns | Abnormal returns around events |
| European Parliament transparency records | 309-meeting negotiation dataset |

The repository also contains the 2019 bank-exposure measure used for the 2020–2021 extension, event-timing data, placebo samples and stored robustness outputs.

---

## Pre-specification and transparency

The project was **pre-specified, not externally pre-registered**.

The event coding and firm universe were frozen before any return was computed. The bank-exposure definition was frozen before the first estimate using it, and the early-event coding and historical exposure were frozen before the corresponding early-period estimates.

- [Frozen analysis-plan snapshot](docs/pap_v1.md)
- [Hashes and timestamps](docs/coding_freeze.sha256)
- [Later project history](docs/pap_history.md)
- [Documented deviations](docs/deviations.md)

Post-specification analyses are reported alongside, rather than in place of, the pre-specified estimate.

---

## Repository structure

~~~text
.
├── paper/          paper and one-page abstract
├── data/
│   ├── hand/       event coding, timing, firm universe, lobbying record
│   ├── raw/        archived source inputs
│   └── derived/    analysis-ready exposure and return data
├── src/            event-study, exposure, inference and robustness code
├── output/         stored estimation outputs
├── docs/           pre-specification, hashes and deviations
├── tests/          unit tests
├── run_all.py      core replication entry point
└── REPLICATION.md  detailed reproduction guide
~~~

---

## Reproduction

Create a Python environment and run:

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
python -m pytest -q
~~~

See [**REPLICATION.md**](REPLICATION.md) for the exact script map and the additional raw ECB rate input required to rerun one post-review euro-excess-return robustness exercise.

---

## Paper

**Kroos, Philip (2026).**  
*The Price of a Design Parameter: Bank Valuations in the Digital Euro Legislative Process.*

[**Download the full paper**](paper/main.pdf)

---

## Citation

Machine-readable citation metadata are available in [CITATION.cff](CITATION.cff).

If you use the paper, event list or negotiation dataset, please cite the paper and link to this repository.
