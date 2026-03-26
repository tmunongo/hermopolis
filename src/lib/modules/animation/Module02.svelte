<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-unused-expressions */
	import { onMount } from 'svelte';

	onMount(() => {
		/* ══════════════════════════════════════════
   HERO DECO — spacing dots
══════════════════════════════════════════ */
		(function () {
			const el = document.getElementById('heroDeco');
			const cols = 7,
				rows = 5;
			for (let c = 0; c < cols; c++) {
				const col = document.createElement('div');
				col.className = 'hero-deco-col';
				for (let r = 0; r < rows; r++) {
					const d = document.createElement('div');
					d.className = 'hero-dot';
					// Spacing increases left to right — simulate easing spacing
					const gap = 4 + c * c * 0.8;
					d.style.marginBottom = gap + 'px';
					col.appendChild(d);
				}
				col.style.marginRight = 4 + c * 2 + 'px';
				el.appendChild(col);
			}
		})();

		/* ══════════════════════════════════════════
   SHARED UTILS
══════════════════════════════════════════ */
		const C = {
			gold: '#f0a830',
			coral: '#e8553a',
			mint: '#4ecbb4',
			lavender: '#c4a8f0',
			muted: '#7a6e5e',
			border: '#28221a',
			border2: '#3c342a',
			raised: '#1c1812',
			surface: '#131009',
			bg: '#0b0906',
			dim: '#4a4035'
		};

		function lerp(a, b, t) {
			return a + (b - a) * t;
		}
		function easeInOut(t) {
			return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
		}
		function easeIn(t) {
			return t * t * t;
		}
		function easeOut(t) {
			return 1 - Math.pow(1 - t, 3);
		}
		function linear(t) {
			return t;
		}

		// Cubic bezier evaluator (for curve editor)
		function cubicBezier(t, p1x, p1y, p2x, p2y) {
			// Approximate using De Casteljau (4-point: 0,0  p1  p2  1,1)
			const cx = 3 * p1x,
				bx = 3 * (p2x - p1x) - cx,
				ax = 1 - cx - bx;
			const cy = 3 * p1y,
				by = 3 * (p2y - p1y) - cy,
				ay = 1 - cy - by;
			// solve for t given x≈t (Newton)
			let u = t;
			for (let i = 0; i < 6; i++) {
				const x = ((ax * u + bx) * u + cx) * u - t;
				const dx = (3 * ax * u + 2 * bx) * u + cx;
				if (Math.abs(dx) < 1e-6) break;
				u -= x / dx;
			}
			return ((ay * u + by) * u + cy) * u;
		}

		// Easing presets defined as bezier handles [p1x,p1y,p2x,p2y]
		const PRESETS = {
			linear: [0.0, 0.0, 1.0, 1.0],
			ease: [0.25, 0.1, 0.25, 1.0],
			easeIn: [0.42, 0.0, 1.0, 1.0],
			easeOut: [0.0, 0.0, 0.58, 1.0],
			overshoot: [0.34, 1.56, 0.64, 1.0],
			anticipate: [0.36, -0.4, 0.7, 0.5]
		};

		const READOUTS = {
			linear: 'Constant speed. Mechanical. Use for data-driven or robotic motion.',
			ease: 'Slow start → fast middle → slow end. The universal default for natural motion.',
			easeIn: 'Slow start → rushes off. Good for launches, exits, impacts.',
			easeOut: 'Fast arrival → settles gently. Good for landings, entrances.',
			overshoot: 'Passes target → snaps back. Adds elasticity and energy. Use for lively UI.',
			anticipate: 'Dips back before moving forward. Classic anticipation — charges the action.'
		};

		/* ══════════════════════════════════════════
   DEMO 2.1 — CURVE EDITOR
══════════════════════════════════════════ */
		const CE = document.getElementById('curveCanvas');
		const cectx = CE.getContext('2d');
		const W = CE.width,
			H = CE.height;
		const PAD = 28;
		const cW = W - PAD * 2,
			cH = H - PAD * 2;

		// Control points in [0..1] space
		let handles = { p1x: 0.25, p1y: 0.1, p2x: 0.25, p2y: 1.0 };
		let activeHandle = null;

		function toCanvas(nx, ny) {
			return { x: PAD + nx * cW, y: PAD + (1 - ny) * cH };
		}
		function fromCanvas(cx, cy) {
			return { nx: (cx - PAD) / cW, ny: 1 - (cy - PAD) / cH };
		}

		function clamp01(v) {
			return Math.max(0, Math.min(1, v));
		}

		function drawCurveEditor() {
			cectx.clearRect(0, 0, W, H);

			// Grid
			cectx.strokeStyle = C.border;
			cectx.lineWidth = 1;
			for (let i = 0; i <= 4; i++) {
				const x = PAD + i * (cW / 4),
					y = PAD + i * (cH / 4);
				cectx.beginPath();
				cectx.moveTo(x, PAD);
				cectx.lineTo(x, PAD + cH);
				cectx.stroke();
				cectx.beginPath();
				cectx.moveTo(PAD, y);
				cectx.lineTo(PAD + cW, y);
				cectx.stroke();
			}

			// Axes labels
			cectx.fillStyle = C.dim;
			cectx.font = `9px 'JetBrains Mono'`;
			cectx.textAlign = 'center';
			cectx.fillText('TIME →', W / 2, H - 4);
			cectx.save();
			cectx.translate(10, H / 2);
			cectx.rotate(-Math.PI / 2);
			cectx.fillText('VALUE ↑', 0, 0);
			cectx.restore();

			// Bezier curve
			const p0 = toCanvas(0, 0),
				p3 = toCanvas(1, 1);
			const p1 = toCanvas(handles.p1x, handles.p1y);
			const p2 = toCanvas(handles.p2x, handles.p2y);

			cectx.strokeStyle = C.coral;
			cectx.lineWidth = 2;
			cectx.beginPath();
			cectx.moveTo(p0.x, p0.y);
			cectx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y);
			cectx.stroke();

			// Handle lines
			cectx.strokeStyle = C.border2;
			cectx.lineWidth = 1;
			cectx.setLineDash([3, 3]);
			cectx.beginPath();
			cectx.moveTo(p0.x, p0.y);
			cectx.lineTo(p1.x, p1.y);
			cectx.stroke();
			cectx.beginPath();
			cectx.moveTo(p3.x, p3.y);
			cectx.lineTo(p2.x, p2.y);
			cectx.stroke();
			cectx.setLineDash([]);

			// Handle dots
			[
				[p1, 'p1', C.coral],
				[p2, 'p2', C.gold]
			].forEach(([p, id, col]) => {
				cectx.fillStyle = col;
				cectx.beginPath();
				cectx.arc(p.x, p.y, 6, 0, Math.PI * 2);
				cectx.fill();
				cectx.strokeStyle = C.bg;
				cectx.lineWidth = 1.5;
				cectx.stroke();
			});

			// End anchors
			[p0, p3].forEach((p) => {
				cectx.fillStyle = C.muted;
				cectx.beginPath();
				cectx.arc(p.x, p.y, 4, 0, Math.PI * 2);
				cectx.fill();
			});
		}

		function evalCurve(t) {
			return cubicBezier(t, handles.p1x, handles.p1y, handles.p2x, handles.p2y);
		}

		// Mouse / touch interaction
		function getPos(e) {
			const r = CE.getBoundingClientRect();
			const sc = CE.width / r.width;
			const raw = e.touches ? e.touches[0] : e;
			return { x: (raw.clientX - r.left) * sc, y: (raw.clientY - r.top) * sc };
		}
		function hitTest(pos) {
			const p1 = toCanvas(handles.p1x, handles.p1y);
			const p2 = toCanvas(handles.p2x, handles.p2y);
			if (Math.hypot(pos.x - p1.x, pos.y - p1.y) < 12) return 'p1';
			if (Math.hypot(pos.x - p2.x, pos.y - p2.y) < 12) return 'p2';
			return null;
		}
		CE.addEventListener('mousedown', (e) => {
			const pos = getPos(e);
			activeHandle = hitTest(pos);
		});
		CE.addEventListener(
			'touchstart',
			(e) => {
				e.preventDefault();
				const pos = getPos(e);
				activeHandle = hitTest(pos);
			},
			{ passive: false }
		);
		function moveHandle(e) {
			if (!activeHandle) return;
			const pos = getPos(e);
			const n = fromCanvas(pos.x, pos.y);
			if (activeHandle === 'p1') {
				handles.p1x = clamp01(n.nx);
				handles.p1y = n.ny;
			} else {
				handles.p2x = clamp01(n.nx);
				handles.p2y = n.ny;
			}
			drawCurveEditor();
			drawSpacingChart();
			updateReadout();
			// deselect presets
			document.querySelectorAll('.preset-btn').forEach((b) => b.classList.remove('active'));
		}
		CE.addEventListener('mousemove', moveHandle);
		CE.addEventListener(
			'touchmove',
			(e) => {
				e.preventDefault();
				moveHandle(e);
			},
			{ passive: false }
		);
		['mouseup', 'mouseleave', 'touchend'].forEach((ev) =>
			CE.addEventListener(ev, () => {
				activeHandle = null;
			})
		);

		function updateReadout() {
			// compute description based on curve shape
			const mid = evalCurve(0.5);
			let desc;
			if (mid < 0.3) desc = 'Heavy ease-in: starts very slowly.';
			else if (mid < 0.45) desc = 'Ease-in dominant: accelerating feel.';
			else if (mid < 0.55) desc = 'Near-linear: roughly constant speed.';
			else if (mid < 0.7) desc = 'Ease-out dominant: decelerating feel.';
			else desc = 'Heavy ease-out: arrives quickly then settles.';
			const h = handles;
			if (h.p1y > 1.1 || h.p2y > 1.1)
				desc = 'Overshoot: value exceeds target then snaps back. Elastic feel.';
			if (h.p1y < -0.1) desc = 'Anticipation: dips back before the main move. Charges the action.';
			document.getElementById('curveReadout').textContent = desc;
		}

		// Spacing chart (shows frame positions)
		const SC_C = document.getElementById('spacingChartCanvas');
		const SC_ctx = SC_C.getContext('2d');
		function drawSpacingChart() {
			const w = SC_C.width,
				h = SC_C.height;
			SC_ctx.clearRect(0, 0, w, h);
			SC_ctx.strokeStyle = C.border2;
			SC_ctx.lineWidth = 1;
			SC_ctx.beginPath();
			SC_ctx.moveTo(12, h / 2);
			SC_ctx.lineTo(w - 12, h / 2);
			SC_ctx.stroke();

			const STEPS = 16;
			const trackW = w - 24;
			for (let i = 0; i <= STEPS; i++) {
				const t = i / STEPS;
				const val = evalCurve(t);
				const x = 12 + val * trackW;
				SC_ctx.fillStyle = C.coral;
				SC_ctx.globalAlpha = 0.85;
				SC_ctx.beginPath();
				SC_ctx.arc(x, h / 2, 3, 0, Math.PI * 2);
				SC_ctx.fill();
			}
			SC_ctx.globalAlpha = 1;
		}

		// Curve preview (small moving ball)
		const CP_C = document.getElementById('curvePreviewCanvas');
		const CP_ctx = CP_C.getContext('2d');
		let curveAnimT = 0,
			curveAnimPlaying = false,
			curveRafId = null,
			curveLastTs = null;

		function drawCurvePreview(t) {
			const w = CP_C.width,
				h = CP_C.height;
			CP_ctx.clearRect(0, 0, w, h);
			// Track
			const pad = 16,
				trackW = w - pad * 2,
				cy = h / 2;
			CP_ctx.strokeStyle = C.border2;
			CP_ctx.lineWidth = 1;
			CP_ctx.setLineDash([3, 3]);
			CP_ctx.beginPath();
			CP_ctx.moveTo(pad, cy);
			CP_ctx.lineTo(w - pad, cy);
			CP_ctx.stroke();
			CP_ctx.setLineDash([]);
			// Trail dots
			for (let i = 0; i < Math.floor(t * 20); i++) {
				const ti = i / 20;
				const xi = pad + evalCurve(ti) * trackW;
				CP_ctx.globalAlpha = 0.15 + (i / 20) * 0.25;
				CP_ctx.fillStyle = C.gold;
				CP_ctx.beginPath();
				CP_ctx.arc(xi, cy, 2.5, 0, Math.PI * 2);
				CP_ctx.fill();
			}
			CP_ctx.globalAlpha = 1;
			// Ball
			const val = evalCurve(t);
			const bx = pad + val * trackW;
			const grd = CP_ctx.createRadialGradient(bx - 3, cy - 3, 1, bx, cy, 12);
			grd.addColorStop(0, '#ffc85a');
			grd.addColorStop(1, '#b07010');
			CP_ctx.fillStyle = grd;
			CP_ctx.beginPath();
			CP_ctx.arc(bx, cy, 12, 0, Math.PI * 2);
			CP_ctx.fill();
		}

		function curveTick(ts) {
			if (curveLastTs === null) curveLastTs = ts;
			const dt = (ts - curveLastTs) / 1000;
			curveLastTs = ts;
			curveAnimT = Math.min(1, curveAnimT + dt * 0.6);
			drawCurvePreview(curveAnimT);
			if (curveAnimT < 1) curveRafId = requestAnimationFrame(curveTick);
			else {
				curveAnimPlaying = false;
				document.getElementById('curvePlayBtn').textContent = '▶ Animate';
				document.getElementById('curvePlayBtn').classList.remove('active');
				curveLastTs = null;
			}
		}

		document.getElementById('curvePlayBtn').onclick = function () {
			if (!curveAnimPlaying) {
				if (curveAnimT >= 1) curveAnimT = 0;
				curveAnimPlaying = true;
				this.textContent = '⏸ Playing…';
				this.classList.add('active');
				curveRafId = requestAnimationFrame(curveTick);
			}
		};
		document.getElementById('curveResetBtn').onclick = function () {
			cancelAnimationFrame(curveRafId);
			curveAnimPlaying = false;
			curveAnimT = 0;
			curveLastTs = null;
			document.getElementById('curvePlayBtn').textContent = '▶ Animate';
			document.getElementById('curvePlayBtn').classList.remove('active');
			drawCurvePreview(0);
		};

		function applyPreset(name) {
			const p = PRESETS[name];
			handles = { p1x: p[0], p1y: p[1], p2x: p[2], p2y: p[3] };
			document
				.querySelectorAll('.preset-btn')
				.forEach((b) => b.classList.toggle('active', b.dataset.preset === name));
			document.getElementById('curveReadout').textContent = READOUTS[name];
			drawCurveEditor();
			drawSpacingChart();
			drawCurvePreview(curveAnimT);
		}

		applyPreset('ease');
		drawCurvePreview(0);

		/* ══════════════════════════════════════════
   DEMO 2.2 — ARC vs STRAIGHT
══════════════════════════════════════════ */
		const ARC = document.getElementById('arcCanvas');
		const actx = ARC.getContext('2d');
		const AW = ARC.width,
			AH = ARC.height;
		let arcMode = 'both',
			arcT = 0,
			arcPlaying = false,
			arcRafId = null,
			arcLastTs = null,
			arcShowPath = true;

		document.getElementById('arcShowPath').onchange = function () {
			arcShowPath = this.checked;
			renderArc();
		};

		function setArcMode(m) {
			arcMode = m;
			document
				.querySelectorAll('.arc-tab')
				.forEach((t) =>
					t.classList.toggle(
						'active',
						t.textContent.toLowerCase().replace(' only', '') === m ||
							(t.textContent.toLowerCase() === 'both' && m === 'both')
					)
				);
			renderArc();
		}
		// fix tab click
		document.querySelectorAll('.arc-tab').forEach((t) => {
			t.onclick = function () {
				const txt = this.textContent;
				if (txt === 'Both') setArcMode('both');
				else if (txt === 'Straight Only') setArcMode('straight');
				else setArcMode('arc');
			};
		});

		const ARC_STARTX = 50,
			ARC_ENDX = AW - 50,
			ARC_Y = AH * 0.72;
		const ARC_PEAKY = AH * 0.15;

		function arcPos(t) {
			// Eased arc path (parabolic)
			const et = easeInOut(t);
			const x = lerp(ARC_STARTX, ARC_ENDX, et);
			const y = ARC_Y + (ARC_PEAKY - ARC_Y) * Math.sin(t * Math.PI); // parabola
			return { x, y };
		}
		function straightPos(t) {
			// Linear straight line
			const x = lerp(ARC_STARTX, ARC_ENDX, t);
			const y = ARC_Y;
			return { x, y };
		}

		function renderArc() {
			actx.clearRect(0, 0, AW, AH);

			const DOTS = 18;

			if (arcShowPath) {
				// Arc path trace
				if (arcMode !== 'straight') {
					actx.strokeStyle = C.gold + '44';
					actx.lineWidth = 1.5;
					actx.setLineDash([3, 4]);
					actx.beginPath();
					for (let i = 0; i <= 60; i++) {
						const p = arcPos(i / 60);
						i === 0 ? actx.moveTo(p.x, p.y) : actx.lineTo(p.x, p.y);
					}
					actx.stroke();
					actx.setLineDash([]);
				}
				// Straight path trace
				if (arcMode !== 'arc') {
					actx.strokeStyle = C.coral + '44';
					actx.lineWidth = 1.5;
					actx.setLineDash([3, 4]);
					actx.beginPath();
					actx.moveTo(ARC_STARTX, ARC_Y);
					actx.lineTo(ARC_ENDX, ARC_Y);
					actx.stroke();
					actx.setLineDash([]);
				}

				// Frame spacing dots
				for (let i = 0; i <= DOTS; i++) {
					const t = i / DOTS;
					if (arcMode !== 'straight') {
						const p = arcPos(t);
						actx.globalAlpha = 0.45;
						actx.fillStyle = C.gold;
						actx.beginPath();
						actx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
						actx.fill();
					}
					if (arcMode !== 'arc') {
						const p = straightPos(t);
						actx.globalAlpha = 0.45;
						actx.fillStyle = C.coral;
						actx.beginPath();
						actx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
						actx.fill();
					}
				}
				actx.globalAlpha = 1;
			}

			// Labels
			actx.fillStyle = C.muted;
			actx.font = `10px 'JetBrains Mono'`;
			actx.textAlign = 'center';
			if (arcMode !== 'straight')
				((actx.fillStyle = C.gold + '99'), actx.fillText('Arc path', AW / 2, ARC_PEAKY + 14));
			if (arcMode !== 'arc') {
				actx.fillStyle = C.coral + '99';
				actx.fillText('Straight path', AW / 2, ARC_Y - 18);
			}

			// Balls
			function drawBall(x, y, col, r = 13) {
				const grd = actx.createRadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r);
				grd.addColorStop(0, '#fff');
				grd.addColorStop(0.3, col);
				grd.addColorStop(1, '#000');
				actx.fillStyle = grd;
				actx.beginPath();
				actx.arc(x, y, r, 0, Math.PI * 2);
				actx.fill();
				actx.strokeStyle = 'rgba(255,255,255,0.1)';
				actx.lineWidth = 1;
				actx.stroke();
			}

			const t = arcT;
			if (arcMode !== 'straight') {
				const p = arcPos(t);
				drawBall(p.x, p.y, C.gold);
			}
			if (arcMode !== 'arc') {
				const p = straightPos(t);
				drawBall(p.x, p.y, C.coral);
			}
		}

		function arcTick(ts) {
			if (arcLastTs === null) arcLastTs = ts;
			const dt = (ts - arcLastTs) / 1000;
			arcLastTs = ts;
			arcT = Math.min(1, arcT + dt * 0.55);
			renderArc();
			if (arcT < 1) arcRafId = requestAnimationFrame(arcTick);
			else {
				arcPlaying = false;
				document.getElementById('arcPlayBtn').textContent = '▶ Animate';
				document.getElementById('arcPlayBtn').classList.remove('active');
				arcLastTs = null;
			}
		}

		document.getElementById('arcPlayBtn').onclick = function () {
			if (!arcPlaying) {
				if (arcT >= 1) arcT = 0;
				arcPlaying = true;
				this.textContent = '⏸ Playing…';
				this.classList.add('active');
				arcRafId = requestAnimationFrame(arcTick);
			}
		};
		document.getElementById('arcResetBtn').onclick = function () {
			cancelAnimationFrame(arcRafId);
			arcPlaying = false;
			arcT = 0;
			arcLastTs = null;
			document.getElementById('arcPlayBtn').textContent = '▶ Animate';
			document.getElementById('arcPlayBtn').classList.remove('active');
			renderArc();
		};
		renderArc();

		/* ══════════════════════════════════════════
   DEMO 2.3 — WEIGHT SIMULATION
══════════════════════════════════════════ */
		const WC = document.getElementById('weightCanvas');
		const wctx = WC.getContext('2d');
		const WW = WC.width,
			WH = WC.height;
		const GROUND_Y = WH - 30;

		let weightSimRunning = false,
			weightSimT = 0,
			weightRafId = null,
			weightLastTs = null;
		let weightShowDots = true;

		// Physics simulation — baked frame positions
		function simulateBounce(elasticity, gravity, frames) {
			const dt = 1 / 24; // 24fps
			const startY = 30;
			let y = startY,
				vy = 0;
			const positions = [];
			for (let i = 0; i < frames; i++) {
				vy += gravity * dt;
				y += vy * dt;
				if (y >= GROUND_Y - 14) {
					y = GROUND_Y - 14;
					vy = -Math.abs(vy) * elasticity;
					// squash amount
				}
				positions.push({ y, vy });
			}
			return positions;
		}

		function getSimParams() {
			return {
				elastA: parseFloat(document.getElementById('elastA').value),
				elastB: parseFloat(document.getElementById('elastB').value),
				grav: parseFloat(document.getElementById('gravSlider').value)
			};
		}

		let cachedSim = null;
		function rebuildSim() {
			const p = getSimParams();
			const frames = 90;
			cachedSim = {
				A: simulateBounce(p.elastA, p.grav, frames),
				B: simulateBounce(p.elastB, p.grav, frames),
				frames
			};
		}

		function renderWeight(frameIdx) {
			wctx.clearRect(0, 0, WW, WH);
			if (!cachedSim) return;

			const frames = cachedSim.frames;
			const fi = Math.min(frameIdx, frames - 1);

			// Ground
			wctx.strokeStyle = C.border2;
			wctx.lineWidth = 1;
			wctx.beginPath();
			wctx.moveTo(20, GROUND_Y);
			wctx.lineTo(WW - 20, GROUND_Y);
			wctx.stroke();

			// Positions: A on left third, B on right third
			const xA = WW * 0.3,
				xB = WW * 0.7;

			function drawWeightBall(x, frames_arr, fi, col, label) {
				// Spacing dots
				if (weightShowDots) {
					for (let i = 0; i < frames_arr.length; i += 2) {
						const alpha = Math.max(0, 1 - Math.abs(i - fi) / 12) * 0.4;
						wctx.globalAlpha = alpha;
						wctx.fillStyle = col;
						wctx.beginPath();
						wctx.arc(x, frames_arr[i].y, 2, 0, Math.PI * 2);
						wctx.fill();
					}
					wctx.globalAlpha = 1;
				}

				const frame = frames_arr[fi];
				const y = frame.y;
				const speed = Math.abs(frame.vy);

				// Squash/stretch based on velocity at impact
				const impactSpeed = Math.min(speed / 400, 1);
				const atGround = y >= GROUND_Y - 16;
				const rx = atGround ? 13 + impactSpeed * 10 : 13;
				const ry = atGround ? 13 - impactSpeed * 6 : 13 + Math.min(speed / 200, 6);

				// Shadow
				const dist = GROUND_Y - y;
				const shAlpha = Math.max(0, 1 - dist / 300) * 0.3;
				wctx.fillStyle = `rgba(0,0,0,${shAlpha})`;
				wctx.beginPath();
				wctx.ellipse(x, GROUND_Y, rx * 0.9, 4, 0, 0, Math.PI * 2);
				wctx.fill();

				// Ball
				const grd = wctx.createRadialGradient(
					x - rx * 0.3,
					y - ry * 0.3,
					1,
					x,
					y,
					Math.max(rx, ry)
				);
				grd.addColorStop(0, '#fff');
				grd.addColorStop(0.3, col);
				grd.addColorStop(1, '#000');
				wctx.fillStyle = grd;
				wctx.beginPath();
				wctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
				wctx.fill();

				// Label
				wctx.fillStyle = col;
				wctx.font = `500 11px 'JetBrains Mono'`;
				wctx.textAlign = 'center';
				wctx.fillText(label, x, GROUND_Y + 18);
			}

			drawWeightBall(xA, cachedSim.A, fi, C.gold, 'A — Heavy');
			drawWeightBall(xB, cachedSim.B, fi, C.coral, 'B — Bouncy');
		}

		function weightTick(ts) {
			if (weightLastTs === null) weightLastTs = ts;
			const dt = (ts - weightLastTs) / 1000;
			weightLastTs = ts;
			weightSimT = Math.min(cachedSim.frames - 1, weightSimT + dt * 24); // 24fps playback
			renderWeight(Math.floor(weightSimT));
			if (weightSimT < cachedSim.frames - 1) weightRafId = requestAnimationFrame(weightTick);
			else {
				weightSimRunning = false;
				document.getElementById('weightPlayBtn').textContent = '▶ Drop';
				document.getElementById('weightPlayBtn').classList.remove('active');
				weightLastTs = null;
			}
		}

		['elastA', 'elastB', 'gravSlider'].forEach((id) => {
			document.getElementById(id).oninput = function () {
				document.getElementById(id + 'Val').textContent = parseFloat(this.value).toFixed(
					id.startsWith('elast') ? 2 : 0
				);
				rebuildSim();
				renderWeight(Math.floor(weightSimT));
			};
		});
		document.getElementById('weightShowDots').onchange = function () {
			weightShowDots = this.checked;
			renderWeight(Math.floor(weightSimT));
		};

		document.getElementById('weightPlayBtn').onclick = function () {
			if (!weightSimRunning) {
				weightSimT = 0;
				rebuildSim();
				weightSimRunning = true;
				this.textContent = '▶ Dropping…';
				this.classList.add('active');
				weightLastTs = null;
				weightRafId = requestAnimationFrame(weightTick);
			}
		};
		document.getElementById('weightResetBtn').onclick = function () {
			cancelAnimationFrame(weightRafId);
			weightSimRunning = false;
			weightSimT = 0;
			weightLastTs = null;
			rebuildSim();
			renderWeight(0);
			document.getElementById('weightPlayBtn').textContent = '▶ Drop';
			document.getElementById('weightPlayBtn').classList.remove('active');
		};

		rebuildSim();
		renderWeight(0);

		/* ══════════════════════════════════════════
   DEMO 2.4 — SPACING CHART BUILDER
══════════════════════════════════════════ */
		const PROFILES = [
			{
				id: 'ease',
				label: 'Ease (Slow-In/Out)',
				fn: easeInOut,
				desc: 'Frames cluster at start and end. Used for almost all natural motion: a ball that accelerates, then decelerates.'
			},
			{
				id: 'easeIn',
				label: 'Ease-In only',
				fn: easeIn,
				desc: 'Frames tight at start, spread at end. Object accelerates away. Good for exits, launches.'
			},
			{
				id: 'easeOut',
				label: 'Ease-Out only',
				fn: easeOut,
				desc: 'Frames spread at start, tight at end. Object decelerates to a stop. Good for entrances, landings.'
			},
			{
				id: 'linear',
				label: 'Linear (even)',
				fn: linear,
				desc: 'Frames perfectly even. Mechanical, robotic. Use sparingly — data-driven or machine motion only.'
			},
			{
				id: 'snap',
				label: 'Quick Snap',
				fn: (t) => easeOut(Math.min(t * 3, 1)),
				desc: 'Snaps quickly to destination and holds. Good for fast UI events, punchy feedback.'
			},
			{
				id: 'delayed',
				label: 'Delayed Start',
				fn: (t) => easeOut(Math.max(0, t - 0.4) / 0.6),
				desc: 'Holds at start, then moves quickly. Creates a "held breath" before action.'
			}
		];

		let activeProfile = 'ease';
		const SCC = document.getElementById('scChartCanvas');
		const scctx = SCC.getContext('2d');
		const SCPREV = document.getElementById('scPreviewCanvas');
		const scPrevCtx = SCPREV.getContext('2d');
		let scAnimT = 0,
			scPlaying = false,
			scRafId = null,
			scLastTs = null;

		function buildProfileList() {
			const list = document.getElementById('profileList');
			list.innerHTML = '';
			PROFILES.forEach((p) => {
				const btn = document.createElement('button');
				btn.className = 'preset-btn' + (p.id === activeProfile ? ' active' : '');
				btn.dataset.pid = p.id;
				btn.textContent = p.label;
				btn.onclick = () => {
					activeProfile = p.id;
					updateProfile();
					buildProfileList();
				};
				list.appendChild(btn);
			});
		}

		function updateProfile() {
			const p = PROFILES.find((x) => x.id === activeProfile);
			if (!p) return;
			const w = SCC.width,
				h = SCC.height;

			// Spacing chart
			scctx.clearRect(0, 0, w, h);
			const pad = 12,
				trackW = w - pad * 2,
				cy = h / 2;
			scctx.strokeStyle = C.border2;
			scctx.lineWidth = 1;
			scctx.beginPath();
			scctx.moveTo(pad, cy);
			scctx.lineTo(w - pad, cy);
			scctx.stroke();
			for (let i = 0; i <= 16; i++) {
				const t = i / 16,
					val = p.fn(t);
				const x = pad + val * trackW;
				scctx.fillStyle = C.gold;
				scctx.globalAlpha = 0.8;
				scctx.beginPath();
				scctx.arc(x, cy, 3.5, 0, Math.PI * 2);
				scctx.fill();
			}
			scctx.globalAlpha = 1;

			// Description
			document.getElementById('scDescription').textContent = p.desc;

			// Preview
			drawScPreview(scAnimT);
		}

		function drawScPreview(t) {
			const p = PROFILES.find((x) => x.id === activeProfile);
			if (!p) return;
			const w = SCPREV.width,
				h = SCPREV.height;
			scPrevCtx.clearRect(0, 0, w, h);
			const pad = 14,
				trackW = w - pad * 2,
				cy = h / 2;
			scPrevCtx.strokeStyle = C.border2;
			scPrevCtx.lineWidth = 1;
			scPrevCtx.setLineDash([3, 3]);
			scPrevCtx.beginPath();
			scPrevCtx.moveTo(pad, cy);
			scPrevCtx.lineTo(w - pad, cy);
			scPrevCtx.stroke();
			scPrevCtx.setLineDash([]);
			const val = p.fn(Math.min(1, t));
			const bx = pad + val * trackW;
			const grd = scPrevCtx.createRadialGradient(bx - 3, cy - 3, 1, bx, cy, 11);
			grd.addColorStop(0, '#ffc85a');
			grd.addColorStop(1, '#b07010');
			scPrevCtx.fillStyle = grd;
			scPrevCtx.beginPath();
			scPrevCtx.arc(bx, cy, 11, 0, Math.PI * 2);
			scPrevCtx.fill();
		}

		function scTick(ts) {
			if (scLastTs === null) scLastTs = ts;
			const dt = (ts - scLastTs) / 1000;
			scLastTs = ts;
			scAnimT = Math.min(1, scAnimT + dt * 0.55);
			drawScPreview(scAnimT);
			if (scAnimT < 1) scRafId = requestAnimationFrame(scTick);
			else {
				scPlaying = false;
				document.getElementById('scPlayBtn').textContent = '▶ Animate';
				document.getElementById('scPlayBtn').classList.remove('active');
				scLastTs = null;
			}
		}

		document.getElementById('scPlayBtn').onclick = function () {
			if (!scPlaying) {
				if (scAnimT >= 1) scAnimT = 0;
				scPlaying = true;
				this.textContent = '⏸ Playing…';
				this.classList.add('active');
				scRafId = requestAnimationFrame(scTick);
			}
		};
		document.getElementById('scResetBtn').onclick = function () {
			cancelAnimationFrame(scRafId);
			scPlaying = false;
			scAnimT = 0;
			scLastTs = null;
			document.getElementById('scPlayBtn').textContent = '▶ Animate';
			document.getElementById('scPlayBtn').classList.remove('active');
			drawScPreview(0);
		};

		buildProfileList();
		updateProfile();

		/* ══════════════════════════════════════════
   QUIZ
══════════════════════════════════════════ */
		let quizScores = {};
		function answer(optEl, qId, result) {
			const qEl = document.getElementById(qId);
			if (qEl.querySelector('.option.correct') || qEl.querySelector('.option.wrong')) return;
			const fb = document.getElementById(qId + '-feedback');
			optEl.classList.add(result === 'correct' ? 'correct' : 'wrong');
			qEl.querySelectorAll('.option').forEach((o) => o.classList.add('disabled'));
			if (result === 'correct') {
				fb.textContent = '✓ Correct.';
				fb.className = 'feedback ok';
				quizScores[qId] = true;
			} else {
				fb.textContent = '✗ Not quite — review the section and look for the correct answer.';
				fb.className = 'feedback bad';
				quizScores[qId] = false;
				qEl.querySelectorAll('.option').forEach((o) => {
					if (!o.classList.contains('wrong')) o.classList.add('correct');
				});
			}
			if (Object.keys(quizScores).length === 5) {
				const correct = Object.values(quizScores).filter(Boolean).length;
				document.getElementById('scoreNum').textContent = `${correct}/5`;
				document.getElementById('scoreLbl').textContent =
					correct === 5
						? 'Perfect — Module 2 Complete!'
						: correct >= 4
							? 'Strong — review any you missed.'
							: 'Good effort — re-read the sections and try again.';
				document.getElementById('quizScore').classList.add('visible');
			}
		}

		/* eslint-disable no-undef */
		if (typeof arcPos === 'function') window.arcPos = arcPos;
		if (typeof clamp01 === 'function') window.clamp01 = clamp01;
		if (typeof drawWeightBall === 'function') window.drawWeightBall = drawWeightBall;
		if (typeof renderArc === 'function') window.renderArc = renderArc;
		if (typeof getSimParams === 'function') window.getSimParams = getSimParams;
		if (typeof scTick === 'function') window.scTick = scTick;
		if (typeof answer === 'function') window.answer = answer;
		if (typeof easeIn === 'function') window.easeIn = easeIn;
		if (typeof arcTick === 'function') window.arcTick = arcTick;
		if (typeof buildProfileList === 'function') window.buildProfileList = buildProfileList;
		if (typeof evalCurve === 'function') window.evalCurve = evalCurve;
		if (typeof cubicBezier === 'function') window.cubicBezier = cubicBezier;
		if (typeof setArcMode === 'function') window.setArcMode = setArcMode;
		if (typeof hitTest === 'function') window.hitTest = hitTest;
		if (typeof easeInOut === 'function') window.easeInOut = easeInOut;
		if (typeof getPos === 'function') window.getPos = getPos;
		if (typeof drawBall === 'function') window.drawBall = drawBall;
		if (typeof rebuildSim === 'function') window.rebuildSim = rebuildSim;
		if (typeof renderWeight === 'function') window.renderWeight = renderWeight;
		if (typeof applyPreset === 'function') window.applyPreset = applyPreset;
		if (typeof linear === 'function') window.linear = linear;
		if (typeof easeOut === 'function') window.easeOut = easeOut;
		if (typeof simulateBounce === 'function') window.simulateBounce = simulateBounce;
		if (typeof drawScPreview === 'function') window.drawScPreview = drawScPreview;
		if (typeof weightTick === 'function') window.weightTick = weightTick;
		if (typeof updateProfile === 'function') window.updateProfile = updateProfile;
		if (typeof updateReadout === 'function') window.updateReadout = updateReadout;
		if (typeof toCanvas === 'function') window.toCanvas = toCanvas;
		if (typeof drawCurveEditor === 'function') window.drawCurveEditor = drawCurveEditor;
		if (typeof drawCurvePreview === 'function') window.drawCurvePreview = drawCurvePreview;
		if (typeof straightPos === 'function') window.straightPos = straightPos;
		if (typeof lerp === 'function') window.lerp = lerp;
		if (typeof fromCanvas === 'function') window.fromCanvas = fromCanvas;
		if (typeof drawSpacingChart === 'function') window.drawSpacingChart = drawSpacingChart;
		if (typeof curveTick === 'function') window.curveTick = curveTick;
		if (typeof moveHandle === 'function') window.moveHandle = moveHandle;
		/* eslint-enable no-undef */

		return () => {
			if (typeof curveRafId !== 'undefined' && curveRafId) cancelAnimationFrame(curveRafId);
			if (typeof arcRafId !== 'undefined' && arcRafId) cancelAnimationFrame(arcRafId);
			if (typeof weightRafId !== 'undefined' && weightRafId) cancelAnimationFrame(weightRafId);
			if (typeof scRafId !== 'undefined' && scRafId) cancelAnimationFrame(scRafId);
		};
	});
