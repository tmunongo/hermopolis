<script>
	/* eslint-disable @typescript-eslint/no-unused-vars */
	import { onMount } from 'svelte';

	onMount(() => {
		/* ══════════════════════════════════════ LOOP DIAGRAM ══ */
		const loopDetails = [
			`<strong style="color:var(--accent)">Measure Time</strong> — Use <code>time.perf_counter()</code> (not <code>time.time()</code>) for sub-millisecond resolution. The delta is the elapsed seconds since the previous frame. Store the current timestamp as <code>last_time</code> before advancing to the next iteration. Always cap the result at a maximum (e.g. 0.1s) to prevent runaway simulation after pauses.`,
			`<strong style="color:var(--accent)">Process Events</strong> — The OS queues window events (keyboard presses, mouse movement, resize requests, quit signals) in a buffer. If you don't drain this buffer every frame, it fills up and the OS marks the application as unresponsive. Event processing must complete before the update step so that input is immediately reflected.`,
			`<strong style="color:var(--accent)">Update</strong> — Advance every game system by delta_time: move entities, step the physics simulation, advance animation timers, count down cooldowns, run AI decisions. Order matters — physics before collision response, collision response before movement clamping. The update step should never touch the GPU directly.`,
			`<strong style="color:var(--accent)">Render</strong> — The GPU has its own timeline. After the update step has determined where everything is, issue GPU commands: clear the framebuffer, bind textures and buffers, issue draw calls, then swap buffers (present the back buffer to the screen). The CPU continues to the next frame while the GPU is still executing this one.`,
			`<strong style="color:var(--accent)">Sleep / Cap</strong> — Without a frame cap, a simple game loop will burn 100% CPU spinning at thousands of FPS. <code>time.sleep(max(0, target_time - elapsed))</code> yields the CPU to other processes. Many display APIs expose VSync — synchronizing swap_buffers to the monitor's refresh rate — which is the preferred method because it also eliminates tearing.`
		];
		function showLoop(i, el) {
			document.querySelectorAll('.loop-stage').forEach((s) => s.classList.remove('active'));
			el.classList.add('active');
			document.getElementById('loop-detail').innerHTML = loopDetails[i];
		}

		/* ══════════════════════════════════════ FRAME TIMELINE ══ */
		const tlC = document.getElementById('timeline-canvas');
		const tlX = tlC.getContext('2d');
		let tlHover = -1;
		const STAGE_COLORS = ['#22d3ee', '#fb923c', '#a3e635', '#e879f9', '#7dd3fc'];
		const STAGE_NAMES = ['Measure', 'Events', 'Update', 'Render', 'Sleep'];

		function drawTimeline() {
			const W = tlC.width,
				H = tlC.height;
			tlX.clearRect(0, 0, W, H);
			tlX.fillStyle = '#030810';
			tlX.fillRect(0, 0, W, H);
			const fps = parseInt(document.getElementById('tl-fps').value);
			const spikePct = parseInt(document.getElementById('tl-spike').value) / 100;
			document.getElementById('tl-fps-val').textContent = fps;
			document.getElementById('tl-spike-val').textContent = Math.round(spikePct * 100) + '%';

			const targetMs = 1000 / fps;
			const NUM_FRAMES = 24;
			const HEADER = 24,
				FOOTER = 20;
			const barH = H - HEADER - FOOTER;
			const barW = (W - 20) / NUM_FRAMES;
			const budgetPx = barH;

			// Budget line
			tlX.strokeStyle = '#1a3048';
			tlX.lineWidth = 1;
			tlX.beginPath();
			tlX.moveTo(10, HEADER);
			tlX.lineTo(W - 10, HEADER);
			tlX.stroke();
			tlX.font = '9px IBM Plex Mono';
			tlX.fillStyle = '#2e5068';
			tlX.textAlign = 'left';
			tlX.fillText(`budget: ${targetMs.toFixed(1)}ms`, 12, HEADER - 4);

			const stagePcts = [0.02, 0.05, 0.18, 0.6, 0.15];

			for (let f = 0; f < NUM_FRAMES; f++) {
				const isSpike = (f === 8 || f === 16) && spikePct > 0;
				const totalFactor = isSpike ? 1 + spikePct * 3 : 0.85 + Math.random() * 0.3;
				const x = 10 + f * barW;
				let yOff = H - FOOTER;
				const frameMs = targetMs * totalFactor;
				const overBudget = frameMs > targetMs;
				const totalPx = Math.min(barH * 1.8, barH * totalFactor);

				// Overflow indicator
				if (overBudget) {
					tlX.fillStyle = 'rgba(248,113,113,0.15)';
					tlX.fillRect(x + 1, HEADER, barW - 2, totalPx - barH);
				}

				stagePcts.forEach((pct, si) => {
					const h = totalPx * pct;
					tlX.fillStyle = tlHover === f ? STAGE_COLORS[si] : STAGE_COLORS[si] + '90';
					tlX.fillRect(x + 1, yOff - h, barW - 2, h - 1);
					yOff -= h;
				});

				if (tlHover === f) {
					tlX.strokeStyle = '#fff';
					tlX.lineWidth = 1;
					tlX.strokeRect(x + 0.5, yOff, barW - 2, totalPx - 1);
				}
				tlX.font = '8px IBM Plex Mono';
				tlX.fillStyle = '#2e5068';
				tlX.textAlign = 'center';
				tlX.fillText(f + 1, x + barW / 2, H - 4);
			}

			// Legend
			STAGE_NAMES.forEach((n, i) => {
				const lx = 12 + i * 80;
				tlX.fillStyle = STAGE_COLORS[i];
				tlX.fillRect(lx, HEADER + 6, 8, 8);
				tlX.fillStyle = '#2e5068';
				tlX.font = '9px IBM Plex Mono';
				tlX.textAlign = 'left';
				tlX.fillText(n, lx + 11, HEADER + 14);
			});
		}

		tlC.addEventListener('mousemove', (e) => {
			const r = tlC.getBoundingClientRect();
			const mx = ((e.clientX - r.left) / r.width) * tlC.width;
			const barW = (tlC.width - 20) / 24;
			const f = Math.floor((mx - 10) / barW);
			if (f !== tlHover) {
				tlHover = f >= 0 && f < 24 ? f : -1;
				drawTimeline();
			}
			if (tlHover >= 0) {
				const fps = parseInt(document.getElementById('tl-fps').value);
				document.getElementById('tl-hover').textContent =
					`Frame ${tlHover + 1}: budget ${(1000 / fps).toFixed(1)}ms — stages: ${STAGE_NAMES.join(', ')}`;
			}
		});
		tlC.addEventListener('mouseleave', () => {
			tlHover = -1;
			drawTimeline();
		});
		['tl-fps', 'tl-spike'].forEach((id) =>
			document.getElementById(id).addEventListener('input', drawTimeline)
		);
		drawTimeline();

		/* ══════════════════════════════════════ DELTA-TIME DEMO ══ */
		const dtC = document.getElementById('dt-canvas');
		const dtX = dtC.getContext('2d');
		let dtX_wrong = 0,
			dtX_right = 0,
			dtT = 0;
		const DT_SPEED = 120; // pixels per second

		function drawDt() {
			const W = dtC.width,
				H = dtC.height;
			const fps = parseInt(document.getElementById('dt-fps').value);
			document.getElementById('dt-fps-val').textContent = fps;
			const dt = 1 / fps;
			const perFrame = DT_SPEED / 60; // wrong: assumes 60fps

			dtT += dt;
			dtX_right += DT_SPEED * dt;
			dtX_wrong += perFrame;
			if (dtX_right > W - 20) {
				dtX_right = 0;
				dtX_wrong = 0;
				dtT = 0;
			}

			dtX.clearRect(0, 0, W, H);
			dtX.fillStyle = '#030810';
			dtX.fillRect(0, 0, W, H);

			// Grid lines
			dtX.strokeStyle = '#0c1520';
			dtX.lineWidth = 1;
			for (let x = 0; x < W; x += 60) {
				dtX.beginPath();
				dtX.moveTo(x, 0);
				dtX.lineTo(x, H);
				dtX.stroke();
			}

			// Reference marker (correct final position)
			const refX = W - 40;
			dtX.strokeStyle = '#1a3048';
			dtX.lineWidth = 1;
			dtX.setLineDash([4, 4]);
			dtX.beginPath();
			dtX.moveTo(refX, 0);
			dtX.lineTo(refX, H);
			dtX.stroke();
			dtX.setLineDash([]);
			dtX.font = '10px IBM Plex Mono';
			dtX.fillStyle = '#1a3048';
			dtX.textAlign = 'center';
			dtX.fillText('target', refX, 12);

			// Wrong object (red)
			const wy = H * 0.32;
			dtX.fillStyle = '#ef4444';
			dtX.font = '11px IBM Plex Mono';
			dtX.textAlign = 'left';
			dtX.fillText('WITHOUT dt (wrong)', 10, wy - 16);
			dtX.beginPath();
			dtX.arc(Math.min(dtX_wrong + 10, W - 10), wy, 10, 0, Math.PI * 2);
			dtX.fillStyle = '#ef4444';
			dtX.fill();
			dtX.strokeStyle = '#fff';
			dtX.lineWidth = 1.5;
			dtX.stroke();

			// Correct object (green)
			const cy2 = H * 0.72;
			dtX.fillStyle = '#a3e635';
			dtX.font = '11px IBM Plex Mono';
			dtX.textAlign = 'left';
			dtX.fillText('WITH dt (correct)', 10, cy2 - 16);
			dtX.beginPath();
			dtX.arc(Math.min(dtX_right + 10, W - 10), cy2, 10, 0, Math.PI * 2);
			dtX.fillStyle = '#a3e635';
			dtX.fill();
			dtX.strokeStyle = '#fff';
			dtX.lineWidth = 1.5;
			dtX.stroke();

			// Speeds
			const wrongSpeed = (perFrame * fps).toFixed(1);
			document.getElementById('dt-wrong-speed').textContent = wrongSpeed + ' px/s';
			document.getElementById('dt-right-speed').textContent = DT_SPEED.toFixed(1) + ' px/s';
		}

		let dtRaf = null;
		function dtLoop() {
			drawDt();
			dtRaf = requestAnimationFrame(dtLoop);
		}
		dtLoop();

		/* ══════════════════════════════════════ FIXED VS VARIABLE ══ */
		const fvvC = document.getElementById('fvv-canvas');
		const fvvX = fvvC.getContext('2d');
		const FIXED_DT = 1 / 60;
		let fvvT = 0;

		// Two simulated balls
		const fixedBall = { x: 0, y: 0, vy: 0, vy_hist: [] };
		const varBall = { x: 0, y: 0, vy: 0 };
		const GRAVITY = 400,
			BOUNCE_Y = 160;
		let fvvAcc = 0;
		const BALL_COLORS = { fixed: '#22d3ee', variable: '#fb923c' };

		function stepBall(ball, dt) {
			ball.vy += GRAVITY * dt;
			ball.y += ball.vy * dt;
			if (ball.y >= BOUNCE_Y) {
				ball.y = BOUNCE_Y;
				ball.vy *= -0.78;
			}
		}

		function drawFVV() {
			const W = fvvC.width,
				H = fvvC.height;
			const fps = parseInt(document.getElementById('fvv-fps').value);
			const spike = parseInt(document.getElementById('fvv-spike').value) / 100;
			document.getElementById('fvv-fps-val').textContent = fps;
			document.getElementById('fvv-spike-val').textContent = Math.round(spike * 100) + '%';
			const renderDt = 1 / fps;
			const actualDt = renderDt * (1 + spike * (Math.sin(fvvT * 1.3) > 0.7 ? 3 : 0));

			// Fixed step
			fvvAcc += actualDt;
			while (fvvAcc >= FIXED_DT) {
				stepBall(fixedBall, FIXED_DT);
				fvvAcc -= FIXED_DT;
			}
			const alpha = fvvAcc / FIXED_DT;

			// Variable step
			stepBall(varBall, Math.min(actualDt, 0.1));

			fvvX.clearRect(0, 0, W, H);
			fvvX.fillStyle = '#030810';
			fvvX.fillRect(0, 0, W, H);
			// Ground
			const gy = H - 40;
			fvvX.fillStyle = '#0c1520';
			fvvX.fillRect(0, gy, W, 40);
			fvvX.strokeStyle = '#1a3048';
			fvvX.lineWidth = 1;
			fvvX.beginPath();
			fvvX.moveTo(0, gy);
			fvvX.lineTo(W, gy);
			fvvX.stroke();

			const halfW = W / 2 - 20;
			// Labels
			[
				['FIXED TIMESTEP', 0, '#22d3ee'],
				['VARIABLE TIMESTEP', W / 2 + 20, '#fb923c']
			].forEach(([lbl, ox, col]) => {
				fvvX.font = '10px IBM Plex Mono';
				fvvX.fillStyle = col;
				fvvX.textAlign = 'center';
				fvvX.fillText(lbl, ox + halfW / 2, 16);
			});

			// Fixed ball
			const fbY = gy - 20 - fixedBall.y;
			fvvX.beginPath();
			fvvX.arc(halfW / 2, fbY, 14, 0, Math.PI * 2);
			fvvX.fillStyle = '#22d3ee40';
			fvvX.fill();
			fvvX.strokeStyle = '#22d3ee';
			fvvX.lineWidth = 2;
			fvvX.stroke();

			// Variable ball
			const vbX = W / 2 + 20 + halfW / 2;
			const vbY = gy - 20 - varBall.y;
			fvvX.beginPath();
			fvvX.arc(vbX, Math.max(20, vbY), 14, 0, Math.PI * 2);
			fvvX.fillStyle = '#fb923c40';
			fvvX.fill();
			fvvX.strokeStyle = '#fb923c';
			fvvX.lineWidth = 2;
			fvvX.stroke();

			// separator
			fvvX.strokeStyle = '#122030';
			fvvX.lineWidth = 1;
			fvvX.beginPath();
			fvvX.moveTo(W / 2, 0);
			fvvX.lineTo(W / 2, H);
			fvvX.stroke();

			document.getElementById('fvv-stats').innerHTML =
				`<span style="color:#2e5068">Fixed DT: <span style="color:#22d3ee">${FIXED_DT.toFixed(4)}s</span></span>` +
				`<span style="color:#2e5068">Accum: <span style="color:#22d3ee">${fvvAcc.toFixed(4)}s</span></span>` +
				`<span style="color:#2e5068">Render α: <span style="color:#22d3ee">${alpha.toFixed(3)}</span></span>` +
				`<span style="color:#2e5068">Actual dt: <span style="color:#fb923c">${actualDt.toFixed(4)}s</span></span>`;

			fvvT += actualDt;
		}
		let fvvRaf = null,
			fvvRunning = true;
		function fvvLoop() {
			if (!fvvRunning) return;
			drawFVV();
			fvvRaf = requestAnimationFrame(fvvLoop);
		}
		['fvv-fps', 'fvv-spike'].forEach((id) =>
			document.getElementById(id).addEventListener('input', drawFVV)
		);
		fvvLoop();

		/* ══════════════════════════════════════ INTERPOLATION PLAYGROUND ══ */
		const ipC = document.getElementById('interp-canvas');
		const ipX = ipC.getContext('2d');
		let ipMode = 'lerp';
		const ipA = { x: 80, y: 120 };
		const ipB = { x: 780, y: 80 };
		let ipDrag = null;

		const interpFns = {
			lerp: (t) => t,
			smoothstep: (t) => t * t * (3 - 2 * t),
			cosine: (t) => (1 - Math.cos(t * Math.PI)) / 2,
			step: (t) => (t < 0.5 ? 0 : 1)
		};
		const interpDesc = {
			lerp: 'Linear: constant velocity from A to B.',
			smoothstep: 'Smoothstep: slow start, fast middle, slow end. Classic for UI transitions.',
			cosine: 'Cosine: similar to smoothstep, derived from cos(). Slightly different curve shape.',
			step: 'Step: jumps immediately at t=0.5. No smooth transition — useful for binary state.'
		};

		function setInterpMode(m, btn) {
			ipMode = m;
			document.querySelectorAll('.demo-box .btn').forEach((b) => {
				if (['lerp', 'smoothstep', 'cosine', 'step'].includes(b.textContent))
					b.classList.remove('active');
			});
			btn.classList.add('active');
			drawInterp();
		}

		function drawInterp() {
			const W = ipC.width,
				H = ipC.height;
			const t = parseInt(document.getElementById('interp-t').value) / 100;
			document.getElementById('interp-t-val').textContent = t.toFixed(2);
			ipX.clearRect(0, 0, W, H);
			ipX.fillStyle = '#030810';
			ipX.fillRect(0, 0, W, H);

			// Grid
			ipX.strokeStyle = '#0c1520';
			ipX.lineWidth = 1;
			for (let x = 0; x < W; x += 80) {
				ipX.beginPath();
				ipX.moveTo(x, 0);
				ipX.lineTo(x, H);
				ipX.stroke();
			}
			for (let y = 0; y < H; y += 40) {
				ipX.beginPath();
				ipX.moveTo(0, y);
				ipX.lineTo(W, y);
				ipX.stroke();
			}

			const fn = interpFns[ipMode];
			const eased = fn(t);
			const px = ipA.x + (ipB.x - ipA.x) * eased;
			const py = ipA.y + (ipB.y - ipA.y) * eased;

			// Path trace
			ipX.beginPath();
			ipX.moveTo(ipA.x, ipA.y);
			for (let i = 0; i <= 100; i++) {
				const ti = i / 100,
					e = fn(ti);
				ipX.lineTo(ipA.x + (ipB.x - ipA.x) * e, ipA.y + (ipB.y - ipA.y) * e);
			}
			ipX.strokeStyle = '#1a3048';
			ipX.lineWidth = 1.5;
			ipX.stroke();

			// A and B
			[
				[ipA, 'A', '#22d3ee'],
				[ipB, 'B', '#fb923c']
			].forEach(([pt, lbl, col]) => {
				ipX.beginPath();
				ipX.arc(pt.x, pt.y, 9, 0, Math.PI * 2);
				ipX.fillStyle = col + '30';
				ipX.fill();
				ipX.strokeStyle = col;
				ipX.lineWidth = 2;
				ipX.stroke();
				ipX.font = '11px IBM Plex Mono';
				ipX.fillStyle = col;
				ipX.textAlign = 'center';
				ipX.fillText(lbl, pt.x, pt.y - 16);
			});

			// Connector line at current t
			ipX.beginPath();
			ipX.moveTo(ipA.x, ipA.y);
			ipX.lineTo(ipB.x, ipB.y);
			ipX.strokeStyle = '#1a3048';
			ipX.lineWidth = 1;
			ipX.setLineDash([3, 4]);
			ipX.stroke();
			ipX.setLineDash([]);

			// Current point
			ipX.beginPath();
			ipX.arc(px, py, 10, 0, Math.PI * 2);
			ipX.fillStyle = '#a3e63560';
			ipX.fill();
			ipX.strokeStyle = '#a3e635';
			ipX.lineWidth = 2;
			ipX.stroke();

			// t and eased labels
			ipX.font = '11px IBM Plex Mono';
			ipX.textAlign = 'left';
			ipX.fillStyle = '#a3e635';
			ipX.fillText(`t=${t.toFixed(2)}  eased=${eased.toFixed(3)}`, px + 14, py - 6);

			document.getElementById('interp-info').textContent = interpDesc[ipMode];
		}

		ipC.addEventListener('pointerdown', (e) => {
			const r = ipC.getBoundingClientRect();
			const mx = ((e.clientX - r.left) / r.width) * ipC.width,
				my = ((e.clientY - r.top) / r.height) * ipC.height;
			if (Math.hypot(ipA.x - mx, ipA.y - my) < 20) {
				ipDrag = 'A';
				e.preventDefault();
			} else if (Math.hypot(ipB.x - mx, ipB.y - my) < 20) {
				ipDrag = 'B';
				e.preventDefault();
			}
		});
		ipC.addEventListener('pointermove', (e) => {
			if (!ipDrag) return;
			const r = ipC.getBoundingClientRect();
			const mx = ((e.clientX - r.left) / r.width) * ipC.width,
				my = ((e.clientY - r.top) / r.height) * ipC.height;
			if (ipDrag === 'A') {
				ipA.x = mx;
				ipA.y = my;
			} else {
				ipB.x = mx;
				ipB.y = my;
			}
			drawInterp();
			e.preventDefault();
		});
		ipC.addEventListener('pointerup', () => {
			ipDrag = null;
		});
		document.getElementById('interp-t').addEventListener('input', drawInterp);
		drawInterp();

		/* ══════════════════════════════════════ EASING GALLERY ══ */
		const easingFns = {
			linear: { fn: (t) => t, code: 'def linear(t):\n    return t' },
			ease_in_quad: { fn: (t) => t * t, code: 'def ease_in_quad(t):\n    return t * t' },
			ease_out_quad: {
				fn: (t) => 1 - (1 - t) ** 2,
				code: 'def ease_out_quad(t):\n    return 1 - (1-t)**2'
			},
			ease_in_out_quad: {
				fn: (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2),
				code: 'def ease_in_out_quad(t):\n    if t < 0.5: return 2*t*t\n    return 1 - (-2*t+2)**2/2'
			},
			ease_in_cubic: { fn: (t) => t ** 3, code: 'def ease_in_cubic(t):\n    return t**3' },
			ease_out_cubic: {
				fn: (t) => 1 - (1 - t) ** 3,
				code: 'def ease_out_cubic(t):\n    return 1 - (1-t)**3'
			},
			ease_in_out_cubic: {
				fn: (t) => (t < 0.5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2),
				code: 'def ease_in_out_cubic(t):\n    if t < 0.5: return 4*t**3\n    return 1 - (-2*t+2)**3/2'
			},
			ease_out_elastic: {
				fn: (t) => {
					if (t === 0 || t === 1) return t;
					const c4 = (2 * Math.PI) / 3;
					return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
				},
				code: 'def ease_out_elastic(t):\n    c4 = (2*pi)/3\n    if t==0 or t==1: return t\n    return 2**(-10*t)*sin((t*10-0.75)*c4)+1'
			},
			ease_out_bounce: {
				fn: (t) => {
					const n1 = 7.5625,
						d1 = 2.75;
					if (t < 1 / d1) return n1 * t * t;
					else if (t < 2 / d1) {
						t -= 1.5 / d1;
						return n1 * t * t + 0.75;
					} else if (t < 2.5 / d1) {
						t -= 2.25 / d1;
						return n1 * t * t + 0.9375;
					} else {
						t -= 2.625 / d1;
						return n1 * t * t + 0.984375;
					}
				},
				code: 'def ease_out_bounce(t):\n    n1,d1 = 7.5625, 2.75\n    if t<1/d1:  return n1*t*t\n    elif t<2/d1:   t-=1.5/d1;  return n1*t*t+0.75\n    elif t<2.5/d1: t-=2.25/d1; return n1*t*t+0.9375\n    else:          t-=2.625/d1;return n1*t*t+0.984375'
			},
			ease_in_back: {
				fn: (t) => {
					const c1 = 1.70158,
						c3 = c1 + 1;
					return c3 * t ** 3 - c1 * t ** 2;
				},
				code: 'def ease_in_back(t):\n    c1,c3 = 1.70158, 1.70158+1\n    return c3*t**3 - c1*t**2'
			},
			ease_out_back: {
				fn: (t) => {
					const c1 = 1.70158,
						c3 = c1 + 1;
					return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2;
				},
				code: 'def ease_out_back(t):\n    c1,c3 = 1.70158, 1.70158+1\n    return 1+c3*(t-1)**3+c1*(t-1)**2'
			},
			smoothstep: {
				fn: (t) => t * t * (3 - 2 * t),
				code: 'def smoothstep(t):\n    return t*t*(3-2*t)'
			}
		};

		let selEase = 'ease_out_quad';
		let easeAnimT = 0,
			easeAnimRunning = true;

		function buildEasingGrid() {
			const grid = document.getElementById('easing-grid');
			grid.innerHTML = '';
			Object.entries(easingFns).forEach(([name, { fn }]) => {
				const card = document.createElement('div');
				card.className = 'ease-card' + (name === selEase ? ' active' : '');
				const c = document.createElement('canvas');
				c.width = 80;
				c.height = 60;
				const cx = c.getContext('2d');
				cx.fillStyle = '#030810';
				cx.fillRect(0, 0, 80, 60);
				cx.beginPath();
				cx.moveTo(4, 56);
				for (let i = 0; i <= 80; i++) {
					const t = i / 80;
					cx.lineTo(4 + t * 72, 56 - fn(t) * 52);
				}
				cx.strokeStyle = name === selEase ? '#fb923c' : '#22d3ee';
				cx.lineWidth = 1.5;
				cx.stroke();
				const lbl = document.createElement('div');
				lbl.className = 'ease-label';
				lbl.textContent = name.replace(/_/g, ' ');
				card.appendChild(c);
				card.appendChild(lbl);
				card.onclick = () => {
					selEase = name;
					buildEasingGrid();
					drawEaseCurve();
				};
				grid.appendChild(card);
			});
		}

		const ecC = document.getElementById('ease-curve-canvas');
		const ecX = ecC.getContext('2d');
		const emC = document.getElementById('ease-motion-canvas');
		const emX = emC.getContext('2d');

		function drawEaseCurve() {
			const W = ecC.width,
				H = ecC.height,
				fn = easingFns[selEase].fn;
			ecX.clearRect(0, 0, W, H);
			ecX.fillStyle = '#030810';
			ecX.fillRect(0, 0, W, H);

			// Grid
			ecX.strokeStyle = '#0c1520';
			ecX.lineWidth = 1;
			for (let i = 0; i <= 4; i++) {
				const x = 20 + (i * (W - 40)) / 4,
					y = 20 + (i * (H - 40)) / 4;
				ecX.beginPath();
				ecX.moveTo(x, 20);
				ecX.lineTo(x, H - 20);
				ecX.stroke();
				ecX.beginPath();
				ecX.moveTo(20, y);
				ecX.lineTo(W - 20, y);
				ecX.stroke();
			}

			// Axes labels
			ecX.font = '9px IBM Plex Mono';
			ecX.fillStyle = '#2e5068';
			ecX.textAlign = 'center';
			ecX.fillText('t=0', 20, H - 6);
			ecX.fillText('t=1', W - 20, H - 6);
			ecX.fillText('0', 8, H - 20);
			ecX.fillText('1', 8, 24);

			// Curve
			ecX.beginPath();
			ecX.moveTo(20, H - 20);
			for (let i = 0; i <= 100; i++) {
				const t = i / 100,
					v = fn(t);
				ecX.lineTo(20 + t * (W - 40), H - 20 - v * (H - 40));
			}
			ecX.strokeStyle = '#fb923c';
			ecX.lineWidth = 2;
			ecX.stroke();

			// Current t indicator
			const t = Math.sin(easeAnimT * 1.5) * 0.5 + 0.5;
			const v = fn(t);
			const cx2 = 20 + t * (W - 40),
				cy2 = H - 20 - v * (H - 40);
			ecX.beginPath();
			ecX.arc(cx2, cy2, 5, 0, Math.PI * 2);
			ecX.fillStyle = '#a3e635';
			ecX.fill();

			document.getElementById('ease-code').textContent = easingFns[selEase].code;
		}

		function drawEaseMotion() {
			const W = emC.width,
				H = emC.height,
				fn = easingFns[selEase].fn;
			emX.clearRect(0, 0, W, H);
			emX.fillStyle = '#030810';
			emX.fillRect(0, 0, W, H);

			const t = Math.sin(easeAnimT * 1.5) * 0.5 + 0.5;
			const eased = fn(t);

			// Linear reference
			const lx = 20 + t * (W - 40);
			emX.beginPath();
			emX.arc(lx, H * 0.3, 10, 0, Math.PI * 2);
			emX.fillStyle = '#22d3ee30';
			emX.fill();
			emX.strokeStyle = '#22d3ee';
			emX.lineWidth = 1.5;
			emX.stroke();
			emX.font = '10px IBM Plex Mono';
			emX.fillStyle = '#22d3ee';
			emX.textAlign = 'center';
			emX.fillText('linear', lx, H * 0.3 - 18);

			// Eased
			const ex = 20 + eased * (W - 40);
			emX.beginPath();
			emX.arc(ex, H * 0.7, 10, 0, Math.PI * 2);
			emX.fillStyle = '#fb923c30';
			emX.fill();
			emX.strokeStyle = '#fb923c';
			emX.lineWidth = 1.5;
			emX.stroke();
			emX.font = '10px IBM Plex Mono';
			emX.fillStyle = '#fb923c';
			emX.textAlign = 'center';
			emX.fillText(selEase.replace(/_/g, ' '), ex, H * 0.7 - 18);

			// Tracks
			[
				[H * 0.3, '#22d3ee'],
				[H * 0.7, '#fb923c']
			].forEach(([y, col]) => {
				emX.beginPath();
				emX.moveTo(20, y);
				emX.lineTo(W - 20, y);
				emX.strokeStyle = col + '30';
				emX.lineWidth = 1;
				emX.stroke();
				emX.beginPath();
				emX.arc(20, y, 4, 0, Math.PI * 2);
				emX.fillStyle = col;
				emX.fill();
				emX.beginPath();
				emX.arc(W - 20, y, 4, 0, Math.PI * 2);
				emX.fillStyle = col;
				emX.fill();
			});
		}

		function easeAnimLoop() {
			easeAnimT += 0.016;
			drawEaseCurve();
			drawEaseMotion();
			requestAnimationFrame(easeAnimLoop);
		}
		buildEasingGrid();
		easeAnimLoop();

		/* ══════════════════════════════════════ FULL DEMO SCENE ══ */
		const flC = document.getElementById('full-canvas');
		const flX = flC.getContext('2d');
		let flRunning = true,
			flT = 0,
			flRAF = null;

		const easeFns = {
			ease_out_bounce: easingFns['ease_out_bounce'].fn,
			ease_out_elastic: easingFns['ease_out_elastic'].fn,
			ease_in_out_cubic: easingFns['ease_in_out_cubic'].fn
		};

		const flEntities = [
			{
				label: 'Character',
				x: 80,
				vx: 80,
				y: 200,
				vy: 0,
				frame: 0,
				ft: 0,
				fps: 8,
				color: '#22d3ee'
			},
			{ label: 'Coin', x: 400, vx: 0, y: 100, vy: 0, baseY: 100, color: '#fbbf24', floatT: 0 },
			{
				label: 'UI Panel',
				x: -200,
				y: 20,
				targetX: 20,
				tweenT: 0,
				tweenDur: 0.8,
				color: '#e879f9'
			}
		];

		function toggleFull() {
			flRunning = !flRunning;
			document.getElementById('full-play-btn').textContent = flRunning ? '⏸ Pause' : '▶ Play';
			if (flRunning) fullLoop();
		}
		function resetFull() {
			flT = 0;
			flEntities[0].x = 80;
			flEntities[2].x = -200;
			flEntities[2].tweenT = 0;
		}

		function drawFull() {
			const W = flC.width,
				H = flC.height;
			const fps = parseInt(document.getElementById('full-fps').value);
			document.getElementById('full-fps-val').textContent = fps;
			const dt = 1 / fps;
			flT += dt;

			flX.clearRect(0, 0, W, H);
			flX.fillStyle = '#030810';
			flX.fillRect(0, 0, W, H);
			// Ground
			flX.fillStyle = '#0c1520';
			flX.fillRect(0, H - 40, W, 40);
			flX.strokeStyle = '#122030';
			flX.lineWidth = 1;
			flX.beginPath();
			flX.moveTo(0, H - 40);
			flX.lineTo(W, H - 40);
			flX.stroke();

			// Character — delta-time movement
			const ch = flEntities[0];
			ch.x += ch.vx * dt;
			if (ch.x > W + 30) ch.x = -30;
			ch.ft += dt;
			if (ch.ft > 1 / ch.fps) {
				ch.frame = (ch.frame + 1) % 4;
				ch.ft = 0;
			}

			// Draw character (simple animated figure)
			const cx2 = ch.x,
				cy2 = H - 60;
			flX.fillStyle = ch.color + '40';
			// body
			flX.beginPath();
			flX.arc(cx2, cy2 - 10, 12, 0, Math.PI * 2);
			flX.fillStyle = ch.color + '30';
			flX.fill();
			flX.strokeStyle = ch.color;
			flX.lineWidth = 2;
			flX.stroke();
			// legs
			const legOff = Math.sin((ch.frame * Math.PI) / 2) * 8;
			flX.beginPath();
			flX.moveTo(cx2, cy2 + 2);
			flX.lineTo(cx2 - legOff, cy2 + 20);
			flX.stroke();
			flX.beginPath();
			flX.moveTo(cx2, cy2 + 2);
			flX.lineTo(cx2 + legOff, cy2 + 20);
			flX.stroke();
			flX.font = '9px IBM Plex Mono';
			flX.fillStyle = ch.color;
			flX.textAlign = 'center';
			flX.fillText(`dt×${ch.vx}px/s`, cx2, cy2 - 30);

			// Coin — eased floating
			const coin = flEntities[1];
			coin.floatT += dt;
			const floatY =
				coin.baseY +
				easingFns['ease_out_elastic'].fn(Math.abs(Math.sin(coin.floatT * 1.2))) * 20 -
				10;
			const coinR = 14;
			flX.beginPath();
			flX.arc(400, floatY, coinR, 0, Math.PI * 2);
			flX.fillStyle = '#fbbf2440';
			flX.fill();
			flX.strokeStyle = '#fbbf24';
			flX.lineWidth = 2;
			flX.stroke();
			flX.font = '10px IBM Plex Mono';
			flX.fillStyle = '#fbbf24';
			flX.textAlign = 'center';
			flX.fillText('elastic float', 400, floatY - 26);

			// UI Panel — eased tween
			const panel = flEntities[2];
			panel.tweenT = Math.min(panel.tweenT + dt, panel.tweenDur);
			if (panel.tweenT >= panel.tweenDur && panel.targetX === 20 && !panel.timeoutScheduled) {
				panel.timeoutScheduled = true;
				setTimeout(() => {
					panel.tweenT = 0;
					panel.targetX = panel.targetX === 20 ? -200 : 20;
					panel.timeoutScheduled = false;
				}, 2000);
			}
			const raw = panel.tweenT / panel.tweenDur;
			const eased =
				panel.targetX === 20
					? easingFns['ease_out_cubic'].fn(raw)
					: 1 - easingFns['ease_in_out_cubic'].fn(raw);
			panel.x = panel.targetX === 20 ? -200 + (20 - -200) * eased : 20 + (-200 - 20) * (1 - eased);
			// Draw panel
			flX.fillStyle = '#e879f920';
			flX.strokeStyle = '#e879f9';
			flX.lineWidth = 1.5;
			flX.fillRect(panel.x, panel.y, 130, 60);
			flX.strokeRect(panel.x, panel.y, 130, 60);
			flX.font = '10px IBM Plex Mono';
			flX.fillStyle = '#e879f9';
			flX.textAlign = 'left';
			flX.fillText('ease_out_cubic', panel.x + 8, panel.y + 20);
			flX.fillText(`tween=${raw.toFixed(2)}`, panel.x + 8, panel.y + 36);
			flX.fillText('UI PANEL', panel.x + 8, panel.y + 52);

			// Stats
			document.getElementById('full-stats').innerHTML =
				`<div style="font-size:11px;color:var(--muted)">frame<br><span style="color:var(--accent)">${Math.round(flT * fps)}</span></div>` +
				`<div style="font-size:11px;color:var(--muted)">elapsed<br><span style="color:var(--accent)">${flT.toFixed(2)}s</span></div>` +
				`<div style="font-size:11px;color:var(--muted)">dt<br><span style="color:var(--accent3)">${(1000 / fps).toFixed(1)}ms</span></div>` +
				`<div style="font-size:11px;color:var(--muted)">char.x<br><span style="color:var(--accent2)">${Math.round(ch.x)}</span></div>`;
		}
		function fullLoop() {
			if (!flRunning) return;
			drawFull();
			flRAF = requestAnimationFrame(fullLoop);
		}
		document.getElementById('full-fps').addEventListener('input', () => {
			document.getElementById('full-fps-val').textContent =
				document.getElementById('full-fps').value;
		});
		drawFull();
		fullLoop();

		/* ══════════════════════════════════════ ASSESSMENT ══ */
		const assessData = [
			{
				title: 'Problem 1 · Frame index calculation',
				table: [
					['FPS (animation)', 'num_frames', 'elapsed time'],
					['8', '6', '0.75 s']
				],
				q: 'Using the formula: frame = floor(elapsed × fps) % num_frames, which frame is displayed?',
				options: ['Frame 0', 'Frame 1', 'Frame 4', 'Frame 6 (out of range)'],
				correct: 2,
				explanation:
					'floor(0.75 × 8) % 6 = floor(6.0) % 6 = 6 % 6 = 0... wait: floor(6.0)=6, 6%6=0. Actually the answer is Frame 0. Let me recheck: 0.75×8=6.0, floor(6.0)=6, 6%6=0 → Frame 0. But the expected answer 4 would be at t=0.75 with fps=6: 0.75×6=4.5→4%6=4. The problem states fps=8, frames=6: 0.75×8=6→6%6=0. Showing Frame 0 is correct.'
			},
			{
				title: 'Problem 2 · Delta-time independence',
				table: [
					['speed (units/s)', 'FPS', 'delta_time (s)'],
					['200', '30', '0.0333']
				],
				q: 'How far does the object move in one frame, using delta-time correctly?',
				options: ['200 units', '6.67 units', '0.0333 units', '30 units'],
				correct: 1,
				explanation:
					'distance_per_frame = speed × dt = 200 × 0.0333 = 6.67 units. Over 30 frames (one second) this totals exactly 200 units — matching the stated speed regardless of FPS.'
			},
			{
				title: 'Problem 3 · Fixed timestep accumulator',
				table: [
					['FIXED_DT', 'accumulated time before frame'],
					['0.01667 s (60 Hz)', '0.04 s']
				],
				q: 'How many physics steps fire this frame, and what is the leftover accumulator?',
				options: [
					'1 step, 0.023 s remaining',
					'2 steps, 0.0067 s remaining',
					'3 steps, 0.00001 s remaining',
					'2 steps, 0.00001 s remaining'
				],
				correct: 1,
				explanation:
					'steps = floor(0.04 / 0.01667) = floor(2.4) = 2 steps. Remainder = 0.04 − 2×0.01667 = 0.04 − 0.03334 = 0.00666 s. The interpolation alpha = 0.00666 / 0.01667 ≈ 0.40.'
			},
			{
				title: 'Problem 4 · Delta-time cap',
				table: [
					['actual elapsed (frozen OS)', 'MAX_DT cap'],
					['2.4 s', '0.1 s']
				],
				q: 'What delta_time is passed to the update function after capping?',
				options: ['2.4 s', '0.1 s', '1.0 s', '0.016 s'],
				correct: 1,
				explanation:
					'delta_time = min(actual, MAX_DT) = min(2.4, 0.1) = 0.1 s. Without this cap, a 2.4 s pause would cause the physics simulation to jump forward 2.4 seconds in one frame, tunnelling through collisions and teleporting objects.'
			},
			{
				title: 'Problem 5 · Easing value',
				table: [
					['easing function', 't'],
					['ease_in_quad (t²)', '0.4']
				],
				q: 'What is the eased value? What does this mean for movement at t=0.4?',
				options: [
					'eased = 0.4 — linear, halfway to 40% progress',
					'eased = 0.16 — only 16% of the way, still accelerating',
					'eased = 0.64 — already 64% of the way, decelerating',
					'eased = 0.8 — just past the midpoint'
				],
				correct: 1,
				explanation:
					'ease_in_quad(0.4) = 0.4² = 0.16. At 40% through time, the object has only covered 16% of the distance. This is the characteristic of ease-in: slow start, the curve is below the linear diagonal, acceleration is still building. At t=1.0 it would reach 1.0² = 1.0 (full distance).'
			}
		];

		let assessAnswered = 0,
			assessCorrect = 0;
		function buildAssess() {
			const c = document.getElementById('assess-container');
			c.innerHTML = '';
			assessData.forEach((p, pi) => {
				const div = document.createElement('div');
				div.className = 'timing-problem';
				let tableHtml =
					'<table class="tp-table"><thead><tr>' +
					p.table[0].map((h) => `<th>${h}</th>`).join('') +
					'</tr></thead><tbody>';
				p.table.slice(1).forEach((row) => {
					tableHtml += '<tr>' + row.map((c2) => `<td>${c2}</td>`).join('') + '</tr>';
				});
				tableHtml += '</tbody></table>';
				div.innerHTML =
					`<div class="tp-header">Question ${pi + 1} · ${p.title}</div>${tableHtml}` +
					`<div class="tp-q">${p.q}</div>` +
					`<div class="tp-options" id="tp-opts-${pi}">${p.options.map((o, oi) => `<div class="tp-option" onclick="assessAnswer(${pi},${oi})" id="tp-opt-${pi}-${oi}">${o}</div>`).join('')}</div>` +
					`<div class="tp-feedback" id="tp-fb-${pi}"></div>`;
				c.appendChild(div);
			});
		}

		function assessAnswer(pi, oi) {
			const p = assessData[pi];
			document
				.querySelectorAll(`#tp-opts-${pi} .tp-option`)
				.forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById(`tp-fb-${pi}`);
			if (oi === p.correct) {
				document.getElementById(`tp-opt-${pi}-${oi}`).classList.add('correct');
				fb.textContent = '✓ ' + p.explanation;
				fb.className = 'tp-feedback ok';
				assessCorrect++;
			} else {
				document.getElementById(`tp-opt-${pi}-${oi}`).classList.add('wrong');
				document.getElementById(`tp-opt-${pi}-${p.correct}`).classList.add('correct');
				fb.textContent = '✗ ' + p.explanation;
				fb.className = 'tp-feedback bad';
			}
			assessAnswered++;
			if (assessAnswered === assessData.length) {
				const s = document.getElementById('assess-score');
				s.style.display = 'block';
				document.getElementById('assess-score-num').textContent =
					`${assessCorrect}/${assessData.length}`;
				s.style.borderColor =
					assessCorrect === assessData.length
						? 'var(--accent)'
						: assessCorrect >= 3
							? 'var(--accent3)'
							: 'var(--accent4)';
			}
		}
		/* fix assessment answer 0 */
		assessData[0].correct = 0;
		assessData[0].options = ['Frame 0', 'Frame 1', 'Frame 4', 'Frame 2'];
		assessData[0].explanation =
			'floor(0.75 × 8) % 6 = floor(6.0) % 6 = 6 % 6 = 0 → Frame 0. The elapsed time times the fps gives exactly 6 "frame-ticks" — which wraps to 0 in a 6-frame cycle. This is why sprite cycles that divide evenly can briefly reset to frame 0 at exact integer multiples of the cycle duration.';

		buildAssess();

		window.addEventListener('scroll', () => {
			document.getElementById('reading-progress').style.width =
				Math.min(100, (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100) +
				'%';
		});

		if (typeof buildEasingGrid === 'function') window.buildEasingGrid = buildEasingGrid;
		if (typeof buildAssess === 'function') window.buildAssess = buildAssess;
		if (typeof setInterpMode === 'function') window.setInterpMode = setInterpMode;
		if (typeof easeAnimLoop === 'function') window.easeAnimLoop = easeAnimLoop;
		if (typeof drawInterp === 'function') window.drawInterp = drawInterp;
		if (typeof toggleFull === 'function') window.toggleFull = toggleFull;
		if (typeof dtLoop === 'function') window.dtLoop = dtLoop;
		if (typeof drawFull === 'function') window.drawFull = drawFull;
		if (typeof drawTimeline === 'function') window.drawTimeline = drawTimeline;
		if (typeof fullLoop === 'function') window.fullLoop = fullLoop;
		if (typeof assessAnswer === 'function') window.assessAnswer = assessAnswer;
		if (typeof drawEaseCurve === 'function') window.drawEaseCurve = drawEaseCurve;
		if (typeof showLoop === 'function') window.showLoop = showLoop;
		if (typeof drawEaseMotion === 'function') window.drawEaseMotion = drawEaseMotion;
		if (typeof resetFull === 'function') window.resetFull = resetFull;
		if (typeof drawFVV === 'function') window.drawFVV = drawFVV;
		if (typeof drawDt === 'function') window.drawDt = drawDt;
		if (typeof fvvLoop === 'function') window.fvvLoop = fvvLoop;
		if (typeof stepBall === 'function') window.stepBall = stepBall;

		return () => {
			if (typeof dtRaf !== 'undefined' && dtRaf) cancelAnimationFrame(dtRaf);
			if (typeof flRAF !== 'undefined' && flRAF) cancelAnimationFrame(flRAF);
			if (typeof fvvRaf !== 'undefined' && fvvRaf) cancelAnimationFrame(fvvRaf);
			// Note: window event listeners use anonymous functions and cannot be auto-removed.
			// Consider refactoring to named handlers for proper cleanup.
		};
	});
</script>

<div class="page-wrapper">
	<header class="course-header">
		<div>
			<div class="course-label">Game Development Fundamentals</div>
			<div class="course-title">From Pixels to Play</div>
		</div>
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 07 of 12</div>
	</header>

	<div class="module-hero">
		<div class="module-number">07</div>
		<div class="module-tag">Module 07 · Theory + Practice</div>
		<h1 class="module-title">Time and<br /><span>Animation</span></h1>
		<div class="progress-bar-wrap">
			<div class="progress-bar-fill" id="reading-progress"></div>
		</div>
	</div>

	<nav class="toc">
		<div class="toc-label">Contents</div>
		<ul class="toc-list">
			<li><a href="#objectives">Objectives</a></li>
			<li><a href="#game-loop">The Game Loop</a></li>
			<li><a href="#delta-time">Delta-Time</a></li>
			<li><a href="#timestep">Fixed vs Variable Timestep</a></li>
			<li><a href="#interpolation">Interpolation</a></li>
			<li><a href="#easing">Easing Functions</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand the structure and responsibilities of a game loop</li>
			<li>Use delta-time correctly to make movement frame-rate independent</li>
			<li>Explain the trade-offs between fixed and variable timestep</li>
			<li>Implement lerp, smoothstep, and common easing functions</li>
			<li>Animate sprite cycles and smooth state transitions</li>
		</ul>
	</section>

	<!-- ══ 07.01 GAME LOOP ══ -->
	<section id="game-loop" class="section">
		<div class="section-header">
			<span class="section-num">07.01</span>
			<h2 class="section-title">The Game Loop</h2>
		</div>

		<p>
			Every game runs inside an infinite loop that repeats until the player quits. Each iteration of
			the loop is one <strong>frame</strong>. The loop has a fixed structure: process input, update
			the world, render the result. Understanding this structure — and how time threads through it —
			is foundational to everything that follows.
		</p>

		<!-- LOOP DIAGRAM -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Game Loop Anatomy</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Click any stage to see what happens there and why the order matters.
				</p>
				<div class="loop-diagram" id="loop-diagram">
					<div
						class="loop-stage"
						tabindex="0"
						role="button"
						onclick={(e) => {
							window.showLoop(0, e.currentTarget);
						}}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.showLoop(0, e.currentTarget);
							}
						}}
					>
						<div class="loop-num">1</div>
						<div class="loop-name">
							<div class="loop-name-main">Measure Time</div>
							<div class="loop-name-sub">clock / delta</div>
						</div>
						<div class="loop-desc">
							Sample the system clock. Compute delta_time = now − last_frame_time.
						</div>
					</div>
					<div
						class="loop-stage"
						tabindex="0"
						role="button"
						onclick={(e) => {
							window.showLoop(1, e.currentTarget);
						}}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.showLoop(1, e.currentTarget);
							}
						}}
					>
						<div class="loop-num">2</div>
						<div class="loop-name">
							<div class="loop-name-main">Process Events</div>
							<div class="loop-name-sub">input / OS events</div>
						</div>
						<div class="loop-desc">
							Drain the OS event queue — keyboard, mouse, window resize, quit signals.
						</div>
					</div>
					<div
						class="loop-stage"
						tabindex="0"
						role="button"
						onclick={(e) => {
							window.showLoop(2, e.currentTarget);
						}}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.showLoop(2, e.currentTarget);
							}
						}}
					>
						<div class="loop-num">3</div>
						<div class="loop-name">
							<div class="loop-name-main">Update</div>
							<div class="loop-name-sub">physics / logic / AI</div>
						</div>
						<div class="loop-desc">
							Advance every system by delta_time: physics, animations, AI, timers.
						</div>
					</div>
					<div
						class="loop-stage"
						tabindex="0"
						role="button"
						onclick={(e) => {
							window.showLoop(3, e.currentTarget);
						}}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.showLoop(3, e.currentTarget);
							}
						}}
					>
						<div class="loop-num">4</div>
						<div class="loop-name">
							<div class="loop-name-main">Render</div>
							<div class="loop-name-sub">draw calls / GPU</div>
						</div>
						<div class="loop-desc">
							Clear the framebuffer, issue draw calls for every visible object, swap buffers.
						</div>
					</div>
					<div
						class="loop-stage"
						tabindex="0"
						role="button"
						onclick={(e) => {
							window.showLoop(4, e.currentTarget);
						}}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.showLoop(4, e.currentTarget);
							}
						}}
					>
						<div class="loop-num">5</div>
						<div class="loop-name">
							<div class="loop-name-main">Sleep / Cap</div>
							<div class="loop-name-sub">frame limiter</div>
						</div>
						<div class="loop-desc">
							Optionally sleep until the next target frame time to cap FPS and reduce CPU load.
						</div>
					</div>
				</div>
				<div class="loop-detail" id="loop-detail">Select a stage for a detailed explanation.</div>
			</div>
		</div>

		<pre><code
				><span class="kw">import</span> time

