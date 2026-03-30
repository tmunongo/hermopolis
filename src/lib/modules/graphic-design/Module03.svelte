<script lang="ts">
	/* eslint-disable @typescript-eslint/no-unused-vars, no-undef, no-useless-assignment */
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
		/* ═══════════════════════════════════
   READING PROGRESS
═══════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width =
					(el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight)) * 100 + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		/* ═══════════════════════════════════
   TYPEFACE EXPLORER
═══════════════════════════════════ */
		const TF_CATS = ['serif', 'sans', 'display', 'mono'];

		function setTfCat(cat) {
			TF_CATS.forEach((c) => {
				document.getElementById('tf-panel-' + c).classList.toggle('active', c === cat);
				document.querySelector(`.tf-tab[data-cat="${c}"]`).classList.toggle('active', c === cat);
			});
		}

		function setSerifVariant(v, btn) {
			document
				.querySelectorAll('#tf-panel-serif .tf-variant-btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			const s = document.getElementById('serif-specimen');
			const sub = document.getElementById('serif-sub');
			if (v === 'display') {
				s.style.fontFamily = "'Playfair Display',serif";
				s.style.fontStyle = 'normal';
				sub.style.fontFamily = "'Crimson Pro',serif";
			} else if (v === 'text') {
				s.style.fontFamily = "'Crimson Pro',serif";
				s.style.fontStyle = 'italic';
				sub.style.fontFamily = "'Crimson Pro',serif";
			} else {
				s.style.fontFamily = "'Fraunces',serif";
				s.style.fontStyle = 'normal';
				sub.style.fontFamily = "'Fraunces',serif";
			}
		}

		function setSansVariant(v, btn) {
			document
				.querySelectorAll('#tf-panel-sans .tf-variant-btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			const s = document.getElementById('sans-specimen');
			s.style.fontFamily =
				v === 'geometric' ? "'DM Sans',sans-serif" : "'Space Grotesk',sans-serif";
		}

		function setDisplayVariant(v, btn) {
			document
				.querySelectorAll('#tf-panel-display .tf-variant-btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			const s = document.getElementById('display-specimen');
			if (v === 'condensed') {
				s.style.fontFamily = "'Bebas Neue',sans-serif";
				s.style.fontWeight = '400';
				s.textContent = 'DESIGN YOUR WORLD';
			} else if (v === 'editorial') {
				s.style.fontFamily = "'Fraunces',serif";
				s.style.fontWeight = '900';
				s.textContent = 'Design Your World';
			} else {
				s.style.fontFamily = "'Syne',sans-serif";
				s.style.fontWeight = '800';
				s.textContent = 'Design Your World';
			}
		}

		function setMonoVariant(v, btn) {
			document
				.querySelectorAll('#tf-panel-mono .tf-variant-btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			const s = document.getElementById('mono-specimen');
			s.style.fontFamily = v === 'ibm' ? "'IBM Plex Mono',monospace" : "'Space Mono',monospace";
		}

		/* ═══════════════════════════════════
   SPACING LAB
═══════════════════════════════════ */
		function updateSpacing() {
			const weight = document.getElementById('sp-weight').value;
			const track = parseFloat(document.getElementById('sp-tracking').value);
			const leading = parseFloat(document.getElementById('sp-leading').value);
			const bodyLead = parseFloat(document.getElementById('sp-body-lead').value);

			document.getElementById('sp-weight-val').textContent = weight;
			document.getElementById('sp-tracking-val').textContent = track.toFixed(2) + 'em';
			document.getElementById('sp-leading-val').textContent = leading.toFixed(2);
			document.getElementById('sp-body-lead-val').textContent = bodyLead.toFixed(2);

			const heading = document.getElementById('spacing-heading');
			const body = document.getElementById('spacing-body');

			heading.style.fontWeight = weight;
			heading.style.letterSpacing = track + 'em';
			heading.style.lineHeight = leading;
			body.style.lineHeight = bodyLead;

			// Readability score
			let score = 100;
			if (track < -0.04) score -= 30;
			if (track > 0.25) score -= 20;
			if (leading < 0.95 || leading > 2.0) score -= 25;
			if (bodyLead < 1.1) score -= 35;
			if (bodyLead > 2.2) score -= 15;
			if (parseInt(weight) < 300 && track > 0.2) score -= 10;
			score = Math.max(0, Math.min(100, score));

			const bar = document.getElementById('readability-bar');
			const val = document.getElementById('readability-val');
			bar.style.width = score + '%';
			bar.style.background =
				score > 70 ? 'var(--sage)' : score > 40 ? 'var(--amber)' : 'var(--rose)';
			val.style.color = score > 70 ? 'var(--sage)' : score > 40 ? 'var(--amber)' : 'var(--rose)';
			val.textContent = score > 70 ? 'Good' : score > 40 ? 'Marginal' : 'Poor';
		}

		function setSpacingPreset(p) {
			const w = document.getElementById('sp-weight');
			const t = document.getElementById('sp-tracking');
			const l = document.getElementById('sp-leading');
			const b = document.getElementById('sp-body-lead');
			if (p === 'editorial') {
				w.value = '700';
				t.value = '0.01';
				l.value = '1.10';
				b.value = '1.75';
			}
			if (p === 'thumbnail') {
				w.value = '900';
				t.value = '0.02';
				l.value = '0.95';
				b.value = '1.70';
			}
			if (p === 'label') {
				w.value = '500';
				t.value = '0.22';
				l.value = '1.40';
				b.value = '1.60';
			}
			if (p === 'broken') {
				w.value = '300';
				t.value = '-0.07';
				l.value = '0.87';
				b.value = '0.92';
			}
			if (p === 'reset') {
				w.value = '700';
				t.value = '0';
				l.value = '1.15';
				b.value = '1.70';
			}
			updateSpacing();
		}

		/* ═══════════════════════════════════
   FONT PAIRING
═══════════════════════════════════ */
		const FONT_DATA = {
			playfair: { family: "'Playfair Display',serif", cat: 'serif', wt: 700, per: 'editorial' },
			fraunces: { family: "'Fraunces',serif", cat: 'serif', wt: 700, per: 'editorial' },
			bebas: { family: "'Bebas Neue',sans-serif", cat: 'display', wt: 400, per: 'impact' },
			syne: { family: "'Syne',sans-serif", cat: 'display', wt: 800, per: 'geometric' },
			crimson: { family: "'Crimson Pro',serif", cat: 'serif', wt: 600, per: 'editorial' },
			'dmsans-head': { family: "'DM Sans',sans-serif", cat: 'sans', wt: 700, per: 'clean' },

			dmsans: { family: "'DM Sans',sans-serif", cat: 'sans', wt: 400, per: 'clean' },
			spacegrotesk: {
				family: "'Space Grotesk',sans-serif",
				cat: 'sans',
				wt: 400,
				per: 'geometric'
			},
			ibmplexmono: {
				family: "'IBM Plex Mono',monospace",
				cat: 'mono',
				wt: 400,
				per: 'technical'
			},
			'crimson-body': { family: "'Crimson Pro',serif", cat: 'serif', wt: 400, per: 'editorial' },
			'playfair-body': {
				family: "'Playfair Display',serif",
				cat: 'serif',
				wt: 400,
				per: 'editorial'
			},
			spacemono: { family: "'Space Mono',monospace", cat: 'mono', wt: 400, per: 'technical' }
		};

		const VERDICTS = {
			great: {
				color: 'var(--sage)',
				text: 'Strong pairing — clear category contrast and compatible personalities. This combination will serve you across thumbnails, headers, and body text.'
			},
			good: {
				color: 'var(--sky)',
				text: 'Solid pairing — works with care. Ensure strong size contrast between the two so hierarchy is never ambiguous.'
			},
			marginal: {
				color: 'var(--amber)',
				text: 'Proceed with caution. The fonts share too much — category, weight, or personality — for a clear visual distinction. Consider a bolder weight contrast.'
			},
			conflict: {
				color: 'var(--rose)',
				text: 'High conflict risk. These fonts work against each other — either same category with no differentiation, or incompatible personalities. Choose a more contrasting body font.'
			}
		};

		function scorePairing(h, b) {
			// Category contrast
			let cat = 0;
			if (h.cat !== b.cat) cat = 100;
			else if (h.cat === 'serif' && b.cat === 'serif') cat = 45;
			else cat = 20;

			// Weight differentiation
			const wDiff = Math.abs(h.wt - b.wt);
			const wt = Math.min(100, (wDiff / 500) * 100 + 20);

			// Personality match
			let per = 60;
			if (h.per === b.per) per = 30;
			if (
				(h.per === 'editorial' && b.per === 'clean') ||
				(h.per === 'clean' && b.per === 'editorial')
			)
				per = 85;
			if (h.per === 'impact' && b.per === 'clean') per = 80;
			if (h.per === 'geometric' && b.per === 'geometric' && h.cat !== b.cat) per = 75;
			if (h.per === 'editorial' && b.per === 'technical') per = 70;
			if (h.cat === 'display' && b.cat === 'display') per = 15;

			return { cat: Math.round(cat), wt: Math.round(wt), per: Math.round(per) };
		}

		function updatePairing() {
			const hKey = document.getElementById('pair-heading').value;
			const bKey = document.getElementById('pair-body').value;
			const h = FONT_DATA[hKey],
				b = FONT_DATA[bKey];

			document.getElementById('pair-headline').style.fontFamily = h.family;
			document.getElementById('pair-headline').style.fontWeight = h.wt;
			document.getElementById('pair-eyebrow').style.fontFamily = b.family;
			document.getElementById('pair-body-text').style.fontFamily = b.family;
			document.getElementById('pair-cta').style.fontFamily = b.family;

			const scores = scorePairing(h, b);
			const overall = Math.round(scores.cat * 0.45 + scores.wt * 0.25 + scores.per * 0.3);

			function setBar(id, sid, val) {
				const bar = document.getElementById(id);
				const sc = document.getElementById(sid);
				bar.style.width = val + '%';
				bar.style.background = val > 70 ? 'var(--sage)' : val > 45 ? 'var(--amber)' : 'var(--rose)';
				sc.textContent = val + '%';
				sc.style.color = val > 70 ? 'var(--sage)' : val > 45 ? 'var(--amber)' : 'var(--rose)';
			}
			setBar('hbar-cat', 'hscore-cat', scores.cat);
			setBar('hbar-wt', 'hscore-wt', scores.wt);
			setBar('hbar-per', 'hscore-per', scores.per);

			const v =
				overall >= 70 ? 'great' : overall >= 52 ? 'good' : overall >= 35 ? 'marginal' : 'conflict';
			const verdict = document.getElementById('harmony-verdict');
			verdict.style.borderColor = VERDICTS[v].color;
			verdict.style.color = VERDICTS[v].color;
			verdict.style.background = `color-mix(in srgb, ${VERDICTS[v].color} 6%, var(--raised))`;
			verdict.textContent = VERDICTS[v].text;
		}

		updatePairing();

		/* ═══════════════════════════════════
   THUMBNAIL TYPE LAB
═══════════════════════════════════ */
		const thumbCanvas = document.getElementById('thumb-canvas');
		const thumbCtx = thumbCanvas.getContext('2d');
		const TW = thumbCanvas.width,
			TH = thumbCanvas.height;

		let thumbBg = 0;
		let thumbScaled = false;

		const BG_SCENES = [
			() => {
				const g = thumbCtx.createLinearGradient(0, 0, TW, TH);
				g.addColorStop(0, '#0c1a2e');
				g.addColorStop(1, '#0a1018');
				thumbCtx.fillStyle = g;
				thumbCtx.fillRect(0, 0, TW, TH);
				// Subject silhouette
				thumbCtx.fillStyle = '#17293e';
				thumbCtx.fillRect(0, 0, Math.floor(TW * 0.44), TH);
				thumbCtx.fillStyle = '#d4a07a';
				thumbCtx.beginPath();
				thumbCtx.ellipse(Math.floor(TW * 0.22), Math.floor(TH * 0.38), 52, 60, 0, 0, Math.PI * 2);
				thumbCtx.fill();
				thumbCtx.fillStyle = '#1a2c44';
				thumbCtx.beginPath();
				thumbCtx.ellipse(TW * 0.22 - 14, TH * 0.33, 5, 4, 0, 0, Math.PI * 2);
				thumbCtx.fill();
				thumbCtx.beginPath();
				thumbCtx.ellipse(TW * 0.22 + 14, TH * 0.33, 5, 4, 0, 0, Math.PI * 2);
				thumbCtx.fill();
				thumbCtx.fillStyle = '#101e30';
				thumbCtx.fillRect(0, Math.floor(TH * 0.58), Math.floor(TW * 0.44), TH);
			},
			() => {
				thumbCtx.fillStyle = '#08100a';
				thumbCtx.fillRect(0, 0, TW, TH);
				const g2 = thumbCtx.createRadialGradient(
					TW * 0.5,
					TH * 0.4,
					0,
					TW * 0.5,
					TH * 0.4,
					TW * 0.6
				);
				g2.addColorStop(0, 'rgba(86,208,100,0.12)');
				g2.addColorStop(1, 'transparent');
				thumbCtx.fillStyle = g2;
				thumbCtx.fillRect(0, 0, TW, TH);
				for (let i = 0; i < 8; i++) {
					thumbCtx.beginPath();
					thumbCtx.arc(TW * (0.1 + i * 0.12), TH * 0.7, TH * 0.15, 0, Math.PI * 2);
					thumbCtx.fillStyle = `rgba(40,80,40,${0.08 + i * 0.02})`;
					thumbCtx.fill();
				}
			},
			() => {
				thumbCtx.fillStyle = '#0f060e';
				thumbCtx.fillRect(0, 0, TW, TH);
				const g3 = thumbCtx.createLinearGradient(0, 0, TW, 0);
				g3.addColorStop(0, 'rgba(155,109,255,0.25)');
				g3.addColorStop(0.5, 'transparent');
				g3.addColorStop(1, 'rgba(232,93,138,0.2)');
				thumbCtx.fillStyle = g3;
				thumbCtx.fillRect(0, 0, TW, TH);
				// Grid
				thumbCtx.strokeStyle = 'rgba(155,109,255,0.08)';
				thumbCtx.lineWidth = 1;
				for (let x = 0; x < TW; x += 40) {
					thumbCtx.beginPath();
					thumbCtx.moveTo(x, 0);
					thumbCtx.lineTo(x, TH);
					thumbCtx.stroke();
				}
				for (let y = 0; y < TH; y += 40) {
					thumbCtx.beginPath();
					thumbCtx.moveTo(0, y);
					thumbCtx.lineTo(TW, y);
					thumbCtx.stroke();
				}
			}
		];

		function drawThumb() {
			const font = document.getElementById('thumb-font').value;
			const size = parseInt(document.getElementById('thumb-size').value);
			const weight = document.getElementById('thumb-weight').value;
			const text1 = document.getElementById('thumb-text1').value || 'DESIGN';
			const text2 = document.getElementById('thumb-text2').value || 'FROM SCRATCH';
			const tracking = parseFloat(document.getElementById('thumb-tracking').value);

			document.getElementById('thumb-size-val').textContent = size;
			document.getElementById('thumb-weight-val').textContent = weight;
			document.getElementById('thumb-tracking-val').textContent = tracking.toFixed(2);

			// Draw background
			BG_SCENES[thumbBg]();

			const ctx = thumbCtx;
			const TX = Math.floor(TW * 0.46);
			const accents = ['#f5a623', '#e85d8a', '#56d0a0'];
			const ac = accents[thumbBg];

			// Accent bar
			ctx.fillStyle = ac;
			ctx.fillRect(TX - 12, Math.floor(TH * 0.12), 3, Math.floor(TH * 0.76));

			// Title line 1
			ctx.save();
			ctx.font = `${weight} ${size}px '${font}', sans-serif`;
			ctx.fillStyle = '#ffffff';
			ctx.letterSpacing = tracking + 'em';

			// Measure to check overflow
			const m1 = ctx.measureText(text1);
			const scale1 = Math.min(1, (TW - TX - 20) / (m1.width + 1));
			ctx.setTransform(scale1, 0, 0, 1, TX + 8 * (1 - scale1), 0);
			ctx.fillText(text1, TX + 8, Math.floor(TH * 0.45));
			ctx.restore();

			// Title line 2
			ctx.save();
			ctx.font = `${weight} ${Math.floor(size * 0.65)}px '${font}', sans-serif`;
			ctx.fillStyle = ac;
			ctx.letterSpacing = tracking + 'em';
			const m2 = ctx.measureText(text2);
			const scale2 = Math.min(1, (TW - TX - 20) / (m2.width + 1));
			ctx.setTransform(scale2, 0, 0, 1, TX + 8 * (1 - scale2), 0);
			ctx.fillText(text2, TX + 8, Math.floor(TH * 0.63));
			ctx.restore();

			// Eyebrow
			ctx.font = `400 11px 'IBM Plex Mono', monospace`;
			ctx.fillStyle = 'rgba(160,180,200,0.6)';
			ctx.letterSpacing = '0.1em';
			ctx.fillText('DESIGN COURSE  ·  EP 01', TX + 8, Math.floor(TH * 0.26));
			ctx.letterSpacing = '0';

			// Scale indicator
			if (thumbScaled) {
				ctx.fillStyle = 'rgba(0,0,0,0.65)';
				ctx.fillRect(0, 0, TW, TH);
				// Small thumbnail inset
				const sw = 168,
					sh = 94;
				const sx = Math.floor((TW - sw) / 2),
					sy = Math.floor((TH - sh) / 2);
				ctx.drawImage(thumbCanvas, 0, 0, TW, TH, sx, sy, sw, sh);
				ctx.strokeStyle = 'rgba(245,166,35,0.7)';
				ctx.lineWidth = 1;
				ctx.strokeRect(sx, sy, sw, sh);
				ctx.fillStyle = 'rgba(245,166,35,0.8)';
				ctx.font = '10px IBM Plex Mono, monospace';
				ctx.textAlign = 'center';
				ctx.fillText('← 168px YouTube thumbnail size →', TW / 2, sy - 8);
				ctx.textAlign = 'left';
			}

			// Legibility check
			const noteEl = document.getElementById('thumb-note');
			const isCondensed = font === 'Bebas Neue';
			const isMono = font === 'IBM Plex Mono' || font === 'Space Mono';
			const isLight = parseInt(weight) <= 400;

			if (isLight) {
				noteEl.style.color = 'var(--rose)';
				noteEl.textContent =
					'⚠ Light weight at thumbnail size — thin strokes will disappear at 168px. Increase weight to 700 or higher.';
			} else if (isMono && size < 38) {
				noteEl.style.color = 'var(--amber)';
				noteEl.textContent =
					'⚠ Monospace fonts have wider characters — legibility drops faster than proportional faces at small sizes. Consider larger size.';
			} else if (size < 36) {
				noteEl.style.color = 'var(--amber)';
				noteEl.textContent =
					'↑ Font size may be too small for thumbnail context. Aim for 48–72px for primary title.';
			} else if (isCondensed && tracking > 0.15) {
				noteEl.style.color = 'var(--amber)';
				noteEl.textContent =
					'Condensed display faces typically need less tracking — too much spacing undermines the vertical rhythm they create.';
			} else {
				noteEl.style.color = 'var(--sage)';
				noteEl.textContent =
					'✓ Looking solid. Toggle "Preview at Thumb Size" to test legibility at 168px.';
			}
		}

		function toggleThumbScale() {
			thumbScaled = !thumbScaled;
			const btn = document.getElementById('thumb-scale-btn');
			btn.classList.toggle('active', thumbScaled);
			btn.textContent = thumbScaled ? 'Back to Full Size' : 'Preview at Thumb Size';
			drawThumb();
		}

		function randomiseThumb() {
			thumbBg = (thumbBg + 1) % BG_SCENES.length;
			drawThumb();
		}

		drawThumb();

		/* ═══════════════════════════════════
   QUIZ
═══════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;
		const explanations = [
			'Correct. Monospace typefaces originated from fixed-width terminals and carry strong associations with systematic, technical, and analytical thinking — which maps directly to a data-driven or research-oriented channel identity.',
			'Correct. Tracking (letter-spacing) is the correct response to optically cramped uppercase text. Uppercase letters are designed for sentence case and become visually tight when set in all-caps — loosening the tracking compensates.',
			"Correct. The serif/sans-serif pairing works because the two fonts are categorically different types of letterform, making the hierarchy readable from category alone — not just from size or weight. The viewer's eye distinguishes them instantly.",
			'Correct. Thumbnails must be read at 168×94 pixels. At that size, thin strokes disappear entirely and generous tracking spreads letters too far apart to read as grouped words in under two seconds.',
			'Correct. Tracking is a global, uniform adjustment across a text block. Kerning is a targeted adjustment between specific letter pairs where the geometry of adjacent shapes creates optical gaps (AV, To, We, etc.).'
		];
		const wrongMsg =
			'Not quite — revisit the principle. Focus on what the viewer experiences, not what the designer intends.';

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

		/* ═══════════════════════════════════
   PAIR AUDIT ASSESSMENT
═══════════════════════════════════ */
		const auditAnswered = {};
		const auditCorrect = { 1: 1, 2: 0 };
		const auditFeedback = {
			1: {
				ok: 'Correct. Bebas Neue is a display font designed exclusively for large sizes. Used at body text sizes (~14px), the letterforms become illegible and the equal weight of both elements destroys any typographic hierarchy.',
				bad: 'Not quite. The fundamental problem is category misuse — a display font used at body size loses legibility, and both elements share the same font with no hierarchy differentiation.'
			},
			2: {
				ok: 'Correct. Pairing two serifs at similar weights is the most common serif-pairing mistake. The fonts read as "almost the same but slightly different" — which feels like an error rather than a deliberate choice. Stronger weight contrast (e.g. Playfair Black heading + Crimson Pro Regular body) would resolve it.',
				bad: 'Not quite. Two serifs can absolutely be used together — but they need strong weight contrast to distinguish the heading from the body. The problem here is that both are set at similar weights, making the hierarchy ambiguous.'
			}
		};

		function handleAudit(el, idx, questionNum) {
			if (auditAnswered[questionNum]) return;
			auditAnswered[questionNum] = true;
			const opts = el.closest('.audit-options').querySelectorAll('.audit-opt');
			opts.forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById('af-' + questionNum);
			if (idx === auditCorrect[questionNum]) {
				el.classList.add('correct');
				fb.textContent = '✓ ' + auditFeedback[questionNum].ok;
				fb.className = 'audit-feedback ok';
			} else {
				el.classList.add('wrong');
				opts[auditCorrect[questionNum]].classList.add('correct');
				fb.textContent = '✗ ' + auditFeedback[questionNum].bad;
				fb.className = 'audit-feedback bad';
			}
		}

		if (typeof setTfCat === 'function') actions.setTfCat = setTfCat;
		if (typeof setSerifVariant === 'function') actions.setSerifVariant = setSerifVariant;
		if (typeof setSansVariant === 'function') actions.setSansVariant = setSansVariant;
		if (typeof setDisplayVariant === 'function') actions.setDisplayVariant = setDisplayVariant;
		if (typeof setMonoVariant === 'function') actions.setMonoVariant = setMonoVariant;
		if (typeof updateSpacing === 'function') actions.updateSpacing = updateSpacing;
		if (typeof setSpacingPreset === 'function') actions.setSpacingPreset = setSpacingPreset;
		if (typeof scorePairing === 'function') actions.scorePairing = scorePairing;
		if (typeof updatePairing === 'function') actions.updatePairing = updatePairing;
		if (typeof setBar === 'function') actions.setBar = setBar;
		if (typeof drawThumb === 'function') actions.drawThumb = drawThumb;
		if (typeof toggleThumbScale === 'function') actions.toggleThumbScale = toggleThumbScale;
		if (typeof randomiseThumb === 'function') actions.randomiseThumb = randomiseThumb;
		if (typeof handleQuiz === 'function') actions.handleQuiz = handleQuiz;
		if (typeof handleAudit === 'function') actions.handleAudit = handleAudit;

		return () => {
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
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 03 of 10</div>
	</header>

	<!-- HERO -->
	<div class="module-hero">
		<div class="module-number">03</div>
		<div class="module-tag">Module 03 · Type + Voice</div>
		<h1 class="module-title">Typography<br /><span>Essentials</span></h1>
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
			<li><a href="#typeface-categories">Typeface Categories</a></li>
			<li><a href="#spacing">Weight, Spacing &amp; Leading</a></li>
			<li><a href="#pairing">Pairing Without Conflict</a></li>
			<li><a href="#applied">Applied: Thumbnails &amp; Web</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<!-- OBJECTIVES -->
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Identify and correctly use serif, sans-serif, monospace, and display typefaces</li>
			<li>Control weight, tracking, kerning, and leading to change reading feel</li>
			<li>Pair two typefaces that create harmony rather than conflict</li>
			<li>Apply typographic hierarchy to thumbnails, title cards, and web layouts</li>
		</ul>
	</section>

	<!-- ══════════════════════════════════
     SECTION 1: TYPEFACE CATEGORIES
══════════════════════════════════ -->
	<section id="typeface-categories" class="section">
		<div class="section-header">
			<span class="section-num">03.01</span>
			<h2 class="section-title">Typeface Categories</h2>
		</div>

		<p>
			Every typeface belongs to a category — and each category carries a set of cultural
			associations, perceptual properties, and appropriate use cases. Choosing a category is the
			first typographic decision, and it is more important than choosing a specific typeface within
			that category. Getting the category wrong is a louder mistake than getting the specific face
			wrong.
		</p>

		<p>
			There are four categories you need to understand for brand and channel work:
			<strong>serif</strong>, <strong>sans-serif</strong>, <strong>display</strong>, and
			<strong>monospace</strong>. Each carries a distinct personality, and that personality either
			reinforces or undermines what your content is communicating.
		</p>

		<!-- DEMO: Typeface Explorer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Typeface Category Explorer</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="tf-tabs" id="tf-tabs">
				<div
					class="tf-tab active"
					data-cat="serif"
					onclick={(e) => actions.setTfCat('serif')}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.setTfCat('serif');
						}
					}}
				>
					Serif
				</div>
				<div
					class="tf-tab"
					data-cat="sans"
					onclick={(e) => actions.setTfCat('sans')}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.setTfCat('sans');
						}
					}}
				>
					Sans-Serif
				</div>
				<div
					class="tf-tab"
					data-cat="display"
					onclick={(e) => actions.setTfCat('display')}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.setTfCat('display');
						}
					}}
				>
					Display
				</div>
				<div
					class="tf-tab"
					data-cat="mono"
					onclick={(e) => actions.setTfCat('mono')}
					role="button"
					tabindex="0"
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							actions.setTfCat('mono');
						}
					}}
				>
					Monospace
				</div>
			</div>

			<!-- SERIF -->
			<div class="tf-panel active" id="tf-panel-serif">
				<div class="tf-meta">
					<span class="tf-tag amber">Authority</span>
					<span class="tf-tag amber">Tradition</span>
					<span class="tf-tag amber">Legibility</span>
					<span class="tf-tag amber">Long-form</span>
				</div>
				<div class="tf-specimen-wrap" id="serif-wrap">
					<div
						class="tf-specimen"
						id="serif-specimen"
						style="font-family: 'Playfair Display', serif; font-weight: 700"
					>
						Aa Bb Gg Rr
					</div>
					<div
						class="tf-specimen-sub"
						id="serif-sub"
						style="font-family: 'Crimson Pro', serif; font-weight: 400"
					>
						The quick brown fox jumps over the lazy dog.
					</div>
					<!-- Anatomy labels -->
					<div class="tf-ann" style="bottom: 10px; left: 40px">serifs →</div>
					<div class="tf-ann" style="top: 10px; right: 16px">high contrast strokes</div>
				</div>
				<div class="tf-desc">
					Serifs are the small finishing strokes at the ends of letterform strokes. They evolved
					from Roman stone-cutting and carry millennia of association with
					<em>authority, tradition, and seriousness</em>. In print, serifs aid long-form legibility
					by guiding the eye along horizontal lines of text. On screen at large sizes, they
					communicate gravitas and editorial quality.
				</div>
				<ul class="tf-use-list">
					<li>Editorial, book, and documentary-style content</li>
					<li>Brand identities that emphasise heritage, luxury, or trust</li>
					<li>Large display titles where contrast and elegance matter</li>
					<li>Avoid for body text at small screen sizes — serifs render poorly below ~14px</li>
				</ul>
				<div class="tf-edit-row">
					<label>Style:</label>
					<button
						class="tf-variant-btn active"
						onclick={(e) => actions.setSerifVariant('display', e.currentTarget)}
					>
						Display (Playfair)
					</button>
					<button
						class="tf-variant-btn"
						onclick={(e) => actions.setSerifVariant('text', e.currentTarget)}
					>
						Text (Crimson Pro)
					</button>
					<button
						class="tf-variant-btn"
						onclick={(e) => actions.setSerifVariant('optical', e.currentTarget)}
					>
						Optical (Fraunces)
					</button>
				</div>
			</div>

			<!-- SANS-SERIF -->
			<div class="tf-panel" id="tf-panel-sans">
				<div class="tf-meta">
					<span class="tf-tag sky">Clarity</span>
					<span class="tf-tag sky">Modern</span>
					<span class="tf-tag sky">Neutral</span>
					<span class="tf-tag sky">Versatile</span>
				</div>
				<div class="tf-specimen-wrap">
					<div
						class="tf-specimen"
						id="sans-specimen"
						style="font-family: 'DM Sans', sans-serif; font-weight: 700"
					>
						Aa Bb Gg Rr
					</div>
					<div class="tf-specimen-sub" style="font-family: 'DM Sans', sans-serif; font-weight: 400">
						The quick brown fox jumps over the lazy dog.
					</div>
					<div class="tf-ann" style="bottom: 10px; left: 40px">no serifs →</div>
					<div class="tf-ann" style="top: 10px; right: 16px">uniform stroke width</div>
				</div>
				<div class="tf-desc">
					Sans-serif typefaces omit the finishing strokes. The word <em>sans</em> is French for
					"without." Without those strokes, letterforms become cleaner, more geometric, and more
					neutral. This neutrality is their strength — they communicate
					<em>clarity, modernity, and function</em> without the cultural baggage of historical type. They
					dominate digital interfaces precisely because they read cleanly at any size.
				</div>
				<ul class="tf-use-list">
					<li>UI text, navigation labels, captions, and metadata at small sizes</li>
					<li>Modern, tech, or analytical brand identities</li>
					<li>Body text on screen — particularly below 16px</li>
					<li>Pairing as a body complement to a more characterful heading serif or display face</li>
				</ul>
				<div class="tf-edit-row">
					<label>Style:</label>
					<button
						class="tf-variant-btn active"
						onclick={(e) => actions.setSansVariant('geometric', e.currentTarget)}
					>
						Geometric (DM Sans)
					</button>
					<button
						class="tf-variant-btn"
						onclick={(e) => actions.setSansVariant('grotesk', e.currentTarget)}
					>
						Grotesk (Space Grotesk)
					</button>
				</div>
			</div>

			<!-- DISPLAY -->
			<div class="tf-panel" id="tf-panel-display">
				<div class="tf-meta">
					<span class="tf-tag rose">Impact</span>
					<span class="tf-tag rose">Personality</span>
					<span class="tf-tag rose">Large Sizes Only</span>
					<span class="tf-tag rose">Context-Specific</span>
				</div>
				<div class="tf-specimen-wrap">
					<div
						class="tf-specimen"
						id="display-specimen"
						style="
									font-family: 'Bebas Neue', sans-serif;
									font-weight: 400;
									letter-spacing: 0.05em;
								"
					>
						DESIGN YOUR WORLD
					</div>
					<div class="tf-specimen-sub" style="font-family: 'DM Sans', sans-serif; font-weight: 400">
						Display faces are designed to command attention. Use them for titles only.
					</div>
					<div class="tf-ann" style="top: 10px; right: 16px">extreme character</div>
				</div>
				<div class="tf-desc">
					Display typefaces are designed exclusively for large sizes — titles, headlines, posters,
					thumbnails. They sacrifice readability at small sizes in exchange for
					<em>extreme personality and visual impact</em>. A condensed display face like Bebas Neue
					can fill a thumbnail frame with authority in a single word. But use it in body text and it
					becomes illegible and exhausting.
				</div>
				<ul class="tf-use-list">
					<li>Thumbnail titles — the single most-viewed typographic element in your brand</li>
					<li>Channel intro cards and lower thirds</li>
					<li>Poster headings and event graphics</li>
					<li>Never use for body text, captions, or anything below ~24px</li>
				</ul>
				<div class="tf-edit-row">
					<label>Style:</label>
					<button
						class="tf-variant-btn active"
						onclick={(e) => actions.setDisplayVariant('condensed', e.currentTarget)}
					>
						Condensed (Bebas Neue)
					</button>
					<button
						class="tf-variant-btn"
						onclick={(e) => actions.setDisplayVariant('editorial', e.currentTarget)}
					>
						Editorial (Fraunces Black)
					</button>
					<button
						class="tf-variant-btn"
						onclick={(e) => actions.setDisplayVariant('syne', e.currentTarget)}
					>
						Geometric Bold (Syne)
					</button>
				</div>
			</div>

			<!-- MONOSPACE -->
			<div class="tf-panel" id="tf-panel-mono">
				<div class="tf-meta">
					<span class="tf-tag violet">Technical</span>
					<span class="tf-tag violet">Systematic</span>
					<span class="tf-tag violet">Analytical</span>
					<span class="tf-tag violet">Distinctive</span>
				</div>
				<div class="tf-specimen-wrap">
					<div
						class="tf-specimen"
						id="mono-specimen"
						style="
									font-family: 'IBM Plex Mono', monospace;
									font-weight: 600;
									font-size: clamp(24px, 3.5vw, 44px);
								"
					>
						Aa Bb Gg Rr
					</div>
					<div
						class="tf-specimen-sub"
						style="font-family: 'Space Mono', monospace; font-weight: 400"
					>
						Every character occupies the same width. Grids emerge.
					</div>
					<div class="tf-ann" style="bottom: 10px; left: 40px">equal width →</div>
					<div class="tf-ann" style="top: 10px; right: 16px">mechanical precision</div>
				</div>
				<div class="tf-desc">
					In monospace typefaces, every character occupies exactly the same horizontal space. This
					originated with typewriters and fixed-width terminals. The equal spacing creates
					<em>grid-like regularity and mechanical precision</em> that communicates systematic thinking,
					code, data, and analysis. In a brand context, it signals rigor and intelligence — a quieter
					form of authority than serif or display.
				</div>
				<ul class="tf-use-list">
					<li>Labels, metadata, timestamps, and secondary information</li>
					<li>
						Technical or analytical brand identities (this course uses IBM Plex Mono throughout)
					</li>
					<li>Code blocks and data presentation</li>
					<li>As a deliberate contrast element in a serif/monospace pairing</li>
				</ul>
				<div class="tf-edit-row">
					<label>Style:</label>
					<button
						class="tf-variant-btn active"
						onclick={(e) => actions.setMonoVariant('ibm', e.currentTarget)}
					>
						IBM Plex Mono
					</button>
					<button
						class="tf-variant-btn"
						onclick={(e) => actions.setMonoVariant('space', e.currentTarget)}
					>
						Space Mono
					</button>
				</div>
			</div>
		</div>
		<!-- end demo-box -->

		<table>
			<thead>
				<tr>
					<th>Category</th>
					<th>Personality</th>
					<th>Primary Use</th>
					<th>Avoid</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Serif</td>
					<td>Authority, tradition, editorial</td>
					<td>Display headings, brand logos, long-form print</td>
					<td>Small screen body text (&lt;14px)</td>
				</tr>
				<tr>
					<td>Sans-serif</td>
					<td>Modern, neutral, functional</td>
					<td>UI text, body copy, anything below 16px</td>
					<td>When personality/distinctiveness is needed</td>
				</tr>
				<tr>
					<td>Display</td>
					<td>High impact, distinctive, context-specific</td>
					<td>Titles, thumbnails, posters — 24px+</td>
					<td>Body text, small sizes, anything that needs to be read at length</td>
				</tr>
				<tr>
					<td>Monospace</td>
					<td>Technical, systematic, precise</td>
					<td>Labels, code, metadata, analytical brands</td>
					<td>Large blocks of prose; emotionally warm contexts</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ══════════════════════════════════
     SECTION 2: WEIGHT, SPACING, LEADING
