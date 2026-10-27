"""Refresh the generated numbers and the standards table in README.md.

Usage, from the repository root, after `piton build`:

    python3 -I tools/readme_stats.py           # rewrite README.md in place
    python3 -I tools/readme_stats.py --check   # exit 1 if README.md is stale

README.md marks each generated value with HTML comments, which GitHub does
not render:

    <!-- stat:rules -->6,456<!-- /stat -->
    <!-- table:standards -->
    ...rows...
    <!-- /table -->

Stats: standards, rules, recommendations, library-files (rounded down to the
hundred) and library-mb. The library figures come from the compiled reference
tree, so run `piton build` first.
"""
import os
import re
import sys

STANDARDS = "spec/standards"
LIBRARY = ".claude/reference/standards"
README = "README.md"


def field(text, key):
    m = re.search(rf"^    {key}:(.*(?:\n        .*)*)", text, re.M)
    return " ".join(m.group(1).split()) if m else ""


def short_license(text):
    first = re.split(r"(?<=[a-z0-9)])\. ", text)[0].rstrip(".")
    if len(first) > 70:
        first = first[:67].rsplit(" ", 1)[0] + "…"
    return first


def collect():
    rows, rules, recs = [], 0, 0
    for d in sorted(os.listdir(STANDARDS)):
        path = os.path.join(STANDARDS, d)
        if not os.path.isdir(path) or d in ("lib", "skills"):
            continue
        std, n, r = None, 0, 0
        for root, _, files in os.walk(path):
            for f in files:
                if not f.endswith(".pi") or f == "index.pi":
                    continue
                text = open(os.path.join(root, f), encoding="utf-8").read()
                if re.search(r"^export coding-standard ", text, re.M):
                    std = text
                elif re.search(r"^export coding-rule ", text, re.M):
                    n += 1
                    if re.search(r"^    tags: \[recommendation\b", text, re.M):
                        r += 1
        if std is None:
            continue
        name = re.search(r"^export coding-standard (\w+)", std, re.M).group(1)
        count = f"{n:,}" + (f" ({r:,} recommendations)" if r else "")
        rows.append((field(std, "title"), field(std, "url"), name, d, count,
                     short_license(field(std, "license"))))
        rules += n
        recs += r
    rows.sort(key=lambda row: row[0].lower())
    return rows, rules, recs


def library():
    files, size = 0, 0
    for root, _, names in os.walk(LIBRARY):
        for f in names:
            if f.endswith(".md"):
                files += 1
                size += os.path.getsize(os.path.join(root, f))
    return files, size


def render(readme):
    rows, rules, recs = collect()
    files, size = library()
    if not files:
        sys.exit(f"{LIBRARY} is empty: run `piton build` first")
    stats = {
        "standards": f"{len(rows):,}",
        "rules": f"{rules:,}",
        "recommendations": f"{recs:,}",
        "library-files": f"{files // 100 * 100:,}",
        "library-mb": f"{round(size / 1_000_000)}",
    }
    table = "| Standard | Anchor | Folder | Rules | License |\n|---|---|---|---|---|\n" + "\n".join(
        f"| [{t}]({u}) | `{a}` | `{d}` | {c} | {lic} |" for t, u, a, d, c, lic in rows)

    def stat(m):
        key = m.group(1)
        if key not in stats:
            sys.exit(f"unknown stat in README: {key}")
        return f"<!-- stat:{key} -->{stats[key]}<!-- /stat -->"

    out = re.sub(r"<!-- stat:([\w-]+) -->.*?<!-- /stat -->", stat, readme)
    out, n = re.subn(r"(<!-- table:standards -->\n).*?(\n<!-- /table -->)",
                     lambda m: m.group(1) + table + m.group(2), out, flags=re.S)
    if n != 1:
        sys.exit("README needs exactly one <!-- table:standards --> block")
    return out


def main():
    readme = open(README, encoding="utf-8").read()
    out = render(readme)
    if "--check" in sys.argv[1:]:
        if out != readme:
            sys.exit("README.md is stale: run python3 -I tools/readme_stats.py")
        print("README.md is up to date")
        return
    if out != readme:
        open(README, "w", encoding="utf-8").write(out)
        print("README.md updated")
    else:
        print("README.md already up to date")


main()