<span class="fn">last_time</span> = time.<span class="fn">perf_counter</span>()

<span class="kw">while</span> running:
    <span class="cm"># 1. Measure time</span>
    now        = time.<span class="fn">perf_counter</span>()
    delta_time = now - last_time
    last_time  = now

    <span class="cm"># 2. Process events</span>
    <span class="kw">for</span> event <span class="kw">in</span> window.<span class="fn"
					>events</span
				>():
        <span class="kw">if</span> event == <span class="str">'quit'</span>: running = <span
					class="kw">False</span
				>

    <span class="cm"># 3. Update world</span>
    player.<span class="fn">update</span>(delta_time)
    physics.<span class="fn">step</span>(delta_time)
    animations.<span class="fn">update</span>(delta_time)

    <span class="cm"># 4. Render</span>
    ctx.<span class="fn">clear</span>()
    renderer.<span class="fn">draw_all</span>()
    window.<span class="fn">swap_buffers</span>()
<span class="lang-tag">python</span></code
			></pre>

		<!-- FRAME TIMELINE VISUALIZER -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Animated · Frame Timeline</div>
				<span class="demo-badge a">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Each bar is one frame, subdivided by stage. Hover a bar to see the exact timings. Drag the
					"heavy frame" slider to simulate a spike.
				</p>
				<div class="slider-row" style="margin-bottom: 0.75rem">
					<label>Target FPS</label>
					<input type="range" id="tl-fps" min="10" max="120" value="60" />
					<span class="slider-val" id="tl-fps-val">60</span>
				</div>
				<div class="slider-row" style="margin-bottom: 0.75rem">
					<label>Heavy frame</label>
					<input type="range" id="tl-spike" min="0" max="100" value="0" />
					<span class="slider-val" id="tl-spike-val">0%</span>
				</div>
				<canvas id="timeline-canvas" width="860" height="180" style="width: 100%"></canvas>
				<div
					id="tl-hover"
					style="font-size: 12px; color: var(--muted); margin-top: 0.6rem; min-height: 1.4em"
				></div>
			</div>
		</div>

		<p>
			The time budget per frame is simply <code>1 / target_fps</code>. At 60 FPS you have roughly
			16.6 ms per frame. At 30 FPS, 33.3 ms. If any stage — usually physics or rendering — takes
			longer than the budget, the frame misses its deadline and the player perceives a stutter or
			dropped frame.
		</p>
	</section>

	<!-- ══ 07.02 DELTA-TIME ══ -->
	<section id="delta-time" class="section">
		<div class="section-header">
			<span class="section-num">07.02</span>
			<h2 class="section-title">Delta-Time: Frame-Rate Independence</h2>
		</div>

		<p>
			<strong>Delta-time</strong> (dt) is the elapsed time in seconds since the last frame. It is the
			most important number in your game loop. Every quantity that changes over time — position, velocity,
			animation progress, timer countdown — must be multiplied by dt to become frame-rate independent.
		</p>

		<pre><code
				><span class="cm"># WRONG — speed depends on frame rate</span>
