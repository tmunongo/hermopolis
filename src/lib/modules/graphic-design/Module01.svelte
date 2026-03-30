<script lang="ts">
	/* eslint-disable @typescript-eslint/no-unused-vars, svelte/prefer-svelte-reactivity */
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
		/* ══════════════════════════════════
   READING PROGRESS
══════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const progress = el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight);
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width = progress * 100 + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		/* ══════════════════════════════════
   STRUCTURE REVEAL DEMO
══════════════════════════════════ */
		const srCanvas = document.getElementById('sr-canvas');
		const srCtx = srCanvas.getContext('2d');
		const W = srCanvas.width,
			H = srCanvas.height;

		const activeLayers = new Set();

		const layerDescriptions = {
			grid: '<strong style="color:var(--violet)">Rule of Thirds Grid</strong> — The subject falls near a thirds intersection, not dead-center. The horizon sits on the lower third line. This creates natural tension and visual interest.',
			hierarchy:
				'<strong style="color:var(--rose)">Visual Hierarchy</strong> — Three tiers: the large face (primary), the title text (secondary), the supporting label (tertiary). The eye moves through them in order of size and contrast.',
			alignment:
				'<strong style="color:var(--sky)">Alignment Axes</strong> — Text elements share a left edge. The subject\'s eye line aligns with the title baseline. Nothing is placed arbitrarily.',
			focal:
				'<strong style="color:var(--amber)">Focal Point</strong> — The single highest-contrast element anchors viewer attention before anything else registers. In thumbnails, this must read at thumbnail scale.',
			spacing:
				'<strong style="color:var(--sage)">Spacing System</strong> — Consistent margins and breathing room separate elements without making the composition feel empty. Crowding is the most common beginner mistake.'
		};

		function drawBaseThumb() {
			const ctx = srCtx;
			// Background
			ctx.fillStyle = '#0f1c2e';
			ctx.fillRect(0, 0, W, H);

			// Sky gradient suggestion
			const sky = ctx.createLinearGradient(0, 0, 0, H * 0.6);
			sky.addColorStop(0, '#0d2140');
			sky.addColorStop(1, '#0f1c2e');
			ctx.fillStyle = sky;
			ctx.fillRect(0, 0, W, Math.floor(H * 0.65));

			// Stylized "subject" silhouette — a figure at left-third
			ctx.fillStyle = '#1a3050';
			ctx.beginPath();
			ctx.ellipse(Math.floor(W * 0.32), Math.floor(H * 0.38), 60, 70, 0, 0, Math.PI * 2);
			ctx.fill();
			// body
			ctx.fillStyle = '#243a55';
			ctx.fillRect(Math.floor(W * 0.32) - 40, Math.floor(H * 0.5), 80, Math.floor(H * 0.5));

			// Face highlight (oval)
			ctx.fillStyle = '#e8c9a0';
			ctx.beginPath();
			ctx.ellipse(Math.floor(W * 0.32), Math.floor(H * 0.36), 36, 42, 0, 0, Math.PI * 2);
			ctx.fill();

			// Eyes (focal indicator)
			ctx.fillStyle = '#1a2535';
			ctx.beginPath();
			ctx.ellipse(Math.floor(W * 0.32) - 12, Math.floor(H * 0.33), 5, 4, 0, 0, Math.PI * 2);
			ctx.ellipse(Math.floor(W * 0.32) + 12, Math.floor(H * 0.33), 5, 4, 0, 0, Math.PI * 2);
			ctx.fill();

			// Title text block
			ctx.fillStyle = '#ffffff';
			ctx.font = `bold ${Math.floor(H * 0.09)}px 'Syne', sans-serif`;
			ctx.fillText('HOW TO', Math.floor(W * 0.48), Math.floor(H * 0.42));

			ctx.fillStyle = '#f5a623';
			ctx.font = `bold ${Math.floor(H * 0.12)}px 'Syne', sans-serif`;
			ctx.fillText('STAND OUT', Math.floor(W * 0.46), Math.floor(H * 0.58));

			ctx.fillStyle = '#90a8c0';
			ctx.font = `${Math.floor(H * 0.06)}px 'IBM Plex Mono', monospace`;
			ctx.fillText('without being loud', Math.floor(W * 0.48), Math.floor(H * 0.73));

			// Bottom bar
			ctx.fillStyle = '#0a1520';
			ctx.fillRect(0, Math.floor(H * 0.88), W, Math.floor(H * 0.12));
			ctx.fillStyle = '#5a7090';
			ctx.font = `${Math.floor(H * 0.055)}px 'IBM Plex Mono', monospace`;
			ctx.fillText('Design Fundamentals  •  Episode 01', 16, Math.floor(H * 0.96));
		}

		function drawLayers() {
			const ctx = srCtx;

			if (activeLayers.has('grid')) {
				ctx.strokeStyle = 'rgba(155, 109, 255, 0.45)';
				ctx.lineWidth = 1;
				ctx.setLineDash([4, 4]);
				// thirds lines
				for (let i = 1; i < 3; i++) {
					ctx.beginPath();
					ctx.moveTo(Math.floor((W * i) / 3), 0);
					ctx.lineTo(Math.floor((W * i) / 3), H);
					ctx.stroke();
					ctx.beginPath();
					ctx.moveTo(0, Math.floor((H * i) / 3));
					ctx.lineTo(W, Math.floor((H * i) / 3));
					ctx.stroke();
				}
				// intersection dots
				ctx.fillStyle = 'rgba(155, 109, 255, 0.9)';
				for (let xi = 1; xi < 3; xi++)
					for (let yi = 1; yi < 3; yi++) {
						ctx.beginPath();
						ctx.arc(Math.floor((W * xi) / 3), Math.floor((H * yi) / 3), 4, 0, Math.PI * 2);
						ctx.fill();
					}
				ctx.setLineDash([]);
			}

			if (activeLayers.has('hierarchy')) {
				// tier 1 — face
				ctx.strokeStyle = 'rgba(232, 93, 138, 0.8)';
				ctx.lineWidth = 2;
				ctx.strokeRect(Math.floor(W * 0.32) - 44, Math.floor(H * 0.1), 88, Math.floor(H * 0.55));
				ctx.fillStyle = 'rgba(232, 93, 138, 0.8)';
				ctx.font = '10px IBM Plex Mono';
				ctx.fillText('TIER 1 — Primary', Math.floor(W * 0.32) - 44, Math.floor(H * 0.1) - 4);

				// tier 2 — title
				ctx.strokeStyle = 'rgba(245, 166, 35, 0.7)';
				ctx.strokeRect(
					Math.floor(W * 0.45),
					Math.floor(H * 0.32),
					Math.floor(W * 0.5),
					Math.floor(H * 0.34)
				);
				ctx.fillStyle = 'rgba(245, 166, 35, 0.7)';
				ctx.fillText('TIER 2 — Secondary', Math.floor(W * 0.45), Math.floor(H * 0.32) - 4);

				// tier 3 — sub
				ctx.strokeStyle = 'rgba(86, 208, 160, 0.6)';
				ctx.setLineDash([3, 3]);
				ctx.strokeRect(
					Math.floor(W * 0.46),
					Math.floor(H * 0.67),
					Math.floor(W * 0.48),
					Math.floor(H * 0.1)
				);
				ctx.fillStyle = 'rgba(86, 208, 160, 0.6)';
				ctx.font = '9px IBM Plex Mono';
				ctx.fillText('TIER 3', Math.floor(W * 0.46), Math.floor(H * 0.67) - 3);
				ctx.setLineDash([]);
			}

			if (activeLayers.has('alignment')) {
				ctx.strokeStyle = 'rgba(56, 192, 232, 0.6)';
				ctx.lineWidth = 1;
				ctx.setLineDash([6, 3]);
				// left edge of text column
				const textX = Math.floor(W * 0.47);
				ctx.beginPath();
				ctx.moveTo(textX, 0);
				ctx.lineTo(textX, H);
				ctx.stroke();
				// eye-line / title baseline
				const eyeY = Math.floor(H * 0.395);
				ctx.beginPath();
				ctx.moveTo(0, eyeY);
				ctx.lineTo(W, eyeY);
				ctx.stroke();
				ctx.setLineDash([]);
				ctx.fillStyle = 'rgba(56, 192, 232, 0.85)';
				ctx.font = '9px IBM Plex Mono';
				ctx.fillText('LEFT AXIS', textX + 4, 14);
				ctx.fillText('EYE LINE / TITLE BASELINE', 4, eyeY - 4);
			}

			if (activeLayers.has('focal')) {
				// Radial highlight on eye area
				const fx = Math.floor(W * 0.32),
					fy = Math.floor(H * 0.33);
				const grad = ctx.createRadialGradient(fx, fy, 0, fx, fy, 90);
				grad.addColorStop(0, 'rgba(245, 166, 35, 0.25)');
				grad.addColorStop(1, 'rgba(245, 166, 35, 0)');
				ctx.fillStyle = grad;
				ctx.beginPath();
				ctx.arc(fx, fy, 90, 0, Math.PI * 2);
				ctx.fill();
				// Ring
				ctx.strokeStyle = 'rgba(245, 166, 35, 0.9)';
				ctx.lineWidth = 1.5;
				ctx.beginPath();
				ctx.arc(fx, fy, 52, 0, Math.PI * 2);
				ctx.stroke();
				ctx.fillStyle = 'rgba(245, 166, 35, 0.9)';
				ctx.font = '9px IBM Plex Mono';
				ctx.fillText('FOCAL POINT', fx - 32, fy + 65);
			}

			if (activeLayers.has('spacing')) {
				ctx.strokeStyle = 'rgba(86, 208, 160, 0.5)';
				ctx.lineWidth = 1;
				ctx.setLineDash([2, 4]);
				// Margin guides
				const mg = 16;
				ctx.strokeRect(mg, mg, W - mg * 2, H - mg * 2);
				// Gap between subject and text
				const gapX1 = Math.floor(W * 0.32) + 48;
				const gapX2 = Math.floor(W * 0.47);
				ctx.beginPath();
				ctx.moveTo(gapX1, Math.floor(H * 0.5));
				ctx.lineTo(gapX2, Math.floor(H * 0.5));
				ctx.stroke();
				ctx.fillStyle = 'rgba(86, 208, 160, 0.75)';
				ctx.font = '9px IBM Plex Mono';
				ctx.fillText('← breathing room →', gapX1 + 2, Math.floor(H * 0.5) - 4);
				ctx.fillText('MARGIN', mg + 4, H - mg - 4);
				ctx.setLineDash([]);
			}
		}

		function redrawSR() {
			drawBaseThumb();
			drawLayers();
		}

		function toggleLayer(btn) {
			const layer = btn.dataset.layer;
			if (activeLayers.has(layer)) {
				activeLayers.delete(layer);
				btn.classList.remove('active');
			} else {
				activeLayers.add(layer);
				btn.classList.add('active');
			}

			const parts = [];
			activeLayers.forEach((l) => parts.push(layerDescriptions[l]));
			document.getElementById('layer-desc').innerHTML = parts.length
				? parts.join('<br><br>')
				: 'Activate a layer above to reveal a structural principle hidden in this composition.';

			redrawSR();
		}

		redrawSR();

		/* ══════════════════════════════════
   TASTE vs SKILL SLIDER
══════════════════════════════════ */
		const tsTrack = document.getElementById('ts-track');
		const tsThumb = document.getElementById('ts-thumb');
		const tsFill = document.getElementById('ts-fill');
		const tsOut = document.getElementById('ts-output');
		const tsHead = document.getElementById('ts-heading');
		const tsBody = document.getElementById('ts-body');

		let tsDragging = false;

		const tsStages = [
			{
				pct: 0,
				mode: 'violet-mode',
				heading: 'Beginning Designer',
				body: "You notice when something is wrong but can't fix it yet. You feel frustrated because the work in your head looks better than the work on screen. This is the correct starting condition. This is where everyone starts."
			},
			{
				pct: 33,
				mode: 'violet-mode',
				heading: 'Building Vocabulary',
				body: "You've learned the names for things: hierarchy, contrast, alignment. You can now say why something fails, not just that it does. This is the most important phase — naming things gives you handles to work with."
			},
			{
				pct: 55,
				mode: 'mix-mode',
				heading: 'The Productive Gap',
				body: 'Your taste is outrunning your skill by a visible margin. This feels painful but is actually a sign of progress. The gap narrows every time you finish a piece, get feedback, and make another one.'
			},
			{
				pct: 75,
				mode: 'mix-mode',
				heading: 'Skill Approaching Taste',
				body: 'Your output is now reliable. You can produce work that matches your internal standards more often than not. You still see the gap, but it motivates rather than paralyzes.'
			},
			{
				pct: 100,
				mode: 'rose-mode',
				heading: 'Taste and Skill Aligned',
				body: "You can execute what you imagine. Your taste continues to evolve, which means the gap never fully closes — but now it pulls you forward rather than holding you back. This is the working designer's permanent condition."
			}
		];

		function setThumb(pct) {
			pct = Math.max(0, Math.min(100, pct));
			tsThumb.style.left = pct + '%';
			tsFill.style.width = pct + '%';

			let stage = tsStages[0];
			for (const s of tsStages) {
				if (pct >= s.pct) stage = s;
			}

			tsOut.className = 'ts-output ' + stage.mode;
			tsHead.textContent = stage.heading;
			tsBody.textContent = stage.body;
		}

		tsTrack.addEventListener('mousedown', (e) => {
			tsDragging = true;
			moveDrag(e);
		});
		_addDocListener('mousemove', (e) => {
			if (tsDragging) moveDrag(e);
		});
		_addDocListener('mouseup', () => {
			tsDragging = false;
		});
		tsTrack.addEventListener('touchstart', (e) => {
			tsDragging = true;
			moveDrag(e.touches[0]);
		});
		_addDocListener('touchmove', (e) => {
			if (tsDragging) moveDrag(e.touches[0]);
		});
		_addDocListener('touchend', () => {
			tsDragging = false;
		});

		function moveDrag(e) {
			const rect = tsTrack.getBoundingClientRect();
			const pct = ((e.clientX - rect.left) / rect.width) * 100;
			setThumb(pct);
		}

		setThumb(10);

		/* ══════════════════════════════════
   TEMPLATE vs CUSTOM DEMO
══════════════════════════════════ */
		const tcT = document.getElementById('cv-template');
		const tcC = document.getElementById('cv-custom');
		const ctxT = tcT.getContext('2d');
		const ctxC = tcC.getContext('2d');

		function drawTemplate() {
			const ctx = ctxT,
				w = tcT.width,
				h = tcT.height;
			// Generic gradient background
			const g = ctx.createLinearGradient(0, 0, w, h);
			g.addColorStop(0, '#1a1060');
			g.addColorStop(1, '#3a1580');
			ctx.fillStyle = g;
			ctx.fillRect(0, 0, w, h);

			// Decorative circles (template cliché)
			ctx.fillStyle = 'rgba(255,255,255,0.05)';
			ctx.beginPath();
			ctx.arc(w * 0.8, h * 0.2, 80, 0, Math.PI * 2);
			ctx.fill();
			ctx.beginPath();
			ctx.arc(w * 0.1, h * 0.8, 60, 0, Math.PI * 2);
			ctx.fill();

			// Centered title (dead center — no hierarchy)
			ctx.fillStyle = '#ffffff';
			ctx.font = 'bold 22px Syne, sans-serif';
			ctx.textAlign = 'center';
			ctx.fillText('MY AMAZING VIDEO', w / 2, h * 0.42);

			// Subtitle (same weight, no differentiation)
			ctx.fillStyle = '#cccccc';
			ctx.font = '14px IBM Plex Mono, monospace';
			ctx.fillText("You Won't Believe This!", w / 2, h * 0.58);

			// Generic divider
			ctx.strokeStyle = 'rgba(255,255,255,0.3)';
			ctx.lineWidth = 1;
			ctx.beginPath();
			ctx.moveTo(w * 0.2, h * 0.48);
			ctx.lineTo(w * 0.8, h * 0.48);
			ctx.stroke();

			// Watermark badge
			ctx.fillStyle = 'rgba(255,255,255,0.15)';
			ctx.fillRect(w - 90, h - 24, 84, 18);
			ctx.fillStyle = '#aaa';
			ctx.font = '9px IBM Plex Mono, monospace';
			ctx.fillText('MADE WITH CANVA', w - 84, h - 11);

			ctx.textAlign = 'left';
		}

		function drawCustom() {
			const ctx = ctxC,
				w = tcC.width,
				h = tcC.height;
			// Specific, intentional dark background
			ctx.fillStyle = '#080b10';
			ctx.fillRect(0, 0, w, h);

			// Left accent bar
			ctx.fillStyle = '#e85d8a';
			ctx.fillRect(0, 0, 4, h);

			// Subject area — implied photo block (left third)
			ctx.fillStyle = '#111822';
			ctx.fillRect(4, 0, Math.floor(w * 0.38), h);
			// Face shape
			ctx.fillStyle = '#d4a07a';
			ctx.beginPath();
			ctx.ellipse(Math.floor(w * 0.2), Math.floor(h * 0.4), 38, 44, 0, 0, Math.PI * 2);
			ctx.fill();
			ctx.fillStyle = '#111822';
			ctx.fillRect(Math.floor(w * 0.2) - 38, Math.floor(h * 0.6), 76, h);

			// Eyeline detail
			ctx.fillStyle = '#1a2535';
			ctx.beginPath();
			ctx.ellipse(Math.floor(w * 0.2) - 12, Math.floor(h * 0.37), 4, 3.5, 0, 0, Math.PI * 2);
			ctx.ellipse(Math.floor(w * 0.2) + 12, Math.floor(h * 0.37), 4, 3.5, 0, 0, Math.PI * 2);
			ctx.fill();

			// Text area — deliberate left alignment
			const tx = Math.floor(w * 0.43);

			// Eyebrow label
			ctx.fillStyle = '#e85d8a';
			ctx.font = '9px IBM Plex Mono, monospace';
			ctx.fillText('DESIGN SERIES', tx, Math.floor(h * 0.28));

			// Title — large, high contrast, specific
			ctx.fillStyle = '#ffffff';
			ctx.font = `bold ${Math.floor(h * 0.17)}px Syne, sans-serif`;
			ctx.fillText('STAND', tx, Math.floor(h * 0.48));
			ctx.fillStyle = '#f5a623';
			ctx.fillText('OUT', tx, Math.floor(h * 0.68));

			// Sub — tertiary, muted
			ctx.fillStyle = '#5a7090';
			ctx.font = '9px IBM Plex Mono, monospace';
			ctx.fillText('without being loud', tx, Math.floor(h * 0.84));

			// Bottom edge accent
			ctx.fillStyle = '#e85d8a';
			ctx.fillRect(0, h - 2, w, 2);
		}

		let issuesVisible = false;

		function toggleIssues() {
			issuesVisible = !issuesVisible;
			const btn = document.getElementById('show-issues-btn');
			const tIssues = document.getElementById('template-issues');
			const cStrengths = document.getElementById('custom-strengths');
			const detail = document.getElementById('compare-detail');

			if (issuesVisible) {
				btn.textContent = 'Hide Analysis';
				btn.classList.add('active');
				tIssues.style.display = 'flex';
				cStrengths.style.display = 'flex';

				tIssues.innerHTML = `
      <li class="problem">Dead-center placement — no visual tension or hierarchy</li>
      <li class="problem">Both text elements share the same visual weight — the eye has no clear path</li>
      <li class="problem">Decorative circles serve no communicative purpose</li>
      <li class="problem">Generic gradient communicates no specific topic or tone</li>
      <li class="problem">"You Won't Believe This!" — borrowed voice, not a distinctive identity</li>
    `;
				cStrengths.innerHTML = `
      <li class="strength">Subject in left third — creates tension, eye moves right to text</li>
      <li class="strength">Three distinct text tiers: eyebrow / primary title / sub-label</li>
      <li class="strength">Specific color palette communicates a consistent identity</li>
      <li class="strength">Every element has a job — nothing is decorative</li>
      <li class="strength">Accent bars add structure, not just decoration</li>
    `;
				detail.innerHTML = `
      Both thumbnails are for the same hypothetical video. The template version follows a predictable pattern that could belong to any channel. 
      The designed version communicates a specific identity: a consistent color language, deliberate hierarchy, 
      and a layout where every element has a defined role. <em style="color:#fff;">The difference is intentionality.</em>
    `;
			} else {
				btn.textContent = 'Show Analysis';
				btn.classList.remove('active');
				tIssues.style.display = 'none';
				cStrengths.style.display = 'none';
				detail.textContent =
					'Press "Show Analysis" to reveal the structural differences between these two approaches.';
			}
		}

		function resetComparison() {
			issuesVisible = false;
			const btn = document.getElementById('show-issues-btn');
			btn.textContent = 'Show Analysis';
			btn.classList.remove('active');
			document.getElementById('template-issues').style.display = 'none';
			document.getElementById('custom-strengths').style.display = 'none';
			document.getElementById('compare-detail').textContent =
				'Press "Show Analysis" to reveal the structural differences between these two approaches.';
		}

		drawTemplate();
		drawCustom();

		/* ══════════════════════════════════
   QUIZ
══════════════════════════════════ */
		let quizScore = 0;
		let quizAnswered = 0;
		const TOTAL_Q = 5;

		const explanations = [
			'Correct. Design thinking starts with the communication constraint, not the aesthetic preference.',
			"Correct. Hierarchy is about directing the viewer's eye through a deliberate sequence — size, contrast, weight, and position all contribute.",
			'Correct. This is the classic Ira Glass gap: taste (the ability to recognize quality) developing ahead of skill (the ability to produce it).',
			"Correct. Templates are optimized to appeal to the general case, which means they can't express a specific identity.",
			"Correct. The structural decisions — alignment, hierarchy, spacing — disappear in the final work precisely because they've done their job."
		];
		const wrongMsg =
			'Not quite. Think about what distinguishes design as a discipline from mere decoration or imitation.';

		function handleQuiz(el, idx) {
			const parent = el.closest('.question');
			const correct = parseInt(parent.querySelector('.options').dataset.correct);
			const opts = parent.querySelectorAll('.option');
			const fbId = 'fb-' + Array.from(document.querySelectorAll('.question')).indexOf(parent);
			const fb = document.getElementById(fbId);

			if (el.classList.contains('disabled')) return;
			opts.forEach((o) => o.classList.add('disabled'));

			if (idx === correct) {
				el.classList.add('correct');
				fb.textContent = '✓ ' + explanations[parseInt(fbId.split('-')[1])];
				fb.className = 'feedback ok';
				quizScore++;
			} else {
				el.classList.add('wrong');
				opts[correct].classList.add('correct');
				fb.textContent = '✗ ' + wrongMsg;
				fb.className = 'feedback bad';
			}

			quizAnswered++;
			if (quizAnswered === TOTAL_Q) {
				const scoreEl = document.getElementById('quiz-score');
				document.getElementById('score-num').textContent = quizScore + ' / ' + TOTAL_Q;
				scoreEl.style.display = 'block';
				setTimeout(() => scoreEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 300);
			}
		}

		/* ══════════════════════════════════
   ASSESSMENT / REFLECTION
══════════════════════════════════ */
		const reflectArea = document.getElementById('reflect-area');
		const charCount = document.getElementById('char-count');
		const reflectFb = document.getElementById('reflect-feedback');

		reflectArea.addEventListener('input', () => {
			const n = reflectArea.value.length;
			charCount.textContent = n + ' / 200+ characters';
			charCount.style.color = n >= 200 ? 'var(--sage)' : 'var(--muted)';
		});

		function submitReflection() {
			const n = reflectArea.value.trim().length;
			if (n < 80) {
				reflectFb.textContent =
					'↑ Try to push further — describe at least one structural element specifically.';
				reflectFb.style.color = 'var(--rose)';
				return;
			}
			reflectFb.textContent =
				'✓ Reflection recorded. This kind of structural observation is the foundation of design literacy.';
			reflectFb.style.color = 'var(--sage)';
		}

		if (typeof drawBaseThumb === 'function') actions.drawBaseThumb = drawBaseThumb;
		if (typeof drawLayers === 'function') actions.drawLayers = drawLayers;
		if (typeof redrawSR === 'function') actions.redrawSR = redrawSR;
		if (typeof toggleLayer === 'function') actions.toggleLayer = toggleLayer;
		if (typeof setThumb === 'function') actions.setThumb = setThumb;
		if (typeof moveDrag === 'function') actions.moveDrag = moveDrag;
		if (typeof drawTemplate === 'function') actions.drawTemplate = drawTemplate;
		if (typeof drawCustom === 'function') actions.drawCustom = drawCustom;
		if (typeof toggleIssues === 'function') actions.toggleIssues = toggleIssues;
		if (typeof resetComparison === 'function') actions.resetComparison = resetComparison;
		if (typeof handleQuiz === 'function') actions.handleQuiz = handleQuiz;
		if (typeof submitReflection === 'function') actions.submitReflection = submitReflection;

		return () => {
			_listeners.forEach((l) => l.target.removeEventListener(...l.args));
		};
	});
