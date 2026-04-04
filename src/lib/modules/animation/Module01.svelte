<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-unused-expressions */
	import { onMount } from 'svelte';

	onMount(() => {
		/* ════════════════════════════════════════
   HERO FILMSTRIP DECORATION
════════════════════════════════════════ */
		(function () {
			const el = document.getElementById('heroFrames');
			for (let r = 0; r < 8; r++) {
				const row = document.createElement('div');
				row.className = 'frame-strip';
				for (let c = 0; c < 5; c++) {
					const cell = document.createElement('div');
					cell.className = 'frame-cell';
					row.appendChild(cell);
				}
				el.appendChild(row);
			}
		})();

		/* ════════════════════════════════════════
   FLIPBOOK DEMO
   13 frames of a bouncing ball with squash & stretch
════════════════════════════════════════ */
		const FRAMES = (() => {
			// Each: { cx, cy, rx, ry } — center x/y, half-widths
			// Canvas 300×180. Ground at y=160.
			return [
				{ cx: 40, cy: 148, rx: 16, ry: 10, trail: false }, // 0 – squash on ground
				{ cx: 65, cy: 135, rx: 13, ry: 18, trail: false }, // 1 – rising, stretch
				{ cx: 95, cy: 110, rx: 11, ry: 22, trail: false }, // 2 – rising fast
				{ cx: 130, cy: 82, rx: 11, ry: 23, trail: false }, // 3 – peak approach, max stretch
				{ cx: 162, cy: 60, rx: 16, ry: 17, trail: false }, // 4 – apex
				{ cx: 192, cy: 82, rx: 11, ry: 22, trail: false }, // 5 – descending
				{ cx: 220, cy: 110, rx: 11, ry: 23, trail: false }, // 6 – falling fast
				{ cx: 245, cy: 138, rx: 14, ry: 19, trail: false }, // 7 – near impact
				{ cx: 258, cy: 152, rx: 22, ry: 9, trail: false }, // 8 – SQUASH (impact)
				{ cx: 265, cy: 136, rx: 13, ry: 19, trail: false }, // 9 – bounce up
				{ cx: 272, cy: 110, rx: 12, ry: 21, trail: false }, // 10 – second rise
				{ cx: 278, cy: 88, rx: 14, ry: 16, trail: false }, // 11 – second apex (lower)
				{ cx: 282, cy: 108, rx: 12, ry: 20, trail: false } // 12 – falling again
			];
		})();

		let flipCurrent = 0;
		let flipPlaying = false;
		let flipTimer = null;
		const flipCanvas = document.getElementById('flipbookCanvas');
		const flipCtx = flipCanvas.getContext('2d');
		const flipNumEl = document.getElementById('flipNum');
		const flipSpeed = document.getElementById('flipSpeed');
		const flipSpeedVal = document.getElementById('flipSpeedVal');

		const cs = getComputedStyle(document.documentElement);
		const C = {
			gold: '#f0a830',
			coral: '#e8553a',
			mint: '#4ecbb4',
			muted: '#7a6e5e',
			border2: '#3c342a',
			raised: '#1c1812',
			bg: '#0b0906'
		};

		function drawBall(ctx, frame, w, h, small) {
			const f = FRAMES[frame];
			const scaleX = small ? w / 300 : 1;
			const scaleY = small ? h / 180 : 1;
			const cx = f.cx * scaleX,
				cy = f.cy * scaleY;
			const rx = f.rx * scaleX,
				ry = f.ry * scaleY;
			const gy = small ? 160 * scaleY : 160; // ground y

			ctx.save();

			if (!small) {
				// Ground line
				ctx.strokeStyle = C.border2;
				ctx.lineWidth = 1;
				ctx.beginPath();
				ctx.moveTo(10, gy + 2);
				ctx.lineTo(w - 10, gy + 2);
				ctx.stroke();

				// Shadow
				const dist = gy - cy;
				const shadowAlpha = Math.max(0, 1 - dist / 140) * 0.4;
				const shadowW = rx * (1 - dist / 200) * 2.2;
				ctx.fillStyle = `rgba(0,0,0,${shadowAlpha})`;
				ctx.beginPath();
				ctx.ellipse(cx, gy + 2, Math.max(4, shadowW), 3, 0, 0, Math.PI * 2);
				ctx.fill();

				// Frame number ghost trail dots
				for (let i = 0; i < frame; i++) {
					const pf = FRAMES[i];
					ctx.globalAlpha = 0.08 + (i / frame) * 0.1;
					ctx.fillStyle = C.gold;
					ctx.beginPath();
					ctx.arc(pf.cx, pf.cy, 3, 0, Math.PI * 2);
					ctx.fill();
				}
				ctx.globalAlpha = 1;
			}

			// Ball gradient
			const grd = ctx.createRadialGradient(
				cx - rx * 0.3,
				cy - ry * 0.3,
				ry * 0.1,
				cx,
				cy,
				Math.max(rx, ry)
			);
			grd.addColorStop(0, small ? C.gold : '#ffc85a');
			grd.addColorStop(0.6, C.gold);
			grd.addColorStop(1, '#b07010');

			ctx.fillStyle = grd;
			ctx.beginPath();
			ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
			ctx.fill();

			if (!small) {
				// Highlight
				ctx.fillStyle = 'rgba(255,255,255,0.3)';
				ctx.beginPath();
				ctx.ellipse(cx - rx * 0.25, cy - ry * 0.3, rx * 0.3, ry * 0.2, -0.3, 0, Math.PI * 2);
				ctx.fill();
			}

			ctx.restore();
		}

		function renderFlipbook() {
			flipCtx.clearRect(0, 0, 300, 180);
			drawBall(flipCtx, flipCurrent, 300, 180, false);
			flipNumEl.textContent = flipCurrent + 1;

			// Update filmstrip highlight
			document.querySelectorAll('.film-frame').forEach((el, i) => {
				el.classList.toggle('active', i === flipCurrent);
			});
		}

		function buildFilmstrip() {
			const strip = document.getElementById('filmstrip');
			FRAMES.forEach((f, i) => {
				const div = document.createElement('div');
				div.className = 'film-frame';
				div.innerHTML = `<span class="film-frame-num">${i + 1}</span>`;
				const c = document.createElement('canvas');
				c.width = 60;
				c.height = 44;
				const ctx2 = c.getContext('2d');
				drawBall(ctx2, i, 60, 44, true);
				div.insertBefore(c, div.firstChild);
				div.onclick = () => {
					flipCurrent = i;
					renderFlipbook();
				};
				strip.appendChild(div);
			});
		}

		document.getElementById('flipPrev').onclick = () => {
			if (flipPlaying) stopFlip();
			flipCurrent = (flipCurrent - 1 + FRAMES.length) % FRAMES.length;
			renderFlipbook();
		};
		document.getElementById('flipNext').onclick = () => {
			if (flipPlaying) stopFlip();
			flipCurrent = (flipCurrent + 1) % FRAMES.length;
			renderFlipbook();
		};

		const flipPlayBtn = document.getElementById('flipPlay');
		function startFlip() {
			flipPlaying = true;
			flipPlayBtn.textContent = '⏹ Stop';
			flipPlayBtn.classList.add('active');
			const fps = parseInt(flipSpeed.value);
			flipTimer = setInterval(() => {
				flipCurrent = (flipCurrent + 1) % FRAMES.length;
				renderFlipbook();
			}, 1000 / fps);
		}
		function stopFlip() {
			flipPlaying = false;
			flipPlayBtn.textContent = '▶ Play';
			flipPlayBtn.classList.remove('active');
			clearInterval(flipTimer);
		}
		flipPlayBtn.onclick = () => {
			flipPlaying ? stopFlip() : startFlip();
		};
		flipSpeed.oninput = () => {
			flipSpeedVal.textContent = flipSpeed.value;
			if (flipPlaying) {
				stopFlip();
				startFlip();
			}
		};

		buildFilmstrip();
		renderFlipbook();

		/* ════════════════════════════════════════
   FPS DEMO — Pendulum animation
════════════════════════════════════════ */
		const fpsCanvas = document.getElementById('fpsCanvas');
		const fpsCtx = fpsCanvas.getContext('2d');
		const fpsLevels = [4, 8, 24, 30, 60];
		const fpsLabels = ['4 fps', '8 fps', '24 fps', '30 fps', '60 fps'];
		let fpsCurrent = 2; // index
		let fpsAngle = 0;
		let fpsLastFrame = 0;
		let fpsFrameTime = 0; // ms between frames at target fps
		let fpsAccum = 0;
		let fpsRafId = null;

		const FPS_W = fpsCanvas.width;
		const FPS_H = fpsCanvas.height;
		const PENDULUMS = [
			{ label: 'A', ox: FPS_W * 0.25, length: 75, phase: 0 },
			{ label: 'B', ox: FPS_W * 0.5, length: 75, phase: 0.4 },
			{ label: 'C', ox: FPS_W * 0.75, length: 75, phase: 0.9 }
		];

		let fpsSimAngle = 0; // master angle that advances in real time
		let fpsLastTs = null;
		let fpsDrawAngle = 0; // snapped to target fps

		function drawPendulums(angle) {
			fpsCtx.clearRect(0, 0, FPS_W, FPS_H);

			// bg grid
			fpsCtx.strokeStyle = 'rgba(255,255,255,0.02)';
			fpsCtx.lineWidth = 1;
			for (let x = 0; x < FPS_W; x += 40) {
				fpsCtx.beginPath();
				fpsCtx.moveTo(x, 0);
				fpsCtx.lineTo(x, FPS_H);
				fpsCtx.stroke();
			}

			PENDULUMS.forEach((p) => {
				const a = Math.sin(angle * 1.4 + p.phase) * 0.9;
				const bx = p.ox + Math.sin(a) * p.length;
				const by = 30 + Math.cos(a) * p.length;

				// Pivot
				fpsCtx.fillStyle = C.border2;
				fpsCtx.beginPath();
				fpsCtx.arc(p.ox, 28, 5, 0, Math.PI * 2);
				fpsCtx.fill();

				// Rod
				fpsCtx.strokeStyle = C.border2;
				fpsCtx.lineWidth = 1.5;
				fpsCtx.beginPath();
				fpsCtx.moveTo(p.ox, 28);
				fpsCtx.lineTo(bx, by);
				fpsCtx.stroke();

				// Ball
				const grd = fpsCtx.createRadialGradient(bx - 4, by - 4, 2, bx, by, 14);
				grd.addColorStop(0, '#ffc85a');
				grd.addColorStop(1, '#b07010');
				fpsCtx.fillStyle = grd;
				fpsCtx.beginPath();
				fpsCtx.arc(bx, by, 13, 0, Math.PI * 2);
				fpsCtx.fill();

				// Label
				fpsCtx.fillStyle = C.muted;
				fpsCtx.font = `500 10px 'JetBrains Mono'`;
				fpsCtx.textAlign = 'center';
				fpsCtx.fillText(p.label, p.ox, FPS_H - 6);
			});
		}

		function fpsTick(ts) {
			if (fpsLastTs === null) fpsLastTs = ts;
			const dt = ts - fpsLastTs;
			fpsLastTs = ts;

			fpsSimAngle += dt * 0.001; // advance master angle

			// Only update drawn angle at target fps
			fpsAccum += dt;
			const targetInterval = 1000 / fpsLevels[fpsCurrent];
			if (fpsAccum >= targetInterval) {
				fpsAccum = fpsAccum % targetInterval;
				fpsDrawAngle = fpsSimAngle;
			}

			drawPendulums(fpsDrawAngle);
			fpsRafId = requestAnimationFrame(fpsTick);
		}

		function setFPS(idx) {
			fpsCurrent = idx;
			document.getElementById('fpsLabel').textContent = fpsLabels[idx];
			// Update button states
			document.querySelectorAll('[onclick^="setFPS"]').forEach((b, i) => {
				b.classList.toggle('active', i === idx);
			});
			fpsAccum = 0;
		}

		document.getElementById('fpsSlider').oninput = function () {
			setFPS(parseInt(this.value));
		};

		fpsRafId = requestAnimationFrame(fpsTick);

		/* ════════════════════════════════════════
   TIMING vs SPACING DEMO
════════════════════════════════════════ */
		const tsCanvas = document.getElementById('tsCanvas');
		const tsCtx = tsCanvas.getContext('2d');
		const TS_W = tsCanvas.width;
		const TS_H = tsCanvas.height;
		const TS_FRAMES = 20;
		let tsProgress = 0; // 0..1
		let tsPlaying = false;
		let tsRafId = null;
		let tsLastTs = null;
		let tsShowDots = true;

		document.getElementById('tsShowDots').onchange = function () {
			tsShowDots = this.checked;
			renderTS();
		};

		function easeInOut(t) {
			return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
		}
		function linear(t) {
			return t;
		}

		function renderTS() {
			tsCtx.clearRect(0, 0, TS_W, TS_H);

			const pad = 40;
			const trackW = TS_W - pad * 2;
			const yLinear = TS_H * 0.32;
			const yEase = TS_H * 0.68;
			const ballR = 13;

			// Track lines
			function drawTrack(y, label, accentColor) {
				tsCtx.strokeStyle = C.border2;
				tsCtx.lineWidth = 1;
				tsCtx.setLineDash([4, 4]);
				tsCtx.beginPath();
				tsCtx.moveTo(pad, y);
				tsCtx.lineTo(TS_W - pad, y);
				tsCtx.stroke();
				tsCtx.setLineDash([]);

				// Track label
				tsCtx.fillStyle = accentColor;
				tsCtx.font = `500 10px 'JetBrains Mono'`;
				tsCtx.textAlign = 'left';
				tsCtx.fillText(label, pad, y - ballR - 6);
			}

			drawTrack(yLinear, 'LINEAR', C.gold);
			drawTrack(yEase, 'EASE IN/OUT', C.coral);

			// Frame position dots
			if (tsShowDots) {
				for (let i = 0; i <= TS_FRAMES; i++) {
					const tl = linear(i / TS_FRAMES);
					const te = easeInOut(i / TS_FRAMES);
					const xl = pad + tl * trackW;
					const xe = pad + te * trackW;

					tsCtx.globalAlpha = 0.35;
					tsCtx.fillStyle = C.gold;
					tsCtx.beginPath();
					tsCtx.arc(xl, yLinear, 2.5, 0, Math.PI * 2);
					tsCtx.fill();

					tsCtx.fillStyle = C.coral;
					tsCtx.beginPath();
					tsCtx.arc(xe, yEase, 2.5, 0, Math.PI * 2);
					tsCtx.fill();
					tsCtx.globalAlpha = 1;
				}
			}

			// Moving balls
			const xlBall = pad + linear(tsProgress) * trackW;
			const xeBall = pad + easeInOut(tsProgress) * trackW;

			function drawMovingBall(x, y, color) {
				const grd = tsCtx.createRadialGradient(x - 4, y - 4, 2, x, y, ballR);
				grd.addColorStop(0, '#fff');
				grd.addColorStop(0.3, color);
				grd.addColorStop(1, '#000');
				tsCtx.fillStyle = grd;
				tsCtx.beginPath();
				tsCtx.arc(x, y, ballR, 0, Math.PI * 2);
				tsCtx.fill();
				tsCtx.strokeStyle = 'rgba(255,255,255,0.15)';
				tsCtx.lineWidth = 1;
				tsCtx.stroke();
			}

			drawMovingBall(xlBall, yLinear, C.gold);
			drawMovingBall(xeBall, yEase, C.coral);

			// Start / end markers
			tsCtx.strokeStyle = C.border2;
			tsCtx.lineWidth = 1;
			[pad, TS_W - pad].forEach((x) => {
				tsCtx.beginPath();
				tsCtx.moveTo(x, 20);
				tsCtx.lineTo(x, TS_H - 20);
				tsCtx.stroke();
			});
			tsCtx.fillStyle = C.muted;
			tsCtx.font = `10px 'JetBrains Mono'`;
			tsCtx.textAlign = 'center';
			tsCtx.fillText('START', pad, 18);
			tsCtx.fillText('END', TS_W - pad, 18);
		}

		function tsAnimate(ts) {
			if (tsLastTs === null) tsLastTs = ts;
			const dt = (ts - tsLastTs) / 1000;
			tsLastTs = ts;
			tsProgress = Math.min(1, tsProgress + dt * 0.5); // 2 second travel
			renderTS();
			if (tsProgress < 1) {
				tsRafId = requestAnimationFrame(tsAnimate);
			} else {
				tsPlaying = false;
				document.getElementById('tsPlayBtn').textContent = '▶ Animate';
				document.getElementById('tsPlayBtn').classList.remove('active');
				tsLastTs = null;
			}
		}

		document.getElementById('tsPlayBtn').onclick = function () {
			if (!tsPlaying) {
				if (tsProgress >= 1) tsProgress = 0;
				tsPlaying = true;
				this.textContent = '⏸ Playing…';
				this.classList.add('active');
				tsRafId = requestAnimationFrame(tsAnimate);
			}
		};
		document.getElementById('tsResetBtn').onclick = function () {
			cancelAnimationFrame(tsRafId);
			tsPlaying = false;
			tsProgress = 0;
			tsLastTs = null;
			document.getElementById('tsPlayBtn').textContent = '▶ Animate';
			document.getElementById('tsPlayBtn').classList.remove('active');
			renderTS();
		};

		renderTS();

		/* ════════════════════════════════════════
   ANIMATION TYPE CARDS
════════════════════════════════════════ */
		const typeDetails = {
			traditional: `
    <strong>Traditional animation</strong> (also called cel animation or hand-drawn animation) requires the animator to draw every single frame. Classic Disney films used this method — 24 unique drawings per second. The main advantages are <strong>expressive control</strong> and a natural, organic feel that is impossible to replicate in software. The disadvantage is sheer labor: a 1-minute clip at 24fps requires 1,440 drawings. For educational YouTube animation, traditional techniques inform <em>how</em> we draw characters and poses, but the production rarely uses it end-to-end.
  `,
			tween: `
    <strong>Tween-based animation</strong> (short for "in-between") is how most modern 2D software works. You set a <em>keyframe</em> at a start position and another at an end position. The software interpolates all the frames in between using a curve you control. This dramatically reduces labor — but the animator must still understand timing and spacing to make the curves feel right. Tools like Adobe Animate, SVGator, and After Effects are built on this model. <strong>This is the primary technique for educational video production.</strong>
  `,
			rig: `
    A <strong>rig</strong> is a skeleton — a hierarchy of bones that deforms a character's artwork. Instead of redrawing the character each frame, you pose the rig. This makes walk cycles, gestures, and recurring characters highly efficient because the drawing assets only need to be created once. Tools like Spine, Duik (for After Effects), and Blender's Grease Pencil all support rigging. For educational channels with a recurring host character, rigging is the professional choice.
  `,
			procedural: `
    <strong>Procedural animation</strong> uses math to generate motion. Instead of posing a character, you write (or configure) equations that produce movement automatically. Common examples: simulated hair physics, crowd movement, generative art, and data-driven visualizations. For educational YouTube, procedural techniques show up in tools like <em>Manim</em> (math visualizations), or when animating charts and diagrams that respond to data. You won't write much procedural code in this course, but you'll learn to use easing curves — which are procedural functions applied to your keyframe animations.
  `
		};

		function selectType(el) {
			document.querySelectorAll('.type-card').forEach((c) => c.classList.remove('active'));
			el.classList.add('active');
			const detail = document.getElementById('typeDetail');
			detail.innerHTML = typeDetails[el.dataset.type];
			detail.classList.add('visible');
		}

		/* ════════════════════════════════════════
   QUIZ
════════════════════════════════════════ */
		let quizScores = {};

		function answer(optionEl, qId, result) {
			const qEl = document.getElementById(qId);
			// Already answered
			if (qEl.querySelector('.option.correct') || qEl.querySelector('.option.wrong')) return;

			const fb = document.getElementById(qId + '-feedback');
			optionEl.classList.add(result === 'correct' ? 'correct' : 'wrong');
			// Disable all options
			qEl.querySelectorAll('.option').forEach((o) => o.classList.add('disabled'));

			if (result === 'correct') {
				fb.textContent = '✓ Correct.';
				fb.className = 'feedback ok';
				quizScores[qId] = true;
			} else {
				fb.textContent = '✗ Not quite — re-read the section and try to find the right answer.';
				fb.className = 'feedback bad';
				quizScores[qId] = false;
				// Reveal correct
				const opts = qEl.querySelectorAll('.option');
				opts.forEach((o) => {
					if (!o.classList.contains('wrong')) o.classList.add('correct');
				});
			}

			// Check if all answered
			const total = 4;
			const answered = Object.keys(quizScores).length;
			if (answered === total) {
				const correct = Object.values(quizScores).filter(Boolean).length;
				const scoreEl = document.getElementById('quizScore');
				document.getElementById('scoreNum').textContent = `${correct}/${total}`;
				scoreEl.classList.add('visible');
				scoreEl.querySelector('.score-lbl').textContent =
					correct === total
						? 'Perfect — Module 1 Complete!'
						: correct >= 3
							? 'Good — Review the sections you missed.'
							: 'Review the module and try again.';
			}
		}

		/* eslint-disable no-undef */
		if (typeof stopFlip === 'function') window.stopFlip = stopFlip;
		if (typeof renderTS === 'function') window.renderTS = renderTS;
		if (typeof answer === 'function') window.answer = answer;
		if (typeof drawTrack === 'function') window.drawTrack = drawTrack;
		if (typeof drawMovingBall === 'function') window.drawMovingBall = drawMovingBall;
		if (typeof fpsTick === 'function') window.fpsTick = fpsTick;
		if (typeof startFlip === 'function') window.startFlip = startFlip;
		if (typeof selectType === 'function') window.selectType = selectType;
		if (typeof setFPS === 'function') window.setFPS = setFPS;
		if (typeof easeInOut === 'function') window.easeInOut = easeInOut;
		if (typeof drawPendulums === 'function') window.drawPendulums = drawPendulums;
		if (typeof linear === 'function') window.linear = linear;
		if (typeof tsAnimate === 'function') window.tsAnimate = tsAnimate;
		if (typeof renderFlipbook === 'function') window.renderFlipbook = renderFlipbook;
		if (typeof buildFilmstrip === 'function') window.buildFilmstrip = buildFilmstrip;
		if (typeof drawBall === 'function') window.drawBall = drawBall;
		/* eslint-enable no-undef */

		return () => {
			if (typeof fpsRafId !== 'undefined' && fpsRafId) cancelAnimationFrame(fpsRafId);
			if (typeof tsRafId !== 'undefined' && tsRafId) cancelAnimationFrame(tsRafId);
			if (typeof flipTimer !== 'undefined' && flipTimer) clearInterval(flipTimer);
		};
	});
