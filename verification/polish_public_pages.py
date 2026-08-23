#!/usr/bin/env python3
"""Apply deterministic GitHub Pages UI, mobile, link, and accessibility polish."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
ESSAY = ROOT / "docs" / "data-center-social-contract.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"missing replacement anchor: {label}")
    return text.replace(old, new, 1)


def polish_index(text: str) -> str:
    text = replace_once(
        text,
        '''    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alignment Theorem - Ethical and Profitable LLM Agents</title>''',
        '''    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="The Alignment Theorem: formal incentive, hyperdeflation, data-center social-contract, and Tau Language research.">
    <meta name="theme-color" content="#0a0a0f">
    <meta property="og:type" content="website">
    <meta property="og:title" content="The Alignment Theorem">
    <meta property="og:description" content="Formal incentive theorems, the Data Center Bargain, and Tau-governed economic alignment.">
    <meta property="og:url" content="https://thedarklightx.github.io/AlignmentTheorem/">
    <link rel="canonical" href="https://thedarklightx.github.io/AlignmentTheorem/">
    <title>Alignment Theorem - Ethical and Profitable LLM Agents</title>''',
        "index metadata",
    )
    text = replace_once(
        text,
        '''        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }''',
        '''        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html { scroll-behavior: smooth; }
        :focus-visible {
            outline: 3px solid var(--accent-gold);
            outline-offset: 4px;
        }
        .skip-link {
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 100;
            padding: 10px 14px;
            border-radius: 10px;
            background: var(--accent-gold);
            color: #0a0a0f;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            transform: translateY(-160%);
            transition: transform 0.18s ease;
        }
        .skip-link:focus { transform: translateY(0); }''',
        "index accessibility css",
    )
    text = replace_once(
        text,
        '''        .section {
            margin: 60px 0;
        }''',
        '''        .section {
            margin: 60px 0;
            scroll-margin-top: 24px;
        }''',
        "index anchor offset",
    )
    text = replace_once(
        text,
        '''        .scenario-button {
            flex: 1;''',
        '''        .scenario-button {
            flex: 1;
            appearance: none;
            background: rgba(255,255,255,0.035);
            font: inherit;''',
        "scenario button reset",
    )
    featured_css = '''
        .featured-essay {
            position: relative;
            overflow: hidden;
            margin: 46px 0 64px;
            padding: clamp(30px, 5vw, 56px);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 24px;
            background:
                radial-gradient(circle at 90% 10%, rgba(157, 78, 221, 0.24), transparent 42%),
                linear-gradient(135deg, rgba(0,255,255,0.08), rgba(255,215,0,0.055));
            box-shadow: 0 24px 70px rgba(0,0,0,0.4);
        }
        .featured-essay::after {
            content: '';
            position: absolute;
            width: 260px;
            height: 260px;
            right: -90px;
            bottom: -120px;
            border-radius: 50%;
            background: rgba(0,255,136,0.08);
            filter: blur(2px);
            pointer-events: none;
        }
        .featured-grid {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(0, 1.55fr) minmax(250px, .75fr);
            gap: 34px;
            align-items: center;
        }
        .featured-kicker {
            display: inline-flex;
            padding: 7px 12px;
            border-radius: 999px;
            border: 1px solid rgba(0,255,255,0.28);
            color: var(--accent-cyan);
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: .12em;
            font-weight: 700;
        }
        .featured-essay h2 {
            margin: 18px 0 16px;
            font-family: 'Orbitron', sans-serif;
            font-size: clamp(1.8rem, 4vw, 3rem);
            line-height: 1.15;
            color: var(--text-primary);
        }
        .featured-essay p {
            max-width: 780px;
            color: var(--text-secondary);
            line-height: 1.75;
            font-size: 1.12rem;
        }
        .featured-equation {
            margin: 22px 0 0;
            padding: 16px 18px;
            border-left: 3px solid var(--accent-green);
            background: rgba(0,0,0,.28);
            color: var(--accent-green);
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            overflow-x: auto;
        }
        .featured-stats { display: grid; gap: 12px; }
        .featured-stat {
            padding: 18px;
            border: 1px solid rgba(255,255,255,.1);
            border-radius: 15px;
            background: rgba(0,0,0,.28);
        }
        .featured-stat strong {
            display: block;
            font-family: 'Orbitron', sans-serif;
            color: var(--accent-gold);
            font-size: 1.45rem;
        }
        .featured-stat span { color: var(--text-secondary); line-height: 1.35; }
        .table-scroll {
            max-width: 100%;
            overflow-x: auto;
            margin-top: 20px;
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 14px;
            scrollbar-color: var(--accent-cyan) rgba(255,255,255,.05);
        }
        .table-scroll .data-table { min-width: 700px; margin-top: 0; }
'''
    text = replace_once(
        text,
        '''        .data-table {
            width: 100%;''',
        featured_css + '''        .data-table {
            width: 100%;''',
        "featured and responsive table css",
    )
    text = replace_once(
        text,
        '''        .data-table a {
            color: var(--accent-gold);
            text-decoration: none;
        }
    </style>''',
        '''        .data-table a {
            color: var(--accent-gold);
            text-decoration: none;
        }

        @media (max-width: 780px) {
            .container { padding: 28px 20px; }
            .featured-grid { grid-template-columns: 1fr; }
            .featured-stats { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .top-nav { gap: 14px 18px; }
            .top-nav a { font-size: .78rem; }
            .chart-container, .proof-container { padding: 26px 20px; }
        }
        @media (max-width: 520px) {
            h1 { font-size: clamp(2.5rem, 15vw, 4.2rem); letter-spacing: 2px; }
            .subtitle { font-size: 1.24rem; }
            .cta-buttons .cta-button { width: min(100%, 300px); text-align: center; }
            .featured-stats { grid-template-columns: 1fr; }
            .featured-essay { padding: 28px 22px; }
            .theorem-box { padding: 28px 20px; }
            .theorem-text { font-size: 1.25rem; }
            .section-title { font-size: 1.65rem; }
        }
        @media (prefers-reduced-motion: reduce) {
            html { scroll-behavior: auto; }
            *, *::before, *::after {
                animation-duration: .01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: .01ms !important;
            }
        }
    </style>''',
        "index responsive css",
    )
    text = replace_once(
        text,
        '''<body>
    <div class="stars"></div>''',
        '''<body id="top">
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <div class="stars" aria-hidden="true"></div>''',
        "index skip link",
    )
    text = replace_once(
        text,
        '''            <div class="top-nav">
                <a href="#core">Core Insight</a>''',
        '''            <nav class="top-nav" aria-label="Main navigation">
                <a href="data-center-social-contract.html">Data Center Bargain</a>
                <a href="#core">Core Insight</a>''',
        "index navigation opening",
    )
    text = replace_once(
        text,
        '''                <a href="alignment-theorem-deep-dive.html">Version 1 Deep Dive</a>
            </div>''',
        '''                <a href="alignment-theorem-deep-dive.html">Version 1 Deep Dive</a>
            </nav>''',
        "index navigation closing",
    )
    text = replace_once(
        text,
        '''                <a class="cta-button primary" href="Alignment_Theorem_V2.pdf" target="_blank" rel="noopener">Download Version 2</a>''',
        '''                <a class="cta-button primary" href="data-center-social-contract.html">Read the Data Center Bargain</a>
                <a class="cta-button secondary" href="Alignment_Theorem_V2.pdf" target="_blank" rel="noopener">Download Version 2</a>''',
        "index primary CTA",
    )
    text = replace_once(
        text,
        '''        </header>
        
        <div class="theorem-box">''',
        '''        </header>

        <main id="main-content">
        <div class="theorem-box">''',
        "index main opening",
    )
    feature = '''

        <section class="featured-essay" id="data-center">
            <div class="featured-grid">
                <div>
                    <span class="featured-kicker">New research · local government · post-AGI economics</span>
                    <h2>The Data Center Bargain</h2>
                    <p>Local communities do not have to choose between rejecting AI infrastructure and subsidizing it. The new social-contract theorem puts grid, water, safety, public-service, household-loss, audit, and decommissioning claims first—then shares only the authenticated residual.</p>
                    <div class="featured-equation">H(m) = Σ max(m, (loss − direct benefit)⁺)</div>
                    <div class="cta-buttons" style="justify-content:flex-start">
                        <a class="cta-button primary" href="data-center-social-contract.html">Open the interactive essay</a>
                        <a class="cta-button secondary" href="https://github.com/TheDarkLightX/AlignmentTheorem/blob/main/research/data_center_social_contract/LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md" target="_blank" rel="noopener">Local policy playbook</a>
                    </div>
                </div>
                <div class="featured-stats" aria-label="Research validation highlights">
                    <div class="featured-stat"><strong>65,100</strong><span>household and floor profiles tested</span></div>
                    <div class="featured-stat"><strong>1,024</strong><span>Tau semantic rows; only all-true admits</span></div>
                    <div class="featured-stat"><strong>0</strong><span>modeled welfare regressions or lifecycle invariant failures</span></div>
                </div>
            </div>
        </section>
'''
    text = replace_once(
        text,
        '''        </div>
        
        <section class="section" id="core">''',
        '''        </div>''' + feature + '''        <section class="section" id="core">''',
        "index featured essay",
    )
    for old, new, label in (
        ('<div class="scenario-button active" data-scarcity="10" data-eetf="10">Baseline</div>', '<button type="button" class="scenario-button active" data-scarcity="10" data-eetf="10">Baseline</button>', "baseline button"),
        ('<div class="scenario-button" data-scarcity="60" data-eetf="15">Accelerated</div>', '<button type="button" class="scenario-button" data-scarcity="60" data-eetf="15">Accelerated</button>', "accelerated button"),
        ('<div class="scenario-button" data-scarcity="80" data-eetf="8">Adversarial Shock</div>', '<button type="button" class="scenario-button" data-scarcity="80" data-eetf="8">Adversarial Shock</button>', "adversarial button"),
    ):
        text = replace_once(text, old, new, label)
    text = replace_once(text, '<span>Scarcity Multiplier</span>', '<label for="scarcitySlider">Scarcity Multiplier</label>', "scarcity label")
    text = replace_once(text, '<span>Agent EETF Score</span>', '<label for="eetfSlider">Agent EETF Score</label>', "EETF label")
    text = replace_once(text, '<div class="result-display">', '<div class="result-display" role="status" aria-live="polite" aria-atomic="true">', "calculator live region")
    text = replace_once(text, '<table class="data-table">', '<div class="table-scroll" role="region" aria-label="Data packs and downloads" tabindex="0">\n            <table class="data-table">', "table wrapper open")
    text = replace_once(
        text,
        '''            </table>
        </section>
        
        <footer>''',
        '''            </table>
            </div>
        </section>
        </main>

        <footer>''',
        "table wrapper and main close",
    )
    text = replace_once(
        text,
        '''            <p>August 2026 • Alignment Theorem Versions 1.1 and 2.0</p>''',
        '''            <p>August 2026 • Alignment Theorem Versions 1.1 and 2.0 • Data Center Social Contract</p>
            <p><a class="inline-link" href="#top">Back to top</a></p>''',
        "index footer",
    )
    text = replace_once(
        text,
        '''        const scenarioButtons = document.querySelectorAll('.scenario-button');''',
        '''        const scenarioButtons = document.querySelectorAll('.scenario-button');
        scenarioButtons.forEach(btn => btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false'));''',
        "scenario aria initialization",
    )
    text = replace_once(
        text,
        '''            scarcityValue.textContent = scarcity + 'x';
            eetfValue.textContent = eetf.toFixed(1);''',
        '''            scarcityValue.textContent = scarcity + 'x';
            eetfValue.textContent = eetf.toFixed(1);
            scarcitySlider.setAttribute('aria-valuetext', scarcity + ' times');
            eetfSlider.setAttribute('aria-valuetext', eetf.toFixed(1));''',
        "slider aria values",
    )
    text = replace_once(
        text,
        '''        scenarioButtons.forEach(button => {
            button.addEventListener('click', () => {
                scenarioButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                scarcitySlider.value = button.dataset.scarcity;
                eetfSlider.value = button.dataset.eetf;
                updateCalculations();
            });
        });
        
        // Animate flow diagram
        const nodes = document.querySelectorAll('.flow-node');
        let currentNode = 0;
        
        setInterval(() => {
            nodes.forEach(node => node.classList.remove('highlight'));
            nodes[currentNode].classList.add('highlight');
            currentNode = (currentNode + 1) % nodes.length;
        }, 1500);''',
        '''        scenarioButtons.forEach(button => {
            button.addEventListener('click', () => {
                scenarioButtons.forEach(btn => {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-pressed', 'false');
                });
                button.classList.add('active');
                button.setAttribute('aria-pressed', 'true');
                scarcitySlider.value = button.dataset.scarcity;
                eetfSlider.value = button.dataset.eetf;
                updateCalculations();
            });
        });
        
        // Animate the historical flow only when motion is welcome.
        const nodes = document.querySelectorAll('.flow-node');
        let currentNode = 0;
        if (nodes.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            setInterval(() => {
                nodes.forEach(node => node.classList.remove('highlight'));
                nodes[currentNode].classList.add('highlight');
                currentNode = (currentNode + 1) % nodes.length;
            }, 1500);
        }''',
        "scenario state and reduced motion",
    )
    return text


def polish_essay(text: str) -> str:
    text = replace_once(
        text,
        '''  <meta name="description" content="A local-government social contract for data centers and post-AGI economics, derived from the Alignment Theorem and designed for Tau Language.">
  <title>The Data Center Bargain | Alignment Theorem</title>''',
        '''  <meta name="description" content="A local-government social contract for data centers and post-AGI economics, derived from the Alignment Theorem and designed for Tau Language.">
  <meta name="theme-color" content="#05060a">
  <meta property="og:type" content="article">
  <meta property="og:title" content="The Data Center Bargain | Alignment Theorem">
  <meta property="og:description" content="A constitutional bargain for data centers: full cost recovery, household protection, public benefit, and Tau-governed rule evolution.">
  <meta property="og:url" content="https://thedarklightx.github.io/AlignmentTheorem/data-center-social-contract.html">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://thedarklightx.github.io/AlignmentTheorem/data-center-social-contract.html">
  <title>The Data Center Bargain | Alignment Theorem</title>''',
        "essay metadata",
    )
    text = replace_once(
        text,
        '''    a { color: var(--cyan); }
    a:hover { color: var(--gold); }''',
        '''    a { color: var(--cyan); }
    a:hover { color: var(--gold); }
    :focus-visible { outline: 3px solid var(--gold); outline-offset: 4px; }
    .skip-link {
      position: fixed;
      top: 10px;
      left: 10px;
      z-index: 100;
      padding: 10px 14px;
      border-radius: 10px;
      background: var(--gold);
      color: #071014;
      font-family: "Space Grotesk", sans-serif;
      font-weight: 700;
      transform: translateY(-160%);
      transition: transform .18s ease;
    }
    .skip-link:focus { transform: translateY(0); }''',
        "essay accessibility css",
    )
    text = replace_once(
        text,
        '''    .button.primary { color: #071014; background: linear-gradient(120deg, var(--cyan), var(--gold)); border: 0; }''',
        '''    .button { transition: transform .18s ease, border-color .18s ease, background .18s ease; }
    .button:hover { transform: translateY(-2px); border-color: rgba(94,231,247,.45); }
    .button.primary { color: #071014; background: linear-gradient(120deg, var(--cyan), var(--gold)); border: 0; }''',
        "essay button feedback",
    )
    text = replace_once(
        text,
        '''    main { padding-bottom: 80px; }
    section { padding: 58px 0; }''',
        '''    main { padding-bottom: 80px; }
    section { padding: 58px 0; }
    section[id] { scroll-margin-top: 90px; }''',
        "essay anchor offset",
    )
    text = replace_once(
        text,
        '''      font: inherit;
    }''',
        '''      font: inherit;
    }
    input:focus { border-color: var(--cyan); box-shadow: 0 0 0 3px rgba(94,231,247,.12); outline: none; }
    .field-help { display: block; margin-top: 7px; color: var(--faint); font-size: .7rem; letter-spacing: 0; text-transform: none; line-height: 1.35; }
    .mobile-nav-hint { display: none; color: var(--faint); font-family: "Space Grotesk", sans-serif; font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; }''',
        "essay form and mobile hint css",
    )
    text = replace_once(
        text,
        '''      .nav-inner { align-items: flex-start; padding: 14px 0; }
      .nav-links { display: none; }''',
        '''      .nav-inner { align-items: stretch; flex-direction: column; padding: 12px 0 10px; gap: 9px; }
      .brand { align-self: flex-start; }
      .nav-links {
        display: flex;
        width: 100%;
        flex-wrap: nowrap;
        justify-content: flex-start;
        overflow-x: auto;
        overscroll-behavior-inline: contain;
        scrollbar-width: none;
        padding: 2px 2px 5px;
        mask-image: linear-gradient(to right, transparent 0, black 12px, black calc(100% - 20px), transparent 100%);
      }
      .nav-links::-webkit-scrollbar { display: none; }
      .nav-links a { flex: 0 0 auto; padding: 6px 3px; }
      .mobile-nav-hint { display: block; }
      section[id] { scroll-margin-top: 150px; }''',
        "essay mobile navigation",
    )
    text = replace_once(
        text,
        '''    @media (max-width: 520px) {
      body { font-size: 18px; }
      .hero { padding-top: 68px; }
      .results, .waterfall { grid-template-columns: 1fr; }
      .card, .calculator { padding: 21px; }
    }
  </style>''',
        '''    @media (max-width: 520px) {
      body { font-size: 18px; }
      .shell { width: min(100% - 28px, 1160px); }
      .hero { padding-top: 58px; }
      .hero-actions .button { width: 100%; }
      .results, .waterfall { grid-template-columns: 1fr; }
      .card, .calculator { padding: 21px; }
      table { font-size: .84rem; }
      th, td { padding: 11px 9px; }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
    }
  </style>''',
        "essay small-screen and motion css",
    )
    text = replace_once(text, '<body>\n  <nav class="nav">', '<body id="top">\n  <a class="skip-link" href="#main-content">Skip to the article</a>\n  <nav class="nav" aria-label="Article navigation">', "essay skip link")
    text = replace_once(
        text,
        '''      <div class="nav-links">
        <a href="#theorem">Theorem</a>''',
        '''      <span class="mobile-nav-hint" aria-hidden="true">Swipe for sections</span>
      <div class="nav-links">
        <a href="#theorem">Theorem</a>''',
        "essay mobile navigation hint",
    )
    text = replace_once(text, '<main>', '<main id="main-content">', "essay main landmark")
    text = text.replace('../research/data_center_social_contract/LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md', 'https://github.com/TheDarkLightX/AlignmentTheorem/blob/main/research/data_center_social_contract/LOCAL_GOVERNMENT_POLICY_PLAYBOOK.md')
    text = text.replace('https://github.com/TheDarkLightX/AlignmentTheorem/tree/research/compute-dividend-wealth-agent/research/data_center_social_contract', 'https://github.com/TheDarkLightX/AlignmentTheorem/tree/main/research/data_center_social_contract')
    replacements = (
        ('<label>Gross committed public value G\n            <input id="gross" type="number" min="0" step="1" value="30">\n          </label>', '<label for="gross">Gross committed public value G</label>\n          <input id="gross" type="number" min="0" step="1" value="30" inputmode="decimal">', "gross label"),
        ('<label>Senior project claims C\n            <input id="costs" type="number" min="0" step="1" value="12">\n          </label>', '<label for="costs">Senior project claims C</label>\n          <input id="costs" type="number" min="0" step="1" value="12" inputmode="decimal">', "cost label"),
        ('<label>Universal household floor m\n            <input id="floor" type="number" min="0" step="1" value="2">\n          </label>', '<label for="floor">Universal household floor m</label>\n          <input id="floor" type="number" min="0" step="1" value="2" inputmode="decimal">', "floor label"),
        ('<label>Household uncompensated deficits\n            <input id="deficits" type="text" value="0, 1, 5, 2">\n          </label>', '<label for="deficits">Household uncompensated deficits</label>\n          <input id="deficits" type="text" value="0, 1, 5, 2" inputmode="decimal" aria-describedby="deficits-help">\n          <span class="field-help" id="deficits-help">Comma-separated nonnegative values, one per household.</span>', "deficits label"),
        ('<label>Available compute reserve Q\n            <input id="compute" type="number" min="0" step="1" value="12">\n          </label>', '<label for="compute">Available compute reserve Q</label>\n          <input id="compute" type="number" min="0" step="1" value="12" inputmode="decimal">', "compute label"),
        ('<label>Compute floor per household c\n            <input id="computeFloor" type="number" min="0" step="1" value="2">\n          </label>', '<label for="computeFloor">Compute floor per household c</label>\n          <input id="computeFloor" type="number" min="0" step="1" value="2" inputmode="decimal">', "compute-floor label"),
    )
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)
    text = replace_once(text, '<div class="results">', '<div class="results" role="status" aria-live="polite" aria-atomic="true">', "essay result live region")
    text = replace_once(text, '<p id="rDetail" class="mono"', '<p id="rDetail" class="mono" aria-live="polite"', "essay detail live region")
    text = replace_once(
        text,
        '''  <footer>
    <div class="shell">Alignment Theorem research. Policy-relative, conditional, and falsifiable. This page is a research and policy proposal, not legal, utility, investment, or engineering advice.</div>
  </footer>''',
        '''  <footer>
    <div class="shell">Alignment Theorem research. Policy-relative, conditional, and falsifiable. This page is a research and policy proposal, not legal, utility, investment, or engineering advice. <a href="#top">Back to top</a></div>
  </footer>''',
        "essay footer",
    )
    return text


def validate(index: str, essay: str) -> None:
    requirements = {
        "index essay integration": 'href="data-center-social-contract.html"' in index and 'class="featured-essay"' in index,
        "index mobile overflow containment": 'class="table-scroll"' in index,
        "index accessible controls": '<button type="button" class="scenario-button' in index and 'label for="scarcitySlider"' in index,
        "essay canonical": 'rel="canonical" href="https://thedarklightx.github.io/AlignmentTheorem/data-center-social-contract.html"' in essay,
        "essay mobile navigation": 'Swipe for sections' in essay and '.nav-links {\n        display: flex;' in essay,
        "essay deployed links": 'research/compute-dividend-wealth-agent' not in essay and '../research/' not in essay,
        "essay accessible calculator": 'label for="deficits"' in essay and 'aria-live="polite"' in essay,
    }
    failed = [name for name, ok in requirements.items() if not ok]
    if failed:
        raise RuntimeError(f"page validation failed: {failed}")


if __name__ == "__main__":
    index = polish_index(INDEX.read_text())
    essay = polish_essay(ESSAY.read_text())
    validate(index, essay)
    INDEX.write_text(index)
    ESSAY.write_text(essay)
    print(f"polished {INDEX.relative_to(ROOT)} ({len(index)} bytes)")
    print(f"polished {ESSAY.relative_to(ROOT)} ({len(essay)} bytes)")
