> **Paper 013 proposal — Consent, disclosure & participatory governance.** Imported 2026-06-07 from the local
> outline `P12` (`ongoing-papers/papers/12-consent-disclosure-governance/`). Read with the
> [`ROADMAP.md`](../ROADMAP.md) deltas in mind: **monorepo** — features are `qfire`
> modules, not `haarf-*` crates or spin-out repos — and **confidential-enclave**
> production deployment, validated locally on Ollama via the OpenAI-compatible
> bridge. The threat model, hypotheses, experiments, datasets, and figures below
> are the pre-registered working plan; they are reconciled against the gateway as
> built at the feature-spec (stage 2) and paper-spec (stage 4) gates.

---

# Paper 12 — Consent, Disclosure & Participatory Governance for Clinical AI Agents

**Crate:** `haarf-consent` · **New dataset:** HAARF-Consent · **Covers:** C4.1, C4.5, C4.6, C4.9, C5.6 · **Status:** outline

## Abstract

HAARF's human-oversight category includes the *patient-facing and ethical* controls that
no harness addresses: patient/public participation in governance (C4.1), clinical
competency/training (C4.5), patient communication & informed consent (C4.6), and ethics
/ patient-centered-care preservation (C4.9). These are not "soft" — an agent action taken
without required consent, or without disclosing AI involvement, is a compliance and
ethical violation regardless of clinical correctness. We build `haarf-consent`, a
consent- and disclosure-aware enforcement layer that gates agent actions on the patient's
recorded consent scope, attaches AI-involvement disclosure to outputs, and records
operator competency attestations. We contribute **HAARF-Consent**, a FHIR-based consent
policy + scenario corpus, and measure consent-violation prevention vs. workflow friction.

## Stakeholders & expert-in-the-loop

This patient-facing work must be co-designed with experts-in-the-loop so the consent,
disclosure, and ethics controls stay clinically grounded, legally sound, and credible to
the patients they govern.

- **Bioethicist / clinical-ethics expert** — defines what counts as an ethics or
  patient-centeredness breach (G4) and adjudicates value-conflict edge cases.
- **Patient advocate / community representative** — supplies the lived-experience voice on
  consent expectations and disclosure that makes this patient-facing paper legitimate.
- **IRB / research-ethics & informed-consent specialist** — validates the consent-scope
  model and scenario ground truth against real informed-consent standards (C4.6).
- **Health-literacy / patient-communication expert** — ensures AI-involvement disclosure
  strings are comprehensible to patients, not just technically complete.
- **Health-law counsel (consent & disclosure)** — maps statutory consent and
  disclosure obligations (HIPAA/GDPR) onto the FHIR Consent policy corpus.
- **Frontline clinician (consent at point of care)** — grounds where consent is captured,
  checked, and broken in real workflows, and tunes acceptable false-block friction.
- **Patient-and-public-involvement (PPI) / governance lead** — designs and records the
  participatory-governance trail (C4.1) so affected patients have genuine input.
- **Clinical credentialing / competency officer** — defines which actions require a
  credentialed operator and the attestation schema that gates them (C4.5, C5.6).

## Problem model

- **G1 Consent-scope violation** — agent performs an action (data use, contact,
  treatment recommendation) outside the patient's recorded consent.
- **G2 Non-disclosure** — AI involvement in a clinical decision/communication is not
  disclosed to the patient/clinician (C4.6).
- **G3 Competency gap** — an action requiring a credentialed/ trained human in the loop
  is taken with an unqualified (or no) operator (C4.5).
- **G4 Ethics/patient-centeredness breach** — action conflicts with documented patient
  values/goals-of-care (C4.9).
- **G5 No participatory governance trail** — no record that affected
  patients/public had input into the agent's deployment (C4.1).

## Research questions

- **RQ1** Can consent scope be represented machine-readably (FHIR Consent) and enforced
  at action time with full prevention of G1?
- **RQ2** Does automatic disclosure attachment achieve complete, auditable AI-disclosure
  (G2) without harming clinician workflow?
