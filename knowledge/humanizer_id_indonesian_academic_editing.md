# Humanizer ID — Indonesian Academic Editing Engine

Source: https://github.com/apissaj/humanizer-id
Author: Hafizh Muzani (apissaj) · License: MIT · Verified 2026-11-10 (169 stars, 15 forks)

## 1. What it is

An editorial guide and deterministic rule engine for **Indonesian academic and professional prose**. It removes AI-sounding stiffness, machine-translation calques, light verbs, empty transitions, and nonstandard forms while preserving facts, numbers, citations, and modality.

It explicitly does **not** promise AI-detector evasion and forbids disguising document origin or fabricating substance.

## 2. Why Indonesian AI text feels stiff

1. Stacked nominalizations and light verbs — "melakukan pengujian terhadap" instead of "menguji".
2. Machine-translation calques — English clause-by-clause translation.
3. Anticipatory denial — "Meskipun X, bukan berarti Y…" answering an objection nobody raised.
4. Monotonous staccato — chains of short one-clause sentences.
5. Mechanical paragraph openers — "Selain itu…", "Lebih lanjut…", "Oleh karena itu…" repeated.
6. Empty transitions — causal connectors without sufficient premises.

## 3. Binding integrity rules

1. **Numbers and data** — preserve all quantities, percentages, p-values, units, equations, and table/figure references exactly.
2. **No fabrication** — never add methods, algorithms, parameters, or citations absent from the source.
3. **Separate language from substance** — flag questionable claims, incomplete references, or weak logic in separate notes; never silently "fix" them.
4. **Preserve modality** — "diharapkan dapat" must not become "terbukti".
5. **No unilateral summarization** — polishing must not cut the depth of the original paragraph.

## 4. Absolute exclusions and false positives

Do not rewrite:
- validated research instruments (questionnaires, Likert scales, psychometric tests),
- legal clauses, contracts, patents,
- direct quotations, law names, institution names, product brands.

Not AI errors:
- methodological passive ("Sampel diekstraksi…") in Methods/Results,
- standard technical loanwords (konduktivitas, entalpi, rekursif, instansiasi, skalabilitas),
- "merupakan" in essential definition sentences.

## 5. Four execution modes

| Mode | Use | Rules |
|---|---|---|
| Academic strict | Thesis, dissertation, journal, paper | Impersonal, methodological passive allowed, EYD V/KBBI, separate Conclusion vs Recommendation |
| Essay/opinion | Article, column, blog | Author voice allowed, dynamic rhythm, concrete analogy |
| Business/executive | Management report, memo, proposal | Action-oriented, no pleasantries, cross-domain glossary |
| Minimal proofread | Typo/basic correction only | Spelling, punctuation, nonstandard forms, capitalization only |

## 6. Rule inventory (verified)

`data/kalke-indonesia.json` contains **420 rules**:

| Category | Count | IDs | Focus |
|---|---:|---|---|
| Machine-translation calques | 155 | KLK | Literal English idioms and phrases |
| Light verbs | 10 | VRB | "melakukan X" → "meng-X" |
| AI rhetoric clichés | 78 | RET, SPK | Formulaic openers, anticipatory denial, empty cohesion |
| Standard forms & morphology | 177 | BAK, DSG | EYD V, KTSP, standard lexemes |

Other data:
- `glosarium-lintas-bidang.json` — cross-domain glossary (technology, law, economics, etc.).
- `pedoman-kampus.json` — campus presets; data contains 18 keys (ui, itb, ugm, its, ipb, undip, unpad, unair, ub, telkom, udinus, uns, unnes, upi, unhas, unand, jurnal-dikbud, jurnal-jipp), while SKILL.md mentions 11.

Additional rule families in `SKILL.md`: connector addiction, empty transitions, agent drift, citation weaving, epistemic hedging, table/figure/equation conventions, effective-sentence criteria, correlative conjunctions, numeral conventions, acronym redundancy, PUPI terminology, capitalization, definition sentences, "dimana" residue, compound words, prepositional redundancy, pleonasm.

## 7. CLI and API

Install: `pip install humanizer-id`

