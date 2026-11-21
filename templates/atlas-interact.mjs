/**
 * Atlas v7.2 — Small interactions that make a page feel alive without getting in the way.
 * Plain DOM, no dependencies. Everything is optional, opt-in by data attribute, and skipped under
 * prefers-reduced-motion or on touch pointers where it would be wrong.
 *
 *   data-magnetic        a button leans a few pixels toward the pointer
 *   data-tilt            a card tilts up to 3.5deg toward the pointer
 *   data-spotlight       sets --mx / --my on the element (pairs with .atlas-bg-spotlight)
 *   data-count="48"      counts up to the number when it scrolls into view (markup keeps the real value)
 *   data-cta-primary     hero action; with [data-mobile-bar] a phone action bar appears once it scrolls away
 *   data-carousel        builds arrows, dots and keyboard support for an .atlas-carousel (see atlas-components.css)
 */

const reduced = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = () => typeof matchMedia === 'function' && matchMedia('(hover: hover) and (pointer: fine)').matches;

export function initAtlasInteract(options = {}) {
  const root = options.root || document;
  const cleanups = [];
  const on = (target, type, fn, opts) => {
    target.addEventListener(type, fn, opts);
    cleanups.push(() => target.removeEventListener(type, fn, opts));
  };

  // Spotlight works for any pointer, motion-safe because it only recolours a gradient.
  for (const el of root.querySelectorAll('[data-spotlight]')) {
    on(el, 'pointermove', (e) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${((e.clientX - r.left) / r.width) * 100}%`);
      el.style.setProperty('--my', `${((e.clientY - r.top) / r.height) * 100}%`);
    });
  }

  if (!reduced() && finePointer()) {
    for (const el of root.querySelectorAll('[data-magnetic]')) {
      const reach = Number(el.dataset.magnetic) || 8;
      on(el, 'pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
        const dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
        el.style.transform = `translate(${(dx * reach).toFixed(1)}px, ${(dy * reach).toFixed(1)}px)`;
      });
      on(el, 'pointerleave', () => { el.style.transform = ''; });
    }
    for (const el of root.querySelectorAll('[data-tilt]')) {
      on(el, 'pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(900px) rotateX(${(-y * 7).toFixed(2)}deg) rotateY(${(x * 7).toFixed(2)}deg)`;
      });
      on(el, 'pointerleave', () => { el.style.transform = ''; });
    }
  }

  // Count-up: the real value is already in the markup, so no-JS and reduced motion show the truth.
  const counters = [...root.querySelectorAll('[data-count]')];
  if (counters.length && !reduced() && typeof IntersectionObserver === 'function') {
    const locale = document.documentElement.lang || undefined;
    const fmt = new Intl.NumberFormat(locale);
    const io = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        io.unobserve(entry.target);
        const el = entry.target;
        const end = Number(el.dataset.count);
        if (!Number.isFinite(end)) continue;
        const final = el.textContent;
        const started = performance.now();
        const duration = 1100;
        const tick = (now) => {
          const t = Math.min(1, (now - started) / duration);
          el.textContent = t < 1 ? fmt.format(Math.round(end * (1 - Math.pow(1 - t, 3)))) : final;
          if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }
    }, { threshold: 0.6 });
    counters.forEach((el) => io.observe(el));
    cleanups.push(() => io.disconnect());
  }

  // Phone action bar: appears once the hero's primary action is no longer on screen.
  const bar = root.querySelector('[data-mobile-bar]');
  const hero = root.querySelector('[data-cta-primary]');
  if (bar && hero && typeof IntersectionObserver === 'function') {
    const io = new IntersectionObserver(([entry]) => { bar.hidden = entry.isIntersecting || entry.boundingClientRect.top > 0; });
    io.observe(hero);
    cleanups.push(() => io.disconnect());
  }

  cleanups.push(initAtlasCarousels(root).destroy);

  return { destroy: () => cleanups.splice(0).forEach((fn) => fn()) };
}

/**
 * Carousels: arrows, dots (or a counter past 5 slides), keyboard and screen-reader roles for every
 * [data-carousel]. Works without Anime.js. Motion-safe: smooth scrolling is dropped under reduced motion.
 */
