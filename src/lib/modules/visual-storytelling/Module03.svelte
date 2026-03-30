<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-unused-expressions, no-undef, no-useless-assignment */
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
		/* ─── READING PROGRESS ─── */
		_addWinListener('scroll', () => {
			const el = document.getElementById('reading-progress');
			const docH = document.documentElement.scrollHeight - window.innerHeight;
			if (docH > 0) el.style.width = Math.min(100, (window.scrollY / docH) * 100) + '%';
		});

		/* ════════════════════════════════════════
   FRAME ANATOMY DEMO
════════════════════════════════════════ */
		const layerStates = {
			headline: false,
			support: false,
			annotation: false,
			lower: false,
			clutter: false
		};
		const layerDescs = {
			headline:
				'HEADLINE LAYER — Primary claim. Highest visual weight in the frame. Font: Syne 800. Position: upper-left (highest reading priority in LTR cultures). Accent bar below creates spatial anchor without competing for hierarchy.',
			support:
				'SUPPORTING POINT LAYER — Secondary hierarchy. Semi-transparent scrim improves legibility over footage. Left accent bar creates visual grouping with the content it supports. Position: lower-left, below visual centre.',
			annotation:
				'ANNOTATION LAYER — Tertiary hierarchy. Small, low-contrast, high letter-spacing for legibility at small sizes. Upper-right position carries the lowest visual weight in the frame. Leader line locates without directing focus away from primary.',
			lower:
				'LOWER THIRD LAYER — A persistent identification or context strip. Anchored to the bottom edge of frame — a convention that viewers recognize and process without effort. Vertical accent bar creates clear hierarchy between label and title.',
			clutter:
				'CLUTTER LAYER — This is what happens when every element is "justified" individually. No hierarchy survives. No element has priority. The eye moves randomly and settles nowhere. Remove the clutter to restore the signal.'
		};

		function toggleLayer(name) {
			const isClutter = name === 'clutter';
			layerStates[name] = !layerStates[name];

			const el = document.getElementById('layer-' + name);
			el.classList.toggle('hidden', !layerStates[name]);

			// Update button state
			const btn = document.getElementById(
				'tl-' +
					{ headline: 'hl', support: 'sp', annotation: 'an', lower: 'lt', clutter: 'cl' }[name]
			);
			if (btn) btn.classList.toggle('active', layerStates[name]);
			if (name === 'clutter' && btn) btn.classList.toggle('red', layerStates[name]);

			// Update description — show last toggled-on layer's desc, or default
			const active = Object.entries(layerStates)
				.filter(([, v]) => v)
				.map(([k]) => k);
			const last = active[active.length - 1];
			document.getElementById('layer-desc').textContent = last
				? layerDescs[last]
				: 'Toggle layers above to explore how text elements occupy and compete within a video frame.';
		}

		/* ════════════════════════════════════════
   HIERARCHY BUILDER
════════════════════════════════════════ */
		const hierLevels = [
			{
				label: 'Headline',
				size: 32,
				weight: 800,
				color: '#ffffff',
				opacity: 100,
				sampleText: 'The Signal Reaches You'
			},
			{
				label: 'Supporting',
				size: 14,
				weight: 400,
				color: '#f5b94a',
				opacity: 80,
				sampleText: 'Noise-to-signal ratio: the core challenge'
			},
			{
				label: 'Annotation',
				size: 10,
				weight: 300,
				color: '#4aafff',
				opacity: 55,
				sampleText: 'ref. focal node'
			},
			{
				label: 'Ambient',
				size: 8,
				weight: 300,
				color: '#ffffff',
				opacity: 15,
				sampleText: 'background context'
			}
		];

		function buildHierControls() {
			const el = document.getElementById('hier-controls');
			el.innerHTML = hierLevels
				.map(
					(lv, i) => `
    <div class="hier-row">
      <div class="hier-rank" style="background:color-mix(in srgb,var(--vs-mint) ${[100, 60, 35, 15][i]}%,transparent);color:#fff;">${i + 1}</div>
      <div class="hier-label">${lv.label}</div>
      <div style="flex:1; display:flex; align-items:center; gap:0.5rem;">
        <input type="range" min="7" max="48" value="${lv.size}" step="1"
          style="flex:1; -webkit-appearance:none; height:3px; background:var(--vs-border2); outline:none;"
          oninput="hierLevels[${i}].size=+this.value; renderHierPreview()">
      </div>
      <div class="hier-props" id="hp-${i}">${lv.size}px · ${lv.opacity}% opacity</div>
    </div>
  `
				)
				.join('');
			// Style thumbs
			document.querySelectorAll('#hier-controls input[type=range]').forEach((inp) => {
				inp.style.cssText += '; -webkit-appearance:none;';
			});
			renderHierPreview();
		}

		function renderHierPreview() {
			const el = document.getElementById('hier-preview');
			el.innerHTML = hierLevels
				.map((lv, i) => {
					document.getElementById('hp-' + i) &&
						(document.getElementById('hp-' + i).textContent =
							`${lv.size}px · ${lv.opacity}% opacity`);
					return `<div style="font-family:'${i === 0 ? 'Syne' : 'IBM Plex Mono'}',monospace; font-weight:${lv.weight}; font-size:${lv.size}px; color:${lv.color}; opacity:${lv.opacity / 100}; line-height:1.2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${lv.sampleText}</div>`;
				})
				.join('');

			// Assess
			const sizes = hierLevels.map((l) => l.size);
			const ratio01 = sizes[0] / sizes[1];
			const ratio12 = sizes[1] / sizes[2];
			let msg = '';
			if (ratio01 < 1.5)
				msg =
					'⚠ Headline and supporting text are too close in size — the hierarchy is unclear. Aim for at least 1.8× difference.';
			else if (ratio01 > 5)
				msg =
					'· Very strong separation between headline and support — works well for bold statement formats.';
			else
				msg = `✓ Size ratio: headline is ${ratio01.toFixed(1)}× the supporting text. ${ratio01 >= 2 ? 'Clear hierarchy.' : 'Acceptable — consider increasing the gap slightly.'}`;
			const aEl = document.getElementById('hier-assessment');
			if (aEl)
				aEl.innerHTML = `<div style="font-size:11px; color:var(--vs-text); padding:0.75rem 1rem; border-left:2px solid var(--vs-mint); background:var(--vs-raised);">${msg}</div>`;
		}

		buildHierControls();

		/* ════════════════════════════════════════
   CONTRAST CHECKER
════════════════════════════════════════ */
		const contrastColors = [
			{ label: 'White', hex: '#ffffff' },
			{ label: 'Mint', hex: '#3dd9a4' },
			{ label: 'Amber', hex: '#f5b94a' },
			{ label: 'Blue', hex: '#4aafff' },
			{ label: 'Red', hex: '#ff4f68' },
			{ label: 'Muted grey', hex: '#7a8a9a' }
		];

		function luminance(hex) {
			const r = parseInt(hex.slice(1, 3), 16) / 255,
				g = parseInt(hex.slice(3, 5), 16) / 255,
				b = parseInt(hex.slice(5, 7), 16) / 255;
			const toL = (c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
			return 0.2126 * toL(r) + 0.7152 * toL(g) + 0.0722 * toL(b);
		}

		function contrastRatio(fg, bg) {
			const l1 = Math.max(luminance(fg), luminance(bg));
			const l2 = Math.min(luminance(fg), luminance(bg));
			return (l1 + 0.05) / (l2 + 0.05);
		}

		function bgHexFromBrightness(pct) {
			const v = Math.round(pct * 2.55);
			return '#' + v.toString(16).padStart(2, '0').repeat(3);
		}

		function updateContrast() {
			const bright = +document.getElementById('bg-bright').value;
			document.getElementById('bg-bright-val').textContent = bright + '%';
			const bgHex = bgHexFromBrightness(bright);
			const swatches = document.getElementById('contrast-swatches');
			swatches.innerHTML = '';
			let bestLabel = '',
				bestRatio = 0,
				worstLabel = '',
				worstRatio = 99;

			contrastColors.forEach((c) => {
				const ratio = contrastRatio(c.hex, bgHex);
				if (ratio > bestRatio) {
					bestRatio = ratio;
					bestLabel = c.label;
				}
				if (ratio < worstRatio) {
					worstRatio = ratio;
					worstLabel = c.label;
				}
				const pass = ratio >= 4.5;
				const div = document.createElement('div');
				div.className = 'contrast-swatch';
				div.style.background = bgHex;
				div.style.color = c.hex;
				div.style.flex = '1';
				div.style.minWidth = '80px';
				div.style.flexDirection = 'column';
				div.style.display = 'flex';
				div.style.gap = '4px';
				div.style.borderColor = pass ? '#3dd9a430' : '#ff4f6830';
				div.innerHTML = `<span style="font-family:'IBM Plex Mono',monospace; font-size:12px;">${c.label}</span><span style="font-size:10px; color:${pass ? '#3dd9a4' : '#ff4f68'}; font-family:'IBM Plex Mono',monospace;">${ratio.toFixed(1)}:1 ${pass ? '✓' : '✗'}</span>`;
				swatches.appendChild(div);
			});

			const verdict =
				bright > 55
					? `High-brightness background (${bright}%). Most text colors fail. ${bestLabel} performs best at ${bestRatio.toFixed(1)}:1. At this brightness, use a dark scrim behind text or switch to dark text on a lighter overlay.`
					: bright > 30
						? `Mid-range background (${bright}%). Some colors pass, others are marginal. ${bestLabel} (${bestRatio.toFixed(1)}:1) is the strongest choice. ${worstLabel} (${worstRatio.toFixed(1)}:1) is risky — avoid for important text.`
						: `Low-brightness background (${bright}%). Most light text colors pass comfortably. ${bestLabel} leads at ${bestRatio.toFixed(1)}:1. This is the ideal range for on-screen text legibility in faceless video.`;
			document.getElementById('contrast-verdict').textContent = verdict;
		}
		updateContrast();

		/* ════════════════════════════════════════
   TEXT TREATMENT STUDIO
════════════════════════════════════════ */
		function selectTreatment(name) {
			document.querySelectorAll('.treatment-tab').forEach((t, i) => {
				t.classList.toggle('active', ['headline', 'support', 'annotation'][i] === name);
			});
			document.querySelectorAll('.treatment-panel').forEach((p, i) => {
				p.classList.toggle(
					'active',
					['tp-headline', 'tp-support', 'tp-annotation'][i] === 'tp-' + name
				);
			});
		}

		let hlColor = '#ffffff';
		function setHlColor(hex) {
			hlColor = hex;
			['white', 'mint', 'amber'].forEach(
				(c) =>
					document.getElementById('hlc-' + c) &&
					document.getElementById('hlc-' + c).classList.remove('active')
			);
			const map = { '#ffffff': 'hlc-white', '#3dd9a4': 'hlc-mint', '#f5b94a': 'hlc-amber' };
			if (map[hex]) {
				const b = document.getElementById(map[hex]);
				b.classList.add('active');
				if (hex === '#f5b94a') b.classList.add('amber');
			}
			updateTreatment('headline');
		}

		function updateTreatment(type) {
			if (type === 'headline') {
				const size = document.getElementById('hl-size').value;
				const ls = document.getElementById('hl-ls').value;
				const lh = document.getElementById('hl-lh').value;
				document.getElementById('hl-size-v').textContent = size;
				document.getElementById('hl-ls-v').textContent = ls;
				document.getElementById('hl-lh-v').textContent = lh;
				const el = document.getElementById('hl-preview');
				el.style.fontSize = size + 'vw';
				el.style.letterSpacing = ls + 'px';
				el.style.lineHeight = lh;
				el.style.color = hlColor;
				const v = document.getElementById('hl-verdict');
				const s = parseFloat(size);
				if (v)
					v.textContent =
						s < 2.5
							? '⚠ Too small for a headline — will not establish primary hierarchy at typical viewing distances.'
							: s > 5.5
								? '· Very large — powerful for single-word statements; may crowd the frame for longer phrases.'
								: '✓ Good headline size range for a 16:9 frame.';
			}
			if (type === 'support') {
				const size = document.getElementById('sp-size').value;
				const opacity = document.getElementById('sp-opacity').value;
				const barW = document.getElementById('sp-bar').value;
				document.getElementById('sp-size-v').textContent = size;
				document.getElementById('sp-opacity-v').textContent = opacity + '%';
				document.getElementById('sp-bar-v').textContent = barW + 'px';
				const el = document.getElementById('sp-main');
				el.style.fontSize = size + 'vw';
				el.style.opacity = opacity / 100;
				document.getElementById('sp-preview').style.borderLeftWidth = barW + 'px';
				const v = document.getElementById('sp-verdict');
				if (v)
					v.textContent =
						parseFloat(opacity) < 60
							? '⚠ Below 60% opacity, the text may be difficult to read on light backgrounds.'
							: '✓ Opacity sits in a readable range. Pair with a semi-transparent background scrim for footage use.';
			}
			if (type === 'annotation') {
				const size = document.getElementById('an-size').value;
				const opacity = document.getElementById('an-opacity').value;
				const lineW = document.getElementById('an-line').value;
				document.getElementById('an-size-v').textContent = size;
				document.getElementById('an-opacity-v').textContent = opacity + '%';
				document.getElementById('an-line-v').textContent = lineW + 'px';
				const el = document.getElementById('an-main');
				el.style.fontSize = size + 'vw';
				el.style.opacity = opacity / 100;
				const lineEl = document.getElementById('an-line-el');
				lineEl.style.width = lineW + 'px';
				lineEl.style.opacity = opacity / 100;
				const v = document.getElementById('an-verdict');
				if (v)
					v.textContent =
						parseFloat(size) > 1.2
							? '· Getting large for an annotation — this size approaches supporting-point territory.'
							: '✓ Annotation size is appropriately subordinate.';
			}
		}

		/* ════════════════════════════════════════
   DECISION TREE
════════════════════════════════════════ */
		const dtreeNodes = [
			{
				id: 0,
				q: "Is this text the primary focus of the viewer's attention at this moment?",
				opts: [
					{ label: "Yes — it's the main message", next: 1 },
					{ label: 'No — it supports the visual or narration', next: 2 }
				]
			},
			{
				id: 1,
				q: 'Does revealing it gradually (word-by-word or phrase-by-phrase) add meaning — e.g. building suspense or matching narration rhythm?',
				opts: [
					{
						label: 'Yes — the reveal is the point',
						next: 'animate',
						reason:
							'Animate it. Progressive reveal of a headline reinforces narrative rhythm and builds anticipation. Use ease-out for each phrase unit.'
					},
					{
						label: 'No — the full text is needed immediately',
						next: 'static',
						reason:
							'Keep it static. If the full text is needed at once, animation delays comprehension without adding value. A precise, timed static appearance is more powerful.'
					}
				]
			},
			{
				id: 2,
				q: "Does the text need to direct the viewer's eye toward a specific location in the frame?",
				opts: [
					{ label: "Yes — it's pointing to something", next: 3 },
					{
						label: "No — it's just labelling or providing context",
						next: 'static',
						reason:
							'Keep it static. Context and label text has low visual priority — animation would pull disproportionate attention. Appear on cue, stay visible, fade cleanly.'
					}
				]
			},
			{
				id: 3,
				q: "Is the thing it's pointing to already visible, or does it appear after the text?",
				opts: [
					{
						label: "Already visible — the text labels what's there",
						next: 'either',
						reason:
							'Either works. A static appear is clean and efficient. A subtle slide-in from the direction of the target can reinforce the spatial relationship — but only if the motion is very short (150–200ms).'
					},
					{
						label: 'Appears after — the text anticipates something',
						next: 'animate',
						reason:
							'Animate it. A text element that precedes its referent can use motion to suggest where to look — e.g. a short pulse or directional nudge before the element appears. Keep it subtle.'
					}
				]
			}
		];

		let dtreePath = [0];
		let dtreeChoices = {};

		function renderDTree() {
			const container = document.getElementById('dtree-container');
			container.innerHTML = '';
			dtreePath.forEach((nodeId, depth) => {
				if (typeof nodeId === 'number') {
					const node = dtreeNodes[nodeId];
					const div = document.createElement('div');
					div.className = 'dnode' + (depth === dtreePath.length - 1 ? ' active' : '');
					div.innerHTML = `<div class="dnode-q">${node.q}</div><div class="dnode-opts">${node.opts.map((o, i) => `<div class="dnode-opt${dtreeChoices[nodeId] === i ? ' chosen' : ''}" onclick="chooseDTree(${nodeId},${i},${JSON.stringify(o.next)},${JSON.stringify(o.reason || '')})">${o.label}</div>`).join('')}</div>`;
					if (depth > 0) {
						const conn = document.createElement('div');
						conn.className = 'dtree-connector';
						container.appendChild(conn);
					}
					container.appendChild(div);
				}
			});

			// Result
			const lastId = dtreePath[dtreePath.length - 1];
			if (typeof lastId === 'string') {
				const conn = document.createElement('div');
				conn.className = 'dtree-connector';
				container.appendChild(conn);
				const res = document.createElement('div');
				const reasonKey = Object.keys(dtreeChoices).pop();
				const lastChoice = dtreeChoices[reasonKey];
				const lastNode = dtreeNodes[reasonKey];
				const reason = lastNode ? lastNode.opts[lastChoice]?.reason || '' : '';
				res.className = `dtree-result ${lastId}`;
				res.style.display = 'block';
				const labels = {
					animate: 'Animate it',
					static: 'Keep it static',
					either: 'Either works'
				};
				res.innerHTML = `<div class="dtree-verdict">${labels[lastId]}</div><div class="dtree-reason">${reason}</div>`;
				container.appendChild(res);
			}
		}

		function chooseDTree(fromId, optIdx, next, reason) {
			dtreeChoices[fromId] = optIdx;
			// Trim path back to this node, then add next
			const idx = dtreePath.indexOf(fromId);
			dtreePath = dtreePath.slice(0, idx + 1);
			// Remove downstream choices
			Object.keys(dtreeChoices).forEach((k) => {
				if (+k > fromId) delete dtreeChoices[k];
			});
			dtreePath.push(next);
			renderDTree();
		}

		function resetDTree() {
			dtreePath = [0];
			dtreeChoices = {};
			renderDTree();
		}
		renderDTree();

		/* ════════════════════════════════════════
   EASING EXPLORER
════════════════════════════════════════ */
		const easings = {
			linear: {
				fn: (t) => t,
				label: 'Linear',
				desc: 'Constant velocity. Feels mechanical and unnatural for most text — nothing in the physical world moves at constant speed. Use for very fast, functional appearances where aesthetics are irrelevant.'
			},
			'ease-out': {
				fn: (t) => 1 - Math.pow(1 - t, 3),
				label: 'Ease Out',
				desc: 'Fast start, slow finish. The element arrives with confidence and settles deliberately. Best for headlines, statistics, impact statements — anything that needs to land with authority.'
			},
			'ease-in': {
				fn: (t) => Math.pow(t, 3),
				label: 'Ease In',
				desc: 'Slow start, fast finish. The element builds speed and then exits or arrives urgently. Unusual for text appearances; more natural for text departures. Use carefully.'
			},
			'ease-in-out': {
				fn: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
				label: 'Ease In-Out',
				desc: 'Slow start, fast middle, slow finish. The most natural-feeling easing for text that accompanies thoughtful narration. Labels, supporting points, explanatory text all benefit from this curve.'
			},
			bounce: {
				fn: (t) => {
					if (t < 1 / 2.75) return 7.5625 * t * t;
					if (t < 2 / 2.75) {
						t -= 1.5 / 2.75;
						return 7.5625 * t * t + 0.75;
					}
					if (t < 2.5 / 2.75) {
						t -= 2.25 / 2.75;
						return 7.5625 * t * t + 0.9375;
					}
					t -= 2.625 / 2.75;
					return 7.5625 * t * t + 0.984375;
				},
				label: 'Overshoot',
				desc: 'The element overshoots its final position before settling. Reads as playful and casual — correct for entertainment contexts, wrong for informational or serious content. Avoid for data, statistics, and professional explainers.'
			},
			spring: {
				fn: (t) => 1 - Math.exp(-8 * t) * Math.cos(12 * t),
				label: 'Spring',
				desc: 'Elastic overshoot with oscillation. The "springy" feeling communicates lightness and play. Like bounce, this easing conflicts with serious informational content. Reserve for interface elements, not for text that is communicating meaning.'
			}
		};
		let currentEasing = 'linear';
		let easingAnimId = null;

		function selectEasing(name) {
			currentEasing = name;
			document.querySelectorAll('#easing-btns .btn').forEach((b, i) => {
				const keys = ['linear', 'ease-out', 'ease-in', 'ease-in-out', 'bounce', 'spring'];
				b.classList.toggle('active', keys[i] === name);
				b.classList.toggle('amber', keys[i] === name && name === 'bounce');
			});
			drawEasingCurve();
			document.getElementById('easing-desc').textContent = easings[name].desc;
		}

		function drawEasingCurve() {
			const canvas = document.getElementById('easing-canvas');
			const dpr = window.devicePixelRatio || 1;
			canvas.width = 280 * dpr;
			canvas.height = 180 * dpr;
			const ctx = canvas.getContext('2d');
			ctx.scale(dpr, dpr);
			const W = 280,
				H = 180;
			const pad = 24;
			ctx.clearRect(0, 0, W, H);

			// Grid
			ctx.strokeStyle = '#14202e';
			ctx.lineWidth = 1;
			for (let i = 0; i <= 4; i++) {
				const x = pad + ((W - pad * 2) * i) / 4;
				const y = pad + ((H - pad * 2) * i) / 4;
				ctx.beginPath();
				ctx.moveTo(x, pad);
				ctx.lineTo(x, H - pad);
				ctx.stroke();
				ctx.beginPath();
				ctx.moveTo(pad, y);
				ctx.lineTo(W - pad, y);
				ctx.stroke();
			}
			// Axes labels
			ctx.font = '8px IBM Plex Mono';
			ctx.fillStyle = '#405068';
			ctx.textAlign = 'center';
			ctx.fillText('time →', W / 2, H - 4);
			ctx.save();
			ctx.translate(10, H / 2);
			ctx.rotate(-Math.PI / 2);
			ctx.fillText('position ↑', 0, 0);
			ctx.restore();

			// Diagonal guide
			ctx.beginPath();
			ctx.moveTo(pad, H - pad);
			ctx.lineTo(W - pad, pad);
			ctx.strokeStyle = '#1e2d40';
			ctx.lineWidth = 1;
			ctx.stroke();

			// Curve
			const fn = easings[currentEasing].fn;
			ctx.beginPath();
			for (let i = 0; i <= 100; i++) {
				const t = i / 100;
				const x = pad + t * (W - pad * 2);
				const y = H - pad - fn(t) * (H - pad * 2);
				i === 0
					? ctx.moveTo(x, Math.max(4, Math.min(H - 4, y)))
					: ctx.lineTo(x, Math.max(4, Math.min(H - 4, y)));
			}
			ctx.strokeStyle = '#3dd9a4';
			ctx.lineWidth = 2;
			ctx.stroke();

			// Dot at t=0 and t=1
			[
				[0, 0],
				[1, 1]
			].forEach(([t, v]) => {
				const x = pad + t * (W - pad * 2);
				const y = H - pad - v * (H - pad * 2);
				ctx.beginPath();
				ctx.arc(x, Math.max(4, Math.min(H - 4, y)), 4, 0, Math.PI * 2);
				ctx.fillStyle = '#3dd9a4';
				ctx.fill();
			});
		}

		function playEasing() {
			if (easingAnimId) cancelAnimationFrame(easingAnimId);
			const textEl = document.getElementById('easing-text-el');
			const container = textEl.parentElement;
			const maxX = container.offsetWidth - textEl.offsetWidth - 20;
			const fn = easings[currentEasing].fn;
			const dur = 800;
			let start = null;
			textEl.style.left = '20px';

			function step(ts) {
				if (!start) start = ts;
				const t = Math.min(1, (ts - start) / dur);
				const pos = fn(t);
				textEl.style.left = 20 + pos * Math.max(0, maxX) + 'px';
				if (t < 1) easingAnimId = requestAnimationFrame(step);
			}
			easingAnimId = requestAnimationFrame(step);
		}

		selectEasing('linear');

		/* ─── QUIZ ─── */
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

		if (typeof toggleLayer === 'function') actions.toggleLayer = toggleLayer;
		if (typeof buildHierControls === 'function') actions.buildHierControls = buildHierControls;
		if (typeof renderHierPreview === 'function') actions.renderHierPreview = renderHierPreview;
		if (typeof luminance === 'function') actions.luminance = luminance;
		if (typeof contrastRatio === 'function') actions.contrastRatio = contrastRatio;
		if (typeof bgHexFromBrightness === 'function')
			actions.bgHexFromBrightness = bgHexFromBrightness;
		if (typeof updateContrast === 'function') actions.updateContrast = updateContrast;
		if (typeof selectTreatment === 'function') actions.selectTreatment = selectTreatment;
		if (typeof setHlColor === 'function') actions.setHlColor = setHlColor;
		if (typeof updateTreatment === 'function') actions.updateTreatment = updateTreatment;
		if (typeof renderDTree === 'function') actions.renderDTree = renderDTree;
		if (typeof chooseDTree === 'function') actions.chooseDTree = chooseDTree;
		if (typeof resetDTree === 'function') actions.resetDTree = resetDTree;
		if (typeof selectEasing === 'function') actions.selectEasing = selectEasing;
		if (typeof drawEasingCurve === 'function') actions.drawEasingCurve = drawEasingCurve;
		if (typeof playEasing === 'function') actions.playEasing = playEasing;
		if (typeof step === 'function') actions.step = step;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			if (typeof easingAnimId !== 'undefined' && easingAnimId) cancelAnimationFrame(easingAnimId);
			_listeners.forEach((l) => l.target.removeEventListener(...l.args.filter(Boolean)));
		};
	});
