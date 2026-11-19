#!/usr/bin/env node
/**
 * Atlas v6.0 — Deterministic Art Direction & Structural Archetype Dealer (deal-direction.mjs)
 * Scores prompts using whole-word boundaries across 12 curated directions (covering SaaS, Hospitality,
 * Dashboards, Portfolios, DevDocs, Events, Healthcare, Nonprofits, Weddings, Legal/Corporate, E-Commerce,
 * and Education) with distinct macro layouts, font pairings, and WCAG AA verified token pairs.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const STRUCTURAL_ARCHETYPES = {
  'editorial-index-rail': {
    id: 'editorial-index-rail',
    name: 'Editorial Index Rail & Practice Matrix',
    structure: 'Left sticky numbered index rail (240px) + main column with numbered practice/service matrix (01-04), credentials index, and direct inquiry desk.',
    allowsWorkbenchHero: false,
    whenToUse: 'Legal firms, management/tax consultants, corporate profiles, policy institutes, and professional advisory services.',
    whenForbidden: 'Forbidden for single-product retail storefronts, real-time operational dashboards, or wedding invitations.'
  },
  'poster-full-bleed': {
    id: 'poster-full-bleed',
    name: 'Full-Bleed Architectural Poster & Timetable/Ledger',
    structure: 'Full-width architectural poster masthead (oversized date/venue/scene composition + docked visit bar) followed by speaker/dish plates and chronological schedule or 2-column print menu.',
    allowsWorkbenchHero: false,
    whenToUse: 'Festivals, conferences, concerts, public events, and hospitality venues (restaurants, roasteries, cafes, bistros).',
    whenForbidden: 'Forbidden for B2B analytics dashboards, API documentation portals, or legal/audit firms.'
  },
  'split-screen': {
    id: 'split-screen',
    name: 'Asymmetric Split-Screen & Live Application Calculator',
    structure: 'Asymmetric 42/58 split hero pairing product value thesis with a focused interactive domain calculator/estimator (only for software/app domains).',
    allowsWorkbenchHero: true,
    whenToUse: 'B2B SaaS applications, productivity/automation tools, and interactive software products.',
    whenForbidden: 'Forbidden for restaurants, photography portfolios, weddings, legal firms, travel itineraries, fashion lookbooks, or nonprofit narratives.'
  },
  'dashboard-shell': {
    id: 'dashboard-shell',
    name: 'Full-Viewport Operational Dashboard Shell',
    structure: 'Collapsible left navigation rail + compact KPI telemetry strip + dense filterable operational table + slide-over detail drawer (zero marketing hero).',
    allowsWorkbenchHero: true,
    whenToUse: 'Operational dashboards, logistics/fleet dispatch, POS/cashier systems, fintech ledgers, and CRM/ERP workspaces.',
    whenForbidden: 'Forbidden for public editorial landing pages, hospitality, portfolios, events, or corporate profiles.'
  },
  'ledger-table-first': {
    id: 'ledger-table-first',
    name: 'Triage Ledger & Schedule Matrix First',
    structure: 'Immediate service triage bar above the fold + structured practitioner/rate schedule matrix table + transparent tariff & preparation guide.',
    allowsWorkbenchHero: false,
    whenToUse: 'Healthcare clinics, hospitals, medical laboratories, financial/accounting rate boards, and academic cohort schedules.',
    whenForbidden: 'Forbidden for fashion lookbooks, wedding invitations, or photography monographs.'
  },
  'narrative-long-scroll': {
    id: 'narrative-long-scroll',
    name: 'Centered Longform Editorial Dossier',
    structure: 'Single-column 68ch editorial narrative with margin facts, inline stacked financial allocation bar, audited distribution table, and bottom pledge sheet.',
    allowsWorkbenchHero: false,
    whenToUse: 'Nonprofits/NGOs, donation campaigns, annual impact reports, research foundations, and longform journalism.',
    whenForbidden: 'Forbidden for multi-variant e-commerce stores, operational dashboards, or SDK documentation.'
  },
  'gallery-masonry': {
    id: 'gallery-masonry',
    name: 'Exhibition Monograph & Asymmetric Masonry Plates',
    structure: 'Minimal top colophon + asymmetric multi-ratio exhibition plate grid (16:9 panoramic paired with 4:5 vertical plates, numbered 01-06) + quiet inquiry sheet.',
    allowsWorkbenchHero: false,
    whenToUse: 'Photography portfolios, architecture studios, creative/branding agencies, art galleries, and high-fashion editorial lookbooks.',
    whenForbidden: 'Forbidden to include search bars, filter dropdowns, or Reset buttons; forbidden for SaaS apps or medical clinics.'
  },
  'docs-three-pane': {
    id: 'docs-three-pane',
    name: 'Three-Pane Technical Reference Portal',
    structure: 'Left navigation tree + center 68ch technical reference & multi-tab code specimen + right On-This-Page anchor rail, opening directly with install command.',
    allowsWorkbenchHero: false,
    whenToUse: 'Developer documentation, SDK/API references, CLI tools, open-source libraries, and infrastructure guides.',
    whenForbidden: 'Forbidden for consumer storefronts, restaurants, events, real estate, or visual portfolios.'
  },
  'catalogue-grid': {
    id: 'catalogue-grid',
    name: 'Curated Product & Property Showcase / Configurator',
    structure: 'Breadcrumb header + 60/40 multi-angle gallery stage or curated unit grid + tactile variant/floorplan selector + measured specification table.',
    allowsWorkbenchHero: false,
    whenToUse: 'Physical product e-commerce, real estate/property developments, artisanal goods, and structured course catalogues.',
    whenForbidden: 'Forbidden to use fake scarcity timers or SaaS workbench cards.'
  },
  'timeline-story': {
    id: 'timeline-story',
    name: 'Monumental Crest & Chronological Story/Itinerary',
    structure: 'Centered ceremonial crest or expedition cover + chronological day-by-day/hour-by-hour timeline + interactive venue/route map + RSVP/booking sheet.',
    allowsWorkbenchHero: false,
    whenToUse: 'Wedding invitations, celebrations, travel/tour itineraries, cultural expeditions, and heritage timelines.',
    whenForbidden: 'Forbidden to use SaaS pricing tiers, corporate dashboard widgets, or search/filter toolbars.'
  }
};

export const DIRECTIONS = [
  {
    id: 'alabaster-botanical-studio',
    archetypeId: 'split-screen',
    name: 'Alabaster Ceramic & Botanical Eucalyptus',
    category: 'warm-neutral',
    bestFor: ['saas', 'studio', 'ai', 'productivity', 'agency', 'workspace', 'general'],
    keywords: [
      'saas', 'ai', 'workspace', 'produktivitas', 'productivity',
      'kolaborasi', 'collaboration', 'catatan', 'notes', 'workflow',
      'otomatisasi', 'automation', 'invoicing', 'contractor', 'freelance'
    ],
    routeType: 'interactive-tool-split',
    macroLayout: 'Asymmetric 42/58 Split Hero + Live Interactive Calculator/Estimator (No generic 3-card row)',
    forbiddenPatterns: [
      'Do not render debug state-switcher dropdowns (Populated/Loading/Empty/Error) in production UI.',
      'Do not use purple-blue gradients or fabricated customer counts.'
    ],
    archetype: 'Sculptural Editorial Split + Live Domain Calculator Workbench',
    fonts: {
      display: "'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      sans: "'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
    },
    tokens: {
      bg: '#f6f6f2',
      surface: '#ecece6',
      elevated: '#ffffff',
      tint: '#e3efe9',
      text: '#151c19',
      muted: '#495650',
      accent: '#1f5c46',
      accentHover: '#174736',
      accentSoft: '#d7ebe2',
      accentContrast: '#f8fbf9',
      border: '#d8ddd9',
      borderStrong: '#b9c2bc',
      darkBand: '#141c18',
      darkSurface: '#1d2823',
      darkBorder: '#2e3d36',
      darkText: '#f1f5f2',
      darkMuted: '#9eb0a7'
    },
    cadence: ['base-alabaster (Split Hero + Calculator)', 'dark-forest-anchor (Workflow Architecture)', 'soft-sage-tint (Export Schema & Trial Signup)'],
    visualProofRule: 'First fold features a working domain calculator or interactive invoice/workflow preview.'
  },
  {
    id: 'linen-espresso-craft',
    archetypeId: 'poster-full-bleed',
    name: 'Warm Linen & Roasted Walnut Atelier',
    category: 'warm-neutral',
    bestFor: ['hospitality', 'coffee', 'bakery', 'restaurant', 'culinary', 'roastery', 'bistro'],
    keywords: [
      'kopi', 'coffee', 'cafe', 'kafe', 'resto', 'restaurant', 'restoran', 'roti', 'bakery',
      'kuliner', 'makanan', 'food', 'artisan', 'atelier', 'tea', 'teh',
      'roastery', 'bistro', 'warung', 'kedai', 'seduh', 'sourdough', 'dining'
    ],
    routeType: 'atmospheric-cover-menu',
    macroLayout: 'Full-Width Atmospheric Architectural Scene + Docked Hours/Address Bar + Two-Column Print Menu Ledger (Zero search inputs or dropdowns)',
    forbiddenPatterns: [
      'Do NOT use a SaaS 2-column hero with a right-hand search/filter/Reset card.',
      'Do NOT use small abstract line charts as visual proof; use a rich multi-layered architectural/table scene or food photography.'
    ],
    archetype: 'Full-Bleed Warm Architectural Scene + Traditional Two-Column Print Menu Ledger',
    fonts: {
      display: "'Fraunces', Georgia, serif",
      sans: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace"
    },
    tokens: {
      bg: '#f8f5ef',
      surface: '#efe9de',
      elevated: '#ffffff',
      tint: '#efe3d3',
      text: '#211b16',
      muted: '#594d43',
      accent: '#694024',
      accentHover: '#50301a',
      accentSoft: '#eddcc9',
      accentContrast: '#fcfaf7',
      border: '#dfd6c7',
      borderStrong: '#c4b7a3',
      darkBand: '#1e1814',
      darkSurface: '#2a221d',
      darkBorder: '#3d322b',
      darkText: '#f6f1ea',
      darkMuted: '#b5a89a'
    },
    cadence: ['warm-linen (Wide Atmospheric Roastery Scene + Hours Bar)', 'elevated-ivory (Two-Column Print Menu with Dotted Leaders)', 'deep-espresso (Bean Origin & Seating Details)'],
    visualProofRule: 'Lead with a wide atmospheric scene or rich culinary composition and a docked practical visit bar (hours, address, walk-in policy).'
  },
  {
    id: 'nordic-fjord-precision',
    archetypeId: 'dashboard-shell',
    name: 'Nordic Mineral Mist & Deep Fjord',
    category: 'cool-mineral',
    bestFor: ['dashboard', 'fintech', 'logistics', 'analytics', 'enterprise', 'data'],
    keywords: [
      'dashboard', 'admin', 'fintech', 'keuangan', 'finance', 'financial', 'kasir', 'pos',
      'logistik', 'logistics', 'analitik', 'analytics', 'data', 'stok', 'inventory', 'erp',
      'crm', 'telemetry', 'ledger', 'pembukuan', 'akuntansi', 'accounting', 'warehouse',
      'gudang', 'pengiriman', 'kurir', 'dispatcher', 'delivery', 'perbankan', 'banking', 'investasi', 'investment', 'reksadana', 'wealth', 'treasury'
    ],
    routeType: 'operational-workbench',
    macroLayout: 'Full-Viewport Operational App Shell (Left Navigation Rail + Compact KPI Strip + Dense Filterable Data Table + Detail Drawer)',
    forbiddenPatterns: [
      'Do NOT include a marketing hero paragraph or promotional banner inside an operational dashboard.',
      'Do NOT expose a debug state switcher (Populated/Loading/Empty/Error) to end users.'
    ],
    archetype: 'Daylight Operational App Shell + High-Contrast Fjord Sidebar & Tabular Ledger',
    fonts: {
      display: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      sans: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace"
    },
    tokens: {
      bg: '#f2f6fa',
      surface: '#e5edf5',
      elevated: '#ffffff',
      tint: '#d9e8f5',
      text: '#0f1a26',
      muted: '#455565',
      accent: '#164e6d',
      accentHover: '#0f3952',
      accentSoft: '#d5e8f2',
      accentContrast: '#f7fbfd',
      border: '#d5dee6',
      borderStrong: '#b4c2cf',
      darkBand: '#101923',
      darkSurface: '#182533',
      darkBorder: '#283a4d',
      darkText: '#eef3f7',
      darkMuted: '#9eb0c2'
    },
    cadence: ['mineral-daylight (App Topbar + KPI Strip)', 'elevated-panel (Dense Filterable Dispatch Table)', 'ice-tint (Active Courier Shift Roster)'],
    visualProofRule: '80%+ of first fold is the live operational table, status pill filters, and courier shift telemetry with aligned tabular numerals.'
  },
  {
    id: 'travertine-terracotta-gallery',
    archetypeId: 'gallery-masonry',
    name: 'Travertine Stone & Architectural Terracotta',
    category: 'warm-neutral',
    bestFor: ['portfolio', 'architecture', 'photography', 'culture', 'gallery', 'museum'],
    keywords: [
      'portfolio', 'portofolio', 'arsitek', 'arsitektur', 'architecture', 'architect',
      'foto', 'fotografi', 'photography', 'photographer', 'galeri', 'gallery', 'pameran',
      'exhibition', 'museum', 'interior', 'kurator', 'monograph', 'katalog seni', 'documentary'
    ],
    routeType: 'exhibition-masonry',
    macroLayout: 'Minimal Top Colophon Header + Asymmetric Multi-Scale Exhibition Plate Grid (01-03) + Quiet Bottom Biography & Inquiry Sheet',
    forbiddenPatterns: [
      'Do NOT put search inputs, select dropdowns, or Reset Filter buttons on a photography/architecture monograph.',
      'Do NOT use small uniform cards; vary plate aspect ratios (wide 16:9 panoramic plate paired with 4:5 vertical plates).'
    ],
    archetype: 'Exhibition Monograph Plate Grid + Numbered Curatorial Captions',
    fonts: {
      display: "'Cormorant Garamond', Georgia, serif",
      sans: "'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', ui-monospace, SFMono-Regular, monospace"
    },
    tokens: {
      bg: '#f7f3ee',
      surface: '#ede6dd',
      elevated: '#ffffff',
      tint: '#f3e1d8',
      text: '#1e1815',
      muted: '#574b44',
      accent: '#8f3519',
      accentHover: '#6e2812',
      accentSoft: '#f2dad0',
      accentContrast: '#fdf9f7',
      border: '#ded5ca',
      borderStrong: '#c2b4a5',
      darkBand: '#1b1614',
      darkSurface: '#27201d',
      darkBorder: '#3b312c',
      darkText: '#f5efe9',
      darkMuted: '#b5a79d'
    },
    cadence: ['travertine-light (Minimal Colophon + Large Asymmetric Plate Grid)', 'obsidian-clay (Fieldwork Essay & Exhibition History)', 'terracotta-tint (Print & Assignment Inquiry)'],
    visualProofRule: 'Open directly with large, richly detailed photographic plates and curatorial captions occupying 75%+ of the viewport.'
  },
  {
    id: 'obsidian-terminal-noir',
    archetypeId: 'docs-three-pane',
    name: 'Obsidian Carbon & Terminal Cyan (Dark Mode)',
    category: 'dark-high-contrast',
    bestFor: ['devtools', 'cli', 'cybersecurity', 'infrastructure', 'cloud', 'developer', 'code'],
    keywords: [
      'dev', 'developer', 'devtools', 'cli', 'terminal', 'sdk', 'api', 'cybersecurity',
      'security', 'keamanan', 'cloud', 'server', 'infrastruktur', 'infrastructure',
      'compiler', 'database', 'git', 'kode', 'code', 'debugger', 'monitoring',
      'javascript', 'typescript', 'library', 'npm', 'quickstart', 'documentation landing'
    ],
    routeType: 'three-pane-devdocs',
    macroLayout: 'Three-Pane Developer Documentation Portal (Left Sidebar Tree + Center Technical Prose & Tabbed Code Examples + Right On-This-Page Rail)',
    forbiddenPatterns: [
      'Do NOT use a marketing hero banner; open directly into the documentation header, version badge, and install command.'
    ],
    archetype: 'Dark Carbon Three-Pane Documentation Hub + Tabbed Code & Symbol Reference',
    fonts: {
      display: "'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      sans: "'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'Fira Code', 'JetBrains Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#0d1117',
      surface: '#151b23',
      elevated: '#1c2430',
      tint: '#132235',
      text: '#ecf2f8',
      muted: '#9fb1c6',
      accent: '#58a6ff',
      accentHover: '#79b8ff',
      accentSoft: '#162942',
      accentContrast: '#071019',
      border: '#2a3441',
      borderStrong: '#415063',
      darkBand: '#070a0e',
      darkSurface: '#10151c',
      darkBorder: '#242e3b',
      darkText: '#f0f6fc',
      darkMuted: '#9fb1c6'
    },
    cadence: ['obsidian-base (3-Pane Docs Shell + Install Command)', 'elevated-slate (Interactive Code Tabs & API Signatures)', 'deep-carbon (Backoff Architecture & Migration Notes)'],
    visualProofRule: 'Show a multi-tab syntax-highlighted code specimen, terminal install strip, and live API method filter.'
  },
  {
    id: 'bauhaus-signal-poster',
    archetypeId: 'poster-full-bleed',
    name: 'Bauhaus Stark Poster & Signal Cobalt',
    category: 'bold-high-contrast',
    bestFor: ['event', 'festival', 'conference', 'concert', 'music', 'tickets', 'symposium'],
    keywords: [
      'event', 'acara', 'festival', 'konferensi', 'conference', 'konser', 'concert',
      'musik', 'music', 'tiket', 'ticket', 'ticketing', 'symposium', 'simposium',
      'hackathon', 'meetup', 'panggung', 'lineup', 'jadwal acara', 'public talk', 'diskusi publik'
    ],
    routeType: 'swiss-poster-timetable',
    macroLayout: 'Full-Width Swiss Architectural Poster Masthead (Giant Date/Time/Venue Grid) + Speaker Portrait Strip + Chronological Timetable',
    forbiddenPatterns: [
      'Do NOT use a 2-column SaaS hero with a right-hand workbench box.',
      'Do NOT use tiny sparse arcs with empty whitespace; build a bold geometric architectural poster composition.'
    ],
    archetype: 'Swiss Typographic Poster Grid + Speaker Plates & Chronological Run-of-Show',
    fonts: {
      display: "'Syne', 'Space Grotesk', sans-serif",
      sans: "'Work Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'Space Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#ffffff',
      surface: '#eef2ff',
      elevated: '#ffffff',
      tint: '#e0e7ff',
      text: '#090d16',
      muted: '#3b4354',
      accent: '#0038a8',
      accentHover: '#002675',
      accentSoft: '#dbeafe',
      accentContrast: '#ffffff',
      border: '#cbd5e1',
      borderStrong: '#64748b',
      darkBand: '#090d16',
      darkSurface: '#131b2e',
      darkBorder: '#293548',
      darkText: '#f8fafc',
      darkMuted: '#a8b6cc'
    },
    cadence: ['stark-poster (Full-Width Date/Venue/Title Architectural Poster)', 'cobalt-tint (Speaker Profiles & Run-of-Show Table)', 'midnight-stage (Accessibility & Seat Registration Strip)'],
    visualProofRule: 'Anchor the top of the page with a bold full-width Swiss poster grid pairing oversized date/time typography with an architectural venue graphic.'
  },
  {
    id: 'clinical-emerald-trust',
    archetypeId: 'ledger-table-first',
    name: 'Clinical Porcelain & Botanical Emerald',
    category: 'cool-clinical',
    bestFor: ['healthcare', 'medical', 'clinic', 'pharmacy', 'wellness', 'laboratory', 'dental'],
    keywords: [
      'medis', 'medical', 'kesehatan', 'healthcare', 'health', 'klinik', 'clinic',
      'rumah sakit', 'hospital', 'dokter', 'doctor', 'apotek', 'pharmacy', 'lab',
      'laboratorium', 'pasien', 'patient', 'telemedicine', 'gigi', 'dental', 'fisioterapi'
    ],
    routeType: 'clinical-service-finder',
    macroLayout: 'Triage Service Header + Specialist Schedule Matrix + Transparent Tariff & Preparation Guide',
    forbiddenPatterns: [
      'Do NOT invent medical guarantees or patient testimonials.'
    ],
    archetype: 'Calm Clinical Clarity + Immediate Appointment & Practitioner Schedule',
    fonts: {
      display: "'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      sans: "'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'Source Code Pro', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f2f8f6',
      surface: '#e3f0ec',
      elevated: '#ffffff',
      tint: '#d5ebe4',
      text: '#0d211b',
      muted: '#3b574e',
      accent: '#0d6345',
      accentHover: '#084a33',
      accentSoft: '#d1fae5',
      accentContrast: '#ffffff',
      border: '#c7ddd6',
      borderStrong: '#9dbfb5',
      darkBand: '#091914',
      darkSurface: '#112820',
      darkBorder: '#214237',
      darkText: '#ecfdf5',
      darkMuted: '#9dc0b5'
    },
    cadence: ['porcelain-mint (Service Triage & Doctor Availability)', 'elevated-white (Transparent Procedure Tariffs)', 'deep-emerald (Emergency & Lab Preparation Protocol)'],
    visualProofRule: 'Prioritize calm readability, real practitioner/facility schedules, and transparent service availability.'
  },
  {
    id: 'scholarly-ink-chronicle',
    archetypeId: 'narrative-long-scroll',
    name: 'Scholarly Paper & Oxford Navy Chronicle',
    category: 'cool-editorial',
    bestFor: ['nonprofit', 'donation', 'publishing', 'research', 'journal', 'annual-report'],
    keywords: [
      'donasi', 'donation', 'nonprofit', 'yayasan', 'foundation', 'jurnal', 'journal',
      'riset', 'research', 'perpustakaan', 'ensiklopedia', 'transparansi', 'literacy',
      'literasi', 'amal', 'charity', 'filantropi', 'philanthropy', 'bantuan', 'laporan tahunan', 'ngo', 'lsm', 'non-profit', 'kemanusiaan', 'humanitarian', 'relawan', 'volunteer', 'wakaf', 'zakat'
    ],
    routeType: 'longform-editorial-dossier',
    macroLayout: 'Centered Longform Editorial Dossier (68ch Single-Column Narrative + Inline Stacked Financial Bar + Audited Delivery Table + Embedded Pledge Box)',
    forbiddenPatterns: [
      'Do NOT use a 2-column SaaS split hero or search/reset toolbar.',
      'Do NOT claim real payment processing on a demonstration donation form.'
    ],
    archetype: 'Single-Column Editorial Dossier + Margin Facts & Audited Impact Ledger',
    fonts: {
      display: "'Newsreader', Georgia, serif",
      sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f7f8fa',
      surface: '#eceff4',
      elevated: '#ffffff',
      tint: '#e2e8f0',
      text: '#111827',
      muted: '#465061',
      accent: '#1e3a8a',
      accentHover: '#172554',
      accentSoft: '#dbeafe',
      accentContrast: '#ffffff',
      border: '#d1d5db',
      borderStrong: '#9ca3af',
      darkBand: '#0f172a',
      darkSurface: '#1e293b',
      darkBorder: '#334155',
      darkText: '#f8fafc',
      darkMuted: '#9fb0c7'
    },
    cadence: ['crisp-paper (Single-Column Editorial Dossier & Allocation Breakdown)', 'elevated-sheet (Audited Village Distribution Table)', 'slate-tint (Transparent Simulation Pledge Box)'],
    visualProofRule: 'Lead with an editorial masthead, inline stacked fund-allocation graphic, and verified distribution ledger.'
  },
  {
    id: 'velvet-champagne-atelier',
    archetypeId: 'timeline-story',
    name: 'Champagne Silk & Botanical Burgundy (Celebration & Wedding)',
    category: 'warm-editorial',
    bestFor: ['wedding', 'pernikahan', 'invitation', 'undangan', 'celebration', 'florist', 'bridal'],
    keywords: [
      'pernikahan', 'wedding', 'undangan', 'invitation', 'mempelai', 'resepsi', 'akad',
      'pengantin', 'bridal', 'bride', 'groom', 'lamaran', 'engagement', 'rsvp', 'florist', 'anniversary'
    ],
    routeType: 'monumental-invitation-scroll',
    macroLayout: 'Centered Archival Invitation Crest + Couple Story & Event Timeline + Interactive RSVP & Gift/Location Sheet',
    forbiddenPatterns: [
      'Do NOT use SaaS cards, search bars, or corporate dashboard widgets on a wedding/celebration site.'
    ],
    archetype: 'Centered Editorial Crest + Chronological Ceremony Timeline & RSVP Sheet',
    fonts: {
      display: "'Cormorant Garamond', Georgia, serif",
      sans: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'IBM Plex Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#fbf8f3',
      surface: '#f3ece1',
      elevated: '#ffffff',
      tint: '#f5e4e6',
      text: '#231719',
      muted: '#5e494d',
      accent: '#6b2737',
      accentHover: '#521c29',
      accentSoft: '#f4dce0',
      accentContrast: '#fdfafb',
      border: '#e2d6c5',
      borderStrong: '#c7b59d',
      darkBand: '#211316',
      darkSurface: '#2f1c20',
      darkBorder: '#472c32',
      darkText: '#faf3f0',
      darkMuted: '#c2aeb2'
    },
    cadence: ['champagne-silk (Monumental Couple Crest & Date)', 'elevated-ivory (Akad & Reception Timeline + Dress Code)', 'deep-burgundy (Love Story & Gallery Plates)', 'rose-tint (RSVP Confirmation & Venue Map)'],
    visualProofRule: 'Center the first fold around an ornate botanical/architectural crest or couple portrait frame with clear ceremony date and time.'
  },
  {
    id: 'savile-navy-counsel',
    archetypeId: 'editorial-index-rail',
    name: 'Savile Parchment & Oxford Counsel (Legal & Corporate Advisory)',
    category: 'cool-authoritative',
    bestFor: ['legal', 'law', 'hukum', 'consulting', 'corporate', 'advisory', 'notary', 'accounting'],
    keywords: [
      'hukum', 'law', 'legal', 'advokat', 'pengacara', 'attorney', 'notaris', 'notary',
      'konsultan', 'consultant', 'consulting', 'company profile', 'korporat', 'corporate',
      'advisory', 'firma', 'litigasi', 'litigation', 'pajak', 'compliance', 'audit'
    ],
    routeType: 'authority-practice-ledger',
    macroLayout: 'Authoritative Masthead + Numbered Practice Areas Grid (01-04) + Partner Credentials & Case Precedent Index + Consultation Request',
    forbiddenPatterns: [
      'Do NOT use playful startups emojis, bouncy animations, or SaaS pricing tiers for a legal/advisory firm.'
    ],
    archetype: 'Architectural Practice Matrix + Partner Credentials & Consultation Desk',
    fonts: {
      display: "'Libre Baskerville', Georgia, serif",
      sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'IBM Plex Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f5f7fa',
      surface: '#e9edf4',
      elevated: '#ffffff',
      tint: '#dde5f0',
      text: '#0f172a',
      muted: '#434e65',
      accent: '#16325c',
      accentHover: '#0e2240',
      accentSoft: '#d8e3f2',
      accentContrast: '#ffffff',
      border: '#cbd5e1',
      borderStrong: '#94a3b8',
      darkBand: '#0b1528',
      darkSurface: '#15233d',
      darkBorder: '#273a5c',
      darkText: '#f1f5f9',
      darkMuted: '#9db0ce'
    },
    cadence: ['parchment-light (Firm Mandate & Practice Area Matrix)', 'oxford-navy (Representative Mandates & Regulatory Publications)', 'elevated-white (Partner Directory & Confidential Inquiry)'],
    visualProofRule: 'Anchor the first fold with numbered practice areas, verifiable bar/regulatory credentials, and direct partner inquiry.'
  },
  {
    id: 'terracotta-artisan-store',
    archetypeId: 'catalogue-grid',
    name: 'Sunlit Clay & Burnt Terracotta Storefront (E-Commerce & Physical Goods)',
    category: 'warm-tactile',
    bestFor: ['ecommerce', 'product', 'store', 'shop', 'retail', 'bottle', 'hardware', 'fashion', 'craft'],
    keywords: [
      'product', 'produk', 'bottle', 'stainless-steel', 'insulated', 'merchant',
      'care instructions', 'medical-grade', 'toko', 'shop', 'store', 'ecommerce',
      'e-commerce', 'belanja', 'cart', 'keranjang', 'checkout', 'keramik', 'ceramic',
      'kemasan', 'spesifikasi produk', 'water bottle', 'perangkat keras', 'gadget'
    ],
    routeType: 'product-showcase-configurator',
    macroLayout: 'Breadcrumb Storebar + 60/40 Product Gallery Stage (Multi-Angle Thumbnail Switcher) & Live Variant/Size Purchase Box + Accordion Specs',
    forbiddenPatterns: [
      'Do NOT put a search/filter/Reset toolbar on a single-product page.',
      'Do NOT use fake scarcity timers.'
    ],
    archetype: 'Multi-Angle Product Showcase + Tactile Variant Selector & Spec Accordion',
    fonts: {
      display: "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      sans: "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'Space Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f6f4ee',
      surface: '#ebe6dc',
      elevated: '#ffffff',
      tint: '#f5e4de',
      text: '#1f1715',
      muted: '#594945',
      accent: '#9a3b1e',
      accentHover: '#732a14',
      accentSoft: '#f7ded6',
      accentContrast: '#ffffff',
      border: '#d6d0c4',
      borderStrong: '#b5ad9e',
      darkBand: '#141f1a',
      darkSurface: '#1d2d26',
      darkBorder: '#2f453b',
      darkText: '#f2f7f4',
      darkMuted: '#9db5aa'
    },
    cadence: ['sand-canvas (60/40 Multi-Angle Product Stage + Variant Selector)', 'elevated-white (Thermal & Material Test Comparison Table)', 'deep-olive (Care Instructions & Warranty Guarantee)'],
    visualProofRule: 'Show a detailed product studio illustration/photo with interactive angle/color switching and immediate price/stock clarity.'
  },
  {
    id: 'campus-amber-academy',
    archetypeId: 'ledger-table-first',
    name: 'Warm Paper & Deep Teal Academy (Education & Learning)',
    category: 'cool-editorial',
    bestFor: ['education', 'pendidikan', 'school', 'university', 'course', 'kursus', 'bootcamp', 'edtech'],
    keywords: [
      'edukasi', 'education', 'pendidikan', 'kampus', 'university', 'universitas',
      'sekolah', 'school', 'kursus', 'course', 'bootcamp', 'akademi', 'academy',
      'pelatihan', 'training', 'belajar', 'kurikulum', 'curriculum', 'silabus', 'bimbel'
    ],
    routeType: 'curriculum-pathway-index',
    macroLayout: 'Program Overview Header + Interactive Syllabus Module Accordion + Cohort Schedule & Tuition Table',
    forbiddenPatterns: [
      'Do NOT invent fake job-placement guarantees.'
    ],
    archetype: 'Structured Syllabus Pathway + Cohort Schedule & Tuition Transparency',
    fonts: {
      display: "'Fraunces', Georgia, serif",
      sans: "'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f6f8f7',
      surface: '#e8efec',
      elevated: '#ffffff',
      tint: '#d9ebe5',
      text: '#102421',
      muted: '#415a56',
      accent: '#115e59',
      accentHover: '#0c4541',
      accentSoft: '#ccfbf1',
      accentContrast: '#ffffff',
      border: '#cbd8d4',
      borderStrong: '#9fb5af',
      darkBand: '#0b1f1d',
      darkSurface: '#13302d',
      darkBorder: '#234a46',
      darkText: '#f0fdfa',
      darkMuted: '#99bdb8'
    },
    cadence: ['paper-mint (Program Thesis & Outcomes)', 'elevated-sheet (Week-by-Week Syllabus Modules)', 'deep-teal (Cohort Dates, Instructors & Tuition)'],
    visualProofRule: 'Display a concrete week-by-week syllabus explorer and real learning artifact previews.'
  }  ,
  {
    id: 'limestone-cedar-property',
    archetypeId: 'catalogue-grid',
    name: 'Limestone Courtyard & Cedar Architecture (Real Estate & Property)',
    category: 'warm-editorial',
    bestFor: ['property', 'properti', 'real-estate', 'housing', 'apartment', 'residential'],
    keywords: [
      'properti', 'property', 'real estate', 'perumahan', 'apartemen', 'apartment',
      'hunian', 'residensial', 'residential', 'townhouse', 'cluster', 'kondominium',
      'condo', 'kavling', 'denah rumah', 'floor plan', 'rumah tapak', 'housing', 'villa'
    ],
    routeType: 'property-unit-catalogue',
    macroLayout: 'Architectural Development Header + Interactive Unit/Floorplan Matrix + Location Connectivity & Mortgage Calculator',
    forbiddenPatterns: [
      'Do NOT use a SaaS workbench card; highlight floorplans, site orientation, and unit specifications.'
    ],
    archetype: 'Curated Property Unit Matrix + Floorplan Spec Sheet & Site Context',
    fonts: {
      display: "'Cormorant Garamond', Georgia, serif",
      sans: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'IBM Plex Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f7f5f0',
      surface: '#ece8df',
      elevated: '#ffffff',
      tint: '#e5ece7',
      text: '#1c1d1a',
      muted: '#52544d',
      accent: '#2b5441',
      accentHover: '#1f3e30',
      accentSoft: '#d8e8df',
      accentContrast: '#ffffff',
      border: '#d8d3c8',
      borderStrong: '#b8b1a3',
      darkBand: '#171a17',
      darkSurface: '#222723',
      darkBorder: '#353d37',
      darkText: '#f4f5f2',
      darkMuted: '#a6afa8'
    },
    cadence: ['limestone-courtyard (Architectural Perspective & Unit Types)', 'elevated-ivory (Floorplan Dimensions & Material Specs)', 'deep-cedar (Site Map & Viewing Appointment)'],
    visualProofRule: 'Lead with architectural elevations or floorplan plates paired with unit dimensions and transparent price tiers.'
  },
  {
    id: 'horizon-terracotta-expedition',
    archetypeId: 'timeline-story',
    name: 'Sunlit Sandstone & Aegean Horizon (Travel & Expedition)',
    category: 'warm-editorial',
    bestFor: ['travel', 'wisata', 'tourism', 'expedition', 'itinerary', 'resort', 'tour'],
    keywords: [
      'travel', 'wisata', 'pariwisata', 'tourism', 'tur', 'tour', 'ekspedisi',
      'expedition', 'itinerary', 'destinasi', 'destination', 'liburan', 'vacation',
      'resort', 'penginapan', 'open trip', 'jelajah', 'voyage', 'perjalanan wisata', 'hotel'
    ],
    routeType: 'expedition-itinerary-timeline',
    macroLayout: 'Panoramic Destination Cover + Day-by-Day Route Timeline & Elevation/Stop Map + Departure Dates & Inclusion Ledger',
    forbiddenPatterns: [
      'Do NOT use a 2-column SaaS hero with a generic search/reset card; structure around the route and day-by-day itinerary.'
    ],
    archetype: 'Panoramic Expedition Cover + Chronological Day-by-Day Route & Departure Ledger',
    fonts: {
      display: "'Fraunces', Georgia, serif",
      sans: "'Work Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'Space Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f8f5ef',
      surface: '#eee8dc',
      elevated: '#ffffff',
      tint: '#e0ecf2',
      text: '#192126',
      muted: '#4b5761',
      accent: '#145374',
      accentHover: '#0d3c55',
      accentSoft: '#d4e7f2',
      accentContrast: '#ffffff',
      border: '#d9d2c5',
      borderStrong: '#b8afa0',
      darkBand: '#101b24',
      darkSurface: '#182836',
      darkBorder: '#2a4054',
      darkText: '#f2f7fa',
      darkMuted: '#9db4c4'
    },
    cadence: ['sandstone-cover (Destination Panorama & Route Summary)', 'elevated-white (Day-by-Day Expedition Timeline)', 'deep-aegean (Departure Cohort Dates & Gear Checklist)'],
    visualProofRule: 'Anchor the page with a route map or destination plate paired with a concrete day-by-day itinerary.'
  },
  {
    id: 'atelier-onyx-lookbook',
    archetypeId: 'gallery-masonry',
    name: 'Editorial Silk & Onyx Lookbook (Fashion & Apparel)',
    category: 'warm-editorial',
    bestFor: ['fashion', 'boutique', 'butik', 'apparel', 'lookbook', 'clothing', 'couture'],
    keywords: [
      'fashion', 'butik', 'boutique', 'apparel', 'busana', 'pakaian', 'clothing',
      'koleksi', 'collection', 'lookbook', 'runway', 'couture', 'tailor', 'penjahit',
      'kebaya', 'batik', 'streetwear', 'menswear', 'womenswear', 'garment'
    ],
    routeType: 'editorial-lookbook-plates',
    macroLayout: 'Season Issue Masthead + Full-Height Editorial Lookbook Plates (Look 01-06) + Fabric Composition & Sizing Sheet',
    forbiddenPatterns: [
      'Do NOT use SaaS dashboard widgets or search/reset filter boxes on an editorial fashion lookbook.'
    ],
    archetype: 'Editorial Lookbook Plates + Garment Fabric & Measurement Index',
    fonts: {
      display: "'Cormorant Garamond', Georgia, serif",
      sans: "'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'IBM Plex Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f7f5f2',
      surface: '#ece8e2',
      elevated: '#ffffff',
      tint: '#e8e2d9',
      text: '#141312',
      muted: '#524e4a',
      accent: '#2b2623',
      accentHover: '#141210',
      accentSoft: '#e4dfd9',
      accentContrast: '#ffffff',
      border: '#d6d0c8',
      borderStrong: '#b3aba0',
      darkBand: '#121110',
      darkSurface: '#1f1d1b',
      darkBorder: '#36322f',
      darkText: '#f5f2ed',
      darkMuted: '#b0a9a0'
    },
    cadence: ['silk-ecru (Season Masthead & Asymmetric Lookbook Plates)', 'onyx-stage (Textile Provenance & Cut Notes)', 'elevated-ivory (Garment Measurements & Private Fitting)'],
    visualProofRule: 'Present large vertical 4:5 lookbook plates with garment numbers, fabric weights, and cut details.'
  },
  {
    id: 'vermilion-editorial-agency',
    archetypeId: 'gallery-masonry',
    name: 'Raw Newsprint & Vermilion Studio (Creative & Branding Agency)',
    category: 'bold-high-contrast',
    bestFor: ['creative-agency', 'agensi-kreatif', 'branding', 'design-studio', 'advertising'],
    keywords: [
      'agensi kreatif', 'creative agency', 'agensi', 'agency', 'branding', 'brand studio',
      'design studio', 'studio desain', 'studio kreatif', 'creative studio', 'art direction',
      'kampanye iklan', 'advertising', 'identitas visual', 'visual identity', 'digital agency'
    ],
    routeType: 'case-study-monograph',
    macroLayout: 'Manifesto Masthead + Numbered Selected Case Studies Grid (Asymmetric Plates + Deliverables List) + Studio Capabilities & Commission Desk',
    forbiddenPatterns: [
      'Do NOT use a SaaS 2-column hero with a right-hand search/filter/Reset card on a creative agency portfolio.'
    ],
    archetype: 'Editorial Case-Study Monograph + Capabilities Matrix',
    fonts: {
      display: "'Syne', 'Space Grotesk', sans-serif",
      sans: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', ui-monospace, monospace"
    },
    tokens: {
      bg: '#f5f3ee',
      surface: '#eae6dd',
      elevated: '#ffffff',
      tint: '#f7e1dc',
      text: '#141312',
      muted: '#4f4b46',
      accent: '#9e2a17',
      accentHover: '#781e0f',
      accentSoft: '#f5d9d3',
      accentContrast: '#ffffff',
      border: '#d6d0c4',
      borderStrong: '#b3aa9b',
      darkBand: '#141211',
      darkSurface: '#211e1c',
      darkBorder: '#38322f',
      darkText: '#f6f3ee',
      darkMuted: '#b3aba2'
    },
    cadence: ['newsprint-base (Studio Manifesto & Numbered Case Study Plates)', 'carbon-stage (Discipline Index & Production Credits)', 'vermilion-tint (New Commission Brief & Contact)'],
    visualProofRule: 'Open with bold typographic direction and large numbered case-study plates showing real deliverables and scope.'
  }
];

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Computes whole-word match score for a direction against a prompt string.
 * Short tokens like "ai", "dev", "data" only match as complete words, never inside "ramai", "develop", "update".
 */
