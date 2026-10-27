"""Generate index.pi files and the `rules:` list of each coding-standard anchor.

Usage: python3 -I gen_index.py <standards-dir> <orders-dir> <collection-dir>...

For each collection directory, rule files are every .pi file below it except
index.pi files and the standard's own file (the one declaring coding-standard).
Order comes from <orders-dir>/<collection>*.txt (concatenated in filename
order); rules missing from the order files are appended sorted by name.
"""
import os
import re
import sys

RULE_RE = re.compile(r"^export coding-rule (\w+)", re.M)
STD_RE = re.compile(r"^export coding-standard (\w+)", re.M)


def natural(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def collect(coll_dir):
    rules = {}  # name -> relative path without .pi
    std_name = std_file = None
    for root, _, files in os.walk(coll_dir):
        for f in files:
            if not f.endswith(".pi") or f == "index.pi":
                continue
            path = os.path.join(root, f)
            text = open(path, encoding="utf-8").read()
            m = STD_RE.search(text)
            if m:
                std_name, std_file = m.group(1), path
                continue
            for name in RULE_RE.findall(text):
                rules[name] = os.path.relpath(path, coll_dir)[:-3]
    return std_name, std_file, rules


def ordered(rules, orders_dir, coll):
    seen, out = set(), []
    for f in sorted(os.listdir(orders_dir)):
        if f == coll + ".txt" or re.fullmatch(re.escape(coll) + r"-\d+\.txt", f):
            for line in open(os.path.join(orders_dir, f), encoding="utf-8"):
                n = line.strip()
                if n in rules and n not in seen:
                    seen.add(n)
                    out.append(n)
    rest = sorted((n for n in rules if n not in seen), key=natural)
    return out, rest


def write_indexes(coll_dir):
    for root, dirs, files in os.walk(coll_dir):
        entries = sorted(f[:-3] for f in files if f.endswith(".pi") and f != "index.pi")
        subs = sorted(d for d in dirs if any(
            fn.endswith(".pi") for _, _, fs in os.walk(os.path.join(root, d)) for fn in fs))
        lines = [f"from ./{e} export *" for e in entries] + [f"from ./{d} export *" for d in subs]
        with open(os.path.join(root, "index.pi"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def write_rules_list(std_file, std_name, rules, names, coll_dir):
    text = open(std_file, encoding="utf-8").read()
    std_dir = os.path.dirname(std_file)
    imports = []
    for n in sorted(names, key=lambda n: rules[n]):
        rel = os.path.relpath(os.path.join(coll_dir, rules[n]), std_dir)
        if not rel.startswith("."):
            rel = "./" + rel
        imports.append(f"from {rel} import {n}")
    head, sep, _ = text.partition(f"export coding-standard {std_name}:")
    body = text[len(head) + len(sep):]
    body = re.sub(r"\n    rules:.*\Z", "", body, flags=re.S).rstrip("\n")
    use_lines = [l for l in head.splitlines() if l.startswith("use ")]
    comments = [l for l in head.splitlines() if l.startswith("//")]
    rules_block = "    rules:\n" + "".join(f"        - @{{{n}}}\n" for n in names) if names else "    rules: []\n"
    out = "\n".join(comments + use_lines) + "\n\n"
    if imports:
        out += "\n".join(imports) + "\n\n"
    out += f"export coding-standard {std_name}:{body}\n{rules_block}"
    open(std_file, "w", encoding="utf-8").write(out)


def main():
    standards, orders = sys.argv[1], sys.argv[2]
    for coll in sys.argv[3:]:
        coll_dir = os.path.join(standards, coll)
        std_name, std_file, rules = collect(coll_dir)
        if not std_file:
            print(f"{coll}: no coding-standard anchor", file=sys.stderr)
            continue
        names, rest = ordered(rules, orders, coll)
        write_rules_list(std_file, std_name, rules, names + rest, coll_dir)
        write_indexes(coll_dir)
        print(f"{coll}: {len(rules)} rules ({len(rest)} not in order file)")


main()
