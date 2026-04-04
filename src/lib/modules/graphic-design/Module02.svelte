<script lang="ts">
	/* eslint-disable @typescript-eslint/no-unused-vars, no-undef */
	import { onMount } from 'svelte';

	let actions: Record<string, unknown> = new Proxy(
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
		/* ═══════════════════════════════════════
   READING PROGRESS
═══════════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const pct = el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight);
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width = pct * 100 + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		/* ═══════════════════════════════════════
   EYE PATH DEMO
═══════════════════════════════════════ */
		const epCanvas = document.getElementById('ep-canvas');
		const epCtx = epCanvas.getContext('2d');
		const EW = epCanvas.width,
			EH = epCanvas.height;

		let epMode = 'strong';
		let epAnimId = null;
		let epStep = 0;
		let epT = 0; // 0-1 within a segment

		const EP_MODES = {
			strong: {
				info: '<strong>Strong Hierarchy</strong> — One clear primary element anchors the eye. The path moves logically from the highest-contrast element (the face/subject) to the headline, then to the sub-label, then to the call-to-action. The eye never has to backtrack.',
				waypoints: [
					{ x: 0.22, y: 0.38, r: 18, label: '1', color: '#9b6dff' },
					{ x: 0.56, y: 0.32, r: 13, label: '2', color: '#9b6dff' },
					{ x: 0.57, y: 0.58, r: 9, label: '3', color: '#9b6dff' },
					{ x: 0.57, y: 0.76, r: 6, label: '4', color: '#9b6dff' }
				],
				draw: drawStrongComposition
			},
			conflict: {
				info: '<strong>Competing Focal Points</strong> — Two elements share equal visual dominance. The eye lands on one, then the other, oscillates, and cannot commit. The viewer experiences this as confusion or visual tension without being able to name it.',
				waypoints: [
					{ x: 0.22, y: 0.38, r: 16, label: '1', color: '#e85d8a' },
					{ x: 0.7, y: 0.38, r: 16, label: '2', color: '#e85d8a' },
					{ x: 0.22, y: 0.38, r: 16, label: '3', color: '#e85d8a' },
					{ x: 0.7, y: 0.38, r: 16, label: '4', color: '#e85d8a' },
					{ x: 0.45, y: 0.72, r: 7, label: '5', color: '#e85d8a' }
				],
				draw: drawConflictComposition
			},
			flat: {
				info: '<strong>No Hierarchy</strong> — All elements share the same visual weight. The eye has no logical entry point and moves erratically, attempting to find a starting point. First impressions form in under 50ms — if nothing says "start here," the viewer moves on.',
				waypoints: [
					{ x: 0.22, y: 0.3, r: 8, label: '1', color: '#f5a623' },
					{ x: 0.65, y: 0.55, r: 8, label: '2', color: '#f5a623' },
					{ x: 0.4, y: 0.72, r: 8, label: '3', color: '#f5a623' },
					{ x: 0.78, y: 0.28, r: 8, label: '4', color: '#f5a623' },
					{ x: 0.15, y: 0.65, r: 8, label: '5', color: '#f5a623' },
					{ x: 0.55, y: 0.35, r: 8, label: '6', color: '#f5a623' }
				],
				draw: drawFlatComposition
			}
		};

		function drawBaseField(ctx) {
			ctx.fillStyle = '#0c1420';
			ctx.fillRect(0, 0, EW, EH);
		}

		function drawStrongComposition() {
			const ctx = epCtx;
			drawBaseField(ctx);

			// Subject — face block, left third
			const fx = Math.floor(EW * 0.22),
				fy = Math.floor(EH * 0.38);
			ctx.fillStyle = '#1a2e44';
			ctx.fillRect(Math.floor(EW * 0.04), 0, Math.floor(EW * 0.36), EH);
			ctx.fillStyle = '#d4a07a';
			ctx.beginPath();
			ctx.ellipse(fx, fy, 52, 60, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#1a2e44';
			ctx.beginPath();
			ctx.ellipse(fx - 16, fy - 10, 6, 5, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.beginPath();
			ctx.ellipse(fx + 16, fy - 10, 6, 5, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#0d1c2a';
			ctx.fillRect(fx - 52, Math.floor(EH * 0.56), 104, EH);

			// Primary title — large, white, high contrast
			ctx.fillStyle = '#ffffff';
			ctx.font = `bold ${Math.floor(EH * 0.15)}px Syne, sans-serif`;
			ctx.fillText('DESIGN', Math.floor(EW * 0.44), Math.floor(EH * 0.35));

			// Secondary — medium, accent
			ctx.fillStyle = '#9b6dff';
			ctx.font = `bold ${Math.floor(EH * 0.11)}px Syne, sans-serif`;
			ctx.fillText('THINKING', Math.floor(EW * 0.44), Math.floor(EH * 0.52));

			// Tertiary — small, muted
			ctx.fillStyle = '#5a7090';
			ctx.font = `${Math.floor(EH * 0.055)}px IBM Plex Mono, monospace`;
			ctx.fillText('A course for systematic minds', Math.floor(EW * 0.44), Math.floor(EH * 0.65));

			// CTA — tiny, low weight
			ctx.fillStyle = '#2a4060';
			ctx.fillRect(Math.floor(EW * 0.44), Math.floor(EH * 0.72), 140, 22);
			ctx.fillStyle = '#5a7090';
			ctx.font = `${Math.floor(EH * 0.045)}px IBM Plex Mono, monospace`;
			ctx.fillText('ENROLL NOW →', Math.floor(EW * 0.455), Math.floor(EH * 0.775));
		}

		function drawConflictComposition() {
			const ctx = epCtx;
			drawBaseField(ctx);

			// TWO competing subjects — same size, same contrast
			const r = 55;
			ctx.fillStyle = '#d4a07a';
			ctx.beginPath();
			ctx.ellipse(Math.floor(EW * 0.22), Math.floor(EH * 0.38), r, r + 10, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#c4907a';
			ctx.beginPath();
			ctx.ellipse(Math.floor(EW * 0.7), Math.floor(EH * 0.38), r, r + 10, 0, 0, Math.PI * 2);
			ctx.fill();

			// Eyes on both
			[
				[0.22, 0.38],
				[0.7, 0.38]
			].forEach(([px, py]) => {
				ctx.fillStyle = '#1a2e44';
				ctx.beginPath();
				ctx.ellipse(EW * px - 14, EH * py - 8, 5, 4, 0, 0, Math.PI * 2);
				ctx.fill();
				ctx.beginPath();
				ctx.ellipse(EW * px + 14, EH * py - 8, 5, 4, 0, 0, Math.PI * 2);
				ctx.fill();
			});

			// Shared title — dead center, medium weight (contributes to confusion)
			ctx.fillStyle = '#8090a8';
			ctx.font = `${Math.floor(EH * 0.08)}px IBM Plex Mono, monospace`;
			ctx.textAlign = 'center';
			ctx.fillText('featuring two guests', EW / 2, EH * 0.75);
			ctx.textAlign = 'left';

			// Labels beneath each — same weight
			ctx.fillStyle = '#ffffff';
			ctx.font = `bold ${Math.floor(EH * 0.07)}px Syne, sans-serif`;
			ctx.textAlign = 'center';
			ctx.fillText('ALEX', Math.floor(EW * 0.22), Math.floor(EH * 0.62));
			ctx.fillText('JORDAN', Math.floor(EW * 0.7), Math.floor(EH * 0.62));
			ctx.textAlign = 'left';
		}

		function drawFlatComposition() {
			const ctx = epCtx;
			drawBaseField(ctx);

			// Six elements, all similar weight
			const items = [
				{ x: 0.1, y: 0.22, w: 0.2, h: 0.09, col: '#2a4060', text: 'EPISODE 47', ts: 11 },
				{ x: 0.5, y: 0.18, w: 0.22, h: 0.09, col: '#2a3855', text: 'subscribe', ts: 11 },
				{ x: 0.1, y: 0.4, w: 0.35, h: 0.12, col: '#243550', text: 'Design Basics', ts: 13 },
				{ x: 0.1, y: 0.6, w: 0.3, h: 0.1, col: '#1e2e45', text: 'watch now', ts: 12 },
				{ x: 0.55, y: 0.45, w: 0.38, h: 0.1, col: '#253348', text: 'this week only', ts: 12 },
				{ x: 0.4, y: 0.72, w: 0.28, h: 0.09, col: '#1a2840', text: 'new video', ts: 11 }
			];
			items.forEach((it) => {
				ctx.fillStyle = it.col;
				ctx.fillRect(
					Math.floor(EW * it.x),
					Math.floor(EH * it.y),
					Math.floor(EW * it.w),
					Math.floor(EH * it.h)
				);
				ctx.fillStyle = '#708aaa';
				ctx.font = `${it.ts}px IBM Plex Mono, monospace`;
				ctx.fillText(
					it.text,
					Math.floor(EW * it.x) + 8,
					Math.floor(EH * it.y) + Math.floor(EH * it.h) * 0.64
				);
			});
		}

		let epDotX = 0,
			epDotY = 0;
		let epPathDrawn = []; // segments drawn so far
		let epAnimating = false;

		function drawEpFrame() {
			const mode = EP_MODES[epMode];
			mode.draw();

			const wps = mode.waypoints;

			// Draw completed path segments
			epPathDrawn.forEach((seg) => {
				ctx_ep_drawSegment(seg.x1, seg.y1, seg.x2, seg.y2, seg.color, 1.0);
			});

			// Draw waypoint numbers (all visible)
			wps.forEach((wp, i) => {
				const px = EW * wp.x,
					py = EH * wp.y;
				if (i < epStep || (i === epStep && epT > 0.05)) {
					ctx_ep_drawWaypoint(px, py, wp.label, wp.color, 1.0);
				}
			});

			// Animate current segment
			if (epAnimating && epStep < wps.length - 1) {
				const a = wps[epStep],
					b = wps[epStep + 1];
				const ax = EW * a.x,
					ay = EH * a.y,
					bx = EW * b.x,
					by = EH * b.y;
				const cx = ax + (bx - ax) * epT,
					cy = ay + (by - ay) * epT;

				// Partial path
				ctx_ep_drawSegment(ax, ay, cx, cy, a.color, 0.8);

				// Animated dot
				epCtx.beginPath();
				epCtx.arc(cx, cy, 7, 0, Math.PI * 2);
				epCtx.fillStyle = 'rgba(255,255,255,0.95)';
				epCtx.fill();
				epCtx.beginPath();
				epCtx.arc(cx, cy, 4, 0, Math.PI * 2);
				epCtx.fillStyle = a.color;
				epCtx.fill();
			}
		}

		function ctx_ep_drawSegment(x1, y1, x2, y2, color, alpha) {
			epCtx.save();
			epCtx.globalAlpha = alpha;
			epCtx.strokeStyle = color;
			epCtx.lineWidth = 2;
			epCtx.setLineDash([6, 4]);
			epCtx.beginPath();
			epCtx.moveTo(x1, y1);
			epCtx.lineTo(x2, y2);
			epCtx.stroke();
			epCtx.setLineDash([]);
			epCtx.restore();
		}

		function ctx_ep_drawWaypoint(px, py, label, color, alpha) {
			epCtx.save();
			epCtx.globalAlpha = alpha;
			epCtx.beginPath();
			epCtx.arc(px, py, 13, 0, Math.PI * 2);
			epCtx.strokeStyle = color;
			epCtx.lineWidth = 1.5;
			epCtx.stroke();
			epCtx.fillStyle = color + '30';
			epCtx.fill();
			epCtx.fillStyle = '#fff';
			epCtx.font = 'bold 11px IBM Plex Mono, monospace';
			epCtx.textAlign = 'center';
			epCtx.fillText(label, px, py + 4);
			epCtx.textAlign = 'left';
			epCtx.restore();
		}

		function setEpMode(mode) {
			epMode = mode;
			epStep = 0;
			epT = 0;
			epPathDrawn = [];
			epAnimating = false;
			if (epAnimId) {
				cancelAnimationFrame(epAnimId);
				epAnimId = null;
			}
			document.getElementById('ep-btn-strong').classList.toggle('active', mode === 'strong');
			document.getElementById('ep-btn-conflict').classList.toggle('active', mode === 'conflict');
			document.getElementById('ep-btn-flat').classList.toggle('active', mode === 'flat');
			drawEpFrame();
			document.getElementById('ep-info').innerHTML =
				'Press <strong style="color:var(--violet)">▶ Play Path</strong> to animate the eye movement through this composition.';
		}

		function playEyePath() {
			if (epAnimId) {
				cancelAnimationFrame(epAnimId);
				epAnimId = null;
			}
			epStep = 0;
			epT = 0;
			epPathDrawn = [];
			epAnimating = true;

			const SPEED = 0.018;
			const wps = EP_MODES[epMode].waypoints;

			function tick() {
				epT += SPEED;
				if (epT >= 1) {
					epT = 0;
					// Commit this segment
					const a = wps[epStep],
						b = wps[epStep + 1];
					epPathDrawn.push({
						x1: EW * a.x,
						y1: EH * a.y,
						x2: EW * b.x,
						y2: EH * b.y,
						color: a.color
					});
					epStep++;
					if (epStep >= wps.length - 1) {
						epAnimating = false;
						drawEpFrame();
						document.getElementById('ep-info').innerHTML = EP_MODES[epMode].info;
						return;
					}
				}
				drawEpFrame();
				epAnimId = requestAnimationFrame(tick);
			}
			epAnimId = requestAnimationFrame(tick);
		}

		function resetEyePath() {
			if (epAnimId) {
				cancelAnimationFrame(epAnimId);
				epAnimId = null;
			}
			epStep = 0;
			epT = 0;
			epPathDrawn = [];
			epAnimating = false;
			drawEpFrame();
			document.getElementById('ep-info').innerHTML =
				'Press <strong style="color:var(--violet)">▶ Play Path</strong> to animate the eye movement through this composition.';
		}

		// Init
		drawEpFrame();

		/* ═══════════════════════════════════════
   RULE OF THIRDS DEMO
═══════════════════════════════════════ */
		const rotCanvas = document.getElementById('rot-canvas');
		const rotCtx = rotCanvas.getContext('2d');
		const RW = rotCanvas.width,
			RH = rotCanvas.height;

		let rotShowGrid = false;
		let rotSubject = { x: RW / 2, y: RH / 2, w: 100, h: 130 }; // center start
		let rotDragging = false;
		let rotDragOff = { x: 0, y: 0 };

		function getRotPowerPoints() {
			return [
				{ x: RW / 3, y: RH / 3 },
				{ x: (2 * RW) / 3, y: RH / 3 },
				{ x: RW / 3, y: (2 * RH) / 3 },
				{ x: (2 * RW) / 3, y: (2 * RH) / 3 }
			];
		}

		function calcRotScore() {
			const sx = rotSubject.x,
				sy = rotSubject.y;
			const pts = getRotPowerPoints();
			let minDist = Infinity;
			pts.forEach((p) => {
				const d = Math.sqrt((sx - p.x) ** 2 + (sy - p.y) ** 2);
				if (d < minDist) minDist = d;
			});
			// Score: 100 at power point, 0 at max distance (RW/2)
			const maxD = Math.sqrt(RW * RW + RH * RH) * 0.5;
			// Center penalty
			const cDist = Math.sqrt((sx - RW / 2) ** 2 + (sy - RH / 2) ** 2);
			const centerPenalty = Math.max(0, 1 - cDist / (RW * 0.15));
			const rawScore = Math.max(0, 1 - minDist / (RW * 0.35));
			return Math.round((rawScore * 0.8 + (1 - centerPenalty) * 0.2) * 100);
		}

		function drawRotFrame() {
			const ctx = rotCtx;

			// Background
			ctx.fillStyle = '#0c1420';
			ctx.fillRect(0, 0, RW, RH);

			// Horizon gradient
			const bg = ctx.createLinearGradient(0, 0, 0, RH * 0.7);
			bg.addColorStop(0, '#0e1e30');
			bg.addColorStop(1, '#0c1420');
			ctx.fillStyle = bg;
			ctx.fillRect(0, 0, RW, RH * 0.7);
			ctx.fillStyle = '#0a1018';
			ctx.fillRect(0, RH * 0.7, RW, RH * 0.3);

			// Subject block
			const sx = rotSubject.x,
				sy = rotSubject.y;
			const sw = rotSubject.w,
				sh = rotSubject.h;

			// Shadow
			ctx.save();
			ctx.shadowColor = 'rgba(155, 109, 255, 0.25)';
			ctx.shadowBlur = 20;
			ctx.fillStyle = '#1e3050';
			ctx.fillRect(sx - sw / 2, sy - sh / 2, sw, sh);
			ctx.restore();

			// Subject face
			ctx.fillStyle = '#d4a07a';
			ctx.beginPath();
			ctx.ellipse(sx, sy - sh * 0.05, sw * 0.38, sh * 0.35, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#1a2e44';
			ctx.beginPath();
			ctx.ellipse(sx - 10, sy - sh * 0.11, 5, 4, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.beginPath();
			ctx.ellipse(sx + 10, sy - sh * 0.11, 5, 4, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#1a2e44';
			ctx.fillRect(sx - sw / 2, sy + sh * 0.2, sw, sh * 0.3);

			// Subject label
			ctx.fillStyle = 'rgba(155,109,255,0.9)';
			ctx.font = '9px IBM Plex Mono, monospace';
			ctx.textAlign = 'center';
			ctx.fillText('SUBJECT', sx, sy - sh / 2 - 5);
			ctx.textAlign = 'left';

			// Grid overlay
			if (rotShowGrid) {
				const pts = getRotPowerPoints();

				ctx.strokeStyle = 'rgba(155, 109, 255, 0.3)';
				ctx.lineWidth = 1;
				ctx.setLineDash([5, 5]);
				[RW / 3, (2 * RW) / 3].forEach((x) => {
					ctx.beginPath();
					ctx.moveTo(x, 0);
					ctx.lineTo(x, RH);
					ctx.stroke();
				});
				[RH / 3, (2 * RH) / 3].forEach((y) => {
					ctx.beginPath();
					ctx.moveTo(0, y);
					ctx.lineTo(RW, y);
					ctx.stroke();
				});
				ctx.setLineDash([]);

				// Power points
				pts.forEach((p) => {
					const dist = Math.sqrt((sx - p.x) ** 2 + (sy - p.y) ** 2);
					const near = dist < 60;
					ctx.beginPath();
					ctx.arc(p.x, p.y, near ? 10 : 6, 0, Math.PI * 2);
					ctx.fillStyle = near ? 'rgba(155,109,255,0.9)' : 'rgba(155,109,255,0.35)';
					ctx.fill();
					if (near) {
						ctx.beginPath();
						ctx.arc(p.x, p.y, 18, 0, Math.PI * 2);
						ctx.strokeStyle = 'rgba(155,109,255,0.5)';
						ctx.lineWidth = 1.5;
						ctx.stroke();
					}
				});
			}

			// Score update
			const score = calcRotScore();
			const bar = document.getElementById('rot-score-bar');
			const pctEl = document.getElementById('rot-score-pct');
			bar.style.width = score + '%';
			bar.style.background =
				score > 75 ? 'var(--sage)' : score > 45 ? 'var(--violet)' : 'var(--rose)';
			pctEl.textContent = score + ' / 100';

			const tipEl = document.getElementById('rot-tip');
			const cDist = Math.sqrt((sx - RW / 2) ** 2 + (sy - RH / 2) ** 2);
			if (cDist < RW * 0.1) {
				tipEl.style.color = 'var(--rose)';
				tipEl.textContent =
					'Subject is near dead-center — stable, but low tension. Try dragging to a grid intersection.';
			} else if (score > 75) {
				tipEl.style.color = 'var(--sage)';
				tipEl.textContent =
					'Subject is near a power point — strong compositional tension. The frame feels dynamic.';
			} else {
				tipEl.style.color = 'var(--muted)';
				tipEl.textContent =
					'Move toward a rule-of-thirds intersection to increase composition strength.';
			}
		}

		function toggleRotGrid() {
			rotShowGrid = !rotShowGrid;
			document.getElementById('rot-grid-btn').classList.toggle('active', rotShowGrid);
			document.getElementById('rot-grid-btn').textContent = rotShowGrid ? 'Hide Grid' : 'Show Grid';
			drawRotFrame();
		}

		function resetRotSubject() {
			rotSubject.x = RW / 2;
			rotSubject.y = RH / 2;
			drawRotFrame();
		}

		function getRotPos(e) {
			const rect = rotCanvas.getBoundingClientRect();
			const scaleX = RW / rect.width,
				scaleY = RH / rect.height;
			const src = e.touches ? e.touches[0] : e;
			return { x: (src.clientX - rect.left) * scaleX, y: (src.clientY - rect.top) * scaleY };
		}

		rotCanvas.addEventListener('mousedown', (e) => {
			const p = getRotPos(e);
			const dx = p.x - rotSubject.x,
				dy = p.y - rotSubject.y;
			if (Math.abs(dx) < 60 && Math.abs(dy) < 70) {
				rotDragging = true;
				rotDragOff = { x: dx, y: dy };
			}
		});
		rotCanvas.addEventListener(
			'touchstart',
			(e) => {
				e.preventDefault();
				const p = getRotPos(e);
				rotDragging = true;
				rotDragOff = { x: p.x - rotSubject.x, y: p.y - rotSubject.y };
			},
			{ passive: false }
		);
		_addDocListener('mousemove', (e) => {
			if (!rotDragging) return;
			const p = getRotPos(e);
			rotSubject.x = Math.max(50, Math.min(RW - 50, p.x - rotDragOff.x));
			rotSubject.y = Math.max(65, Math.min(RH - 65, p.y - rotDragOff.y));
			drawRotFrame();
		});
		_addDocListener(
			'touchmove',
			(e) => {
				if (!rotDragging) return;
				const p = getRotPos(e);
				rotSubject.x = Math.max(50, Math.min(RW - 50, p.x - rotDragOff.x));
				rotSubject.y = Math.max(65, Math.min(RH - 65, p.y - rotDragOff.y));
				drawRotFrame();
			},
			{ passive: false }
		);
		_addDocListener('mouseup', () => {
			rotDragging = false;
		});
		_addDocListener('touchend', () => {
			rotDragging = false;
		});

		drawRotFrame();

		/* ═══════════════════════════════════════
   CONTRAST DEMO
═══════════════════════════════════════ */
		const ctCanvas = document.getElementById('ct-canvas');
		const ctCtx = ctCanvas.getContext('2d');
		const CTW = ctCanvas.width,
			CTH = ctCanvas.height;

		// 4x3 grid of circles
		const CT_COLS = 4,
			CT_ROWS = 3;
		const CT_TARGET = 5; // index of target element

		function getCtValues() {
			return {
				size: parseFloat(document.getElementById('ct-size').value),
				bright: parseFloat(document.getElementById('ct-bright').value),
				hue: parseFloat(document.getElementById('ct-hue').value)
			};
		}

		function drawContrast() {
			const ctx = ctCtx;
			const v = getCtValues();
			ctx.fillStyle = '#0c1420';
			ctx.fillRect(0, 0, CTW, CTH);

			const cellW = CTW / CT_COLS,
				cellH = CTH / CT_ROWS;
			const baseR = Math.min(cellW, cellH) * 0.28;

			for (let i = 0; i < CT_COLS * CT_ROWS; i++) {
				const col = i % CT_COLS,
					row = Math.floor(i / CT_COLS);
				const cx = cellW * col + cellW / 2;
				const cy = cellH * row + cellH / 2;

				let r = baseR;
				let fillColor;
				const isTarget = i === CT_TARGET;

				if (isTarget) {
					r = baseR * v.size;
					if (v.hue > 0.05) {
						const hue = Math.round(v.hue * 280);
						const sat = Math.round(40 + v.hue * 60);
						const lit = Math.round(v.bright * 65 + 15);
						fillColor = `hsl(${hue}, ${sat}%, ${lit}%)`;
					} else {
						const lit = Math.round(v.bright * 85 + 8);
						fillColor = `hsl(220, 15%, ${lit}%)`;
					}

					// Glow if highly contrasted
					const contrast = Math.abs(v.bright - 0.5) * 2 + v.hue * 0.6 + ((v.size - 1) / 2) * 0.4;
					if (contrast > 0.4) {
						ctx.save();
						ctx.shadowColor = fillColor;
						ctx.shadowBlur = 16 * contrast;
						ctx.beginPath();
						ctx.arc(cx, cy, r, 0, Math.PI * 2);
						ctx.fillStyle = fillColor;
						ctx.fill();
						ctx.restore();
					}
				} else {
					// Background elements: if chaos mode, each gets random properties
					if (v.size > 2.5 && v.bright > 0.75 && v.hue > 0.75) {
						// chaos — everyone contrasts
						const hue = (i * 37 + 120) % 360;
						const lit = 35 + (i % 3) * 15;
						const sr = baseR * (0.7 + (i % 3) * 0.3);
						fillColor = `hsl(${hue}, 60%, ${lit}%)`;
						ctx.beginPath();
						ctx.arc(cx, cy, sr, 0, Math.PI * 2);
						ctx.fillStyle = fillColor;
						ctx.fill();
						continue;
					} else {
						fillColor = 'hsl(220, 12%, 22%)';
					}
				}

				ctx.beginPath();
				ctx.arc(cx, cy, r, 0, Math.PI * 2);
				ctx.fillStyle = fillColor;
				ctx.fill();
			}

			// Note
			const v2 = getCtValues();
			const noteEl = document.getElementById('ct-note');
			const totalContrast =
				Math.abs(v2.bright - 0.5) * 2 + v2.hue * 0.6 + ((v2.size - 1) / 2) * 0.4;
			const isChaos = v2.size > 2.5 && v2.bright > 0.75 && v2.hue > 0.75;

			if (isChaos) {
				noteEl.style.color = 'var(--rose)';
				noteEl.textContent =
					'Maximum contrast on all elements — nothing stands out because everything is competing. The field is equally chaotic.';
			} else if (totalContrast > 0.7) {
				noteEl.style.color = 'var(--sage)';
				noteEl.textContent =
					'Strong focal point established. The target element dominates because it is distinctly different from its neighbors — contrast is relational.';
			} else if (totalContrast > 0.3) {
				noteEl.style.color = 'var(--violet)';
				noteEl.textContent =
					'A focal point is forming. Increase the difference to make it stronger.';
			} else {
				noteEl.style.color = 'var(--muted)';
				noteEl.textContent = 'Adjust a property to see how contrast directs attention.';
			}

			document.getElementById('ct-size-val').textContent = parseFloat(v.size).toFixed(1) + '×';
			document.getElementById('ct-bright-val').textContent = Math.round(v.bright * 100) + '%';
			document.getElementById('ct-hue-val').textContent = Math.round(v.hue * 100) + '%';
		}

		function updateContrast() {
			drawContrast();
		}

		function setCtPreset(p) {
			const s = document.getElementById('ct-size');
			const b = document.getElementById('ct-bright');
			const h = document.getElementById('ct-hue');
			if (p === 'size') {
				s.value = '2.8';
				b.value = '0.5';
				h.value = '0';
			}
			if (p === 'value') {
				s.value = '1';
				b.value = '0.92';
				h.value = '0';
			}
			if (p === 'color') {
				s.value = '1';
				b.value = '0.5';
				h.value = '0.85';
			}
			if (p === 'chaos') {
				s.value = '3';
				b.value = '0.9';
				h.value = '0.9';
			}
			if (p === 'reset') {
				s.value = '1';
				b.value = '0.5';
				h.value = '0';
			}
			drawContrast();
		}

		drawContrast();

		/* ═══════════════════════════════════════
   CLUTTERED → CLEAN DEMO
═══════════════════════════════════════ */
		const ccCanvas = document.getElementById('cc-canvas');
		const ccCtx = ccCanvas.getContext('2d');
		const CCW = ccCanvas.width,
			CCH = ccCanvas.height;

		let ccMode = 'bad';

		const CC_ANNOTATIONS = {
			bad: [
				{ cls: 'bad', text: 'No consistent margin — text touches edges at irregular distances' },
				{
					cls: 'bad',
					text: 'Three competing focal points: title, subhead, and photo are similar weights'
				},
				{ cls: 'bad', text: 'Five different font sizes with no clear hierarchy relationship' },
				{ cls: 'bad', text: 'Elements are center, left, and right aligned with no shared axis' },
				{
					cls: 'bad',
					text: 'Decorative element (circle) adds visual noise without communicating anything'
				}
			],
			good: [
				{
					cls: 'good',
					text: 'Consistent 24px margin on all sides — every element respects the same boundary'
				},
				{
					cls: 'good',
					text: 'One dominant primary element (title), two clear secondary elements, one tertiary'
				},
				{
					cls: 'good',
					text: 'Type scale: 38px / 22px / 14px / 11px — each tier clearly subordinate to the one above'
				},
				{
					cls: 'good',
					text: 'Strict left-axis alignment creates a single invisible vertical line'
				},
				{
					cls: 'good',
					text: 'Spacing between groups creates perceived sections without visual dividers'
				}
			]
		};

		function drawCluttered() {
			const ctx = ccCtx;
			ctx.fillStyle = '#0c1520';
			ctx.fillRect(0, 0, CCW, CCH);

			// Decorative circle — noise
			ctx.beginPath();
			ctx.arc(CCW * 0.82, CCH * 0.22, 68, 0, Math.PI * 2);
			ctx.fillStyle = 'rgba(100,80,200,0.12)';
			ctx.fill();
			ctx.strokeStyle = 'rgba(100,80,200,0.2)';
			ctx.lineWidth = 1;
			ctx.stroke();

			// Photo block — takes lots of visual attention
			ctx.fillStyle = '#1a2c44';
			ctx.fillRect(CCW * 0.58, CCH * 0.08, CCW * 0.36, CCH * 0.42);
			ctx.fillStyle = '#d4a07a';
			ctx.beginPath();
			ctx.ellipse(CCW * 0.76, CCH * 0.22, 38, 44, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#1a2c44';
			ctx.fillRect(CCW * 0.58, CCH * 0.34, CCW * 0.36, CCH * 0.16);

			// Title — large but not dominant enough
			ctx.fillStyle = '#c8d8e8';
			ctx.font = `bold 28px Syne, sans-serif`;
			ctx.textAlign = 'center';
			ctx.fillText('DESIGN CHANNEL', CCW * 0.3, CCH * 0.18);

			// Subhead — too close in weight to title
			ctx.fillStyle = '#9b6dff';
			ctx.font = `bold 22px IBM Plex Mono, monospace`;
			ctx.fillText('NEW SERIES', CCW * 0.3, CCH * 0.34);

			// Date — same weight as subhead
			ctx.fillStyle = '#c8d8e8';
			ctx.font = `18px IBM Plex Mono, monospace`;
			ctx.fillText('STARTS JAN 15', CCW * 0.3, CCH * 0.5);

			// Random small text, misaligned right
			ctx.textAlign = 'right';
			ctx.fillStyle = '#5a7090';
			ctx.font = `11px IBM Plex Mono, monospace`;
			ctx.fillText('Subscribe for updates', CCW * 0.94, CCH * 0.64);

			// Bottom text, centered again
			ctx.textAlign = 'center';
			ctx.fillStyle = '#4a6080';
			ctx.font = `14px IBM Plex Mono, monospace`;
			ctx.fillText('Visual design · Typography · Motion', CCW * 0.5, CCH * 0.8);
			ctx.fillText('New episode every Thursday', CCW * 0.5, CCH * 0.9);

			ctx.textAlign = 'left';
		}

		function drawClean() {
			const ctx = ccCtx;
			ctx.fillStyle = '#0a1018';
			ctx.fillRect(0, 0, CCW, CCH);

			const M = 24; // consistent margin
			const LX = M; // left alignment axis

			// Accent bar
			ctx.fillStyle = '#9b6dff';
			ctx.fillRect(0, 0, 4, CCH);

			// Primary — title, large, white, maximum contrast
			ctx.fillStyle = '#ffffff';
			ctx.font = `bold 38px Syne, sans-serif`;
			ctx.fillText('DESIGN', LX + 8, CCH * 0.22);

			ctx.fillStyle = '#9b6dff';
			ctx.font = `bold 38px Syne, sans-serif`;
			ctx.fillText('CHANNEL', LX + 8, CCH * 0.37);

			// Eyebrow label — tertiary, above title
			ctx.fillStyle = '#5a7090';
			ctx.font = `10px IBM Plex Mono, monospace`;
			ctx.fillText('NEW SERIES  ·  EST. 2025', LX + 8, CCH * 0.11);

			// Divider line — short, aligned
			ctx.fillStyle = '#1e3050';
			ctx.fillRect(LX + 8, CCH * 0.41, 180, 1);

			// Secondary — date, clearly subordinate
			ctx.fillStyle = '#d0dbe8';
			ctx.font = `bold 18px IBM Plex Mono, monospace`;
			ctx.fillText('Starts January 15', LX + 8, CCH * 0.54);

			// Tertiary — description, muted
			ctx.fillStyle = '#5a7090';
			ctx.font = `12px IBM Plex Mono, monospace`;
			ctx.fillText('Visual design · Typography · Motion', LX + 8, CCH * 0.65);

			// CTA — bottom, consistent margin
			ctx.fillStyle = '#1a2e48';
			ctx.fillRect(LX + 8, CCH * 0.76, 140, 26);
			ctx.fillStyle = '#9b6dff';
			ctx.font = `10px IBM Plex Mono, monospace`;
			ctx.fillText('SUBSCRIBE →', LX + 22, CCH * 0.76 + 17);

			// Photo — right column, doesn't compete with text
			ctx.fillStyle = '#131e2e';
			ctx.fillRect(CCW * 0.6, CCH * 0.06, CCW * 0.37, CCH * 0.88);
			ctx.fillStyle = '#d4a07a';
			ctx.beginPath();
			ctx.ellipse(CCW * 0.785, CCH * 0.36, 52, 60, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#131e2e';
			ctx.fillRect(CCW * 0.6, CCH * 0.58, CCW * 0.37, CCH * 0.36);

			// Bottom margin line (visual boundary)
			ctx.fillStyle = '#9b6dff';
			ctx.fillRect(0, CCH - 3, CCW, 3);
		}

		function setCcMode(mode) {
			ccMode = mode;
			document.getElementById('cc-btn-bad').classList.toggle('active', mode === 'bad');
			document.getElementById('cc-btn-good').classList.toggle('active', mode === 'good');

			const label = document.getElementById('cc-state-label');
			if (mode === 'bad') {
				label.textContent = 'Before: Cluttered Layout';
				label.style.color = 'var(--rose)';
				drawCluttered();
			} else {
				label.textContent = 'After: Rebuilt Layout';
				label.style.color = 'var(--sage)';
				drawClean();
			}

			const list = document.getElementById('cc-annotations');
			list.innerHTML = CC_ANNOTATIONS[mode]
				.map((a) => `<div class="cc-item ${a.cls}">${a.text}</div>`)
				.join('');
		}

		setCcMode('bad');

		/* ═══════════════════════════════════════
   DIAGNOSTIC CANVAS
═══════════════════════════════════════ */
		const diagCanvas = document.getElementById('diag-canvas');
		const diagCtx = diagCanvas.getContext('2d');
		const DW = diagCanvas.width,
			DH = diagCanvas.height;

		function drawDiagComposition() {
			const ctx = diagCtx;
			ctx.fillStyle = '#0c1520';
			ctx.fillRect(0, 0, DW, DH);

			// Channel name — correct, dominant
			ctx.fillStyle = '#ffffff';
			ctx.font = `bold 44px Syne, sans-serif`;
			ctx.textAlign = 'center';
			ctx.fillText('VISUAL NOTES', DW / 2, DH * 0.3);

			// Launch date — medium weight
			ctx.fillStyle = '#9b8fd8'; // similar visual weight to description below
			ctx.font = `bold 19px IBM Plex Mono, monospace`;
			ctx.fillText('LAUNCHING MARCH 1ST', DW / 2, DH * 0.52);

			// Topic description — same weight as launch date
			ctx.fillStyle = '#8a9ec8'; // nearly identical to above
			ctx.font = `18px IBM Plex Mono, monospace`; // nearly same size
			ctx.fillText('Design · Motion · Storytelling', DW / 2, DH * 0.68);

			// Tiny label
			ctx.fillStyle = '#3a5070';
			ctx.font = `10px IBM Plex Mono, monospace`;
			ctx.fillText('youtube.com/@visualnotes', DW / 2, DH * 0.85);

			ctx.textAlign = 'left';

			// Annotation arrows pointing to the problem elements
			ctx.strokeStyle = 'rgba(232, 93, 138, 0.4)';
			ctx.lineWidth = 1;
			ctx.setLineDash([3, 3]);
			ctx.beginPath();
			ctx.moveTo(DW * 0.05, DH * 0.52);
			ctx.lineTo(DW * 0.95, DH * 0.52);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(DW * 0.05, DH * 0.68);
			ctx.lineTo(DW * 0.95, DH * 0.68);
			ctx.stroke();
			ctx.setLineDash([]);

			// Bracket showing the problem zone
			ctx.strokeStyle = 'rgba(232, 93, 138, 0.6)';
			ctx.lineWidth = 1.5;
			ctx.beginPath();
			ctx.moveTo(DW * 0.04, DH * 0.44);
			ctx.lineTo(DW * 0.04, DH * 0.76);
			ctx.stroke();
			ctx.fillStyle = 'rgba(232,93,138,0.7)';
			ctx.font = '9px IBM Plex Mono, monospace';
			ctx.save();
			ctx.translate(DW * 0.016, DH * 0.62);
			ctx.rotate(-Math.PI / 2);
			ctx.fillText('SIMILAR WEIGHT', 0, 0);
			ctx.restore();
		}

		drawDiagComposition();

		let diagAnswered = false;
		function handleDiag(el, idx) {
			if (diagAnswered) return;
			diagAnswered = true;
			const opts = document.querySelectorAll('.debug-option');
			opts.forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById('diag-feedback');
			if (idx === 1) {
				el.classList.add('correct');
				fb.style.color = 'var(--sage)';
				fb.innerHTML =
					'<strong style="color:var(--sage)">✓ Correct.</strong> The Channel Name is clearly primary — its size and contrast force the eye there first. But the Launch Date and Topic Description share nearly identical font size, weight, and color. The eye cannot determine which to read second. The fix: reduce the Topic Description to a clearly smaller/lighter tier, making the reading sequence unambiguous.';
			} else {
				el.classList.add('wrong');
				opts[1].classList.add('correct');
				fb.style.color = 'var(--rose)';
				fb.innerHTML =
					'<strong style="color:var(--rose)">✗ Not quite.</strong> The primary problem is that the Launch Date and Topic Description have nearly identical visual weight — the second and third tiers of hierarchy are indistinguishable from each other. More colors, more content, or reducing the title size would not fix this. The hierarchy must make each tier clearly subordinate to the one above it.';
			}
		}

		/* ═══════════════════════════════════════
   QUIZ
═══════════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;
		const explanations = [
			'Correct. Two elements at equal visual weight create visual conflict — the eye oscillates between them. Only one element can be primary at a given moment in the reading sequence.',
			'Correct. Off-center placement creates visual tension — the subject pulls against the frame edges, and that tension generates dynamism. Centered subjects feel more static and formal.',
			'Correct. Contrast is relational. When every element is maximally contrasting, none of them is contrasting relative to any other — the field becomes uniformly chaotic, and the eye cannot find an entry point.',
			'Correct. Proximity creates perceived grouping without any visual elements needed. Space is the separator. Reaching for boxes and dividers is almost always a sign that spacing decisions should be reconsidered first.',
			'Correct. Visual weight is a perception, not a measurement. A small but saturated colored element can outweigh a large grey block because weight is determined by multiple relational properties, not size alone.'
		];
		const wrongMsg =
			'Not quite. Revisit the principle at stake — focus on the perceptual experience of the viewer, not the mechanics of the software.';

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
				fb.textContent = '✗ ' + wrongMsg;
				fb.className = 'feedback bad';
			}
			quizAnswered++;
			if (quizAnswered === 5) {
				const scoreEl = document.getElementById('quiz-score');
				document.getElementById('score-num').textContent = quizScore + ' / 5';
				scoreEl.style.display = 'block';
				setTimeout(() => scoreEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 300);
			}
		}

		if (typeof drawBaseField === 'function') actions.drawBaseField = drawBaseField;
		if (typeof drawStrongComposition === 'function')
			actions.drawStrongComposition = drawStrongComposition;
		if (typeof drawConflictComposition === 'function')
			actions.drawConflictComposition = drawConflictComposition;
		if (typeof drawFlatComposition === 'function')
			actions.drawFlatComposition = drawFlatComposition;
		if (typeof drawEpFrame === 'function') actions.drawEpFrame = drawEpFrame;
		if (typeof ctx_ep_drawSegment === 'function') actions.ctx_ep_drawSegment = ctx_ep_drawSegment;
		if (typeof ctx_ep_drawWaypoint === 'function')
			actions.ctx_ep_drawWaypoint = ctx_ep_drawWaypoint;
		if (typeof setEpMode === 'function') actions.setEpMode = setEpMode;
		if (typeof playEyePath === 'function') actions.playEyePath = playEyePath;
		if (typeof tick === 'function') actions.tick = tick;
		if (typeof resetEyePath === 'function') actions.resetEyePath = resetEyePath;
		if (typeof getRotPowerPoints === 'function') actions.getRotPowerPoints = getRotPowerPoints;
		if (typeof calcRotScore === 'function') actions.calcRotScore = calcRotScore;
		if (typeof drawRotFrame === 'function') actions.drawRotFrame = drawRotFrame;
		if (typeof toggleRotGrid === 'function') actions.toggleRotGrid = toggleRotGrid;
		if (typeof resetRotSubject === 'function') actions.resetRotSubject = resetRotSubject;
		if (typeof getRotPos === 'function') actions.getRotPos = getRotPos;
		if (typeof getCtValues === 'function') actions.getCtValues = getCtValues;
		if (typeof drawContrast === 'function') actions.drawContrast = drawContrast;
		if (typeof updateContrast === 'function') actions.updateContrast = updateContrast;
		if (typeof setCtPreset === 'function') actions.setCtPreset = setCtPreset;
		if (typeof drawCluttered === 'function') actions.drawCluttered = drawCluttered;
		if (typeof drawClean === 'function') actions.drawClean = drawClean;
		if (typeof setCcMode === 'function') actions.setCcMode = setCcMode;
		if (typeof drawDiagComposition === 'function')
			actions.drawDiagComposition = drawDiagComposition;
		if (typeof handleDiag === 'function') actions.handleDiag = handleDiag;
		if (typeof handleQuiz === 'function') actions.handleQuiz = handleQuiz;

		return () => {
			if (typeof epAnimId !== 'undefined' && epAnimId) cancelAnimationFrame(epAnimId);
			_listeners.forEach((l) => l.target.removeEventListener(...l.args));
		};
	});
</script>

<div class="page-wrapper">
	<!-- HEADER -->
	<header class="course-header">
		<div>
			<div class="course-label">Graphic Design &amp; Visual Storytelling</div>
			<div class="course-title">Building a Personal Creative Identity</div>
		</div>
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 02 of 10</div>
	</header>

	<!-- HERO -->
	<div class="module-hero">
		<div class="module-number">02</div>
		<div class="module-tag">Module 02 · Perception + Composition</div>
		<h1 class="module-title">Visual Perception<br /><span>and Composition</span></h1>
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

	<!-- TOC -->
	<nav class="toc">
		<div class="toc-label">Contents</div>
		<ul class="toc-list">
			<li><a href="#objectives">Objectives</a></li>
			<li><a href="#how-eye-moves">How the Eye Moves</a></li>
			<li><a href="#hierarchy-focal">Hierarchy &amp; Focal Points</a></li>
			<li><a href="#thirds-balance">Rule of Thirds &amp; Balance</a></li>
			<li><a href="#contrast-grouping">Contrast, Spacing &amp; Grouping</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<!-- OBJECTIVES -->
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand how the eye moves across a composition and why</li>
			<li>Apply visual hierarchy to control the viewer's reading order</li>
			<li>Use the rule of thirds, balance, and asymmetry as deliberate tools</li>
			<li>Apply contrast, alignment, spacing, and grouping to achieve clarity</li>
		</ul>
	</section>

	<!-- ═══════════════════════════════
       SECTION 1: HOW THE EYE MOVES
  ═══════════════════════════════ -->
	<section id="how-eye-moves" class="section">
		<div class="section-header">
			<span class="section-num">02.01</span>
			<h2 class="section-title">How the Eye Moves Across an Image</h2>
		</div>

		<p>
			The human visual system does not take in an image all at once. It performs rapid, involuntary
			movements called <em>saccades</em> — darting from one point of visual interest to the next in a
			sequence your viewer has no conscious control over. Your job as a designer is to predict and direct
			that sequence.
		</p>

		<p>
			The eye is drawn toward certain visual properties: <strong>high contrast</strong> (a bright
			object on a dark field), <strong>faces</strong> and eyes (a deeply hardwired instinct),
			<strong>large elements</strong>
			before small ones,
			<strong>warm or saturated colors</strong> before cool or muted ones, and
			<strong>text</strong> in a viewer's native language. These are not preferences — they are perceptual
			reflexes, consistent across cultures.
		</p>

		<div class="callout sky">
			<div class="callout-label">What This Means for Design</div>
			Every element you place in a composition competes for one of a limited number of saccade stops.
			The viewer's eye will only settle on five to seven distinct points before forming a first impression.
			Design the path through those points deliberately.
		</div>

		<p>
			When a composition has no hierarchy — when every element has the same weight, the same
			contrast, the same size — the eye has nowhere to start and nowhere logical to go. It wanders,
			finds no path, and the viewer's brain categorizes the design as confusing without being able
			to say why.
		</p>

		<p>
			When a composition is over-hierarchied — when so many elements are trying to be primary that
			the field is chaotic — the same thing happens: the eye doesn't know where to land. Maximum
			contrast everywhere is equivalent to no contrast anywhere.
		</p>

		<!-- DEMO: Eye Path -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Eye Path Simulator</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Each composition is built from the same elements with different hierarchy decisions. Press
					Play to watch the predicted eye path animate through the composition.
				</p>
				<div class="ep-controls">
					<button
						class="btn active"
						id="ep-btn-strong"
						onclick={(e) => actions.setEpMode('strong')}
					>
						Strong Hierarchy
					</button>
					<button class="btn" id="ep-btn-conflict" onclick={(e) => actions.setEpMode('conflict')}>
						Competing Focal Points
					</button>
					<button class="btn" id="ep-btn-flat" onclick={(e) => actions.setEpMode('flat')}
						>No Hierarchy</button
					>
				</div>
				<canvas
					id="ep-canvas"
					width="620"
					height="340"
					aria-label="Ep Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>
				<div style="display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap">
					<button class="btn sky" id="ep-play-btn" onclick={(e) => actions.playEyePath()}
						>▶ Play Path</button
					>
					<button class="btn" onclick={(e) => actions.resetEyePath()}>Reset</button>
				</div>
				<div class="ep-info" id="ep-info">
					Select a hierarchy mode above, then press Play to animate the predicted eye movement path
					through the composition.
				</div>
			</div>
		</div>

		<p>
			Notice that "strong hierarchy" doesn't mean simple. A composition can have many elements while
			still providing a clear reading order. What matters is that no two elements share the same
			visual weight at the same moment in the reading sequence.
		</p>
	</section>

	<!-- ═══════════════════════════════
       SECTION 2: HIERARCHY + FOCAL POINTS
  ═══════════════════════════════ -->
	<section id="hierarchy-focal" class="section">
		<div class="section-header">
			<span class="section-num">02.02</span>
			<h2 class="section-title">Visual Hierarchy and Focal Points</h2>
		</div>

		<p>
			<em>Visual hierarchy</em> is the system of visual relationships that tells the viewer which
			element to look at first, second, and third. It is not about what is most important to the
			<em>designer</em>. It is about what needs to be communicated first to the
			<em>viewer</em> to serve the design's purpose.
		</p>

		<p>
			Hierarchy is expressed through six properties. These can be applied independently or combined,
			and the more of them that distinguish an element from its neighbors, the more dominant it
			becomes:
		</p>

		<table>
			<thead>
				<tr>
					<th>Property</th>
					<th>How to Apply It</th>
					<th>Effect</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Size</td>
					<td>Make the primary element significantly larger</td>
					<td>The eye registers larger objects first, universally</td>
				</tr>
				<tr>
					<td>Value contrast</td>
					<td>White text on dark, or dark on light — extreme contrast</td>
					<td>High contrast pulls attention before color or shape</td>
				</tr>
				<tr>
					<td>Color</td>
					<td>One warm/saturated element in a muted field</td>
					<td>Chromatically distinct elements read as "active"</td>
				</tr>
				<tr>
					<td>Weight</td>
					<td>Bold or heavy type versus light surroundings</td>
					<td>Heavier elements feel closer and more important</td>
				</tr>
				<tr>
					<td>Position</td>
					<td>Upper-left (Western reading cultures) or true center</td>
					<td>Reading order defaults to top-left; center = importance signal</td>
				</tr>
				<tr>
					<td>Isolation</td>
					<td>Surround the primary element with empty space</td>
					<td>Negative space says "stop here"</td>
				</tr>
			</tbody>
		</table>

		<p>
			A <em>focal point</em> is a specific location in the composition where the primary visual hierarchy
			lands — where the eye goes first. In a thumbnail, the focal point is typically the face or the single
			most visually distinct element. In a logo, it is often the most distinctive letterform or the icon.
			In a diagram, it is the concept being explained.
		</p>

		<div class="callout">
			<div class="callout-label">Single Focal Point Rule</div>
			A composition should have exactly one primary focal point. Two elements of equal visual weight create
			what designers call "visual conflict" — the eye oscillates between them and the viewer's brain interprets
			the uncertainty as confusion. This is one of the most common and most damaging beginner mistakes.
		</div>

		<p>
			Achieving a single focal point doesn't mean the composition is boring. A complex composition
			can have one primary focal point, two or three secondary stops, and several tertiary elements
			— all at distinct visual weights. The hierarchy is like a melody: one lead voice, harmonies
			below it, no two voices at the same volume at the same time.
		</p>
	</section>

	<!-- ═══════════════════════════════
       SECTION 3: RULE OF THIRDS + BALANCE
  ═══════════════════════════════ -->
	<section id="thirds-balance" class="section">
		<div class="section-header">
			<span class="section-num">02.03</span>
			<h2 class="section-title">Rule of Thirds, Balance, and Asymmetry</h2>
		</div>

		<p>
			The <em>rule of thirds</em> divides any rectangular composition into a 3×3 grid by drawing two
			equally-spaced horizontal and two vertical lines. The four points where these lines intersect
			are called <em>power points</em> or <em>crash points</em>. Placing your focal element at or
			near one of these intersections produces a composition that feels more dynamic and visually
			stable than placing it dead-center.
		</p>

		<p>
			Dead-center placement is not wrong — it creates a specific feeling of formality, symmetry, and
			authority. Logos are often centered for exactly this reason. But in storytelling compositions
			— thumbnails, posters, editorial images — dead center can feel static, predictable, and
			boring. Off-center placement creates <strong>visual tension</strong>: the subject pulls
			against the frame, and that tension is what holds a viewer's eye.
		</p>

		<div class="callout info">
			<div class="callout-label">Why It Works Perceptually</div>
			The rule of thirds roughly approximates the golden ratio distribution. More practically: off-center
			subjects create implied space — the viewer's eye wants to follow where the subject is "looking"
			or "moving," and that implied direction generates visual energy.
		</div>

		<!-- DEMO: Rule of Thirds -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Rule of Thirds Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Drag the subject (the colored block) anywhere in the frame. The composition strength meter
					responds in real time. Toggle the grid overlay to see the thirds lines and power points.
				</p>
				<div class="rot-controls">
					<button class="btn" id="rot-grid-btn" onclick={(e) => actions.toggleRotGrid()}
						>Show Grid</button
					>
					<button class="btn rose" onclick={(e) => actions.resetRotSubject()}>Center Subject</button
					>
				</div>
				<canvas
					id="rot-canvas"
					width="560"
					height="340"
					aria-label="Rot Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>
				<div class="rot-score-wrap">
					<div
						style="
									display: flex;
									justify-content: space-between;
									font-size: 10px;
									color: var(--muted);
									margin-bottom: 4px;
									letter-spacing: 0.1em;
									text-transform: uppercase;
								"
					>
						<span>Composition Strength</span>
						<span id="rot-score-pct">—</span>
					</div>
					<div class="rot-score-bar-bg">
						<div class="rot-score-bar" id="rot-score-bar" style="width: 0%"></div>
					</div>
					<div class="rot-tip" id="rot-tip">Drag the subject to explore composition strength.</div>
				</div>
			</div>
		</div>

		<p>
			<em>Balance</em> is a related but distinct concept. A composition is visually balanced when the
			implied weights of elements on each side of the composition's center feel roughly equal — not necessarily
			symmetrical, but stable. A large dark shape on the left can be balanced by a smaller but highly
			saturated element on the right. Visual weight includes size, value, color intensity, and even textural
			density.
		</p>

		<p>
			<em>Symmetry</em> divides a composition identically on either side of a central axis. It
			communicates stability, authority, and formality — which is why it appears in institutional
			logos, government seals, and religious iconography.
			<em>Asymmetry</em> creates visual tension and dynamism. Most effective storytelling design is asymmetric
			but balanced — the two sides are not identical, but they feel equally weighted.
		</p>
	</section>

	<!-- ═══════════════════════════════
       SECTION 4: CONTRAST, SPACING, GROUPING
  ═══════════════════════════════ -->
	<section id="contrast-grouping" class="section">
		<div class="section-header">
			<span class="section-num">02.04</span>
			<h2 class="section-title">Contrast, Alignment, Spacing, and Grouping</h2>
		</div>

		<p>
			Four mechanical tools produce most of the structural clarity in professional design: contrast,
			alignment, spacing, and grouping. These are not stylistic choices — they are decisions about
			how visual information is organized. They work below the level of aesthetics.
		</p>

		<p>
			<strong>Contrast</strong> is difference. Size contrast, value contrast, color contrast, shape contrast
			— any property that makes one element distinct from its neighbors. Contrast is how you make something
			matter. The greater the contrast between an element and its surrounding field, the more attention
			it demands. Critically, contrast is relational: an element is only high-contrast relative to what
			surrounds it. There is no absolute "high contrast" — only "more contrast than the neighboring elements."
		</p>

		<!-- DEMO: Contrast Focal Point -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Contrast &amp; Focal Point</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					A field of identical elements. Use the controls to apply contrast properties to a single
					target element and observe how attention snaps to it. Try the "Maximum Contrast" preset to
					see what happens when everything competes.
				</p>
				<div class="two-col" style="align-items: start; gap: 1.5rem">
					<div>
						<canvas
							id="ct-canvas"
							width="300"
							height="260"
							aria-label="Ct Canvas Demonstration"
							role="region"
							tabindex="0"
						></canvas>
					</div>
					<div>
						<div class="ct-controls">
							<div class="slider-row">
								<label for="ct-size">Size</label>
								<input
									type="range"
									id="ct-size"
									min="1"
									max="3"
									step="0.05"
									value="1"
									oninput={() => {
										actions.updateContrast();
									}}
								/>
								<span class="slider-val" id="ct-size-val">1×</span>
							</div>
							<div class="slider-row">
								<label for="ct-bright">Brightness</label>
								<input
									type="range"
									id="ct-bright"
									min="0"
									max="1"
									step="0.02"
									value="0.5"
									oninput={() => {
										actions.updateContrast();
									}}
								/>
								<span class="slider-val" id="ct-bright-val">50%</span>
							</div>
							<div class="slider-row">
								<label for="ct-hue">Hue</label>
								<input
									type="range"
									id="ct-hue"
									min="0"
									max="1"
									step="0.02"
									value="0"
									oninput={() => {
										actions.updateContrast();
									}}
								/>
								<span class="slider-val" id="ct-hue-val">0%</span>
							</div>
							<div class="ct-presets">
								<button class="btn" onclick={(e) => actions.setCtPreset('size')}>Size Only</button>
								<button class="btn" onclick={(e) => actions.setCtPreset('value')}>Value Only</button
								>
								<button class="btn" onclick={(e) => actions.setCtPreset('color')}>Color Only</button
								>
								<button class="btn rose" onclick={(e) => actions.setCtPreset('chaos')}
									>Max Contrast</button
								>
								<button class="btn" onclick={(e) => actions.setCtPreset('reset')}>Reset</button>
							</div>
						</div>
						<div class="ct-note" id="ct-note">
							Adjust a property to see how contrast directs attention.
						</div>
					</div>
				</div>
			</div>
		</div>

		<p>
			<strong>Alignment</strong> is the practice of placing elements along shared invisible axes — a common
			left edge, a shared center line, a consistent grid column. Alignment creates the sense of order
			and intentionality that makes a design feel professional. Misalignment, conversely, creates subtle
			visual noise that viewers cannot identify but respond to as disorder. The rule is simple: if two
			elements are near each other, they should either share an edge exactly or be clearly separated.
			The visual problem happens in the ambiguous middle.
		</p>

		<p>
			<strong>Spacing</strong> — sometimes called white space or negative space — is one of the most misunderstood
			tools in design. Beginners typically try to fill available space, treating emptiness as waste. Empty
			space is not nothing; it is an active ingredient. Generous spacing around an element signals that
			it is important. Tight, crowded spacing suggests hierarchy has collapsed and everything is competing.
			As a rule: when in doubt, give elements more space than you think they need.
		</p>

		<p>
			<strong>Grouping</strong> is a perceptual principle rooted in Gestalt psychology: elements that
			are close together are perceived as belonging together. You use this constantly in design — placing
			a headline close to its subheading, keeping a caption near its image, grouping related navigation
			items. The boundary between groups is created by spacing, not by visual containers. You don't need
			a box or a line to create a group — just enough space between items to make the separation read.
		</p>

		<div class="callout green">
			<div class="callout-label">Gestalt: Proximity</div>
			If you find yourself reaching for boxes, dividers, or background fills to separate content sections,
			ask first whether additional spacing would do the same job. In almost every case it will — and the
			result will be cleaner.
		</div>
	</section>

	<!-- ═══════════════════════════════
       SECTION 5: PRACTICAL WORK
  ═══════════════════════════════ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">02.05</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<!-- DEMO: Cluttered vs Clean -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Exercise · Rebuild a Composition</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					The same poster content in two states: a cluttered, unstructured version and a rebuilt,
					principled version. Toggle between them and read the annotations to identify each
					structural change.
				</p>
				<div class="cc-toggle-wrap">
					<button class="btn rose active" id="cc-btn-bad" onclick={(e) => actions.setCcMode('bad')}>
						Cluttered
					</button>
					<button class="btn sage" id="cc-btn-good" onclick={(e) => actions.setCcMode('good')}
						>Rebuilt</button
					>
				</div>
				<div id="cc-state-label" class="cc-state-label" style="color: var(--rose)">
					Before: Cluttered Layout
				</div>
				<canvas
					id="cc-canvas"
					width="560"
					height="380"
					aria-label="Cc Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>
				<div class="cc-annotation-list" id="cc-annotations"></div>
			</div>
		</div>

		<div class="callout info">
			<div class="callout-label">Exercise 1 — Composition Rebuild</div>
			Take any piece of content you have — a social post, a slide, a document heading — and rebuild it
			using only these four tools: one primary element (contrast), shared edges (alignment), breathing
			room (spacing), and logical proximity (grouping). You are not allowed to change the content, only
			the structural decisions.
		</div>

		<div class="callout green">
			<div class="callout-label">Exercise 2 — Focus Poster</div>
			Create a simple poster (any tool: Canva, Figma, even Keynote) for a real or invented event. Constraint:
			the viewer must be able to identify the event name, date, and location within three seconds — in
			that order. Your hierarchy must force that reading sequence. After you create it, cover up the lower
			two-thirds and see what a viewer gets from the top third alone.
		</div>
	</section>

	<hr class="divider" />

	<!-- ═══════════════════════════════
       QUIZ
  ═══════════════════════════════ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 02 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit · Select the best answer for each.</div>

		<!-- Q1 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> A designer places two headlines in a composition — both bold, both
				the same size, both high contrast against the background. What problem has this created?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The composition is now overdesigned and should be simplified
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. The headlines will be too large for mobile viewing
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Two equally-weighted primary elements create visual conflict — the eye oscillates
					between them without a clear reading order
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The composition is actually stronger because it has more emphasis
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<!-- Q2 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> Why does placing a subject at a rule-of-thirds power point typically
				produce a more dynamic composition than centering it?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Centered compositions always feel unbalanced
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Off-center placement creates visual tension — the subject pulls against the frame,
					generating energy and implied direction
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Power points are mathematically more visible than the center
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The rule of thirds prevents cropping issues on social platforms
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<!-- Q3 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> A design has every element at maximum contrast — large, bright,
				bold, colored. What is the perceptual result?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The design communicates more information faster
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Every element feels equally important, which reinforces the message
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The high contrast makes the design legible at small sizes
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Maximum contrast everywhere is equivalent to no contrast anywhere — there is no focal
					point, and the composition reads as chaotic
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<!-- Q4 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> A designer wants to separate two content groups on a webpage. They
				are considering adding a horizontal dividing line. What should they try first?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Increase the spacing between the groups — proximity alone creates perceived grouping,
					and a line may not be necessary
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Use a different background color for one group
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Add a border box around each group
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Reduce the font size of one group to indicate it is secondary
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<!-- Q5 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> Which of the following most accurately describes what "visual weight"
				means in the context of balance?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The physical file size of an image element
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. The number of pixels an element occupies on screen
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The perceived heaviness of an element based on its size, value, color, and isolation
					relative to surrounding elements
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The amount of visual information (detail) contained in an element
				</button>
			</div>
			<div class="feedback" id="fb-4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-num">—</div>
			<div class="score-label">questions correct out of 5</div>
		</div>
	</section>

	<!-- ═══════════════════════════════
       ASSESSMENT
  ═══════════════════════════════ -->
	<section id="assessment" class="assessment-section">
		<div class="assessment-header">Module Assessment — Diagnose a Failing Hierarchy</div>
		<div class="assessment-sub">
			Given a broken composition, identify which principle is failing and why.
		</div>

		<p style="font-size: 13px; margin-bottom: 1rem">
			The composition below was designed for a YouTube channel announcement. The creator wants
			viewers to read: channel name first, then the launch date, then the topic description. Examine
			the layout and identify what is structurally preventing that reading order.
		</p>

		<div class="debug-question">
			<div class="debug-q-header">Diagnosis Exercise · Composition Analysis</div>
			<div class="debug-body">
				<p style="font-size: 12px; color: var(--muted)">
					The intended reading order is: Channel Name → Launch Date → Topic Description. Identify
					the primary structural problem.
				</p>
				<div class="debug-canvas-wrap">
					<canvas
						id="diag-canvas"
						width="560"
						height="300"
						aria-label="Diag Canvas Demonstration"
						role="region"
						tabindex="0"
					></canvas>
				</div>
			</div>
			<div class="debug-options">
				<div
					class="debug-option"
					onclick={(e) => actions.handleDiag(e.currentTarget, 0)}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.handleDiag(e.currentTarget, 0);
						}
					}}
				>
					A. The color palette is too limited — more colors would create better hierarchy
				</div>
				<div
					class="debug-option"
					onclick={(e) => actions.handleDiag(e.currentTarget, 1)}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.handleDiag(e.currentTarget, 1);
						}
					}}
				>
					B. The Launch Date and Topic Description have nearly identical visual weight, so the eye
					cannot determine which to read second — the intended sequence fails at step two
				</div>
				<div
					class="debug-option"
					onclick={(e) => actions.handleDiag(e.currentTarget, 2)}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.handleDiag(e.currentTarget, 2);
						}
					}}
				>
					C. The Channel Name is too large and crowds out the other elements
				</div>
				<div
					class="debug-option"
					onclick={(e) => actions.handleDiag(e.currentTarget, 3)}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.handleDiag(e.currentTarget, 3);
						}
					}}
				>
					D. There are too few elements — more content would fill the composition and fix the
					hierarchy
				</div>
			</div>
			<div
				class="debug-feedback"
				id="diag-feedback"
				style="color: var(--muted); font-size: 12px"
			></div>
		</div>
	</section>

	<!-- NAV -->
	<div class="nav-links">
		<a href="gd-module-01.html" class="prev-link">← Module 01: What Design Is</a>
		<a href="gd-module-03.html" class="next-module" style="flex: 1; max-width: 420px">
			<div>
				<div class="next-label">Next — Module 03</div>
				<div class="next-title">Typography Essentials</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</div>
</div>

<!-- .page-wrapper -->

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

	/* HEADER */
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

	/* HERO */
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
		max-width: 600px;
	}
	.module-title span {
		color: var(--violet);
	}

	/* TOC */
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

	/* OBJECTIVES */
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

	/* SECTIONS */
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
		color: var(--sky);
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

	/* CALLOUTS */
	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
		font-size: 13px;
	}
	:global(.callout.green) {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--surface));
	}
	.callout.info {
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
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
	:global(.callout.green) .callout-label {
		color: var(--sage);
	}
	.callout.info .callout-label {
		color: var(--amber);
	}
	:global(.callout.warn) .callout-label {
		color: var(--rose);
	}
	:global(.callout.sky) .callout-label {
		color: var(--sky);
	}

	/* DEMO BOXES */
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
	:global(.demo-badge.animated) {
		color: var(--amber);
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	/* CONTROLS */
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
		margin: 0.6rem 0;
	}
	:global(.slider-row) label {
		font-size: 12px;
		min-width: 90px;
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
		min-width: 36px;
		text-align: right;
		font-weight: 600;
	}

	/* LAYOUT HELPERS */
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

	/* TABLE */
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

	/* QUIZ */
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

	/* ASSESSMENT */
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
		margin-bottom: 2rem;
	}

	/* PROGRESS */
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

	/* DIVIDER */
	.divider {
		border: none;
		border-top: 1px solid var(--border);
		margin: 3rem 0;
	}

	/* NAV LINKS */
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
     DEMO-SPECIFIC
  ═══════════════════════════════════ */

	/* Eye Path Demo */
	#ep-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
		background: #0a0f18;
	}
	.ep-controls {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	.ep-info {
		margin-top: 1rem;
		font-size: 12px;
		line-height: 1.7;
		padding: 0.75rem 1rem;
		border: 1px solid var(--border);
		background: var(--code-bg);
		min-height: 60px;
		color: var(--text);
	}
	:global(.ep-info strong) {
		color: var(--violet);
	}

	/* Rule of Thirds */
	#rot-canvas {
		display: block;
		max-width: 100%;
		cursor: grab;
		border: 1px solid var(--border2);
	}
	#rot-canvas:active {
		cursor: grabbing;
	}
	.rot-controls {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1rem;
		align-items: center;
	}
	.rot-score-wrap {
		margin-top: 1rem;
	}
	.rot-score-bar-bg {
		height: 4px;
		background: var(--border2);
		position: relative;
	}
	.rot-score-bar {
		height: 100%;
		background: var(--violet);
		transition: width 0.3s;
	}
	:global(.rot-score-label) {
		font-size: 11px;
		color: var(--muted);
		margin-top: 0.4rem;
	}
	:global(.rot-score-label) span {
		color: var(--violet);
		font-weight: 600;
	}
	.rot-tip {
		font-size: 11px;
		color: var(--muted);
		margin-top: 0.5rem;
		min-height: 1.4em;
		transition: color 0.2s;
	}

	/* Contrast Demo */
	#ct-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
	}
	.ct-controls {
		margin-top: 1rem;
	}
	.ct-presets {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-top: 0.75rem;
	}
	.ct-note {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.75rem;
		min-height: 1.8em;
		transition: color 0.2s;
	}

	/* Cluttered/Clean Demo */
	.cc-toggle-wrap {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1rem;
		align-items: center;
	}
	#cc-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
	}
	.cc-annotation-list {
		margin-top: 1rem;
		font-size: 11px;
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		min-height: 80px;
	}
	:global(.cc-item) {
		padding: 3px 8px;
		border-left: 2px solid;
		line-height: 1.5;
	}
	:global(.cc-item.bad) {
		border-color: var(--rose);
		color: var(--rose);
		background: color-mix(in srgb, var(--rose) 6%, transparent);
	}
	:global(.cc-item.good) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 6%, transparent);
	}
	.cc-state-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		margin-bottom: 0.4rem;
	}

	/* Assessment */
	.debug-question {
		margin: 2rem 0;
		border: 1px solid var(--border);
	}
	.debug-q-header {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--border);
		background: var(--raised);
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.debug-body {
		padding: 1rem 1.25rem;
		font-size: 13px;
	}
	.debug-canvas-wrap {
		margin: 1rem 0;
	}
	#diag-canvas {
		display: block;
		max-width: 100%;
		border: 1px solid var(--border2);
	}
	.debug-options {
		padding: 0 1.25rem 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	:global(.debug-option) {
		padding: 0.6rem 1rem;
		border: 1px solid var(--border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		font-family: 'IBM Plex Mono', monospace;
		user-select: none;
	}
	:global(.debug-option:hover) {
		border-color: var(--border2);
		background: var(--raised);
	}
	:global(.debug-option.correct) {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
		color: var(--sage);
	}
	:global(.debug-option.wrong) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
		color: var(--rose);
	}
	:global(.debug-option.disabled) {
		pointer-events: none;
	}
	.debug-feedback {
		padding: 0.75rem 1.25rem;
		font-size: 12px;
		border-top: 1px solid var(--border);
		min-height: 2em;
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
