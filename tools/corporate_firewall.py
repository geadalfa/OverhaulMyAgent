#!/usr/bin/env python3
"""
Corporate Firewall & Executive Comms CLI Tool (corporate_firewall.py)
--------------------------------------------------------------------
Disciplined utility for corporate communication, upward messaging (managing up),
emotional firewalling, anti-AI-slop linting, and 1-3-1 escalation structuring.

Zero external dependencies (pure Python standard library).
"""

import sys
import os
import re
import argparse
import json
from typing import List, Dict, Any, Tuple

# Banned AI-slop vocabulary (English)
BANNED_WORDS_EN = [
    "delve", "tapestry", "testament", "beacon", "symphony",
    "game-changer", "gamechanger", "landscape", "realm", "foster",
    "underscore", "pivotal", "intricate", "unwavering", "bespoke",
    "transformative", "paradigm shift", "plethora", "multifaceted",
    "harness", "supercharge", "holistic approach", "seamless"
]

# Banned AI-slop constructions & openers (English)
BANNED_PHRASES_EN = [
    r"i hope this email finds you well",
    r"in today'?s fast-paced (world|environment|market)",
    r"allow me to (share|explain|delve)",
    r"it is important to (note|remember|highlight) that",
    r"it'?s not just (about )?.+?, but (rather )?.+",
    r"not only .+? but also .+"
]

# Banned AI-slop constructions & openers (Indonesian)
BANNED_WORDS_ID = [
    "permadani", "lanskap", "menyelami", "menyelami lebih dalam"
]

BANNED_PHRASES_ID = [
    r"dalam lanskap yang terus berkembang",
    r"penting untuk dicatat bahwa",
    r"hal ini menjadi bukti nyata",
    r"semoga email ini menemui anda dalam keadaan baik",
    r"bukan sekadar .+?, melainkan .+",
    r"tidak hanya .+?, tetapi juga .+"
]

# Common raw emotional scenarios & corporate transformations
FIREWALL_SCENARIOS = {
    "sudden_scope": {
        "pattern": r"(mendadak|tiba-tiba|out of scope|deadline mepet|gak keburu|keburu|gak masuk akal|overload)",
        "id": {
            "title": "Permintaan Mendadak / Scope Creep",
            "bluf": "Siap Pak/Bu, inisiatif ini sangat menarik untuk didukung.",
            "body": "Mengingat saat ini tim sedang fokus memfinalisasi [Proyek A] agar rilis tepat waktu di hari Jumat, penambahan fitur ini akan mempengaruhi jadwal tersebut. Kita memiliki dua opsi alokasi: menggeser jadwal rilis [Proyek A] ke minggu depan, atau menjadwalkan fitur baru ini ke sprint berikutnya.",
            "ask": "Mohon arahannya mana yang menjadi prioritas utama Bapak/Ibu saat ini?"
        },
        "en": {
            "title": "Sudden Out-of-Scope / Tight Deadline",
            "bluf": "Happy to support this initiative.",
            "body": "Since the team is currently locked in on delivering [Project A] for Friday's target release, incorporating this scope now will impact that timeline. We have two viable options: reprioritize [Project A] to next week, or schedule this new initiative into our upcoming sprint.",
            "ask": "Please let us know your preferred priority so we can align sprint commitments."
        }
    },
    "bug_incident": {
        "pattern": r"(error|bug|bocor|down|rusak|ancur|hancur|kacau|salah spek|ketinggalan)",
        "id": {
            "title": "Melaporkan Bug / Delay / Insiden",
            "bluf": "Update status terkait [Modul X]: kami menemukan celah validasi pada integrasi saat uji beban.",
            "body": "Tim telah menerapkan perbaikan penahanan (containment fix) sehingga fungsi inti tetap stabil. Kami membutuhkan tambahan waktu 1 hari kerja untuk memperkuat pipeline validasi otomatis agar kelas insiden serupa tidak terulang.",
            "ask": "Layanan utama tetap beroperasi normal dan estimasi penyelesaian menyeluruh adalah [Hari/Jam]."
        },
        "en": {
            "title": "Reporting Bug / Incident / Delay",
            "bluf": "Status update on [Module X]: we identified an edge-case validation gap during load testing.",
            "body": "The team has deployed an immediate containment fix to keep core services stable. We are allocating an additional 24 hours to harden the automated test pipeline to prevent this class of issue going forward.",
            "ask": "Core operations remain unaffected, and complete verification will conclude by [Date/Time]."
        }
    },
    "team_friction": {
        "pattern": r"(salah paham|gak ngerti|rekan kerja|lambat banget|salah dia|tim lain)",
        "id": {
            "title": "Menjelaskan Miskomunikasi Tim secara Elegan",
            "bluf": "Terdapat perbedaan interpretasi teknis pada spesifikasi awal, yang kini telah kami selaraskan kembali.",
            "body": "Momen ini menjadi masukan berharga bagi kami untuk memperketat checklist spesifikasi sebelum implementasi sprint. Seluruh pihak telah tersinkronisasi dan target milestone tetap berjalan sesuai rencana.",
            "ask": "Kami akan terus memonitor delivery harian untuk memastikan timeline aman."
        },
        "en": {
            "title": "Reframing Team Misalignment & Friction",
            "bluf": "We experienced an initial alignment gap on the technical specs, which has now been fully reconciled.",
            "body": "This highlighted a valuable opportunity to tighten our pre-sprint documentation checklist. The workflow across teams is now synchronized and milestones remain on track.",
            "ask": "Daily progress tracking is active to safeguard the delivery schedule."
        }
    },
    "pushback_architecture": {
        "pattern": r"(ngawur|ambruk|jelek|shortcut|asal-asalan|maksa)",
        "id": {
            "title": "Menolak Shortcut Teknis yang Berisiko",
            "bluf": "Pendekatan tersebut efisien untuk rilis cepat, namun membawa trade-off risiko stabilitas pada database.",
            "body": "Rekomendasi teknis kami adalah menerapkan pola validasi atomik yang membutuhkan tambahan estimasi waktu 4 jam, namun memberikan garansi 100% konsistensi data transaksi saat lonjakan trafik.",
            "ask": "Apakah Bapak/Ibu menyetujui kami menggunakan pendekatan atomik tersebut?"
        },
        "en": {
            "title": "Technical Pushback against Risky Shortcuts",
            "bluf": "While that approach offers rapid initial delivery, it carries concurrency risk at peak traffic.",
            "body": "Our technical recommendation is to implement atomic validation: it requires 4 additional development hours, but guarantees 100% data integrity and eliminates transaction failure risks.",
            "ask": "Would you approve us proceeding with the atomic approach to protect system stability?"
        }
    }
}


