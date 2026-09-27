#!/usr/bin/env python3
"""Build alternate homepage layouts and drop them into preview/ as home-<name>.html."""
import pathlib, shutil, subprocess, re

SITE = pathlib.Path("/home/claude/pnp-hugo")
PREVIEW = SITE / "preview"
HUGO = "/home/claude/hugo"
LANDING = pathlib.Path("/home/claude/index-landing.md").read_text()

FEATURES = LANDING.split("---\n", 2)[2].replace('columns="4"', 'columns="3"')
FEATURES = re.sub(r'\{\{< feature icon="graduation-cap".*?\{\{< /feature >\}\}\n', '', FEATURES, flags=re.S)  # 3 cards fit the narrower column

PROFILE_BODY = """
<p class="text-center">Hands-on write-ups on red teaming, RF and software-defined radio, RFID, and hardware hacking.</p>
"""

LANDING_FRONT = LANDING.split("---\n", 2)[1]
VARIANTS = {
    "landing": {
        "label": "Landing",
        "blurb": "Editorial headline with your avatar, buttons, topic cards, recent posts.",
        "params": "",
        "front": LANDING_FRONT,
        "body": LANDING.split("---\n", 2)[2],
        "out": "index",
    },
    "combined": {
        "label": "Combined",
        "blurb": "Landing hero and avatar over the Signal photo, then the Operator post list.",
        "params": """[homepage]
  layout = "landing"
  showRecent = true
  showRecentItems = 6
  showMoreLink = true
  showMoreLinkDest = "posts"
  cardView = false
""",
        "front": LANDING_FRONT + 'heroImage: "img/hero-proxmark.png"\n',
        "body": LANDING.split("---\n", 2)[2],
    },
    "operator": {
        "label": "Operator",
        "blurb": "Profile first. Avatar, one-line bio, links, then a clean post list.",
        "params": """[homepage]
  layout = "profile"
  showRecent = true
  showRecentItems = 8
  showMoreLink = true
  showMoreLinkDest = "posts"
  cardView = false
[list]
  showCards = true
""",
        "front": 'title: "Pwn & Pivot"\n',
        "body": PROFILE_BODY,
    },
    "signal": {
        "label": "Signal",
        "blurb": "Full-bleed hardware photo behind your avatar, topic cards, then post cards.",
        "params": """[homepage]
  layout = "background"
  homepageImage = "img/hero-proxmark.png"
  layoutBackgroundBlur = true
  showRecent = true
  showRecentItems = 6
  showMoreLink = true
  showMoreLinkDest = "posts"
  cardView = true
""",
        "front": 'title: "Pwn & Pivot"\n',
        "body": FEATURES,
    },
    "dossier_unused": {
        "label": "Dossier",
        "blurb": "Banner image with your profile, then wide full-width post cards.",
        "params": """[homepage]
  layout = "hero"
  homepageImage = "img/hero-proxmark.png"
  showRecent = true
  showRecentItems = 6
  showMoreLink = true
  showMoreLinkDest = "posts"
  cardView = true
  cardViewScreenWidth = true
""",
        "front": 'title: "Pwn & Pivot"\n',
        "body": FEATURES,
    },
}

CUSTOM = {
    "terminal": ("Terminal", "A Pentoo shell session in a tmux pane. Posts are an ls -lt listing."),
    "spectrum": ("Spectrum", "A live SDR waterfall hero. Posts are tuned channels with word-count meters."),
    "hud": ("HUD", "The Proxmark photo graded to midnight, framed like a target lock, with post cards."),
}
for key, (label, blurb) in CUSTOM.items():
    VARIANTS[key] = {"label": label, "blurb": blurb, "front": 'title: "Pwn & Pivot"\n', "body": "",
                     "params": f'[homepage]\n  layout = "{key}"\n  showRecent = false\n'}
ORDER = ["terminal", "spectrum", "hud", "landing", "combined", "signal", "operator"]