══════════════════════════════════ -->
	<section id="spacing" class="section">
		<div class="section-header">
			<span class="section-num">03.02</span>
			<h2 class="section-title">Weight, Tracking, Kerning &amp; Leading</h2>
		</div>

		<p>
			Choosing a typeface is the first decision. The second is how you set it. Four properties
			control the texture and feel of type: <strong>weight</strong> (how heavy the strokes are),
			<strong>tracking</strong> (global letter-spacing across a block of text),
			<strong>kerning</strong> (spacing between specific letter pairs), and
			<strong>leading</strong> (line height). These are not stylistic flourishes — they directly determine
			readability, tone, and hierarchy.
		</p>

		<p>
			<em>Weight</em> is the most powerful hierarchy tool after size. Moving a word from 400 (regular)
			to 700 (bold) doubles its visual mass without changing its size. Used in a pairing — a bold heading
			above a light body — weight alone creates a clear primary/secondary distinction.
		</p>

		<p>
			<em>Tracking</em> is global letter-spacing applied uniformly across a word or block. Tight tracking
			feels urgent and compressed. Loose tracking feels spacious, editorial, and refined — particularly
			effective for uppercase labels and eyebrow text. The convention: track uppercase text out (loosen
			it), never in. Track lowercase out only for very small sizes. Never tighten tracked all-caps.
		</p>

		<p>
			<em>Leading</em> (line height) controls vertical breathing room in multi-line text. Too tight and
			lines visually merge; the eye cannot find its return path. Too loose and the block fragments into
			separate lines with no sense of paragraph unity. Body text conventionally sits between 1.4 and 1.7×
			the type size. Display headings are typically set tighter — 1.0 to 1.2×.
		</p>

		<div class="callout">
			<div class="callout-label">Kerning vs Tracking</div>
			Tracking adjusts spacing uniformly between all characters. Kerning adjusts the space between specific
			pairs — "AV", "To", "We" — where the letterform shapes create optically uneven gaps. Most font software
			handles kerning automatically using the font's built-in kerning tables. You only manually kern when
			something looks wrong at large display sizes.
		</div>

		<!-- DEMO: Spacing Lab -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Spacing &amp; Weight Lab</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Adjust the three spacing properties and observe how they change the texture, mood, and
					readability of both the heading and body text. Try finding the point where body text
					becomes difficult to scan.
				</p>

				<div class="spacing-preview" id="spacing-preview">
					<div>
						<div class="spacing-text" id="spacing-heading">Design is Thinking Made Visual</div>
						<div class="spacing-body" id="spacing-body">
							Type is the voice of your brand before a single word is read. The weight, spacing, and
							rhythm of letterforms communicate personality independent of meaning.
						</div>
					</div>
				</div>

				<div class="spacing-readability">
					<span class="readability-label">Readability</span>
					<div class="readability-bar-bg">
						<div class="readability-bar" id="readability-bar" style="width: 80%"></div>
					</div>
					<span class="readability-val" id="readability-val" style="color: var(--sage)">Good</span>
				</div>

				<div style="margin-top: 1.25rem">
					<div class="slider-row">
						<label for="sp-weight">Font Weight</label>
						<input
							type="range"
							id="sp-weight"
							min="300"
							max="900"
							step="100"
							value="700"
							oninput={() => {
								actions.updateSpacing();
							}}
						/>
						<span class="slider-val" id="sp-weight-val">700</span>
					</div>
					<div class="slider-row">
						<label for="sp-tracking">Tracking</label>
						<input
							type="range"
							id="sp-tracking"
							min="-0.08"
							max="0.4"
							step="0.01"
							value="0"
							oninput={() => {
								actions.updateSpacing();
							}}
						/>
						<span class="slider-val" id="sp-tracking-val">0em</span>
					</div>
					<div class="slider-row">
						<label for="sp-leading">Leading</label>
						<input
							type="range"
							id="sp-leading"
							min="0.85"
							max="2.4"
							step="0.05"
							value="1.15"
							oninput={() => {
								actions.updateSpacing();
							}}
						/>
						<span class="slider-val" id="sp-leading-val">1.15</span>
					</div>
					<div class="slider-row">
						<label for="sp-body-lead">Body Leading</label>
						<input
							type="range"
							id="sp-body-lead"
							min="0.9"
							max="2.5"
							step="0.05"
							value="1.7"
							oninput={() => {
								actions.updateSpacing();
							}}
						/>
						<span class="slider-val" id="sp-body-lead-val">1.70</span>
					</div>
				</div>

				<div style="margin-top: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap">
					<button class="btn" onclick={(e) => actions.setSpacingPreset('editorial')}
						>Editorial</button
					>
					<button class="btn" onclick={(e) => actions.setSpacingPreset('thumbnail')}
						>Thumbnail Title</button
					>
					<button class="btn" onclick={(e) => actions.setSpacingPreset('label')}
						>Uppercase Label</button
					>
					<button class="btn rose" onclick={(e) => actions.setSpacingPreset('broken')}
						>Broken</button
					>
					<button class="btn" onclick={(e) => actions.setSpacingPreset('reset')}>Reset</button>
				</div>
			</div>
		</div>

		<div class="callout green">
			<div class="callout-label">The Broken Preset</div>
			Try the "Broken" preset above. Every value is at an extreme. The result feels oppressive or unreadable
			even though the words haven't changed. This is the point: spacing properties communicate tone regardless
			of content. A perfectly-worded heading can be made unreadable by poor spacing alone.
		</div>
	</section>

	<!-- ══════════════════════════════════
     SECTION 3: PAIRING
