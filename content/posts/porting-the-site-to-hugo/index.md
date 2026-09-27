---
title: Porting My Site from Jekyll to Hugo
description: Why I moved this blog off Jekyll/Chirpy onto Hugo with a custom SDR "Spectrum" design, and how I built the live waterfall, the frequency bands, and the channel log without breaking any old URLs.
summary: Why I moved this blog off Jekyll/Chirpy onto Hugo with a custom SDR "Spectrum" design, and how I built the live waterfall, the frequency bands, and the channel log without breaking any old URLs.
date: 2026-09-26 20:00:00 -0400
slug: porting-the-site-to-hugo
categories:
- Blog
tags:
- hugo
- jekyll
- static site
- web
- blowfish
weight: 1
featured: true
---

This is the story of rebuilding this site. It started on Jekyll with the Chirpy theme,
and I moved it over to Hugo with a custom look I'm calling "Spectrum": the homepage is a
live SDR waterfall, topics are frequency bands, and each post is a channel you tune into.

![The homepage: waterfall, title, topic bands, channel log](/assets/img/posts/porting-the-site-to-hugo/home-desktop.png)

### Why move off Jekyll

Chirpy is a good theme and it served me fine. But two things kept nagging me:

- Every local build meant Ruby, `bundle`, and a Gemfile.lock that liked to drift. On a
  Gentoo box that is more of a fight than it should be.
- I wanted the site to actually look like the stuff I write about. RF, SDR, RFID. A
  generic blog theme wasn't saying any of that.

