<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, no-undef */
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
			if (!el) return;
			const docH = document.documentElement.scrollHeight - window.innerHeight;
			el.style.width = Math.min(100, (window.scrollY / docH) * 100) + '%';
		});

		/* ═══════════════════════════════════
   CADENCE WHEEL
═══════════════════════════════════ */
		const cadenceLevels = {
			micro: {
				label: 'Micro Level',
				desc: 'Governs individual clip durations and cut timing — the moment-to-moment texture of the video. At this level, you decide how long to hold on a single image, when a cut arrives relative to a word in narration, and how text appears on screen.',
				examples: [
					'Cut lands on stressed syllable → feels punchy',
					'Hold 2s after narration ends → feels settled',
					'Text appears 0.3s before narration → anticipatory'
				],
				segments: [
					{ label: 'CUT', angle: 0, color: '#f5b94a', r: 58 },
					{ label: 'HOLD', angle: 80, color: '#4aafff', r: 68 },
					{ label: 'TEXT', angle: 165, color: '#3dd9a4', r: 52 },
					{ label: 'PAUSE', angle: 250, color: '#ff4f68', r: 60 },
					{ label: 'CUT', angle: 315, color: '#f5b94a', r: 48 }
				]
			},
			section: {
				label: 'Section Level',
				desc: 'Governs the density and airiness of each content block. How many ideas per minute in this section? How long is the transition between topics? What signals mark the end of one section and the start of another?',
				examples: [
					'Dense section → airy transition → next dense section',
					'Section title card = explicit chunk boundary signal',
					'Longer pauses after complex sections'
				],
				segments: [
					{ label: 'DENSE', angle: 10, color: '#ff4f68', r: 72 },
					{ label: 'TRANS', angle: 100, color: '#f5b94a', r: 48 },
					{ label: 'DENSE', angle: 170, color: '#ff4f68', r: 68 },
					{ label: 'BREATH', angle: 250, color: '#3dd9a4', r: 55 },
					{ label: 'DENSE', angle: 320, color: '#ff4f68', r: 60 }
				]
			},
			macro: {
				label: 'Macro Level',
				desc: 'Governs the overall energy shape of the entire video — how it opens, where it accelerates, where tension releases, and how it ends. The macro shape determines whether the viewer finishes with a feeling of satisfaction or incompleteness.',
				examples: [
					'Low → build → peak → release → insight',
					'Flat macro shape = the most common fatal flaw',
					'Endings should always decelerate, not stop'
				],
				segments: [
					{ label: 'OPEN', angle: 20, color: '#4aafff', r: 50 },
					{ label: 'BUILD', angle: 90, color: '#f5b94a', r: 62 },
					{ label: 'PEAK', angle: 165, color: '#ff4f68', r: 80 },
					{ label: 'FALL', angle: 235, color: '#3dd9a4', r: 65 },
					{ label: 'LAND', angle: 305, color: '#4aafff', r: 45 }
				]
			}
		};

		let currentCadLevel = 'micro';

		function setCadenceLevel(level) {
			currentCadLevel = level;
			['micro', 'section', 'macro'].forEach((l) => {
				document.getElementById('cad-' + l).classList.toggle('active', l === level);
			});
			drawCadenceWheel();
			const d = cadenceLevels[level];
			document.getElementById('cadence-title').textContent = d.label;
			document.getElementById('cadence-desc').textContent = d.desc;
			document.getElementById('cadence-examples').innerHTML = d.examples
				.map(
					(e) =>
						`<div style="padding-left:1rem; position:relative;"><span style="position:absolute;left:0;color:var(--vs-amber);">·</span>${e}</div>`
				)
				.join('');
		}

		function drawCadenceWheel() {
			const canvas = document.getElementById('cadence-canvas');
			const ctx = canvas.getContext('2d');
			const dpr = window.devicePixelRatio || 1;
			canvas.width = 200 * dpr;
			canvas.height = 200 * dpr;
			ctx.scale(dpr, dpr);
			ctx.clearRect(0, 0, 200, 200);
			const cx = 100,
				cy = 100;

			// Rings
			for (let r = 20; r <= 90; r += 20) {
				ctx.beginPath();
				ctx.arc(cx, cy, r, 0, Math.PI * 2);
				ctx.strokeStyle = '#14202e';
				ctx.lineWidth = 1;
				ctx.stroke();
			}

			const segs = cadenceLevels[currentCadLevel].segments;
			segs.forEach((seg) => {
				const rad = ((seg.angle - 90) * Math.PI) / 180;
				const x = cx + Math.cos(rad) * seg.r;
				const y = cy + Math.sin(rad) * seg.r;

				// Spoke
				ctx.beginPath();
				ctx.moveTo(cx, cy);
				ctx.lineTo(x, y);
				ctx.strokeStyle = seg.color + '40';
				ctx.lineWidth = 1;
				ctx.stroke();

				// Dot
				ctx.beginPath();
				ctx.arc(x, y, 5, 0, Math.PI * 2);
				ctx.fillStyle = seg.color;
				ctx.fill();

				// Label
				ctx.font = '8px IBM Plex Mono';
				ctx.fillStyle = seg.color;
				ctx.textAlign = 'center';
				const lx = cx + Math.cos(rad) * (seg.r + 14);
				const ly = cy + Math.sin(rad) * (seg.r + 14);
				ctx.fillText(seg.label, lx, ly + 3);
			});

			// Centre dot
			ctx.beginPath();
			ctx.arc(cx, cy, 4, 0, Math.PI * 2);
			ctx.fillStyle = '#fff';
			ctx.fill();
		}

		setCadenceLevel('micro');

		/* ═══════════════════════════════════
   BEAT MAP BUILDER
═══════════════════════════════════ */
		let beats = [];
		let currentBeatType = 'cut';
		const beatColors = { cut: '#f5b94a', text: '#4aafff', audio: '#3dd9a4', peak: '#ff4f68' };
		const beatLabels = { cut: '✂', text: 'T', audio: '♪', peak: '●' };
		const DURATION = 180; // seconds

		function setBeatType(type) {
			currentBeatType = type;
			['cut', 'text', 'audio', 'peak'].forEach((t) => {
				const btn = document.getElementById('bbt-' + t);
				btn.classList.toggle('active', t === type);
				if (t === 'peak') {
					btn.classList.toggle('red', t === type);
				}
			});
		}

		function getCanvasSize() {
			const canvas = document.getElementById('beatmap-canvas');
			return { w: canvas.offsetWidth, h: canvas.offsetHeight };
		}

		function initBeatmapCanvas() {
			const canvas = document.getElementById('beatmap-canvas');
			const dpr = window.devicePixelRatio || 1;
			const w = canvas.offsetWidth || 600;
			canvas.width = w * dpr;
			canvas.height = 120 * dpr;
			canvas.getContext('2d').scale(dpr, dpr);
		}

		function drawBeatmap() {
			const canvas = document.getElementById('beatmap-canvas');
			const ctx = canvas.getContext('2d');
			const w = canvas.offsetWidth || 600;
			const h = 120;
			ctx.clearRect(0, 0, w * 2, h * 2);

			const pad = { left: 10, right: 10, top: 20, bottom: 20 };
			const cw = w - pad.left - pad.right;
			const ch = h - pad.top - pad.bottom;

			// Background
			ctx.fillStyle = '#040710';
			ctx.fillRect(0, 0, w, h);

			// Grid lines at 30s intervals
			for (let t = 0; t <= DURATION; t += 30) {
				const x = pad.left + (t / DURATION) * cw;
				ctx.beginPath();
				ctx.moveTo(x, pad.top);
				ctx.lineTo(x, h - pad.bottom);
				ctx.strokeStyle = '#14202e';
				ctx.lineWidth = 1;
				ctx.stroke();
			}

			// Row labels
			const rows = ['cut', 'text', 'audio', 'peak'];
			rows.forEach((r, i) => {
				const y = pad.top + (i / rows.length) * ch + ch / rows.length / 2;
				ctx.fillStyle = beatColors[r] + '30';
				ctx.fillRect(pad.left, pad.top + (i / rows.length) * ch, cw, ch / rows.length);
			});

			// Beats
			beats.forEach((b) => {
				const row = rows.indexOf(b.type);
				const x = pad.left + (b.t / DURATION) * cw;
				const rowH = ch / rows.length;
				const y = pad.top + row * rowH + rowH * 0.2;
				const bh = rowH * 0.6;

				ctx.fillStyle = beatColors[b.type];
				ctx.fillRect(x - 3, y, 6, bh);

				ctx.font = '9px IBM Plex Mono';
				ctx.fillStyle = beatColors[b.type];
				ctx.textAlign = 'center';
				ctx.fillText(beatLabels[b.type], x, y - 3);
			});

			// Row labels on left edge
			rows.forEach((r, i) => {
				const rowH = ch / rows.length;
				const y = pad.top + i * rowH + rowH / 2 + 3;
				ctx.font = '9px IBM Plex Mono';
				ctx.fillStyle = beatColors[r] + '80';
				ctx.textAlign = 'left';
				ctx.fillText(r.toUpperCase(), pad.left + 3, y);
			});

			updateBeatmapStats();
		}

		function updateBeatmapStats() {
			const total = beats.length;
			document.getElementById('bms-total').textContent = total;
			if (total < 2) {
				document.getElementById('bms-avg').textContent = '—';
				document.getElementById('bms-max-gap').textContent = '—';
				document.getElementById('bms-density').textContent = '—';
				document.getElementById('bm-diagnosis').textContent =
					'Add beats to the timeline to generate a diagnosis.';
				return;
			}

			const sorted = [...beats].sort((a, b) => a.t - b.t);
			const gaps = [];
			for (let i = 1; i < sorted.length; i++) gaps.push(sorted[i].t - sorted[i - 1].t);
			const avgGap = gaps.reduce((a, b) => a + b, 0) / gaps.length;
			const maxGap = Math.max(...gaps);
			const variance = Math.sqrt(
				gaps.map((g) => (g - avgGap) ** 2).reduce((a, b) => a + b, 0) / gaps.length
			);

			document.getElementById('bms-avg').textContent = avgGap.toFixed(1) + 's';
			document.getElementById('bms-max-gap').textContent = maxGap.toFixed(1) + 's';

			let grade, gradeColor, diagnosis;
			if (maxGap > 20) {
				grade = 'DESERT';
				gradeColor = '#ff4f68';
				diagnosis = `⚠ Desert detected: a ${maxGap.toFixed(0)}s gap with no events. Viewers are likely to drift here. Add a beat or ensure the visual is carrying full load during this window.`;
			} else if (variance < 2) {
				grade = 'FLAT';
				gradeColor = '#f5b94a';
				diagnosis = `Uniform spacing detected (variance: ${variance.toFixed(1)}s). The rhythm is predictable, which reads as monotony. Introduce deliberate clusters and pauses — variation creates felt pace.`;
			} else if (avgGap < 4 && total > 15) {
				grade = 'DENSE';
				gradeColor = '#ff4f68';
				diagnosis = `High event density: avg ${avgGap.toFixed(1)}s between beats. This may cause overload if sustained. Ensure the content complexity justifies this density, or add breathing room.`;
			} else {
				grade = 'GOOD';
				gradeColor = '#3dd9a4';
				diagnosis = `Rhythm looks intentional: avg ${avgGap.toFixed(1)}s gap, max gap ${maxGap.toFixed(0)}s, variance ${variance.toFixed(1)}s. The pattern has variation without deserts. Watch for clusters that don't serve the content.`;
			}

			document.getElementById('bms-density').textContent = grade;
			document.getElementById('bms-density').style.color = gradeColor;
			document.getElementById('bm-diagnosis').textContent = diagnosis;
		}

		document.getElementById('beatmap-canvas').addEventListener('click', function (e) {
			const rect = this.getBoundingClientRect();
			const x = e.clientX - rect.left;
			const pad = { left: 10, right: 10, top: 20, bottom: 20 };
			const cw = rect.width - pad.left - pad.right;
			const ch = rect.height - pad.top - pad.bottom;
			if (x < pad.left || x > rect.width - pad.right) return;
			const t = ((x - pad.left) / cw) * DURATION;
			beats.push({ type: currentBeatType, t });
			drawBeatmap();
		});

		function clearBeats() {
			beats = [];
			drawBeatmap();
		}

		function loadPreset(name) {
			beats = [];
			if (name === 'good') {
				const pattern = [
					{ type: 'cut', t: 5 },
					{ type: 'text', t: 8 },
					{ type: 'cut', t: 16 },
					{ type: 'audio', t: 18 },
					{ type: 'text', t: 26 },
					{ type: 'cut', t: 30 },
					{ type: 'peak', t: 38 },
					{ type: 'cut', t: 42 },
					{ type: 'text', t: 50 },
					{ type: 'audio', t: 55 },
					{ type: 'cut', t: 62 },
					{ type: 'text', t: 68 },
					{ type: 'cut', t: 78 },
					{ type: 'peak', t: 84 },
					{ type: 'cut', t: 92 },
					{ type: 'audio', t: 96 },
					{ type: 'text', t: 105 },
					{ type: 'cut', t: 112 },
					{ type: 'text', t: 120 },
					{ type: 'cut', t: 128 },
					{ type: 'peak', t: 136 },
					{ type: 'audio', t: 140 },
					{ type: 'cut', t: 150 },
					{ type: 'text', t: 158 },
					{ type: 'cut', t: 168 },
					{ type: 'audio', t: 174 }
				];
				beats = pattern;
			} else {
				beats = [
					{ type: 'cut', t: 2 },
					{ type: 'text', t: 3 },
					{ type: 'audio', t: 4 },
					{ type: 'peak', t: 6 },
					{ type: 'cut', t: 8 },
					{ type: 'text', t: 10 },
					{ type: 'cut', t: 65 },
					{ type: 'text', t: 68 },
					{ type: 'cut', t: 130 },
					{ type: 'audio', t: 132 },
					{ type: 'peak', t: 134 },
					{ type: 'cut', t: 136 },
					{ type: 'text', t: 138 },
					{ type: 'cut', t: 140 }
				];
			}
			drawBeatmap();
		}

		_addWinListener('resize', () => {
			initBeatmapCanvas();
			drawBeatmap();
		});
		initBeatmapCanvas();
		drawBeatmap();

		/* ═══════════════════════════════════
   PACING SIMULATOR
═══════════════════════════════════ */
		const paceData = {
			slow: {
				narr: [
					{ w: 5, label: 'Opening context', color: '#4aafff' },
					{ w: 0.5, color: 'transparent' },
					{ w: 7, label: 'First concept introduced', color: '#4aafff' },
					{ w: 1, color: 'transparent' },
					{ w: 6, label: 'Explanation continues...', color: '#4aafff' },
					{ w: 1.5, color: 'transparent' },
					{ w: 5, label: 'Closing idea', color: '#4aafff' }
				],
				vis: [
					{ w: 6, label: 'Establishing shot', color: '#405068' },
					{ w: 1, color: 'transparent' },
					{ w: 8, label: 'Diagram A', color: '#405068' },
					{ w: 2, color: 'transparent' },
					{ w: 8, label: 'Diagram B', color: '#405068' },
					{ w: 1, color: 'transparent' }
				],
				text: [
					{ w: 3, color: 'transparent' },
					{ w: 4, label: 'KEY TERM', color: '#2a3a1a' },
					{ w: 5, color: 'transparent' },
					{ w: 5, label: 'DEFINITION', color: '#2a3a1a' },
					{ w: 6, color: 'transparent' },
					{ w: 4, label: 'TAKEAWAY', color: '#2a3a1a' }
				],
				info: '<strong>Slow pacing</strong> — Each idea occupies its own time. Narration pauses often. Visuals hold long enough to read and comprehend fully. Text events are separated. Optimal for new or complex information. Viewer retention is high per unit of content, but total throughput is low. Use when building a new mental model.'
			},
			medium: {
				narr: [
					{ w: 4, label: 'Context', color: '#4aafff' },
					{ w: 0.5, color: 'transparent' },
					{ w: 5, label: 'Concept 1', color: '#4aafff' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Concept 2', color: '#4aafff' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Bridge', color: '#4aafff' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Closing', color: '#4aafff' },
					{ w: 0.5, color: 'transparent' }
				],
				vis: [
					{ w: 4, label: 'Shot A', color: '#405068' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Shot B', color: '#405068' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Diag A', color: '#405068' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Diag B', color: '#405068' },
					{ w: 0.5, color: 'transparent' },
					{ w: 4, label: 'Shot C', color: '#405068' },
					{ w: 0.5, color: 'transparent' }
				],
				text: [
					{ w: 2, color: 'transparent' },
					{ w: 2.5, label: 'TERM', color: '#2a3a1a' },
					{ w: 2, color: 'transparent' },
					{ w: 2.5, label: 'STAT', color: '#2a3a1a' },
					{ w: 2, color: 'transparent' },
					{ w: 2.5, label: 'LINK', color: '#2a3a1a' },
					{ w: 2, color: 'transparent' },
					{ w: 2.5, label: 'KEY', color: '#2a3a1a' },
					{ w: 2.5, color: 'transparent' }
				],
				info: '<strong>Medium pacing</strong> — Narration, visuals, and text events maintain distinct roles but begin to overlap slightly. Cuts arrive at natural phrase endings. Text appears just ahead of the corresponding spoken term. Viewer comprehension and engagement are balanced. This is the default for most explainer content.'
			},
			fast: {
				narr: [
					{ w: 2.5, label: 'Hook', color: '#4aafff' },
					{ w: 2, label: 'C1', color: '#4aafff' },
					{ w: 2, label: 'C2', color: '#4aafff' },
					{ w: 2, label: 'C3', color: '#4aafff' },
					{ w: 2.5, label: 'Example', color: '#4aafff' },
					{ w: 2, label: 'C4', color: '#4aafff' },
					{ w: 2, label: 'C5', color: '#4aafff' },
					{ w: 2.5, label: 'Landing', color: '#4aafff' }
				],
				vis: [
					{ w: 1.5, label: 'A', color: '#405068' },
					{ w: 1.5, label: 'B', color: '#405068' },
					{ w: 1.5, label: 'C', color: '#405068' },
					{ w: 1.5, label: 'D', color: '#405068' },
					{ w: 1.5, label: 'E', color: '#405068' },
					{ w: 1.5, label: 'F', color: '#405068' },
					{ w: 1.5, label: 'G', color: '#405068' },
					{ w: 1.5, label: 'H', color: '#405068' },
					{ w: 1.5, label: 'I', color: '#405068' },
					{ w: 1.5, label: 'J', color: '#405068' },
					{ w: 1, label: 'K', color: '#405068' }
				],
				text: [
					{ w: 1.5, label: 'H', color: '#2a3a1a' },
					{ w: 1.5, label: 'T1', color: '#2a3a1a' },
					{ w: 1, color: 'transparent' },
					{ w: 1.5, label: 'T2', color: '#2a3a1a' },
					{ w: 1.5, label: 'T3', color: '#2a3a1a' },
					{ w: 1, color: 'transparent' },
					{ w: 1.5, label: 'T4', color: '#2a3a1a' },
					{ w: 1.5, label: 'EX', color: '#2a3a1a' },
					{ w: 1, color: 'transparent' },
					{ w: 1.5, label: 'T5', color: '#2a3a1a' },
					{ w: 1.5, label: 'KY', color: '#2a3a1a' }
				],
				info: '<strong>Fast pacing</strong> — Multiple events per sentence. Visuals cut frequently. Text events coincide with, not precede, key words. Narration is compressed, with short pauses only at major transitions. Correct for familiar material, emotional beats, and rapid-fire list segments. Sustained fast pacing without recovery zones causes exhaustion.'
			}
		};

		let currentPaceMode = 'slow';
		let paceAnim = null;

		function setPaceMode(mode) {
			currentPaceMode = mode;
			['slow', 'medium', 'fast'].forEach((m) => {
				document.getElementById('pm-' + m).classList.toggle('active', m === mode);
			});
			renderPaceTracks(mode);
			document.getElementById('pace-info').innerHTML = paceData[mode].info;
		}

		function renderPaceTracks(mode) {
			const data = paceData[mode];
			const totalDur = mode === 'slow' ? 27 : mode === 'medium' ? 27 : 20;

			const trackMap = { narr: data.narr, vis: data.vis, text: data.text };
			const accentMap = { narr: '#4aafff', vis: '#405068', text: '#3dd9a4' };

			Object.entries(trackMap).forEach(([key, clips]) => {
				const el = document.getElementById('pc-' + key);
				el.innerHTML = '';
				const trackEl = document.getElementById('pt-' + key);
				const availW = trackEl.offsetWidth - 74;

				clips.forEach((clip) => {
					const div = document.createElement('div');
					div.className = 'pace-clip';
					const w = Math.max(2, (clip.w / totalDur) * availW - 2);
					div.style.width = w + 'px';
					div.style.minWidth = w + 'px';
					div.style.maxWidth = w + 'px';

					if (clip.color === 'transparent') {
						div.style.background = 'transparent';
						div.style.border = '1px dashed #14202e';
					} else if (key === 'narr') {
						div.style.background = `color-mix(in srgb, ${accentMap[key]} 18%, transparent)`;
						div.style.border = `1px solid ${accentMap[key]}60`;
						div.style.color = accentMap[key];
					} else if (key === 'vis') {
						div.style.background = `color-mix(in srgb, #405068 40%, transparent)`;
						div.style.border = `1px solid #405068`;
						div.style.color = '#8090a8';
					} else {
						div.style.background = `color-mix(in srgb, var(--vs-mint) 14%, transparent)`;
						div.style.border = `1px solid #3dd9a440`;
						div.style.color = '#3dd9a4';
					}

					if (clip.label && w > 25) div.textContent = clip.label;
					el.appendChild(div);
				});
			});
		}

		function playAllPaces() {
			stopAllPaces();
			['narr', 'vis', 'text'].forEach((key) => {
				const ph = document.getElementById('ph-' + key);
				ph.style.opacity = '1';
			});

			const dur = currentPaceMode === 'fast' ? 4000 : 6000;
			let start = null;

			function anim(ts) {
				if (!start) start = ts;
				const prog = Math.min(1, (ts - start) / dur);

				['narr', 'vis', 'text'].forEach((key) => {
					const trackEl = document.getElementById('pt-' + key);
					const availW = trackEl.offsetWidth - 74;
					const ph = document.getElementById('ph-' + key);
					ph.style.left = 74 + prog * availW + 'px';
				});

				document.getElementById('bm-fill').style.width = prog * 100 + '%';

				if (prog < 1) paceAnim = requestAnimationFrame(anim);
				else {
					['narr', 'vis', 'text'].forEach((key) => {
						document.getElementById('ph-' + key).style.opacity = '0';
					});
				}
			}
			paceAnim = requestAnimationFrame(anim);
		}

		function stopAllPaces() {
			if (paceAnim) cancelAnimationFrame(paceAnim);
			paceAnim = null;
			['narr', 'vis', 'text'].forEach((key) => {
				document.getElementById('ph-' + key).style.opacity = '0';
			});
		}

		setPaceMode('slow');

		/* ═══════════════════════════════════
   CHUNK BUILDER
═══════════════════════════════════ */
		const chunkColors = {
			term: { bg: '#ff4f6820', border: '#ff4f68', text: '#ff4f68' },
			stat: { bg: '#f5b94a20', border: '#f5b94a', text: '#f5b94a' },
			example: { bg: '#3dd9a420', border: '#3dd9a4', text: '#3dd9a4' },
			step: { bg: '#4aafff20', border: '#4aafff', text: '#4aafff' },
			break: { bg: 'transparent', border: '#1e2d40', text: '#405068' }
		};
		const chunkLoad = { term: 2, stat: 1.5, example: 0.5, step: 1, break: -99 };
		const MAX_LOAD = 4;
		let chunks = [];
		let currentLoad = 0;

		function addChunk(type, label, load) {
			chunks.push({ type, label });
			if (type === 'break') {
				currentLoad = 0;
			} else {
				currentLoad = Math.min(MAX_LOAD + 2, currentLoad + load);
			}
			renderChunks();
		}

		function clearChunks() {
			chunks = [];
			currentLoad = 0;
			renderChunks();
		}

		function renderChunks() {
			const el = document.getElementById('chunk-sequence');
			el.innerHTML = '';

			let runningLoad = 0;
			const row = document.createElement('div');
			row.className = 'chunk-row';

			chunks.forEach((chunk, i) => {
				if (chunk.type === 'break') {
					el.appendChild(row.cloneNode(true));
					const sep = document.createElement('div');
					sep.style.cssText =
						'width:100%; height:1px; background:var(--vs-amber)40; margin:4px 0; position:relative;';
					sep.innerHTML =
						'<span style="position:absolute; left:50%; transform:translateX(-50%); background:var(--vs-bg); padding:0 8px; font-size:10px; color:var(--vs-amber); letter-spacing:0.1em; top:-7px;">CHUNK BOUNDARY</span>';
					el.appendChild(sep);
					const newRow = document.createElement('div');
					newRow.className = 'chunk-row';
					el.appendChild(newRow);
					runningLoad = 0;
					return;
				}

				const c = chunkColors[chunk.type];
				const div = document.createElement('div');
				div.className = 'chunk-block';
				div.style.background = c.bg;
				div.style.borderColor = c.border;
				div.style.color = c.text;
				div.textContent = chunk.label;

				const lastRow = el.querySelector('.chunk-row:last-child') || row;
				lastRow.appendChild(div);
				runningLoad += chunkLoad[chunk.type] || 0;
			});

			if (!el.querySelector('.chunk-row')) el.appendChild(row);

			// Update meter
			const pct = Math.min(100, (currentLoad / MAX_LOAD) * 100);
			const fill = document.getElementById('chunk-meter-fill');
			fill.style.width = pct + '%';
			fill.style.background =
				currentLoad > MAX_LOAD ? '#ff4f68' : currentLoad > MAX_LOAD * 0.75 ? '#f5b94a' : '#3dd9a4';
			document.getElementById('chunk-load-val').textContent =
				currentLoad.toFixed(1) + ' / ' + MAX_LOAD + ' units';
			document.getElementById('chunk-load-val').style.color =
				currentLoad > MAX_LOAD ? '#ff4f68' : currentLoad > MAX_LOAD * 0.75 ? '#f5b94a' : '#3dd9a4';

			const warn = document.getElementById('chunk-warning');
			if (currentLoad > MAX_LOAD) {
				warn.textContent = '⚠ Working memory overloaded — add a chunk break before continuing.';
			} else if (currentLoad > MAX_LOAD * 0.75) {
				warn.textContent = '· Approaching capacity — next new term should follow a break.';
			} else {
				warn.textContent = '';
			}
		}

		/* ═══════════════════════════════════
   RHYTHM PATTERN BUILDER
═══════════════════════════════════ */
		const GRID_CELLS = 24; // 24 × 5s = 2 min
		let rhythmState = new Array(GRID_CELLS).fill('empty');
		const beatCycle = ['empty', 'hold', 'cut', 'peak'];

		const presets = {
			explain:
				'hold,hold,cut,hold,hold,hold,cut,empty,hold,hold,cut,hold,hold,empty,hold,hold,cut,peak,cut,hold,hold,hold,empty,empty'.split(
					','
				),
			essay:
				'hold,hold,hold,hold,cut,hold,hold,cut,hold,peak,cut,cut,peak,peak,cut,cut,peak,cut,hold,cut,hold,hold,empty,empty'.split(
					','
				),
			list: 'cut,cut,cut,cut,cut,cut,cut,cut,peak,empty,cut,cut,cut,cut,cut,cut,cut,cut,peak,empty,hold,hold,empty,empty'.split(
				','
			),
			empty: new Array(GRID_CELLS).fill('empty')
		};

		function loadRhythmPreset(name) {
			['explain', 'essay', 'list', 'empty'].forEach((p) => {
				const btn =
					document.querySelectorAll('#rhythm .btn')[
						['explain', 'essay', 'list', 'empty'].indexOf(p)
					];
				if (btn) btn.classList.toggle('active', p === name);
			});
			rhythmState = [...presets[name]];
			renderRhythmGrid();
		}

		function toggleRhythmBeat(i) {
			const cur = beatCycle.indexOf(rhythmState[i]);
			rhythmState[i] = beatCycle[(cur + 1) % beatCycle.length];
			renderRhythmGrid();
		}

		function renderRhythmGrid() {
			const el = document.getElementById('rhythm-grid');
			el.innerHTML = '';
			rhythmState.forEach((state, i) => {
				const div = document.createElement('div');
				div.className =
					'rhythm-beat' +
					(state !== 'empty'
						? ' ' + (state === 'hold' ? 'hold' : state === 'cut' ? 'cut' : 'peak')
						: '');
				div.title = `Block ${i + 1} (${i * 5}–${i * 5 + 5}s)`;
				div.textContent =
					state === 'empty' ? '' : state === 'hold' ? '—' : state === 'cut' ? '✂' : '●';
				div.onclick = () => toggleRhythmBeat(i);
				el.appendChild(div);
			});
			analyzeRhythm();
		}

		function analyzeRhythm() {
			const counts = { hold: 0, cut: 0, peak: 0, empty: 0 };
			rhythmState.forEach((s) => counts[s]++);

			const peakClusters = [];
			let cluster = 0;
			rhythmState.forEach((s) => {
				if (s === 'peak') cluster++;
				else {
					if (cluster > 0) peakClusters.push(cluster);
					cluster = 0;
				}
			});
			if (cluster > 0) peakClusters.push(cluster);

			let analysis = '';
			const holdPct = Math.round((counts.hold / GRID_CELLS) * 100);
			const emptyPct = Math.round((counts.empty / GRID_CELLS) * 100);
			const peakPct = Math.round((counts.peak / GRID_CELLS) * 100);

			if (peakPct > 40) {
				analysis +=
					'⚠ Too many peak-density moments — sustained intensity without recovery causes fatigue. ';
			} else if (peakPct === 0) {
				analysis +=
					'· No tension peaks — the pattern is even but may lack momentum-generating moments. ';
			}
			if (emptyPct < 8) {
				analysis +=
					'· Very few empty blocks — consider adding breathing room after dense sequences. ';
			} else if (emptyPct > 40) {
				analysis += '⚠ High proportion of empty blocks may produce abandonment zones. ';
			}
			if (holdPct > 0 && counts.cut > 0) {
				analysis += `Pattern: ${holdPct}% hold / ${Math.round((counts.cut / GRID_CELLS) * 100)}% cut / ${peakPct}% peak / ${emptyPct}% empty over ${GRID_CELLS * 5}s. `;
			}
			if (!analysis)
				analysis =
					'Click blocks to cycle through beat types. Load a preset to see common rhythm structures.';

			document.getElementById('rhythm-analysis').textContent = analysis;
		}

		loadRhythmPreset('explain');

		/* ─── QUIZ ─── */
		const scores = {};
		function answer(qId, el, correct) {
			if (scores[qId] !== undefined) return;
			scores[qId] = correct ? 1 : 0;
			const opts = el.parentElement.querySelectorAll('.option');
			opts.forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById('fb-' + qId);
			if (correct) {
				el.classList.add('correct');
				fb.textContent = '✓ Correct.';
				fb.className = 'feedback ok';
			} else {
				el.classList.add('wrong');
				opts.forEach((o) => {
					if (o.onclick.toString().includes('true')) o.classList.add('correct');
				});
				fb.textContent = '✗ Not quite — the correct answer is highlighted above.';
				fb.className = 'feedback bad';
			}
			if (Object.keys(scores).length === 4) {
				const total = Object.values(scores).reduce((a, b) => a + b, 0);
				const sc = document.getElementById('quiz-score');
				sc.style.display = 'block';
				document.getElementById('score-display').textContent = total + ' / 4';
				document.getElementById('score-display').style.color =
					total >= 3 ? 'var(--vs-mint)' : total >= 2 ? 'var(--vs-amber)' : 'var(--vs-red)';
			}
		}

		if (typeof setCadenceLevel === 'function') actions.setCadenceLevel = setCadenceLevel;
		if (typeof drawCadenceWheel === 'function') actions.drawCadenceWheel = drawCadenceWheel;
		if (typeof setBeatType === 'function') actions.setBeatType = setBeatType;
		if (typeof getCanvasSize === 'function') actions.getCanvasSize = getCanvasSize;
		if (typeof initBeatmapCanvas === 'function') actions.initBeatmapCanvas = initBeatmapCanvas;
		if (typeof drawBeatmap === 'function') actions.drawBeatmap = drawBeatmap;
		if (typeof updateBeatmapStats === 'function') actions.updateBeatmapStats = updateBeatmapStats;
		if (typeof clearBeats === 'function') actions.clearBeats = clearBeats;
		if (typeof loadPreset === 'function') actions.loadPreset = loadPreset;
		if (typeof setPaceMode === 'function') actions.setPaceMode = setPaceMode;
		if (typeof renderPaceTracks === 'function') actions.renderPaceTracks = renderPaceTracks;
		if (typeof playAllPaces === 'function') actions.playAllPaces = playAllPaces;
		if (typeof anim === 'function') actions.anim = anim;
		if (typeof stopAllPaces === 'function') actions.stopAllPaces = stopAllPaces;
		if (typeof addChunk === 'function') actions.addChunk = addChunk;
		if (typeof clearChunks === 'function') actions.clearChunks = clearChunks;
		if (typeof renderChunks === 'function') actions.renderChunks = renderChunks;
		if (typeof loadRhythmPreset === 'function') actions.loadRhythmPreset = loadRhythmPreset;
		if (typeof toggleRhythmBeat === 'function') actions.toggleRhythmBeat = toggleRhythmBeat;
		if (typeof renderRhythmGrid === 'function') actions.renderRhythmGrid = renderRhythmGrid;
		if (typeof analyzeRhythm === 'function') actions.analyzeRhythm = analyzeRhythm;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			if (typeof paceAnim !== 'undefined' && paceAnim) cancelAnimationFrame(paceAnim);
			_listeners.forEach((l) => l.target.removeEventListener(...l.args.filter(Boolean)));
		};
	});
