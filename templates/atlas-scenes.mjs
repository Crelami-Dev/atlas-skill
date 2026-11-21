/**
 * Atlas v7.2 — Scene engine: 15%-threshold reveals + a registry of scroll-scrubbed scenes.
 * Built for Anime.js v4 (`animate`, `createTimeline`, `createScope`, `stagger`, `utils`).
 * Safe progressive enhancement: every scene keeps a complete, readable "rest" composition
 * without JS, when Anime.js is unavailable, and under prefers-reduced-motion.
 *
 * Scenes are either HEAVY (sticky, ~1.45 viewport tall; at most ONE pinned per page, >= 1024px) or
 * LIGHT (no sticky track; at most TWO scroll-scrubbed per page). Below 1024px (tablet portrait, phones)
 * every scene instead PLAYS ONCE, smoothly, when 15% of it is on screen, so nothing sits still.
 *
 *   heavy: window-reveal  mask-zoom  type-parting  pull-back  split-wipe  horizontal-rail
 *   light: parallax-depth  word-light  step-assemble  drift-type
 *
 * Markup contracts live in references/scenes.md; metadata for choosing a scene lives in
 * templates/scene-catalog.json (see scripts/deal-scene.mjs).
 */

const ANIME_CDN_ESM = 'https://cdn.jsdelivr.net/npm/animejs@4/+esm';
const MAX_HEAVY = 1;
const MAX_LIGHT = 2;
const PLAY_MS = 1700; // total time of a play-once scene on tablets and phones

async function resolveAnime(passedLib) {
  if (passedLib && typeof passedLib.animate === 'function') return passedLib;
  try {
    const pkg = 'animejs';
    return await import(/* @vite-ignore */ pkg);
  } catch {
    if (typeof window !== 'undefined') {
      try {
        return await import(/* @vite-ignore */ ANIME_CDN_ESM);
      } catch {
        return null;
      }
    }
    return null;
  }
}

const clamp01 = (v) => Math.min(1, Math.max(0, v));

/**
 * Computes an IntersectionObserver threshold clamped so extra-tall sections still fire reliably
 * when at least 15% of the viewport/element height enters view.
 */
function effective15PercentThreshold(el, requested = 0.15) {
  if (typeof window === 'undefined' || !el) return requested;
  const rect = el.getBoundingClientRect();
  const minRatio = (window.innerHeight * requested) / Math.max(rect.height, 1);
  return Math.max(0.04, Math.min(requested, minRatio));
}

/** True once at least the requested share of the element is on screen (the first callback may fire for a sliver). */
const reachedThreshold = (entry, threshold) => entry.isIntersecting && entry.intersectionRatio >= threshold - 0.01;

function playEntrance(animate, stagger, targets, opts) {
  return animate(targets, {
    y: [opts.distance, 0],
    opacity: [opts.startOpacity, 1],
    scale: [opts.startScale, 1],
    duration: opts.duration,
    delay: stagger(opts.staggerMs),
    ease: opts.ease
  });
}

/** Splits a plain-text element into word spans (text stays readable: the element keeps an aria-label). */
function splitWords(el) {
  const existing = [...el.querySelectorAll('.atlas-word')];
  if (existing.length) return existing;
  const text = el.textContent.replace(/\s+/g, ' ').trim();
  if (!text) return [];
  el.setAttribute('aria-label', text);
  el.textContent = '';
  const words = text.split(' ').map((word, i, all) => {
    const span = document.createElement('span');
    span.className = 'atlas-word';
    span.setAttribute('aria-hidden', 'true');
    span.textContent = word;
    el.append(span);
    if (i < all.length - 1) el.append(' ');
    return span;
  });
  return words;
}

/**
 * Scene registry. Each builder receives (sceneEl, ctx) and returns
 *   { tl?, onProgress?(p), range?: [from, to], cleanup?() }
 * `tl` is a paused Anime.js v4 timeline seeked from scroll progress; `onProgress` is for effects
 * that are cheaper to write directly (horizontal-rail).
 */
