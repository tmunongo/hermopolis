<script lang="ts">
	/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any */
	import { onMount } from 'svelte';

	let actions: Record<string, any> = new Proxy(
		{},
		{
			get: (target: Record<string, unknown>, prop: string | symbol) => {
				if (prop === 'then') return undefined;
				if (typeof prop !== 'string') return (..._args: unknown[]) => {};
				if (prop in target) return target[prop];
				return (..._args: unknown[]) => {};
			}
		}
	);

	onMount(() => {
		const _listeners = [];
		const _addWinListener = (type, listener, options) => {
			window.addEventListener(type, listener, options);
			_listeners.push({ target: window, args: [type, listener, options] });
		};
		const _addDocListener = (type, listener, options) => {
			document.addEventListener(type, listener, options);
			_listeners.push({ target: document, args: [type, listener, options] });
		};
		/* ══════════════════════════════════════
   READING PROGRESS
══════════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width =
					(el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight)) * 100 + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		/* ══════════════════════════════════════
   UTILITIES
══════════════════════════════════════ */
		function roundRect(ctx, x, y, w, h, r) {
			r = Math.min(r, w / 2, h / 2);
			ctx.beginPath();
			ctx.moveTo(x + r, y);
			ctx.lineTo(x + w - r, y);
			ctx.arcTo(x + w, y, x + w, y + r, r);
			ctx.lineTo(x + w, y + h - r);
			ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
			ctx.lineTo(x + r, y + h);
			ctx.arcTo(x, y + h, x, y + h - r, r);
			ctx.lineTo(x, y + r);
			ctx.arcTo(x, y, x + r, y, r);
			ctx.closePath();
		}

		/* ══════════════════════════════════════
   DEMO 1: THUMBNAIL LAYOUT LAB
══════════════════════════════════════ */
		const tlCvs = document.getElementById('thumb-lab-canvas');
		const tlCtx = tlCvs.getContext('2d');
		const TLW = tlCvs.width,
			TLH = tlCvs.height;

		let tlLayout = 'thirds';
		let tlShowZones = false;
		let tlShowGrid = false;
		let tlScaleMode = false;

		const TL_INFO = {
			thirds: {
				color: 'var(--violet)',
				text: 'Left-Third Subject + Right Text Zone — the most reliable thumbnail structure. Subject anchors the left third, creating visual tension. The text zone occupies the right two-thirds with generous breathing room. Hierarchy is unambiguous: eye goes to subject (highest contrast), moves right to title, then to sub-label. Works at all sizes.'
			},
			center: {
				color: 'var(--amber)',
				text: 'Centered Subject — communicates authority and directness, but creates a static composition with no visual tension. The eye goes to center and stops — there is nowhere obvious to move next. Text must be placed above or below the subject, not beside it, which competes with the dominant element rather than complementing it. Use only when the subject alone carries enough curiosity.'
			},
			fill: {
				color: 'var(--sky)',
				text: 'Full-Bleed Subject — the subject fills the frame. Text is overlaid with a high-contrast treatment (solid background bar, heavy shadow, or extreme weight/color). Very effective when the subject is visually rich and the text is minimal (2–3 words maximum). Risk: the subject and text can fight for attention if the overlay is insufficient. Test at thumbnail scale before committing.'
			},
			split: {
				color: 'var(--rose)',
				text: 'Side-by-Side Split — two subjects or before/after states. Creates immediate curiosity through implied comparison or contrast. Works when both elements are visually distinct and the relationship between them is the point of the video. Fails when both halves have similar visual weight, creating a confused focal point. Text must be minimal — the visual contrast does the communicative work.'
			}
		};

		const TL_DRAWS = {
			thirds: (ctx, w, h) => {
				ctx.fillStyle = '#080c12';
				ctx.fillRect(0, 0, w, h);
				// Subject zone (left third)
				ctx.fillStyle = '#121e30';
				ctx.fillRect(0, 0, Math.floor(w * 0.36), h);
				// Face silhouette
				ctx.fillStyle = '#d4a07a';
				ctx.beginPath();
				ctx.ellipse(w * 0.18, h * 0.4, w * 0.1, h * 0.22, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#1a2c44';
				ctx.beginPath();
				ctx.ellipse(w * 0.18 - w * 0.04, h * 0.37, w * 0.022, h * 0.018, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.beginPath();
				ctx.ellipse(w * 0.18 + w * 0.04, h * 0.37, w * 0.022, h * 0.018, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#0e1820';
				ctx.fillRect(0, h * 0.59, w * 0.36, h);
				// Accent bar
				ctx.fillStyle = '#9b6dff';
				ctx.fillRect(0, 0, 4, h);
				// Text zone — right two thirds
				ctx.fillStyle = '#fff';
				ctx.font = `800 ${Math.floor(h * 0.16)}px Syne,sans-serif`;
				ctx.fillText('THINK', w * 0.4, h * 0.38);
				ctx.fillStyle = '#9b6dff';
				ctx.font = `800 ${Math.floor(h * 0.16)}px Syne,sans-serif`;
				ctx.fillText('BIGGER', w * 0.4, h * 0.57);
				ctx.fillStyle = 'rgba(155,109,255,0.6)';
				ctx.font = `400 ${Math.floor(h * 0.07)}px IBM Plex Mono,monospace`;
				ctx.fillText('Design Fundamentals · Ep 04', w * 0.4, h * 0.73);
			},
			center: (ctx, w, h) => {
				ctx.fillStyle = '#0c1020';
				ctx.fillRect(0, 0, w, h);
				// Subject — centered, dominant
				ctx.fillStyle = '#1a2840';
				ctx.fillRect(w * 0.25, h * 0.12, w * 0.5, h * 0.76);
				ctx.fillStyle = '#d4a07a';
				ctx.beginPath();
				ctx.ellipse(w * 0.5, h * 0.42, w * 0.11, h * 0.24, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#1a2840';
				ctx.beginPath();
				ctx.ellipse(w * 0.46, h * 0.39, w * 0.022, h * 0.018, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.beginPath();
				ctx.ellipse(w * 0.54, h * 0.39, w * 0.022, h * 0.018, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#0c1020';
				ctx.fillRect(w * 0.25, h * 0.6, w * 0.5, h);
				// Title top, sub bottom — text on both sides of subject
				ctx.fillStyle = 'rgba(255,255,255,0.9)';
				ctx.font = `700 ${Math.floor(h * 0.1)}px Syne,sans-serif`;
				ctx.textAlign = 'center';
				ctx.fillText('THE DESIGN MYTH', w * 0.5, h * 0.1);
				ctx.fillStyle = 'rgba(155,109,255,0.7)';
				ctx.font = `400 ${Math.floor(h * 0.07)}px IBM Plex Mono,monospace`;
				ctx.fillText('what nobody tells you', w * 0.5, h * 0.9);
				ctx.textAlign = 'left';
			},
			fill: (ctx, w, h) => {
				// Full bleed subject
				ctx.fillStyle = '#162438';
				ctx.fillRect(0, 0, w, h);
				// Atmospheric background
				const g = ctx.createRadialGradient(w * 0.4, h * 0.4, 0, w * 0.4, h * 0.4, w * 0.5);
				g.addColorStop(0, 'rgba(155,109,255,0.2)');
				g.addColorStop(1, 'transparent');
				ctx.fillStyle = g;
				ctx.fillRect(0, 0, w, h);
				// Large face
				ctx.fillStyle = '#c9956e';
				ctx.beginPath();
				ctx.ellipse(w * 0.35, h * 0.42, w * 0.2, h * 0.38, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#1a2c44';
				ctx.beginPath();
				ctx.ellipse(w * 0.32, h * 0.38, w * 0.03, h * 0.025, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.beginPath();
				ctx.ellipse(w * 0.4, h * 0.38, w * 0.03, h * 0.025, 0, 0, Math.PI * 2);
				ctx.fill();
				// Text bar at bottom — solid for legibility
				ctx.fillStyle = 'rgba(0,0,0,0.75)';
				ctx.fillRect(0, h * 0.72, w, h * 0.28);
				ctx.fillStyle = '#fff';
				ctx.font = `800 ${Math.floor(h * 0.17)}px Syne,sans-serif`;
				ctx.fillText('EXPOSED', w * 0.04, h * 0.9);
				ctx.fillStyle = '#9b6dff';
				ctx.font = `400 ${Math.floor(h * 0.075)}px IBM Plex Mono,monospace`;
				ctx.fillText('Design secrets decoded', w * 0.04, h * 0.97);
			},
			split: (ctx, w, h) => {
				// Two-panel split
				ctx.fillStyle = '#080c12';
				ctx.fillRect(0, 0, w, h);
				// Left panel — before
				ctx.fillStyle = '#1a1a1a';
				ctx.fillRect(0, 0, w * 0.48, h);
				ctx.fillStyle = '#8a8a8a';
				ctx.font = `700 ${Math.floor(h * 0.55)}px Syne,sans-serif`;
				ctx.textAlign = 'center';
				ctx.fillText('?', w * 0.24, h * 0.7);
				ctx.fillStyle = 'rgba(255,255,255,0.3)';
				ctx.font = `400 ${Math.floor(h * 0.07)}px IBM Plex Mono,monospace`;
				ctx.fillText('BEFORE', w * 0.24, h * 0.92);
				// Divider
				ctx.fillStyle = '#9b6dff';
				ctx.fillRect(w * 0.48, 0, 4, h);
				// Right panel — after
				ctx.fillStyle = '#0e1a2c';
				ctx.fillRect(w * 0.52, 0, w * 0.48, h);
				const g2 = ctx.createRadialGradient(w * 0.76, h * 0.45, 0, w * 0.76, h * 0.45, w * 0.18);
				g2.addColorStop(0, 'rgba(155,109,255,0.35)');
				g2.addColorStop(1, 'transparent');
				ctx.fillStyle = g2;
				ctx.fillRect(w * 0.52, 0, w * 0.48, h);
				ctx.fillStyle = '#d4a07a';
				ctx.beginPath();
				ctx.ellipse(w * 0.76, h * 0.42, w * 0.1, h * 0.2, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#fff';
				ctx.font = `400 ${Math.floor(h * 0.07)}px IBM Plex Mono,monospace`;
				ctx.fillText('AFTER', w * 0.76, h * 0.92);
				ctx.textAlign = 'left';
				// Title overlay
				ctx.fillStyle = 'rgba(0,0,0,0.5)';
				ctx.fillRect(0, 0, w, h * 0.16);
				ctx.fillStyle = '#fff';
				ctx.font = `700 ${Math.floor(h * 0.1)}px Syne,sans-serif`;
				ctx.textAlign = 'center';
				ctx.fillText('THE TRANSFORMATION', w * 0.5, h * 0.12);
				ctx.textAlign = 'left';
			}
		};

		function drawThumbLab() {
			if (tlScaleMode) {
				tlCtx.fillStyle = 'rgba(0,0,0,0.7)';
				tlCtx.fillRect(0, 0, TLW, TLH);
				const sw = Math.floor(TLW * 0.1),
					sh = Math.floor(TLH * 0.1);
				// Render the thumbnail at 10% scale temporarily
				const offscreen = document.createElement('canvas');
				offscreen.width = TLW;
				offscreen.height = TLH;
				const oCtx = offscreen.getContext('2d');
				TL_DRAWS[tlLayout](oCtx, TLW, TLH);
				// Show at 10%
				tlCtx.save();
				tlCtx.imageSmoothingEnabled = true;
				const ox = (TLW - sw) / 2,
					oy = (TLH - sh) / 2;
				tlCtx.drawImage(offscreen, 0, 0, TLW, TLH, ox, oy, sw, sh);
				// Callout border
				tlCtx.strokeStyle = 'rgba(155,109,255,0.8)';
				tlCtx.lineWidth = 1.5;
				tlCtx.strokeRect(ox - 1, oy - 1, sw + 2, sh + 2);
				tlCtx.fillStyle = 'rgba(155,109,255,0.9)';
				tlCtx.font = '10px IBM Plex Mono,monospace';
				tlCtx.fillText('10% scale preview — ' + sw + '×' + sh + 'px', ox, oy - 6);
				tlCtx.restore();
			} else {
				TL_DRAWS[tlLayout](tlCtx, TLW, TLH);
				if (tlShowZones) drawThumbZones();
				if (tlShowGrid) drawThumbGrid();
			}
			syncThumbScales();
		}

		function drawThumbZones() {
			const ctx = tlCtx;
			const zones = {
				thirds: [
					{
						x: 0,
						y: 0,
						w: TLW * 0.36,
						h: TLH,
						col: 'rgba(155,109,255,0.18)',
						label: 'VISUAL ZONE'
					},
					{
						x: TLW * 0.36,
						y: TLH * 0.1,
						w: TLW * 0.55,
						h: TLH * 0.7,
						col: 'rgba(56,192,232,0.14)',
						label: 'TEXT ZONE'
					},
					{
						x: TLW * 0.36,
						y: TLH * 0.8,
						w: TLW * 0.55,
						h: TLH * 0.15,
						col: 'rgba(86,208,160,0.12)',
						label: 'BREATH'
					}
				],
				center: [
					{
						x: TLW * 0.25,
						y: TLH * 0.15,
						w: TLW * 0.5,
						h: TLH * 0.7,
						col: 'rgba(155,109,255,0.18)',
						label: 'VISUAL'
					},
					{ x: 0, y: 0, w: TLW, h: TLH * 0.14, col: 'rgba(56,192,232,0.14)', label: 'TEXT TOP' },
					{
						x: 0,
						y: TLH * 0.84,
						w: TLW,
						h: TLH * 0.14,
						col: 'rgba(86,208,160,0.12)',
						label: 'TEXT BOTTOM'
					}
				],
				fill: [
					{
						x: 0,
						y: 0,
						w: TLW,
						h: TLH,
						col: 'rgba(155,109,255,0.1)',
						label: 'VISUAL (FULL BLEED)'
					},
					{
						x: 0,
						y: TLH * 0.72,
						w: TLW,
						h: TLH * 0.28,
						col: 'rgba(56,192,232,0.18)',
						label: 'TEXT OVERLAY'
					}
				],
				split: [
					{ x: 0, y: 0, w: TLW * 0.48, h: TLH, col: 'rgba(232,93,138,0.14)', label: 'BEFORE' },
					{
						x: TLW * 0.52,
						y: 0,
						w: TLW * 0.48,
						h: TLH,
						col: 'rgba(155,109,255,0.14)',
						label: 'AFTER'
					},
					{ x: 0, y: 0, w: TLW, h: TLH * 0.16, col: 'rgba(56,192,232,0.18)', label: 'TEXT BAR' }
				]
			};
			(zones[tlLayout] || []).forEach((z) => {
				ctx.fillStyle = z.col;
				ctx.fillRect(z.x, z.y, z.w, z.h);
				ctx.strokeStyle = z.col.replace(/[^,]+\)$/, '0.7)');
				ctx.lineWidth = 1;
				ctx.setLineDash([4, 3]);
				ctx.strokeRect(z.x + 0.5, z.y + 0.5, z.w - 1, z.h - 1);
				ctx.setLineDash([]);
				ctx.fillStyle = 'rgba(255,255,255,0.6)';
				ctx.font = '9px IBM Plex Mono,monospace';
				ctx.fillText(z.label, z.x + 6, z.y + 14);
			});
		}

		function drawThumbGrid() {
			const ctx = tlCtx;
			ctx.strokeStyle = 'rgba(245,166,35,0.3)';
			ctx.lineWidth = 1;
			ctx.setLineDash([4, 4]);
			[TLW / 3, (2 * TLW) / 3].forEach((x) => {
				ctx.beginPath();
				ctx.moveTo(x, 0);
				ctx.lineTo(x, TLH);
				ctx.stroke();
			});
			[TLH / 3, (2 * TLH) / 3].forEach((y) => {
				ctx.beginPath();
				ctx.moveTo(0, y);
				ctx.lineTo(TLW, y);
				ctx.stroke();
			});
			[
				[TLW / 3, TLH / 3],
				[(2 * TLW) / 3, TLH / 3],
				[TLW / 3, (2 * TLH) / 3],
				[(2 * TLW) / 3, (2 * TLH) / 3]
			].forEach(([x, y]) => {
				ctx.fillStyle = 'rgba(245,166,35,0.8)';
				ctx.beginPath();
				ctx.arc(x, y, 4, 0, Math.PI * 2);
				ctx.fill();
			});
			ctx.setLineDash([]);
		}

		function syncThumbScales() {
			[
				['ts-home', 210, 118],
				['ts-search', 120, 68],
				['ts-related', 84, 47],
				['ts-mobile', 48, 27]
			].forEach(([id, w, h]) => {
				const cvs = document.getElementById(id);
				const ctx = cvs.getContext('2d');
				ctx.fillStyle = '#080c12';
				ctx.fillRect(0, 0, w, h);
				if (!tlScaleMode) {
					const off = document.createElement('canvas');
					off.width = TLW;
					off.height = TLH;
					TL_DRAWS[tlLayout](off.getContext('2d'), TLW, TLH);
					ctx.drawImage(off, 0, 0, TLW, TLH, 0, 0, w, h);
				}
			});
		}

		function setThumbLayout(layout, btn) {
			tlLayout = layout;
			tlScaleMode = false;
			document
				.querySelectorAll('.thumb-zone-btns .btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			document.getElementById('scale-btn').classList.remove('active');
			document.getElementById('scale-btn').textContent = 'Preview at 10%';
			const info = document.getElementById('zone-info');
			info.style.color = TL_INFO[layout].color;
			info.textContent = TL_INFO[layout].text;
			drawThumbLab();
		}

		function toggleZones() {
			tlShowZones = !tlShowZones;
			document.getElementById('zones-btn').classList.toggle('active', tlShowZones);
			drawThumbLab();
		}

		function toggleThirdGrid() {
			tlShowGrid = !tlShowGrid;
			document.getElementById('grid-btn').classList.toggle('active', tlShowGrid);
			drawThumbLab();
		}

		function toggleThumbScale() {
			tlScaleMode = !tlScaleMode;
			const btn = document.getElementById('scale-btn');
			btn.classList.toggle('active', tlScaleMode);
			btn.textContent = tlScaleMode ? 'Back to Full Size' : 'Preview at 10%';
			drawThumbLab();
		}

		drawThumbLab();

		/* ══════════════════════════════════════
   DEMO 2: BANNER SAFE ZONE BUILDER
══════════════════════════════════════ */
		const bnCvs = document.getElementById('banner-canvas');
		const bnCtx = bnCvs.getContext('2d');
		const BW = bnCvs.width,
			BH = bnCvs.height;
		// Proportional safe zones (relative to 2560×1440, scaled to 560px wide)
		const BN_TV = { x: 0, y: 0, w: 1.0, h: 1.0 };
		const BN_DESK = { x: 0.08, y: 0, w: 0.84, h: 1.0 };
		const BN_SAFE = { x: 0.22, y: 0.16, w: 0.56, h: 0.68 };
		const BN_MOB = { x: 0.25, y: 0.18, w: 0.5, h: 0.64 };

		let bnStyle = 'grid';
		let bnShowSafe = false;
		let bnDevice = 'all'; // all, tv, desk, safe, mobile

		const BN_STYLES = {
			grid: (ctx, w, h) => {
				ctx.fillStyle = '#070b10';
				ctx.fillRect(0, 0, w, h);
				ctx.strokeStyle = 'rgba(155,109,255,0.1)';
				ctx.lineWidth = 1;
				for (let x = 0; x < w; x += w / 16) {
					ctx.beginPath();
					ctx.moveTo(x, 0);
					ctx.lineTo(x, h);
					ctx.stroke();
				}
				for (let y = 0; y < h; y += h / 9) {
					ctx.beginPath();
					ctx.moveTo(0, y);
					ctx.lineTo(w, y);
					ctx.stroke();
				}
				const sx = BN_SAFE.x * w,
					sy = BN_SAFE.y * h,
					sw = BN_SAFE.w * w,
					sh = BN_SAFE.h * h;
				ctx.strokeStyle = 'rgba(155,109,255,0.08)';
				ctx.lineWidth = 1;
				ctx.beginPath();
				ctx.arc(sx + sw * 0.12, sy + sh * 0.5, sh * 0.28, 0, Math.PI * 2);
				ctx.stroke();
				ctx.strokeStyle = 'rgba(155,109,255,0.04)';
				ctx.lineWidth = 2;
				ctx.beginPath();
				ctx.arc(sx + sw * 0.12, sy + sh * 0.5, sh * 0.4, 0, Math.PI * 2);
				ctx.stroke();
				ctx.fillStyle = '#9b6dff';
				ctx.beginPath();
				ctx.arc(sx + sw * 0.12, sy + sh * 0.5, sh * 0.18, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = 'rgba(155,109,255,0.7)';
				ctx.beginPath();
				ctx.arc(sx + sw * 0.12, sy + sh * 0.5, sh * 0.07, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#fff';
				ctx.font = `700 ${Math.floor(sh * 0.28)}px Syne,sans-serif`;
				ctx.fillText('SIGNAL', sx + sw * 0.28, sy + sh * 0.55);
				ctx.fillStyle = 'rgba(155,109,255,0.6)';
				ctx.font = `400 ${Math.floor(sh * 0.12)}px IBM Plex Mono,monospace`;
				ctx.fillText('DESIGN FOR SYSTEMATIC MINDS', sx + sw * 0.28, sy + sh * 0.75);
				ctx.fillStyle = 'rgba(155,109,255,0.3)';
				ctx.font = `400 ${Math.floor(sh * 0.1)}px IBM Plex Mono,monospace`;
				ctx.textAlign = 'right';
				ctx.fillText('New episodes every week', sx + sw * 0.9, sy + sh * 0.9);
				ctx.textAlign = 'left';
			},
			editorial: (ctx, w, h) => {
				ctx.fillStyle = '#f5f4f0';
				ctx.fillRect(0, 0, w, h);
				ctx.fillStyle = 'rgba(0,0,0,0.04)';
				for (let i = 0; i < 10; i++) {
					ctx.fillRect(0, i * (h / 10), w, (h / 10) * (i % 2 === 0 ? 1 : 0));
				}
				const sx = BN_SAFE.x * w,
					sy = BN_SAFE.y * h,
					sw = BN_SAFE.w * w,
					sh = BN_SAFE.h * h;
				ctx.fillStyle = '#111';
				ctx.fillRect(sx, sy + sh * 0.1, sw * 0.55, sh * 0.06);
				ctx.fillStyle = '#f5f4f0';
				ctx.font = `700 ${Math.floor(sh * 0.12)}px IBM Plex Mono,monospace`;
				ctx.fillText('SIGNAL', sx + 8, sy + sh * 0.19);
				ctx.fillStyle = '#111';
				ctx.font = `900 ${Math.floor(sh * 0.42)}px Syne,sans-serif`;
				ctx.fillText('DESIGN', sx, sy + sh * 0.65);
				ctx.fillStyle = 'rgba(0,0,0,0.4)';
				ctx.font = `400 ${Math.floor(sh * 0.13)}px IBM Plex Mono,monospace`;
				ctx.fillText('systematic visual thinking', sx, sy + sh * 0.88);
			},
			gradient: (ctx, w, h) => {
				const g = ctx.createLinearGradient(0, 0, w, h);
				g.addColorStop(0, '#0c0818');
				g.addColorStop(0.5, '#1a0d2e');
				g.addColorStop(1, '#0c1828');
				ctx.fillStyle = g;
				ctx.fillRect(0, 0, w, h);
				const r1 = ctx.createRadialGradient(w * 0.2, h * 0.5, 0, w * 0.2, h * 0.5, w * 0.4);
				r1.addColorStop(0, 'rgba(155,109,255,0.2)');
				r1.addColorStop(1, 'transparent');
				ctx.fillStyle = r1;
				ctx.fillRect(0, 0, w, h);
				const r2 = ctx.createRadialGradient(w * 0.8, h * 0.5, 0, w * 0.8, h * 0.5, w * 0.35);
				r2.addColorStop(0, 'rgba(56,192,232,0.15)');
				r2.addColorStop(1, 'transparent');
				ctx.fillStyle = r2;
				ctx.fillRect(0, 0, w, h);
				const sx = BN_SAFE.x * w,
					sy = BN_SAFE.y * h,
					sw = BN_SAFE.w * w,
					sh = BN_SAFE.h * h;
				ctx.fillStyle = '#fff';
				ctx.font = `800 ${Math.floor(sh * 0.38)}px Syne,sans-serif`;
				ctx.fillText('SIGNAL', sx + sw * 0.02, sy + sh * 0.62);
				ctx.fillStyle = 'rgba(155,109,255,0.8)';
				ctx.font = `400 ${Math.floor(sh * 0.14)}px IBM Plex Mono,monospace`;
				ctx.fillText('VISUAL DESIGN FUNDAMENTALS', sx + sw * 0.02, sy + sh * 0.82);
				ctx.fillStyle = 'rgba(56,192,232,0.5)';
				ctx.fillRect(sx + sw * 0.02, sy + sh * 0.88, sw * 0.35, 1);
			}
		};

		function drawBanner() {
			BN_STYLES[bnStyle](bnCtx, BW, BH);
			if (bnShowSafe) {
				const devices =
					bnDevice === 'all'
						? [
								['TV', BN_TV, 'rgba(56,192,232,0.15)', 'rgba(56,192,232,0.5)'],
								['Desktop', BN_DESK, 'rgba(155,109,255,0.12)', 'rgba(155,109,255,0.5)'],
								['Safe Zone', BN_SAFE, 'rgba(86,208,160,0.18)', 'rgba(86,208,160,0.8)'],
								['Mobile', BN_MOB, 'rgba(232,93,138,0.12)', 'rgba(232,93,138,0.5)']
							]
						: bnDevice === 'tv'
							? [['TV', BN_TV, 'rgba(56,192,232,0.18)', 'rgba(56,192,232,0.8)']]
							: bnDevice === 'desk'
								? [['Desktop', BN_DESK, 'rgba(155,109,255,0.18)', 'rgba(155,109,255,0.8)']]
								: bnDevice === 'safe'
									? [['Safe Zone', BN_SAFE, 'rgba(86,208,160,0.22)', 'rgba(86,208,160,0.9)']]
									: [['Mobile', BN_MOB, 'rgba(232,93,138,0.18)', 'rgba(232,93,138,0.8)']];

				devices.forEach(([label, z, fill, stroke]) => {
					const zx = z.x * BW,
						zy = z.y * BH,
						zw = z.w * BW,
						zh = z.h * BH;
					bnCtx.fillStyle = fill;
					bnCtx.fillRect(zx, zy, zw, zh);
					bnCtx.strokeStyle = stroke;
					bnCtx.lineWidth = 1.5;
					bnCtx.setLineDash([4, 3]);
					bnCtx.strokeRect(zx + 0.5, zy + 0.5, zw - 1, zh - 1);
					bnCtx.setLineDash([]);
					bnCtx.fillStyle = stroke;
					bnCtx.font = '9px IBM Plex Mono,monospace';
					bnCtx.fillText(label.toUpperCase(), zx + 5, zy + 12);
				});
			}

			const notes = {
				all: 'All device zones overlaid. Notice how the safe zone (green) sits within all cropped areas — content inside it is visible on every device.',
				tv: 'TV displays the full 2560×1440 banner. Wide decorative content extends to both edges.',
				desk: 'Desktop crops to roughly the central 84% width. Left/right margins are clipped.',
				safe: 'The safe zone (central 56% width, 68% height) is visible on ALL devices including mobile.',
				mobile:
					'Mobile shows only the central ~50% width strip. Anything outside this area is invisible on phones.'
			};
			document.getElementById('banner-device-note').textContent = notes[bnDevice] || '';
		}

		function setBannerStyle(style, btn) {
			bnStyle = style;
			document.querySelectorAll('#banner-toggle .btn').forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			drawBanner();
		}

		function toggleSafeZone() {
			bnShowSafe = !bnShowSafe;
			document.getElementById('safe-btn').classList.toggle('active', bnShowSafe);
			drawBanner();
		}

		const DEVICES = ['all', 'tv', 'desk', 'safe', 'mobile'];
		const DEVICE_LABELS = {
			all: 'Show: All Devices',
			tv: 'Show: TV',
			desk: 'Show: Desktop',
			safe: 'Show: Safe Zone',
			mobile: 'Show: Mobile'
		};
		let bnDeviceIdx = 0;
		function cycleDevice() {
			bnDeviceIdx = (bnDeviceIdx + 1) % DEVICES.length;
			bnDevice = DEVICES[bnDeviceIdx];
			document.getElementById('device-btn').textContent = DEVICE_LABELS[bnDevice];
			if (bnDevice !== 'all') {
				bnShowSafe = true;
				document.getElementById('safe-btn').classList.add('active');
			}
			drawBanner();
		}

		drawBanner();

		/* ══════════════════════════════════════
   DEMO 3: WEB LAYOUT GRID BUILDER
══════════════════════════════════════ */
		const webCvs = document.getElementById('web-canvas');
		const webCtx = webCvs.getContext('2d');
		const WW = webCvs.width,
			WH = webCvs.height;

		let webGrids = { cols: false, base: false, zones: true };

		function toggleWebGrid(type) {
			webGrids[type] = !webGrids[type];
			document.getElementById(type + '-grid-btn').classList.toggle('active', webGrids[type]);
			drawWebLayout();
		}

		function drawWebLayout() {
			const unit = parseInt(document.getElementById('web-unit').value);
			const cols = parseInt(document.getElementById('web-cols').value);
			const gutter = parseInt(document.getElementById('web-gutter').value);

			document.getElementById('web-unit-val').textContent = unit + 'px';
			document.getElementById('web-cols-val').textContent = cols;
			document.getElementById('web-gutter-val').textContent = gutter + 'px';

			// Scale everything to canvas width
			const scale = WW / 1200;
			const colW = (WW - (cols + 1) * gutter * scale) / cols;
			const maxW = 960 * scale;
			const marginX = (WW - maxW) / 2;

			const ctx = webCtx;
			ctx.fillStyle = '#080b0f';
			ctx.fillRect(0, 0, WW, WH);

			// Draw content zones first
			if (webGrids.zones) {
				// Nav bar
				ctx.fillStyle = '#0d1117';
				ctx.fillRect(0, 0, WW, unit * 4 * scale);
				ctx.fillStyle = 'rgba(56,192,232,0.05)';
				ctx.fillRect(0, 0, WW, unit * 4 * scale);

				// Hero section
				ctx.fillStyle = 'rgba(155,109,255,0.05)';
				ctx.fillRect(marginX, unit * 6 * scale, maxW, unit * 18 * scale);

				// Feature grid
				const cardH = unit * 14 * scale;
				const c3w = (maxW - gutter * scale * 2) / 3;
				[0, 1, 2].forEach((i) => {
					ctx.fillStyle = `rgba(56,192,232,0.04)`;
					roundRect(ctx, marginX + i * (c3w + gutter * scale), unit * 28 * scale, c3w, cardH, 4);
					ctx.fill();
				});

				// CTA section
				ctx.fillStyle = 'rgba(245,166,35,0.04)';
				ctx.fillRect(marginX, unit * 46 * scale, maxW, unit * 12 * scale);

				// Content labels
				ctx.font = `400 10px IBM Plex Mono,monospace`;
				const zones = [
					['NAV', WW * 0.5, unit * 2.8 * scale, 'rgba(56,192,232,0.5)'],
					['HERO SECTION', marginX + maxW * 0.35, unit * 15 * scale, 'rgba(155,109,255,0.5)'],
					['FEATURE CARDS', marginX + maxW * 0.35, unit * 36 * scale, 'rgba(56,192,232,0.4)'],
					['CTA SECTION', marginX + maxW * 0.35, unit * 52 * scale, 'rgba(245,166,35,0.5)']
				];
				zones.forEach(([label, x, y, col]) => {
					ctx.fillStyle = col;
					ctx.textAlign = 'center';
					ctx.fillText(label, x, y);
				});
				ctx.textAlign = 'left';

				// Simulate actual content
				// Nav items
				ctx.fillStyle = '#fff';
				ctx.font = `700 12px Syne,sans-serif`;
				ctx.fillText('SIGNAL', marginX + 8, unit * 2.8 * scale);
				ctx.fillStyle = 'rgba(155,109,255,0.7)';
				ctx.font = `400 10px IBM Plex Mono,monospace`;
				['Learn', 'About', 'Course'].forEach((t, i) =>
					ctx.fillText(t, marginX + maxW * 0.6 + i * 60, unit * 2.8 * scale)
				);

				// Hero text
				ctx.fillStyle = '#fff';
				ctx.font = `800 ${unit * 4.5 * scale}px Syne,sans-serif`;
				ctx.fillText('Design with', marginX + unit * scale, unit * 12 * scale);
				ctx.fillStyle = '#9b6dff';
				ctx.fillText('Intention', marginX + unit * scale, unit * 17 * scale);
				ctx.fillStyle = 'rgba(208,219,232,0.6)';
				ctx.font = `400 ${unit * 1.8 * scale}px IBM Plex Mono,monospace`;
				ctx.fillText(
					'Systematic approaches to visual communication',
					marginX + unit * scale,
					unit * 20.5 * scale
				);

				// Feature cards
				[0, 1, 2].forEach((i) => {
					const cx2 = marginX + i * (c3w + gutter * scale);
					ctx.fillStyle = '#38c0e8';
					roundRect(ctx, cx2 + c3w * 0.08, unit * 30 * scale, c3w * 0.84, unit * 4 * scale, 3);
					ctx.fill();
					ctx.fillStyle = '#fff';
					ctx.font = `600 ${unit * 1.5 * scale}px IBM Plex Mono,monospace`;
					ctx.fillText(['Typography', 'Color', 'Layout'][i], cx2 + c3w * 0.12, unit * 32.5 * scale);
					ctx.fillStyle = 'rgba(208,219,232,0.45)';
					ctx.font = `400 ${unit * 1.2 * scale}px IBM Plex Mono,monospace`;
					ctx.fillText('8 lessons', cx2 + c3w * 0.12, unit * 34.5 * scale);
					ctx.fillText('→ Start', cx2 + c3w * 0.12, unit * 39 * scale);
				});
			}

			// Column grid overlay
			if (webGrids.cols) {
				for (let i = 0; i < cols; i++) {
					const x = marginX + i * (colW + gutter * scale) + gutter * scale * 0.5;
					ctx.fillStyle = 'rgba(155,109,255,0.08)';
					ctx.fillRect(x, 0, colW, WH);
					ctx.strokeStyle = 'rgba(155,109,255,0.2)';
					ctx.lineWidth = 1;
					ctx.beginPath();
					ctx.moveTo(x, 0);
					ctx.lineTo(x, WH);
					ctx.stroke();
					ctx.beginPath();
					ctx.moveTo(x + colW, 0);
					ctx.lineTo(x + colW, WH);
					ctx.stroke();
				}
				// Max-width boundary
				ctx.strokeStyle = 'rgba(245,166,35,0.3)';
				ctx.lineWidth = 1;
				ctx.setLineDash([4, 3]);
				ctx.beginPath();
				ctx.moveTo(marginX, 0);
				ctx.lineTo(marginX, WH);
				ctx.stroke();
				ctx.beginPath();
				ctx.moveTo(marginX + maxW, 0);
				ctx.lineTo(marginX + maxW, WH);
				ctx.stroke();
				ctx.setLineDash([]);
				ctx.fillStyle = 'rgba(245,166,35,0.6)';
				ctx.font = '9px IBM Plex Mono,monospace';
				ctx.fillText(`max-width: 960px`, marginX + 4, 12);
			}

			// Baseline grid overlay
			if (webGrids.base) {
				const baseH = unit * 1.5 * scale;
				ctx.strokeStyle = 'rgba(232,93,138,0.12)';
				ctx.lineWidth = 1;
				for (let y = 0; y < WH; y += baseH) {
					ctx.beginPath();
					ctx.moveTo(0, y);
					ctx.lineTo(WW, y);
					ctx.stroke();
				}
				ctx.fillStyle = 'rgba(232,93,138,0.5)';
				ctx.font = '8px IBM Plex Mono,monospace';
				ctx.textAlign = 'right';
				ctx.fillText(`baseline: ${Math.round(unit * 1.5)}px`, WW - 4, baseH);
				ctx.textAlign = 'left';
			}

			// Update rhythm display
			const scale4 = [1, 2, 3, 4, 6, 8, 12, 16].map((m) => `${unit * m}px`).slice(0, 6);
			document.getElementById('web-rhythm-display').innerHTML =
				`<span style="color:var(--violet)">Base unit: ${unit}px</span> &nbsp;·&nbsp; ` +
				`<span style="color:var(--muted)">Scale: ${scale4.join(' / ')}</span> &nbsp;·&nbsp; ` +
				`<span style="color:var(--sky)">Column width: ~${Math.round(colW / scale)}px</span> &nbsp;·&nbsp; ` +
				`<span style="color:var(--sage)">Gutter: ${gutter}px · ${cols} cols</span>`;
		}

		function updateWebLayout() {
			drawWebLayout();
		}
		drawWebLayout();

		/* ══════════════════════════════════════
   DEMO 4: THUMBNAIL COMPARISON
══════════════════════════════════════ */
		const CMP_PAIRS = [
			{
				topic: 'How to study effectively',
				A: {
					draw: (ctx, w, h) => {
						ctx.fillStyle = '#0a0f18';
						ctx.fillRect(0, 0, w, h);
						// Cluttered — too many elements, low contrast text
						ctx.fillStyle = '#1a2a40';
						ctx.fillRect(0, 0, w * 0.4, h);
						ctx.fillStyle = '#c4906e';
						ctx.beginPath();
						ctx.ellipse(w * 0.2, h * 0.42, w * 0.12, h * 0.26, 0, 0, Math.PI * 2);
						ctx.fill();
						// Weak title — too much text, low contrast
						ctx.fillStyle = 'rgba(200,210,220,0.7)';
						ctx.font = `500 ${h * 0.08}px IBM Plex Mono,monospace`;
						ctx.fillText('How to study more', w * 0.42, h * 0.28);
						ctx.fillText('effectively using', w * 0.42, h * 0.4);
						ctx.fillText('proven techniques', w * 0.42, h * 0.52);
						ctx.fillText('from experts', w * 0.42, h * 0.64);
						// Extra badges
						ctx.fillStyle = 'rgba(86,208,160,0.4)';
						ctx.fillRect(w * 0.42, h * 0.72, w * 0.3, h * 0.1);
						ctx.fillStyle = 'rgba(255,255,255,0.5)';
						ctx.font = `400 ${h * 0.07}px IBM Plex Mono,monospace`;
						ctx.fillText('NEW VIDEO', w * 0.44, h * 0.8);
					},
					label: 'Option A'
				},
				B: {
					draw: (ctx, w, h) => {
						ctx.fillStyle = '#080d14';
						ctx.fillRect(0, 0, w, h);
						ctx.fillStyle = '#121e30';
						ctx.fillRect(0, 0, w * 0.38, h);
						ctx.fillStyle = '#c4906e';
						ctx.beginPath();
						ctx.ellipse(w * 0.19, h * 0.42, w * 0.11, h * 0.24, 0, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = '#141e2c';
						ctx.fillRect(0, h * 0.62, w * 0.38, h);
						ctx.fillStyle = 'rgba(56,192,232,1)';
						ctx.fillRect(0, 0, 3, h);
						ctx.fillStyle = '#fff';
						ctx.font = `800 ${h * 0.2}px Syne,sans-serif`;
						ctx.fillText('STUDY', w * 0.42, h * 0.45);
						ctx.fillStyle = '#38c0e8';
						ctx.font = `800 ${h * 0.14}px Syne,sans-serif`;
						ctx.fillText('SMARTER', w * 0.42, h * 0.63);
						ctx.fillStyle = 'rgba(56,192,232,0.5)';
						ctx.font = `400 ${h * 0.075}px IBM Plex Mono,monospace`;
						ctx.fillText('5 evidence-based methods', w * 0.42, h * 0.79);
					},
					label: 'Option B'
				},
				winner: 'B',
				analysis: `Option B communicates more effectively on every criterion. Attention: the white headline at maximum weight (800) immediately anchors the eye at any scale. Communication: "STUDY SMARTER" conveys the topic in two words; Option A requires reading four lines. Curiosity: "5 evidence-based methods" promises specific, credible value. Option A uses 14 words in the text zone — invisible at thumbnail scale and structurally unfocused.`
			},
			{
				topic: 'The best camera for YouTube',
				A: {
					draw: (ctx, w, h) => {
						// Centered, static, low energy
						ctx.fillStyle = '#0f1820';
						ctx.fillRect(0, 0, w, h);
						// Camera centered and small
						ctx.strokeStyle = 'rgba(200,210,220,0.6)';
						ctx.lineWidth = 2;
						const cx = w * 0.5,
							cy = h * 0.44,
							cw = w * 0.4,
							ch = h * 0.32;
						roundRect(ctx, cx - cw / 2, cy - ch / 2, cw, ch, 8);
						ctx.stroke();
						ctx.beginPath();
						ctx.arc(cx, cy, ch * 0.32, 0, Math.PI * 2);
						ctx.stroke();
						ctx.beginPath();
						ctx.arc(cx, cy, ch * 0.18, 0, Math.PI * 2);
						ctx.stroke();
						roundRect(ctx, cx - cw * 0.25, cy - ch * 0.62, cw * 0.22, ch * 0.2, 4);
						ctx.stroke();
						// Text centered below
						ctx.fillStyle = 'rgba(200,210,220,0.65)';
						ctx.font = `400 ${h * 0.1}px IBM Plex Mono,monospace`;
						ctx.textAlign = 'center';
						ctx.fillText('Best Camera', w * 0.5, h * 0.78);
						ctx.fillStyle = 'rgba(150,165,180,0.5)';
						ctx.font = `400 ${h * 0.08}px IBM Plex Mono,monospace`;
						ctx.fillText('for YouTube 2024', w * 0.5, h * 0.9);
						ctx.textAlign = 'left';
					},
					label: 'Option A'
				},
				B: {
					draw: (ctx, w, h) => {
						ctx.fillStyle = '#0a0c10';
						ctx.fillRect(0, 0, w, h);
						const g = ctx.createLinearGradient(0, 0, 0, h);
						g.addColorStop(0, 'rgba(245,166,35,0.08)');
						g.addColorStop(1, 'transparent');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, w, h);
						// Large camera — dominant left
						ctx.strokeStyle = '#f5a623';
						ctx.lineWidth = 2.5;
						const cw = w * 0.48,
							ch = h * 0.52,
							cx = w * 0.28,
							cy = h * 0.46;
						roundRect(ctx, cx - cw / 2, cy - ch / 2, cw, ch, 10);
						ctx.stroke();
						ctx.beginPath();
						ctx.arc(cx, cy, ch * 0.34, 0, Math.PI * 2);
						ctx.stroke();
						ctx.beginPath();
						ctx.arc(cx, cy, ch * 0.2, 0, Math.PI * 2);
						ctx.stroke();
						ctx.fillStyle = 'rgba(245,166,35,0.3)';
						ctx.beginPath();
						ctx.arc(cx, cy, ch * 0.2, 0, Math.PI * 2);
						ctx.fill();
						roundRect(ctx, cx - cw * 0.2, cy - ch * 0.66, cw * 0.28, ch * 0.22, 5);
						ctx.stroke();
						ctx.fillStyle = '#fff';
						ctx.font = `800 ${h * 0.18}px Syne,sans-serif`;
						ctx.fillText('#1', w * 0.58, h * 0.42);
						ctx.fillStyle = '#f5a623';
						ctx.font = `800 ${h * 0.14}px Syne,sans-serif`;
						ctx.fillText('CAMERA', w * 0.58, h * 0.6);
						ctx.fillStyle = 'rgba(255,255,255,0.55)';
						ctx.font = `400 ${h * 0.075}px IBM Plex Mono,monospace`;
						ctx.fillText('for YouTube in 2024', w * 0.58, h * 0.77);
					},
					label: 'Option B'
				},
				winner: 'B',
				analysis: `Option B wins decisively. Option A places a small, low-contrast camera in the center with regular-weight text below — at thumbnail scale, both the subject and the text near-disappear. Option B makes the camera dominant and large (occupying the left 40% of the frame), uses maximum-weight type in high contrast, and an amber accent that provides immediate focal color. The reading order is clear: camera → "#1" → "CAMERA" → supporting text.`
			},
			{
				topic: 'Why your designs look amateur',
				A: {
					draw: (ctx, w, h) => {
						ctx.fillStyle = '#0a0d14';
						ctx.fillRect(0, 0, w, h);
						ctx.fillStyle = '#141e2e';
						ctx.fillRect(0, 0, w * 0.38, h);
						ctx.fillStyle = '#c4906e';
						ctx.beginPath();
						ctx.ellipse(w * 0.19, h * 0.42, w * 0.11, h * 0.24, 0, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = '#1a2a3e';
						ctx.fillRect(0, h * 0.62, w * 0.38, h);
						// Competing accents — rose AND sky AND amber
						ctx.fillStyle = '#e85d8a';
						ctx.font = `800 ${h * 0.17}px Syne,sans-serif`;
						ctx.fillText('YOUR', w * 0.42, h * 0.3);
						ctx.fillStyle = '#38c0e8';
						ctx.font = `800 ${h * 0.17}px Syne,sans-serif`;
						ctx.fillText('DESIGNS', w * 0.42, h * 0.48);
						ctx.fillStyle = '#f5a623';
						ctx.font = `800 ${h * 0.17}px Syne,sans-serif`;
						ctx.fillText('SUCK', w * 0.42, h * 0.66);
						// Random badge
						ctx.fillStyle = 'rgba(155,109,255,0.5)';
						roundRect(ctx, w * 0.42, h * 0.74, w * 0.26, h * 0.1, 4);
						ctx.fill();
						ctx.fillStyle = '#fff';
						ctx.font = `400 ${h * 0.07}px IBM Plex Mono,monospace`;
						ctx.fillText('watch this!', w * 0.44, h * 0.82);
					},
					label: 'Option A'
				},
				B: {
					draw: (ctx, w, h) => {
						ctx.fillStyle = '#08090e';
						ctx.fillRect(0, 0, w, h);
						// High contrast face — wide
						ctx.fillStyle = '#10192a';
						ctx.fillRect(0, 0, w * 0.42, h);
						const g = ctx.createLinearGradient(w * 0.42, 0, w * 0.42 + 40, 0);
						g.addColorStop(0, 'rgba(8,9,14,0)');
						g.addColorStop(1, 'rgba(8,9,14,1)');
						ctx.fillStyle = '#c4906e';
						ctx.beginPath();
						ctx.ellipse(w * 0.21, h * 0.4, w * 0.13, h * 0.28, 0, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = '#10192a';
						ctx.fillRect(0, h * 0.6, w * 0.42, h);
						// Single accent — clean
						ctx.fillStyle = '#e85d8a';
						ctx.fillRect(w * 0.42, 0, 3, h);
						ctx.fillStyle = '#fff';
						ctx.font = `800 ${h * 0.16}px Syne,sans-serif`;
						ctx.fillText('WHY IT', w * 0.46, h * 0.38);
						ctx.fillStyle = '#e85d8a';
						ctx.font = `800 ${h * 0.16}px Syne,sans-serif`;
						ctx.fillText('LOOKS', w * 0.46, h * 0.55);
						ctx.fillStyle = '#fff';
						ctx.font = `800 ${h * 0.16}px Syne,sans-serif`;
						ctx.fillText('AMATEUR', w * 0.46, h * 0.72);
						ctx.fillStyle = 'rgba(232,93,138,0.5)';
						ctx.font = `400 ${h * 0.07}px IBM Plex Mono,monospace`;
						ctx.fillText('5 fixable mistakes', w * 0.46, h * 0.86);
					},
					label: 'Option B'
				},
				winner: 'B',
				analysis: `Option A uses three different accent colors (rose, sky, amber) for three consecutive title words — destroying visual hierarchy. Each word competes equally for dominance, and the eye cannot determine a reading order. The additional badge introduces a fourth color. Option B uses a single accent (rose) precisely: one bar, one title-word highlight. The reading path is unambiguous — face → "WHY IT LOOKS AMATEUR" as a unified block → supporting line. Single accent color = single focal energy.`
			}
		];

		let currentPair = 0;
		let pairAnswered = [false, false, false];

		function drawCompare(pair) {
			const p = CMP_PAIRS[pair];
			const lCvs = document.getElementById('cmp-left-canvas');
			const rCvs = document.getElementById('cmp-right-canvas');
			p.A.draw(lCvs.getContext('2d'), lCvs.width, lCvs.height);
			p.B.draw(rCvs.getContext('2d'), rCvs.width, rCvs.height);
			document.getElementById('cmp-left-label').textContent = p.A.label;
			document.getElementById('cmp-right-label').textContent = p.B.label;
			document.getElementById('cmp-left').classList.remove('selected');
			document.getElementById('cmp-right').classList.remove('selected');
			if (!pairAnswered[pair]) {
				document.getElementById('compare-verdict').textContent =
					'Click the thumbnail you think communicates more effectively.';
				document.getElementById('compare-verdict').style.color = 'var(--muted)';
			} else {
				showVerdict(pair, p.winner);
			}
		}

		function showVerdict(pair, winner) {
			const v = document.getElementById('compare-verdict');
			v.style.color = 'var(--text)';
			v.innerHTML = `<strong style="color:var(--sage)">Option ${winner} is more effective.</strong><br><br>${CMP_PAIRS[pair].analysis}`;
		}

		document.getElementById('cmp-left').addEventListener('click', () => {
			if (pairAnswered[currentPair]) return;
			pairAnswered[currentPair] = true;
			const winner = CMP_PAIRS[currentPair].winner;
			document.getElementById('cmp-left').classList.add('selected');
			showVerdict(currentPair, winner);
		});
		document.getElementById('cmp-right').addEventListener('click', () => {
			if (pairAnswered[currentPair]) return;
			pairAnswered[currentPair] = true;
			const winner = CMP_PAIRS[currentPair].winner;
			document.getElementById('cmp-right').classList.add('selected');
			showVerdict(currentPair, winner);
		});

		function showPair(idx, btn) {
			currentPair = idx;
			document.querySelectorAll('#pair-selector .btn').forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			drawCompare(idx);
		}

		drawCompare(0);

		/* ══════════════════════════════════════
   ASSESSMENT
══════════════════════════════════════ */
		const ASSESS_QS = [
			{
				label: 'Specimen A — Thumbnail Text Problem',
				canvasDraw: (ctx, w, h) => {
					ctx.fillStyle = '#0a0d14';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = '#141e2e';
					ctx.fillRect(0, 0, w * 0.38, h);
					ctx.fillStyle = '#c4906e';
					ctx.beginPath();
					ctx.ellipse(w * 0.19, h * 0.42, w * 0.11, h * 0.24, 0, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = '#1a2a3e';
					ctx.fillRect(0, h * 0.62, w * 0.38, h);
					ctx.fillStyle = 'rgba(200,215,230,0.55)';
					ctx.font = `400 ${h * 0.09}px IBM Plex Mono,monospace`;
					ctx.fillText('how to get better at', w * 0.42, h * 0.28);
					ctx.fillText('graphic design fast', w * 0.42, h * 0.41);
					ctx.fillText('with these simple', w * 0.42, h * 0.54);
					ctx.fillText('beginner techniques', w * 0.42, h * 0.67);
					ctx.fillText('you can try today', w * 0.42, h * 0.8);
				},
				question:
					'This thumbnail has five lines of text at regular weight in a medium-contrast colour. What are the two critical failures?',
				correct: 1,
				opts: [
					'A. The text is too centered and the font family is inappropriate for thumbnails',
					'B. Too many words (17 total) at insufficient weight (400) and insufficient contrast — at thumbnail scale the text collapses to unreadable pixels; a viewer has less than 2 seconds and 2–4 bold high-contrast words to work with',
					'C. The subject area (left third) is too small relative to the text zone',
					'D. Using a monospace font for thumbnail text always fails — only display or sans-serif fonts work'
				],
				ok: 'Correct. Two compounding failures: quantity (17 words where 2–4 is the limit) and weight/contrast (regular weight at medium contrast becomes invisible at 168px). Both must be fixed — reducing words alone without increasing weight and contrast still produces an unreadable thumbnail.',
				bad: 'Not quite. The core problems are word count (17 words vs the 2–4 maximum) and text weight/contrast (regular weight at medium contrast disappears at thumbnail scale). The font family and subject size are not the primary issues here.'
			},
			{
				label: 'Specimen B — Banner Safe Zone Failure',
				canvasDraw: (ctx, w, h) => {
					const bg = ctx.createLinearGradient(0, 0, w, 0);
					bg.addColorStop(0, '#0a0e14');
					bg.addColorStop(0.5, '#0d1520');
					bg.addColorStop(1, '#0a0e14');
					ctx.fillStyle = bg;
					ctx.fillRect(0, 0, w, h);
					// Essential content placed at far left — outside safe zone
					ctx.fillStyle = '#9b6dff';
					ctx.beginPath();
					ctx.arc(w * 0.06, h * 0.5, h * 0.28, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = 'rgba(155,109,255,0.6)';
					ctx.beginPath();
					ctx.arc(w * 0.06, h * 0.5, h * 0.15, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = '#fff';
					ctx.font = `700 ${h * 0.22}px Syne,sans-serif`;
					ctx.fillText('SIGNAL', w * 0.12, h * 0.56);
					ctx.fillStyle = 'rgba(155,109,255,0.6)';
					ctx.font = `400 ${h * 0.1}px IBM Plex Mono,monospace`;
					ctx.fillText('visual design course', w * 0.12, h * 0.76);
					// Decorative only content at center
					ctx.strokeStyle = 'rgba(155,109,255,0.12)';
					ctx.lineWidth = 1;
					for (let x = w * 0.28; x < w * 0.72; x += w * 0.04) {
						ctx.beginPath();
						ctx.moveTo(x, 0);
						ctx.lineTo(x, h);
						ctx.stroke();
					}
					ctx.fillStyle = 'rgba(56,192,232,0.08)';
					ctx.fillRect(w * 0.28, 0, w * 0.44, h);
					// Safe zone indicator
					ctx.strokeStyle = 'rgba(232,93,138,0.5)';
					ctx.lineWidth = 1;
					ctx.setLineDash([3, 3]);
					ctx.strokeRect(w * 0.22, h * 0.16, w * 0.56, h * 0.68);
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(232,93,138,0.6)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.fillText('← safe zone boundary', w * 0.23, h * 0.14);
				},
				question:
					'The channel name and logo are placed at the far left of the banner (outside the dashed safe zone boundary shown). What is the consequence on mobile?',
				correct: 2,
				opts: [
					'A. The left-aligned logo creates poor visual balance — it should be centered for all devices',
					"B. YouTube's algorithm penalises banners with off-center branding",
					'C. Mobile users only see the central safe zone strip — the channel name and logo fall outside this area and are invisible to the majority of viewers who use YouTube on phones',
					'D. The gradient background causes the text to become unreadable on mobile screens'
				],
				ok: "Correct. The safe zone (dashed boundary) shows the only area visible across all devices, including mobile. The channel name and logo are positioned at the far left — entirely outside the safe zone — meaning mobile viewers, often 60–70% of a channel's audience, see only the neutral grid decoration in the center. Essential content must live within the safe zone.",
				bad: 'Not quite. The safe zone (dashed boundary) marks the only area visible on all devices. Content placed outside it — including the channel name and logo shown here — is invisible to mobile viewers. This is a platform constraint, not a visual balance issue.'
			}
		];

		const assessAnswered = {};
		function buildAssessment() {
			const wrap = document.getElementById('assess-wrap');
			ASSESS_QS.forEach((q, qi) => {
				const div = document.createElement('div');
				div.className = 'assess-q';
				const hdr = document.createElement('div');
				hdr.className = 'assess-q-header';
				hdr.textContent = q.label;
				const body = document.createElement('div');
				body.className = 'assess-q-body';
				const cvs = document.createElement('canvas');
				cvs.width = 560;
				cvs.height = 200;
				cvs.style.cssText = 'display:block;max-width:100%;border-bottom:1px solid var(--border)';
				const qt = document.createElement('div');
				qt.className = 'assess-q-text';
				qt.textContent = q.question;
				const opts = document.createElement('div');
				opts.className = 'assess-opts';
				q.opts.forEach((opt, oi) => {
					const btn = document.createElement('div');
					btn.className = 'assess-opt';
					btn.textContent = opt;
					btn.addEventListener('click', () => {
						if (assessAnswered[qi]) return;
						assessAnswered[qi] = true;
						opts.querySelectorAll('.assess-opt').forEach((b, bi) => {
							b.classList.add('disabled');
							if (bi === q.correct) b.classList.add('correct');
						});
						const fb = div.querySelector('.assess-feedback');
						if (oi === q.correct) {
							btn.classList.remove('disabled');
							fb.textContent = '✓ ' + q.ok;
							fb.className = 'assess-feedback ok';
						} else {
							btn.classList.add('wrong');
							fb.textContent = '✗ ' + q.bad;
							fb.className = 'assess-feedback bad';
						}
					});
					opts.appendChild(btn);
				});
				const fb = document.createElement('div');
				fb.className = 'assess-feedback';
				body.appendChild(cvs);
				body.appendChild(qt);
				body.appendChild(opts);
				body.appendChild(fb);
				div.appendChild(hdr);
				div.appendChild(body);
				wrap.appendChild(div);
				const ctx = cvs.getContext('2d');
				q.canvasDraw(ctx, cvs.width, cvs.height);
			});
		}
		buildAssessment();

		/* ══════════════════════════════════════
   QUIZ
══════════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;
		const explanations = [
			'Correct. At 168×94px (smallest thumbnail render), 18px regular weight becomes roughly 2–3 pixels tall of low-contrast grey — completely invisible. Thumbnails require 700–800 weight and near-maximum value contrast to survive the scale reduction.',
			'Correct. YouTube crops banners to a narrow central strip on mobile devices, which account for the majority of viewers. Content placed at the left edge — outside the safe zone — is invisible on mobile regardless of how it looks on desktop.',
			'Correct. When all spacing values are mathematically related (multiples of a base unit), the eye perceives an underlying order even without consciously identifying it. Arbitrary values create low-level perceptual noise that makes layouts feel amateurish — a sensation viewers have without being able to articulate why.',
			'Correct. 12 divides evenly into 2, 3, 4, and 6 — providing halves, thirds, quarters, and sixths as layout options. 10 only divides into 2 and 5, which covers far fewer practical layout configurations.',
			"Correct. The evaluation sequence follows the viewer's actual cognitive path: first they notice something (attention), then they understand what it's about (communication), then they decide whether to engage (curiosity). A thumbnail that wins the first criterion has a structural head start on the subsequent ones."
		];

		function handleQuiz(el, idx) {
			const parent = el.closest('.question');
			const correct = parseInt(parent.querySelector('.options').dataset.correct);
			const opts = parent.querySelectorAll('.option');
			const fbIdx = Array.from(document.querySelectorAll('.question')).indexOf(parent);
			const fb = document.getElementById('fb-' + fbIdx);
			if (el.classList.contains('disabled')) return;
			opts.forEach((o) => o.classList.add('disabled'));
			if (idx === correct) {
				el.classList.add('correct');
				fb.textContent = '✓ ' + explanations[fbIdx];
				fb.className = 'feedback ok';
				quizScore++;
			} else {
				el.classList.add('wrong');
				opts[correct].classList.add('correct');
				fb.textContent =
					'✗ Revisit the relevant section — think about what the viewer actually experiences, not what looks good at full resolution.';
				fb.className = 'feedback bad';
			}
			quizAnswered++;
			if (quizAnswered === 5) {
				const s = document.getElementById('quiz-score');
				document.getElementById('score-num').textContent = quizScore + ' / 5';
				s.style.display = 'block';
				setTimeout(() => s.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 300);
			}
		}

		if (typeof roundRect === 'function') actions.roundRect = roundRect;
		if (typeof drawThumbLab === 'function') actions.drawThumbLab = drawThumbLab;
		if (typeof drawThumbZones === 'function') actions.drawThumbZones = drawThumbZones;
		if (typeof drawThumbGrid === 'function') actions.drawThumbGrid = drawThumbGrid;
		if (typeof syncThumbScales === 'function') actions.syncThumbScales = syncThumbScales;
		if (typeof setThumbLayout === 'function') actions.setThumbLayout = setThumbLayout;
		if (typeof toggleZones === 'function') actions.toggleZones = toggleZones;
		if (typeof toggleThirdGrid === 'function') actions.toggleThirdGrid = toggleThirdGrid;
		if (typeof toggleThumbScale === 'function') actions.toggleThumbScale = toggleThumbScale;
		if (typeof drawBanner === 'function') actions.drawBanner = drawBanner;
		if (typeof setBannerStyle === 'function') actions.setBannerStyle = setBannerStyle;
		if (typeof toggleSafeZone === 'function') actions.toggleSafeZone = toggleSafeZone;
		if (typeof cycleDevice === 'function') actions.cycleDevice = cycleDevice;
		if (typeof toggleWebGrid === 'function') actions.toggleWebGrid = toggleWebGrid;
		if (typeof drawWebLayout === 'function') actions.drawWebLayout = drawWebLayout;
		if (typeof updateWebLayout === 'function') actions.updateWebLayout = updateWebLayout;
		if (typeof drawCompare === 'function') actions.drawCompare = drawCompare;
		if (typeof showVerdict === 'function') actions.showVerdict = showVerdict;
		if (typeof showPair === 'function') actions.showPair = showPair;
		if (typeof buildAssessment === 'function') actions.buildAssessment = buildAssessment;
		if (typeof handleQuiz === 'function') actions.handleQuiz = handleQuiz;

		return () => {
			_listeners.forEach((l) => l.target.removeEventListener(...l.args));
		};
	});
</script>

<div class="page-wrapper">
	<header class="course-header">
		<div>
			<div class="course-label">Graphic Design &amp; Visual Storytelling</div>
			<div class="course-title">Building a Personal Creative Identity</div>
		</div>
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 07 of 10</div>
	</header>

	<div class="module-hero">
		<div class="module-number">07</div>
		<div class="module-tag">Module 07 · Grids + Platforms</div>
		<h1 class="module-title">Layout for<br /><span>Digital Platforms</span></h1>
		<div class="progress-bar-wrap">
			<div
				class="progress-bar-fill"
				id="reading-progress"
				role="progressbar"
				aria-valuemin="0"
				aria-valuemax="100"
				aria-valuenow="0"
			></div>
		</div>
	</div>

	<nav class="toc">
		<div class="toc-label">Contents</div>
		<ul class="toc-list">
			<li><a href="#objectives">Objectives</a></li>
			<li><a href="#thumbnail-layout">Thumbnail Layout</a></li>
			<li><a href="#banner">Banner Composition</a></li>
			<li><a href="#web-layout">Website Grid &amp; Rhythm</a></li>
			<li><a href="#comparison">Thumbnail Comparison</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Apply the three-zone layout model to thumbnail compositions</li>
			<li>Understand the YouTube banner safe zone and design within its constraints</li>
			<li>Build a website layout using a consistent spacing unit and typographic grid</li>
			<li>Evaluate two thumbnails and determine which communicates more effectively</li>
		</ul>
	</section>

	<!-- ═══════════════════════════════
     SECTION 1: THUMBNAIL LAYOUT
═══════════════════════════════ -->
	<section id="thumbnail-layout" class="section">
		<div class="section-header">
			<span class="section-num">07.01</span>
			<h2 class="section-title">Designing for Thumbnails: Scale, Clarity, Text Legibility</h2>
		</div>

		<p>
			A YouTube thumbnail is one of the most constrained design surfaces in existence. It must do
			three things simultaneously: be legible at 168×94 pixels (the smallest size YouTube renders
			it), communicate the video's value in under two seconds, and compete visually with dozens of
			adjacent thumbnails. Every layout decision is subordinate to these three constraints.
		</p>

		<p>
			The most reliable thumbnail structure is the <strong>three-zone model</strong>: a dominant
			visual zone (the primary subject — typically a face, object, or high-contrast graphic), a text
			zone (the title or key phrase, maximum five words), and a breathing zone (visual rest that
			separates the two). These zones do not need to be rigid columns — they can be asymmetric,
			overlapping, or diagonal — but they must exist. Thumbnails that violate this model typically
			suffer from one of two failure modes: visual noise (too many competing elements, no clear zone
			boundaries) or visual emptiness (a single centered element with no structural tension).
		</p>

		<p>
			Text in thumbnails follows rules that differ sharply from body typography.
			<em>Weight must be maximum</em> — 700 or 800. <em>Size must be aggressive</em> — typically
			48–72px at 1280×720, which renders at approximately 6–9px at thumbnail scale.
			<em>Contrast must be absolute</em> — white on dark or dark on light, never medium on medium.
			<em>Word count must be minimal</em> — two to four words is the sweet spot. A five-word title is
			acceptable; a ten-word title is invisible.
		</p>

		<div class="callout amber">
			<div class="callout-label">The 10% Rule</div>
			Design your thumbnail at full resolution, then scale it to 10% of its size (128×72px) and look at
			it for two seconds. If you can identify the primary subject and read the first two words of the
			title, it passes. If anything is unclear at that scale, it is not a layout problem — it is a hierarchy
			problem that the layout exposed.
		</div>

		<!-- DEMO 1: Thumbnail Layout Lab -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Thumbnail Layout Lab</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Toggle layout zones to see how the three-zone model structures a thumbnail. Switch between
					layout patterns and observe how each changes the reading order and compositional energy.
				</p>

				<div class="thumb-zone-btns" id="thumb-zone-btns">
					<button
						class="btn active"
						onclick={(e) => actions.setThumbLayout('thirds', e.currentTarget)}
					>
						Left-Third Subject
					</button>
					<button class="btn" onclick={(e) => actions.setThumbLayout('center', e.currentTarget)}
						>Centered Subject</button
					>
					<button class="btn" onclick={(e) => actions.setThumbLayout('fill', e.currentTarget)}
						>Full-Bleed Subject</button
					>
					<button class="btn" onclick={(e) => actions.setThumbLayout('split', e.currentTarget)}>
						Side-by-Side Split
					</button>
				</div>

				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button class="btn sky" id="zones-btn" onclick={(e) => actions.toggleZones()}
						>Show Zones</button
					>
					<button class="btn" id="grid-btn" onclick={(e) => actions.toggleThirdGrid()}
						>Show Grid</button
					>
					<button class="btn violet" id="scale-btn" onclick={(e) => actions.toggleThumbScale()}>
						Preview at 10%
					</button>
				</div>

				<canvas
					id="thumb-lab-canvas"
					width="560"
					height="315"
					aria-label="Thumb Lab Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>

				<div class="zone-info" id="zone-info">
					Select a layout pattern above to see how the three zones are distributed.
				</div>

				<div class="thumb-scale-row" id="thumb-scale-row">
					<div style="font-size: 11px; color: var(--muted); flex: 1; line-height: 1.5">
						Size comparison — how this thumbnail renders across YouTube contexts:
					</div>
					<div class="thumb-scale-item">
						<canvas
							id="ts-home"
							width="210"
							height="118"
							style="border: 1px solid var(--border2)"
							aria-label="Ts Home Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<div class="thumb-scale-label">Home feed</div>
					</div>
					<div class="thumb-scale-item">
						<canvas
							id="ts-search"
							width="120"
							height="68"
							style="border: 1px solid var(--border2)"
							aria-label="Ts Search Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<div class="thumb-scale-label">Search results</div>
					</div>
					<div class="thumb-scale-item">
						<canvas
							id="ts-related"
							width="84"
							height="47"
							style="border: 1px solid var(--border2)"
							aria-label="Ts Related Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<div class="thumb-scale-label">Sidebar / related</div>
					</div>
					<div class="thumb-scale-item">
						<canvas
							id="ts-mobile"
							width="48"
							height="27"
							style="border: 1px solid var(--border2)"
							aria-label="Ts Mobile Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<div class="thumb-scale-label">Mobile list</div>
					</div>
				</div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Layout Zone</th>
					<th>Purpose</th>
					<th>Common Errors</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Dominant visual zone</td>
					<td>Arrests attention at any scale — typically a face or high-contrast graphic</td>
					<td>Too small, too centered, competing with text for visual weight</td>
				</tr>
				<tr>
					<td>Text zone</td>
					<td>Communicates the video's topic in 2–4 words at extreme weight</td>
					<td>Too many words, light weight, low contrast, placed over busy background</td>
				</tr>
				<tr>
					<td>Breathing zone</td>
					<td>Visual rest — prevents crowding, lets the eye move between zones</td>
					<td>
						Absent entirely (leads to visual noise) or too large (leaves composition feeling empty)
					</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══════════════════════════════
     SECTION 2: BANNER COMPOSITION
═══════════════════════════════ -->
	<section id="banner" class="section">
		<div class="section-header">
			<span class="section-num">07.02</span>
			<h2 class="section-title">Banner Composition &amp; Safe Zones</h2>
		</div>

		<p>
			The YouTube channel banner is 2560×1440 pixels — but it is never displayed at that size in a
			single context. YouTube crops and scales it differently depending on the device: the full
			width shows on TV screens; a narrow center strip shows on desktop; an even narrower strip on
			mobile. This creates a design problem that has no equivalent in print: the same image must
			work at three radically different aspect ratios simultaneously.
		</p>

		<p>
			The solution is the <strong>safe zone model</strong>. YouTube specifies a central 1546×423
			pixel zone that is visible on all devices, including mobile. Everything essential — brand
			name, tagline, logo mark — must fit within this zone. The regions outside the safe zone should
			contain visual content (pattern, background, extended graphic) that looks complete if cropped
			at any point. They must not contain information that would be missed if cropped.
		</p>

		<p>
			Compositionally, banners differ from thumbnails in a key way: they are
			<em>read at full size</em> on desktop and TV screens. Text can be smaller (relative to the canvas)
			and still legible. The primary purpose is brand communication and context-setting — a new visitor
			should understand within two seconds what this channel is about and whether it aligns with their
			interests.
		</p>

		<!-- DEMO 2: Banner Safe Zone Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Banner Safe Zone Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Toggle device overlays to see how the same banner is cropped on each platform. The safe
					zone (green) must contain all essential content. Toggle between banner styles to see
					different compositional approaches.
				</p>

				<div class="banner-safe-toggle" id="banner-toggle">
					<button
						class="btn active"
						onclick={(e) => actions.setBannerStyle('grid', e.currentTarget)}
					>
						Grid / Technical
					</button>
					<button class="btn" onclick={(e) => actions.setBannerStyle('editorial', e.currentTarget)}
						>Editorial</button
					>
					<button class="btn" onclick={(e) => actions.setBannerStyle('gradient', e.currentTarget)}
						>Gradient Field</button
					>
				</div>

				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button class="btn sky" id="safe-btn" onclick={(e) => actions.toggleSafeZone()}>
						Show Safe Zone
					</button>
					<button class="btn" id="device-btn" onclick={(e) => actions.cycleDevice()}
						>Show: All Devices</button
					>
				</div>

				<canvas
					id="banner-canvas"
					width="560"
					height="158"
					aria-label="Banner Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>

				<div class="banner-legend">
					<div class="banner-legend-item">
						<div class="banner-legend-dot" style="background: rgba(56, 192, 232, 0.6)"></div>
						<span style="font-size: 11px; color: var(--muted)">TV (full width)</span>
					</div>
					<div class="banner-legend-item">
						<div class="banner-legend-dot" style="background: rgba(155, 109, 255, 0.6)"></div>
						<span style="font-size: 11px; color: var(--muted)">Desktop crop</span>
					</div>
					<div class="banner-legend-item">
						<div class="banner-legend-dot" style="background: rgba(86, 208, 160, 0.6)"></div>
						<span style="font-size: 11px; color: var(--muted)">Safe zone (all devices)</span>
					</div>
					<div class="banner-legend-item">
						<div class="banner-legend-dot" style="background: rgba(232, 93, 138, 0.6)"></div>
						<span style="font-size: 11px; color: var(--muted)">Mobile crop</span>
					</div>
				</div>
				<div
					style="font-size: 12px; color: var(--muted); margin-top: 0.75rem; min-height: 1.4em"
					id="banner-device-note"
				></div>
			</div>
		</div>

		<div class="callout warn">
			<div class="callout-label">The Banner Design Trap</div>
			The most common banner failure: designing for the full 2560×1440 canvas as if every viewer will
			see it. Mobile viewers — typically 60–70% of a channel's audience — only see the central 1235×338
			pixel strip. Text placed in the wide left or right margins is invisible to the majority. Always
			design the safe zone first, and treat the surrounding area as decorative extension.
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 3: WEB LAYOUT
═══════════════════════════════ -->
	<section id="web-layout" class="section">
		<div class="section-header">
			<span class="section-num">07.03</span>
			<h2 class="section-title">Website Layout: Spacing Systems, Grids &amp; Rhythm</h2>
		</div>

		<p>
			Website layouts feel consistent and professional when all spacing decisions derive from a
			single base unit. This is called a <strong>spacing system</strong>. The base unit (typically
			4px, 8px, or a multiple of the body font size) multiplies into a scale: 4, 8, 12, 16, 24, 32,
			48, 64, 96. Every gap, padding value, margin, and section break is pulled from this scale — no
			arbitrary pixel values.
		</p>

		<p>
			The reason this works: when all spatial relationships are mathematically related, the eye
			perceives underlying order even without being able to articulate it. When spacing is arbitrary
			— when one gap is 13px and the next is 17px — the eye detects the inconsistency as low-grade
			visual noise. The layout feels amateurish without the viewer knowing why.
		</p>

		<p>
			<em>Typographic rhythm</em> is the vertical equivalent of a spacing system. It requires that all
			vertical text elements — headings, subheadings, body paragraphs, captions — snap to a common baseline
			grid. The grid unit is typically the body font's line height. When headings occupy the same vertical
			rhythm as body paragraphs (their line height is a multiple of the body baseline), the page feels
			composed rather than assembled from separate pieces.
		</p>

		<p>
			<strong>Column grids</strong> organize horizontal space. A twelve-column grid is the most common
			choice because twelve divides evenly into 2, 3, 4, and 6 columns — giving you flexible layout options
			without awkward fractions. Content columns typically span eight or ten of the twelve columns; navigation
			and sidebar content spans two or four. The gutters (gaps between columns) are fixed and pulled from
			the spacing system.
		</p>

		<div class="callout sage">
			<div class="callout-label">The Spacing System for This Course</div>
			This course uses a base unit of 4px, with a scale of 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64. Section
			padding is 64px. Card padding is 24px. Label spacing is 8px. The consistency you feel reading these
			modules is produced by pulling every spatial decision from the same scale — not by individual judgment
			calls.
		</div>

		<!-- DEMO 3: Web Layout Grid Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Web Layout Grid Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Adjust the spacing base unit, column count, and gutter size. The layout preview updates to
					show how the grid underlies the page structure. Toggle overlays to reveal the grid and
					baseline rhythm.
				</p>

				<div class="web-layout-wrap">
					<canvas
						id="web-canvas"
						width="560"
						height="420"
						aria-label="Web Canvas Demonstration"
						role="region"
						tabindex="0"
					></canvas>
				</div>

				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.75rem 0">
					<button
						class="btn violet"
						id="col-grid-btn"
						onclick={(e) => actions.toggleWebGrid('cols')}
					>
						Column Grid
					</button>
					<button class="btn" id="base-grid-btn" onclick={(e) => actions.toggleWebGrid('base')}>
						Baseline Grid
					</button>
					<button class="btn" id="zones-web-btn" onclick={(e) => actions.toggleWebGrid('zones')}>
						Content Zones
					</button>
				</div>

				<div class="web-controls">
					<div class="web-ctrl-group">
						<div class="web-ctrl-label">Base Unit</div>
						<div class="slider-row" style="margin: 0">
							<input
								type="range"
								id="web-unit"
								min="4"
								max="12"
								step="4"
								value="8"
								oninput={() => {
									actions.updateWebLayout();
								}}
							/>
							<span class="slider-val" id="web-unit-val">8px</span>
						</div>
					</div>
					<div class="web-ctrl-group">
						<div class="web-ctrl-label">Columns</div>
						<div class="slider-row" style="margin: 0">
							<input
								type="range"
								id="web-cols"
								min="4"
								max="12"
								step="4"
								value="12"
								oninput={() => {
									actions.updateWebLayout();
								}}
							/>
							<span class="slider-val" id="web-cols-val">12</span>
						</div>
					</div>
					<div class="web-ctrl-group">
						<div class="web-ctrl-label">Gutter</div>
						<div class="slider-row" style="margin: 0">
							<input
								type="range"
								id="web-gutter"
								min="8"
								max="32"
								step="8"
								value="16"
								oninput={() => {
									actions.updateWebLayout();
								}}
							/>
							<span class="slider-val" id="web-gutter-val">16px</span>
						</div>
					</div>
				</div>
				<div class="web-rhythm-display" id="web-rhythm-display"></div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Layout Element</th>
					<th>What It Controls</th>
					<th>Typical Values</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Base unit</td>
					<td>The smallest spacing increment — all values are multiples</td>
					<td>4px, 8px, or line-height × 0.25</td>
				</tr>
				<tr>
					<td>Column count</td>
					<td>Horizontal divisions available for content placement</td>
					<td>12 (flexible), 8 (simpler), 4 (mobile)</td>
				</tr>
				<tr>
					<td>Gutter</td>
					<td>Fixed gap between columns</td>
					<td>16–32px depending on content density</td>
				</tr>
				<tr>
					<td>Content max-width</td>
					<td>Maximum width of text columns for readability</td>
					<td>640–740px for body text; 960–1200px for full layout</td>
				</tr>
				<tr>
					<td>Section padding</td>
					<td>Vertical space between major content sections</td>
					<td>4–6× base unit (32–64px)</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══════════════════════════════
     SECTION 4: THUMBNAIL COMPARISON
═══════════════════════════════ -->
	<section id="comparison" class="section">
		<div class="section-header">
			<span class="section-num">07.04</span>
			<h2 class="section-title">Comparing Thumbnails: Effectiveness Analysis</h2>
		</div>

		<p>
			Thumbnail effectiveness is not a matter of personal taste. It is measurable against specific
			criteria: clarity of subject at thumbnail scale, legibility of title text, strength of the
			visual hierarchy, and presence of a clear call to curiosity. A thumbnail that scores well on
			all four criteria will consistently outperform one that fails on any of them, regardless of
			how polished the failed version looks at full size.
		</p>

		<p>
			When comparing two thumbnails, the evaluation framework is sequential: first determine which
			one you notice first when placed side-by-side (attention capture), then determine which
			conveys the topic faster (communication efficiency), then determine which makes you more
			curious about the content (curiosity gap). The winner on the first criterion has a structural
			advantage; the winner on all three is the stronger design.
		</p>

		<!-- DEMO 4: Thumbnail Comparison Tool -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Thumbnail Effectiveness Comparison</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Three thumbnail pairs — the same video topic with two different layouts. Click the
					thumbnail you think communicates more effectively, then read the structural analysis.
				</p>

				<div
					style="display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap"
					id="pair-selector"
				>
					<button class="btn active" onclick={(e) => actions.showPair(0, e.currentTarget)}
						>Pair A</button
					>
					<button class="btn" onclick={(e) => actions.showPair(1, e.currentTarget)}>Pair B</button>
					<button class="btn" onclick={(e) => actions.showPair(2, e.currentTarget)}>Pair C</button>
				</div>

				<div class="compare-pair" id="compare-pair">
					<div class="compare-item" id="cmp-left">
						<canvas
							id="cmp-left-canvas"
							width="240"
							height="135"
							aria-label="Cmp Left Canvas Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<div class="compare-item-label" id="cmp-left-label">Option A</div>
					</div>
					<div class="compare-item" id="cmp-right">
						<canvas
							id="cmp-right-canvas"
							width="240"
							height="135"
							aria-label="Cmp Right Canvas Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<div class="compare-item-label" id="cmp-right-label">Option B</div>
					</div>
				</div>

				<div class="compare-verdict" id="compare-verdict">
					Click a thumbnail above to evaluate it.
				</div>
			</div>
		</div>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">07.05</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout violet">
			<div class="callout-label">Exercise 1 — Three Thumbnail Variants</div>
			Using your brand identity from Module 6, produce three thumbnail variants for a single hypothetical
			video:<br /><br />
			· Variant A: Left-third subject, text right — classic structure<br />
			· Variant B: Full-bleed subject, text overlay with strong contrast<br />
			· Variant C: Text-dominant with minimal or no photography<br /><br />
			Scale each to 128×72px and evaluate them using the 10% rule. Document which elements survive the
			reduction and which collapse. The variant that scores best at 128px is your structural winner —
			regardless of which looks best at full size.
		</div>

		<div class="callout amber">
			<div class="callout-label">Exercise 2 — Website Header &amp; Homepage Structure</div>
			Design a website header and homepage visual structure for your channel. Requirements:<br /><br
			/>
			· Header must contain: logo mark, channel name, and one navigation element<br />
			· Hero section must answer "What is this?" in under three seconds<br />
			· All spacing values must come from a defined base unit (document it)<br />
			· Use a max-width of 960px for content, with consistent left/right margin<br /><br />
			Sketch or wireframe first — no colors, no images, just boxes and text placeholders arranged in a
			grid. The wireframe reveals structural problems that polish hides.
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 07 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> A thumbnail at 1280×720 has a title set at 18px with regular weight
				(400) in a medium-grey color. Why will this fail at thumbnail scale?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The font is too small at full resolution — thumbnails require at least 36px
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Grey text is never appropriate for thumbnails regardless of contrast
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. At 168×94px (thumbnail scale), 18px regular weight medium-grey becomes approximately
					2–3px of low-contrast pixels — completely invisible. Thumbnails require maximum weight
					(700–800) and extreme contrast (white on dark or dark on white)
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The aspect ratio is wrong — thumbnails should use portrait orientation for text
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> A creator designs their channel banner with the channel name placed
				near the left edge at 2560×1440 full size. What problem will most viewers encounter?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. On mobile devices — which account for the majority of YouTube views — the banner is
					cropped to a narrow central strip. Content placed near the outer edges is invisible to
					mobile viewers
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Left-edge placement creates poor visual balance — channel names should always be
					centered
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The text will be too small to read at the full banner resolution
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. YouTube automatically overlays channel statistics on the left third of banners,
					covering the text
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> Why do spacing systems (all values derived from a single base unit)
				produce more consistent layouts than arbitrary spacing decisions?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. They reduce file sizes because fewer unique values are stored
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Design tools automatically enforce spacing systems, preventing errors
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Spacing systems limit layout options, forcing simpler and cleaner designs
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Mathematically-related spacing values create underlying visual order that the eye
					perceives as coherent, even unconsciously — arbitrary values produce low-grade perceptual
					noise that makes layouts feel amateurish without the viewer knowing why
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> A twelve-column grid is preferred over a ten-column grid for most
				web layouts. What is the practical reason?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Twelve divides evenly into 2, 3, 4, and 6 columns — providing flexible layout options
					(half, thirds, quarters, sixths) without awkward fractions. Ten only divides evenly into 2
					and 5
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Twelve columns is the standard enforced by CSS grid specifications
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. More columns always produce more flexible layouts — twenty-four columns would be even
					better
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Twelve is the minimum number of columns required for responsive layouts to work
					correctly
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> When evaluating two thumbnails for effectiveness, what is the correct
				order of evaluation criteria?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Aesthetic quality → topic communication → curiosity generated
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Color harmony → type legibility → subject recognition
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Attention capture (which is noticed first) → communication efficiency (which conveys
					topic faster) → curiosity gap (which makes you want to click) — structural advantage
					compounds in this sequence
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Subject size → word count → contrast ratio — these are the only objective criteria
				</button>
			</div>
			<div class="feedback" id="fb-4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-num">—</div>
			<div class="score-label">questions correct out of 5</div>
		</div>
	</section>

	<!-- ASSESSMENT -->
	<section id="assessment" class="assessment-section">
		<div class="assessment-header">Module Assessment — Layout Diagnosis</div>
		<div class="assessment-sub">
			Examine each layout specimen and identify the structural problem.
		</div>
		<div class="assess-wrap" id="assess-wrap"></div>
	</section>

	<div class="nav-links">
		<a href="gd-module-06.html" class="prev-link">← Module 06: Brand Identity</a>
		<a href="gd-module-08.html" class="next-module" style="flex: 1; max-width: 420px">
			<div>
				<div class="next-label">Next — Module 08</div>
				<div class="next-title">Designing Story-Driven Visuals</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</div>
</div>

<!-- page-wrapper -->

<style>
	.page-wrapper {
		background: var(--bg);
		color: var(--text);
		font-family: 'IBM Plex Mono', monospace;
		font-size: 14px;
		line-height: 1.8;
	}

	.page-wrapper {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem 6rem;
	}

	.course-header {
		border-bottom: 1px solid var(--border);
		padding: 2rem 0 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.course-label {
		font-size: 11px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.course-title {
		font-family: 'Syne', sans-serif;
		font-size: 13px;
		color: var(--muted);
		font-weight: 400;
	}

	.module-hero {
		padding: 5rem 0 3.5rem;
		border-bottom: 1px solid var(--border);
		position: relative;
		overflow: hidden;
	}
	.module-number {
		font-family: 'Syne', sans-serif;
		font-size: clamp(80px, 15vw, 140px);
		font-weight: 800;
		line-height: 1;
		color: transparent;
		-webkit-text-stroke: 1px var(--border2);
		position: absolute;
		right: -10px;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
		user-select: none;
	}
	.module-tag {
		display: inline-block;
		font-size: 10px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--violet);
		border: 1px solid var(--violet);
		padding: 3px 10px;
		margin-bottom: 1.5rem;
	}
	.module-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(28px, 5vw, 48px);
		font-weight: 800;
		line-height: 1.1;
		color: #fff;
		max-width: 620px;
	}
	.module-title span {
		color: var(--violet);
	}

	.toc {
		margin: 3rem 0;
		padding: 1.5rem;
		border: 1px solid var(--border);
		background: var(--surface);
	}
	.toc-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 1rem;
	}
	.toc-list {
		list-style: none;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.toc-list a {
		font-size: 12px;
		color: var(--muted);
		text-decoration: none;
		border: 1px solid var(--border);
		padding: 4px 10px;
		transition: all 0.15s;
	}
	.toc-list a:hover {
		color: var(--violet);
		border-color: var(--violet);
	}

	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--violet);
		background: var(--surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--violet);
		margin-bottom: 1rem;
	}
	.objectives ul {
		list-style: none;
	}
	.objectives li {
		padding: 0.2rem 0;
		padding-left: 1.2rem;
		position: relative;
	}
	.objectives li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--rose);
	}

	.section {
		margin: 4rem 0;
	}
	.section-header {
		display: flex;
		align-items: baseline;
		gap: 1rem;
		margin-bottom: 2rem;
		padding-bottom: 0.75rem;
		border-bottom: 1px solid var(--border);
	}
	.section-num {
		font-size: 11px;
		color: var(--rose);
		letter-spacing: 0.1em;
		font-weight: 600;
	}
	.section-title {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		color: #fff;
	}

	p {
		margin-bottom: 1.2rem;
		color: var(--text);
	}
	p:last-child {
		margin-bottom: 0;
	}
	strong {
		color: var(--violet);
		font-weight: 600;
	}
	em {
		color: #fff;
		font-style: normal;
		font-weight: 500;
	}
	a {
		color: inherit;
		text-decoration: none;
	}
	:global(code) {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 1px 6px;
		font-size: 12px;
		color: var(--sky);
		font-family: 'IBM Plex Mono', monospace;
	}

	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
		font-size: 13px;
	}
	:global(.callout.amber) {
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
	}
	.callout.sage {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--surface));
	}
	:global(.callout.warn) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 5%, var(--surface));
	}
	:global(.callout.sky) {
		border-color: var(--sky);
		background: color-mix(in srgb, var(--sky) 5%, var(--surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--violet);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	:global(.callout.amber) .callout-label {
		color: var(--amber);
	}
	.callout.sage .callout-label {
		color: var(--sage);
	}
	:global(.callout.warn) .callout-label {
		color: var(--rose);
	}
	:global(.callout.sky) .callout-label {
		color: var(--sky);
	}

	.demo-box {
		background: var(--surface);
		border: 1px solid var(--border);
		margin: 2rem 0;
	}
	.demo-header {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--border);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.demo-header > span {
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--muted);
	}
	:global(.demo-badge) {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	:global(.demo-badge.interactive) {
		color: var(--violet);
		border-color: var(--violet);
		background: color-mix(in srgb, var(--violet) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	:global(.btn) {
		background: transparent;
		border: 1px solid var(--border2);
		color: var(--text);
		padding: 6px 16px;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s;
	}
	:global(.btn:hover) {
		border-color: var(--violet);
		color: var(--violet);
	}
	:global(.btn.active) {
		border-color: var(--violet);
		color: var(--violet);
		background: color-mix(in srgb, var(--violet) 10%, transparent);
	}
	:global(.btn.rose:hover) {
		border-color: var(--rose);
		color: var(--rose);
	}
	:global(.btn.rose.active) {
		border-color: var(--rose);
		color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
	}
	:global(.btn.sky:hover) {
		border-color: var(--sky);
		color: var(--sky);
	}
	:global(.btn.sky.active) {
		border-color: var(--sky);
		color: var(--sky);
		background: color-mix(in srgb, var(--sky) 10%, transparent);
	}
	:global(.btn.amber:hover) {
		border-color: var(--amber);
		color: var(--amber);
	}
	:global(.btn.amber.active) {
		border-color: var(--amber);
		color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	:global(.btn.sage:hover) {
		border-color: var(--sage);
		color: var(--sage);
	}
	:global(.btn.sage.active) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
	}

	:global(.slider-row) {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 0.5rem 0;
	}
	:global(.slider-row) label {
		font-size: 12px;
		min-width: 120px;
		color: var(--text);
	}
	:global(.slider-row) :global(input[type='range']) {
		flex: 1;
		-webkit-appearance: none;
		height: 3px;
		background: var(--border2);
		outline: none;
	}
	:global(.slider-row) :global(input[type='range']::-webkit-slider-thumb) {
		-webkit-appearance: none;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--violet);
		cursor: pointer;
	}
	:global(.slider-val) {
		font-size: 12px;
		color: var(--violet);
		min-width: 52px;
		text-align: right;
		font-weight: 600;
	}

	:global(.two-col) {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}
	@media (max-width: 640px) {
		:global(.two-col) {
			grid-template-columns: 1fr;
		}
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--raised);
		color: var(--violet);
		text-align: left;
		padding: 0.6rem 1rem;
		border: 1px solid var(--border);
		font-weight: 600;
		letter-spacing: 0.05em;
	}
	td {
		padding: 0.5rem 1rem;
		border: 1px solid var(--border);
		color: var(--text);
	}
	tr:nth-child(even) td {
		background: color-mix(in srgb, var(--raised) 50%, transparent);
	}

	.progress-bar-wrap {
		height: 3px;
		background: var(--border);
		width: 100%;
		margin: 2rem 0 0;
	}
	.progress-bar-fill {
		height: 100%;
		background: var(--violet);
		width: 0;
		transition: width 0.4s ease;
	}
	.divider {
		border: none;
		border-top: 1px solid var(--border);
		margin: 3rem 0;
	}

	.quiz-section {
		margin: 4rem 0;
		padding: 2rem;
		border: 1px solid var(--border);
		background: var(--surface);
	}
	.quiz-header {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-bottom: 0.5rem;
	}
	.quiz-sub {
		font-size: 12px;
		color: var(--muted);
		margin-bottom: 2rem;
	}
	:global(.question) {
		margin: 2rem 0;
	}
	:global(.q-text) {
		font-size: 13px;
		color: #fff;
		margin-bottom: 1rem;
	}
	:global(.q-num) {
		color: var(--violet);
		margin-right: 0.5rem;
	}
	:global(.options) {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	:global(.option) {
		padding: 0.6rem 1rem;
		border: 1px solid var(--border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		user-select: none;
		font-family: 'IBM Plex Mono', monospace;
	}
	:global(.option:hover) {
		border-color: var(--border2);
		background: var(--raised);
	}
	:global(.option.correct) {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
		color: var(--sage);
	}
	:global(.option.wrong) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
		color: var(--rose);
	}
	:global(.option.disabled) {
		pointer-events: none;
	}
	:global(.feedback) {
		font-size: 12px;
		margin-top: 0.75rem;
		min-height: 1.5em;
		color: var(--muted);
	}
	:global(.feedback.ok) {
		color: var(--sage);
	}
	:global(.feedback.bad) {
		color: var(--rose);
	}
	.quiz-score {
		margin-top: 2rem;
		padding: 1.5rem;
		border: 1px solid var(--border);
		text-align: center;
		display: none;
	}
	.score-num {
		font-family: 'Syne', sans-serif;
		font-size: 36px;
		font-weight: 800;
		color: var(--violet);
	}
	.score-label {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.25rem;
	}

	.assessment-section {
		margin: 4rem 0;
		padding: 2rem;
		border: 1px solid var(--border);
		background: var(--surface);
	}
	.assessment-header {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-bottom: 0.25rem;
	}
	.assessment-sub {
		font-size: 12px;
		color: var(--muted);
		margin-bottom: 1.5rem;
	}

	.nav-links {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: 4rem;
		flex-wrap: wrap;
		gap: 1rem;
	}
	:global(.prev-link) {
		font-size: 12px;
		color: var(--muted);
		text-decoration: none;
		border: 1px solid var(--border);
		padding: 0.75rem 1.25rem;
		transition: all 0.2s;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}
	:global(.prev-link:hover) {
		border-color: var(--violet);
		color: var(--violet);
	}
	.next-module {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem 2rem;
		border: 1px solid var(--border);
		text-decoration: none;
		transition: all 0.2s;
		background: var(--surface);
	}
	.next-module:hover {
		border-color: var(--sky);
	}
	.next-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.next-title {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-top: 0.25rem;
	}
	.next-arrow {
		font-size: 28px;
		color: var(--sky);
	}

	/* ══════════════════════════════════
   DEMO-SPECIFIC
══════════════════════════════════ */

	/* Thumbnail Layout Lab */
	#thumb-lab-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
	}
	.thumb-zone-btns {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-bottom: 1rem;
	}
	.zone-info {
		font-size: 12px;
		color: var(--muted);
		padding: 0.6rem 0.85rem;
		border: 1px solid var(--border);
		background: var(--code-bg);
		min-height: 52px;
		line-height: 1.6;
		margin-top: 0.75rem;
		transition: color 0.2s;
	}
	.thumb-scale-row {
		display: flex;
		gap: 0.75rem;
		align-items: flex-end;
		margin-top: 1rem;
		padding: 0.75rem;
		background: var(--code-bg);
		border: 1px solid var(--border);
	}
	.thumb-scale-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.3rem;
	}
	.thumb-scale-label {
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
	}

	/* Banner Builder */
	#banner-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
	}
	.banner-safe-toggle {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}
	.banner-legend {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		margin-top: 0.75rem;
		font-size: 11px;
	}
	.banner-legend-item {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}
	.banner-legend-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
	}

	/* Web Layout Builder */
	.web-layout-wrap {
		position: relative;
		overflow: hidden;
		border: 1px solid var(--border2);
		background: #080c12;
	}
	#web-canvas {
		display: block;
		width: 100%;
	}
	.web-controls {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 0.75rem;
		margin-top: 1rem;
	}
	@media (max-width: 560px) {
		.web-controls {
			grid-template-columns: 1fr;
		}
	}
	.web-ctrl-group {
		padding: 0.75rem;
		border: 1px solid var(--border);
		background: var(--raised);
	}
	.web-ctrl-label {
		font-size: 10px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.5rem;
	}
	.web-rhythm-display {
		margin-top: 0.75rem;
		font-size: 12px;
		color: var(--muted);
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--border);
		background: var(--code-bg);
		line-height: 1.6;
	}

	/* Thumb Comparison */
	.compare-pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}
	@media (max-width: 500px) {
		.compare-pair {
			grid-template-columns: 1fr;
		}
	}
	.compare-item {
		border: 2px solid var(--border);
	}
	:global(.compare-item.selected) {
		border-color: var(--violet);
	}
	.compare-item canvas {
		display: block;
		width: 100%;
	}
	.compare-item-label {
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		padding: 0.4rem 0.6rem;
		background: var(--raised);
		color: var(--muted);
		border-top: 1px solid var(--border);
	}
	.compare-verdict {
		margin-top: 1rem;
		padding: 0.75rem 1rem;
		border: 1px solid var(--border);
		font-size: 12px;
		color: var(--muted);
		min-height: 48px;
		line-height: 1.6;
	}

	/* Assessment */
	.assess-wrap {
		margin-top: 1.25rem;
	}
	:global(.assess-q) {
		margin: 1.5rem 0;
		border: 1px solid var(--border);
	}
	:global(.assess-q-header) {
		padding: 0.6rem 1rem;
		background: var(--raised);
		border-bottom: 1px solid var(--border);
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
	}
	:global(.assess-q-body) {
		padding: 1.25rem;
	}
	:global(.assess-canvas-wrap) {
		margin: 0.75rem 0;
		border: 1px solid var(--border2);
		overflow: hidden;
	}
	:global(.assess-canvas-wrap) canvas {
		display: block;
		max-width: 100%;
	}
	:global(.assess-q-text) {
		font-size: 13px;
		color: #fff;
		margin: 0.75rem 0;
	}
	:global(.assess-opts) {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
	:global(.assess-opt) {
		padding: 0.55rem 1rem;
		border: 1px solid var(--border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		user-select: none;
		font-family: 'IBM Plex Mono', monospace;
	}
	:global(.assess-opt:hover) {
		border-color: var(--border2);
		background: var(--raised);
	}
	:global(.assess-opt.correct) {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
		color: var(--sage);
		pointer-events: none;
	}
	:global(.assess-opt.wrong) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
		color: var(--rose);
		pointer-events: none;
	}
	:global(.assess-opt.disabled) {
		pointer-events: none;
	}
	:global(.assess-feedback) {
		font-size: 12px;
		margin-top: 0.5rem;
		min-height: 1.2em;
		color: var(--muted);
	}
	:global(.assess-feedback.ok) {
		color: var(--sage);
	}
	:global(.assess-feedback.bad) {
		color: var(--rose);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
