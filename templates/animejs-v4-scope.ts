/**
 * Reusable Anime.js v4 Component Scope Helper (React / Vanilla / Framework-agnostic)
 * Enforces official Anime.js v4 APIs: createScope, mediaQueries (prefers-reduced-motion), and clean revert().
 */
import {
  animate,
  createScope,
  createTimeline,
  createLayout,
  onScroll,
  spring,
  splitText,
  stagger,
  svg,
  utils,
  waapi,
  type Scope,
} from 'animejs';

export interface MotionScopeContext {
  reduceMotion: boolean;
  isMobile: boolean;
}

/**
 * Mounts an Anime.js v4 scope bound to a root DOM container and returns a deterministic cleanup function.
 * Always keeps initial HTML visible if JS is disabled or reduced motion is preferred.
 */
export function mountAtlasMotion(
  rootElement: HTMLElement | null,
  setup: (ctx: MotionScopeContext, scope: Scope) => void
): () => void {
  if (!rootElement) return () => {};

  const scope = createScope({
    root: rootElement,
    mediaQueries: {
      reduceMotion: '(prefers-reduced-motion: reduce)',
      isMobile: '(max-width: 767px)',
    },
  }).add((self) => {
    const matches = (self?.matches ?? {}) as Record<string, boolean>;
    setup(
      {
        reduceMotion: Boolean(matches.reduceMotion),
        isMobile: Boolean(matches.isMobile),
      },
      self
    );
  });

  return () => {
    scope.revert();
  };
}

export {
  animate,
  createScope,
  createTimeline,
  createLayout,
  onScroll,
  spring,
  splitText,
  stagger,
  svg,
  utils,
  waapi,
};