def lint_prose(text: str) -> Dict[str, Any]:
    """Lints input text against corporate anti-slop rules, banned phrases, and structural heuristics."""
    findings = []
    text_lower = text.lower()
    
    # 1. Check English Banned Words
    for word in BANNED_WORDS_EN:
        pattern = r"\b" + re.escape(word) + r"\b"
        matches = list(re.finditer(pattern, text_lower))
        for m in matches:
            findings.append({
                "type": "banned_word_en",
                "severity": "error",
                "term": word,
                "position": m.start(),
                "message": f"Banned AI-slop vocabulary: '{word}'. Replace with concrete metrics or factual verbs."
            })
            
    # 2. Check English Banned Phrases
    for phrase_pat in BANNED_PHRASES_EN:
        matches = list(re.finditer(phrase_pat, text_lower))
        for m in matches:
            findings.append({
                "type": "banned_phrase_en",
                "severity": "error",
                "term": m.group(0),
                "position": m.start(),
                "message": f"Banned generic AI opener/contrast: '{m.group(0)}'. State point directly."
            })
            
    # 3. Check Indonesian Banned Words
    for word in BANNED_WORDS_ID:
        pattern = r"\b" + re.escape(word) + r"\b"
        matches = list(re.finditer(pattern, text_lower))
        for m in matches:
            findings.append({
                "type": "banned_word_id",
                "severity": "error",
                "term": word,
                "position": m.start(),
                "message": f"Banned Indonesian AI-slop translation: '{word}'."
            })
            
    # 4. Check Indonesian Banned Phrases
    for phrase_pat in BANNED_PHRASES_ID:
        matches = list(re.finditer(phrase_pat, text_lower))
        for m in matches:
            findings.append({
                "type": "banned_phrase_id",
                "severity": "error",
                "term": m.group(0),
                "position": m.start(),
                "message": f"Banned Indonesian robotic construction: '{m.group(0)}'."
            })
            
    # 5. Check Em-Dash Count
    em_dash_count = text.count("—") + text.count(" - ")
    if em_dash_count > 2:
        findings.append({
            "type": "em_dash_overuse",
            "severity": "warning",
            "term": "—",
            "position": 0,
            "message": f"Found {em_dash_count} em-dashes/hyphen dividers. Corporate standard allows maximum 1 per communication."
        })
        
    # 6. Check for Vague Qualitative Adverbs (without numbers)
    vague_adverbs = ["significantly", "greatly", "very fast", "sangat cepat", "banyak sekali", "luar biasa"]
    for adv in vague_adverbs:
        if adv in text_lower:
            findings.append({
                "type": "vague_metric",
                "severity": "warning",
                "term": adv,
                "position": text_lower.find(adv),
                "message": f"Vague qualitative claim: '{adv}'. Replace with specific percentage, latency, or numeric data."
            })

    # Calculate overall quality score (100 base, -15 per error, -5 per warning)
    score = 100
    for f in findings:
        if f["severity"] == "error":
            score -= 15
        elif f["severity"] == "warning":
            score -= 5
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "is_clean": len(findings) == 0,
        "issues_count": len(findings),
        "findings": findings
    }


