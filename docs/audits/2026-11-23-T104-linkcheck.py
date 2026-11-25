"""T-104 CK-LINK: check repo links in key files against `git ls-files`. Run: python -I <this file> [--baseline F | --compare F]. Exit 0 unless --compare finds new broken entries."""
import json, re, subprocess, sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
FILES = ["README.md", "CLAUDE.md", "redesign/README.md", "redesign/SHOWCASE.md",
         "redesign/site/index.html", "redesign/site/app.html",
         "redesign/qp/A/drawings/out/links.json"]
BLOB = re.compile(r"blob/redesign/v1/([^\s\"'<>)\]#?]+)")
HTML = re.compile(r"""(?:href|src)\s*=\s*["']([^"']*)["']""", re.I)
MD = re.compile(r"\]\(\s*<?([^)\s>]+)")
SKIP = ("http://", "https://", "mailto:", "#", "data:", "javascript:", "//")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    files = set(out.decode("utf-8").split("\0")) - {""}
    dirs = set()
    for f in files:
        p = PurePosixPath(f)
        for a in p.parents:
            dirs.add(str(a))
    return files, dirs


def norm(path):
    parts = []
    for s in path.split("/"):
        if s in ("", "."):
            continue
        if s == "..":
            if not parts:
                return None
            parts.pop()
        else:
            parts.append(s)
    return "/".join(parts)


def main():
    files, dirs = tracked()
    broken = []
    for rel in FILES:
        fp = ROOT / rel
        if not fp.is_file():
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        targets = set()
        for m in BLOB.finditer(text):
            targets.add(norm(unquote(m.group(1))))
        rels = HTML.findall(text) + MD.findall(text)
        if rel.endswith(".json"):
            rels = []
        base = str(PurePosixPath(rel).parent)
        for r in rels:
            r = r.strip()
            if not r or r.lower().startswith(SKIP):
                continue
            r = unquote(re.split(r"[#?]", r, maxsplit=1)[0])
            if not r:
                continue
            if r.startswith("/"):
                targets.add(norm(r))
            else:
                targets.add(norm((base + "/" if base != "." else "") + r))
        for t in sorted(targets, key=lambda x: (x is None, x or "")):
            if t is None:
                broken.append(f"{rel} -> <outside repo>")
            elif t == "" or t in files or t in dirs:
                continue
            else:
                broken.append(f"{rel} -> {t}")
    for b in broken:
        print(b)
    print(f"{len(broken)} broken")
    args = sys.argv[1:]
    rc = 0
    if "--baseline" in args:
        Path(args[args.index("--baseline") + 1]).write_text("\n".join(broken) + ("\n" if broken else ""), encoding="utf-8")
    if "--compare" in args:
        base = set(Path(args[args.index("--compare") + 1]).read_text(encoding="utf-8").split("\n")) - {""}
        new = [b for b in broken if b not in base]
        if new:
            print("NEW broken:")
            for n in new:
                print(n)
            rc = 1
    print(len(broken))
    return rc


sys.exit(main())
