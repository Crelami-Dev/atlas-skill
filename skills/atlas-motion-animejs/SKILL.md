---
name: atlas-motion-animejs
description: "Design and implement web animations, FLIP layout transitions, scroll choreography, and spring physics with Anime.js v4 (Gunakan saat merancang atau mengimplementasikan animasi web, transisi layout FLIP, koreografi scroll, dan efek pegas menggunakan Anime.js v4). Do not use for simple color hover effects handled cleanly by CSS transitions."
---

# Atlas Motion Engine - Koreografi Anime.js v4

Gunakan **Anime.js v4 (`animejs@^4.0.0`)** saat antarmuka membutuhkan koreografi masuk bertahap, fisika pegas, transisi layout FLIP, animasi berbasis scroll, atau animasi garis SVG. Untuk perubahan satu properti sederhana saat hover, gunakan `transition` CSS biasa agar beban JavaScript tetap minimal.

Baca [Anime.js v4 Playbook](../../references/animejs-v4-playbook.md) dan [Scope Helper Template](../../templates/animejs-v4-scope.ts) sebelum menulis kode animasi.

## 1. Aturan Sintaks Anime.js v4 vs Legacy v3

Jangan mencampur sintaks Anime.js v3 ke dalam proyek v4 karena struktur ekspor modul dan nama propertinya telah berubah dan akan memicu error saat runtime:

| Kemampuan | Sintaks Lama v3 (Ditolak Linter) | Sintaks Resmi Anime.js v4 |
|---|---|---|
| Impor Modul | `import anime from 'animejs'` | `import { animate, createTimeline, createScope, stagger, spring, onScroll } from 'animejs'` |
| Pemanggilan Dasar | `anime({ targets: '.card', translateY: 20 })` | `animate('.card', { y: [20, 0], opacity: [0, 1] })` |
| Properti & Nama Easing | `easing: 'easeOutExpo'` | `ease: 'outExpo'` |
| Fisika Pegas | `easing: 'spring(1, 80, 10, 0)'` | `ease: spring({ bounce: 0.25, duration: 500 })` |
| Timeline | `anime.timeline({ ... })` | `createTimeline({ defaults: { ease: 'outQuart' } })` |
| Stagger | `delay: anime.stagger(60)` | `delay: stagger(60, { from: 'first' })` |
| Arah Bolak-balik | `direction: 'alternate'` | `alternate: true` atau `reversed: true` |
| Pemicu Scroll | IntersectionObserver manual | `autoplay: onScroll({ container, enter: 'bottom-=12% top' })` |
| Pemecah Teks | SplitType pihak ketiga | `splitText(el, { lines: { wrap: 'clip' }, words: true })` |
| Gambar Garis SVG | `strokeDashoffset: [anime.setDashoffset, 0]` | `animate(svg.createDrawable('path.route'), { draw: ['0 0', '0 1'] })` |
| Transisi Layout (FLIP) | Hitung bounding-box manual | `const layout = createLayout(root); layout.record(); updateDOM(); layout.animate();` |
| Pembersihan Komponen | `anime.remove()` | `const scope = createScope({ root }).add(...); return () => scope.revert();` |

## 2. Isolasi Siklus Hidup dengan `createScope()`

Bungkus inisialisasi animasi komponen di dalam `createScope({ root, mediaQueries })` dan panggil `scope.revert()` saat komponen dilepas agar listener scroll dan timer tidak bocor di memori:

```tsx
'use client';
import { useEffect, useRef } from 'react';
import { createScope, createTimeline, stagger } from 'animejs';

export function HeroShowcase() {
  const rootRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!rootRef.current) return;
    const scope = createScope({
      root: rootRef.current,
      mediaQueries: { reduceMotion: '(prefers-reduced-motion: reduce)' },
    }).add((self) => {
      if (self.matches.reduceMotion) return;
      createTimeline({ defaults: { ease: 'outQuart', duration: 520 } })
        .add('[data-hero-title]', { opacity: [0, 1], y: [18, 0] })
        .add('[data-hero-cta]', { opacity: [0, 1], y: [12, 0], delay: stagger(60) }, '-=280');
    });
    return () => scope.revert();
  }, []);

  return <section ref={rootRef} data-hero>...</section>;
}
```

## 3. Visibilitas Progresif & Performa GPU

- **Jangan Sembunyikan Konten di CSS Statis:** Jangan menulis `[data-reveal] { opacity: 0; }` pada stylesheet global karena halaman akan tampak kosong saat SSR, koneksi lambat, atau ketika JavaScript dinonaktifkan. Biarkan elemen terlihat secara default dan gunakan keyframe `opacity: [0, 1]` saat `animate()` dijalankan.
- **Animasikan Properti Komposit GPU:** Gunakan `x`, `y`, `scale`, `scaleX`, `scaleY`, `rotate`, atau `opacity` dan hindari menganimasikan `top`, `left`, `width`, atau `height` secara langsung karena memicu perhitungan ulang tata letak (layout reflow) di setiap frame.
- **Batas Durasi:** Pastikan animasi masuk selesai dalam waktu maksimal `1500ms` agar tidak menghambat pengguna membaca atau menekan tombol utama.

## Perintah Verifikasi

Jalankan `node <atlas>/scripts/check-motion-v4.mjs <project-root>` untuk memverifikasi sintaks v4, pembersihan scope, dan ketiadaan jebakan `opacity: 0` statis.