player.x += speed            <span class="cm"># moves 'speed' pixels per FRAME</span>
                             <span class="cm"># at 30 FPS: 30 * speed per second</span>
                             <span class="cm"># at 120 FPS: 120 * speed per second</span>

<span class="cm"># CORRECT — speed is independent of frame rate</span>
player.x += speed * delta_time   <span class="cm"># moves 'speed' pixels per SECOND</span>
                                 <span class="cm"># identical regardless of FPS</span>
<span class="lang-tag">python</span></code
			></pre>

		<!-- DELTA-TIME DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Frame-Rate Independence</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Two objects move at the same <em>intended</em> speed. One uses delta-time; the other does not.
					Change the simulated FPS to see them diverge.
				</p>
				<div class="slider-row" style="margin-bottom: 1rem">
					<label>Sim FPS</label>
					<input type="range" id="dt-fps" min="5" max="120" value="60" />
					<span class="slider-val" id="dt-fps-val">60</span>
				</div>
				<canvas id="dt-canvas" width="860" height="180" style="width: 100%"></canvas>
				<div class="two-col" style="margin-top: 1rem">
					<div class="info-panel">
						<div class="info-row">
							<span class="info-key">Speed setting</span><span class="info-val">120 px/s</span>
						</div>
						<div class="info-row">
							<span class="info-key">Without dt (wrong)</span><span
								class="info-val"
								id="dt-wrong-speed">— px/s</span
							>
						</div>
						<div class="info-row">
							<span class="info-key">With dt (correct)</span><span
								class="info-val"
								id="dt-right-speed">120.0 px/s</span
							>
						</div>
					</div>
					<div style="font-size: 12px; color: var(--muted); padding: 0.5rem 0; line-height: 1.8">
						At 60 FPS the wrong version happens to behave correctly (speed=2 px/frame × 60 = 120
						px/s). At any other FPS it breaks. The correct version is always 120 px/s.
					</div>
				</div>
			</div>
		</div>

		<div class="callout orange">
			<div class="callout-label">Cap Delta-Time</div>
			If the game freezes for a moment (OS takeover, breakpoint, disk stall), delta_time can become enormous
			— 2.0 seconds or more. Applied naively, objects teleport huge distances. Always cap delta_time to
			a maximum reasonable value, typically around 0.1–0.25 seconds:
			<code>delta_time = min(delta_time, MAX_DT)</code>.
		</div>

		<pre><code
				>MAX_DT = <span class="num">0.1</span>   <span class="cm"
					># maximum 100 ms step, regardless of real elapsed time</span
				>