const PRESETS = {
  /* ───── HEAVY ───── */
  'window-reveal': {
    mode: 'heavy',
    build(sc, { tl }) {
      const left = sc.querySelector('.atlas-scene__shutter--left');
      const right = sc.querySelector('.atlas-scene__shutter--right');
      const media = sc.querySelector('.atlas-scene__backdrop img');
      const caption = sc.querySelector('.atlas-scene__caption');
      if (left) tl.add(left, { x: ['0%', '-105%'] }, 0);
      if (right) tl.add(right, { x: ['0%', '105%'] }, 0);
      if (media) tl.add(media, { scale: [1.14, 1] }, 0);
      if (caption) tl.add(caption, { y: [24, 0], opacity: [0.55, 1] }, 150);
      return { tl };
    }
  },

  'mask-zoom': {
    mode: 'heavy',
    build(sc, { tl }) {
      const frame = sc.querySelector('.atlas-scene__frame');
      const media = sc.querySelector('.atlas-scene__backdrop img');
      const caption = sc.querySelector('.atlas-scene__caption');
      if (frame) tl.add(frame, { clipPath: ['inset(10% 14% round 1.25rem)', 'inset(0% 0% round 0rem)'] }, 0);
      if (media) tl.add(media, { scale: [1.12, 1] }, 0);
      if (caption) tl.add(caption, { y: [24, 0], opacity: [0.55, 1] }, 150);
      return { tl };
    }
  },

  'type-parting': {
    mode: 'heavy',
    build(sc, { tl }) {
      const leftHalves = sc.querySelectorAll('.atlas-scene__half--left');
      const rightHalves = sc.querySelectorAll('.atlas-scene__half--right');
      const center = sc.querySelector('.atlas-scene__centerpiece');
      if (leftHalves.length) tl.add(leftHalves, { x: ['0px', '-56px'] }, 0);
      if (rightHalves.length) tl.add(rightHalves, { x: ['0px', '56px'] }, 0);
      if (center) tl.add(center, { scale: [0.88, 1.02], y: [28, 0], opacity: [0.55, 1] }, 0);
      return { tl };
    }
  },

  // A tight crop of one detail pulls back until the whole subject is in frame; the caption swaps
  // from the detail's line to the whole's line. data-zoom (default 1.8), data-origin ("30% 40%").
  // Crispness: the photo's width should be at least zoom x its displayed width (fetch-photos --width 3200).
  'pull-back': {
    mode: 'heavy',
    build(sc, { tl }) {
      const img = sc.querySelector('.atlas-scene__backdrop img');
      const from = sc.querySelector('.atlas-scene__caption--from');
      const to = sc.querySelector('.atlas-scene__caption--to');
      const zoom = Number(sc.dataset.zoom) || 1.8;
      if (img) {
        img.style.transformOrigin = sc.dataset.origin || '50% 50%';
        tl.add(img, { scale: [zoom, 1], duration: 1000 }, 0);
      }
      if (from) tl.add(from, { opacity: [1, 0], y: [0, -14], duration: 260 }, 160);
      if (to) {
        tl.set(to, { opacity: 0 }, 0);
        tl.add(to, { opacity: [0, 1], y: [14, 0], duration: 320 }, 440);
      }
      return { tl };
    }
  },

  // Two states of the same place: a divider travels across and the second state takes over.
  // Markup: .atlas-scene__compare > img.atlas-scene__after + .atlas-scene__before-clip > img + divider.
  'split-wipe': {
    mode: 'heavy',
    build(sc, { tl }) {
      const clip = sc.querySelector('.atlas-scene__before-clip');
      const divider = sc.querySelector('.atlas-scene__divider');
      if (clip) tl.add(clip, { clipPath: ['inset(0 0 0 0%)', 'inset(0 0 0 100%)'] }, 0);
      if (divider) tl.add(divider, { left: ['0%', '100%'] }, 0);
      return { tl };
    }
  },

  // Vertical scroll drives a horizontal strip of plates. Phones get a native scroll-snap row.
  'horizontal-rail': {
    mode: 'heavy',
    build(sc, { tl, mode }) {
      const rail = sc.querySelector('.atlas-scene__rail');
      const track = sc.querySelector('.atlas-scene__track');
      if (!rail || !track) return {};
      if (mode === 'play') {
        // Phones and tablets keep a native swipe row; the plates glide in one after another.
        [...sc.querySelectorAll('.atlas-scene__plate')].forEach((plate, i) => tl.add(plate, { x: [56, 0], opacity: [0, 1], duration: 800 }, i * 150));
        return { tl };
      }
      let distance = 0;
      const measure = () => {
        distance = Math.max(0, track.scrollWidth - rail.clientWidth);
        sc.style.minHeight = `${window.innerHeight + distance}px`;
      };
      measure();
      const ro = typeof ResizeObserver === 'function' ? new ResizeObserver(measure) : null;
      ro?.observe(track);
      ro?.observe(rail);
      window.addEventListener('resize', measure);
      return {
        onProgress(p) {
          track.style.transform = `translate3d(${-p * distance}px, 0, 0)`;
        },
        cleanup() {
          ro?.disconnect();
          window.removeEventListener('resize', measure);
          track.style.transform = '';
          sc.style.minHeight = '';
        }
      };
    }
  },

  /* ───── LIGHT ───── */
  'parallax-depth': {
    mode: 'light',
    build(sc, { tl }) {
      const media = sc.querySelector('.atlas-scene__media img');
      const copy = sc.querySelector('.atlas-scene__copy');
      if (media) tl.add(media, { y: ['-5%', '5%'], scale: [1.08, 1.01] }, 0);
      if (copy) tl.add(copy, { y: [28, -10] }, 0);
      return { tl };
    }
  },

  // A statement lights up word by word as it crosses the screen. Plain text only.
  'word-light': {
    mode: 'light',
    build(sc, { tl }) {
      const host = sc.querySelector('.atlas-scene__statement');
      const words = host ? splitWords(host) : [];
      if (words.length) {
        const per = Math.max(18, Math.floor(700 / words.length));
        tl.add(words, { opacity: [0.16, 1], duration: 300, delay: (_, i) => i * per }, 0);
      }
      return { tl, range: [0.12, 0.62] };
    }
  },

  // Process steps start scattered and settle into a row while a progress line draws.
  'step-assemble': {
    mode: 'light',
    build(sc, { tl }) {
      const steps = [...sc.querySelectorAll('.atlas-step')];
      steps.forEach((step, i) => {
        const side = i % 2 ? 1 : -1;
        tl.add(step, { x: [side * 36, 0], y: [26 + i * 6, 0], rotate: [side * 3.5, 0], opacity: [0.15, 1], duration: 520 }, i * 150);
      });
      const total = steps.length * 150 + 520;
      const lineH = sc.querySelector('.atlas-scene__line--h');
      const lineV = sc.querySelector('.atlas-scene__line--v');
      if (lineH) tl.add(lineH, { scaleX: [0, 1], duration: total }, 0);
      if (lineV) tl.add(lineV, { scaleY: [0, 1], duration: total }, 0);
      return { tl, range: [0.08, 0.62] };
    }
  },

  // Two giant lines of type drift in opposite directions. Rows are decorative (aria-hidden).
  'drift-type': {
    mode: 'light',
    build(sc, { tl }) {
      const rows = [...sc.querySelectorAll('.atlas-drift__row')];
      rows.forEach((row, i) => {
        const reverse = row.classList.contains('atlas-drift__row--rev') || i % 2 === 1;
        tl.add(row, { x: reverse ? ['-24%', '2%'] : ['2%', '-24%'] }, 0);
      });
      return { tl, range: [0, 1] };
    }
  }
};

