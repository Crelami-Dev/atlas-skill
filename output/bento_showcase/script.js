/* ==========================================================================
   Atlas Design System — Vanilla Interactive Components
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Accessible Mobile Navigation Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      navToggle.innerHTML = isOpen ? '✕' : '☰';
    });

    // Close menu when clicking outside or pressing Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navMenu.classList.contains('open')) {
        navMenu.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.innerHTML = '☰';
      }
    });

    // Close mobile menu on link navigation
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navMenu.classList.contains('open')) {
          navMenu.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
          navToggle.innerHTML = '☰';
        }
      });
    });
  }

  // 2. Accessible FAQ Accordions
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    if (question) {
      question.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        
        // Close other items
        faqItems.forEach(other => {
          if (other !== item) {
            other.classList.remove('active');
            const otherBtn = other.querySelector('.faq-question');
            if (otherBtn) {
              otherBtn.setAttribute('aria-expanded', 'false');
              otherBtn.querySelector('span:last-child').textContent = '+';
            }
          }
        });

        // Toggle current item
        item.classList.toggle('active', !isActive);
        question.setAttribute('aria-expanded', !isActive ? 'true' : 'false');
        const icon = question.querySelector('span:last-child');
        if (icon) {
          icon.textContent = !isActive ? '−' : '+';
        }
      });
    }
  });
});


    // Atlas Motion Adapter Runtime Integration
    (function() {
      const motionPlan = {
  "engine": "animejs-v4-with-css-fallback",
  "engineCompatibility": "Anime.js v4.x official runtime target; native CSS fallback when library is not loaded",
  "primaryPattern": "masked-headline",
  "patterns": [
    {
      "id": "masked-headline",
      "name": "Masked Headline",
      "intent": "Establish immediate typographic hierarchy on load by revealing headlines line-by-line from baseline without full-page layout shift.",
      "useCase": "Hero section display typography (h1) capped at two lines.",
      "trigger": "load",
      "targets": [
        ".hero h1 [data-line]",
        ".lines [data-line]"
      ],
      "timing": {
        "durationMs": 900,
        "delayMs": 150,
        "staggerMs": 110
      },
      "easing": {
        "token": "--ease-expo",
        "bezier": "cubic-bezier(0.16, 1, 0.3, 1)",
        "animeName": "easeOutExpo"
      },
      "stagger": {
        "intervalMs": 110,
        "startMs": 150,
        "from": "first"
      },
      "reducedMotionFallback": {
        "behavior": "instant",
        "description": "Headlines render instantly in place without transform or delay."
      },
      "performanceConsiderations": "Uses transform: translateY and overflow: hidden parent; GPU accelerated, zero layout reflow.",
      "lifecycle": {
        "cleanupRequirements": "Reset will-change and clear inline transforms upon animation completion.",
        "removesListeners": false,
        "resetsTransform": false
      },
      "responsiveBehavior": "Preserved across desktop and mobile viewports with responsive font size clamp.",
      "sourceProvenance": {
        "sourceFile": "library/motions.json",
        "originalId": "masked-headline",
        "license": "MIT (Leonxlnx, 2026)"
      },
      "adapterConfig": {
        "anime": {
          "translateY": [
            "105%",
            "0%"
          ],
          "opacity": [
            1,
            1
          ],
          "duration": 900,
          "easing": "cubicBezier(0.16, 1, 0.3, 1)",
          "delay": 150
        }
      }
    },
    {
      "id": "shutter-image",
      "name": "Shutter Image",
      "intent": "Draw focus to the single hero or showcase image by opening an aperture clip-path while settling scale.",
      "useCase": "Single focal hero image or primary product showcase.",
      "trigger": "load",
      "targets": [
        ".hero [data-shutter]",
        ".showcase [data-shutter]"
      ],
      "timing": {
        "durationMs": 1100,
        "delayMs": 100,
        "staggerMs": 0
      },
      "easing": {
        "token": "--ease-expo",
        "bezier": "cubic-bezier(0.16, 1, 0.3, 1)",
        "animeName": "easeOutExpo"
      },
      "stagger": null,
      "reducedMotionFallback": {
        "behavior": "instant",
        "description": "Clip-path set to inset(0) and scale(1) immediately."
      },
      "performanceConsiderations": "Requires composited clip-path and transform scale; fetchpriority=high on image.",
      "lifecycle": {
        "cleanupRequirements": "Remove clip-path once fully opened to allow natural image overlays or tooltips.",
        "removesListeners": false,
        "resetsTransform": false
      },
      "responsiveBehavior": "Maintains aspect ratio; clip-path opens vertically on narrow screens.",
      "sourceProvenance": {
        "sourceFile": "library/motions.json",
        "originalId": "shutter-image",
        "license": "MIT (Leonxlnx, 2026)"
      },
      "adapterConfig": {
        "anime": {
          "clipPath": [
            "inset(0 100% 0 0)",
            "inset(0 0% 0 0)"
          ],
          "scale": [
            1.12,
            1
          ],
          "duration": 1100,
          "easing": "cubicBezier(0.16, 1, 0.3, 1)"
        }
      }
    }
  ],
  "reducedMotionBehavior": "instant",
  "rationale": "Selected 'masked-headline' for crisp value proposition presentation. Selected 'shutter-image' for hero visual aperture reveal.",
  "tokens": {
    "easeOut": "cubic-bezier(0.22, 1, 0.36, 1)",
    "easeExpo": "cubic-bezier(0.16, 1, 0.3, 1)",
    "easeSoft": "cubic-bezier(0.33, 1, 0.68, 1)",
    "easeExit": "cubic-bezier(0.55, 0.055, 0.675, 0.19)",
    "durationRevealMs": 800,
    "durationHeroMs": 1100,
    "staggerLineMs": 110
  }
};
      
      function runMotion() {
        if (typeof AtlasMotionAdapter === 'undefined') {
          // Graceful fallback if adapter script failed to load
          document.querySelectorAll('.lines [data-line], .hero h1 [data-line]').forEach(el => {
            el.style.transform = 'none';
            el.style.opacity = '1';
          });
          return;
        }
        
        const adapter = new AtlasMotionAdapter();
        if (motionPlan.patterns && motionPlan.patterns.length > 0) {
          motionPlan.patterns.forEach(spec => {
            adapter.execute(spec);
          });
        }
        window.__atlasMotionAdapterInstance = adapter;
      }
      
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runMotion);
      } else {
        runMotion();
      }
    })();
