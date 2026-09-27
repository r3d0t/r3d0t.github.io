/* ==========================================================================
   PnP spectrum waterfall
   --------------------------------------------------------------------------
   Draws the fake SDR "waterfall" you see behind the homepage title, on the
   About header, and in the thin strip on every post. It is not real radio,
   it just paints noise + a few bright "carriers" scrolling downward so it
   feels like a live capture.

   How to use it from HTML:
     <canvas data-waterfall data-carriers="0.5,0.3"></canvas>
       - any <canvas data-waterfall> on the page turns into a waterfall
       - data-carriers  = comma list of bright spikes, 0 = far left, 1 = far right
       - data-noise     = background noise multiplier (default 1; lower = calmer)

   Highlighting a channel (the amber line that slides in on hover):
     window.pnpTune(0.62, "24 MHz - 1.7 GHz")   // light up a spot + set the label
     window.pnpTune(null)                        // clear it

   This file is minified by Hugo before it ships, so comment as much as you want,
   none of it reaches the browser.
   ========================================================================== */
(() => {
  // If the visitor has "reduce motion" turned on, we paint one still frame and never animate.
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Colour ramp for the waterfall, from quietest to loudest signal:
  // near-black navy -> blue -> brighter blue -> red -> amber -> near-white.
  // Each entry is [R, G, B]. Change these to recolour the whole effect.
  const stops = [[3,5,13],[18,28,90],[60,70,200],[255,59,78],[255,181,71],[255,245,230]];

  // Pre-compute a 256-step lookup table (LUT) by smoothly blending between the stops above.
  // Later we turn a signal strength 0..255 into a colour with one array lookup instead of maths.
  const lut = Array.from({ length: 256 }, (_, i) => {
    const x = i / 255 * (stops.length - 1),          // where this step lands on the 0..(stops-1) ramp
          k = Math.min(stops.length - 2, Math.floor(x)), // which pair of stops we sit between
          f = x - k;                                  // how far between that pair (0..1)
    // linear blend each of R,G,B between stop k and stop k+1
    return stops[k].map((v, j) => Math.round(v + (stops[k + 1][j] - v) * f));
  });

  let tuned = null;           // the currently highlighted channel: { pos, strength } or null
  const falls = [];           // every waterfall canvas we're animating on this page

  // ---- set up one canvas ---------------------------------------------------
  function make(c) {
    const ctx = c.getContext('2d', { alpha: false }); // 2D drawing surface, opaque (faster)

    // Read data-carriers ("0.5,0.3") into an array of numbers, dropping anything invalid.
    const seed = (c.dataset.carriers || '0.5').split(',').map(Number).filter(n => !isNaN(n));

    // Turn each carrier position into a full carrier object. w = width of the spike,
    // a = brightness/amplitude, burst = phase offset so they don't all blink together.
    // The [..][i % 6] bits just cycle through 6 preset widths/amplitudes so stacked carriers vary.
    const carriers = seed.map((f, i) => ({ f, w: [.006, .004, .012, .003, .02, .002][i % 6], a: [1, .6, .55, .8, .35, .9][i % 6], burst: (i * .37) % 1 }));

    const noise = Number(c.dataset.noise || 1); // background hiss level from data-noise

    // s = the full state for this one canvas. t is the frame counter (drives the animation).
    const s = { c, ctx, carriers, noise, W: 0, H: 0, row: null, t: 0, visible: true };

    // (Re)size the canvas to match its box on screen and pre-fill it with frames.
    s.size = () => {
      const r = c.getBoundingClientRect(), k = Math.min(devicePixelRatio || 1, 1.5); // cap DPR at 1.5 for speed
      // Internal resolution is half the CSS size (the "/ 2"): cheaper to draw, still looks fine.
      s.W = c.width = Math.max(160, Math.floor(r.width * k / 2)); s.H = c.height = Math.max(24, Math.floor(r.height * k / 2));
      ctx.fillStyle = '#03050d'; ctx.fillRect(0, 0, s.W, s.H);  // paint the background colour first
      s.row = ctx.createImageData(s.W, 1);                       // a reusable 1px-tall strip we redraw each frame
      for (let i = 0; i < s.H; i++) step(s);                     // pre-roll a full screen so it starts already "running"
    };
    s.size();

    // Re-fit if the canvas changes size (window resize, layout shift).
    new ResizeObserver(() => s.size()).observe(c);
    // Only animate while the canvas is actually on screen (saves battery when scrolled away).
    new IntersectionObserver(([e]) => { s.visible = e.isIntersecting; }).observe(c);
    falls.push(s);
  }

  // ---- draw one new line and scroll everything down -----------------------
  function step(s) {
    const { ctx, W, H, row } = s; s.t++;                     // bump the frame counter
    ctx.drawImage(s.c, 0, 0, W, H - 1, 0, 1, W, H - 1);      // shift the whole image down by 1px (the "waterfall" scroll)
    const d = row.data;                                      // the pixel bytes of the new top line: [R,G,B,A, R,G,B,A, ...]

    if (tuned) tuned.strength = Math.min(1, tuned.strength + .08); // fade the highlighted channel in smoothly

    // Build the new top line one horizontal pixel at a time.
    for (let x = 0; x < W; x++) {
      const fx = x / W;   // this pixel's position across the width as 0..1 (same scale as carrier positions)

      // Base background: random hiss + a slow sine ripple so it isn't flat. Scaled by the noise setting.
      let v = (Math.random() * 60 + 22 + Math.sin(fx * 40 + s.t * .01) * 6) * s.noise;

      // Add each carrier as a bright bump centred on its position.
      for (const k of s.carriers) {
        if (k.burst && Math.sin(s.t * .05 + k.burst * 9) < -.2) continue; // occasionally "drop out" for a bursty feel
        const drift = k.f + Math.sin(s.t * .004 + k.burst * 5) * .004;    // wobble the centre a touch so it looks alive
        const dx = (fx - drift) / k.w; v += k.a * 210 * Math.exp(-dx * dx); // Gaussian bump: bright at centre, fading out
      }

      // If a channel is tuned, add a tall narrow spike at its position (the "we locked on" look).
      if (tuned) { const dx = (fx - tuned.pos) / .01; v += 260 * tuned.strength * Math.exp(-dx * dx); }

      // Convert strength -> colour via the LUT, clamped to 0..255, and write the RGBA bytes.
      const col = lut[Math.max(0, Math.min(255, v | 0))];
      d[x * 4] = col[0]; d[x * 4 + 1] = col[1]; d[x * 4 + 2] = col[2]; d[x * 4 + 3] = 255;
    }
    ctx.putImageData(row, 0, 0); // stamp the finished line at the very top
  }

  // ---- public: highlight (or clear) a channel -----------------------------
  // Called by the hover handlers below, and available as window.pnpTune for anything else.
  window.pnpTune = (pos, label) => {
    tuned = pos == null ? null : { pos, strength: 0 }; // null clears; otherwise start a fresh fade-in at pos
    // Update any readout element (e.g. the "TUNED 1090.000 MHz" text) with the channel's label.
    document.querySelectorAll('[data-tune-readout]').forEach(el => {
      el.textContent = label || el.dataset.tuneReadout; // fall back to its default label when clearing
    });
    // Slide the vertical marker line to the tuned position, or hide it when clearing.
    document.querySelectorAll('[data-tune-marker]').forEach(el => {
      el.style.opacity = pos == null ? 0 : 1; if (pos != null) el.style.left = (pos * 100) + '%';
    });
  };

  // ---- wire everything up on page load ------------------------------------
  function init() {
    document.querySelectorAll('canvas[data-waterfall]').forEach(make); // turn every marked canvas into a waterfall

    // Any element with data-tune (a topic band, a channel row) tunes the waterfall on hover/focus.
    document.querySelectorAll('[data-tune]').forEach(el => {
      const pos = Number(el.dataset.tune), label = el.dataset.tuneLabel;
      el.addEventListener('mouseenter', () => pnpTune(pos, label));   // mouse in  -> tune
      el.addEventListener('focus',      () => pnpTune(pos, label));   // keyboard focus -> tune (accessibility)
      el.addEventListener('mouseleave', () => pnpTune(null));         // mouse out -> clear
      el.addEventListener('blur',       () => pnpTune(null));         // focus lost -> clear
    });

    if (still) return; // reduce-motion: leave the pre-rolled still frame, don't start the loop

    // Animation loop, throttled to ~25fps (the "ts - last > 40" = 40ms between frames).
    let last = 0;
    const loop = ts => {
      if (!document.hidden && ts - last > 40) { falls.forEach(s => s.visible && step(s)); last = ts; } // step only visible canvases
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  // Start now if the page is ready, otherwise wait for the DOM.
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();
})();
