<script lang="ts">
	/* eslint-disable @typescript-eslint/no-unused-vars, no-undef, @typescript-eslint/no-explicit-any */
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
   DEMO 1: ASSET CHECKLIST
══════════════════════════════════ */
		const CHECKLIST_DATA = [
			{
				module: 'Brand Brief & Strategy',
				items: [
					{
						text: 'Three core brand words defined and written down',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Target audience described — who they are, what they expect visually',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: "One-paragraph brand voice statement with do/don't examples",
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'One brand you admire (reference) and one you want to avoid (anti-reference)',
						tag: 'Important',
						tagColor: 'var(--amber)'
					}
				]
			},
			{
				module: 'Logo System',
				items: [
					{
						text: 'Primary logo lockup (horizontal: mark + wordmark) as SVG',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Secondary logo (stacked or vertical) as SVG',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Icon mark only (for favicon, profile avatar, app icon) as SVG + 512×512 PNG',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Logo on dark background PNG — minimum 300×100px',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{ text: 'Logo on white background PNG', tag: 'Important', tagColor: 'var(--amber)' },
					{
						text: 'Clear-space rule documented with measurement',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Minimum size documented (px at which mark becomes unreadable)',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Three prohibited use examples documented',
						tag: 'Enhance',
						tagColor: 'var(--muted)'
					}
				]
			},
			{
				module: 'Color Palette',
				items: [
					{
						text: 'Five colors defined with HSL and hex values',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Role definitions written for every palette color (background, surface, accent, text, muted)',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'WCAG AA contrast ratio verified for all text-on-background combinations',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Dark-mode and light-mode variants specified if both are used',
						tag: 'Enhance',
						tagColor: 'var(--muted)'
					}
				]
			},
			{
				module: 'Typography System',
				items: [
					{
						text: 'Heading typeface named with weight (e.g. Syne 800)',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Body/UI typeface named with weight',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Type scale documented: heading size / subheading size / body size / label size',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Thumbnail-specific type rules documented (minimum weight, minimum contrast)',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Line height and letter-spacing values for each tier documented',
						tag: 'Enhance',
						tagColor: 'var(--muted)'
					}
				]
			},
			{
				module: 'Production Assets',
				items: [
					{
						text: 'Thumbnail template at 1280×720px with locked brand layers and editable zones',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Channel banner at 2560×1440px with safe zone marked',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Title card (static version) at 1920×1080px',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Title card (animated version) with timeline documented',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Three thumbnail variants produced to test the template',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'YouTube profile avatar at 800×800px (your logo mark in the circle)',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					}
				]
			},
			{
				module: 'Icon Set & Diagram Kit',
				items: [
					{
						text: 'Twelve icons in brand stroke weight and corner radius as SVG',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Icon usage rules documented (stroke weight, grid, minimum size)',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Six reusable diagram components (arrows, callouts, flow nodes, labels)',
						tag: 'Enhance',
						tagColor: 'var(--muted)'
					},
					{
						text: 'Diagram color rules: which palette colors are used for each diagram element type',
						tag: 'Enhance',
						tagColor: 'var(--muted)'
					}
				]
			},
			{
				module: 'Style Guide Document',
				items: [
					{
						text: 'Logo system section with all specifications and prohibited uses',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Colour palette section with role definitions and contrast ratios',
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: "Typography section with scale, weights, and do/don't examples",
						tag: 'Critical',
						tagColor: 'var(--rose)'
					},
					{
						text: 'Shape register section with corner radius, stroke weight, icon grid',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Motion rules section with timing table',
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: "Voice and tone section with paired do/don't examples",
						tag: 'Important',
						tagColor: 'var(--amber)'
					},
					{
						text: 'Usage examples: one correct thumbnail, one correct website header',
						tag: 'Enhance',
						tagColor: 'var(--muted)'
					}
				]
			}
		];

		const checkState = {};

		function buildChecklist() {
			const container = document.getElementById('checklist-container');
			CHECKLIST_DATA.forEach((mod, mi) => {
				const wrap = document.createElement('div');
				wrap.className = 'checklist-module';

				const header = document.createElement('div');
				header.className = 'checklist-module-header';
				const barWrap = document.createElement('div');
				barWrap.className = 'checklist-module-bar';
				const barFill = document.createElement('div');
				barFill.className = 'checklist-module-bar-fill';
				barFill.id = 'module-bar-' + mi;
				barFill.style.width = '0%';
				barWrap.appendChild(barFill);

				const title = document.createElement('div');
				title.className = 'checklist-module-title';
				title.textContent = mod.module;
				const prog = document.createElement('div');
				prog.className = 'checklist-module-progress';
				prog.id = 'module-prog-' + mi;
				prog.textContent = '0 / ' + mod.items.length;
				header.appendChild(title);
				header.appendChild(prog);
				wrap.appendChild(header);
				wrap.appendChild(barWrap);

				const itemsWrap = document.createElement('div');
				itemsWrap.className = 'checklist-items';
				mod.items.forEach((item, ii) => {
					const key = `${mi}-${ii}`;
					checkState[key] = false;
					const div = document.createElement('div');
					div.className = 'checklist-item';
					div.innerHTML = `
        <div class="ci-box"><span class="ci-check">✓</span></div>
        <div class="ci-text">${item.text}</div>
        <div class="ci-tag" style="color:${item.tagColor};border-color:${item.tagColor}">${item.tag}</div>`;
					div.addEventListener('click', () => {
						checkState[key] = !checkState[key];
						div.classList.toggle('done', checkState[key]);
						updateModuleProgress(mi, mod.items.length);
						updateOverallProgress();
					});
					itemsWrap.appendChild(div);
				});
				wrap.appendChild(itemsWrap);
				container.appendChild(wrap);
			});
		}

		function updateModuleProgress(mi, total) {
			const done = CHECKLIST_DATA[mi].items.filter((_, ii) => checkState[`${mi}-${ii}`]).length;
			document.getElementById('module-prog-' + mi).textContent = done + ' / ' + total;
			document.getElementById('module-bar-' + mi).style.width = (done / total) * 100 + '%';
		}

		function updateOverallProgress() {
			const total = Object.keys(checkState).length;
			const done = Object.values(checkState).filter(Boolean).length;
			const pct = Math.round((done / total) * 100);
			document.getElementById('overall-bar').style.width = pct + '%';
			document.getElementById('overall-pct').textContent = pct + '%';
			document.getElementById('overall-label').textContent = done + ' / ' + total + ' items';
			document.getElementById('overall-pct').style.color =
				pct >= 80 ? 'var(--sage)' : pct >= 50 ? 'var(--amber)' : 'var(--amber)';
		}

		buildChecklist();

		/* ══════════════════════════════════
   DEMO 2: STYLE GUIDE VIEWER
══════════════════════════════════ */
		function setSgPage(page, tab) {
			document.querySelectorAll('.sg-tab').forEach((t) => t.classList.remove('active'));
			document.querySelectorAll('.sg-page').forEach((p) => p.classList.remove('active'));
			tab.classList.add('active');
			document.getElementById('sgp-' + page).classList.add('active');
		}

		// Logo variants
		function buildLogoVariants() {
			const wrap = document.getElementById('sg-logo-variants');
			const variants = [
				{ label: 'Primary (H)', ok: true, w: 180, h: 64 },
				{ label: 'Icon only', ok: true, w: 64, h: 64 },
				{ label: 'Reversed', ok: true, w: 180, h: 64 },
				{ label: 'Wrong colour', ok: false, w: 180, h: 64 },
				{ label: 'Busy BG', ok: false, w: 180, h: 64 }
			];
			variants.forEach((v) => {
				const cell = document.createElement('div');
				cell.className = 'sg-logo-variant' + (v.ok ? ' sg-do' : ' sg-dont');
				cell.style.background =
					v.label === 'Reversed'
						? '#fff'
						: v.label === 'Busy BG'
							? "url(\"data:image/svg+xml,%3Csvg width='10' height='10' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='10' height='10' fill='%23234'/%3E%3Crect width='5' height='5' fill='%23345'/%3E%3Crect x='5' y='5' width='5' height='5' fill='%23345'/%3E%3C/svg%3E\")"
							: 'var(--code-bg)';
				const cvs = document.createElement('canvas');
				cvs.width = v.w;
				cvs.height = v.h;
				cvs.style.display = 'block';
				cell.appendChild(cvs);
				const lbl = document.createElement('div');
				lbl.className = 'sg-logo-variant-label';
				lbl.textContent = v.label;
				cell.appendChild(lbl);
				wrap.appendChild(cell);

				const ctx = cvs.getContext('2d');
				const bgCol = v.label === 'Reversed' ? '#fff' : 'transparent';
				ctx.clearRect(0, 0, v.w, v.h);
				const wrongColor = v.label === 'Wrong colour';
				const accentCol = wrongColor ? '#ff0000' : v.label === 'Reversed' ? '#080b0f' : '#38c0e8';
				const textCol = v.label === 'Reversed' ? '#080b0f' : '#ffffff';

				if (v.label === 'Icon only') {
					ctx.strokeStyle = accentCol;
					ctx.lineWidth = 2;
					ctx.beginPath();
					ctx.arc(32, 32, 18, 0, Math.PI * 2);
					ctx.stroke();
					ctx.fillStyle = accentCol;
					ctx.beginPath();
					ctx.arc(32, 32, 6, 0, Math.PI * 2);
					ctx.fill();
				} else {
					// Mark
					ctx.strokeStyle = accentCol;
					ctx.lineWidth = 2;
					ctx.beginPath();
					ctx.arc(22, 32, 14, 0, Math.PI * 2);
					ctx.stroke();
					ctx.fillStyle = accentCol;
					ctx.beginPath();
					ctx.arc(22, 32, 5, 0, Math.PI * 2);
					ctx.fill();
					// Wordmark
					ctx.fillStyle = textCol;
					ctx.font = `800 18px Syne,sans-serif`;
					ctx.fillText('SIGNAL', 44, 38);
					if (wrongColor) {
						ctx.strokeStyle = 'rgba(232,93,138,0.5)';
						ctx.lineWidth = 1;
						ctx.setLineDash([2, 2]);
						ctx.strokeRect(1, 1, v.w - 2, v.h - 2);
						ctx.setLineDash([]);
					}
				}
			});
		}
		buildLogoVariants();

		// Palette chips
		function buildPaletteChips() {
			const wrap = document.getElementById('sg-color-row');
			const colors = [
				{
					name: 'Background',
					role: 'All dark surfaces and canvas backgrounds',
					val: '#080b0f',
					col: '#080b0f'
				},
				{ name: 'Surface', role: 'Card and panel backgrounds', val: '#0d1117', col: '#0d1117' },
				{
					name: 'Sky — Accent',
					role: 'Interactive elements, logo, focal points ONLY',
					val: '#38c0e8',
					col: '#38c0e8'
				},
				{
					name: 'Rose — Secondary',
					role: 'Supporting highlights — one per composition max',
					val: '#e85d8a',
					col: '#e85d8a'
				},
				{
					name: 'Text',
					role: 'All body copy on dark backgrounds',
					val: '#d0dbe8',
					col: '#d0dbe8'
				},
				{
					name: 'Muted',
					role: 'Captions, metadata, secondary labels — never for primary text',
					val: '#5a7090',
					col: '#5a7090'
				}
			];
			colors.forEach((c) => {
				const chip = document.createElement('div');
				chip.className = 'sg-color-chip';
				chip.innerHTML = `
      <div class="sg-color-chip-swatch" style="background:${c.col};border-bottom:1px solid var(--border)"></div>
      <div class="sg-color-chip-info">
        <div class="sg-color-chip-name">${c.name}</div>
        <div class="sg-color-chip-role">${c.role}</div>
        <div class="sg-color-chip-val">${c.val}</div>
      </div>`;
				wrap.appendChild(chip);
			});
		}
		buildPaletteChips();

		// Typography
		function buildTypeContent() {
			const wrap = document.getElementById('sg-type-content');
			const types = [
				{
					sample: 'Design Thinking',
					style: 'font-family:Syne,sans-serif;font-weight:800;font-size:32px;color:#fff',
					name: 'Display Heading',
					specs: [
						'Syne 800',
						'38–52px',
						'Thumbnails, title cards, hero sections',
						'Never below 24px'
					]
				},
				{
					sample: 'Visual Hierarchy',
					style: 'font-family:Syne,sans-serif;font-weight:700;font-size:22px;color:#fff',
					name: 'Section Heading',
					specs: ['Syne 700', '20–26px', 'Section titles, card headlines', 'Line height: 1.2']
				},
				{
					sample: 'How contrast creates clarity',
					style:
						'font-family:IBM Plex Mono,monospace;font-weight:400;font-size:14px;color:var(--text)',
					name: 'Body Copy',
					specs: [
						'IBM Plex Mono 400',
						'13–15px',
						'All running text and explanations',
						'Line height: 1.8'
					]
				},
				{
					sample: 'MODULE 03  ·  TYPOGRAPHY',
					style:
						'font-family:IBM Plex Mono,monospace;font-weight:500;font-size:10px;letter-spacing:0.2em;color:var(--muted);text-transform:uppercase',
					name: 'Label / Eyebrow',
					specs: [
						'IBM Plex Mono 500',
						'9–11px',
						'Labels, metadata, navigation items',
						'Tracking: 0.15–0.25em'
					]
				}
			];
			types.forEach((t) => {
				const row = document.createElement('div');
				row.className = 'sg-type-row';
				row.innerHTML = `
      <div style="${t.style}">${t.sample}</div>
      <div style="font-size:10px;color:var(--muted);margin-top:0.2rem">${t.name}</div>
      <div class="sg-type-spec">${t.specs.map((s) => `<div class="sg-type-tag">${s}</div>`).join('')}</div>`;
				wrap.appendChild(row);
			});
		}
		buildTypeContent();

		// Icons
		function buildIconGrid() {
			const wrap = document.getElementById('sg-icon-grid');
			const icons = [
				{
					label: 'Camera',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						ctx.lineJoin = 'round';
						const p = w * 0.15;
						roundRect(ctx, p, h * 0.28, w - p * 2, h * 0.44, 3);
						ctx.stroke();
						ctx.beginPath();
						ctx.arc(w / 2, h / 2 + h * 0.02, w * 0.13, 0, Math.PI * 2);
						ctx.stroke();
						roundRect(ctx, w * 0.35, h * 0.28 - h * 0.1, w * 0.12, h * 0.1, 2);
						ctx.stroke();
					}
				},
				{
					label: 'Person',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						ctx.beginPath();
						ctx.arc(w / 2, h * 0.3, h * 0.15, 0, Math.PI * 2);
						ctx.stroke();
						ctx.beginPath();
						ctx.moveTo(w * 0.25, h * 0.9);
						ctx.bezierCurveTo(w * 0.25, h * 0.58, w * 0.75, h * 0.58, w * 0.75, h * 0.9);
						ctx.stroke();
					}
				},
				{
					label: 'Document',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						ctx.lineJoin = 'round';
						const fold = w * 0.28;
						ctx.beginPath();
						ctx.moveTo(w * 0.18, h * 0.12);
						ctx.lineTo(w * 0.82 - fold, h * 0.12);
						ctx.lineTo(w * 0.82, h * 0.12 + fold);
						ctx.lineTo(w * 0.82, h * 0.88);
						ctx.lineTo(w * 0.18, h * 0.88);
						ctx.closePath();
						ctx.stroke();
						ctx.beginPath();
						ctx.moveTo(w * 0.82 - fold, h * 0.12);
						ctx.lineTo(w * 0.82 - fold, h * 0.12 + fold);
						ctx.lineTo(w * 0.82, h * 0.12 + fold);
						ctx.stroke();
						[0.42, 0.54, 0.66].forEach((y) => {
							ctx.beginPath();
							ctx.moveTo(w * 0.28, h * y);
							ctx.lineTo(w * 0.72, h * y);
							ctx.stroke();
						});
					}
				},
				{
					label: 'Chart',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						ctx.beginPath();
						ctx.moveTo(w * 0.18, h * 0.82);
						ctx.lineTo(w * 0.18, h * 0.18);
						ctx.stroke();
						ctx.beginPath();
						ctx.moveTo(w * 0.18, h * 0.82);
						ctx.lineTo(w * 0.82, h * 0.82);
						ctx.stroke();
						const pts = [
							[0.3, 0.62],
							[0.45, 0.4],
							[0.6, 0.5],
							[0.75, 0.28]
						];
						ctx.beginPath();
						ctx.moveTo(w * pts[0][0], h * pts[0][1]);
						pts.forEach(([x, y]) => ctx.lineTo(w * x, h * y));
						ctx.stroke();
						pts.forEach(([x, y]) => {
							ctx.beginPath();
							ctx.arc(w * x, h * y, 3, 0, Math.PI * 2);
							ctx.fillStyle = '#38c0e8';
							ctx.fill();
						});
					}
				},
				{
					label: 'Grid',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						const s = w * 0.24;
						[
							[0.18, 0.18],
							[0.5, 0.18],
							[0.18, 0.5],
							[0.5, 0.5]
						].forEach(([x, y]) => {
							roundRect(ctx, w * x, h * y, s, s, 2);
							ctx.stroke();
						});
					}
				},
				{
					label: 'Layers',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						[
							[0.65, 0.24],
							[0.55, 0.42],
							[0.45, 0.6]
						].forEach(([cy], i) => {
							ctx.strokeStyle =
								i === 0 ? 'rgba(56,192,232,0.5)' : i === 1 ? 'rgba(56,192,232,0.75)' : '#38c0e8';
							ctx.beginPath();
							ctx.moveTo(w * 0.2, h * cy);
							ctx.lineTo(w / 2, h * (cy - 0.12));
							ctx.lineTo(w * 0.8, h * cy);
							ctx.lineTo(w / 2, h * (cy + 0.12));
							ctx.closePath();
							ctx.stroke();
						});
					}
				},
				{
					label: 'Eye',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						ctx.beginPath();
						ctx.moveTo(w * 0.16, h / 2);
						ctx.bezierCurveTo(w * 0.36, h * 0.2, w * 0.64, h * 0.2, w * 0.84, h / 2);
						ctx.bezierCurveTo(w * 0.64, h * 0.8, w * 0.36, h * 0.8, w * 0.16, h / 2);
						ctx.stroke();
						ctx.beginPath();
						ctx.arc(w / 2, h / 2, h * 0.14, 0, Math.PI * 2);
						ctx.stroke();
					}
				},
				{
					label: 'Lock',
					fn: (ctx, w, h) => {
						ctx.strokeStyle = '#38c0e8';
						ctx.lineWidth = 1.5;
						ctx.lineCap = 'round';
						ctx.lineJoin = 'round';
						roundRect(ctx, w * 0.22, h * 0.48, w * 0.56, h * 0.4, 3);
						ctx.stroke();
						ctx.beginPath();
						ctx.moveTo(w * 0.35, h * 0.48);
						ctx.lineTo(w * 0.35, h * 0.35);
						ctx.bezierCurveTo(w * 0.35, h * 0.14, w * 0.65, h * 0.14, w * 0.65, h * 0.35);
						ctx.lineTo(w * 0.65, h * 0.48);
						ctx.stroke();
						ctx.fillStyle = '#38c0e8';
						ctx.beginPath();
						ctx.arc(w / 2, h * 0.68, h * 0.06, 0, Math.PI * 2);
						ctx.fill();
					}
				}
			];

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

			icons.forEach((ic) => {
				const cell = document.createElement('div');
				cell.className = 'sg-icon-cell';
				const cvs = document.createElement('canvas');
				cvs.width = 40;
				cvs.height = 40;
				cvs.style.display = 'block';
				const lbl = document.createElement('div');
				lbl.className = 'sg-icon-cell-label';
				lbl.textContent = ic.label;
				cell.appendChild(cvs);
				cell.appendChild(lbl);
				wrap.appendChild(cell);
				const ctx = cvs.getContext('2d');
				ctx.fillStyle = '#0d1117';
				ctx.fillRect(0, 0, 40, 40);
				ic.fn(ctx, 40, 40);
			});
		}
		buildIconGrid();

		// Voice
		function buildVoiceContent() {
			const wrap = document.getElementById('sg-voice-content');
			const pairs = [
				{
					do: 'This module covers three principles that govern every layout decision you will make.',
					dont: "Hey everyone! Today we're going to learn some really cool stuff about layouts that I think you'll totally love!"
				},
				{
					do: 'The rule: never use more than two typefaces in a single composition.',
					dont: 'There are lots of different approaches you could try with typefaces and it really depends on what feels right for your specific situation.'
				},
				{
					do: 'This approach fails. Here is why, and here is what to do instead.',
					dont: 'This approach might not always work perfectly in every case, but it can sometimes be a useful starting point to consider.'
				}
			];
			pairs.forEach((pair) => {
				const div = document.createElement('div');
				div.className = 'sg-voice-pair';
				div.innerHTML = `
      <div class="sg-voice-do">
        <div class="sg-voice-label" style="color:var(--sage)">✓ Write like this</div>
        <div class="sg-voice-text">${pair.do}</div>
      </div>
      <div class="sg-voice-dont">
        <div class="sg-voice-label" style="color:var(--rose)">✗ Not like this</div>
        <div class="sg-voice-text">${pair.dont}</div>
      </div>`;
				wrap.appendChild(div);
			});
		}
		buildVoiceContent();

		/* ══════════════════════════════════
   DEMO 3: EXPORT FORMAT GUIDE
══════════════════════════════════ */
		const EXPORT_FORMATS = [
			{
				fmt: 'SVG',
				type: 'Vector',
				category: 'logo',
				typeColor: 'var(--violet)',
				desc: 'Scalable Vector Graphics. Mathematical paths — no quality loss at any size.',
				uses: [
					'All logo variants (primary, secondary, icon)',
					'Icon set deliverables',
					'Diagrams embedded in web'
				],
				warn: '',
				warnColor: '',
				color: 'var(--violet)'
			},
			{
				fmt: 'PNG',
				type: 'Raster',
				category: 'logo',
				typeColor: 'var(--sky)',
				desc: 'Portable Network Graphics. Lossless compression with full transparency support.',
				uses: [
					'Logo on dark/light backgrounds (512×512, 1024×1024)',
					'Social profile avatar (800×800)',
					'YouTube profile picture (800×800)'
				],
				warn: 'Always export at 2× your display size for retina screens',
				warnColor: 'var(--amber)',
				color: 'var(--sky)'
			},
			{
				fmt: 'JPEG',
				type: 'Raster',
				category: 'video',
				typeColor: 'var(--amber)',
				desc: 'Lossy compression. No transparency. Smallest file size for photographs.',
				uses: [
					'YouTube thumbnails (1280×720)',
					'Channel banner (2560×1440)',
					'Photographic content with no transparency needed'
				],
				warn: 'Never use for logos or anything requiring a transparent background',
				warnColor: 'var(--rose)',
				color: 'var(--amber)'
			},
			{
				fmt: 'WebP',
				type: 'Raster',
				category: 'web',
				typeColor: 'var(--sage)',
				desc: 'Modern web format. Better compression than JPEG/PNG. Supports transparency.',
				uses: [
					'Website images and thumbnails',
					'Next-gen image replacement for PNG and JPEG on web',
					'Favicons (alongside ICO)'
				],
				warn: 'Check browser support — legacy systems may not render WebP correctly',
				warnColor: 'var(--amber)',
				color: 'var(--sage)'
			},
			{
				fmt: 'MP4',
				type: 'Video',
				category: 'video',
				typeColor: 'var(--rose)',
				desc: 'H.264 encoded video. Universal compatibility across platforms.',
				uses: [
					'Animated title card (H.264, 1920×1080, 24fps)',
					'Short motion graphic deliverables',
					'YouTube upload format'
				],
				warn: 'Export at 10–20Mbps for YouTube; lower for social media',
				warnColor: 'var(--amber)',
				color: 'var(--rose)'
			},
			{
				fmt: 'PDF',
				type: 'Vector',
				category: 'print',
				typeColor: 'var(--violet)',
				desc: 'Portable Document Format. Preserves vector data, fonts, and color profiles.',
				uses: ['Style guide document', 'Print-ready logo files', 'Brand brief deliverable'],
				warn: 'Embed all fonts before export — missing fonts break rendering on other systems',
				warnColor: 'var(--rose)',
				color: 'var(--violet)'
			},
			{
				fmt: 'GIF',
				type: 'Raster',
				category: 'web',
				typeColor: 'var(--muted)',
				desc: 'Animated raster images. Limited to 256 colors. Small file size for simple animations.',
				uses: [
					'Simple looping animations on web (prefer WebP or MP4 where possible)',
					'Discord and messaging platform stickers'
				],
				warn: '256 color limit makes GIF unsuitable for photographic content or gradients',
				warnColor: 'var(--rose)',
				color: 'var(--muted)'
			},
			{
				fmt: 'ICO',
				type: 'Raster',
				category: 'web',
				typeColor: 'var(--sky)',
				desc: 'Icon format. Contains multiple size variants (16, 32, 48, 64px) in one file.',
				uses: ['Website favicon', 'Browser tab icon', 'Windows desktop shortcut icon'],
				warn: 'Generate from SVG source, not from PNG — ensures clean rendering at 16px',
				warnColor: 'var(--amber)',
				color: 'var(--sky)'
			}
		];

		let exportFilter = 'all';

		function setExportFilter(filter, btn) {
			exportFilter = filter;
			document.querySelectorAll('#export-filter .btn').forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			renderExportGrid();
		}

		function renderExportGrid() {
			const grid = document.getElementById('export-grid');
			grid.innerHTML = '';
			const filtered =
				exportFilter === 'all'
					? EXPORT_FORMATS
					: EXPORT_FORMATS.filter((f) => f.category === exportFilter);
			filtered.forEach((f) => {
				const card = document.createElement('div');
				card.className = 'export-card';
				card.innerHTML = `
      <div class="export-card-header">
        <div class="export-card-fmt" style="color:${f.color}">${f.fmt}</div>
        <div class="export-card-type" style="color:${f.typeColor};border-color:${f.typeColor}">${f.type}</div>
      </div>
      <div class="export-card-body">
        <div style="color:var(--muted);margin-bottom:0.5rem">${f.desc}</div>
        <div class="export-card-uses">
          ${f.uses.map((u) => `<div class="export-use-item"><div class="export-use-dot" style="background:${f.color}"></div><span style="color:var(--text)">${u}</span></div>`).join('')}
        </div>
        ${f.warn ? `<div class="export-card-warn" style="border-color:${f.warnColor};color:${f.warnColor}">⚠ ${f.warn}</div>` : ''}
      </div>`;
				grid.appendChild(card);
			});
		}

		renderExportGrid();

		/* ══════════════════════════════════
   DEMO 4: SELF-AUDIT
══════════════════════════════════ */
		const AUDIT_QS = [
			{
				cat: 'Identity',
				q: 'Your three core brand words are written down and you have evaluated your last three thumbnails against them.'
			},
			{
				cat: 'Identity',
				q: 'Every element in your logo — mark, wordmark, color — can be justified by reference to your brand brief.'
			},
			{
				cat: 'Colour',
				q: 'Every palette color has a documented role, and you never use a color outside its defined role when producing assets.'
			},
			{
				cat: 'Colour',
				q: 'All text-on-background combinations in your assets pass WCAG AA (4.5:1 minimum contrast ratio).'
			},
			{
				cat: 'Typography',
				q: 'You always use the same two typefaces at the same weights. You have never introduced a third typeface "just for this one piece."'
			},
			{
				cat: 'Typography',
				q: 'Your thumbnail title is always 700+ weight and always passes the 10% scale test.'
			},
			{ cat: 'Layout', q: 'Every asset begins from a template, not from a blank canvas.' },
			{
				cat: 'Layout',
				q: 'Your banner has been tested at mobile crop size (central 50% strip) and all essential content is within the safe zone.'
			},
			{
				cat: 'Consistency',
				q: 'A viewer who encounters your thumbnail, website header, and social post would recognize all three as belonging to the same creator without seeing your channel name.'
			},
			{
				cat: 'Consistency',
				q: 'Your logo mark appears at the same size and in the same position across thumbnails.'
			},
			{
				cat: 'Motion',
				q: 'Your title card uses staggered entry with ease-out. No element animates simultaneously with another.'
			},
			{ cat: 'Motion', q: 'No looping animation plays behind your title text in any video.' }
		];

		const auditAnswers = {};

		function buildAuditQuestions() {
			const wrap = document.getElementById('audit-questions');
			AUDIT_QS.forEach((q, i) => {
				const div = document.createElement('div');
				div.className = 'audit-q-item';
				const hdr = document.createElement('div');
				hdr.className = 'audit-q-header';
				hdr.id = 'aq-hdr-' + i;
				hdr.textContent = q.q;
				const body = document.createElement('div');
				body.className = 'audit-q-body';
				const cat = document.createElement('div');
				cat.className = 'audit-q-cat';
				cat.textContent = q.cat;
				const btns = document.createElement('div');
				btns.className = 'audit-q-btns';
				const yBtn = document.createElement('button');
				yBtn.className = 'audit-q-btn';
				yBtn.textContent = 'Yes';
				const nBtn = document.createElement('button');
				nBtn.className = 'audit-q-btn';
				nBtn.textContent = 'No';
				yBtn.addEventListener('click', () => {
					auditAnswers[i] = 'yes';
					updateAuditBtn(i, 'yes', yBtn, nBtn);
					checkAuditComplete();
				});
				nBtn.addEventListener('click', () => {
					auditAnswers[i] = 'no';
					updateAuditBtn(i, 'no', yBtn, nBtn);
					checkAuditComplete();
				});
				btns.appendChild(yBtn);
				btns.appendChild(nBtn);
				body.appendChild(cat);
				body.appendChild(btns);
				div.appendChild(hdr);
				div.appendChild(body);
				wrap.appendChild(div);
			});
		}

		function updateAuditBtn(i, val, yBtn, nBtn) {
			yBtn.className = 'audit-q-btn' + (val === 'yes' ? ' yes' : '');
			nBtn.className = 'audit-q-btn' + (val === 'no' ? ' no' : '');
			const hdr = document.getElementById('aq-hdr-' + i);
			hdr.className = 'audit-q-header answered-' + val;
		}

		function checkAuditComplete() {
			if (Object.keys(auditAnswers).length < AUDIT_QS.length) return;
			const yesCount = Object.values(auditAnswers).filter((v) => v === 'yes').length;
			const pct = Math.round((yesCount / AUDIT_QS.length) * 100);

			// Category breakdown
			const cats = {};
			AUDIT_QS.forEach((q, i) => {
				if (!cats[q.cat]) cats[q.cat] = { yes: 0, total: 0 };
				cats[q.cat].total++;
				if (auditAnswers[i] === 'yes') cats[q.cat].yes++;
			});
			const weak = Object.entries(cats)
				.filter(([, v]) => v.yes < v.total)
				.map(([k, v]) => `${k}: ${v.yes}/${v.total}`);

			const result = document.getElementById('audit-result');
			result.classList.add('visible');
			const col = pct >= 85 ? 'var(--sage)' : pct >= 70 ? 'var(--amber)' : 'var(--rose)';
			document.getElementById('audit-result-score').textContent = pct + '%';
			document.getElementById('audit-result-score').style.color = col;
			document.getElementById('audit-result-label').textContent =
				yesCount + ' of ' + AUDIT_QS.length + ' criteria met';

			const areas = document.getElementById('audit-result-areas');
			areas.innerHTML = '';
			weak.forEach((area) => {
				const div = document.createElement('div');
				div.className = 'audit-area-item';
				div.style.borderColor = 'var(--amber)';
				div.style.color = 'var(--amber)';
				div.textContent = '↑ ' + area;
				areas.appendChild(div);
			});

			const recEl = document.getElementById('audit-recommendation');
			recEl.textContent =
				pct >= 85
					? '✓ System is production-ready. Proceed to deployment. Schedule a quarterly review in three months.'
					: pct >= 70
						? 'Good foundation. Address the flagged areas before deployment — they represent real consistency gaps that viewers will detect.'
						: 'Significant gaps remain. Do not deploy until the Identity, Colour, and Consistency areas score at least 2/2. A partially-complete system is worse than a deliberately minimal one.';
			recEl.style.color = pct >= 85 ? 'var(--sage)' : pct >= 70 ? 'var(--amber)' : 'var(--rose)';
			result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
		}

		buildAuditQuestions();

		/* ══════════════════════════════════
   QUIZ
══════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;
		const explanations = [
			'Correct. A logo file is a visual — it shows what the logo looks like. A specification adds the rules that govern how the logo must and must not be used: clear-space requirements, minimum sizes, approved backgrounds, and prohibited uses. Without these rules, the file is a decoration, not a system.',
			'Correct. Vector files store geometry as mathematical paths — no pixels, no fixed resolution. The same SVG file renders sharply at 16px for a favicon and at 10,000px for a billboard. Raster files have a fixed pixel grid and degrade when scaled beyond it.',
			'Correct. Consistency is maintained most reliably by design, not discipline. Templates with locked color values, fixed typefaces, and constrained composition zones make correct production the default path. Rule-following is unreliable under time pressure; system design is not.',
			'Correct. JPEG format does not support transparent pixels — any transparent area defaults to white. Logos placed on non-white backgrounds must use PNG (which supports alpha channel transparency) or SVG.',
			"Correct. A rebrand is a strategic decision, not an aesthetic one. It is justified when the existing visual system actively misrepresents the brand's current positioning — not when the designer has grown or when trends have shifted. Evolution within the system is almost always preferable to starting over."
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
					'✗ Revisit the section — focus on the functional purpose of specifications versus assets.';
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

		/* ══════════════════════════════════
   FINAL ASSESSMENT
══════════════════════════════════ */
		const FA_CORRECT = { 1: 1, 2: 0 };
		const FA_OK = {
			1: 'Correct. A brief description is a decoration, not a specification. Clear-space rules tell the designer exactly how much margin is required around the logo (preventing crowding). Minimum size prevents the mark from being used at scales where it becomes illegible. Approved backgrounds prevent the logo from appearing on contexts that compromise legibility. Prohibited uses examples make the rules concrete. Without these, every designer makes different judgment calls.',
			2: 'Correct. Five hex values tell a designer what the palette looks like. They do not tell the designer what each color is for. Without role definitions, a designer might use the accent color (#38c0e8) as a background fill, or use the muted color for headings — technically correct palette usage but systemically wrong. Role definitions transform a list of colors into a decision-making system.'
		};
		const FA_BAD = {
			1: 'Not quite. The typeface (Syne 800) and the hex value are already present. What is absent is the specification of how the logo must and must not be used — clear-space rules, minimum sizes, approved backgrounds, and prohibited use examples. Without these, every designer applies their own judgment, producing inconsistent results.',
			2: 'Not quite. Hex values are sufficient for digital production. The missing element is role definitions — which color serves as the background, which is the interactive accent, which is for body text, which is for secondary labels. Without roles, the colors are ingredients without a recipe.'
		};
		const faAnswered = {};

		function handleFA(el, idx, qNum) {
			if (faAnswered[qNum]) return;
			faAnswered[qNum] = true;
			const optsEl = document.getElementById('fa' + qNum + '-opts');
			optsEl.querySelectorAll('.assess-opt').forEach((b, bi) => {
				b.classList.add('disabled');
				if (bi === FA_CORRECT[qNum]) b.classList.add('correct');
			});
			const fb = document.getElementById('fa' + qNum + '-fb');
			if (idx === FA_CORRECT[qNum]) {
				el.classList.remove('disabled');
				fb.textContent = '✓ ' + FA_OK[qNum];
				fb.className = 'assess-fb ok';
			} else {
				el.classList.add('wrong');
				fb.textContent = '✗ ' + FA_BAD[qNum];
				fb.className = 'assess-fb bad';
			}
		}

		if (typeof buildChecklist === 'function') actions.buildChecklist = buildChecklist;
		if (typeof updateModuleProgress === 'function')
			actions.updateModuleProgress = updateModuleProgress;
		if (typeof updateOverallProgress === 'function')
			actions.updateOverallProgress = updateOverallProgress;
		if (typeof setSgPage === 'function') actions.setSgPage = setSgPage;
		if (typeof buildLogoVariants === 'function') actions.buildLogoVariants = buildLogoVariants;
		if (typeof buildPaletteChips === 'function') actions.buildPaletteChips = buildPaletteChips;
		if (typeof buildTypeContent === 'function') actions.buildTypeContent = buildTypeContent;
		if (typeof buildIconGrid === 'function') actions.buildIconGrid = buildIconGrid;
		if (typeof roundRect === 'function') actions.roundRect = roundRect;
		if (typeof buildVoiceContent === 'function') actions.buildVoiceContent = buildVoiceContent;
		if (typeof setExportFilter === 'function') actions.setExportFilter = setExportFilter;
		if (typeof renderExportGrid === 'function') actions.renderExportGrid = renderExportGrid;
		if (typeof buildAuditQuestions === 'function')
			actions.buildAuditQuestions = buildAuditQuestions;
		if (typeof updateAuditBtn === 'function') actions.updateAuditBtn = updateAuditBtn;
		if (typeof checkAuditComplete === 'function') actions.checkAuditComplete = checkAuditComplete;
		if (typeof handleQuiz === 'function') actions.handleQuiz = handleQuiz;
		if (typeof handleFA === 'function') actions.handleFA = handleFA;

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
		<div style="font-size: 11px; color: var(--muted); text-align: right">
			Module 10 of 10 — Final
		</div>
	</header>

	<div class="module-hero">
		<div class="module-number">10</div>
		<div class="module-tag">Module 10 · Capstone</div>
		<h1 class="module-title">Building Final Assets<br /><span>&amp; Style Guide</span></h1>
		<div class="module-subtitle">
			Finalize your identity system. Produce ready-to-use assets. Document everything.
		</div>
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
			<li><a href="#what-goes-in">What Goes Into a Final Package</a></li>
			<li><a href="#asset-checklist">Asset Checklist</a></li>
			<li><a href="#style-guide-anatomy">Style Guide Anatomy</a></li>
			<li><a href="#export-formats">Export &amp; File Formats</a></li>
			<li><a href="#brand-maintenance">Maintaining Consistency Over Time</a></li>
			<li><a href="#self-audit">Brand Consistency Self-Audit</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#final-assessment">Final Assessment</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Identify every deliverable that constitutes a complete brand identity package</li>
			<li>Understand the structure and purpose of each section of a style guide</li>
			<li>Export assets in the correct formats for each platform and use case</li>
			<li>Evaluate your own brand system for consistency gaps before publishing</li>
		</ul>
	</section>

	<!-- ═══════════════════════════════
     SECTION 1: WHAT GOES IN
