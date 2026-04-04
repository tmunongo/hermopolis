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
		/* ══════════════════════════════════
   READING PROGRESS
══════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width =
					(el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight)) * 100 + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		/* ══════════════════════════════════
   UTILITIES
══════════════════════════════════ */
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

		function arrow(ctx, x1, y1, x2, y2, col, aw = 8) {
			ctx.strokeStyle = col;
			ctx.fillStyle = col;
			ctx.lineWidth = 1.5;
			const angle = Math.atan2(y2 - y1, x2 - x1);
			ctx.beginPath();
			ctx.moveTo(x1, y1);
			ctx.lineTo(x2, y2);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(x2, y2);
			ctx.lineTo(x2 - aw * Math.cos(angle - 0.4), y2 - aw * Math.sin(angle - 0.4));
			ctx.lineTo(x2 - aw * Math.cos(angle + 0.4), y2 - aw * Math.sin(angle + 0.4));
			ctx.closePath();
			ctx.fill();
		}

		/* ══════════════════════════════════
   DEMO 1: VISUAL ANALOGY BUILDER
══════════════════════════════════ */
		const ANALOGIES = [
			{
				concept: 'Visual Hierarchy',
				source: 'Newspaper Front Page',
				thumb: (ctx, w, h) => {
					ctx.fillStyle = '#080c12';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = '#fff';
					ctx.font = `700 ${h * 0.26}px Syne,sans-serif`;
					ctx.textAlign = 'center';
					ctx.fillText('HEADLINE', w / 2, h * 0.34);
					ctx.fillStyle = 'rgba(245,166,35,0.8)';
					ctx.font = `500 ${h * 0.14}px Syne,sans-serif`;
					ctx.fillText('Subheading text here', w / 2, h * 0.56);
					ctx.fillStyle = 'rgba(208,219,232,0.4)';
					ctx.font = `400 ${h * 0.09}px IBM Plex Mono,monospace`;
					ctx.fillText('body body body body body', w / 2, h * 0.74);
					ctx.textAlign = 'left';
				},
				large: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const half = w / 2 - 20;
					// Newspaper side
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(20, 20, half, h - 40);
					ctx.fillStyle = '#fff';
					ctx.font = `700 18px Syne,sans-serif`;
					ctx.fillText('BREAKING: DESIGN WORKS', 30, 55);
					ctx.fillStyle = 'rgba(208,219,232,0.6)';
					ctx.font = `500 11px Syne,sans-serif`;
					ctx.fillText('Scientists confirm hierarchy improves recall', 30, 76);
					ctx.fillStyle = 'rgba(208,219,232,0.35)';
					ctx.font = `400 9px IBM Plex Mono,monospace`;
					[
						'A study published this week',
						'found that readers scan',
						'pages in a predictable',
						'order determined by visual',
						'weight and contrast…'
					].forEach((l, i) => ctx.fillText(l, 30, 95 + i * 12));
					// Labels on newspaper
					const labels = [
						['TIER 1', 30, 48, 'var(--amber)'],
						['TIER 2', 30, 70, 'var(--sky)'],
						['TIER 3', 30, 90, 'var(--sage)']
					];
					labels.forEach(([t, x, y, c]) => {
						ctx.fillStyle = c;
						ctx.font = '8px IBM Plex Mono,monospace';
						ctx.fillText('← ' + t, half - 58, y);
					});
					// Arrow connecting to concept
					ctx.strokeStyle = 'rgba(245,166,35,0.5)';
					ctx.lineWidth = 1;
					ctx.setLineDash([4, 4]);
					ctx.beginPath();
					ctx.moveTo(half + 20, h / 2 - 30);
					ctx.lineTo(w / 2 + 10, h / 2 - 30);
					ctx.stroke();
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(245,166,35,0.7)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('same structure', w / 2 + half / 4 + 10, h / 2 - 36);
					ctx.textAlign = 'left';
					// Concept side
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(w / 2 + 10, 20, half - 10, h - 40);
					ctx.fillStyle = '#fff';
					ctx.font = `800 24px Syne,sans-serif`;
					ctx.fillText('PRIMARY', w / 2 + 20, 60);
					ctx.fillStyle = 'rgba(245,166,35,0.8)';
					ctx.font = `600 15px Syne,sans-serif`;
					ctx.fillText('SECONDARY', w / 2 + 20, 85);
					ctx.fillStyle = 'rgba(208,219,232,0.4)';
					ctx.font = `400 10px IBM Plex Mono,monospace`;
					ctx.fillText('tertiary element', w / 2 + 20, 102);
					// Tier brackets
					const bx = w - 28;
					ctx.strokeStyle = 'rgba(245,166,35,0.5)';
					ctx.lineWidth = 1;
					[
						[52, 66, 'TIER 1', 'var(--amber)'],
						[78, 92, 'TIER 2', 'var(--sky)'],
						[95, 108, 'TIER 3', 'var(--sage)']
					].forEach(([y1, y2, lbl, c]) => {
						ctx.strokeStyle = c;
						ctx.beginPath();
						ctx.moveTo(bx, y1);
						ctx.lineTo(bx + 6, y1);
						ctx.lineTo(bx + 6, y2);
						ctx.lineTo(bx, y2);
						ctx.stroke();
						ctx.fillStyle = c;
						ctx.font = '7px IBM Plex Mono,monospace';
						ctx.fillText(lbl, bx + 8, (y1 + y2) / 2 + 3);
					});
				},
				explanation:
					'The newspaper front page maps directly onto visual hierarchy: the headline is the largest element (Tier 1 — primary), the subheading is smaller and secondary, and the body copy is smallest and tertiary. Your eye reads them in size order automatically. This is the same cognitive mechanism that operates in any designed composition — the newspaper just makes it visible because readers already understand it.'
			},
			{
				concept: 'Spacing Rhythm',
				source: 'Musical Meter',
				thumb: (ctx, w, h) => {
					ctx.fillStyle = '#080c12';
					ctx.fillRect(0, 0, w, h);
					// Staff lines
					ctx.strokeStyle = 'rgba(86,208,160,0.4)';
					ctx.lineWidth = 1;
					[0.28, 0.38, 0.48, 0.58, 0.68].forEach((y) => {
						ctx.beginPath();
						ctx.moveTo(8, h * y);
						ctx.lineTo(w - 8, h * y);
						ctx.stroke();
					});
					// Notes at consistent intervals
					const positions = [0.15, 0.32, 0.49, 0.66, 0.83];
					positions.forEach((x, i) => {
						ctx.fillStyle = 'rgba(86,208,160,0.9)';
						ctx.beginPath();
						ctx.ellipse(
							w * x,
							h * (0.38 + Math.sin(i * 1.2) * 0.12),
							w * 0.05,
							h * 0.065,
							0.3,
							0,
							Math.PI * 2
						);
						ctx.fill();
					});
					ctx.fillStyle = 'rgba(86,208,160,0.5)';
					ctx.font = `400 ${h * 0.1}px IBM Plex Mono,monospace`;
					ctx.textAlign = 'center';
					ctx.fillText('consistent intervals', w / 2, h * 0.9);
					ctx.textAlign = 'left';
				},
				large: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const mid = w / 2;
					// Music side
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(16, 16, mid - 28, h - 32);
					ctx.strokeStyle = 'rgba(86,208,160,0.35)';
					ctx.lineWidth = 1;
					[0.35, 0.45, 0.55, 0.65, 0.75].forEach((y) => {
						ctx.beginPath();
						ctx.moveTo(24, h * y);
						ctx.lineTo(mid - 20, h * y);
						ctx.stroke();
					});
					// Consistent notes
					const xPositions = [0.08, 0.18, 0.28, 0.38, 0.48];
					xPositions.forEach((xr, i) => {
						ctx.fillStyle = 'rgba(86,208,160,0.85)';
						ctx.beginPath();
						ctx.ellipse(xr * w, h * (0.5 + Math.sin(i) * 0.08), 10, 13, 0.3, 0, Math.PI * 2);
						ctx.fill();
						ctx.strokeStyle = 'rgba(86,208,160,0.35)';
						ctx.lineWidth = 1;
						ctx.beginPath();
						ctx.moveTo(xr * w + 9, h * (0.5 + Math.sin(i) * 0.08));
						ctx.lineTo(xr * w + 9, h * 0.3);
						ctx.stroke();
						// interval marker
						if (i < xPositions.length - 1) {
							const nx = xPositions[i + 1] * w;
							ctx.fillStyle = 'rgba(86,208,160,0.4)';
							ctx.font = '8px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('↔ 8px', (xr * w + nx) / 2, h * 0.88);
						}
					});
					ctx.fillStyle = 'rgba(86,208,160,0.6)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('regular beat', (mid - 28) / 2 + 16, h * 0.97);
					ctx.textAlign = 'left';
					// Label
					ctx.fillStyle = 'rgba(86,208,160,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('MUSIC — CONSISTENT INTERVAL', 24, 30);
					// Arrow
					ctx.strokeStyle = 'rgba(245,166,35,0.4)';
					ctx.lineWidth = 1;
					ctx.setLineDash([4, 4]);
					ctx.beginPath();
					ctx.moveTo(mid - 10, h / 2);
					ctx.lineTo(mid + 10, h / 2);
					ctx.stroke();
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(245,166,35,0.7)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('maps to', mid, h / 2 - 5);
					ctx.textAlign = 'left';
					// Layout side
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(mid + 12, 16, mid - 28, h - 32);
					// Consistent spacing blocks
					const unit = 8;
					const blocks = [
						{ y: 0.22, h: 0.08, w: 0.7, label: 'Heading' },
						{ y: 0.36, h: 0.05, w: 0.9, label: 'Subheading' },
						{ y: 0.46, h: 0.04, w: 0.85, label: 'Body line' },
						{ y: 0.54, h: 0.04, w: 0.75, label: 'Body line' },
						{ y: 0.64, h: 0.035, w: 0.6, label: 'Caption' }
					];
					blocks.forEach((b, i) => {
						const bx = mid + 20,
							by = h * b.y,
							bw = (mid - 40) * b.w,
							bh = h * b.h;
						const col =
							i === 0
								? 'rgba(245,166,35,0.7)'
								: i === 1
									? 'rgba(208,219,232,0.5)'
									: 'rgba(208,219,232,0.25)';
						ctx.fillStyle = col;
						ctx.fillRect(bx, by, bw, bh);
						// Gap markers
						if (i < blocks.length - 1) {
							const nextY = h * blocks[i + 1].y;
							ctx.strokeStyle = 'rgba(245,166,35,0.3)';
							ctx.lineWidth = 1;
							ctx.beginPath();
							ctx.moveTo(bx + bw + 4, by + bh);
							ctx.lineTo(bx + bw + 4, nextY);
							ctx.stroke();
							ctx.fillStyle = 'rgba(245,166,35,0.5)';
							ctx.font = '7px IBM Plex Mono,monospace';
							ctx.textAlign = 'right';
							ctx.fillText(i < 2 ? '16px' : '8px', bx + bw + 2, (by + bh + nextY) / 2 + 3);
						}
					});
					ctx.textAlign = 'left';
					ctx.fillStyle = 'rgba(245,166,35,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('LAYOUT — CONSISTENT SPACING', mid + 20, 30);
				},
				explanation:
					'Musical meter uses consistent intervals between beats to create rhythm — and the listener perceives it as organised even before consciously processing the pattern. Spacing systems work identically: when all gaps are multiples of a base unit, the eye perceives underlying order. Arbitrary gaps produce the visual equivalent of a drummer who cannot keep time — technically present but perceptually disorienting.'
			},
			{
				concept: 'Brand Identity Invariants',
				source: 'Military Uniform',
				thumb: (ctx, w, h) => {
					ctx.fillStyle = '#08100c';
					ctx.fillRect(0, 0, w, h);
					// Three figures with same uniform colour but different positions
					[
						[0.22, 0.45],
						[0.5, 0.42],
						[0.78, 0.48]
					].forEach(([x, y], i) => {
						ctx.fillStyle = 'rgba(86,208,160,0.7)';
						ctx.beginPath();
						ctx.ellipse(w * x, h * (y - 0.15), w * 0.07, h * 0.1, 0, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = 'rgba(56,160,86,0.5)';
						roundRect(ctx, w * x - w * 0.08, h * y, w * 0.16, h * 0.28, 4);
						ctx.fill();
					});
					ctx.fillStyle = 'rgba(86,208,160,0.5)';
					ctx.font = `9px IBM Plex Mono,monospace`;
					ctx.textAlign = 'center';
					ctx.fillText('same uniform = recognition', w / 2, h * 0.92);
					ctx.textAlign = 'left';
				},
				large: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					// Three brand instances — different content, same invariants
					const w3 = (w - 60) / 3,
						pad = 16;
					const INVARIANTS_COL = '#38c0e8',
						VAR_COL = 'rgba(208,219,232,0.5)';
					['Thumbnail', 'Website Header', 'Social Post'].forEach((label, i) => {
						const ox = 20 + i * (w3 + 10);
						ctx.fillStyle = '#0d1520';
						ctx.fillRect(ox, 24, w3, h - 40);
						// Invariant: accent color bar
						ctx.fillStyle = INVARIANTS_COL;
						ctx.fillRect(ox, 24, 3, h - 40);
						// Invariant: logo mark (circle + dot)
						ctx.strokeStyle = INVARIANTS_COL;
						ctx.lineWidth = 1.5;
						ctx.beginPath();
						ctx.arc(ox + 18, 40, 10, 0, Math.PI * 2);
						ctx.stroke();
						ctx.fillStyle = INVARIANTS_COL;
						ctx.beginPath();
						ctx.arc(ox + 18, 40, 3, 0, Math.PI * 2);
						ctx.fill();
						// Invariant: type
						ctx.fillStyle = '#fff';
						ctx.font = `700 ${w3 * 0.14}px Syne,sans-serif`;
						ctx.fillText('SIG', ox + 32, 46);
						// Variable content
						if (i === 0) {
							ctx.fillStyle = '#1a2840';
							ctx.fillRect(ox + 8, 62, w3 - 16, h * 0.38);
							ctx.fillStyle = VAR_COL;
							ctx.font = `600 ${w3 * 0.12}px Syne,sans-serif`;
							ctx.fillText('EP 12', ox + 16, 90);
							ctx.fillText('DESIGN', ox + 16, 108);
						} else if (i === 1) {
							['Learn', 'About', 'Blog'].forEach((t, j) => {
								ctx.fillStyle = j === 0 ? INVARIANTS_COL : VAR_COL;
								ctx.font = '9px IBM Plex Mono,monospace';
								ctx.fillText(t, ox + 8 + j * 38, 66);
							});
							ctx.fillStyle = 'rgba(255,255,255,0.15)';
							ctx.fillRect(ox + 8, 78, w3 - 16, h * 0.38);
							ctx.fillStyle = '#fff';
							ctx.font = `700 ${w3 * 0.11}px Syne,sans-serif`;
							ctx.fillText('Design with', ox + 16, 100);
							ctx.fillText('Intention', ox + 16, 116);
						} else {
							ctx.fillStyle = 'rgba(255,255,255,0.1)';
							ctx.fillRect(ox + 8, 62, w3 - 16, h * 0.32);
							ctx.fillStyle = INVARIANTS_COL;
							ctx.font = `9px IBM Plex Mono,monospace`;
							ctx.fillText('NEW POST', ox + 16, 98);
							ctx.fillStyle = VAR_COL;
							ctx.font = `600 ${w3 * 0.1}px Syne,sans-serif`;
							ctx.fillText('Colour', ox + 16, 112);
							ctx.fillText('Theory', ox + 16, 124);
						}
						// Label
						ctx.fillStyle = 'rgba(255,255,255,0.35)';
						ctx.font = '8px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText(label, ox + w3 / 2, h - 10);
						ctx.textAlign = 'left';
						// Mark invariants
						if (i === 2) {
							ctx.strokeStyle = 'rgba(56,192,232,0.4)';
							ctx.lineWidth = 1;
							ctx.setLineDash([3, 3]);
							ctx.strokeRect(ox + 1, 25, 2, h - 42);
							ctx.strokeRect(ox + 8, 30, 24, 24);
							ctx.setLineDash([]);
						}
					});
					ctx.fillStyle = 'rgba(56,192,232,0.6)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('← same accent · same mark · same typeface on every surface →', 20, 18);
				},
				explanation:
					'A military uniform illustrates brand invariants perfectly. Every soldier wears the same uniform (invariants: colour, insignia, structure) but is a different person (variables: face, build, expression). Together, uniform + person = recognisable unit. A brand works identically: accent colour, logo mark, and typeface are the uniform. The content of each asset is the person. The viewer recognises the unit — the brand — across any context.'
			},
			{
				concept: 'Completeness Bias in Diagrams',
				source: 'Restaurant Menu',
				thumb: (ctx, w, h) => {
					ctx.fillStyle = '#080c12';
					ctx.fillRect(0, 0, w, h);
					// Cluttered menu vs clean menu
					// Cluttered left
					ctx.fillStyle = '#0e1520';
					ctx.fillRect(4, 4, w / 2 - 8, h - 8);
					ctx.fillStyle = 'rgba(200,210,220,0.35)';
					ctx.font = `7px IBM Plex Mono,monospace`;
					const items = [
						'Burger $12',
						'Salad $9',
						'Pasta $14',
						'Fish $18',
						'Soup $7',
						'Steak $28',
						'Wrap $10',
						'Bowl $11',
						'Sandwich $9',
						'Wings $13',
						'Pizza $16',
						'Tacos $11'
					];
					items.forEach((it, i) => ctx.fillText(it, 8, 18 + i * 14));
					ctx.fillStyle = 'rgba(232,93,138,0.6)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('12 items = paralysis', w / 4, h - 6);
					// Clean right
					ctx.fillStyle = '#0e1520';
					ctx.fillRect(w / 2 + 4, 4, w / 2 - 8, h - 8);
					ctx.fillStyle = 'rgba(245,166,35,0.8)';
					ctx.font = `600 ${h * 0.12}px IBM Plex Mono,monospace`;
					['BURGER', 'SALAD', 'PASTA'].forEach((it, i) => ctx.fillText(it, w / 2 + 8, 28 + i * 28));
					ctx.fillStyle = 'rgba(86,208,160,0.6)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('3 items = decision', w * 0.75, h - 6);
					ctx.textAlign = 'left';
				},
				large: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const half = w / 2 - 16;
					// Overcomplete diagram left
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(16, 16, half, h - 32);
					ctx.fillStyle = 'rgba(208,219,232,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('VISUAL HIERARCHY — COMPLETE', 24, 32);
					// Too many nodes
					const nodes = [
						{ x: 0.28, y: 0.25, r: 22, label: 'SIZE', col: 'rgba(245,166,35,0.6)' },
						{ x: 0.15, y: 0.55, r: 14, label: 'WEIGHT', col: 'rgba(56,192,232,0.5)' },
						{ x: 0.28, y: 0.72, r: 14, label: 'CONTRAST', col: 'rgba(155,109,255,0.5)' },
						{ x: 0.42, y: 0.52, r: 12, label: 'COLOUR', col: 'rgba(86,208,160,0.45)' },
						{ x: 0.35, y: 0.35, r: 10, label: 'SPACING', col: 'rgba(232,93,138,0.4)' },
						{ x: 0.22, y: 0.4, r: 9, label: 'ISOLATION', col: 'rgba(208,219,232,0.35)' },
						{ x: 0.4, y: 0.68, r: 9, label: 'POSITION', col: 'rgba(245,166,35,0.35)' }
					];
					nodes.forEach((n) => {
						ctx.fillStyle = n.col;
						ctx.beginPath();
						ctx.arc(n.x * w, n.y * h, n.r, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = 'rgba(255,255,255,0.7)';
						ctx.font = '7px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText(n.label, n.x * w, n.y * h + 3);
						ctx.textAlign = 'left';
					});
					// Connections everywhere
					ctx.strokeStyle = 'rgba(255,255,255,0.1)';
					ctx.lineWidth = 1;
					for (let i = 0; i < nodes.length; i++)
						for (let j = i + 1; j < nodes.length; j++) {
							ctx.beginPath();
							ctx.moveTo(nodes[i].x * w, nodes[i].y * h);
							ctx.lineTo(nodes[j].x * w, nodes[j].y * h);
							ctx.stroke();
						}
					ctx.fillStyle = 'rgba(232,93,138,0.7)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('7 nodes · 21 connections · confused', half / 2 + 16, h - 18);
					ctx.textAlign = 'left';

					// Arrow
					ctx.strokeStyle = 'rgba(245,166,35,0.4)';
					ctx.lineWidth = 1;
					ctx.setLineDash([4, 4]);
					ctx.beginPath();
					ctx.moveTo(half + 16, h / 2);
					ctx.lineTo(half + 32, h / 2);
					ctx.stroke();
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(245,166,35,0.7)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('reduce', half + 24, h / 2 - 4);
					ctx.textAlign = 'left';

					// Reduced diagram right
					const rx = half + 36;
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(rx, 16, half, h - 32);
					ctx.fillStyle = 'rgba(208,219,232,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('VISUAL HIERARCHY — ESSENTIAL', rx + 8, 32);
					const rn = [
						{
							x: rx + half * 0.5,
							y: h * 0.32,
							r: 28,
							label: 'SIZE',
							col: 'rgba(245,166,35,0.8)'
						},
						{
							x: rx + half * 0.3,
							y: h * 0.62,
							r: 18,
							label: 'WEIGHT',
							col: 'rgba(56,192,232,0.6)'
						},
						{
							x: rx + half * 0.7,
							y: h * 0.62,
							r: 18,
							label: 'CONTRAST',
							col: 'rgba(155,109,255,0.6)'
						}
					];
					rn.forEach((n) => {
						ctx.fillStyle = n.col;
						ctx.beginPath();
						ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = '#fff';
						ctx.font = `600 8px IBM Plex Mono,monospace`;
						ctx.textAlign = 'center';
						ctx.fillText(n.label, n.x, n.y + 3);
						ctx.textAlign = 'left';
					});
					ctx.strokeStyle = 'rgba(245,166,35,0.4)';
					ctx.lineWidth = 1.5;
					arrow(ctx, rn[0].x, rn[0].y + 28, rn[1].x, rn[1].y - 18, 'rgba(245,166,35,0.5)');
					arrow(ctx, rn[0].x, rn[0].y + 28, rn[2].x, rn[2].y - 18, 'rgba(245,166,35,0.5)');
					ctx.fillStyle = 'rgba(86,208,160,0.7)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('3 nodes · 2 connections · clear', rx + half / 2, h - 18);
					ctx.textAlign = 'left';
				},
				explanation:
					'A restaurant menu with 40 items causes decision paralysis — the cognitive load of evaluating every option prevents any decision from forming. A menu with 5 curated items communicates confidence and makes choosing easy. Diagrams fail identically: every additional node or connection requires processing attention. Strip to the three relationships that carry the most explanatory weight, and the concept becomes learnable.'
			},
			{
				concept: 'Sequential Information Flow',
				source: 'Film Screenplay',
				thumb: (ctx, w, h) => {
					ctx.fillStyle = '#080c12';
					ctx.fillRect(0, 0, w, h);
					// Three film frames in sequence
					[
						[0.12, 0.35],
						[0.46, 0.35],
						[0.8, 0.35]
					].forEach(([x, y], i) => {
						const fw = w * 0.28,
							fh = h * 0.38;
						ctx.fillStyle = '#0d1a2a';
						roundRect(ctx, w * x - fw / 2, h * y - fh / 2, fw, fh, 3);
						ctx.fill();
						ctx.strokeStyle = i === 2 ? 'rgba(245,166,35,0.7)' : 'rgba(56,192,232,0.4)';
						ctx.lineWidth = 1;
						ctx.beginPath();
						ctx.arc(w * x, h * y, fh * 0.25, 0, Math.PI * 2);
						ctx.stroke();
						if (i < 2) {
							arrow(
								ctx,
								w * x + fw / 2 + 2,
								h * y,
								w * (x + 0.34) - fw / 2 - 2,
								h * y,
								'rgba(56,192,232,0.4)'
							);
						}
						ctx.fillStyle = 'rgba(255,255,255,0.4)';
						ctx.font = '7px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText('Frame ' + (i + 1), w * x, h * y + fh * 0.36);
						ctx.textAlign = 'left';
					});
				},
				large: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					// Five frames: setup → introduce A → introduce B → combine → conclusion
					const fw = (w - 60) / 5,
						fh = h * 0.55,
						fy = (h - fh) / 2;
					const LABELS = ['SETUP', 'ADD A', 'ADD B', 'COMBINE', 'CONCLUSION'];
					const COLS = [
						'rgba(208,219,232,0.3)',
						'rgba(56,192,232,0.5)',
						'rgba(155,109,255,0.5)',
						'rgba(245,166,35,0.7)',
						'rgba(86,208,160,0.7)'
					];
					LABELS.forEach((label, i) => {
						const fx = 16 + i * (fw + 8);
						ctx.fillStyle = '#0d1520';
						roundRect(ctx, fx, fy, fw, fh, 4);
						ctx.fill();
						// Frame content
						if (i === 0) {
							ctx.fillStyle = 'rgba(208,219,232,0.15)';
							ctx.fillRect(fx + 8, fy + 12, fw - 16, fh - 24);
							ctx.fillStyle = 'rgba(255,255,255,0.3)';
							ctx.font = '8px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('context', fx + fw / 2, fy + fh / 2 + 4);
						} else if (i === 1) {
							ctx.fillStyle = 'rgba(208,219,232,0.1)';
							ctx.fillRect(fx + 8, fy + 12, fw - 16, fh - 24);
							ctx.fillStyle = COLS[1];
							ctx.beginPath();
							ctx.arc(fx + fw / 2, fy + fh * 0.4, 12, 0, Math.PI * 2);
							ctx.fill();
							ctx.fillStyle = 'rgba(255,255,255,0.6)';
							ctx.font = '7px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('element A', fx + fw / 2, fy + fh * 0.7);
						} else if (i === 2) {
							ctx.fillStyle = 'rgba(208,219,232,0.1)';
							ctx.fillRect(fx + 8, fy + 12, fw - 16, fh - 24);
							ctx.fillStyle = COLS[1];
							ctx.beginPath();
							ctx.arc(fx + fw / 2 - 10, fy + fh * 0.4, 10, 0, Math.PI * 2);
							ctx.fill();
							ctx.fillStyle = COLS[2];
							ctx.beginPath();
							ctx.arc(fx + fw / 2 + 10, fy + fh * 0.4, 10, 0, Math.PI * 2);
							ctx.fill();
							ctx.fillStyle = 'rgba(255,255,255,0.6)';
							ctx.font = '7px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('A + B added', fx + fw / 2, fy + fh * 0.7);
						} else if (i === 3) {
							ctx.fillStyle = 'rgba(245,166,35,0.15)';
							ctx.fillRect(fx + 8, fy + 12, fw - 16, fh - 24);
							ctx.fillStyle = COLS[3];
							ctx.beginPath();
							ctx.arc(fx + fw / 2, fy + fh * 0.4, 16, 0, Math.PI * 2);
							ctx.fill();
							ctx.fillStyle = 'rgba(0,0,0,0.7)';
							ctx.font = '7px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('A+B', fx + fw / 2, fy + fh * 0.42);
							ctx.fillText('combined', fx + fw / 2, fy + fh * 0.55);
						} else {
							ctx.fillStyle = 'rgba(86,208,160,0.12)';
							ctx.fillRect(fx + 8, fy + 12, fw - 16, fh - 24);
							ctx.fillStyle = COLS[4];
							ctx.font = `700 9px Syne,sans-serif`;
							ctx.textAlign = 'center';
							ctx.fillText('THE POINT:', fx + fw / 2, fy + fh * 0.38);
							ctx.fillStyle = 'rgba(255,255,255,0.7)';
							ctx.font = '8px IBM Plex Mono,monospace';
							ctx.fillText('A causes B', fx + fw / 2, fy + fh * 0.55);
						}
						ctx.textAlign = 'left';
						// Label
						ctx.fillStyle = COLS[i];
						ctx.font = '8px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText(label, fx + fw / 2, fy + fh + 16);
						ctx.textAlign = 'left';
						// Arrow to next
						if (i < LABELS.length - 1) {
							arrow(
								ctx,
								fx + fw + 2,
								fy + fh / 2,
								fx + fw + 6,
								fy + fh / 2,
								'rgba(245,166,35,0.4)'
							);
						}
					});
					// One idea per frame annotation
					ctx.fillStyle = 'rgba(245,166,35,0.5)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('← one new element introduced per frame →', w / 2, h - 12);
					ctx.textAlign = 'left';
				},
				explanation:
					'A screenplay structures information identically to a diagram sequence: establish context first, introduce characters and stakes one at a time, build complexity only after foundations are laid, then resolve. The viewer cannot understand act three without act one. Every educational sequence follows the same logic — the conclusion is meaningless without the setup, and the setup must be shown before any building begins.'
			},
			{
				concept: 'Visual Alignment',
				source: 'Sheet Music Staff',
				thumb: (ctx, w, h) => {
					ctx.fillStyle = '#080c12';
					ctx.fillRect(0, 0, w, h);
					ctx.strokeStyle = 'rgba(56,192,232,0.4)';
					ctx.lineWidth = 1;
					[0.3, 0.42, 0.54, 0.66, 0.78].forEach((y) => {
						ctx.beginPath();
						ctx.moveTo(10, h * y);
						ctx.lineTo(w - 10, h * y);
						ctx.stroke();
					});
					[
						[0.18, 0.36],
						[0.35, 0.54],
						[0.52, 0.42],
						[0.68, 0.3],
						[0.84, 0.66]
					].forEach(([x, y]) => {
						ctx.fillStyle = 'rgba(56,192,232,0.8)';
						ctx.beginPath();
						ctx.ellipse(w * x, h * y, w * 0.045, h * 0.06, 0.2, 0, Math.PI * 2);
						ctx.fill();
					});
					ctx.fillStyle = 'rgba(56,192,232,0.4)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('invisible lines create visible order', w / 2, h * 0.93);
					ctx.textAlign = 'left';
				},
				large: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const half = w / 2 - 16;
					// Staff/music left
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(16, 16, half, h - 32);
					ctx.strokeStyle = 'rgba(56,192,232,0.3)';
					ctx.lineWidth = 1;
					[0.3, 0.4, 0.5, 0.6, 0.7].forEach((y) => {
						ctx.beginPath();
						ctx.moveTo(24, h * y);
						ctx.lineTo(half + 8, h * y);
						ctx.stroke();
					});
					[
						[0.12, 0.35],
						[0.25, 0.55],
						[0.38, 0.45],
						[0.52, 0.3],
						[0.66, 0.6]
					].forEach(([xr, yr]) => {
						ctx.fillStyle = 'rgba(56,192,232,0.8)';
						ctx.beginPath();
						ctx.ellipse(16 + xr * half, h * yr, 10, 13, 0.2, 0, Math.PI * 2);
						ctx.fill();
						ctx.strokeStyle = 'rgba(56,192,232,0.35)';
						ctx.lineWidth = 1;
						ctx.beginPath();
						ctx.moveTo(16 + xr * half + 9, h * yr);
						ctx.lineTo(16 + xr * half + 9, h * (yr - 0.18));
						ctx.stroke();
					});
					ctx.fillStyle = 'rgba(56,192,232,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('staff lines = invisible constraint', half / 2 + 16, h - 18);
					ctx.textAlign = 'left';
					ctx.fillStyle = 'rgba(56,192,232,0.3)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('MUSIC STAFF', 24, 30);
					// Divider
					ctx.strokeStyle = 'rgba(245,166,35,0.3)';
					ctx.lineWidth = 1;
					ctx.setLineDash([4, 4]);
					ctx.beginPath();
					ctx.moveTo(half + 16, h / 2);
					ctx.lineTo(half + 32, h / 2);
					ctx.stroke();
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(245,166,35,0.6)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('same', half + 24, h / 2 - 4);
					ctx.textAlign = 'left';
					// Alignment grid right
					const rx = half + 36;
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(rx, 16, half, h - 32);
					ctx.strokeStyle = 'rgba(56,192,232,0.15)';
					ctx.lineWidth = 1;
					const leftAxis = rx + 24;
					ctx.beginPath();
					ctx.moveTo(leftAxis, 28);
					ctx.lineTo(leftAxis, h - 28);
					ctx.stroke();
					// Elements aligned to left axis
					const items = [
						{ y: 0.22, w: 0.55, h: 0.06, col: 'rgba(255,255,255,0.8)', label: 'Heading' },
						{ y: 0.33, w: 0.8, h: 0.04, col: 'rgba(208,219,232,0.5)', label: 'Subheading' },
						{ y: 0.41, w: 0.75, h: 0.035, col: 'rgba(208,219,232,0.3)', label: 'Body text' },
						{ y: 0.49, w: 0.68, h: 0.035, col: 'rgba(208,219,232,0.3)', label: '' },
						{ y: 0.58, w: 0.45, h: 0.04, col: 'rgba(56,192,232,0.6)', label: 'CTA button' }
					];
					items.forEach((item) => {
						const ix = leftAxis,
							iy = h * item.y,
							iw = (half - 30) * item.w,
							ih = h * item.h;
						ctx.fillStyle = item.col;
						ctx.fillRect(ix, iy, iw, ih);
						if (item.label) {
							ctx.fillStyle = 'rgba(245,166,35,0.5)';
							ctx.font = '7px IBM Plex Mono,monospace';
							ctx.fillText('← ' + item.label, ix + iw + 4, iy + ih / 2 + 3);
						}
					});
					ctx.fillStyle = 'rgba(56,192,232,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('invisible left edge = visible order', rx + half / 2, h - 18);
					ctx.textAlign = 'left';
					ctx.fillStyle = 'rgba(56,192,232,0.3)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('ALIGNMENT GRID', rx + 8, 30);
				},
				explanation:
					'Sheet music places notes on a five-line staff — the lines are invisible constraints that define a scale of positions. The notes themselves vary freely, but because they snap to the staff positions, the reader can decode their pitch and rhythm at a glance. An alignment grid works identically: invisible column lines constrain element placement, and because all elements share the same edges, the eye perceives order without seeing the grid that produces it.'
			}
		];

		let selectedAnalogy = null;

		function buildAnalogies() {
			const grid = document.getElementById('analogy-grid');
			ANALOGIES.forEach((a, i) => {
				const card = document.createElement('div');
				card.className = 'analogy-card';
				const cvs = document.createElement('canvas');
				cvs.width = 160;
				cvs.height = 100;
				const lbl = document.createElement('div');
				lbl.className = 'analogy-card-label';
				lbl.textContent = a.concept;
				card.appendChild(cvs);
				card.appendChild(lbl);
				grid.appendChild(card);
				const ctx = cvs.getContext('2d');
				a.thumb(ctx, 160, 100);
				card.addEventListener('click', () => {
					document.querySelectorAll('.analogy-card').forEach((c) => c.classList.remove('selected'));
					if (selectedAnalogy === i) {
						selectedAnalogy = null;
						document.getElementById('analogy-reveal').style.display = 'none';
					} else {
						selectedAnalogy = i;
						card.classList.add('selected');
						showAnalogy(i);
					}
				});
			});
		}

		function showAnalogy(i) {
			const a = ANALOGIES[i];
			const reveal = document.getElementById('analogy-reveal');
			reveal.style.display = 'block';
			document.getElementById('analogy-concept-label').textContent =
				`Concept: ${a.concept}  ·  Analogy Source: ${a.source}`;
			const largeCvs = document.getElementById('analogy-large-canvas');
			const ctx = largeCvs.getContext('2d');
			a.large(ctx, largeCvs.width, largeCvs.height);
			document.getElementById('analogy-explanation').textContent = a.explanation;
			reveal.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
		}

		buildAnalogies();

		/* ══════════════════════════════════
   DEMO 2: SEQUENCE FLOW BUILDER
══════════════════════════════════ */
		const seqCvs = document.getElementById('seq-canvas');
		const sCtx = seqCvs.getContext('2d');
		const SW = seqCvs.width,
			SH = seqCvs.height;

		let seqMode = 'additive';
		let seqStep = 0;

		const SEQ_MODES = {
			additive: {
				stages: [
					'Context',
					'Add: Colors',
					'Add: Type',
					'Add: Shapes',
					'Add: Spacing',
					'Complete System'
				],
				info: [
					'Frame 1 — Context only: an empty canvas with a "Design System" label. No elements yet. The viewer understands what they are about to see.',
					"Frame 2 — One element added: the color palette. Nothing else changes. The viewer's full attention goes to understanding the role of color.",
					"Frame 3 — One element added: typography. The previous element (colors) is slightly dimmed to signal it's established. Focus is on type.",
					'Frame 4 — One element added: shape register. The accumulated layers begin to suggest a coherent system. Still one new thing at a time.',
					'Frame 5 — One element added: spacing rules. The viewer can now see how the four elements interact — the spacing defines the relationships.',
					'Frame 6 — The complete picture. All five elements visible at full weight. The conclusion lands because the viewer was walked through each component.'
				],
				draw: (ctx, w, h, step) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(255,255,255,0.15)';
					ctx.font = '10px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('DESIGN SYSTEM', w / 2, 22);
					ctx.textAlign = 'left';

					const DIM = 0.25;
					const cx = w / 2,
						cy = h / 2 + 10;

					// Element 1: Colors (step >= 1)
					if (step >= 1) {
						const alpha = step === 1 ? 1 : DIM + (1 - DIM) * (step === 5 ? 1 : 0);
						const palette = ['#e85d8a', '#9b6dff', '#38c0e8', '#f5a623', '#56d0a0'];
						palette.forEach((col, i) => {
							ctx.globalAlpha = alpha;
							ctx.fillStyle = col;
							ctx.fillRect(cx - 110 + i * 22, cy - 90, 18, 18);
						});
						if (step === 1) {
							ctx.globalAlpha = 1;
							ctx.fillStyle = 'rgba(245,166,35,0.8)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('← COLOR PALETTE →', cx - 88 + 44, cy - 95);
							ctx.textAlign = 'left';
						}
						ctx.globalAlpha = 1;
					}

					// Element 2: Type (step >= 2)
					if (step >= 2) {
						const alpha = step === 2 ? 1 : DIM + (1 - DIM) * (step === 5 ? 1 : 0);
						ctx.globalAlpha = alpha;
						ctx.fillStyle = '#fff';
						ctx.font = `800 20px Syne,sans-serif`;
						ctx.textAlign = 'center';
						ctx.fillText('Heading', cx, cy - 44);
						ctx.fillStyle = 'rgba(208,219,232,0.7)';
						ctx.font = `400 11px IBM Plex Mono,monospace`;
						ctx.fillText('body text · label', cx, cy - 24);
						if (step === 2) {
							ctx.fillStyle = 'rgba(56,192,232,0.8)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.fillText('← TYPOGRAPHY SYSTEM →', cx, cy - 12);
						}
						ctx.globalAlpha = 1;
						ctx.textAlign = 'left';
					}

					// Element 3: Shapes (step >= 3)
					if (step >= 3) {
						const alpha = step === 3 ? 1 : DIM + (1 - DIM) * (step === 5 ? 1 : 0);
						ctx.globalAlpha = alpha;
						ctx.fillStyle = '#38c0e8';
						ctx.beginPath();
						ctx.arc(cx - 60, cy + 20, 14, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = '#9b6dff';
						ctx.fillRect(cx - 16, cy + 6, 24, 24);
						ctx.fillStyle = '#f5a623';
						ctx.beginPath();
						ctx.moveTo(cx + 46, cy + 6);
						ctx.lineTo(cx + 62, cy + 30);
						ctx.lineTo(cx + 30, cy + 30);
						ctx.closePath();
						ctx.fill();
						if (step === 3) {
							ctx.fillStyle = 'rgba(155,109,255,0.8)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('← SHAPE REGISTER →', cx, cy + 46);
							ctx.textAlign = 'left';
						}
						ctx.globalAlpha = 1;
					}

					// Element 4: Spacing (step >= 4)
					if (step >= 4) {
						const alpha = step === 4 ? 1 : DIM + (1 - DIM) * (step === 5 ? 1 : 0);
						ctx.globalAlpha = alpha;
						ctx.strokeStyle = 'rgba(86,208,160,0.5)';
						ctx.lineWidth = 1;
						ctx.setLineDash([3, 3]);
						[cy - 95, cy - 50, cy - 18, cy + 4, cy + 46].forEach((y) => {
							ctx.beginPath();
							ctx.moveTo(cx - 130, y);
							ctx.lineTo(cx + 130, y);
							ctx.stroke();
						});
						ctx.setLineDash([]);
						if (step === 4) {
							ctx.fillStyle = 'rgba(86,208,160,0.8)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.textAlign = 'center';
							ctx.fillText('← SPACING SYSTEM →', cx, cy + 60);
							ctx.textAlign = 'left';
						}
						ctx.globalAlpha = 1;
					}

					// Border (step 0 and 5)
					if (step === 0 || step === 5) {
						ctx.strokeStyle = step === 5 ? 'rgba(245,166,35,0.6)' : 'rgba(255,255,255,0.1)';
						ctx.lineWidth = 1.5;
						ctx.strokeRect(w * 0.1, h * 0.08, w * 0.8, h * 0.84);
						if (step === 5) {
							ctx.fillStyle = 'rgba(245,166,35,0.7)';
							ctx.font = '700 10px Syne,sans-serif';
							ctx.textAlign = 'center';
							ctx.fillText('↑ COMPLETE DESIGN SYSTEM', w / 2, h * 0.08 - 5);
							ctx.textAlign = 'left';
						}
					}
				}
			},
			transform: {
				stages: [
					'Before',
					'Identify Problem',
					'Apply Fix: Color',
					'Apply Fix: Type',
					'Apply Fix: Spacing',
					'After — Fixed'
				],
				info: [
					"Frame 1 — Before: a composition with no visual hierarchy. The viewer sees the problem but doesn't yet know what's wrong.",
					'Frame 2 — Problem identified: red indicators highlight the specific failures. Naming the problem before showing the fix creates cognitive preparation for the solution.',
					'Frame 3 — First fix applied: color hierarchy restored. The viewer can compare directly to the previous state. One change, clearly attributable.',
					'Frame 4 — Second fix applied: typographic weight contrast. The additive nature of fixes makes each change attributable — the viewer knows what caused each improvement.',
					'Frame 5 — Third fix applied: spacing system. The composition is approaching resolution. The viewer has tracked every intervention.',
					'Frame 6 — After: the fixed composition. The viewer has witnessed the transformation step by step — which is more educational than showing before/after alone.'
				],
				draw: (ctx, w, h, step) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const hasCFix = step >= 3;
					const hasTFix = step >= 4;
					const hasSFix = step >= 5;
					const isAfter = step === 5;

					// Background card
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(w * 0.12, h * 0.1, w * 0.76, h * 0.8);

					const titleColor = hasCFix ? '#fff' : 'rgba(200,215,230,0.5)';
					const subColor = hasCFix ? 'rgba(245,166,35,0.85)' : 'rgba(200,215,230,0.5)';
					const titleSize = hasTFix ? 26 : 14;
					const subSize = hasTFix ? 14 : 13;
					const padding = hasSFix ? 32 : 14;

					ctx.fillStyle = titleColor;
					ctx.font = `${hasTFix ? '800' : '400'} ${titleSize}px ${hasTFix ? 'Syne,sans-serif' : 'IBM Plex Mono,monospace'}`;
					ctx.textAlign = 'center';
					ctx.fillText('DESIGN THINKING', w / 2, h * 0.1 + padding + titleSize);

					ctx.fillStyle = subColor;
					ctx.font = `${hasTFix ? '600' : '400'} ${subSize}px IBM Plex Mono,monospace`;
					ctx.fillText(
						'A systematic approach',
						w / 2,
						h * 0.1 + padding + titleSize + (hasSFix ? 22 : 14)
					);

					ctx.fillStyle = 'rgba(208,219,232,0.4)';
					ctx.font = `400 9px IBM Plex Mono,monospace`;
					ctx.fillText(
						'course overview · 12 modules',
						w / 2,
						h * 0.1 + padding + titleSize + (hasSFix ? 44 : 28)
					);
					ctx.textAlign = 'left';

					// Problem indicators (step 1 only)
					if (step === 1) {
						ctx.strokeStyle = 'rgba(232,93,138,0.8)';
						ctx.lineWidth = 1.5;
						ctx.setLineDash([3, 3]);
						ctx.strokeRect(w * 0.14, h * 0.14, w * 0.72, h * 0.22);
						ctx.setLineDash([]);
						ctx.fillStyle = 'rgba(232,93,138,0.9)';
						ctx.font = '9px IBM Plex Mono,monospace';
						ctx.fillText('← ALL ELEMENTS SAME COLOR', w * 0.15, h * 0.14 - 4);
						ctx.fillText('← ALL ELEMENTS SAME WEIGHT', w * 0.15, h * 0.37 + 4);
						ctx.fillText('← SPACING ARBITRARY', w * 0.15, h * 0.54);
					}

					// Fix indicators
					if (step === 3) {
						ctx.fillStyle = 'rgba(86,208,160,0.7)';
						ctx.font = '9px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText('✓ COLOR HIERARCHY APPLIED', w / 2, h * 0.9);
						ctx.textAlign = 'left';
					}
					if (step === 4) {
						ctx.fillStyle = 'rgba(56,192,232,0.7)';
						ctx.font = '9px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText('✓ TYPE WEIGHT CONTRAST APPLIED', w / 2, h * 0.9);
						ctx.textAlign = 'left';
					}
					if (isAfter) {
						ctx.fillStyle = 'rgba(245,166,35,0.7)';
						ctx.font = '700 10px Syne,sans-serif';
						ctx.textAlign = 'center';
						ctx.fillText('COMPOSITION FIXED — all three interventions visible', w / 2, h * 0.92);
						ctx.textAlign = 'left';
					}
				}
			},
			narrative: {
				stages: [
					'The Problem',
					'The Cause',
					'Failure Shown',
					'The Solution',
					'Applied',
					'The Resolution'
				],
				info: [
					'Frame 1 — The Problem: establish a situation the viewer can empathise with. "Your viewers keep dropping off at the 2-minute mark." Stakes are set before the concept is introduced.',
					'Frame 2 — The Cause: reveal the underlying reason for the problem. "The information isn\'t sequenced correctly — you show the conclusion before the setup." The viewer now wants to understand the solution.',
					'Frame 3 — The Failure Illustrated: a concrete example of what the wrong sequence looks like. Showing failure before solution makes the solution more memorable.',
					'Frame 4 — The Solution: the correct principle introduced. "One idea per frame. Setup before conclusion." The viewer is primed and receptive.',
					'Frame 5 — The Principle Applied: the correct sequence shown. The contrast with Frame 3 makes the improvement visceral, not abstract.',
					'Frame 6 — The Resolution: the original problem resolved. "Viewers watched 87% of the video." The narrative closes. The concept is anchored to an outcome the viewer cares about.'
				],
				draw: (ctx, w, h, step) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const SCENES = [
						// 0: The problem
						() => {
							ctx.fillStyle = '#1a0a0a';
							ctx.fillRect(w * 0.1, h * 0.1, w * 0.8, h * 0.65);
							ctx.fillStyle = 'rgba(232,93,138,0.8)';
							ctx.font = `700 13px Syne,sans-serif`;
							ctx.textAlign = 'center';
							ctx.fillText('VIEWERS DROPPING OFF AT 2:00', w / 2, h * 0.36);
							ctx.fillStyle = 'rgba(208,219,232,0.5)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.fillText('Watch time: 38% of video', w / 2, h * 0.5);
							// Drop-off chart
							ctx.strokeStyle = 'rgba(232,93,138,0.6)';
							ctx.lineWidth = 2;
							ctx.beginPath();
							ctx.moveTo(w * 0.2, h * 0.6);
							ctx.lineTo(w * 0.45, h * 0.58);
							ctx.lineTo(w * 0.47, h * 0.7);
							ctx.stroke();
							ctx.fillStyle = 'rgba(232,93,138,0.9)';
							ctx.font = '8px IBM Plex Mono,monospace';
							ctx.fillText('← drop-off', w * 0.48, h * 0.7);
							ctx.textAlign = 'left';
						},
						// 1: The cause
						() => {
							ctx.fillStyle = '#0a0a1a';
							ctx.fillRect(w * 0.1, h * 0.1, w * 0.8, h * 0.65);
							ctx.fillStyle = 'rgba(155,109,255,0.8)';
							ctx.font = `700 12px Syne,sans-serif`;
							ctx.textAlign = 'center';
							ctx.fillText('THE CAUSE:', w / 2, h * 0.28);
							ctx.fillStyle = 'rgba(208,219,232,0.7)';
							ctx.font = '10px IBM Plex Mono,monospace';
							ctx.fillText('Conclusion shown before setup', w / 2, h * 0.42);
							ctx.fillText('Viewer has no context to attach it to', w / 2, h * 0.55);
							ctx.textAlign = 'left';
						},
						// 2: Wrong sequence
						() => {
							ctx.fillStyle = '#100a0a';
							ctx.fillRect(w * 0.05, h * 0.08, w * 0.9, h * 0.72);
							['CONCLUSION', 'SETUP', 'MIDDLE'].forEach((t, i) => {
								const x = w * (0.12 + i * 0.3);
								ctx.fillStyle = 'rgba(232,93,138,0.5)';
								roundRect(ctx, x, h * 0.2, w * 0.22, h * 0.45, 4);
								ctx.fill();
								ctx.fillStyle = 'rgba(255,255,255,0.8)';
								ctx.font = `700 10px Syne,sans-serif`;
								ctx.textAlign = 'center';
								ctx.fillText(t, x + w * 0.11, h * 0.47);
								if (i < 2)
									arrow(
										ctx,
										x + w * 0.22 + 2,
										h * 0.43,
										x + w * 0.3 - 2,
										h * 0.43,
										'rgba(232,93,138,0.6)'
									);
							});
							ctx.fillStyle = 'rgba(232,93,138,0.8)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.fillText('✗ Wrong order — viewer lost', w / 2, h * 0.87);
							ctx.textAlign = 'left';
						},
						// 3: Solution
						() => {
							ctx.fillStyle = '#0a1008';
							ctx.fillRect(w * 0.1, h * 0.1, w * 0.8, h * 0.65);
							ctx.fillStyle = 'rgba(86,208,160,0.8)';
							ctx.font = `700 12px Syne,sans-serif`;
							ctx.textAlign = 'center';
							ctx.fillText('THE PRINCIPLE:', w / 2, h * 0.3);
							ctx.fillStyle = '#fff';
							ctx.font = `800 14px Syne,sans-serif`;
							ctx.fillText('Setup before conclusion.', w / 2, h * 0.46);
							ctx.fillStyle = 'rgba(86,208,160,0.6)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.fillText('One idea per frame.', w / 2, h * 0.6);
							ctx.textAlign = 'left';
						},
						// 4: Correct sequence
						() => {
							ctx.fillStyle = '#080f0a';
							ctx.fillRect(w * 0.05, h * 0.08, w * 0.9, h * 0.72);
							['SETUP', 'MIDDLE', 'CONCLUSION'].forEach((t, i) => {
								const x = w * (0.12 + i * 0.3);
								ctx.fillStyle = 'rgba(86,208,160,0.55)';
								roundRect(ctx, x, h * 0.2, w * 0.22, h * 0.45, 4);
								ctx.fill();
								ctx.fillStyle = 'rgba(255,255,255,0.8)';
								ctx.font = `700 10px Syne,sans-serif`;
								ctx.textAlign = 'center';
								ctx.fillText(t, x + w * 0.11, h * 0.47);
								if (i < 2)
									arrow(
										ctx,
										x + w * 0.22 + 2,
										h * 0.43,
										x + w * 0.3 - 2,
										h * 0.43,
										'rgba(86,208,160,0.6)'
									);
							});
							ctx.fillStyle = 'rgba(86,208,160,0.8)';
							ctx.font = '9px IBM Plex Mono,monospace';
							ctx.fillText('✓ Correct order — viewer follows', w / 2, h * 0.87);
							ctx.textAlign = 'left';
						},
						// 5: Resolution
						() => {
							ctx.fillStyle = '#080f08';
							ctx.fillRect(w * 0.1, h * 0.1, w * 0.8, h * 0.65);
							ctx.fillStyle = 'rgba(86,208,160,0.8)';
							ctx.font = `700 13px Syne,sans-serif`;
							ctx.textAlign = 'center';
							ctx.fillText('RESULT:', w / 2, h * 0.3);
							ctx.fillStyle = '#fff';
							ctx.font = `800 20px Syne,sans-serif`;
							ctx.fillText('Watch time: 87%', w / 2, h * 0.48);
							ctx.fillStyle = 'rgba(86,208,160,0.6)';
							ctx.font = '10px IBM Plex Mono,monospace';
							ctx.fillText('Problem solved. Concept learned.', w / 2, h * 0.62);
							ctx.textAlign = 'left';
						}
					];
					SCENES[Math.min(step, SCENES.length - 1)]();
				}
			}
		};

		function buildSeqStages() {
			const wrap = document.getElementById('seq-stages');
			wrap.innerHTML = '';
			const stages = SEQ_MODES[seqMode].stages;
			stages.forEach((label, i) => {
				const div = document.createElement('div');
				div.className = 'seq-stage' + (i === seqStep ? ' active' : '');
				div.innerHTML = `<div class="seq-stage-num">${String(i + 1).padStart(2, '0')}</div><div class="seq-stage-label">${label}</div>`;
				div.addEventListener('click', () => {
					seqStep = i;
					renderSeq();
				});
				wrap.appendChild(div);
			});
		}

		function renderSeq() {
			SEQ_MODES[seqMode].draw(sCtx, SW, SH, seqStep);
			document.getElementById('seq-info').textContent = SEQ_MODES[seqMode].info[seqStep];
			const stages = document.querySelectorAll('.seq-stage');
			stages.forEach((s, i) => s.classList.toggle('active', i === seqStep));
			document.getElementById('seq-prev').disabled = seqStep === 0;
			document.getElementById('seq-next').disabled =
				seqStep >= SEQ_MODES[seqMode].stages.length - 1;
		}

		function setSeqMode(mode, btn) {
			seqMode = mode;
			seqStep = 0;
			document
				.querySelectorAll('#seq-flow-controls .btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			buildSeqStages();
			renderSeq();
		}

		function stepSeq(dir) {
			const max = SEQ_MODES[seqMode].stages.length - 1;
			seqStep = Math.max(0, Math.min(max, seqStep + dir));
			renderSeq();
		}

		function resetSeq() {
			seqStep = 0;
			renderSeq();
		}

		buildSeqStages();
		renderSeq();

		/* ══════════════════════════════════
   DEMO 3: DIAGRAM REDUCTION LAB
══════════════════════════════════ */
		const rdCvs = document.getElementById('reduction-canvas');
		const rCtx = rdCvs.getContext('2d');
		const RW = rdCvs.width,
			RH = rdCvs.height;
		let rdStep = 0;

		const REDUCTION_STAGES = [
			{
				label: 'Complete',
				score: 18,
				scoreColor: 'var(--rose)',
				note: 'All seven factors affecting visual hierarchy shown simultaneously, with full labels, connecting lines between related factors, background colour blocks, and descriptive annotations. Technically accurate. Cognitively overwhelming — the viewer cannot identify which relationship is most important.',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(208,219,232,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('FACTORS AFFECTING VISUAL HIERARCHY', w / 2, 18);
					ctx.textAlign = 'left';
					const nodes = [
						{
							x: 0.5,
							y: 0.42,
							r: 32,
							label: 'SIZE',
							col: 'rgba(245,166,35,0.75)',
							sub: 'largest first'
						},
						{
							x: 0.24,
							y: 0.28,
							r: 20,
							label: 'WEIGHT',
							col: 'rgba(56,192,232,0.65)',
							sub: 'bold dominates'
						},
						{
							x: 0.76,
							y: 0.28,
							r: 20,
							label: 'CONTRAST',
							col: 'rgba(155,109,255,0.65)',
							sub: 'dark on light'
						},
						{
							x: 0.18,
							y: 0.62,
							r: 16,
							label: 'COLOUR',
							col: 'rgba(86,208,160,0.55)',
							sub: 'warm advances'
						},
						{
							x: 0.82,
							y: 0.62,
							r: 16,
							label: 'POSITION',
							col: 'rgba(232,93,138,0.55)',
							sub: 'top-left first'
						},
						{
							x: 0.38,
							y: 0.72,
							r: 14,
							label: 'ISOLATION',
							col: 'rgba(245,166,35,0.5)',
							sub: 'space = signal'
						},
						{
							x: 0.62,
							y: 0.72,
							r: 14,
							label: 'TEXTURE',
							col: 'rgba(56,192,232,0.45)',
							sub: 'detail attracts'
						}
					];
					// All connections
					ctx.strokeStyle = 'rgba(255,255,255,0.08)';
					ctx.lineWidth = 1;
					for (let i = 0; i < nodes.length; i++)
						for (let j = i + 1; j < nodes.length; j++) {
							ctx.beginPath();
							ctx.moveTo(nodes[i].x * w, nodes[i].y * h);
							ctx.lineTo(nodes[j].x * w, nodes[j].y * h);
							ctx.stroke();
						}
					// Background fills
					nodes.forEach((n) => {
						const bgC = n.col.replace(/[^,]+\)/, '0.06)');
						ctx.fillStyle = bgC;
						ctx.beginPath();
						ctx.arc(n.x * w, n.y * h, n.r + 16, 0, Math.PI * 2);
						ctx.fill();
					});
					// Nodes
					nodes.forEach((n) => {
						ctx.fillStyle = n.col;
						ctx.beginPath();
						ctx.arc(n.x * w, n.y * h, n.r, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = 'rgba(0,0,0,0.7)';
						ctx.font = `700 ${Math.min(9, n.r * 0.4)}px Syne,sans-serif`;
						ctx.textAlign = 'center';
						ctx.fillText(n.label, n.x * w, n.y * h + 3);
						ctx.fillStyle = 'rgba(255,255,255,0.4)';
						ctx.font = '7px IBM Plex Mono,monospace';
						ctx.fillText(n.sub, n.x * w, n.y * h + n.r + 12);
						ctx.textAlign = 'left';
					});
				}
			},
			{
				label: 'Remove clutter',
				score: 42,
				scoreColor: 'var(--amber)',
				note: 'Decorative background fills and sub-labels removed. The seven nodes remain but the visual noise is reduced. The core structure is becoming visible — but seven elements still compete for attention simultaneously.',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(208,219,232,0.5)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('FACTORS AFFECTING VISUAL HIERARCHY', w / 2, 18);
					ctx.textAlign = 'left';
					const nodes = [
						{ x: 0.5, y: 0.42, r: 32, label: 'SIZE', col: 'rgba(245,166,35,0.75)' },
						{ x: 0.24, y: 0.28, r: 20, label: 'WEIGHT', col: 'rgba(56,192,232,0.65)' },
						{ x: 0.76, y: 0.28, r: 20, label: 'CONTRAST', col: 'rgba(155,109,255,0.65)' },
						{ x: 0.18, y: 0.62, r: 16, label: 'COLOUR', col: 'rgba(86,208,160,0.55)' },
						{ x: 0.82, y: 0.62, r: 16, label: 'POSITION', col: 'rgba(232,93,138,0.55)' },
						{ x: 0.38, y: 0.72, r: 14, label: 'ISOLATION', col: 'rgba(245,166,35,0.5)' },
						{ x: 0.62, y: 0.72, r: 14, label: 'TEXTURE', col: 'rgba(56,192,232,0.45)' }
					];
					ctx.strokeStyle = 'rgba(255,255,255,0.08)';
					ctx.lineWidth = 1;
					for (let i = 0; i < nodes.length; i++)
						for (let j = i + 1; j < nodes.length; j++) {
							ctx.beginPath();
							ctx.moveTo(nodes[i].x * w, nodes[i].y * h);
							ctx.lineTo(nodes[j].x * w, nodes[j].y * h);
							ctx.stroke();
						}
					nodes.forEach((n) => {
						ctx.fillStyle = n.col;
						ctx.beginPath();
						ctx.arc(n.x * w, n.y * h, n.r, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = 'rgba(0,0,0,0.7)';
						ctx.font = `700 ${Math.min(9, n.r * 0.4)}px Syne,sans-serif`;
						ctx.textAlign = 'center';
						ctx.fillText(n.label, n.x * w, n.y * h + 3);
						ctx.textAlign = 'left';
					});
				}
			},
			{
				label: 'Reduce to essentials',
				score: 72,
				scoreColor: 'var(--amber)',
				note: 'Cut to the three factors that carry the most explanatory weight: Size (the primary driver), Weight, and Contrast. The connections now only show how these three create a reading order. A viewer can absorb three nodes in a single glance.',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(208,219,232,0.6)';
					ctx.font = '10px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('THE THREE PRIMARY DRIVERS', w / 2, 22);
					ctx.textAlign = 'left';
					const nodes = [
						{ x: 0.5, y: 0.38, r: 42, label: 'SIZE', col: 'rgba(245,166,35,0.85)' },
						{ x: 0.25, y: 0.68, r: 26, label: 'WEIGHT', col: 'rgba(56,192,232,0.75)' },
						{ x: 0.75, y: 0.68, r: 26, label: 'CONTRAST', col: 'rgba(155,109,255,0.75)' }
					];
					// Clean connections
					ctx.strokeStyle = 'rgba(245,166,35,0.35)';
					ctx.lineWidth = 1.5;
					arrow(
						ctx,
						nodes[0].x * w,
						nodes[0].y * h + 42,
						nodes[1].x * w,
						nodes[1].y * h - 26,
						'rgba(245,166,35,0.4)'
					);
					arrow(
						ctx,
						nodes[0].x * w,
						nodes[0].y * h + 42,
						nodes[2].x * w,
						nodes[2].y * h - 26,
						'rgba(245,166,35,0.4)'
					);
					nodes.forEach((n) => {
						ctx.fillStyle = n.col;
						ctx.beginPath();
						ctx.arc(n.x * w, n.y * h, n.r, 0, Math.PI * 2);
						ctx.fill();
						ctx.fillStyle = 'rgba(0,0,0,0.8)';
						ctx.font = `800 ${n.r * 0.28}px Syne,sans-serif`;
						ctx.textAlign = 'center';
						ctx.fillText(n.label, n.x * w, n.y * h + n.r * 0.12);
						ctx.textAlign = 'left';
					});
				}
			},
			{
				label: 'Minimum viable',
				score: 92,
				scoreColor: 'var(--sage)',
				note: 'The single core insight: SIZE dominates. Weight and Contrast modify it. The diagram communicates the one relationship the viewer must understand to apply the concept. Every element earns its place. The concept transfers in under five seconds.',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(245,166,35,0.7)';
					ctx.font = '10px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('VISUAL HIERARCHY RULE', w / 2, 22);
					ctx.textAlign = 'left';
					// Single dominant message
					const cx = w / 2,
						cy = h / 2 + 10;
					ctx.fillStyle = 'rgba(245,166,35,0.15)';
					ctx.beginPath();
					ctx.arc(cx, cy, 80, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = 'rgba(245,166,35,0.9)';
					ctx.beginPath();
					ctx.arc(cx, cy, 60, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = '#111';
					ctx.font = `800 22px Syne,sans-serif`;
					ctx.textAlign = 'center';
					ctx.fillText('SIZE', cx, cy + 8);
					ctx.textAlign = 'left';
					// Two supporting modifiers
					ctx.fillStyle = 'rgba(56,192,232,0.7)';
					ctx.font = '10px IBM Plex Mono,monospace';
					ctx.fillText('+ WEIGHT', cx - w * 0.3, cy - 15);
					ctx.fillText('+ CONTRAST', cx + w * 0.12, cy - 15);
					// Arrows from modifiers to center
					arrow(ctx, cx - w * 0.18, cy - 10, cx - 62, cy - 10, 'rgba(56,192,232,0.45)');
					arrow(ctx, cx + w * 0.2, cy - 10, cx + 62, cy - 10, 'rgba(56,192,232,0.45)');
					// Caption
					ctx.fillStyle = 'rgba(245,166,35,0.65)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('Larger = noticed first.', cx, h * 0.88);
					ctx.fillText('Weight and contrast amplify or reduce.', cx, h * 0.94);
					ctx.textAlign = 'left';
				}
			}
		];

		function buildReductionStages() {
			const row = document.getElementById('reduction-stage-row');
			row.innerHTML = '';
			REDUCTION_STAGES.forEach((s, i) => {
				const btn = document.createElement('button');
				btn.className = 'reduction-step-btn' + (i === rdStep ? ' active' : '');
				btn.innerHTML = `<span class="step-num">${String(i + 1).padStart(2, '0')}</span>${s.label}`;
				btn.addEventListener('click', () => {
					rdStep = i;
					renderReduction();
				});
				row.appendChild(btn);
			});
		}

		function renderReduction() {
			REDUCTION_STAGES[rdStep].draw(rCtx, RW, RH);
			const s = REDUCTION_STAGES[rdStep];
			const bar = document.getElementById('reduction-bar');
			bar.style.width = s.score + '%';
			bar.style.background = s.scoreColor;
			document.getElementById('reduction-score-val').textContent = s.score + '%';
			document.getElementById('reduction-score-val').style.color = s.scoreColor;
			document.getElementById('reduction-note').textContent = s.note;
			document
				.querySelectorAll('.reduction-step-btn')
				.forEach((b, i) => b.classList.toggle('active', i === rdStep));
		}

		buildReductionStages();
		renderReduction();

		/* ══════════════════════════════════
   DEMO 4: STORYBOARD BUILDER
══════════════════════════════════ */
		const SB_PANEL_COUNT = 6;
		const SB_W = 140,
			SB_H = 80;

		const sbState = Array.from({ length: SB_PANEL_COUNT }, (_, i) => ({
			type: i === 0 ? 'intro' : 'empty',
			caption: i === 0 ? 'Introduce the concept of visual hierarchy.' : ''
		}));

		let sbSelected = 0;

		const SB_TYPES = {
			intro: {
				label: 'Concept Intro',
				draw: (ctx, w, h, caption) => {
					ctx.fillStyle = '#080c14';
					ctx.fillRect(0, 0, w, h);
					const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w * 0.4);
					g.addColorStop(0, 'rgba(245,166,35,0.15)');
					g.addColorStop(1, 'transparent');
					ctx.fillStyle = g;
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(245,166,35,0.8)';
					ctx.font = `700 ${h * 0.18}px Syne,sans-serif`;
					ctx.textAlign = 'center';
					ctx.fillText('CONCEPT', w / 2, h * 0.42);
					ctx.fillStyle = 'rgba(245,166,35,0.4)';
					ctx.font = `400 ${h * 0.1}px IBM Plex Mono,monospace`;
					ctx.fillText('intro frame', w / 2, h * 0.62);
					ctx.textAlign = 'left';
					ctx.strokeStyle = 'rgba(245,166,35,0.3)';
					ctx.lineWidth = 1;
					ctx.strokeRect(4, 4, w - 8, h - 8);
				}
			},
			build: {
				label: 'Build Frame',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#080c14';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(56,192,232,0.25)';
					ctx.fillRect(8, 8, w - 16, h * 0.4);
					ctx.fillStyle = 'rgba(255,255,255,0.2)';
					ctx.fillRect(8, h * 0.52, w * 0.55, h * 0.1);
					ctx.fillStyle = 'rgba(255,255,255,0.15)';
					ctx.fillRect(8, h * 0.66, w * 0.4, h * 0.1);
					// New element marker
					ctx.fillStyle = 'rgba(56,192,232,0.7)';
					ctx.beginPath();
					ctx.arc(w - 18, h * 0.25, 8, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = '#fff';
					ctx.font = `700 ${h * 0.12}px IBM Plex Mono,monospace`;
					ctx.textAlign = 'center';
					ctx.fillText('+', w - 18, h * 0.28);
					ctx.textAlign = 'left';
					ctx.strokeStyle = 'rgba(56,192,232,0.4)';
					ctx.lineWidth = 1;
					ctx.setLineDash([2, 2]);
					ctx.strokeRect(4, 4, w - 8, h * 0.45);
					ctx.setLineDash([]);
				}
			},
			compare: {
				label: 'Comparison',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#080c14';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = '#0d1a2c';
					ctx.fillRect(4, 8, w / 2 - 8, h - 16);
					ctx.fillStyle = '#0d200f';
					ctx.fillRect(w / 2 + 4, 8, w / 2 - 8, h - 16);
					ctx.fillStyle = 'rgba(232,93,138,0.6)';
					ctx.font = `9px IBM Plex Mono,monospace`;
					ctx.textAlign = 'center';
					ctx.fillText('BEFORE', w / 4, h * 0.55);
					ctx.fillStyle = 'rgba(86,208,160,0.6)';
					ctx.fillText('AFTER', (w * 3) / 4, h * 0.55);
					ctx.textAlign = 'left';
					ctx.fillStyle = 'rgba(245,166,35,0.8)';
					ctx.fillRect(w / 2 - 1, 8, 2, h - 16);
				}
			},
			process: {
				label: 'Process Step',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#080c14';
					ctx.fillRect(0, 0, w, h);
					ctx.fillStyle = 'rgba(155,109,255,0.6)';
					roundRect(ctx, 8, h * 0.2, w * 0.3, h * 0.5, 4);
					ctx.fill();
					arrow(ctx, w * 0.38 + 2, h / 2, w * 0.58 - 2, h / 2, 'rgba(245,166,35,0.8)', 7);
					ctx.fillStyle = 'rgba(155,109,255,0.4)';
					roundRect(ctx, w * 0.58, h * 0.2, w * 0.34, h * 0.5, 4);
					ctx.fill();
					ctx.fillStyle = 'rgba(255,255,255,0.5)';
					ctx.font = '7px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('INPUT', w * 0.23, h * 0.78);
					ctx.fillText('OUTPUT', w * 0.75, h * 0.78);
					ctx.textAlign = 'left';
				}
			},
			summary: {
				label: 'Summary',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#070a0e';
					ctx.fillRect(0, 0, w, h);
					// Many small elements dimmed
					const items = [
						{ x: 0.12, y: 0.22 },
						{ x: 0.35, y: 0.28 },
						{ x: 0.6, y: 0.22 },
						{ x: 0.82, y: 0.3 },
						{ x: 0.2, y: 0.55 },
						{ x: 0.45, y: 0.5 },
						{ x: 0.7, y: 0.55 }
					];
					items.forEach((item) => {
						ctx.fillStyle = 'rgba(208,219,232,0.15)';
						ctx.fillRect(w * item.x - 12, h * item.y - 8, 22, 14);
					});
					// One key takeaway prominent
					ctx.fillStyle = 'rgba(86,208,160,0.15)';
					ctx.fillRect(8, h * 0.66, w - 16, h * 0.22);
					ctx.fillStyle = 'rgba(86,208,160,0.9)';
					ctx.font = `700 ${h * 0.14}px Syne,sans-serif`;
					ctx.textAlign = 'center';
					ctx.fillText('KEY TAKEAWAY', w / 2, h * 0.81);
					ctx.textAlign = 'left';
				}
			},
			empty: {
				label: 'Empty',
				draw: (ctx, w, h) => {
					ctx.fillStyle = '#060809';
					ctx.fillRect(0, 0, w, h);
					ctx.strokeStyle = 'rgba(255,255,255,0.08)';
					ctx.lineWidth = 1;
					ctx.setLineDash([3, 3]);
					ctx.strokeRect(4, 4, w - 8, h - 8);
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(255,255,255,0.12)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('empty', w / 2, h / 2 + 4);
					ctx.textAlign = 'left';
				}
			}
		};

		function buildSbPanels() {
			const wrap = document.getElementById('sb-panels');
			wrap.innerHTML = '';
			sbState.forEach((panel, i) => {
				const div = document.createElement('div');
				div.className = 'sb-panel' + (i === sbSelected ? ' selected' : '');
				const cvs = document.createElement('canvas');
				cvs.width = SB_W;
				cvs.height = SB_H;
				const footer = document.createElement('div');
				footer.className = 'sb-panel-footer';
				footer.innerHTML = `<span class="sb-panel-num">${String(i + 1).padStart(2, '0')}</span><span>${SB_TYPES[panel.type].label}</span>`;
				div.appendChild(cvs);
				div.appendChild(footer);
				wrap.appendChild(div);
				SB_TYPES[panel.type].draw(cvs.getContext('2d'), SB_W, SB_H, panel.caption);
				div.addEventListener('click', () => {
					sbSelected = i;
					document
						.querySelectorAll('.sb-panel')
						.forEach((p, pi) => p.classList.toggle('selected', pi === i));
					document.getElementById('sb-caption-input').value = sbState[i].caption;
					document
						.querySelectorAll('.sb-type-btn')
						.forEach((b) => b.classList.toggle('active', b.dataset.type === sbState[i].type));
				});
			});
			buildSbStrip();
		}

		function buildSbStrip() {
			const strip = document.getElementById('sb-preview-strip');
			const existing = strip.querySelectorAll('.sb-strip-item');
			existing.forEach((e) => e.remove());
			sbState.forEach((panel, i) => {
				const item = document.createElement('div');
				item.className = 'sb-strip-item';
				const cvs = document.createElement('canvas');
				cvs.width = 56;
				cvs.height = 32;
				const lbl = document.createElement('div');
				lbl.className = 'sb-strip-label';
				lbl.textContent = String(i + 1).padStart(2, '0');
				item.appendChild(cvs);
				item.appendChild(lbl);
				strip.appendChild(item);
				const ctx = cvs.getContext('2d');
				// Scale down the panel draw
				ctx.save();
				ctx.scale(56 / SB_W, 32 / SB_H);
				SB_TYPES[panel.type].draw(ctx, SB_W, SB_H, panel.caption);
				ctx.restore();
				// Arrow between
				if (i < sbState.length - 1) {
					const arrow = document.createElement('div');
					arrow.textContent = '›';
					arrow.style.cssText =
						'font-size:14px;color:var(--border2);align-self:center;flex-shrink:0';
					strip.appendChild(arrow);
				}
			});
		}

		function setSbType(type, btn) {
			sbState[sbSelected].type = type;
			document
				.querySelectorAll('.sb-type-btn')
				.forEach((b) => b.classList.toggle('active', b.dataset.type === type));
			buildSbPanels();
		}

		function updateSbCaption() {
			sbState[sbSelected].caption = document.getElementById('sb-caption-input').value;
			buildSbStrip();
		}

		buildSbPanels();

		/* ══════════════════════════════════
   ASSESSMENT
══════════════════════════════════ */
		const ASSESS_QS = [
			{
				label: 'Specimen A — Analogy Failure',
				canvasDraw: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const half = w / 2;
					// Left: illustration (decorative, no structural parallel)
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(16, 16, half - 28, h - 32);
					ctx.fillStyle = 'rgba(208,219,232,0.6)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('COLOUR CONTRAST', 24, 32);
					// Literal colour swatches — no structural analogy
					[
						['#e85d8a', 0.2],
						['#38c0e8', 0.42],
						['#56d0a0', 0.62],
						['#f5a623', 0.8]
					].forEach(([col, xr]) => {
						ctx.fillStyle = col;
						ctx.fillRect((half - 28) * xr + 8, h * 0.38, 28, 28);
						ctx.fillStyle = 'rgba(255,255,255,0.3)';
						ctx.font = '7px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText(col, (half - 28) * xr + 22, h * 0.38 + 40);
						ctx.textAlign = 'left';
					});
					ctx.fillStyle = 'rgba(255,255,255,0.3)';
					ctx.font = '8px IBM Plex Mono,monospace';
					ctx.textAlign = 'center';
					ctx.fillText('← some colours shown →', half / 2, h * 0.82);
					ctx.textAlign = 'left';
					// Right: structural analogy
					ctx.fillStyle = '#0d1520';
					ctx.fillRect(half + 12, 16, half - 28, h - 32);
					ctx.fillStyle = 'rgba(245,166,35,0.6)';
					ctx.font = '9px IBM Plex Mono,monospace';
					ctx.fillText('COLOUR CONTRAST', half + 20, 32);
					// Traffic light on dark road — structural
					ctx.fillStyle = '#111';
					ctx.fillRect(half + 40, h * 0.2, 24, 60);
					[
						['#e85d8a', 0.27],
						['#f5a623', 0.4],
						['#56d0a0', 0.53]
					].forEach(([col, yr]) => {
						ctx.fillStyle = col;
						ctx.beginPath();
						ctx.arc(half + 52, h * yr, 9, 0, Math.PI * 2);
						ctx.fill();
					});
					ctx.fillStyle = '#333';
					ctx.fillRect(half + 20, h * 0.7, w - half - 36, 10); // Road
					// Labels: signal = accent, field = background
					ctx.strokeStyle = 'rgba(245,166,35,0.4)';
					ctx.lineWidth = 1;
					ctx.setLineDash([2, 2]);
					ctx.beginPath();
					ctx.moveTo(half + 62, h * 0.27);
					ctx.lineTo(half + 95, h * 0.27);
					ctx.stroke();
					ctx.setLineDash([]);
					ctx.fillStyle = 'rgba(245,166,35,0.6)';
					ctx.font = '7px IBM Plex Mono,monospace';
					ctx.fillText('signal = accent', half + 97, h * 0.29);
					ctx.fillStyle = 'rgba(208,219,232,0.5)';
					ctx.font = '7px IBM Plex Mono,monospace';
					ctx.fillText('field = background', half + 20, h * 0.82);
				},
				question:
					'The left side shows an illustration of colour contrast (swatches displayed). The right side shows a structural analogy (traffic lights on a dark road). What does the right side do that the left side cannot?',
				correct: 1,
				opts: [
					'A. The right side uses a more relatable cultural reference that viewers will prefer',
					"B. The right side maps a familiar structure (signal visible against field, field providing context) onto the concept — borrowing the viewer's existing understanding of traffic lights to explain how accent colours work against backgrounds",
					'C. The right side uses fewer colours, which makes the diagram easier to read',
					'D. The right side is a before/after comparison, which is always more effective than a single-state illustration'
				],
				ok: 'Correct. The traffic light analogy maps a structural relationship — a high-contrast signal against a neutral field — directly onto how colour contrast works in design. The viewer already understands why a red light is visible at night; the analogy borrows that understanding without building it from scratch. The swatches on the left just show what colours look like — they communicate no structural relationship.',
				bad: "Not quite. The key distinction is structural transfer: the analogy maps the relationship between signal and field (how contrast works in the source domain) onto the design concept, allowing the viewer's existing knowledge to do the explanatory work. The illustration only shows what the concept looks like, not how it works."
			},
			{
				label: 'Specimen B — Sequence Ordering Problem',
				canvasDraw: (ctx, w, h) => {
					ctx.fillStyle = '#070b10';
					ctx.fillRect(0, 0, w, h);
					const fw = (w - 60) / 4,
						fh = h * 0.6,
						fy = (h - fh) / 2;
					const SEQUENCE = ['CONCLUSION', 'WHY IT FAILS', 'THE PRINCIPLE', 'HOW TO APPLY'];
					const COLS = [
						'rgba(86,208,160,0.7)',
						'rgba(232,93,138,0.6)',
						'rgba(245,166,35,0.6)',
						'rgba(56,192,232,0.6)'
					];
					SEQUENCE.forEach((label, i) => {
						const fx = 16 + i * (fw + 8);
						ctx.fillStyle = '#0d1520';
						roundRect(ctx, fx, fy, fw, fh, 4);
						ctx.fill();
						ctx.fillStyle = COLS[i];
						ctx.font = `700 ${fw * 0.11}px Syne,sans-serif`;
						ctx.textAlign = 'center';
						const words = label.split(' ');
						words.forEach((word, wi) => ctx.fillText(word, fx + fw / 2, fy + fh * 0.42 + wi * 14));
						ctx.textAlign = 'left';
						if (i < 3)
							arrow(
								ctx,
								fx + fw + 2,
								fy + fh / 2,
								fx + fw + 6,
								fy + fh / 2,
								'rgba(245,166,35,0.4)'
							);
						ctx.fillStyle = COLS[i];
						ctx.font = '8px IBM Plex Mono,monospace';
						ctx.textAlign = 'center';
						ctx.fillText(String(i + 1), fx + fw / 2, fy + fh + 14);
						ctx.textAlign = 'left';
					});
				},
				question:
					'This sequence starts with CONCLUSION, then explains why it fails, then introduces the principle, then shows application. What is the structural problem with this ordering?',
				correct: 2,
				opts: [
					'A. The sequence has four steps — two or three steps is the maximum for effective educational sequences',
					'B. The conclusion should always come last, but the other three steps are in the correct order',
					'C. The conclusion is shown before the viewer has any context to attach it to — they cannot understand what the conclusion means or why it matters until after the principle and failure have been established. Setup must precede conclusion.',
					'D. The sequence has no visual variety — all four frames use the same layout structure'
				],
				ok: 'Correct. Showing a conclusion before the viewer has context for it is the defining sequential error. "Why it fails" and "The principle" establish the stakes and concept; "How to apply" builds on the principle. "Conclusion" requires all three of those to be meaningful. Presenting it first is like revealing the punchline before telling the joke — the setup is what makes the conclusion land.',
				bad: 'Not quite. The fundamental error is ordering: a conclusion requires the setup that gives it meaning. Showing the conclusion first means the viewer has no context to anchor it to — they cannot know what it resolves or why it matters. The viewer must be walked through setup and principle before the conclusion is meaningful.'
			}
		];

		const assessAnswered = {};
		function buildAssessment() {
			const wrap = document.getElementById('assess-wrap');
			ASSESS_QS.forEach((q, qi) => {
				const div = document.createElement('div');
				div.className = 'assess-question';
				const hdr = document.createElement('div');
				hdr.className = 'assess-q-hdr';
				hdr.textContent = q.label;
				const body = document.createElement('div');
				body.className = 'assess-q-body';
				const cw = document.createElement('div');
				cw.className = 'assess-canvas-row';
				const cvs = document.createElement('canvas');
				cvs.width = 560;
				cvs.height = 180;
				cvs.style.maxWidth = '100%';
				cw.appendChild(cvs);
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
						const fb = div.querySelector('.assess-fb');
						if (oi === q.correct) {
							btn.classList.remove('disabled');
							fb.textContent = '✓ ' + q.ok;
							fb.className = 'assess-fb ok';
						} else {
							btn.classList.add('wrong');
							fb.textContent = '✗ ' + q.bad;
							fb.className = 'assess-fb bad';
						}
					});
					opts.appendChild(btn);
				});
				const fb = document.createElement('div');
				fb.className = 'assess-fb';
				body.appendChild(cw);
				body.appendChild(qt);
				body.appendChild(opts);
				body.appendChild(fb);
				div.appendChild(hdr);
				div.appendChild(body);
				wrap.appendChild(div);
				q.canvasDraw(cvs.getContext('2d'), cvs.width, cvs.height);
			});
		}

		buildAssessment();

		/* ══════════════════════════════════
   QUIZ
══════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;
		const explanations = [
			"Correct. An illustration shows appearance — what a concept looks like. A visual analogy maps the structural relationships of a familiar domain onto the unfamiliar concept, allowing the viewer's existing knowledge to do the explanatory work. The former describes; the latter transfers understanding.",
			"Correct. When two ideas arrive in the same frame, the viewer's attention must split to process both simultaneously. Neither idea receives the full cognitive engagement needed to be absorbed. The constraint is cognitive capacity, not preference.",
			'Correct. Completeness bias describes the impulse to include all relevant information. The result is a diagram that is accurate but unusable — the cognitive load of parsing every element consumes the attention needed to understand any of them.',
			'Correct. The floor of reduction is set by accuracy: if the stripped version communicates a false or misleading version of the concept, it has been reduced too far. The target is minimum viable accuracy — not minimum elements.',
			"Correct. Storyboarding forces alignment between narration and visuals before editing. The most common educational video failure is narrating something that isn't visible on screen — a gap the storyboard surfaces when it's still cheap to fix."
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
					'✗ Revisit the section — focus on the cognitive mechanism at work, not the surface feature.';
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
		if (typeof arrow === 'function') actions.arrow = arrow;
		if (typeof buildAnalogies === 'function') actions.buildAnalogies = buildAnalogies;
		if (typeof showAnalogy === 'function') actions.showAnalogy = showAnalogy;
		if (typeof buildSeqStages === 'function') actions.buildSeqStages = buildSeqStages;
		if (typeof renderSeq === 'function') actions.renderSeq = renderSeq;
		if (typeof setSeqMode === 'function') actions.setSeqMode = setSeqMode;
		if (typeof stepSeq === 'function') actions.stepSeq = stepSeq;
		if (typeof resetSeq === 'function') actions.resetSeq = resetSeq;
		if (typeof buildReductionStages === 'function')
			actions.buildReductionStages = buildReductionStages;
		if (typeof renderReduction === 'function') actions.renderReduction = renderReduction;
		if (typeof buildSbPanels === 'function') actions.buildSbPanels = buildSbPanels;
		if (typeof buildSbStrip === 'function') actions.buildSbStrip = buildSbStrip;
		if (typeof setSbType === 'function') actions.setSbType = setSbType;
		if (typeof updateSbCaption === 'function') actions.updateSbCaption = updateSbCaption;
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
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 08 of 10</div>
	</header>

	<div class="module-hero">
		<div class="module-number">08</div>
		<div class="module-tag">Module 08 · Story + Explanation</div>
		<h1 class="module-title">Designing<br /><span>Story-Driven Visuals</span></h1>
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
			<li><a href="#visual-analogies">Visual Analogies</a></li>
			<li><a href="#sequential">Sequential Design &amp; Flow</a></li>
			<li><a href="#simplification">Simplifying Complex Ideas</a></li>
			<li><a href="#storyboard">Storyboard Panels</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Construct visual analogies that make abstract concepts immediately tangible</li>
			<li>Design information in deliberate sequences that guide the viewer through a narrative</li>
			<li>Reduce a complex diagram to its minimum legible elements without losing meaning</li>
			<li>Build a set of storyboard frames that plan visual communication before production</li>
		</ul>
	</section>

	<!-- ═══════════════════════════════
     SECTION 1: VISUAL ANALOGIES
═══════════════════════════════ -->
	<section id="visual-analogies" class="section">
		<div class="section-header">
			<span class="section-num">08.01</span>
			<h2 class="section-title">Visual Analogies</h2>
		</div>

		<p>
			An analogy is a cognitive shortcut: it maps an unfamiliar idea onto a familiar structure,
			allowing the viewer's existing mental models to do most of the explanatory work. The power of
			a good visual analogy is that it transfers understanding rather than constructing it from
			scratch. A viewer who has never encountered the concept of
			<em>visual hierarchy</em> will understand it immediately if you show them a newspaper front page
			— the headline large, the subheading smaller, the body text smaller still. They already know how
			to read a newspaper. The analogy borrows that knowledge.
		</p>

		<p>
			The construction of a visual analogy has two steps. First, identify the
			<strong>structural similarity</strong> between the abstract concept and the concrete source:
			what is the relationship in each domain? Second,
			<strong>make the parallel explicit</strong> through visual labelling — show the source system, show
			the target system, connect corresponding elements with consistent visual treatment (color, position,
			shape). The viewer should not have to infer the connection; the design makes it unavoidable.
		</p>

		<p>
			The most common failure in educational visuals is <em>illustration without analogy</em> — drawing
			a picture of the concept rather than a structure that mirrors it. A drawing of a hierarchy (boxes
			in a tree) is an illustration. A newspaper front page with hierarchy tiers labeled and connected
			to the concept being taught is an analogy. The illustration shows what something looks like; the
			analogy shows how it works.
		</p>

		<div class="callout">
			<div class="callout-label">Source Selection Principle</div>
			The ideal analogy source is something your specific audience encounters so frequently it requires
			no introduction. For a general audience: architecture, cooking, maps, music. For a technical audience:
			codebases, networks, pipelines. For creators: cameras, scripts, editing timelines. The source must
			be more familiar than the target — if both require explanation, the analogy fails.
		</div>

		<!-- DEMO 1: Visual Analogy Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Visual Analogy Library</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Each card shows a design concept paired with a visual analogy. Click any card to expand
					the full analogy diagram and see how the parallel structure is made explicit.
				</p>
				<div class="analogy-grid" id="analogy-grid"></div>
				<div class="analogy-reveal" id="analogy-reveal" style="display: none">
					<div class="analogy-concept-label" id="analogy-concept-label"></div>
					<canvas
						class="analogy-canvas-large"
						id="analogy-large-canvas"
						width="560"
						height="280"
						aria-label="Analogy Large Canvas Demonstration"
						role="region"
						tabindex="0"
					></canvas>
					<div
						style="font-size: 12px; color: var(--muted); margin-top: 0.75rem; line-height: 1.6"
						id="analogy-explanation"
					></div>
				</div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Abstract Concept</th>
					<th>Analogy Source</th>
					<th>Structural Parallel</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Visual hierarchy</td>
					<td>Newspaper front page</td>
					<td>Size signals importance; eye reads largest → smallest</td>
				</tr>
				<tr>
					<td>Color contrast</td>
					<td>Traffic lights on a dark night</td>
					<td>Signal pops from field; field provides context</td>
				</tr>
				<tr>
					<td>Alignment grid</td>
					<td>Sheet music staff</td>
					<td>Invisible lines constrain placement to create legible order</td>
				</tr>
				<tr>
					<td>Brand identity system</td>
					<td>A national uniform</td>
					<td>Variant elements (person) + invariant elements (uniform) = recognizable whole</td>
				</tr>
				<tr>
					<td>Spacing system</td>
					<td>Musical rhythm</td>
					<td>Consistent intervals create perceived order; arbitrary intervals create noise</td>
				</tr>
				<tr>
					<td>Typographic weight</td>
					<td>Speaking volume</td>
					<td>Heavy = loud / dominant; light = quiet / subordinate</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══════════════════════════════
     SECTION 2: SEQUENTIAL DESIGN
═══════════════════════════════ -->
	<section id="sequential" class="section">
		<div class="section-header">
			<span class="section-num">08.02</span>
			<h2 class="section-title">Sequential Design &amp; Flow</h2>
		</div>

		<p>
			Most visual communication in educational contexts is not a single image — it is a sequence. A
			diagram that reveals itself in steps, a slide deck that builds argument incrementally, a
			motion graphic that introduces elements one at a time. Sequential design is the practice of
			controlling
			<em>what the viewer sees, in what order, and at what pace</em>.
		</p>

		<p>
			The fundamental rule of information sequence: never show the conclusion before the setup.
			Every piece of information requires context to be understood; that context must arrive first.
			A diagram that shows the final state of a complex system teaches nothing unless the viewer has
			already been walked through the components individually and understands how they relate.
		</p>

		<p>
			Sequence has three modes in visual storytelling. <em>Additive sequence</em> builds up — each
			frame adds one element to the composition until the full picture is assembled. This is ideal
			for showing how systems are constructed or how processes accumulate.
			<em>Transformative sequence</em> shows change — the same element before and after an
			intervention. This is ideal for before/after demonstrations, cause-and-effect explanations,
			and comparison. <em>Narrative sequence</em> tells a story — characters, stakes, and resolution.
			This is ideal for explaining concepts through scenarios that create emotional investment.
		</p>

		<div class="callout sky">
			<div class="callout-label">The One Idea Per Frame Rule</div>
			Each frame in a sequence must introduce exactly one new piece of information. If a frame introduces
			two ideas simultaneously, the viewer's attention splits — neither idea is absorbed fully. This rule
			applies to motion graphics, diagram reveals, slide decks, and tutorial sequences. Violating it feels
			efficient; it is not.
		</div>

		<!-- DEMO 2: Sequence Flow Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Sequential Reveal Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Step through three sequence types applied to the same concept (building a design system).
					Notice how each mode emphasises different aspects of the information, and how the
					one-idea-per-frame rule changes the experience.
				</p>

				<div class="seq-flow-controls" id="seq-flow-controls">
					<button
						class="btn active"
						data-mode="additive"
						onclick={(e) => actions.setSeqMode('additive', e.currentTarget)}
					>
						Additive Build
					</button>
					<button
						class="btn"
						data-mode="transform"
						onclick={(e) => actions.setSeqMode('transform', e.currentTarget)}
					>
						Before → After
					</button>
					<button
						class="btn"
						data-mode="narrative"
						onclick={(e) => actions.setSeqMode('narrative', e.currentTarget)}
					>
						Narrative Arc
					</button>
				</div>

				<div class="seq-stages" id="seq-stages"></div>

				<canvas
					id="seq-canvas"
					width="560"
					height="300"
					aria-label="Seq Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>
				<div class="seq-info" id="seq-info"></div>

				<div style="display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap">
					<button class="btn" id="seq-prev" onclick={(e) => actions.stepSeq(-1)}>← Prev</button>
					<button class="btn amber" id="seq-next" onclick={(e) => actions.stepSeq(1)}>Next →</button
					>
					<button class="btn" onclick={(e) => actions.resetSeq()}>Reset</button>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 3: SIMPLIFICATION
═══════════════════════════════ -->
	<section id="simplification" class="section">
		<div class="section-header">
			<span class="section-num">08.03</span>
			<h2 class="section-title">Simplifying Complex Ideas into Clear Visuals</h2>
		</div>

		<p>
			The most common error in educational diagram design is <em>completeness bias</em> — the impulse
			to include every relevant detail so that nothing important is omitted. The result is a diagram that
			is technically accurate and practically useless. A viewer overwhelmed by simultaneous detail does
			not learn more; they learn less, because the cognitive load of parsing the diagram consumes the
			attention needed to understand the concept.
		</p>

		<p>
			Effective diagram design is an act of strategic omission. The question is not "what should I
			include?" but "what is the <strong>minimum information required</strong> to make this concept understandable?"
			Every element beyond the minimum is a competing signal that reduces the diagram's clarity.
		</p>

		<p>
			The reduction process has four stages. First, identify the <em>core relationship</em> the diagram
			must communicate — typically one cause and one effect, or one comparison, or one process step. Second,
			strip everything else: labels, decorative elements, secondary connections, contextual detail. Third,
			verify that the stripped version still communicates the core relationship. Fourth, add back only
			what is strictly necessary to prevent misunderstanding. If you add an element and the diagram becomes
			clearer, it was necessary. If you add it and nothing changes, it is noise.
		</p>

		<div class="callout violet">
			<div class="callout-label">The Five-Second Test</div>
			Show your diagram to someone unfamiliar with the concept for exactly five seconds, then hide it.
			Ask them to describe what they understood. What they report is what your diagram actually communicates
			— not what you intended it to communicate. If the five-second impression misses the core relationship,
			the diagram has failed regardless of how accurate or complete it is.
		</div>

		<!-- DEMO 3: Diagram Reduction Lab -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Diagram Reduction Lab</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					The same concept — "how visual hierarchy works" — in four stages of reduction. Step
					through each stage and observe the clarity score. The most reduced version communicates
					the concept faster than the complete version.
				</p>

				<div class="reduction-stage-row" id="reduction-stage-row"></div>

				<canvas
					id="reduction-canvas"
					width="560"
					height="300"
					aria-label="Reduction Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>

				<div class="reduction-score-wrap">
					<span style="font-size: 11px; color: var(--muted); min-width: 100px">Clarity score</span>
					<div class="reduction-score-bar-bg">
						<div class="reduction-score-bar" id="reduction-bar" style="width: 0%"></div>
					</div>
					<span
						style="font-size: 12px; font-weight: 600; min-width: 40px; text-align: right"
						id="reduction-score-val"
					></span>
				</div>
				<div class="reduction-note" id="reduction-note"></div>
			</div>
		</div>

		<div class="callout sage">
			<div class="callout-label">When Simplification Goes Too Far</div>
			There is a floor to reduction. A diagram so stripped that it communicates nothing accurate fails
			in the opposite direction. The test is whether the core relationship survives. If the stripped version
			teaches something false, it has been over-reduced. The goal is minimum viable accuracy — not maximum
			minimalism.
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 4: STORYBOARD PANELS
═══════════════════════════════ -->
	<section id="storyboard" class="section">
		<div class="section-header">
			<span class="section-num">08.04</span>
			<h2 class="section-title">Storyboard Panels for Educational Videos</h2>
		</div>

		<p>
			A storyboard is a sequence of annotated frames that plans the visual content of a video before
			any production begins. In professional video production it is mandatory. For a YouTube
			creator, it is the single most underused tool — and the one that most reliably prevents
			expensive re-shoots and confusing final edits.
		</p>

		<p>
			A storyboard frame has three components: a <strong>visual sketch</strong> (rough composition
			of what the viewer sees), a <strong>caption</strong> (what is being said or labelled in this
			moment), and a <strong>transition note</strong> (how the frame changes to the next). The sketch
			does not need to be beautiful — it needs to establish the camera angle, the subject position, and
			the relationship between visual elements and text elements.
		</p>

		<p>
			For educational YouTube content, storyboards serve a specific function beyond visual planning:
			they force you to verify that your
			<em>visual sequence aligns with your verbal sequence</em>. The most common educational video
			failure is an information gap — the narration assumes the viewer can see something that isn't
			on screen yet. Storyboarding surfaces these gaps before editing, when they are cheap to fix.
		</p>

		<table>
			<thead>
				<tr>
					<th>Frame Type</th>
					<th>When to Use</th>
					<th>Key Design Consideration</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Concept intro</td>
					<td>First appearance of a new idea</td>
					<td>Single element, maximum breathing room, label prominent</td>
				</tr>
				<tr>
					<td>Build frame</td>
					<td>Adding one element to an established scene</td>
					<td>New element visually distinct; existing elements slightly dimmed</td>
				</tr>
				<tr>
					<td>Comparison</td>
					<td>Showing two states or options side by side</td>
					<td>
						Strong visual divider; identical scale; contrast treatment signals the difference
					</td>
				</tr>
				<tr>
					<td>Process step</td>
					<td>One action in a sequence</td>
					<td>
						Action visually prominent; input and output both visible; arrow or indicator shows
						direction
					</td>
				</tr>
				<tr>
					<td>Summary</td>
					<td>Closing sequence — the whole picture</td>
					<td>All elements at reduced weight; key takeaway at full weight and contrast</td>
				</tr>
			</tbody>
		</table>

		<!-- DEMO 4: Storyboard Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Storyboard Panel Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Click a panel to select it, choose a frame type, and write a caption. Build a six-panel
					storyboard for a hypothetical explanation. The strip preview at the bottom shows how the
					sequence reads as a whole.
				</p>

				<div class="sb-panels" id="sb-panels"></div>

				<div class="sb-controls">
					<div class="sb-ctrl-label">Selected Panel — Frame Type</div>
					<div class="sb-type-row" id="sb-type-row">
						<button
							class="sb-type-btn active"
							data-type="intro"
							onclick={(e) => actions.setSbType('intro', e.currentTarget)}
						>
							Concept Intro
						</button>
						<button
							class="sb-type-btn"
							data-type="build"
							onclick={(e) => actions.setSbType('build', e.currentTarget)}
						>
							Build Frame
						</button>
						<button
							class="sb-type-btn"
							data-type="compare"
							onclick={(e) => actions.setSbType('compare', e.currentTarget)}
						>
							Comparison
						</button>
						<button
							class="sb-type-btn"
							data-type="process"
							onclick={(e) => actions.setSbType('process', e.currentTarget)}
						>
							Process Step
						</button>
						<button
							class="sb-type-btn"
							data-type="summary"
							onclick={(e) => actions.setSbType('summary', e.currentTarget)}
						>
							Summary
						</button>
						<button
							class="sb-type-btn"
							data-type="empty"
							onclick={(e) => actions.setSbType('empty', e.currentTarget)}
						>
							Empty
						</button>
					</div>
					<div class="sb-ctrl-label" style="margin-top: 0.75rem">
						Caption (what is being said in this frame)
					</div>
					<input
						type="text"
						class="sb-caption-input"
						id="sb-caption-input"
						placeholder="Type the narration or label for this frame…"
						oninput={() => {
							actions.updateSbCaption();
						}}
					/>
				</div>

				<div class="sb-preview-strip" id="sb-preview-strip">
					<div
						style="
									font-size: 10px;
									color: var(--muted);
									writing-mode: vertical-lr;
									transform: rotate(180deg);
									letter-spacing: 0.1em;
									text-transform: uppercase;
									align-self: center;
									padding-right: 0.4rem;
								"
					>
						Sequence
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">08.05</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout amber">
			<div class="callout-label">Exercise 1 — Explainer Diagram</div>
			Choose one concept from your channel's subject matter that viewers consistently find confusing.
			Design an explainer diagram for it using the reduction process:<br /><br />
			1. Write one sentence defining the core relationship to communicate<br />
			2. Sketch the full diagram with all relevant detail<br />
			3. Apply the four-stage reduction — strip until you reach minimum viable accuracy<br />
			4. Apply the five-second test with someone unfamiliar with the concept<br />
			5. Add back only what the five-second test revealed was missing<br /><br />
			The final diagram should fit on a 1280×720 frame with comfortable breathing room.
		</div>

		<div class="callout sage">
			<div class="callout-label">Exercise 2 — Six-Panel Storyboard</div>
			Storyboard a two-minute explanation of a concept using exactly six panels. Constraints:<br
			/><br />
			· Panel 1: Context (what problem are we solving?)<br />
			· Panels 2–4: Three build frames, each introducing one element<br />
			· Panel 5: The full picture assembled<br />
			· Panel 6: The single key takeaway, stripped to minimum elements<br /><br />
			Write a one-line caption for each panel. Then check: does each caption correspond to something visible
			in the panel? If a caption refers to something not sketched, the visual and verbal sequences are
			misaligned — fix the sketch, not the caption.
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 08 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> What is the structural difference between an illustration and a
				visual analogy?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. An illustration uses colour; a visual analogy uses only black and white
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. An illustration shows what something looks like; a visual analogy maps a familiar
					structure onto an unfamiliar concept, borrowing the viewer's existing understanding to
					transfer meaning
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Visual analogies are more complex than illustrations — they require more visual
					elements
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. An illustration is for static media; an analogy is used only in motion graphics
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> The "one idea per frame" rule states that each frame in a sequence
				should introduce exactly one new piece of information. Why?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Multiple ideas per frame require more production time and increase costs
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Viewers can only read one sentence per frame before moving on
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. It makes sequences longer, which improves watch time metrics
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. When two ideas arrive simultaneously, attention splits — neither is fully absorbed. The
					cognitive load of parsing two ideas consumes the attention needed to understand either of
					them
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> A diagram contains eight elements when only three are needed to
				communicate the core concept. What is this error called, and what is its effect?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Visual hierarchy failure — the elements compete because none is more prominent than the
					others
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Analogy failure — the concept has been mapped onto an incorrect source structure
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Completeness bias — the impulse to include all relevant detail overwhelms the diagram
					with competing signals, increasing cognitive load and reducing the amount the viewer
					actually learns
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Sequential failure — the diagram presents information out of order
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> In the diagram reduction process, what is the test for knowing
				when you have reduced too far?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The stripped version teaches something false — the core relationship no longer
					survives. The goal is minimum viable accuracy, not maximum minimalism
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. The diagram has fewer than three visual elements
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. A viewer cannot identify it as belonging to your brand identity
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The diagram looks unfinished or unprofessional to a design-literate audience
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> What specific failure does storyboarding most reliably prevent
				in educational YouTube videos?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Poor thumbnail design — storyboarding includes thumbnail planning
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Colour inconsistency — storyboards define the palette used in each frame
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Information gaps where the narration refers to something not yet visible on screen —
					storyboarding forces alignment between the verbal and visual sequences before editing
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Poor audio quality — storyboards force creators to plan voiceover before recording
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
		<div class="assessment-header">Module Assessment — Visual Communication Critique</div>
		<div class="assessment-sub">Identify the structural problem in each educational visual.</div>
		<div id="assess-wrap"></div>
	</section>

	<div class="nav-links">
		<a href="gd-module-07.html" class="prev-link">← Module 07: Layout</a>
		<a href="gd-module-09.html" class="next-module" style="flex: 1; max-width: 420px">
			<div>
				<div class="next-label">Next — Module 09</div>
				<div class="next-title">Motion as a Design Tool</div>
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
		color: var(--amber);
		border: 1px solid var(--amber);
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
		color: var(--amber);
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
		color: var(--amber);
		border-color: var(--amber);
	}
	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--amber);
		background: var(--surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--amber);
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
		color: var(--amber);
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
		color: var(--violet);
		font-family: 'IBM Plex Mono', monospace;
	}
	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--amber);
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
		font-size: 13px;
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
	:global(.callout.violet) {
		border-color: var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--amber);
		margin-bottom: 0.4rem;
		font-weight: 600;
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
	:global(.callout.violet) .callout-label {
		color: var(--violet);
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
		color: var(--amber);
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
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
		border-color: var(--amber);
		color: var(--amber);
	}
	:global(.btn.active) {
		border-color: var(--amber);
		color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
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
	:global(.btn.sage:hover) {
		border-color: var(--sage);
		color: var(--sage);
	}
	:global(.btn.sage.active) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
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
	:global(.btn.violet:hover) {
		border-color: var(--violet);
		color: var(--violet);
	}
	:global(.btn.violet.active) {
		border-color: var(--violet);
		color: var(--violet);
		background: color-mix(in srgb, var(--violet) 10%, transparent);
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
		color: var(--amber);
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
		background: var(--amber);
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
		color: var(--amber);
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
		color: var(--amber);
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
		border-color: var(--amber);
		color: var(--amber);
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
		border-color: var(--rose);
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
		color: var(--rose);
	}

	/* ═══════════════════════════════════
   DEMO 1: VISUAL ANALOGY BUILDER
═══════════════════════════════════ */
	.analogy-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		margin-bottom: 1rem;
	}
	@media (max-width: 560px) {
		.analogy-grid {
			grid-template-columns: 1fr 1fr;
		}
	}
	:global(.analogy-card) {
		border: 2px solid var(--border);
		cursor: pointer;
		transition: all 0.2s;
		background: var(--code-bg);
		padding: 0;
	}
	:global(.analogy-card:hover) {
		border-color: var(--amber);
	}
	:global(.analogy-card.selected) {
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 8%, var(--code-bg));
	}
	:global(.analogy-card) canvas {
		display: block;
		width: 100%;
	}
	:global(.analogy-card-label) {
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
		padding: 4px 8px;
		border-top: 1px solid var(--border);
		text-align: center;
	}
	.analogy-reveal {
		border: 1px solid var(--border);
		background: var(--raised);
		padding: 1.25rem;
		margin-top: 0.5rem;
		min-height: 80px;
	}
	.analogy-concept-label {
		font-size: 10px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--amber);
		margin-bottom: 0.5rem;
	}
	.analogy-canvas-large {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
		background: var(--code-bg);
	}

	/* ═══════════════════════════════════
   DEMO 2: SEQUENCE FLOW BUILDER
═══════════════════════════════════ */
	.seq-stages {
		display: flex;
		gap: 0;
		overflow-x: auto;
		margin-bottom: 1rem;
	}
	:global(.seq-stage) {
		flex: 0 0 auto;
		width: 120px;
		padding: 0.75rem 0.5rem;
		border: 1px solid var(--border);
		border-right: none;
		cursor: pointer;
		transition: all 0.2s;
		text-align: center;
		user-select: none;
		position: relative;
	}
	:global(.seq-stage:last-child) {
		border-right: 1px solid var(--border);
	}
	:global(.seq-stage:hover),
	:global(.seq-stage.active) {
		background: color-mix(in srgb, var(--amber) 8%, var(--surface));
		border-color: var(--amber);
		z-index: 1;
	}
	:global(.seq-stage:hover) + :global(.seq-stage),
	:global(.seq-stage.active) + :global(.seq-stage) {
		border-left-color: var(--amber);
	}
	:global(.seq-stage-num) {
		font-size: 22px;
		font-weight: 800;
		font-family: 'Syne', sans-serif;
		color: var(--amber);
		line-height: 1;
	}
	:global(.seq-stage-label) {
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
		margin-top: 0.25rem;
	}
	#seq-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
		background: #070b10;
	}
	.seq-info {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.75rem;
		padding: 0.6rem 0.85rem;
		border: 1px solid var(--border);
		background: var(--code-bg);
		min-height: 48px;
		line-height: 1.6;
	}
	.seq-flow-controls {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}

	/* ═══════════════════════════════════
   DEMO 3: DIAGRAM REDUCTION LAB
═══════════════════════════════════ */
	.reduction-stage-row {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1rem;
		flex-wrap: wrap;
		align-items: center;
	}
	:global(.reduction-step-btn) {
		padding: 4px 12px;
		font-size: 11px;
		font-family: 'IBM Plex Mono', monospace;
		border: 1px solid var(--border);
		background: transparent;
		color: var(--muted);
		cursor: pointer;
		transition: all 0.15s;
		position: relative;
	}
	:global(.reduction-step-btn:hover) {
		border-color: var(--amber);
		color: var(--amber);
	}
	:global(.reduction-step-btn.active) {
		border-color: var(--amber);
		color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	:global(.reduction-step-btn) .step-num {
		font-size: 9px;
		color: var(--rose);
		position: absolute;
		top: -6px;
		left: 6px;
		background: var(--bg);
		padding: 0 2px;
	}
	#reduction-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
		background: #070b10;
	}
	.reduction-score-wrap {
		margin-top: 0.75rem;
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	.reduction-score-bar-bg {
		flex: 1;
		height: 4px;
		background: var(--border2);
	}
	.reduction-score-bar {
		height: 100%;
		transition:
			width 0.4s,
			background 0.4s;
	}
	.reduction-note {
		font-size: 12px;
		margin-top: 0.5rem;
		min-height: 2em;
		line-height: 1.6;
		color: var(--muted);
	}

	/* ═══════════════════════════════════
   DEMO 4: STORYBOARD BUILDER
═══════════════════════════════════ */
	.sb-panels {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.75rem;
		margin-bottom: 1rem;
	}
	@media (max-width: 520px) {
		.sb-panels {
			grid-template-columns: 1fr 1fr;
		}
	}
	:global(.sb-panel) {
		border: 2px solid var(--border);
		cursor: pointer;
		transition: all 0.15s;
		position: relative;
	}
	:global(.sb-panel.selected) {
		border-color: var(--amber);
	}
	:global(.sb-panel) canvas {
		display: block;
		width: 100%;
	}
	:global(.sb-panel-footer) {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 4px 6px;
		border-top: 1px solid var(--border);
		background: var(--raised);
		font-size: 9px;
		color: var(--muted);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
	:global(.sb-panel-num) {
		color: var(--amber);
		font-weight: 600;
	}
	.sb-controls {
		border: 1px solid var(--border);
		background: var(--raised);
		padding: 1rem;
	}
	.sb-ctrl-label {
		font-size: 10px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.5rem;
	}
	.sb-type-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-bottom: 0.75rem;
	}
	.sb-type-btn {
		padding: 3px 10px;
		font-size: 11px;
		font-family: 'IBM Plex Mono', monospace;
		border: 1px solid var(--border);
		background: transparent;
		color: var(--muted);
		cursor: pointer;
		transition: all 0.15s;
	}
	.sb-type-btn:hover {
		border-color: var(--amber);
		color: var(--amber);
	}
	.sb-type-btn.active {
		border-color: var(--amber);
		color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	.sb-caption-input {
		width: 100%;
		background: var(--code-bg);
		border: 1px solid var(--border);
		color: var(--text);
		padding: 5px 8px;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 12px;
		outline: none;
		margin-top: 0.5rem;
	}
	.sb-caption-input:focus {
		border-color: var(--amber);
	}
	.sb-preview-strip {
		display: flex;
		gap: 4px;
		margin-top: 1rem;
		padding: 0.75rem;
		background: var(--code-bg);
		border: 1px solid var(--border);
		align-items: flex-end;
		overflow-x: auto;
	}
	:global(.sb-strip-item) {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		flex-shrink: 0;
	}
	:global(.sb-strip-item) canvas {
		display: block;
		border: 1px solid var(--border2);
	}
	:global(.sb-strip-label) {
		font-size: 8px;
		color: var(--muted);
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}

	/* Assessment */
	:global(.assess-question) {
		border: 1px solid var(--border);
		margin: 1.5rem 0;
	}
	:global(.assess-q-hdr) {
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
	:global(.assess-canvas-row) {
		margin: 0.75rem 0;
		overflow: hidden;
		border: 1px solid var(--border2);
	}
	:global(.assess-canvas-row) canvas {
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
	:global(.assess-fb) {
		font-size: 12px;
		margin-top: 0.5rem;
		min-height: 1.2em;
		color: var(--muted);
	}
	:global(.assess-fb.ok) {
		color: var(--sage);
	}
	:global(.assess-fb.bad) {
		color: var(--rose);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
