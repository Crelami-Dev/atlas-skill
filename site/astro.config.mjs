import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://crelami-dev.github.io',
  base: '/atlas-skill',
  redirects: {
    '/': '/atlas-skill/id/'
  },
  integrations: [
    starlight({
      title: 'Atlas-skill',
      description:
        'Suite desain frontend, token CSS, animasi Anime.js v4, gate browser multi-viewport, dan QA & keamanan untuk agen AI coding.',
      defaultLocale: 'id',
      locales: {
        id: {
          label: 'Bahasa Indonesia',
          lang: 'id'
        },
        en: {
          label: 'English',
          lang: 'en'
        }
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/Crelami-Dev/atlas-skill'
        }
      ],
      customCss: ['./src/styles/tokens.css', './src/styles/atlas-starlight.css'],
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 3
      },
      sidebar: [
        {
          label: 'Mulai Cepat & Instalasi',
          translations: { en: 'Getting Started' },
          items: [
            {
              label: 'Mulai Cepat 5 Menit',
              translations: { en: '5-Minute Quick Start' },
              slug: 'getting-started/quick-start'
            },
            {
              label: 'Pasang per Agen & CLI',
              translations: { en: 'Install by Agent & CLI' },
              slug: 'getting-started/install-by-agent'
            },
            {
              label: 'Instruksi Prompt',
              translations: { en: 'Prompt Instructions' },
              slug: 'guides/prompt-instructions'
            }
          ]
        },
        {
          label: 'Konsep & Alur Kerja',
          translations: { en: 'Concepts & Workflow' },
          items: [
            {
              label: 'Arsitektur: 3 Skill & 10 Modul',
              translations: { en: 'Architecture: 3 Skills & 10 Modules' },
              slug: 'concepts/architecture'
            },
            {
              label: 'Alur Kerja Fase 0–7',
              translations: { en: 'Phase Workflow (Phases 0–7)' },
              slug: 'workflow/phase-workflow'
            }
          ]
        },
        {
          label: 'Scene & Gerak',
          translations: { en: 'Scenes & Motion' },
          items: [
            {
              label: 'Ikhtisar 10 Scene & Mode Gerak',
              translations: { en: '10 Scenes Overview & Modes' },
              slug: 'scenes'
            },
            { label: 'pull-back', slug: 'scenes/pull-back' },
            { label: 'split-wipe', slug: 'scenes/split-wipe' },
            { label: 'horizontal-rail', slug: 'scenes/horizontal-rail' },
            { label: 'window-reveal', slug: 'scenes/window-reveal' },
            { label: 'mask-zoom', slug: 'scenes/mask-zoom' },
            { label: 'type-parting', slug: 'scenes/type-parting' },
            { label: 'parallax-depth', slug: 'scenes/parallax-depth' },
            { label: 'word-light', slug: 'scenes/word-light' },
            { label: 'step-assemble', slug: 'scenes/step-assemble' },
            { label: 'drift-type', slug: 'scenes/drift-type' }
          ]
        },
        {
          label: 'Panduan Sistem & Pola',
          translations: { en: 'Design & Engineering Guides' },
          items: [
            {
              label: 'Loop Otomatis (atlas-loops)',
              translations: { en: 'Self-Playing Loops (atlas-loops)' },
              slug: 'guides/loops'
            },
            {
              label: 'Komposisi & 10 Arketipe',
              translations: { en: 'Composition & 10 Archetypes' },
              slug: 'guides/components-and-composition'
            },
            {
              label: 'Tipografi',
              translations: { en: 'Typography System' },
              slug: 'guides/typography'
            },
            {
              label: 'Teks Ringkas (check-copy)',
              translations: { en: 'Concise Copy Budgets' },
              slug: 'guides/concise-copy'
            },
            {
              label: 'Citra & Foto Berlisensi',
              translations: { en: 'Imagery & Licensed Photos' },
              slug: 'guides/imagery'
            },
            {
              label: 'Mobile & Tablet',
              translations: { en: 'Phones & Tablets' },
              slug: 'guides/mobile-and-tablet'
            },
            {
              label: 'Anti-Slop: 18 Pola',
              translations: { en: 'Anti-Slop: 18 Patterns' },
              slug: 'anti-slop/patterns'
            },
            {
              label: 'Referensi Teknis Lainnya',
              translations: { en: 'Additional Technical References' },
              slug: 'guides/references'
            }
          ]
        },
        {
          label: 'Gate, Pemeriksa & QA',
          translations: { en: 'Gates, Checkers & QA' },
          items: [
            {
              label: 'Gate Deterministik & Pemeriksa',
              translations: { en: 'Deterministic Gates & Checkers' },
              slug: 'checks/gates-and-checkers'
            },
            {
              label: 'Kamus Kode Temuan (quick-check)',
              translations: { en: 'Findings Dictionary (quick-check)' },
              slug: 'checks/findings-dictionary'
            },
            {
              label: 'Suite QA & Keamanan (--with-qa)',
              translations: { en: 'QA & Security Suite (--with-qa)' },
              slug: 'qa/project-qa-suite'
            }
          ]
        },
        {
          label: 'Evaluasi, Rilis & Bantuan',
          translations: { en: 'Evaluation, Releases & Help' },
          items: [
            {
              label: 'Evaluasi Empiris (Blind A/B)',
              translations: { en: 'Empirical Evaluation (Blind A/B)' },
              slug: 'evaluation/blind-ab'
            },
            {
              label: 'Pemecahan Masalah',
              translations: { en: 'Troubleshooting' },
              slug: 'guides/troubleshooting'
            },
            {
              label: 'Riwayat Versi (CHANGELOG)',
              translations: { en: 'Changelog' },
              slug: 'changelog'
            },
            {
              label: 'Panduan Kontribusi',
              translations: { en: 'Contributing Guide' },
              slug: 'guides/contributing'
            }
          ]
        }
      ]
    })
  ]
});
