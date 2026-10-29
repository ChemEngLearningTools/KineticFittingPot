from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #050505;
            --panel: #111214;
            --panel2: #17191c;
            --text: #f4f4f5;
            --muted: #a8adb4;
            --line: #2a2d33;
            --accent: #14b8a6;
            --accent2: #22d3ee;
            --warn: #f59e0b;
            --good: #22c55e;
            --bad: #ef4444;
        }
        .stApp { background: var(--bg); color: var(--text); }
        header[data-testid="stHeader"], div[data-testid="stToolbar"], #MainMenu, footer {
            visibility: hidden !important; height: 0 !important;
        }
        section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        .block-container {
            padding-top: 1.0rem !important;
            padding-bottom: 3.0rem !important;
            max-width: 1500px;
        }
        h1,h2,h3,h4 { color: var(--text) !important; letter-spacing: -0.02em; }

        /* KineticFittingPot Home ------------------------------------------------ */
        .reactionpot-hero {
            max-width: 1180px;
            min-height: 245px;
            margin: 0.2rem auto 1.3rem auto;
            padding: 1.65rem 2.0rem;
            border: 1px solid #164e4a;
            border-radius: 28px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
            background:
                radial-gradient(circle at 7% 10%, rgba(20,184,166,.28), transparent 33%),
                radial-gradient(circle at 90% 15%, rgba(56,189,248,.14), transparent 35%),
                linear-gradient(135deg, #0a0b0e 0%, #111417 62%, #050505 100%);
            box-shadow: 0 18px 55px rgba(0,0,0,.42);
        }
        .reactionpot-logo {
            color: #5eead4 !important;
            font-size: 4.0rem;
            font-weight: 940;
            line-height: .96;
            letter-spacing: -.06em;
            text-shadow: 0 0 28px rgba(20,184,166,.20);
        }
        .reactionpot-subtitle {
            margin-top: .62rem;
            color: #f8fafc !important;
            font-size: 1.17rem;
            font-weight: 760;
            letter-spacing: -.02em;
        }
        .reactionpot-capability-line {
            margin-top: 1.08rem;
            color: #94a3b8 !important;
            font-size: .97rem;
            line-height: 1.5;
            font-weight: 700;
            letter-spacing: .015em;
        }
        .home-section-heading {
            max-width: 1180px;
            margin: .35rem auto .2rem auto;
            color: #f8fafc !important;
            font-size: 1.04rem;
            font-weight: 900;
        }
        .home-section-copy {
            max-width: 1180px;
            margin: 0 auto .62rem auto;
            color: #94a3b8 !important;
            font-size: .86rem;
            line-height: 1.35;
        }
        .home-active-section {
            max-width: 1180px;
            margin: .9rem auto .6rem auto;
            color: #67e8f9 !important;
            font-size: .80rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .11em;
        }
        .home-metric-wrap {
            max-width: 1180px;
            margin: 0 auto .55rem auto;
        }
        .home-metric-grid {
            max-width: 1180px;
            margin: 0 auto .65rem auto;
            display: grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap: .62rem;
        }
        .home-mini-metric {
            border: 1px solid #293039;
            border-radius: 16px;
            padding: .72rem .85rem;
            background: linear-gradient(180deg,#121419 0%,#0d0f12 100%);
        }
        .home-mini-label { color:#8f98a5 !important; font-size:.76rem; font-weight:760; }
        .home-mini-value { color:#f8fafc !important; font-size:1.32rem; font-weight:900; margin-top:.08rem; }
        .home-mini-note { color:#7f8b99 !important; font-size:.70rem; margin-top:.08rem; }
        div[data-testid="stRadio"] div[role="radiogroup"] {
            flex-wrap: wrap !important;
            gap: .35rem .55rem !important;
        }

        .stack-card-link {
            display: block;
            max-width: 1180px;
            margin: 0 auto .78rem auto;
            text-decoration: none !important;
            color: inherit !important;
        }
        .stack-card {
            --card-accent: #14b8a6;
            min-height: 126px;
            border: 1px solid color-mix(in srgb, var(--card-accent) 48%, #263041);
            border-radius: 23px;
            padding: 1.08rem 1.28rem;
            background:
                radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--card-accent) 26%, transparent) 0%, transparent 44%),
                linear-gradient(135deg, #121419 0%, #0b0c0f 100%);
            box-shadow: 0 14px 34px rgba(0,0,0,.28);
            transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease, background 150ms ease;
            cursor: pointer;
        }
        .stack-card:hover {
            transform: translateY(-3px);
            border-color: var(--card-accent);
            box-shadow: 0 18px 45px rgba(0,0,0,.38), 0 0 0 1px color-mix(in srgb, var(--card-accent) 30%, transparent);
            background:
                radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--card-accent) 34%, transparent) 0%, transparent 47%),
                linear-gradient(135deg, #15171c 0%, #0b0c0f 100%);
        }
        .stack-kicker {
            color: var(--card-accent) !important;
            font-size: .76rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .11em;
            margin-bottom: .25rem;
        }
        .stack-title {
            color: #f8fafc !important;
            font-size: 1.48rem;
            font-weight: 900;
            line-height: 1.08;
            letter-spacing: -.025em;
        }
        .stack-desc {
            color: #cbd5e1 !important;
            font-size: .94rem;
            line-height: 1.38;
            margin-top: .36rem;
            max-width: 1040px;
        }
        .stack-open {
            color: var(--card-accent) !important;
            font-size: .77rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .09em;
            margin-top: .72rem;
        }
        .stack-card-planned { opacity: .92; }
        .stack-card-locked {
            opacity: .88;
            border-style: dashed;
            filter: saturate(.72);
        }
        .stack-card-locked .stack-open { color:#fbbf24 !important; }

        /* Shared workspace presentation ---------------------------------- */
        .workspace-breadcrumb {
            color: #8ca0b5 !important;
            font-size: .82rem;
            font-weight: 700;
            margin: .25rem 0 .55rem 0;
        }
        .workspace-title-card {
            --workspace-accent: #14b8a6;
            margin: 0 0 1.2rem 0;
            padding: 1.05rem 1.3rem;
            border: 1px solid color-mix(in srgb, var(--workspace-accent) 48%, #263041);
            border-radius: 22px;
            background:
                radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--workspace-accent) 23%, transparent) 0%, transparent 42%),
                linear-gradient(135deg, #111214 0%, #0b0c0f 100%);
            box-shadow: 0 14px 34px rgba(0,0,0,.28);
        }
        .workspace-title {
            color: #f8fafc !important;
            font-size: 1.76rem;
            font-weight: 920;
            line-height: 1.06;
            letter-spacing: -.025em;
        }
        .workspace-desc {
            color: #cbd5e1 !important;
            font-size: .98rem;
            line-height: 1.4;
            margin-top: .38rem;
            max-width: 1120px;
        }

        .metric-card {
            background: linear-gradient(180deg,#15171b 0%,#0f1012 100%);
            border:1px solid var(--line);
            border-radius:18px;
            padding:1.05rem 1.2rem;
            min-height:108px;
            box-shadow:0 8px 22px rgba(0,0,0,.35);
        }
        .metric-label { color:var(--muted); font-size:.91rem; margin-bottom:.22rem; }
        .metric-value { color:var(--text); font-size:1.43rem; line-height:1.17; font-weight:850; overflow-wrap:anywhere; }
        .metric-card-compact .metric-value { font-size:1.43rem; line-height:1.14; }
        .metric-note { color:#8f98a5; font-size:.79rem; margin-top:.15rem; }
        .panel { background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:1.2rem 1.35rem; box-shadow:0 8px 22px rgba(0,0,0,.26); margin-bottom:1rem; }
        .soft-panel { background:#0c0d0f; border:1px solid #23262b; border-radius:14px; padding:1rem 1.15rem; margin:.6rem 0; }
        .question-box { background:linear-gradient(180deg,#12161a,#0d0f12); border:1px solid #2b343d; border-left:4px solid var(--accent); border-radius:16px; padding:1.25rem 1.4rem; font-size:1.06rem; line-height:1.62; }
        .solution-step { background:#0d1013; border:1px solid #282d33; border-radius:14px; padding:.9rem 1rem; margin:.55rem 0; }
        .step-title { color:#86efdf; font-weight:700; font-size:.94rem; margin-bottom:.25rem; }
        .chip { display:inline-block; padding:.22rem .58rem; margin:.12rem .18rem .12rem 0; border-radius:999px; background:#10221f; border:1px solid #1f5b52; color:#a7f3d0 !important; font-size:.82rem; }
        .chip-blue { background:#10202a; border-color:#22576d; color:#bae6fd !important; }
        .chip-warn { background:#2a1f0d; border-color:#6b4b14; color:#fde68a !important; }
        .section-kicker { color:#6ee7d8; font-size:.78rem; text-transform:uppercase; letter-spacing:.13em; font-weight:800; }
        .muted { color:var(--muted) !important; }
        .small { font-size:.83rem; }
        div.stButton > button, div.stDownloadButton > button { border-radius:12px; border:1px solid #2c5c58; background:#102421; color:#ecfdf5; }
        div.stButton > button:hover, div.stDownloadButton > button:hover { border-color:#14b8a6; color:white; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
        div[data-testid="stMetric"] { background:#111214; border:1px solid #2a2d33; padding:.75rem .9rem; border-radius:14px; }
        div[data-testid="stExpander"] { border:1px solid #292c31; border-radius:12px; background:#0d0e10; }
        hr { border-color:#272a2f !important; }

        /* Engineering notation / worked-solution presentation ------------ */
        .engineering-text { font-variant-numeric: lining-nums tabular-nums; }
        .engineering-text sub, .eng-data-table sub, .final-answer-grid sub, .rubric-table sub {
            font-size: .72em; line-height: 0; vertical-align: -0.28em;
        }
        .engineering-text sup, .eng-data-table sup, .final-answer-grid sup, .rubric-table sup {
            font-size: .72em; line-height: 0; vertical-align: .48em;
        }
        .eng-data-group-title {
            color:#7dd3fc !important; font-size:.82rem; font-weight:850;
            letter-spacing:.08em; text-transform:uppercase; margin:.95rem 0 .32rem 0;
        }
        .eng-data-table {
            width:100%; border-collapse:separate; border-spacing:0; margin:0 0 .7rem 0;
            background:#0d1013; border:1px solid #283038; border-radius:14px; overflow:hidden;
        }
        .eng-data-table td { padding:.72rem .9rem; border-bottom:1px solid #232a31; vertical-align:top; }
        .eng-data-table tr:last-child td { border-bottom:none; }
        .eng-data-label { width:34%; color:#aab4c0 !important; font-weight:720; }
        .eng-data-value { color:#f3f4f6 !important; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; line-height:1.55; }
        .data-note { color:#8f98a5 !important; font-family:inherit; font-size:.78rem; margin-top:.12rem; }
        .eng-exp-table-wrap { overflow-x:auto; margin:0 0 .75rem 0; border:1px solid #283038; border-radius:14px; }
        .eng-exp-table { width:100%; border-collapse:collapse; background:#0d1013; font-variant-numeric:tabular-nums; }
        .eng-exp-table th, .eng-exp-table td { padding:.62rem .78rem; border-bottom:1px solid #232a31; text-align:right; }
        .eng-exp-table th { background:#11161a; color:#7dd3fc !important; font-size:.78rem; font-weight:820; }
        .eng-exp-table td { color:#e5e7eb !important; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
        .eng-exp-table tr:last-child td { border-bottom:none; }
        .assumption-row {
            display:grid; grid-template-columns:34px 1fr; gap:.65rem; align-items:start;
            background:#0d1013; border:1px solid #282d33; border-radius:12px; padding:.72rem .82rem; margin:.42rem 0;
        }
        .assumption-number {
            width:27px; height:27px; border-radius:999px; display:flex; align-items:center; justify-content:center;
            background:#102d29; border:1px solid #256a61; color:#99f6e4 !important; font-weight:850; font-size:.78rem;
        }
        .assumption-text { color:#e5e7eb !important; line-height:1.52; }
        .step-body { color:#e5e7eb !important; line-height:1.68; font-size:1.0rem; }
        .solution-step { border-left:3px solid #1f766d; }
        .final-answer-grid {
            display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.72rem; margin:.35rem 0 .7rem 0;
        }
        .final-answer-card {
            background:radial-gradient(circle at 10% 10%,rgba(20,184,166,.20),transparent 42%),linear-gradient(180deg,#11171a,#0c0f11);
            border:1px solid #24665e; border-radius:16px; padding:1rem 1.1rem; box-shadow:0 10px 28px rgba(0,0,0,.28);
        }
        .final-answer-label { color:#8ddfd4 !important; font-size:.78rem; font-weight:820; text-transform:uppercase; letter-spacing:.06em; }
        .final-answer-value { color:#ffffff !important; font-size:1.42rem; font-weight:900; line-height:1.32; margin-top:.22rem; }
        .final-answer-description { color:#aeb8c4 !important; margin:.2rem 0 .65rem 0; line-height:1.5; }
        .final-answer-fallback {
            background:#0d1114; border:1px solid #36515a; border-left:4px solid #22d3ee; border-radius:14px; padding:1rem 1.1rem;
        }
        .final-answer-fallback-value { color:#f8fafc !important; line-height:1.62; margin-top:.25rem; }
        .rubric-total {
            display:flex; justify-content:space-between; align-items:center; background:#101317; border:1px solid #2b3138;
            border-radius:12px; padding:.75rem .9rem; margin:.25rem 0 .72rem 0; color:#aab4c0 !important;
        }
        .rubric-total strong { color:#f8fafc !important; font-size:1.2rem; }
        .rubric-note { background:#111318; border:1px solid #2b3138; border-radius:12px; padding:.72rem .85rem; color:#d6d9de !important; line-height:1.5; margin:.25rem 0 .7rem 0; }
        .rubric-table { width:100%; border-collapse:collapse; background:#0d1013; border:1px solid #283038; border-radius:12px; overflow:hidden; }
        .rubric-table th, .rubric-table td { padding:.68rem .82rem; border-bottom:1px solid #232a31; text-align:left; }
        .rubric-table th { color:#8ddfd4 !important; font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; background:#11161a; }
        .rubric-table td { color:#e5e7eb !important; }
        .rubric-table tr:last-child td { border-bottom:none; }
        .rubric-marks { width:90px; text-align:right !important; font-weight:850; color:#f8fafc !important; }

        /* Batch-reactor fundamentals ----------------------------------- */
        .learning-objectives {
            margin:.8rem 0 1.2rem 0; padding:1rem 1.1rem; border:1px solid #275d58; border-radius:16px;
            background:linear-gradient(180deg,#0d1716,#0b0f11);
        }
        .learning-objectives-title { color:#99f6e4 !important; font-weight:900; font-size:.88rem; text-transform:uppercase; letter-spacing:.08em; margin-bottom:.7rem; }
        .learning-objectives-grid { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:.55rem; }
        .learning-objectives-grid > div { background:#101416; border:1px solid #252d30; border-radius:12px; padding:.7rem .75rem; color:#eef2f5 !important; line-height:1.4; }
        .learning-objectives-grid span { color:#98a3ad !important; font-size:.79rem; }
        .teaching-card {
            --teach-accent:#2dd4bf; margin:.72rem 0 .92rem 0; padding:.9rem 1rem; border-radius:14px;
            border:1px solid color-mix(in srgb,var(--teach-accent) 50%,#252a30); border-left:4px solid var(--teach-accent);
            background:linear-gradient(90deg,color-mix(in srgb,var(--teach-accent) 9%,#0d1012),#0d1012 55%);
        }
        .teaching-card-title { color:#f8fafc !important; font-size:.95rem; font-weight:880; margin-bottom:.28rem; }
        .teaching-card-body { color:#cbd2d9 !important; line-height:1.6; }
        .equation-caption { color:#8ddfd4 !important; font-size:.78rem; font-weight:850; text-transform:uppercase; letter-spacing:.07em; margin:.72rem 0 .1rem 0; }
        .symbol-card { background:#0e1215; border:1px solid #273039; border-radius:13px; padding:.75rem .8rem; min-height:88px; text-align:center; }
        .symbol-main { color:#f8fafc !important; font-size:1.25rem; font-weight:900; }
        .symbol-desc { color:#98a3ad !important; font-size:.76rem; margin-top:.18rem; line-height:1.35; }
        .model-chain {
            display:flex; align-items:stretch; justify-content:center; flex-wrap:wrap; gap:.42rem; margin:1rem 0 1.25rem 0;
            padding:.85rem; border:1px solid #26333a; border-radius:16px; background:#0b0e10;
        }
        .model-chain > div:not(.model-arrow) { min-width:150px; flex:1 1 150px; border:1px solid #283139; border-radius:12px; background:#111519; padding:.68rem .72rem; text-align:center; }
        .model-chain b { display:block; color:#e8edf2 !important; font-size:.80rem; }
        .model-chain span { display:block; color:#8ddfd4 !important; font-size:.82rem; margin-top:.2rem; }
        .model-arrow { display:flex; align-items:center; color:#5eead4 !important; font-size:1.2rem; font-weight:900; padding:0 .1rem; }

        .teaching-table-wrap {
            width:100%; overflow-x:auto; margin:.7rem 0 1rem 0; border:1px solid #2a3036; border-radius:14px;
            background:#080a0c;
        }
        .teaching-table { width:100%; border-collapse:collapse; background:#080a0c; }
        .teaching-table th, .teaching-table td {
            padding:.72rem .78rem; border-right:1px solid #252a30; border-bottom:1px solid #252a30;
            color:#eef2f5 !important; vertical-align:middle;
        }
        .teaching-table th { background:#101316; color:#aeb8c4 !important; font-weight:760; }
        .teaching-table th:last-child, .teaching-table td:last-child { border-right:none; }
        .teaching-table tr:last-child td { border-bottom:none; }
        .teaching-table .tt-left { text-align:left; }
        .teaching-table .tt-center { text-align:center; }
        .teaching-table .tt-right { text-align:right; }
        .teaching-table .tt-mono { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-variant-numeric:tabular-nums; }

        @media (max-width: 900px) {
            .reactionpot-hero { min-height: 225px; }
            .reactionpot-logo { font-size: 3.05rem; }
            .reactionpot-capability-line { font-size: .90rem; }
            .stack-title { font-size: 1.30rem; }
            .stack-card { min-height: 116px; }
            .home-metric-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
            .learning-objectives-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
            .model-arrow { display:none; }
        }

        /* KineticFittingPot v1.02: light presentation layer --------------------- */
        :root { --bg:#f6f9fc; --panel:#ffffff; --panel2:#edf4fa;
                --text:#17314f; --muted:#526880; --line:#d9e4ef;
                --accent:#2463a6; --accent2:#3c80bd; }
        .stApp, [data-testid="stAppViewContainer"] { background:#f6f9fc !important; color:#17314f !important; }
        .block-container { max-width:1360px; padding-top:1.2rem !important; }
        h1,h2,h3,h4, p, label { color:#17314f; }
        .workspace-title-card, .kfp-home-title { background:#ffffff !important;
          border:1px solid #d9e4ef !important; border-left:4px solid #2463a6 !important;
          box-shadow:0 3px 12px rgba(25,62,103,.05) !important; border-radius:15px !important; }
        .workspace-title { color:#163d65 !important; font-size:1.75rem; }
        .workspace-desc,.workspace-breadcrumb { color:#526880 !important; }
        .home-active-section { color:#245987 !important; letter-spacing:.065em; margin-top:1.1rem; }
        .stack-card-link { max-width:none; margin-bottom:.65rem; }
        .stack-card { min-height:126px; background:#ffffff !important;
          border:1px solid #d9e4ef !important; border-radius:15px !important;
          box-shadow:0 3px 12px rgba(25,62,103,.04) !important; padding:1rem 1.15rem; }
        .stack-card:hover { background:#f1f7fd !important; border-color:#83afd4 !important;
          box-shadow:0 7px 18px rgba(25,62,103,.10) !important; }
        .stack-title { color:#17314f !important; font-size:1.14rem !important; line-height:1.25; }
        .stack-kicker,.stack-open { color:#2463a6 !important; font-size:.72rem; }
        .stack-desc { color:#526880 !important; font-size:.87rem; }
        .metric-card,.panel,.soft-panel,.question-box,.solution-step,.symbol-card,
        .learning-objectives-grid > div,.model-chain > div:not(.model-arrow),.rubric-note,
        .eng-exp-table-wrap,.teaching-table-wrap { background:#fff !important;
          border-color:#d9e4ef !important; box-shadow:none !important; color:#17314f !important; }
        .metric-note,.metric-label { color:#526880 !important; }
        .metric-value { color:#17314f !important; }
        .teaching-table,.eng-exp-table,.rubric-table { background:#fff !important; color:#17314f !important; }
        .teaching-table th,.eng-exp-table th,.rubric-table th { background:#edf4fa !important; color:#234f7e !important; }
        .teaching-table td,.eng-exp-table td,.rubric-table td { color:#17314f !important; border-color:#d9e4ef !important; }
        div[data-testid="stMetric"],div[data-testid="stExpander"] { background:#fff !important; border-color:#d9e4ef !important; }
        div.stButton > button,div.stDownloadButton > button { background:#eaf3fb !important;
          border:1px solid #b5cee5 !important; color:#174a78 !important; }
        div.stButton > button:hover,div.stDownloadButton > button:hover { background:#d8ebfa !important; }
        [data-testid="stDataFrame"], [data-testid="stTable"] { background:#ffffff !important; }

        /* v1.03 - Normalise legacy educational content to light theme */
        .reactionpot-hero,.learning-objectives,.teaching-card,.model-chain,
        .final-answer-card,.final-answer-fallback,.rubric-total,.rubric-note,
        .assumption-card,.step-card,.home-metric-card,.teaching-table-wrap,
        .eng-exp-table-wrap,.rubric-table,.eng-exp-table,
        .panel,.soft-panel,.question-box,.solution-step,.symbol-card,
        .metric-card,.learning-objectives-grid > div,.model-chain > div:not(.model-arrow),
        .rubric-table td,.teaching-table td,.eng-exp-table td {
            background:#ffffff !important; background-image:none !important;
            color:#17314f !important; border-color:#d9e4ef !important;
            box-shadow:0 2px 9px rgba(28,68,113,.045) !important;
        }
        .learning-objectives,.model-chain,.final-answer-fallback,.teaching-card {
            border-left:4px solid #2868ad !important;
        }
        .learning-objectives-title,.teaching-card-title,.symbol-main,
        .final-answer-value,.final-answer-fallback-value,.rubric-total strong,
        .model-chain b,.rubric-marks,.reactionpot-logo {
            color:#17314f !important;
        }
        .learning-objectives-grid span,.teaching-card-body,.symbol-desc,
        .final-answer-description,.assumption-text,.step-body,.rubric-note,
        .model-chain span,.metric-note,.rubric-total {
            color:#526880 !important;
        }
        .equation-caption,.final-answer-label,.model-arrow,.step-number,
        .learning-objectives-title { color:#2868ad !important; }
        .teaching-table,.eng-exp-table,.rubric-table,
        .teaching-table tr,.eng-exp-table tr,.rubric-table tr { background:#ffffff !important; }
        .teaching-table th,.eng-exp-table th,.rubric-table th {
            background:#e9f2fa !important; color:#1c507c !important;
        }
        .teaching-table td,.eng-exp-table td,.rubric-table td {
            color:#17314f !important; border-color:#d9e4ef !important;
        }
        .chip,.chip-blue,.chip-warn {
            background:#eaf3fb !important; border:1px solid #c9ddec !important;
            color:#245987 !important;
        }
        .step-number { background:#eaf3fb !important; border-color:#bdd7ec !important; }
        .metric-label,.workspace-breadcrumb,.workspace-desc { color:#526880 !important; }

        @media(max-width:850px) { .stack-title { font-size:1.05rem !important; }
          .stack-card { min-height:115px; } }
        .kfp-data-wrap { overflow-x:auto; max-width:100%; border:1px solid #d4e0eb; border-radius:14px; margin:.6rem 0 1.2rem; }
        .kfp-data-table { width:100%; border-collapse:collapse; background:#fff; color:#1d3551; font-size:.93rem; }
        .kfp-data-table th { background:#edf4fa; color:#536e88; text-align:center; padding:.68rem .72rem; border-bottom:1px solid #d4e0eb; white-space:nowrap; }
        .kfp-data-table td { border-top:1px solid #e0e8f0; padding:.65rem .72rem; }
        .kfp-data-table td.num { text-align:center; font-variant-numeric:tabular-nums; }
        .kfp-data-table td.txt { text-align:left; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def teaching_table(headers, rows, *, alignments=None, monospace_columns=None) -> None:
    """Render a compact teaching table with explicit cell alignment.

    Streamlit's dataframe grid may apply its own numeric alignment even when a
    pandas Styler requests centring. This renderer is intended for small,
    static explanatory tables where visual column alignment is part of the
    teaching content.
    """
    headers = list(headers)
    rows = [list(row) for row in rows]
    alignments = list(alignments or ["left"] * len(headers))
    monospace_columns = set(monospace_columns or [])
    if len(alignments) != len(headers):
        raise ValueError("alignments must contain one entry per table column")

    valid_alignments = {"left", "center", "right"}
    if any(a not in valid_alignments for a in alignments):
        raise ValueError("table alignment must be left, center or right")

    head = "".join(
        f"<th class='tt-{html.escape(align)}'>{html.escape(str(label))}</th>"
        for label, align in zip(headers, alignments)
    )
    body_rows = []
    for row in rows:
        if len(row) != len(headers):
            raise ValueError("each table row must match the number of headers")
        cells = []
        for idx, (value, align) in enumerate(zip(row, alignments)):
            mono = " tt-mono" if idx in monospace_columns else ""
            cells.append(
                f"<td class='tt-{html.escape(align)}{mono}'>{html.escape(str(value))}</td>"
            )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    st.markdown(
        "<div class='teaching-table-wrap'><table class='teaching-table'>"
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody>"
        "</table></div>",
        unsafe_allow_html=True,
    )


def _clear_page_query() -> None:
    try:
        if "page" in st.query_params:
            del st.query_params["page"]
    except Exception:
        try:
            st.query_params.clear()
        except Exception:
            pass


def navigate(page: str) -> None:
    st.session_state["page"] = page
    try:
        st.query_params["page"] = page
    except Exception:
        pass
    st.rerun()


def go_home(section: str = "Learning & Reference") -> None:
    st.session_state["page"] = "Home"
    st.session_state["home_section_choice"] = section
    _clear_page_query()
    st.rerun()


def home_hero() -> None:
    """Compatibility helper for the standalone KineticFittingPot identity."""
    st.markdown("<div class='workspace-title-card'><div class='workspace-title'>KineticFittingPot</div>"
                "<div class='workspace-desc'>Simulation, fitting and model diagnostics</div></div>",
                unsafe_allow_html=True)


def workspace_header(title: str, subtitle: str, section: str = "Learning & Reference", accent: str = "#14b8a6") -> None:
    if st.button("Home", key=f"back_{title}"):
        go_home(section)
    st.markdown(
        f"<div class='workspace-breadcrumb'>KineticFittingPot &nbsp;›&nbsp; {html.escape(section)} &nbsp;›&nbsp; {html.escape(title)}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class='workspace-title-card' style='--workspace-accent:{html.escape(accent)};'>
            <div class='workspace-title'>{html.escape(title)}</div>
            <div class='workspace-desc'>{html.escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    """Backward-compatible workspace title helper used by any remaining modules."""
    workspace_header(title, subtitle)


def metric_card(label: str, value: str, note: str = "", compact: bool = False) -> None:
    note_html = f"<div class='metric-note'>{html.escape(note)}</div>" if note else ""
    card_class = "metric-card metric-card-compact" if compact else "metric-card"
    st.markdown(
        f"<div class='{card_class}'><div class='metric-label'>{html.escape(label)}</div><div class='metric-value'>{html.escape(str(value))}</div>{note_html}</div>",
        unsafe_allow_html=True,
    )


def chips(items: Iterable[tuple[str, str]]) -> None:
    parts = []
    for text, kind in items:
        cls = "chip"
        if kind == "blue": cls += " chip-blue"
        elif kind == "warn": cls += " chip-warn"
        parts.append(f"<span class='{cls}'>{html.escape(str(text))}</span>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def section(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def page_note(text: str) -> None:
    st.markdown(f"<div class='soft-panel muted'>{html.escape(text)}</div>", unsafe_allow_html=True)


def show_dataframe(data, *, use_container_width=True, hide_index=True, height=None, **kwargs) -> None:
    """Consistent static results tables: centered numbers, concise display only.

    Large/interactive dataframes retain Streamlit's grid. Original underlying
    numeric data are never modified by this formatting.
    """
    import numbers
    import pandas as pd
    from pandas.io.formats.style import Styler
    # Import Styler explicitly: pd.io.formats.style may not be available as
    # an attribute until its submodule has been loaded. Both plain DataFrames
    # and Pandas Styler input are supported.
    if isinstance(data, Styler):
        data = data.data
    frame = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    if len(frame) > 150 or len(frame.columns) > 18 or kwargs or height is not None:
        native_options = dict(use_container_width=use_container_width, hide_index=hide_index)
        # Streamlit releases differ in how they treat height=None. Omitting the
        # optional argument uses Streamlit's own default in every version.
        if height is not None:
            if not ((isinstance(height, int) and not isinstance(height, bool) and height > 0)
                    or height in ("stretch", "content")):
                raise ValueError("Table height must be a positive integer, 'stretch', or 'content'.")
            native_options["height"] = height
        st.dataframe(frame, **native_options, **kwargs)
        return
    def show(value):
        if pd.isna(value): return "—"
        if isinstance(value, (bool,)): return str(value)
        if isinstance(value, numbers.Integral): return str(value)
        if isinstance(value, numbers.Real): return f"{float(value):.6g}"
        return str(value)
    cols = list(frame.columns)
    heads = "".join(f"<th>{html.escape(str(c))}</th>" for c in cols)
    rows = []
    for _, series in frame.iterrows():
        cells = []
        for c in cols:
            val = series[c]
            cls = "num" if isinstance(val, numbers.Number) and not isinstance(val, bool) else "txt"
            cells.append(f"<td class='{cls}'>{html.escape(show(val))}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown("<div class='kfp-data-wrap'><table class='kfp-data-table'><thead><tr>" + heads +
                "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>", unsafe_allow_html=True)
