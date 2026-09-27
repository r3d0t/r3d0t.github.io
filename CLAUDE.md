# Pwn & Pivot: Spectrum port (handoff)

This folder is a working Hugo prototype of r3d0t.github.io, ported from Jekyll/Chirpy to Hugo + Blowfish with a custom "Spectrum" design (live SDR waterfall, topics as frequency bands, posts as tuned channels). All 12 posts, images, the About page, categories and tags are already converted.

**Two zips:** `pnp-spectrum-1-site.zip` (everything else) and `pnp-spectrum-2-post-images.zip` (`static/assets/img/`, the screenshots used inside posts). Unzip both in the same place; they fill the same `pnp-hugo/` folder. Without part 2, post body images will be missing.

**The job:** move this into the `r3d0t/r3d0t.github.io` repo on a new branch, verify it, and open a PR. Do not touch `main` or the live site until the owner merges.

## Requirements

- Hugo **extended** 0.163.0 or newer (built and tested with 0.165.0). Check `themes/blowfish/config.toml` for the supported range.
- No Node or npm needed. Fonts are self-hosted in `static/fonts/`.

## Run it locally

```sh
hugo server            # http://localhost:1313
hugo --gc --minify     # production build into public/
```

## Port steps

1. In the repo, create a branch: `git checkout -b spectrum`.
2. Remove the Chirpy/Jekyll files from the branch (git history keeps them): `_config.yml`, `_data/`, `_includes/`, `_javascript/`, `_layouts/`, `_plugins/`, `_posts/`, `_sass/`, `_tabs/`, `Gemfile*`, `jekyll-theme-chirpy.gemspec`, `index.html`, `404.md`, `package.json`, `rollup.config.js`, `purgecss.js`, `eslint.config.js`, `.husky/`, `.markdownlint.json`, `.stylelintrc.json`, `tools/` (Chirpy's), `docs/`, `.nojekyll`, the old `.github/workflows/*` (Jekyll build), and `assets/` (old Chirpy assets; images now live in `static/assets/img/`). Keep `LICENSE` and `.git*` files you still want.
3. Copy everything from this folder into the repo root **except** `public/`, `preview/`, `resources/_gen/`.
4. Theme: `themes/blowfish/` is vendored (Blowfish commit `51a361e`, 2026-09-24, with `exampleSite/` and the README screenshots in `images/` removed). Either commit it as is (simplest), or replace it with a submodule: `git submodule add -b main https://github.com/nunocoracao/blowfish.git themes/blowfish`. The workflow already checks out submodules.
5. `hugo --gc --minify` must build with no errors. Then run the checks below.
6. Commit, push the `spectrum` branch, open a PR into `main`.
7. The owner goes live by merging the PR and setting **Settings → Pages → Source → GitHub Actions** (`.github/workflows/hugo.yml` builds and deploys). Switching the source back restores the old Jekyll site.

## Checks before opening the PR

- Old URLs still resolve: `/posts/<slug>/` for all 12 posts (note `/posts/AD-Hacking/` keeps its capitals via `url:` in front matter), `/categories/<name>/`, `/tags/<name>/`, `/about/`.
- RSS: Chirpy served `/feed.xml`; Hugo serves `/index.xml`. Add a redirect or an extra output so `/feed.xml` keeps working for existing subscribers.
- Every image in every post loads (post bodies reference `/assets/img/posts/...`, served from `static/`).
- Callouts render: Chirpy `{: .prompt-*}` blocks were converted to GitHub alert syntax (`> [!TIP]`, `> [!NOTE]`, `> [!WARNING]`, `> [!CAUTION]`).
- Search (Ctrl/Cmd K) works on the built site.
- Mobile width (390px): no sideways scroll on home, posts, categories, tags, about, a post.
- `prefers-reduced-motion`: waterfalls render one still frame and stop.

## Still to do

- **Comments (Giscus):** not wired yet. The old Chirpy config used: repo `r3d0t/r3d0t.github.io`, repo_id `R_kgDOQ5GDFA`, category `Comments`, category_id `DIC_kwDOQ5GDFM4C1YNW`, mapping `pathname`, reactions on. Add it as `layouts/partials/comments.html` (Blowfish renders this partial when `showComments = true` in `[article]` params). Mapping by pathname keeps existing threads attached because post paths are unchanged.
- **`static/assets/img/posts/rfid-hacking-2/NFC-URI Prefix Mapping`** is a plain text file with no extension that a post links to as an image. Check that post and fix the reference.
- **Homepage copy:** the lead sentence on the homepage was written during prototyping; the owner may replace it (`layouts/partials/home/spectrum.html`).
- Optional later: English + French (Hugo multilingual; add `languages.fr.toml` and `*.fr.md` files).

## Where things live

| What | File |
| --- | --- |
| Site config | `config/_default/*.toml` (homepage layout = `spectrum`, color scheme = `pnp`) |
| Topic frequencies (e.g. RFID 13.56 MHz, Burp TCP 8080) | `data/spectrum.yaml` |
| Waterfall engine (all canvases, hover-to-tune) | `assets/js/waterfall.js` |
| Global styles, fonts, Spectrum components | `assets/css/custom.css` |
| Midnight color scheme | `assets/css/schemes/pnp.css` |
| Homepage | `layouts/partials/home/spectrum.html` |
| Posts list / category + tag page / categories + tags index / About | `layouts/_default/list.html`, `term.html`, `terms.html`, `about.html` |
| Post page (theme copy + waterfall band) | `layouts/_default/single.html` |
| Shared partials (channel row, header strip, frequency lookup) | `layouts/partials/pnp/` |
| Head hook (loads waterfall.js, preloads fonts) | `layouts/partials/extend-head.html` |
| Alternate homepages from prototyping (unused) | `layouts/partials/home/terminal.html`, `hud.html`, `landing.html` |

`layouts/_default/single.html` is a copy of the theme's template with one block added at the top. If Blowfish is updated, re-copy the theme's `single.html` and re-add that block.

## Helper scripts (`tools/`)

- `convert.py`: the one-off Chirpy → Hugo post converter that produced `content/posts/`. Already run; kept for reference. Paths inside point at the original prototype machine.
- `build_preview.py`: builds a static preview with `.html` file links (for hosts without directory indexes). Not needed for GitHub Pages.
- `variants.py`: built the homepage layout comparisons. Not needed.
