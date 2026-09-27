#!/usr/bin/env python3
"""Build a static preview that works without directory indexes (for the artifact host)."""
import pathlib, re, shutil, subprocess, os, urllib.parse

SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = SITE / "preview"
env = SITE / "config/preview"
env.mkdir(parents=True, exist_ok=True)
(env / "hugo.toml").write_text("uglyURLs = true\nrelativeURLs = true\n")
shutil.rmtree(OUT, ignore_errors=True)
r = subprocess.run(["hugo", "--gc", "--minify", "--destination", str(OUT), "--baseURL", "/", "--environment", "preview"],
                   cwd=SITE, capture_output=True, text=True)
print(r.stdout[-400:], r.stderr[-2000:])
if r.returncode: raise SystemExit(1)
root = OUT.resolve()

# drop redirect stubs, feeds, empty taxonomies
for f in list(root.rglob("*.html")):
    if "http-equiv=refresh" in f.read_text(errors="ignore")[:600]: f.unlink()
for f in root.rglob("*.xml"): f.unlink()
for d in ("authors", "series"): shutil.rmtree(root / d, ignore_errors=True)
for f in root.rglob(".DS_Store"): f.unlink()

def fix(m, base):
    attr, q, url = m.group(1), m.group(2), m.group(3)
    if re.match(r"^(https?:|mailto:|#|data:|javascript:)", url) or not url.endswith("/"):
        return m.group(0)
    tgt = (base / url).resolve()
    for cand in (tgt / "index.html", pathlib.Path(str(tgt).rstrip("/") + ".html")):
        if cand.exists():
            return f"{attr}={q}{os.path.relpath(cand, base)}{q}"
    return m.group(0)

for h in root.rglob("*.html"):
    s = h.read_text()
    new = re.sub(r'(href)=("?)([^"\s>]+)\2(?=[\s>])', lambda m: fix(m, h.parent), s)
    if new != s: h.write_text(new)

# prune files nothing references
refs = set()
for h in root.rglob("*"):
    if h.suffix in (".html", ".css", ".js", ".json", ".webmanifest"):
        s = h.read_text(errors="ignore")
        for u in re.findall(r'(?:href|src|srcset)=["\']?([^"\'\s>]+)', s) + re.findall(r'url\(([^)]+)\)', s):
            u = urllib.parse.unquote(u.split("#")[0].split("?")[0].strip("\"'"))
            try: refs.add((h.parent / u).resolve())
            except Exception: pass
        for u in re.findall(r'srcset=["\']([^"\']+)', s):
            for part in u.split(","):
                p = part.strip().split(" ")[0]
                if p: refs.add((h.parent / urllib.parse.unquote(p)).resolve())
n = 0
for f in list(root.rglob("*")):
    if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg") and f.resolve() not in refs:
        f.unlink(); n += 1
for d in sorted(root.rglob("*"), reverse=True):
    if d.is_dir() and not any(d.iterdir()): d.rmdir()
shutil.rmtree(env, ignore_errors=True)
files = [p for p in root.rglob("*") if p.is_file()]
print("pruned", n, "files:", len(files))
