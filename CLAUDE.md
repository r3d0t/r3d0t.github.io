# Pwn & Pivot — site guide

r3d0t.github.io is a Hugo site on the [Blowfish](https://blowfish.page) theme with a custom
"Spectrum" design: a live SDR waterfall homepage, topics shown as frequency bands, and posts
as tuned channels. It's live at https://r3d0t.github.io/, built and deployed from `main` by
GitHub Actions.

History: ported from Jekyll/Chirpy in Sept 2026. The old Jekyll history is still in git, and
the last Jekyll commit is tagged `jekyll-final`.

## Requirements

- Hugo **extended** 0.163.0+ (built and tested with 0.165.0, which the CI workflow pins).
  Build it in userspace so local matches CI:
  ```sh
  CGO_ENABLED=1 go install -tags extended github.com/gohugoio/hugo@v0.165.0
  ```
- No Node or npm. Fonts are self-hosted in `static/fonts/`.

## Run locally

```sh
hugo server            # http://localhost:1313, live reload
hugo --gc --minify     # production build into public/
```

## Deploy

- Push to `main` → `.github/workflows/hugo.yml` builds with Hugo extended and deploys to Pages.
- Always work on a branch, open a PR, and merge to go live. Don't push straight to `main`.
- Rollback: revert the merge commit, or flip **Settings → Pages → Source**.

## Common edits

- **Add a post:** `content/posts/<slug>/index.md` (a page bundle). Featured/hero image =
  `feature.png` inside the bundle; body images go under `static/assets/img/posts/<slug>/` and
  are referenced as `/assets/img/posts/<slug>/...`. The date must not be in the future or the
  post is skipped (`buildFuture = false`) — mind the `-0400` timezone.
- **Topic frequency / label / position:** `data/spectrum.yaml`, one entry per category slug.
  Unknown categories get a stable hashed position automatically, so nothing breaks if you
  forget to add one.
- **Which bands show on the homepage:** the `slice` list in
  `layouts/partials/home/spectrum.html`; long names are shortened in the `cond` right below it
  (e.g. "Software Defined Radio" is displayed as "Wireless & SDR").
- **Channel numbers:** assigned automatically in `layouts/partials/pnp/channel.html` as each
  post's chronological rank (oldest = CH01, newest = highest). Nothing to maintain by hand.
- **Colours:** the `--sx-*` tokens at the top of `assets/css/custom.css`; the theme palette is
  in `assets/css/schemes/pnp.css`.
- **Homepage lead sentence:** `layouts/partials/home/spectrum.html`.

## URL compatibility (don't break these)

- Posts live at `/posts/<slug>/` (`/posts/AD-Hacking/` keeps its capitals via `url:` in front
  matter).
- `/archives/` is aliased to `/posts/`. RSS is at `/feed.xml` (`baseName` in `hugo.toml`).
  `/categories/certifications/` is aliased to `/categories/blog/` after that rename.

## Still to do

- **Comments (Giscus):** not wired yet. Old Chirpy config: repo `r3d0t/r3d0t.github.io`,
  repo_id `R_kgDOQ5GDFA`, category `Comments`, category_id `DIC_kwDOQ5GDFM4C1YNW`, mapping
  `pathname`, reactions on. Add it as `layouts/partials/comments.html` (Blowfish renders this
  partial when `showComments = true` in `[article]`). Mapping by pathname keeps existing
  threads attached because post paths are unchanged.
- **`static/assets/img/posts/rfid-hacking-2/NFC-URI Prefix Mapping`** is an extensionless text
  file that `rfid-hacking-pt2` links to as an image — fix the reference.
- **Categories cleanup:** "Blog" is currently a catch-all (cert reviews + meta posts), and
  "Wireless Security" exists in `spectrum.yaml` but has no posts yet.

## Where things live

| What | File |
| --- | --- |
| Site config | `config/_default/*.toml` (homepage layout = `spectrum`, color scheme = `pnp`) |
| Topic frequencies | `data/spectrum.yaml` |
| Waterfall engine (all canvases, hover-to-tune) | `assets/js/waterfall.js` |
| Global styles, fonts, Spectrum components | `assets/css/custom.css` |
| Color scheme (theme palette) | `assets/css/schemes/pnp.css` |
| Homepage | `layouts/partials/home/spectrum.html` |
| Posts list / tag + category pages / About | `layouts/_default/list.html`, `term.html`, `terms.html`, `about.html` |
| Post page (theme copy + waterfall band) | `layouts/_default/single.html` |
| Channel row, header strip, frequency lookup | `layouts/partials/pnp/` |
| Head hook (loads waterfall.js, preloads fonts) | `layouts/partials/extend-head.html` |
| Unused prototype homepages | `layouts/partials/home/terminal.html`, `hud.html`, `landing.html` |

`layouts/_default/single.html` is a copy of the theme's template with one PnP block added at
the top (the waterfall strip). If Blowfish is updated, re-copy the theme's `single.html` and
re-add that block — it's fenced with `PnP addition` comments.

## Helper scripts (`tools/`)

- `convert.py`: the one-off Chirpy → Hugo post converter that produced `content/posts/`.
  Already run; kept for reference. Paths inside point at the original prototype machine.
- `build_preview.py`, `variants.py`: prototyping helpers, not needed for GitHub Pages.
