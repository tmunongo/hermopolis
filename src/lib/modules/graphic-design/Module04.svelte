<script lang="ts">
	/* eslint-disable @typescript-eslint/no-unused-vars */
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
		/* ════════════════════════════════════════
   READING PROGRESS
════════════════════════════════════════ */
		_addWinListener('scroll', () => {
			const el = document.documentElement;
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width =
					(el.scrollTop / Math.max(1, el.scrollHeight - el.clientHeight)) * 100 + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		/* ════════════════════════════════════════
   UTILITIES
════════════════════════════════════════ */
		function hslToRgb(h, s, l) {
			s /= 100;
			l /= 100;
			const k = (n) => (n + h / 30) % 12;
			const a = s * Math.min(l, 1 - l);
			const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
			return [Math.round(f(0) * 255), Math.round(f(8) * 255), Math.round(f(4) * 255)];
		}

		function hslToHex(h, s, l) {
			const [r, g, b] = hslToRgb(h, s, l);
			return '#' + [r, g, b].map((x) => x.toString(16).padStart(2, '0')).join('');
		}

		function getLuminance(r, g, b) {
			const lin = (v) => {
				v /= 255;
				return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
			};
			return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
		}

		function getContrastRatio(h1, s1, l1, h2, s2, l2) {
			const [r1, g1, b1] = hslToRgb(h1, s1, l1);
			const [r2, g2, b2] = hslToRgb(h2, s2, l2);
			const lum1 = getLuminance(r1, g1, b1);
			const lum2 = getLuminance(r2, g2, b2);
			const lighter = Math.max(lum1, lum2),
				darker = Math.min(lum1, lum2);
			return (lighter + 0.05) / (darker + 0.05);
		}

		function contrastColor(h, s, l) {
			const [r, g, b] = hslToRgb(h, s, l);
			return getLuminance(r, g, b) > 0.35 ? '#111' : '#fff';
		}

		/* ════════════════════════════════════════
   HSL EXPLORER
════════════════════════════════════════ */
		function buildHueStrip(elId, fixedS, fixedL) {
			const el = document.getElementById(elId);
			const stops = Array.from(
				{ length: 13 },
				(_, i) => `hsl(${i * 30},${fixedS}%,${fixedL}%)`
			).join(',');
			el.style.background = `linear-gradient(to right, ${stops})`;
		}

		function updateHSL() {
			const h = parseInt(document.getElementById('hsl-h').value);
			const s = parseInt(document.getElementById('hsl-s').value);
			const l = parseInt(document.getElementById('hsl-l').value);

			document.getElementById('hsl-h-val').textContent = h + '°';
			document.getElementById('hsl-s-val').textContent = s + '%';
			document.getElementById('hsl-l-val').textContent = l + '%';

			const hex = hslToHex(h, s, l);
			const swatch = document.getElementById('hsl-swatch');
			swatch.style.background = `hsl(${h},${s}%,${l}%)`;

			const textC = contrastColor(h, s, l);
			document.getElementById('hsl-hex').style.color = textC;
			document.getElementById('hsl-sub').style.color = textC;
			document.getElementById('hsl-hex').textContent = hex.toUpperCase();
			document.getElementById('hsl-sub').textContent = `HSL(${h}°, ${s}%, ${l}%)`;

			// Strips
			buildHueStrip('hue-strip', s, l);
			// Saturation strip — hue fixed, L fixed, S 0→100
			const satStops = [0, 20, 40, 60, 80, 100].map((sv) => `hsl(${h},${sv}%,${l}%)`).join(',');
			document.getElementById('sat-strip').style.background =
				`linear-gradient(to right,${satStops})`;
			// Lightness strip — hue fixed, S fixed, L 0→100
			const litStops = [0, 20, 40, 60, 80, 100].map((lv) => `hsl(${h},${s}%,${lv}%)`).join(',');
			document.getElementById('lit-strip').style.background =
				`linear-gradient(to right,${litStops})`;

			// Meaning
			const meaning = document.getElementById('hsl-meaning');
			if (s < 8) {
				meaning.style.color = 'var(--amber)';
				meaning.textContent = `Saturation is near 0 — this is essentially a neutral grey regardless of the hue value. Changing hue now has no visible effect.`;
			} else if (l < 8) {
				meaning.style.color = 'var(--muted)';
				meaning.textContent = `Lightness is near 0 — the color is collapsing toward black. At this lightness, hue and saturation are barely visible.`;
			} else if (l > 92) {
				meaning.style.color = 'var(--muted)';
				meaning.textContent = `Lightness is near 100% — the color is collapsing toward white. Hue and saturation are lost.`;
			} else if (s > 88) {
				meaning.style.color = 'var(--rose)';
				meaning.textContent = `Saturation above 88% — vivid and intense. Suitable as a small accent element only. Large areas at this saturation cause visual fatigue.`;
			} else {
				meaning.style.color = 'var(--sage)';
				meaning.textContent = `H ${h}° · S ${s}% · L ${l}% — ${s < 40 ? 'Low saturation: muted, neutral, restful.' : s < 70 ? 'Moderate saturation: professional, clear.' : 'High saturation: energetic, vivid.'} ${l < 30 ? ' Dark — suitable for background or shadow tones.' : l > 70 ? ' Light — suitable for text on dark surfaces.' : ' Mid-range lightness — ideal for accent colors.'}`;
			}
		}

		function setHSLPreset(h, s, l) {
			document.getElementById('hsl-h').value = h;
			document.getElementById('hsl-s').value = s;
			document.getElementById('hsl-l').value = l;
			updateHSL();
		}

		updateHSL();

		/* ════════════════════════════════════════
   COLOR WHEEL
════════════════════════════════════════ */
		const wheelCanvas = document.getElementById('wheel-canvas');
		const wCtx = wheelCanvas.getContext('2d');
		const WS = wheelCanvas.width;
		const WCX = WS / 2,
			WCY = WS / 2,
			OUTER_R = WS / 2 - 4,
			INNER_R = WS / 2 - 38;

		let baseHue = 198;
		let harmonyType = 'complementary';

		function drawWheel() {
			wCtx.clearRect(0, 0, WS, WS);
			const steps = 360;
			for (let i = 0; i < steps; i++) {
				const angle1 = (i / steps) * Math.PI * 2 - Math.PI / 2;
				const angle2 = ((i + 1) / steps) * Math.PI * 2 - Math.PI / 2;
				wCtx.beginPath();
				wCtx.moveTo(WCX, WCY);
				wCtx.arc(WCX, WCY, OUTER_R, angle1, angle2);
				wCtx.closePath();
				wCtx.fillStyle = `hsl(${i}, 80%, 55%)`;
				wCtx.fill();
			}
			// White center hole
			wCtx.beginPath();
			wCtx.arc(WCX, WCY, INNER_R, 0, Math.PI * 2);
			wCtx.fillStyle = '#0d1117';
			wCtx.fill();

			// Draw harmony markers
			const hues = getHarmonyHues(baseHue, harmonyType);
			hues.forEach((hue, i) => {
				const angle = (hue / 360) * Math.PI * 2 - Math.PI / 2;
				const mx = WCX + Math.cos(angle) * (OUTER_R - 18);
				const my = WCY + Math.sin(angle) * (OUTER_R - 18);
				const isBase = i === 0;
				wCtx.beginPath();
				wCtx.arc(mx, my, isBase ? 10 : 7, 0, Math.PI * 2);
				wCtx.fillStyle = `hsl(${hue}, 80%, 55%)`;
				wCtx.fill();
				wCtx.strokeStyle = '#fff';
				wCtx.lineWidth = isBase ? 2.5 : 1.5;
				wCtx.stroke();

				// Line from center to marker
				if (!isBase) {
					wCtx.beginPath();
					wCtx.moveTo(WCX, WCY);
					wCtx.lineTo(mx, my);
					wCtx.strokeStyle = `rgba(255,255,255,0.18)`;
					wCtx.lineWidth = 1;
					wCtx.setLineDash([3, 3]);
					wCtx.stroke();
					wCtx.setLineDash([]);
				}
			});

			updateHarmonySwatches();
		}

		function getHarmonyHues(base, type) {
			switch (type) {
				case 'complementary':
					return [base, (base + 180) % 360];
				case 'analogous':
					return [base, (base + 30) % 360, (base - 30 + 360) % 360];
				case 'triadic':
					return [base, (base + 120) % 360, (base + 240) % 360];
				case 'split':
					return [base, (base + 150) % 360, (base + 210) % 360];
				case 'monochromatic':
					return [base, base, base, base, base]; // handled specially
				default:
					return [base];
			}
		}

		const HARMONY_CONFIGS = {
			complementary: {
				desc: 'Complementary — maximum contrast. The two colors are exact opposites on the wheel. Each makes the other appear more vivid. Use the dominant color for 80–90% of the palette; the complement only as an accent.',
				balance:
					'· 80% dominant color at varied lightness\n· 20% complement as focal accent only\n· Avoid equal areas of both — creates visual vibration'
			},
			analogous: {
				desc: 'Analogous — natural harmony. Three adjacent hues that share color DNA. Feels cohesive, restful, and organic. The risk: without value contrast, the colors blur together.',
				balance:
					'· Use value (lightness) contrast to differentiate within the palette\n· One hue should clearly dominate\n· Add a complementary accent if the palette feels too passive'
			},
			triadic: {
				desc: 'Triadic — vibrant balance. Three evenly-spaced hues, each 120° apart. Dynamic and energetic while retaining visual balance. Requires careful dominance management.',
				balance:
					'· 60% dominant · 30% secondary · 10% accent\n· Desaturate two colors to let one lead\n· Often works best when one hue is near-neutral'
			},
			split: {
				desc: 'Split-complementary — softer tension. Pairs the base with two colors flanking its complement. Retains contrast without the harshness of a direct complementary pairing.',
				balance:
					'· The base color leads — the two splits support\n· Slightly more flexible than complementary for body/background use\n· Often the most beginner-friendly high-contrast strategy'
			},
			monochromatic: {
				desc: 'Monochromatic — single hue, varied value and saturation. All tones from the same hue family. Feels highly cohesive, refined, and controlled. Relies entirely on lightness contrast for hierarchy.',
				balance:
					'· Distribute across dark, mid, and light tones\n· Add saturation contrast — one vivid, others muted\n· Introduce a neutral (very low saturation) to give the eye a rest'
			}
		};

		function updateHarmonySwatches() {
			const swatchWrap = document.getElementById('harmony-swatches');
			const descEl = document.getElementById('harmony-desc');
			const balanceEl = document.getElementById('balance-guide');
			swatchWrap.innerHTML = '';

			let colors;
			if (harmonyType === 'monochromatic') {
				colors = [
					{ h: baseHue, s: 75, l: 55, label: 'Primary' },
					{ h: baseHue, s: 55, l: 40, label: 'Dark' },
					{ h: baseHue, s: 40, l: 25, label: 'Darker' },
					{ h: baseHue, s: 30, l: 15, label: 'Deep' },
					{ h: baseHue, s: 60, l: 72, label: 'Light' }
				];
			} else {
				const hues = getHarmonyHues(baseHue, harmonyType);
				const labels = ['Base', 'Complement', 'Third', 'Split A', 'Split B'];
				colors = hues.map((h, i) => ({ h, s: 75, l: 55, label: labels[i] || 'Color' }));
				if (harmonyType === 'analogous') colors[0].label = 'Base';
				if (harmonyType === 'split') {
					colors[1].label = 'Split A';
					colors[2].label = 'Split B';
				}
			}

			colors.forEach((c) => {
				const hex = hslToHex(c.h, c.s, c.l);
				const textC = contrastColor(c.h, c.s, c.l);
				const div = document.createElement('div');
				div.className = 'h-swatch';
				div.style.background = `hsl(${c.h},${c.s}%,${c.l}%)`;
				div.title = `${hex.toUpperCase()} · HSL(${c.h}°, ${c.s}%, ${c.l}%)`;
				div.innerHTML = `<span class="h-swatch-label" style="color:${textC}">${c.label}</span>`;
				swatchWrap.appendChild(div);
			});

			const cfg = HARMONY_CONFIGS[harmonyType];
			descEl.textContent = cfg.desc;
			balanceEl.style.whiteSpace = 'pre-line';
			balanceEl.textContent = cfg.balance;
		}

		function setHarmony(type, btn) {
			harmonyType = type;
			document.querySelectorAll('#harmony-btns .btn').forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			drawWheel();
		}

		wheelCanvas.addEventListener('click', (e) => {
			const rect = wheelCanvas.getBoundingClientRect();
			const scale = WS / rect.width;
			const mx = (e.clientX - rect.left) * scale - WCX;
			const my = (e.clientY - rect.top) * scale - WCY;
			const dist = Math.sqrt(mx * mx + my * my);
			if (dist > INNER_R && dist < OUTER_R + 10) {
				let angle = Math.atan2(my, mx) + Math.PI / 2;
				if (angle < 0) angle += Math.PI * 2;
				baseHue = Math.round((angle / (Math.PI * 2)) * 360) % 360;
				drawWheel();
			}
		});

		drawWheel();

		/* ════════════════════════════════════════
   MOOD PALETTE SWITCHER
════════════════════════════════════════ */
		const MOODS = {
			energetic: {
				bg: 'hsl(15,90%,12%)',
				title: '#fff',
				sub: 'hsl(15,80%,75%)',
				tag: 'hsl(40,95%,55%)',
				tagBorder: 'hsl(40,95%,55%)',
				accent: 'hsl(40,95%,55%)',
				circle: 'hsl(15,80%,50%)',
				palette: [
					'hsl(15,90%,12%)',
					'hsl(15,80%,25%)',
					'hsl(25,85%,45%)',
					'hsl(40,95%,55%)',
					'hsl(50,90%,70%)'
				],
				explanation:
					'High-saturation warm palette: reds, oranges, ambers. This signals urgency, excitement, and energy. Effective for fitness, entertainment, food, and high-motivation content. The dark background prevents it from feeling cheap — it reads as intense rather than casual.'
			},
			calm: {
				bg: 'hsl(200,30%,14%)',
				title: 'hsl(195,60%,88%)',
				sub: 'hsl(200,25%,62%)',
				tag: 'hsl(175,55%,55%)',
				tagBorder: 'hsl(175,55%,55%)',
				accent: 'hsl(175,55%,55%)',
				circle: 'hsl(210,50%,40%)',
				palette: [
					'hsl(200,30%,14%)',
					'hsl(200,25%,22%)',
					'hsl(205,30%,35%)',
					'hsl(190,40%,48%)',
					'hsl(175,55%,55%)'
				],
				explanation:
					'Cool blue-teal palette at moderate saturation. Communicates calm, trust, and professional steadiness. Works well for mindfulness, finance, health, and educational content where authority and clarity matter more than excitement.'
			},
			dark: {
				bg: 'hsl(250,25%,8%)',
				title: '#fff',
				sub: 'hsl(250,15%,65%)',
				tag: 'hsl(270,75%,65%)',
				tagBorder: 'hsl(270,75%,65%)',
				accent: 'hsl(270,75%,65%)',
				circle: 'hsl(260,60%,35%)',
				palette: [
					'hsl(250,25%,8%)',
					'hsl(250,20%,14%)',
					'hsl(255,20%,22%)',
					'hsl(265,50%,45%)',
					'hsl(270,75%,65%)'
				],
				explanation:
					'Deep dark background with violet-to-purple accent. Communicates depth, precision, and technical intensity. This is the register of premium developer tools, creative software, and courses for serious practitioners — the palette says "this is not for beginners."'
			},
			warm: {
				bg: 'hsl(30,20%,11%)',
				title: 'hsl(35,40%,88%)',
				sub: 'hsl(30,20%,60%)',
				tag: 'hsl(145,40%,52%)',
				tagBorder: 'hsl(145,40%,52%)',
				accent: 'hsl(145,40%,52%)',
				circle: 'hsl(25,45%,40%)',
				palette: [
					'hsl(30,20%,11%)',
					'hsl(25,25%,18%)',
					'hsl(28,35%,30%)',
					'hsl(20,50%,48%)',
					'hsl(145,40%,52%)'
				],
				explanation:
					'Warm earthy neutrals (terracotta, sand, clay) with a sage green accent. Communicates authenticity, craft, and organic warmth. The sage accent provides contrast without disrupting the earthy register. Effective for wellness, food, crafts, and educational content that should feel approachable and grounded.'
			},
			editorial: {
				bg: 'hsl(0,0%,97%)',
				title: 'hsl(0,0%,7%)',
				sub: 'hsl(0,0%,40%)',
				tag: 'hsl(0,0%,12%)',
				tagBorder: 'hsl(0,0%,12%)',
				accent: 'hsl(0,0%,12%)',
				circle: 'hsl(0,0%,82%)',
				palette: [
					'hsl(0,0%,97%)',
					'hsl(0,0%,90%)',
					'hsl(0,0%,75%)',
					'hsl(0,0%,40%)',
					'hsl(0,0%,7%)'
				],
				explanation:
					'High-key neutral palette: near-white background, charcoal text, graduated greys. Zero saturation. Communicates restraint, sophistication, and editorial confidence — the palette of publishing, architecture, and design-world brands. Everything depends on typography and spacing when color steps aside entirely.'
			}
		};

		function setMood(mood, btn) {
			const m = MOODS[mood];
			document.querySelectorAll('#mood-btns .btn').forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');

			const stage = document.getElementById('mood-stage');
			stage.style.background = m.bg;
			document.getElementById('mood-title').style.color = m.title;
			document.getElementById('mood-sub').style.color = m.sub;
			document.getElementById('mood-tag').style.color = m.tag;
			document.getElementById('mood-tag').style.borderColor = m.tagBorder;
			document.getElementById('mood-accent-bar').style.background = m.accent;
			document.getElementById('mood-circle').style.background = m.circle;

			m.palette.forEach((col, i) => {
				document.getElementById('ms' + i).style.background = col;
			});
			document.getElementById('mood-explanation').textContent = m.explanation;
		}

		setMood('energetic', document.querySelector('#mood-btns .btn'));

		/* ════════════════════════════════════════
   CONTRAST CHECKER
════════════════════════════════════════ */
		function updateContrast() {
			const th = parseInt(document.getElementById('cc-text-h').value);
			const ts = parseInt(document.getElementById('cc-text-s').value);
			const tl = parseInt(document.getElementById('cc-text-l').value);
			const bh = parseInt(document.getElementById('cc-bg-h').value);
			const bs = parseInt(document.getElementById('cc-bg-s').value);
			const bl = parseInt(document.getElementById('cc-bg-l').value);

			document.getElementById('cc-th-val').textContent = th + '°';
			document.getElementById('cc-ts-val').textContent = ts + '%';
			document.getElementById('cc-tl-val').textContent = tl + '%';
			document.getElementById('cc-bh-val').textContent = bh + '°';
			document.getElementById('cc-bs-val').textContent = bs + '%';
			document.getElementById('cc-bl-val').textContent = bl + '%';

			const textCSS = `hsl(${th},${ts}%,${tl}%)`;
			const bgCSS = `hsl(${bh},${bs}%,${bl}%)`;

			document.getElementById('cc-preview').style.background = bgCSS;
			document.getElementById('cc-preview').style.color = textCSS;
			document.getElementById('cc-large').style.color = textCSS;

			// Strips
			const tStops = [0, 25, 50, 75, 100].map((lv) => `hsl(${th},${ts}%,${lv}%)`).join(',');
			document.getElementById('cc-text-strip').style.background =
				`linear-gradient(to right,${tStops})`;
			const bStops = [0, 25, 50, 75, 100].map((lv) => `hsl(${bh},${bs}%,${lv}%)`).join(',');
			document.getElementById('cc-bg-strip').style.background =
				`linear-gradient(to right,${bStops})`;

			const ratio = getContrastRatio(th, ts, tl, bh, bs, bl);
			const ratioEl = document.getElementById('cc-ratio');
			ratioEl.textContent = ratio.toFixed(2) + ':1';
			ratioEl.style.color =
				ratio >= 7 ? 'var(--sage)' : ratio >= 4.5 ? 'var(--amber)' : 'var(--rose)';

			const badges = document.getElementById('cc-badges');
			const B = (label, pass) =>
				`<span class="cc-badge ${pass ? 'pass' : 'fail'}">${pass ? '✓' : '✗'} ${label}</span>`;
			badges.innerHTML =
				B('AA Normal (4.5:1)', ratio >= 4.5) +
				B('AA Large (3.0:1)', ratio >= 3.0) +
				B('AAA Normal (7.0:1)', ratio >= 7.0) +
				B('AAA Large (4.5:1)', ratio >= 4.5);
		}

		function setCCPreset(p) {
			const vals = {
				'our-dark': [210, 15, 88, 215, 20, 9],
				'white-on-white': [0, 0, 95, 0, 0, 100],
				'grey-fail': [0, 0, 55, 0, 0, 100],
				'black-white': [0, 0, 0, 0, 0, 100],
				'red-fail': [0, 70, 45, 10, 65, 38]
			};
			const v = vals[p];
			document.getElementById('cc-text-h').value = v[0];
			document.getElementById('cc-text-s').value = v[1];
			document.getElementById('cc-text-l').value = v[2];
			document.getElementById('cc-bg-h').value = v[3];
			document.getElementById('cc-bg-s').value = v[4];
			document.getElementById('cc-bg-l').value = v[5];
			updateContrast();
		}

		updateContrast();

		/* ════════════════════════════════════════
   QUIZ
════════════════════════════════════════ */
		let quizScore = 0,
			quizAnswered = 0;

		const explanations = [
			'Correct. Very high saturation (90%+) on large visual areas is physically fatiguing and reads as aggressive or cheap in most professional contexts. High-saturation colors are most effective as small focal accents — 10% of the visual field or less.',
			'Correct. When saturation drops to 0, all hue information disappears — the color becomes a neutral grey. The lightness value determines where on the grey scale it lands, but no hue is visible. This is why hue changes have no effect on desaturated colors.',
			'Correct. Split-complementary palettes avoid the direct 180° opposition — instead pairing the base with colors at 150° and 210°. This preserves contrast and visual interest while avoiding the visual tension of two fully opposing hues fighting for dominance.',
			'Correct. The WCAG contrast ratio is driven by relative luminance, which is determined primarily by lightness. Moving the text from 55% to ~30% lightness will dramatically increase luminance difference against a white background, pushing the ratio above 4.5:1.',
			'Correct. WCAG contrast uses relative luminance — a measure of how much light a surface appears to emit. Luminance is almost entirely determined by lightness in HSL. Hue changes at the same lightness barely affect luminance; saturation changes have a moderate effect but much smaller than lightness.'
		];
		const wrongMsg =
			"Not quite — revisit the section and consider the viewer's perceptual experience.";

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
				const s = document.getElementById('quiz-score');
				document.getElementById('score-num').textContent = quizScore + ' / 5';
				s.style.display = 'block';
				setTimeout(() => s.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 300);
			}
		}

		/* ════════════════════════════════════════
   PALETTE ASSESSMENT
════════════════════════════════════════ */
		const paletteAnswered = {};
		const paletteCorrect = { 0: 2, 1: 0 };
		const paletteFeedback = {
			0: {
				ok: 'Correct. Every color in this palette is a high-saturation warm hue (red, orange, crimson). These colors universally signal urgency, excitement, and heat — the opposite of calm and professional. The fix is to rebuild the palette in a cool or neutral register: muted blues, greens, or earthy neutrals.',
				bad: 'Not quite. The number of colors is not the issue. The problem is that every single color in this palette is a warm, high-saturation red or orange — color families strongly associated with urgency and energy, which directly contradict the calm emotional register required.'
			},
			1: {
				ok: 'Correct. Lightness is the primary driver of contrast ratio. Moving the text from 55% to ~30–35% lightness while keeping the background at 92% will dramatically increase the luminance difference and push the ratio above the 4.5:1 WCAG AA threshold. Saturation and hue changes would not solve a contrast failure.',
				bad: 'Not quite. Contrast failures are driven by insufficient lightness difference, not hue or saturation differences. The fix is to darken the text — moving its lightness from 55% to approximately 30–35% — which increases luminance difference against the light background.'
			}
		};

		function handlePQ(el, idx, qNum) {
			if (paletteAnswered[qNum]) return;
			paletteAnswered[qNum] = true;
			const opts = el.closest('.palette-opts').querySelectorAll('.palette-opt');
			opts.forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById('pf-' + (qNum - 1)); // pf-0 and pf-1
			if (idx === paletteCorrect[qNum - 1]) {
				el.classList.add('correct');
				fb.textContent = '✓ ' + paletteFeedback[qNum - 1].ok;
				fb.className = 'palette-feedback ok';
			} else {
				el.classList.add('wrong');
				opts[paletteCorrect[qNum - 1]].classList.add('correct');
				fb.textContent = '✗ ' + paletteFeedback[qNum - 1].bad;
				fb.className = 'palette-feedback bad';
			}
		}

		if (typeof hslToRgb === 'function') actions.hslToRgb = hslToRgb;
		if (typeof hslToHex === 'function') actions.hslToHex = hslToHex;
		if (typeof getLuminance === 'function') actions.getLuminance = getLuminance;
		if (typeof getContrastRatio === 'function') actions.getContrastRatio = getContrastRatio;
		if (typeof contrastColor === 'function') actions.contrastColor = contrastColor;
		if (typeof buildHueStrip === 'function') actions.buildHueStrip = buildHueStrip;
		if (typeof updateHSL === 'function') actions.updateHSL = updateHSL;
		if (typeof setHSLPreset === 'function') actions.setHSLPreset = setHSLPreset;
		if (typeof drawWheel === 'function') actions.drawWheel = drawWheel;
		if (typeof getHarmonyHues === 'function') actions.getHarmonyHues = getHarmonyHues;
		if (typeof updateHarmonySwatches === 'function')
			actions.updateHarmonySwatches = updateHarmonySwatches;
		if (typeof setHarmony === 'function') actions.setHarmony = setHarmony;
		if (typeof setMood === 'function') actions.setMood = setMood;
		if (typeof updateContrast === 'function') actions.updateContrast = updateContrast;
		if (typeof setCCPreset === 'function') actions.setCCPreset = setCCPreset;
		if (typeof handleQuiz === 'function') actions.handleQuiz = handleQuiz;
		if (typeof handlePQ === 'function') actions.handlePQ = handlePQ;

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
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 04 of 10</div>
	</header>

	<!-- HERO -->
	<div class="module-hero">
		<div class="module-number">04</div>
		<div class="module-tag">Module 04 · Color + Feeling</div>
		<h1 class="module-title">Color Theory &amp;<br /><span>Emotional Impact</span></h1>
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
			<li><a href="#hsl">Hue, Saturation &amp; Value</a></li>
			<li><a href="#harmony">Color Relationships</a></li>
			<li><a href="#psychology">Warm, Cool &amp; Emotional Palettes</a></li>
			<li><a href="#accessibility">Accessibility &amp; Contrast</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<!-- OBJECTIVES -->
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>
				Understand and manipulate hue, saturation, and lightness as three independent dimensions
			</li>
			<li>Build complementary, analogous, and triadic palettes from a base color</li>
			<li>Apply warm and cool color logic to create intended emotional tone</li>
			<li>Test and achieve accessible contrast ratios for text legibility</li>
		</ul>
	</section>

	<!-- ═══════════════════════════════
     SECTION 1: HSL
