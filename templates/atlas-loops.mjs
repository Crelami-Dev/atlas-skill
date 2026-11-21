/**
 * Atlas v7.4: self-playing loops. Small things that keep moving on their own, politely.
 *
 *   [data-loop]      a replayable mini demo: types a line, runs a progress bar, brings in rows and chips,
 *                    shows a result, holds, resets and plays again (see references/loops.md for markup)
 *   [data-rotate]    words that swap in place (the widest word reserves the width: no layout shift)
 *   [data-marquee]   a seamless ticker that pauses on hover and focus
 *   .atlas-fx / .atlas-float   ambient glow, rings, marks and drift (CSS animation, paused by this script)
 *   [data-loops-toggle]        a page-level "pause all motion" button
 *
 * Accessibility rules enforced here (WCAG 2.2.2): everything pauses when it leaves the screen, every
 * moving thing can be paused (a button on demos and tickers; a page-level toggle for the rest, created
 * automatically when the page has none), and under prefers-reduced-motion nothing moves: demos show
 * their finished frame, rotators their first word, tickers wrap and scroll.
 * Anime.js v4 drives demos and rotators; the ticker and ambient layers need no library.
 */

const ANIME_CDN_ESM = 'https://cdn.jsdelivr.net/npm/animejs@4/+esm';
const LOOP_START_THRESHOLD = 0.15; // the same 15% rule as scenes and reveals

async function resolveAnime(passedLib) {
  if (passedLib && typeof passedLib.createTimeline === 'function') return passedLib;
  try {
    const pkg = 'animejs';
    return await import(/* @vite-ignore */ pkg);
  } catch {
    try {
      return await import(/* @vite-ignore */ ANIME_CDN_ESM);
    } catch {
      return null;
    }
  }
}

const reducedMotion = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

function labels() {
  const id = /^id\b/i.test(document.documentElement.lang || '');
  return id
    ? { pause: 'Jeda animasi', play: 'Putar animasi', pauseAll: 'Jeda semua animasi', playAll: 'Putar semua animasi' }
    : { pause: 'Pause animation', play: 'Play animation', pauseAll: 'Pause all animation', playAll: 'Play all animation' };
}

/** A clone is decoration: no ids (they would duplicate), hidden from assistive tech, links out of the tab order. */
function decorate(node) {
  node.removeAttribute('id');
  node.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));
  node.setAttribute('aria-hidden', 'true');
  node.querySelectorAll('a, button, [tabindex]').forEach((el) => el.setAttribute('tabindex', '-1'));
  if (node.matches('a, button')) node.setAttribute('tabindex', '-1');
  return node;
}

const GLYPH_PAUSE = '❚❚';
const GLYPH_PLAY = '▶';

/**
 * Initialises every loop under `root`. Returns { destroy, refresh, animated }.
 * `animated` is false when motion is reduced or Anime.js could not load (loops then show static frames).
 * Call refresh() after changing translated text so typed lines and rotator words are read again.
 */