</script>

<div class="page-wrapper">
	<!-- ══════════════════ HERO ══════════════════ -->
	<header class="module-hero">
		<div class="hero-frames" aria-hidden="true" id="heroFrames"></div>
		<div class="module-eyebrow">Animation Fundamentals · Module 01</div>
		<h1 class="module-title">What <em>Animation</em> Is</h1>
		<p class="module-subtitle">How still images become motion — and why the brain believes them.</p>

		<div class="objectives">
			<div class="obj-label">Learning Objectives</div>
			<ul>
				<li>Understand how motion emerges from still images</li>
				<li>Explain frame-based representation, timing, and perception</li>
				<li>Distinguish between traditional, digital, and procedural animation</li>
			</ul>
		</div>
	</header>

	<!-- ══════════════════ SECTION 1: PERSISTENCE OF VISION ══════════════════ -->
	<section class="section" id="s1">
		<div class="section-header">
			<span class="section-num">01</span>
			<h2 class="section-title">Persistence of Vision</h2>
		</div>

		<p>
			Animation is a trick. It exploits a quirk in human visual perception: when a series of images
			are shown quickly enough, your brain
			<strong>stitches them together into continuous motion</strong> rather than perceiving them as separate
			pictures.
		</p>
		<p>
			This is sometimes called <em>persistence of vision</em> — the retina briefly "holds" an image for
			a fraction of a second after it disappears. Show the next image before the previous one fades, and
			you get the illusion of movement.
		</p>

		<div class="callout gold">
			<div class="callout-label">Key Insight</div>
			There is no actual motion in an animation. Only a rapid sequence of
			<strong>still frames</strong>. Everything animators do is a calculated illusion designed to
			fool the perceptual system.
		</div>

		<p>
			The simplest possible animation tool is a <strong>flipbook</strong>: drawings on the edges of
			pages that, when flipped rapidly with a thumb, appear to move. Every sophisticated animation
			tool — from 2D software to game engines — is based on the same principle.
		</p>

		<!-- DEMO: Flipbook -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 1.1 — Flipbook</span>
				<span class="demo-badge">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1rem">
					A bouncing ball, 13 hand-crafted frames. Use the controls to step through or play it — at
					different speeds.
				</p>

				<div style="display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: flex-start">
					<div>
						<canvas
							id="flipbookCanvas"
							width="300"
							height="180"
							style="background: var(--raised); border: 1px solid var(--border)"
						></canvas>
						<div class="frame-counter" style="margin-top: 0.5rem">
							Frame <span id="flipNum">1</span> / 13
						</div>
					</div>

					<div style="flex: 1; min-width: 200px">
						<div class="btn-row">
							<button class="btn" id="flipPrev">← Prev</button>
							<button class="btn" id="flipNext">Next →</button>
							<button class="btn coral" id="flipPlay">▶ Play</button>
						</div>

						<div class="ctrl-row" style="margin-top: 1.25rem">
							<span class="ctrl-label">Speed</span>
							<input type="range" id="flipSpeed" min="2" max="24" value="12" step="1" />
							<span class="ctrl-val"><span id="flipSpeedVal">12</span> fps</span>
						</div>

						<!-- Filmstrip -->
						<div class="filmstrip" id="filmstrip" style="margin-top: 1rem"></div>
					</div>
				</div>
			</div>
		</div>

		<p>
			Notice that at low speeds (2–4 fps) you can clearly see discrete images. Around
			<strong>12 fps</strong> the brain begins to merge them. At 24 fps — the traditional cinema standard
			— the motion feels solid and continuous.
		</p>
	</section>

	<!-- ══════════════════ SECTION 2: FPS ══════════════════ -->
	<section class="section" id="s2">
		<div class="section-header">
			<span class="section-num">02</span>
			<h2 class="section-title">Frames Per Second &amp; Smoothness</h2>
		</div>

		<p>
			<strong>Frames per second (fps)</strong> is how many still images are shown every second. It is
			the single most important number in any animation pipeline. Higher fps = more images per second
			= smoother perceived motion.
		</p>
		<p>
			But fps is not free — more frames means more drawing, more computation, and more memory.
			Animators have always made deliberate tradeoffs:
		</p>

		<div class="stat-row-mini" style="margin-bottom: 1.5rem">
			<div class="stat-badge">
				<span class="sv">8–12</span><span class="sk">Classic cartoons</span>
			</div>
			<div class="stat-badge">
				<span class="sv">24</span><span class="sk">Film standard</span>
			</div>
			<div class="stat-badge">
				<span class="sv">30</span><span class="sk">TV / Web video</span>
			</div>
			<div class="stat-badge"><span class="sv">60</span><span class="sk">Games / UI</span></div>
			<div class="stat-badge">
				<span class="sv">120+</span><span class="sk">VR / high-end</span>
			</div>
		</div>

		<!-- DEMO: FPS comparison -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 1.2 — FPS Experiment</span>
				<span class="demo-badge">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					Watch the same pendulum animation at different frame rates. Drag the slider to feel the
					difference between choppy and smooth.
				</p>

				<canvas
					id="fpsCanvas"
					width="560"
					height="140"
					style="background: var(--raised); border: 1px solid var(--border); max-width: 100%"
				></canvas>

				<div class="ctrl-row" style="margin-top: 1rem">
					<span class="ctrl-label">Frame rate</span>
					<input type="range" id="fpsSlider" min="0" max="4" value="2" step="1" style="flex: 1" />
					<span class="ctrl-val" id="fpsLabel">24 fps</span>
				</div>

				<div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap">
					<button
						class="btn"
						onclick={(e) => {
							window.setFPS(0);
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setFPS(0);
						}}>4 fps</button
					>
					<button
						class="btn"
						onclick={(e) => {
							window.setFPS(1);
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setFPS(1);
						}}>8 fps</button
					>
					<button
						class="btn active"
						onclick={(e) => {
							window.setFPS(2);
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setFPS(2);
						}}
						id="fps24Btn">24 fps</button
					>
					<button
						class="btn"
						onclick={(e) => {
							window.setFPS(3);
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setFPS(3);
						}}>30 fps</button
					>
					<button
						class="btn"
						onclick={(e) => {
							window.setFPS(4);
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter') window.setFPS(4);
						}}>60 fps</button
					>
				</div>

				<div class="callout mint" style="margin-top: 1.25rem">
					<div class="callout-label">Notice</div>
					Below 12 fps the individual frames become visible. Above 30 fps, increases in smoothness are
					subtle — but can matter a lot in fast action.
				</div>
			</div>
		</div>

		<p>
			For educational animation — the kind used in explainer videos — <strong>24 fps</strong> is the sweet
			spot. It feels cinematic and smooth without requiring 2.5× more work than 24fps alternatives.
		</p>
	</section>

	<!-- ══════════════════ SECTION 3: TIMING vs SPACING ══════════════════ -->
	<section class="section" id="s3">
		<div class="section-header">
			<span class="section-num">03</span>
			<h2 class="section-title">Timing vs. Spacing</h2>
		</div>

		<p>
			This is one of the most important conceptual distinctions in all of animation — and one of the
			most commonly confused.
		</p>

		<p>
			<strong>Timing</strong> is <em>how many frames</em> an action takes. A punch that takes 3
			frames feels faster than the same punch in 12 frames. Timing controls <em>speed</em>.
		</p>
		<p>
			<strong>Spacing</strong> is <em>where</em> the object is positioned in each of those frames —
			how far it moves between consecutive frames. Spacing controls
			<em>acceleration</em>, <em>weight</em>, and <em>feel</em>.
		</p>

		<div class="callout coral">
			<div class="callout-label">The Key Distinction</div>
			Two animations can have<strong>identical timing</strong> (same number of frames) but feel
			completely different because of <strong>different spacing</strong>. This is how animators
			convey weight, gravity, and personality without changing speed.
		</div>

		<!-- DEMO: Timing vs Spacing -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 1.3 — Timing vs. Spacing</span>
				<span class="demo-badge coral">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					Both balls travel the same distance in the same number of frames. Only their spacing
					differs. The dots show where each ball is <em>per frame</em>.
				</p>

				<canvas
					id="tsCanvas"
					width="560"
					height="200"
					style="background: var(--raised); border: 1px solid var(--border); max-width: 100%"
				></canvas>

				<div class="btn-row">
					<button class="btn mint" id="tsPlayBtn">▶ Animate</button>
					<button class="btn" id="tsResetBtn">↺ Reset</button>
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
						<input type="checkbox" id="tsShowDots" checked style="accent-color: var(--gold)" />
						Show frame positions
					</label>
				</div>

				<div class="two-track" style="margin-top: 1.25rem">
					<div class="track-panel">
						<div class="track-label"><span>Linear</span> spacing</div>
						<p style="font-size: 12px; color: var(--muted); margin: 0">
							Equal distance between every frame. Feels mechanical, robotic — like a conveyor belt.
							No sense of weight.
						</p>
					</div>
					<div class="track-panel">
						<div class="track-label coral"><span>Ease-in / Ease-out</span> spacing</div>
						<p style="font-size: 12px; color: var(--muted); margin: 0">
							Slow start, fast middle, slow end. Feels natural — like a ball thrown through air, or
							a person walking. This is how physics works.
						</p>
					</div>
				</div>
			</div>
		</div>

		<p>
			Almost all motion in nature is eased. Objects accelerate from rest and decelerate before
			stopping. <strong>Linear animation always looks wrong</strong> because nothing in the real world
			moves at constant speed. Understanding spacing is understanding physics through drawing.
		</p>
	</section>

	<!-- ══════════════════ SECTION 4: TYPES ══════════════════ -->
	<section class="section" id="s4">
		<div class="section-header">
			<span class="section-num">04</span>
			<h2 class="section-title">Three Animation Workflows</h2>
		</div>

		<p>
			The same timing-and-spacing principles apply in every animation workflow. But how you
			<em>create</em> frames differs fundamentally across three approaches. Understanding these differences
			shapes every tool choice you'll make.
		</p>

		<!-- Type cards -->
		<div class="type-grid" id="typeGrid">
			<div
				class="type-card"
				data-type="traditional"
				onclick={(e) => {
					window.selectType(e.currentTarget);
				}}
				role="button"
				tabindex="0"
				onkeydown={(e) => {
					if (e.key === 'Enter') window.selectType(e.currentTarget);
				}}
			>
				<div class="type-icon">✏️</div>
				<div class="type-name">Traditional</div>
				<div class="type-tag">Hand-drawn · Frame-by-frame</div>
				<div class="type-desc">Every frame is drawn by hand. Full control, maximum effort.</div>
			</div>
			<div
				class="type-card"
				data-type="tween"
				onclick={(e) => {
					window.selectType(e.currentTarget);
				}}
				role="button"
				tabindex="0"
				onkeydown={(e) => {
					if (e.key === 'Enter') window.selectType(e.currentTarget);
				}}
			>
				<div class="type-icon">⬦</div>
				<div class="type-name">Tween-based</div>
				<div class="type-tag">Keyframes · Interpolation</div>
				<div class="type-desc">Set start and end positions; software fills in between.</div>
			</div>
			<div
				class="type-card"
				data-type="rig"
				onclick={(e) => {
					window.selectType(e.currentTarget);
				}}
				role="button"
				tabindex="0"
				onkeydown={(e) => {
					if (e.key === 'Enter') window.selectType(e.currentTarget);
				}}
			>
				<div class="type-icon">🦴</div>
				<div class="type-name">Rig-based</div>
				<div class="type-tag">Bones · Hierarchy</div>
				<div class="type-desc">A skeleton drives the character. Pose it frame by frame.</div>
			</div>
			<div
				class="type-card"
				data-type="procedural"
				onclick={(e) => {
					window.selectType(e.currentTarget);
				}}
				role="button"
				tabindex="0"
				onkeydown={(e) => {
					if (e.key === 'Enter') window.selectType(e.currentTarget);
				}}
			>
				<div class="type-icon">⌥</div>
				<div class="type-name">Procedural</div>
				<div class="type-tag">Math · Code</div>
				<div class="type-desc">Motion is computed from equations, not drawn by a human.</div>
			</div>
		</div>

		<div id="typeDetail" class="type-detail"></div>

		<p style="margin-top: 1.5rem">
			This course focuses primarily on <strong>tween-based</strong> and
			<strong>rig-based</strong> workflows, since they are the workhorses of educational video animation.
			You will also encounter procedural concepts when we deal with motion graphs and expression-driven
			animation.
		</p>
	</section>

	<!-- ══════════════════ QUIZ ══════════════════ -->
	<div class="quiz-section" id="quiz">
		<div class="quiz-header-bar">
			<div>
				<div class="quiz-title">Module Check</div>
				<div class="quiz-sub">4 questions · Ungraded</div>
			</div>
			<span class="demo-badge">Assessment</span>
		</div>

		<div class="quiz-body" id="quizBody">
			<!-- Q1 -->
			<div class="question" id="q1">
				<div class="q-num">Q1 of 4</div>
				<div class="q-text">
					What is the primary reason animation creates the illusion of motion?
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
						The images are actually moving on screen
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
						The brain merges quickly-displayed still images into perceived motion
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
						High-resolution images blur together at fast speeds
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
						Pixels change color fast enough to simulate movement
					</div>
				</div>
				<div class="feedback" id="q1-feedback"></div>
			</div>

			<!-- Q2 -->
			<div class="question" id="q2">
				<div class="q-num">Q2 of 4</div>
				<div class="q-text">
					An animation runs for 3 seconds at 24 fps. How many individual frames does it contain?
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
						24
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
						48
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
						72
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
						96
					</div>
				</div>
				<div class="feedback" id="q2-feedback"></div>
			</div>

			<!-- Q3 -->
			<div class="question" id="q3">
				<div class="q-num">Q3 of 4</div>
				<div class="q-text">
					Two balls animate from left to right in 10 frames. Ball A's dots are evenly spaced; Ball
					B's dots are clustered near the start and end. What is different between them?
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
						Their timing — Ball B takes more frames
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
						Their timing — Ball A takes more frames
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
						Their spacing — Ball B has eased motion, Ball A is linear
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
						Their size — Ball A is physically larger
					</div>
				</div>
				<div class="feedback" id="q3-feedback"></div>
			</div>

			<!-- Q4 -->
			<div class="question" id="q4">
				<div class="q-num">Q4 of 4</div>
				<div class="q-text">
					Which animation workflow involves setting only the start and end states, letting software
					calculate the frames in between?
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
						Traditional (hand-drawn)
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
						Tween-based
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
						Rig-based
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
						Procedural
					</div>
				</div>
				<div class="feedback" id="q4-feedback"></div>
			</div>
		</div>

		<div class="quiz-score" id="quizScore">
			<div class="score-big" id="scoreNum">0/4</div>
			<div class="score-lbl">Module 1 Complete</div>
		</div>
	</div>

	<!-- ══════════════════ NEXT ══════════════════ -->
	<nav class="nav-links">
		<a href="/courses/animation/02" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">Timing, Spacing &amp; Weight</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</nav>
