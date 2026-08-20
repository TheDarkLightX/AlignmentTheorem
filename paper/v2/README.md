# Alignment Theorem Version 2 paper

Build with either:

```bash
cd paper/v2
tectonic alignment_theorem_v2.tex
```

or a standard BibTeX toolchain:

```bash
cd paper/v2
pdflatex alignment_theorem_v2.tex
bibtex alignment_theorem_v2
pdflatex alignment_theorem_v2.tex
pdflatex alignment_theorem_v2.tex
```

Build the GitHub Pages copy from this directory with:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -jobname=Alignment_Theorem_V2 -outdir=../../docs \
  alignment_theorem_v2.tex
```

The paper's empirical and formal statements must remain synchronized with:

- `verification/receipts/tau_v2_fd137e8.json`
- `verification/receipts/lean_v2_v4.33.0.json`
- `proofs/v2/AlignmentTheoremV2.lean`
- `verification/alignment_v2_model.py`
- `tests/test_alignment_v2_model.py`
- `tests/test_tau_policy_v2.py`

Do not promote the trained-agent discussion into a claim that this repository
trained a model. It presents a compatible architecture and a network-side
guarantee.