══════════════════════════════════ -->
	<section id="pairing" class="section">
		<div class="section-header">
			<span class="section-num">03.03</span>
			<h2 class="section-title">Pairing Fonts Without Conflict</h2>
		</div>

		<p>
			A brand typically uses two typefaces: one for headings and display contexts, one for body and
			UI text. The challenge is making two different faces feel like they belong to the same system
			— they must be distinct enough to create hierarchy, but harmonious enough to feel intentional.
		</p>

		<p>
			The most reliable pairing principle:
			<em>contrast in category, harmony in personality.</em> A serif heading paired with a sans-serif
			body creates clear category contrast that reads as intentional and professional. A serif heading
			paired with a different serif body creates category sameness that requires careful weight and size
			management to avoid a muddy result.
		</p>

		<p>
			Personality harmony is harder to codify but easier to feel. Both fonts should feel like they
			could exist in the same room without the design looking confused. A condensed aggressive
			display face and a delicate thin-weight elegant serif would conflict even if their categories
			differ — the personalities are incompatible. A warm humanist sans and a warm text serif,
			conversely, feel cohesive.
		</p>

		<table>
			<thead>
				<tr>
					<th>Pairing Pattern</th>
					<th>Reliability</th>
					<th>Notes</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Serif heading + Sans-serif body</td>
					<td style="color: var(--sage)">★★★★★</td>
					<td>The classic combination. Works across almost every context.</td>
				</tr>
				<tr>
					<td>Display heading + Sans-serif body</td>
					<td style="color: var(--sage)">★★★★☆</td>
					<td>High impact. Requires the display font to match brand personality precisely.</td>
				</tr>
				<tr>
					<td>Sans-serif heading + Monospace body</td>
					<td style="color: var(--amber)">★★★☆☆</td>
					<td>Works well for technical/analytical brands. Risk of coldness.</td>
				</tr>
				<tr>
					<td>Serif heading + Serif body</td>
					<td style="color: var(--amber)">★★★☆☆</td>
					<td>Requires strong weight contrast between the two. Easy to make muddy.</td>
				</tr>
				<tr>
					<td>Two display fonts</td>
					<td style="color: var(--rose)">★★☆☆☆</td>
					<td>Almost always conflict. Each display face is too distinctive to share space.</td>
				</tr>
				<tr>
					<td>Same font, weight contrast only</td>
					<td style="color: var(--sage)">★★★★☆</td>
					<td>
						Underused and often elegant. One family, different weights creates clean hierarchy.
					</td>
				</tr>
			</tbody>
		</table>

		<!-- DEMO: Font Pairing Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Font Pairing Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Choose a heading and body font. The preview shows them in a channel identity context. The
					harmony meter scores category contrast, personality match, and weight differentiation.
				</p>

				<div class="two-col" style="margin-bottom: 1.25rem; gap: 1rem">
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
							Heading / Display Font
						</div>
						<select
							id="pair-heading"
							onchange={() => {
								actions.updatePairing();
							}}
						>
							<option value="playfair">Playfair Display (Serif)</option>
							<option value="fraunces">Fraunces (Optical Serif)</option>
							<option value="bebas">Bebas Neue (Display)</option>
							<option value="syne" selected>Syne (Geometric Bold)</option>
							<option value="crimson">Crimson Pro (Text Serif)</option>
							<option value="dmsans-head">DM Sans Bold (Sans)</option>
						</select>
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
							Body / Support Font
						</div>
						<select
							id="pair-body"
							onchange={() => {
								actions.updatePairing();
							}}
						>
							<option value="dmsans" selected>DM Sans (Geometric Sans)</option>
							<option value="spacegrotesk">Space Grotesk (Sans)</option>
							<option value="ibmplexmono">IBM Plex Mono (Monospace)</option>
							<option value="crimson-body">Crimson Pro (Serif)</option>
							<option value="playfair-body">Playfair Display (Serif)</option>
							<option value="spacemono">Space Mono (Monospace)</option>
						</select>
					</div>
				</div>

				<div class="pair-preview" id="pair-preview">
					<div class="pair-eyebrow" id="pair-eyebrow" style="color: var(--amber)">
						Visual Design Course
					</div>
					<div class="pair-headline" id="pair-headline">How to Design<br />with Intention</div>
					<div class="pair-body-text" id="pair-body-text">
						This channel explores the principles behind great visual communication — from typography
						and color to layout and motion. New episodes every week.
					</div>
					<div
						class="pair-cta"
						id="pair-cta"
						style="color: var(--amber); border-color: var(--amber)"
					>
						Subscribe →
					</div>
				</div>

				<div class="harmony-wrap" id="harmony-wrap">
					<div class="harmony-row">
						<span class="harmony-label">Category contrast</span>
						<div class="harmony-bar-bg">
							<div class="harmony-bar" id="hbar-cat" style="width: 0%"></div>
						</div>
						<span class="harmony-score" id="hscore-cat">—</span>
					</div>
					<div class="harmony-row">
						<span class="harmony-label">Weight differentiation</span>
						<div class="harmony-bar-bg">
							<div class="harmony-bar" id="hbar-wt" style="width: 0%"></div>
						</div>
						<span class="harmony-score" id="hscore-wt">—</span>
					</div>
					<div class="harmony-row">
						<span class="harmony-label">Personality match</span>
						<div class="harmony-bar-bg">
							<div class="harmony-bar" id="hbar-per" style="width: 0%"></div>
						</div>
						<span class="harmony-score" id="hscore-per">—</span>
					</div>
					<div class="harmony-verdict" id="harmony-verdict"></div>
				</div>
			</div>
		</div>

		<div class="callout violet">
			<div class="callout-label">The Single Font Rule</div>
			When in doubt, use one typeface family with strong weight contrast: a Black or ExtraBold heading
			and a Regular or Light body from the same family. The result is almost always cleaner than a poorly-considered
			two-font pairing.
		</div>
	</section>

	<!-- ══════════════════════════════════
     SECTION 4: APPLIED TYPOGRAPHY
