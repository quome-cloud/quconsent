#!/usr/bin/env python3
# Copyright 2026 Quome. Licensed under the Apache License, Version 2.0.
"""Summarize ConsentBench results (paper 013) into figures + numbers.tex.

Reads results/013-consent/*.json (produced by the `consentrun` bench binary) and
writes figures to papers/013-consent/figs/, headline macros to
papers/013-consent/numbers.tex, and a markdown table to papers/013-consent/tables/.
Skips any experiment whose results file is absent (e.g. E1 still running).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = "results/013-consent"
FIGS = "papers/013-consent/figs"
TABLES = "papers/013-consent/tables"
NUMBERS = "papers/013-consent/numbers.tex"

NAVY, TEAL, AMBER, RED, GREY = "#1b2a4a", "#2a9d8f", "#e9c46a", "#c1432f", "#9aa0a6"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

macros = {}


def load(name):
    p = os.path.join(R, name)
    return json.load(open(p)) if os.path.exists(p) else None


def pct(x):
    return f"{100 * x:.1f}\\%"


# --- E1: live disclosure + out-of-scope action gap --------------------------
def fig_e1():
    d = load("e1_live.json")
    if not d:
        print("E1: results absent, skipping fig1")
        return
    disc = d["disclosure"]
    scope = d["scope"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.4))

    # Left: AI-disclosure rate, un-gated (spontaneous) vs gated.
    bars = [disc["ungated_rate"], disc["gated_rate"]]
    err = [
        [disc["ungated_rate"] - disc["ungated_ci"][0], disc["gated_rate"] - disc["gated_ci"][0]],
        [disc["ungated_ci"][1] - disc["ungated_rate"], disc["gated_ci"][1] - disc["gated_rate"]],
    ]
    ax1.bar(["un-gated\n(spontaneous)", "consent\nlayer"], bars, color=[RED, TEAL], width=0.6,
            yerr=err, error_kw={"ecolor": "#333", "capsize": 4})
    for i, v in enumerate(bars):
        ax1.text(i, v + 0.03, f"{100*v:.0f}%", ha="center", fontsize=10)
    ax1.set_ylim(0, 1.12)
    ax1.set_ylabel("AI-involvement disclosure rate")
    ax1.set_title("Disclosure (G2)")

    # Right: out-of-scope/withdrawn-consent action rate.
    vbars = [scope["ungated_violation_rate"], scope["gated_violation_rate"]]
    ax2.bar(["un-gated", "consent\nlayer"], vbars, color=[RED, TEAL], width=0.6)
    for i, v in enumerate(vbars):
        ax2.text(i, v + 0.03, f"{100*v:.0f}%", ha="center", fontsize=10)
    ax2.set_ylim(0, 1.12)
    ax2.set_ylabel("Out-of-scope action rate")
    ax2.set_title("Consent scope (G1)")
    fig.suptitle("E1 · The live gateway under-discloses and cannot gate consent", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "fig1_live_gap.png"), dpi=160)
    plt.close(fig)

    macros["EoneModel"] = d["model"].replace("_", "\\_").replace(":", ":")
    macros["EoneN"] = str(d["n_scored"])
    macros["EoneUngatedDisc"] = pct(disc["ungated_rate"])
    macros["EoneGatedDisc"] = pct(disc["gated_rate"])
    macros["EoneMcnemarFlip"] = str(disc["mcnemar_b_undisclosed_to_disclosed"])
    macros["EoneMcnemarP"] = fmt_p(disc["mcnemar_p"])
    macros["EoneViolUngated"] = pct(scope["ungated_violation_rate"])
    macros["EoneViolGated"] = pct(scope["gated_violation_rate"])
    macros["EoneViolCases"] = str(scope["violation_cases"])
    print(f"E1: spontaneous disclosure {100*disc['ungated_rate']:.1f}% -> 100%; "
          f"violations {100*scope['ungated_violation_rate']:.0f}% -> {100*scope['gated_violation_rate']:.0f}%")


def fmt_p(p):
    if p < 1e-4:
        return "<10^{-4}"
    if p < 1e-3:
        return "<0.001"
    return f"{p:.3f}"


# --- E2: consent-scope enforcement ------------------------------------------
def fig_e2():
    d = load("e2_enforcement.json")
    if not d:
        return
    g = d["gate"]
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    cats = ["CVP\n(violations stopped)", "FBR\n(in-scope blocked)"]
    vals = [g["cvp"], g["fbr"]]
    cis = [g["cvp_ci"], g["fbr_ci"]]
    err = [[vals[i] - cis[i][0] for i in range(2)], [cis[i][1] - vals[i] for i in range(2)]]
    ax.bar(cats, vals, color=[TEAL, AMBER], width=0.5,
           yerr=err, error_kw={"ecolor": "#333", "capsize": 4})
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f"{100*v:.1f}%", ha="center", fontsize=10)
    ax.axhline(0.05, ls="--", color=RED, lw=1, label="5% false-block target")
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Rate")
    ax.set_title("E2 · Consent-scope enforcement (G1)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "fig2_enforcement.png"), dpi=160)
    plt.close(fig)
    macros["EtwoCVP"] = pct(g["cvp"])
    macros["EtwoFBR"] = pct(g["fbr"])
    macros["EtwoViolTotal"] = str(g["viol_total"])
    macros["EtwoInscope"] = str(g["inscope_total"])
    print(f"E2: CVP {100*g['cvp']:.1f}%, FBR {100*g['fbr']:.1f}%")


# --- E3: disclosure coverage + latency --------------------------------------
def fig_e3():
    d = load("e3_disclosure.json")
    if not d:
        return
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    vals = [d["baseline_coverage"], d["gated_coverage"]]
    ax.bar(["bare output", "with attacher"], vals, color=[RED, TEAL], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f"{100*v:.0f}%", ha="center", fontsize=10)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Disclosure coverage")
    ax.set_title(f"E3 · Disclosure coverage ({d['attacher_latency_us']:.2f} µs/msg)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "fig3_disclosure.png"), dpi=160)
    plt.close(fig)
    macros["EthreeBaseCov"] = pct(d["baseline_coverage"])
    macros["EthreeGatedCov"] = pct(d["gated_coverage"])
    macros["EthreeLatencyUs"] = f"{d['attacher_latency_us']:.2f}"
    print(f"E3: coverage {100*d['baseline_coverage']:.0f}% -> {100*d['gated_coverage']:.0f}%")


# --- E4: competency gating --------------------------------------------------
def fig_e4():
    d = load("e4_competency.json")
    if not d:
        return
    by = d["by_action"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    names = list(by.keys())
    cgps = [by[k]["cgp"] for k in names]
    short = [n.replace("order_", "").replace("_", "\n") for n in names]
    ax.bar(short, cgps, color=TEAL, width=0.6)
    for i, v in enumerate(cgps):
        ax.text(i, v + 0.02, f"{100*v:.0f}%", ha="center", fontsize=10)
    ax.axhline(1.0, ls="--", color=GREY, lw=1)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Competency-gate prevention")
    ax.set_title(f"E4 · Competency gating by action class (friction {100*d['friction']:.1f}%)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "fig4_competency.png"), dpi=160)
    plt.close(fig)
    macros["EfourCGP"] = pct(d["cgp"])
    macros["EfourFriction"] = pct(d["friction"])
    macros["EfourShould"] = str(d["should_total"])
    print(f"E4: CGP {100*d['cgp']:.1f}%, friction {100*d['friction']:.1f}%")


# --- E5: goals-of-care detection vs false-block -----------------------------
def fig_e5():
    d = load("e5_goals.json")
    if not d:
        return
    sweep = d["sweep"]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    fprs = [s["fpr"] for s in sweep]
    tprs = [s["tpr"] for s in sweep]
    ax.plot(fprs, tprs, "-o", color=NAVY, lw=1.8, ms=3)
    op = d["operating_point_0_5"]
    ax.scatter([op["fpr"]], [op["tpr"]], s=110, color=RED, zorder=5, label="threshold 0.5")
    ax.plot([0, 1], [0, 1], ls=":", color=GREY, lw=1)
    ax.set_xlabel("False-block rate (FPR)")
    ax.set_ylabel("Conflict detection (TPR)")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title(f"E5 · Goals-of-care detection (κ={d['kappa_inter_rater']:.2f})")
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "fig5_goals.png"), dpi=160)
    plt.close(fig)
    macros["EfiveTPR"] = pct(op["tpr"])
    macros["EfiveFPR"] = pct(op["fpr"])
    macros["EfiveKappa"] = f"{d['kappa_inter_rater']:.2f}"
    macros["EfiveN"] = str(d["n"])
    print(f"E5: TPR {100*op['tpr']:.0f}% @ FPR {100*op['fpr']:.0f}%, kappa {d['kappa_inter_rater']:.2f}")


# --- E6: overhead -----------------------------------------------------------
def num_e6():
    d = load("e6_overhead.json")
    if not d:
        return
    macros["EsixPerDecisionUs"] = f"{d['per_decision_us']:.3f}"
    macros["EsixThroughput"] = f"{d['throughput_per_s']/1e6:.1f}M"
    macros["EsixDecisions"] = f"{d['decisions']:,}".replace(",", "{,}")
    print(f"E6: {d['per_decision_us']:.3f} us/decision")


def write_table():
    parts = []
    e2 = load("e2_enforcement.json")
    e4 = load("e4_competency.json")
    if e2:
        g = e2["gate"]
        parts.append(f"| G1 consent scope | {100*g['cvp']:.1f}% | {100*g['fbr']:.1f}% |")
    if e4:
        parts.append(f"| G3 competency | {100*e4['cgp']:.1f}% | {100*e4['friction']:.1f}% |")
    if parts:
        os.makedirs(TABLES, exist_ok=True)
        lines = ["| control | prevention | false-block / friction |", "|---|---|---|"] + parts
        open(os.path.join(TABLES, "controls.md"), "w").write("\n".join(lines) + "\n")


def write_numbers():
    os.makedirs(os.path.dirname(NUMBERS), exist_ok=True)
    with open(NUMBERS, "w") as f:
        f.write("% Auto-generated by scripts/013-consent/summarize.py — do not edit.\n")
        f.write("% Core macros are \\providecommand'd in main.tex; override here.\n")
        for k, v in macros.items():
            f.write(f"\\renewcommand{{\\{k}}}{{{v}}}\n")
    print(f"wrote {NUMBERS} ({len(macros)} macros)")


def main():
    for d in (FIGS, TABLES):
        os.makedirs(d, exist_ok=True)
    fig_e1()
    fig_e2()
    fig_e3()
    fig_e4()
    fig_e5()
    num_e6()
    write_table()
    write_numbers()


if __name__ == "__main__":
    main()