def structure_1_3_1(problem: str, lang: str = "id") -> Dict[str, str]:
    """Generates a disciplined 1-3-1 escalation structure from a raw problem description."""
    if lang == "id":
        return {
            "format": "1-3-1 Escalation (Indonesian)",
            "output": f"""[Action Required] Eskalasi Hambatan Teknis: {problem[:40]}...

1. Masalah Inti (Core Problem):
   Kendala teridentifikasi pada: {problem.strip()}. Isu ini berisiko mempengaruhi stabilitas pengiriman jika tidak segera diputuskan langkah mitigasinya.

2. Opsi Solusi & Trade-Off:
   - Opsi A (Mitigasi Cepat / Penahanan): Menerapkan perbaikan taktis langsung.
     -> Trade-off: Menyelesaikan isu dalam 2 jam, namun menyisakan hutang teknis sementara.
   - Opsi B (Solusi Arsitektural / Rekomendasi): Merefaktor alur validasi dan menambah unit testing menyeluruh.
     -> Trade-off: Membutuhkan waktu 1 hari kerja, tetapi menjamin stabilitas 100% dan bebas regresi.
   - Opsi C (Penyesuaian Scope): Menunda rilis modul ini ke sprint berikutnya dan fokus pada fungsi inti.
     -> Trade-off: Risiko teknis nol, namun delivery fitur tertunda satu siklus sprint.

3. Rekomendasi Tim:
   Kami merekomendasikan Opsi B untuk melindungi reliabilitas sistem jangka panjang. Mohon persetujuan Bapak/Ibu agar tim dapat langsung mengeksekusi Opsi B hari ini."""
        }
    else:
        return {
            "format": "1-3-1 Escalation (English)",
            "output": f"""[Action Required] Escalation: {problem[:40]}...

1. Core Problem:
   Identified blocker: {problem.strip()}. This risks milestone timeline and system stability if mitigation is not finalized.

2. Solution Options & Trade-offs:
   - Option A (Rapid Containment): Deploy temporary tactical hotfix.
     -> Trade-off: Restores service in 2 hours, but leaves technical debt.
   - Option B (Architectural Hardening / Recommended): Refactor validation pipeline and establish automated regression guardrails.
     -> Trade-off: Requires 1 business day, but guarantees zero-regression and long-term stability.
   - Option C (Scope De-prioritization): Defer this module to next sprint to prioritize core delivery.
     -> Trade-off: Zero technical risk, but delays feature availability by 1 release cycle.

3. Recommendation:
   We recommend Option B to preserve production integrity. Unless you advise otherwise, the engineering team will execute Option B immediately."""
        }


def structure_blameless(issue: str, lang: str = "id") -> Dict[str, str]:
    """Generates a blameless 4-step post-mortem / incident communication."""
    if lang == "id":
        return {
            "format": "Blameless Incident Arc (Indonesian)",
            "output": f"""Update Status & Mitigasi Sistem:

- Dampak Insiden (Blast Radius):
  Terjadi anomali pemrosesan pada {issue.strip()} yang berdampak pada keterlambatan validasi data.

- Akar Masalah Sistemik (Systemic Root Cause):
  Analisis awal menunjukkan adanya celah pada validasi batas (boundary check) saat menerima beban transaksi tinggi, bukan kegagalan individu.

- Mitigasi Saat Ini (Immediate Containment):
  Tim telah menerapkan hotfix dan memulihkan service utama ke kondisi stabil 100%.

- Pencegahan Jangka Panjang (Long-Term Guardrail):
  Kami memasang automated integration test pada CI/CD pipeline dan menambahkan alert Prometheus agar anomali serupa terdeteksi secara otomatis di masa mendatang."""
        }
    else:
        return {
            "format": "Blameless Incident Arc (English)",
            "output": f"""System Status & Incident Mitigation Update:

- Blast Radius / Impact:
  Processing anomaly observed in {issue.strip()}, impacting automated data reconciliation.

- Systemic Root Cause:
  Root cause analysis identified a boundary validation gap under peak load conditions.

- Immediate Containment:
  The team deployed a containment patch; core services are fully verified and operational.

- Long-Term Guardrails:
  Automated load regression tests added to CI pipeline and threshold alerts configured to permanently prevent recurrences."""
        }


