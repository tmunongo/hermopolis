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
		/* ── READING PROGRESS ── */
		_addWinListener('scroll', () => {
			const el = document.getElementById('reading-progress');
			const d = document.documentElement.scrollHeight - window.innerHeight;
			if (d > 0) el.style.width = Math.min(100, (window.scrollY / d) * 100) + '%';
		});

		/* ══════════════════════════════════════════
   B-ROLL FUNCTION SPECTRUM CANVAS
══════════════════════════════════════════ */
		const spectrumZones = [
			{
				x: 0,
				w: 0.18,
				color: '#ff4f68',
				label: 'Misleading',
				short: 'MISLEADS',
				desc: 'The visual contradicts or confuses the narration. The viewer forms an incorrect mental model. This is worse than no visual at all — it requires cognitive correction.'
			},
			{
				x: 0.18,
				w: 0.2,
				color: '#f5b94a',
				label: 'Redundant',
				short: 'REDUNDANT',
				desc: 'The visual depicts exactly what the narration says, adding no new dimension. Technically accurate but communicatively inert. The most common type of weak b-roll — it fills the frame without contributing.'
			},
			{
				x: 0.38,
				w: 0.2,
				color: '#8a8acc',
				label: 'Ambient',
				short: 'AMBIENT',
				desc: 'The visual creates tonal context but does not directly reinforce the content. Acceptable for emotional priming between denser segments — but overuse produces a generic, unfocused feel.'
			},
			{
				x: 0.58,
				w: 0.22,
				color: '#3dd9a4',
				label: 'Reinforcing',
				short: 'REINFORCES',
				desc: 'The visual adds an emotional or sensory dimension that the narration describes but cannot fully convey. The viewer feels something from the visual that the words only implied. This is the baseline for strong b-roll.'
			},
			{
				x: 0.8,
				w: 0.2,
				color: '#4aafff',
				label: 'Additive',
				short: 'ADDS LAYER',
				desc: 'The visual contributes a layer of meaning that the narration does not provide at all — scale, contrast, metaphor, process, or specificity. The viewer understands something from the visual they would not have understood from the words alone.'
			}
		];

		(function initSpectrum() {
			const canvas = document.getElementById('broll-func-canvas');
			const dpr = window.devicePixelRatio || 1;
			function draw() {
				const W = canvas.offsetWidth || 600;
				const H = 200;
				canvas.width = W * dpr;
				canvas.height = H * dpr;
				const ctx = canvas.getContext('2d');
				ctx.scale(dpr, dpr);
				ctx.clearRect(0, 0, W, H);

				const pad = { t: 40, b: 50, l: 0, r: 0 };
				const bw = W - pad.l - pad.r;
				const barH = 48;
				const barY = pad.t;

				spectrumZones.forEach((z) => {
					const x = pad.l + z.x * bw;
					const w = z.w * bw;
					// Gradient fill
					const grd = ctx.createLinearGradient(x, 0, x + w, 0);
					grd.addColorStop(0, z.color + '22');
					grd.addColorStop(0.5, z.color + '44');
					grd.addColorStop(1, z.color + '22');
					ctx.fillStyle = grd;
					ctx.fillRect(x, barY, w, barH);
					// Border
					ctx.strokeStyle = z.color + '60';
					ctx.lineWidth = 1;
					ctx.strokeRect(x, barY, w, barH);
					// Label
					ctx.fillStyle = z.color;
					ctx.font = `600 10px IBM Plex Mono`;
					ctx.textAlign = 'center';
					ctx.fillText(z.short, x + w / 2, barY + barH / 2 - 6);
					ctx.font = '9px IBM Plex Mono';
					ctx.fillStyle = z.color + 'cc';
					ctx.fillText(z.label, x + w / 2, barY + barH / 2 + 8);
				});

				// Axis label
				ctx.font = '9px IBM Plex Mono';
				ctx.fillStyle = '#405068';
				ctx.textAlign = 'left';
				ctx.fillText('← Less effective', pad.l + 4, H - 8);
				ctx.textAlign = 'right';
				ctx.fillText('More effective →', W - pad.r - 4, H - 8);
				ctx.textAlign = 'center';
				ctx.fillText('Click any zone to learn more', W / 2, H - 8);

				// Arrow markers at bottom
				const arrowY = barY + barH + 12;
				ctx.strokeStyle = '#1e2d40';
				ctx.lineWidth = 1;
				ctx.beginPath();
				ctx.moveTo(pad.l, arrowY);
				ctx.lineTo(W - pad.r, arrowY);
				ctx.stroke();
				for (let i = 0; i <= 4; i++) {
					const x = pad.l + (i / 4) * bw;
					ctx.beginPath();
					ctx.moveTo(x, arrowY - 3);
					ctx.lineTo(x, arrowY + 3);
					ctx.stroke();
				}
			}
			draw();
			_addWinListener('resize', draw);

			canvas.addEventListener('click', function (e) {
				const rect = canvas.getBoundingClientRect();
				const rx = (e.clientX - rect.left) / rect.width;
				const zone = spectrumZones.find((z) => rx >= z.x && rx < z.x + z.w);
				if (zone) {
					const el = document.getElementById('broll-func-desc');
					el.style.borderLeftColor = zone.color;
					el.innerHTML = `<span style="color:${zone.color}; font-weight:600; letter-spacing:0.08em;">${zone.label}:</span> ${zone.desc}`;
				}
			});
		})();

		/* ══════════════════════════════════════════
   B-ROLL SORTER
══════════════════════════════════════════ */
		const brollCards = [
			{
				emoji: '📅',
				label: 'Calendar / planner',
				bg: '#1a1a2e',
				correct: 'literal',
				analysis:
					'LITERAL. A calendar depicts the concept of time planning directly — it is the most obvious symbol of the planning fallacy. It tells the viewer what they already understood from the word "planning" and adds no felt dimension.'
			},
			{
				emoji: '🏔️',
				label: 'Person at base of mountain',
				bg: '#0a1628',
				correct: 'strong',
				analysis:
					'STRONG. A person standing at the base of a mountain they cannot see the top of adds the dimension of scale and underestimation that the narration describes but cannot show. The viewer feels the gap between the visible start and the invisible end.'
			},
			{
				emoji: '🧠',
				label: 'Animated brain graphic',
				bg: '#1a0a28',
				correct: 'literal',
				analysis:
					'LITERAL. A brain graphic signals "this is about thinking" — which the word "cognitive" already communicated. It adds no new dimension and reads as generic stock imagery. The concept is about bias, not brain anatomy.'
			},
			{
				emoji: '🏗️',
				label: 'Half-built structure',
				bg: '#0a1a10',
				correct: 'strong',
				analysis:
					'STRONG. A half-finished building or project makes the underestimation visible and concrete — the gap between where the work is and where it needs to be. This adds spatial and physical scale to an abstract cognitive concept.'
			},
			{
				emoji: '⏰',
				label: 'Close-up of clock',
				bg: '#1a0a0a',
				correct: 'literal',
				analysis:
					'LITERAL. A clock is the most overused symbol in educational video for any concept involving time. It depicts the subject accurately and adds nothing. Viewers have become habituated to clock b-roll and process it as background rather than signal.'
			},
			{
				emoji: '🌊',
				label: 'Small wave growing into large wave',
				bg: '#0a1428',
				correct: 'strong',
				analysis:
					'STRONG. A wave that starts small and grows unexpectedly captures the structure of the planning fallacy — a process that looks manageable at the start and overwhelming at the end. The visual metaphor maps directly to the cognitive experience.'
			},
			{
				emoji: '📊',
				label: 'Bar chart on screen',
				bg: '#101028',
				correct: 'weak',
				analysis:
					'WEAK. A bar chart is a data-display graphic, not a narrative visual. Unless the narration is specifically discussing statistics about the planning fallacy, a chart in b-roll introduces a cognitive task (reading the chart) that competes with the narration.'
			},
			{
				emoji: '😤',
				label: 'Person looking frustrated at desk',
				bg: '#1a0a10',
				correct: 'literal',
				analysis:
					'LITERAL. Frustration is the result of the planning fallacy, not the bias itself. This depicts a consequence rather than the cognitive experience being described — and it is so common in stock libraries that it reads as generic.'
			},
			{
				emoji: '🪨',
				label: 'Rolling boulder, distant finish line',
				bg: '#0e1a0e',
				correct: 'strong',
				analysis:
					'STRONG. A boulder rolling toward a distant or obscured finish line adds scale, momentum, and the visual sense of a task with more distance than it appears. The metaphor maps to the structure of underestimation.'
			}
		];

		let brollRatings = {};
		function buildBrollCards() {
			const grid = document.getElementById('broll-cards');
			grid.innerHTML = '';
			brollCards.forEach((card, i) => {
				const div = document.createElement('div');
				div.className = 'broll-card';
				div.id = 'broll-card-' + i;
				div.innerHTML = `
      <div class="broll-thumb" style="background:${card.bg};">
        <span>${card.emoji}</span>
        <span class="broll-thumb-label">b-roll</span>
      </div>
      <div class="broll-desc">${card.label}</div>
      <div class="broll-rating-strip">
        <button class="broll-rate-btn" id="br-s-${i}" onclick="rateBroll(${i},'strong')">Strong</button>
        <button class="broll-rate-btn" id="br-l-${i}" onclick="rateBroll(${i},'literal')">Literal</button>
        <button class="broll-rate-btn" id="br-w-${i}" onclick="rateBroll(${i},'weak')">Weak</button>
      </div>`;
				grid.appendChild(div);
			});
		}

		function rateBroll(i, rating) {
			brollRatings[i] = rating;
			const card = document.getElementById('broll-card-' + i);
			card.className = 'broll-card rated-' + rating;
			['strong', 'literal', 'weak'].forEach((r) => {
				const btn = document.getElementById('br-' + r[0] + '-' + i);
				btn.className = 'broll-rate-btn' + (r === rating ? ' sel-' + r : '');
			});
			updateBrollCounts();
		}

		function updateBrollCounts() {
			['strong', 'literal', 'weak'].forEach((r) => {
				document.getElementById('count-' + r).textContent = Object.values(brollRatings).filter(
					(v) => v === r
				).length;
			});
		}

		function revealBrollAnalysis() {
			const el = document.getElementById('broll-analysis');
			el.style.display = 'block';
			el.innerHTML = brollCards
				.map((c, i) => {
					const userRating = brollRatings[i];
					const correct = c.correct;
					const match = userRating === correct;
					const rColor = { strong: '#3dd9a4', literal: '#f5b94a', weak: '#ff4f68' };
					return `<div style="padding:0.6rem 0; border-bottom:1px solid var(--vs-border); display:flex; gap:0.75rem; align-items:flex-start;">
      <span style="font-size:18px; flex-shrink:0;">${c.emoji}</span>
      <div style="flex:1;">
        <div style="font-size:11px; margin-bottom:0.25rem;">
          <span style="color:${rColor[correct]}; font-weight:600;">${correct.toUpperCase()}</span>
          ${userRating ? `· You said: <span style="color:${match ? '#3dd9a4' : '#ff4f68'};">${userRating.toUpperCase()} ${match ? '✓' : '✗'}</span>` : '<span style="color:#405068;">· Not rated</span>'}
        </div>
        <div style="color:#b8c8de; font-size:11px; line-height:1.6;">${c.analysis}</div>
      </div>
    </div>`;
				})
				.join('');
		}

		buildBrollCards();

		/* ══════════════════════════════════════════
   VISUAL FUNCTION EXPLORER
══════════════════════════════════════════ */
		const vfuncs = [
			{
				icon: '🎭',
				name: 'Reinforce',
				freq: 'HIGH',
				freqColor: '#3dd9a4',
				desc: 'Adds the emotional or sensory texture that the narration describes but cannot convey alone.',
				example:
					'<strong>Narration:</strong> "The pressure of a deadline changes how people make decisions." <strong>Visual:</strong> Extreme close-up of hands gripping a pen, knuckles white. The narration tells us about pressure; the visual makes us feel it physically.'
			},
			{
				icon: '⚡',
				name: 'Contrast',
				freq: 'MEDIUM',
				freqColor: '#4aafff',
				desc: "Places two opposing states side by side so the difference illuminates the narration's claim more vividly than either state alone.",
				example:
					'<strong>Narration:</strong> "A 1% daily improvement compounds into a 37-times improvement over a year." <strong>Visual sequence:</strong> A wilting plant, cut to a thriving one. The juxtaposition makes the compound effect visceral in a way numbers alone cannot.'
			},
			{
				icon: '🌍',
				name: 'Establish Scale',
				freq: 'MEDIUM',
				freqColor: '#f5b94a',
				desc: 'Provides a spatial or numerical reference that allows the viewer to grasp proportions that are otherwise abstract.',
				example:
					'<strong>Narration:</strong> "The Great Barrier Reef covers an area larger than Germany and the UK combined." <strong>Visual:</strong> An aerial shot showing the reef alongside a landmass reference. Without this, "larger than two countries" is a number, not a felt size.'
			},
			{
				icon: '🔄',
				name: 'Reveal Process',
				freq: 'HIGH',
				freqColor: '#a78bfa',
				desc: 'Shows how something works through a visual sequence — movement, transformation, or progression that the narration can name but not demonstrate.',
				example:
					'<strong>Narration:</strong> "The immune system identifies pathogens by their surface proteins." <strong>Visual:</strong> Animated diagram showing an immune cell approaching a pathogen, binding to it, and triggering a response. The process is visible, not just described.'
			},
			{
				icon: '🌫️',
				name: 'Atmosphere',
				freq: 'LOW–MEDIUM',
				freqColor: '#ff4f68',
				desc: "Sets the emotional register of a section before the narration's content arrives — priming the viewer's mood rather than contributing directly to the argument.",
				example:
					'<strong>Narration:</strong> "The financial crisis of 2008 began with what seemed like small, manageable problems." <strong>Visual:</strong> A slow pan across an empty office building at dusk. The visual installs a sense of something ending before the narration explains what ended.'
			}
		];

		let openVFunc = null;
		function buildVFuncs() {
			const el = document.getElementById('vfunc-list');
			el.innerHTML = '';
			vfuncs.forEach((fn, i) => {
				const wrap = document.createElement('div');
				wrap.innerHTML = `
      <div class="vfunc-row" id="vfr-${i}" onclick="toggleVFunc(${i})">
        <div class="vfunc-icon">${fn.icon}</div>
        <div class="vfunc-body">
          <div class="vfunc-name" style="color:${fn.freqColor};">${fn.name}</div>
          <div class="vfunc-desc">${fn.desc}</div>
        </div>
        <div class="vfunc-badge" style="color:${fn.freqColor}; background:color-mix(in srgb,${fn.freqColor} 8%,transparent);">
          ${fn.freq}
        </div>
      </div>
      <div class="vfunc-example" id="vfe-${i}">${fn.example}</div>`;
				el.appendChild(wrap);
			});
		}

		function toggleVFunc(i) {
			if (openVFunc === i) {
				document.getElementById('vfe-' + i).classList.remove('open');
				document.getElementById('vfr-' + i).classList.remove('selected');
				openVFunc = null;
			} else {
				if (openVFunc !== null) {
					document.getElementById('vfe-' + openVFunc).classList.remove('open');
					document.getElementById('vfr-' + openVFunc).classList.remove('selected');
				}
				document.getElementById('vfe-' + i).classList.add('open');
				document.getElementById('vfr-' + i).classList.add('selected');
				openVFunc = i;
			}
		}
		buildVFuncs();

		/* ══════════════════════════════════════════
   VISUAL METAPHOR WORKSHOP
══════════════════════════════════════════ */
		const concepts = [
			{
				label: 'Compounding Interest',
				panels: [
					{
						type: 'literal',
						label: '📊 Literal',
						svgFn: (s) =>
							`<text x="50%" y="48%" dominant-baseline="middle" text-anchor="middle" font-size="28" font-family="IBM Plex Mono" fill="#f5b94a">$$$</text><text x="50%" y="68%" dominant-baseline="middle" text-anchor="middle" font-size="10" font-family="IBM Plex Mono" fill="#405068">MONEY GROWING</text>`,
						desc: 'Stock footage of cash, a rising bar chart, or a bank logo. Depicts the subject but communicates nothing about the mechanism.',
						verdict: 'WEAK',
						vcolor: '#f5b94a'
					},
					{
						type: 'diagram',
						label: '📐 Diagram',
						svgFn: () => {
							const pts = [0, 0.01, 0.04, 0.1, 0.21, 0.46, 1.0].map((v, i) => [
								14 + i * 12,
								86 - v * 72
							]);
							const path = pts
								.map((p, i) => (i === 0 ? `M${p[0]},${p[1]}` : `L${p[0]},${p[1]}`))
								.join(' ');
							return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
            <line x1="10" y1="90" x2="10" y2="10" stroke="#1e2d40" stroke-width="1"/>
            <line x1="10" y1="90" x2="90" y2="90" stroke="#1e2d40" stroke-width="1"/>
            <path d="${path}" fill="none" stroke="#3dd9a4" stroke-width="2"/>
            ${pts.map((p) => `<circle cx="${p[0]}" cy="${p[1]}" r="2" fill="#3dd9a4"/>`).join('')}
            <text x="50" y="98" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">time</text>
          </svg>`;
						},
						desc: 'An exponential curve chart. Technically accurate and correct — ideal for mathematical explanation where the shape of the curve is the point.',
						verdict: 'CORRECT',
						vcolor: '#3dd9a4'
					},
					{
						type: 'metaphor',
						label: '🌨️ Metaphor',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <circle cx="50" cy="28" r="8" fill="none" stroke="#4aafff" stroke-width="1.5"/>
          <circle cx="50" cy="55" r="16" fill="none" stroke="#4aafff" stroke-width="1.5" opacity="0.7"/>
          <circle cx="50" cy="78" r="22" fill="none" stroke="#4aafff" stroke-width="1.5" opacity="0.4"/>
          <text x="50" y="99" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">SNOWBALL</text>
        </svg>`,
						desc: 'A snowball rolling downhill, growing as it moves. Maps: small start → initial principal. Speed increase → interest on interest. Growing size → exponential not linear growth.',
						verdict: 'STRONG',
						vcolor: '#ff4f68'
					}
				],
				verdict:
					'The diagram is technically superior for mathematical precision. The snowball metaphor is superior for intuitive comprehension — a viewer who has never heard of compound interest immediately grasps the self-reinforcing mechanism. Use the metaphor first to build intuition, then the diagram to provide precision.'
			},
			{
				label: 'Information Overload',
				panels: [
					{
						type: 'literal',
						label: '💻 Literal',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <rect x="20" y="20" width="60" height="45" rx="2" fill="none" stroke="#405068" stroke-width="1.5"/>
          ${Array.from({ length: 8 }, (_, i) => `<rect x="25" y="${26 + i * 5}" width="${15 + Math.random() * 30}" height="3" rx="1" fill="#405068" opacity="0.6"/>`).join('')}
          <text x="50" y="95" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">SCREEN WITH DATA</text>
        </svg>`,
						desc: 'A busy screen, data visualisation, or notification panel. Depicts the source of overload but not the experience of being overwhelmed.',
						verdict: 'WEAK',
						vcolor: '#f5b94a'
					},
					{
						type: 'diagram',
						label: '📐 Diagram',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <rect x="30" y="35" width="40" height="30" rx="2" fill="none" stroke="#4aafff" stroke-width="1.5"/>
          <text x="50" y="53" font-size="6" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle">WORKING</text>
          <text x="50" y="60" font-size="6" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle">MEMORY</text>
          ${[
						[18, 22, 'I1'],
						[70, 18, 'I2'],
						[10, 55, 'I3'],
						[75, 58, 'I4'],
						[25, 80, 'I5'],
						[60, 82, 'I6']
					]
						.map(
							([x, y, l]) => `
            <circle cx="${x}" cy="${y}" r="6" fill="none" stroke="#ff4f68" stroke-width="1" opacity="0.7"/>
            <text x="${x}" y="${y + 2}" font-size="4" font-family="IBM Plex Mono" fill="#ff4f68" text-anchor="middle">${l}</text>
            <line x1="${x < 50 ? x + 6 : x - 6}" y1="${y}" x2="${x < 50 ? 30 : 70}" y2="50" stroke="#ff4f68" stroke-width="0.5" opacity="0.4" stroke-dasharray="2,2"/>
          `
						)
						.join('')}
          <text x="50" y="95" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">CAPACITY MODEL</text>
        </svg>`,
						desc: 'A working memory capacity diagram with inputs exceeding the container. Precise for cognitive science context.',
						verdict: 'CORRECT',
						vcolor: '#3dd9a4'
					},
					{
						type: 'metaphor',
						label: '🌊 Metaphor',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <path d="M0,55 Q15,40 30,55 Q45,70 60,55 Q75,40 90,55 Q95,58 100,55 L100,100 L0,100 Z" fill="color-mix(in srgb,#4aafff 20%,transparent)" stroke="#4aafff" stroke-width="1"/>
          <path d="M0,45 Q20,30 40,45 Q60,60 80,45 Q90,38 100,45 L100,100 L0,100 Z" fill="color-mix(in srgb,#4aafff 12%,transparent)" stroke="#4aafff" stroke-width="0.8" opacity="0.6"/>
          <text x="50" y="30" font-size="18" font-family="IBM Plex Mono" fill="#b8c8de" text-anchor="middle" opacity="0.7">🧍</text>
          <text x="50" y="97" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">RISING TIDE</text>
        </svg>`,
						desc: 'A figure surrounded by rising water. Maps: the water level → volume of incoming information. The fixed height of the person → cognitive capacity. Flooding → the experience of being overwhelmed.',
						verdict: 'STRONG',
						vcolor: '#ff4f68'
					}
				],
				verdict:
					'The rising water metaphor makes the experience of overload visceral in a way a capacity diagram cannot — the viewer feels the rising pressure rather than understanding it abstractly. Use it when the goal is empathy and recognition. Use the diagram when the goal is a precise explanation of cognitive load theory.'
			},
			{
				label: 'Institutional Inertia',
				panels: [
					{
						type: 'literal',
						label: '🏛️ Literal',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <rect x="25" y="40" width="50" height="35" fill="none" stroke="#405068" stroke-width="1.5"/>
          ${Array.from({ length: 5 }, (_, i) => `<rect x="${28 + i * 9}" y="40" width="7" height="35" fill="none" stroke="#405068" stroke-width="0.8" opacity="0.5"/>`).join('')}
          <polygon points="50,15 75,40 25,40" fill="none" stroke="#405068" stroke-width="1.5"/>
          <text x="50" y="95" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">GOVERNMENT BUILDING</text>
        </svg>`,
						desc: 'A government building, meeting room, or bureaucratic forms. Depicts the setting but not the felt experience of being unable to change direction.',
						verdict: 'WEAK',
						vcolor: '#f5b94a'
					},
					{
						type: 'diagram',
						label: '📐 Diagram',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <circle cx="50" cy="50" r="28" fill="none" stroke="#4aafff" stroke-width="1.5" stroke-dasharray="4,2"/>
          ${Array.from({ length: 8 }, (_, i) => {
						const a = (i / 8) * Math.PI * 2;
						const x = 50 + 28 * Math.cos(a);
						const y = 50 + 28 * Math.sin(a);
						const nx = 50 + 22 * Math.cos(a + 0.4);
						const ny = 50 + 22 * Math.sin(a + 0.4);
						return `<line x1="${x}" y1="${y}" x2="${nx}" y2="${ny}" stroke="#ff4f68" stroke-width="1.5" marker-end="url(#arr)"/>`;
					}).join('')}
          <text x="50" y="53" font-size="5.5" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle">FEEDBACK</text>
          <text x="50" y="60" font-size="5.5" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle">LOOP</text>
          <text x="50" y="95" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">REINFORCING CYCLE</text>
        </svg>`,
						desc: 'A reinforcing feedback loop diagram showing how institutional processes self-perpetuate. Technically precise for systems-thinking contexts.',
						verdict: 'CORRECT',
						vcolor: '#3dd9a4'
					},
					{
						type: 'metaphor',
						label: '🚢 Metaphor',
						svgFn:
							() => `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <path d="M15,65 Q50,55 85,65 L90,78 Q50,88 10,78 Z" fill="none" stroke="#4aafff" stroke-width="1.5"/>
          <rect x="35" y="40" width="30" height="25" fill="none" stroke="#4aafff" stroke-width="1"/>
          <rect x="45" y="28" width="10" height="14" fill="none" stroke="#4aafff" stroke-width="0.8"/>
          <path d="M20,78 Q10,90 5,100" stroke="#4aafff" stroke-width="1" fill="none" stroke-dasharray="2,2" opacity="0.5"/>
          <path d="M80,78 Q90,90 95,100" stroke="#4aafff" stroke-width="1" fill="none" stroke-dasharray="2,2" opacity="0.5"/>
          <path d="M85,65 L98,65" stroke="#ff4f68" stroke-width="1.5" marker-end="url(#arr)"/>
          <path d="M50,36 L50,20" stroke="#f5b94a" stroke-width="1.5" opacity="0.5"/>
          <circle cx="50" cy="18" r="3" fill="#f5b94a" opacity="0.4"/>
          <text x="50" y="97" font-size="5" font-family="IBM Plex Mono" fill="#405068" text-anchor="middle">SUPERTANKER</text>
        </svg>`,
						desc: 'A supertanker that takes many kilometres to change course. Maps: mass → scale of institution. Forward momentum → existing processes/culture. Turn radius → how long change takes. Rudder → leadership decisions.',
						verdict: 'STRONG',
						vcolor: '#ff4f68'
					}
				],
				verdict:
					'The supertanker metaphor communicates both the scale and the physics of inertia — viewers understand intuitively that you cannot stop a vessel of that mass with a small command. It pre-loads the viewer with a structural understanding of the problem before the narration provides the specifics. The mapping is complete and unambiguous.'
			}
		];

		let currentConcept = 0;

		function buildMetaphorConcepts() {
			const el = document.getElementById('metaphor-concepts');
			el.innerHTML = concepts
				.map(
					(c, i) =>
						`<span class="metaphor-concept-pill${i === 0 ? ' selected' : ''}" onclick="selectConcept(${i})">${c.label}</span>`
				)
				.join('');
			renderMetaphorPanels();
		}

		function selectConcept(i) {
			currentConcept = i;
			document
				.querySelectorAll('.metaphor-concept-pill')
				.forEach((p, j) => p.classList.toggle('selected', j === i));
			renderMetaphorPanels();
		}

		function renderMetaphorPanels() {
			const c = concepts[currentConcept];
			document.getElementById('metaphor-display').style.display = 'block';
			const panelColors = { literal: '#f5b94a', diagram: '#3dd9a4', metaphor: '#ff4f68' };
			document.getElementById('metaphor-panels').innerHTML = c.panels
				.map(
					(p) => `
    <div class="metaphor-panel">
      <div class="metaphor-panel-label" style="color:${panelColors[p.type]};">${p.label}</div>
      <div class="metaphor-visual">
        ${p.type === 'diagram' ? p.svgFn() : `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="80" height="80">${p.svgFn()}</svg>`}
      </div>
      <div class="metaphor-text">${p.desc}</div>
      <div style="margin-top:0.5rem;">
        <span class="metaphor-verdict" style="border-color:${panelColors[p.type]}; color:${panelColors[p.type]};">${p.verdict}</span>
      </div>
    </div>`
				)
				.join('');
			document.getElementById('metaphor-verdict').textContent = c.verdict;
		}

		buildMetaphorConcepts();

		/* ══════════════════════════════════════════
   DIAGRAM SEQUENCER
══════════════════════════════════════════ */
		const diagSteps = [
			{
				label: 'Step 1 of 5',
				badge: 'FIRST ELEMENT',
				badgeColor: '#405068',
				narration:
					'"A feedback loop begins with an action." — Only the starting node is visible. The viewer has nothing else to parse.',
				detail:
					'<strong>Reveal principle:</strong> Start with the entry point of the diagram only. The viewer needs one anchor before anything can be connected to it. Narration: "A feedback loop begins with a single action." Duration at this stage: 3–4 seconds.',
				draw: (svg) => {
					svg.innerHTML = `
        <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#ff4f68" opacity="0.7"/></marker></defs>
        <circle cx="280" cy="140" r="38" fill="none" stroke="#ff4f68" stroke-width="2"/>
        <text x="280" y="135" font-size="13" font-family="IBM Plex Mono" fill="#ff4f68" text-anchor="middle" font-weight="600">ACTION</text>
        <text x="280" y="152" font-size="10" font-family="IBM Plex Mono" fill="#ff4f68" opacity="0.6" text-anchor="middle">entry point</text>`;
				}
			},
			{
				label: 'Step 2 of 5',
				badge: '+ EFFECT',
				badgeColor: '#f5b94a',
				narration:
					'"…which produces an effect." — Second node added. The relationship is now visible.',
				detail:
					'<strong>Reveal principle:</strong> Add the first connection and destination together. An arrow without a destination creates confusion; a destination without an arrow has no context. Narration: "…which produces an effect." Duration: 3–4 seconds.',
				draw: (svg) => {
					svg.innerHTML = `
        <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#ff4f68" opacity="0.7"/></marker></defs>
        <circle cx="160" cy="140" r="38" fill="none" stroke="#ff4f68" stroke-width="2"/>
        <text x="160" y="135" font-size="13" font-family="IBM Plex Mono" fill="#ff4f68" text-anchor="middle" font-weight="600">ACTION</text>
        <text x="160" y="152" font-size="10" font-family="IBM Plex Mono" fill="#ff4f68" opacity="0.6" text-anchor="middle">entry point</text>
        <line x1="198" y1="140" x2="332" y2="140" stroke="#ff4f68" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr)" opacity="0.7"/>
        <circle cx="370" cy="140" r="38" fill="none" stroke="#f5b94a" stroke-width="2"/>
        <text x="370" y="135" font-size="13" font-family="IBM Plex Mono" fill="#f5b94a" text-anchor="middle" font-weight="600">EFFECT</text>
        <text x="370" y="152" font-size="10" font-family="IBM Plex Mono" fill="#f5b94a" opacity="0.6" text-anchor="middle">consequence</text>`;
				}
			},
			{
				label: 'Step 3 of 5',
				badge: '+ AMPLIFIER',
				badgeColor: '#4aafff',
				narration: '"…which is amplified by a reinforcing condition." — Third element introduced.',
				detail:
					'<strong>Reveal principle:</strong> Add the mechanism that makes this a loop, not just a chain. Now the viewer has three elements and begins to anticipate that something will close back to the start. Narration: "…which is amplified by a reinforcing condition." Duration: 4 seconds.',
				draw: (svg) => {
					svg.innerHTML = `
        <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#ff4f68" opacity="0.7"/></marker>
        <marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#4aafff" opacity="0.7"/></marker></defs>
        <circle cx="120" cy="200" r="34" fill="none" stroke="#ff4f68" stroke-width="2"/>
        <text x="120" y="197" font-size="12" font-family="IBM Plex Mono" fill="#ff4f68" text-anchor="middle" font-weight="600">ACTION</text>
        <line x1="154" y1="200" x2="236" y2="200" stroke="#ff4f68" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr)" opacity="0.7"/>
        <circle cx="270" cy="200" r="34" fill="none" stroke="#f5b94a" stroke-width="2"/>
        <text x="270" y="197" font-size="12" font-family="IBM Plex Mono" fill="#f5b94a" text-anchor="middle" font-weight="600">EFFECT</text>
        <line x1="296" y1="172" x2="380" y2="118" stroke="#f5b94a" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr2)" opacity="0.7"/>
        <circle cx="420" cy="90" r="34" fill="none" stroke="#4aafff" stroke-width="2"/>
        <text x="420" y="84" font-size="11" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle" font-weight="600">AMPLIFIER</text>
        <text x="420" y="98" font-size="9" font-family="IBM Plex Mono" fill="#4aafff" opacity="0.6" text-anchor="middle">reinforcing</text>`;
				}
			},
			{
				label: 'Step 4 of 5',
				badge: '+ LOOP CLOSES',
				badgeColor: '#3dd9a4',
				narration:
					'"…which feeds back into the original action, making it stronger." — The loop closes.',
				detail:
					'<strong>Reveal principle:</strong> Close the loop as the narration describes the feedback connection. This is the moment of structural insight — the viewer sees that this is a cycle, not a chain. Narration: "…which feeds back into the original action, making it stronger." Duration: 4–5 seconds.',
				draw: (svg) => {
					svg.innerHTML = `
        <defs>
          <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#ff4f68" opacity="0.7"/></marker>
          <marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#4aafff" opacity="0.7"/></marker>
          <marker id="arr3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#3dd9a4" opacity="0.9"/></marker>
        </defs>
        <circle cx="120" cy="200" r="34" fill="none" stroke="#ff4f68" stroke-width="2"/>
        <text x="120" y="197" font-size="12" font-family="IBM Plex Mono" fill="#ff4f68" text-anchor="middle" font-weight="600">ACTION</text>
        <line x1="154" y1="200" x2="236" y2="200" stroke="#ff4f68" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr)" opacity="0.7"/>
        <circle cx="270" cy="200" r="34" fill="none" stroke="#f5b94a" stroke-width="2"/>
        <text x="270" y="197" font-size="12" font-family="IBM Plex Mono" fill="#f5b94a" text-anchor="middle" font-weight="600">EFFECT</text>
        <line x1="296" y1="172" x2="380" y2="118" stroke="#f5b94a" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr2)" opacity="0.7"/>
        <circle cx="420" cy="90" r="34" fill="none" stroke="#4aafff" stroke-width="2"/>
        <text x="420" y="84" font-size="11" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle" font-weight="600">AMPLIFIER</text>
        <text x="420" y="98" font-size="9" font-family="IBM Plex Mono" fill="#4aafff" opacity="0.6" text-anchor="middle">reinforcing</text>
        <path d="M390,124 Q320,40 200,40 Q140,40 120,166" fill="none" stroke="#3dd9a4" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr3)"/>
        <text x="240" y="28" font-size="9" font-family="IBM Plex Mono" fill="#3dd9a4" text-anchor="middle">feedback path</text>`;
				}
			},
			{
				label: 'Step 5 of 5',
				badge: 'COMPLETE',
				badgeColor: '#3dd9a4',
				narration:
					'"This is a reinforcing feedback loop — each cycle amplifies the next." — Full diagram with labels.',
				detail:
					'<strong>Reveal principle:</strong> Only now show the complete diagram with all labels. The viewer has built this structure step by step and recognizes each element. The full diagram is a confirmation, not an introduction. Narration: "This is a reinforcing feedback loop — each cycle amplifies the next." Duration: 5–6 seconds.',
				draw: (svg) => {
					svg.innerHTML = `
        <defs>
          <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#ff4f68" opacity="0.7"/></marker>
          <marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#4aafff" opacity="0.7"/></marker>
          <marker id="arr3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#3dd9a4" opacity="0.9"/></marker>
        </defs>
        <rect x="1" y="1" width="558" height="278" rx="2" fill="none" stroke="#1e2d40" stroke-width="1"/>
        <circle cx="120" cy="200" r="34" fill="color-mix(in srgb,#ff4f68 8%,transparent)" stroke="#ff4f68" stroke-width="2"/>
        <text x="120" y="197" font-size="12" font-family="IBM Plex Mono" fill="#ff4f68" text-anchor="middle" font-weight="600">ACTION</text>
        <line x1="154" y1="200" x2="236" y2="200" stroke="#ff4f68" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr)" opacity="0.7"/>
        <text x="195" y="214" font-size="8" font-family="IBM Plex Mono" fill="#ff4f68" opacity="0.5" text-anchor="middle">causes</text>
        <circle cx="270" cy="200" r="34" fill="color-mix(in srgb,#f5b94a 8%,transparent)" stroke="#f5b94a" stroke-width="2"/>
        <text x="270" y="197" font-size="12" font-family="IBM Plex Mono" fill="#f5b94a" text-anchor="middle" font-weight="600">EFFECT</text>
        <line x1="296" y1="172" x2="380" y2="118" stroke="#f5b94a" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arr2)" opacity="0.7"/>
        <text x="348" y="158" font-size="8" font-family="IBM Plex Mono" fill="#f5b94a" opacity="0.5" text-anchor="middle">amplifies</text>
        <circle cx="420" cy="90" r="34" fill="color-mix(in srgb,#4aafff 8%,transparent)" stroke="#4aafff" stroke-width="2"/>
        <text x="420" y="84" font-size="11" font-family="IBM Plex Mono" fill="#4aafff" text-anchor="middle" font-weight="600">AMPLIFIER</text>
        <text x="420" y="98" font-size="9" font-family="IBM Plex Mono" fill="#4aafff" opacity="0.6" text-anchor="middle">reinforcing</text>
        <path d="M390,124 Q320,40 200,40 Q140,40 120,166" fill="none" stroke="#3dd9a4" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr3)"/>
        <text x="240" y="28" font-size="9" font-family="IBM Plex Mono" fill="#3dd9a4" text-anchor="middle">feedback path</text>
        <rect x="180" y="120" width="110" height="28" rx="2" fill="color-mix(in srgb,#3dd9a4 10%,transparent)" stroke="#3dd9a4" stroke-width="1"/>
        <text x="235" y="133" font-size="9" font-family="IBM Plex Mono" fill="#3dd9a4" text-anchor="middle" font-weight="600">REINFORCING LOOP</text>
        <text x="235" y="143" font-size="8" font-family="IBM Plex Mono" fill="#3dd9a4" opacity="0.6" text-anchor="middle">each cycle amplifies the next</text>`;
				}
			}
		];

		let currentDiagStep = 0;

		function renderDiagStep() {
			const step = diagSteps[currentDiagStep];
			const svg = document.getElementById('diag-svg');
			step.draw(svg);

			// Stage border
			const stage = document.getElementById('diag-stage');
			stage.style.borderColor =
				currentDiagStep === diagSteps.length - 1
					? '#3dd9a4'
					: currentDiagStep > 0
						? '#1e2d40'
						: '#14202e';

			// Dots
			const dots = document.getElementById('diag-dots');
			dots.innerHTML = diagSteps
				.map(
					(_, i) =>
						`<div class="diag-dot${i === currentDiagStep ? ' active' : ''}" onclick="goDiagStep(${i})"></div>`
				)
				.join('');

			// Detail
			document.getElementById('diag-detail').innerHTML =
				`<div style="font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:${step.badgeColor}; margin-bottom:0.3rem;">${step.badge}</div>` +
				`<div style="font-size:11px; color:var(--vs-muted); margin-bottom:0.4rem; font-style:italic;">${step.narration}</div>` +
				step.detail;

			document.getElementById('diag-prev').disabled = currentDiagStep === 0;
			document.getElementById('diag-next').disabled = currentDiagStep === diagSteps.length - 1;
			document.getElementById('diag-prev').style.opacity = currentDiagStep === 0 ? '0.3' : '1';
			document.getElementById('diag-next').style.opacity =
				currentDiagStep === diagSteps.length - 1 ? '0.3' : '1';
		}

		function diagStep(dir) {
			currentDiagStep = Math.max(0, Math.min(diagSteps.length - 1, currentDiagStep + dir));
			renderDiagStep();
		}
		function goDiagStep(i) {
			currentDiagStep = i;
			renderDiagStep();
		}
		renderDiagStep();

		/* ── QUIZ ── */
		const scores = {};
		function answer(qId, el, correct) {
			if (scores[qId] !== undefined) return;
			scores[qId] = correct ? 1 : 0;
			el.parentElement.querySelectorAll('.option').forEach((o) => {
				o.classList.add('disabled');
				if (o.onclick.toString().includes(',true)')) o.classList.add('correct');
			});
			el.classList.remove('correct');
			if (!correct) el.classList.add('wrong');
			const fb = document.getElementById('fb-' + qId);
			fb.textContent = correct
				? '✓ Correct.'
				: '✗ Not quite — the correct answer is highlighted above.';
			fb.className = 'feedback ' + (correct ? 'ok' : 'bad');
			if (Object.keys(scores).length === 4) {
				const total = Object.values(scores).reduce((a, b) => a + b, 0);
				const sc = document.getElementById('quiz-score');
				sc.style.display = 'block';
				document.getElementById('score-display').textContent = total + ' / 4';
				document.getElementById('score-display').style.color =
					total >= 3 ? 'var(--vs-mint)' : total >= 2 ? 'var(--vs-amber)' : 'var(--vs-red)';
			}
		}

		if (typeof initSpectrum === 'function') actions.initSpectrum = initSpectrum;
		if (typeof draw === 'function') actions.draw = draw;
		if (typeof buildBrollCards === 'function') actions.buildBrollCards = buildBrollCards;
		if (typeof rateBroll === 'function') actions.rateBroll = rateBroll;
		if (typeof updateBrollCounts === 'function') actions.updateBrollCounts = updateBrollCounts;
		if (typeof revealBrollAnalysis === 'function')
			actions.revealBrollAnalysis = revealBrollAnalysis;
		if (typeof buildVFuncs === 'function') actions.buildVFuncs = buildVFuncs;
		if (typeof toggleVFunc === 'function') actions.toggleVFunc = toggleVFunc;
		if (typeof buildMetaphorConcepts === 'function')
			actions.buildMetaphorConcepts = buildMetaphorConcepts;
		if (typeof selectConcept === 'function') actions.selectConcept = selectConcept;
		if (typeof renderMetaphorPanels === 'function')
			actions.renderMetaphorPanels = renderMetaphorPanels;
		if (typeof renderDiagStep === 'function') actions.renderDiagStep = renderDiagStep;
		if (typeof diagStep === 'function') actions.diagStep = diagStep;
		if (typeof goDiagStep === 'function') actions.goDiagStep = goDiagStep;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			_listeners.forEach((l) => l.target.removeEventListener(...l.args));
		};
	});
</script>

<div class="page-wrapper">
	<header class="course-header">
		<div>
			<div class="course-label">Visual Storytelling for Faceless Video</div>
			<div class="course-title">Narrative, Pacing &amp; Visual Communication</div>
		</div>
		<div style="font-size: 11px; color: var(--vs-muted); text-align: right">Module 04 of 10</div>
	</header>

	<div class="module-hero">
		<div class="module-number">04</div>
		<div class="module-tag">Module 04 · Theory + Practice</div>
		<h1 class="module-title">Images, Diagrams &amp;<br /><span>B-Roll Intentionally</span></h1>
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
			<li><a href="#broll-function">The Function of B-Roll</a></li>
			<li><a href="#literal-trap">The Literal Trap</a></li>
			<li><a href="#visual-functions">Five Visual Functions</a></li>
			<li><a href="#metaphors">Visual Metaphors</a></li>
			<li><a href="#diagrams">Diagrams as Sequences</a></li>
			<li><a href="#selection">Selecting Stronger Visuals</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand the five distinct functions a visual can serve in a video</li>
			<li>Identify and avoid the literal trap: imagery that illustrates without contributing</li>
			<li>Select b-roll based on what it adds to meaning, not what it depicts</li>
			<li>Use visual metaphors and conceptual diagrams to explain abstract ideas</li>
			<li>Convert a static diagram into a progressive reveal sequence</li>
		</ul>
	</section>

	<!-- ══════════════════════════════════════
       SECTION 1: THE FUNCTION OF B-ROLL
  ══════════════════════════════════════ -->
	<section id="broll-function" class="section">
		<div class="section-header">
			<span class="section-num">04.01</span>
			<h2 class="section-title">The Function of B-Roll</h2>
		</div>

		<p>
			B-roll is any footage that plays over narration — it is not the primary recording of the
			subject, but the visual layer that accompanies the story being told. In faceless video, b-roll
			is not supplementary. It is the entire visual layer. There is no face, no presenter, no direct
			address — so b-roll is doing all of the visual communicative work for the full duration of the
			video.
		</p>
		<p>
			Most creators approach b-roll as a coverage problem: the narrator is talking, so something
			needs to be on screen. They search a stock library for footage that depicts what is being
			described, and they cut it in. This produces videos where b-roll is visually correlated with
			the narration but functionally inert — it covers the gap without adding anything to the
			message.
		</p>
		<p>
			The more useful question is not <em>what depicts this?</em> but
			<em>what advances this?</em> Each visual should be chosen because it does something the narration
			alone cannot — it adds a dimension of scale, emotion, abstraction, or specificity that the words
			leave open.
		</p>

		<div class="callout blue">
			<div class="callout-label">The Coverage Fallacy</div>
			B-roll chosen to "cover" narration is producing the video equivalent of wallpaper — it fills space
			and adds texture, but it is not communicating. Every visual that merely illustrates what the narration
			already says is a wasted channel. The question is always: what does this visual add that the words
			cannot?
		</div>

		<!-- DEMO: B-Roll Function Canvas -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · B-Roll Function Spectrum</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Every piece of b-roll sits somewhere on the spectrum between purely redundant and
					genuinely additive. Click a position on the spectrum to understand what type of visual it
					represents.
				</p>
				<canvas
					id="broll-func-canvas"
					aria-label="Broll Func Canvas Demonstration"
					role="img"
					tabindex="0"
				></canvas>
				<div
					id="broll-func-desc"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								min-height: 52px;
								background: var(--vs-raised);
							"
				>
					Click anywhere on the spectrum above to learn about that type of visual.
				</div>
			</div>
		</div>
	</section>

	<!-- ══════════════════════════════════════
       SECTION 2: THE LITERAL TRAP
  ══════════════════════════════════════ -->
	<section id="literal-trap" class="section">
		<div class="section-header">
			<span class="section-num">04.02</span>
			<h2 class="section-title">The Literal Trap</h2>
		</div>

		<p>
			The literal trap is the most common visual mistake in faceless video production. It occurs
			when the creator chooses a visual that
			<em>depicts exactly what the narration describes</em> — and nothing more. The narration says "global
			supply chains"; the b-roll shows a container ship. The narration says "people using smartphones";
			the b-roll shows a person looking at a phone. The narration says "money"; the b-roll shows dollar
			bills.
		</p>
		<p>
			Literal b-roll is not wrong, but it is inert. It confirms what the viewer already understood
			from the narration and adds no new dimension. At best, it functions as visual punctuation. At
			worst, it makes the video feel like a stock-footage slideshow — which is exactly how most
			viewers describe low-quality educational content.
		</p>

		<div class="callout">
			<div class="callout-label">Why Literal B-Roll Persists</div>
			Stock libraries are organized by subject, not by function. A search for "teamwork" returns images
			of people shaking hands and gesturing at whiteboards — literal depictions of the word. Creators
			who search by subject will always land in literal territory. Creators who search by the<em
				>feeling or dimension</em
			> they want to add — scale, vulnerability, tension, surprise — find better material.
		</div>

		<!-- DEMO: B-Roll Strength Sorter -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · B-Roll Strength Sorter</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1rem">
					The narration below is fixed. Rate each b-roll option: Strong (adds a dimension), Literal
					(depicts accurately but adds nothing), or Weak (misleads or distracts). Then reveal the
					analysis.
				</p>

				<div class="broll-narration-box">
					<div class="broll-narration-label">Narration line</div>
					"Most people dramatically underestimate how long difficult tasks will take — a cognitive bias
					called the planning fallacy."
				</div>

				<div class="broll-grid" id="broll-cards"></div>

				<div class="broll-score-row">
					<div class="broll-score-chip" style="border-color: var(--vs-mint); color: var(--vs-mint)">
						<span>Strong:</span><span
							id="count-strong"
							style="font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700">0</span
						>
					</div>
					<div
						class="broll-score-chip"
						style="border-color: var(--vs-amber); color: var(--vs-amber)"
					>
						<span>Literal:</span><span
							id="count-literal"
							style="font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700">0</span
						>
					</div>
					<div class="broll-score-chip" style="border-color: var(--vs-red); color: var(--vs-red)">
						<span>Weak:</span><span
							id="count-weak"
							style="font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700">0</span
						>
					</div>
					<button
						class="btn amber"
						onclick={(e) => actions.revealBrollAnalysis()}
						style="margin-left: auto"
					>
						Reveal Analysis
					</button>
				</div>
				<div
					id="broll-analysis"
					style="
								display: none;
								margin-top: 1rem;
								padding: 1rem;
								border: 1px solid var(--vs-border);
								background: #040710;
								font-size: 12px;
								line-height: 1.8;
								color: var(--vs-text);
							"
				></div>
			</div>
		</div>

		<p>
			The shift from literal to strong b-roll is a shift in thinking from
			<em>what is this about?</em> to <em>what dimension is missing?</em> The narration about the
			planning fallacy already communicates the concept clearly. What it cannot communicate is the
			<em>felt experience</em> of underestimation — the person who looks at a project and feels confident,
			then finds themselves exhausted halfway through. A visual that captures that experience adds something.
			A calendar does not.
		</p>
	</section>

	<!-- ══════════════════════════════════════
       SECTION 3: FIVE VISUAL FUNCTIONS
  ══════════════════════════════════════ -->
	<section id="visual-functions" class="section">
		<div class="section-header">
			<span class="section-num">04.03</span>
			<h2 class="section-title">The Five Visual Functions</h2>
		</div>

		<p>
			Rather than categorizing visuals by what they depict, a more useful framework is categorizing
			them by what they <em>do</em>. Every visual in a well-constructed video is performing one of
			five distinct functions. Knowing which function a visual is supposed to serve clarifies both
			the selection decision and the evaluation of whether it is working.
		</p>

		<!-- DEMO: Visual Function Explorer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Visual Function Explorer</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Click any function to expand its definition, visual characteristics, and a concrete
					example. Each function represents a different job a visual can perform.
				</p>
				<div id="vfunc-list"></div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Function</th>
					<th>What It Adds</th>
					<th>Common Failure Mode</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Reinforce</td>
					<td>Emotional texture that the narration describes but cannot convey alone</td>
					<td>Literal depiction instead of felt experience</td>
				</tr>
				<tr>
					<td>Contrast</td>
					<td>A juxtaposition that makes the narration's claim more vivid</td>
					<td>The contrast is too subtle or too obvious</td>
				</tr>
				<tr>
					<td>Establish Scale</td>
					<td>A reference that gives the viewer a sense of proportion</td>
					<td>The scale reference is unfamiliar to the viewer</td>
				</tr>
				<tr>
					<td>Reveal Process</td>
					<td>A visual sequence that shows how something works step-by-step</td>
					<td>The process is too fast or too abstracted to follow</td>
				</tr>
				<tr>
					<td>Atmosphere</td>
					<td>Tonal context that primes the viewer emotionally for the content</td>
					<td>The tone mismatches the narration's register</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ══════════════════════════════════════
       SECTION 4: VISUAL METAPHORS
  ══════════════════════════════════════ -->
	<section id="metaphors" class="section">
		<div class="section-header">
			<span class="section-num">04.04</span>
			<h2 class="section-title">Visual Metaphors &amp; Conceptual Imagery</h2>
		</div>

		<p>
			A visual metaphor is an image or footage choice that uses something concrete to represent
			something abstract. Rather than depicting the concept directly — which for many abstract ideas
			is impossible — it finds a physical analog that carries the same structure or feeling. The
			viewer makes the mapping instantly and unconsciously, which is why well-chosen metaphors feel
			natural rather than clever.
		</p>
		<p>
			Visual metaphors are the most underused tool in faceless video. They require more creative
			effort than literal imagery because you cannot search a stock library for "cognitive bias."
			But they produce the most memorable sequences, because the viewer does cognitive work to make
			the connection — and that work is what lodges the concept in memory.
		</p>

		<!-- DEMO: Visual Metaphor Workshop -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Visual Metaphor Workshop</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Select a concept. Compare three approaches: literal imagery, a conceptual diagram, and a
					visual metaphor. Evaluate which adds the most dimension.
				</p>
				<div id="metaphor-concepts"></div>
				<div id="metaphor-display" style="display: none">
					<div class="metaphor-panels" id="metaphor-panels"></div>
					<div
						id="metaphor-verdict"
						style="
									margin-top: 1rem;
									padding: 0.75rem 1rem;
									border-left: 2px solid var(--vs-red);
									background: color-mix(in srgb, var(--vs-red) 4%, var(--vs-surface));
									font-size: 12px;
									color: var(--vs-text);
									line-height: 1.7;
								"
					></div>
				</div>
			</div>
		</div>

		<div class="callout amber">
			<div class="callout-label">The Mapping Test</div>
			A good visual metaphor passes the mapping test: every structural element of the metaphor corresponds
			to something in the concept. A tightrope walk maps to risk (height = stakes, balance = precision,
			one direction = no going back). A leaking pipe maps to resource drain (pressure = effort, leak =
			waste, destination = goal). If you cannot articulate the mapping, the metaphor is decorative, not
			communicative.
		</div>
	</section>

	<!-- ══════════════════════════════════════
       SECTION 5: DIAGRAMS AS SEQUENCES
  ══════════════════════════════════════ -->
	<section id="diagrams" class="section">
		<div class="section-header">
			<span class="section-num">04.05</span>
			<h2 class="section-title">Diagrams as Sequences, Not Slides</h2>
		</div>

		<p>
			A diagram dropped onto the screen all at once is a problem. The viewer must simultaneously
			parse the narration and decode the entire diagram — two distinct cognitive tasks that share
			the same working memory. The result is that neither task completes fully before the next
			element arrives.
		</p>
		<p>
			The solution is to treat every diagram as a <strong>sequence of reveals</strong> rather than a single
			frame. Each reveal introduces one element of the diagram — one node, one arrow, one label — at the
			moment the narration introduces the corresponding concept. This synchronizes the visual and the
			verbal, reducing load and building a mental model step by step instead of all at once.
		</p>

		<!-- DEMO: Diagram Sequencer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Diagram Sequence Builder</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					This diagram explains a feedback loop. Click through each stage to see how a single
					diagram is broken into a sequence of progressive reveals — each tied to one narration
					beat.
				</p>

				<div style="max-width: 560px; margin: 0 auto">
					<div class="diag-stage" id="diag-stage">
						<svg
							class="diag-svg"
							id="diag-svg"
							viewBox="0 0 560 280"
							xmlns="http://www.w3.org/2000/svg"
						></svg>
					</div>
					<div class="diag-nav" id="diag-nav">
						<button class="btn" onclick={(e) => actions.diagStep(-1)} id="diag-prev">← Prev</button>
						<div
							style="
										display: flex;
										gap: 6px;
										align-items: center;
										flex: 1;
										justify-content: center;
									"
							id="diag-dots"
						></div>
						<button class="btn" onclick={(e) => actions.diagStep(1)} id="diag-next">Next →</button>
					</div>
					<div class="diag-detail" id="diag-detail"></div>
				</div>

				<div
					style="
								margin-top: 1.5rem;
								padding: 1rem;
								border: 1px solid var(--vs-border);
								background: #040710;
								font-size: 11px;
								color: var(--vs-muted);
								line-height: 1.8;
							"
				>
					<div
						style="
									color: var(--vs-red);
									font-size: 10px;
									letter-spacing: 0.12em;
									text-transform: uppercase;
									margin-bottom: 0.4rem;
									font-weight: 600;
								"
					>
						Design principle at work
					</div>
					Each step of the diagram corresponds to exactly one narration beat. The viewer builds the mental
					model incrementally — each element arriving only when they are ready for it. The full diagram
					only appears at step 5, after all components are individually understood.
				</div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Approach</th>
					<th>Cognitive Load</th>
					<th>Comprehension</th>
					<th>Use When</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Full diagram, instant reveal</td>
					<td>Very High</td>
					<td>Low — viewer scans randomly</td>
					<td>Reference material only, not explanation</td>
				</tr>
				<tr>
					<td>Progressive reveal, unsynced</td>
					<td>Medium</td>
					<td>Medium — better but still competes</td>
					<td>Short diagrams with simple structure</td>
				</tr>
				<tr>
					<td>Progressive reveal, synced to narration</td>
					<td>Low</td>
					<td>High — visual and verbal align</td>
					<td>Any explanatory diagram in video</td>
				</tr>
				<tr>
					<td>Animated transition between states</td>
					<td>Low–Medium</td>
					<td>Very High — process is visible</td>
					<td>Showing change, flow, or causation</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ══════════════════════════════════════
       SECTION 6: SELECTING STRONGER VISUALS
  ══════════════════════════════════════ -->
	<section id="selection" class="section">
		<div class="section-header">
			<span class="section-num">04.06</span>
			<h2 class="section-title">Selecting Stronger Visuals: A Practical Method</h2>
		</div>

		<p>
			The practical challenge of visual selection is that you are usually working under time
			pressure against a stock library organized for surface-level searching. Here is a method that
			consistently produces stronger results regardless of the library.
		</p>

		<p>
			Start from the narration line you need to cover. Ask three questions in sequence: (1)
			<strong>What does the viewer need to feel at this moment</strong> — not what they need to
			know, but what they need to feel? (2)
			<strong>What physical situation produces that feeling</strong> in real life? (3)
			<strong>What footage depicts that physical situation</strong> without being so specific it distracts
			from the narration?
		</p>

		<p>
			This method sidesteps the literal trap entirely because you are searching for an emotional
			state rather than a subject. For the planning fallacy narration: the viewer needs to feel the
			experience of confident underestimation. The physical situation: someone energetically
			starting a large task. The footage: a person beginning something with visible enthusiasm — not
			a calendar, not a clock, not a brain diagram.
		</p>

		<div class="callout mint">
			<div class="callout-label">The Three Questions</div>
			(1) What does the viewer need to feel? → (2) What physical situation produces that feeling? → (3)
			What footage depicts that situation without distracting? This sequence reliably breaks the literal
			habit because it begins from emotional function rather than subject matter.
		</div>

		<table>
			<thead>
				<tr>
					<th>Narration topic</th>
					<th>Literal search term</th>
					<th>Better search term</th>
					<th>Why</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Information overload</td>
					<td>"information" "data" "screen"</td>
					<td>"overwhelmed" "drowning" "flood"</td>
					<td>Captures the felt experience, not the subject</td>
				</tr>
				<tr>
					<td>Decision under pressure</td>
					<td>"decision" "choice" "thinking"</td>
					<td>"crossroads" "timer" "narrow path"</td>
					<td>Creates tension the narration describes</td>
				</tr>
				<tr>
					<td>Compounding growth</td>
					<td>"growth" "chart" "increase"</td>
					<td>"snowball" "avalanche" "cascade"</td>
					<td>Visual metaphor for the exponential structure</td>
				</tr>
				<tr>
					<td>Slow deterioration</td>
					<td>"decline" "decrease" "problem"</td>
					<td>"rust" "erosion" "slow leak"</td>
					<td>Physicality makes the gradual quality visceral</td>
				</tr>
				<tr>
					<td>Hidden complexity</td>
					<td>"complex" "system" "network"</td>
					<td>"iceberg" "roots" "machinery"</td>
					<td>The depth/surface contrast maps to the concept</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">04.07</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout">
			<div class="callout-label">Exercise A · Weak B-Roll Replacement</div>
			Find a 2–3 minute educational video that uses heavily literal b-roll. For each piece of footage,
			apply the three-question method: what should the viewer feel here, what physical situation produces
			that feeling, and what footage would you use instead? Write your replacement choices and the function
			each is serving. You do not need to actually source or edit — the exercise is in the diagnostic
			and selection thinking.
		</div>

		<div class="callout amber">
			<div class="callout-label">Exercise B · Static Diagram to Sequence</div>
			Find or create a static diagram of any process with at least 4 components (a flowchart, a cycle,
			a system map). Plan the reveal sequence: which element appears first, what narration line triggers
			each reveal, and what animation or transition — if any — connects each stage. Document this as a
			numbered list with the corresponding narration beat beside each item. This is the planning document
			your editor or motion designer would work from.
		</div>

		<div class="callout blue">
			<div class="callout-label">Exercise C · Metaphor Mapping</div>
			Choose three abstract concepts from your own content area. For each, find a physical metaphor and
			write the mapping — every structural element of the metaphor and what it corresponds to in the concept.
			Reject any metaphor where you cannot complete the mapping fully. The incomplete mappings are the
			ones that will confuse rather than clarify.
		</div>

		<div style="margin-top: 2rem">
			<div
				style="
							font-size: 10px;
							letter-spacing: 0.15em;
							text-transform: uppercase;
							color: var(--vs-muted);
							margin-bottom: 1rem;
						"
			>
				Key terms from this module
			</div>
			<div class="two-col">
				<div class="stats-panel">
					<div class="stat-row">
						<span class="stat-label">Coverage fallacy</span><span class="stat-val"
							>filling ≠ communicating</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Literal trap</span><span class="stat-val"
							>depicts without adding</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Visual function</span><span class="stat-val"
							>what it does, not shows</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Mapping test</span><span class="stat-val"
							>metaphor must map fully</span
						>
					</div>
				</div>
				<div class="stats-panel">
					<div class="stat-row">
						<span class="stat-label">Progressive reveal</span><span class="stat-val"
							>one beat = one element</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Three questions</span><span class="stat-val"
							>feel → situation → footage</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Visual metaphor</span><span class="stat-val"
							>concrete → abstract</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Functional search</span><span class="stat-val"
							>by emotion, not subject</span
						>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 04 — Check Your Understanding</div>
		<div class="quiz-sub">4 questions · No time limit</div>

		<div class="question" id="q1">
			<div class="q-text">
				<span class="q-num">01.</span>A narration line says "social media companies profit from
				outrage." The creator uses b-roll of someone looking at a smartphone with a frustrated
				expression. What is the most accurate description of this visual choice?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					Strong — the emotional expression adds a dimension the narration cannot convey
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q1', e.currentTarget, true)}
				>
					Literal — it accurately depicts the subject but adds no dimension beyond what the
					narration already communicates; the viewer gains nothing from the visual that they did not
					get from the words
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					Weak — the frustration expression contradicts the concept of profit, creating mixed
					signals
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					Atmospheric — it sets a tonal context appropriate to the serious subject
				</button>
			</div>
			<div class="feedback" id="fb-q1"></div>
		</div>

		<div class="question" id="q2">
			<div class="q-text">
				<span class="q-num">02.</span>A creator wants to visually explain a concept with four
				distinct components. They have 40 seconds of narration. What is the most effective approach
				to presenting the diagram?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					Show the full diagram at the start so viewers can orient before the narration begins
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q2', e.currentTarget, true)}
				>
					Reveal each component progressively, synchronized with the narration beat that introduces
					that component, so the viewer builds the model incrementally
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					Show the diagram only at the end, after the narration has explained all four components
					verbally
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					Animate all four components simultaneously with a brief hold on the full diagram at the
					end
				</button>
			</div>
			<div class="feedback" id="fb-q2"></div>
		</div>

		<div class="question" id="q3">
			<div class="q-text">
				<span class="q-num">03.</span>According to the mapping test, when is a visual metaphor
				considered effective?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					When the metaphor is surprising or unexpected enough to create viewer delight
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					When the audience recognizes the metaphor without any explanation from the narrator
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q3', e.currentTarget, true)}
				>
					When every structural element of the metaphor corresponds to a specific element of the
					concept being explained, so the mapping is complete and unambiguous
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					When the metaphor is more visually interesting than a literal depiction of the concept
					would be
				</button>
			</div>
			<div class="feedback" id="fb-q3"></div>
		</div>

		<div class="question" id="q4">
			<div class="q-text">
				<span class="q-num">04.</span>Using the three-question method for visual selection, what is
				the correct starting point?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					The subject matter of the narration — what topic is being discussed
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					The visual style established earlier in the video — what footage would match
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q4', e.currentTarget, true)}
				>
					The emotional state the viewer needs to be in at this moment — what the viewer needs to
					feel, not what they need to know
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					The available footage — what is already in the library that relates to the topic
				</button>
			</div>
			<div class="feedback" id="fb-q4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-display">—</div>
			<div class="score-label">questions correct out of 4</div>
		</div>
	</section>

	<div class="nav-links">
		<a href="./03" class="prev-link">← Module 03: Structuring Text for Video</a>
		<a href="./05" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">Composition &amp; Visual Hierarchy in Video Frames</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</div>
</div>

<style>
	.page-wrapper {
		background: var(--vs-bg);
		color: var(--vs-text);
		font-family: 'IBM Plex Mono', monospace;
		font-size: 14px;
		line-height: 1.8;
	}

	.page-wrapper {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem 6rem;
	}
	:global(.two-col) {
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
		:global(.two-col),
		:global(.three-col) {
			grid-template-columns: 1fr;
		}
	}

	.course-header {
		border-bottom: 1px solid var(--vs-border);
		padding: 2rem 0 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.course-label {
		font-size: 11px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-muted);
	}
	.course-title {
		font-family: 'Syne', sans-serif;
		font-size: 13px;
		color: var(--vs-muted);
		font-weight: 400;
	}

	.module-hero {
		padding: 5rem 0 3.5rem;
		border-bottom: 1px solid var(--vs-border);
		position: relative;
		overflow: hidden;
	}
	.module-hero::before {
		content: '';
		position: absolute;
		inset: 0;
		pointer-events: none;
		background: repeating-linear-gradient(
			0deg,
			transparent,
			transparent 2px,
			rgba(255, 79, 104, 0.012) 2px,
			rgba(255, 79, 104, 0.012) 4px
		);
	}
	.module-number {
		font-family: 'Syne', sans-serif;
		font-size: clamp(80px, 15vw, 140px);
		font-weight: 800;
		line-height: 1;
		color: transparent;
		-webkit-text-stroke: 1px var(--vs-border2);
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
		color: var(--vs-red);
		border: 1px solid var(--vs-red);
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
		color: var(--vs-red);
	}

	.toc {
		margin: 3rem 0;
		padding: 1.5rem;
		border: 1px solid var(--vs-border);
		background: var(--vs-surface);
	}
	.toc-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-muted);
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
		color: var(--vs-muted);
		text-decoration: none;
		border: 1px solid var(--vs-border);
		padding: 4px 10px;
		transition: all 0.15s;
	}
	.toc-list a:hover {
		color: var(--vs-red);
		border-color: var(--vs-red);
	}

	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--vs-red);
		background: var(--vs-surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-red);
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
		color: var(--vs-amber);
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
		border-bottom: 1px solid var(--vs-border);
	}
	.section-num {
		font-size: 11px;
		color: var(--vs-amber);
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
		color: var(--vs-text);
	}
	p:last-child {
		margin-bottom: 0;
	}
	strong {
		color: var(--vs-red);
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
		background: #040710;
		border: 1px solid var(--vs-border);
		padding: 1px 6px;
		font-size: 12px;
		color: var(--vs-mint);
		font-family: 'IBM Plex Mono', monospace;
	}

	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 5%, var(--vs-surface));
		font-size: 13px;
	}
	:global(.callout.amber) {
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-surface));
	}
	:global(.callout.blue) {
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 5%, var(--vs-surface));
	}
	:global(.callout.mint) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 5%, var(--vs-surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-red);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	:global(.callout.amber .callout-label) {
		color: var(--vs-amber);
	}
	:global(.callout.blue .callout-label) {
		color: var(--vs-blue);
	}
	:global(.callout.mint .callout-label) {
		color: var(--vs-mint);
	}

	.demo-box {
		background: var(--vs-surface);
		border: 1px solid var(--vs-border);
		margin: 2rem 0;
	}
	.demo-header {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--vs-border);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.demo-header > span {
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-muted);
	}
	:global(.demo-badge) {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	:global(.demo-badge.interactive) {
		color: var(--vs-red);
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
	}
	:global(.demo-badge.animated) {
		color: var(--vs-amber);
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	:global(.btn) {
		background: transparent;
		border: 1px solid var(--vs-border2);
		color: var(--vs-text);
		padding: 6px 16px;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s;
	}
	:global(.btn:hover) {
		border-color: var(--vs-red);
		color: var(--vs-red);
	}
	:global(.btn.active) {
		border-color: var(--vs-red);
		color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
	}
	:global(.btn.amber:hover) {
		border-color: var(--vs-amber);
		color: var(--vs-amber);
	}
	:global(.btn.amber.active) {
		border-color: var(--vs-amber);
		color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	:global(.btn.mint:hover) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	:global(.btn.mint.active) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
	}
	:global(.btn.blue:hover) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
	}
	:global(.btn.blue.active) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 10%, transparent);
	}
	:global(.btn-row) {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.25rem;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--vs-raised);
		color: var(--vs-red);
		text-align: left;
		padding: 0.6rem 1rem;
		border: 1px solid var(--vs-border);
		font-weight: 600;
		letter-spacing: 0.05em;
	}
	td {
		padding: 0.5rem 1rem;
		border: 1px solid var(--vs-border);
		color: var(--vs-text);
	}
	tr:nth-child(even) td {
		background: color-mix(in srgb, var(--vs-raised) 50%, transparent);
	}

	.divider {
		border: none;
		border-top: 1px solid var(--vs-border);
		margin: 3rem 0;
	}
	.stats-panel {
		background: #040710;
		border: 1px solid var(--vs-border);
		padding: 1rem;
		font-size: 12px;
	}
	.stat-row {
		display: flex;
		justify-content: space-between;
		padding: 0.2rem 0;
		border-bottom: 1px solid var(--vs-border);
	}
	.stat-row:last-child {
		border-bottom: none;
	}
	.stat-label {
		color: var(--vs-muted);
	}
	.stat-val {
		color: var(--vs-red);
		font-weight: 600;
	}

	.progress-bar-wrap {
		height: 3px;
		background: var(--vs-border);
		width: 100%;
		margin: 2rem 0 0;
	}
	.progress-bar-fill {
		height: 100%;
		background: var(--vs-red);
		width: 0;
		transition: width 0.4s ease;
	}

	/* QUIZ */
	.quiz-section {
		margin: 4rem 0;
		padding: 2rem;
		border: 1px solid var(--vs-border);
		background: var(--vs-surface);
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
		color: var(--vs-muted);
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
		color: var(--vs-amber);
		margin-right: 0.5rem;
	}
	:global(.options) {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	:global(.option) {
		padding: 0.6rem 1rem;
		border: 1px solid var(--vs-border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		user-select: none;
		font-family: 'IBM Plex Mono', monospace;
	}
	:global(.option:hover) {
		border-color: var(--vs-border2);
		background: var(--vs-raised);
	}
	:global(.option.correct) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
		color: var(--vs-mint);
	}
	:global(.option.wrong) {
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
		color: var(--vs-red);
	}
	:global(.option.disabled) {
		pointer-events: none;
	}
	:global(.feedback) {
		font-size: 12px;
		margin-top: 0.75rem;
		min-height: 1.5em;
		color: var(--vs-muted);
	}
	:global(.feedback.ok) {
		color: var(--vs-mint);
	}
	:global(.feedback.bad) {
		color: var(--vs-red);
	}
	.quiz-score {
		margin-top: 2rem;
		padding: 1.5rem;
		border: 1px solid var(--vs-border);
		text-align: center;
		display: none;
	}
	.score-num {
		font-family: 'Syne', sans-serif;
		font-size: 36px;
		font-weight: 800;
		color: var(--vs-red);
	}
	.score-label {
		font-size: 12px;
		color: var(--vs-muted);
		margin-top: 0.25rem;
	}

	.nav-links {
		display: flex;
		justify-content: space-between;
		align-items: stretch;
		margin-top: 4rem;
		flex-wrap: wrap;
		gap: 1rem;
	}
	:global(.prev-link) {
		font-size: 12px;
		color: var(--vs-muted);
		text-decoration: none;
		border: 1px solid var(--vs-border);
		padding: 0.75rem 1.25rem;
		transition: all 0.2s;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}
	:global(.prev-link:hover) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
	}
	.next-module {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem 2rem;
		border: 1px solid var(--vs-border);
		text-decoration: none;
		transition: all 0.2s;
		background: var(--vs-surface);
		flex: 1;
	}
	.next-module:hover {
		border-color: var(--vs-amber);
	}
	.next-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-muted);
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
		color: var(--vs-amber);
	}

	/* ══════════════════════════════════════
     MODULE-SPECIFIC COMPONENTS
  ══════════════════════════════════════ */

	/* ── B-ROLL SORTER ── */
	.broll-narration-box {
		padding: 1rem 1.5rem;
		border: 1px solid var(--vs-border2);
		background: #040710;
		font-size: 13px;
		color: #fff;
		margin-bottom: 1.5rem;
		border-left: 2px solid var(--vs-amber);
	}
	.broll-narration-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-amber);
		margin-bottom: 0.4rem;
	}
	.broll-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}
	@media (max-width: 640px) {
		.broll-grid {
			grid-template-columns: 1fr 1fr;
		}
	}
	:global(.broll-card) {
		border: 1px solid var(--vs-border);
		background: var(--vs-raised);
		padding: 0;
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
		overflow: hidden;
	}
	:global(.broll-card:hover) {
		border-color: var(--vs-border2);
	}
	:global(.broll-card.rated-strong) {
		border-color: var(--vs-mint);
	}
	:global(.broll-card.rated-literal) {
		border-color: var(--vs-amber);
	}
	:global(.broll-card.rated-weak) {
		border-color: var(--vs-red);
	}
	:global(.broll-thumb) {
		height: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28px;
		position: relative;
		overflow: hidden;
	}
	:global(.broll-thumb-label) {
		position: absolute;
		bottom: 4px;
		right: 6px;
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: rgba(255, 255, 255, 0.35);
	}
	:global(.broll-desc) {
		padding: 0.5rem 0.6rem;
		font-size: 10px;
		color: var(--vs-text);
		border-top: 1px solid var(--vs-border);
		line-height: 1.5;
	}
	:global(.broll-rating-strip) {
		display: flex;
		border-top: 1px solid var(--vs-border);
	}
	:global(.broll-rate-btn) {
		flex: 1;
		padding: 4px;
		font-size: 9px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		text-align: center;
		cursor: pointer;
		border-right: 1px solid var(--vs-border);
		transition: all 0.15s;
		color: var(--vs-muted);
		background: transparent;
		font-family: 'IBM Plex Mono', monospace;
		border-top: none;
		border-left: none;
		border-bottom: none;
	}
	:global(.broll-rate-btn:last-child) {
		border-right: none;
	}
	:global(.broll-rate-btn:hover) {
		color: #fff;
		background: var(--vs-dim);
	}
	:global(.broll-rate-btn.sel-strong) {
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 12%, transparent);
	}
	:global(.broll-rate-btn.sel-literal) {
		color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 12%, transparent);
	}
	:global(.broll-rate-btn.sel-weak) {
		color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 12%, transparent);
	}
	.broll-score-row {
		display: flex;
		gap: 1rem;
		margin-top: 0.75rem;
		flex-wrap: wrap;
	}
	.broll-score-chip {
		padding: 4px 12px;
		border: 1px solid;
		font-size: 11px;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	/* ── VISUAL FUNCTION MATRIX ── */
	:global(.vfunc-row) {
		display: flex;
		align-items: stretch;
		gap: 0;
		border: 1px solid var(--vs-border);
		overflow: hidden;
		margin: 0.5rem 0;
		cursor: pointer;
		transition: border-color 0.15s;
	}
	:global(.vfunc-row:hover) {
		border-color: var(--vs-border2);
	}
	:global(.vfunc-row.selected) {
		border-color: var(--vs-red);
	}
	:global(.vfunc-icon) {
		width: 52px;
		min-width: 52px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 20px;
		background: var(--vs-raised);
		border-right: 1px solid var(--vs-border);
	}
	:global(.vfunc-body) {
		flex: 1;
		padding: 0.6rem 1rem;
	}
	:global(.vfunc-name) {
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		margin-bottom: 0.2rem;
	}
	:global(.vfunc-desc) {
		font-size: 11px;
		color: var(--vs-muted);
		line-height: 1.5;
	}
	:global(.vfunc-badge) {
		width: 52px;
		min-width: 52px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 0.08em;
	}
	:global(.vfunc-example) {
		padding: 0.75rem 1rem;
		font-size: 12px;
		color: var(--vs-text);
		line-height: 1.7;
		border-top: 1px solid var(--vs-border2);
		display: none;
		background: color-mix(in srgb, var(--vs-red) 4%, var(--vs-surface));
	}
	:global(.vfunc-example.open) {
		display: block;
	}
	:global(.vfunc-example strong) {
		color: var(--vs-red);
	}

	/* ── DIAGRAM SEQUENCER ── */
	:global(.diag-stage) {
		border: 1px solid var(--vs-border);
		background: var(--vs-raised);
		aspect-ratio: 16/9;
		position: relative;
		overflow: hidden;
		transition: border-color 0.2s;
	}
	:global(.diag-stage.current) {
		border-color: var(--vs-red);
	}
	:global(.diag-stage-num) {
		position: absolute;
		top: 8px;
		left: 10px;
		font-size: 9px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-muted);
	}
	:global(.diag-stage-badge) {
		position: absolute;
		top: 8px;
		right: 10px;
		font-size: 9px;
		padding: 2px 6px;
		border: 1px solid;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.diag-nav {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.75rem;
		flex-wrap: wrap;
	}
	:global(.diag-dot) {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		border: 1px solid var(--vs-border2);
		cursor: pointer;
		transition: all 0.15s;
	}
	:global(.diag-dot.active) {
		background: var(--vs-red);
		border-color: var(--vs-red);
	}
	:global(.diag-detail) {
		margin-top: 0.75rem;
		padding: 0.75rem 1rem;
		border-left: 2px solid var(--vs-border2);
		font-size: 12px;
		color: var(--vs-text);
		line-height: 1.7;
		min-height: 52px;
	}
	:global(.diag-detail strong) {
		color: var(--vs-red);
	}

	/* ── SVG DIAGRAM ELEMENTS ── */
	.diag-svg {
		width: 100%;
		height: 100%;
	}

	/* ── METAPHOR WORKSHOP ── */
	:global(.metaphor-concept-pill) {
		display: inline-block;
		padding: 4px 14px;
		border: 1px solid var(--vs-border2);
		font-size: 11px;
		cursor: pointer;
		transition: all 0.15s;
		margin: 3px;
		color: var(--vs-muted);
	}
	:global(.metaphor-concept-pill:hover) {
		border-color: var(--vs-red);
		color: var(--vs-red);
	}
	:global(.metaphor-concept-pill.selected) {
		border-color: var(--vs-red);
		color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
	}
	.metaphor-panels {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1px;
		background: var(--vs-border);
		margin-top: 1.25rem;
	}
	@media (max-width: 640px) {
		.metaphor-panels {
			grid-template-columns: 1fr;
		}
	}
	:global(.metaphor-panel) {
		background: var(--vs-raised);
		padding: 1rem;
	}
	:global(.metaphor-panel-label) {
		font-size: 9px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		margin-bottom: 0.75rem;
		font-weight: 600;
		padding-bottom: 0.4rem;
		border-bottom: 1px solid var(--vs-border);
	}
	:global(.metaphor-visual) {
		height: 100px;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 0.75rem;
		position: relative;
	}
	:global(.metaphor-text) {
		font-size: 11px;
		color: var(--vs-text);
		line-height: 1.6;
	}
	:global(.metaphor-verdict) {
		font-size: 10px;
		margin-top: 0.5rem;
		padding: 3px 8px;
		display: inline-block;
		border: 1px solid;
	}

	/* ── BROLL FUNCTION CANVAS ── */
	#broll-func-canvas {
		display: block;
		width: 100%;
		height: 200px;
		border: 1px solid var(--vs-border);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
