"""Flag rule files whose prose or code repeats fetched source text.

Usage: python3 -I overlap.py <scratchpad> <standards-dir> [collection ...]

Corpus: every .html/.htm/.md/.txt/.rst/.adoc/.markdown file under the
scratchpad, except the generators' own files (.py) and orders/.
Prose check: any run of N consecutive words (default 10) in a rule's
title/statement/rationale/exceptions that also appears in the corpus.
Code check: any code line of 40+ characters that appears verbatim
(whitespace-normalized) in the corpus.
"""
import html
import os
import re
import sys

N = int(os.environ.get("OVERLAP_N", "10"))
TEXT_EXT = {".html", ".htm", ".md", ".txt", ".rst", ".adoc", ".markdown", ".xhtml"}


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def load_corpus(root):
    shingles, lines = set(), set()
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ("orders", "tools", "__pycache__", "cppfix", ".claude", "consumer", "backup") and not (x.startswith("cr") and x[2:].isdigit() or x == "cr")]
        for f in files:
            own = f in ("mylines.txt", "mine.txt", "my-ids.txt", "files.txt", "used.txt") or f.endswith("-retitle.txt") or f.startswith("order")
            if own or d.endswith("gen-owasp-asvs/data") or f in ("BRIEF.md", "COMMON.md") or "report" in f or os.path.splitext(f)[1].lower() not in TEXT_EXT:
                continue
            try:
                raw = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for line in raw.splitlines():
                norm = " ".join(html.unescape(line).split())
                if len(norm) >= 40:
                    lines.add(norm)
            text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
            w = words(text)
            for i in range(len(w) - N + 1):
                shingles.add(hash(tuple(w[i:i + N])))
    return shingles, lines


FIELD_RE = re.compile(r"^    (\w+):(.*)$")


def fields(path):
    out, key = {}, None
    for line in open(path, encoding="utf-8"):
        m = FIELD_RE.match(line.rstrip("\n"))
        if m:
            key = m.group(1)
            out[key] = [m.group(2).strip()]
        elif key and line.startswith("        "):
            out[key].append(line[8:].rstrip("\n"))
    return out


def main():
    root, standards = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    shingles, lines = load_corpus(root)
    flagged = 0
    for coll in sorted(os.listdir(standards)):
        cdir = os.path.join(standards, coll)
        if not os.path.isdir(cdir) or coll in ("lib", "skills") or (only and coll not in only):
            continue
        for d, _, files in os.walk(cdir):
            for f in sorted(files):
                if not f.endswith(".pi") or f == "index.pi":
                    continue
                path = os.path.join(d, f)
                fl = fields(path)
                if "ruleId" not in fl:
                    continue
                hits = []
                for k in ("title", "statement", "rationale", "exceptions"):
                    w = words(" ".join(fl.get(k, [])))
                    run = [" ".join(w[i:i + N]) for i in range(len(w) - N + 1)
                           if hash(tuple(w[i:i + N])) in shingles]
                    if run:
                        hits.append(f"{k}: \"{run[0]}\"" + (f" (+{len(run) - 1})" if len(run) > 1 else ""))
                for k in ("noncompliant", "compliant"):
                    for line in fl.get(k, []):
                        norm = " ".join(line.split())
                        if len(norm) >= 40 and norm in lines:
                            hits.append(f"{k} line: {norm[:70]}")
                            break
                if hits:
                    flagged += 1
                    print(os.path.relpath(path, standards))
                    for h in hits:
                        print("    " + h)
    print(f"{flagged} files flagged")


main()