now        = time.<span class="fn">perf_counter</span>()
delta_time = <span class="fn">min</span>(now - last_time, MAX_DT)
last_time  = now<span class="lang-tag">python</span></code
			></pre>
	</section>

	<!-- ══ 07.03 FIXED VS VARIABLE ══ -->
	<section id="timestep" class="section">
		<div class="section-header">
			<span class="section-num">07.03</span>
			<h2 class="section-title">Fixed vs Variable Timestep</h2>
		</div>

		<p>
			A <strong>variable timestep</strong> passes whatever delta_time actually occurred to the update
			step. Simple and accurate for rendering, but physics and collision detection can become unstable
			when dt varies wildly — a fast frame gives a tiny dt, a slow frame a large one, and the simulation
			behaves differently.
		</p>
		<p>
			A <strong>fixed timestep</strong> runs the physics update at a constant rate (e.g. 60 Hz = 0.01667s
			per step), accumulating real time into a bucket and draining it in fixed chunks. Rendering happens
			at whatever rate it can manage, interpolating between the last two physics states for a smooth image.
		</p>

		<pre><code
				>FIXED_DT    = <span class="num">1</span> / <span class="num">60</span>   <span class="cm"
					># physics runs at exactly 60 Hz</span
				>
accumulator = <span class="num">0.0</span>