ALL = [(v.get("out", f"home-{k}"), v["label"], v["blurb"]) for k, v in ((k, VARIANTS[k]) for k in ORDER)]


def switcher(current):
    chips = "".join(
        f'<a href="./{f}.html" style="padding:5px 11px;border-radius:999px;font:600 12px system-ui,sans-serif;'
        f'text-decoration:none;{"background:#dc2626;color:#fff;" if f == current else "color:#e4e4e7;border:1px solid #52525b;"}"'
        f' title="{b}">{l}</a>'
        for f, l, b in ALL
    )
    return (
        '<div id="layout-picker" style="position:fixed;left:50%;transform:translateX(-50%);'
        'bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:100;display:flex;gap:6px;align-items:center;'
        'flex-wrap:nowrap;overflow-x:auto;max-width:calc(100vw - 32px);padding:6px 8px;border-radius:999px;white-space:nowrap;'
        'background:rgba(12,12,14,.88);backdrop-filter:blur(10px);border:1px solid #3f3f46;'
        'box-shadow:0 10px 30px rgba(0,0,0,.5)">'
        + chips + "</div>"
    )


def inject(path, current):
    s = path.read_text()
    s = re.sub(r'<div id="layout-picker".*?</div></div>|<div id="layout-picker".*?</a></div>', "", s, flags=re.S)
    s = s.replace("</body>", switcher(current) + "</body>")
    path.write_text(s)


cfg_dir = pathlib.Path("/home/claude/preview-cfg")
index_md = SITE / "content/_index.md"
try:
    for name, v in VARIANTS.items():
        if name == "dossier_unused": continue
        env_dir = SITE / "config" / f"v-{name}"
        env_dir.mkdir(parents=True, exist_ok=True)
        (env_dir / "hugo.toml").write_text("uglyURLs = true\n")
        (env_dir / "params.toml").write_text(v["params"])
        index_md.write_text(f"---\n{v['front']}---\n{v['body']}")
        out = pathlib.Path(f"/home/claude/build-{name}")
        shutil.rmtree(out, ignore_errors=True)
        r = subprocess.run([HUGO, "--minify", "--destination", str(out), "--baseURL", "/",
                            "--environment", f"v-{name}"],
                           cwd=SITE, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-1500:]); raise SystemExit(1)
        home = (out / "index.html").read_text()
        # copy any home-specific assets (hero image, avatar renditions, extra JS) that preview lacks
        for ref in set(re.findall(r'(?:(?:src|href)=["]?|url\([\'"]?)\./([^"\'\s>)]+)', home)):
            ref = ref.split("#")[0]
            if ref.endswith(".html") or not ref:
                continue
            src, dst = out / ref, PREVIEW / ref
            if src.is_file() and not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)
                print("  + asset", ref)
        # directory links -> file links, same as the main preview
        home = home.replace('href=./posts/ ', 'href=./posts/index.html ').replace('href=./posts/>', 'href=./posts/index.html>')
        home = re.sub(r'href=\./about/([ >])', r'href=./about.html\1', home)
        home = re.sub(r'href=\./categories/([\w-]+)/([ >])', r'href=./categories/\1.html\2', home)
        home = re.sub(r'href=\./([ >])', r'href=./index.html\1', home)
        home = re.sub(r'href=\./([\w/-]+)/([ >])', lambda m: f'href=./{m.group(1)}/index.html{m.group(2)}' if (PREVIEW / m.group(1) / "index.html").exists() else (f'href=./{m.group(1)}.html{m.group(2)}' if (PREVIEW / (m.group(1) + ".html")).exists() else m.group(0)), home)
        (PREVIEW / f"{v.get('out', 'home-' + name)}.html").write_text(home)
        print("built", name)
finally:
    index_md.write_text(LANDING)
    for name in VARIANTS:
        shutil.rmtree(SITE / "config" / f"v-{name}", ignore_errors=True)

for f, _, _ in ALL:
    inject(PREVIEW / f"{f}.html", f)
print("switcher injected")