</div>

<!-- /page-wrapper -->

<style>
	/* ═══════════════════════════════════════
   ANIMATION COURSE — DESIGN TOKENS
   Warm studio palette, distinct from game dev course
═══════════════════════════════════════ */

	.page-wrapper {
		background: var(--anim-bg);
		color: var(--anim-text);
		font-family: var(--ff-body);
		font-size: 15px;
		line-height: 1.8;
		min-height: 100vh;
	}

	/* ═══════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════ */
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

	/* ═══════════════════════════════════════
   LAYOUT
═══════════════════════════════════════ */
	.page-wrapper {
		max-width: 900px;
		margin: 0 auto;
		padding: 0 2rem 8rem;
	}

	/* ═══════════════════════════════════════
   MODULE HEADER
═══════════════════════════════════════ */
	.module-hero {
		padding: 5rem 0 4rem;
		border-bottom: 1px solid var(--anim-border);
		margin-bottom: 4rem;
		position: relative;
		overflow: hidden;
	}

	/* Animated dots background — film frames motif */
	.hero-frames {
		position: absolute;
		top: 0;
		right: -40px;
		display: flex;
		flex-direction: column;
		gap: 6px;
		opacity: 0.07;
		pointer-events: none;
	}
	:global(.frame-strip) {
		display: flex;
		gap: 6px;
	}
	:global(.frame-cell) {
		width: 32px;
		height: 24px;
		border: 1px solid var(--anim-gold);
		border-radius: 2px;
		flex-shrink: 0;
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
	.module-eyebrow::before {
		content: '';
		display: inline-block;
		width: 24px;
		height: 1px;
		background: var(--anim-gold);
	}
	.module-eyebrow::after {
		content: '';
		display: inline-block;
		width: 24px;
		height: 1px;
		background: var(--anim-gold);
	}

	.module-title {
		font-size: clamp(36px, 6vw, 60px);
		color: #fff;
		margin-bottom: 0.5rem;
		letter-spacing: -0.02em;
	}
	.module-title em {
		color: var(--anim-gold);
		font-style: italic;
	}
	.module-subtitle {
		font-family: var(--ff-body);
		font-size: 16px;
		color: var(--anim-muted);
		font-weight: 400;
		margin-bottom: 2.5rem;
	}

	/* ═══════════════════════════════════════
   OBJECTIVES
═══════════════════════════════════════ */
	.objectives {
		border: 1px solid var(--anim-border);
		border-left: 3px solid var(--anim-gold);
		background: var(--anim-surface);
		padding: 1.5rem 2rem;
		margin-bottom: 1rem;
	}
	.obj-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--anim-gold);
		margin-bottom: 1rem;
	}
	.objectives ul {
		list-style: none;
	}
	.objectives li {
		padding: 0.25rem 0 0.25rem 1.5rem;
		position: relative;
		font-size: 14px;
		color: var(--anim-text);
	}
	.objectives li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--anim-coral);
	}

	/* ═══════════════════════════════════════
   SECTIONS
═══════════════════════════════════════ */
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
		color: var(--anim-coral);
		letter-spacing: 0.1em;
	}
	.section-title {
		font-family: var(--ff-display);
		font-size: 26px;
		color: #fff;
		font-weight: 600;
	}

	/* ═══════════════════════════════════════
   CALLOUT
═══════════════════════════════════════ */
	.callout {
		margin: 1.75rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--anim-lavender);
		background: color-mix(in srgb, var(--anim-lavender) 5%, var(--anim-surface));
		font-size: 13.5px;
	}
	:global(.callout.gold) {
		border-color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 5%, var(--anim-surface));
	}
	.callout.coral {
		border-color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 5%, var(--anim-surface));
	}
	:global(.callout.mint) {
		border-color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 5%, var(--anim-surface));
	}
	.callout-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--anim-lavender);
		margin-bottom: 0.4rem;
		font-weight: 500;
	}
	:global(.callout.gold) .callout-label {
		color: var(--anim-gold);
	}
	.callout.coral .callout-label {
		color: var(--anim-coral);
	}
	:global(.callout.mint) .callout-label {
		color: var(--anim-mint);
	}

	/* ═══════════════════════════════════════
   DEMO BOX
═══════════════════════════════════════ */
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
	:global(.demo-badge) {
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
	.demo-body {
		padding: 1.5rem;
	}

	canvas {
		display: block;
	}

	/* ═══════════════════════════════════════
   CONTROLS
═══════════════════════════════════════ */
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
		min-width: 64px;
	}
	.ctrl-val {
		font-family: var(--ff-mono);
		font-size: 12px;
		color: var(--anim-gold);
		font-weight: 500;
		min-width: 48px;
	}

	:global(input[type='range']) {
		flex: 1;
		-webkit-appearance: none;
		height: 2px;
		background: var(--anim-border2);
		outline: none;
		min-width: 120px;
	}
	:global(input[type='range']::-webkit-slider-thumb) {
		-webkit-appearance: none;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: var(--anim-gold);
		cursor: pointer;
		border: 2px solid var(--anim-bg);
	}

	:global(.btn) {
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
	:global(.btn:hover) {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
	}
	:global(.btn.active) {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 12%, transparent);
	}
	.btn.coral:hover {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
	}
	:global(.btn.coral.active) {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 12%, transparent);
	}
	.btn.mint:hover {
		border-color: var(--anim-mint);
		color: var(--anim-mint);
	}
	:global(.btn.mint.active) {
		border-color: var(--anim-mint);
		color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 12%, transparent);
	}

	:global(.btn-row) {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-top: 1rem;
	}

	/* ═══════════════════════════════════════
   FRAME COUNTER DISPLAY
═══════════════════════════════════════ */
	.frame-counter {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-family: var(--ff-mono);
		font-size: 12px;
		color: var(--anim-muted);
	}
	.frame-counter span {
		color: var(--anim-gold);
		font-weight: 500;
		font-size: 14px;
	}

	/* ═══════════════════════════════════════
   FILMSTRIP
═══════════════════════════════════════ */
	.filmstrip {
		display: flex;
		gap: 4px;
		overflow-x: auto;
		padding: 0.75rem 0;
		scrollbar-width: thin;
	}
	:global(.film-frame) {
		flex-shrink: 0;
		width: 60px;
		height: 44px;
		border: 1px solid var(--anim-border2);
		cursor: pointer;
		transition: border-color 0.15s;
		position: relative;
		overflow: hidden;
	}
	:global(.film-frame.active) {
		border-color: var(--anim-gold);
	}
	:global(.film-frame) canvas {
		width: 100%;
		height: 100%;
	}
	:global(.film-frame-num) {
		position: absolute;
		bottom: 2px;
		right: 3px;
		font-family: var(--ff-mono);
		font-size: 8px;
		color: var(--anim-dim);
		pointer-events: none;
	}

	/* ═══════════════════════════════════════
   COMPARISON GRID (animation types)
═══════════════════════════════════════ */
	.type-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1px;
		background: var(--anim-border);
		border: 1px solid var(--anim-border);
		margin: 1.5rem 0;
	}
	.type-card {
		background: var(--anim-surface);
		padding: 1.5rem;
		cursor: pointer;
		transition: background 0.15s;
	}
	.type-card:hover {
		background: var(--anim-raised);
	}
	.type-card.active {
		background: color-mix(in srgb, var(--anim-gold) 6%, var(--anim-surface));
	}
	.type-icon {
		font-size: 24px;
		margin-bottom: 0.5rem;
	}
	.type-name {
		font-family: var(--ff-display);
		font-size: 16px;
		font-weight: 600;
		color: #fff;
		margin-bottom: 0.25rem;
	}
	.type-tag {
		font-family: var(--ff-mono);
		font-size: 9px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--anim-muted);
		margin-bottom: 0.75rem;
	}
	.type-desc {
		font-size: 13px;
		color: var(--anim-muted);
		line-height: 1.6;
	}
	.type-detail {
		display: none;
		padding: 1.25rem 1.5rem;
		background: color-mix(in srgb, var(--anim-gold) 4%, var(--anim-raised));
		border-top: 1px solid var(--anim-border);
		font-size: 13px;
		line-height: 1.7;
	}
	.type-detail.visible {
		display: block;
	}
	.type-detail strong {
		color: var(--anim-gold);
	}

	/* ═══════════════════════════════════════
   QUIZ
═══════════════════════════════════════ */
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
	:global(.question) {
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

	/* ═══════════════════════════════════════
   PROGRESS / NAV
═══════════════════════════════════════ */
	.divider {
		border: none;
		border-top: 1px solid var(--anim-border);
		margin: 3rem 0;
	}

	.nav-links {
		display: flex;
		justify-content: flex-end;
		margin-top: 4rem;
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
		min-width: 280px;
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
		.type-grid {
			grid-template-columns: 1fr;
		}
		.page-wrapper {
			padding: 0 1.25rem 6rem;
		}
	}

	/* small stat badges */
	.stat-row-mini {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		margin-top: 0.75rem;
	}
	.stat-badge {
		display: flex;
		flex-direction: column;
		background: var(--anim-raised);
		border: 1px solid var(--anim-border);
		padding: 0.4rem 0.75rem;
		min-width: 72px;
	}
	.stat-badge .sv {
		font-family: var(--ff-mono);
		font-size: 18px;
		font-weight: 500;
		color: var(--anim-gold);
		line-height: 1.2;
	}
	.stat-badge .sk {
		font-family: var(--ff-mono);
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--anim-muted);
	}

	/* timing/spacing two-track layout */
	.two-track {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1px;
		background: var(--anim-border);
		margin: 1rem 0;
	}
	.track-panel {
		background: var(--anim-surface);
		padding: 1rem 1.25rem 0.75rem;
	}
	.track-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--anim-muted);
		margin-bottom: 0.5rem;
	}
	.track-label span {
		color: var(--anim-gold);
	}
	.track-label.coral span {
		color: var(--anim-coral);
	}
	@media (max-width: 600px) {
		.two-track {
			grid-template-columns: 1fr;
		}
	}
</style>