export function scorePromptForDirection(promptText, direction) {
  const normalized = String(promptText || '').toLowerCase();
  let score = 0;
  const matchedKeywords = [];

  for (const kw of direction.keywords) {
    const cleanKw = kw.trim().toLowerCase();
    const pattern = new RegExp(`(?<![\\p{L}\\p{N}_])${escapeRegex(cleanKw)}(?![\\p{L}\\p{N}_])`, 'gu');
    const matches = [...normalized.matchAll(pattern)];
    if (matches.length > 0) {
      const weight = cleanKw.includes(' ') ? 3 : 2;
      score += weight * matches.length;
      matchedKeywords.push(cleanKw);
    }
  }
  return { score, matchedKeywords };
}

export const TONE_FALLBACK_RULES = [
  {
    tone: 'warm-craft',
    directionId: 'linen-espresso-craft',
    adjectives: ['hangat', 'warm', 'akrab', 'natural', 'organik', 'organic', 'earthy', 'ramah', 'cozy', 'tradisional', 'craft', 'taktil']
  },
  {
    tone: 'bold-contrast',
    directionId: 'bauhaus-signal-poster',
    adjectives: ['tegas', 'bold', 'kontras', 'kuat', 'brutalist', 'ekspresif', 'energetik', 'lantang', 'poster', 'dinamis', 'vibrant']
  },
  {
    tone: 'minimal-calm',
    directionId: 'travertine-terracotta-gallery',
    adjectives: ['minimalis', 'minimal', 'tenang', 'calm', 'hening', 'quiet', 'bersih', 'clean', 'sederhana', 'zen', 'monokrom', 'monochrome']
  },
  {
    tone: 'dark-technical',
    directionId: 'obsidian-terminal-noir',
    adjectives: ['gelap', 'dark', 'noir', 'futuristik', 'futuristic', 'cyber', 'teknis', 'technical', 'malam']
  },
  {
    tone: 'formal-authoritative',
    directionId: 'savile-navy-counsel',
    adjectives: ['resmi', 'formal', 'klasik', 'classic', 'otoritatif', 'authoritative', 'elegan', 'elegant', 'serius', 'profesional', 'institusional']
  }
];