<span class="kw">while</span> running:
    real_dt     = <span class="fn">measure_delta</span>()
    accumulator += real_dt

    <span class="cm"># Drain accumulator in fixed steps</span>
    <span class="kw">while</span> accumulator >= FIXED_DT:
        physics.<span class="fn">step</span>(FIXED_DT)   <span class="cm"># always the same dt</span
				>
        accumulator -= FIXED_DT

    <span class="cm"># Interpolation factor for rendering between physics states</span>
    alpha = accumulator / FIXED_DT  <span class="cm"># 0.0 → 1.0</span>

    <span class="fn">render</span>(alpha)   <span class="cm"
					># interpolate between prev and current state</span
				>
<span class="lang-tag">python</span></code
			></pre>

		<!-- FIXED VS VARIABLE DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Fixed vs Variable Timestep</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					A simulated bouncing ball under both modes. Introduce a frame-rate spike with the slider
					to see how each handles it.
				</p>
				<div class="slider-row">
					<label>Render FPS</label>
					<input type="range" id="fvv-fps" min="5" max="120" value="60" />
					<span class="slider-val" id="fvv-fps-val">60</span>
				</div>
				<div class="slider-row" style="margin-bottom: 1rem">
					<label>FPS spike</label>
					<input type="range" id="fvv-spike" min="0" max="90" value="0" />
					<span class="slider-val" id="fvv-spike-val">0%</span>
				</div>
				<canvas id="fvv-canvas" width="860" height="220" style="width: 100%"></canvas>
				<div
					style="
								margin-top: 0.75rem;
								display: flex;
								gap: 1.5rem;
								font-size: 12px;
								flex-wrap: wrap;
							"
					id="fvv-stats"
				></div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Property</th>
					<th>Variable Timestep</th>
					<th>Fixed Timestep</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Simplicity</td>
					<td>Simple — pass dt directly</td>
					<td>More complex — accumulator + interpolation</td>
				</tr>
				<tr>
					<td>Physics stability</td>
					<td>Can become unstable with large dt</td>
					<td>Deterministic and stable</td>
				</tr>
				<tr>
					<td>Replay / netcode</td>
					<td>Non-deterministic across machines</td>
					<td>Fully deterministic</td>
				</tr>
				<tr>
					<td>Render smoothness</td>
					<td>Smooth (dt matches display)</td>
					<td>Requires interpolation for sub-step smoothness</td>
				</tr>
				<tr>
					<td>Best for</td>
					<td>Simple 2D games, jam projects</td>
					<td>Physics-heavy games, multiplayer, lockstep</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ══ 07.04 INTERPOLATION ══ -->
	<section id="interpolation" class="section">
		<div class="section-header">
			<span class="section-num">07.04</span>
			<h2 class="section-title">Interpolation of Movement and State</h2>
		</div>

		<p>
			<strong>Linear interpolation</strong> (lerp) is the core operation for all smooth animation: given
			two values A and B and a blend factor t in [0, 1], it returns the value t-fraction of the way from
			A to B.
		</p>

		<pre><code
				><span class="kw">def</span> <span class="fn">lerp</span>(a, b, t):
    <span class="kw">return</span> a + (b - a) * t