</script>

<div class="page-wrapper">
	<!-- COURSE HEADER -->
	<header class="course-header">
		<div>
			<div class="course-label">Visual Storytelling for Faceless Video</div>
			<div class="course-title">Narrative, Pacing & Visual Communication</div>
		</div>
		<div style="font-size: 11px; color: var(--vs-muted); text-align: right">Module 02 of 10</div>
	</header>

	<!-- HERO -->
	<div class="module-hero">
		<div class="module-number">02</div>
		<div class="module-tag">Module 02 · Theory + Practice</div>
		<h1 class="module-title">Sequencing, Pacing &amp;<br /><span>Viewer Retention</span></h1>
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
			<li><a href="#cadence">Cadence and Flow</a></li>
			<li><a href="#beat-mapping">Beat Mapping</a></li>
			<li><a href="#pacing-modes">Pacing Modes</a></li>
			<li><a href="#chunking">Chunking</a></li>
			<li><a href="#rhythm">Rhythm Patterns</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#quiz">Quiz</a></li>
		</ul>
	</nav>

	<!-- OBJECTIVES -->
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand cadence as a deliberate design layer, not an accident of editing speed</li>
			<li>Build and read a beat map to diagnose pacing problems before they reach the viewer</li>
			<li>
				Apply slow, medium, and fast pacing to the same content and understand when each is correct
			</li>
			<li>Chunk information to manage cognitive load and create natural breathing room</li>
		</ul>
	</section>

	<!-- SECTION 1: CADENCE AND FLOW -->
	<section id="cadence" class="section">
		<div class="section-header">
			<span class="section-num">02.01</span>
			<h2 class="section-title">Cadence and Flow</h2>
		</div>

		<p>
			Cadence is the felt rhythm of a video — the pattern of movement, stillness, density, and
			release that the viewer experiences over time. It is not the same as editing speed. A video
			can cut fast and feel slow. A video can hold for long durations and feel propulsive. The
			difference is intentionality: whether each moment of the video is doing work, and whether the
			transitions between moments create anticipation or friction.
		</p>

		<p>
			<em>Flow</em> is what happens when cadence is well-managed. The viewer stops noticing the mechanics
			of the video — the cuts, the narration rhythm, the text appearances — and enters a state of continuous
			comprehension. They are carried. Flow breaks the moment a viewer becomes aware of a pause that should
			not be there, or a cut that arrives before they have processed the previous frame.
		</p>

		<div class="callout blue">
			<div class="callout-label">Key Distinction</div>
			Pacing is not about how fast your video moves. It is about whether every moment has a reason to
			exist at its current duration. A 10-second pause on a diagram is correct pacing if the diagram requires
			10 seconds to read. A 10-second pause on a simple phrase is broken pacing.
		</div>

		<p>
			Good cadence operates at three levels simultaneously. At the <strong>micro level</strong>, it
			governs individual clip durations and cut timing — the moment-to-moment feel. At the
			<strong>section level</strong>, it governs how dense or airy each block of content feels, and
			how transitions between topics are handled. At the <strong>macro level</strong>, it governs
			the overall shape of the video — how energy builds, where it releases, and whether the end
			lands with weight.
		</p>

		<!-- DEMO: Cadence Wheel -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Cadence Levels</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Click a cadence level to see how it operates. Good video design manages all three levels
					simultaneously — they compound.
				</p>
				<div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap">
					<canvas
						id="cadence-canvas"
						width="200"
						height="200"
						aria-label="Cadence Canvas Demonstration"
						role="region"
						tabindex="0"
					></canvas>
					<div style="flex: 1; min-width: 200px">
						<div class="btn-row">
							<button
								class="btn active"
								onclick={(e) => {
									actions.setCadenceLevel('micro');
								}}
								id="cad-micro"
							>
								Micro
							</button>
							<button
								class="btn"
								onclick={(e) => {
									actions.setCadenceLevel('section');
								}}
								id="cad-section"
							>
								Section
							</button>
							<button
								class="btn"
								onclick={(e) => {
									actions.setCadenceLevel('macro');
								}}
								id="cad-macro"
							>
								Macro
							</button>
						</div>
						<div
							id="cadence-title"
							style="
										font-family: 'Syne', sans-serif;
										font-size: 16px;
										font-weight: 700;
										color: #fff;
										margin-bottom: 0.5rem;
									"
						></div>
						<div
							id="cadence-desc"
							style="font-size: 12px; color: var(--vs-text); line-height: 1.7"
						></div>
						<div style="margin-top: 1rem">
							<div
								id="cadence-examples"
								style="font-size: 11px; color: var(--vs-muted); line-height: 1.9"
							></div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<p>
			Cadence problems are almost always felt before they are understood. A viewer who says a video
			"feels slow" or "feels exhausting" is usually responding to a cadence failure — either too
			little variation at the micro level, too few breaks at the section level, or an imbalanced
			macro shape that never releases tension.
		</p>
	</section>

	<!-- SECTION 2: BEAT MAPPING -->
	<section id="beat-mapping" class="section">
		<div class="section-header">
			<span class="section-num">02.02</span>
			<h2 class="section-title">Beat Mapping a Video</h2>
		</div>

		<p>
			A beat map is a visual representation of every event in a video laid out on a timeline. Events
			include visual cuts, narration pauses, text appearances, audio peaks, and any moment where the
			viewer's attention is redirected. Beat mapping lets you see the rhythm of your video before
			you finish editing — or diagnose what is wrong with one you have already made.
		</p>

		<p>
			The most common revelation from a beat map is
			<strong>unintentional clusters and deserts</strong>: sections where events pile up without
			breathing room (overload), and sections where nothing happens for too long (abandonment). Both
			are retention killers, but they feel different to the viewer — overload feels exhausting,
			abandonment feels boring — which is why editors often mis-diagnose one as the other.
		</p>

		<!-- DEMO: Beat Map Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Beat Map Builder</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1rem">
					Click the canvas to place beats on the timeline. Select the beat type first, then click to
					add. The analyzer will diagnose your pattern.
				</p>
				<div class="btn-row">
					<button
						class="btn active"
						onclick={(e) => {
							actions.setBeatType('cut');
						}}
						id="bbt-cut"
					>
						✂ Cut / Edit
					</button>
					<button
						class="btn"
						onclick={(e) => {
							actions.setBeatType('text');
						}}
						id="bbt-text">T Text Event</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.setBeatType('audio');
						}}
						id="bbt-audio"
					>
						♪ Audio Peak
					</button>
					<button
						class="btn red"
						onclick={(e) => {
							actions.setBeatType('peak');
						}}
						id="bbt-peak"
					>
						● Tension Peak
					</button>
					<button
						class="btn"
						style="margin-left: auto"
						onclick={(e) => {
							actions.clearBeats();
						}}>Clear</button
					>
					<button
						class="btn mint"
						onclick={(e) => {
							actions.loadPreset('good');
						}}>Load: Balanced</button
					>
					<button
						class="btn red"
						onclick={(e) => {
							actions.loadPreset('bad');
						}}>Load: Uneven</button
					>
				</div>

				<canvas
					id="beatmap-canvas"
					aria-label="Beatmap Canvas Demonstration"
					role="region"
					tabindex="0"
				></canvas>
				<div class="bm-playhead"><div class="bm-playhead-fill" id="bm-fill"></div></div>
				<div class="bm-time">
					<span>0:00</span><span>0:30</span><span>1:00</span><span>1:30</span>
					<span>2:00</span><span>2:30</span><span>3:00</span>
				</div>

				<div class="bm-stats">
					<div class="bm-stat">
						<div class="bm-stat-val" id="bms-total" style="color: var(--vs-amber)">0</div>
						<div class="bm-stat-lbl">Total Beats</div>
					</div>
					<div class="bm-stat">
						<div class="bm-stat-val" id="bms-avg" style="color: var(--vs-blue)">—</div>
						<div class="bm-stat-lbl">Avg Interval</div>
					</div>
					<div class="bm-stat">
						<div class="bm-stat-val" id="bms-max-gap" style="color: var(--vs-red)">—</div>
						<div class="bm-stat-lbl">Longest Gap</div>
					</div>
					<div class="bm-stat">
						<div class="bm-stat-val" id="bms-density" style="color: var(--vs-mint)">—</div>
						<div class="bm-stat-lbl">Rhythm Grade</div>
					</div>
				</div>

				<div
					id="bm-diagnosis"
					style="
								margin-top: 1rem;
								padding: 0.75rem 1rem;
								border: 1px solid var(--vs-border);
								background: #040710;
								font-size: 12px;
								color: var(--vs-text);
								min-height: 48px;
								line-height: 1.7;
							"
				></div>
			</div>
		</div>

		<p>
			Beat mapping is a planning tool, not a constraint. You are not trying to space beats perfectly
			evenly — that would create mechanical monotony. You are looking for
			<em>intentional variation</em>: beats clustered for intensity, spaced for recovery, with no
			accidental deserts longer than the content justifies.
		</p>

		<table>
			<thead>
				<tr>
					<th>Gap Duration</th>
					<th>Typical Effect</th>
					<th>When Correct</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>0–3 seconds</td>
					<td>High energy, urgency, momentum</td>
					<td>Action sequences, rapid data reveals</td>
				</tr>
				<tr>
					<td>3–8 seconds</td>
					<td>Normal rhythm, comfortable flow</td>
					<td>Explanation, demonstration, narration</td>
				</tr>
				<tr>
					<td>8–15 seconds</td>
					<td>Deliberate breath, weight</td>
					<td>Complex diagrams, important pauses</td>
				</tr>
				<tr>
					<td>15+ seconds</td>
					<td>Perceived stagnation</td>
					<td>Rarely — only if visual carries full load</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- SECTION 3: PACING MODES -->
	<section id="pacing-modes" class="section">
		<div class="section-header">
			<span class="section-num">02.03</span>
			<h2 class="section-title">Pacing Modes: Slow, Medium, Fast</h2>
		</div>

		<p>
			Pacing is not a single setting — it is a mode that should change within a single video in
			response to what the content requires. Dense, abstract information requires slower pacing so
			the viewer can process it. Familiar setups, transitions, and emotional beats can move faster.
			Lists and rapid-fire examples benefit from a staccato rhythm that creates energy without
			requiring deep comprehension per item.
		</p>

		<p>
			The mistake is choosing a pacing mode and staying in it. A video that is uniformly fast
			becomes numbing. A video that is uniformly slow becomes work. Contrast is what creates the
			felt experience of pace — the slow section makes the fast one feel electric; the fast section
			makes the slow one feel earned.
		</p>

		<!-- DEMO: Pacing Simulator -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Pacing Mode Simulator</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					The same 30-second content segment rendered at three pacing modes. Each track shows how
					clips are cut and sequenced differently. Press Play to simulate.
				</p>

				<div class="btn-row">
					<button
						class="btn active"
						onclick={(e) => {
							actions.setPaceMode('slow');
						}}
						id="pm-slow">Slow</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.setPaceMode('medium');
						}}
						id="pm-medium">Medium</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.setPaceMode('fast');
						}}
						id="pm-fast">Fast</button
					>
					<button
						class="btn mint"
						onclick={(e) => {
							actions.playAllPaces();
						}}
						id="pm-play">▶ Simulate</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.stopAllPaces();
						}}>■ Stop</button
					>
				</div>

				<!-- Track: Narration -->
				<div class="pace-track" id="pt-narr">
					<div class="pace-track-label">Narration</div>
					<div class="pace-clips-wrap" id="pc-narr"></div>
					<div class="pace-playhead" id="ph-narr"></div>
				</div>
				<!-- Track: Visual -->
				<div class="pace-track" id="pt-vis">
					<div class="pace-track-label">Visual Cut</div>
					<div class="pace-clips-wrap" id="pc-vis"></div>
					<div class="pace-playhead" id="ph-vis"></div>
				</div>
				<!-- Track: Text -->
				<div class="pace-track" id="pt-text">
					<div class="pace-track-label">Text Event</div>
					<div class="pace-clips-wrap" id="pc-text"></div>
					<div class="pace-playhead" id="ph-text"></div>
				</div>

				<div class="pace-info" id="pace-info"></div>

				<div
					style="
								margin-top: 1.25rem;
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
										color: var(--vs-amber);
										font-size: 9px;
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Slow Pacing
						</div>
						<div style="color: var(--vs-text); line-height: 1.6">
							One idea per cut. Narration leads. Viewer has time to form mental model before next
							beat arrives.
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
										color: var(--vs-blue);
										font-size: 9px;
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Medium Pacing
						</div>
						<div style="color: var(--vs-text); line-height: 1.6">
							Visual and text beats complement narration. Slight overlap creates momentum without
							losing comprehension.
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
										color: var(--vs-mint);
										font-size: 9px;
										letter-spacing: 0.1em;
										text-transform: uppercase;
										margin-bottom: 0.4rem;
									"
						>
							Fast Pacing
						</div>
						<div style="color: var(--vs-text); line-height: 1.6">
							Multiple events per beat. Narration is compressed. Works when content is familiar or
							emotionally driven.
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="callout">
			<div class="callout-label">Pacing Selection Rule</div>
			Match pacing to cognitive requirement, not emotional preference. New or complex ideas need slow
			pacing. Familiar scaffolding can move fast. Transitions can be very fast. Endings should slow.
		</div>
	</section>

	<!-- SECTION 4: CHUNKING -->
	<section id="chunking" class="section">
		<div class="section-header">
			<span class="section-num">02.04</span>
			<h2 class="section-title">Chunking: Grouping Information to Prevent Fatigue</h2>
		</div>

		<p>
			Chunking is the practice of grouping related information into bounded units with clear
			beginnings and ends. Each chunk should represent a single complete thought — something the
			viewer can hold and file before the next chunk begins. When information is not chunked, it
			arrives as a continuous stream that the viewer cannot organize in real time, and working
			memory overloads.
		</p>

		<p>
			In video, chunking is expressed through multiple overlapping signals: a pause in narration, a
			visual transition, a section title card, a change in background color, or a shift in audio
			character. Not all of these signals need to be used simultaneously — but at least one should
			mark every chunk boundary, so the viewer knows that one thing has ended and another is
			beginning.
		</p>

		<!-- DEMO: Chunk Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Chunk Load Calculator</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Build a sequence of information units. The load meter shows how much the viewer is holding
					at any moment. Cross the threshold and retention drops.
				</p>

				<div style="margin-bottom: 1.25rem">
					<div
						style="
									font-size: 11px;
									color: var(--vs-muted);
									margin-bottom: 0.75rem;
									letter-spacing: 0.08em;
									text-transform: uppercase;
								"
					>
						Add an information unit:
					</div>
					<div class="btn-row">
						<button
							class="btn"
							onclick={(e) => {
								actions.addChunk('term', 'New Term / Concept', 2);
							}}
						>
							+ New Term
						</button>
						<button
							class="btn"
							onclick={(e) => {
								actions.addChunk('stat', 'Statistic / Data', 1.5);
							}}
						>
							+ Statistic
						</button>
						<button
							class="btn"
							onclick={(e) => {
								actions.addChunk('example', 'Example / Story', 0.5);
							}}
						>
							+ Example
						</button>
						<button
							class="btn"
							onclick={(e) => {
								actions.addChunk('step', 'Procedural Step', 1);
							}}>+ Step</button
						>
						<button
							class="btn mint"
							onclick={(e) => {
								actions.addChunk('break', '〈 Chunk Break 〉', -99);
							}}
						>
							+ Break
						</button>
						<button
							class="btn"
							onclick={(e) => {
								actions.clearChunks();
							}}
							style="margin-left: auto">Clear</button
						>
					</div>
				</div>

				<div id="chunk-sequence"></div>
				<div class="overload-warning" id="chunk-warning"></div>

				<div style="margin-top: 1rem">
					<div
						style="
									display: flex;
									justify-content: space-between;
									font-size: 11px;
									margin-bottom: 4px;
								"
					>
						<span style="color: var(--vs-muted)">Working memory load</span>
						<span id="chunk-load-val" style="color: var(--vs-amber); font-weight: 600"
							>0 / 4 units</span
						>
					</div>
					<div class="chunk-meter">
						<div
							class="chunk-meter-fill"
							id="chunk-meter-fill"
							style="background: var(--vs-mint)"
						></div>
					</div>
				</div>
			</div>
		</div>

		<p>
			The most powerful chunking tool in faceless video is the <strong>visual pause</strong> — a moment
			of relative emptiness on screen that gives the viewer permission to process before continuing. It
			does not need to be long. Two to three seconds of a simpler or static visual after a dense explanation
			is enough to signal the chunk boundary without creating a dead zone.
		</p>

		<div class="callout mint">
			<div class="callout-label">The Breath Rule</div>
			After every concept that introduced something genuinely new, give the viewer one breath before the
			next idea. Narration can continue — but the visual load should drop, or the narration should restate
			rather than advance.
		</div>
	</section>

	<!-- SECTION 5: RHYTHM PATTERNS -->
	<section id="rhythm" class="section">
		<div class="section-header">
			<span class="section-num">02.05</span>
			<h2 class="section-title">Rhythm Patterns &amp; Practical Templates</h2>
		</div>

		<p>
			Once you understand cadence, beat mapping, pacing modes, and chunking, you can begin
			assembling them into deliberate rhythm patterns — predictable structures that produce reliable
			viewer experiences. Rhythm patterns are not formulas. They are starting points that you modify
			based on your specific content.
		</p>

		<!-- DEMO: Rhythm Pattern Builder -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Rhythm Pattern Editor</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1rem">
					Each cell is a 5-second block. Click to cycle through: Hold (steady) → Cut (transition) →
					Peak (high tension) → empty. Load a preset to see common patterns.
				</p>
				<div class="btn-row">
					<button
						class="btn active"
						onclick={(e) => {
							actions.loadRhythmPreset('explain');
						}}>Explainer</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.loadRhythmPreset('essay');
						}}>Essay</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.loadRhythmPreset('list');
						}}>Rapid List</button
					>
					<button
						class="btn"
						onclick={(e) => {
							actions.loadRhythmPreset('empty');
						}}>Clear</button
					>
				</div>
				<div class="rhythm-grid" id="rhythm-grid"></div>
				<div
					style="
								display: flex;
								gap: 1.5rem;
								margin-top: 0.75rem;
								flex-wrap: wrap;
								font-size: 11px;
								color: var(--vs-muted);
							"
				>
					<span><span style="color: var(--vs-blue)">■</span> Hold — steady visual, explanation</span
					>
					<span><span style="color: var(--vs-amber)">■</span> Cut — transition, new angle</span>
					<span><span style="color: var(--vs-red)">■</span> Peak — high event density</span>
					<span><span style="color: var(--vs-border2)">□</span> Empty — breathing room</span>
				</div>
				<div
					id="rhythm-analysis"
					style="
								margin-top: 1.25rem;
								padding: 0.75rem 1rem;
								border: 1px solid var(--vs-border);
								background: #040710;
								font-size: 12px;
								color: var(--vs-text);
								min-height: 48px;
								line-height: 1.7;
							"
				></div>
			</div>
		</div>

		<p>
			Three rhythm patterns appear frequently in successful faceless content. The
			<strong>explainer pattern</strong> alternates between dense explanation and recovery: explain,
			breathe, example, breathe, deeper explain, breathe. The
			<strong>essay pattern</strong> builds slowly, accelerates through evidence, and decelerates
			toward the ending. The <strong>rapid list pattern</strong> clusters fast beats for energy, then
			pauses hard before the insight that earns them.
		</p>
	</section>

	<!-- SECTION 6: PRACTICAL WORK -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">02.06</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<div class="callout">
			<div class="callout-label">Exercise A · Three-Pass Pacing Edit</div>
			Take any 30–40 second script segment you have written or found. Edit it three times, each time targeting
			a different pacing mode: slow, medium, and fast. Do not change the information — change only the
			clip durations, pause lengths, and number of visual events per sentence. Watch all three back to
			back and write one sentence about what changed in how the content felt, not just how it moved.
		</div>

		<div class="callout red">
			<div class="callout-label">Exercise B · Beat Map Analysis</div>
			Choose a faceless video between 2 and 5 minutes long that you feel is either very engaging or very
			boring. On a sheet of paper or in a spreadsheet, mark every visual event at its approximate timestamp.
			Calculate the average gap and find the longest desert. Write a diagnosis: is the pacing problem
			overload, abandonment, or monotony — and where does it occur?
		</div>

		<div class="callout mint">
			<div class="callout-label">Assessment · Justify Your Pacing</div>
			For a clip of your own (or a clip you select), write a brief justification for the pacing choices
			at three specific moments — one where you chose slow, one medium, one fast. Explain what the content
			required and why the chosen mode serves it. This is the core habit of a deliberate editor: every
			duration is a decision, not a default.
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
						<span class="stat-label">Cadence</span><span class="stat-val"
							>felt rhythm of a video</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Flow state</span><span class="stat-val"
							>mechanics disappear</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Beat map</span><span class="stat-val"
							>visual event timeline</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Desert</span><span class="stat-val">beat gap &gt; 15 sec</span>
					</div>
				</div>
				<div class="stats-panel">
					<div class="stat-row">
						<span class="stat-label">Pacing mode</span><span class="stat-val"
							>slow / medium / fast</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Chunking</span><span class="stat-val">bounded info units</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Visual pause</span><span class="stat-val"
							>chunk boundary signal</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Rhythm pattern</span><span class="stat-val"
							>intentional beat shape</span
						>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 02 — Check Your Understanding</div>
		<div class="quiz-sub">4 questions · No time limit</div>

		<!-- Q1 -->
		<div class="question" id="q1">
			<div class="q-text">
				<span class="q-num">01.</span>A creator says their video "feels slow" even though they cut
				every 3–4 seconds throughout. What is the most likely cause?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, false);
					}}
				>
					The cuts are too infrequent — they should cut every 1–2 seconds instead
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, true);
					}}
				>
					The pacing is uniform and there is no contrast — cuts are consistent but every moment is
					doing the same work, so there is no felt variation in energy
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, false);
					}}
				>
					The narration speed is too slow regardless of cut frequency
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q1', e.currentTarget, false);
					}}
				>
					The video lacks music, which is the primary source of felt pace
				</button>
			</div>
			<div class="feedback" id="fb-q1"></div>
		</div>

		<!-- Q2 -->
		<div class="question" id="q2">
			<div class="q-text">
				<span class="q-num">02.</span>In a beat map, a 22-second section with zero visual events
				appears between two dense clusters. How should this be diagnosed?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, false);
					}}
				>
					An intentional breath — it is always correct to allow long pauses after dense content
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, true);
					}}
				>
					A potential abandonment zone — unless the visual during that gap carries full cognitive
					load independently, 22 seconds without an event will lose viewers
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, false);
					}}
				>
					A cognitive overload zone — the viewer needs more events to stay engaged
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q2', e.currentTarget, false);
					}}
				>
					A correct pacing choice if the narration continues uninterrupted throughout
				</button>
			</div>
			<div class="feedback" id="fb-q2"></div>
		</div>

		<!-- Q3 -->
		<div class="question" id="q3">
			<div class="q-text">
				<span class="q-num">03.</span>You are explaining a complex, unfamiliar concept that requires
				the viewer to build a new mental model. Which pacing mode is most appropriate?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, false);
					}}
				>
					Fast — energy signals importance and keeps the viewer alert
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, false);
					}}
				>
					Medium — a compromise between clarity and engagement is always the safest choice
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, true);
					}}
				>
					Slow — the cognitive requirement is high; the viewer needs time to process each idea
					before the next arrives
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q3', e.currentTarget, false);
					}}
				>
					Variable — the pacing should change every few seconds to maintain novelty
				</button>
			</div>
			<div class="feedback" id="fb-q3"></div>
		</div>

		<!-- Q4 -->
		<div class="question" id="q4">
			<div class="q-text">
				<span class="q-num">04.</span>Which of the following best describes the function of a chunk
				boundary signal in faceless video?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, false);
					}}
				>
					It marks the end of the video so the viewer knows when to stop watching
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, false);
					}}
				>
					It provides a visual rest that replaces narration at regular intervals
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, true);
					}}
				>
					It tells the viewer that one complete unit of information has ended, giving them
					permission to file what they have processed before the next unit begins
				</button>
				<button
					type="button"
					class="option"
					onclick={(e) => {
						actions.answer('q4', e.currentTarget, false);
					}}
				>
					It resets the viewer's working memory by repeating the previous section's key points
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
		<a href="./01" class="prev-link">← Module 01: Foundations of Visual Storytelling</a>
		<a href="./03" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">Structuring Text for Video</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</div>
