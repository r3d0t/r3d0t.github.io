#!/usr/bin/env python3
"""Port Chirpy (Jekyll) posts to Blowfish (Hugo) page bundles."""
import re, shutil, pathlib, yaml

SRC = pathlib.Path("/home/claude/r3d0t/r3d0t.github.io")
DST = pathlib.Path("/home/claude/pnp-hugo")
ALERT = {"tip": "TIP", "info": "NOTE", "warning": "WARNING", "danger": "CAUTION"}


def split_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return yaml.safe_load(m.group(1)), m.group(2)


def convert_callouts(body):
    """Chirpy: '> text' lines followed by '{: .prompt-x}'. Hugo: '> [!X]' header."""
    lines = body.split("\n")
    out = []
    for line in lines:
        m = re.match(r"^\s*\{:\s*\.prompt-(\w+)\s*\}\s*$", line, re.I)
        if not m:
            out.append(line)
            continue
        kind = ALERT.get(m.group(1).lower(), "NOTE")
        # walk back to the start of the blockquote just emitted
        i = len(out) - 1
        while i >= 0 and out[i].strip() == "":
            i -= 1
        end = i
        while i >= 0 and out[i].lstrip().startswith(">"):
            i -= 1
        start = i + 1
        if start <= end:
            out.insert(start, f"> [!{kind}]")
    return "\n".join(out)


for post in sorted((SRC / "_posts").glob("*.md")):
    fm, body = split_fm(post.read_text())
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post.stem)
    bundle = DST / "content/posts" / slug
    bundle.mkdir(parents=True, exist_ok=True)

    img = fm.get("image")
    if isinstance(img, dict):
        img = img.get("path")
    if img:
        src_img = SRC / img.lstrip("/")
        if src_img.exists():
            shutil.copy(src_img, bundle / ("feature" + src_img.suffix.lower()))

    date = fm["date"]
    new = {
        "title": fm["title"],
        "description": fm.get("description", "").strip(),
        "summary": fm.get("description", "").strip(),
        "date": date.isoformat() if hasattr(date, "isoformat") else str(date),
        "slug": slug,
        "categories": fm.get("categories", []),
        "tags": fm.get("tags", []),
    }
    if fm.get("pin"):
        new["weight"] = 1
        new["featured"] = True

    body = convert_callouts(body)
    fm_text = yaml.safe_dump(new, sort_keys=False, allow_unicode=True, width=1000)
    (bundle / "index.md").write_text(f"---\n{fm_text}---\n{body}")
    print("ported", slug, "(feature image)" if img else "")

# About page
fm, body = split_fm((SRC / "_tabs/about.md").read_text())
(DST / "content/about.md").write_text(
    "---\ntitle: \"$ whoami\"\nshowDate: false\nshowReadingTime: false\nshowWordCount: false\n"
    "showAuthor: false\nshowTableOfContents: false\n---\n" + body
)
print("ported about")