</script>

<div class="page-wrapper">
	<!-- ══ HERO ══ -->
	<header class="module-hero">
		<!-- Spacing-chart deco: dots with increasing gaps -->
		<div class="hero-deco" id="heroDeco" aria-hidden="true"></div>

		<div class="module-eyebrow">Animation Fundamentals · Module 02</div>
		<h1 class="module-title">Timing, Spacing<br />&amp; the Illusion of <em>Weight</em></h1>
		<p class="module-subtitle">Making motion feel like it has mass, gravity, and consequence.</p>

		<div class="objectives">
			<div class="obj-label">Learning Objectives</div>
			<ul>
				<li>Produce convincing motion using timing and spacing variations</li>
				<li>Understand and apply easing curves (slow-in / slow-out)</li>
				<li>Convey weight, gravity, and impact through spacing alone</li>
				<li>Read a motion graph and predict what the animation will look like</li>
				<li>Use arcs to make movement feel natural and physical</li>
			</ul>
		</div>
	</header>

	<!-- ══ SECTION 1: RECAP + DEEPER DIVE ══ -->
	<section class="section" id="s1">
		<div class="section-header">
			<span class="section-num">01</span>
			<h2 class="section-title">From Spacing to Weight</h2>
		</div>

		<p>
			In Module 1 you saw that <strong>timing</strong> (how many frames) and
			<strong>spacing</strong> (where in each frame) are different things. Now we go deeper: spacing
			is not just a stylistic choice. It is how you encode <em>physics</em> into your animation.
		</p>
		<p>
			Every object in the real world is subject to forces — gravity, friction, momentum, elasticity.
			These forces produce <strong>non-linear motion</strong>. Nothing starts or stops instantly.
			Nothing travels at perfectly constant speed. Spacing is how you translate those physical
			realities into frame positions.
		</p>

		<div class="callout gold">
			<div class="callout-label">Core Principle</div>
			The distance between two consecutive frames tells the viewer how fast the object is moving
			<em>at that moment</em>. Tightly packed frames = slow. Widely spread frames = fast. The
			pattern of that spacing over time communicates acceleration, deceleration, and — therefore —
			<strong>mass</strong>.
		</div>

		<p>
			A feather and a bowling ball dropped from the same height take the same number of frames to
			fall (same timing). What differs is the character of their <em>bounce</em> — how much they deform
			on impact, how high they rebound, how quickly that rebound decays. All of that lives in spacing.
		</p>
	</section>

	<!-- ══ SECTION 2: EASING CURVES ══ -->
	<section class="section" id="s2">
		<div class="section-header">
			<span class="section-num">02</span>
			<h2 class="section-title">Easing &amp; the Motion Graph</h2>
		</div>

		<p>
			Every animation software gives you a <strong>motion graph</strong> (also called a graph editor
			or curve editor). It plots an object's property — position, rotation, scale — against time.
			The <em>shape</em> of that curve determines the spacing between frames.
		</p>
		<p>
			A straight diagonal line means constant speed (linear). A curve that starts shallow and gets
			steep means the object is <em>accelerating</em>. A curve that starts steep and flattens means
			it is <em>decelerating</em>. The animator's job is to sculpt these curves.
		</p>

		<!-- DEMO 2.1: Curve Editor -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 2.1 — Motion Graph &amp; Live Preview</span>
				<span class="demo-badge coral">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1rem">
					Edit the curve by dragging the <strong style="color: var(--coral)">handles</strong>, or
					pick a preset. Watch how the curve shape directly produces the ball's motion below.
				</p>

				<div style="display: flex; gap: 1.5rem; flex-wrap: wrap">
					<!-- Curve editor -->
					<div style="flex: 0 0 auto">
						<canvas
							id="curveCanvas"
							width="240"
							height="220"
							style="
										background: var(--raised);
										border: 1px solid var(--border);
										cursor: crosshair;
										touch-action: none;
									"
						></canvas>
						<div
							style="
										margin-top: 0.4rem;
										font-family: var(--ff-mono);
										font-size: 9px;
										color: var(--dim);
										text-align: center;
									"
						>
							Drag handles to reshape
						</div>
					</div>

					<!-- Live preview + spacing chart -->
					<div style="flex: 1; min-width: 220px; display: flex; flex-direction: column; gap: 1rem">
						<canvas
							id="curvePreviewCanvas"
							width="300"
							height="80"
							style="
										background: var(--raised);
										border: 1px solid var(--border);
										max-width: 100%;
									"
						></canvas>

						<div>
							<div
								style="
											font-family: var(--ff-mono);
											font-size: 10px;
											color: var(--muted);
											margin-bottom: 0.4rem;
										"
							>
								Spacing Chart — frame positions
							</div>
							<canvas
								id="spacingChartCanvas"
								width="300"
								height="48"
								style="
											background: var(--raised);
											border: 1px solid var(--border);
											max-width: 100%;
										"
							></canvas>
						</div>

						<div>
							<div
								style="
											font-family: var(--ff-mono);
											font-size: 10px;
											color: var(--muted);
											margin-bottom: 0.3rem;
										"
							>
								Presets
							</div>
							<div class="preset-row" id="presetRow">
								<button
									class="preset-btn"
									data-preset="linear"
									onclick={(e) => {
										window.applyPreset('linear');
									}}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter') window.applyPreset('linear');
									}}
								>
									Linear
								</button>
								<button
									class="preset-btn active"
									data-preset="ease"
									onclick={(e) => {
										window.applyPreset('ease');
									}}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter') window.applyPreset('ease');
									}}
								>
									Ease
								</button>
								<button
									class="preset-btn"
									data-preset="easeIn"
									onclick={(e) => {
										window.applyPreset('easeIn');
									}}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter') window.applyPreset('easeIn');
									}}
								>
									Ease In
								</button>
								<button
									class="preset-btn"
									data-preset="easeOut"
									onclick={(e) => {
										window.applyPreset('easeOut');
									}}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter') window.applyPreset('easeOut');
									}}
								>
									Ease Out
								</button>
								<button
									class="preset-btn"
									data-preset="overshoot"
									onclick={(e) => {
										window.applyPreset('overshoot');
									}}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter') window.applyPreset('overshoot');
									}}
								>
									Overshoot
								</button>
								<button
									class="preset-btn"
									data-preset="anticipate"
									onclick={(e) => {
										window.applyPreset('anticipate');
									}}
									role="button"
									tabindex="0"
									onkeydown={(e) => {
										if (e.key === 'Enter') window.applyPreset('anticipate');
									}}
								>
									Anticipate
								</button>
							</div>
						</div>

						<div
							id="curveReadout"
							style="
										font-family: var(--ff-mono);
										font-size: 11px;
										color: var(--muted);
										line-height: 1.8;
									"
						></div>
					</div>
				</div>

				<div class="btn-row" style="margin-top: 1.25rem">
					<button class="btn coral" id="curvePlayBtn">▶ Animate</button>
					<button class="btn" id="curveResetBtn">↺ Reset</button>
				</div>
			</div>
		</div>

		<p>
			The <strong>Ease</strong> preset (slow-in, slow-out) is the default choice for almost all secondary
			motion in educational animation — camera moves, label reveals, diagram transitions. It feels natural
			because it mirrors how objects actually accelerate and decelerate in the world.
		</p>
		<p>
			<strong>Ease In</strong> alone means the object starts slow then rushes off — good for
			launches and impacts. <strong>Ease Out</strong> alone means it arrives quickly then settles —
			good for things landing. <strong>Overshoot</strong> goes past the target and snaps back, adding
			springiness and life.
		</p>
	</section>

	<!-- ══ SECTION 3: ARCS ══ -->
	<section class="section" id="s3">
		<div class="section-header">
			<span class="section-num">03</span>
			<h2 class="section-title">Arcs — The Path of Action</h2>
		</div>

		<p>
			Natural motion rarely travels in straight lines. A thrown object traces a
			<em>parabola</em>. A swinging arm follows an arc centered on the shoulder joint. Even a simple
			head turn describes a curved path through space. Animators call this the
			<strong>arc</strong> of the motion.
		</p>
		<p>
			Straight-line paths between keyframes are one of the most common mistakes beginners make.
			Software interpolation defaults to linear paths — you must <em>add arcs yourself</em>, either
			by adding intermediate keyframes along a curve or by shaping the motion path directly.
		</p>

		<div class="callout coral">
			<div class="callout-label">Why Arcs Matter</div>
			Straight paths feel mechanical and stiff because they don't exist in nature — they're how
			<em>machines</em> move. Arcs feel alive because every joint, limb, and projectile in the real world
			follows rotational or ballistic trajectories. Arcs are the difference between a robot and a living
			thing.
		</div>

		<!-- DEMO 2.2: Arc vs Straight Path -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 2.2 — Arc vs. Straight Path</span>
				<span class="demo-badge mint">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1rem">
					Both objects travel from left to right in the same number of frames. Toggle between motion
					types to see the difference.
				</p>

				<div class="arc-tabs" id="arcTabs">
					<div
						class="arc-tab active"
						onclick={(e) => {
							window.setArcMode('both');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setArcMode('both');
						}}
					>
						Both
					</div>
					<div
						class="arc-tab"
						onclick={(e) => {
							window.setArcMode('straight');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setArcMode('straight');
						}}
					>
						Straight Only
					</div>
					<div
						class="arc-tab"
						onclick={(e) => {
							window.setArcMode('arc');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setArcMode('arc');
						}}
					>
						Arc Only
					</div>
				</div>

				<canvas
					id="arcCanvas"
					width="560"
					height="180"
					style="background: var(--raised); border: 1px solid var(--border); max-width: 100%"
				></canvas>

				<div style="display: flex; gap: 1.5rem; margin-top: 0.75rem; flex-wrap: wrap">
					<div class="legend-item">
						<div class="legend-swatch" style="background: var(--gold)"></div>
						Arc path
					</div>
					<div class="legend-item">
						<div class="legend-swatch" style="background: var(--coral)"></div>
						Straight path
					</div>
				</div>

				<div class="btn-row">
					<button class="btn mint" id="arcPlayBtn">▶ Animate</button>
					<button class="btn" id="arcResetBtn">↺ Reset</button>
					<label
						style="
									display: flex;
									align-items: center;
									gap: 0.5rem;
									font-family: var(--ff-mono);
									font-size: 11px;
									color: var(--muted);
									cursor: pointer;
									margin-left: auto;
								"
					>
						<input type="checkbox" id="arcShowPath" checked style="accent-color: var(--gold)" />Show
						paths
					</label>
				</div>

				<div class="callout mint" style="margin-top: 1.25rem">
					<div class="callout-label">Notice</div>
					The arc path also has eased spacing along the curve — frames are clustered at the start and
					end, spread in the middle. The straight path uses linear spacing. Both effects compound to make
					the arc feel dramatically more alive.
				</div>
			</div>
		</div>
	</section>

	<!-- ══ SECTION 4: WEIGHT ══ -->
	<section class="section" id="s4">
		<div class="section-header">
			<span class="section-num">04</span>
			<h2 class="section-title">Conveying Weight Through Spacing</h2>
		</div>

		<p>
			Weight is one of the most powerful things an animator can communicate, and it is done entirely
			through <strong>spacing decisions</strong>. A heavy object accelerates slowly, hits hard, and
			barely bounces. A light object accelerates quickly, bounces high, and loses energy gradually.
		</p>
		<p>
			These perceptions come from frame density patterns. Watch the spacing chart below each ball:
			the heavy ball's frames are packed tight near the top (slow start) and spread wide near impact
			(fast arrival). The light ball's frames spread quickly — it accelerates fast. Their <em
				>timing</em
			>
			(total frames) is similar. The <em>physics</em> is all in spacing.
		</p>

		<!-- DEMO 2.3: Weight Comparison -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 2.3 — Weight Simulation</span>
				<span class="demo-badge">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					Adjust mass, elasticity, and gravity to see how spacing patterns encode physical
					properties. The trace dots show frame positions on the path.
				</p>

				<canvas
					id="weightCanvas"
					width="560"
					height="220"
					style="background: var(--raised); border: 1px solid var(--border); max-width: 100%"
				></canvas>

				<div
					style="
								margin-top: 1rem;
								display: grid;
								grid-template-columns: 1fr 1fr;
								gap: 1px;
								background: var(--border);
							"
					id="weightControls"
				>
					<div style="background: var(--surface); padding: 0.75rem 1rem">
						<div
							style="
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--gold);
										margin-bottom: 0.5rem;
									"
						>
							BALL A
						</div>
						<div class="ctrl-row">
							<span class="ctrl-label">Elasticity</span>
							<input type="range" id="elastA" min="0.1" max="0.95" step="0.05" value="0.3" />
							<span class="ctrl-val" id="elastAVal">0.30</span>
						</div>
					</div>
					<div style="background: var(--surface); padding: 0.75rem 1rem">
						<div
							style="
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--coral);
										margin-bottom: 0.5rem;
									"
						>
							BALL B
						</div>
						<div class="ctrl-row">
							<span class="ctrl-label">Elasticity</span>
							<input
								type="range"
								id="elastB"
								min="0.1"
								max="0.95"
								step="0.05"
								value="0.75"
								class="coral"
							/>
							<span class="ctrl-val" id="elastBVal" style="color: var(--coral)">0.75</span>
						</div>
					</div>
				</div>
				<div
					style="
								padding: 0.75rem 1rem;
								border: 1px solid var(--border);
								border-top: none;
								background: var(--raised);
							"
				>
					<div class="ctrl-row">
						<span class="ctrl-label">Gravity</span>
						<input type="range" id="gravSlider" min="200" max="900" step="50" value="500" />
						<span class="ctrl-val" id="gravVal">500</span>
					</div>
				</div>

				<div class="btn-row">
					<button class="btn" id="weightPlayBtn">▶ Drop</button>
					<button class="btn" id="weightResetBtn">↺ Reset</button>
					<label
						style="
									display: flex;
									align-items: center;
									gap: 0.5rem;
									font-family: var(--ff-mono);
									font-size: 11px;
									color: var(--muted);
									cursor: pointer;
									margin-left: auto;
								"
					>
						<input
							type="checkbox"
							id="weightShowDots"
							checked
							style="accent-color: var(--gold)"
						/>Show spacing dots
					</label>
				</div>
			</div>
		</div>

		<p>
			The <strong>squash-and-stretch</strong> on impact also reinforces weight. A heavy object
			squashes more aggressively on impact and takes longer to return to its rest shape. A rubber
			ball squashes fast and snaps back instantly. These are not arbitrary stylistic choices — they
			are the visual language of <em>mass and material</em>.
		</p>

		<div class="callout gold">
			<div class="callout-label">Practical Rule</div>
			When in doubt, make your animation slightly slower than you think it needs to be. Beginners almost
			always animate too fast. Weight requires<strong>patience</strong> in frames — you need to give the
			audience time to perceive the object's mass before impact.
		</div>
	</section>

	<!-- ══ SECTION 5: SPACING CHARTS ══ -->
	<section class="section" id="s5">
		<div class="section-header">
			<span class="section-num">05</span>
			<h2 class="section-title">Spacing Charts — Planning on Paper</h2>
		</div>

		<p>
			Before digital tools existed, animators used <strong>spacing charts</strong> — simple diagrams drawn
			on the side of an exposure sheet that showed how far apart each in-between frame should be. The
			assistant animators (in-betweeners) used these charts to know where to draw each intermediate frame.
		</p>
		<p>
			Even if you work entirely in software, understanding spacing charts trains your eye to
			<em>read</em> motion graphs. They're the same information in a different visual form.
		</p>

		<!-- DEMO 2.4: Spacing Chart Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 2.4 — Spacing Chart Builder</span>
				<span class="demo-badge">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1rem">
					Choose a motion profile and see the corresponding spacing chart. Then hit "Animate" to
					watch the motion it produces.
				</p>

				<div style="display: flex; gap: 1.5rem; flex-wrap: wrap">
					<div style="flex: 1; min-width: 200px">
						<div
							style="
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--muted);
										margin-bottom: 0.5rem;
									"
						>
							Motion Profile
						</div>
						<div style="display: flex; flex-direction: column; gap: 0.4rem" id="profileList"></div>
					</div>

					<div style="flex: 2; min-width: 260px">
						<div
							style="
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--muted);
										margin-bottom: 0.5rem;
									"
						>
							Spacing Chart
						</div>
						<canvas
							id="scChartCanvas"
							width="320"
							height="56"
							style="
										background: var(--raised);
										border: 1px solid var(--border);
										display: block;
										max-width: 100%;
									"
						></canvas>

						<div
							style="
										margin-top: 1rem;
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--muted);
										margin-bottom: 0.5rem;
									"
						>
							Live Preview
						</div>
						<canvas
							id="scPreviewCanvas"
							width="320"
							height="60"
							style="
										background: var(--raised);
										border: 1px solid var(--border);
										display: block;
										max-width: 100%;
									"
						></canvas>

						<div
							id="scDescription"
							style="
										margin-top: 0.75rem;
										font-size: 12px;
										color: var(--muted);
										line-height: 1.6;
										font-family: var(--ff-mono);
										min-height: 2.5em;
									"
						></div>
					</div>
				</div>

				<div class="btn-row">
					<button class="btn" id="scPlayBtn">▶ Animate</button>
					<button class="btn" id="scResetBtn">↺ Reset</button>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ QUIZ ══ -->
	<div class="quiz-section" id="quiz">
		<div class="quiz-header-bar">
			<div>
				<div class="quiz-title">Module Check</div>
				<div class="quiz-sub">5 questions · Motion graph analysis</div>
			</div>
			<span class="demo-badge coral">Assessment</span>
		</div>

		<div class="quiz-body">
			<!-- Q1 -->
			<div class="question" id="q1">
				<div class="q-num">Q1 of 5</div>
				<div class="q-text">
					A motion graph shows a curve that starts very steep and gradually flattens out toward the
					end. What does this animation look like?
				</div>
				<div class="options">
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q1', 'wrong');
						}}
					>
						The object starts slowly and accelerates toward the end
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q1', 'correct');
						}}
					>
						The object moves fast at first, then decelerates to a stop
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q1', 'wrong');
						}}
					>
						The object moves at constant speed throughout
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q1', 'wrong');
						}}
					>
						The object reverses direction halfway through
					</div>
				</div>
				<div class="feedback" id="q1-feedback"></div>
			</div>

			<!-- Q2 -->
			<div class="question" id="q2">
				<div class="q-num">Q2 of 5</div>
				<div class="q-text">
					Two balls animate across the screen. Ball A has frames evenly spaced. Ball B has frames
					clustered at the start and end, spread in the middle. Which statement is true?
				</div>
				<div class="options">
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q2', 'wrong');
						}}
					>
						Ball A has eased motion; Ball B is linear
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q2', 'correct');
						}}
					>
						Ball A is linear; Ball B has slow-in/slow-out easing
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q2', 'wrong');
						}}
					>
						Both balls have the same spacing — only their timing differs
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q2', 'wrong');
						}}
					>
						Ball B is moving backwards
					</div>
				</div>
				<div class="feedback" id="q2-feedback"></div>
			</div>

			<!-- Q3 — with inline canvas as "image" -->
			<div class="question" id="q3">
				<div class="q-num">Q3 of 5</div>
				<div class="q-text">
					Why do animators draw motion along arcs rather than straight lines?
				</div>
				<div class="options">
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q3', 'wrong');
						}}
					>
						Straight lines are harder to draw in software
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q3', 'wrong');
						}}
					>
						Arcs use fewer keyframes
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q3', 'correct');
						}}
					>
						Natural motion follows rotational and ballistic trajectories — arcs mimic how things
						actually move in the physical world
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q3', 'wrong');
						}}
					>
						Arcs are only needed for character animation, not objects
					</div>
				</div>
				<div class="feedback" id="q3-feedback"></div>
			</div>

			<!-- Q4 -->
			<div class="question" id="q4">
				<div class="q-num">Q4 of 5</div>
				<div class="q-text">
					A heavy iron ball and a rubber ball are dropped from the same height. Their timing (total
					frames to fall) is identical. What differs between them in the animation?
				</div>
				<div class="options">
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q4', 'wrong');
						}}
					>
						The frame rate used to render each ball
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q4', 'correct');
						}}
					>
						Their spacing patterns and bounce behaviour — the rubber ball rebounds high and bounces
						many times; the iron ball barely bounces
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q4', 'wrong');
						}}
					>
						The arcs they travel along
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q4', 'wrong');
						}}
					>
						Nothing — identical timing means identical animation
					</div>
				</div>
				<div class="feedback" id="q4-feedback"></div>
			</div>

			<!-- Q5 -->
			<div class="question" id="q5">
				<div class="q-num">Q5 of 5</div>
				<div class="q-text">
					An "overshoot" easing curve means the animated value briefly goes past its target before
					settling. What visual effect does this create?
				</div>
				<div class="options">
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q5', 'wrong');
						}}
					>
						The object reverses direction completely
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q5', 'wrong');
						}}
					>
						The animation plays in reverse
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q5', 'correct');
						}}
					>
						The object feels springy and alive — it overshoots the end position and snaps back,
						conveying elasticity
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.answer(e.currentTarget, 'q5', 'wrong');
						}}
					>
						The object accelerates to infinite speed
					</div>
				</div>
				<div class="feedback" id="q5-feedback"></div>
			</div>
		</div>

		<div class="quiz-score" id="quizScore">
			<div class="score-big" id="scoreNum">0/5</div>
			<div class="score-lbl" id="scoreLbl">Module 2 Complete</div>
		</div>
	</div>

	<!-- ══ NAV ══ -->
	<nav class="nav-links">
		<a href="/courses/animation/01" class="prev-link">← Module 1: What Animation Is</a>
		<a href="/courses/animation/03" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">The 12 Principles</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</nav>