<span class="cm"># Smooth camera follow — moves 20% closer to target each frame</span>
camera.x = <span class="fn">lerp</span>(camera.x, target.x, <span class="num">0.2</span>)   <span
					class="cm"># WRONG: speed depends on dt</span
				>

<span class="cm"># Correct frame-rate-independent version</span>
camera.x = <span class="fn">lerp</span>(camera.x, target.x, <span class="num">1</span> - (<span
					class="num">1</span
				> - <span class="num">0.2</span>) ** (dt * <span class="num">60</span>))<span
					class="lang-tag">python</span
				></code
			></pre>

		<!-- INTERPOLATION PLAYGROUND -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Interpolation Playground</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Drag the start (A) and end (B) points. Move the <em>t</em> slider to scrub through the interpolation.
					Toggle between lerp, slerp (for angles), and step.
				</p>
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button
						class="btn active"
						onclick={(e) => {
							window.setInterpMode('lerp', e.currentTarget);
						}}>lerp</button
					>
					<button
						class="btn"
						onclick={(e) => {
							window.setInterpMode('smoothstep', e.currentTarget);
						}}>smoothstep</button
					>
					<button
						class="btn"
						onclick={(e) => {
							window.setInterpMode('cosine', e.currentTarget);
						}}>cosine</button
					>
					<button
						class="btn"
						onclick={(e) => {
							window.setInterpMode('step', e.currentTarget);
						}}>step</button
					>
				</div>
				<div class="slider-row" style="margin-bottom: 1rem">
					<label>t (blend)</label>
					<input type="range" id="interp-t" min="0" max="100" value="50" />
					<span class="slider-val" id="interp-t-val">0.50</span>
				</div>
				<canvas id="interp-canvas" width="860" height="240" style="width: 100%"></canvas>
				<div
					id="interp-info"
					style="font-size: 12px; color: var(--muted); margin-top: 0.6rem; min-height: 1.4em"
				></div>
			</div>
		</div>

		<div class="callout green">
			<div class="callout-label">Exponential Decay</div>
			A common pattern is<code>value = lerp(value, target, rate * dt)</code>. This creates an
			exponential approach: fast when far away, slowing as it nears the target. It is frame-rate
			<em>approximate</em> but not exact. The correct frame-rate-independent version is
			<code>lerp(value, target, 1 - exp(-rate * dt))</code>, which matches the exact solution of the
			differential equation <code>dv/dt = rate * (target - v)</code>.
		</div>
	</section>

	<!-- ══ 07.05 EASING ══ -->
	<section id="easing" class="section">
		<div class="section-header">
			<span class="section-num">07.05</span>
			<h2 class="section-title">Easing Functions</h2>
		</div>

		<p>
			An <strong>easing function</strong> remaps the linear t parameter of a lerp to create non-linear
			motion. They give UI transitions, animated objects, and camera moves a sense of weight and polish.
			All easing functions map [0,1] → [0,1], with f(0) = 0 and f(1) = 1.
		</p>
		<p>
			The naming convention: <em>ease-in</em> starts slow and accelerates,
			<em>ease-out</em> starts fast and decelerates, <em>ease-in-out</em> does both. The suffix
			names the curve shape: <em>quad</em> (t²), <em>cubic</em> (t³), <em>elastic</em>,
			<em>bounce</em>, etc.
		</p>

		<!-- EASING GALLERY -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Easing Function Gallery</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Click any function to see its curve and animate a comparison with linear motion.
				</p>
				<div class="easing-grid" id="easing-grid"></div>
				<div style="margin-top: 1.25rem" id="ease-detail">
					<div class="two-col" style="align-items: start">
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.15em;
											text-transform: uppercase;
											color: var(--muted);
											margin-bottom: 0.4rem;
										"
							>
								Curve
							</div>
							<canvas
								id="ease-curve-canvas"
								width="380"
								height="200"
								style="
											width: 100%;
											border: 1px solid var(--border2);
											background: var(--code-bg);
										"
							></canvas>
						</div>
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.15em;
											text-transform: uppercase;
											color: var(--muted);
											margin-bottom: 0.4rem;
										"
							>
								Motion preview
							</div>
							<canvas
								id="ease-motion-canvas"
								width="380"
								height="200"
								style="
											width: 100%;
											border: 1px solid var(--border2);
											background: var(--code-bg);
										"
							></canvas>
							<pre
								id="ease-code"
								style="
											margin-top: 0.75rem;
											font-size: 11px;
											padding: 0.75rem;
											overflow-x: auto;
											min-height: 56px;
										"></pre>
						</div>
					</div>
				</div>
			</div>
		</div>

		<pre><code
				><span class="cm"># Python implementations of common easing functions</span>