export function initAtlasCarousels(root = document) {
  const cleanups = [];
  const isId = /^id\b/i.test(document.documentElement.lang || '');
  const text = isId
    ? { prev: 'Sebelumnya', next: 'Berikutnya', of: 'dari', go: 'Ke slide' }
    : { prev: 'Previous', next: 'Next', of: 'of', go: 'Go to slide' };

  for (const el of root.querySelectorAll('[data-carousel]')) {
    const track = el.querySelector('.atlas-carousel__track');
    const slides = track ? [...track.children] : [];
    if (slides.length < 2 || el.dataset.carouselReady) continue;
    el.dataset.carouselReady = 'true';

    el.setAttribute('role', 'region');
    el.setAttribute('aria-roledescription', 'carousel');
    track.tabIndex = 0;
    slides.forEach((slide, i) => {
      slide.setAttribute('role', 'group');
      slide.setAttribute('aria-roledescription', 'slide');
      slide.setAttribute('aria-label', `${i + 1} ${text.of} ${slides.length}`);
    });

    let controls = el.querySelector('.atlas-carousel__controls');
    if (!controls) {
      controls = document.createElement('div');
      controls.className = 'atlas-carousel__controls';
      el.append(controls);
    }
    controls.textContent = '';
    const button = (label, glyph, onClick) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'atlas-carousel__btn';
      b.setAttribute('aria-label', label);
      b.textContent = glyph;
      b.addEventListener('click', onClick);
      return b;
    };

    const behavior = () => (reduced() ? 'auto' : 'smooth');
    // The track is the slides' offsetParent (position: relative), so offsetLeft is already track-relative.
    const leftOf = (slide) => slide.offsetLeft;
    const maxScroll = () => Math.max(0, track.scrollWidth - track.clientWidth);
    const scrollToLeft = (left) => track.scrollTo({ left: Math.max(0, Math.min(maxScroll(), left)), behavior: behavior() });
    const go = (index) => scrollToLeft(leftOf(slides[Math.max(0, Math.min(slides.length - 1, index))]));
    // One step by position, not by index: with several slides visible the last ones cannot reach the left
    // edge, so stepping from "the active index" would leave previous stuck at the end of the track.
    const step = (direction) => {
      const here = track.scrollLeft;
      if (direction > 0) {
        const target = slides.find((slide) => leftOf(slide) > here + 2);
        if (target) scrollToLeft(leftOf(target));
      } else {
        const target = [...slides].reverse().find((slide) => leftOf(slide) < here - 2);
        scrollToLeft(target ? leftOf(target) : 0);
      }
    };
    const activeIndex = () => {
      if (track.scrollLeft + track.clientWidth >= track.scrollWidth - 2) return slides.length - 1;
      let best = 0;
      let bestDistance = Infinity;
      slides.forEach((slide, i) => {
        const distance = Math.abs(leftOf(slide) - track.scrollLeft);
        if (distance < bestDistance) { bestDistance = distance; best = i; }
      });
      return best;
    };

    const prev = button(text.prev, '‹', () => step(-1));
    const next = button(text.next, '›', () => step(1));
    const middle = document.createElement('div');
    let dots = [];
    let count = null;
    if (slides.length <= 5) {
      middle.className = 'atlas-carousel__dots';
      dots = slides.map((_, i) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'atlas-carousel__dot';
        dot.setAttribute('aria-label', `${text.go} ${i + 1}`);
        dot.addEventListener('click', () => go(i));
        middle.append(dot);
        return dot;
      });
    } else {
      middle.className = 'atlas-carousel__count';
      count = middle;
    }
    controls.append(prev, middle, next);

    let raf = 0;
    const update = () => {
      raf = 0;
      const i = activeIndex();
      dots.forEach((dot, n) => dot.setAttribute('aria-current', String(n === i)));
      if (count) count.textContent = `${i + 1} / ${slides.length}`;
      prev.disabled = i <= 0;
      next.disabled = i >= slides.length - 1;
    };
    const schedule = () => { if (!raf) raf = requestAnimationFrame(update); };
    track.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    const onKey = (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
      else if (e.key === 'Home') { e.preventDefault(); scrollToLeft(0); }
      else if (e.key === 'End') { e.preventDefault(); scrollToLeft(maxScroll()); }
    };
    track.addEventListener('keydown', onKey);
    update();
    cleanups.push(() => {
      track.removeEventListener('scroll', schedule);
      window.removeEventListener('resize', schedule);
      track.removeEventListener('keydown', onKey);
      if (raf) cancelAnimationFrame(raf);
      controls.textContent = ''; // drops the buttons and their handlers so a later init starts clean
      delete el.dataset.carouselReady;
    });
  }
  return { destroy: () => cleanups.splice(0).forEach((fn) => fn()) };
}
