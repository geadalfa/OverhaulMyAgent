---
name: exact-output-protocol
description: Use when User says "JANGAN memanggil tool", "tanpa tool", "tambahkan tepat satu baris", "hapus kalimat", or requests an exact final line or literal output. Enforces zero tool calls and literal output with no acknowledgments, preambles, or extra prose.
---

# Exact Output Protocol

When User asks for an exact output, deliver only that output.

## Rules

1. **Tool prohibition is absolute** — if User says "JANGAN memanggil tool", call no tools.
2. **No preamble** — never add "Baik", "Siap", "Tentu", "Tidak ada tool yang dipanggil", or any acknowledgment.
3. **No explanation** — unless User explicitly asks why; the requested line stands alone.
4. **Literal final line** — if a line must be at the end, it must be the last line, character-for-character, with no trailing commentary.
5. **No extra usage lines** — never add a Qoder usage line unless User requests it.
6. **Deleted phrase stays deleted** — if User says to remove a sentence from future responses, never include it again.
7. **One short conflict note only if unavoidable** — if a hard system requirement makes literal compliance impossible, state the conflict in one sentence, then comply as far as possible.

## Examples

**Wrong**
> Baik, tidak ada tool yang dipanggil.
>
> Qoder usage · …

**Right**
> Qoder usage · …

**Wrong**
> Siap, Gemi hapus kalimat itu. Berikut jawabannya: …

**Right**
> <jawaban yang diminta, tanpa preamble>

## Scope

Apply only to exact-output requests. Normal tasks keep the usual brief progress updates and explanations.