═══════════════════════════════ -->
	<section id="hsl" class="section">
		<div class="section-header">
			<span class="section-num">04.01</span>
			<h2 class="section-title">Hue, Saturation &amp; Value (HSL)</h2>
		</div>

		<p>
			Color has three independent dimensions. Most people think about color as a single thing —
			"blue," "red," "green" — but each of those words only describes one dimension:
			<strong>hue</strong>. Understanding all three is what allows you to build palettes with
			intention rather than guessing.
		</p>

		<p>
			<em>Hue</em> is the wavelength of light — the position on the color spectrum. It is what we conventionally
			mean when we say "red" or "teal." It wraps around a circle: red at 0°, yellow at 60°, green at 120°,
			cyan at 180°, blue at 240°, magenta at 300°, back to red at 360°. Hue alone tells you nothing about
			how a color will actually look — it only tells you which family it belongs to.
		</p>

		<p>
			<em>Saturation</em> is color intensity — how much of that hue is present relative to grey. At 100%
			saturation, you get the fullest, most vivid expression of the hue. At 0%, the color collapses entirely
			to grey, regardless of hue. Most professional brand colors sit between 40–80% saturation. Very high
			saturation (90–100%) is physically fatiguing at large areas and reads as cheap or aggressive unless
			used deliberately for accent elements.
		</p>

		<p>
			<em>Lightness</em> (sometimes called value or brightness) is the amount of light — how close a color
			is to white or black. At 100% lightness, any hue becomes white. At 0%, any hue becomes black. The
			midpoint (50%) gives the most saturated possible version of a hue. Lightness is the most powerful
			dimension for creating contrast, because the human visual system detects value differences before
			it detects hue differences.
		</p>

		<div class="callout">
			<div class="callout-label">Why HSL, Not RGB</div>
			RGB describes color in terms of light mixing — useful for hardware but completely unintuitive for
			design. In RGB, there is no direct way to "make this color lighter" or "reduce the saturation."
			HSL maps directly to how designers think: move the hue, adjust the intensity, change the brightness.
			Always think and specify color in HSL when designing.
		</div>

		<!-- DEMO: HSL Explorer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · HSL Color Space Explorer</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Adjust each axis independently to understand what it controls. Notice how hue changes are
					invisible when saturation is 0. Notice how lightness extremes collapse any hue to white or
					black.
				</p>

				<div class="two-col" style="align-items: start; gap: 1.5rem">
					<div>
						<div class="hsl-swatch-large" id="hsl-swatch">
							<div class="hsl-overlay">
								<div class="hsl-hex-display" id="hsl-hex">#38c0e8</div>
								<div class="hsl-sub-display" id="hsl-sub">HSL(198°, 78%, 57%)</div>
							</div>
						</div>

						<div style="margin-top: 1rem">
							<div class="hsl-axis-label">Hue axis (0° → 360°)</div>
							<div class="hsl-axis-strip" id="hue-strip"></div>
							<div class="hsl-axis-label">
								Saturation axis (0% → 100% at current hue &amp; lightness)
							</div>
							<div class="hsl-axis-strip" id="sat-strip"></div>
							<div class="hsl-axis-label">
								Lightness axis (0% → 100% at current hue &amp; saturation)
							</div>
							<div class="hsl-axis-strip" id="lit-strip"></div>
						</div>
					</div>

					<div>
						<div class="slider-row">
							<label for="hsl-h">Hue</label>
							<input
								type="range"
								id="hsl-h"
								min="0"
								max="360"
								value="198"
								oninput={() => {
									actions.updateHSL();
								}}
							/>
							<span class="slider-val" id="hsl-h-val">198°</span>
						</div>
						<div class="slider-row">
							<label for="hsl-s">Saturation</label>
							<input
								type="range"
								id="hsl-s"
								min="0"
								max="100"
								value="78"
								oninput={() => {
									actions.updateHSL();
								}}
							/>
							<span class="slider-val" id="hsl-s-val">78%</span>
						</div>
						<div class="slider-row">
							<label for="hsl-l">Lightness</label>
							<input
								type="range"
								id="hsl-l"
								min="0"
								max="100"
								value="57"
								oninput={() => {
									actions.updateHSL();
								}}
							/>
							<span class="slider-val" id="hsl-l-val">57%</span>
						</div>

						<div class="hsl-meaning" id="hsl-meaning">
							Adjust the sliders to explore what each dimension controls.
						</div>

						<div style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.4rem">
							<button class="btn" onclick={(e) => actions.setHSLPreset(198, 78, 57)}
								>Sky Blue</button
							>
							<button class="btn" onclick={(e) => actions.setHSLPreset(345, 72, 55)}>Rose</button>
							<button class="btn" onclick={(e) => actions.setHSLPreset(38, 91, 55)}>Amber</button>
							<button class="btn" onclick={(e) => actions.setHSLPreset(152, 55, 58)}>Sage</button>
							<button class="btn" onclick={(e) => actions.setHSLPreset(260, 80, 60)}>Violet</button>
							<button class="btn rose" onclick={(e) => actions.setHSLPreset(198, 95, 50)}>
								Over-Saturated
							</button>
							<button class="btn" onclick={(e) => actions.setHSLPreset(198, 0, 50)}
								>Desaturated</button
							>
						</div>
					</div>
				</div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Dimension</th>
					<th>Range</th>
					<th>Perceptual Effect</th>
					<th>Design Use</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Hue</td>
					<td>0° – 360°</td>
					<td>Which color family</td>
					<td>Brand color identity, palette relationships</td>
				</tr>
				<tr>
					<td>Saturation</td>
					<td>0% – 100%</td>
					<td>Intensity vs. greyness</td>
					<td>Accent vs. neutral; energy vs. restraint</td>
				</tr>
				<tr>
					<td>Lightness</td>
					<td>0% – 100%</td>
					<td>Dark to light</td>
					<td>Contrast ratios; background vs. text tones</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══════════════════════════════
     SECTION 2: HARMONY