```bash
humanizer-id naskah.md
humanizer-id naskah.md --fix
humanizer-id naskah.md --fix --write
humanizer-id naskah.md --preset akademik
humanizer-id surat.md --preset dinas
humanizer-id --demo
humanizer-id naskah.md --kampus ugm
```

Flags: `--fix`, `--write`/`-w`, `--preset umum|akademik|dinas|jurnalistik`, `--kampus <id>`, `--demo`.

Python API:

```python
from humanizer_id.audit import load_default_data, audit_text
kalke, glos = load_default_data()
findings = audit_text(text, kalke, glos)
```

## 8. Verified behavior and limitations

Tested on 2026-11-10 from a shallow clone:

- `--demo`: 10 findings, including RET-002, RET-006, VRB-001, GLOS-TEK, GLOS-HUK, JURNAL-EKONOMI.
- Academic preset on a synthetic AI-style paragraph: 6 findings, including KLK-008 ("yang mana"), VRB-004 ("memberikan pengaruh"), VRB-007 ("melakukan analisis"), RET-001, DSG-003 ("di era" → "pada era").
- `--fix` applied 4 replacements but produced awkward collocations:
  - "menganalisis terhadap data" (should be "menganalisis data")
  - "memengaruhi terhadap performa" (should be "memengaruhi performa")

**Conclusion:** the audit is useful; the autofix is lexical and context-blind. Never apply `--fix --write` without human review of the diff.

Other limitations:
- Rule-based, not a full grammar or fact checker.
- False positives on legitimate technical terms and passive methodology.
- Campus presets vary by edition; verify against the current campus guide.
- Version metadata is inconsistent: `pyproject.toml` 1.6.0, `SKILL.md` 1.5.1, dataset metadata 1.3.0. Check the installed version before citing a rule count.
- Does not replace a human editor for academic argumentation or journal-specific style.

## 9. Repository structure

- `humanizer_id/` — engine.py (audit/fix/CLI), matchers.py (786 lines of pattern rules), audit.py (public API), cli.py.
- `data/` — kalke-indonesia.json, glosarium-lintas-bidang.json, pedoman-kampus.json.
- `SKILL.md` — full agent skill (95 KB) with four modes and rule families.
- `PROMPT.md`, `PROMPT-AKADEMIK.md` — copy-paste prompts for LLM platforms.
- `examples/` — before/after academic samples.
- `references/` — extracts from official Indonesian textbooks and Badan Bahasa guides.
- `tests/` — smoke, regression, fix, packaging, benchmark, large benchmark; 20 AI abstract corpus files.
- `.github/workflows/` — CI and publish pipelines.

Repo map from `repo_recon.py`: 165 files — 135 Markdown, 14 Python, 8 JSON, 2 YAML, 1 TOML.

## 10. How Gemi should use it

1. Treat it as an Indonesian academic/professional editing checklist and audit tool.
2. Run the audit on a **copy**; present findings with rule IDs and suggested replacements.
3. Never `--fix --write` without explicit approval; show the diff and fix awkward collocations.
4. Preserve numbers, citations, modality, and paragraph depth; put substantive concerns in a separate note.
5. Use `--preset akademik` for theses/journals, `dinas` for official letters, `jurnalistik` for news/opinion.
6. Do not claim detector evasion; disclose AI assistance where required by the institution.
7. Pair with `human-technical-writing` for general prose and `document-ocr-and-conversion` for extracting text from PDFs.

## 11. Official references used by the project

- EYD Edisi V (Keputusan Kepala Badan Bahasa No. 0424/I/BS.00.01/2022)
- TBBBI Edisi IV
- KBBI V and PASTI (pasti.kemendikdasmen.go.id)
- Kemendikbudristek Indonesian textbooks (2021–2024 editions)
- Badan Bahasa penyuluhan series (Kalimat, Paragraf, Bentuk dan Pilihan Kata, Tata Istilah, Preposisi)
- Ivan Lanin, *Xenoglosofilia* (2018) and *Recehan Bahasa* (2020)
- Kobak et al., *Science Advances* (2025), DOI: 10.1126/sciadv.adt3813

## 12. Ethical boundary

Use for clarity, register, and editorial quality. Do not use to hide authorship, evade academic-integrity checks, or fabricate research content. The repository's own rules forbid these uses.