</div>

<!-- /page-wrapper -->

<style>
	/* ═══════════════════════════════════════════════════════
     VISUAL STORYTELLING COURSE — DESIGN TOKENS
  ═══════════════════════════════════════════════════════ */

	.page-wrapper {
		background: var(--vs-bg);
		color: var(--vs-text);
		font-family: 'IBM Plex Mono', monospace;
		font-size: 14px;
		line-height: 1.8;
	}

	/* ── LAYOUT ── */
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
		background: repeating-linear-gradient(
			0deg,
			transparent,
			transparent 2px,
			rgba(245, 185, 74, 0.012) 2px,
			rgba(245, 185, 74, 0.012) 4px
		);
		pointer-events: none;
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
		color: var(--vs-amber);
		border: 1px solid var(--vs-amber);
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
		color: var(--vs-amber);
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
		color: var(--vs-amber);
		border-color: var(--vs-amber);
	}

	/* ── OBJECTIVES ── */
	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--vs-amber);
		background: var(--vs-surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-amber);
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
		color: var(--vs-blue);
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
		color: var(--vs-blue);
		letter-spacing: 0.1em;
		font-weight: 600;
	}
	.section-title {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		color: #fff;
	}

	/* ── TYPOGRAPHY ── */
	p {
		margin-bottom: 1.2rem;
		color: var(--vs-text);
	}
	p:last-child {
		margin-bottom: 0;
	}
	strong {
		color: var(--vs-amber);
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
	:global(pre) {
		background: #040710;
		border: 1px solid var(--vs-border);
		padding: 1.5rem;
		overflow-x: auto;
		margin: 1.5rem 0;
		font-size: 13px;
		line-height: 1.6;
		position: relative;
	}
	:global(pre) :global(.lang-tag) {
		position: absolute;
		top: 8px;
		right: 12px;
		font-size: 10px;
		color: var(--vs-muted);
		letter-spacing: 0.1em;
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
		border-left: 2px solid var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-surface));
		font-size: 13px;
	}
	.callout.blue {
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 5%, var(--vs-surface));
	}
	:global(.callout.red) {
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 5%, var(--vs-surface));
	}
	.callout.mint {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 5%, var(--vs-surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-amber);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	.callout.blue .callout-label {
		color: var(--vs-blue);
	}
	:global(.callout.red) .callout-label {
		color: var(--vs-red);
	}
	.callout.mint .callout-label {
		color: var(--vs-mint);
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
		color: var(--vs-amber);
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	:global(.demo-badge.animated) {
		color: var(--vs-blue);
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	/* ── CONTROLS ── */
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
		border-color: var(--vs-amber);
		color: var(--vs-amber);
	}
	:global(.btn.active) {
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
	:global(.btn.mint:hover) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	:global(.btn.mint.active) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
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
		margin: 0.6rem 0;
	}
	:global(.slider-row) label {
		font-size: 12px;
		min-width: 100px;
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
		background: var(--vs-amber);
		cursor: pointer;
	}
	:global(.slider-val) {
		font-size: 12px;
		color: var(--vs-amber);
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
		color: var(--vs-amber);
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

	/* ── DIVIDER ── */
	.divider {
		border: none;
		border-top: 1px solid var(--vs-border);
		margin: 3rem 0;
	}

	/* ── STATS PANEL ── */
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
		color: var(--vs-amber);
		font-weight: 600;
	}

	/* ── PROGRESS BAR ── */
	.progress-bar-wrap {
		height: 3px;
		background: var(--vs-border);
		width: 100%;
		margin: 2rem 0 0;
	}
	.progress-bar-fill {
		height: 100%;
		background: var(--vs-amber);
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
		color: var(--vs-amber);
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
     MODULE-SPECIFIC COMPONENTS
  ════════════════════════════════════════════ */

	/* ── BEAT MAP ── */
	#beatmap-canvas {
		width: 100%;
		height: 120px;
		display: block;
		border: 1px solid var(--vs-border);
		cursor: crosshair;
	}
	.bm-playhead {
		width: 100%;
		height: 4px;
		background: var(--vs-border);
		margin-top: 4px;
		position: relative;
		overflow: hidden;
	}
	.bm-playhead-fill {
		height: 100%;
		background: var(--vs-amber);
		width: 0%;
		transition: width 0.05s linear;
	}
	.bm-time {
		font-size: 11px;
		color: var(--vs-muted);
		margin-top: 6px;
		display: flex;
		justify-content: space-between;
	}
	.bm-stats {
		display: flex;
		gap: 1.5rem;
		margin-top: 1rem;
		flex-wrap: wrap;
	}
	.bm-stat {
		border: 1px solid var(--vs-border);
		padding: 0.5rem 1rem;
		font-size: 11px;
		background: var(--vs-raised);
	}
	.bm-stat-val {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		line-height: 1.1;
	}
	.bm-stat-lbl {
		color: var(--vs-muted);
		font-size: 10px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	/* ── PACING SIMULATOR ── */
	.pace-track {
		position: relative;
		height: 64px;
		background: var(--vs-raised);
		border: 1px solid var(--vs-border);
		margin: 0.75rem 0;
		overflow: hidden;
	}
	.pace-track-label {
		position: absolute;
		left: 8px;
		top: 50%;
		transform: translateY(-50%);
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--vs-muted);
		z-index: 2;
		width: 60px;
	}
	.pace-clips-wrap {
		position: absolute;
		left: 74px;
		right: 0;
		top: 8px;
		bottom: 8px;
		display: flex;
		gap: 2px;
	}
	:global(.pace-clip) {
		border-radius: 2px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 9px;
		font-weight: 600;
		letter-spacing: 0.05em;
		overflow: hidden;
		white-space: nowrap;
		transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
		flex-shrink: 0;
	}
	:global(.pace-separator) {
		width: 1px;
		background: var(--vs-border2);
		align-self: stretch;
		margin: 0 1px;
		flex-shrink: 0;
	}
	.pace-playhead {
		position: absolute;
		left: 74px;
		top: 0;
		bottom: 0;
		width: 2px;
		background: #fff;
		opacity: 0;
		transition: left 0.05s linear;
		z-index: 3;
		box-shadow: 0 0 6px rgba(255, 255, 255, 0.4);
	}
	.pace-info {
		margin-top: 1.5rem;
		padding: 1rem;
		border: 1px solid var(--vs-border);
		background: #040710;
		font-size: 12px;
		min-height: 60px;
	}
	:global(.pace-info strong) {
		color: var(--vs-amber);
	}

	/* ── CADENCE WHEEL ── */
	#cadence-canvas {
		display: block;
		margin: 0 auto;
	}

	/* ── CHUNK BUILDER ── */
	:global(.chunk-row) {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin: 0.5rem 0;
		flex-wrap: wrap;
	}
	:global(.chunk-block) {
		padding: 0.35rem 0.75rem;
		border: 1px solid;
		font-size: 11px;
		border-radius: 2px;
		cursor: default;
		transition: all 0.2s;
	}
	:global(.chunk-divider) {
		width: 20px;
		height: 2px;
		background: var(--vs-border2);
		flex-shrink: 0;
	}
	:global(.chunk-divider.strong) {
		background: var(--vs-amber);
	}
	:global(.chunk-label) {
		font-size: 10px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--vs-muted);
		min-width: 70px;
	}
	.chunk-meter {
		height: 6px;
		background: var(--vs-border);
		flex: 1;
		border-radius: 3px;
		overflow: hidden;
		min-width: 100px;
	}
	.chunk-meter-fill {
		height: 100%;
		border-radius: 3px;
		transition: width 0.4s ease;
	}
	.overload-warning {
		font-size: 11px;
		color: var(--vs-red);
		margin-top: 0.25rem;
		min-height: 1.2em;
	}

	/* ── RHYTHM PATTERN ── */
	.rhythm-grid {
		display: flex;
		gap: 3px;
		flex-wrap: wrap;
		margin: 1rem 0;
	}
	:global(.rhythm-beat) {
		width: 28px;
		height: 28px;
		border: 1px solid var(--vs-border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 9px;
		cursor: pointer;
		transition: all 0.15s;
		user-select: none;
	}
	:global(.rhythm-beat:hover) {
		border-color: var(--vs-border2);
	}
	:global(.rhythm-beat.cut) {
		background: color-mix(in srgb, var(--vs-amber) 20%, transparent);
		border-color: var(--vs-amber);
		color: var(--vs-amber);
	}
	:global(.rhythm-beat.hold) {
		background: color-mix(in srgb, var(--vs-blue) 12%, transparent);
		border-color: var(--vs-blue);
		color: var(--vs-blue);
	}
	:global(.rhythm-beat.peak) {
		background: color-mix(in srgb, var(--vs-red) 20%, transparent);
		border-color: var(--vs-red);
		color: var(--vs-red);
	}
</style>