═══════════════════════════════ -->
	<section id="harmony" class="section">
		<div class="section-header">
			<span class="section-num">04.02</span>
			<h2 class="section-title">Color Relationships &amp; Palette Harmony</h2>
		</div>

		<p>
			A palette is not a collection of colors you happen to like. It is a system of relationships —
			colors chosen because of how they behave next to each other. The relationships are defined by
			their positions on the color wheel, and each type of relationship produces a different
			expressive quality.
		</p>

		<p>
			<em>Complementary</em> colors sit exactly opposite each other on the wheel (180° apart). They create
			maximum visual contrast — each makes the other appear more vivid. Orange against blue, red against
			green, violet against yellow. In branding, a complementary accent against a muted dominant color
			creates high-energy focal points. Too much of both simultaneously creates visual vibration and fatigue.
		</p>

		<p>
			<em>Analogous</em> colors sit adjacent on the wheel (within 60° of each other). They are inherently
			harmonious — they share hue components and feel cohesive, natural, and restful. Most landscape color
			palettes are analogous. The risk: without value or saturation contrast between them, analogous palettes
			feel muddy or undifferentiated.
		</p>

		<p>
			<em>Triadic</em> palettes use three hues evenly spaced (120° apart). They are vibrant and dynamic
			while remaining balanced. The challenge is that three strong hues compete — triadic palettes typically
			work best when one hue dominates (60%), one supports (30%), and one accents (10%).
		</p>

		<p>
			<em>Split-complementary</em> palettes take a base hue and pair it with the two hues on either side
			of its complement (150° and 210°). This gives most of the visual tension of a complementary pair
			with softer, less confrontational contrast — useful when you want energy without aggression.
		</p>

		<!-- DEMO: Color Wheel -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Color Wheel &amp; Harmony Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Click anywhere on the color wheel to set your base hue. Select a harmony type to see the
					related palette colors. The resulting swatches show the palette at working saturation and
					lightness.
				</p>

				<div class="harmony-btns" id="harmony-btns">
					<button
						class="btn active"
						data-h="complementary"
						onclick={(e) => actions.setHarmony('complementary', e.currentTarget)}
					>
						Complementary
					</button>
					<button
						class="btn"
						data-h="analogous"
						onclick={(e) => actions.setHarmony('analogous', e.currentTarget)}
					>
						Analogous
					</button>
					<button
						class="btn"
						data-h="triadic"
						onclick={(e) => actions.setHarmony('triadic', e.currentTarget)}
					>
						Triadic
					</button>
					<button
						class="btn"
						data-h="split"
						onclick={(e) => actions.setHarmony('split', e.currentTarget)}
					>
						Split-Complementary
					</button>
					<button
						class="btn"
						data-h="monochromatic"
						onclick={(e) => actions.setHarmony('monochromatic', e.currentTarget)}
					>
						Monochromatic
					</button>
				</div>

				<div class="two-col" style="align-items: start">
					<div>
						<div class="wheel-wrap">
							<canvas
								id="wheel-canvas"
								width="240"
								height="240"
								aria-label="Wheel Canvas Demonstration"
								role="region"
								tabindex="0"
							></canvas>
						</div>
					</div>
					<div>
						<div
							style="
										font-size: 11px;
										color: var(--muted);
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.5rem;
									"
						>
							Palette Swatches
						</div>
						<div class="harmony-swatches" id="harmony-swatches"></div>
						<div class="harmony-desc" id="harmony-desc">Click the wheel to choose a base hue.</div>

						<div
							style="
										margin-top: 1.25rem;
										font-size: 11px;
										color: var(--muted);
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Applied Balance Guide
						</div>
						<div
							id="balance-guide"
							style="font-size: 12px; color: var(--muted); line-height: 1.6"
						></div>
					</div>
				</div>
			</div>
		</div>

		<div class="callout amber">
			<div class="callout-label">The 60-30-10 Rule</div>
			A functional palette for brand work is almost never equal parts. The dominant color covers roughly
			60% of visual space (usually a neutral dark or light), a secondary color covers 30% (your primary
			brand hue), and an accent covers 10% (a complementary or high-contrast pop). Most design system
			failures come from treating all palette colors as equal-weight participants.
		</div>
	</section>

	<!-- ═══════════════════════════════
     SECTION 3: WARM / COOL / MOOD