export function selectDirection(promptText) {
  const DEFAULT_PROMPT = 'general web application';
  const normalized = String(promptText || '').trim().toLowerCase();
  const isDefaultPrompt = !normalized || normalized === DEFAULT_PROMPT;

  const evaluations = DIRECTIONS.map((dir) => {
    if (isDefaultPrompt) return { direction: dir, score: 0, matchedKeywords: [] };
    const { score, matchedKeywords } = scorePromptForDirection(promptText, dir);
    return { direction: dir, score, matchedKeywords };
  });

  let best = evaluations[0];
  for (const item of evaluations) {
    if (item.score > best.score) {
      best = item;
    }
  }

  let primary = DIRECTIONS[0];
  let fallbackStrategy = 'domain-matched';
  let matchedToneAdjectives = [];
  let needsClarification = false;
  let clarificationQuestion = null;

  if (best.score > 0) {
    primary = best.direction;
  } else {
    // Check tone adjectives using whole-word boundaries before falling back
    let bestTone = null;
    let bestToneMatches = [];
    if (!isDefaultPrompt) {
      for (const rule of TONE_FALLBACK_RULES) {
        const hits = [];
        for (const adj of rule.adjectives) {
          const pattern = new RegExp(`(?<![\\p{L}\\p{N}_])${escapeRegex(adj)}(?![\\p{L}\\p{N}_])`, 'gu');
          if (pattern.test(normalized)) {
            // Avoid matching "pasar malam" as dark-technical tone when "malam" is part of "pasar malam"
            if (adj === 'malam' && /\bpasar\s+malam\b/i.test(normalized)) continue;
            hits.push(adj);
          }
        }
        if (hits.length > bestToneMatches.length) {
          bestTone = rule;
          bestToneMatches = hits;
        }
      }
    }

    if (bestTone && bestToneMatches.length > 0) {
      primary = DIRECTIONS.find((d) => d.id === bestTone.directionId) || DIRECTIONS[0];
      fallbackStrategy = `tone-derived:${bestTone.tone}`;
      matchedToneAdjectives = bestToneMatches;
    } else {
      primary = DIRECTIONS[0];
      fallbackStrategy = 'clarification-required';
      needsClarification = true;
      clarificationQuestion = 'Domain atau kata sifat nada belum terdeteksi dari prompt. Tanyakan ke user: apakah ingin nada hangat/editorial, tegas/kontras, minimalis/tenang, gelap/teknis, atau resmi/institusional?';
    }
  }

  const scores = Object.fromEntries(evaluations.map((e) => [e.direction.id, { score: e.score, matchedKeywords: e.matchedKeywords }]));
  const selectedArchetype = STRUCTURAL_ARCHETYPES[primary.archetypeId] || STRUCTURAL_ARCHETYPES['editorial-index-rail'];
  return {
    primary,
    selectedArchetype,
    matchedKeywords: best.score > 0 ? best.matchedKeywords : [],
    matchedToneAdjectives,
    fallbackStrategy,
    needsClarification,
    clarificationQuestion,
    scores
  };
}

