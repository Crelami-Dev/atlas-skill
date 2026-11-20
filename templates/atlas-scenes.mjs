/**
 * Atlas v7.1 — Scroll-Triggered (15% Viewport Entry) & Scroll-Scrubbed Signature Scenes
 * Built for Anime.js v4 (`animate`, `createScope`, `onScroll`, `stagger`, `utils`).
 * Safe progressive enhancement: keeps all DOM visible without JS or under prefers-reduced-motion.
 */

const ANIME_CDN_ESM = 'https://cdn.jsdelivr.net/npm/animejs@4/+esm';

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

function setupScenePreset(sceneEl, preset, anime) {
  const { animate, createTimeline, onScroll } = anime;
  const scrollConfig = {
    target: sceneEl,
    enter: 'bottom-=15% top',
    leave: 'bottom bottom',
    sync: 0.25
  };

  // Anime.js v4 ScrollObserver links 1 tickable (`this.linked`), so use a single createTimeline
  // to drive all moving scene layers together in lockstep.
  if (typeof createTimeline === 'function') {
    const tl = createTimeline({
      defaults: { duration: 1000, ease: 'linear' },
      autoplay: onScroll(scrollConfig)
    });

    if (preset === 'window-reveal') {
      const left = sceneEl.querySelector('.atlas-scene__shutter--left');
      const right = sceneEl.querySelector('.atlas-scene__shutter--right');
      const media = sceneEl.querySelector('.atlas-scene__backdrop img');
      const caption = sceneEl.querySelector('.atlas-scene__caption');
      if (left) tl.add(left, { x: ['0%', '-105%'] }, 0);
      if (right) tl.add(right, { x: ['0%', '105%'] }, 0);
      if (media) tl.add(media, { scale: [1.14, 1] }, 0);
      if (caption) tl.add(caption, { y: [24, 0], opacity: [0.55, 1] }, 150);
      return tl;
    }

    if (preset === 'mask-zoom') {
      const frame = sceneEl.querySelector('.atlas-scene__frame');
      const media = sceneEl.querySelector('.atlas-scene__backdrop img');
      const caption = sceneEl.querySelector('.atlas-scene__caption');
      if (frame) tl.add(frame, { clipPath: ['inset(10% 14% round 1.25rem)', 'inset(0% 0% round 0rem)'] }, 0);
      if (media) tl.add(media, { scale: [1.12, 1] }, 0);
      if (caption) tl.add(caption, { y: [24, 0], opacity: [0.55, 1] }, 150);
      return tl;
    }

    if (preset === 'type-parting') {
      const leftHalves = sceneEl.querySelectorAll('.atlas-scene__half--left');
      const rightHalves = sceneEl.querySelectorAll('.atlas-scene__half--right');
      const center = sceneEl.querySelector('.atlas-scene__centerpiece');
      if (leftHalves.length) tl.add(leftHalves, { x: ['0px', '-56px'] }, 0);
      if (rightHalves.length) tl.add(rightHalves, { x: ['0px', '56px'] }, 0);
      if (center) tl.add(center, { scale: [0.88, 1.02], y: [28, 0], opacity: [0.55, 1] }, 0);
      return tl;
    }

    if (preset === 'parallax-depth') {
      const media = sceneEl.querySelector('.atlas-scene__media img');
      const copy = sceneEl.querySelector('.atlas-scene__copy');
      if (media) tl.add(media, { y: ['-5%', '5%'], scale: [1.08, 1.01] }, 0);
      if (copy) tl.add(copy, { y: [28, -10] }, 0);
      return tl;
    }
    return tl;
  }

  // Fallback if caller didn't pass createTimeline: each element gets its own ScrollObserver
  if (preset === 'window-reveal') {
    const left = sceneEl.querySelector('.atlas-scene__shutter--left');
    const right = sceneEl.querySelector('.atlas-scene__shutter--right');
    const media = sceneEl.querySelector('.atlas-scene__backdrop img');
    if (left) animate(left, { x: ['0%', '-105%'], ease: 'linear', autoplay: onScroll(scrollConfig) });
    if (right) animate(right, { x: ['0%', '105%'], ease: 'linear', autoplay: onScroll(scrollConfig) });
    if (media) animate(media, { scale: [1.14, 1], ease: 'linear', autoplay: onScroll(scrollConfig) });
  }
}