═══════════════════════════════ -->
	<section id="psychology" class="section">
		<div class="section-header">
			<span class="section-num">04.03</span>
			<h2 class="section-title">Warm, Cool &amp; Emotional Color Palettes</h2>
		</div>

		<p>
			Color psychology is partially universal (rooted in evolutionary associations with fire, sky,
			blood, and vegetation) and partially cultural (red means danger in one context, luck in
			another). For brand design purposes, the most reliable dimension is the warm/cool spectrum and
			the saturation-energy relationship, both of which operate cross-culturally.
		</p>

		<p>
			<strong>Warm colors</strong> — reds, oranges, yellows — are associated with energy, urgency, heat,
			danger, appetite, and excitement. They advance visually (they appear closer than they are), which
			is why warm accent colors naturally become focal points. High-saturation warm palettes feel intense,
			young, or aggressive. Low-saturation warm palettes feel organic, earthy, or comfortable.
		</p>

		<p>
			<strong>Cool colors</strong> — blues, greens, purples — recede visually and carry associations with
			calm, trust, intelligence, and professionalism. Blue is the most universally trusted color in brand
			contexts, which is why it dominates finance, health, and technology branding. Cool palettes at low
			saturation feel sophisticated and authoritative. Cool palettes at high saturation feel electric
			and technical.
		</p>

		<p>
			<em>Dark backgrounds</em> with saturated accent colors communicate a specific register: premium,
			technical, nocturnal, high-intensity. This course uses it deliberately — it signals a learning environment
			for people who take their craft seriously, not a casual self-help platform. Light backgrounds communicate
			openness, approachability, and neutrality. The background tone is often the highest-leverage single
			decision in a brand palette.
		</p>

		<!-- DEMO: Mood Palette Switcher -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Emotional Palette Switcher</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					The same channel banner content — identical words, identical layout — in five different
					palettes. Notice how the emotional register of the entire piece shifts with only color
					changes.
				</p>

				<div class="mood-btns" id="mood-btns">
					<button class="btn active" onclick={(e) => actions.setMood('energetic', e.currentTarget)}
						>Energetic</button
					>
					<button class="btn" onclick={(e) => actions.setMood('calm', e.currentTarget)}>Calm</button
					>
					<button class="btn" onclick={(e) => actions.setMood('dark', e.currentTarget)}
						>Dark / Technical</button
					>
					<button class="btn" onclick={(e) => actions.setMood('warm', e.currentTarget)}
						>Warm / Organic</button
					>
					<button class="btn" onclick={(e) => actions.setMood('editorial', e.currentTarget)}
						>Editorial</button
					>
				</div>

				<div class="mood-stage" id="mood-stage">
					<div class="mood-accent-bar" id="mood-accent-bar"></div>
					<div class="mood-circle" id="mood-circle"></div>
					<div class="mood-banner-text">
						<div class="mood-title" id="mood-title">Visual Design<br />Fundamentals</div>
						<div class="mood-sub" id="mood-sub">A systematic approach to creative thinking</div>
						<div class="mood-tag" id="mood-tag">New Series</div>
					</div>
				</div>

				<div
					style="
								font-size: 10px;
								letter-spacing: 0.12em;
								text-transform: uppercase;
								color: var(--muted);
								margin: 0.75rem 0 0.3rem;
							"
				>
					Palette
				</div>
				<div class="mood-palette-strip" id="mood-palette-strip">
					<div class="mood-strip-cell" id="ms0"></div>
					<div class="mood-strip-cell" id="ms1"></div>
					<div class="mood-strip-cell" id="ms2"></div>
					<div class="mood-strip-cell" id="ms3"></div>
					<div class="mood-strip-cell" id="ms4"></div>
				</div>
				<div class="mood-explanation" id="mood-explanation"></div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Palette Type</th>
					<th>Dominant Colors</th>
					<th>Communicates</th>
					<th>Use Case</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>High-energy warm</td>
					<td>Orange, red, yellow</td>
					<td>Urgency, excitement, youth</td>
					<td>Entertainment, fitness, food</td>
				</tr>
				<tr>
					<td>Cool professional</td>
					<td>Navy, steel blue, grey</td>
					<td>Trust, competence, clarity</td>
					<td>Finance, health, B2B tech</td>
				</tr>
				<tr>
					<td>Dark technical</td>
					<td>Deep navy/black, cyan, violet</td>
					<td>Precision, depth, intensity</td>
					<td>Developer tools, security, premium SaaS</td>
				</tr>
				<tr>
					<td>Warm organic</td>
					<td>Terracotta, sand, sage</td>
					<td>Comfort, nature, authenticity</td>
					<td>Wellness, food, crafts, education</td>
				</tr>
				<tr>
					<td>Editorial neutral</td>
					<td>Black, white, single accent</td>
					<td>Sophistication, restraint, intelligence</td>
					<td>Publishing, design, architecture</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══════════════════════════════
     SECTION 4: ACCESSIBILITY