export const ATLAS_SCENE_NAMES = Object.keys(PRESETS);

/** Maps scroll position to 0..1 progress for a scene. Heavy: across its sticky track. Light: across the viewport. */
function readProgress(sc, mode) {
  const rect = sc.getBoundingClientRect();
  const vh = window.innerHeight;
  if (mode === 'heavy') {
    const total = rect.height - vh;
    return total > 1 ? clamp01(-rect.top / total) : clamp01((vh - rect.top) / (vh + rect.height));
  }
  return clamp01((vh - rect.top) / (vh + rect.height));
}

/** Drives a scene from scroll with one rAF-throttled listener. Returns a disposer. */
function bindScroll(sc, mode, result) {
  const [from, to] = result.range || [0, 1];
  let raf = 0;
  let last = -1;
  const update = () => {
    raf = 0;
    const p = clamp01((readProgress(sc, mode) - from) / Math.max(0.001, to - from));
    if (Math.abs(p - last) < 0.0004) return;
    last = p;
    if (result.tl) result.tl.seek(p * result.tl.duration);
    result.onProgress?.(p);
  };
  const schedule = () => { if (!raf) raf = requestAnimationFrame(update); };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  update();
  return () => {
    window.removeEventListener('scroll', schedule);
    window.removeEventListener('resize', schedule);
    if (raf) cancelAnimationFrame(raf);
  };
}