══════════════════════════════════ -->
	<section id="applied" class="section">
		<div class="section-header">
			<span class="section-num">03.04</span>
			<h2 class="section-title">Applied: Thumbnails, Title Cards &amp; Web</h2>
		</div>

		<p>
			The rules shift depending on the context. Typography that works in a website body column fails
			in a thumbnail. Typography that works in a thumbnail becomes aggressive on a website. You need
			separate type strategies for each surface, united by the same underlying typeface system.
		</p>

		<p>
			<strong>Thumbnails</strong> are the most demanding typographic context. The text must be legible
			at 168×94 pixels — roughly the size of a postage stamp. This means: one font, maximum weight, maximum
			contrast against the background, minimal tracking, very few words. The title of your video is often
			the secondary element — the face or the visual hook comes first. Two to five words is the hard limit.
		</p>

		<p>
			<strong>Title cards</strong> (the animated opener) can use more text because the viewer is watching
			at full size and has opted in. But typography for motion must account for reading speed — text that
			stays on screen for less than 1.5 seconds should have fewer than five words. Text that stays longer
			than three seconds must be worth reading.
		</p>

		<p>
			<strong>Website layouts</strong> tolerate — and often require — more typographic complexity. A three-tier
			system is common: display or heavy sans heading (36–60px), medium weight subheading (20–24px), and
			regular weight body (15–17px). Navigation and labels use uppercase tracking at 11–13px. Each tier
			must be visually distinct from the one above it — the difference between adjacent tiers should feel
			obvious, not marginal.
		</p>

		<!-- DEMO: Thumbnail Type Lab -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Thumbnail Typography Lab</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Build a thumbnail title treatment using your font choices. Observe legibility at full size
					— then use the scale button to preview at YouTube thumbnail size.
				</p>

				<div class="thumb-outer">
					<canvas
						id="thumb-canvas"
						width="560"
						height="315"
						aria-label="Thumb Canvas Demonstration"
						role="region"
						tabindex="0"
					></canvas>
				</div>

				<div style="display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap">
					<button class="btn" id="thumb-scale-btn" onclick={(e) => actions.toggleThumbScale()}>
						Preview at Thumb Size
					</button>
					<button class="btn sage" onclick={(e) => actions.randomiseThumb()}
						>Randomise Background</button
					>
				</div>

				<div class="thumb-controls">
					<div class="ctrl-group">
						<div class="ctrl-group-label">Title Font</div>
						<select
							id="thumb-font"
							onchange={() => {
								actions.drawThumb();
							}}
						>
							<option value="Bebas Neue">Bebas Neue (Condensed)</option>
							<option value="Syne" selected>Syne (Geometric)</option>
							<option value="Playfair Display">Playfair Display (Serif)</option>
							<option value="Fraunces">Fraunces (Optical)</option>
							<option value="DM Sans">DM Sans (Sans)</option>
							<option value="IBM Plex Mono">IBM Plex Mono (Mono)</option>
						</select>
						<div class="slider-row" style="margin-top: 0.5rem">
							<label style="min-width: 60px; font-size: 11px">Size</label>
							<input
								type="range"
								id="thumb-size"
								min="28"
								max="80"
								value="56"
								oninput={() => {
									actions.drawThumb();
								}}
							/>
							<span class="slider-val" id="thumb-size-val">56</span>
						</div>
						<div class="slider-row">
							<label style="min-width: 60px; font-size: 11px">Weight</label>
							<input
								type="range"
								id="thumb-weight"
								min="300"
								max="900"
								step="100"
								value="800"
								oninput={() => {
									actions.drawThumb();
								}}
							/>
							<span class="slider-val" id="thumb-weight-val">800</span>
						</div>
					</div>
					<div class="ctrl-group">
						<div class="ctrl-group-label">Title Text</div>
						<input
							type="text"
							id="thumb-text1"
							value="DESIGN"
							maxlength="14"
							style="
										width: 100%;
										background: var(--code-bg);
										border: 1px solid var(--border);
										color: #fff;
										padding: 6px 8px;
										font-family: 'IBM Plex Mono', monospace;
										font-size: 13px;
										outline: none;
										margin-bottom: 0.4rem;
									"
							oninput={() => {
								actions.drawThumb();
							}}
						/>
						<input
							type="text"
							id="thumb-text2"
							value="FROM SCRATCH"
							maxlength="18"
							style="
										width: 100%;
										background: var(--code-bg);
										border: 1px solid var(--border);
										color: var(--muted);
										padding: 6px 8px;
										font-family: 'IBM Plex Mono', monospace;
										font-size: 13px;
										outline: none;
									"
							oninput={() => {
								actions.drawThumb();
							}}
						/>
						<div class="slider-row" style="margin-top: 0.5rem">
							<label style="min-width: 60px; font-size: 11px">Tracking</label>
							<input
								type="range"
								id="thumb-tracking"
								min="-0.02"
								max="0.25"
								step="0.01"
								value="0.02"
								oninput={() => {
									actions.drawThumb();
								}}
							/>
							<span class="slider-val" id="thumb-tracking-val">0.02</span>
						</div>
					</div>
				</div>
				<div class="thumb-note" id="thumb-note">
					Adjust the controls to build your thumbnail typography.
				</div>
			</div>
		</div>
	</section>

	<!-- ══════════════════════════════════
     SECTION 5: PRACTICAL WORK