═══════════════════════════════ -->
	<section id="accessibility" class="section">
		<div class="section-header">
			<span class="section-num">04.04</span>
			<h2 class="section-title">Accessibility &amp; Contrast</h2>
		</div>

		<p>
			Color contrast for text legibility is not an optional consideration. It determines whether
			your design is actually readable by anyone with non-perfect vision — which, accounting for
			age-related vision changes and color vision deficiency, is a significant portion of any
			audience. In many professional and legal contexts, meeting accessibility standards is a
			requirement.
		</p>

		<p>
			The Web Content Accessibility Guidelines (WCAG) define contrast in terms of
			<em>relative luminance</em> — a measure of how much light a color appears to emit. The contrast
			ratio between a text color and its background ranges from 1:1 (identical, invisible) to 21:1 (black
			on white, maximum). Two thresholds matter for design:
		</p>

		<table>
			<thead>
				<tr>
					<th>Level</th>
					<th>Normal Text (&lt;18pt)</th>
					<th>Large Text (≥18pt bold)</th>
					<th>Meaning</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>WCAG AA</td>
					<td>4.5 : 1</td>
					<td>3.0 : 1</td>
					<td>Minimum standard — legally required in many contexts</td>
				</tr>
				<tr>
					<td>WCAG AAA</td>
					<td>7.0 : 1</td>
					<td>4.5 : 1</td>
					<td>Enhanced — recommended for body text and critical information</td>
				</tr>
			</tbody>
		</table>

		<p>
			The most common contrast failure is placing medium-lightness text on a medium-lightness
			background — two muted colors that <em>feel</em> different but produce a ratio below 3:1. The fix
			is almost always to move lightness, not hue: darken the text or lighten the background (or both).
			Hue changes almost never fix a contrast problem because luminance is driven by lightness, not hue.
		</p>

		<div class="callout warn">
			<div class="callout-label">Common Failure</div>
			Grey text on a white background — the combination that every default theme uses for secondary text
			— typically fails WCAG AA for normal-size body text. This is not a hypothetical edge case. It affects
			a large percentage of published websites and course materials.
		</div>

		<!-- DEMO: Contrast Checker -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · WCAG Contrast Checker</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1.25rem">
					Set text and background colors using the lightness sliders. The contrast ratio and WCAG
					pass/fail status update live. Try the presets to see common successes and failures.
				</p>

				<div class="two-col" style="align-items: start; gap: 1.5rem">
					<div>
						<div class="cc-preview-text" id="cc-preview">
							<div class="cc-preview-large" id="cc-large">Large Text (18pt+)</div>
							Normal body text — this is the paragraph size your readers will encounter most often on
							your website. It must remain legible across a wide range of viewing conditions and distances.
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
							Text Color
						</div>
						<div class="slider-row">
							<label style="min-width: 80px">Hue</label>
							<input
								type="range"
								id="cc-text-h"
								min="0"
								max="360"
								value="210"
								oninput={() => {
									actions.updateContrast();
								}}
							/>
							<span class="slider-val" id="cc-th-val">210°</span>
						</div>
						<div class="slider-row">
							<label style="min-width: 80px">Saturation</label>
							<input
								type="range"
								id="cc-text-s"
								min="0"
								max="100"
								value="15"
								oninput={() => {
									actions.updateContrast();
								}}
							/>
							<span class="slider-val" id="cc-ts-val">15%</span>
						</div>
						<div class="slider-row">
							<label style="min-width: 80px">Lightness</label>
							<input
								type="range"
								id="cc-text-l"
								min="0"
								max="100"
								value="88"
								oninput={() => {
									actions.updateContrast();
								}}
							/>
							<span class="slider-val" id="cc-tl-val">88%</span>
						</div>

						<div class="cc-hue-strip" id="cc-text-strip" style="margin-top: 0.25rem"></div>

						<div
							style="
										font-size: 10px;
										letter-spacing: 0.12em;
										text-transform: uppercase;
										color: var(--muted);
										margin: 0.85rem 0 0.5rem;
									"
						>
							Background Color
						</div>
						<div class="slider-row">
							<label style="min-width: 80px">Hue</label>
							<input
								type="range"
								id="cc-bg-h"
								min="0"
								max="360"
								value="215"
								oninput={() => {
									actions.updateContrast();
								}}
							/>
							<span class="slider-val" id="cc-bh-val">215°</span>
						</div>
						<div class="slider-row">
							<label style="min-width: 80px">Saturation</label>
							<input
								type="range"
								id="cc-bg-s"
								min="0"
								max="100"
								value="20"
								oninput={() => {
									actions.updateContrast();
								}}
							/>
							<span class="slider-val" id="cc-bs-val">20%</span>
						</div>
						<div class="slider-row">
							<label style="min-width: 80px">Lightness</label>
							<input
								type="range"
								id="cc-bg-l"
								min="0"
								max="100"
								value="9"
								oninput={() => {
									actions.updateContrast();
								}}
							/>
							<span class="slider-val" id="cc-bl-val">9%</span>
						</div>
						<div class="cc-hue-strip" id="cc-bg-strip" style="margin-top: 0.25rem"></div>

						<div style="margin-top: 1.25rem">
							<div class="cc-ratio-display" id="cc-ratio">—</div>
							<div style="font-size: 11px; color: var(--muted); margin-top: 0.2rem">
								contrast ratio
							</div>
						</div>

						<div class="cc-badges" id="cc-badges"></div>

						<div class="cc-presets" id="cc-presets">
							<div
								style="
											font-size: 10px;
											color: var(--muted);
											letter-spacing: 0.1em;
											text-transform: uppercase;
											width: 100%;
											margin-bottom: 0.3rem;
										"
							>
								Presets
							</div>
							<button class="btn" onclick={(e) => actions.setCCPreset('our-dark')}
								>This Course (Dark)</button
							>
							<button class="btn" onclick={(e) => actions.setCCPreset('white-on-white')}>
								Light on Light ⚠
							</button>
							<button class="btn" onclick={(e) => actions.setCCPreset('grey-fail')}
								>Grey on White ⚠</button
							>
							<button class="btn" onclick={(e) => actions.setCCPreset('black-white')}
								>Black on White</button
							>
							<button class="btn rose" onclick={(e) => actions.setCCPreset('red-fail')}>
								Red on Red Fail ⚠
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="callout sky">
			<div class="callout-label">Practical Rule</div>
			For dark-background designs (which most YouTube-facing brands use), pure white text gives ~15:1
			contrast — far above what is needed. The risk is the opposite: accent colors and muted greys used
			for secondary text often drop below 3:1. Always check your muted/secondary text color, not just
			your primary.
		</div>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">04.05</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout">
			<div class="callout-label">Exercise 1 — Build Your Brand Palette</div>
			Starting from a single hue that feels right for your channel's personality, build a five-color palette:<br
			/><br />
			1. A dark background tone (your base hue at 10–15% lightness, 15–25% saturation)<br />
			2. A surface tone (same hue, 2–4% lighter)<br />
			3. Your primary accent (your base hue at 55–65% lightness, 70–85% saturation)<br />
			4. A secondary accent at 150–180° from your primary (complementary range)<br />
			5. A muted text tone (your base hue, low saturation, 65–75% lightness)<br /><br />
			Test all five using the contrast checker. Every text tone must pass WCAG AA (4.5:1) against your
			darkest background.
		</div>

		<div class="callout amber">
			<div class="callout-label">Exercise 2 — Apply a Palette to a Thumbnail</div>
			Take a thumbnail you made or sketched in Module 2 or 3. Apply your palette to it — exactly and only
			your palette colors. Then answer:<br /><br />
			· Which color is doing 60% of the visual work?<br />
			· Which color is the accent (10%)?<br />
			· Does the palette feel consistent with the video topic's emotional register?<br /><br />
			If the answer to the last question is no — the palette is technically fine but emotionally wrong
			— go back and shift the base hue. This is normal and expected.
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 04 — Check Your Understanding</div>
		<div class="quiz-sub">Five questions · No time limit</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">01.</span> A designer sets their brand accent to HSL(45°, 95%, 55%). A colleague
				says it feels "cheap" and "aggressive." What is the most likely cause?
			</div>
			<div class="options" data-correct="1">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. 45° is a poor hue choice — yellow-orange does not suit professional brands
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. The saturation is at 95% — very high saturation on large areas is physically fatiguing
					and reads as cheap or aggressive unless used only as a small accent
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The lightness at 55% is too dark for an accent color
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The hue is too close to other warm colors and creates visual conflict
				</button>
			</div>
			<div class="feedback" id="fb-0"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">02.</span> A color at HSL(120°, 80%, 50%) is compared to HSL(120°, 0%, 50%).
				What has changed between these two values, and what has stayed the same?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. The hue has changed; the saturation and lightness stayed the same
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. The lightness changed; the hue and saturation stayed the same
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The saturation dropped to zero — the color became a neutral grey — while the hue and
					lightness value stayed the same (though hue is now invisible)
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. The hue rotated 80° and the color became a blue-grey
				</button>
			</div>
			<div class="feedback" id="fb-1"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">03.</span> Why do split-complementary palettes often feel less aggressive
				than true complementary pairings?
			</div>
			<div class="options" data-correct="3">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Split-complementary palettes use lower saturation than complementary pairs
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Three colors are always more harmonious than two
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. The split hues are less saturated because they are further from the color wheel center
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Instead of pairing with the exact opposite hue, the base pairs with two hues on either
					side of the complement — which softens the maximum contrast while retaining visual
					interest
				</button>
			</div>
			<div class="feedback" id="fb-2"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">04.</span> A text element reads as HSL(0°, 0%, 55%) on a background of HSL(0°,
				0%, 100%). This combination likely fails WCAG AA for normal text. What is the fastest fix?
			</div>
			<div class="options" data-correct="0">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Reduce the lightness of the text color — moving from 55% to 30% dramatically increases
					contrast because luminance is driven primarily by lightness
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Add a hue to the text color — saturated colors are more visible
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Increase the font size so the large text threshold applies
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. Change the background to a complementary color to increase visual distinction
				</button>
			</div>
			<div class="feedback" id="fb-3"></div>
		</div>

		<div class="question">
			<div class="q-text">
				<span class="q-num">05.</span> Which color property is primarily responsible for making two colors
				distinguishable in terms of contrast ratio, according to WCAG luminance calculation?
			</div>
			<div class="options" data-correct="2">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 0)}
				>
					A. Hue — the wavelength difference between colors
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 1)}
				>
					B. Saturation — more saturated colors appear brighter
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 2)}
				>
					C. Lightness / value — the amount of light a color appears to emit is what WCAG luminance
					primarily measures
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.handleQuiz(e.currentTarget, 3)}
				>
					D. All three properties contribute equally to contrast ratio
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
		<div class="assessment-header">Module Assessment — Palette Diagnosis</div>
		<div class="assessment-sub">
			Identify the structural problem in each palette and select the correct diagnosis.
		</div>

		<!-- Q1 -->
		<div class="palette-question">
			<div class="palette-q-header">Palette 01 — Emotional Register Problem</div>
			<div class="palette-q-body">
				<div style="font-size: 12px; color: var(--muted); margin-bottom: 0.5rem">
					This palette is intended for a calm, professional meditation and mindfulness channel.
				</div>
				<div class="palette-swatches-row">
					<div style="position: relative; margin-bottom: 20px">
						<div class="p-swatch" style="background: hsl(0, 85%, 48%)"></div>
						<div class="p-swatch-label">Primary</div>
					</div>
					<div style="position: relative; margin-bottom: 20px">
						<div class="p-swatch" style="background: hsl(15, 90%, 55%)"></div>
						<div class="p-swatch-label">Accent</div>
					</div>
					<div style="position: relative; margin-bottom: 20px">
						<div class="p-swatch" style="background: hsl(350, 80%, 45%)"></div>
						<div class="p-swatch-label">Secondary</div>
					</div>
					<div style="position: relative; margin-bottom: 20px">
						<div class="p-swatch" style="background: hsl(8, 75%, 35%)"></div>
						<div class="p-swatch-label">Dark</div>
					</div>
					<div style="position: relative; margin-bottom: 20px">
						<div class="p-swatch" style="background: hsl(5, 60%, 72%)"></div>
						<div class="p-swatch-label">Light</div>
					</div>
				</div>
				<div class="palette-q-text">
					What is the primary problem with this palette for the stated context?
				</div>
				<div class="palette-opts">
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 0, 2)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 0, 2);
							}
						}}
					>
						A. The palette has too many colors — five is excessive for a brand system
					</div>
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 1, 2)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 1, 2);
							}
						}}
					>
						B. The saturation levels are inconsistent across the five colors
					</div>
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 2, 2)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 2, 2);
							}
						}}
					>
						C. The palette is built entirely from high-saturation warm reds and oranges — colors
						strongly associated with urgency and excitement — which contradict the calm,
						professional register the brand requires
					</div>
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 3, 2)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 3, 2);
							}
						}}
					>
						D. The dark swatch is too dark and will fail accessibility contrast requirements
					</div>
				</div>
				<div class="palette-feedback" id="pf-0"></div>
			</div>
		</div>

		<!-- Q2 -->
		<div class="palette-question">
			<div class="palette-q-header">Palette 02 — Contrast Problem</div>
			<div class="palette-q-body">
				<div style="font-size: 12px; color: var(--muted); margin-bottom: 0.5rem">
					Website body text color (left) against website background (right).
				</div>
				<div class="palette-swatches-row">
					<div style="position: relative; margin-bottom: 20px">
						<div class="p-swatch" style="background: hsl(220, 15%, 55%); width: 80px"></div>
						<div class="p-swatch-label">Text</div>
					</div>
					<div style="position: relative; margin-bottom: 20px">
						<div
							class="p-swatch"
							style="background: hsl(220, 15%, 92%); width: 80px; border: 1px solid #ddd"
						></div>
						<div class="p-swatch-label">Background</div>
					</div>
				</div>
				<div
					style="
								padding: 1rem 1.25rem;
								background: hsl(220, 15%, 92%);
								border: 1px solid #ddd;
								margin: 0.5rem 0;
							"
				>
					<span
						style="
									color: hsl(220, 15%, 55%);
									font-size: 14px;
									font-family: 'IBM Plex Mono', monospace;
									line-height: 1.7;
								"
						>This is how your body text will appear to readers. It may feel sufficient on a bright
						monitor, but the contrast ratio here is approximately 2.8:1 — well below the WCAG AA
						requirement of 4.5:1.</span
					>
				</div>
				<div class="palette-q-text">
					What is the fastest typographic fix for this contrast failure?
				</div>
				<div class="palette-opts">
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 0, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 0, 0);
							}
						}}
					>
						A. Reduce the text lightness from 55% to approximately 30–35% — this alone will push the
						contrast ratio above 4.5:1 without any other changes
					</div>
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 1, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 1, 0);
							}
						}}
					>
						B. Add saturation to the text color so it appears more vivid against the background
					</div>
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 2, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 2, 0);
							}
						}}
					>
						C. Change the text hue to a complementary color to increase visual distinction
					</div>
					<div
						class="palette-opt"
						onclick={(e) => actions.handlePQ(e.currentTarget, 3, 0)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.handlePQ(e.currentTarget, 3, 0);
							}
						}}
					>
						D. Increase the font size so the large-text WCAG threshold (3:1) applies instead
					</div>
				</div>
				<div class="palette-feedback" id="pf-1"></div>
			</div>
		</div>
	</section>

	<!-- NAV -->
	<div class="nav-links">
		<a href="gd-module-03.html" class="prev-link">← Module 03: Typography</a>
		<a href="gd-module-05.html" class="next-module" style="flex: 1; max-width: 420px">
			<div>
				<div class="next-label">Next — Module 05</div>
				<div class="next-title">Shape Language &amp; Iconography</div>
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
		color: var(--sage);
		border: 1px solid var(--sage);
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
		color: var(--sage);
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
		color: var(--sage);
		border-color: var(--sage);
	}

	/* ── OBJECTIVES ── */
	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--sage);
		background: var(--surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--sage);
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
		color: var(--sage);
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

	/* ── CALLOUTS ── */
	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--sage);
		background: color-mix(in srgb, var(--sage) 5%, var(--surface));
		font-size: 13px;
	}
	:global(.callout.amber) {
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
	:global(.callout.violet) {
		border-color: var(--violet);
		background: color-mix(in srgb, var(--violet) 5%, var(--surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--sage);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	:global(.callout.amber) .callout-label {
		color: var(--amber);
	}
	:global(.callout.warn) .callout-label {
		color: var(--rose);
	}
	:global(.callout.sky) .callout-label {
		color: var(--sky);
	}
	:global(.callout.violet) .callout-label {
		color: var(--violet);
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
	:global(.demo-badge) {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	:global(.demo-badge.interactive) {
		color: var(--sage);
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	/* ── BUTTONS ── */
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
		border-color: var(--sage);
		color: var(--sage);
	}
	:global(.btn.active) {
		border-color: var(--sage);
		color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
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
	:global(.btn.sky:hover) {
		border-color: var(--sky);
		color: var(--sky);
	}
	:global(.btn.sky.active) {
		border-color: var(--sky);
		color: var(--sky);
		background: color-mix(in srgb, var(--sky) 10%, transparent);
	}

	/* ── SLIDERS ── */
	:global(.slider-row) {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 0.6rem 0;
	}
	:global(.slider-row) label {
		font-size: 12px;
		min-width: 110px;
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
		background: var(--sage);
		cursor: pointer;
	}
	:global(.slider-val) {
		font-size: 12px;
		color: var(--sage);
		min-width: 52px;
		text-align: right;
		font-weight: 600;
	}

	/* ── LAYOUT ── */
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

	/* ── TABLE ── */
	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--raised);
		color: var(--sage);
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
		color: var(--sage);
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
		color: var(--sage);
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
		margin-bottom: 1.5rem;
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
		background: var(--sage);
		width: 0;
		transition: width 0.4s ease;
	}

	/* ── DIVIDER ── */
	.divider {
		border: none;
		border-top: 1px solid var(--border);
		margin: 3rem 0;
	}

	/* ── NAV ── */
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
		border-color: var(--sage);
		color: var(--sage);
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

	/* ═══════════════════════════════════════
   DEMO-SPECIFIC
═══════════════════════════════════════ */

	/* HSL EXPLORER */
	.hsl-swatch-large {
		height: 140px;
		border: 1px solid var(--border);
		transition: background 0.15s;
		position: relative;
		overflow: hidden;
	}
	.hsl-overlay {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		padding: 0.75rem 1rem;
	}
	.hsl-hex-display {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		transition: color 0.15s;
	}
	.hsl-sub-display {
		font-size: 11px;
		opacity: 0.7;
		margin-top: 0.2rem;
	}
	.hsl-axis-strip {
		height: 12px;
		border-radius: 2px;
		margin: 0.3rem 0;
		border: 1px solid var(--border);
	}
	.hsl-axis-label {
		font-size: 9px;
		color: var(--muted);
		letter-spacing: 0.1em;
		text-transform: uppercase;
		margin-bottom: 0.2rem;
		margin-top: 0.5rem;
	}
	.hsl-meaning {
		font-size: 12px;
		color: var(--muted);
		min-height: 2.4em;
		margin-top: 0.5rem;
		line-height: 1.5;
		transition: color 0.2s;
	}

	/* COLOR WHEEL */
	#wheel-canvas {
		display: block;
		cursor: crosshair;
		border-radius: 50%;
	}
	.wheel-wrap {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem 0;
	}
	.harmony-swatches {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-top: 1rem;
	}
	:global(.h-swatch) {
		height: 48px;
		flex: 1;
		min-width: 60px;
		border: 1px solid var(--border);
		position: relative;
		cursor: default;
		transition: transform 0.15s;
	}
	:global(.h-swatch:hover) {
		transform: translateY(-2px);
	}
	:global(.h-swatch-label) {
		position: absolute;
		bottom: 4px;
		left: 0;
		right: 0;
		text-align: center;
		font-size: 9px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		font-family: 'IBM Plex Mono', monospace;
		mix-blend-mode: difference;
		color: #fff;
	}
	.harmony-desc {
		margin-top: 0.75rem;
		font-size: 12px;
		color: var(--muted);
		min-height: 2em;
		line-height: 1.6;
	}
	.harmony-btns {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-bottom: 1rem;
	}

	/* MOOD SWITCHER */
	.mood-stage {
		height: 220px;
		border: 1px solid var(--border);
		position: relative;
		overflow: hidden;
		transition: background 0.5s;
	}
	.mood-banner-text {
		position: absolute;
		left: 32px;
		top: 50%;
		transform: translateY(-50%);
	}
	.mood-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(26px, 4vw, 40px);
		font-weight: 800;
		line-height: 1.1;
		transition: color 0.4s;
	}
	.mood-sub {
		font-size: 12px;
		margin-top: 0.5rem;
		transition: color 0.4s;
	}
	.mood-tag {
		display: inline-block;
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
		margin-top: 0.75rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		transition: all 0.4s;
	}
	.mood-accent-bar {
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		width: 5px;
		transition: background 0.4s;
	}
	.mood-circle {
		position: absolute;
		right: -40px;
		top: 50%;
		transform: translateY(-50%);
		width: 200px;
		height: 200px;
		border-radius: 50%;
		opacity: 0.12;
		transition: background 0.4s;
	}
	.mood-palette-strip {
		display: flex;
		height: 24px;
		margin-top: 0.75rem;
		border: 1px solid var(--border);
		overflow: hidden;
	}
	.mood-strip-cell {
		flex: 1;
		transition: background 0.4s;
	}
	.mood-btns {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-bottom: 1rem;
	}
	.mood-explanation {
		font-size: 12px;
		color: var(--muted);
		margin-top: 0.75rem;
		min-height: 2.5em;
		line-height: 1.6;
	}

	/* CONTRAST CHECKER */
	.cc-preview-text {
		padding: 1.5rem 2rem;
		font-size: 16px;
		line-height: 1.7;
		border: 1px solid var(--border);
		transition: all 0.2s;
		font-family: 'Syne', sans-serif;
	}
	.cc-preview-large {
		font-size: 28px;
		font-weight: 700;
		margin-bottom: 0.5rem;
		transition: all 0.2s;
		font-family: 'Syne', sans-serif;
	}
	.cc-ratio-display {
		font-family: 'Syne', sans-serif;
		font-size: clamp(36px, 6vw, 56px);
		font-weight: 800;
		line-height: 1;
		transition: color 0.2s;
	}
	.cc-badges {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-top: 0.75rem;
	}
	:global(.cc-badge) {
		font-size: 11px;
		padding: 3px 10px;
		border: 1px solid;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		font-weight: 600;
	}
	:global(.cc-badge.pass) {
		color: var(--sage);
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
	}
	:global(.cc-badge.fail) {
		color: var(--rose);
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
	}
	.cc-presets {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-top: 0.75rem;
	}
	.cc-hue-strip {
		height: 10px;
		border-radius: 2px;
		margin: 0.25rem 0;
		border: 1px solid var(--border);
	}

	/* PALETTE QUIZ (assessment) */
	.palette-question {
		border: 1px solid var(--border);
		margin: 1.5rem 0;
	}
	.palette-q-header {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--border);
		background: var(--raised);
		font-size: 11px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.palette-q-body {
		padding: 1.25rem;
	}
	.palette-swatches-row {
		display: flex;
		gap: 0.5rem;
		margin: 0.75rem 0;
		flex-wrap: wrap;
	}
	.p-swatch {
		width: 52px;
		height: 52px;
		border: 1px solid var(--border);
		border-radius: 2px;
		position: relative;
	}
	.p-swatch-label {
		position: absolute;
		bottom: -18px;
		left: 0;
		right: 0;
		text-align: center;
		font-size: 9px;
		color: var(--muted);
		font-family: 'IBM Plex Mono', monospace;
	}
	.palette-q-text {
		font-size: 13px;
		color: #fff;
		margin: 0.75rem 0;
	}
	.palette-opts {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		margin-top: 0.75rem;
	}
	.palette-opt {
		padding: 0.55rem 1rem;
		border: 1px solid var(--border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		user-select: none;
		font-family: 'IBM Plex Mono', monospace;
	}
	.palette-opt:hover {
		border-color: var(--border2);
		background: var(--raised);
	}
	:global(.palette-opt.correct) {
		border-color: var(--sage);
		background: color-mix(in srgb, var(--sage) 10%, transparent);
		color: var(--sage);
		pointer-events: none;
	}
	:global(.palette-opt.wrong) {
		border-color: var(--rose);
		background: color-mix(in srgb, var(--rose) 10%, transparent);
		color: var(--rose);
		pointer-events: none;
	}
	:global(.palette-opt.disabled) {
		pointer-events: none;
	}
	.palette-feedback {
		font-size: 12px;
		margin-top: 0.5rem;
		min-height: 1.2em;
		color: var(--muted);
	}
	:global(.palette-feedback.ok) {
		color: var(--sage);
	}
	:global(.palette-feedback.bad) {
		color: var(--rose);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