═══════════════════════════════ -->
	<section id="what-goes-in" class="section">
		<div class="section-header">
			<span class="section-num">10.01</span>
			<h2 class="section-title">What Goes Into a Final Identity Package</h2>
		</div>

		<p>
			A complete identity package for a YouTube channel and website is not a single file or a single
			deliverable — it is a structured collection of assets organized so that any individual piece
			can be found, understood, and applied without referring back to its creator for guidance. That
			is the test of completion: could someone else produce a new, correct asset using only what you
			have packaged?
		</p>

		<p>
			The package has three components. The <strong>brand brief</strong> (one page of text) defines
			strategy: three core words, audience, voice, and positioning. This was built in Module 6. The
			<strong>style guide</strong>
			(ten to fifteen pages) defines the visual system: logo specifications, palette with role definitions,
			type scale, shape register, spacing system, and usage examples. The
			<strong>asset library</strong> is the collection of production-ready files: logo variants, thumbnail
			templates, title card, icon set, diagram kit, and website layout components. Together these three
			form the deliverable.
		</p>

		<p>
			The most important characteristic of a production-ready package is
			<em>completeness of specification</em>. A logo file is not a specification — it is an asset. A
			logo file accompanied by its clear-space rules, minimum size, approved background variants,
			and prohibited uses is a specification. The difference: an asset tells you what the brand
			looks like; a specification tells you what the brand looks like
			<em>and</em> what it must never look like, and why.
		</p>

		<div class="callout amber">
			<div class="callout-label">The Production-Ready Test</div>
			Give your package to someone who has never seen your channel. Give them a brief: "Produce a thumbnail
			for a new video titled [X] about [Y]." If they produce something that looks like it belongs to your
			brand without asking you any questions, your package is production-ready. If they ask about colors,
			fonts, or proportions, something is missing.
		</div>

		<table>
			<thead>
				<tr>
					<th>Component</th>
					<th>Contents</th>
					<th>Purpose</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Brand Brief</td>
					<td>Three words, audience, voice, positioning, anti-examples</td>
					<td>Strategic filter — every visual decision is evaluated against this</td>
				</tr>
				<tr>
					<td>Style Guide</td>
					<td>Logo system, palette, type, shape, spacing, motion, voice</td>
					<td>Decision-making system — removes judgment calls from asset production</td>
				</tr>
				<tr>
					<td>Logo Package</td>
					<td>Primary, secondary (horizontal), icon-only, each in SVG + PNG + light/dark</td>
					<td>Identity anchor — consistent across every platform</td>
				</tr>
				<tr>
					<td>Thumbnail Template</td>
					<td>Working file with locked brand elements, editable text/image zones</td>
					<td>Enables fast production without re-building hierarchy each time</td>
				</tr>
				<tr>
					<td>Title Card</td>
					<td>Animated + static versions at 1920×1080</td>
					<td>Video identity — the first thing viewers see in each video</td>
				</tr>
				<tr>
					<td>Diagram Set</td>
					<td>Six to twelve reusable diagram components in brand style</td>
					<td>Consistent educational graphics without starting from zero</td>
				</tr>
				<tr>
					<td>Website Kit</td>
					<td>Header, hero section, content blocks, footer — all specced</td>
					<td>Consistent web presence without per-page design decisions</td>
				</tr>
				<tr>
					<td>Icon Set</td>
					<td>Twelve to twenty icons in brand stroke weight and corner radius</td>
					<td>Reusable across thumbnails, diagrams, and web</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══════════════════════════════
     SECTION 2: ASSET CHECKLIST