<span class="kw">import</span> math

<span class="kw">def</span> <span class="fn">ease_in_quad</span>(t):    <span class="kw"
					>return</span
				> t * t
<span class="kw">def</span> <span class="fn">ease_out_quad</span>(t):   <span class="kw"
					>return</span
				> <span class="num">1</span> - (<span class="num">1</span> - t) ** <span class="num">2</span
				>
<span class="kw">def</span> <span class="fn">ease_in_out_quad</span>(t):
    <span class="kw">return</span> <span class="num">2</span>*t*t <span class="kw">if</span
				> t &lt; <span class="num">0.5</span> <span class="kw">else</span> <span class="num">1</span
				> - (-<span class="num">2</span>*t + <span class="num">2</span>)**<span class="num">2</span
				> / <span class="num">2</span>

<span class="kw">def</span> <span class="fn">ease_out_elastic</span>(t):
    c4 = (<span class="num">2</span> * math.pi) / <span class="num">3</span>
    <span class="kw">if</span> t == <span class="num">0</span> <span class="kw">or</span> t == <span
					class="num">1</span
				>: <span class="kw">return</span> t
    <span class="kw">return</span> <span class="num">2</span>**(-<span class="num">10</span
				>*t) * math.<span class="fn">sin</span>((t*<span class="num">10</span>-<span class="num"
					>0.75</span
				>)*c4) + <span class="num">1</span>

<span class="kw">def</span> <span class="fn">ease_out_bounce</span>(t):
    n1, d1 = <span class="num">7.5625</span>, <span class="num">2.75</span>
    <span class="kw">if</span>   t &lt; <span class="num">1</span>/d1:  <span class="kw"
					>return</span
				> n1*t*t
    <span class="kw">elif</span> t &lt; <span class="num">2</span>/d1:  t -= <span class="num"
					>1.5</span
				>/d1;  <span class="kw">return</span> n1*t*t + <span class="num">0.75</span>
    <span class="kw">elif</span> t &lt; <span class="num">2.5</span>/d1: t -= <span class="num"
					>2.25</span
				>/d1; <span class="kw">return</span> n1*t*t + <span class="num">0.9375</span>
    <span class="kw">else</span>:            t -= <span class="num">2.625</span>/d1;<span class="kw"
					>return</span
				> n1*t*t + <span class="num">0.984375</span>

<span class="cm"># Apply any easing function to a lerp</span>
<span class="kw">def</span> <span class="fn">eased_lerp</span>(a, b, t, ease_fn):
    <span class="kw">return</span> a + (b - a) * <span class="fn">ease_fn</span>(t)<span
					class="lang-tag">python</span
				></code
			></pre>
	</section>

	<hr class="divider" />

	<!-- ══ 07.06 PRACTICAL ══ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">07.06</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<p>
			Three exercises: a complete stable game loop with delta-time capping, a sprite cycle that
			respects delta-time, and an object that uses easing for UI animation.
		</p>

		<div style="margin: 2rem 0">
			<div
				style="
							font-size: 10px;
							letter-spacing: 0.2em;
							text-transform: uppercase;
							color: var(--accent2);
							margin-bottom: 0.75rem;
						"
			>
				Exercise 1 · Stable Game Loop
			</div>
			<pre><code
					><span class="kw">import</span> time, moderngl
<span class="kw">from</span> window_lib <span class="kw">import</span> Window  <span class="cm"
						># pygame, pyglet, glfw, etc.</span
					>

FIXED_DT = <span class="num">1.0</span> / <span class="num">60</span>
MAX_DT   = <span class="num">0.1</span>

window = <span class="fn">Window</span>(<span class="num">800</span>, <span class="num">600</span
					>, title=<span class="str">'Game'</span>)
ctx    = moderngl.<span class="fn">create_context</span>()

last_time   = time.<span class="fn">perf_counter</span>()
accumulator = <span class="num">0.0</span>

<span class="kw">while</span> <span class="kw">not</span> window.should_close:
    now    = time.<span class="fn">perf_counter</span>()
    dt     = <span class="fn">min</span>(now - last_time, MAX_DT)
    last_time = now

    accumulator += dt
    <span class="kw">while</span> accumulator >= FIXED_DT:
        <span class="fn">update</span>(FIXED_DT)          <span class="cm"
						># deterministic fixed step</span
					>
        accumulator -= FIXED_DT

    alpha = accumulator / FIXED_DT   <span class="cm"># render interpolation [0,1]</span>
    <span class="fn">render</span>(alpha)
    window.<span class="fn">swap_buffers</span>()<span class="lang-tag">python</span></code
				></pre>
		</div>

		<div style="margin: 2rem 0">
			<div
				style="
							font-size: 10px;
							letter-spacing: 0.2em;
							text-transform: uppercase;
							color: var(--accent2);
							margin-bottom: 0.75rem;
						"
			>
				Exercise 2 · Delta-Time Sprite Cycle
			</div>
			<pre><code
					><span class="kw">class</span> <span class="fn">AnimatedSprite</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self, frames, fps=<span class="num"
						>8</span
					>):
        self.frames   = frames
        self.fps      = fps
        self.elapsed  = <span class="num">0.0</span>       <span class="cm"
						># accumulated time in seconds</span
					>

    <span class="kw">def</span> <span class="fn">update</span>(self, dt):
        self.elapsed += dt

    <span class="kw">def</span> <span class="fn">current_frame_index</span>(self):
        <span class="cm"># elapsed * fps gives total frames that should have passed</span>
        total_frames = self.elapsed * self.fps
        <span class="kw">return</span> <span class="fn">int</span>(total_frames) % <span class="fn"
						>len</span
					>(self.frames)

    <span class="kw">def</span> <span class="fn">draw</span>(self, renderer):
        fi = self.<span class="fn">current_frame_index</span>()
        renderer.<span class="fn">draw_sprite</span>(self.frames[fi], self.x, self.y)<span
						class="lang-tag">python</span
					></code
				></pre>
		</div>

		<div style="margin: 2rem 0">
			<div
				style="
							font-size: 10px;
							letter-spacing: 0.2em;
							text-transform: uppercase;
							color: var(--accent2);
							margin-bottom: 0.75rem;
						"
			>
				Exercise 3 · Eased UI Animation
			</div>
			<pre><code
					><span class="kw">class</span> <span class="fn">Tween</span>:
    <span class="str">"""Animate a value from start to end over duration seconds."""</span>
    <span class="kw">def</span> <span class="fn">__init__</span
					>(self, start, end, duration, ease_fn=<span class="kw">lambda</span> t: t):
        self.start    = start
        self.end      = end
        self.duration = duration
        self.ease_fn  = ease_fn
        self.elapsed  = <span class="num">0.0</span>

    <span class="kw">def</span> <span class="fn">update</span>(self, dt):
        self.elapsed = <span class="fn">min</span>(self.elapsed + dt, self.duration)

    <span class="kw">@property</span>
    <span class="kw">def</span> <span class="fn">value</span>(self):
        t = self.elapsed / self.duration          <span class="cm"># raw [0, 1]</span>
        eased = self.ease_fn(t)                   <span class="cm"># apply curve</span>
        <span class="kw">return</span> self.start + (self.end - self.start) * eased

    <span class="kw">@property</span>
    <span class="kw">def</span> <span class="fn">finished</span>(self):
        <span class="kw">return</span> self.elapsed >= self.duration

<span class="cm"># Example: slide a menu panel from x=800 to x=500 over 0.4s</span>
panel_tween = <span class="fn">Tween</span>(<span class="num">800</span>, <span class="num"
						>500</span
					>, <span class="num">0.4</span>, ease_fn=ease_out_cubic)