export function hexToRelativeLuminance(hex) {
  const clean = hex.replace('#', '');
  const full = clean.length === 3 ? clean.split('').map((c) => c + c).join('') : clean;
  const num = parseInt(full, 16);
  const channels = [(num >> 16) & 255, (num >> 8) & 255, num & 255].map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

export function contrastRatio(hexA, hexB) {
  const l1 = hexToRelativeLuminance(hexA);
  const l2 = hexToRelativeLuminance(hexB);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url));

if (isMain) {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`Usage: node deal-direction.mjs [--prompt "<user request>"] [--project <dir>] [--write-tokens]
Deterministically deals a studio art direction + macro layout blueprint + 2 contrast alternatives
and optionally writes a pre-validated design-tokens.css + .atlas-direction.json.`);
    process.exit(0);
  }

  const getArg = (flag, fallback = '') => {
    const idx = args.indexOf(flag);
    return idx >= 0 && args[idx + 1] ? args[idx + 1] : fallback;
  };

  const promptText = getArg('--prompt', 'general web application');
  const projectRoot = path.resolve(getArg('--project', '.'));
  const writeTokens = args.includes('--write-tokens') || args.includes('--write');

  const { primary, selectedArchetype, matchedKeywords, matchedToneAdjectives, fallbackStrategy, needsClarification, clarificationQuestion, scores } = selectDirection(promptText);
  const alternatives = DIRECTIONS.filter((d) => d.id !== primary.id).slice(0, 2);

  const displayFont = primary.fonts.display || primary.fonts.sans;
  const sansFont = primary.fonts.sans;
  const monoFont = primary.fonts.mono || "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace";
  const fontLines = [
    `  --font-display: ${displayFont};`,
    `  --font-sans: ${sansFont};`,
    `  --font-mono: ${monoFont};`
  ].join('\n');

  const tokensCss = `:root {
${fontLines}

  --text-2xs: 0.6875rem;
  --text-xs: 0.78125rem;
  --text-sm: 0.90625rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.35rem;
  --text-2xl: clamp(1.65rem, 1.35rem + 1.3vw, 2.35rem);
  --text-3xl: clamp(2.15rem, 1.65rem + 2.4vw, 3.55rem);

  --leading-tight: 1.08;
  --leading-snug: 1.26;
  --leading-body: 1.62;
  --tracking-tight: -0.032em;
  --tracking-wide: 0.075em;

  --color-bg: ${primary.tokens.bg};
  --color-surface: ${primary.tokens.surface};
  --color-surface-elevated: ${primary.tokens.elevated};
  --color-surface-tint: ${primary.tokens.tint};
  --color-text: ${primary.tokens.text};
  --color-muted: ${primary.tokens.muted};

  --color-accent: ${primary.tokens.accent};
  --color-accent-hover: ${primary.tokens.accentHover};
  --color-accent-soft: ${primary.tokens.accentSoft};
  --color-accent-contrast: ${primary.tokens.accentContrast};

  --color-border: ${primary.tokens.border};
  --color-border-strong: ${primary.tokens.borderStrong};
  --color-tactile-edge: ${primary.tokens.text};

  --color-blueprint: ${primary.tokens.darkBand};
  --color-blueprint-surface: ${primary.tokens.darkSurface};
  --color-blueprint-border: ${primary.tokens.darkBorder};
  --color-blueprint-text: ${primary.tokens.darkText};
  --color-blueprint-muted: ${primary.tokens.darkMuted};

  --color-success: #1d6547;
  --color-success-bg: #daf0e5;
  --color-warn: #8c581c;
  --color-warn-bg: #f6e7d2;
  --color-danger: #9e2f2b;
  --color-danger-bg: #f8dfdd;

  --space-0: 0rem;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;

  --radius-xs: 0.425rem;
  --radius-sm: 0.75rem;
  --radius-md: 1.125rem;
  --radius-lg: 1.5rem;
  --radius-pill: 999px;

  --shadow-sm: 0 2px 8px rgba(21, 28, 25, 0.04);
  --shadow-md: 0 12px 30px rgba(21, 28, 25, 0.065);
  --shadow-tactile: 0 3px 0 ${primary.tokens.text};
  --shadow-tactile-soft: 0 3px 0 ${primary.tokens.borderStrong};

  --duration-fast: 170ms;
  --duration-base: 300ms;
  --duration-slow: 540ms;
  --ease-standard: cubic-bezier(0.22, 1, 0.36, 1);
}
/* 6. Base Foundation, Editorial Specimen Plates, & Styled Form Controls */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background-color: var(--color-bg); color: var(--color-text); font-family: var(--font-sans); font-size: var(--text-base); line-height: var(--leading-body, 1.6); -webkit-font-smoothing: antialiased; }
h1, h2, h3, h4 { font-family: var(--font-display, var(--font-sans)); line-height: var(--leading-tight, 1.12); letter-spacing: var(--tracking-tight, -0.025em); margin-top: 0; }
code, pre, kbd, samp, .mono { font-family: var(--font-mono, ui-monospace, monospace); }
img, svg, video, canvas { max-width: 100%; height: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--color-border); }
.editorial-plate, figure[data-photo-slot] { margin: 0; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background-color: var(--color-surface-elevated); overflow: hidden; }
.editorial-plate-stage { position: relative; display: flex; flex-direction: column; justify-content: space-between; gap: var(--space-4); padding: var(--space-6); min-height: 220px; background: radial-gradient(circle at 82% 18%, var(--color-surface-tint, var(--color-surface)), var(--color-surface) 72%); border-bottom: 1px solid var(--color-border); }
.editorial-plate-meta { display: flex; flex-wrap: wrap; justify-content: space-between; gap: var(--space-2); font-family: var(--font-mono, ui-monospace, monospace); font-size: var(--text-xs); letter-spacing: var(--tracking-wide, 0.05em); text-transform: uppercase; color: var(--color-muted); }
.editorial-plate figcaption, figure[data-photo-slot] > figcaption { padding: var(--space-3) var(--space-4); font-size: var(--text-xs); color: var(--color-muted); background-color: var(--color-surface-elevated); }
input:not([type="checkbox"]):not([type="radio"]), select, textarea {
  appearance: none;
  -webkit-appearance: none;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-body, 1.5);
  color: var(--color-text);
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xs);
  padding: var(--space-2) var(--space-3);
}
select {
  max-width: 100%;
  text-overflow: ellipsis;
  padding-right: var(--space-8);
  background-image: linear-gradient(45deg, transparent 50%, var(--color-muted) 50%), linear-gradient(135deg, var(--color-muted) 50%, transparent 50%);
  background-position: calc(100% - 1.15rem) 52%, calc(100% - 0.8rem) 52%;
  background-size: 0.35rem 0.35rem, 0.35rem 0.35rem;
  background-repeat: no-repeat;
  cursor: pointer;
}
textarea { min-height: 6.5rem; resize: vertical; }
input[type="checkbox"], input[type="radio"] { accent-color: var(--color-accent); width: 1.125rem; height: 1.125rem; cursor: pointer; }
button, .btn, .btn-primary, .btn-secondary, .btn-ghost {
  appearance: none;
  text-decoration: none;
  -webkit-appearance: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: 600;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-xs);
  border: 1px solid var(--color-border);
  background-color: var(--color-surface-elevated);
  color: var(--color-text);
  cursor: pointer;
}
.btn-primary, button[type="submit"] { background-color: var(--color-accent); color: var(--color-accent-contrast); border-color: var(--color-accent); }
.btn-secondary { background-color: var(--color-surface-elevated); color: var(--color-text); border-color: var(--color-border); }
.btn-ghost { background-color: transparent; color: var(--color-text); border-color: transparent; }
.segmented-control { display: inline-flex; gap: var(--space-1); padding: var(--space-1); background-color: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-sm); }
.filter-chip { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-1) var(--space-3); border-radius: var(--radius-pill); border: 1px solid var(--color-border); background-color: var(--color-surface-elevated); font-size: var(--text-xs); cursor: pointer; }
input:focus-visible, select:focus-visible, textarea:focus-visible, button:focus-visible, .btn:focus-visible, .filter-chip:focus-visible, a:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
input:disabled, select:disabled, textarea:disabled, button:disabled, [aria-disabled="true"] { opacity: 0.55; cursor: not-allowed; }
input[aria-invalid="true"], select[aria-invalid="true"], textarea[aria-invalid="true"], .is-error { border-color: var(--color-danger); }
.panel, .panel h1, .panel h2, .panel h3, .panel h4, .band-dark .panel h1, .band-dark .panel h2, .band-dark .panel h3, .band-dark .panel h4 { color: var(--color-text); }
`;

  const payload = {
    promptAnalyzed: promptText,
    matchedKeywords,
    matchedToneAdjectives,
    fallbackStrategy,
    needsClarification,
    clarificationQuestion,
    directionScores: scores,
    selectedArchetype,
    dealtPrimaryDirection: primary,
    contrastAlternativesForBrief: alternatives.map((a) => ({ id: a.id, name: a.name, archetype: a.archetype, macroLayout: a.macroLayout })),
    nonNegotiableOpRules: [
      `Follow dealtPrimaryDirection.macroLayout ("${primary.macroLayout}")—never force a uniform 2-column hero + right-hand search/filter/Reset card onto every domain.`,
      'Never render debug state-switcher dropdowns (Populated/Loading/Empty/Error) in the user-facing UI.',
      'Only include search/filter/Reset toolbars on data-dense views (dashboards, API indexes, or 20+ item catalogues); keep narrative, hospitality, wedding, legal, and portfolio pages free of filter toolbars.',
      'Build rich, domain-authentic visual proof (detailed multi-layered illustrations, architectural/product scenes, or real photography)—never tiny sparse line arcs with empty space.',
      'Capture desktop, tablet, & mobile screenshots after build and inspect the rendered PNG images directly.'
    ]
  };

  if (writeTokens) {
    fs.mkdirSync(projectRoot, { recursive: true });
    fs.writeFileSync(path.join(projectRoot, '.atlas-direction.json'), JSON.stringify(payload, null, 2) + '\n');
    const tokenOut = path.join(projectRoot, 'design-tokens.css');
    if (!fs.existsSync(tokenOut)) {
      fs.writeFileSync(tokenOut, tokensCss);
    }
  }

  console.log(JSON.stringify(payload, null, 2));
}