Hugo is a single binary, builds the whole site in under a second, and the templating is
flexible enough to build something weird on top of a solid theme. I picked
[Blowfish](https://blowfish.page) as the base because it handles all the boring parts
(SEO, taxonomies, search, RSS) and lets me override just the pages I care about.

> [!NOTE]
> The plan the whole time was: don't reinvent a blog engine, just paint over a good one.
> Blowfish does the plumbing, my custom templates do the paint.

### Getting Hugo (the extended build)

Blowfish needs Hugo *extended*, and it wants a recent version. Portage only had an older
one, and the GitHub Actions workflow I was going to deploy with pins 0.165. I didn't want
the version I build with locally to be different from the one that builds in CI, so I
skipped the package manager and built it straight from source with Go:

```bash
CGO_ENABLED=1 go install -tags extended github.com/gohugoio/hugo@v0.165.0
~/go/bin/hugo version    # should say +extended
```

`CGO_ENABLED=1` and the `extended` tag are what pull in the SCSS/WebP support. No root
needed, it lands in `~/go/bin`. Now local and CI are building with the exact same Hugo.

### The idea: the site as a spectrum

Here's the mental model I built everything around.

- The **homepage** is a receiver. There's a waterfall scrolling behind the title with a
  frequency ruler sitting around 1090 MHz (that's ADS-B, the aircraft band, my little
  nod to the airplane tracker post).
- **Topics are bands.** Each one gets a real-ish frequency: RFID sits at 13.56 MHz because
  that's the actual NFC frequency, Burp gets TCP 8080, LDAP gets TCP 389, and so on.
- **Posts are channels.** The post list looks like a scanner log: CH01, CH02, a date, the
  band, and a little signal-strength bar (which is really just word count).

Hover any band or channel and the waterfall tunes to it. An amber line slides over and a
spike lights up at that frequency. It's fake, but it's the good kind of fake.

![The posts list, styled as a scanner channel log](/assets/img/posts/porting-the-site-to-hugo/posts-list.png)

### Building the waterfall

This was the fun part. I didn't want a video or a gif, I wanted it drawn live so it's tiny
and never repeats. It's one small script, about 80 lines.

The trick to a waterfall is you never redraw the old lines. Each frame you shove the whole
image down by one pixel and only draw a fresh line at the top:

```js
ctx.drawImage(s.c, 0, 0, W, H - 1, 0, 1, W, H - 1); // shift everything down 1px
// ...then compute and stamp one new row at y=0
```

For that new row, each pixel is background noise plus a few "carriers." A carrier is just a
bright bump at a position, drawn with a Gaussian so it's bright in the middle and fades at
the edges:

```js
const dx = (fx - drift) / k.w;
v += k.a * 210 * Math.exp(-dx * dx);   // bright bump centred on the carrier
```

Then the strength value gets turned into a colour through a lookup table that ramps from
near-black navy up through blue, red, amber, and finally white for the hottest signal.

A few things I made sure of because they matter more than the effect itself:

- If the visitor has **reduce-motion** turned on, it paints one still frame and stops. No
  exceptions.
- It only animates canvases that are **actually on screen**, and it pauses when the tab is
  hidden. No point cooking someone's battery for a background.
- It renders at **half resolution** internally. On a waterfall you genuinely cannot tell,
  and it's much cheaper.

### One file to map topics to frequencies

I didn't want frequency numbers hardcoded all over the templates. So there's one data file
that maps every category to its label and its position on the waterfall (0 is the far left,
1 is the far right):

```yaml
categories:
  rfid:                   { freq: "13.56 MHz · NFC",   pos: 0.34 }
  software-defined-radio: { freq: "24 MHz – 1.7 GHz",  pos: 0.62 }
  burp-suite:             { freq: "TCP 8080",          pos: 0.22 }
```

A little partial looks a topic up in there. If a topic isn't listed, it hashes the name
into a stable position so it still lands somewhere sensible instead of crashing. That means
I can add a post in a brand new category and the site won't break, it just won't have a
hand-picked frequency until I add one.

> [!TIP]
> If you want to give a topic a proper frequency, that one data file is the only thing you
> touch. Everything else reads from it.

### Bringing the posts over

All the posts came over from Chirpy. The content was basically fine, but two things needed
converting:

- **Callouts.** Chirpy uses `{: .prompt-tip}` style blocks. Hugo uses `> [!TIP]`,
  `> [!NOTE]`, `> [!WARNING]`. Those got swapped over.
- **Image paths.** The screenshots inside posts all live under `static/assets/img/posts/`
  so the old links keep working without touching a single post body.

Each post also gets its own little tuned waterfall strip above the hero image, set to that
post's band. Small touch, but it ties the whole thing together.

![A single post with its tuned strip up top](/assets/img/posts/porting-the-site-to-hugo/post-single.png)

### Not breaking the old links

This was the part I refused to get wrong. The site has been up for a while, search engines
know the URLs, and I've linked posts to each other. Breaking those on a redesign is how you
throw away every bit of SEO you built.

Hugo builds posts at `/posts/<slug>/`, same as Chirpy did, so those all matched already.
But I still checked every single one instead of assuming:

```bash
for f in _posts/*.md; do
  t=$(basename "$f" .md | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}-//')  # strip the date
  [ -f "public/posts/$t/index.html" ] && echo "OK $t" || echo "BROKEN $t"
done
```

They all came back OK. Two other things did need fixing:

- **`/archives/`** didn't exist in Hugo. I pointed it at the posts list with an alias in the
  section's `_index.md`:
  ```yaml
  aliases: ["/archives/"]
  ```
- **The RSS feed.** Chirpy served it at `/feed.xml`, Hugo serves `/index.xml` by default.
  Anyone subscribed would have silently lost the feed. One setting fixes it:
  ```toml
  [outputFormats.RSS]
    baseName = "feed"
  ```
  Heads up if you copy this: that renames the feed everywhere, so any link that pointed at
  `/index.xml` now needs to point at `/feed.xml`. I had one in the author links that bit me.

### The About page and mobile

The About page got the same treatment: an "Operator profile" header over the waterfall,
the bio on the left, and a sidebar of bands and links on the right.

![The About page](/assets/img/posts/porting-the-site-to-hugo/about.png)

And because half of anyone's traffic is on a phone, I checked every page at 390px wide for
sideways scroll. The bands go from four columns to two, the signal meter on channel rows
drops off, and the sidebar slides under the text.

![The homepage on a phone](/assets/img/posts/porting-the-site-to-hugo/home-mobile.png)

### Deploying

No more Ruby in CI. The whole thing is a single GitHub Actions workflow that installs Hugo
extended, builds, and pushes to Pages on every push to `main`. The nice part: if it ever
goes wrong, flipping the Pages source back to the old branch restores the Jekyll site,
because that history is still in the repo.

### What I'd tell myself starting over

- Build with the **same Hugo version as CI** from day one. Chasing a "works locally, breaks
  in Actions" bug over a version mismatch is a waste of an evening.
- Put the moving numbers in **one data file**. I'm glad it exists every time I add a post.
- Check the **old URLs** before you're proud of the new design, not after someone emails you
  that their bookmark 404s.

That's the build. The effect is a gimmick, sure, but it's a gimmick that matches what the
site is about, and everything under it is a normal, fast, boring-in-a-good-way Hugo site.
