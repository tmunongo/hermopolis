<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-unused-expressions */
	import { onMount } from 'svelte';

	let actions = {};

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
		/* ═══════════════════════════════════
   READING PROGRESS
═══════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const progress = el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight);
			const bar = document.getElementById('reading-progress');
			const pct = Math.round(Math.max(0, Math.min(1, progress)) * 100);
			bar.style.width = pct + '%';
			bar.setAttribute('aria-valuenow', String(pct));
		});

		/* ═══════════════════════════════════
   SHAPE PERSONALITY EXPLORER
═══════════════════════════════════ */
		const shapeCanvas = document.getElementById('shape-canvas');
		const sCtx = shapeCanvas.getContext('2d');
		const SW = shapeCanvas.width,
			SH = shapeCanvas.height;

		function lerp(a, b, t) {
			return a + (b - a) * t;
		}

		function drawShapeExplorer() {
			const corner = parseInt(document.getElementById('axis-corner').value) / 100; // 0=round,1=sharp
			const geom = parseInt(document.getElementById('axis-geom').value) / 100; // 0=organic,1=geometric

			sCtx.fillStyle = '#0a0f18';
			sCtx.fillRect(0, 0, SW, SH);

			const cx = SW / 2,
				cy = SH / 2;

			// Grid lines (appear as geom increases)
			if (geom > 0.3) {
				const g = (geom - 0.3) / 0.7;
				sCtx.strokeStyle = `rgba(232,93,138,${g * 0.06})`;
				sCtx.lineWidth = 1;
				for (let x = 0; x < SW; x += 30) {
					sCtx.beginPath();
					sCtx.moveTo(x, 0);
					sCtx.lineTo(x, SH);
					sCtx.stroke();
				}
				for (let y = 0; y < SH; y += 30) {
					sCtx.beginPath();
					sCtx.moveTo(0, y);
					sCtx.lineTo(SW, y);
					sCtx.stroke();
				}
			}

			// Main mark — morphs shape
			const mainR = lerp(65, 55, geom);
			const radius = lerp(mainR, corner < 0.1 ? mainR : 0, corner);

			// Color — warm when organic/round, cool when geometric/sharp
			const hue = lerp(340, 200, geom * 0.4 + corner * 0.6);
			const sat = lerp(60, 80, corner);
			const lit = lerp(55, 50, geom);

			sCtx.fillStyle = `hsl(${hue},${sat}%,${lit}%)`;
			sCtx.shadowColor = `hsl(${hue},${sat}%,${lit}%)`;
			sCtx.shadowBlur = 22;

			if (geom < 0.3) {
				// Organic blob — using sin wave deformation
				sCtx.beginPath();
				const pts = 80;
				for (let i = 0; i <= pts; i++) {
					const angle = (i / pts) * Math.PI * 2;
					const organicness = 1 - geom / 0.3;
					const noise =
						Math.sin(angle * 3 + 0.5) * 14 * organicness +
						Math.sin(angle * 5 + 1.2) * 8 * organicness +
						Math.sin(angle * 7 + 2.1) * 5 * organicness;
					const r = mainR + noise;
					const px = cx + Math.cos(angle) * r;
					const py = cy + Math.sin(angle) * r;
					if (i === 0) sCtx.moveTo(px, py);
					else sCtx.lineTo(px, py);
				}
				sCtx.closePath();
				sCtx.fill();
			} else if (geom < 0.65) {
				// Rounded rect or circle
				const t = (geom - 0.3) / 0.35;
				const w = lerp(mainR * 1.4, mainR * 2, t);
				const h = lerp(mainR * 1.4, mainR * 1.4, t);
				const r = lerp(mainR * 0.7, mainR * (1 - corner) * 0.5, t);
				roundRect(sCtx, cx - w / 2, cy - h / 2, w, h, r * (1 - corner * 0.8));
				sCtx.fill();
			} else {
				// Sharp geometric — rect or triangle based on corner
				const t = (geom - 0.65) / 0.35;
				if (corner > 0.6) {
					// Triangle
					const tc = (corner - 0.6) / 0.4;
					const s = lerp(80, 100, tc);
					sCtx.beginPath();
					sCtx.moveTo(cx, cy - s);
					sCtx.lineTo(cx + s * 0.866, cy + s * 0.5);
					sCtx.lineTo(cx - s * 0.866, cy + s * 0.5);
					sCtx.closePath();
					sCtx.fill();
				} else {
					const w = lerp(90, 110, t);
					roundRect(
						sCtx,
						cx - w / 2,
						cy - w / 2,
						w,
						w,
						corner < 0.15 ? w * 0.5 : (1 - corner) * 12
					);
					sCtx.fill();
				}
			}

			sCtx.shadowBlur = 0;

			// Secondary element
			if (geom > 0.5) {
				sCtx.fillStyle = `hsla(${hue + 30}, 70%, 70%, 0.22)`;
				const sr = lerp(22, 15, corner);
				const offX = lerp(0, 44, geom);
				const offY = lerp(0, -38, geom);
				if (corner > 0.55) {
					sCtx.beginPath();
					sCtx.moveTo(cx + offX, cy + offY - sr);
					sCtx.lineTo(cx + offX + sr, cy + offY + sr * 0.6);
					sCtx.lineTo(cx + offX - sr, cy + offY + sr * 0.6);
					sCtx.closePath();
					sCtx.fill();
				} else {
					sCtx.beginPath();
					sCtx.arc(cx + offX, cy + offY, sr, 0, Math.PI * 2);
					sCtx.fill();
				}
			}

			// Personality tags
			updatePersonalityTags(corner, geom);
		}

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

		const TAG_DATA = [
			{ label: 'Approachable', fn: (c, g) => (1 - c) * (1 - g) },
			{ label: 'Trustworthy', fn: (c, g) => (1 - c) * 0.7 },
			{ label: 'Warm', fn: (c, g) => (1 - c) * (1 - g * 0.5) },
			{ label: 'Natural', fn: (c, g) => (1 - g) * (1 - c * 0.4) },
			{ label: 'Precise', fn: (c, g) => g * 0.8 + c * 0.2 },
			{ label: 'Geometric', fn: (c, g) => g },
			{ label: 'Modern', fn: (c, g) => g * 0.7 + c * 0.3 },
			{ label: 'Sharp', fn: (c, g) => c },
			{ label: 'Dynamic', fn: (c, g) => c * 0.8 },
			{ label: 'Aggressive', fn: (c, g) => c * g },
			{ label: 'Technical', fn: (c, g) => g * c * 0.9 },
			{ label: 'Wild', fn: (c, g) => c * (1 - g) * 0.85 }
		];

		const TAG_COLORS = {
			Approachable: 'var(--sage)',
			Trustworthy: 'var(--sky)',
			Warm: 'var(--amber)',
			Natural: 'var(--sage)',
			Precise: 'var(--sky)',
			Geometric: 'var(--violet)',
			Modern: 'var(--sky)',
			Sharp: 'var(--rose)',
			Dynamic: 'var(--rose)',
			Aggressive: 'var(--rose)',
			Technical: 'var(--violet)',
			Wild: 'var(--amber)'
		};

		function updatePersonalityTags(corner, geom) {
			const scored = TAG_DATA.map((t) => ({ ...t, score: t.fn(corner, geom) }))
				.filter((t) => t.score > 0.35)
				.sort((a, b) => b.score - a.score)
				.slice(0, 5);

			const wrap = document.getElementById('personality-tags');
			wrap.innerHTML = scored
				.map((t) => {
					const col = TAG_COLORS[t.label] || 'var(--muted)';
					return `<span class="p-tag" style="color:${col};border-color:${col};background:color-mix(in srgb,${col} 10%,transparent)">${t.label}</span>`;
				})
				.join('');

			const desc = document.getElementById('shape-desc');
			const top = scored[0];
			if (!top) {
				desc.textContent = '';
				return;
			}

			const descs = {
				Approachable:
					'Rounded organic forms feel safe and familiar — ideal for consumer-facing brands, educational content, and anything requiring trust before expertise.',
				Warm: 'Soft irregular shapes mirror natural forms. This register works for wellness, food, crafts, and any brand that wants to feel human rather than institutional.',
				Natural:
					'Organic irregularity signals authenticity — something that grew rather than was engineered. Powerful for brands emphasising craft, sustainability, or personal voice.',
				Precise:
					'Geometric precision communicates intellectual control. This register suits analytical, technical, or research-based content where rigor is a core value.',
				Geometric:
					'Pure mathematical forms communicate that every element was a considered decision. This is the register of design-conscious and systems-thinking brands.',
				Modern:
					'Geometric clarity with controlled sharpness reads as contemporary and professional — the default register for tech products and digital services.',
				Sharp:
					'Angular forms create immediate visual tension. They work for high-energy content but must be used with restraint — sustained sharpness is fatiguing.',
				Dynamic:
					'Triangular geometry implies directionality and forward movement. Strong for content about growth, achievement, and progress.',
				Aggressive:
					'Maximum angularity combined with geometric precision creates an intense, confrontational register. Reserved for combat sports, gaming, or counterculture brands.',
				Technical:
					'Sharp geometric forms at high precision signal engineered complexity — the visual register of security, infrastructure, and hard-science content.',
				Wild: "Sharp organic forms are the rarest and most unsettling combination — nature's danger signals. Used deliberately in music, art, and counterculture contexts.",
				Trustworthy:
					'Rounded forms in any geometry signal safety and reliability. The rounder a form, the more approachable and trustworthy it reads.'
			};
			desc.style.color = TAG_COLORS[top.label] || 'var(--muted)';
			desc.textContent = descs[top.label] || '';
		}

		function setShapePreset(corner, geom) {
			document.getElementById('axis-corner').value = corner;
			document.getElementById('axis-geom').value = geom;
			drawShapeExplorer();
		}

		drawShapeExplorer();

		/* ═══════════════════════════════════
   ICON RULES CHECKER
═══════════════════════════════════ */
		const ICON_RULES = [
			{
				label: 'Stroke Consistency',
				verdict_pass: 'PASS',
				verdict_fail: 'FAIL',
				pass_note:
					'Consistent 2px stroke weight across all elements. The icon reads as a unified system.',
				fail_note:
					'Inconsistent stroke weights (1px, 3px, 5px mixed). Breaks visual cohesion — looks assembled, not designed.',
				draw_pass: (ctx, w, h) => {
					ctx.strokeStyle = '#e85d8a';
					ctx.lineWidth = 2;
					ctx.fillStyle = 'transparent';
					// House icon — consistent strokes
					const m = w * 0.15;
					ctx.beginPath();
					ctx.moveTo(w / 2, m);
					ctx.lineTo(w - m, h * 0.48);
					ctx.lineTo(m, h * 0.48);
					ctx.closePath();
					ctx.stroke();
					ctx.strokeRect(w * 0.3, h * 0.48, w * 0.4, h * 0.38);
					ctx.strokeRect(w * 0.42, h * 0.62, w * 0.16, w * 0.24);
				},
				draw_fail: (ctx, w, h) => {
					const m = w * 0.15;
					// Inconsistent strokes
					ctx.strokeStyle = '#e85d8a';
					ctx.lineWidth = 5;
					ctx.beginPath();
					ctx.moveTo(w / 2, m);
					ctx.lineTo(w - m, h * 0.48);
					ctx.lineTo(m, h * 0.48);
					ctx.closePath();
					ctx.stroke();
					ctx.lineWidth = 1;
					ctx.strokeRect(w * 0.3, h * 0.48, w * 0.4, h * 0.38);
					ctx.lineWidth = 3;
					ctx.strokeRect(w * 0.42, h * 0.62, w * 0.16, w * 0.24);
				}
			},
			{
				label: 'Optical Alignment',
				pass_note:
					'Circle enlarged to optically match the square — both feel the same visual size.',
				fail_note:
					'Circle and square at identical pixel dimensions. The circle appears noticeably smaller.',
				draw_pass: (ctx, w, h) => {
					ctx.fillStyle = '#56d0a0';
					// Square
					const s = w * 0.3;
					ctx.fillRect(w * 0.08, h / 2 - s / 2, s, s);
					// Circle — slightly larger to optically match
					ctx.beginPath();
					ctx.arc(w * 0.72, h / 2, s / 2 + 3, 0, Math.PI * 2);
					ctx.fill();
					// Labels
					ctx.fillStyle = 'rgba(255,255,255,0.4)';
					ctx.font = `${w * 0.1}px IBM Plex Mono`;
					ctx.textAlign = 'center';
					ctx.fillText('A', w * 0.23, h / 2 + w * 0.04);
					ctx.fillText('A', w * 0.72, h / 2 + w * 0.04);
					ctx.textAlign = 'left';
				},
				draw_fail: (ctx, w, h) => {
					ctx.fillStyle = '#e85d8a';
					const s = w * 0.3;
					ctx.fillRect(w * 0.08, h / 2 - s / 2, s, s);
					ctx.beginPath();
					ctx.arc(w * 0.72, h / 2, s / 2, 0, Math.PI * 2);
					ctx.fill();
					ctx.fillStyle = 'rgba(255,255,255,0.4)';
					ctx.font = `${w * 0.1}px IBM Plex Mono`;
					ctx.textAlign = 'center';
					ctx.fillText('A', w * 0.23, h / 2 + w * 0.04);
					ctx.fillText('A', w * 0.72, h / 2 + w * 0.04);
					ctx.textAlign = 'left';
				}
			},
			{
				label: 'Detail at Size',
				pass_note: 'Three shapes, clean at 24px. Every element reads at target size.',
				fail_note: 'Eight detail elements. At 24px they collapse into a visual blob.',
				draw_pass: (ctx, w, h) => {
					ctx.strokeStyle = '#38c0e8';
					ctx.lineWidth = w * 0.055;
					ctx.lineCap = 'round';
					// Simple camera: 3 shapes
					const W = w * 0.58,
						H = h * 0.42,
						x = w * 0.21,
						y = h * 0.32;
					roundRect(ctx, x, y, W, H, w * 0.06);
					ctx.stroke();
					ctx.beginPath();
					ctx.arc(w / 2, h / 2 + h * 0.02, w * 0.13, 0, Math.PI * 2);
					ctx.stroke();
					roundRect(ctx, w * 0.36, y - h * 0.1, w * 0.12, h * 0.1, w * 0.02);
					ctx.stroke();
				},
				draw_fail: (ctx, w, h) => {
					ctx.strokeStyle = '#9b6dff';
					ctx.lineWidth = w * 0.03;
					ctx.lineCap = 'round';
					const W = w * 0.58,
						H = h * 0.42,
						x = w * 0.21,
						y = h * 0.32;
					roundRect(ctx, x, y, W, H, w * 0.06);
					ctx.stroke();
					ctx.beginPath();
					ctx.arc(w / 2, h / 2 + h * 0.02, w * 0.13, 0, Math.PI * 2);
					ctx.stroke();
					ctx.beginPath();
					ctx.arc(w / 2, h / 2 + h * 0.02, w * 0.07, 0, Math.PI * 2);
					ctx.stroke();
					ctx.beginPath();
					ctx.arc(w / 2, h / 2 + h * 0.02, w * 0.03, 0, Math.PI * 2);
					ctx.stroke();
					roundRect(ctx, w * 0.36, y - h * 0.1, w * 0.12, h * 0.1, w * 0.02);
					ctx.stroke();
					// Flash detail
					ctx.beginPath();
					ctx.arc(w * 0.72, y + h * 0.09, w * 0.04, 0, Math.PI * 2);
					ctx.stroke();
					// Shutter button detail
					ctx.beginPath();
					ctx.arc(w * 0.72, y + h * 0.09, w * 0.025, 0, Math.PI * 2);
					ctx.stroke();
					// Extra lines
					ctx.beginPath();
					ctx.moveTo(x + 4, y + H - 8);
					ctx.lineTo(x + W - 4, y + H - 8);
					ctx.stroke();
				}
			},
			{
				label: 'Concept Count',
				pass_note: 'Two concepts (document + pencil) combined cleanly into one readable form.',
				fail_note: 'Four concepts (document + pencil + clock + globe) — unreadable at any size.',
				draw_pass: (ctx, w, h) => {
					ctx.strokeStyle = '#f5a623';
					ctx.lineWidth = w * 0.055;
					ctx.lineCap = 'round';
					ctx.lineJoin = 'round';
					// Doc shape
					const dw = w * 0.42,
						dh = h * 0.58,
						dx = w * 0.14,
						dy = h * 0.2;
					ctx.beginPath();
					ctx.moveTo(dx, dy);
					ctx.lineTo(dx + dw - dw * 0.28, dy);
					ctx.lineTo(dx + dw, dy + dh * 0.22);
					ctx.lineTo(dx + dw, dy + dh);
					ctx.lineTo(dx, dy + dh);
					ctx.closePath();
					ctx.stroke();
					// Corner fold
					ctx.beginPath();
					ctx.moveTo(dx + dw - dw * 0.28, dy);
					ctx.lineTo(dx + dw - dw * 0.28, dy + dh * 0.22);
					ctx.lineTo(dx + dw, dy + dh * 0.22);
					ctx.stroke();
					// Pencil
					ctx.beginPath();
					const px = w * 0.62,
						py = h * 0.28;
					ctx.moveTo(px, py);
					ctx.lineTo(px + w * 0.22, py + h * 0.22);
					ctx.lineTo(px + w * 0.14, py + h * 0.3);
					ctx.lineTo(px - w * 0.08, py + h * 0.08);
					ctx.closePath();
					ctx.stroke();
					ctx.beginPath();
					ctx.moveTo(px + w * 0.22, py + h * 0.22);
					ctx.lineTo(px + w * 0.27, py + h * 0.33);
					ctx.lineTo(px + w * 0.14, py + h * 0.3);
					ctx.stroke();
				},
				draw_fail: (ctx, w, h) => {
					ctx.strokeStyle = '#e85d8a';
					ctx.lineWidth = w * 0.035;
					ctx.lineCap = 'round';
					ctx.lineJoin = 'round';
					// Tiny doc
					ctx.strokeRect(w * 0.06, h * 0.06, w * 0.25, h * 0.38);
					// Tiny clock
					ctx.beginPath();
					ctx.arc(w * 0.5, h * 0.25, w * 0.16, 0, Math.PI * 2);
					ctx.stroke();
					ctx.beginPath();
					ctx.moveTo(w * 0.5, h * 0.14);
					ctx.lineTo(w * 0.5, h * 0.25);
					ctx.lineTo(w * 0.58, h * 0.25);
					ctx.stroke();
					// Tiny globe
					ctx.beginPath();
					ctx.arc(w * 0.78, h * 0.25, w * 0.16, 0, Math.PI * 2);
					ctx.stroke();
					ctx.beginPath();
					ctx.moveTo(w * 0.62, h * 0.25);
					ctx.lineTo(w * 0.94, h * 0.25);
					ctx.stroke();
					ctx.beginPath();
					ctx.ellipse(w * 0.78, h * 0.25, w * 0.07, w * 0.16, 0, 0, Math.PI * 2);
					ctx.stroke();
					// Tiny pencil
					ctx.beginPath();
					ctx.moveTo(w * 0.2, h * 0.56);
					ctx.lineTo(w * 0.42, h * 0.78);
					ctx.lineTo(w * 0.36, h * 0.84);
					ctx.lineTo(w * 0.14, h * 0.62);
					ctx.closePath();
					ctx.stroke();
					// Tiny person
					ctx.beginPath();
					ctx.arc(w * 0.72, h * 0.62, w * 0.08, 0, Math.PI * 2);
					ctx.stroke();
					ctx.beginPath();
					ctx.moveTo(w * 0.72, h * 0.7);
					ctx.lineTo(w * 0.72, h * 0.88);
					ctx.stroke();
				}
			}
		];

		function drawIconRuleCanvas(canvas, drawFn) {
			const ctx = canvas.getContext('2d');
			const w = canvas.width,
				h = canvas.height;
			ctx.fillStyle = '#080c12';
			ctx.fillRect(0, 0, w, h);
			drawFn(ctx, w, h);
		}

		const rulesGrid = document.getElementById('icon-rules-grid');
		ICON_RULES.forEach((rule, i) => {
			const passCard = document.createElement('div');
			passCard.className = 'icon-rule-card';
			const passCvs = document.createElement('canvas');
			passCvs.width = 120;
			passCvs.height = 120;
			passCvs.className = 'icon-rule-canvas';
			passCard.innerHTML = `<div class="icon-rule-card-label" style="color:var(--sage)">✓ ${rule.label}</div>`;
			passCard.appendChild(passCvs);
			const passVerdict = document.createElement('div');
			passVerdict.className = 'icon-rule-verdict pass';
			passVerdict.textContent = rule.pass_note;
			passCard.appendChild(passVerdict);
			rulesGrid.appendChild(passCard);
			drawIconRuleCanvas(passCvs, rule.draw_pass);

			const failCard = document.createElement('div');
			failCard.className = 'icon-rule-card';
			const failCvs = document.createElement('canvas');
			failCvs.width = 120;
			failCvs.height = 120;
			failCvs.className = 'icon-rule-canvas';
			failCard.innerHTML = `<div class="icon-rule-card-label" style="color:var(--rose)">✗ ${rule.label}</div>`;
			failCard.appendChild(failCvs);
			const failVerdict = document.createElement('div');
			failVerdict.className = 'icon-rule-verdict fail';
			failVerdict.textContent = rule.fail_note;
			failCard.appendChild(failVerdict);
			rulesGrid.appendChild(failCard);
			drawIconRuleCanvas(failCvs, rule.draw_fail);
		});

		/* ═══════════════════════════════════
   ICON CONSTRUCTION LAB
═══════════════════════════════════ */
		const iconCanvas = document.getElementById('icon-canvas');
		const iCtx = iconCanvas.getContext('2d');
		const IW = iconCanvas.width,
			IH = iconCanvas.height;

		let iconTool = 'circle';
		let iconColor = '#e85d8a';
		let iconShapes = [];

		function setIconTool(btn) {
			document.querySelectorAll('.icon-tool').forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			iconTool = btn.dataset.tool;
		}

		function setIconColor(el) {
			iconColor = el.dataset.col;
			document.querySelectorAll('.icon-color-btn').forEach((b) => (b.style.outline = 'none'));
			el.style.outline = '2px solid #fff';
		}

		function redrawIconCanvas() {
			iCtx.fillStyle = '#080c12';
			iCtx.fillRect(0, 0, IW, IH);

			// Guide lines
			iCtx.strokeStyle = 'rgba(232,93,138,0.08)';
			iCtx.lineWidth = 1;
			iCtx.setLineDash([4, 4]);
			iCtx.beginPath();
			iCtx.moveTo(IW / 2, 0);
			iCtx.lineTo(IW / 2, IH);
			iCtx.stroke();
			iCtx.beginPath();
			iCtx.moveTo(0, IH / 2);
			iCtx.lineTo(IW, IH / 2);
			iCtx.stroke();
			iCtx.beginPath();
			iCtx.arc(IW / 2, IH / 2, IW * 0.38, 0, Math.PI * 2);
			iCtx.stroke();
			iCtx.setLineDash([]);

			iconShapes.forEach((s) => drawIconShape(iCtx, s));
			syncIconPreviews();
		}

		function drawIconShape(ctx, s) {
			ctx.save();
			if (s.strokeOnly) {
				ctx.strokeStyle = s.color;
				ctx.lineWidth = Math.max(2, s.size * 0.08);
				ctx.fillStyle = 'transparent';
			} else {
				ctx.fillStyle = s.color;
			}
			ctx.lineCap = 'round';
			ctx.lineJoin = 'round';

			const sz = s.size,
				r = s.radius;
			switch (s.tool) {
				case 'circle':
					ctx.beginPath();
					ctx.arc(s.x, s.y, sz / 2, 0, Math.PI * 2);
					s.strokeOnly ? ctx.stroke() : ctx.fill();
					break;
				case 'rect':
					roundRect(ctx, s.x - sz / 2, s.y - (sz * 0.7) / 2, sz, sz * 0.7, r * sz * 0.01);
					s.strokeOnly ? ctx.stroke() : ctx.fill();
					break;
				case 'triangle':
					ctx.beginPath();
					ctx.moveTo(s.x, s.y - sz * 0.55);
					ctx.lineTo(s.x + sz * 0.55, s.y + sz * 0.35);
					ctx.lineTo(s.x - sz * 0.55, s.y + sz * 0.35);
					ctx.closePath();
					s.strokeOnly ? ctx.stroke() : ctx.fill();
					break;
				case 'line':
					ctx.strokeStyle = s.color;
					ctx.lineWidth = Math.max(2, sz * 0.08);
					ctx.beginPath();
					ctx.moveTo(s.x - sz * 0.5, s.y);
					ctx.lineTo(s.x + sz * 0.5, s.y);
					ctx.stroke();
					break;
				case 'arc':
					ctx.strokeStyle = s.color;
					ctx.lineWidth = Math.max(2, sz * 0.08);
					ctx.beginPath();
					ctx.arc(s.x, s.y, sz * 0.4, -Math.PI * 0.8, 0);
					ctx.stroke();
					break;
				case 'dot':
					ctx.fillStyle = s.color;
					ctx.beginPath();
					ctx.arc(s.x, s.y, Math.max(3, sz * 0.15), 0, Math.PI * 2);
					ctx.fill();
					break;
			}
			ctx.restore();
		}

		function syncIconPreviews() {
			[64, 32, 16].forEach((size) => {
				const cvs = document.getElementById(`icon-preview-${size}`);
				const ctx = cvs.getContext('2d');
				ctx.fillStyle = '#080c12';
				ctx.fillRect(0, 0, size, size);
				const scale = size / IW;
				ctx.save();
				ctx.scale(scale, scale);
				iconShapes.forEach((s) => drawIconShape(ctx, s));
				ctx.restore();
			});
		}

		iconCanvas.addEventListener('click', (e) => {
			const rect = iconCanvas.getBoundingClientRect();
			const scaleX = IW / rect.width,
				scaleY = IH / rect.height;
			const x = (e.clientX - rect.left) * scaleX;
			const y = (e.clientY - rect.top) * scaleY;
			const size = parseInt(document.getElementById('icon-size').value);
			const radius = parseInt(document.getElementById('icon-radius').value);
			const stroke = parseInt(document.getElementById('icon-stroke').value) === 1;
			document.getElementById('icon-size-val').textContent = size;
			document.getElementById('icon-radius-val').textContent = radius;

			iconShapes.push({
				tool: iconTool,
				x,
				y,
				size,
				radius,
				color: iconColor,
				strokeOnly: stroke
			});
			redrawIconCanvas();
		});

		document.getElementById('icon-size').addEventListener('input', (e) => {
			document.getElementById('icon-size-val').textContent = e.target.value;
		});
		document.getElementById('icon-radius').addEventListener('input', (e) => {
			document.getElementById('icon-radius-val').textContent = e.target.value;
		});
		document.getElementById('icon-stroke').addEventListener('input', (e) => {
			document.getElementById('icon-stroke-val').textContent =
				e.target.value === '1' ? 'Stroke' : 'Fill';
		});

		function undoIcon() {
			iconShapes.pop();
			redrawIconCanvas();
		}

		function clearIcon() {
			iconShapes = [];
			redrawIconCanvas();
		}

		function loadIconTemplate(t) {
			iconShapes = [];
			const cx = IW / 2,
				cy = IH / 2;
			if (t === 'camera') {
				iconShapes = [
					{
						tool: 'rect',
						x: cx,
						y: cy + 10,
						size: 120,
						radius: 15,
						color: '#e85d8a',
						strokeOnly: true
					},
					{
						tool: 'circle',
						x: cx,
						y: cy + 14,
						size: 56,
						radius: 0,
						color: '#e85d8a',
						strokeOnly: true
					},
					{
						tool: 'rect',
						x: cx - 22,
						y: cy - 38,
						size: 40,
						radius: 8,
						color: '#e85d8a',
						strokeOnly: true
					}
				];
			} else if (t === 'person') {
				iconShapes = [
					{
						tool: 'circle',
						x: cx,
						y: cy - 50,
						size: 60,
						radius: 0,
						color: '#38c0e8',
						strokeOnly: false
					},
					{
						tool: 'rect',
						x: cx,
						y: cy + 25,
						size: 90,
						radius: 30,
						color: '#38c0e8',
						strokeOnly: false
					}
				];
			} else if (t === 'doc') {
				iconShapes = [
					{
						tool: 'rect',
						x: cx,
						y: cy + 5,
						size: 100,
						radius: 8,
						color: '#f5a623',
						strokeOnly: true
					},
					{
						tool: 'line',
						x: cx - 8,
						y: cy - 12,
						size: 60,
						radius: 0,
						color: '#f5a623',
						strokeOnly: false
					},
					{
						tool: 'line',
						x: cx - 8,
						y: cy + 8,
						size: 60,
						radius: 0,
						color: '#f5a623',
						strokeOnly: false
					},
					{
						tool: 'line',
						x: cx - 8,
						y: cy + 28,
						size: 40,
						radius: 0,
						color: '#f5a623',
						strokeOnly: false
					}
				];
			}
			redrawIconCanvas();
		}

		// init color selection
		document.querySelector('.icon-color-btn').style.outline = '2px solid #fff';
		redrawIconCanvas();

		/* ═══════════════════════════════════
   BRAND SHAPE MATCHER
═══════════════════════════════════ */
		const BRAND_SCENARIOS = [
			{
				prompt:
					'A productivity app for software engineers. Communicates: logical structure, precision, efficiency, no wasted motion.',
				options: [
					{
						label: 'Sharp Geometric',
						colors: ['#38c0e8', '#1a3050'],
						fn: (ctx, w, h) => {
							ctx.fillStyle = '#38c0e8';
							ctx.fillRect(w * 0.08, h * 0.08, w * 0.38, w * 0.38);
							ctx.beginPath();
							ctx.moveTo(w * 0.62, h * 0.08);
							ctx.lineTo(w * 0.92, h * 0.08);
							ctx.lineTo(w * 0.92, h * 0.46);
							ctx.lineTo(w * 0.62, h * 0.46);
							ctx.closePath();
							ctx.fill();
							ctx.fillStyle = 'rgba(56,192,232,0.3)';
							ctx.fillRect(w * 0.08, h * 0.58, w * 0.82, h * 0.08);
							ctx.fillRect(w * 0.08, h * 0.72, w * 0.55, h * 0.08);
						}
					},
					{
						label: 'Organic Rounded',
						colors: ['#56d0a0', '#0f2018'],
						fn: (ctx, w, h) => {
							ctx.fillStyle = '#56d0a0';
							ctx.beginPath();
							for (let i = 0; i <= 60; i++) {
								const a = (i / 60) * Math.PI * 2,
									r = w * 0.28 + Math.sin(a * 3) * w * 0.06 + Math.sin(a * 5) * w * 0.03;
								ctx.lineTo(w * 0.35 + Math.cos(a) * r, h * 0.35 + Math.sin(a) * r);
							}
							ctx.closePath();
							ctx.fill();
							ctx.beginPath();
							for (let i = 0; i <= 60; i++) {
								const a = (i / 60) * Math.PI * 2,
									r = w * 0.2 + Math.sin(a * 4 + 1) * w * 0.05;
								ctx.lineTo(w * 0.7 + Math.cos(a) * r, h * 0.65 + Math.sin(a) * r);
							}
							ctx.closePath();
							ctx.fill();
						}
					},
					{
						label: 'Soft Geometric',
						colors: ['#9b6dff', '#140f22'],
						fn: (ctx, w, h) => {
							ctx.fillStyle = '#9b6dff';
							roundRect(ctx, w * 0.08, h * 0.08, w * 0.38, h * 0.38, w * 0.12);
							ctx.fill();
							roundRect(ctx, w * 0.54, h * 0.08, w * 0.38, h * 0.38, w * 0.19);
							ctx.fill();
							roundRect(ctx, w * 0.08, h * 0.54, w * 0.82, h * 0.14, w * 0.07);
							ctx.fill();
							roundRect(ctx, w * 0.08, h * 0.74, w * 0.55, h * 0.14, w * 0.07);
							ctx.fill();
						}
					}
				],
				correct: 0,
				feedback_ok:
					'Correct. Sharp geometric shapes communicate logical structure and precision — the visual register of engineering tools. The hard edges and mathematical alignment signal efficiency and no wasted motion.',
				feedback_bad:
					'Not quite. For a precision engineering context, sharp geometric forms best signal logical structure, efficiency, and exactness. Organic forms feel too casual; soft rounded geometric is warmer than an engineering tool needs to be.'
			},
			{
				prompt:
					'An online community for independent artists. Communicates: creativity, individual expression, warmth, anti-corporate authenticity.',
				options: [
					{
						label: 'Sharp Geometric',
						colors: ['#e85d8a', '#1a0510'],
						fn: (ctx, w, h) => {
							ctx.fillStyle = '#e85d8a';
							ctx.beginPath();
							ctx.moveTo(w * 0.5, h * 0.06);
							ctx.lineTo(w * 0.94, h * 0.94);
							ctx.lineTo(w * 0.06, h * 0.94);
							ctx.closePath();
							ctx.fill();
							ctx.fillStyle = 'rgba(232,93,138,0.3)';
							ctx.beginPath();
							ctx.moveTo(w * 0.5, h * 0.28);
							ctx.lineTo(w * 0.78, h * 0.78);
							ctx.lineTo(w * 0.22, h * 0.78);
							ctx.closePath();
							ctx.fill();
						}
					},
					{
						label: 'Organic Warm',
						colors: ['#f5a623', '#1a0e05'],
						fn: (ctx, w, h) => {
							ctx.fillStyle = '#f5a623';
							const pts = [
								[0.5, 0.12],
								[0.82, 0.32],
								[0.88, 0.65],
								[0.65, 0.88],
								[0.35, 0.92],
								[0.12, 0.72],
								[0.08, 0.38],
								[0.28, 0.18]
							];
							ctx.beginPath();
							pts.forEach(([px, py], i) => {
								if (i === 0) ctx.moveTo(px * w, py * h);
								else ctx.lineTo(px * w, py * h);
							});
							ctx.closePath();
							ctx.fill();
							ctx.fillStyle = 'rgba(245,166,35,0.2)';
							ctx.beginPath();
							ctx.arc(w * 0.5, h * 0.52, w * 0.18, 0, Math.PI * 2);
							ctx.fill();
						}
					},
					{
						label: 'Corporate Grid',
						colors: ['#5a7090', '#0d1117'],
						fn: (ctx, w, h) => {
							ctx.strokeStyle = '#5a7090';
							ctx.lineWidth = 1;
							for (let x = 0; x < w; x += w / 5) {
								ctx.beginPath();
								ctx.moveTo(x, 0);
								ctx.lineTo(x, h);
								ctx.stroke();
							}
							for (let y = 0; y < h; y += h / 5) {
								ctx.beginPath();
								ctx.moveTo(0, y);
								ctx.lineTo(w, y);
								ctx.stroke();
							}
							ctx.fillStyle = '#5a7090';
							ctx.fillRect(w * 0.2, h * 0.2, w * 0.6, h * 0.6);
						}
					}
				],
				correct: 1,
				feedback_ok:
					'Correct. Organic warm shapes communicate individual expression, authentic creativity, and anti-corporate warmth. The irregular, grown-not-built feeling matches a community of independent artists perfectly.',
				feedback_bad:
					'Not quite. Organic warm forms best match a community valuing individuality and authenticity. Sharp geometric signals precision and engineering; a corporate grid signals structure and hierarchy — both contradict the independent, expressive register.'
			}
		];

		function buildBrandScenarios() {
			BRAND_SCENARIOS.forEach((scenario, si) => {
				const container =
					document.getElementById('brand-scenarios') || document.createElement('div');
				const div = document.createElement('div');
				div.className = 'brand-scenario';
				div.innerHTML = `<div class="brand-scenario-label">Scenario ${si + 1}</div>
      <div class="brand-prompt">${scenario.prompt}</div>
      <div class="shape-options" id="shape-opts-${si}"></div>
      <div class="brand-feedback" id="brand-fb-${si}"></div>`;
				container.appendChild(div);

				const optsWrap = div.querySelector(`#shape-opts-${si}`);
				scenario.options.forEach((opt, oi) => {
					const wrap = document.createElement('div');
					wrap.style.textAlign = 'center';
					const cvs = document.createElement('canvas');
					cvs.width = 96;
					cvs.height = 96;
					cvs.className = 'shape-choice';
					cvs.style.background = opt.colors[1] || '#080c12';
					const lbl = document.createElement('div');
					lbl.textContent = opt.label;
					lbl.style.cssText =
						'font-size:9px;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;margin-top:4px';
					wrap.appendChild(cvs);
					wrap.appendChild(lbl);
					optsWrap.appendChild(wrap);

					const ctx = cvs.getContext('2d');
					ctx.fillStyle = opt.colors[1] || '#080c12';
					ctx.fillRect(0, 0, 96, 96);
					opt.fn(ctx, 96, 96);

					cvs.addEventListener('click', () => {
						if (div.dataset.answered) return;
						div.dataset.answered = '1';
						const fb = div.querySelector(`#brand-fb-${si}`);
						optsWrap.querySelectorAll('.shape-choice').forEach((c, ci) => {
							if (ci === scenario.correct) c.classList.add('correct-reveal');
							else c.classList.add('wrong-reveal');
						});
						if (oi === scenario.correct) {
							cvs.classList.remove('wrong-reveal');
							fb.textContent = '✓ ' + scenario.feedback_ok;
							fb.className = 'brand-feedback ok';
						} else {
							fb.textContent = '✗ ' + scenario.feedback_bad;
							fb.className = 'brand-feedback bad';
						}
					});
				});
			});
		}

		buildBrandScenarios();

		/* ═══════════════════════════════════
   ASSESSMENT SHAPE CANVASES
═══════════════════════════════════ */
		const ASSESS_BRIEFS = [
			{
				correct: 0,
				options: [
					{
						label: 'Sharp Geometric',
						ok: true,
						fn: (ctx, w, h) => {
							ctx.strokeStyle = '#38c0e8';
							ctx.lineWidth = 2.5;
							ctx.lineJoin = 'miter';
							ctx.beginPath();
							ctx.moveTo(w * 0.5, h * 0.1);
							ctx.lineTo(w * 0.9, h * 0.9);
							ctx.lineTo(w * 0.1, h * 0.9);
							ctx.closePath();
							ctx.stroke();
							ctx.beginPath();
							ctx.arc(w * 0.5, h * 0.55, w * 0.14, 0, Math.PI * 2);
							ctx.stroke();
							ctx.beginPath();
							ctx.moveTo(w * 0.3, h * 0.9);
							ctx.lineTo(w * 0.7, h * 0.9);
							ctx.stroke();
						}
					},
					{
						label: 'Organic Blob',
						ok: false,
						fn: (ctx, w, h) => {
							ctx.fillStyle = 'rgba(86,208,160,0.7)';
							const pts = [
								[0.5, 0.1],
								[0.88, 0.35],
								[0.82, 0.72],
								[0.55, 0.92],
								[0.28, 0.88],
								[0.1, 0.58],
								[0.18, 0.28]
							];
							ctx.beginPath();
							pts.forEach(([x, y], i) => (i ? ctx.lineTo(x * w, y * h) : ctx.moveTo(x * w, y * h)));
							ctx.closePath();
							ctx.fill();
						}
					},
					{
						label: 'Soft Rounded',
						ok: false,
						fn: (ctx, w, h) => {
							ctx.fillStyle = 'rgba(245,166,35,0.7)';
							ctx.beginPath();
							ctx.arc(w * 0.5, h * 0.45, w * 0.32, 0, Math.PI * 2);
							ctx.fill();
							ctx.fillStyle = 'rgba(245,166,35,0.4)';
							ctx.beginPath();
							ctx.arc(w * 0.5, h * 0.8, w * 0.15, 0, Math.PI * 2);
							ctx.fill();
						}
					}
				],
				feedback_ok:
					'✓ Correct. Sharp geometric forms — mathematical precision, hard edges, intentional structure — directly communicate the vigilance, authority, and technical precision that define a security brand.',
				feedback_bad:
					'✗ Not quite. A cybersecurity firm needs sharp, precise, geometric forms — communicating vigilance, structure, and engineered protection. Organic blobs and soft rounded shapes suggest warmth and approachability, which contradict the professional intensity required.'
			},
			{
				correct: 1,
				options: [
					{
						label: 'Corporate Sharp',
						ok: false,
						fn: (ctx, w, h) => {
							ctx.fillStyle = 'rgba(90,112,144,0.8)';
							ctx.fillRect(w * 0.1, h * 0.1, w * 0.35, h * 0.35);
							ctx.fillRect(w * 0.55, h * 0.1, w * 0.35, h * 0.35);
							ctx.fillRect(w * 0.1, h * 0.55, w * 0.35, h * 0.35);
							ctx.fillRect(w * 0.55, h * 0.55, w * 0.35, h * 0.35);
						}
					},
					{
						label: 'Playful Rounded',
						ok: true,
						fn: (ctx, w, h) => {
							const cols = ['#f5a623', '#56d0a0', '#e85d8a', '#9b6dff'];
							[
								[0.3, 0.35],
								[0.68, 0.35],
								[0.3, 0.68],
								[0.68, 0.68]
							].forEach(([x, y], i) => {
								ctx.fillStyle = cols[i];
								ctx.beginPath();
								ctx.arc(x * w, y * h, w * 0.2, 0, Math.PI * 2);
								ctx.fill();
							});
						}
					},
					{
						label: 'Angular Diagonal',
						ok: false,
						fn: (ctx, w, h) => {
							ctx.fillStyle = 'rgba(232,93,138,0.8)';
							ctx.beginPath();
							ctx.moveTo(w * 0.1, h * 0.5);
							ctx.lineTo(w * 0.5, h * 0.08);
							ctx.lineTo(w * 0.9, h * 0.5);
							ctx.lineTo(w * 0.5, h * 0.92);
							ctx.closePath();
							ctx.fill();
							ctx.fillStyle = 'rgba(232,93,138,0.3)';
							ctx.beginPath();
							ctx.moveTo(w * 0.28, h * 0.5);
							ctx.lineTo(w * 0.5, h * 0.26);
							ctx.lineTo(w * 0.72, h * 0.5);
							ctx.lineTo(w * 0.5, h * 0.74);
							ctx.closePath();
							ctx.fill();
						}
					}
				],
				feedback_ok:
					'✓ Correct. Rounded, colourful, playful circles communicate friendliness, curiosity, and approachability — precisely the register that invites children to engage. Each circle is a distinct, joyful entity that together form a welcoming community.',
				feedback_bad:
					"✗ Not quite. For a children's science podcast, rounded and playful shapes communicate the friendliness and curiosity the brand needs. Sharp corporate grids feel authoritarian and unwelcoming; aggressive angular diagonals communicate intensity rather than discovery."
			}
		];

		function buildAssessment() {
			ASSESS_BRIEFS.forEach((brief, bi) => {
				const row = document.getElementById(`assess-row-${bi}`);
				brief.options.forEach((opt, oi) => {
					const wrap = document.createElement('div');
					const cvs = document.createElement('canvas');
					cvs.width = 120;
					cvs.height = 120;
					cvs.className = 'assess-option-canvas';
					cvs.style.background = '#080c12';
					const lbl = document.createElement('span');
					lbl.className = 'assess-canvas-label';
					lbl.textContent = opt.label;
					wrap.appendChild(cvs);
					wrap.appendChild(lbl);
					row.appendChild(wrap);

					const ctx = cvs.getContext('2d');
					ctx.fillStyle = '#080c12';
					ctx.fillRect(0, 0, 120, 120);
					opt.fn(ctx, 120, 120);

					cvs.addEventListener('click', () => {
						if (row.dataset.answered) return;
						row.dataset.answered = '1';
						const fb = document.getElementById(`assess-fb-${bi}`);
						row.querySelectorAll('.assess-option-canvas').forEach((c, ci) => {
							c.classList.add(ci === brief.correct ? 'correct-reveal' : 'wrong-reveal');
						});
						if (oi === brief.correct) {
							cvs.classList.remove('wrong-reveal');
							fb.textContent = brief.feedback_ok;
							fb.className = 'assess-feedback ok';
						} else {
							fb.textContent = brief.feedback_bad;
							fb.className = 'assess-feedback bad';
						}
					});
				});
			});
		}

		buildAssessment();

		/* ═══════════════════════════════════
   QUIZ
═══════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;
		const explanations = [
			'Correct. Geometric shapes are defined by mathematical relationships — perfect circles, equilateral triangles, precise ratios. They communicate deliberate construction, precision, and engineered order.',
			'Correct. Icons must be designed for and tested at their smallest required size. Details that look refined at 200px are invisible at 24px — they contribute no information and only add visual noise that hurts legibility.',
			'Correct. Shape language must be consistent across all brand touchpoints. Conflicting shape registers — soft logo + aggressive thumbnails — prevent the viewer from forming a coherent brand impression.',
			'Correct. Optical alignment is about perception, not mathematics. A circle lacks corner mass, so it appears smaller than a same-dimensioned square. Designers compensate by making the circle physically larger to achieve perceptual equality.',
			'Correct. Effective icons combine two familiar visual concepts into one readable mark. Three concepts exceed what the format can compress without becoming illegible.'
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
					'✗ Revisit the section — focus on how the viewer perceives shape before they process any content.';
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

		if (typeof lerp === 'function') actions.lerp = lerp;
		if (typeof drawShapeExplorer === 'function') actions.drawShapeExplorer = drawShapeExplorer;
		if (typeof roundRect === 'function') actions.roundRect = roundRect;
		if (typeof updatePersonalityTags === 'function')
			actions.updatePersonalityTags = updatePersonalityTags;
		if (typeof setShapePreset === 'function') actions.setShapePreset = setShapePreset;
		if (typeof drawIconRuleCanvas === 'function') actions.drawIconRuleCanvas = drawIconRuleCanvas;
		if (typeof setIconTool === 'function') actions.setIconTool = setIconTool;
		if (typeof setIconColor === 'function') actions.setIconColor = setIconColor;
		if (typeof redrawIconCanvas === 'function') actions.redrawIconCanvas = redrawIconCanvas;
		if (typeof drawIconShape === 'function') actions.drawIconShape = drawIconShape;
		if (typeof syncIconPreviews === 'function') actions.syncIconPreviews = syncIconPreviews;
		if (typeof undoIcon === 'function') actions.undoIcon = undoIcon;
		if (typeof clearIcon === 'function') actions.clearIcon = clearIcon;
		if (typeof loadIconTemplate === 'function') actions.loadIconTemplate = loadIconTemplate;
		if (typeof buildBrandScenarios === 'function')
			actions.buildBrandScenarios = buildBrandScenarios;
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
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 05 of 10</div>
	</header>

	<div class="module-hero">
		<div class="module-number">05</div>
		<div class="module-tag">Module 05 · Shape + Symbol</div>
		<h1 class="module-title">Shape Language<br /><span>&amp; Iconography</span></h1>
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
			<li><a href="#shape-personality">Shape Personality</a></li>
			<li><a href="#geometric-organic">Geometric vs Organic</a></li>
			<li><a href="#symbol-rules">Symbol Design Rules</a></li>
			<li><a href="#icon-construction">Icon Construction Lab</a></li>
			<li><a href="#brand-shape">Shape in Brand Identity</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>
				Identify the psychological associations of sharp, rounded, geometric, and organic shapes
			</li>
			<li>Apply shape language to express a specific brand personality</li>
			<li>Construct simple, functional icons from basic geometric primitives</li>
			<li>Evaluate icons against the core rules of symbol design</li>
		</ul>
	</section>

	<!-- ═══════════════════════
     SECTION 1: SHAPE PERSONALITY
═══════════════════════ -->
	<section id="shape-personality" class="section">
		<div class="section-header">
			<span class="section-num">05.01</span>
			<h2 class="section-title">What Shapes Communicate</h2>
		</div>

		<p>
			Long before a viewer reads a word or recognizes a logo, they have already formed a response to
			its shapes. Shape language is one of the oldest communication systems human beings use —
			rooted in evolutionary pattern recognition, where angular forms signaled danger (rocks, claws,
			teeth) and rounded forms signaled safety (faces, fruit, shelter).
		</p>

		<p>
			In design, this translates directly into personality expression.
			<strong>Sharp, angular shapes</strong> communicate speed, aggression, precision, energy,
			danger, masculinity, and modernity. Think of the Nike swoosh, every sports car logo, every
			tech startup that wants to look fast. <strong>Rounded shapes</strong> communicate warmth, friendliness,
			accessibility, trust, and approachability. Think of Google's product logos, children's educational
			brands, and healthcare. Neither is better — they serve different communicative purposes.
		</p>

		<p>
			The key insight is that these associations are not decorative preferences. They are
			<em>pre-rational</em> — they operate before the viewer consciously processes any information. By
			the time someone has read your channel name, they have already felt something about its shapes.
		</p>

		<!-- DEMO 1: Shape Personality Explorer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Shape Personality Explorer</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Drag the two axes to morph a logo mark between four personality extremes. The personality
					tags and description update to reflect what the shape combination communicates.
				</p>
				<div class="two-col" style="align-items: start; gap: 1.5rem">
					<div>
						<canvas
							id="shape-canvas"
							width="300"
							height="300"
							aria-label="Shape Canvas Demonstration"
							role="img"
							tabindex="0"
						></canvas>
						<div class="personality-tags" id="personality-tags"></div>
						<div class="shape-desc" id="shape-desc"></div>
					</div>
					<div>
						<div class="shape-axes">
							<div class="axis-track">
								<div class="axis-label-row"><span>Rounded</span><span>Angular</span></div>
								<input
									type="range"
									class="axis-slider"
									id="axis-corner"
									min="0"
									max="100"
									value="15"
									oninput={() => {
										actions.drawShapeExplorer();
									}}
								/>
							</div>
							<div class="axis-track">
								<div class="axis-label-row"><span>Organic</span><span>Geometric</span></div>
								<input
									type="range"
									class="axis-slider"
									id="axis-geom"
									min="0"
									max="100"
									value="20"
									oninput={() => {
										actions.drawShapeExplorer();
									}}
								/>
							</div>
						</div>

						<div style="margin-top: 1.25rem; display: flex; flex-direction: column; gap: 0.4rem">
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.12em;
											text-transform: uppercase;
											color: var(--muted);
											margin-bottom: 0.3rem;
										"
							>
								Presets
							</div>
							<div style="display: flex; flex-wrap: wrap; gap: 0.4rem">
								<button
									class="btn"
									onclick={(e) => {
										actions.setShapePreset(5, 8);
									}}>Friendly / Organic</button
								>
								<button
									class="btn"
									onclick={(e) => {
										actions.setShapePreset(90, 90);
									}}>Sharp / Geometric</button
								>
								<button
									class="btn"
									onclick={(e) => {
										actions.setShapePreset(15, 85);
									}}>Precise / Clean</button
								>
								<button
									class="btn"
									onclick={(e) => {
										actions.setShapePreset(85, 12);
									}}>Warm / Natural</button
								>
								<button
									class="btn amber"
									onclick={(e) => {
										actions.setShapePreset(50, 50);
									}}>Balanced</button
								>
							</div>
						</div>

						<div
							style="
										margin-top: 1.5rem;
										padding: 1rem;
										background: var(--code-bg);
										border: 1px solid var(--border);
										font-size: 12px;
										line-height: 1.7;
									"
						>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.12em;
											text-transform: uppercase;
											color: var(--muted);
											margin-bottom: 0.5rem;
										"
							>
								Shape Psychology Reference
							</div>
							<div style="color: var(--rose); margin-bottom: 0.3rem">Sharp + Geometric</div>
							<div style="color: var(--muted); margin-bottom: 0.75rem">
								Speed · Precision · Technology · Edge
							</div>
							<div style="color: var(--sage); margin-bottom: 0.3rem">Rounded + Organic</div>
							<div style="color: var(--muted); margin-bottom: 0.75rem">
								Warmth · Trust · Nature · Accessibility
							</div>
							<div style="color: var(--amber); margin-bottom: 0.3rem">Rounded + Geometric</div>
							<div style="color: var(--muted); margin-bottom: 0.75rem">
								Friendliness · Clarity · Approachable Tech
							</div>
							<div style="color: var(--violet); margin-bottom: 0.3rem">Sharp + Organic</div>
							<div style="color: var(--muted)">Tension · Wild Energy · Counterculture</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══════════════════════
     SECTION 2: GEOMETRIC vs ORGANIC
═══════════════════════ -->
	<section id="geometric-organic" class="section">
		<div class="section-header">
			<span class="section-num">05.02</span>
			<h2 class="section-title">Geometric vs Organic Forms</h2>
		</div>

		<p>
			The geometric/organic axis is distinct from the sharp/round axis, though they often travel
			together. <em>Geometric</em> shapes are built from mathematical relationships — perfect
			circles, equilateral triangles, squares with equal sides, grids and ratios. They communicate
			<em>order, precision, and human construction</em>. They say: someone thought very carefully
			about this. Geometric design feels deliberate, engineered, and modern.
		</p>

		<p>
			<em>Organic</em> shapes are irregular, asymmetric, and imperfect — the shapes found in nature. Leaves,
			coastlines, water, flame. They communicate naturalness, authenticity, and spontaneity. They suggest
			something that grew rather than something that was built. In brand contexts, organic shapes feel
			less corporate and more human — which is both their advantage and their limitation.
		</p>

		<p>
			Most successful logos sit toward the geometric end of the spectrum, for a practical reason:
			geometric shapes reduce identically at any size. A perfect circle remains a perfect circle at
			16px. An organic blob shape may become unrecognizable. This is a functional constraint, not an
			aesthetic preference.
		</p>

		<table>
			<thead>
				<tr>
					<th>Form Type</th>
					<th>Communicates</th>
					<th>Scales Well</th>
					<th>Typical Use</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Circle</td>
					<td>Unity, completeness, protection, infinity</td>
					<td style="color: var(--sage)">Excellent</td>
					<td>Community, global, lifecycle brands</td>
				</tr>
				<tr>
					<td>Square / Rectangle</td>
					<td>Stability, reliability, trust, structure</td>
					<td style="color: var(--sage)">Excellent</td>
					<td>Finance, government, construction</td>
				</tr>
				<tr>
					<td>Triangle (pointing up)</td>
					<td>Growth, ambition, direction, hierarchy</td>
					<td style="color: var(--sage)">Excellent</td>
					<td>Consulting, achievement, sports</td>
				</tr>
				<tr>
					<td>Triangle (pointing down)</td>
					<td>Instability, danger, inversion, mystery</td>
					<td style="color: var(--sage)">Excellent</td>
					<td>Creative agencies, counterculture</td>
				</tr>
				<tr>
					<td>Hexagon</td>
					<td>Efficiency, structure, nature (honeycomb)</td>
					<td style="color: var(--amber)">Good</td>
					<td>Tech, science, engineering</td>
				</tr>
				<tr>
					<td>Organic blob</td>
					<td>Approachability, growth, uniqueness</td>
					<td style="color: var(--rose)">Poor</td>
					<td>Consumer apps, children's brands (large sizes only)</td>
				</tr>
				<tr>
					<td>Diagonal / asymmetric</td>
					<td>Movement, dynamism, disruption</td>
					<td style="color: var(--amber)">Variable</td>
					<td>Sports, media, startups</td>
				</tr>
			</tbody>
		</table>

		<div class="callout amber">
			<div class="callout-label">The Scalability Rule</div>
			Any shape that will appear in your brand system must be legible at 16×16 pixels — favicon size.
			If it loses its identity at that size, it is not a logo shape; it is an illustration. Brand marks
			must be constructed from geometric primitives that survive extreme reduction.
		</div>
	</section>

	<!-- ═══════════════════════
     SECTION 3: SYMBOL DESIGN RULES
═══════════════════════ -->
	<section id="symbol-rules" class="section">
		<div class="section-header">
			<span class="section-num">05.03</span>
			<h2 class="section-title">Symbol Design Rules</h2>
		</div>

		<p>
			Icons and symbols are compressed communication. They must convey meaning with fewer elements
			than any other graphic form. This compression has strict rules — not stylistic suggestions,
			but structural requirements that determine whether a symbol works or fails.
		</p>

		<p>
			<strong>Consistency of stroke weight.</strong> All lines in an icon set must share the same stroke
			width. Mixing stroke weights across icons in the same set breaks visual cohesion — the set feels
			like it was assembled from different sources rather than designed as a system. Pick one stroke weight
			and apply it absolutely.
		</p>

		<p>
			<strong>Optical alignment over mathematical alignment.</strong> A circle and a square of identical
			pixel dimensions do not look the same size. The circle appears smaller because its corners are absent
			— the four points where visual mass concentrates most. To make them appear equal, the circle must
			be physically larger. This principle applies to all icon elements: design for perception, not for
			the grid.
		</p>

		<p>
			<strong>Minimum detail at target size.</strong> Design your icon at 24px or 32px and test it there
			— not at 200px where every detail is visible. Every detail that disappears at target size is a detail
			that should not exist. Icons that look intricate and beautiful at 200px and turn into blobs at 24px
			are failed icons.
		</p>

		<p>
			<strong>No more than two visual concepts.</strong> An icon that tries to communicate three separate
			ideas at once communicates none of them. The best icons combine two familiar elements into a single
			recognizable form — a camera plus a location pin, a paper plus a pencil, a clock plus a person.
			Three concepts require three icons used together, not a single combined symbol.
		</p>

		<!-- DEMO: Icon Rules Visual Checker -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Icon Rules Checker</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Four icon pairs — each showing the same concept done correctly and incorrectly. Click each
					card to see the rule being violated and why it matters.
				</p>
				<div class="icon-rules-grid" id="icon-rules-grid"></div>
			</div>
		</div>

		<div class="callout sage">
			<div class="callout-label">The Squint Test</div>
			Squint at your icon until it blurs. If you can still identify its essential form — if the core shape
			survives — it passes the squint test. If it collapses into an unreadable smudge, it has too much
			detail or insufficient contrast. The squint test approximates what happens at small sizes and across
			varied screen densities.
		</div>
	</section>

	<!-- ═══════════════════════
     SECTION 4: ICON CONSTRUCTION LAB
═══════════════════════ -->
	<section id="icon-construction" class="section">
		<div class="section-header">
			<span class="section-num">05.04</span>
			<h2 class="section-title">Icon Construction Lab</h2>
		</div>

		<p>
			All icons are built from the same six primitive shapes: circles, rectangles, triangles, lines,
			arcs, and dots. The icon designer's skill is not in drawing but in
			<em>selecting, combining, and constraining</em> these primitives into a form that reads immediately
			as a specific concept. This is a reduction problem, not a drawing problem.
		</p>

		<p>
			The construction method: start with the most essential shape that contains the concept's
			identity. A camera is essentially a rectangle. A person is essentially a circle above a
			trapezoid. A document is a rectangle with a folded corner. Then add one clarifying element —
			the camera gets a lens circle, the person gets arms, the document gets a line suggesting text.
			Stop there.
		</p>

		<!-- DEMO: Icon Construction Lab -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Icon Construction Lab</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Select a primitive and click the canvas to place it. Build an icon from geometric parts.
					The size preview row shows how your construction reads at different scales.
				</p>

				<div class="two-col" style="align-items: start; gap: 1.5rem">
					<div>
						<canvas
							id="icon-canvas"
							width="300"
							height="300"
							aria-label="Icon Canvas Demonstration"
							role="img"
							tabindex="0"
						></canvas>
						<div class="icon-size-preview" id="icon-size-preview">
							<div class="icon-size-wrap">
								<canvas
									id="icon-preview-64"
									width="64"
									height="64"
									style="border: 1px solid var(--border2)"
									aria-label="Icon Preview 64 Demonstration"
									role="img"
									tabindex="0"
								></canvas>
								<span class="icon-size-label">64px</span>
							</div>
							<div class="icon-size-wrap">
								<canvas
									id="icon-preview-32"
									width="32"
									height="32"
									style="border: 1px solid var(--border2)"
									aria-label="Icon Preview 32 Demonstration"
									role="img"
									tabindex="0"
								></canvas>
								<span class="icon-size-label">32px</span>
							</div>
							<div class="icon-size-wrap">
								<canvas
									id="icon-preview-16"
									width="16"
									height="16"
									style="border: 1px solid var(--border2)"
									aria-label="Icon Preview 16 Demonstration"
									role="img"
									tabindex="0"
								></canvas>
								<span class="icon-size-label">16px</span>
							</div>
							<div
								style="
											margin-left: auto;
											font-size: 11px;
											color: var(--muted);
											max-width: 140px;
											line-height: 1.5;
										"
							>
								The 16px preview shows favicon-level readability. If your icon becomes
								unrecognizable here, it has too many details.
							</div>
						</div>
					</div>
					<div>
						<div
							style="
										font-size: 10px;
										letter-spacing: 0.12em;
										text-transform: uppercase;
										color: var(--muted);
										margin-bottom: 0.5rem;
									"
						>
							Primitives
						</div>
						<div class="icon-controls" id="icon-controls">
							<button
								class="icon-tool active"
								data-tool="circle"
								onclick={(e) => {
									actions.setIconTool(e.currentTarget);
								}}
							>
								<span class="icon-tool-icon">●</span> Circle
							</button>
							<button
								class="icon-tool"
								data-tool="rect"
								onclick={(e) => {
									actions.setIconTool(e.currentTarget);
								}}
							>
								<span class="icon-tool-icon">■</span> Rectangle
							</button>
							<button
								class="icon-tool"
								data-tool="triangle"
								onclick={(e) => {
									actions.setIconTool(e.currentTarget);
								}}
							>
								<span class="icon-tool-icon">▲</span> Triangle
							</button>
							<button
								class="icon-tool"
								data-tool="line"
								onclick={(e) => {
									actions.setIconTool(e.currentTarget);
								}}
							>
								<span class="icon-tool-icon">━</span> Line
							</button>
							<button
								class="icon-tool"
								data-tool="arc"
								onclick={(e) => {
									actions.setIconTool(e.currentTarget);
								}}
							>
								<span class="icon-tool-icon">◜</span> Arc
							</button>
							<button
								class="icon-tool"
								data-tool="dot"
								onclick={(e) => {
									actions.setIconTool(e.currentTarget);
								}}
							>
								<span class="icon-tool-icon">•</span> Dot
							</button>
						</div>

						<div style="margin-top: 0.75rem">
							<div class="slider-row">
								<label style="min-width: 80px">Size</label>
								<input type="range" id="icon-size" min="8" max="80" value="32" />
								<span class="slider-val" id="icon-size-val" style="color: var(--rose)">32</span>
							</div>
							<div class="slider-row">
								<label style="min-width: 80px">Corner radius</label>
								<input type="range" id="icon-radius" min="0" max="50" value="0" />
								<span class="slider-val" id="icon-radius-val" style="color: var(--rose)">0</span>
							</div>
							<div class="slider-row">
								<label style="min-width: 80px">Stroke only</label>
								<input type="range" id="icon-stroke" min="0" max="1" step="1" value="0" />
								<span class="slider-val" id="icon-stroke-val" style="color: var(--rose)">Fill</span>
							</div>
						</div>

						<div
							style="
										font-size: 10px;
										letter-spacing: 0.12em;
										text-transform: uppercase;
										color: var(--muted);
										margin: 0.75rem 0 0.4rem;
									"
						>
							Color
						</div>
						<div style="display: flex; gap: 0.4rem; flex-wrap: wrap">
							<div
								class="icon-color-btn"
								data-col="#e85d8a"
								onclick={(e) => {
									actions.setIconColor(e.currentTarget);
								}}
								role="button"
								tabindex="0"
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										actions.setIconColor(e.currentTarget);
									}
								}}
								style="
											width: 22px;
											height: 22px;
											background: #e85d8a;
											border: 2px solid #fff;
											cursor: pointer;
										"
							></div>
							<div
								class="icon-color-btn"
								data-col="#ffffff"
								onclick={(e) => {
									actions.setIconColor(e.currentTarget);
								}}
								role="button"
								tabindex="0"
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										actions.setIconColor(e.currentTarget);
									}
								}}
								style="
											width: 22px;
											height: 22px;
											background: #fff;
											border: 2px solid var(--border2);
											cursor: pointer;
										"
							></div>
							<div
								class="icon-color-btn"
								data-col="#38c0e8"
								onclick={(e) => {
									actions.setIconColor(e.currentTarget);
								}}
								role="button"
								tabindex="0"
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										actions.setIconColor(e.currentTarget);
									}
								}}
								style="
											width: 22px;
											height: 22px;
											background: #38c0e8;
											border: 2px solid var(--border2);
											cursor: pointer;
										"
							></div>
							<div
								class="icon-color-btn"
								data-col="#f5a623"
								onclick={(e) => {
									actions.setIconColor(e.currentTarget);
								}}
								role="button"
								tabindex="0"
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										actions.setIconColor(e.currentTarget);
									}
								}}
								style="
											width: 22px;
											height: 22px;
											background: #f5a623;
											border: 2px solid var(--border2);
											cursor: pointer;
										"
							></div>
							<div
								class="icon-color-btn"
								data-col="#56d0a0"
								onclick={(e) => {
									actions.setIconColor(e.currentTarget);
								}}
								role="button"
								tabindex="0"
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										actions.setIconColor(e.currentTarget);
									}
								}}
								style="
											width: 22px;
											height: 22px;
											background: #56d0a0;
											border: 2px solid var(--border2);
											cursor: pointer;
										"
							></div>
						</div>

						<div class="icon-action-row">
							<button
								class="btn rose"
								onclick={(e) => {
									actions.undoIcon();
								}}>Undo</button
							>
							<button
								class="btn"
								onclick={(e) => {
									actions.clearIcon();
								}}>Clear</button
							>
							<button
								class="btn amber"
								onclick={(e) => {
									actions.loadIconTemplate('camera');
								}}
							>
								Template: Camera
							</button>
							<button
								class="btn amber"
								onclick={(e) => {
									actions.loadIconTemplate('person');
								}}
							>
								Template: Person
							</button>
							<button
								class="btn amber"
								onclick={(e) => {
									actions.loadIconTemplate('doc');
								}}
							>
								Template: Document
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══════════════════════
     SECTION 5: SHAPE IN BRAND IDENTITY
═══════════════════════ -->
	<section id="brand-shape" class="section">
		<div class="section-header">
			<span class="section-num">05.05</span>
			<h2 class="section-title">Shape Language in Brand Identity</h2>
		</div>

		<p>
			Shape language operates at every scale of a brand system, not just in the logo. The corner
			radius of your button components, the angle of your thumbnail compositions, the silhouette of
			your channel banner graphic, the weight of your icon strokes — all of these are shape language
			decisions that either reinforce or contradict your brand personality.
		</p>

		<p>
			The rule: pick a shape register and apply it everywhere. If your logo mark uses rounded
			corners, your button components should use rounded corners. If your brand mark is built from
			sharp triangular geometry, your thumbnail compositions should use diagonal energy. A brand
			that uses soft rounded shapes in its logo but sharp angular photography in its thumbnails
			sends contradictory signals — the viewer can't synthesize them into a single personality.
		</p>

		<p>
			For a YouTube channel, the shapes most viewers interact with are: the logo mark (in the
			profile picture circle, which already constrains the logo into a round container), the
			thumbnail composition geometry, the title card shapes and overlays, and the icon set used in
			graphics and explainers. These are the four layers where shape consistency creates a
			recognizable visual identity.
		</p>

		<!-- DEMO: Brand Personality Matcher -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Brand Shape Matcher</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					For each brand description, select the shape set that best matches the personality. Then
					check your reasoning.
				</p>
				<div class="brand-scenarios" id="brand-scenarios"></div>
			</div>
		</div>

		<div class="callout violet">
			<div class="callout-label">Your Shape Register</div>
			Before building any assets, define your shape register in one sentence: "My brand uses [rounded/angular/geometric/organic]
			forms because my content communicates [warm/precise/energetic/natural] ideas to an audience that
			expects [accessible/professional/intense/authentic] visual signals." This sentence will prevent
			every future inconsistency.
		</div>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">05.06</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout">
			<div class="callout-label">Exercise 1 — Icon Set of Five</div>
			Design five related icons for your channel's subject matter using only geometric primitives. Rules:<br
			/><br />
			· All five icons must use the same stroke weight<br />
			· No icon may contain more than three primitive shapes<br />
			· Every icon must be legible at 24px<br />
			· All five must feel like they came from the same system (consistent corner radius, consistent visual
			weight)<br /><br />
			If you can't make an icon with three shapes, simplify the concept — you're trying to show too much.
		</div>

		<div class="callout sage">
			<div class="callout-label">Exercise 2 — Shape-Based Character</div>
			Build a simple character or mascot for educational use using only rectangles, circles, and triangles.
			No curves, no organic forms — only primitives. Constraints force creativity: the limitation reveals
			which shapes are truly essential to communicate "person," "figure," or "identity." This exercise
			teaches you to reduce, which is the core skill of iconography.
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 05 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> A logo mark uses perfect circles and equilateral triangles at mathematically-defined
				proportions. Which shape register does this represent, and what does it communicate?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 0);
					}}
				>
					A. Organic — natural forms that grew rather than were constructed
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 1);
					}}
				>
					B. Sharp — aggressive energy and speed
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 2);
					}}
				>
					C. Geometric — communicating order, precision, and deliberate construction; the shapes say
					something was carefully engineered
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 3);
					}}
				>
					D. Rounded — approachability and warmth through soft edges
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> An icon for a children's educational platform is designed at 200px
				and looks charming and detailed. At 24px it becomes an unrecognizable blob. What is the core design
				failure?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 0);
					}}
				>
					A. The icon uses rounded shapes, which don't scale as well as angular ones
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 1);
					}}
				>
					B. The icon contains too much detail — it was designed for a display context, not for the
					target size where it will actually be used. Icon design must start at the smallest
					required size.
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 2);
					}}
				>
					C. The colors used are inappropriate for small sizes
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 3);
					}}
				>
					D. Icons for children's platforms should always be designed larger to aid recognition
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> A brand identity uses a soft, rounded logo mark but features sharp
				angular photography and diagonal thumbnail compositions. What problem does this create?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 0);
					}}
				>
					A. The photography will compete with the logo mark for visual attention
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 1);
					}}
				>
					B. Angular photography makes thumbnails feel aggressive, which lowers click-through rates
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 2);
					}}
				>
					C. Rounded logos are not compatible with photographic content
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 3);
					}}
				>
					D. Contradictory shape registers across brand touchpoints produce conflicting personality
					signals — the viewer cannot synthesize them into a single coherent brand identity
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> Why must a circle be physically larger than a square to appear
				the same visual size?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 0);
					}}
				>
					A. The circle lacks corner mass — visual weight concentrates at the four corners of a
					square, so a same-dimensioned circle appears smaller. Optical alignment requires
					compensating for this perceptual difference.
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 1);
					}}
				>
					B. Circles always appear smaller because curved lines create less contrast than straight
					lines
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 2);
					}}
				>
					C. This is a color perception issue, not a shape issue — circles reflect light differently
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 3);
					}}
				>
					D. They don't need to be different sizes — mathematical equality and visual equality are
					the same thing
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> What is the maximum number of visual concepts an effective single
				icon should attempt to communicate?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 0);
					}}
				>
					A. One — icons should represent a single, unambiguous idea with no combination
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 1);
					}}
				>
					B. Two — the most effective icons combine two familiar elements into a single readable
					form; a third concept exceeds what the format can hold
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 2);
					}}
				>
					C. Three — complex ideas require complex icons to avoid oversimplification
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.handleQuiz(e.currentTarget, 3);
					}}
				>
					D. There is no limit — skilled icon designers can compress any number of concepts
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
		<div class="assessment-header">Module Assessment — Shape Personality Diagnosis</div>
		<div class="assessment-sub">
			For each brief, select the shape option that best matches the described brand personality.
		</div>

		<div class="assess-question">
			<div class="assess-q-header">
				Brief 01 — A cybersecurity firm. Communicates: precision, vigilance, protection, technical
				authority.
			</div>
			<div class="assess-body">
				<div class="assess-canvas-row" id="assess-row-0"></div>
				<div class="assess-feedback" id="assess-fb-0"></div>
			</div>
		</div>

		<div class="assess-question">
			<div class="assess-q-header">
				Brief 02 — A children's science podcast. Communicates: curiosity, friendliness, discovery,
				approachability.
			</div>
			<div class="assess-body">
				<div class="assess-canvas-row" id="assess-row-1"></div>
				<div class="assess-feedback" id="assess-fb-1"></div>
			</div>
		</div>
	</section>

	<!-- NAV -->
	<div class="nav-links">
		<a href="gd-module-04.html" class="prev-link">← Module 04: Color Theory</a>
		<a href="gd-module-06.html" class="next-module" style="flex: 1; max-width: 420px">
			<div>
				<div class="next-label">Next — Module 06</div>
				<div class="next-title">Brand Identity &amp; Visual Systems</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</div>
</div>

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
		color: var(--rose);
		border: 1px solid var(--rose);
		padding: 3px 10px;
		margin-bottom: 1.5rem;
	}
	.module-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(28px, 5vw, 48px);
		font-weight: 800;
		line-height: 1.1;
		color: #fff;
		max-width: 600px;
	}
	.module-title span {
		color: var(--rose);
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
		color: var(--rose);
		border-color: var(--rose);
	}

	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--rose);
		background: var(--surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--rose);
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
		color: var(--amber);
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
		color: var(--amber);
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
		color: var(--rose);
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

	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--rose);
		background: color-mix(in srgb, var(--rose) 5%, var(--surface));
		font-size: 13px;
	}
	.callout.amber {
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
	}
	.callout.sage {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--surface));
	}
	:global(.callout.sky) {
		border-color: var(--sky);
		background: color-mix(in srgb, var(--sky) 5%, var(--surface));
	}
	.callout.violet {
		border-color: var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--rose);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	.callout.amber .callout-label {
		color: var(--amber);
	}
	.callout.sage .callout-label {
		color: var(--sage);
	}
	:global(.callout.sky) .callout-label {
		color: var(--sky);
	}
	.callout.violet .callout-label {
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
	.demo-badge {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	.demo-badge.interactive {
		color: var(--rose);
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
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
		border-color: var(--rose);
		color: var(--rose);
	}
	:global(.btn.active) {
		border-color: var(--rose);
		color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
	}
	.btn.amber:hover {
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
	:global(.btn.violet:hover) {
		border-color: var(--violet);
		color: var(--violet);
	}
	:global(.btn.violet.active) {
		border-color: var(--violet);
		color: var(--violet);
		background: color-mix(in srgb, var(--violet) 10%, transparent);
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

	.slider-row {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 0.6rem 0;
	}
	.slider-row label {
		font-size: 12px;
		min-width: 110px;
		color: var(--text);
	}
	.slider-row :global(input[type='range']) {
		flex: 1;
		-webkit-appearance: none;
		height: 3px;
		background: var(--border2);
		outline: none;
	}
	.slider-row :global(input[type='range']::-webkit-slider-thumb) {
		-webkit-appearance: none;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--rose);
		cursor: pointer;
	}
	.slider-val {
		font-size: 12px;
		color: var(--rose);
		min-width: 48px;
		text-align: right;
		font-weight: 600;
	}

	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}
	:global(.three-col) {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1rem;
	}
	@media (max-width: 640px) {
		.two-col,
		:global(.three-col) {
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
		color: var(--rose);
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
		background: var(--rose);
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
		color: var(--rose);
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
		color: var(--rose);
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
	.prev-link {
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
	.prev-link:hover {
		border-color: var(--rose);
		color: var(--rose);
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
		border-color: var(--amber);
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
		color: var(--amber);
	}

	/* ═══════════════════════════════════════
   DEMO-SPECIFIC
═══════════════════════════════════════ */

	/* Shape Personality Explorer */
	#shape-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
		background: #0a0f18;
	}
	.shape-axes {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-top: 1rem;
	}
	.axis-track {
		position: relative;
	}
	.axis-label-row {
		display: flex;
		justify-content: space-between;
		font-size: 10px;
		color: var(--muted);
		letter-spacing: 0.1em;
		text-transform: uppercase;
		margin-bottom: 0.4rem;
	}
	.axis-label-row span:last-child {
		color: var(--rose);
	}
	.axis-slider {
		width: 100%;
		-webkit-appearance: none;
		height: 3px;
		background: linear-gradient(to right, var(--border2), var(--border2));
		outline: none;
		display: block;
	}
	.axis-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: var(--rose);
		cursor: pointer;
		border: 2px solid #fff;
	}
	.personality-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-top: 1rem;
	}
	:global(.p-tag) {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
		letter-spacing: 0.08em;
		transition: all 0.25s;
	}
	.shape-desc {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.75rem;
		min-height: 2.4em;
		line-height: 1.6;
		transition: color 0.2s;
	}

	/* Icon Construction Lab */
	#icon-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
		background: #080c12;
		cursor: crosshair;
	}
	.icon-controls {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
		gap: 0.5rem;
		margin: 0.75rem 0;
	}
	.icon-tool {
		padding: 5px 10px;
		font-size: 11px;
		font-family: 'IBM Plex Mono', monospace;
		border: 1px solid var(--border);
		background: transparent;
		color: var(--muted);
		cursor: pointer;
		transition: all 0.15s;
		text-align: left;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.icon-tool:hover {
		border-color: var(--rose);
		color: var(--rose);
	}
	.icon-tool.active {
		border-color: var(--rose);
		color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
	}
	.icon-tool-icon {
		font-size: 14px;
		line-height: 1;
	}
	.icon-action-row {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-top: 0.75rem;
	}
	.icon-size-preview {
		display: flex;
		align-items: flex-end;
		gap: 1rem;
		margin-top: 1rem;
		padding: 1rem;
		background: var(--code-bg);
		border: 1px solid var(--border);
	}
	.icon-size-label {
		font-size: 9px;
		color: var(--muted);
		letter-spacing: 0.1em;
		text-transform: uppercase;
		display: block;
		text-align: center;
		margin-top: 0.3rem;
	}
	.icon-size-wrap {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	/* Brand Personality Matcher */
	.brand-scenarios {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}
	:global(.brand-scenario) {
		border: 1px solid var(--border);
		padding: 1.25rem;
	}
	:global(.brand-scenario-label) {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.75rem;
	}
	:global(.brand-prompt) {
		font-size: 13px;
		color: #fff;
		margin-bottom: 1rem;
	}
	:global(.shape-options) {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
		margin-bottom: 0.75rem;
	}
	:global(.shape-choice) {
		padding: 4px;
		border: 2px solid var(--border);
		cursor: pointer;
		transition: all 0.15s;
		background: var(--code-bg);
	}
	:global(.shape-choice:hover) {
		border-color: var(--rose);
	}
	:global(.shape-choice.selected) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 8%, var(--code-bg));
	}
	:global(.shape-choice.correct-reveal) {
		border-color: var(--sage);
	}
	:global(.shape-choice.wrong-reveal) {
		border-color: var(--rose);
		opacity: 0.5;
	}
	:global(.brand-feedback) {
		font-size: 12px;
		color: var(--muted);
		min-height: 1.4em;
		margin-top: 0.5rem;
	}
	:global(.brand-feedback.ok) {
		color: var(--sage);
	}
	:global(.brand-feedback.bad) {
		color: var(--rose);
	}

	/* Icon Rules checker */
	.icon-rules-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 1rem;
		margin-top: 1rem;
	}
	:global(.icon-rule-card) {
		border: 1px solid var(--border);
		background: var(--code-bg);
		padding: 1rem;
	}
	:global(.icon-rule-card-label) {
		font-size: 10px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		margin-bottom: 0.75rem;
		font-weight: 600;
	}
	:global(.icon-rule-canvas) {
		display: block;
		width: 100%;
		border: 1px solid var(--border2);
	}
	:global(.icon-rule-verdict) {
		font-size: 11px;
		margin-top: 0.5rem;
		padding: 3px 8px;
		border-left: 2px solid;
		line-height: 1.5;
	}
	:global(.icon-rule-verdict.pass) {
		border-color: var(--sage);
		color: var(--sage);
	}
	:global(.icon-rule-verdict.fail) {
		border-color: var(--rose);
		color: var(--rose);
	}

	/* Assessment */
	.assess-question {
		border: 1px solid var(--border);
		margin: 1.5rem 0;
	}
	.assess-q-header {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--border);
		background: var(--raised);
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.assess-body {
		padding: 1.25rem;
	}
	.assess-canvas-row {
		display: flex;
		gap: 1rem;
		margin: 0.75rem 0;
		flex-wrap: wrap;
	}
	:global(.assess-option-canvas) {
		cursor: pointer;
		border: 2px solid var(--border);
		transition: all 0.15s;
		display: block;
	}
	:global(.assess-option-canvas:hover) {
		border-color: var(--rose);
	}
	:global(.assess-option-canvas.correct-reveal) {
		border-color: var(--sage);
	}
	:global(.assess-option-canvas.wrong-reveal) {
		border-color: var(--rose);
		opacity: 0.55;
	}
	:global(.assess-canvas-label) {
		font-size: 10px;
		color: var(--muted);
		text-align: center;
		display: block;
		margin-top: 0.3rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
	.assess-feedback {
		font-size: 12px;
		margin-top: 0.75rem;
		min-height: 1.4em;
		color: var(--muted);
	}
	:global(.assess-feedback.ok) {
		color: var(--sage);
	}
	:global(.assess-feedback.bad) {
		color: var(--rose);
	}
</style>