══════════════════════════════════ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">03.05</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout green">
			<div class="callout-label">Exercise 1 — Title Card Design</div>
			Design a title card for one of your videos (or a hypothetical video) using only typography — no
			photography, no illustration. Constraints:<br /><br />
			· One heading typeface, one body or label typeface only<br />
			· Channel name, video title, and episode number must all read at a glance<br />
			· The visual weight difference between each tier must be obvious<br />
			· Use tight tracking on uppercase labels, natural tracking on the title<br /><br />
			The challenge: make it feel like it belongs to your channel, not any channel.
		</div>

		<div class="callout info">
			<div class="callout-label">Exercise 2 — Font Pairing for Your Brand</div>
			Identify two typefaces you want to use for your channel. Research their full families — do they
			have light, regular, bold, and black weights? Do they have italics?<br /><br />
			Set them in the following contexts and note which breaks first:<br />
			· 52px heading on a dark background (thumbnail context)<br />
			· 14px body paragraph, 200 words (website context)<br />
			· 10px uppercase label (metadata/caption context)<br /><br />
			A robust brand font must survive all three. Most display faces fail the third test — and that's
			fine if you have a separate UI font.
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 03 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit · Select the best answer.</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> A creator wants their channel to communicate analytical rigor and
				systematic thinking. Which typeface category is most aligned with this personality?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Display — high-impact and distinctive
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Serif — tradition and authority
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Monospace — mechanical precision and systematic structure
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
					>D. Sans-serif — clean and modern</button
				>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> Uppercase text at a small size (11px) feels optically too tight.
				What is the correct typographic response?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Increase the font weight to compensate for the optical crowding
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Increase tracking — add letter-spacing to loosen the text and improve legibility
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Switch to a display typeface which is designed for all sizes
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Increase the font size until the crowding resolves itself
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> What makes the pairing of "serif heading + sans-serif body" so
				reliably effective?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. It creates category contrast — the two fonts are clearly distinct types of letter,
					making hierarchy immediately readable without relying purely on size or weight
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Serifs are always better at large sizes, and sans-serifs are always better at small
					sizes
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The pairing has existed the longest, so viewers are trained to expect it
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Serifs and sans-serifs have opposite personalities that create visual tension
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> A thumbnail title is set in a light-weight serif at 20px with generous
				tracking. Why is this likely to fail?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Serif fonts are not permitted in thumbnails — only sans-serifs and display faces work
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Generous tracking is always wrong — it should always be tightened
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Light-weight fonts are the correct weight for thumbnails to avoid visual congestion
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. At thumbnail size, light-weight serifs lose legibility — thin strokes disappear and
					generous tracking spreads letters too far apart to read as words at a glance
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> What is the difference between kerning and tracking?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Tracking adjusts vertical spacing; kerning adjusts horizontal spacing
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Kerning applies to paragraphs; tracking applies to individual letters
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Tracking adjusts spacing uniformly across all characters; kerning adjusts the space
					between specific pairs of letters where optical gaps appear
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. They are synonyms — different software uses different terminology for the same property
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
		<div class="assessment-header">Module Assessment — Font Pair Audit</div>
		<div class="assessment-sub">
			Identify the typographic problem in each pairing below and select the correct diagnosis.
		</div>

		<div class="pair-audit">
			<!-- AUDIT 1 -->
			<div class="audit-item">
				<div class="audit-item-label">Pairing 01 — Identify the Problem</div>
				<div
					class="audit-specimen"
					style="font-family: 'Bebas Neue', sans-serif; letter-spacing: 0.05em; color: #fff"
				>
					DESIGN THINKING
				</div>
				<div
					class="audit-sub"
					style="
								font-family: 'Bebas Neue', sans-serif;
								font-size: 14px;
								letter-spacing: 0.03em;
								color: var(--text);
							"
				>
					This week we explore how systematic approaches to visual communication can transform the
					way you build creative work. Each episode covers a foundational principle.
				</div>
				<div class="audit-options">
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 0, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 0, 1);
							}
						}}
					>
						A. The heading is too large relative to the body text
					</div>
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 1, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 1, 1);
							}
						}}
					>
						B. Both heading and body use the same display font — Bebas Neue is illegible at body
						text sizes and creates no typographic hierarchy
					</div>
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 2, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 2, 1);
							}
						}}
					>
						C. The tracking on the heading is too tight
					</div>
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 3, 1)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 3, 1);
							}
						}}
					>
						D. Display fonts can only be used once per composition
					</div>
				</div>
				<div class="audit-feedback" id="af-1"></div>
			</div>

			<!-- AUDIT 2 -->
			<div class="audit-item">
				<div class="audit-item-label">Pairing 02 — Identify the Problem</div>
				<div
					class="audit-specimen"
					style="font-family: 'Playfair Display', serif; font-weight: 400; color: #fff"
				>
					How to Build a Brand
				</div>
				<div
					class="audit-sub"
					style="
								font-family: 'Crimson Pro', serif;
								font-weight: 400;
								font-size: 14px;
								color: var(--text);
							"
				>
					Building a consistent visual identity requires understanding the principles behind color,
					typography, and composition — and knowing how to apply them systematically across every
					surface your audience encounters.
				</div>
				<div class="audit-options">
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 0, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 0, 0);
							}
						}}
					>
						A. Both fonts are serifs at similar weights — the heading doesn't dominate clearly
						enough, and the pairing reads as muddy without stronger weight or size contrast
					</div>
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 1, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 1, 0);
							}
						}}
					>
						B. Two serif fonts can never be used together — always pair with a sans-serif body
					</div>
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 2, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 2, 0);
							}
						}}
					>
						C. Playfair Display is a display font and cannot be used at heading size — it is too
						decorative
					</div>
					<div
						class="audit-opt"
						onclick={(e) => actions.handleAudit(e.currentTarget, 3, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handleAudit(e.currentTarget, 3, 0);
							}
						}}
					>
						D. Crimson Pro is too wide for body text — a condensed font would work better
					</div>
				</div>
				<div class="audit-feedback" id="af-2"></div>
			</div>
		</div>
	</section>

	<!-- NAV -->
	<div class="nav-links">
		<a href="gd-module-02.html" class="prev-link">← Module 02: Composition</a>
		<a href="gd-module-04.html" class="next-module" style="flex: 1; max-width: 420px">
			<div>
				<div class="next-label">Next — Module 04</div>
				<div class="next-title">Color Theory &amp; Emotional Impact</div>
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
		max-width: 600px;
	}
	.module-title span {
		color: var(--amber);
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
		color: var(--amber);
		border-color: var(--amber);
	}

	/* OBJECTIVES */
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

	/* CALLOUTS */
	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--amber);
		background: color-mix(in srgb, var(--amber) 5%, var(--surface));
		font-size: 13px;
	}
	.callout.green {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--surface));
	}
	.callout.warn {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 5%, var(--surface));
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
		color: var(--amber);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	.callout.green .callout-label {
		color: var(--sage);
	}
	.callout.warn .callout-label {
		color: var(--rose);
	}
	:global(.callout.sky) .callout-label {
		color: var(--sky);
	}
	.callout.violet .callout-label {
		color: var(--violet);
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
	.demo-badge {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	.demo-badge.interactive {
		color: var(--amber);
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	:global(.demo-badge.animated) {
		color: var(--sky);
		border-color: var(--sky);
		background: color-mix(in srgb, var(--sky) 10%, transparent);
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
	:global(.btn.sage:hover) {
		border-color: var(--sage);
		color: var(--sage);
	}
	:global(.btn.sage.active) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
	}

	select {
		background: var(--raised);
		border: 1px solid var(--border2);
		color: var(--text);
		padding: 5px 10px;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 12px;
		outline: none;
		cursor: pointer;
	}
	select:focus {
		border-color: var(--amber);
	}

	:global(.slider-row) {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 0.6rem 0;
	}
	:global(.slider-row) label {
		font-size: 12px;
		min-width: 100px;
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
		background: var(--amber);
		cursor: pointer;
	}
	:global(.slider-val) {
		font-size: 12px;
		color: var(--amber);
		min-width: 48px;
		text-align: right;
		font-weight: 600;
	}

	/* LAYOUT */
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

	/* TABLE */
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

	/* PROGRESS */
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

	/* DIVIDER */
	.divider {
		border: none;
		border-top: 1px solid var(--border);
		margin: 3rem 0;
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
		margin-bottom: 1.5rem;
	}

	/* NAV */
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

	/* ══════════════════════════════════════
   DEMO-SPECIFIC
══════════════════════════════════════ */

	/* --- TYPEFACE EXPLORER --- */
	.tf-tabs {
		display: flex;
		gap: 0;
		border-bottom: 1px solid var(--border);
		margin-bottom: 0;
	}
	.tf-tab {
		padding: 0.6rem 1.25rem;
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--muted);
		cursor: pointer;
		border-bottom: 2px solid transparent;
		transition: all 0.15s;
		user-select: none;
	}
	.tf-tab:hover {
		color: var(--text);
	}
	.tf-tab.active {
		color: var(--amber);
		border-bottom-color: var(--amber);
	}
	.tf-panel {
		display: none;
		padding: 1.5rem;
	}
	.tf-panel.active {
		display: block;
	}
	.tf-specimen-wrap {
		position: relative;
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 2rem 2rem 1.5rem;
		margin-bottom: 1.25rem;
		overflow: hidden;
	}
	.tf-specimen {
		font-size: clamp(36px, 6vw, 64px);
		line-height: 1.1;
		color: #fff;
		transition: all 0.3s;
	}
	.tf-specimen-sub {
		font-size: clamp(14px, 2vw, 18px);
		color: var(--muted);
		margin-top: 0.75rem;
		line-height: 1.5;
		transition: all 0.3s;
	}
	.tf-anatomy {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		pointer-events: none;
	}
	.tf-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	.tf-tag {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
		letter-spacing: 0.1em;
	}
	.tf-tag.amber {
		color: var(--amber);
		border-color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	.tf-tag.violet {
		color: var(--violet);
		border-color: var(--violet);
		background: color-mix(in srgb, var(--violet) 10%, transparent);
	}
	.tf-tag.sky {
		color: var(--sky);
		border-color: var(--sky);
		background: color-mix(in srgb, var(--sky) 10%, transparent);
	}
	.tf-tag.sage {
		color: var(--sage);
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
	}
	.tf-desc {
		font-size: 12px;
		color: var(--muted);
		line-height: 1.7;
		margin-bottom: 1rem;
	}
	.tf-use-list {
		font-size: 11px;
		color: var(--text);
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	.tf-use-list li {
		list-style: none;
		padding-left: 1rem;
		position: relative;
	}
	.tf-use-list li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--amber);
		font-size: 10px;
	}
	.tf-edit-row {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		align-items: center;
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid var(--border);
	}
	.tf-edit-row label {
		font-size: 11px;
		color: var(--muted);
	}
	.tf-variant-btn {
		padding: 3px 10px;
		font-size: 11px;
		font-family: 'IBM Plex Mono', monospace;
		border: 1px solid var(--border);
		background: transparent;
		color: var(--muted);
		cursor: pointer;
		transition: all 0.15s;
	}
	.tf-variant-btn:hover {
		border-color: var(--amber);
		color: var(--amber);
	}
	.tf-variant-btn.active {
		border-color: var(--amber);
		color: var(--amber);
		background: color-mix(in srgb, var(--amber) 10%, transparent);
	}
	/* Anatomy markers */
	.tf-ann {
		position: absolute;
		font-size: 9px;
		font-family: 'IBM Plex Mono', monospace;
		color: rgba(245, 166, 35, 0.6);
		letter-spacing: 0.1em;
		text-transform: uppercase;
		pointer-events: none;
	}
	.tf-ann-line {
		position: absolute;
		background: rgba(245, 166, 35, 0.25);
		pointer-events: none;
	}

	/* --- SPACING LAB --- */
	.spacing-preview {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 2rem 2.5rem;
		min-height: 180px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
	}
	.spacing-text {
		color: #fff;
		font-size: 32px;
		font-weight: 700;
		font-family: 'Playfair Display', serif;
		line-height: 1.4;
		text-align: center;
		transition: all 0.25s;
		word-break: break-word;
	}
	.spacing-body {
		color: var(--text);
		font-size: 14px;
		font-family: 'DM Sans', sans-serif;
		margin-top: 1rem;
		text-align: left;
		max-width: 400px;
		transition: all 0.25s;
	}
	.spacing-readability {
		margin-top: 0.75rem;
		font-size: 11px;
		padding: 6px 10px;
		border: 1px solid var(--border);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.readability-bar-bg {
		flex: 1;
		height: 3px;
		background: var(--border2);
		margin: 0 1rem;
	}
	.readability-bar {
		height: 100%;
		background: var(--sage);
		transition: width 0.3s;
	}
	.readability-label {
		font-size: 10px;
		color: var(--muted);
		white-space: nowrap;
	}
	.readability-val {
		font-size: 10px;
		font-weight: 600;
		white-space: nowrap;
	}

	/* --- FONT PAIRING --- */
	.pair-preview {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 2rem 2.5rem;
		min-height: 220px;
	}
	.pair-eyebrow {
		font-size: 10px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		margin-bottom: 0.5rem;
		transition: all 0.2s;
	}
	.pair-headline {
		font-size: clamp(28px, 4vw, 42px);
		line-height: 1.1;
		color: #fff;
		margin-bottom: 0.75rem;
		transition: all 0.2s;
	}
	.pair-body-text {
		font-size: 15px;
		line-height: 1.8;
		color: var(--text);
		transition: all 0.2s;
		max-width: 480px;
	}
	.pair-cta {
		display: inline-block;
		margin-top: 1.25rem;
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		padding: 6px 16px;
		border: 1px solid;
		transition: all 0.2s;
	}
	.harmony-wrap {
		margin-top: 1.25rem;
		padding: 1rem;
		background: var(--raised);
		border: 1px solid var(--border);
	}
	.harmony-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0.3rem 0;
	}
	.harmony-label {
		font-size: 11px;
		color: var(--muted);
		min-width: 130px;
	}
	.harmony-bar-bg {
		flex: 1;
		height: 3px;
		background: var(--border2);
	}
	.harmony-bar {
		height: 100%;
		transition:
			width 0.35s,
			background 0.35s;
	}
	.harmony-score {
		font-size: 11px;
		font-weight: 600;
		min-width: 36px;
		text-align: right;
	}
	.harmony-verdict {
		margin-top: 0.75rem;
		font-size: 12px;
		padding: 0.5rem 0.75rem;
		border-left: 2px solid;
		transition: all 0.3s;
	}

	/* --- THUMBNAIL TYPE LAB --- */
	.thumb-outer {
		position: relative;
		background: var(--code-bg);
		border: 1px solid var(--border);
		aspect-ratio: 16/9;
		max-width: 560px;
		overflow: hidden;
	}
	canvas#thumb-canvas {
		display: block;
		width: 100%;
		height: 100%;
	}
	.thumb-controls {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-top: 1rem;
	}
	@media (max-width: 560px) {
		.thumb-controls {
			grid-template-columns: 1fr;
		}
	}
	.ctrl-group {
		padding: 0.75rem;
		border: 1px solid var(--border);
		background: var(--raised);
	}
	.ctrl-group-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.6rem;
	}
	.thumb-note {
		margin-top: 0.75rem;
		font-size: 12px;
		color: var(--muted);
		min-height: 1.8em;
		line-height: 1.6;
	}

	/* Assessment: pair audit */
	.pair-audit {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-top: 1.5rem;
	}
	.audit-item {
		padding: 1rem;
		border: 1px solid var(--border);
		background: var(--code-bg);
	}
	.audit-item-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.75rem;
	}
	.audit-specimen {
		font-size: 26px;
		line-height: 1.15;
		margin-bottom: 0.5rem;
	}
	.audit-sub {
		font-size: 13px;
		line-height: 1.6;
		margin-bottom: 0.75rem;
	}
	.audit-options {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
	.audit-opt {
		padding: 0.5rem 0.85rem;
		border: 1px solid var(--border);
		font-size: 12px;
		cursor: pointer;
		font-family: 'IBM Plex Mono', monospace;
		transition: all 0.15s;
		user-select: none;
	}
	.audit-opt:hover {
		border-color: var(--border2);
		background: var(--raised);
	}
	.audit-opt.correct {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
		color: var(--sage);
		pointer-events: none;
	}
	.audit-opt.wrong {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
		color: var(--rose);
		pointer-events: none;
	}
	.audit-opt.disabled {
		pointer-events: none;
	}
	.audit-feedback {
		font-size: 12px;
		margin-top: 0.5rem;
		color: var(--muted);
		min-height: 1.2em;
	}
	.audit-feedback.ok {
		color: var(--sage);
	}
	.audit-feedback.bad {
		color: var(--rose);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