═══════════════════════════════ -->
	<section id="asset-checklist" class="section">
		<div class="section-header">
			<span class="section-num">10.02</span>
			<h2 class="section-title">Asset Checklist</h2>
		</div>

		<p>
			The checklist below reflects the minimum viable identity package for a YouTube channel and
			accompanying website. Items marked
			<span style="color: var(--rose); font-weight: 600">Critical</span> must be completed before
			publishing. Items marked
			<span style="color: var(--amber); font-weight: 600">Important</span> should be completed
			within the first month. Items marked <span style="color: var(--muted)">Enhance</span> add consistency
			and production speed over time.
		</p>

		<!-- DEMO 1: Interactive Asset Checklist -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Identity Package Checklist</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Check off each item as you complete it. Your progress is saved in this session. Use this
					as a production checklist when building your package.
				</p>
				<div id="checklist-container"></div>
				<div class="overall-progress">
					<span style="font-size: 11px; color: var(--muted)">Overall package completion</span>
					<div class="overall-bar-bg">
						<div class="overall-bar" id="overall-bar" style="width: 0%"></div>
					</div>
					<span class="overall-pct" id="overall-pct">0%</span>
					<span
						class="overall-label"
						id="overall-label"
						style="font-size: 11px; color: var(--muted)">0 / 0 items</span
					>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 3: STYLE GUIDE ANATOMY