/**
 * Initializes visible Anime.js v4 15%-threshold section choreography and optional 1 Signature Scroll Scene.
 * @returns {Promise<{ destroy: () => void, anime: object | null }>}
 */
export async function initAtlasMotion(options = {}) {
  const root = options.root || (typeof document !== 'undefined' ? document.body : null);
  if (!root) return { destroy() {}, anime: null };

  const sceneEls = [...root.querySelectorAll('[data-atlas-scene]')];
  const revealGroups = [...root.querySelectorAll('[data-reveal], [data-scroll-section]')];

  const markAllRest = () => {
    for (const sc of sceneEls) {
      sc.classList.remove('is-live');
      sc.classList.add('is-rest');
    }
    for (const el of revealGroups) {
      el.dataset.atlasRevealed = 'true';
    }
  };

  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    markAllRest();
    return { destroy() {}, anime: null };
  }

  const anime = await resolveAnime(options.anime);
  if (!anime || typeof anime.createScope !== 'function' || typeof anime.animate !== 'function') {
    markAllRest();
    return { destroy() {}, anime: null };
  }

  const { animate, createScope, stagger, utils } = anime;
  const observers = [];
  const cfg = {
    threshold: options.threshold ?? 0.15,
    heroDuration: options.heroDuration ?? 900,
    duration: options.revealDuration ?? 920,
    staggerMs: options.revealStagger ?? 95,
    distance: options.revealDistance ?? 36,
    startOpacity: options.startOpacity ?? 0.14,
    startScale: options.startScale ?? 0.975,
    ease: options.ease ?? 'outExpo'
  };

  const scope = createScope({
    root,
    mediaQueries: {
      reduceMotion: '(prefers-reduced-motion: reduce)',
      isMobile: '(max-width: 767px)'
    }
  }).add((self) => {
    if (self?.matches?.reduceMotion) {
      markAllRest();
      return;
    }

    // 1. Hero above-the-fold choreography
    const heroTargets = root.querySelectorAll('[data-hero-reveal], [data-hero-item], [data-hero-title]');
    if (heroTargets.length) {
      playEntrance(animate, stagger, heroTargets, {
        ...cfg,
        duration: cfg.heroDuration,
        distance: 28,
        startOpacity: 0.18,
        startScale: 0.985
      });
    }

    // 2. 15% Viewport Threshold Scroll-Reveal for sections/cards below the fold
    for (const group of revealGroups) {
      const items = group.querySelectorAll('[data-reveal-item], [data-scroll-item]');
      const targets = items.length ? [...items] : [group];
      const rect = group.getBoundingClientRect();
      const alreadyInView = rect.top < window.innerHeight * 0.85;

      if (alreadyInView) {
        group.dataset.atlasRevealed = 'true';
        playEntrance(animate, stagger, targets, cfg);
        continue;
      }

      if (utils && typeof utils.set === 'function') {
        utils.set(targets, { y: cfg.distance, opacity: cfg.startOpacity, scale: cfg.startScale });
      }

      if (typeof IntersectionObserver !== 'function') {
        group.dataset.atlasRevealed = 'true';
        playEntrance(animate, stagger, targets, cfg);
        continue;
      }

      const io = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            group.dataset.atlasRevealed = 'true';
            playEntrance(animate, stagger, targets, cfg);
            io.unobserve(group);
            break;
          }
        },
        { threshold: effective15PercentThreshold(group, cfg.threshold) }
      );
      io.observe(group);
      observers.push(io);
    }

    // 3. Mount at most 1 continuous Signature Scroll Scene on desktop viewports
    sceneEls.forEach((sc, idx) => {
      if (idx > 0 || self?.matches?.isMobile) {
        sc.classList.remove('is-live');
        sc.classList.add('is-rest');
        return;
      }
      sc.classList.remove('is-rest');
      sc.classList.add('is-live');
      const preset = sc.getAttribute('data-atlas-scene') || 'window-reveal';
      setupScenePreset(sc, preset, anime);
    });
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