- **RQ3** Can competency attestations gate credentialed actions (G3) and integrate with
  the Paper-6 escalation routing?
- **RQ4** How are goals-of-care / values encoded and checked (G4) — and what is the
  false-block cost?

## Hypotheses

- **H1** FHIR-Consent-driven gating prevents 100% of G1 scope violations on
  HAARF-Consent with ≤ 5% false-blocks on in-scope actions.
- **H2** Automatic disclosure yields 100% disclosure coverage with negligible workflow
  latency.
- **H3** Competency gating prevents G3 with ≤ X% legitimate-action friction.
- **H4** Goals-of-care checks catch G4 conflicts at a quantified, clinician-tunable
  false-block rate.

## Experiments → figures

- **E1 Consent enforcement (→ Fig 1):** G1 prevention vs. false-block across consent
  scenarios; {no gate, gate}.
- **E2 Disclosure coverage (→ Fig 2):** disclosure completeness + latency overhead.
- **E3 Competency gating (→ Fig 3):** G3 prevention vs. friction by action class.
- **E4 Goals-of-care (→ Fig 4):** G4 conflict detection vs. false-block; clinician
  threshold sweep.
- **E5 Gateway overhead (→ shared Fig).**

## Datasets

**Public:**
- **HL7 FHIR Consent** resource + examples — the consent representation standard.
- **Synthea** — patients with synthetic consent directives + goals-of-care.
- HIPAA/GDPR consent requirement texts and **MIMIC** consent/access structures
  (methodology grounding).

**New — HAARF-Consent (the contribution):**
- A FHIR-based **consent policy corpus** (data-use, contact, treatment, research scopes)
  + synthetic patient consent directives and goals-of-care/values records.
- A **scenario suite**: agent actions that are in-scope, out-of-scope (G1), require
  disclosure (G2), require credentialed operators (G3), or conflict with values (G4),
  each with ground-truth expected gateway behavior.
- A **disclosure-string spec** and **competency-attestation schema**. Apache-2.0,
  synthetic.

## Validation & statistics

- Prevention / false-block rates with 95% Wilson CIs; paired comparison vs. no-gate.
- Disclosure coverage as exact completeness; latency via the load harness.
- Goals-of-care detection validated against clinician-labeled conflicts (multi-rater κ).
- **Threats to validity:** values/goals encoding is inherently lossy (stated; human
  review remains the backstop via Paper 6); consent law varies by jurisdiction (link
  Paper 8 harmonization).

## Rust components (`haarf-consent`)

- **Consent engine:** loads FHIR Consent; resolves whether a given action+data-use is
  in the patient's consent scope (expressible via `haarf-policy`).
- **Disclosure attacher:** stamps AI-involvement disclosure onto agent outputs/
  communications; records disclosure in the audit chain (Paper 2) → C4.6.
- **Competency gate:** verifies a credentialed operator attestation is present for
  credentialed actions; otherwise `Escalate` (Paper 6) → C4.5, C5.6.
- **Goals-of-care checker:** flags actions conflicting with recorded values → C4.9.
- **Governance ledger:** append-only record of participatory-governance inputs (C4.1)
  anchored in the audit chain.

## Server / proxy design

- Consent + competency run as enforcing layers after identity/policy; disclosure runs on
  the *output* path.
- All consent decisions, disclosures, and competency attestations are audited (Paper 2)
  for the patient-facing accountability trail.
- Consent scope can flip an action to `Escalate` (broken/expired consent ⇒ human),
  never silent-allow.

## Metrics

| Metric | Definition | Target |
|---|---|---|
| CVP | Consent-violation prevention (G1) | 100% |
| DSC | Disclosure coverage (G2) | 100% |
| CGP | Competency-gate prevention (G3) | ≥ target |
| GoC | Goals-of-care conflict detection (G4) | report |
| FBR | In-scope false-block rate | ≤ 5% |

## Repo scaffold

```
haarf-consent/
├── crates/haarf-consent/           # consent engine + disclosure + competency + GoC + ledger
├── dataset/haarf-consent/          # FHIR consent corpus + scenarios + schemas
├── figures/
└── paper/
```