/**
 * Initializes 15%-threshold reveals and the scene registry.
 *
 * Motion modes (written to <html data-atlas-motion="...">, handy when debugging a device):
 *   scrub  >= 1024px: heavy scenes pin and follow scroll (one per page); light scenes follow scroll (two).
 *   play   <  1024px (tablet portrait, phones): every scene plays ONCE, smoothly, when 15% of it is on screen.
 *   soft   prefers-reduced-motion: opacity-only fades at 15%; scenes show their finished composition.
 *   rest   Anime.js unavailable: everything stays visible and still.
 * The 15% rule is the same on every device: a section starts when 15% of the SCREEN height of it is visible.
 * @returns {Promise<{ destroy: () => void, anime: object | null }>}
 */
export async function initAtlasMotion(options = {}) {
  const root = options.root || (typeof document !== 'undefined' ? document.body : null);
  if (!root) return { destroy() {}, anime: null };

  const sceneEls = [...root.querySelectorAll('[data-atlas-scene]')];
  const revealGroups = [...root.querySelectorAll('[data-reveal], [data-scroll-section]')];
  const setMode = (mode) => { document.documentElement.dataset.atlasMotion = mode; };

  const setRest = (sc) => {
    sc.classList.remove('is-live', 'is-play');
    sc.classList.add('is-rest');
  };
  const markAllRest = () => {
    sceneEls.forEach(setRest);
    for (const el of revealGroups) el.dataset.atlasRevealed = 'true';
    setMode('rest');
  };

  const anime = await resolveAnime(options.anime);
  if (!anime || typeof anime.createScope !== 'function' || typeof anime.animate !== 'function') {
    markAllRest();
    return { destroy() {}, anime: null };
  }

  const { animate, createScope, createTimeline, stagger, utils } = anime;
  const observers = [];
  const cfg = {
    threshold: options.threshold ?? 0.15,
    heroDuration: options.heroDuration ?? 1100,
    duration: options.revealDuration ?? 1250,
    staggerMs: options.revealStagger ?? 110,
    distance: options.revealDistance ?? 36,
    startOpacity: options.startOpacity ?? 0.14,
    startScale: options.startScale ?? 0.975,
    ease: options.ease ?? 'outQuart',
    sceneMs: options.sceneDuration ?? PLAY_MS
  };

  const scope = createScope({
    root,
    mediaQueries: {
      reduceMotion: '(prefers-reduced-motion: reduce)',
      isScrub: '(min-width: 1024px)'
    }
  }).add((self) => {
    const soft = Boolean(self?.matches?.reduceMotion);
    const scrub = Boolean(self?.matches?.isScrub);
    setMode(soft ? 'soft' : scrub ? 'scrub' : 'play');

    // Soft mode keeps the 15% trigger but only fades: no travel, no scale.
    const enter = (targets, overrides = {}) => (soft
      ? animate(targets, { opacity: [0, 1], duration: 700, delay: stagger(60), ease: 'outQuad' })
      : playEntrance(animate, stagger, targets, { ...cfg, ...overrides }));
    const primeHidden = (targets) => {
      if (!utils || typeof utils.set !== 'function') return;
      utils.set(targets, soft ? { opacity: 0 } : { y: cfg.distance, opacity: cfg.startOpacity, scale: cfg.startScale });
    };

    // 1. Hero above-the-fold choreography
    const heroTargets = root.querySelectorAll('[data-hero-reveal], [data-hero-item], [data-hero-title]');
    if (heroTargets.length) enter(heroTargets, { duration: cfg.heroDuration, distance: 28, startOpacity: 0.18, startScale: 0.985 });

    // 2. 15% viewport threshold scroll-reveal for sections/cards below the fold
    for (const group of revealGroups) {
      const items = group.querySelectorAll('[data-reveal-item], [data-scroll-item]');
      const targets = items.length ? [...items] : [group];
      const rect = group.getBoundingClientRect();
      const alreadyInView = rect.top < window.innerHeight * (1 - cfg.threshold);

      if (alreadyInView) {
        group.dataset.atlasRevealed = 'true';
        enter(targets);
        continue;
      }

      primeHidden(targets);

      if (typeof IntersectionObserver !== 'function') {
        group.dataset.atlasRevealed = 'true';
        enter(targets);
        continue;
      }

      const groupThreshold = effective15PercentThreshold(group, cfg.threshold);
      const io = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!reachedThreshold(entry, groupThreshold)) continue;
            group.dataset.atlasRevealed = 'true';
            enter(targets);
            io.unobserve(group);
            break;
          }
        },
        { threshold: groupThreshold }
      );
      io.observe(group);
      observers.push(io);
    }

    // 3. Scenes.
    const disposers = [];
    const timelines = [];

    const mountScrub = (sc, preset) => {
      const isHeavy = preset.mode === 'heavy';
      sc.classList.remove('is-rest', 'is-play');
      sc.classList.add('is-live');
      sc.classList.toggle('atlas-scene--light', !isHeavy);
      const tl = createTimeline({ autoplay: false, defaults: { duration: 1000, ease: 'linear' } });
      const result = preset.build(sc, { tl, anime, mode: 'scrub' }) || {};
      result.tl = result.tl || (tl.duration > 0 ? tl : null);
      timelines.push(tl);
      disposers.push(bindScroll(sc, preset.mode, result));
      if (result.cleanup) disposers.push(result.cleanup);
    };

    // Play once, smoothly, when 15% of the scene is on screen. Works the same on every device.
    const mountPlay = (sc, preset) => {
      sc.classList.remove('is-rest', 'is-live');
      sc.classList.add('is-play');
      const tl = createTimeline({ autoplay: false, defaults: { duration: 1000, ease: cfg.ease } });
      const result = preset.build(sc, { tl, anime, mode: 'play' }) || {};
      const timeline = result.tl || tl;
      timelines.push(timeline);
      if (!(timeline.duration > 0)) return;
      const target = Number(sc.dataset.motionMs) || cfg.sceneMs;
      timeline.speed = Math.max(0.2, timeline.duration / target);
      timeline.seek(0); // apply the start state now so nothing flashes at its final pose first
      if (typeof IntersectionObserver !== 'function') { timeline.play(); return; }
      const sceneThreshold = effective15PercentThreshold(sc, cfg.threshold);
      const io = new IntersectionObserver(
        (entries) => {
          if (!entries.some((entry) => reachedThreshold(entry, sceneThreshold))) return;
          io.disconnect();
          timeline.play();
        },
        { threshold: sceneThreshold }
      );
      io.observe(sc);
      observers.push(io);
      disposers.push(() => io.disconnect());
    };

    let heavy = 0;
    let light = 0;
    for (const sc of sceneEls) {
      const preset = PRESETS[sc.getAttribute('data-atlas-scene')];
      if (!preset || typeof createTimeline !== 'function' || soft) { setRest(sc); continue; }
      const isHeavy = preset.mode === 'heavy';
      // Pinned (scrub) scenes are capped per page; any extra scene still plays once instead of sitting still.
      const canScrub = scrub && (isHeavy ? heavy < MAX_HEAVY : light < MAX_LIGHT);
      if (canScrub) {
        isHeavy ? heavy++ : light++;
        mountScrub(sc, preset);
      } else {
        mountPlay(sc, preset);
      }
    }

    return () => {
      disposers.forEach((dispose) => dispose());
      timelines.forEach((timeline) => timeline.revert?.());
      sceneEls.forEach(setRest);
    };
  });

  const destroy = () => {
    for (const io of observers) io.disconnect();
    observers.length = 0;
    scope.revert();
  };

  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', destroy, { once: true });
  }

  return { destroy, anime };
}

/** id -> 'heavy' | 'light'. Used by tests to keep scene-catalog.json and the engine in sync. */
export const ATLAS_SCENE_MODES = Object.fromEntries(Object.entries(PRESETS).map(([id, preset]) => [id, preset.mode]));