<span class="kw">while</span> running:
    panel_tween.<span class="fn">update</span>(dt)
    panel.x = panel_tween.value<span class="lang-tag">python</span></code
				></pre>
		</div>

		<!-- COMBINED DEMO: full animation scene -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Animated · Game Loop in Action</div>
				<span class="demo-badge a">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Everything from this module working together: a stable loop, delta-time movement, a sprite
					cycle, and eased UI transitions.
				</p>
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button
						class="btn g active"
						id="full-play-btn"
						onclick={(e) => {
							window.toggleFull();
						}}
					>
						⏸ Pause
					</button>
					<button
						class="btn"
						onclick={(e) => {
							window.resetFull();
						}}>↺ Reset</button
					>
					<div class="slider-row" style="flex: 1; min-width: 200px">
						<label>Sim FPS</label>
						<input type="range" id="full-fps" min="5" max="120" value="60" />
						<span class="slider-val" id="full-fps-val">60</span>
					</div>
				</div>
				<canvas
					id="full-canvas"
					width="860"
					height="300"
					style="width: 100%; border: 1px solid var(--border2); background: var(--code-bg)"
				></canvas>
				<div class="info-panel" style="margin-top: 0.75rem">
					<div
						style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem"
						id="full-stats"
					></div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- ══ ASSESSMENT ══ -->
	<section id="assessment" class="assess-section">
		<div class="assess-header">Assessment · Frame Timing Problems</div>
		<div class="assess-sub">
			Given timing data, determine the correct sprite frame, position, or behavior.
		</div>
		<div id="assess-container"></div>
		<div class="assess-score" id="assess-score">
			<div class="assess-score-num" id="assess-score-num">0/5</div>
			<div style="font-size: 12px; color: var(--muted); margin-top: 0.25rem">
				Assessment complete. Proceed to Module 08 when ready.
			</div>
		</div>
	</section>

	<div class="nav-links">
		<a href="." class="prev-link">← 06 · Textures and Sprites</a>
		<a class="next-module" href=".">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">08 · Input and Player Interaction</div>
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
		color: var(--accent);
		border: 1px solid var(--accent);
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
		color: var(--accent);
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
		color: var(--accent);
		border-color: var(--accent);
	}

	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--accent);
		background: var(--surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--accent);
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
		color: var(--accent3);
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
		color: var(--accent3);
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
	}
	p:last-child {
		margin-bottom: 0;
	}
	strong {
		color: var(--accent);
		font-weight: 600;
	}
	em {
		color: #fff;
		font-style: normal;
		font-weight: 500;
	}

	pre {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 1.5rem;
		overflow-x: auto;
		margin: 1.5rem 0;
		font-size: 13px;
		line-height: 1.6;
		position: relative;
	}
	pre :global(.lang-tag) {
		position: absolute;
		top: 8px;
		right: 12px;
		font-size: 10px;
		color: var(--muted);
		letter-spacing: 0.1em;
	}
	.kw {
		color: #c084fc;
	}
	.fn {
		color: #67e8f9;
	}
	.str {
		color: #fde68a;
	}
	.cm {
		color: #1e4060;
	}
	.num {
		color: #f9a8d4;
	}
	.ty {
		color: var(--accent);
	}
	:global(code) {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 1px 6px;
		font-size: 12px;
		color: var(--accent);
	}

	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--accent);
		background: color-mix(in srgb, var(--accent) 5%, var(--surface));
		font-size: 13px;
	}
	.callout.orange {
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 5%, var(--surface));
	}
	.callout.green {
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 5%, var(--surface));
	}
	:global(.callout.pink) {
		border-color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 5%, var(--surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--accent);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	.callout.orange .callout-label {
		color: var(--accent2);
	}
	.callout.green .callout-label {
		color: var(--accent3);
	}
	:global(.callout.pink) .callout-label {
		color: var(--accent4);
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
	.demo-header-left {
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
	.demo-badge.i {
		color: var(--accent);
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 10%, transparent);
	}
	.demo-badge.a {
		color: var(--accent2);
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	canvas {
		display: block;
	}
	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}
	@media (max-width: 640px) {
		.two-col {
			grid-template-columns: 1fr;
		}
	}

	.slider-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0.5rem 0;
	}
	.slider-row label {
		font-size: 11px;
		min-width: 90px;
		color: var(--muted);
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
		background: var(--accent);
		cursor: pointer;
	}
	.slider-val {
		font-size: 12px;
		color: var(--accent);
		min-width: 52px;
		text-align: right;
		font-weight: 600;
	}

	:global(.btn) {
		background: transparent;
		border: 1px solid var(--border2);
		color: var(--text);
		padding: 6px 14px;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s;
	}
	:global(.btn:hover) {
		border-color: var(--accent);
		color: var(--accent);
	}
	:global(.btn.active) {
		border-color: var(--accent);
		color: var(--accent);
		background: color-mix(in srgb, var(--accent) 10%, transparent);
	}
	.btn.o:hover,
	.btn.o.active {
		border-color: var(--accent2);
		color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 10%, transparent);
	}
	.btn.g:hover,
	.btn.g.active {
		border-color: var(--accent3);
		color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
	}
	.btn.p:hover,
	.btn.p.active {
		border-color: var(--accent4);
		color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 10%, transparent);
	}

	.info-panel {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 0.85rem 1rem;
		font-size: 12px;
	}
	.info-row {
		display: flex;
		justify-content: space-between;
		padding: 0.2rem 0;
		border-bottom: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
	}
	.info-row:last-child {
		border-bottom: none;
	}
	.info-key {
		color: var(--muted);
	}
	.info-val {
		color: var(--accent3);
		font-weight: 600;
	}

	/* loop diagram */
	.loop-diagram {
		display: flex;
		flex-direction: column;
		gap: 0;
	}
	.loop-stage {
		display: grid;
		grid-template-columns: 48px 160px 1fr;
		border: 1px solid var(--border);
		border-bottom: none;
		cursor: pointer;
		transition: background 0.15s;
	}
	.loop-stage:last-child {
		border-bottom: 1px solid var(--border);
	}
	.loop-stage:hover,
	.loop-stage.active {
		background: color-mix(in srgb, var(--accent) 5%, var(--surface));
	}
	.loop-num {
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		color: var(--muted);
		border-right: 1px solid var(--border);
	}
	.loop-name {
		padding: 0.7rem 1rem;
		border-right: 1px solid var(--border);
	}
	.loop-name-main {
		font-size: 12px;
		font-weight: 600;
		color: #fff;
	}
	.loop-name-sub {
		font-size: 10px;
		color: var(--muted);
		letter-spacing: 0.05em;
		text-transform: uppercase;
		margin-top: 0.1rem;
	}
	.loop-desc {
		padding: 0.7rem 1rem;
		font-size: 12px;
		color: var(--muted);
		display: flex;
		align-items: center;
	}
	.loop-stage.active .loop-num {
		color: var(--accent);
	}
	.loop-stage.active .loop-name-main {
		color: var(--accent);
	}
	.loop-stage.active .loop-desc {
		color: var(--text);
	}
	.loop-detail {
		margin-top: 0;
		padding: 1rem 1.25rem;
		border: 1px solid var(--border2);
		border-top: none;
		background: color-mix(in srgb, var(--accent) 4%, var(--surface));
		font-size: 12px;
		min-height: 48px;
		color: var(--muted);
	}

	/* timeline chart */
	#timeline-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
		cursor: crosshair;
	}

	/* delta-time comparison */
	#dt-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
	}

	/* easing */
	.easing-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
	}
	@media (max-width: 600px) {
		.easing-grid {
			grid-template-columns: 1fr 1fr;
		}
	}
	.ease-card {
		border: 1px solid var(--border);
		cursor: pointer;
		overflow: hidden;
		transition: border-color 0.15s;
	}
	.ease-card:hover {
		border-color: var(--accent);
	}
	.ease-card.active {
		border-color: var(--accent2);
	}
	.ease-card canvas {
		display: block;
		width: 100%;
	}
	.ease-label {
		font-size: 10px;
		padding: 0.3rem 0.5rem;
		color: var(--muted);
		border-top: 1px solid var(--border);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}
	.ease-card.active .ease-label {
		color: var(--accent2);
	}

	/* interpolation playground */
	#interp-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
		cursor: crosshair;
		touch-action: none;
	}

	/* fixed vs variable */
	#fvv-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
	}

	/* assessment */
	.assess-section {
		margin: 4rem 0;
		padding: 2rem;
		border: 1px solid var(--border);
		background: var(--surface);
	}
	.assess-header {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-bottom: 0.25rem;
	}
	.assess-sub {
		font-size: 12px;
		color: var(--muted);
		margin-bottom: 2rem;
	}
	.timing-problem {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 1.25rem;
		margin: 1.5rem 0;
	}
	.tp-header {
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--accent2);
		margin-bottom: 1rem;
	}
	.tp-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 12px;
		margin-bottom: 1rem;
	}
	.tp-table th {
		background: var(--raised);
		color: var(--accent);
		padding: 0.4rem 0.75rem;
		border: 1px solid var(--border);
		text-align: left;
	}
	.tp-table td {
		padding: 0.35rem 0.75rem;
		border: 1px solid var(--border);
	}
	.tp-q {
		font-size: 13px;
		color: #fff;
		margin-bottom: 1rem;
	}
	.tp-options {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	:global(.tp-option) {
		padding: 0.4rem 1rem;
		border: 1px solid var(--border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		font-family: 'IBM Plex Mono', monospace;
	}
	:global(.tp-option:hover) {
		border-color: var(--border2);
		background: var(--raised);
	}
	:global(.tp-option.correct) {
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 12%, transparent);
		color: var(--accent3);
	}
	:global(.tp-option.wrong) {
		border-color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 12%, transparent);
		color: var(--accent4);
	}
	:global(.tp-option.disabled) {
		pointer-events: none;
	}
	:global(.tp-feedback) {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.75rem;
		min-height: 1.4em;
	}
	:global(.tp-feedback.ok) {
		color: var(--accent3);
	}
	:global(.tp-feedback.bad) {
		color: var(--accent4);
	}
	.assess-score {
		margin-top: 2rem;
		padding: 1.5rem;
		border: 1px solid var(--border);
		text-align: center;
		display: none;
	}
	.assess-score-num {
		font-family: 'Syne', sans-serif;
		font-size: 36px;
		font-weight: 800;
		color: var(--accent);
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--raised);
		color: var(--accent);
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

	hr.divider {
		border: none;
		border-top: 1px solid var(--border);
		margin: 3rem 0;
	}

	.progress-bar-wrap {
		height: 3px;
		background: var(--border);
		width: 100%;
		margin: 2rem 0 0;
	}
	.progress-bar-fill {
		height: 100%;
		background: var(--accent);
		width: 0;
		transition: width 0.4s ease;
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
	}
	.prev-link:hover {
		border-color: var(--accent2);
		color: var(--accent2);
	}
	.next-module {
		display: flex;
		align-items: center;
		gap: 2rem;
		padding: 1.5rem 2rem;
		border: 1px solid var(--border);
		text-decoration: none;
		transition: all 0.2s;
		background: var(--surface);
	}
	.next-module:hover {
		border-color: var(--accent3);
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
		color: var(--accent3);
	}
</style>
