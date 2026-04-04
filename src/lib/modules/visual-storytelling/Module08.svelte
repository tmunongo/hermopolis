<script lang="ts">
	// @ts-nocheck
	/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any, no-undef, no-useless-assignment */
	import { onMount } from 'svelte';

	let actions: Record<string, any> = new Proxy(
		{},
		{
			get: (target: Record<string, any>, prop: string | symbol) => {
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

		const easeOut = (t) => 1 - Math.pow(1 - t, 3);
		const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
		const lerp = (a, b, t) => a + (b - a) * t;
		const clamp = (v, mn, mx) => Math.max(mn, Math.min(mx, v));

		/* ════════════════════════════════════════════
   CUT TYPE EXPLORER
════════════════════════════════════════════ */
		const cutTypes = [
			{
				id: 'hard',
				icon: '✂',
				name: 'Hard Cut',
				detail:
					'<strong>Hard Cut</strong> — The default. Two frames placed adjacent with no interpolation. Communicates confidence, continuity, and forward movement. The edit itself is invisible when the content justifies the change. Roughly 60–75% of all cuts in a well-edited educational video should be hard cuts.',
				anim(ctx, W, H, t) {
					// Scene A: blue gradient, then instant scene B: amber
					const cut = 0.45;
					if (t < cut) {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#0d1a2e');
						g.addColorStop(1, '#1a3050');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne,sans-serif`;
						ctx.fillStyle = 'rgba(74,175,255,0.6)';
						ctx.textAlign = 'center';
						ctx.fillText('SCENE A', W / 2, H / 2 + 8);
						// Countdown to cut
						const pct = t / cut;
						ctx.strokeStyle = '#ff4f6840';
						ctx.lineWidth = 1;
						ctx.strokeRect(W * 0.05, H * 0.05, W * 0.9 * pct, H * 0.04);
					} else {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#1a1000');
						g.addColorStop(1, '#2a1a00');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne,sans-serif`;
						ctx.fillStyle = 'rgba(245,185,74,0.6)';
						ctx.textAlign = 'center';
						ctx.fillText('SCENE B', W / 2, H / 2 + 8);
						// Flash at cut point
						if (t - cut < 0.06) {
							ctx.fillStyle = `rgba(255,255,255,${(1 - (t - cut) / 0.06) * 0.5})`;
							ctx.fillRect(0, 0, W, H);
						}
					}
				}
			},
			{
				id: 'dissolve',
				icon: '⊹',
				name: 'Cross-Dissolve',
				detail:
					'<strong>Cross-Dissolve</strong> — Outgoing fades while incoming fades in. Communicates time passing or a soft tonal shift. Correct for section transitions where the shift is significant but not abrupt. Incorrect as a default for all cuts — the interpolation costs attention without communicating anything when applied to normal content changes.',
				anim(ctx, W, H, t) {
					const transStart = 0.35,
						transEnd = 0.65;
					const draw = (alpha, isA) => {
						const g = ctx.createLinearGradient(0, 0, W, H);
						if (isA) {
							g.addColorStop(0, '#0d1a2e');
							g.addColorStop(1, '#1a3050');
						} else {
							g.addColorStop(0, '#0a1500');
							g.addColorStop(1, '#1a2a00');
						}
						ctx.globalAlpha = alpha;
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne,sans-serif`;
						ctx.fillStyle = isA ? 'rgba(74,175,255,0.7)' : 'rgba(61,217,164,0.7)';
						ctx.textAlign = 'center';
						ctx.fillText(isA ? 'SCENE A' : 'SCENE B', W / 2, H / 2 + 8);
						ctx.globalAlpha = 1;
					};
					if (t < transStart) {
						ctx.clearRect(0, 0, W, H);
						draw(1, true);
					} else if (t > transEnd) {
						ctx.clearRect(0, 0, W, H);
						draw(1, false);
					} else {
						const progress = (t - transStart) / (transEnd - transStart);
						ctx.clearRect(0, 0, W, H);
						draw(1 - progress, true);
						draw(progress, false);
						// Dissolve indicator
						ctx.font = `${W * 0.02}px IBM Plex Mono`;
						ctx.fillStyle = 'rgba(255,255,255,0.4)';
						ctx.textAlign = 'center';
						ctx.globalAlpha = 1;
						ctx.fillText(`dissolving… ${Math.round(progress * 100)}%`, W / 2, H * 0.88);
					}
				}
			},
			{
				id: 'jcut',
				icon: '↬',
				name: 'J-Cut',
				detail:
					'<strong>J-Cut</strong> — Audio of the incoming scene begins before its visual appears. The most effective transition for educational video: the viewer\'s attention is pulled into the new section before the visual cut arrives, nearly eliminating the disruption of the transition. The "J" shape comes from the audio track (new) overlapping under the outgoing visual. Master this before any visual transition.',
				anim(ctx, W, H, t) {
					const audioLead = 0.3,
						visualCut = 0.55;
					ctx.clearRect(0, 0, W, H);
					// Background
					if (t < visualCut) {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#0d1a2e');
						g.addColorStop(1, '#1a3050');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne,sans-serif`;
						ctx.fillStyle = 'rgba(74,175,255,0.6)';
						ctx.textAlign = 'center';
						ctx.fillText('VISUAL A', W / 2, H * 0.45);
					} else {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#100a1a');
						g.addColorStop(1, '#1a0f2a');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne,sans-serif`;
						ctx.fillStyle = 'rgba(167,139,250,0.6)';
						ctx.textAlign = 'center';
						ctx.fillText('VISUAL B', W / 2, H * 0.45);
					}
					// Audio track indicators
					const aW = W * 0.8,
						aX = W * 0.1,
						aY = H * 0.72;
					ctx.fillStyle = '#14202e';
					ctx.fillRect(aX, aY, aW, 14);
					// Audio A bar
					const aAend = visualCut * aW;
					ctx.fillStyle = 'rgba(74,175,255,0.4)';
					ctx.fillRect(aX, aY, aAend, 14);
					ctx.font = '8px IBM Plex Mono';
					ctx.fillStyle = '#4aafff';
					ctx.textAlign = 'left';
					ctx.fillText('AUDIO A', aX + 4, aY + 10);
					// Audio B bar — starts at audioLead
					if (t > audioLead) {
						const aBstart = audioLead * aW;
						const aBend = aW;
						ctx.fillStyle = 'rgba(167,139,250,0.5)';
						ctx.fillRect(aX + aBstart, aY, aBend - aBstart, 14);
						ctx.fillStyle = '#a78bfa';
						ctx.textAlign = 'center';
						ctx.fillText('AUDIO B (starts early)', aX + aBstart + (aBend - aBstart) / 2, aY + 10);
					}
					// Playhead
					const px = aX + t * aW;
					ctx.strokeStyle = '#ffffff80';
					ctx.lineWidth = 1.5;
					ctx.beginPath();
					ctx.moveTo(px, H * 0.68);
					ctx.lineTo(px, aY + 16);
					ctx.stroke();
					// Labels
					if (t > audioLead && t < visualCut) {
						ctx.font = `${W * 0.022}px IBM Plex Mono`;
						ctx.fillStyle = 'rgba(167,139,250,0.7)';
						ctx.textAlign = 'center';
						ctx.fillText('← audio B already playing', W / 2, H * 0.63);
					}
				}
			},
			{
				id: 'lcut',
				icon: '↫',
				name: 'L-Cut',
				detail:
					'<strong>L-Cut</strong> — The reverse of the J-cut: the visual of the new scene appears before its audio begins, while the audio of the outgoing scene continues. Useful when the outgoing narration is completing a thought while the viewer is already oriented in the new visual context. The "L" shape comes from the visual track (new) cutting before the audio follows.',
				anim(ctx, W, H, t) {
					const visualCut = 0.35,
						audioCut = 0.6;
					ctx.clearRect(0, 0, W, H);
					if (t < visualCut) {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#0d1a2e');
						g.addColorStop(1, '#1a3050');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne`;
						ctx.fillStyle = 'rgba(74,175,255,0.6)';
						ctx.textAlign = 'center';
						ctx.fillText('VISUAL A', W / 2, H * 0.45);
					} else {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#001a10');
						g.addColorStop(1, '#002a18');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						ctx.font = `700 ${W * 0.07}px Syne`;
						ctx.fillStyle = 'rgba(61,217,164,0.6)';
						ctx.textAlign = 'center';
						ctx.fillText('VISUAL B', W / 2, H * 0.45);
						if (t < audioCut) {
							ctx.font = `${W * 0.022}px IBM Plex Mono`;
							ctx.fillStyle = 'rgba(74,175,255,0.5)';
							ctx.textAlign = 'center';
							ctx.fillText('← audio A still playing', W / 2, H * 0.63);
						}
					}
					const aW = W * 0.8,
						aX = W * 0.1,
						aY = H * 0.72;
					ctx.fillStyle = '#14202e';
					ctx.fillRect(aX, aY, aW, 14);
					// Audio A continues past visual cut
					const aAend = audioCut * aW;
					ctx.fillStyle = 'rgba(74,175,255,0.4)';
					ctx.fillRect(aX, aY, aAend, 14);
					ctx.font = '8px IBM Plex Mono';
					ctx.fillStyle = '#4aafff';
					ctx.textAlign = 'left';
					ctx.fillText('AUDIO A (continues)', aX + 4, aY + 10);
					if (t > audioCut) {
						ctx.fillStyle = 'rgba(61,217,164,0.4)';
						ctx.fillRect(aX + audioCut * aW, aY, aW * (1 - audioCut), 14);
						ctx.fillStyle = '#3dd9a4';
						ctx.textAlign = 'left';
						ctx.fillText('AUDIO B', aX + audioCut * aW + 4, aY + 10);
					}
					const px = aX + t * aW;
					ctx.strokeStyle = '#ffffff80';
					ctx.lineWidth = 1.5;
					ctx.beginPath();
					ctx.moveTo(px, H * 0.68);
					ctx.lineTo(px, aY + 16);
					ctx.stroke();
				}
			},
			{
				id: 'match',
				icon: '⟷',
				name: 'Match Cut',
				detail:
					'<strong>Match Cut</strong> — A hard cut aligned on a visual or motion similarity between two shots: same shape, colour, movement direction, or composition. Communicates connection, equivalence, or parallel — two things that are related or that share a structure. Not always available, but when it is, it produces a powerful sense of meaning without any visual transition.',
				anim(ctx, W, H, t) {
					const cut = 0.45;
					const drawCircle = (col, x, y, r, label) => {
						const g = ctx.createRadialGradient(x, y, 0, x, y, r);
						g.addColorStop(0, col + 'cc');
						g.addColorStop(1, col + '20');
						ctx.beginPath();
						ctx.arc(x, y, r, 0, Math.PI * 2);
						ctx.fillStyle = g;
						ctx.fill();
						ctx.strokeStyle = col + '80';
						ctx.lineWidth = 2;
						ctx.stroke();
						ctx.font = `700 ${W * 0.02}px IBM Plex Mono`;
						ctx.fillStyle = '#fff';
						ctx.textAlign = 'center';
						ctx.fillText(label, x, y + 4);
					};
					ctx.clearRect(0, 0, W, H);
					if (t < cut) {
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#0d1a2e');
						g.addColorStop(1, '#1a3050');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						drawCircle('#4aafff', W / 2, H / 2, H * 0.25, 'EARTH');
						ctx.font = `${W * 0.022}px IBM Plex Mono`;
						ctx.fillStyle = '#4aafff50';
						ctx.textAlign = 'center';
						ctx.fillText('round shape → cuts to →', W / 2, H * 0.88);
					} else {
						const flash = Math.max(0, (0.06 - (t - cut)) / 0.06);
						const g = ctx.createLinearGradient(0, 0, W, H);
						g.addColorStop(0, '#1a0a0a');
						g.addColorStop(1, '#2a1010');
						ctx.fillStyle = g;
						ctx.fillRect(0, 0, W, H);
						if (flash > 0) {
							ctx.fillStyle = `rgba(255,255,255,${flash * 0.4})`;
							ctx.fillRect(0, 0, W, H);
						}
						drawCircle('#f5b94a', W / 2, H / 2, H * 0.22, 'SUN');
						ctx.font = `${W * 0.022}px IBM Plex Mono`;
						ctx.fillStyle = '#f5b94a50';
						ctx.textAlign = 'center';
						ctx.fillText('same shape → connection felt', W / 2, H * 0.88);
					}
				}
			},
			{
				id: 'fade',
				icon: '◐',
				name: 'Fade to Black',
				detail:
					'<strong>Fade to Black</strong> — Out to black, then in from black. The most emphatic structural signal in editing — it communicates a major break, the end of a chapter, or a moment of reflection. Use sparingly: 1–3 times per video maximum. Used more frequently, it loses all force and reads as a nervous editing habit rather than a deliberate signal.',
				anim(ctx, W, H, t) {
					const outEnd = 0.3,
						inStart = 0.5;
					ctx.clearRect(0, 0, W, H);
					let alpha = 1;
					if (t < outEnd) alpha = 1 - t / outEnd;
					else if (t < inStart) alpha = 0;
					else alpha = (t - inStart) / (1 - inStart);
					const isB = t > inStart;
					const g = ctx.createLinearGradient(0, 0, W, H);
					if (!isB) {
						g.addColorStop(0, '#0d1a2e');
						g.addColorStop(1, '#1a3050');
					} else {
						g.addColorStop(0, '#1a0a00');
						g.addColorStop(1, '#2a1800');
					}
					ctx.globalAlpha = alpha;
					ctx.fillStyle = g;
					ctx.fillRect(0, 0, W, H);
					ctx.font = `700 ${W * 0.07}px Syne`;
					ctx.fillStyle = isB ? 'rgba(245,185,74,0.6)' : 'rgba(74,175,255,0.6)';
					ctx.textAlign = 'center';
					ctx.fillText(isB ? 'CHAPTER B' : 'CHAPTER A', W / 2, H / 2 + 8);
					ctx.globalAlpha = 1;
					if (t >= outEnd && t <= inStart) {
						ctx.fillStyle = '#040710';
						ctx.fillRect(0, 0, W, H);
						ctx.font = `${W * 0.02}px IBM Plex Mono`;
						ctx.fillStyle = '#405068';
						ctx.textAlign = 'center';
						ctx.fillText('complete break — major structural signal', W / 2, H / 2);
					}
				}
			}
		];

		let currentCutType = 'hard';
		let cutAnimId = null;
		let cutPhase = 0;
		let cutStartTime = null;
		const CUT_DUR = 2200;

		function buildCutGrid() {
			const el = document.getElementById('cut-type-grid');
			el.innerHTML = cutTypes
				.map(
					(ct) =>
						`<div class="cut-type-cell${ct.id === currentCutType ? ' selected' : ''}" onclick="selectCutType('${ct.id}')">
      <div class="cut-type-icon">${ct.icon}</div>
      <div class="cut-type-name">${ct.name}</div>
    </div>`
				)
				.join('');
			document.getElementById('cut-detail').innerHTML = cutTypes.find(
				(c) => c.id === currentCutType
			).detail;
		}

		function selectCutType(id) {
			currentCutType = id;
			resetCut();
			buildCutGrid();
		}

		function initCutCanvas() {
			const canvas = document.getElementById('cut-canvas');
			const wrap = canvas.parentElement;
			const dpr = window.devicePixelRatio || 1;
			const W = wrap.offsetWidth || 560;
			const H = (W * 9) / 16;
			canvas.width = W * dpr;
			canvas.height = H * dpr;
			canvas.style.width = W + 'px';
			canvas.style.height = H + 'px';
			canvas.getContext('2d').scale(dpr, dpr);
		}

		function drawCutFrame(t) {
			const canvas = document.getElementById('cut-canvas');
			const W = parseInt(canvas.style.width) || 560;
			const H = parseInt(canvas.style.height) || 315;
			const ctx = canvas.getContext('2d');
			ctx.clearRect(0, 0, W, H);
			ctx.fillStyle = '#040710';
			ctx.fillRect(0, 0, W, H);
			const ct = cutTypes.find((c) => c.id === currentCutType);
			ct.anim(ctx, W, H, t);
		}

		function playCut() {
			if (cutAnimId) {
				resetCut();
				return;
			}
			document.getElementById('cut-play-btn').textContent = '■ Stop';
			cutStartTime = null;
			function tick(ts) {
				if (!cutStartTime) cutStartTime = ts;
				const t = Math.min(1, (ts - cutStartTime) / CUT_DUR);
				cutPhase = t;
				drawCutFrame(t);
				document.getElementById('cut-prog').style.width = t * 100 + '%';
				if (t < 1) cutAnimId = requestAnimationFrame(tick);
				else {
					cutAnimId = null;
					document.getElementById('cut-play-btn').textContent = '▶ Play';
				}
			}
			cutAnimId = requestAnimationFrame(tick);
		}

		function resetCut() {
			if (cutAnimId) cancelAnimationFrame(cutAnimId);
			cutAnimId = null;
			cutPhase = 0;
			cutStartTime = null;
			document.getElementById('cut-play-btn').textContent = '▶ Play';
			document.getElementById('cut-prog').style.width = '0%';
			drawCutFrame(0);
		}

		buildCutGrid();
		initCutCanvas();
		drawCutFrame(0);
		_addWinListener('resize', () => {
			initCutCanvas();
			drawCutFrame(cutPhase);
		});

		/* ════════════════════════════════════════════
   REDUNDANCY SCANNER
════════════════════════════════════════════ */
		const RS_SCRIPT = `In this video, I'm going to explain to you what cognitive bias is and I'm also going to show you how it works. So, basically, cognitive bias is, essentially, a systematic error in thinking. It basically means that the brain takes mental shortcuts, which are also sometimes called heuristics, that can lead to errors in judgement. So what I'm trying to say is that our brains don't always reason in a completely objective, unbiased way. The thing is, everyone is susceptible to cognitive bias, even very highly intelligent people and experts in their fields. What's really interesting, I think, is that these biases tend to operate below the level of conscious awareness, which basically means we're often not even aware that we're doing it. So, to summarise what I've just said: cognitive bias is a systematic error in thinking caused by mental shortcuts.`;

		let rsMode = 'redundant';
		const rsWords = RS_SCRIPT.split(/\s+/).map((w, i) => ({ text: w, idx: i, flag: null }));

		// Pre-defined auto-flags
		const autoFlags = {
			redundant: [
				0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 80,
				81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96
			],
			filler: [
				8, 9, 15, 16, 17, 34, 35, 36, 43, 44, 45, 46, 55, 56, 57, 58, 59, 60, 61, 67, 68, 69, 70,
				71, 72, 73, 74, 75, 76, 77, 78, 79
			]
		};

		function buildRSDisplay() {
			const el = document.getElementById('redund-script');
			el.innerHTML = rsWords
				.map(
					(w) =>
						`<span class="rs-word${w.flag ? ' flagged-' + w.flag : ''}" id="rsw-${w.idx}" onclick="toggleRSWord(${w.idx})">${w.text} </span>`
				)
				.join('');
			updateRSStats();
		}

		function setRSMode(mode) {
			rsMode = mode;
			['redundant', 'filler', 'keeper'].forEach((m) => {
				const btn = document.getElementById('rsm-' + m);
				btn.className = 'rs-mode-btn' + (mode === m ? ' on-' + m : '');
			});
		}

		function toggleRSWord(idx) {
			const w = rsWords[idx];
			if (w.flag === rsMode) w.flag = null;
			else w.flag = rsMode;
			buildRSDisplay();
		}

		function clearRS() {
			rsWords.forEach((w) => (w.flag = null));
			buildRSDisplay();
		}

		function autoFlagRS() {
			rsWords.forEach((w) => (w.flag = null));
			autoFlags.redundant.forEach((i) => {
				if (rsWords[i]) rsWords[i].flag = 'redundant';
			});
			autoFlags.filler.forEach((i) => {
				if (rsWords[i]) rsWords[i].flag = 'filler';
			});
			buildRSDisplay();
		}

		function updateRSStats() {
			const red = rsWords.filter((w) => w.flag === 'redundant').length;
			const fill = rsWords.filter((w) => w.flag === 'filler').length;
			const keep = rsWords.filter((w) => w.flag === 'keeper').length;
			const total = rsWords.length;
			const removed = red + fill;
			const pct = Math.round((removed / total) * 100);

			document.getElementById('rs-cnt-red').textContent = red;
			document.getElementById('rs-cnt-fill').textContent = fill;
			document.getElementById('rs-cnt-keep').textContent = keep;
			document.getElementById('rs-cnt-total').textContent = total;
			document.getElementById('rs-bar').style.width = pct + '%';
			document.getElementById('rs-pct').textContent = pct + '% removed';
			document.getElementById('rs-pct').style.color =
				pct > 40 ? '#ff4f68' : pct > 20 ? '#f5b94a' : '#3dd9a4';

			let verdict = '';
			if (removed === 0)
				verdict =
					'No flags yet. Use Auto-Flag to see the redundancies in this script, or flag manually in any mode.';
			else if (pct < 15)
				verdict = `${removed} words flagged (${pct}%). Low redundancy removal — the script still contains significant filler and restatement. Most first-draft scripts shed 25–40% in a thorough redundancy pass.`;
			else if (pct <= 40)
				verdict = `${removed} words flagged (${pct}%). Solid reduction. ${red} verbal redundancies and ${fill} filler phrases removed. The remaining ${total - removed} words should be load-bearing. Review the flagged regions — ensure no essential concept was removed along with the restatement.`;
			else
				verdict = `${removed} words flagged (${pct}%). Aggressive reduction — ensure the remaining content can still carry the full argument. Reductions above 40% often remove structural connective tissue along with the padding.`;

			document.getElementById('rs-verdict').textContent = verdict;
			document.getElementById('rs-verdict').style.borderLeftColor =
				pct > 40 ? '#ff4f68' : pct > 20 ? '#3dd9a4' : '#4aafff';
		}

		buildRSDisplay();
		setRSMode('redundant');

		/* ════════════════════════════════════════════
   TEMPORAL COMPRESSION LAB
════════════════════════════════════════════ */
		const tcModes = {
			raw: {
				label: 'Raw',
				dur: 90,
				color: '#ff4f68',
				compressionType: 'None',
				segments: [
					{ label: 'Wide intro', dur: 12, color: '#4aafff', type: 'setup' },
					{ label: 'Slow setup', dur: 10, color: '#405068', type: 'padding' },
					{ label: 'Concept A', dur: 14, color: '#f5b94a', type: 'content' },
					{ label: 'Waiting...', dur: 8, color: '#182033', type: 'dead' },
					{ label: 'Concept B', dur: 16, color: '#3dd9a4', type: 'content' },
					{ label: 'Repeat demo', dur: 10, color: '#405068', type: 'padding' },
					{ label: 'Insight', dur: 12, color: '#ff4f68', type: 'peak' },
					{ label: 'Long outro', dur: 8, color: '#182033', type: 'dead' }
				],
				verdict:
					'Unedited sequence. Contains all recorded material including setup padding, dead time, a repeated demonstration, and an over-extended outro. Total: 90 seconds. Viewer will begin drifting at ~35s.'
			},
			light: {
				label: 'Light Trim',
				dur: 62,
				color: '#f5b94a',
				compressionType: 'Gaps removed',
				segments: [
					{ label: 'Intro', dur: 8, color: '#4aafff', type: 'setup' },
					{ label: 'Setup', dur: 6, color: '#405068', type: 'padding' },
					{ label: 'Concept A', dur: 14, color: '#f5b94a', type: 'content' },
					{ label: 'Concept B', dur: 16, color: '#3dd9a4', type: 'content' },
					{ label: 'Demo', dur: 7, color: '#405068', type: 'padding' },
					{ label: 'Insight', dur: 11, color: '#ff4f68', type: 'peak' }
				],
				verdict:
					'Light trim — dead time and most padding removed. Intro shortened. Outro eliminated. Still contains the repeated demo segment at reduced length. 62s total. This is the minimum acceptable edit for most content.'
			},
			optimal: {
				label: 'Optimal',
				dur: 38,
				color: '#3dd9a4',
				compressionType: 'Gaps + redundancy',
				segments: [
					{ label: 'Hook', dur: 5, color: '#4aafff', type: 'setup' },
					{ label: 'Concept A', dur: 12, color: '#f5b94a', type: 'content' },
					{ label: 'Concept B', dur: 14, color: '#3dd9a4', type: 'content' },
					{ label: 'Insight', dur: 7, color: '#ff4f68', type: 'peak' }
				],
				verdict:
					'Optimal compression — all padding removed. Intro compressed to a hook (5s). Both content segments preserved in full. Demo redundancy removed — the concept was explained once, clearly. Insight gets its full weight. Outro replaced by a clean end on the insight. 38s total. This is the target.'
			},
			heavy: {
				label: 'Over-compressed',
				dur: 18,
				color: '#ff4f68',
				compressionType: 'Structural damage',
				segments: [
					{ label: 'Hook', dur: 3, color: '#4aafff', type: 'setup' },
					{ label: 'A+B', dur: 8, color: '#f5b94a', type: 'content' },
					{ label: 'Insight', dur: 7, color: '#ff4f68', type: 'peak' }
				],
				verdict:
					'⚠ Over-compressed — content segments A and B are merged and cut to 8s combined, losing the distinct logical structure of each idea. The viewer cannot build separate mental models for two concepts delivered in one rapid block. The insight arrives without adequate preparation and does not land. 18s total.'
			}
		};

		let currentTCMode = 'raw';
		let tcAnimId = null;

		function setTCMode(mode) {
			currentTCMode = mode;
			['raw', 'light', 'optimal', 'heavy'].forEach((m, i) => {
				const btn = document.querySelectorAll('#tc-mode-btns .btn')[i];
				btn.classList.remove('active', 'amber', 'red', 'mint');
				if (m === mode) {
					btn.classList.add('active');
					if (m === 'optimal') btn.classList.add('amber');
					else if (m === 'heavy') btn.classList.add('red');
				}
			});
			buildTCTracks();
			renderTCMetrics();
			document.getElementById('tc-verdict').textContent = tcModes[mode].verdict;
			document.getElementById('tc-verdict').style.borderLeftColor = tcModes[currentTCMode].color;
		}

		function buildTCTracks() {
			const m = tcModes[currentTCMode];
			const el = document.getElementById('tc-tracks');
			el.innerHTML = `
    <div class="tc-timeline" id="tc-track">
      <div class="tc-label" style="color:${m.color};">${m.label}</div>
      <div class="tc-clips" id="tc-clips-inner">
        ${m.segments
					.map((s) => {
						const w = (s.dur / m.dur) * 100;
						const isDead = s.type === 'dead' || s.type === 'padding';
						return `<div class="tc-clip" style="left:0;width:${w}%;background:color-mix(in srgb,${s.color} ${isDead ? 15 : 30}%,transparent);border:1px solid ${s.color}${isDead ? '30' : '60'};color:${s.color};position:relative;transition:none;">
            ${s.label}
          </div>`;
					})
					.join('')}
        <div class="tc-playhead" id="tc-ph"></div>
      </div>
    </div>`;
			// Reposition clips properly
			let left = 0;
			document.querySelectorAll('.tc-clip').forEach((el, i) => {
				const s = m.segments[i];
				const w = (s.dur / m.dur) * 100;
				el.style.left = left + '%';
				el.style.width = w + '%';
				el.style.position = 'absolute';
				left += w;
			});

			// Ruler
			const rulerEl = document.getElementById('tc-ruler');
			const ticks = Math.min(10, Math.ceil(m.dur / 10));
			const tickInterval = Math.ceil(m.dur / ticks / 5) * 5;
			const labels = [];
			for (let t = 0; t <= m.dur; t += tickInterval) labels.push(`${t}s`);
			rulerEl.innerHTML = labels.map((l, i) => `<span>${l}</span>`).join('');
		}

		function renderTCMetrics() {
			const m = tcModes[currentTCMode];
			const rawDur = 90;
			const el = document.getElementById('tc-metrics');
			const ratio = Math.round((1 - m.dur / rawDur) * 100);
			const contentDur = m.segments
				.filter((s) => s.type === 'content' || s.type === 'peak')
				.reduce((s, c) => s + c.dur, 0);
			const contentPct = Math.round((contentDur / m.dur) * 100);
			el.innerHTML = `
    <div class="tc-metric"><div class="tc-metric-val" style="color:${m.color};">${m.dur}s</div><div class="tc-metric-lbl">Duration</div></div>
    <div class="tc-metric"><div class="tc-metric-val" style="color:${m.color};">${ratio}%</div><div class="tc-metric-lbl">Compressed</div></div>
    <div class="tc-metric"><div class="tc-metric-val" style="color:${contentPct > 60 ? '#3dd9a4' : '#f5b94a'};">${contentPct}%</div><div class="tc-metric-lbl">Content %</div></div>
    <div class="tc-metric"><div class="tc-metric-val" style="color:${m.color};">${m.compressionType}</div><div class="tc-metric-lbl">Removed</div></div>`;
		}

		function playTC() {
			stopTC();
			document.getElementById('tc-play-btn').textContent = '■ Stop';
			const m = tcModes[currentTCMode];
			const dur = Math.min(4000, m.dur * 50); // speed up for demo
			let start = null;
			const ph = document.getElementById('tc-ph');
			const clips = document.getElementById('tc-clips-inner');
			if (ph) ph.style.opacity = '1';
			var _dup_tick = function (ts) {
				if (!start) start = ts;
				const t = Math.min(1, (ts - start) / dur);
				if (ph && clips) ph.style.left = t * clips.offsetWidth + 'px';
				document.getElementById('tc-prog').style.width = t * 100 + '%';
				document.getElementById('tc-time').textContent = Math.round(t * m.dur) + 's';
				if (t < 1) tcAnimId = requestAnimationFrame(tick);
				else {
					tcAnimId = null;
					document.getElementById('tc-play-btn').textContent = '▶ Play';
					if (ph) ph.style.opacity = '0';
				}
			};
			tcAnimId = requestAnimationFrame(tick);
		}

		function stopTC() {
			if (tcAnimId) cancelAnimationFrame(tcAnimId);
			tcAnimId = null;
			document.getElementById('tc-play-btn').textContent = '▶ Play';
			const ph = document.getElementById('tc-ph');
			if (ph) ph.style.opacity = '0';
			document.getElementById('tc-prog').style.width = '0%';
			document.getElementById('tc-time').textContent = '0s';
		}

		setTCMode('raw');

		/* ════════════════════════════════════════════
   EDIT DECISION ANALYZER
════════════════════════════════════════════ */
		const edaSegments = [
			{
				id: 0,
				label: 'Hook sequence',
				dur: 0.1,
				color: '#4aafff',
				type: 'Information cut',
				justification:
					'Opens with a provocative question — the hard cut from silence to content is correct.',
				verdict: 'keep',
				detail:
					'<strong>Information cut.</strong> The hook sequence opens the video with a question the viewer immediately wants answered. The hard cut is confident and direct — no transition needed because the viewer has no context to leave behind. Correct duration: short enough to establish urgency, long enough for the question to land.'
			},
			{
				id: 1,
				label: 'Long preamble',
				dur: 0.18,
				color: '#405068',
				type: 'Structural redundancy',
				justification: 'Creator explains what they are about to say — viewer does not need this.',
				verdict: 'remove',
				detail:
					"<strong>Structural redundancy.</strong> This segment explains the structure of the video before delivering it: \"In this video I'm going to cover three things — first, second, third.\" The viewer has already committed by watching the hook; this scaffolding serves the creator's organisation, not the viewer's comprehension. Recommended action: <strong>Remove</strong> — cut straight to the first concept."
			},
			{
				id: 2,
				label: 'Concept A',
				dur: 0.15,
				color: '#f5b94a',
				type: 'Information cut',
				justification: 'Dense explanatory content — cut arrives when the concept is complete.',
				verdict: 'keep',
				detail:
					'<strong>Information cut.</strong> First concept delivered cleanly. Duration is appropriate: dense enough to communicate the idea fully, not so long that the viewer begins to drift. The cut at the end arrives exactly when the concept closes — not before it is complete, not after it starts to trail.'
			},
			{
				id: 3,
				label: 'Repeat of A',
				dur: 0.12,
				color: '#ff4f68',
				type: 'Verbal redundancy',
				justification: 'Restates concept A in different words — adds no new dimension.',
				verdict: 'remove',
				detail:
					'<strong>Verbal redundancy.</strong> The narrator restates concept A with slightly different phrasing to "make sure" the viewer understood it. The viewer who understood does not need the restatement; the viewer who did not understand needs clarification, not repetition. Recommended action: <strong>Remove</strong> — if the concept was unclear, fix the explanation of A, not add a second version of it.'
			},
			{
				id: 4,
				label: 'Concept B',
				dur: 0.17,
				color: '#3dd9a4',
				type: 'Information cut',
				justification: "Second concept with J-cut lead from concept A's audio.",
				verdict: 'keep',
				detail:
					"<strong>Information cut with J-cut.</strong> The audio of concept B begins 1.5 seconds before its visual, creating a smooth transition from concept A without a structural pause. The viewer's attention is already orienting toward the new content before the visual arrives. Correct application of the J-cut for a within-section transition."
			},
			{
				id: 5,
				label: 'Tangent / aside',
				dur: 0.14,
				color: '#a78bfa',
				type: 'Structural redundancy',
				justification: 'Interesting but not load-bearing — disrupts momentum before the peak.',
				verdict: 'trim',
				detail:
					'<strong>Structural redundancy — tangent.</strong> The creator introduces an interesting but non-essential related idea, then loops back to the main thread. This is not incorrect information — it may genuinely be relevant. But it arrives immediately before the peak moment, at which point the viewer needs maximum forward momentum. Recommended action: <strong>Trim</strong> — reduce to one sentence or remove to a separate note. Do not develop a tangent immediately before the peak.'
			},
			{
				id: 6,
				label: 'Insight / peak',
				dur: 0.14,
				color: '#ff4f68',
				type: 'Emphasis cut',
				justification:
					'The most important moment — hard cut in, full duration, no competing elements.',
				verdict: 'keep',
				detail:
					'<strong>Emphasis cut.</strong> The peak insight delivered at full duration, with a hard cut in from the preceding content. No transition is used because the abruptness of the hard cut adds weight — the viewer is snapped to attention rather than floated in. Correct duration: long enough for the insight to settle, short enough to maintain the tension. This is the moment the entire video built toward.'
			}
		];

		let edaSelected = null;
		const edaDecisions = {};

		function buildEDATimeline() {
			const el = document.getElementById('eda-timeline');
			const totalW = el.offsetWidth || 700;
			el.innerHTML = edaSegments
				.map((s) => {
					const w = Math.round(s.dur * totalW);
					const dec = edaDecisions[s.id];
					const decColor =
						dec === 'keep'
							? '#3dd9a4'
							: dec === 'trim'
								? '#f5b94a'
								: dec === 'remove'
									? '#ff4f68'
									: 'transparent';
					const opacity = dec === 'remove' ? 0.3 : 1;
					return `<div class="eda-segment" id="edas-${s.id}" onclick="selectEDA(${s.id})"
      style="width:${w}px;height:68px;
      background:color-mix(in srgb,${s.color} ${edaSelected === s.id ? 25 : 15}%,transparent);
      border-right:2px solid ${edaSelected === s.id ? s.color : '#1e2d40'};
      border-top:3px solid ${edaSelected === s.id ? s.color : decColor};
      opacity:${opacity};">
      <div class="eda-segment-label" style="color:${s.color};font-size:${w > 80 ? '9' : '8'}px;padding:0 3px;">${s.label}</div>
      ${dec ? `<div class="eda-annotation" style="color:${decColor};">${dec.toUpperCase()}</div>` : ''}
      ${edaSelected === s.id ? `<div style="position:absolute;top:0;left:0;right:0;height:3px;background:${s.color};"></div>` : ''}
    </div>`;
				})
				.join('');
		}

		function selectEDA(id) {
			edaSelected = edaSelected === id ? null : id;
			buildEDATimeline();
			const seg = edaSegments.find((s) => s.id === id);
			if (seg) {
				document.getElementById('eda-detail').innerHTML =
					`<div style="color:var(--vs-amber); font-size:10px; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.3rem;">${seg.type}</div>` +
					`<div style="font-size:11px; color:var(--vs-muted); margin-bottom:0.4rem;">${seg.justification}</div>` +
					seg.detail;
				document.getElementById('eda-actions').style.display = 'flex';
			} else {
				document.getElementById('eda-detail').innerHTML =
					'<span style="color:var(--vs-muted);">Click a segment above to analyse its edit decision.</span>';
				document.getElementById('eda-actions').style.display = 'none';
			}
			updateEDAVerdict();
		}

		function edaAction(action) {
			if (edaSelected === null) return;
			edaDecisions[edaSelected] = action;
			buildEDATimeline();
			updateEDAVerdict();
		}

		function edaReset() {
			edaSelected = null;
			Object.keys(edaDecisions).forEach((k) => delete edaDecisions[k]);
			buildEDATimeline();
			document.getElementById('eda-detail').innerHTML =
				'<span style="color:var(--vs-muted);">Click a segment above to analyse its edit decision.</span>';
			document.getElementById('eda-actions').style.display = 'none';
			document.getElementById('eda-verdict').textContent =
				'Make decisions on each segment to build your edit analysis.';
		}

		function updateEDAVerdict() {
			const decided = Object.keys(edaDecisions).length;
			const total = edaSegments.length;
			const keeps = Object.values(edaDecisions).filter((d) => d === 'keep').length;
			const removes = Object.values(edaDecisions).filter((d) => d === 'remove').length;
			const trims = Object.values(edaDecisions).filter((d) => d === 'trim').length;
			// Check against expected
			const correct = edaSegments.filter((s) => edaDecisions[s.id] === s.verdict).length;

			if (decided === 0) {
				document.getElementById('eda-verdict').textContent =
					'Make decisions on each segment to build your edit analysis.';
				return;
			}
			let msg = `${decided}/${total} segments decided. Correct decisions: ${correct}/${decided}. `;
			if (decided < total) msg += `${total - decided} remaining.`;
			else {
				if (correct === total)
					msg +=
						'✓ All decisions correct. This edit preserves load-bearing content, removes verbal redundancy, trims the momentum-disrupting tangent, and keeps the structural emphasis of the peak cut.';
				else
					msg += `${total - correct} decision${total - correct !== 1 ? 's' : ''} differ from the recommended edit. Review the highlighted segments.`;
			}
			document.getElementById('eda-verdict').textContent = msg;
			document.getElementById('eda-verdict').style.borderLeftColor =
				correct === decided && decided > 0
					? '#3dd9a4'
					: correct > decided / 2
						? '#f5b94a'
						: '#ff4f68';
		}

		setTimeout(buildEDATimeline, 80);
		_addWinListener('resize', buildEDATimeline);

		/* ════════════════════════════════════════════
   MOMENTUM ARC BUILDER
════════════════════════════════════════════ */
		const momentumClipTypes = [
			{
				id: 'hook',
				label: 'Hook',
				color: '#4aafff',
				energy: 0.4,
				dur: 5,
				desc: 'Opening statement or question that establishes stakes.'
			},
			{
				id: 'setup',
				label: 'Setup',
				color: '#405068',
				energy: 0.3,
				dur: 8,
				desc: 'Context and background — necessary but low-intensity.'
			},
			{
				id: 'concept',
				label: 'Concept',
				color: '#f5b94a',
				energy: 0.6,
				dur: 12,
				desc: 'A single new idea or argument with supporting evidence.'
			},
			{
				id: 'example',
				label: 'Example',
				color: '#3dd9a4',
				energy: 0.55,
				dur: 8,
				desc: 'Concrete illustration making a concept tangible.'
			},
			{
				id: 'tension',
				label: 'Tension',
				color: '#ff4f68',
				energy: 0.8,
				dur: 6,
				desc: 'The problem, paradox, or challenge to be resolved.'
			},
			{
				id: 'insight',
				label: 'Insight',
				color: '#ff4f68',
				energy: 1.0,
				dur: 8,
				desc: 'The peak — the resolution or key realisation.'
			},
			{
				id: 'resolve',
				label: 'Resolve',
				color: '#a78bfa',
				energy: 0.35,
				dur: 5,
				desc: 'Brief landing — lets the insight settle.'
			},
			{
				id: 'filler',
				label: 'Filler ✕',
				color: '#182033',
				energy: 0.1,
				dur: 6,
				desc: 'Dead time — setup or restatement adding no energy.'
			}
		];
		let selectedMomentumType = 'hook';
		let momentumClips = [];

		function buildMomentumPalette() {
			const el = document.getElementById('momentum-palette');
			el.innerHTML = momentumClipTypes
				.map(
					(ct) =>
						`<div class="momentum-clip-chip${ct.id === selectedMomentumType ? ' selected' : ''}"
      style="border-color:${ct.color}; color:${ct.color}; ${ct.id === selectedMomentumType ? `background:color-mix(in srgb,${ct.color} 12%,transparent);` : ''}"
      onclick="selectMomentumType('${ct.id}')" title="${ct.desc}">
      ${ct.label}
    </div>`
				)
				.join('');
		}

		function selectMomentumType(id) {
			selectedMomentumType = id;
			buildMomentumPalette();
		}

		function initMomentumCanvas() {
			const canvas = document.getElementById('momentum-canvas');
			const W = canvas.offsetWidth || 560;
			const dpr = window.devicePixelRatio || 1;
			canvas.width = W * dpr;
			canvas.height = 200 * dpr;
			canvas.style.width = W + 'px';
			canvas.style.height = '200px';
			canvas.getContext('2d').scale(dpr, dpr);
			drawMomentumCanvas();
		}

		function drawMomentumCanvas() {
			const canvas = document.getElementById('momentum-canvas');
			const W = canvas.offsetWidth || 560;
			const H = 200;
			const ctx = canvas.getContext('2d');
			ctx.clearRect(0, 0, W, H);
			ctx.fillStyle = '#040710';
			ctx.fillRect(0, 0, W, H);

			const PAD_L = 8,
				PAD_R = 8,
				PAD_T = 16,
				PAD_B = 52;
			const CW = W - PAD_L - PAD_R;
			const CH = H - PAD_T - PAD_B;

			// Grid
			ctx.strokeStyle = '#14202e';
			ctx.lineWidth = 1;
			for (let i = 0; i <= 4; i++) {
				const y = PAD_T + (i / 4) * CH;
				ctx.beginPath();
				ctx.moveTo(PAD_L, y);
				ctx.lineTo(W - PAD_R, y);
				ctx.stroke();
			}
			ctx.font = '8px IBM Plex Mono';
			ctx.fillStyle = '#405068';
			ctx.textAlign = 'left';
			ctx.fillText('HIGH', PAD_L + 2, PAD_T + 8);
			ctx.fillText('LOW', PAD_L + 2, PAD_T + CH - 4);

			// Clips bar at bottom
			const totalDur =
				momentumClips.reduce(
					(s, c) => s + (momentumClipTypes.find((t) => t.id === c.type)?.dur || 8),
					0
				) || 1;
			let cx = PAD_L;
			momentumClips.forEach((clip, i) => {
				const ct = momentumClipTypes.find((t) => t.id === clip.type);
				if (!ct) return;
				const cw = (ct.dur / totalDur) * CW;
				ctx.fillStyle = `color-mix(in srgb,${ct.color} 30%,transparent)`;
				ctx.fillRect(cx, H - PAD_B + 4, cw - 1, PAD_B - 8);
				ctx.strokeStyle = ct.color + '80';
				ctx.lineWidth = 1;
				ctx.strokeRect(cx, H - PAD_B + 4, cw - 1, PAD_B - 8);
				if (cw > 22) {
					ctx.font = '8px IBM Plex Mono';
					ctx.fillStyle = ct.color;
					ctx.textAlign = 'center';
					ctx.fillText(ct.label.substring(0, 5), cx + cw / 2, H - PAD_B + PAD_B / 2 + 4);
				}
				cx += cw;
			});

			if (momentumClips.length === 0) {
				ctx.font = '11px IBM Plex Mono';
				ctx.fillStyle = '#405068';
				ctx.textAlign = 'center';
				ctx.fillText('Click to add clips — select a type from the palette above', W / 2, H / 2);
				return;
			}

			// Engagement curve
			let pos = 0;
			const curvePoints = [];
			let prevEnergy =
				momentumClipTypes.find((t) => t.id === momentumClips[0]?.type)?.energy || 0.3;
			curvePoints.push({ x: PAD_L, y: PAD_T + CH * (1 - prevEnergy * 0.9) });

			momentumClips.forEach((clip, i) => {
				const ct = momentumClipTypes.find((t) => t.id === clip.type);
				if (!ct) return;
				const cw = (ct.dur / totalDur) * CW;
				pos += cw;
				const energy = ct.energy * (1 - i * 0.02); // slight decay
				const y = PAD_T + CH * (1 - Math.min(1, energy * 0.92));
				// Smooth via control points
				const px = PAD_L + pos;
				curvePoints.push({ x: px, y: Math.max(PAD_T + 4, Math.min(PAD_T + CH - 4, y)) });
				prevEnergy = energy;
			});

			// Fill under curve
			ctx.beginPath();
			ctx.moveTo(curvePoints[0].x, PAD_T + CH);
			curvePoints.forEach((p, i) => {
				if (i === 0) {
					ctx.lineTo(p.x, p.y);
					return;
				}
				const prev = curvePoints[i - 1];
				const cpx = (prev.x + p.x) / 2;
				ctx.bezierCurveTo(cpx, prev.y, cpx, p.y, p.x, p.y);
			});
			ctx.lineTo(curvePoints[curvePoints.length - 1].x, PAD_T + CH);
			ctx.closePath();
			const grd = ctx.createLinearGradient(0, PAD_T, 0, PAD_T + CH);
			grd.addColorStop(0, 'rgba(255,79,104,0.25)');
			grd.addColorStop(1, 'rgba(255,79,104,0.02)');
			ctx.fillStyle = grd;
			ctx.fill();

			// Line
			ctx.beginPath();
			curvePoints.forEach((p, i) => {
				if (i === 0) {
					ctx.moveTo(p.x, p.y);
					return;
				}
				const prev = curvePoints[i - 1];
				const cpx = (prev.x + p.x) / 2;
				ctx.bezierCurveTo(cpx, prev.y, cpx, p.y, p.x, p.y);
			});
			ctx.strokeStyle = '#ff4f68';
			ctx.lineWidth = 2;
			ctx.stroke();

			// Ideal arc overlay (dashed)
			const idealPeak = 0.7;
			ctx.beginPath();
			ctx.moveTo(PAD_L, PAD_T + CH * 0.85);
			const ip = [
				{ x: PAD_L, y: PAD_T + CH * 0.85 },
				{ x: PAD_L + CW * 0.2, y: PAD_T + CH * 0.55 },
				{ x: PAD_L + CW * idealPeak, y: PAD_T + CH * 0.05 },
				{ x: PAD_L + CW * 0.85, y: PAD_T + CH * 0.35 },
				{ x: PAD_L + CW, y: PAD_T + CH * 0.55 }
			];
			ip.forEach((p, i) => {
				if (i === 0) {
					ctx.moveTo(p.x, p.y);
					return;
				}
				ctx.lineTo(p.x, p.y);
			});
			ctx.strokeStyle = 'rgba(255,255,255,0.12)';
			ctx.lineWidth = 1;
			ctx.setLineDash([4, 4]);
			ctx.stroke();
			ctx.setLineDash([]);
			ctx.font = '8px IBM Plex Mono';
			ctx.fillStyle = 'rgba(255,255,255,0.2)';
			ctx.textAlign = 'left';
			ctx.fillText('ideal arc', PAD_L + CW * 0.72, PAD_T + CH * 0.02);

			updateMomentumStats();
		}

		function updateMomentumStats() {
			if (momentumClips.length === 0) {
				['clips', 'duration', 'peak', 'shape'].forEach(
					(id) =>
						(document.getElementById('ms-' + id).textContent =
							id === 'clips' ? '0' : id === 'duration' ? '0s' : '—')
				);
				document.getElementById('momentum-verdict').textContent =
					'Place clips on the timeline to begin building your momentum arc.';
				return;
			}
			const totalDur = momentumClips.reduce(
				(s, c) => s + (momentumClipTypes.find((t) => t.id === c.type)?.dur || 8),
				0
			);
			document.getElementById('ms-clips').textContent = momentumClips.length;
			document.getElementById('ms-duration').textContent = totalDur + 's';

			// Peak position
			let pos = 0,
				peakPos = 0,
				peakEnergy = 0;
			momentumClips.forEach((clip) => {
				const ct = momentumClipTypes.find((t) => t.id === clip.type);
				if (!ct) return;
				pos += ct.dur;
				if (ct.energy > peakEnergy) {
					peakEnergy = ct.energy;
					peakPos = pos;
				}
			});
			const peakPct = Math.round((peakPos / totalDur) * 100);
			document.getElementById('ms-peak').textContent = peakPct + '%';
			document.getElementById('ms-peak').style.color =
				peakPct >= 60 && peakPct <= 80 ? '#3dd9a4' : peakPct > 80 ? '#f5b94a' : '#ff4f68';

			// Shape assessment
			const hasInsight = momentumClips.some((c) => c.type === 'insight');
			const hasHook = momentumClips[0]?.type === 'hook';
			const hasResolve = momentumClips[momentumClips.length - 1]?.type === 'resolve';
			const fillerCount = momentumClips.filter((c) => c.type === 'filler').length;
			let shape = '—',
				shapeColor = '#405068';
			if (hasInsight && peakPct >= 60 && peakPct <= 80 && fillerCount === 0) {
				shape = 'BUILD→PEAK';
				shapeColor = '#3dd9a4';
			} else if (peakPct < 50) {
				shape = 'FRONT-LOADED';
				shapeColor = '#f5b94a';
			} else if (peakPct > 80) {
				shape = 'BACK-LOADED';
				shapeColor = '#4aafff';
			} else if (fillerCount > 2) {
				shape = 'PADDED';
				shapeColor = '#ff4f68';
			} else {
				shape = 'DEVELOPING';
				shapeColor = '#4aafff';
			}
			document.getElementById('ms-shape').textContent = shape;
			document.getElementById('ms-shape').style.color = shapeColor;

			let verdict = '';
			if (shape === 'BUILD→PEAK')
				verdict = `✓ Well-formed arc — energy builds to a peak at ${peakPct}% of duration, within the target 65–75% range. The sequence has forward momentum throughout and a clear landing point. ${hasResolve ? 'Resolve segment correctly positioned at the end.' : 'Consider adding a brief resolve segment after the insight.'}`;
			else if (shape === 'FRONT-LOADED')
				verdict = `Peak arrives at ${peakPct}% — too early. The viewer reaches the high point before they have built adequate context and investment. After the peak, energy declines and the remaining content has no narrative destination. Move the insight later and build more context before it.`;
			else if (shape === 'PADDED')
				verdict = `${fillerCount} filler segment${fillerCount !== 1 ? 's' : ''} detected. Filler breaks momentum by providing extended periods of low-energy content that the viewer has no reason to sustain attention through. Remove or replace with content that actively advances the sequence.`;
			else if (shape === 'BACK-LOADED')
				verdict = `Peak at ${peakPct}% — late. The build phase is very long relative to the resolution phase, which can feel like the payoff was withheld too long. Consider shortening the build or moving the peak 5–10% earlier.`;
			else
				verdict = `${momentumClips.length} clips placed (${totalDur}s). Keep adding content to see your arc shape develop. Aim for: hook → build → concept(s) → tension → insight (at 65–75%) → resolve.`;

			document.getElementById('momentum-verdict').textContent = verdict;
			document.getElementById('momentum-verdict').style.borderLeftColor = shapeColor;
		}

		document.getElementById('momentum-canvas').addEventListener('click', function (e) {
			if (momentumClips.length >= 20) return;
			momentumClips.push({ type: selectedMomentumType, id: Date.now() });
			drawMomentumCanvas();
		});

		function clearMomentum() {
			momentumClips = [];
			drawMomentumCanvas();
		}

		function loadMomentumPreset(name) {
			momentumClips = [];
			const presets = {
				good: ['hook', 'setup', 'concept', 'example', 'tension', 'concept', 'insight', 'resolve'],
				flat: ['setup', 'concept', 'filler', 'concept', 'filler', 'concept', 'filler', 'resolve'],
				front: ['hook', 'tension', 'insight', 'concept', 'filler', 'concept', 'setup', 'resolve']
			};
			(presets[name] || []).forEach((t) =>
				momentumClips.push({ type: t, id: Date.now() + Math.random() })
			);
			drawMomentumCanvas();
		}

		buildMomentumPalette();
		initMomentumCanvas();
		_addWinListener('resize', initMomentumCanvas);

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

		if (typeof buildCutGrid === 'function') actions.buildCutGrid = buildCutGrid;
		if (typeof selectCutType === 'function') actions.selectCutType = selectCutType;
		if (typeof initCutCanvas === 'function') actions.initCutCanvas = initCutCanvas;
		if (typeof drawCutFrame === 'function') actions.drawCutFrame = drawCutFrame;
		if (typeof playCut === 'function') actions.playCut = playCut;
		if (typeof tick === 'function') actions.tick = tick;
		if (typeof resetCut === 'function') actions.resetCut = resetCut;
		if (typeof buildRSDisplay === 'function') actions.buildRSDisplay = buildRSDisplay;
		if (typeof setRSMode === 'function') actions.setRSMode = setRSMode;
		if (typeof toggleRSWord === 'function') actions.toggleRSWord = toggleRSWord;
		if (typeof clearRS === 'function') actions.clearRS = clearRS;
		if (typeof autoFlagRS === 'function') actions.autoFlagRS = autoFlagRS;
		if (typeof updateRSStats === 'function') actions.updateRSStats = updateRSStats;
		if (typeof setTCMode === 'function') actions.setTCMode = setTCMode;
		if (typeof buildTCTracks === 'function') actions.buildTCTracks = buildTCTracks;
		if (typeof renderTCMetrics === 'function') actions.renderTCMetrics = renderTCMetrics;
		if (typeof playTC === 'function') actions.playTC = playTC;
		if (typeof stopTC === 'function') actions.stopTC = stopTC;
		if (typeof buildEDATimeline === 'function') actions.buildEDATimeline = buildEDATimeline;
		if (typeof selectEDA === 'function') actions.selectEDA = selectEDA;
		if (typeof edaAction === 'function') actions.edaAction = edaAction;
		if (typeof edaReset === 'function') actions.edaReset = edaReset;
		if (typeof updateEDAVerdict === 'function') actions.updateEDAVerdict = updateEDAVerdict;
		if (typeof buildMomentumPalette === 'function')
			actions.buildMomentumPalette = buildMomentumPalette;
		if (typeof selectMomentumType === 'function') actions.selectMomentumType = selectMomentumType;
		if (typeof initMomentumCanvas === 'function') actions.initMomentumCanvas = initMomentumCanvas;
		if (typeof drawMomentumCanvas === 'function') actions.drawMomentumCanvas = drawMomentumCanvas;
		if (typeof updateMomentumStats === 'function')
			actions.updateMomentumStats = updateMomentumStats;
		if (typeof clearMomentum === 'function') actions.clearMomentum = clearMomentum;
		if (typeof loadMomentumPreset === 'function') actions.loadMomentumPreset = loadMomentumPreset;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			if (typeof cutAnimId !== 'undefined' && cutAnimId) cancelAnimationFrame(cutAnimId);
			if (typeof tcAnimId !== 'undefined' && tcAnimId) cancelAnimationFrame(tcAnimId);
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
		<div style="font-size: 11px; color: var(--vs-muted); text-align: right">Module 08 of 10</div>
	</header>

	<div class="module-hero">
		<div class="module-number">08</div>
		<div class="module-tag">Module 08 · Theory + Practice</div>
		<h1 class="module-title">Editing for<br /><span>Clarity &amp; Engagement</span></h1>
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
			<li><a href="#cuts-vs-transitions">Cuts vs Transitions</a></li>
			<li><a href="#cut-types">Cut Type Reference</a></li>
			<li><a href="#redundancy">Removing Redundancy</a></li>
			<li><a href="#temporal">Temporal Compression</a></li>
			<li><a href="#edit-decisions">Edit Decision Framework</a></li>
			<li><a href="#momentum">Building Momentum</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Distinguish hard cuts from transitions and know when each is the correct choice</li>
			<li>Apply temporal compression to tighten sequences without losing narrative clarity</li>
			<li>Identify and remove three categories of redundancy from a rough edit</li>
			<li>Build edit decision habits that treat every cut as a purposeful act, not a default</li>
			<li>
				Assemble a sequence with deliberate momentum — a felt arc of energy from open to close
			</li>
		</ul>
	</section>

	<!-- ═══ SECTION 1: CUTS VS TRANSITIONS ═══ -->
	<section id="cuts-vs-transitions" class="section">
		<div class="section-header">
			<span class="section-num">08.01</span>
			<h2 class="section-title">Hard Cuts vs Soft Transitions</h2>
		</div>

		<p>
			The cut is the fundamental unit of editing — two frames placed adjacent, the first ending and
			the second beginning with no interpolation. Most creators treat the cut as the default and
			transitions as upgrades: more polished, more professional, more sophisticated. This is
			precisely backwards. <strong>Hard cuts are the premium option.</strong> They are direct, confident,
			and rhythmically precise. Transitions are tools for specific communicative problems — they are not
			enhancements.
		</p>
		<p>
			A hard cut works when the information in the second shot is immediately interpretable in the
			context of the first — when the viewer's brain performs the connection between the two frames
			without effort. A cross-dissolve, a wipe, or a push transition works when that connection
			requires guidance: when time has passed, when context has shifted in a way the hard cut would
			not signal, or when continuity needs to be preserved across a jump that would otherwise feel
			jarring.
		</p>

		<div class="callout">
			<div class="callout-label">The Default Problem</div>
			The most common editing error in self-produced faceless video is applying the same transition type
			— usually a cross-dissolve — to every cut in the timeline. This is not style. It is the editor avoiding
			decisions. Every transition creates a small cognitive cost: the viewer must process the interpolation
			between states. Applied everywhere, that cost compounds into a video that feels sluggish and unconfident.
		</div>

		<p>
			The correct mental model is: start with hard cuts everywhere. Then review each cut and ask
			whether something specific is lost — a sense of time passing, a tonal shift, a spatial
			reorientation — that a transition would communicate. Add a transition only to answer a
			specific communicative need. The result is a timeline where every transition has a reason to
			exist, and the hard cuts (which will be most of them) feel clean and driven.
		</p>

		<!-- DEMO: Cut Type Explorer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Cut Type Explorer</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Select a cut or transition type. The canvas simulates the felt visual experience of that
					transition between two scenes. Use the Play button to observe the transition in motion.
				</p>

				<div class="cut-type-grid" id="cut-type-grid"></div>

				<div
					style="
								display: flex;
								gap: 0.75rem;
								margin-bottom: 1rem;
								align-items: center;
								flex-wrap: wrap;
							"
				>
					<button class="btn active" onclick={(e) => actions.playCut()} id="cut-play-btn"
						>▶ Play</button
					>
					<button class="btn" onclick={(e) => actions.resetCut()}>↺ Reset</button>
					<div
						style="
									flex: 1;
									height: 3px;
									background: var(--vs-border);
									overflow: hidden;
									min-width: 80px;
								"
					>
						<div id="cut-prog" style="height: 100%; background: var(--vs-red); width: 0%"></div>
					</div>
				</div>

				<div class="cut-stage">
					<canvas
						id="cut-canvas"
						aria-label="Cut Canvas Demonstration"
						role="application"
						tabindex="0"
					></canvas>
				</div>

				<div class="cut-detail" id="cut-detail" style="margin-top: 0.75rem; border-top: none"></div>
			</div>
		</div>
	</section>

	<!-- ═══ SECTION 2: CUT TYPE REFERENCE ═══ -->
	<section id="cut-types" class="section">
		<div class="section-header">
			<span class="section-num">08.02</span>
			<h2 class="section-title">Cut Types in Educational Faceless Video</h2>
		</div>

		<p>
			Educational faceless video uses a narrower range of cut and transition types than narrative
			film or commercial production. The vocabulary is constrained by function: almost everything
			either directly advances the explanation or is marking a structural boundary. Outside of these
			two purposes, any cut complexity is visual noise.
		</p>

		<table>
			<thead>
				<tr>
					<th>Type</th>
					<th>Visual Mechanic</th>
					<th>Communicates</th>
					<th>Use Frequency</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Hard cut</td>
					<td>Instant frame change</td>
					<td>Continuity, momentum, confidence</td>
					<td>60–75% of all cuts</td>
				</tr>
				<tr>
					<td>Match cut</td>
					<td>Hard cut aligned on visual or motion similarity</td>
					<td>Connection, equivalence, parallel</td>
					<td>5–10% — when available</td>
				</tr>
				<tr>
					<td>J-cut / L-cut</td>
					<td>Audio leads or trails the visual by 0.5–2s</td>
					<td>Smooth transition; audio bridges the gap</td>
					<td>10–20% of section transitions</td>
				</tr>
				<tr>
					<td>Cross-dissolve</td>
					<td>Outgoing fades while incoming fades in</td>
					<td>Time passing; soft tonal shift</td>
					<td>5–10% — section transitions only</td>
				</tr>
				<tr>
					<td>Fade to black</td>
					<td>Out to black; in from black</td>
					<td>Major break; chapter end; reflection</td>
					<td>1–3 times per video maximum</td>
				</tr>
				<tr>
					<td>Graphic wipe</td>
					<td>A shape reveals the new frame</td>
					<td>New section, energetic shift — brand-specific</td>
					<td>Consistent or never</td>
				</tr>
				<tr>
					<td>Push / slide</td>
					<td>Frame moves laterally or vertically</td>
					<td>Spatial relationship between two states</td>
					<td>Very sparingly — only when spatial logic applies</td>
				</tr>
			</tbody>
		</table>

		<div class="callout amber">
			<div class="callout-label">The J-Cut: The Most Underused Tool</div>
			The J-cut — where the audio of the incoming scene begins before its visual appears — is the single
			most effective transition in faceless educational video. It creates a seamless sense of forward
			movement: the viewer's attention is pulled into the next section by its audio before the visual
			confirms it. The cognitive disruption of the cut is almost eliminated because the brain has already
			started processing the new context. Master this one technique before reaching for any visual transition.
		</div>
	</section>

	<!-- ═══ SECTION 3: REMOVING REDUNDANCY ═══ -->
	<section id="redundancy" class="section">
		<div class="section-header">
			<span class="section-num">08.03</span>
			<h2 class="section-title">Removing Redundancy</h2>
		</div>

		<p>
			Redundancy in editing is any moment where what is present on screen or in the audio could be
			removed without the viewer losing information, understanding, or emotional connection. It is
			not the same as repetition — strategic repetition of a key concept is reinforcement, not
			redundancy. Redundancy is passive: it is content that exists because it was recorded, not
			because it is needed.
		</p>
		<p>
			Redundancy appears in three forms. <em>Verbal redundancy</em> — phrases and sentences that
			restate what was just said, usually arising from the narrator's desire to ensure clarity.
			<em>Visual redundancy</em> — footage or graphics that show what the narration is already
			describing at the same level of specificity, with no additional dimension.
			<em>Structural redundancy</em> — sections that exist as scaffolding for the creator's thinking process
			but add no value for the viewer: long setups, excessive caveats, and conclusions that restate the
			body rather than extending it.
		</p>

		<!-- DEMO: Redundancy Scanner -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Redundancy Scanner</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1rem">
					The script below contains all three types of redundancy. Select a flag mode and click
					individual words or phrases to mark them. The reduction meter shows how much tighter the
					script becomes.
				</p>

				<div
					style="
								display: flex;
								gap: 0.5rem;
								flex-wrap: wrap;
								margin-bottom: 1rem;
								align-items: center;
							"
				>
					<span
						style="
									font-size: 10px;
									letter-spacing: 0.1em;
									text-transform: uppercase;
									color: var(--vs-muted);
								">Flag mode:</span
					>
					<button
						class="rs-mode-btn"
						id="rsm-redundant"
						onclick={(e) => actions.setRSMode('redundant')}
					>
						✕ Verbal Redundancy
					</button>
					<button class="rs-mode-btn" id="rsm-filler" onclick={(e) => actions.setRSMode('filler')}>
						~ Filler / Hedge
					</button>
					<button class="rs-mode-btn" id="rsm-keeper" onclick={(e) => actions.setRSMode('keeper')}>
						✓ Essential
					</button>
					<button class="btn" onclick={(e) => actions.clearRS()} style="margin-left: auto"
						>Clear</button
					>
					<button class="btn active" onclick={(e) => actions.autoFlagRS()}>Auto-Flag</button>
				</div>

				<div class="redund-script" id="redund-script"></div>

				<div class="redund-stats">
					<div class="redund-chip" style="border-color: var(--vs-red); color: var(--vs-red)">
						<span class="chip-count" id="rs-cnt-red">0</span><span>Redundant</span>
					</div>
					<div class="redund-chip" style="border-color: var(--vs-amber); color: var(--vs-amber)">
						<span class="chip-count" id="rs-cnt-fill">0</span><span>Filler</span>
					</div>
					<div class="redund-chip" style="border-color: var(--vs-mint); color: var(--vs-mint)">
						<span class="chip-count" id="rs-cnt-keep">0</span><span>Essential</span>
					</div>
					<div class="redund-chip" style="border-color: var(--vs-blue); color: var(--vs-blue)">
						<span class="chip-count" id="rs-cnt-total">—</span><span>Words total</span>
					</div>
				</div>

				<div style="margin-top: 1rem">
					<div
						style="
									display: flex;
									justify-content: space-between;
									font-size: 11px;
									margin-bottom: 4px;
								"
					>
						<span style="color: var(--vs-muted)">Script reduction</span>
						<span id="rs-pct" style="color: var(--vs-red); font-weight: 600">0% removed</span>
					</div>
					<div
						style="
									height: 8px;
									background: var(--vs-border);
									border-radius: 4px;
									overflow: hidden;
								"
					>
						<div
							id="rs-bar"
							style="
										height: 100%;
										background: var(--vs-red);
										border-radius: 4px;
										width: 0%;
										transition: width 0.4s ease;
									"
						></div>
					</div>
				</div>
				<div
					id="rs-verdict"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								background: var(--vs-raised);
								min-height: 40px;
							"
				></div>
			</div>
		</div>

		<div class="callout mint">
			<div class="callout-label">The Minimum Viable Script</div>
			The test for a minimum viable script: read it aloud after removing everything you marked as redundant.
			If a viewer who has no prior knowledge of the topic can follow the argument without the removed
			content, the content was redundant. If they lose the thread, something essential was removed along
			with the redundancy. Restore only what is essential, not what is comfortable.
		</div>
	</section>

	<!-- ═══ SECTION 4: TEMPORAL COMPRESSION ═══ -->
	<section id="temporal" class="section">
		<div class="section-header">
			<span class="section-num">08.04</span>
			<h2 class="section-title">Temporal Compression &amp; Expansion</h2>
		</div>

		<p>
			Temporal compression is the editing of a real-time sequence to remove duration without
			removing information. It is not the same as cutting content — it is cutting
			<em>time</em> while preserving the content's logical and emotional integrity. A process that takes
			ten minutes in reality can be compressed to forty seconds of video without the viewer perceiving
			anything is missing — if the compression is applied at the correct points.
		</p>
		<p>
			The correct compression points are gaps: moments of transition, waiting, repetition, and setup
			that carry no new information. The incorrect compression points are the moments of actual
			change, insight, or reaction — these must be shown at or near their original duration to feel
			real. Compressing them creates the uncanny impression that the video has jumped, even if
			technically nothing is missing.
		</p>
		<p>
			<em>Temporal expansion</em> — dwelling longer than real-time on a moment — is the opposite tool.
			It is used for emphasis: a reaction, a result, a reveal that earns more than its natural duration
			because of the weight it carries in the narrative. Slow motion is the most literal form, but expansion
			can also be achieved through cut-away reactions, extended holds on a still frame, or repeating a
			key moment from a different angle.
		</p>

		<!-- DEMO: Temporal Compression Lab -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Temporal Compression Lab</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					A 90-second real-time sequence is shown in three compression modes. Each mode removes
					different types of duration. Toggle modes and run the playhead to feel the difference.
				</p>

				<div class="btn-row" id="tc-mode-btns">
					<button class="btn active" onclick={(e) => actions.setTCMode('raw')}>Raw (90s)</button>
					<button class="btn" onclick={(e) => actions.setTCMode('light')}>Light Trim (62s)</button>
					<button class="btn amber" onclick={(e) => actions.setTCMode('optimal')}
						>Optimal (38s)</button
					>
					<button class="btn red" onclick={(e) => actions.setTCMode('heavy')}
						>Over-compressed (18s)</button
					>
				</div>

				<div id="tc-tracks"></div>
				<div class="tc-ruler" id="tc-ruler"></div>

				<div
					style="
								display: flex;
								gap: 0.5rem;
								margin-top: 1rem;
								flex-wrap: wrap;
								align-items: center;
							"
				>
					<button class="btn active" onclick={(e) => actions.playTC()} id="tc-play-btn"
						>▶ Play</button
					>
					<button class="btn" onclick={(e) => actions.stopTC()}>■ Stop</button>
					<div
						style="
									flex: 1;
									height: 3px;
									background: var(--vs-border);
									overflow: hidden;
									min-width: 80px;
								"
					>
						<div
							id="tc-prog"
							style="height: 100%; background: var(--vs-red); width: 0%; transition: none"
						></div>
					</div>
					<span
						id="tc-time"
						style="font-size: 11px; color: var(--vs-muted); min-width: 36px; text-align: right"
						>0s</span
					>
				</div>

				<div class="tc-metrics" id="tc-metrics"></div>
				<div
					id="tc-verdict"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								background: var(--vs-raised);
								min-height: 40px;
							"
				></div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>What to compress</th>
					<th>What to preserve</th>
					<th>Warning signs of over-compression</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Transition periods between ideas</td>
					<td>Moments of change, reaction, insight</td>
					<td>Viewer loses spatial or temporal orientation</td>
				</tr>
				<tr>
					<td>Repetitive demonstrations of the same action</td>
					<td>The first and last instance of any repeated action</td>
					<td>Story feels like a highlight reel, not a sequence</td>
				</tr>
				<tr>
					<td>Setup time before the event</td>
					<td>The event itself at near-full duration</td>
					<td>Important moments feel rushed or abbreviated</td>
				</tr>
				<tr>
					<td>Explanatory scaffolding the viewer does not need</td>
					<td>All information required for the conclusion to land</td>
					<td>Conclusions arrive without adequate preparation</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══ SECTION 5: EDIT DECISION FRAMEWORK ═══ -->
	<section id="edit-decisions" class="section">
		<div class="section-header">
			<span class="section-num">08.05</span>
			<h2 class="section-title">The Edit Decision Framework</h2>
		</div>

		<p>
			Every cut in a timeline is an edit decision. The difference between an accidental cut and a
			purposeful one is not technical — it is intentional. A purposeful cut answers the question: <em
				>why does the viewer's attention need to change right now?</em
			> There are six valid answers, each corresponding to a different type of edit.
		</p>

		<!-- DEMO: Edit Decision Analyzer -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Edit Decision Analyzer</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					A sequence of seven segments is shown on the timeline. Click each segment to see its edit
					type, purpose, and whether the cut decision is justified. Then decide: Keep, Trim, or Cut.
				</p>

				<div
					id="eda-timeline"
					class="eda-timeline"
					style="height: 72px; white-space: nowrap; overflow-x: auto"
				></div>

				<div
					id="eda-detail"
					style="
								margin-top: 0.75rem;
								padding: 1rem;
								border: 1px solid var(--vs-border);
								background: #040710;
								font-size: 12px;
								line-height: 1.7;
								min-height: 80px;
							"
				>
					<span style="color: var(--vs-muted)"
						>Click a segment above to analyse its edit decision.</span
					>
				</div>

				<div
					id="eda-actions"
					style="display: none; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap"
				>
					<button class="btn mint" onclick={(e) => actions.edaAction('keep')} id="eda-keep"
						>✓ Keep</button
					>
					<button class="btn amber" onclick={(e) => actions.edaAction('trim')} id="eda-trim"
						>⊡ Trim</button
					>
					<button class="btn red" onclick={(e) => actions.edaAction('remove')}>✕ Remove</button>
					<button class="btn" onclick={(e) => actions.edaReset()}>Reset All</button>
				</div>

				<div class="eda-verdict" id="eda-verdict">
					Make decisions on each segment to build your edit analysis.
				</div>
			</div>
		</div>

		<table>
			<thead>
				<tr>
					<th>Edit Type</th>
					<th>Question It Answers</th>
					<th>Correct When</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Information cut</td>
					<td>New information requires a new visual context</td>
					<td>The current visual can no longer serve the narration's claim</td>
				</tr>
				<tr>
					<td>Pacing cut</td>
					<td>The current duration is too long for its content weight</td>
					<td>The segment has communicated its point and is now coasting</td>
				</tr>
				<tr>
					<td>Emphasis cut</td>
					<td>The incoming frame needs to land with impact</td>
					<td>A hard cut creates abruptness that serves the content's weight</td>
				</tr>
				<tr>
					<td>Tonal cut</td>
					<td>The emotional register of the content is changing</td>
					<td>A dissolve or audio lead bridges a shift that a hard cut would make jarring</td>
				</tr>
				<tr>
					<td>Structural cut</td>
					<td>A section is ending and a new section is beginning</td>
					<td>
						A clear visual and audio signal marks the boundary without interrupting momentum
					</td>
				</tr>
				<tr>
					<td>Compression cut</td>
					<td>Time has passed that does not need to be shown</td>
					<td>The intervening period contains no information or emotion the viewer needs</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ═══ SECTION 6: BUILDING MOMENTUM ═══ -->
	<section id="momentum" class="section">
		<div class="section-header">
			<span class="section-num">08.06</span>
			<h2 class="section-title">Building Momentum</h2>
		</div>

		<p>
			Momentum is the felt quality of forward movement in a sequence — the sensation that each
			moment is pulling toward the next, that something is at stake, and that the video is going
			somewhere. It is the macro-level quality that makes a viewer who pauses decide to unpause. It
			is built from the accumulation of micro-level edit decisions: each cut placed purposefully,
			each redundant moment removed, each transition earning its existence.
		</p>
		<p>
			The shape of momentum in a well-edited video is not linear. It follows a pattern: a build
			phase where energy and density increase, a peak where the most important content lands, and a
			resolution phase where the content settles and the viewer is released. The build and peak
			consume roughly 70% of the video's duration; the resolution is short — viewers who have
			reached the peak do not need a lengthy wind-down.
		</p>

		<!-- DEMO: Momentum Arc Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Momentum Arc Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Select a clip type and click the timeline to build a sequence. The engagement curve
					updates in real time as your edit decisions shape the arc. Aim for a build-peak-resolve
					shape.
				</p>

				<div class="momentum-clip-palette" id="momentum-palette"></div>

				<div class="momentum-canvas-wrap">
					<canvas
						id="momentum-canvas"
						height="200"
						aria-label="Momentum Canvas Demonstration"
						role="application"
						tabindex="0"
					></canvas>
				</div>

				<div style="display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap">
					<button class="btn" onclick={(e) => actions.clearMomentum()}>Clear</button>
					<button class="btn active" onclick={(e) => actions.loadMomentumPreset('good')}>
						Load: Good Arc
					</button>
					<button class="btn red" onclick={(e) => actions.loadMomentumPreset('flat')}
						>Load: Flat</button
					>
					<button class="btn amber" onclick={(e) => actions.loadMomentumPreset('front')}>
						Load: Front-Loaded
					</button>
				</div>

				<div class="momentum-stats" id="momentum-stats">
					<div class="momentum-stat">
						<div class="momentum-stat-val" id="ms-clips" style="color: var(--vs-red)">0</div>
						<div class="momentum-stat-lbl">Clips</div>
					</div>
					<div class="momentum-stat">
						<div class="momentum-stat-val" id="ms-duration" style="color: var(--vs-amber)">0s</div>
						<div class="momentum-stat-lbl">Duration</div>
					</div>
					<div class="momentum-stat">
						<div class="momentum-stat-val" id="ms-peak" style="color: var(--vs-blue)">—</div>
						<div class="momentum-stat-lbl">Peak at</div>
					</div>
					<div class="momentum-stat">
						<div class="momentum-stat-val" id="ms-shape" style="color: var(--vs-mint)">—</div>
						<div class="momentum-stat-lbl">Arc Shape</div>
					</div>
				</div>
				<div
					id="momentum-verdict"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								background: var(--vs-raised);
								min-height: 40px;
							"
				>
					Place clips on the timeline to begin building your momentum arc.
				</div>
			</div>
		</div>

		<div class="callout red">
			<div class="callout-label">The Last 20%</div>
			The most commonly over-extended section in self-produced video is the resolution. After the peak
			content lands, creators feel compelled to summarise, restate, and close formally — adding 20–40%
			to the video's length to say something the viewer already understood. The edit rule: end sooner
			than you think you should. If the insight has landed, the video is done. The summary that follows
			is the viewer's job, not yours.
		</div>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">08.07</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout">
			<div class="callout-label">Exercise A · Before/After Edit</div>
			Take a 60–90 second rough edit you have made or can source. Apply the full redundancy scanner process:
			mark every verbal, visual, and structural redundancy. Remove all marked content. Then review the
			result for over-compression — restore only what is essential. Submit (or note for yourself) the
			before and after duration, and write one sentence for each change explaining its type (verbal/visual/structural)
			and what was lost or preserved by making it.
		</div>

		<div class="callout amber">
			<div class="callout-label">Exercise B · Cut Type Audit</div>
			Open any 2–5 minute faceless video in an editing tool or watch it frame by frame. Mark every cut
			and label it with a type from the framework: hard cut, dissolve, J/L-cut, etc. Count the totals.
			Then assess: is the distribution consistent with the frequency guidelines in the table above? Are
			any transition types applied uniformly without regard to context? Write a one-sentence diagnosis
			for the most common inappropriate transition use you find.
		</div>

		<div class="callout blue">
			<div class="callout-label">Exercise C · Momentum Arc Analysis</div>
			Watch a video you consider to be well-edited — one where you stayed engaged from start to finish
			without wanting to skip. As you watch, mark on a piece of paper where the energy feels like it is
			building, where it peaks, and where it resolves. Then answer: where exactly did the peak occur as
			a percentage of the video's total duration? What edit choices produced the build — tighter cuts,
			shorter clips, increasing information density? And where did the resolution begin — was it too early,
			correct, or too late?
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
						<span class="stat-label">Hard cut</span><span class="stat-val">default; most edits</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">J-cut</span><span class="stat-val"
							>audio leads visual by 0.5–2s</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Verbal redundancy</span><span class="stat-val"
							>restates without adding</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Temporal compression</span><span class="stat-val"
							>removes time, not content</span
						>
					</div>
				</div>
				<div class="stats-panel">
					<div class="stat-row">
						<span class="stat-label">Six edit types</span><span class="stat-val"
							>info / pace / emphasis / tone / struct / compress</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Momentum arc</span><span class="stat-val"
							>build → peak → resolve</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Correct peak position</span><span class="stat-val"
							>~65–75% of duration</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Last 20% rule</span><span class="stat-val"
							>end sooner than feels right</span
						>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 08 — Check Your Understanding</div>
		<div class="quiz-sub">4 questions · No time limit</div>

		<div class="question" id="q1">
			<div class="q-text">
				<span class="q-num">01.</span>A creator applies a cross-dissolve to every cut in their
				timeline, reasoning that it makes the video feel more polished. What is the primary problem
				with this approach?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					Cross-dissolves are outdated — modern viewers expect hard cuts as the default professional
					style
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q1', e.currentTarget, true)}
				>
					Applying the same transition uniformly means no transition is communicating anything
					specific — each dissolve costs the viewer cognitive processing without providing a
					distinct signal, and the cumulative cost makes the video feel sluggish
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					Cross-dissolves interrupt the audio continuity, making it harder to follow narration
					across cuts
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					Using a consistent transition style is actually correct — it creates visual continuity and
					reduces cognitive friction
				</button>
			</div>
			<div class="feedback" id="fb-q1"></div>
		</div>

		<div class="question" id="q2">
			<div class="q-text">
				<span class="q-num">02.</span>In the J-cut technique, what happens and why is it effective
				for section transitions?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					The visual of the new section appears before its audio — giving the viewer a moment to
					read any new on-screen text before narration begins
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q2', e.currentTarget, true)}
				>
					The audio of the incoming section begins before its visual appears — because the auditory
					system registers change before the visual system does, this pulls the viewer's attention
					smoothly into the new section before the cut arrives, nearly eliminating the cognitive
					disruption of the transition
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					The cut is aligned to a matching visual element in both the outgoing and incoming frames —
					creating a perceptual bridge between the two shots
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					The outgoing audio fades out as the incoming visual fades in — combining a fade with a cut
					for a hybrid transition effect
				</button>
			</div>
			<div class="feedback" id="fb-q2"></div>
		</div>

		<div class="question" id="q3">
			<div class="q-text">
				<span class="q-num">03.</span>What is the correct point in a sequence to apply temporal
				compression, and what should be preserved at near-full duration?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					Compress the peak moments and expand the setup — viewers need time to understand context
					before the important content
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					Compress uniformly across the sequence — consistent pacing avoids the jarring feeling of
					uneven cuts
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q3', e.currentTarget, true)}
				>
					Compress transition periods, waiting time, and repetition — preserve moments of actual
					change, insight, and reaction at near-full duration, because compressing these creates the
					uncanny impression of jumping even when nothing informational is removed
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					Compress the opening and closing — viewers' attention is lowest at the start and end, so
					those sections can be shorter
				</button>
			</div>
			<div class="feedback" id="fb-q3"></div>
		</div>

		<div class="question" id="q4">
			<div class="q-text">
				<span class="q-num">04.</span>In a well-structured momentum arc, where should the peak
				content position fall as a percentage of the video's total duration?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					At the 50% mark — directly in the middle, creating symmetric build and resolve phases
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					At the very end — content should build continuously with the peak as the final moment
					before a brief close
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q4', e.currentTarget, true)}
				>
					Around 65–75% of the total duration — the build phase is longer than the resolve; after
					the peak lands, the viewer needs only a brief resolution, not a full restatement
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					At 33% — early peaks capture attention before it begins to decay, leaving the rest of the
					video for consolidation
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
		<a href="./07" class="prev-link">← Module 07: Audio as a Narrative Anchor</a>
		<a href="./09" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">Building a Repeatable Visual Language</div>
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
			rgba(255, 79, 104, 0.013) 2px,
			rgba(255, 79, 104, 0.013) 4px
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
	.callout.amber {
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-surface));
	}
	.callout.blue {
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 5%, var(--vs-surface));
	}
	.callout.mint {
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
	.callout.amber .callout-label {
		color: var(--vs-amber);
	}
	.callout.blue .callout-label {
		color: var(--vs-blue);
	}
	.callout.mint .callout-label {
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
	.demo-badge {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	.demo-badge.interactive {
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
		color: var(--vs-blue);
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
		border-color: var(--vs-mint);
		color: var(--vs-mint);
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

	/* ══════════════════════════════
     MODULE-SPECIFIC COMPONENTS
  ══════════════════════════════ */

	/* ── CUT TYPE EXPLORER ── */
	.cut-stage {
		aspect-ratio: 16/9;
		background: #040710;
		border: 1px solid var(--vs-border2);
		overflow: hidden;
		position: relative;
	}
	.cut-stage canvas {
		display: block;
		width: 100%;
		height: 100%;
	}
	.cut-type-grid {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1px;
		background: var(--vs-border);
		margin-bottom: 0.75rem;
	}
	@media (max-width: 600px) {
		.cut-type-grid {
			grid-template-columns: 1fr 1fr;
		}
	}
	.cut-type-cell {
		background: var(--vs-raised);
		padding: 0.75rem;
		cursor: pointer;
		transition: all 0.15s;
		border: 2px solid transparent;
		text-align: center;
	}
	.cut-type-cell:hover {
		border-color: var(--vs-border2);
	}
	.cut-type-cell.selected {
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 8%, var(--vs-raised));
	}
	.cut-type-icon {
		font-size: 20px;
		margin-bottom: 4px;
	}
	.cut-type-name {
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--vs-muted);
	}
	.cut-type-cell.selected .cut-type-name {
		color: var(--vs-red);
	}
	.cut-detail {
		padding: 0.75rem 1rem;
		border-left: 2px solid var(--vs-red);
		font-size: 12px;
		color: var(--vs-text);
		line-height: 1.7;
		background: color-mix(in srgb, var(--vs-red) 4%, var(--vs-surface));
		min-height: 56px;
	}
	.cut-detail strong {
		color: var(--vs-red);
	}

	/* ── REDUNDANCY SCANNER ── */
	.redund-script {
		background: #040710;
		border: 1px solid var(--vs-border);
		padding: 1.25rem;
		font-size: 13px;
		line-height: 2;
		position: relative;
	}
	.rs-word {
		display: inline;
		padding: 1px 3px;
		border-radius: 2px;
		cursor: pointer;
		transition: all 0.15s;
		user-select: none;
	}
	.rs-word:hover {
		background: var(--vs-dim);
	}
	.rs-word.flagged-redundant {
		background: color-mix(in srgb, var(--vs-red) 20%, transparent);
		color: var(--vs-red);
		text-decoration: line-through;
		opacity: 0.7;
	}
	.rs-word.flagged-filler {
		background: color-mix(in srgb, var(--vs-amber) 18%, transparent);
		color: var(--vs-amber);
	}
	.rs-word.flagged-keeper {
		background: color-mix(in srgb, var(--vs-mint) 14%, transparent);
		color: var(--vs-mint);
	}
	.redund-stats {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		margin-top: 1rem;
	}
	.redund-chip {
		padding: 4px 12px;
		border: 1px solid;
		font-size: 11px;
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.redund-chip .chip-count {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		line-height: 1;
	}
	.rs-mode-btn {
		padding: 4px 10px;
		border: 1px solid var(--vs-border2);
		font-size: 10px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		cursor: pointer;
		font-family: 'IBM Plex Mono', monospace;
		background: transparent;
		transition: all 0.15s;
		color: var(--vs-muted);
	}
	.rs-mode-btn.on-redundant {
		border-color: var(--vs-red);
		color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
	}
	.rs-mode-btn.on-filler {
		border-color: var(--vs-amber);
		color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	.rs-mode-btn.on-keeper {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
	}

	/* ── TEMPORAL COMPRESSION ── */
	.tc-timeline {
		position: relative;
		height: 56px;
		background: var(--vs-raised);
		border: 1px solid var(--vs-border);
		margin: 0.5rem 0;
		overflow: hidden;
	}
	.tc-label {
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		width: 72px;
		display: flex;
		align-items: center;
		padding: 0 8px;
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--vs-muted);
		border-right: 1px solid var(--vs-border);
		background: var(--vs-raised);
		z-index: 2;
	}
	.tc-clips {
		position: absolute;
		left: 72px;
		right: 0;
		top: 6px;
		bottom: 6px;
	}
	.tc-clip {
		position: absolute;
		top: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 9px;
		font-weight: 600;
		letter-spacing: 0.05em;
		border-radius: 1px;
		overflow: hidden;
		white-space: nowrap;
		padding: 0 4px;
		transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
	}
	.tc-cut-line {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 2px;
		z-index: 3;
		transition: left 0.5s cubic-bezier(0.4, 0, 0.2, 1);
	}
	.tc-playhead {
		position: absolute;
		top: -2px;
		bottom: -2px;
		width: 2px;
		background: #fff;
		opacity: 0;
		z-index: 4;
		box-shadow: 0 0 6px rgba(255, 255, 255, 0.5);
		transition: left 0.04s linear;
	}
	.tc-ruler {
		display: flex;
		justify-content: space-between;
		font-size: 9px;
		color: var(--vs-muted);
		padding: 2px 0 0 72px;
	}
	.tc-metrics {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr;
		gap: 1px;
		background: var(--vs-border);
		margin-top: 0.75rem;
	}
	.tc-metric {
		background: var(--vs-raised);
		padding: 0.5rem 0.75rem;
		text-align: center;
	}
	.tc-metric-val {
		font-family: 'Syne', sans-serif;
		font-size: 20px;
		font-weight: 700;
		line-height: 1;
	}
	.tc-metric-lbl {
		font-size: 9px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--vs-muted);
		margin-top: 3px;
	}

	/* ── EDIT DECISION ANALYZER ── */
	.eda-timeline {
		position: relative;
		background: #040710;
		border: 1px solid var(--vs-border);
		overflow: hidden;
		user-select: none;
	}
	.eda-segment {
		display: inline-flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		position: relative;
		cursor: pointer;
		transition: all 0.2s;
		vertical-align: top;
		overflow: hidden;
	}
	.eda-segment:hover {
		filter: brightness(1.2);
	}
	.eda-segment-label {
		font-size: 9px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		text-align: center;
		line-height: 1.3;
		pointer-events: none;
	}
	.eda-cut-marker {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 3px;
		background: rgba(255, 255, 255, 0.5);
		right: 0;
		z-index: 2;
		transition: all 0.2s;
	}
	.eda-annotation {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		font-size: 8px;
		background: rgba(0, 0, 0, 0.7);
		padding: 2px 4px;
		text-align: center;
		pointer-events: none;
	}
	.eda-verdict {
		margin-top: 0.75rem;
		padding: 0.75rem 1rem;
		border-left: 2px solid var(--vs-border2);
		font-size: 12px;
		color: var(--vs-text);
		line-height: 1.7;
		background: var(--vs-raised);
		min-height: 44px;
	}

	/* ── MOMENTUM BUILDER ── */
	.momentum-canvas-wrap {
		position: relative;
	}
	#momentum-canvas {
		display: block;
		width: 100%;
		cursor: pointer;
		border: 1px solid var(--vs-border);
		background: #040710;
	}
	.momentum-clip-palette {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}
	.momentum-clip-chip {
		padding: 5px 12px;
		border: 1px solid;
		font-size: 11px;
		cursor: pointer;
		transition: all 0.15s;
		user-select: none;
	}
	.momentum-clip-chip.selected {
		opacity: 1;
	}
	.momentum-clip-chip:not(.selected) {
		opacity: 0.5;
	}
	.momentum-stats {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr;
		gap: 1px;
		background: var(--vs-border);
		margin-top: 0.75rem;
	}
	.momentum-stat {
		background: var(--vs-raised);
		padding: 0.5rem 0.75rem;
		text-align: center;
	}
	.momentum-stat-val {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		line-height: 1;
	}
	.momentum-stat-lbl {
		font-size: 9px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--vs-muted);
		margin-top: 3px;
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