═══════════════════════════════ -->
	<section id="style-guide-anatomy" class="section">
		<div class="section-header">
			<span class="section-num">10.03</span>
			<h2 class="section-title">Style Guide Anatomy</h2>
		</div>

		<p>
			A style guide is not a mood board, a showcase of finished work, or a collection of color
			swatches. It is a <em>rulebook</em> — specific enough that a designer who has never worked with
			your brand can produce correct, on-brand assets by following it, and can recognize incorrect, off-brand
			assets and say specifically what is wrong with them.
		</p>

		<p>
			The distinction between a decoration and a specification is the presence of
			<strong>rules</strong> and <strong>anti-examples</strong>. Showing your logo is a decoration.
			Showing your logo with its clear-space rule (minimum X-height margin on all sides), its
			minimum size (32px at which the mark becomes unreadable), and three examples of incorrect use
			(wrong color, on a busy background, with modified proportions) is a specification.
		</p>

		<!-- DEMO 2: Style Guide Viewer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Style Guide Page Viewer</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					A six-section style guide for a hypothetical "Signal" channel. Each section shows both the
					specification and the do/don't examples. Use this as a structural template for your own
					guide.
				</p>
				<div class="sg-nav" id="sg-nav">
					<div
						class="sg-tab active"
						onclick={(e) => actions.setSgPage('logo', e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.setSgPage('logo', e.currentTarget);
							}
						}}
					>
						Logo System
					</div>
					<div
						class="sg-tab"
						onclick={(e) => actions.setSgPage('palette', e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.setSgPage('palette', e.currentTarget);
							}
						}}
					>
						Colour Palette
					</div>
					<div
						class="sg-tab"
						onclick={(e) => actions.setSgPage('type', e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.setSgPage('type', e.currentTarget);
							}
						}}
					>
						Typography
					</div>
					<div
						class="sg-tab"
						onclick={(e) => actions.setSgPage('shape', e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.setSgPage('shape', e.currentTarget);
							}
						}}
					>
						Shape &amp; Icons
					</div>
					<div
						class="sg-tab"
						onclick={(e) => actions.setSgPage('motion', e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.setSgPage('motion', e.currentTarget);
							}
						}}
					>
						Motion Rules
					</div>
					<div
						class="sg-tab"
						onclick={(e) => actions.setSgPage('voice', e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.setSgPage('voice', e.currentTarget);
							}
						}}
					>
						Voice &amp; Tone
					</div>
				</div>

				<!-- LOGO PAGE -->
				<div class="sg-page active" id="sgp-logo">
					<div class="sg-section-label">Logo System — Variants &amp; Usage Rules</div>
					<div class="sg-logo-variants" id="sg-logo-variants">
						<!-- Drawn by JS -->
					</div>
					<div style="font-size: 12px; color: var(--muted); line-height: 1.7; margin-top: 0.75rem">
						<strong style="color: var(--amber)">Clear space rule:</strong> minimum margin equal to
						the cap-height of the wordmark on all sides.<br />
						<strong style="color: var(--amber)">Minimum size:</strong> 32px height for the icon
						mark; 80px height for the full horizontal lockup.<br />
						<strong style="color: var(--amber)">Approved backgrounds:</strong> brand dark (#080b0f),
						white, and mid-grey (#888) only.<br />
						<strong style="color: var(--amber)">Never:</strong> place on a busy photographic background,
						rotate or skew, change the accent color, or use at sizes below minimums.
					</div>
				</div>

				<!-- PALETTE PAGE -->
				<div class="sg-page" id="sgp-palette">
					<div class="sg-section-label">Colour Palette — Roles &amp; Values</div>
					<div
						class="sg-color-row"
						id="sg-color-row"
						style="
									display: grid;
									grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
									gap: 0.5rem;
								"
					></div>
					<div style="margin-top: 1rem; font-size: 12px; color: var(--muted); line-height: 1.7">
						<strong style="color: var(--amber)">Usage rule:</strong> Accent is used only for
						interactive elements, focal points, and the logo mark. It is never used for large
						background areas.<br />
						<strong style="color: var(--amber)">Secondary accent</strong> appears as a supporting
						highlight only — one per composition maximum.<br />
						<strong style="color: var(--amber)">Text color</strong> is used for all body copy. Muted is
						used for captions, metadata, and secondary labels only.
					</div>
				</div>

				<!-- TYPOGRAPHY PAGE -->
				<div class="sg-page" id="sgp-type">
					<div class="sg-section-label">Typography — Scale &amp; Usage</div>
					<div id="sg-type-content"></div>
				</div>

				<!-- SHAPE PAGE -->
				<div class="sg-page" id="sgp-shape">
					<div class="sg-section-label">Shape Register &amp; Icon System</div>
					<div style="font-size: 12px; color: var(--text); margin-bottom: 1rem; line-height: 1.7">
						All shapes use <strong style="color: var(--amber)">sharp geometry</strong> (0–4px corner
						radius). Stroke weight:
						<strong style="color: var(--amber)">1.5px</strong> for all icons at 24px,
						<strong style="color: var(--amber)">2px</strong> at 32px+. No organic or irregular shapes
						in the system.
					</div>
					<div class="sg-icon-grid" id="sg-icon-grid"></div>
					<div style="margin-top: 1rem; font-size: 12px; color: var(--muted); line-height: 1.7">
						<strong style="color: var(--amber)">Consistency rule:</strong> All icons in the set must share
						the same stroke weight and corner radius. Adding a new icon requires matching these two values
						exactly before use.
					</div>
				</div>

				<!-- MOTION PAGE -->
				<div class="sg-page" id="sgp-motion">
					<div class="sg-section-label">Motion Rules — Timing &amp; Easing</div>
					<table>
						<thead>
							<tr>
								<th>Element</th>
								<th>Trigger</th>
								<th>Duration</th>
								<th>Easing</th>
								<th>Distance</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td>Primary title (entrance)</td>
								<td>Scene start</td>
								<td>300ms</td>
								<td>Ease-out cubic</td>
								<td>Y +24px → 0</td>
							</tr>
							<tr>
								<td>Accent bar (entrance)</td>
								<td>T=0ms</td>
								<td>200ms</td>
								<td>Ease-out</td>
								<td>Grow from 0px height</td>
							</tr>
							<tr>
								<td>Secondary text (entrance)</td>
								<td>T=180ms</td>
								<td>260ms</td>
								<td>Ease-out</td>
								<td>Y +16px → 0, opacity 0→1</td>
							</tr>
							<tr>
								<td>Tertiary / labels (entrance)</td>
								<td>T=320ms</td>
								<td>220ms</td>
								<td>Ease-out</td>
								<td>Opacity 0→1 only</td>
							</tr>
							<tr>
								<td>All elements (exit)</td>
								<td>Scene end</td>
								<td>200ms</td>
								<td>Ease-in</td>
								<td>Opacity 1→0</td>
							</tr>
							<tr>
								<td>Scene transition</td>
								<td>Between scenes</td>
								<td>300ms</td>
								<td>Ease-in-out</td>
								<td>Cut or cross-dissolve</td>
							</tr>
						</tbody>
					</table>
					<div style="font-size: 12px; color: var(--muted); margin-top: 0.5rem; line-height: 1.7">
						<strong style="color: var(--amber)">Never:</strong> animate background elements continuously
						while foreground text is present. No looping decorative animations. No duration over 500ms
						for content elements.
					</div>
				</div>

				<!-- VOICE PAGE -->
				<div class="sg-page" id="sgp-voice">
					<div class="sg-section-label">Voice &amp; Tone — Dos and Don'ts</div>
					<div style="font-size: 12px; color: var(--text); margin-bottom: 1rem">
						Core voice words: <strong style="color: var(--amber)">Precise</strong> ·
						<strong style="color: var(--amber)">Rigorous</strong> ·
						<strong style="color: var(--amber)">Direct</strong>
					</div>
					<div id="sg-voice-content"></div>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 4: EXPORT FORMATS
═══════════════════════════════ -->
	<section id="export-formats" class="section">
		<div class="section-header">
			<span class="section-num">10.04</span>
			<h2 class="section-title">Export &amp; File Formats</h2>
		</div>

		<p>
			The format of a file determines where it can be used, how it scales, and what quality it
			preserves. Exporting a logo as a JPEG and using it on a dark background produces a white
			rectangle around the mark — a format error that signals inexperience regardless of how
			well-designed the logo itself is. Format decisions are not aesthetic; they are technical
			prerequisites.
		</p>

		<p>
			The distinction that matters most: <strong>vector</strong> versus <strong>raster</strong>.
			Vector files (SVG, PDF, EPS) store geometry as mathematical paths — they scale to any size
			without quality loss. Raster files (PNG, JPEG, WebP) store a fixed grid of pixels — they
			degrade when scaled beyond their native resolution. All logos must exist as vector files. All
			rendered outputs (thumbnails, banners, frames) are raster files at specific pixel dimensions.
		</p>

		<!-- DEMO 3: Export Format Guide -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Asset Export Reference</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Filter by asset type to see the correct export format, size, and settings for each
					deliverable in your package.
				</p>
				<div class="export-filter" id="export-filter">
					<button
						class="btn active"
						data-filter="all"
						onclick={(e) => actions.setExportFilter('all', e.currentTarget)}
					>
						All
					</button>
					<button
						class="btn"
						data-filter="logo"
						onclick={(e) => actions.setExportFilter('logo', e.currentTarget)}
					>
						Logo
					</button>
					<button
						class="btn"
						data-filter="video"
						onclick={(e) => actions.setExportFilter('video', e.currentTarget)}
					>
						Video
					</button>
					<button
						class="btn"
						data-filter="web"
						onclick={(e) => actions.setExportFilter('web', e.currentTarget)}
					>
						Web
					</button>
					<button
						class="btn"
						data-filter="print"
						onclick={(e) => actions.setExportFilter('print', e.currentTarget)}
					>
						Print
					</button>
				</div>
				<div class="export-grid" id="export-grid"></div>
			</div>
		</div>

		<div class="callout sage">
			<div class="callout-label">The Naming Convention</div>
			Every file in your package should follow a consistent naming pattern:
			<code>brand-asset-variant-size.ext</code>. For example:
			<code>signal-logo-primary-horizontal.svg</code>,
			<code>signal-thumbnail-template-1280x720.fig</code>,
			<code>signal-icon-camera-24.png</code>. Consistent naming means you can find any asset in
			seconds and know its purpose without opening it.
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 5: BRAND MAINTENANCE
═══════════════════════════════ -->
	<section id="brand-maintenance" class="section">
		<div class="section-header">
			<span class="section-num">10.05</span>
			<h2 class="section-title">Maintaining Brand Consistency Over Time</h2>
		</div>

		<p>
			A brand identity system is not finished when it is documented — it is finished when it is
			consistently applied over time. The most common failure is not a bad initial design but
			<em>identity drift</em>: small deviations made under time pressure that accumulate into
			inconsistency. A slightly different accent color in one thumbnail, a different corner radius
			on one icon, a different font weight in one graphic — each individually invisible,
			collectively corrosive.
		</p>

		<p>
			The mechanism that prevents drift is not discipline but <em>system design</em>. A
			well-structured template cannot use the wrong color because the color is locked. A
			well-structured icon grid cannot produce off-register strokes because the stroke weight is a
			shared component. The style guide's job is not to remind you of the rules — it is to make
			violating the rules harder than following them.
		</p>

		<p>
			Three habits sustain consistency over months and years. First:
			<strong>never start from scratch</strong>. Every new asset begins from a template that already
			contains the correct brand elements, not from a blank canvas. Second:
			<strong>quarterly review</strong>. Every three months, audit your three most recent thumbnails
			against the style guide. If any element deviates, update either the asset or the guide — drift
			is always a signal that the system needs correction somewhere. Third:
			<strong>version control</strong>. When the style guide changes, update it with a version
			number and note what changed. "Version 1.2 — updated accent color from #38c0e8 to #42c9f0"
			prevents confusion about which version of the brand is current.
		</p>

		<div class="callout violet">
			<div class="callout-label">When to Rebrand</div>
			A rebrand is justified when the brand's positioning has fundamentally changed — new audience, new
			subject focus, new strategic direction. It is not justified because you have gotten better at design,
			because you are tired of the current look, or because a competitor has a more exciting visual style.
			Evolution within the existing system (refining a color, sharpening a typeface, modernizing an icon)
			is almost always a better choice than starting over.
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 6: SELF-AUDIT
═══════════════════════════════ -->
	<section id="self-audit" class="section">
		<div class="section-header">
			<span class="section-num">10.06</span>
			<h2 class="section-title">Brand Consistency Self-Audit</h2>
		</div>

		<p>
			Before publishing any identity system, run a structured self-audit. The audit questions below
			are organized by the five dimensions of visual consistency. A score of 85% or higher indicates
			a system ready for publication. Below 70% indicates specific areas that need completion before
			assets are deployed.
		</p>

		<!-- DEMO 4: Self-Audit Tool -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Brand Consistency Self-Audit</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Answer each question honestly about your current identity system. The audit generates a
					score and identifies your weakest areas.
				</p>
				<div class="audit-questions" id="audit-questions"></div>
				<div class="audit-result" id="audit-result">
					<div class="audit-result-score" id="audit-result-score"></div>
					<div class="audit-result-label" id="audit-result-label"></div>
					<div class="audit-result-areas" id="audit-result-areas"></div>
					<div
						style="margin-top: 1rem; font-size: 12px; color: var(--muted); line-height: 1.7"
						id="audit-recommendation"
					></div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 10 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · Final module</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> What is the structural difference between a logo file and a logo
				specification?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. A logo file is a raster image; a logo specification is a vector file
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. A logo file shows what the logo looks like. A logo specification also defines
					clear-space rules, minimum sizes, approved background variants, and prohibited uses — it
					tells you what the brand must never look like, not just what it does look like
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. A logo specification is the same as a logo file but in a higher resolution format
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. A logo specification is the brand brief — it describes the strategy behind the logo
					design
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> Why must all logos exist as vector files (SVG, EPS) in addition
				to raster variants?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Vector files are required by YouTube's brand asset upload system
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Vector files are smaller in file size than raster equivalents at the same quality
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Raster files cannot be used on websites — only vector formats work in browsers
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Vector files store geometry as mathematical paths and scale to any size without quality
					loss — a logo used at favicon size (32px) and billboard size (10,000px) from the same
					vector file will both render perfectly
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> What mechanism most effectively prevents identity drift over time?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Reviewing the style guide before producing each new asset
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Keeping the identity simple enough that there are few rules to violate
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. System design — templates with locked brand elements make it harder to violate the
					rules than to follow them, so correct production becomes the default path rather than the
					deliberate one
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Hiring a designer to review every piece of content before it is published
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> A creator exports their thumbnail as a JPEG and places it on a
				dark background. A white rectangle appears around the logo mark. What caused this?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. JPEG does not support transparency — its background defaults to white. Logos on
					non-white backgrounds require PNG (with transparency) or SVG
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. The logo was created with a white fill layer that was accidentally left in the export
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The thumbnail dimensions exceeded YouTube's maximum canvas size
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. JPEG compression artifacts produce visible edges around high-contrast elements
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> When is a full rebrand justified rather than a refinement within
				the existing system?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. When the creator has significantly improved their design skills and the current system
					feels dated
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. When a competitor launches a visually stronger brand identity
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. When the brand's fundamental positioning has changed — new audience, new subject, or
					new strategic direction that the existing visual system actively contradicts
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. After 12–18 months, because brand identities have a natural lifecycle and should be
					refreshed regularly
				</button>
			</div>
			<div class="feedback" id="fb-4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-num">—</div>
			<div class="score-label">questions correct out of 5</div>
		</div>
	</section>

	<!-- FINAL ASSESSMENT: PACKAGE REVIEW -->
	<section id="final-assessment" class="assessment-section" style="border-color: var(--amber)">
		<div class="assessment-header" style="color: var(--amber)">
			Final Assessment — Identity Package Review
		</div>
		<div class="assessment-sub">
			Evaluate two partial style guide sections for specification completeness.
		</div>

		<div style="margin: 1.5rem 0; border: 1px solid var(--border)">
			<div
				style="
							padding: 0.65rem 1rem;
							background: var(--raised);
							border-bottom: 1px solid var(--border);
							font-size: 11px;
							letter-spacing: 0.1em;
							text-transform: uppercase;
							color: var(--muted);
						"
			>
				Section A — Logo Page Review
			</div>
			<div style="padding: 1.25rem">
				<div
					style="
								background: var(--code-bg);
								border: 1px solid var(--border2);
								padding: 1.25rem;
								margin-bottom: 1rem;
								font-size: 12px;
								line-height: 1.8;
							"
				>
					<div
						style="
									font-size: 10px;
									letter-spacing: 0.12em;
									text-transform: uppercase;
									color: var(--muted);
									margin-bottom: 0.75rem;
								"
					>
						Logo System (Excerpt)
					</div>
					<div style="color: var(--text)">
						Our logo uses the Syne typeface in 800 weight with our primary accent color #38c0e8. The
						mark should always appear clearly and should look good on the surfaces where it is used.
						Avoid using the logo in ways that make it hard to read.
					</div>
				</div>
				<div style="font-size: 13px; color: #fff; margin: 0.75rem 0">
					What is missing from this logo specification that would prevent a designer from producing
					correct assets?
				</div>
				<div style="display: flex; flex-direction: column; gap: 0.4rem" id="fa1-opts">
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 0, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 0, 1);
							}
						}}
					>
						A. The typeface name and weight are missing — the designer does not know which font to
						use
					</div>
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 1, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 1, 1);
							}
						}}
					>
						B. Clear-space rules, minimum sizes, approved background variants, and prohibited uses
						are absent — the document describes what the logo looks like but provides no enforceable
						rules about how it must and must not be used
					</div>
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 2, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 2, 1);
							}
						}}
					>
						C. The hex value for the accent color is missing
					</div>
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 3, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 3, 1);
							}
						}}
					>
						D. The specification is complete — a brief description is sufficient for a simple logo
						system
					</div>
				</div>
				<div class="assess-fb" id="fa1-fb"></div>
			</div>
		</div>

		<div style="margin: 1.5rem 0; border: 1px solid var(--border)">
			<div
				style="
							padding: 0.65rem 1rem;
							background: var(--raised);
							border-bottom: 1px solid var(--border);
							font-size: 11px;
							letter-spacing: 0.1em;
							text-transform: uppercase;
							color: var(--muted);
						"
			>
				Section B — Palette Review
			</div>
			<div style="padding: 1.25rem">
				<div
					style="
								background: var(--code-bg);
								border: 1px solid var(--border2);
								padding: 1.25rem;
								margin-bottom: 1rem;
							"
				>
					<div
						style="
									font-size: 10px;
									letter-spacing: 0.12em;
									text-transform: uppercase;
									color: var(--muted);
									margin-bottom: 0.75rem;
								"
					>
						Colour Palette (Excerpt)
					</div>
					<div style="display: flex; gap: 0.5rem; flex-wrap: wrap">
						<div style="text-align: center">
							<div
								style="
											width: 48px;
											height: 32px;
											background: #080b0f;
											border: 1px solid var(--border2);
											margin-bottom: 4px;
										"
							></div>
							<div style="font-size: 9px; color: var(--muted)">#080b0f</div>
						</div>
						<div style="text-align: center">
							<div style="width: 48px; height: 32px; background: #38c0e8; margin-bottom: 4px"></div>
							<div style="font-size: 9px; color: var(--muted)">#38c0e8</div>
						</div>
						<div style="text-align: center">
							<div style="width: 48px; height: 32px; background: #e85d8a; margin-bottom: 4px"></div>
							<div style="font-size: 9px; color: var(--muted)">#e85d8a</div>
						</div>
						<div style="text-align: center">
							<div style="width: 48px; height: 32px; background: #d0dbe8; margin-bottom: 4px"></div>
							<div style="font-size: 9px; color: var(--muted)">#d0dbe8</div>
						</div>
						<div style="text-align: center">
							<div style="width: 48px; height: 32px; background: #5a7090; margin-bottom: 4px"></div>
							<div style="font-size: 9px; color: var(--muted)">#5a7090</div>
						</div>
					</div>
				</div>
				<div style="font-size: 13px; color: #fff; margin: 0.75rem 0">
					The palette shows five colors with hex values. What critical information is absent that
					would make this a functional specification?
				</div>
				<div style="display: flex; flex-direction: column; gap: 0.4rem" id="fa2-opts">
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 0, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 0, 0);
							}
						}}
					>
						A. Role definitions are missing — without knowing which color is the background, which
						is the accent for interactive elements, which is for body text, and which is
						muted/secondary, a designer cannot make consistent color decisions. The list of swatches
						is a decoration, not a system.
					</div>
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 1, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 1, 0);
							}
						}}
					>
						B. HSL values are missing — hex values alone are insufficient for a production system
					</div>
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 2, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 2, 0);
							}
						}}
					>
						C. The palette has too few colors — a complete system requires at least eight swatches
					</div>
					<div
						class="assess-opt"
						onclick={(e) => actions.handleFA(e.currentTarget, 3, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleFA(e.currentTarget, 3, 0);
							}
						}}
					>
						D. Accessibility contrast ratios are missing for each color combination
					</div>
				</div>
				<div class="assess-fb" id="fa2-fb"></div>
			</div>
		</div>
	</section>

	<!-- COMPLETION BANNER -->
	<div class="completion-banner">
		<h2 class="completion-title">Course <span>Complete.</span></h2>
		<p class="completion-sub">
			You have covered the full spectrum of graphic design fundamentals — from the invisible
			structure behind good design to the motion principles that bring static work to life. The ten
			modules below now form your working reference.
		</p>
		<div class="completion-modules">
			<span class="completion-module-tag done">01 — What Design Is</span>
			<span class="completion-module-tag done">02 — Composition</span>
			<span class="completion-module-tag done">03 — Typography</span>
			<span class="completion-module-tag done">04 — Color Theory</span>
			<span class="completion-module-tag done">05 — Shape Language</span>
			<span class="completion-module-tag done">06 — Brand Identity</span>
			<span class="completion-module-tag done">07 — Layout</span>
			<span class="completion-module-tag done">08 — Story Visuals</span>
			<span class="completion-module-tag done">09 — Motion</span>
			<span class="completion-module-tag done">10 — Final Assets</span>
		</div>
	</div>

	<!-- FINAL NAV -->
	<div class="final-nav">
		<a href="gd-module-09.html" class="prev-link">← Module 09: Motion</a>
		<div class="course-complete-badge">
			<div class="ccb-icon">◈</div>
			<div class="ccb-text">
				<div class="ccb-title">Graphic Design &amp; Visual Storytelling</div>
				<div class="ccb-sub">10 modules · Theory · Practice · Applied brand-building</div>
			</div>
		</div>
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
		max-width: 660px;
	}
	.module-title span {
		color: var(--amber);
	}
	.module-subtitle {
		font-size: 13px;
		color: var(--muted);
		margin-top: 0.75rem;
		letter-spacing: 0.05em;
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
	:global(.callout.sky) {
		border-color: var(--sky);
		background: color-mix(in srgb, var(--sky) 5%, var(--surface));
	}
	:global(.callout.violet) {
		border-color: var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
	}
	:global(.callout.warn) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 5%, var(--surface));
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
	:global(.callout.sky) .callout-label {
		color: var(--sky);
	}
	:global(.callout.violet) .callout-label {
		color: var(--violet);
	}
	:global(.callout.warn) .callout-label {
		color: var(--rose);
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
	:global(.btn.sage:hover) {
		border-color: var(--sage);
		color: var(--sage);
	}
	:global(.btn.sage.active) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
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
	:global(.three-col) {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1rem;
	}
	@media (max-width: 560px) {
		:global(.three-col) {
			grid-template-columns: 1fr 1fr;
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

	/* ════════════════════════════════
   DEMO 1: ASSET CHECKLIST
════════════════════════════════ */
	:global(.checklist-module) {
		margin-bottom: 1.5rem;
		border: 1px solid var(--border);
	}
	:global(.checklist-module-header) {
		padding: 0.65rem 1rem;
		background: var(--raised);
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-bottom: 1px solid var(--border);
	}
	:global(.checklist-module-title) {
		font-family: 'Syne', sans-serif;
		font-size: 14px;
		font-weight: 700;
		color: #fff;
	}
	:global(.checklist-module-progress) {
		font-size: 10px;
		color: var(--muted);
		letter-spacing: 0.1em;
	}
	:global(.checklist-module-bar) {
		height: 2px;
		background: var(--border);
	}
	:global(.checklist-module-bar-fill) {
		height: 100%;
		background: var(--amber);
		transition: width 0.4s;
	}
	:global(.checklist-items) {
		padding: 0.5rem 0;
	}
	:global(.checklist-item) {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 0.5rem 1rem;
		cursor: pointer;
		transition: background 0.15s;
		border-bottom: 1px solid var(--border);
	}
	:global(.checklist-item:last-child) {
		border-bottom: none;
	}
	:global(.checklist-item:hover) {
		background: color-mix(in srgb, var(--amber) 3%, var(--surface));
	}
	:global(.checklist-item.done .ci-box) {
		background: color-mix(in srgb, var(--sage) 15%, transparent);
		border-color: var(--sage);
	}
	:global(.checklist-item.done .ci-check) {
		opacity: 1;
	}
	:global(.checklist-item.done .ci-text) {
		color: var(--muted);
		text-decoration: line-through;
		text-decoration-color: var(--muted);
	}
	:global(.ci-box) {
		width: 18px;
		height: 18px;
		border: 1px solid var(--border2);
		flex-shrink: 0;
		margin-top: 2px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
	}
	:global(.ci-check) {
		color: var(--sage);
		font-size: 11px;
		font-weight: 700;
		opacity: 0;
		transition: opacity 0.2s;
	}
	:global(.ci-text) {
		font-size: 12px;
		line-height: 1.5;
		flex: 1;
	}
	:global(.ci-tag) {
		font-size: 9px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		padding: 1px 5px;
		border: 1px solid;
		border-radius: 1px;
		flex-shrink: 0;
		margin-top: 3px;
	}
	.overall-progress {
		padding: 1rem;
		background: var(--raised);
		border: 1px solid var(--border);
		margin-top: 1rem;
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	.overall-bar-bg {
		flex: 1;
		height: 6px;
		background: var(--border2);
	}
	.overall-bar {
		height: 100%;
		background: linear-gradient(90deg, var(--amber), var(--sage));
		transition: width 0.5s;
	}
	.overall-label {
		font-size: 11px;
		color: var(--muted);
		min-width: 80px;
		text-align: right;
	}
	.overall-pct {
		font-size: 14px;
		font-weight: 700;
		color: var(--amber);
		min-width: 40px;
		text-align: right;
	}

	/* ════════════════════════════════
   DEMO 2: STYLE GUIDE VIEWER
════════════════════════════════ */
	.sg-nav {
		display: flex;
		gap: 0;
		border-bottom: 1px solid var(--border);
		overflow-x: auto;
	}
	.sg-tab {
		padding: 0.55rem 1.1rem;
		font-size: 11px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--muted);
		cursor: pointer;
		border-bottom: 2px solid transparent;
		transition: all 0.15s;
		white-space: nowrap;
		user-select: none;
	}
	.sg-tab:hover {
		color: var(--text);
	}
	.sg-tab.active {
		color: var(--amber);
		border-bottom-color: var(--amber);
	}
	.sg-page {
		padding: 1.5rem;
		min-height: 340px;
		display: none;
	}
	.sg-page.active {
		display: block;
	}

	/* Style guide page internals */
	.sg-section-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.75rem;
		padding-bottom: 0.4rem;
		border-bottom: 1px solid var(--border);
	}
	.sg-logo-variants {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		margin-bottom: 1.5rem;
	}
	:global(.sg-logo-variant) {
		border: 1px solid var(--border);
		padding: 1.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--code-bg);
		min-width: 130px;
		min-height: 80px;
		position: relative;
	}
	:global(.sg-logo-variant-label) {
		position: absolute;
		bottom: 4px;
		right: 6px;
		font-size: 8px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
	}
	:global(.sg-dont) {
		border-color: var(--rose) !important;
	}
	:global(.sg-dont::before) {
		content: '✗';
		position: absolute;
		top: 4px;
		left: 6px;
		font-size: 10px;
		color: var(--rose);
		font-weight: 700;
	}
	:global(.sg-do) {
		border-color: var(--sage) !important;
	}
	:global(.sg-do::before) {
		content: '✓';
		position: absolute;
		top: 4px;
		left: 6px;
		font-size: 10px;
		color: var(--sage);
		font-weight: 700;
	}
	.sg-color-row {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}
	:global(.sg-color-chip) {
		width: 100%;
		border: 1px solid var(--border);
	}
	:global(.sg-color-chip-swatch) {
		height: 40px;
	}
	:global(.sg-color-chip-info) {
		padding: 0.35rem 0.5rem;
		background: var(--raised);
	}
	:global(.sg-color-chip-name) {
		font-size: 10px;
		font-weight: 600;
		color: var(--text);
	}
	:global(.sg-color-chip-role) {
		font-size: 9px;
		color: var(--muted);
		letter-spacing: 0.06em;
	}
	:global(.sg-color-chip-val) {
		font-size: 9px;
		color: var(--violet);
	}
	:global(.sg-type-row) {
		margin-bottom: 1rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid var(--border);
	}
	:global(.sg-type-row:last-child) {
		border-bottom: none;
	}
	:global(.sg-type-spec) {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-top: 0.25rem;
	}
	:global(.sg-type-tag) {
		font-size: 9px;
		padding: 1px 6px;
		border: 1px solid var(--border);
		color: var(--muted);
		letter-spacing: 0.08em;
	}
	.sg-icon-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
		gap: 0.5rem;
	}
	:global(.sg-icon-cell) {
		border: 1px solid var(--border);
		background: var(--code-bg);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0.6rem 0.4rem;
		gap: 0.3rem;
	}
	:global(.sg-icon-cell) canvas {
		display: block;
	}
	:global(.sg-icon-cell-label) {
		font-size: 8px;
		color: var(--muted);
		letter-spacing: 0.06em;
		text-align: center;
		text-transform: uppercase;
	}
	:global(.sg-voice-pair) {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}
	:global(.sg-voice-do) {
		border: 1px solid var(--sage);
		padding: 0.75rem;
		background: color-mix(in srgb, var(--sage) 5%, var(--code-bg));
	}
	:global(.sg-voice-dont) {
		border: 1px solid var(--rose);
		padding: 0.75rem;
		background: color-mix(in srgb, var(--rose) 5%, var(--code-bg));
	}
	:global(.sg-voice-label) {
		font-size: 9px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		margin-bottom: 0.35rem;
		font-weight: 600;
	}
	:global(.sg-voice-text) {
		font-size: 11px;
		color: var(--text);
		line-height: 1.5;
	}

	/* ════════════════════════════════
   DEMO 3: EXPORT FORMAT GUIDE
════════════════════════════════ */
	.export-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
		gap: 1rem;
	}
	:global(.export-card) {
		border: 1px solid var(--border);
		background: var(--code-bg);
	}
	:global(.export-card-header) {
		padding: 0.6rem 0.85rem;
		border-bottom: 1px solid var(--border);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	:global(.export-card-fmt) {
		font-family: 'Syne', sans-serif;
		font-size: 16px;
		font-weight: 800;
		letter-spacing: 0.05em;
	}
	:global(.export-card-type) {
		font-size: 9px;
		padding: 2px 6px;
		border: 1px solid;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	:global(.export-card-body) {
		padding: 0.75rem 0.85rem;
		font-size: 11px;
		line-height: 1.7;
	}
	:global(.export-card-uses) {
		margin-top: 0.4rem;
	}
	:global(.export-use-item) {
		display: flex;
		align-items: baseline;
		gap: 0.4rem;
		padding: 0.15rem 0;
	}
	:global(.export-use-dot) {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		flex-shrink: 0;
		margin-top: 5px;
	}
	:global(.export-card-warn) {
		font-size: 10px;
		margin-top: 0.5rem;
		padding: 4px 8px;
		border-left: 2px solid;
	}
	.export-filter {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-bottom: 1rem;
	}

	/* ════════════════════════════════
   DEMO 4: CONSISTENCY SELF-AUDIT
════════════════════════════════ */
	.audit-questions {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	:global(.audit-q-item) {
		border: 1px solid var(--border);
		background: var(--code-bg);
	}
	:global(.audit-q-header) {
		padding: 0.65rem 1rem;
		border-bottom: 1px solid var(--border);
		font-size: 12px;
		color: var(--text);
	}
	:global(.audit-q-header.answered-yes) {
		border-bottom-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--code-bg));
	}
	:global(.audit-q-header.answered-no) {
		border-bottom-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 5%, var(--code-bg));
	}
	:global(.audit-q-body) {
		padding: 0.5rem 1rem;
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}
	:global(.audit-q-cat) {
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
		min-width: 80px;
	}
	:global(.audit-q-btns) {
		display: flex;
		gap: 0.4rem;
		margin-left: auto;
	}
	:global(.audit-q-btn) {
		padding: 3px 14px;
		font-size: 11px;
		font-family: 'IBM Plex Mono', monospace;
		border: 1px solid var(--border);
		background: transparent;
		color: var(--muted);
		cursor: pointer;
		transition: all 0.15s;
	}
	:global(.audit-q-btn.yes) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
	}
	:global(.audit-q-btn.no) {
		border-color: var(--rose);
		color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
	}
	.audit-result {
		margin-top: 1.25rem;
		padding: 1.25rem;
		border: 1px solid var(--border);
		background: var(--raised);
		display: none;
	}
	:global(.audit-result.visible) {
		display: block;
	}
	.audit-result-score {
		font-family: 'Syne', sans-serif;
		font-size: 42px;
		font-weight: 800;
		line-height: 1;
	}
	.audit-result-label {
		font-size: 11px;
		color: var(--muted);
		margin-top: 0.2rem;
	}
	.audit-result-areas {
		margin-top: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
	:global(.audit-area-item) {
		font-size: 12px;
		padding: 0.4rem 0.75rem;
		border-left: 2px solid;
	}

	/* Course completion */
	.completion-banner {
		margin: 3rem 0;
		padding: 2.5rem;
		background: var(--surface);
		border: 1px solid var(--amber);
		position: relative;
		overflow: hidden;
	}
	.completion-banner::before {
		content: '';
		position: absolute;
		inset: 0;
		background: radial-gradient(
			ellipse at 30% 50%,
			color-mix(in srgb, var(--amber) 8%, transparent),
			transparent 70%
		);
		pointer-events: none;
	}
	.completion-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(22px, 4vw, 36px);
		font-weight: 800;
		color: #fff;
		margin-bottom: 0.5rem;
	}
	.completion-title span {
		color: var(--amber);
	}
	.completion-sub {
		font-size: 13px;
		color: var(--muted);
		max-width: 560px;
		line-height: 1.7;
	}
	.completion-modules {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-top: 1.5rem;
	}
	.completion-module-tag {
		font-size: 9px;
		padding: 2px 8px;
		border: 1px solid var(--border);
		color: var(--muted);
		letter-spacing: 0.08em;
	}
	.completion-module-tag.done {
		border-color: var(--amber);
		color: var(--amber);
		background: color-mix(in srgb, var(--amber) 8%, transparent);
	}

	/* Final nav — no next, just prev */
	.final-nav {
		display: flex;
		align-items: center;
		margin-top: 4rem;
		gap: 1rem;
		flex-wrap: wrap;
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
	.course-complete-badge {
		flex: 1;
		max-width: 380px;
		border: 1px solid var(--amber);
		padding: 1.25rem 1.75rem;
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
		display: flex;
		align-items: center;
		gap: 1.25rem;
	}
	.ccb-icon {
		font-size: 32px;
		flex-shrink: 0;
	}
	.ccb-text .ccb-title {
		font-family: 'Syne', sans-serif;
		font-size: 15px;
		font-weight: 700;
		color: var(--amber);
	}
	.ccb-text .ccb-sub {
		font-size: 11px;
		color: var(--muted);
		margin-top: 0.1rem;
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