</div>

<!-- /page-wrapper -->

<style>
	.page-wrapper {
		background: var(--anim-bg);
		color: var(--anim-text);
		font-family: var(--ff-body);
		font-size: 15px;
		line-height: 1.8;
	}

	h1,
	h2,
	:global(h3) {
		font-family: var(--ff-display);
		font-weight: 800;
		line-height: 1.15;
		color: #fff;
	}
	p {
		margin-bottom: 1.1rem;
	}
	p:last-child {
		margin-bottom: 0;
	}
	strong {
		color: var(--anim-gold);
		font-weight: 600;
	}
	em {
		color: #fff;
		font-style: italic;
	}
	:global(code) {
		font-family: var(--ff-mono);
		font-size: 12px;
		background: var(--anim-raised);
		border: 1px solid var(--anim-border2);
		padding: 1px 6px;
		color: var(--anim-mint);
	}

	.page-wrapper {
		max-width: 900px;
		margin: 0 auto;
		padding: 0 2rem 8rem;
	}

	/* ── HERO ── */
	.module-hero {
		padding: 5rem 0 4rem;
		border-bottom: 1px solid var(--anim-border);
		margin-bottom: 4rem;
		position: relative;
		overflow: hidden;
	}
	.module-eyebrow {
		font-family: var(--ff-mono);
		font-size: 11px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--anim-gold);
		margin-bottom: 1rem;
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	.module-eyebrow::before,
	.module-eyebrow::after {
		content: '';
		display: inline-block;
		width: 24px;
		height: 1px;
		background: var(--anim-gold);
	}
	.module-title {
		font-size: clamp(32px, 6vw, 58px);
		color: #fff;
		margin-bottom: 0.5rem;
		letter-spacing: -0.02em;
	}
	.module-title em {
		color: var(--anim-coral);
		font-style: italic;
	}
	.module-subtitle {
		font-size: 16px;
		color: var(--anim-muted);
		font-weight: 400;
		margin-bottom: 2.5rem;
	}

	/* hero deco — spacing dots */
	.hero-deco {
		position: absolute;
		top: 20px;
		right: 0;
		pointer-events: none;
		opacity: 0.06;
		display: flex;
		gap: 0;
	}
	:global(.hero-deco-col) {
		display: flex;
		flex-direction: column;
		gap: 0;
	}
	:global(.hero-dot) {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--anim-coral);
	}

	/* ── OBJECTIVES ── */
	.objectives {
		border: 1px solid var(--anim-border);
		border-left: 3px solid var(--anim-coral);
		background: var(--anim-surface);
		padding: 1.5rem 2rem;
		margin-bottom: 1rem;
	}
	.obj-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--anim-coral);
		margin-bottom: 1rem;
	}
	.objectives ul {
		list-style: none;
	}
	.objectives li {
		padding: 0.25rem 0 0.25rem 1.5rem;
		position: relative;
		font-size: 14px;
	}
	.objectives li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--anim-gold);
	}

	/* ── SECTIONS ── */
	.section {
		margin: 5rem 0;
	}
	.section-header {
		display: flex;
		align-items: baseline;
		gap: 1rem;
		margin-bottom: 2rem;
		padding-bottom: 0.75rem;
		border-bottom: 1px solid var(--anim-border);
	}
	.section-num {
		font-family: var(--ff-mono);
		font-size: 11px;
		color: var(--anim-gold);
		letter-spacing: 0.1em;
	}
	.section-title {
		font-family: var(--ff-display);
		font-size: 26px;
		color: #fff;
		font-weight: 600;
	}

	/* ── CALLOUT ── */
	.callout {
		margin: 1.75rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--anim-lavender);
		background: color-mix(in srgb, var(--anim-lavender) 5%, var(--anim-surface));
		font-size: 13.5px;
	}
	.callout.gold {
		border-color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 5%, var(--anim-surface));
	}
	.callout.coral {
		border-color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 5%, var(--anim-surface));
	}
	.callout.mint {
		border-color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 5%, var(--anim-surface));
	}
	.callout-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		margin-bottom: 0.4rem;
		font-weight: 500;
	}
	.callout .callout-label {
		color: var(--anim-lavender);
	}
	.callout.gold .callout-label {
		color: var(--anim-gold);
	}
	.callout.coral .callout-label {
		color: var(--anim-coral);
	}
	.callout.mint .callout-label {
		color: var(--anim-mint);
	}

	/* ── DEMO BOX ── */
	.demo-box {
		background: var(--anim-surface);
		border: 1px solid var(--anim-border);
		margin: 2.5rem 0;
	}
	.demo-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--anim-border);
	}
	.demo-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--anim-muted);
	}
	.demo-badge {
		font-family: var(--ff-mono);
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid var(--anim-gold);
		color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 10%, transparent);
	}
	.demo-badge.coral {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 10%, transparent);
	}
	.demo-badge.mint {
		border-color: var(--anim-mint);
		color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	canvas {
		display: block;
	}

	/* ── CONTROLS ── */
	.ctrl-row {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 0.5rem 0;
		flex-wrap: wrap;
	}
	.ctrl-label {
		font-family: var(--ff-mono);
		font-size: 11px;
		color: var(--anim-muted);
		min-width: 80px;
	}
	.ctrl-val {
		font-family: var(--ff-mono);
		font-size: 12px;
		color: var(--anim-gold);
		font-weight: 500;
		min-width: 52px;
	}

	input[type='range'] {
		flex: 1;
		-webkit-appearance: none;
		height: 2px;
		background: var(--anim-border2);
		outline: none;
		min-width: 100px;
	}
	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: var(--anim-gold);
		cursor: pointer;
		border: 2px solid var(--anim-bg);
	}
	input[type='range'].coral::-webkit-slider-thumb {
		background: var(--anim-coral);
	}
	input[type='range'].mint::-webkit-slider-thumb {
		background: var(--anim-mint);
	}

	.btn {
		background: transparent;
		border: 1px solid var(--anim-border2);
		color: var(--anim-text);
		padding: 6px 16px;
		font-family: var(--ff-mono);
		font-size: 11px;
		cursor: pointer;
		transition: all 0.15s;
		letter-spacing: 0.05em;
	}
	.btn:hover {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
	}
	:global(.btn.active) {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 12%, transparent);
	}
	.btn.coral:hover,
	:global(.btn.coral.active) {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
	}
	:global(.btn.coral.active) {
		background: color-mix(in srgb, var(--anim-coral) 12%, transparent);
	}
	.btn.mint:hover,
	:global(.btn.mint.active) {
		border-color: var(--anim-mint);
		color: var(--anim-mint);
	}
	:global(.btn.mint.active) {
		background: color-mix(in srgb, var(--anim-mint) 12%, transparent);
	}

	.btn-row {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-top: 1rem;
	}

	/* ── EASING PRESETS ROW ── */
	.preset-row {
		display: flex;
		gap: 0.4rem;
		flex-wrap: wrap;
		margin: 0.75rem 0;
	}
	:global(.preset-btn) {
		background: var(--anim-raised);
		border: 1px solid var(--anim-border2);
		color: var(--anim-muted);
		padding: 5px 12px;
		font-family: var(--ff-mono);
		font-size: 10px;
		cursor: pointer;
		transition: all 0.15s;
		letter-spacing: 0.05em;
	}
	:global(.preset-btn:hover) {
		border-color: var(--anim-border2);
		color: var(--anim-text);
	}
	:global(.preset-btn.active) {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 10%, transparent);
	}

	/* ── SPACING CHART ── */
	:global(.spacing-chart-wrap) {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 0.75rem 0;
	}
	:global(.spacing-row) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	:global(.spacing-row-label) {
		font-family: var(--ff-mono);
		font-size: 10px;
		color: var(--anim-muted);
		min-width: 72px;
		text-align: right;
	}
	:global(.spacing-track) {
		flex: 1;
		height: 20px;
		position: relative;
	}
	:global(.spacing-dot) {
		position: absolute;
		top: 50%;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		transform: translate(-50%, -50%);
	}

	/* ── ARC PATH SELECTOR ── */
	.arc-tabs {
		display: flex;
		gap: 0;
		border: 1px solid var(--anim-border);
		margin-bottom: 1rem;
	}
	.arc-tab {
		flex: 1;
		padding: 0.5rem 0.75rem;
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		cursor: pointer;
		text-align: center;
		border-right: 1px solid var(--anim-border);
		color: var(--anim-muted);
		transition: all 0.15s;
	}
	.arc-tab:last-child {
		border-right: none;
	}
	.arc-tab:hover {
		color: var(--anim-text);
	}
	.arc-tab.active {
		background: color-mix(in srgb, var(--anim-mint) 8%, var(--anim-raised));
		color: var(--anim-mint);
	}

	/* ── WEIGHT COMPARISON ── */
	:global(.weight-grid) {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1px;
		background: var(--anim-border);
		border: 1px solid var(--anim-border);
	}
	:global(.weight-panel) {
		background: var(--anim-surface);
		padding: 0.75rem 1rem;
	}
	:global(.weight-label) {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--anim-muted);
		margin-bottom: 0.4rem;
	}
	:global(.weight-label) span {
		color: var(--anim-gold);
	}
	@media (max-width: 600px) {
		:global(.weight-grid) {
			grid-template-columns: 1fr;
		}
	}

	/* ── CURVE MINI DISPLAY ── */
	:global(.curve-mini) {
		display: inline-block;
		vertical-align: middle;
	}

	/* ── QUIZ ── */
	.quiz-section {
		margin: 5rem 0;
		border: 1px solid var(--anim-border);
		background: var(--anim-surface);
	}
	.quiz-header-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1.75rem;
		border-bottom: 1px solid var(--anim-border);
	}
	.quiz-title {
		font-family: var(--ff-display);
		font-size: 22px;
		font-weight: 800;
		color: #fff;
	}
	.quiz-sub {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--anim-muted);
		margin-top: 0.2rem;
	}
	.quiz-body {
		padding: 1.75rem;
	}
	.question {
		margin: 2rem 0;
	}
	.question:first-child {
		margin-top: 0;
	}
	.q-num {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.1em;
		color: var(--anim-coral);
		margin-bottom: 0.4rem;
	}
	.q-text {
		font-size: 14px;
		color: #fff;
		margin-bottom: 1rem;
		line-height: 1.6;
	}
	:global(.q-img) {
		margin: 0.75rem 0;
		border: 1px solid var(--anim-border);
	}
	.options {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
	.option {
		padding: 0.65rem 1rem;
		border: 1px solid var(--anim-border);
		cursor: pointer;
		font-size: 13px;
		font-family: var(--ff-body);
		transition: all 0.15s;
		user-select: none;
		background: var(--anim-bg);
	}
	.option:hover {
		border-color: var(--anim-border2);
		background: var(--anim-raised);
	}
	:global(.option.correct) {
		border-color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 10%, transparent);
		color: var(--anim-mint);
	}
	:global(.option.wrong) {
		border-color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 10%, transparent);
		color: var(--anim-coral);
	}
	:global(.option.disabled) {
		pointer-events: none;
	}
	.feedback {
		font-size: 12px;
		margin-top: 0.6rem;
		min-height: 1.4em;
		font-family: var(--ff-mono);
		color: var(--anim-muted);
	}
	:global(.feedback.ok) {
		color: var(--anim-mint);
	}
	:global(.feedback.bad) {
		color: var(--anim-coral);
	}
	.quiz-score {
		margin-top: 2rem;
		padding: 2rem;
		border: 1px solid var(--anim-border);
		text-align: center;
		background: var(--anim-raised);
		display: none;
	}
	:global(.quiz-score.visible) {
		display: block;
	}
	.score-big {
		font-family: var(--ff-display);
		font-size: 52px;
		font-weight: 800;
		color: var(--anim-gold);
		line-height: 1;
	}
	.score-lbl {
		font-family: var(--ff-mono);
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--anim-muted);
		margin-top: 0.5rem;
	}

	/* ── NAV ── */
	.nav-links {
		display: flex;
		justify-content: space-between;
		margin-top: 4rem;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.prev-link {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 1.5rem 2rem;
		border: 1px solid var(--anim-border);
		background: var(--anim-surface);
		text-decoration: none;
		transition: all 0.2s;
		color: var(--anim-muted);
		font-family: var(--ff-mono);
		font-size: 11px;
	}
	.prev-link:hover {
		border-color: var(--anim-muted);
	}
	.next-module {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
		padding: 1.5rem 2rem;
		border: 1px solid var(--anim-border);
		background: var(--anim-surface);
		text-decoration: none;
		transition: all 0.2s;
		min-width: 260px;
	}
	.next-module:hover {
		border-color: var(--anim-gold);
	}
	.next-label {
		font-family: var(--ff-mono);
		font-size: 9px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--anim-muted);
	}
	.next-title {
		font-family: var(--ff-display);
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-top: 0.2rem;
	}
	.next-arrow {
		font-size: 28px;
		color: var(--anim-gold);
		flex-shrink: 0;
	}

	@media (max-width: 640px) {
		.page-wrapper {
			padding: 0 1.25rem 6rem;
		}
	}

	/* ── MOTION GRAPH LABELS ── */
	:global(.graph-legend) {
		display: flex;
		gap: 1.5rem;
		flex-wrap: wrap;
		margin: 0.75rem 0;
	}
	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--ff-mono);
		font-size: 10px;
		color: var(--anim-muted);
	}
	.legend-swatch {
		width: 16px;
		height: 2px;
		flex-shrink: 0;
	}
</style>