</script>

<div class="page-wrapper">
	<!-- COURSE HEADER -->
	<header class="course-header">
		<div>
			<div class="course-label">Visual Storytelling for Faceless Video</div>
			<div class="course-title">Narrative, Pacing &amp; Visual Communication</div>
		</div>
		<div style="font-size: 11px; color: var(--vs-muted); text-align: right">Module 03 of 10</div>
	</header>

	<!-- HERO -->
	<div class="module-hero">
		<div class="module-number">03</div>
		<div class="module-tag">Module 03 · Theory + Practice</div>
		<h1 class="module-title">Structuring<br /><span>Text for Video</span></h1>
		<div class="progress-bar-wrap">
			<div
				class="progress-bar-fill"
				id="reading-progress"
				role="progressbar"
				aria-valuemin="0"
				aria-valuemax="100"
			></div>
		</div>
	</div>

	<!-- TOC -->
	<nav class="toc">
		<div class="toc-label">Contents</div>
		<ul class="toc-list">
			<li><a href="#objectives">Objectives</a></li>
			<li><a href="#text-as-visual">Text as a Visual Element</a></li>
			<li><a href="#hierarchy">Hierarchy &amp; Contrast</a></li>
			<li><a href="#treatments">The Three Treatments</a></li>
			<li><a href="#clutter">Clutter &amp; Overload</a></li>
			<li><a href="#animate-or-not">Animate or Static?</a></li>
			<li><a href="#easing">Easing &amp; Movement</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
		</ul>
	</nav>

	<!-- OBJECTIVES -->
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand text as a visual element with spatial weight, not as a written transcript</li>
			<li>Apply emphasis, contrast, and hierarchy to direct the viewer's eye</li>
			<li>Design headline, supporting point, and annotation treatments for video frames</li>
			<li>Make deliberate decisions about when to animate text and when to keep it static</li>
			<li>Use easing and motion to reinforce meaning rather than decorate</li>
		</ul>
	</section>

	<!-- ═══ SECTION 1: TEXT AS A VISUAL ELEMENT ═══ -->
	<section id="text-as-visual" class="section">
		<div class="section-header">
			<span class="section-num">03.01</span>
			<h2 class="section-title">Text as a Visual Element</h2>
		</div>

		<p>
			In writing, text is a container for language. In video, text is also a
			<em>shape on screen</em> — it occupies space, carries visual weight, competes with other elements
			for attention, and influences the perceived balance of the frame. Most creators treat on-screen
			text purely as language. The ones whose videos feel polished treat it as design.
		</p>

		<p>
			The distinction matters because it changes every decision. A transcript mindset produces
			screens filled with text that mirrors what the narrator is saying, in whatever font size fits
			the space. A design mindset asks:
			<strong>what job does this text do in the frame?</strong> Does it introduce a key term? Anchor a
			statistic? Point to a detail in the diagram? Each job requires a different visual treatment — and
			using the wrong one for the job creates friction even when the viewer cannot explain why.
		</p>

		<div class="callout blue">
			<div class="callout-label">The Transcript Trap</div>
			Putting full sentences on screen while narrating them is not reinforcement — it is redundancy. Both
			channels are saying the exact same thing, which means one channel is wasted. On-screen text should
			either compress the narration into a key phrase, add a layer the narration does not speak, or point
			to something in the visual that needs labelling.
		</div>

		<p>
			Think of on-screen text as operating in three registers simultaneously. It is
			<em>linguistic</em> — it carries meaning through the words it contains. It is
			<em>typographic</em> — it carries meaning through size, weight, spacing, and font choice. And
			it is <em>spatial</em> — it carries meaning through where it sits in the frame and how it relates
			to the other elements around it. All three registers are active at once, whether or not you designed
			them intentionally.
		</p>

		<!-- DEMO: Frame Anatomy -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Frame Text Anatomy</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Toggle each text layer to see how different elements occupy the frame and what job each is
					doing. Notice how each layer has a distinct visual weight and position.
				</p>
				<div class="btn-row">
					<button
						class="btn active"
						id="tl-hl"
						onclick={(e) => {
							actions.toggleLayer('headline');
						}}
					>
						Headline
					</button>
					<button
						class="btn"
						id="tl-sp"
						onclick={(e) => {
							actions.toggleLayer('support');
						}}
					>
						Supporting Point
					</button>
					<button
						class="btn"
						id="tl-an"
						onclick={(e) => {
							actions.toggleLayer('annotation');
						}}>Annotation</button
					>
					<button
						class="btn blue"
						id="tl-lt"
						onclick={(e) => {
							actions.toggleLayer('lower');
						}}
					>
						Lower Third
					</button>
					<button
						class="btn red"
						id="tl-cl"
						onclick={(e) => {
							actions.toggleLayer('clutter');
						}}>+ Clutter</button
					>
				</div>

				<div class="frame-preview" id="frame-preview">
					<!-- Background suggestion -->
					<div class="frame-bg">
						<div class="frame-bg-label">VIDEO FRAME</div>
						<!-- Faint grid to suggest image content -->
						<svg
							width="100%"
							height="100%"
							style="position: absolute; inset: 0; opacity: 0.06"
							xmlns="http://www.w3.org/2000/svg"
						>
							<defs>
								<pattern id="fg" width="40" height="40" patternUnits="userSpaceOnUse">
									<path d="M40 0L0 0 0 40" fill="none" stroke="#4aafff" stroke-width="0.5" />
								</pattern>
							</defs>
							<rect width="100%" height="100%" fill="url(#fg)" />
							<!-- Horizon line suggestion -->
							<line
								x1="0"
								y1="55%"
								x2="100%"
								y2="55%"
								stroke="#4aafff"
								stroke-width="0.8"
								opacity="0.4"
							/>
							<!-- Rule of thirds -->
							<line
								x1="33.3%"
								y1="0"
								x2="33.3%"
								y2="100%"
								stroke="#ffffff"
								stroke-width="0.4"
								opacity="0.2"
							/>
							<line
								x1="66.6%"
								y1="0"
								x2="66.6%"
								y2="100%"
								stroke="#ffffff"
								stroke-width="0.4"
								opacity="0.2"
							/>
							<line
								x1="0"
								y1="33.3%"
								x2="100%"
								y2="33.3%"
								stroke="#ffffff"
								stroke-width="0.4"
								opacity="0.2"
							/>
							<line
								x1="0"
								y1="66.6%"
								x2="100%"
								y2="66.6%"
								stroke="#ffffff"
								stroke-width="0.4"
								opacity="0.2"
							/>
						</svg>
					</div>

					<div class="frame-safezone"></div>

					<!-- Headline layer -->
					<div class="txt-layer txt-headline hidden" id="layer-headline">
						<div
							style="
										font-size: clamp(14px, 3.2vw, 28px);
										color: #ffffff;
										font-family: 'Syne', sans-serif;
										font-weight: 800;
										line-height: 1.1;
										text-shadow: 0 2px 12px rgba(0, 0, 0, 0.8);
									"
						>
							The Signal<br />Gets Through
						</div>
						<div
							style="width: 32px; height: 2px; background: var(--vs-mint); margin-top: 6px"
						></div>
					</div>

					<!-- Supporting point layer -->
					<div class="txt-layer txt-support hidden" id="layer-support">
						<div
							style="
										background: rgba(0, 0, 0, 0.7);
										padding: 0.3rem 0.6rem;
										border-left: 2px solid var(--vs-amber);
										display: inline-block;
									"
						>
							<div
								style="
											font-size: clamp(9px, 1.4vw, 12px);
											color: var(--vs-amber);
											letter-spacing: 0.12em;
											text-transform: uppercase;
											line-height: 1.4;
										"
							>
								Noise-to-signal ratio
							</div>
							<div
								style="
											font-size: clamp(10px, 1.6vw, 13px);
											color: #ffffffcc;
											margin-top: 2px;
											line-height: 1.5;
										"
							>
								Every visual competes for attention
							</div>
						</div>
					</div>

					<!-- Annotation layer -->
					<div class="txt-layer txt-annotation hidden" id="layer-annotation">
						<div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px">
							<div
								style="
											font-size: clamp(8px, 1.1vw, 11px);
											color: var(--vs-blue);
											letter-spacing: 0.15em;
											text-transform: uppercase;
										"
							>
								ref. point
							</div>
							<div
								style="
											font-size: clamp(8px, 1.1vw, 10px);
											color: rgba(255, 255, 255, 0.5);
											line-height: 1.5;
											text-align: right;
										"
							>
								Upper-right quad<br />low visual mass
							</div>
							<div
								style="
											width: 24px;
											height: 1px;
											background: var(--vs-blue);
											opacity: 0.5;
											align-self: flex-end;
										"
							></div>
						</div>
					</div>

					<!-- Lower third layer -->
					<div
						class="txt-layer txt-lower-third hidden"
						id="layer-lower"
						style="background: rgba(0, 0, 0, 0.82)"
					>
						<div class="txt-lower-third-bar" style="background: var(--vs-mint)"></div>
						<div>
							<div
								style="
											font-size: clamp(9px, 1.4vw, 12px);
											color: var(--vs-mint);
											letter-spacing: 0.15em;
											text-transform: uppercase;
											line-height: 1.3;
										"
							>
								Key concept
							</div>
							<div
								style="
											font-size: clamp(11px, 1.8vw, 15px);
											color: #ffffff;
											font-family: 'Syne', sans-serif;
											font-weight: 700;
											line-height: 1.2;
										"
							>
								Visual hierarchy in frames
							</div>
						</div>
					</div>

					<!-- Clutter layer -->
					<div class="txt-clutter hidden" id="layer-clutter" style="inset: 0; position: absolute">
						<div
							style="
										position: absolute;
										top: 8%;
										left: 30%;
										font-size: clamp(8px, 1.1vw, 10px);
										color: #ff4f6888;
									"
						>
							SUB-HEADING THAT GOES ON TOO LONG
						</div>
						<div
							style="
										position: absolute;
										top: 22%;
										right: 8%;
										font-size: clamp(9px, 1.2vw, 11px);
										color: #f5b94a66;
									"
						>
							• bullet one
						</div>
						<div
							style="
										position: absolute;
										top: 30%;
										right: 8%;
										font-size: clamp(9px, 1.2vw, 11px);
										color: #f5b94a66;
									"
						>
							• bullet two here
						</div>
						<div
							style="
										position: absolute;
										top: 38%;
										right: 8%;
										font-size: clamp(9px, 1.2vw, 11px);
										color: #f5b94a66;
									"
						>
							• another point
						</div>
						<div
							style="
										position: absolute;
										top: 46%;
										right: 8%;
										font-size: clamp(9px, 1.2vw, 11px);
										color: #f5b94a66;
									"
						>
							• more text
						</div>
						<div
							style="
										position: absolute;
										top: 15%;
										left: 35%;
										font-size: clamp(8px, 1vw, 9px);
										color: #ffffff33;
									"
						>
							lorem ipsum label copy
						</div>
						<div
							style="
										position: absolute;
										bottom: 28%;
										left: 22%;
										font-size: clamp(8px, 1.1vw, 10px);
										color: #3dd9a455;
									"
						>
							stat: 47%
						</div>
						<div
							style="
										position: absolute;
										top: 62%;
										left: 50%;
										font-size: clamp(8px, 1vw, 9px);
										color: #ffffff22;
									"
						>
							secondary note here
						</div>
					</div>
				</div>

				<div
					id="layer-desc"
					style="
								margin-top: 1rem;
								font-size: 12px;
								color: var(--vs-text);
								min-height: 2.8em;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								line-height: 1.7;
								background: var(--vs-raised);
							"
				>
					Toggle layers above to explore how text elements occupy and compete within a video frame.
				</div>
			</div>
		</div>
	</section>

	<!-- ═══ SECTION 2: HIERARCHY & CONTRAST ═══ -->
	<section id="hierarchy" class="section">
		<div class="section-header">
			<span class="section-num">03.02</span>
			<h2 class="section-title">Emphasis, Contrast &amp; Hierarchy</h2>
		</div>

		<p>
			Visual hierarchy is the order in which a viewer's eye processes elements on screen. In text,
			hierarchy is established through contrast — differences in size, weight, color, and spacing
			that signal importance. The element with the highest contrast relative to its surroundings is
			processed first. If everything has the same contrast, nothing has priority.
		</p>

		<p>
			In video, you are competing with the moving image behind the text. This means text hierarchy
			has to work harder than it does in static design. Subtle differences in size or weight
			disappear against a busy background. The tools available to you are:
			<strong>size</strong> (the most powerful), <strong>color contrast</strong> against the
			background, <strong>weight</strong> (bold vs regular), <strong>spacing</strong> (isolated text
			reads before crowded text), and <strong>position</strong> (upper-left reads before lower-right in
			left-to-right cultures).
		</p>

		<!-- DEMO: Hierarchy Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Text Hierarchy Ruler</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Adjust the properties of each hierarchy level to see how the visual weight and reading
					order change. A well-built hierarchy creates an unambiguous reading path.
				</p>

				<div class="two-col" style="gap: 2rem; align-items: start">
					<div>
						<!-- Level controls -->
						<div id="hier-controls"></div>
					</div>
					<div>
						<!-- Live preview -->
						<div
							style="
										background: #040710;
										border: 1px solid var(--vs-border);
										padding: 1.5rem;
										min-height: 200px;
										display: flex;
										flex-direction: column;
										justify-content: center;
										gap: 0.6rem;
									"
							id="hier-preview"
						></div>
						<div style="margin-top: 1rem" id="hier-assessment"></div>
					</div>
				</div>
			</div>
		</div>

		<p>
			The most common hierarchy failure is <em>competing primaries</em>: two elements that both
			appear to be the most important thing on screen. This happens when a large headline and a
			large statistic appear simultaneously at similar sizes, or when too many text elements use the
			same high-contrast accent color. The viewer's eye stalls, trying to decide which to read
			first, and both lose impact.
		</p>

		<table>
			<thead>
				<tr>
					<th>Hierarchy Level</th>
					<th>Visual Properties</th>
					<th>Typical Use</th>
					<th>Max per Frame</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Primary</td>
					<td>Largest, highest contrast, isolated</td>
					<td>Main headline, key term, central claim</td>
					<td>1</td>
				</tr>
				<tr>
					<td>Secondary</td>
					<td>Medium size, medium contrast, grouped</td>
					<td>Supporting stat, subtitle, category label</td>
					<td>1–2</td>
				</tr>
				<tr>
					<td>Tertiary</td>
					<td>Small, low contrast, recedes</td>
					<td>Annotations, source credits, labels</td>
					<td>2–4</td>
				</tr>
				<tr>
					<td>Ambient</td>
					<td>Near-invisible, texture only</td>
					<td>Watermarks, background text motifs</td>
					<td>unlimited</td>
				</tr>
			</tbody>
		</table>

		<!-- Contrast checker -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Text Contrast on Video</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Background luminosity in video footage varies constantly. Test how your text color
					performs across different background brightness levels.
				</p>
				<div class="slider-row" style="margin-bottom: 1rem">
					<label for="bg-bright">Background brightness</label>
					<input
						type="range"
						id="bg-bright"
						min="0"
						max="100"
						value="20"
						oninput={() => {
							actions.updateContrast();
						}}
					/>
					<span class="slider-val" id="bg-bright-val">20%</span>
				</div>
				<div
					style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem"
					id="contrast-swatches"
				></div>
				<div
					id="contrast-verdict"
					style="
								font-size: 12px;
								color: var(--vs-text);
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								background: var(--vs-raised);
								line-height: 1.7;
							"
				></div>
			</div>
		</div>
	</section>

	<!-- ═══ SECTION 3: THE THREE TREATMENTS ═══ -->
	<section id="treatments" class="section">
		<div class="section-header">
			<span class="section-num">03.03</span>
			<h2 class="section-title">The Three Core Text Treatments</h2>
		</div>

		<p>
			Every piece of on-screen text in a well-designed video fits into one of three functional
			categories. Each category has distinct visual requirements that follow from its communicative
			job. Designing these three treatments deliberately — and using them consistently — is what
			separates videos that feel produced from videos that feel assembled.
		</p>

		<!-- DEMO: Treatment Studio -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Text Treatment Studio</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<div class="treatment-tabs" id="treatment-tabs">
					<div
						class="treatment-tab active"
						onclick={(e) => {
							actions.selectTreatment('headline');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.selectTreatment('headline');
							}
						}}
					>
						Headline
					</div>
					<div
						class="treatment-tab"
						onclick={(e) => {
							actions.selectTreatment('support');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.selectTreatment('support');
							}
						}}
					>
						Supporting Point
					</div>
					<div
						class="treatment-tab"
						onclick={(e) => {
							actions.selectTreatment('annotation');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.selectTreatment('annotation');
							}
						}}
					>
						Annotation
					</div>
				</div>

				<!-- Headline panel -->
				<div
					class="treatment-panel active"
					id="tp-headline"
					style="border: 1px solid var(--vs-border); border-top: none; padding: 1.5rem"
				>
					<div class="two-col" style="align-items: start; gap: 2rem">
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.15em;
											text-transform: uppercase;
											color: var(--vs-mint);
											margin-bottom: 1rem;
											font-weight: 600;
										"
							>
								Headline Treatment
							</div>
							<p style="font-size: 12px">
								The <strong>headline</strong> carries the primary claim of a section. It is the first
								thing the eye goes to. It should be able to stand alone — if a viewer reads nothing else,
								the headline delivers the essential message.
							</p>
							<div style="margin-top: 1.25rem">
								<div class="slider-row">
									<label for="dummy">Font size (vw)</label><input
										type="range"
										id="hl-size"
										min="2"
										max="6"
										step="0.1"
										value="3.8"
										oninput={() => {
											actions.updateTreatment('headline');
										}}
									/><span class="slider-val" id="hl-size-v">3.8</span>
								</div>
								<div class="slider-row">
									<label for="dummy">Letter spacing</label><input
										type="range"
										id="hl-ls"
										min="-2"
										max="20"
										step="1"
										value="0"
										oninput={() => {
											actions.updateTreatment('headline');
										}}
									/><span class="slider-val" id="hl-ls-v">0</span>
								</div>
								<div class="slider-row">
									<label for="dummy">Line height</label><input
										type="range"
										id="hl-lh"
										min="0.8"
										max="2.0"
										step="0.05"
										value="1.05"
										oninput={() => {
											actions.updateTreatment('headline');
										}}
									/><span class="slider-val" id="hl-lh-v">1.05</span>
								</div>
								<div class="slider-row" style="margin-top: 0.75rem">
									<label>Color</label>
									<div style="display: flex; gap: 0.5rem">
										<div
											class="btn active"
											id="hlc-white"
											onclick={(e) => {
												actions.setHlColor('#ffffff');
											}}
											role="button"
											tabindex="0"
											onkeydown={(e) => {
												if (e.key === 'Enter' || e.key === ' ') {
													e.preventDefault();
													actions.setHlColor('#ffffff');
												}
											}}
											style="padding: 4px 10px; font-size: 11px"
										>
											White
										</div>
										<div
											class="btn"
											id="hlc-mint"
											onclick={(e) => {
												actions.setHlColor('#3dd9a4');
											}}
											role="button"
											tabindex="0"
											onkeydown={(e) => {
												if (e.key === 'Enter' || e.key === ' ') {
													e.preventDefault();
													actions.setHlColor('#3dd9a4');
												}
											}}
											style="padding: 4px 10px; font-size: 11px"
										>
											Mint
										</div>
										<div
											class="btn amber"
											id="hlc-amber"
											onclick={(e) => {
												actions.setHlColor('#f5b94a');
											}}
											role="button"
											tabindex="0"
											onkeydown={(e) => {
												if (e.key === 'Enter' || e.key === ' ') {
													e.preventDefault();
													actions.setHlColor('#f5b94a');
												}
											}}
											style="padding: 4px 10px; font-size: 11px"
										>
											Amber
										</div>
									</div>
								</div>
							</div>
							<div
								style="
											margin-top: 1rem;
											font-size: 11px;
											color: var(--vs-muted);
											line-height: 1.7;
										"
							>
								<div
									style="
												color: #fff;
												font-size: 10px;
												letter-spacing: 0.1em;
												text-transform: uppercase;
												margin-bottom: 0.4rem;
											"
								>
									Design rules
								</div>
								<div>· One headline per section — never two competing primaries</div>
								<div>· Use display-weight font (700–800) for authority</div>
								<div>· Leave generous space above and below — isolation = importance</div>
								<div>· Avoid all-caps for long headlines; use it only for short labels</div>
							</div>
						</div>
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.12em;
											text-transform: uppercase;
											color: var(--vs-muted);
											margin-bottom: 0.5rem;
										"
							>
								Live preview
							</div>
							<div
								style="
											background: #000;
											border: 1px solid var(--vs-border2);
											padding: 2rem 1.5rem;
											min-height: 140px;
											display: flex;
											flex-direction: column;
											justify-content: center;
										"
							>
								<div
									id="hl-preview"
									style="
												font-family: 'Syne', sans-serif;
												font-weight: 800;
												color: #ffffff;
												line-height: 1.05;
												font-size: 3.8vw;
												word-break: break-word;
											"
								>
									The Signal<br />Reaches You
								</div>
								<div
									id="hl-bar"
									style="width: 32px; height: 2px; background: var(--vs-mint); margin-top: 10px"
								></div>
							</div>
							<div
								id="hl-verdict"
								style="
											margin-top: 0.75rem;
											font-size: 11px;
											color: var(--vs-muted);
											line-height: 1.6;
										"
							></div>
						</div>
					</div>
				</div>

				<!-- Supporting Point panel -->
				<div
					class="treatment-panel"
					id="tp-support"
					style="border: 1px solid var(--vs-border); border-top: none; padding: 1.5rem"
				>
					<div class="two-col" style="align-items: start; gap: 2rem">
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.15em;
											text-transform: uppercase;
											color: var(--vs-amber);
											margin-bottom: 1rem;
											font-weight: 600;
										"
							>
								Supporting Point Treatment
							</div>
							<p style="font-size: 12px">
								The <strong>supporting point</strong> provides evidence, context, or elaboration for the
								headline claim. It appears at a lower hierarchy level — it should visually recede behind
								the headline while still remaining clearly legible.
							</p>
							<div style="margin-top: 1.25rem">
								<div class="slider-row">
									<label for="dummy">Font size (vw)</label><input
										type="range"
										id="sp-size"
										min="0.8"
										max="2.2"
										step="0.1"
										value="1.3"
										oninput={() => {
											actions.updateTreatment('support');
										}}
									/><span class="slider-val" id="sp-size-v">1.3</span>
								</div>
								<div class="slider-row">
									<label for="dummy">Opacity</label><input
										type="range"
										id="sp-opacity"
										min="40"
										max="100"
										value="80"
										oninput={() => {
											actions.updateTreatment('support');
										}}
									/><span class="slider-val" id="sp-opacity-v">80%</span>
								</div>
								<div class="slider-row">
									<label for="dummy">Left bar width</label><input
										type="range"
										id="sp-bar"
										min="0"
										max="6"
										step="1"
										value="2"
										oninput={() => {
											actions.updateTreatment('support');
										}}
									/><span class="slider-val" id="sp-bar-v">2px</span>
								</div>
							</div>
							<div
								style="
											margin-top: 1rem;
											font-size: 11px;
											color: var(--vs-muted);
											line-height: 1.7;
										"
							>
								<div
									style="
												color: #fff;
												font-size: 10px;
												letter-spacing: 0.1em;
												text-transform: uppercase;
												margin-bottom: 0.4rem;
											"
								>
									Design rules
								</div>
								<div>· Should never be larger than 60% of headline size</div>
								<div>· A left-border accent helps group it visually</div>
								<div>· Semi-transparent background improves legibility over footage</div>
								<div>· Limit to 1–2 lines; longer becomes a paragraph, not a point</div>
							</div>
						</div>
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.12em;
											text-transform: uppercase;
											color: var(--vs-muted);
											margin-bottom: 0.5rem;
										"
							>
								Live preview
							</div>
							<div
								style="
											background: #000;
											border: 1px solid var(--vs-border2);
											padding: 2rem 1.5rem;
											min-height: 140px;
											display: flex;
											flex-direction: column;
											justify-content: flex-end;
										"
							>
								<div
									id="sp-preview"
									style="
												background: rgba(0, 0, 0, 0.7);
												padding: 0.4rem 0.75rem;
												border-left: 2px solid var(--vs-amber);
												display: inline-block;
											"
								>
									<div
										style="
													font-size: 10px;
													color: var(--vs-amber);
													letter-spacing: 0.12em;
													text-transform: uppercase;
													line-height: 1.3;
													margin-bottom: 2px;
												"
									>
										Key finding
									</div>
									<div
										id="sp-main"
										style="
													font-family: 'IBM Plex Mono', monospace;
													color: rgba(255, 255, 255, 0.8);
													font-size: 1.3vw;
													line-height: 1.5;
												"
									>
										Every frame competes for attention
									</div>
								</div>
							</div>
							<div
								id="sp-verdict"
								style="
											margin-top: 0.75rem;
											font-size: 11px;
											color: var(--vs-muted);
											line-height: 1.6;
										"
							></div>
						</div>
					</div>
				</div>

				<!-- Annotation panel -->
				<div
					class="treatment-panel"
					id="tp-annotation"
					style="border: 1px solid var(--vs-border); border-top: none; padding: 1.5rem"
				>
					<div class="two-col" style="align-items: start; gap: 2rem">
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.15em;
											text-transform: uppercase;
											color: var(--vs-blue);
											margin-bottom: 1rem;
											font-weight: 600;
										"
							>
								Annotation Treatment
							</div>
							<p style="font-size: 12px">
								The <strong>annotation</strong> labels, identifies, or references a specific element in
								the visual. It should feel like it belongs to the diagram or image — positioned close
								to what it labels, visually lighter than everything else.
							</p>
							<div style="margin-top: 1.25rem">
								<div class="slider-row">
									<label for="dummy">Font size (vw)</label><input
										type="range"
										id="an-size"
										min="0.6"
										max="1.4"
										step="0.1"
										value="0.9"
										oninput={() => {
											actions.updateTreatment('annotation');
										}}
									/><span class="slider-val" id="an-size-v">0.9</span>
								</div>
								<div class="slider-row">
									<label for="dummy">Opacity</label><input
										type="range"
										id="an-opacity"
										min="30"
										max="80"
										value="55"
										oninput={() => {
											actions.updateTreatment('annotation');
										}}
									/><span class="slider-val" id="an-opacity-v">55%</span>
								</div>
								<div class="slider-row">
									<label for="dummy">Line length (px)</label><input
										type="range"
										id="an-line"
										min="0"
										max="40"
										step="4"
										value="20"
										oninput={() => {
											actions.updateTreatment('annotation');
										}}
									/><span class="slider-val" id="an-line-v">20px</span>
								</div>
							</div>
							<div
								style="
											margin-top: 1rem;
											font-size: 11px;
											color: var(--vs-muted);
											line-height: 1.7;
										"
							>
								<div
									style="
												color: #fff;
												font-size: 10px;
												letter-spacing: 0.1em;
												text-transform: uppercase;
												margin-bottom: 0.4rem;
											"
								>
									Design rules
								</div>
								<div>· Smallest text on screen — legible at reading distance, not dominant</div>
								<div>· Leader lines should be thin (0.5–1px), not thick arrows</div>
								<div>· Letter-spacing helps small text read at lower contrast</div>
								<div>· Group related annotations — scatter creates noise</div>
							</div>
						</div>
						<div>
							<div
								style="
											font-size: 10px;
											letter-spacing: 0.12em;
											text-transform: uppercase;
											color: var(--vs-muted);
											margin-bottom: 0.5rem;
										"
							>
								Live preview
							</div>
							<div
								style="
											background: #000;
											border: 1px solid var(--vs-border2);
											padding: 2rem 1.5rem;
											min-height: 140px;
											display: flex;
											align-items: center;
											justify-content: center;
											position: relative;
										"
							>
								<!-- Diagram placeholder -->
								<svg width="80" height="80" viewBox="0 0 80 80" style="opacity: 0.4">
									<circle cx="40" cy="40" r="30" fill="none" stroke="#4aafff" stroke-width="1.5" />
									<circle cx="40" cy="40" r="5" fill="#4aafff" />
									<line x1="40" y1="10" x2="40" y2="30" stroke="#4aafff" stroke-width="1" />
									<line x1="40" y1="50" x2="40" y2="70" stroke="#4aafff" stroke-width="1" />
									<line x1="10" y1="40" x2="30" y2="40" stroke="#4aafff" stroke-width="1" />
									<line x1="50" y1="40" x2="70" y2="40" stroke="#4aafff" stroke-width="1" />
								</svg>
								<div
									id="an-preview"
									style="position: absolute; top: 16px; right: 16px; text-align: right"
								>
									<div
										id="an-line-el"
										style="
													width: 20px;
													height: 1px;
													background: rgba(74, 175, 255, 0.55);
													margin-left: auto;
													margin-bottom: 4px;
												"
									></div>
									<div
										id="an-main"
										style="
													font-size: 0.9vw;
													color: rgba(74, 175, 255, 0.55);
													letter-spacing: 0.1em;
													text-transform: uppercase;
													line-height: 1.5;
												"
									>
										focal<br />node
									</div>
								</div>
							</div>
							<div
								id="an-verdict"
								style="
											margin-top: 0.75rem;
											font-size: 11px;
											color: var(--vs-muted);
											line-height: 1.6;
										"
							></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══ SECTION 4: CLUTTER & OVERLOAD ═══ -->
	<section id="clutter" class="section">
		<div class="section-header">
			<span class="section-num">03.04</span>
			<h2 class="section-title">Clutter, Overload &amp; the Empty Frame</h2>
		</div>

		<p>
			Text clutter is the most pervasive quality failure in self-produced video. It emerges not from
			adding bad text, but from adding too much text that individually seems justified. Each element
			has a reason to be there. Collectively, they destroy legibility, hierarchy, and pace.
		</p>

		<p>
			Clutter signals anxiety to the viewer — a creator who does not trust the narration to carry
			the meaning, so they reinforce it with bullets, sub-points, labels, and counter-labels. The
			irony is that the addition reduces comprehension rather than supporting it. The viewer's eye
			does not know where to look, so it looks nowhere in particular.
		</p>

		<div class="callout red">
			<div class="callout-label">The Removal Test</div>
			For every piece of text on screen, ask: if I removed this, would the viewer miss something they
			could not get from the narration or visual alone? If the answer is no, remove it. If you remove
			it and the frame feels "empty," that emptiness is the correct state — it is giving the viewer space
			to process.
		</div>

		<p>
			The <em>empty frame</em> is not a failure. It is the most powerful tool in text design. A single
			headline on a clean dark background has more visual authority than the same headline surrounded
			by supporting bullets. The space around text is what gives it weight. Remove the competition and
			the text becomes the scene.
		</p>

		<table>
			<thead>
				<tr>
					<th>Warning Sign</th>
					<th>What It Usually Means</th>
					<th>Fix</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Full-sentence narration on screen</td>
					<td>Transcript mindset</td>
					<td>Reduce to key phrase or single term</td>
				</tr>
				<tr>
					<td>3+ bullet points visible simultaneously</td>
					<td>List mindset, not sequence mindset</td>
					<td>Reveal one bullet at a time with pacing</td>
				</tr>
				<tr>
					<td>Two elements in the same accent color</td>
					<td>No true primary</td>
					<td>Reserve accent for one element per frame</td>
				</tr>
				<tr>
					<td>Text in all four quadrants</td>
					<td>No spatial priority</td>
					<td>Anchor text to two zones maximum</td>
				</tr>
				<tr>
					<td>Label for every diagram element</td>
					<td>Over-explanation</td>
					<td>Label only what the narration cannot name</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══ SECTION 5: ANIMATE OR STATIC? ═══ -->
	<section id="animate-or-not" class="section">
		<div class="section-header">
			<span class="section-num">03.05</span>
			<h2 class="section-title">When to Animate Text — and When Not To</h2>
		</div>

		<p>
			Animation adds cognitive cost. Every moving element on screen draws attention — motion is
			processed by a different, faster visual pathway than static content, and it is processed
			<em>first</em>. This means animated text will be seen before everything else in the frame,
			which is powerful when it is the most important element, and catastrophically distracting when
			it is not.
		</p>

		<p>
			The decision to animate text should be driven by one question:
			<strong
				>does the motion reinforce what this text is communicating, or does it merely decorate its
				arrival?</strong
			>
			A word that fades in while being spoken reinforces the rhythm of narration. A word that flies in
			from the left, bounces, and then settles does nothing except announce that animation software was
			used.
		</p>

		<!-- DEMO: Animation Decision Tree -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Animate vs Static Decision Tool</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Answer each question about your text element to get a recommendation. Reset to start over.
				</p>
				<div id="dtree-container"></div>
				<button
					class="btn"
					onclick={(e) => {
						actions.resetDTree();
					}}
					style="margin-top: 1rem">Reset</button
				>
			</div>
		</div>

		<p>
			Static text is underused by beginners who equate animation with professionalism. The reverse
			is closer to the truth: restraint in animation signals a creator who understands that
			attention is finite, and uses motion only when it earns its cost. A well-timed static reveal —
			text appearing exactly on the beat of a word in narration — is more powerful than an animated
			one if the timing is precise and the text is the right size.
		</p>
	</section>

	<!-- ═══ SECTION 6: EASING & MOVEMENT ═══ -->
	<section id="easing" class="section">
		<div class="section-header">
			<span class="section-num">03.06</span>
			<h2 class="section-title">Easing &amp; the Character of Movement</h2>
		</div>

		<p>
			When you do animate text, the easing curve — the acceleration profile of the movement — is
			doing as much communicative work as the text itself. A linear ease feels mechanical and
			unnatural. An ease-in feels heavy, like something arriving with weight. An ease-out feels
			light, like something that has already done its work and is settling. Ease-in-out feels
			organic, like a natural breath.
		</p>

		<p>
			The correct easing for any text element follows from what that element is communicating. A
			statistic that lands with authority wants a snappy ease-out: it arrives fast and settles hard.
			A calm, reflective statement wants a soft ease-in-out: it arrives quietly and takes its time.
			A fast-cut list item wants a linear or near-linear move: it should feel efficient, not
			decorated.
		</p>

		<!-- DEMO: Easing Visualiser -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Easing Curve Explorer</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Select an easing curve and click Play to see both the mathematical curve and the felt
					experience of that motion applied to a text element.
				</p>
				<div class="btn-row" id="easing-btns">
					<button
						class="btn active"
						onclick={(e) => {
							actions.selectEasing('linear');
						}}>Linear</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.selectEasing('ease-out');
						}}>Ease Out</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.selectEasing('ease-in');
						}}>Ease In</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.selectEasing('ease-in-out');
						}}>Ease In-Out</button
					>
					<button
						class="btn amber"
						onclick={(e) => {
							actions.selectEasing('bounce');
						}}>Overshoot</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.selectEasing('spring');
						}}>Spring</button
					>
				</div>
				<div class="two-col" style="align-items: start; gap: 1.5rem">
					<div>
						<div
							style="
										font-size: 10px;
										letter-spacing: 0.12em;
										text-transform: uppercase;
										color: var(--vs-muted);
										margin-bottom: 6px;
									"
						>
							Curve
						</div>
						<canvas
							id="easing-canvas"
							width="280"
							height="180"
							aria-label="Easing Canvas Demonstration"
							role="region"
							tabindex="0"
						></canvas>
					</div>
					<div>
						<div
							style="
										font-size: 10px;
										letter-spacing: 0.12em;
										text-transform: uppercase;
										color: var(--vs-muted);
										margin-bottom: 6px;
									"
						>
							Text preview
						</div>
						<div class="easing-demo-text">
							<div class="easing-text-el" id="easing-text-el">SIGNAL</div>
						</div>
						<div style="margin-top: 1rem">
							<div class="btn-row" style="margin-bottom: 0">
								<button
									class="btn mint"
									onclick={(e) => {
										actions.playEasing();
									}}
									id="ease-play-btn"
								>
									▶ Play
								</button>
							</div>
						</div>
						<div
							id="easing-desc"
							style="
										margin-top: 1rem;
										font-size: 12px;
										color: var(--vs-text);
										line-height: 1.7;
										min-height: 3em;
										padding: 0.75rem;
										border-left: 2px solid var(--vs-border2);
										background: var(--vs-raised);
									"
						></div>
					</div>
				</div>
				<div
					style="
								margin-top: 1.5rem;
								display: grid;
								grid-template-columns: 1fr 1fr 1fr;
								gap: 1rem;
								font-size: 11px;
							"
				>
					<div
						style="
									border: 1px solid var(--vs-border);
									padding: 0.75rem;
									background: var(--vs-raised);
								"
					>
						<div
							style="
										color: var(--vs-mint);
										font-size: 9px;
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Use Ease-Out for
						</div>
						<div style="color: var(--vs-text); line-height: 1.7">
							Statistics, headlines, impact statements. Arrives with authority, settles decisively.
						</div>
					</div>
					<div
						style="
									border: 1px solid var(--vs-border);
									padding: 0.75rem;
									background: var(--vs-raised);
								"
					>
						<div
							style="
										color: var(--vs-amber);
										font-size: 9px;
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Use Ease-In-Out for
						</div>
						<div style="color: var(--vs-text); line-height: 1.7">
							Explanatory text, labels, supporting points. Feels considered, not urgent.
						</div>
					</div>
					<div
						style="
									border: 1px solid var(--vs-border);
									padding: 0.75rem;
									background: var(--vs-raised);
								"
					>
						<div
							style="
										color: var(--vs-red);
										font-size: 9px;
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Avoid Overshoot for
						</div>
						<div style="color: var(--vs-text); line-height: 1.7">
							Serious content, data-heavy contexts. Bounce/spring reads as casual or playful.
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══ SECTION 7: PRACTICAL WORK ═══ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">03.07</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout amber">
			<div class="callout-label">Exercise A · Three-Treatment Design</div>
			Choose a topic you know well. Design the three text treatments for a single section of a video on
			that topic: a headline (max 6 words), a supporting point (max 15 words, with category label), and
			an annotation (max 3 words + leader line). Sketch these as a layout — you do not need software,
			a rough diagram is fine. The constraint forces the decisions.
		</div>

		<div class="callout blue">
			<div class="callout-label">Exercise B · Animate vs Static Audit</div>
			Find a video that uses text animation throughout. For each animated text element, apply the decision
			tree from this module: does the motion reinforce the meaning of the text, or does it merely decorate
			its arrival? Count both. Creators who score more decorative than reinforcing animations are using
			motion as a substitute for good text design.
		</div>

		<div class="callout">
			<div class="callout-label">Exercise C · Removal Pass</div>
			Take a draft of your own on-screen text — or find a heavily-texted reference video — and apply the
			removal test to every element. Keep only what the viewer would miss. Note what percentage of the
			original text survived. Most first-pass designs lose 40–60% of their text without losing any meaning.
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
						<span class="stat-label">Transcript trap</span><span class="stat-val"
							>narration on screen</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Visual hierarchy</span><span class="stat-val"
							>reading order by contrast</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Primary / Secondary / Tertiary</span><span class="stat-val"
							>3-level system</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Clutter</span><span class="stat-val">justified excess</span>
					</div>
				</div>
				<div class="stats-panel">
					<div class="stat-row">
						<span class="stat-label">Headline treatment</span><span class="stat-val"
							>primary claim, 1 per frame</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Removal test</span><span class="stat-val"
							>if not missed, cut it</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Easing curve</span><span class="stat-val"
							>acceleration = character</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Empty frame</span><span class="stat-val">space = weight</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 03 — Check Your Understanding</div>
		<div class="quiz-sub">4 questions · No time limit</div>

		<div class="question" id="q1">
			<div class="q-text">
				<span class="q-num">01.</span>A creator displays the full text of each narrated sentence on
				screen as it is spoken, word for word. What is the primary problem with this approach?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, false);
					}}
				>
					The text moves too quickly for most viewers to read in sync
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, true);
					}}
				>
					Both channels — narration and on-screen text — are carrying exactly the same message,
					making one entirely redundant and wasting a channel that could add a distinct layer
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, false);
					}}
				>
					Full sentences create clutter that obscures the background visual
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, false);
					}}
				>
					Viewers prefer bullet points to full sentences on screen
				</button>
			</div>
			<div class="feedback" id="fb-q1"></div>
		</div>

		<div class="question" id="q2">
			<div class="q-text">
				<span class="q-num">02.</span>Two elements on screen are the same large size and both use
				the same accent color. What visual hierarchy problem does this create?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, false);
					}}
				>
					Redundancy — the viewer sees the same information twice
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, true);
					}}
				>
					Competing primaries — the viewer's eye stalls because both elements signal equal
					importance, so neither receives full attention
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, false);
					}}
				>
					Overcrowding — the frame does not have enough physical space for two large elements
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, false);
					}}
				>
					Contrast failure — same-color elements cannot be distinguished from each other
				</button>
			</div>
			<div class="feedback" id="fb-q2"></div>
		</div>

		<div class="question" id="q3">
			<div class="q-text">
				<span class="q-num">03.</span>According to the decision framework in this module, when is
				text animation clearly justified?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, false);
					}}
				>
					When the video needs more visual interest to maintain viewer attention
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, false);
					}}
				>
					When the creator's editing software supports smooth animation
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, true);
					}}
				>
					When the motion itself reinforces what the text is communicating — e.g. timing with
					narration rhythm, revealing information progressively, or directing attention to a
					specific frame element
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, false);
					}}
				>
					When the text is a headline, since primary elements always benefit from animation
				</button>
			</div>
			<div class="feedback" id="fb-q3"></div>
		</div>

		<div class="question" id="q4">
			<div class="q-text">
				<span class="q-num">04.</span>A statistic needs to land with authority — the viewer should
				feel its weight when it appears. Which easing type is most appropriate?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, false);
					}}
				>
					Ease-in — the element builds speed as it arrives, signalling momentum
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, false);
					}}
				>
					Overshoot/bounce — the energetic motion amplifies the impact of the number
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, true);
					}}
				>
					Ease-out — the element arrives fast and settles decisively, communicating authority and
					finality
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, false);
					}}
				>
					Linear — the mechanical consistency is appropriate for data-driven content
				</button>
			</div>
			<div class="feedback" id="fb-q4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-display">—</div>
			<div class="score-label">questions correct out of 4</div>
		</div>
	</section>

	<!-- NAV -->
	<div class="nav-links">
		<a href="./02" class="prev-link">← Module 02: Sequencing, Pacing &amp; Retention</a>
		<a href="./04" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">Using Images, Diagrams &amp; B-Roll Intentionally</div>
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

	/* ── HEADER ── */
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

	/* ── HERO ── */
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
			rgba(61, 217, 164, 0.013) 2px,
			rgba(61, 217, 164, 0.013) 4px
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
		color: var(--vs-mint);
		border: 1px solid var(--vs-mint);
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
		color: var(--vs-mint);
	}

	/* ── TOC ── */
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
		color: var(--vs-mint);
		border-color: var(--vs-mint);
	}

	/* ── OBJECTIVES ── */
	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--vs-mint);
		background: var(--vs-surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-mint);
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
		color: var(--vs-mint);
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

	/* ── CALLOUTS ── */
	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 5%, var(--vs-surface));
		font-size: 13px;
	}
	.callout.amber {
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-surface));
	}
	.callout.blue {
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 5%, var(--vs-surface));
	}
	:global(.callout.red) {
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 5%, var(--vs-surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-mint);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	.callout.amber .callout-label {
		color: var(--vs-amber);
	}
	.callout.blue .callout-label {
		color: var(--vs-blue);
	}
	:global(.callout.red) .callout-label {
		color: var(--vs-red);
	}

	/* ── DEMO BOXES ── */
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
	.demo-badge {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	.demo-badge.interactive {
		color: var(--vs-mint);
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
	}
	:global(.demo-badge.animated) {
		color: var(--vs-amber);
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	/* ── BUTTONS / CONTROLS ── */
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
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	:global(.btn.active) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
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
	:global(.btn.blue:hover) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
	}
	:global(.btn.blue.active) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 10%, transparent);
	}
	:global(.btn.red:hover) {
		border-color: var(--vs-red);
		color: var(--vs-red);
	}
	:global(.btn.red.active) {
		border-color: var(--vs-red);
		color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
	}
	:global(.btn-row) {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.25rem;
	}

	:global(.slider-row) {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 0.5rem 0;
	}
	:global(.slider-row) label {
		font-size: 12px;
		min-width: 110px;
		color: var(--vs-text);
	}
	:global(.slider-row) :global(input[type='range']) {
		flex: 1;
		-webkit-appearance: none;
		height: 3px;
		background: var(--vs-border2);
		outline: none;
	}
	:global(.slider-row) :global(input[type='range']::-webkit-slider-thumb) {
		-webkit-appearance: none;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--vs-mint);
		cursor: pointer;
	}
	:global(.slider-val) {
		font-size: 12px;
		color: var(--vs-mint);
		min-width: 40px;
		text-align: right;
		font-weight: 600;
	}

	/* ── TABLE ── */
	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--vs-raised);
		color: var(--vs-mint);
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
		color: var(--vs-mint);
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
		background: var(--vs-mint);
		width: 0;
		transition: width 0.4s ease;
	}

	/* ── QUIZ ── */
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
		color: var(--vs-mint);
	}
	.score-label {
		font-size: 12px;
		color: var(--vs-muted);
		margin-top: 0.25rem;
	}

	/* ── NAV ── */
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

	/* ════════════════════════════════════════════
     MODULE-SPECIFIC: VIDEO FRAME PREVIEW
  ════════════════════════════════════════════ */
	.frame-preview {
		aspect-ratio: 16 / 9;
		background: #000;
		position: relative;
		overflow: hidden;
		border: 1px solid var(--vs-border2);
		user-select: none;
	}
	.frame-bg {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.frame-bg-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: #ffffff18;
		pointer-events: none;
	}
	/* safe zone overlay */
	.frame-safezone {
		position: absolute;
		top: 5%;
		left: 5%;
		right: 5%;
		bottom: 5%;
		border: 1px dashed #ffffff12;
		pointer-events: none;
	}

	/* ── TEXT ELEMENT LAYERS ── */
	.txt-layer {
		position: absolute;
		pointer-events: none;
		transition:
			opacity 0.35s ease,
			transform 0.35s ease;
	}
	.txt-layer.hidden {
		opacity: 0;
		transform: translateY(6px);
	}

	/* Headline treatment */
	.txt-headline {
		top: 12%;
		left: 6%;
		font-family: 'Syne', sans-serif;
		font-weight: 800;
		line-height: 1.1;
	}
	/* Supporting point */
	.txt-support {
		bottom: 18%;
		left: 6%;
		font-family: 'IBM Plex Mono', monospace;
		font-weight: 400;
	}
	/* Annotation */
	.txt-annotation {
		top: 38%;
		right: 6%;
		font-family: 'IBM Plex Mono', monospace;
		font-weight: 300;
		text-align: right;
	}
	/* Lower third strip */
	.txt-lower-third {
		bottom: 0;
		left: 0;
		right: 0;
		padding: 0.5rem 6%;
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	.txt-lower-third-bar {
		width: 3px;
		align-self: stretch;
		flex-shrink: 0;
	}

	/* Clutter layer */
	.txt-clutter {
		position: absolute;
		pointer-events: none;
		font-family: 'IBM Plex Mono', monospace;
		transition: opacity 0.35s;
	}

	/* ── HIERARCHY RULER ── */
	:global(.hier-row) {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.6rem 0;
		border-bottom: 1px solid var(--vs-border);
	}
	:global(.hier-row:last-child) {
		border-bottom: none;
	}
	:global(.hier-rank) {
		width: 24px;
		height: 24px;
		border-radius: 2px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 10px;
		font-weight: 700;
		flex-shrink: 0;
	}
	:global(.hier-label) {
		flex: 1;
		font-size: 12px;
		color: var(--vs-text);
	}
	:global(.hier-bar-wrap) {
		width: 120px;
		height: 6px;
		background: var(--vs-border);
		border-radius: 3px;
		overflow: hidden;
		flex-shrink: 0;
	}
	:global(.hier-bar-fill) {
		height: 100%;
		border-radius: 3px;
	}
	:global(.hier-props) {
		font-size: 10px;
		color: var(--vs-muted);
		min-width: 160px;
		text-align: right;
	}

	/* ── ANIMATION DECISION TREE ── */
	:global(.dtree) {
		position: relative;
	}
	:global(.dnode) {
		border: 1px solid var(--vs-border);
		padding: 0.75rem 1rem;
		background: var(--vs-raised);
		font-size: 12px;
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
	}
	:global(.dnode:hover) {
		border-color: var(--vs-mint);
	}
	:global(.dnode.active) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 8%, var(--vs-raised));
	}
	:global(.dnode.result-animate) {
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 8%, var(--vs-raised));
	}
	:global(.dnode.result-static) {
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 8%, var(--vs-raised));
	}
	:global(.dnode.result-either) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 8%, var(--vs-raised));
	}
	:global(.dnode-q) {
		color: #fff;
		font-weight: 500;
		margin-bottom: 0.6rem;
	}
	:global(.dnode-opts) {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	:global(.dnode-opt) {
		padding: 4px 12px;
		border: 1px solid var(--vs-border2);
		font-size: 11px;
		cursor: pointer;
		transition: all 0.15s;
		font-family: 'IBM Plex Mono', monospace;
		color: var(--vs-muted);
	}
	:global(.dnode-opt:hover) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	:global(.dnode-opt.chosen) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
	}
	:global(.dtree-connector) {
		width: 2px;
		height: 20px;
		background: var(--vs-border2);
		margin: 0 auto;
	}
	:global(.dtree-result) {
		padding: 1rem 1.25rem;
		border: 1px solid;
		font-size: 12px;
		text-align: center;
		display: none;
	}
	:global(.dtree-result.animate) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 6%, var(--vs-surface));
	}
	:global(.dtree-result.static) {
		border-color: var(--vs-amber);
		color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 6%, var(--vs-surface));
	}
	:global(.dtree-result.either) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 6%, var(--vs-surface));
	}
	:global(.dtree-verdict) {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		margin-bottom: 0.4rem;
	}
	:global(.dtree-reason) {
		font-size: 12px;
	}

	/* ── TEXT TREATMENT STUDIO ── */
	.treatment-tabs {
		display: flex;
		gap: 0;
		border: 1px solid var(--vs-border);
		overflow: hidden;
		margin-bottom: 0;
	}
	.treatment-tab {
		flex: 1;
		padding: 0.6rem;
		text-align: center;
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		cursor: pointer;
		border-right: 1px solid var(--vs-border);
		color: var(--vs-muted);
		transition: all 0.15s;
		background: var(--vs-raised);
	}
	.treatment-tab:last-child {
		border-right: none;
	}
	.treatment-tab.active {
		background: color-mix(in srgb, var(--vs-mint) 10%, var(--vs-raised));
		color: var(--vs-mint);
	}
	.treatment-panel {
		display: none;
	}
	.treatment-panel.active {
		display: block;
	}

	/* ── EASING VISUALISER ── */
	#easing-canvas {
		display: block;
		border: 1px solid var(--vs-border);
		background: #040710;
	}
	.easing-demo-text {
		height: 60px;
		background: var(--vs-raised);
		border: 1px solid var(--vs-border);
		display: flex;
		align-items: center;
		overflow: hidden;
		position: relative;
		margin-top: 8px;
	}
	.easing-text-el {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		color: var(--vs-mint);
		white-space: nowrap;
		position: absolute;
		left: 20px;
	}

	/* ── CONTRAST METER ── */
	:global(.contrast-swatch) {
		height: 56px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: 'Syne', sans-serif;
		font-size: 16px;
		font-weight: 700;
		border: 1px solid var(--vs-border);
		letter-spacing: 0.05em;
		transition: all 0.2s;
	}
</style>