def structure_brag(outcome: str, metric: str, action: str, lang: str = "id") -> Dict[str, str]:
    """Generates Google XYZ achievement bullet point."""
    if lang == "id":
        return {
            "format": "Google XYZ Performance Bullet (Indonesian)",
            "output": f"Berhasil mencapai {outcome.strip()}, yang terukur melalui {metric.strip()}, dengan merancang dan mengimplementasikan {action.strip()}."
        }
    else:
        return {
            "format": "Google XYZ Performance Bullet (English)",
            "output": f"Accomplished {outcome.strip()}, as measured by {metric.strip()}, by implementing {action.strip()}."
        }


def transform_emotional_firewall(raw_text: str, lang: str = "id") -> Dict[str, Any]:
    """Transforms raw emotional or frustrated text into composed, executive corporate prose."""
    matched_scenario = None
    for key, scenario in FIREWALL_SCENARIOS.items():
        if re.search(scenario["pattern"], raw_text, re.IGNORECASE):
            matched_scenario = scenario
            break
            
    if not matched_scenario:
        # Default fallback
        matched_scenario = FIREWALL_SCENARIOS["sudden_scope"]
        
    template = matched_scenario[lang]
    formatted = f"{template['bluf']}\n\n{template['body']}\n\n{template['ask']}"
    
    return {
        "detected_scenario": matched_scenario[lang]["title"],
        "language": lang,
        "executive_version": formatted
    }


def main():
    parser = argparse.ArgumentParser(description="Corporate Firewall & Executive Communication CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: lint
    lint_parser = subparsers.add_parser("lint", help="Lint text against AI slop and corporate quality rules")
    lint_parser.add_argument("--text", type=str, help="Raw text string to lint")
    lint_parser.add_argument("--file", type=str, help="Path to text/markdown file to lint")
    lint_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    # Command: transform
    trans_parser = subparsers.add_parser("transform", help="Transform raw inputs into corporate formats")
    trans_parser.add_argument("--mode", choices=["firewall", "1-3-1", "blameless", "brag"], default="firewall",
                              help="Transformation mode")
    trans_parser.add_argument("--lang", choices=["id", "en"], default="id", help="Language target (id or en)")
    trans_parser.add_argument("--text", type=str, required=True, help="Input text or raw statement")
    trans_parser.add_argument("--metric", type=str, default="", help="Quantifiable metric (for brag mode)")
    trans_parser.add_argument("--action", type=str, default="", help="Engineering action (for brag mode)")
    trans_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "lint":
        raw_content = ""
        if args.text:
            raw_content = args.text
        elif args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                raw_content = f.read()
        else:
            print("Error: Specify either --text or --file to lint.", file=sys.stderr)
            sys.exit(1)

        result = lint_prose(raw_content)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== CORPORATE PROSE LINTER REPORT ===")
            print(f"Score: {result['score']}/100 | Clean: {result['is_clean']} | Issues: {result['issues_count']}")
            print("-" * 45)
            if result["is_clean"]:
                print("All checks passed! No AI-slop or corporate violations found.")
            else:
                for idx, issue in enumerate(result["findings"], 1):
                    sev = issue["severity"].upper()
                    print(f"[{idx}] [{sev}] {issue['message']}")

    elif args.command == "transform":
        if args.mode == "firewall":
            res = transform_emotional_firewall(args.text, lang=args.lang)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"=== EMOTIONAL FIREWALL TRANSFORMATION ===")
                print(f"Scenario: {res['detected_scenario']} ({args.lang.upper()})")
                print("-" * 45)
                print(res["executive_version"])
        elif args.mode == "1-3-1":
            res = structure_1_3_1(args.text, lang=args.lang)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"=== 1-3-1 ESCALATION STRUCTURE ===")
                print(res["output"])
        elif args.mode == "blameless":
            res = structure_blameless(args.text, lang=args.lang)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"=== BLAMELESS POST-MORTEM STRUCTURE ===")
                print(res["output"])
        elif args.mode == "brag":
            metric = args.metric if args.metric else "penurunan latensi 35% dan zero timeout"
            action = args.action if args.action else "optimalisasi arsitektur connection pool"
            res = structure_brag(args.text, metric, action, lang=args.lang)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"=== GOOGLE XYZ PERFORMANCE BULLET ===")
                print(res["output"])

if __name__ == "__main__":
    main()