</script>

<div class="page-wrapper">
	<!-- COURSE HEADER -->
	<header class="course-header">
		<div>
			<div class="course-label">Graphic Design &amp; Visual Storytelling</div>
			<div class="course-title">Building a Personal Creative Identity</div>
		</div>
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 01 of 10</div>
	</header>

	<!-- HERO -->
	<div class="module-hero">
		<div class="module-number">01</div>
		<div class="module-tag">Module 01 · Foundations</div>
		<h1 class="module-title">What Design<br /><span>Is (and Isn't)</span></h1>
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
			<li><a href="#design-as-problem">Design as Problem-Solving</a></li>
			<li><a href="#invisible-structure">The Invisible Structure</a></li>
			<li><a href="#taste-vs-skill">Taste vs Skill</a></li>
			<li><a href="#template-problem">The Template Problem</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<!-- OBJECTIVES -->
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand what graphic design actually involves — and what it doesn't</li>
			<li>Identify the difference between "taste" and "skill" and why you already have both</li>
			<li>Understand why templates fail to create authentic visual identity</li>
		</ul>
	</section>

	<!-- ══════════════════════════════════
       SECTION 1: DESIGN AS PROBLEM-SOLVING
  ══════════════════════════════════ -->
	<section id="design-as-problem" class="section">
		<div class="section-header">
			<span class="section-num">01.01</span>
			<h2 class="section-title">Design as Intentional Problem-Solving</h2>
		</div>

		<p>
			Most people's first instinct is to think of graphic design as decoration — the act of making
			things look nice. This is understandable, because the end product is always visual. But it is
			wrong, and the misunderstanding is what makes beginners feel like they need to be "creative"
			or "artistic" before they can start.
		</p>

		<p>
			<em>Design is the act of solving a communication problem using visual means.</em> Every design
			decision — what font to use, how large to make something, what color to choose, where to place
			an element — is an answer to a specific question:
			<strong>What does this need to communicate, and to whom?</strong>
		</p>

		<div class="callout">
			<div class="callout-label">Core Principle</div>
			A logo isn't beautiful because the designer was talented. It's beautiful because every element does
			a specific job. The elegance is a byproduct of clarity, not its cause.
		</div>

		<p>
			Consider a YouTube thumbnail. Its job is brutally specific: be legible at 168×94 pixels,
			communicate the video's topic in under two seconds, and generate enough curiosity to earn a
			click — all while competing with dozens of other thumbnails. That is an engineering problem as
			much as a visual one. The designer's job is to solve it. The visual output is just the
			solution.
		</p>

		<p>
			This reframing matters practically. When you sit down to design something, instead of asking <em
				>"What should this look like?"</em
			>, you ask:
			<em>"What does this need to do?"</em> The first question paralyzes. The second gives you somewhere
			to start.
		</p>

		<table>
			<thead>
				<tr>
					<th>Design Object</th>
					<th>Communication Problem It Solves</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Logo</td>
					<td>Identify a brand at a glance across any surface</td>
				</tr>
				<tr>
					<td>Thumbnail</td>
					<td>Generate a click from a 168px wide image in under 2 seconds</td>
				</tr>
				<tr>
					<td>Website header</td>
					<td>Answer "What is this?" before the user decides to scroll</td>
				</tr>
				<tr>
					<td>Explainer diagram</td>
					<td>Make one specific idea impossible to misunderstand</td>
				</tr>
				<tr>
					<td>Title card</td>
					<td>Set the visual tone before the video's first word</td>
				</tr>
			</tbody>
		</table>

		<div class="callout green">
			<div class="callout-label">Key Insight</div>
			You have been solving problems your whole life. Design is just problem-solving with visual tools.
			You are not starting from nothing.
		</div>
	</section>

	<!-- ══════════════════════════════════
       SECTION 2: INVISIBLE STRUCTURE
  ══════════════════════════════════ -->
	<section id="invisible-structure" class="section">
		<div class="section-header">
			<span class="section-num">01.02</span>
			<h2 class="section-title">The Invisible Structure Behind Good Design</h2>
		</div>

		<p>
			When you look at a design you find beautiful, you typically cannot explain why. It "just
			works." This is by intention. Good design hides its scaffolding. What you're responding to —
			the sense of order, clarity, and intention — is produced by underlying decisions about
			<strong>hierarchy</strong>, <strong>alignment</strong>, <strong>spacing</strong>, and
			<strong>contrast</strong>. These are learnable. They are rules, not intuitions.
		</p>

		<p>
			Visual <em>hierarchy</em> is the practice of arranging elements so that the eye encounters them
			in a specific order — most important first, least important last. It is achieved through size, weight,
			color, position, and contrast. Without hierarchy, every element competes for attention equally,
			and the viewer's eye has nowhere to land.
		</p>

		<p>
			<em>Alignment</em> is the practice of placing elements along invisible lines. When elements share
			an edge or a center axis, they feel intentional. When they don't, a design feels messy even if you
			can't say why. Alignment creates the invisible grid that gives professional design its sense of
			order.
		</p>

		<p>
			The interactive below lets you reveal these invisible layers on a composed thumbnail. Notice
			how the structure — the grid, the focal point, the hierarchy — becomes visible the moment you
			look for it.
		</p>

		<!-- DEMO: Structure Reveal -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Structure Reveal</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Toggle the overlay layers to reveal the invisible structure beneath a YouTube-style
					thumbnail composition.
				</p>

				<div class="layer-btns" id="layer-btns">
					<button
						class="btn"
						data-layer="grid"
						onclick={(e) => actions.toggleLayer(e.currentTarget)}>Grid</button
					>
					<button
						class="btn"
						data-layer="hierarchy"
						onclick={(e) => actions.toggleLayer(e.currentTarget)}
					>
						Hierarchy
					</button>
					<button
						class="btn"
						data-layer="alignment"
						onclick={(e) => actions.toggleLayer(e.currentTarget)}
					>
						Alignment
					</button>
					<button
						class="btn"
						data-layer="focal"
						onclick={(e) => actions.toggleLayer(e.currentTarget)}
					>
						Focal Point
					</button>
					<button
						class="btn"
						data-layer="spacing"
						onclick={(e) => actions.toggleLayer(e.currentTarget)}>Spacing</button
					>
				</div>

				<div class="sr-canvas-wrap">
					<canvas
						id="sr-canvas"
						width="560"
						height="315"
						style="max-width: 100%"
						aria-label="Sr Canvas Demonstration"
						role="region"
						tabindex="0"
					></canvas>
				</div>
				<div class="layer-desc" id="layer-desc">
					Activate a layer above to reveal a structural principle hidden in this composition.
				</div>
			</div>
		</div>

		<div class="callout info">
			<div class="callout-label">Notice</div>
			Every layer you toggled existed in the original — you just couldn't see it consciously. Training
			your eye to notice structure is what separates designers from everyone else looking at the same
			image.
		</div>
	</section>

	<!-- ══════════════════════════════════
       SECTION 3: TASTE VS SKILL
  ══════════════════════════════════ -->
	<section id="taste-vs-skill" class="section">
		<div class="section-header">
			<span class="section-num">01.03</span>
			<h2 class="section-title">Taste vs Skill — and Why You Already Have Both</h2>
		</div>

		<p>
			<em>Taste</em> is the ability to recognize quality. It is the voice that says "something feels off"
			about a design, or "this is good" without being able to articulate why. Most people assume this
			is a gift. It is not. Taste is developed by exposure — by looking at a lot of things and forming
			opinions.
		</p>

		<p>
			<em>Skill</em> is the ability to produce quality. It is knowing <em>why</em> something feels off,
			and knowing what to do about it. Skill is entirely learnable through practice and feedback.
		</p>

		<p>
			Here is what Ira Glass — a radio producer, not a designer — described as the most important
			thing beginners need to understand: you got into a creative field because your taste was
			already good. But in the beginning, your skill hasn't caught up. This gap is uncomfortable but
			temporary. Everyone who is good at creative work went through it.
		</p>

		<div class="callout">
			<div class="callout-label">The Gap</div>
			When you look at your own work and think "this isn't as good as I want it to be" — that feeling
			is your taste working correctly. It is proof you have standards. Skill is just taste expressed with
			tools.
		</div>

		<!-- DEMO: Taste vs Skill Slider -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Taste vs Skill Spectrum</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Drag the slider to explore what it means to have each combination of taste and skill.
				</p>

				<div class="taste-skill-wrap">
					<div class="ts-labels">
						<span>High Taste · Low Skill</span>
						<span>High Taste · High Skill</span>
					</div>
					<div class="ts-track" id="ts-track">
						<div class="ts-fill" id="ts-fill" style="width: 10%"></div>
						<div class="ts-thumb" id="ts-thumb" style="left: 10%"></div>
					</div>
					<div class="ts-output violet-mode" id="ts-output">
						<div class="ts-heading" id="ts-heading">Beginning Designer</div>
						<div id="ts-body">
							You notice when something is wrong but can't fix it yet. You feel frustrated because
							the work in your head looks better than the work on screen. This is the correct
							starting condition. This is where everyone starts.
						</div>
					</div>
				</div>
			</div>
		</div>

		<p>
			There is also a third combination worth naming: low taste and high skill. This produces
			technically proficient but empty work — execution without judgment. That is a harder problem
			to fix than low skill, because you can't practice your way out of it. The fact that you're
			here, with standards you've already developed, puts you in the better position.
		</p>
	</section>

	<!-- ══════════════════════════════════
       SECTION 4: THE TEMPLATE PROBLEM
  ══════════════════════════════════ -->
	<section id="template-problem" class="section">
		<div class="section-header">
			<span class="section-num">01.04</span>
			<h2 class="section-title">Why Templates Fail to Create Authentic Identity</h2>
		</div>

		<p>
			Templates have a seductive appeal. They are fast, they look professional immediately, and they
			remove the anxiety of a blank canvas. If you are building a YouTube channel or a website and
			you just need something that works, a template seems like the right tool.
		</p>

		<p>
			The problem is structural. A template is designed to look acceptable to the largest number of
			people. To achieve this, it makes conservative choices: neutral colors, safe type
			combinations, conventional layouts. It is optimized for general use, which means it is
			optimized for <em>nobody in particular</em>.
		</p>

		<p>
			Your identity — the thing that makes your channel or website feel like <em>you</em> — cannot come
			from a template. A template was designed by someone who doesn't know your subject, your audience,
			your aesthetic sensibility, or your message. At best, it's a starting point you have to escape.
			At worst, it locks you into visual decisions that communicate the wrong things.
		</p>

		<div class="callout warn">
			<div class="callout-label">The Core Problem</div>
			Templates communicate<strong>genericness</strong>. Genericness communicates that you didn't
			make a decision. Not making a decision about your visual identity <em>is</em> a decision — just
			not one you made intentionally.
		</div>

		<!-- DEMO: Template vs Custom Comparison -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Template vs Designed — Structural Analysis</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Two thumbnails for the same hypothetical video. Click elements on each to reveal their
					structural properties.
				</p>

				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button class="btn" id="show-issues-btn" onclick={(e) => actions.toggleIssues()}>
						Show Analysis
					</button>
					<button class="btn violet" id="reset-btn" onclick={(e) => actions.resetComparison()}
						>Reset</button
					>
				</div>

				<div class="compare-wrap">
					<div class="compare-panel">
						<div class="compare-label template">Template Version</div>
						<canvas
							id="cv-template"
							width="320"
							height="180"
							aria-label="Cv Template Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<ul class="issue-list" id="template-issues" style="display: none"></ul>
					</div>
					<div class="compare-panel">
						<div class="compare-label custom">Designed Version</div>
						<canvas
							id="cv-custom"
							width="320"
							height="180"
							aria-label="Cv Custom Demonstration"
							role="region"
							tabindex="0"
						></canvas>
						<ul class="issue-list" id="custom-strengths" style="display: none"></ul>
					</div>
				</div>

				<div
					style="margin-top: 1rem; font-size: 12px; color: var(--muted); line-height: 1.6"
					id="compare-detail"
				>
					Press "Show Analysis" to reveal the structural differences between these two approaches.
				</div>
			</div>
		</div>

		<p>
			The goal of this course is not to make you avoid all starting points. It is to give you the
			vocabulary and judgment to make intentional decisions. Once you understand structure, you can
			use a template as raw material and redesign it from the inside out — or you can start from
			nothing, because you understand the principles behind what you are building.
		</p>
	</section>

	<!-- ══════════════════════════════════
       SECTION 5: PRACTICAL WORK
  ══════════════════════════════════ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">01.05</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout green">
			<div class="callout-label">Exercise 1 — Structure Analysis</div>
			Find a logo or YouTube thumbnail you consider "well designed." It can be from any channel, brand,
			or product. In your notes, write down:
			<br /><br />
			1. What is the focal point — where does the eye go first?<br />
			2. How many elements are competing for attention?<br />
			3. Is there a dominant color? What does it communicate?<br />
			4. What would you remove, and what would you keep?<br /><br />
			You are not being asked to replicate or judge aesthetics. You are being asked to read structure.
		</div>

		<div class="callout info">
			<div class="callout-label">Exercise 2 — Template Autopsy</div>
			Find a YouTube channel using an obvious template (Canva templates are a good source). Identify:
			<br /><br />
			1. Three design decisions that feel generic or interchangeable<br />
			2. One element that <em>might</em> be intentional, not template-derived<br />
			3. What you would do differently if you were designing for that creator's specific subject<br
			/><br />
			The goal is not to criticize — it is to train your eye to separate structure from decoration.
		</div>
	</section>

	<hr class="divider" />

	<!-- ══════════════════════════════════
       QUIZ
  ══════════════════════════════════ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 01 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit · Select the best answer for each.</div>

		<!-- Q1 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> A designer is working on a YouTube thumbnail. Which question best
				reflects a design-as-problem-solving mindset?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. What colors look good together for this topic?
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. How can I make this look similar to channels I admire?
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. What does this thumbnail need to communicate at 168px wide to earn a click?
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. How many elements can I fit without it looking too empty?
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<!-- Q2 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> Visual hierarchy is best described as:
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Making the most important elements the most colourful
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Arranging elements so the eye encounters them in a deliberate order
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Ensuring all elements are the same visual weight
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Placing text at the top of every composition
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<!-- Q3 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> A beginning designer says: "I know my work isn't good yet, even
				though I can tell something is wrong with it." What does this indicate?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. They lack both taste and skill and should reconsider this path
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. They have skill but their taste hasn't developed yet
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Their taste is already working — their skill just needs to catch up
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. They should stop critiquing their work and focus on output volume
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<!-- Q4 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> Why do templates fail to create authentic visual identity?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
					>A. They use too many colors</button
				>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. They are designed by people with low skill
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. They are hard to edit without professional tools
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. They are optimized for general acceptability, not a specific creator's identity
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<!-- Q5 -->
		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> Good design "hides its scaffolding." What does this mean?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The underlying structural decisions (hierarchy, alignment, spacing) are invisible in
					the final work, even though they drive its quality
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Designers should not show their work-in-progress to clients
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The best designs use hidden layers that can only be seen in editing software
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Simple designs are always better than complex ones
				</button>
			</div>
			<div class="feedback" id="fb-4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-num">—</div>
			<div class="score-label">questions correct out of 5</div>
		</div>
	</section>

	<!-- ══════════════════════════════════
       ASSESSMENT
  ══════════════════════════════════ -->
	<section id="assessment" class="assessment-section">
		<div class="assessment-header">Module Assessment — Structural Reflection</div>
		<div class="assessment-sub">
			Short written reflection · ~100–200 words · No right or wrong answers
		</div>

		<p style="font-size: 13px; margin-bottom: 1.25rem">
			Find a design you genuinely like — a logo, a thumbnail, a poster, or any visual object.
			Describe it structurally: where does your eye go first, what is doing the most work, and what
			would break if you removed it. Avoid aesthetic language ("it's pretty," "I like the vibe") and
			focus on what you can observe about hierarchy, alignment, contrast, or purpose.
		</p>

		<textarea
			class="reflect-area"
			id="reflect-area"
			placeholder="Describe the design structurally — not whether you like it, but how it works..."
		></textarea>
		<div class="reflect-footer">
			<span class="char-count" id="char-count">0 / 200+ characters</span>
			<button class="btn amber" onclick={(e) => actions.submitReflection()}>Mark Complete</button>
		</div>
		<div
			id="reflect-feedback"
			style="font-size: 12px; margin-top: 0.75rem; min-height: 1.2em"
		></div>
	</section>

	<!-- NEXT MODULE -->
	<a href="gd-module-02.html" class="next-module">
		<div>
			<div class="next-label">Next — Module 02</div>
			<div class="next-title">Visual Perception and Composition Foundations</div>
		</div>
		<div class="next-arrow">→</div>
	</a>
</div>

<!-- .page-wrapper -->

<style>
	/* ── TOKENS ── */

	.page-wrapper {
		background: var(--bg);
		color: var(--text);
		font-family: 'IBM Plex Mono', monospace;
		font-size: 14px;
		line-height: 1.8;
	}

	/* ── SCROLLBAR ── */

	/* ── LAYOUT ── */
	.page-wrapper {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem 6rem;
	}

	/* ── HEADER ── */
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

	/* ── HERO ── */
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

	/* ── TOC ── */
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

	/* ── OBJECTIVES ── */
	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--sky);
		background: var(--surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--sky);
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

	/* ── SECTIONS ── */
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

	/* ── CODE ── */
	:global(code) {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 1px 6px;
		font-size: 12px;
		color: var(--violet);
		font-family: 'IBM Plex Mono', monospace;
	}

	/* ── CALLOUTS ── */
	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
		font-size: 13px;
	}
	.callout.info {
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
	}
	.callout.green {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--surface));
	}
	.callout.warn {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 5%, var(--surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--violet);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	.callout.info .callout-label {
		color: var(--amber);
	}
	.callout.green .callout-label {
		color: var(--sage);
	}
	.callout.warn .callout-label {
		color: var(--rose);
	}

	/* ── DEMO BOXES ── */
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
		color: var(--sky);
		border-color: var(--sky);
		background: color-mix(in srgb, var(--sky) 10%, transparent);
	}
	:global(.demo-badge.animated) {
		color: var(--amber);
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	/* ── CONTROLS ── */
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
		border-color: var(--sky);
		color: var(--sky);
	}
	:global(.btn.active) {
		border-color: var(--sky);
		color: var(--sky);
		background: color-mix(in srgb, var(--sky) 10%, transparent);
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
	:global(.btn.violet:hover) {
		border-color: var(--violet);
		color: var(--violet);
	}
	:global(.btn.violet.active) {
		border-color: var(--violet);
		color: var(--violet);
		background: color-mix(in srgb, var(--violet) 10%, transparent);
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

	/* ── PROGRESS ── */
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

	/* ── DIVIDER ── */
	.divider {
		border: none;
		border-top: 1px solid var(--border);
		margin: 3rem 0;
	}

	/* ── TWO-COL ── */
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

	/* ── TABLE ── */
	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--raised);
		color: var(--sky);
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

	/* ── QUIZ ── */
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
		color: var(--sky);
	}
	.score-label {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.25rem;
	}

	/* ── ASSESSMENT ── */
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
	.reflect-area {
		width: 100%;
		min-height: 120px;
		background: var(--code-bg);
		border: 1px solid var(--border);
		color: var(--text);
		font-family: 'IBM Plex Mono', monospace;
		font-size: 13px;
		padding: 1rem;
		line-height: 1.7;
		resize: vertical;
		outline: none;
		transition: border-color 0.2s;
	}
	.reflect-area:focus {
		border-color: var(--violet);
	}
	.reflect-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: 0.75rem;
	}
	.char-count {
		font-size: 11px;
		color: var(--muted);
	}

	/* ── NEXT MODULE ── */
	.next-module {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem 2rem;
		border: 1px solid var(--border);
		text-decoration: none;
		margin-top: 4rem;
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

	/* ══════════════════════════════════
     DEMO-SPECIFIC STYLES
  ══════════════════════════════════ */

	/* --- Structure Reveal Demo --- */
	.sr-canvas-wrap {
		position: relative;
		display: inline-block;
		border: 1px solid var(--border2);
		background: #0a0f15;
	}
	#sr-canvas {
		display: block;
	}
	.layer-btns {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-bottom: 1rem;
	}
	.layer-desc {
		font-size: 12px;
		color: var(--muted);
		margin-top: 1rem;
		min-height: 2.5em;
		line-height: 1.6;
		transition: color 0.2s;
	}

	/* --- Template vs Custom Demo --- */
	.compare-wrap {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}
	@media (max-width: 560px) {
		.compare-wrap {
			grid-template-columns: 1fr;
		}
	}
	.compare-panel {
		position: relative;
	}
	.compare-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		margin-bottom: 0.5rem;
	}
	.compare-label.template {
		color: var(--rose);
	}
	.compare-label.custom {
		color: var(--sage);
	}
	#cv-template,
	#cv-custom {
		display: block;
		width: 100%;
		border: 1px solid var(--border);
	}
	.issue-list {
		margin-top: 0.75rem;
		font-size: 11px;
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}
	:global(.issue-list li) {
		padding: 3px 8px;
		border-left: 2px solid;
		transition: background 0.2s;
	}
	:global(.issue-list li.problem) {
		border-color: var(--rose);
		color: var(--rose);
		background: color-mix(in srgb, var(--rose) 6%, transparent);
	}
	:global(.issue-list li.strength) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 6%, transparent);
	}

	/* --- Taste vs Skill slider --- */
	.taste-skill-wrap {
		margin: 1.5rem 0;
	}
	.ts-track {
		display: flex;
		height: 3px;
		background: var(--border2);
		position: relative;
		margin: 2rem 0 0.5rem;
	}
	.ts-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--violet), var(--rose));
		transition: width 0.3s;
	}
	.ts-thumb {
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: #fff;
		border: 2px solid var(--rose);
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		cursor: grab;
		z-index: 10;
		transition: border-color 0.2s;
	}
	.ts-thumb:active {
		cursor: grabbing;
	}
	.ts-labels {
		display: flex;
		justify-content: space-between;
		font-size: 10px;
		color: var(--muted);
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.ts-output {
		margin-top: 1.2rem;
		padding: 1rem;
		background: var(--code-bg);
		border: 1px solid var(--border);
		font-size: 12px;
		min-height: 70px;
		line-height: 1.6;
		transition: all 0.3s;
	}
	.ts-output .ts-heading {
		font-weight: 600;
		margin-bottom: 0.4rem;
	}
	.ts-output.violet-mode .ts-heading {
		color: var(--violet);
	}
	:global(.ts-output.rose-mode .ts-heading) {
		color: var(--rose);
	}
	:global(.ts-output.mix-mode .ts-heading) {
		color: var(--amber);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