export async function initAtlasLoops(options = {}) {
  const root = options.root || document;
  let session = null;

  const setup = async () => {
    const cleanups = [];
    const parts = [];
    let globalPaused = false;
    const text = labels();
    const motionOk = !reducedMotion();
    const anime = motionOk ? await resolveAnime(options.anime) : null;

    const setState = (part, state) => { part.host.dataset.loopState = state; };

    const apply = (part) => {
      if (!part.ready) return;
      const shouldRun = part.visible && !part.userPaused && !globalPaused && !part.held;
      if (shouldRun) { part.run(); setState(part, 'playing'); }
      else {
        part.halt();
        setState(part, part.userPaused || globalPaused ? 'user-paused' : 'paused');
      }
    };

    const watch = (part, threshold) => {
      if (typeof IntersectionObserver !== 'function') { part.visible = true; apply(part); return; }
      const io = new IntersectionObserver((entries) => {
        for (const entry of entries) {
          part.visible = entry.isIntersecting && entry.intersectionRatio >= threshold - 0.01;
          apply(part);
        }
      }, { threshold: [0, threshold] });
      io.observe(part.host);
      cleanups.push(() => io.disconnect());
    };

    const addPauseButton = (part) => {
      const host = part.host;
      if (host.dataset.pause === 'none') { part.hasButton = true; return; } // the author owns the control
      if (host.querySelector(':scope > .atlas-pause')) { part.hasButton = true; return; }
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'atlas-pause';
      const paint = () => {
        button.setAttribute('aria-pressed', String(part.userPaused));
        button.setAttribute('aria-label', part.userPaused ? text.play : text.pause);
        button.textContent = part.userPaused ? GLYPH_PLAY : GLYPH_PAUSE;
      };
      paint();
      button.addEventListener('click', () => { part.userPaused = !part.userPaused; paint(); apply(part); });
      host.append(button);
      part.hasButton = true;
      cleanups.push(() => button.remove());
    };

    const register = (host, { run, halt, threshold = 0 }, withButton) => {
      const part = { host, run, halt, userPaused: false, held: false, visible: false, ready: true, hasButton: false };
      parts.push(part);
      if (withButton) addPauseButton(part);
      watch(part, threshold);
      return part;
    };

    // Ambient CSS layers: paused off screen, and by the page-level toggle like everything else.
    if (motionOk) {
      for (const fx of root.querySelectorAll('.atlas-fx, .atlas-float')) {
        register(fx, {
          run: () => fx.classList.remove('is-paused'),
          halt: () => fx.classList.add('is-paused')
        }, false);
        cleanups.push(() => { fx.classList.remove('is-paused'); delete fx.dataset.loopState; });
      }
    }

    // Tickers.
    for (const host of root.querySelectorAll('[data-marquee]')) {
      const track = host.querySelector('.atlas-marquee__track');
      const group = track?.querySelector('.atlas-marquee__group');
      if (!track || !group) continue;
      if (!motionOk) { host.dataset.loopState = 'static'; continue; }
      const original = [...group.children];
      const speed = Number(host.dataset.speed) || 40; // pixels per second

      // Repeat the sequence until one scrolling half covers the viewport, then duplicate it once for the
      // seamless -50% loop; recomputed when the ticker's width changes.
      const layout = () => {
        group.querySelectorAll('[data-atlas-fill]').forEach((n) => n.remove());
        track.querySelectorAll(':scope > [data-atlas-group-clone]').forEach((n) => n.remove());
        let guard = 0;
        while (group.scrollWidth < host.clientWidth && guard++ < 12) {
          original.forEach((item) => {
            const copy = decorate(item.cloneNode(true));
            copy.dataset.atlasFill = 'true';
            group.append(copy);
          });
        }
        const clone = decorate(group.cloneNode(true));
        clone.dataset.atlasGroupClone = 'true';
        track.append(clone);
        track.style.setProperty('--atlas-marquee-duration', `${Math.max(8, group.scrollWidth / speed)}s`);
      };
      layout();

      const part = register(host, {
        run: () => track.classList.remove('is-paused'),
        halt: () => track.classList.add('is-paused')
      }, true);

      // Hover and focus are tracked separately: motion resumes only when neither is active.
      let hovering = false;
      let focused = false;
      const settle = () => { part.held = hovering || focused; apply(part); };
      const onEnter = () => { hovering = true; settle(); };
      const onLeave = () => { hovering = false; settle(); };
      const onFocusIn = () => { focused = true; settle(); };
      const onFocusOut = (event) => { focused = host.contains(event.relatedTarget); settle(); };
      host.addEventListener('pointerenter', onEnter);
      host.addEventListener('pointerleave', onLeave);
      host.addEventListener('focusin', onFocusIn);
      host.addEventListener('focusout', onFocusOut);

      let ro = null;
      if (typeof ResizeObserver === 'function') {
        let lastWidth = host.clientWidth;
        ro = new ResizeObserver(() => { if (host.clientWidth !== lastWidth) { lastWidth = host.clientWidth; layout(); } });
        ro.observe(host);
      }
      cleanups.push(() => {
        ro?.disconnect();
        host.removeEventListener('pointerenter', onEnter);
        host.removeEventListener('pointerleave', onLeave);
        host.removeEventListener('focusin', onFocusIn);
        host.removeEventListener('focusout', onFocusOut);
        group.querySelectorAll('[data-atlas-fill]').forEach((n) => n.remove());
        track.querySelectorAll(':scope > [data-atlas-group-clone]').forEach((n) => n.remove());
        track.classList.remove('is-paused');
        track.style.removeProperty('--atlas-marquee-duration');
        delete host.dataset.loopState;
        part.ready = false;
      });
    }

    // Rotating words.
    for (const host of root.querySelectorAll('[data-rotate]')) {
      const words = [...host.children];
      if (words.length < 2) continue;
      if (!motionOk || !anime) { host.dataset.loopState = 'static'; continue; }
      const period = Number(host.dataset.rotate) || 2600;
      words.slice(1).forEach((word) => word.setAttribute('aria-hidden', 'true'));
      const tl = anime.createTimeline({ autoplay: false, loop: true, defaults: { ease: 'outQuart' } });
      words.forEach((word, i) => {
        const start = i * period;
        tl.add(word, { opacity: [0, 1], y: ['55%', '0%'], duration: 650 }, start);
        tl.add(word, { opacity: [1, 0], y: ['0%', '-55%'], duration: 500, ease: 'inQuad' }, start + period - 500);
      });
      const part = register(host, { run: () => tl.play(), halt: () => tl.pause() }, false);
      cleanups.push(() => {
        tl.revert?.();
        words.forEach((word) => word.removeAttribute('aria-hidden'));
        delete host.dataset.loopState;
        part.ready = false;
      });
    }

    // Replayable mini demos.
    for (const host of root.querySelectorAll('[data-loop]')) {
      if (!motionOk || !anime) { host.dataset.loopState = 'static'; continue; }
      const { createTimeline, utils, stagger } = anime;
      const hold = Number(host.dataset.loopHold) || 1800;
      const typed = [...host.querySelectorAll('[data-loop-type]')].map((el) => {
        const full = el.dataset.loopType || el.textContent.trim();
        el.dataset.loopType = full; // the finished text lives in the attribute; the element shows a prefix while typing
        // An invisible copy of the finished line shares the element's grid cell, so the card keeps its
        // full height (including wrapped lines on narrow screens) while the visible text is typed.
        const ghost = document.createElement('span');
        ghost.className = 'atlas-loop__ghost';
        ghost.setAttribute('aria-hidden', 'true');
        ghost.textContent = full;
        el.after(ghost);
        return { el, ghost, full, p: { n: 0 } };
      });
      const progress = host.querySelector('[data-loop-progress]');
      const rows = [...host.querySelectorAll('[data-loop-row]')];
      const chips = [...host.querySelectorAll('[data-loop-chip]')];
      const rings = [...host.querySelectorAll('[data-loop-ring]')];
      const foot = host.querySelector('[data-loop-foot]');

      const reset = () => {
        host.dataset.loopPhase = 'idle';
        typed.forEach((t) => { t.p.n = 0; t.el.textContent = ''; });
        if (progress) utils.set(progress, { scaleX: 0, opacity: 0 });
        if (rows.length) utils.set(rows, { opacity: 0, y: 10 });
        if (chips.length) utils.set(chips, { opacity: 0, scale: 0.7 });
        if (rings.length) utils.set(rings, { opacity: 0, scale: 1 });
        if (foot) utils.set(foot, { opacity: 0 });
      };

      const tl = createTimeline({ autoplay: false, loop: true, loopDelay: hold, defaults: { ease: 'outQuart' }, onLoop: reset });
      let cursor = 0;
      tl.call(reset, 0);
      typed.forEach((t) => {
        const duration = Math.max(500, t.full.length * 42);
        tl.call(() => { host.dataset.loopPhase = 'type'; }, cursor);
        tl.add(t.p, {
          n: [0, t.full.length], duration, ease: 'linear',
          onUpdate: () => { t.el.textContent = t.full.slice(0, Math.round(t.p.n)); }
        }, cursor);
        cursor += duration + 160;
        tl.call(() => { host.dataset.loopPhase = 'idle'; }, cursor);
      });
      if (progress) {
        tl.add(progress, { opacity: [0, 1], duration: 120 }, cursor);
        tl.add(progress, { scaleX: [0, 1], duration: 760, ease: 'inOutQuad' }, cursor);
        tl.add(progress, { opacity: [1, 0], duration: 240 }, cursor + 760);
        cursor += 820;
      }
      if (rows.length) {
        tl.add(rows, { opacity: [0, 1], y: [10, 0], duration: 560, delay: stagger(220) }, cursor);
      }
      const rowsEnd = cursor + Math.max(0, rows.length - 1) * 220 + 560;
      if (chips.length) {
        tl.add(chips, { opacity: [0, 1], scale: [0.7, 1], duration: 440, delay: stagger(220) }, cursor + 240);
        if (rings.length) tl.add(rings, { opacity: [0.7, 0], scale: [1, 1.6], duration: 700, delay: stagger(220) }, cursor + 420);
      }
      if (foot) tl.add(foot, { opacity: [0, 1], duration: 520 }, rowsEnd);

      const part = register(host, { run: () => tl.play(), halt: () => tl.pause(), threshold: LOOP_START_THRESHOLD }, true);
      cleanups.push(() => {
        tl.revert?.();
        typed.forEach((t) => { t.el.textContent = t.el.dataset.loopType; t.ghost.remove(); });
        delete host.dataset.loopPhase;
        delete host.dataset.loopState;
        part.ready = false;
      });
    }

    // Page-level pause. If anything moves without a pause button of its own (rotators, ambient layers)
    // and the page has no toggle, one is added so every moving thing can be stopped.
    const toggles = [...root.querySelectorAll('[data-loops-toggle]')];
    if (motionOk && !toggles.length && parts.some((part) => !part.hasButton)) {
      const auto = document.createElement('button');
      auto.type = 'button';
      auto.className = 'atlas-pause atlas-pause--floating';
      auto.setAttribute('data-loops-toggle', '');
      auto.dataset.auto = 'true';
      document.body.append(auto);
      toggles.push(auto);
      cleanups.push(() => auto.remove());
    }
    for (const toggle of toggles) {
      if (!motionOk) { toggle.hidden = true; continue; }
      const paint = () => {
        toggle.setAttribute('aria-pressed', String(globalPaused));
        toggle.setAttribute('aria-label', globalPaused ? text.playAll : text.pauseAll);
        toggle.dataset.state = globalPaused ? 'paused' : 'playing';
        if (toggle.dataset.auto) toggle.textContent = globalPaused ? GLYPH_PLAY : GLYPH_PAUSE;
      };
      paint();
      const onClick = () => { globalPaused = !globalPaused; toggles.forEach((other) => other !== toggle && other.setAttribute('aria-pressed', String(globalPaused))); paint(); parts.forEach(apply); };
      toggle.addEventListener('click', onClick);
      cleanups.push(() => toggle.removeEventListener('click', onClick));
    }

    return { cleanups, parts, animated: motionOk && Boolean(anime) };
  };

  session = await setup();

  const destroy = () => {
    if (!session) return;
    session.cleanups.splice(0).reverse().forEach((fn) => fn());
    session = null;
  };
  const refresh = async () => { destroy(); session = await setup(); };
  return {
    destroy,
    refresh,
    get animated() { return Boolean(session?.animated); }
  };
}
