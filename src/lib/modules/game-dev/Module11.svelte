<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, svelte/prefer-svelte-reactivity */
	import { onMount } from 'svelte';

	let actions = new Proxy(
		{},
		{
			get: (target, prop) => {
				if (prop === 'then') return undefined;
				if (typeof prop !== 'string') return (..._args) => {};
				if (prop in target) return target[prop];
				return (..._args) => {};
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
		/* ═══════════════════ FSM DIAGRAM ═══════════════════ */
		const fsmC = document.getElementById('fsm-canvas'),
			fsmX = fsmC.getContext('2d');
		const FSM = [
			{ id: 'title', x: 60, y: 103, w: 120, h: 54, label: 'TITLE\nSCREEN', col: '#a78bfa' },
			{ id: 'play', x: 280, y: 103, w: 120, h: 54, label: 'GAMEPLAY', col: '#34d399' },
			{ id: 'pause', x: 280, y: 20, w: 110, h: 42, label: 'PAUSED', col: '#fbbf24' },
			{ id: 'gameover', x: 530, y: 160, w: 120, h: 54, label: 'GAME\nOVER', col: '#f87171' },
			{ id: 'victory', x: 530, y: 50, w: 120, h: 54, label: 'VICTORY', col: '#60a5fa' }
		];
		const FSMTR = [
			{ f: 'title', t: 'play', lbl: 'Start' },
			{ f: 'play', t: 'pause', lbl: 'ESC' },
			{ f: 'pause', t: 'play', lbl: 'Resume' },
			{ f: 'pause', t: 'title', lbl: 'Quit' },
			{ f: 'play', t: 'gameover', lbl: 'lives≤0' },
			{ f: 'play', t: 'victory', lbl: 'cleared' },
			{ f: 'gameover', t: 'title', lbl: 'ENTER' },
			{ f: 'victory', t: 'play', lbl: 'Next Level' },
			{ f: 'victory', t: 'title', lbl: 'ESC' }
		];
		const FSMDET = {
			title:
				'on_enter: load title assets, start menu music\nupdate: wait for start input\non_exit: stop music\ntransitions → GAMEPLAY on Start/Enter',
			play: 'on_enter: build_level(n), spawn player and enemies\nupdate: run all 8 engine subsystems\non_exit: save score, destroy world\ntransitions → PAUSED, GAMEOVER, VICTORY',
			pause:
				'on_enter: freeze all timers and physics\nupdate: handle resume/quit input only\non_exit: resume timers\ntransitions → GAMEPLAY (resume), TITLE (quit)',
			gameover:
				'on_enter: play death SFX, show final score\nupdate: wait for restart input\non_exit: reset score display\ntransitions → TITLE on Enter',
			victory:
				'on_enter: play win fanfare, tally score\nupdate: wait for next-level or menu input\non_exit: save high score\ntransitions → GAMEPLAY (next level), TITLE (menu)'
		};
		const nodeMap = {};
		FSM.forEach((s) => (nodeMap[s.id] = s));
		let fsmCur = 'title';
		function drawFSM() {
			const W = fsmC.width,
				H = fsmC.height;
			fsmX.clearRect(0, 0, W, H);
			fsmX.fillStyle = '#050310';
			fsmX.fillRect(0, 0, W, H);
			FSMTR.forEach((tr) => {
				const a = nodeMap[tr.f],
					b = nodeMap[tr.t];
				const ax = a.x + a.w / 2,
					ay = a.y + a.h / 2,
					bx = b.x + b.w / 2,
					by = b.y + b.h / 2;
				const dx = bx - ax,
					dy = by - ay,
					len = Math.sqrt(dx * dx + dy * dy) || 1;
				const ux = dx / len,
					uy = dy / len;
				const sx = ax + ux * (a.w / 2 + 4),
					sy = ay + uy * (a.h / 2 + 4);
				const ex = bx - ux * (b.w / 2 + 8),
					ey = by - uy * (b.h / 2 + 8);
				const act = tr.f === fsmCur || tr.t === fsmCur;
				fsmX.beginPath();
				fsmX.moveTo(sx, sy);
				fsmX.lineTo(ex, ey);
				fsmX.strokeStyle = act ? nodeMap[tr.f].col + '80' : '#201a38';
				fsmX.lineWidth = act ? 1.5 : 1;
				fsmX.stroke();
				const ang = Math.atan2(ey - sy, ex - sx);
				fsmX.beginPath();
				fsmX.moveTo(ex, ey);
				fsmX.lineTo(ex - 8 * Math.cos(ang - 0.4), ey - 8 * Math.sin(ang - 0.4));
				fsmX.lineTo(ex - 8 * Math.cos(ang + 0.4), ey - 8 * Math.sin(ang + 0.4));
				fsmX.closePath();
				fsmX.fillStyle = act ? nodeMap[tr.f].col + '80' : '#201a38';
				fsmX.fill();
				if (act) {
					fsmX.font = '9px IBM Plex Mono';
					fsmX.fillStyle = nodeMap[tr.f].col + '90';
					fsmX.textAlign = 'center';
					fsmX.fillText(tr.lbl, (sx + ex) / 2, (sy + ey) / 2 - 6);
				}
			});
			FSM.forEach((s) => {
				const isc = s.id === fsmCur;
				fsmX.fillStyle = isc ? s.col + '22' : s.col + '0d';
				fsmX.fillRect(s.x, s.y, s.w, s.h);
				fsmX.strokeStyle = isc ? s.col : '#2e2650';
				fsmX.lineWidth = isc ? 2 : 1;
				if (isc) {
					fsmX.shadowColor = s.col;
					fsmX.shadowBlur = 10;
				}
				fsmX.strokeRect(s.x, s.y, s.w, s.h);
				fsmX.shadowBlur = 0;
				const lines = s.label.split('\n');
				fsmX.font = 'bold 12px IBM Plex Mono';
				fsmX.fillStyle = isc ? s.col : '#50408a';
				fsmX.textAlign = 'center';
				lines.forEach((l, i) =>
					fsmX.fillText(l, s.x + s.w / 2, s.y + s.h / 2 + (i - (lines.length - 1) / 2) * 14 + 2)
				);
				if (isc) {
					fsmX.font = '9px IBM Plex Mono';
					fsmX.fillStyle = s.col + '70';
					fsmX.fillText('● CURRENT', s.x + s.w / 2, s.y + s.h + 12);
				}
			});
		}
		fsmC.addEventListener('click', (e) => {
			const r = fsmC.getBoundingClientRect();
			const mx = ((e.clientX - r.left) / r.width) * fsmC.width,
				my = ((e.clientY - r.top) / r.height) * fsmC.height;
			FSM.forEach((s) => {
				if (mx >= s.x && mx <= s.x + s.w && my >= s.y && my <= s.y + s.h) {
					fsmCur = s.id;
					drawFSM();
					document.getElementById('fsm-detail').innerHTML =
						`<span style="color:${s.col};font-weight:600;">${s.label.replace('\n', ' ')}</span><br>` +
						`<pre style="margin-top:.4rem;font-size:11px;background:transparent;border:none;padding:0;color:var(--muted);white-space:pre-wrap;">${FSMDET[s.id]}</pre>`;
				}
			});
		});
		drawFSM();

		/* ═══════════════════ SCORING DEMO ═══════════════════ */
		const scC = document.getElementById('score-canvas'),
			scX = scC.getContext('2d');
		let sc = { score: 0, hi: 0, combo: 0, lives: 3, level: 1 };
		let scLogs = [],
			scFloats = [],
			scPrevT = performance.now();

		function scoreKill() {
			sc.combo++;
			const mult = 1 + (sc.combo - 1) * 0.5,
				pts = Math.floor(20 * mult);
			sc.score += pts;
			if (sc.score > sc.hi) sc.hi = sc.score;
			const m = sc.combo > 1 ? `+${pts} (${mult.toFixed(1)}× COMBO)` : `+${pts}`;
			scLogs.unshift({ t: performance.now(), msg: m, col: sc.combo > 1 ? '#fbbf24' : '#34d399' });
			scFloats.push({
				x: 100 + Math.random() * 600,
				y: 80,
				vy: -60,
				life: 1.4,
				msg: m,
				col: sc.combo > 1 ? '#fbbf24' : '#34d399'
			});
			updateScUI();
		}
		function scoreCoin() {
			sc.score += 5;
			if (sc.score > sc.hi) sc.hi = sc.score;
			scLogs.unshift({ t: performance.now(), msg: '★+5', col: '#fbbf24' });
			scFloats.push({
				x: 300 + Math.random() * 200,
				y: 90,
				vy: -50,
				life: 1,
				msg: '★+5',
				col: '#fbbf24'
			});
			updateScUI();
		}
		function scoreHit() {
			sc.combo = 0;
			sc.lives = Math.max(0, sc.lives - 1);
			scLogs.unshift({ t: performance.now(), msg: '💥 Hit! Combo reset', col: '#f87171' });
			scFloats.push({ x: 400, y: 80, vy: -40, life: 1, msg: '💥', col: '#f87171' });
			updateScUI();
		}
		function scoreLevelClear() {
			const bonus = sc.lives * 50;
			sc.score += bonus;
			if (sc.score > sc.hi) sc.hi = sc.score;
			sc.level++;
			scLogs.unshift({ t: performance.now(), msg: `Level clear! +${bonus}`, col: '#60a5fa' });
			scFloats.push({
				x: 430,
				y: 60,
				vy: -80,
				life: 2,
				msg: `LEVEL CLEAR +${bonus}`,
				col: '#60a5fa'
			});
			updateScUI();
		}
		function scoreReset() {
			sc = { score: 0, hi: 0, combo: 0, lives: 3, level: 1 };
			scLogs = [];
			scFloats = [];
			updateScUI();
		}
		function updateScUI() {
			document.getElementById('sc-score').textContent = sc.score;
			document.getElementById('sc-hi').textContent = sc.hi;
			document.getElementById('sc-combo').textContent = sc.combo;
			document.getElementById('sc-mult').textContent =
				(1 + Math.max(0, sc.combo - 1) * 0.5).toFixed(1) + '×';
			document.getElementById('sc-lives').textContent = '♥'.repeat(sc.lives) || '—';
			document.getElementById('sc-log').innerHTML = scLogs
				.slice(0, 8)
				.map((l) => `<div style="color:${l.col};padding:1px 0;">${l.msg}</div>`)
				.join('');
		}
		function drawScore() {
			const W = scC.width,
				H = scC.height,
				now = performance.now(),
				dt = (now - scPrevT) / 1000;
			scPrevT = now;
			scX.clearRect(0, 0, W, H);
			scX.fillStyle = '#050310';
			scX.fillRect(0, 0, W, H);
			const mult = 1 + Math.max(0, sc.combo - 1) * 0.5;
			const mw = Math.min(W - 40, (mult - 1) * 180);
			scX.fillStyle = '#201a38';
			scX.fillRect(20, H - 24, W - 40, 12);
			if (mw > 0) {
				scX.fillStyle = sc.combo > 3 ? '#fbbf24' : '#34d399';
				scX.fillRect(20, H - 24, mw, 12);
			}
			scX.font = '10px IBM Plex Mono';
			scX.fillStyle = '#4a3870';
			scX.textAlign = 'left';
			scX.fillText('COMBO METER', 22, H - 28);
			scX.fillStyle = '#fff';
			scX.textAlign = 'right';
			scX.fillText(mult.toFixed(1) + '×', W - 22, H - 28);
			scX.font = 'bold 26px Syne,sans-serif';
			scX.fillStyle = '#e879f9';
			scX.textAlign = 'center';
			scX.fillText(sc.score.toString().padStart(6, '0'), W / 2, 46);
			scX.font = '10px IBM Plex Mono';
			scX.fillStyle = '#4a3870';
			scX.fillText('SCORE', W / 2, 14);
			for (let i = 0; i < 3; i++) {
				scX.fillStyle = i < sc.lives ? '#f87171' : '#201a38';
				scX.font = '18px sans-serif';
				scX.textAlign = 'left';
				scX.fillText('♥', 16 + i * 26, 52);
			}
			scFloats = scFloats.filter((f) => {
				f.y += f.vy * dt;
				f.life -= dt;
				if (f.life <= 0) return false;
				scX.globalAlpha = Math.min(1, f.life * 2);
				scX.font = 'bold 13px IBM Plex Mono';
				scX.fillStyle = f.col;
				scX.textAlign = 'center';
				scX.fillText(f.msg, f.x, f.y);
				scX.globalAlpha = 1;
				return true;
			});
			requestAnimationFrame(drawScore);
		}
		drawScore();
		updateScUI();

		/* ═══════════════════ JUICE DEMO ═══════════════════ */
		const jC = document.getElementById('juice-canvas'),
			jX = jC.getContext('2d');
		let jEff = { shake: true, particles: true, flash: true, squash: true, text: true };
		let jShake = { trauma: 0 },
			jParts = [],
			jTexts = [],
			jObj = { x: 430, y: 140, scaleX: 1, scaleY: 1, flash: 0 },
			jLT = performance.now();

		function buildJuiceToggles() {
			document.getElementById('juice-toggles').innerHTML = Object.entries(jEff)
				.map(
					([k, v]) =>
						`<button class="btn ${v ? 'active' : ''}" id="jt-${k}" onclick="toggleJ('${k}',this)">${k}</button>`
				)
				.join('');
		}
		function toggleJ(k, btn) {
			jEff[k] = !jEff[k];
			btn.classList.toggle('active', jEff[k]);
		}

		jC.addEventListener('click', (e) => {
			const r = jC.getBoundingClientRect();
			const cx = ((e.clientX - r.left) / r.width) * jC.width,
				cy = ((e.clientY - r.top) / r.height) * jC.height;
			if (jEff.shake) jShake.trauma = Math.min(1, jShake.trauma + 0.7);
			if (jEff.particles) {
				for (let i = 0; i < 18; i++) {
					const a = Math.random() * Math.PI * 2,
						sp = 60 + Math.random() * 180,
						col = ['#e879f9', '#fbbf24', '#34d399', '#60a5fa'][Math.floor(Math.random() * 4)];
					jParts.push({
						x: cx,
						y: cy,
						vx: Math.cos(a) * sp,
						vy: Math.sin(a) * sp - 60,
						r: 2 + Math.random() * 4,
						life: 0.5 + Math.random() * 0.4,
						maxLife: 0.9,
						col
					});
				}
			}
			if (jEff.flash) jObj.flash = 0.2;
			if (jEff.squash) {
				jObj.scaleX = 1.6;
				jObj.scaleY = 0.5;
			}
			if (jEff.text)
				jTexts.push({
					x: cx,
					y: cy,
					vy: -80,
					life: 1.2,
					msg: ['BOOM!', 'COMBO!', 'NICE!', 'ULTRA!'][Math.floor(Math.random() * 4)],
					col: '#fbbf24'
				});
		});

		function drawJuice() {
			const W = jC.width,
				H = jC.height,
				now = performance.now(),
				dt = Math.min((now - jLT) / 1000, 0.05);
			jLT = now;
			jShake.trauma = Math.max(0, jShake.trauma - dt * 2.5);
			const si = jEff.shake ? jShake.trauma ** 2 : 0;
			const ox = (Math.random() - 0.5) * 2 * 16 * si,
				oy = (Math.random() - 0.5) * 2 * 16 * si;
			jX.clearRect(0, 0, W, H);
			jX.fillStyle = '#04020c';
			jX.fillRect(0, 0, W, H);
			jX.save();
			jX.translate(ox, oy);
			jX.fillStyle = '#141025';
			jX.fillRect(0, H - 28, W, 28);
			jObj.flash = Math.max(0, jObj.flash - dt);
			if (jEff.squash) {
				jObj.scaleX += (1 - jObj.scaleX) * 10 * dt;
				jObj.scaleY += (1 - jObj.scaleY) * 10 * dt;
			} else {
				jObj.scaleX = 1;
				jObj.scaleY = 1;
			}
			jX.save();
			jX.translate(jObj.x, jObj.y + 14);
			jX.scale(jObj.scaleX, jObj.scaleY);
			const flash = jEff.flash && jObj.flash > 0;
			jX.fillStyle = flash ? '#ffffff' : '#e879f940';
			jX.fillRect(-18, -18, 36, 36);
			jX.strokeStyle = flash ? '#ffffff' : '#e879f9';
			jX.lineWidth = 2;
			jX.strokeRect(-18, -18, 36, 36);
			jX.restore();
			jParts = jParts.filter((p) => {
				p.x += p.vx * dt;
				p.y += p.vy * dt;
				p.vy += 300 * dt;
				p.life -= dt;
				if (p.life <= 0) return false;
				jX.globalAlpha = p.life / p.maxLife;
				jX.beginPath();
				jX.arc(p.x, p.y, p.r, 0, Math.PI * 2);
				jX.fillStyle = p.col;
				jX.fill();
				jX.globalAlpha = 1;
				return true;
			});
			jTexts = jTexts.filter((t) => {
				t.y += t.vy * dt;
				t.life -= dt;
				if (t.life <= 0) return false;
				jX.globalAlpha = Math.min(1, t.life);
				jX.font = 'bold 16px Syne,sans-serif';
				jX.fillStyle = t.col;
				jX.textAlign = 'center';
				jX.fillText(t.msg, t.x, t.y);
				jX.globalAlpha = 1;
				return true;
			});
			jX.restore();
			jX.font = '11px IBM Plex Mono';
			jX.fillStyle = '#4a3870';
			jX.textAlign = 'center';
			jX.fillText('Click to trigger effects', W / 2, 16);
			requestAnimationFrame(drawJuice);
		}
		buildJuiceToggles();
		drawJuice();

		/* ═══════════════════ THE COMPLETE GAME ═══════════════════ */
		const GC = document.getElementById('game-canvas'),
			GX = GC.getContext('2d');
		const GW = GC.width,
			GH = GC.height;
		function rnd(a, b) {
			return a + Math.random() * (b - a);
		}
		function clamp(v, lo, hi) {
			return Math.min(hi, Math.max(lo, v));
		}
		function aabb(ax, ay, aw, ah, bx, by, bw, bh) {
			return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
		}

		let gState = 'title',
			gLastT = performance.now(),
			gScore = 0,
			gHiScore = 0,
			gLives = 3,
			gLevel = 1,
			gCombo = 0;
		let gPlayer, gPlatforms, gEnemies, gCoins, gBullets, gParticles, gFloats;
		let gShake = { trauma: 0 },
			gCamX = 0,
			gCamY = 0,
			gMouseX = GW / 2,
			gMouseY = GH / 2,
			gMDown = false,
			gShot = 0;
		const gHeld = new Set(),
			gPressed = new Set();

		_addDocListener('keydown', (e) => {
			if (e.repeat) return;
			gHeld.add(e.key);
			gPressed.add(e.key);
			if ([' ', 'ArrowUp', 'ArrowDown'].includes(e.key)) e.preventDefault();
		});
		_addDocListener('keyup', (e) => {
			gHeld.delete(e.key);
		});
		GC.addEventListener('mousemove', (e) => {
			const r = GC.getBoundingClientRect();
			gMouseX = ((e.clientX - r.left) / r.width) * GW;
			gMouseY = ((e.clientY - r.top) / r.height) * GH;
		});
		GC.addEventListener('mousedown', (e) => {
			if (e.button === 0) {
				gMDown = true;
				if (gState === 'title' || gState === 'gameover' || gState === 'victory') startGame();
			}
			e.preventDefault();
		});
		GC.addEventListener('mouseup', (e) => {
			if (e.button === 0) gMDown = false;
		});
		GC.addEventListener('contextmenu', (e) => e.preventDefault());

		function makePlats(lv) {
			const p = [
				{ x: 0, y: GH - 30, w: GW, h: 30 },
				{ x: 80, y: GH - 155, w: 170, h: 13 },
				{ x: 340, y: GH - 195, w: 150, h: 13 },
				{ x: 590, y: GH - 155, w: 170, h: 13 },
				{ x: 180, y: GH - 275, w: 130, h: 13 },
				{ x: 470, y: GH - 295, w: 120, h: 13 },
				{ x: 60, y: GH - 375, w: 120, h: 13 },
				{ x: 650, y: GH - 355, w: 130, h: 13 },
				{ x: 300, y: GH - 395, w: 240, h: 13 }
			];
			if (lv >= 2)
				p.push({ x: 150, y: GH - 455, w: 90, h: 13 }, { x: 570, y: GH - 435, w: 100, h: 13 });
			return p;
		}
		function makeEnemies(lv) {
			const plats = gPlatforms.slice(1),
				count = 3 + lv * 2,
				enemies = [];
			for (let i = 0; i < count; i++) {
				const pl = plats[Math.floor(Math.random() * plats.length)];
				enemies.push({
					x: pl.x + pl.w * 0.4,
					y: pl.y - 28,
					w: 20,
					h: 28,
					vx: rnd(40, 80) * (Math.random() < 0.5 ? 1 : -1),
					vy: 0,
					hp: 2 + lv,
					maxHp: 2 + lv,
					col: '#f87171',
					pl,
					flash: 0,
					dt: -1,
					pL: pl.x,
					pR: pl.x + pl.w - 20
				});
			}
			return enemies;
		}
		function makeCoins(lv) {
			return [
				[200, GH - 200],
				[440, GH - 250],
				[630, GH - 215],
				[160, GH - 325],
				[510, GH - 345],
				[60, GH - 425],
				[660, GH - 410],
				[380, GH - 445]
			]
				.slice(0, 5 + lv)
				.map(([cx, cy]) => ({
					x: cx,
					y: cy,
					origY: cy,
					r: 8,
					col: false,
					bobT: Math.random() * Math.PI * 2
				}));
		}
		function spawnParts(x, y, col, n = 12) {
			for (let i = 0; i < n; i++) {
				const a = rnd(0, Math.PI * 2),
					sp = rnd(60, 220);
				gParticles.push({
					x,
					y,
					vx: Math.cos(a) * sp,
					vy: Math.sin(a) * sp - 60,
					r: rnd(2, 5),
					life: rnd(0.3, 0.6),
					ml: 0.6,
					col
				});
			}
		}
		function addFloat(x, y, msg, col = '#fbbf24') {
			gFloats.push({ x, y, vy: -70, life: 1.4, msg, col });
		}
		function shake(v) {
			gShake.trauma = clamp(gShake.trauma + v, 0, 1);
		}

		function buildLevel(lv) {
			gPlatforms = makePlats(lv);
			gEnemies = makeEnemies(lv);
			gCoins = makeCoins(lv);
			gBullets = [];
			gParticles = [];
			gFloats = [];
			gShake.trauma = 0;
			gShot = 0;
			gPlayer = {
				x: 60,
				y: GH - 200,
				w: 22,
				h: 30,
				vx: 0,
				vy: 0,
				hp: 5,
				maxHp: 5,
				onG: false,
				face: 1,
				jHeld: false,
				jTime: 0,
				coy: 0,
				jBuf: 0,
				flash: 0,
				inv: 0,
				scX: 1,
				scY: 1
			};
		}

		function startGame() {
			gState = 'playing';
			gScore = 0;
			gCombo = 0;
			gLives = 3;
			gLevel = 1;
			buildLevel(1);
		}

		function pDie() {
			if (gPlayer) spawnParts(gPlayer.x + gPlayer.w / 2, gPlayer.y + gPlayer.h / 2, '#f87171', 20);
			shake(0.9);
			gLives--;
			if (gLives <= 0) {
				gState = 'gameover';
				return;
			}
			gPlayer.x = 80;
			gPlayer.y = GH - 200;
			gPlayer.vx = 0;
			gPlayer.vy = 0;
			gPlayer.inv = 2;
			gCombo = 0;
		}

		function pHit() {
			const p = gPlayer;
			if (p.inv > 0) return;
			p.hp--;
			p.flash = 0.3;
			p.inv = 1.5;
			shake(0.5);
			gCombo = 0;
			const juice = parseInt(document.getElementById('gm-juice').value) / 100;
			if (juice > 0.4) spawnParts(p.x + p.w / 2, p.y + p.h / 2, '#f87171', 6);
			if (p.hp <= 0) {
				p.hp = 0;
				pDie();
			}
		}

		function updatePlayer(dt) {
			const p = gPlayer,
				juice = parseInt(document.getElementById('gm-juice').value) / 100;
			const gravity = parseInt(document.getElementById('gm-gravity').value);
			document.getElementById('gm-gravity-val').textContent = gravity;
			document.getElementById('gm-juice-val').textContent = Math.round(juice * 100) + '%';
			if (p.onG) p.coy = 0.1;
			else p.coy = Math.max(0, p.coy - dt);
			p.jBuf = Math.max(0, p.jBuf - dt);
			const left = gHeld.has('ArrowLeft') || gHeld.has('a') || gHeld.has('A');
			const right = gHeld.has('ArrowRight') || gHeld.has('d') || gHeld.has('D');
			const jKey = gHeld.has(' ') || gHeld.has('w') || gHeld.has('W') || gHeld.has('ArrowUp');
			const jJP =
				gPressed.has(' ') || gPressed.has('w') || gPressed.has('W') || gPressed.has('ArrowUp');
			if (jJP) p.jBuf = 0.1;
			if (p.coy > 0 && p.jBuf > 0) {
				p.vy = -520;
				p.jHeld = true;
				p.jTime = 0;
				p.coy = 0;
				p.jBuf = 0;
				if (juice > 0.3) spawnParts(p.x + p.w / 2, p.y + p.h, '#a78bfa', 5);
				if (juice > 0.5) {
					p.scX = 0.7;
					p.scY = 1.5;
				}
			}
			if (jKey && p.jHeld) {
				p.jTime += dt;
				if (p.jTime < 0.2) p.vy -= 520 * 0.8 * dt;
				else p.jHeld = false;
			}
			if (!jKey) p.jHeld = false;
			if (left) {
				p.vx -= 720 * dt;
				p.face = -1;
			}
			if (right) {
				p.vx += 720 * dt;
				p.face = 1;
			}
			p.vx *= 1 - 8 * dt;
			p.vy += gravity * dt;
			p.vy = clamp(p.vy, -1200, 900);
			if (juice > 0.5) {
				p.scX += (1 - p.scX) * 10 * dt;
				p.scY += (1 - p.scY) * 10 * dt;
			} else {
				p.scX = 1;
				p.scY = 1;
			}
			p.flash = Math.max(0, p.flash - dt);
			p.inv = Math.max(0, p.inv - dt);
			p.x += p.vx * dt;
			p.y += p.vy * dt;
			p.onG = false;
			gPlatforms.forEach((pl) => {
				if (!aabb(p.x, p.y, p.w, p.h, pl.x, pl.y, pl.w, pl.h)) return;
				const ox = Math.min(p.x + p.w, pl.x + pl.w) - Math.max(p.x, pl.x);
				const oy = Math.min(p.y + p.h, pl.y + pl.h) - Math.max(p.y, pl.y);
				if (oy < ox) {
					if (p.vy >= 0 && p.y + p.h / 2 < pl.y + pl.h / 2) {
						p.y = pl.y - p.h;
						p.vy = 0;
						p.onG = true;
						p.jHeld = false;
						if (juice > 0.5 && p.scY < 0.85) {
							p.scX = 1.5;
							p.scY = 0.6;
						}
						if (juice > 0.4) spawnParts(p.x + p.w / 2, p.y + p.h, '#6050a0', 3);
					} else if (p.vy < 0) {
						p.y = pl.y + pl.h;
						p.vy = 0;
					}
				} else {
					if (p.vx > 0) p.x = pl.x - p.w;
					else p.x = pl.x + pl.w;
					p.vx = 0;
				}
			});
			if (p.x + p.w < 0) p.x = GW;
			if (p.x > GW) p.x = -p.w;
			if (p.y > GH + 60) pDie();
		}

		function updateEnemies(dt) {
			gEnemies.forEach((e) => {
				if (e.dt >= 0) {
					e.dt += dt;
					return;
				}
				e.flash = Math.max(0, e.flash - dt);
				e.x += e.vx * dt;
				e.vy += 600 * dt;
				e.y += e.vy * dt;
				if (aabb(e.x, e.y, e.w, e.h, e.pl.x, e.pl.y, e.pl.w, e.pl.h)) {
					e.y = e.pl.y - e.h;
					e.vy = 0;
				}
				if (e.x <= e.pL || e.x >= e.pR) e.vx *= -1;
				e.x = clamp(e.x, e.pL, e.pR);
				if (aabb(e.x, e.y, e.w, e.h, gPlayer.x, gPlayer.y, gPlayer.w, gPlayer.h)) pHit();
			});
			gBullets.forEach((b) => {
				gEnemies.forEach((e) => {
					if (e.dt >= 0) return;
					if (aabb(b.x - b.r, b.y - b.r, b.r * 2, b.r * 2, e.x, e.y, e.w, e.h)) {
						b.dead = true;
						e.hp--;
						e.flash = 0.1;
						const juice = parseInt(document.getElementById('gm-juice').value) / 100;
						if (juice > 0.3) spawnParts(b.x, b.y, '#fbbf24', 5);
						if (e.hp <= 0) {
							e.dt = 0;
							gCombo++;
							const mult = 1 + (gCombo - 1) * 0.5,
								pts = Math.floor(20 * mult);
							gScore += pts;
							if (gScore > gHiScore) gHiScore = gScore;
							addFloat(
								e.x + e.w / 2,
								e.y,
								gCombo > 1 ? `+${pts} ${mult.toFixed(1)}×!` : `+${pts}`,
								'#fbbf24'
							);
							if (juice > 0.5) {
								shake(0.3);
								spawnParts(e.x + e.w / 2, e.y + e.h / 2, '#f87171', 14);
							}
						}
					}
				});
			});
			gEnemies = gEnemies.filter((e) => e.dt < 0 || e.dt < 0.4);
		}

		function updateBullets(dt) {
			gShot = Math.max(0, gShot - dt);
			if ((gMDown || gPressed.has('e') || gPressed.has('E')) && gShot <= 0) {
				const px = gPlayer.x + gPlayer.w / 2,
					py = gPlayer.y + gPlayer.h / 2;
				const dx = gMouseX - px,
					dy = gMouseY - py,
					len = Math.sqrt(dx * dx + dy * dy) || 1;
				gBullets.push({
					x: px,
					y: py,
					vx: (dx / len) * 620,
					vy: (dy / len) * 620,
					r: 4,
					life: 1.5,
					dead: false
				});
				gShot = 0.18;
			}
			gBullets = gBullets.filter((b) => {
				b.x += b.vx * dt;
				b.y += b.vy * dt;
				b.life -= dt;
				return b.life > 0 && !b.dead && b.x > 0 && b.x < GW && b.y > 0 && b.y < GH;
			});
		}

		function updateCoins(dt) {
			gCoins.forEach((c) => {
				if (c.col) return;
				c.bobT += dt * 3;
				c.y = c.origY + Math.sin(c.bobT) * 4;
				if (
					aabb(gPlayer.x, gPlayer.y, gPlayer.w, gPlayer.h, c.x - c.r, c.y - c.r, c.r * 2, c.r * 2)
				) {
					c.col = true;
					gScore += 5;
					if (gScore > gHiScore) gHiScore = gScore;
					spawnParts(c.x, c.y, '#fbbf24', 8);
					addFloat(c.x, c.y - 14, '★+5', '#fbbf24');
				}
			});
		}

		function updateShake(dt) {
			gShake.trauma = Math.max(0, gShake.trauma - dt * 2.5);
			const si = gShake.trauma ** 2,
				juice = parseInt(document.getElementById('gm-juice').value) / 100;
			gCamX = (Math.random() - 0.5) * 2 * 18 * si * juice;
			gCamY = (Math.random() - 0.5) * 2 * 18 * si * juice;
		}

		function checkWin() {
			if (gState !== 'playing') return;
			if (gEnemies.every((e) => e.dt >= 0)) {
				const cb = gCoins.filter((c) => c.col).length * 10;
				gScore += cb;
				if (gScore > gHiScore) gHiScore = gScore;
				gState = 'victory';
			}
		}

		function drawWorld() {
			GX.save();
			GX.translate(gCamX, gCamY);
			// Stars
			GX.fillStyle = '#6050a020';
			for (let i = 0; i < 30; i++) {
				GX.fillRect((i * 137) % GW, (i * 197) % GH, 1, 1);
			}
			// Platforms
			gPlatforms.forEach((pl, i) => {
				GX.fillStyle = i === 0 ? '#141025' : '#1a1030';
				GX.fillRect(pl.x, pl.y, pl.w, pl.h);
				GX.strokeStyle = '#e879f925';
				GX.lineWidth = 1;
				GX.strokeRect(pl.x, pl.y, pl.w, pl.h);
			});
			// Coins
			gCoins.forEach((c) => {
				if (c.col) return;
				GX.beginPath();
				GX.arc(c.x, c.y, c.r, 0, Math.PI * 2);
				GX.fillStyle = '#fbbf2428';
				GX.fill();
				GX.strokeStyle = '#fbbf24';
				GX.lineWidth = 1.5;
				GX.stroke();
				GX.font = 'bold 9px sans-serif';
				GX.fillStyle = '#fbbf24';
				GX.textAlign = 'center';
				GX.fillText('★', c.x, c.y + 3);
			});
			// Particles
			gParticles = gParticles.filter((p) => {
				p.x += p.vx * 0.016;
				p.y += p.vy * 0.016;
				p.vy += 300 * 0.016;
				p.life -= 0.016;
				if (p.life <= 0) return false;
				GX.globalAlpha = p.life / p.ml;
				GX.beginPath();
				GX.arc(p.x, p.y, p.r, 0, Math.PI * 2);
				GX.fillStyle = p.col;
				GX.fill();
				GX.globalAlpha = 1;
				return true;
			});
			// Enemies
			gEnemies.forEach((e) => {
				const al = e.dt >= 0 ? Math.max(0, 1 - e.dt / 0.4) : 1,
					sc2 = e.dt >= 0 ? 1 + e.dt * 2 : 1;
				GX.globalAlpha = al;
				GX.save();
				GX.translate(e.x + e.w / 2, e.y + e.h / 2);
				GX.scale(sc2, sc2);
				const f = e.flash > 0;
				GX.fillStyle = f ? '#ffffff' : '#f8717128';
				GX.fillRect(-e.w / 2, -e.h / 2, e.w, e.h);
				GX.strokeStyle = f ? '#ffffff' : '#f87171';
				GX.lineWidth = 2;
				GX.strokeRect(-e.w / 2, -e.h / 2, e.w, e.h);
				if (e.dt < 0) {
					GX.fillStyle = '#201020';
					GX.fillRect(-e.w / 2, -e.h / 2 - 9, e.w, 5);
					GX.fillStyle = '#f87171';
					GX.fillRect(-e.w / 2, -e.h / 2 - 9, e.w * (e.hp / e.maxHp), 5);
				}
				GX.restore();
				GX.globalAlpha = 1;
			});
			// Bullets
			gBullets.forEach((b) => {
				GX.beginPath();
				GX.arc(b.x, b.y, b.r, 0, Math.PI * 2);
				GX.fillStyle = '#e879f9';
				GX.fill();
				GX.beginPath();
				GX.arc(b.x, b.y, b.r + 3, 0, Math.PI * 2);
				GX.strokeStyle = '#e879f950';
				GX.lineWidth = 1;
				GX.stroke();
			});
			// Player
			const p = gPlayer,
				pf = p.flash > 0 && Math.floor(p.inv * 10) % 2 === 0;
			GX.save();
			GX.translate(p.x + p.w / 2, p.y + p.h / 2);
			GX.scale(p.scX * p.face, p.scY);
			GX.fillStyle = pf ? '#ffffff' : '#e879f935';
			GX.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
			GX.strokeStyle = pf ? '#ffffff' : '#e879f9';
			GX.lineWidth = 2;
			GX.strokeRect(-p.w / 2, -p.h / 2, p.w, p.h);
			GX.fillStyle = '#fff';
			GX.fillRect(4, -8, 5, 5);
			const adx = gMouseX - (p.x + p.w / 2),
				ady = gMouseY - (p.y + p.h / 2),
				al2 = Math.sqrt(adx * adx + ady * ady) || 1;
			GX.beginPath();
			GX.moveTo(0, 0);
			GX.lineTo((adx / al2) * 24, (ady / al2) * 24);
			GX.strokeStyle = '#e879f960';
			GX.lineWidth = 1;
			GX.setLineDash([3, 4]);
			GX.stroke();
			GX.setLineDash([]);
			GX.restore();
			// Float texts
			gFloats = gFloats.filter((ft) => {
				ft.y += ft.vy * 0.016;
				ft.life -= 0.016;
				if (ft.life <= 0) return false;
				GX.globalAlpha = Math.min(1, ft.life);
				GX.font = 'bold 13px IBM Plex Mono';
				GX.fillStyle = ft.col;
				GX.textAlign = 'center';
				GX.fillText(ft.msg, ft.x, ft.y);
				GX.globalAlpha = 1;
				return true;
			});
			GX.restore();
		}

		function drawHUD() {
			const p = gPlayer;
			GX.fillStyle = '#201020';
			GX.fillRect(16, 16, 140, 12);
			GX.fillStyle = p.hp > 2 ? '#e879f9' : '#f87171';
			GX.fillRect(16, 16, 140 * (p.hp / p.maxHp), 12);
			GX.strokeStyle = '#2e2650';
			GX.lineWidth = 1;
			GX.strokeRect(16, 16, 140, 12);
			GX.font = '10px IBM Plex Mono';
			GX.fillStyle = '#fff';
			GX.textAlign = 'left';
			GX.fillText(`HP ${p.hp}/${p.maxHp}`, 20, 26);
			for (let i = 0; i < 3; i++) {
				GX.fillStyle = i < gLives ? '#f87171' : '#201020';
				GX.font = '16px sans-serif';
				GX.textAlign = 'left';
				GX.fillText('♥', 16 + i * 22, 50);
			}
			GX.font = 'bold 18px IBM Plex Mono';
			GX.fillStyle = '#fbbf24';
			GX.textAlign = 'right';
			GX.fillText(gScore.toString().padStart(6, '0'), GW - 16, 28);
			GX.font = '10px IBM Plex Mono';
			GX.fillStyle = '#4a3870';
			GX.fillText(`HI ${gHiScore.toString().padStart(6, '0')}`, GW - 16, 44);
			if (gCombo > 1) {
				GX.font = 'bold 12px IBM Plex Mono';
				GX.fillStyle = '#fbbf24';
				GX.textAlign = 'center';
				GX.fillText(`${gCombo}× COMBO`, GW / 2, 18);
			}
			GX.font = '11px IBM Plex Mono';
			GX.fillStyle = '#4a3870';
			GX.textAlign = 'center';
			const alive = gEnemies.filter((e) => e.dt < 0).length;
			GX.fillText(
				`${alive} enemies · ${gCoins.filter((c) => !c.col).length} coins · LEVEL ${gLevel}`,
				GW / 2,
				GH - 10
			);
			if (gShot > 0) {
				GX.fillStyle = '#4a3870';
				GX.textAlign = 'left';
				GX.fillText('reloading...', 16, GH - 12);
			}
		}

		function drawOverlay(title, sub, hint, col) {
			GX.fillStyle = 'rgba(0,0,0,.82)';
			GX.fillRect(0, 0, GW, GH);
			GX.font = 'bold 46px Syne,sans-serif';
			GX.fillStyle = col;
			GX.textAlign = 'center';
			GX.fillText(title, GW / 2, GH / 2 - 60);
			GX.font = '22px IBM Plex Mono';
			GX.fillStyle = '#fbbf24';
			GX.fillText(sub, GW / 2, GH / 2 - 12);
			const t = performance.now() / 1000,
				pu = 0.5 + 0.5 * Math.sin(t * 3);
			GX.font = '14px IBM Plex Mono';
			GX.fillStyle = `rgba(224,121,249,${pu})`;
			GX.fillText(hint, GW / 2, GH / 2 + 36);
			GX.font = '12px IBM Plex Mono';
			GX.fillStyle = '#4a3870';
			GX.fillText(`HI-SCORE: ${gHiScore.toString().padStart(6, '0')}`, GW / 2, GH / 2 + 70);
		}

		function gameLoop() {
			const now = performance.now(),
				dt = Math.min((now - gLastT) / 1000, 0.05);
			gLastT = now;
			if (gState === 'playing') {
				updateShake(dt);
				updatePlayer(dt);
				updateEnemies(dt);
				updateBullets(dt);
				updateCoins(dt);
				checkWin();
				if (gPressed.has('Escape') || gPressed.has('p') || gPressed.has('P')) gState = 'paused';
				if (gPressed.has('r') || gPressed.has('R')) startGame();
			} else if (gState === 'paused') {
				if (gPressed.has('Escape')) gState = 'playing';
			} else if (gState === 'gameover' || gState === 'victory') {
				if (gPressed.has('r') || gPressed.has('R')) startGame();
			}
			gPressed.clear();
			GX.clearRect(0, 0, GW, GH);
			GX.fillStyle = '#04020c';
			GX.fillRect(0, 0, GW, GH);
			GX.fillStyle = '#6050a018';
			for (let i = 0; i < 40; i++) GX.fillRect((i * 137) % GW, (i * 197) % GH, 1, 1);
			if (gState === 'title') {
				const t = performance.now() / 1000,
					pu = 0.5 + 0.5 * Math.sin(t * 3);
				GX.font = 'bold 50px Syne,sans-serif';
				GX.fillStyle = '#e879f9';
				GX.textAlign = 'center';
				GX.fillText('ASTRAL DASH', GW / 2, GH / 2 - 70);
				GX.font = '15px IBM Plex Mono';
				GX.fillStyle = `rgba(224,121,249,${pu})`;
				GX.fillText('CLICK TO START', GW / 2, GH / 2 + 10);
				GX.font = '12px IBM Plex Mono';
				GX.fillStyle = '#4a3870';
				GX.fillText(
					'WASD / Arrows = move   Space / W / ↑ = jump   Mouse = aim   Click = shoot',
					GW / 2,
					GH / 2 + 44
				);
				GX.fillText(
					'Defeat all enemies to win each level   Collect ★ coins for bonus points',
					GW / 2,
					GH / 2 + 64
				);
				GX.fillText(`HI-SCORE: ${gHiScore.toString().padStart(6, '0')}`, GW / 2, GH / 2 + 90);
			} else if (gState === 'playing' || gState === 'paused') {
				drawWorld();
				drawHUD();
				if (gState === 'paused') {
					GX.fillStyle = 'rgba(0,0,0,.6)';
					GX.fillRect(0, 0, GW, GH);
					GX.font = 'bold 36px Syne,sans-serif';
					GX.fillStyle = '#e879f9';
					GX.textAlign = 'center';
					GX.fillText('PAUSED', GW / 2, GH / 2 - 16);
					GX.font = '14px IBM Plex Mono';
					GX.fillStyle = '#6050a0';
					GX.fillText('ESC to resume', GW / 2, GH / 2 + 20);
				}
			} else if (gState === 'gameover') {
				drawOverlay(
					'GAME OVER',
					`SCORE: ${gScore.toString().padStart(6, '0')}`,
					gScore >= gHiScore && gScore > 0
						? '✦ NEW HIGH SCORE — CLICK TO RESTART ✦'
						: 'CLICK TO RESTART',
					'#f87171'
				);
			} else if (gState === 'victory') {
				if (!gParticles) gParticles = [];
				if (Math.random() < 0.3)
					gParticles.push({
						x: Math.random() * GW,
						y: Math.random() * GH,
						vx: rnd(-80, 80),
						vy: rnd(-120, 0),
						r: rnd(2, 5),
						life: 0.8,
						ml: 0.8,
						col: ['#e879f9', '#fbbf24', '#34d399', '#60a5fa'][Math.floor(Math.random() * 4)]
					});
				GX.clearRect(0, 0, GW, GH);
				GX.fillStyle = '#04020c';
				GX.fillRect(0, 0, GW, GH);
				gParticles = gParticles.filter((p) => {
					p.x += p.vx * 0.016;
					p.y += p.vy * 0.016;
					p.vy += 200 * 0.016;
					p.life -= 0.016;
					if (p.life <= 0) return false;
					GX.globalAlpha = p.life / p.ml;
					GX.beginPath();
					GX.arc(p.x, p.y, p.r, 0, Math.PI * 2);
					GX.fillStyle = p.col;
					GX.fill();
					GX.globalAlpha = 1;
					return true;
				});
				drawOverlay(
					'VICTORY!',
					`FINAL SCORE: ${gScore.toString().padStart(6, '0')} (Level ${gLevel})`,
					gScore >= gHiScore ? '✦ HIGH SCORE ✦  Click to play again' : 'Click to play again',
					'#60a5fa'
				);
			}
			requestAnimationFrame(gameLoop);
		}
		if (!gParticles) gParticles = [];
		gameLoop();

		/* ═══════════════════ POLISH CHECKLIST ═══════════════════ */
		const PLIST = [
			'All FSM transitions work without crashes or missing resources',
			'Win and lose conditions are clearly communicated',
			'High score is saved across sessions (localStorage or file)',
			'Screen shake on heavy impacts',
			'Particles on death, collect, and jump landing',
			'Player flashes during invincibility after damage',
			'Coyote time and jump buffering implemented',
			'HUD text readable on all backgrounds',
			'Stable FPS with 20+ entities on screen',
			'Sound effects: jump, shoot, hit, collect, death',
			'Music loops without click/pop artifact',
			'Controls shown on title screen',
			'Game window has custom title and icon',
			'Distributable package tested on clean machine',
			'At least one playtester session completed'
		];
		const pDone = new Set();
		function buildPolish() {
			document.getElementById('polish-list').innerHTML = PLIST.map(
				(t, i) =>
					`<div class="polish-item"><div class="polish-check ${pDone.has(i) ? 'done' : ''}" onclick="toggleP(${i})">${pDone.has(i) ? '✓' : ''}</div><div class="polish-label ${pDone.has(i) ? 'done' : ''}">${t}</div></div>`
			).join('');
			document.getElementById('polish-progress').textContent =
				`${pDone.size}/${PLIST.length} complete${pDone.size === PLIST.length ? ' — ship it! 🚀' : ''}`;
		}
		function toggleP(i) {
			if (pDone.has(i)) pDone.delete(i);
			else pDone.add(i);
			buildPolish();
		}
		buildPolish();

		/* ═══════════════════ QUIZ ═══════════════════ */
		const quizData = [
			{
				q: 'A game FSM transitions from GAMEPLAY to GAMEOVER mid-update when lives reach 0. What breaks?',
				options: [
					'Nothing — FSM transitions are always safe',
					'Systems that run later in the same frame (renderer, camera) still reference a now-destroyed player entity, causing null errors',
					"The screen flickers because the GPU hasn't finished the last frame",
					'The transition fires twice if update is called again'
				],
				correct: 1,
				explanation:
					'Transitioning mid-frame tears down the world while the render system and camera still hold entity references. The fix: set a pending flag and apply the transition at end-of-frame after all systems have completed reading from the world.'
			},
			{
				q: 'What is coyote time, and what problem does it solve?',
				options: [
					'A brief mid-air direction change window to improve aerial maneuverability',
					'A short grace window (~80ms) after walking off a ledge during which jumping is still allowed — preventing the frustration of pressing jump one frame too late',
					'An invincibility window after respawning to prevent immediate re-death',
					'Automatic slowdown when near a ledge to warn the player'
				],
				correct: 1,
				explanation:
					'Coyote time grants a small time window after the player leaves a platform during which a jump is still registered. Without it, players who press jump fractionally late after walking off a ledge get no jump — feeling unfair. With it, timing feels responsive.'
			},
			{
				q: 'Screen shake uses trauma². A hit adds 0.4 trauma. What is the displacement intensity, and why square it?',
				options: [
					'Intensity = 0.4 — linear trauma gives proportional shake',
					'Intensity = 0.16 — squaring means small trauma values have barely visible effect; large values shake violently. This creates a sharper, more physical falloff',
					'Intensity = 0.2 — squaring halves the trauma value',
					'Intensity = 0.64 — squaring amplifies the effect'
				],
				correct: 1,
				explanation:
					'trauma = 0.4, so intensity = 0.4² = 0.16. The square makes the relationship non-linear: a trauma of 0.2 gives only 4% of maximum displacement (barely visible), while 0.9 gives 81% (very dramatic). This matches physical intuition where small events cause negligible shake and major events cause strong shake.'
			},
			{
				q: 'A combo system gives multiplier = 1 + (combo−1) × 0.5. On a 4-kill streak the player kills another enemy (base 20 pts). What score is awarded?',
				options: ['20 points', '40 points', '60 points', '50 points'],
				correct: 2,
				explanation:
					'combo becomes 5. multiplier = 1 + (5−1)×0.5 = 1 + 2 = 3. score = floor(20 × 3) = 60 points. A 5-kill streak gives 3× the base value. Resetting to combo=0 on any hit makes this risk-reward meaningful — aggressive play is rewarded but punished if careless.'
			},
			{
				q: 'HUD elements (score, health bar) must render on top of all 3D/2D world geometry. What is the correct technique?',
				options: [
					'Render the HUD first at z=0, before all game objects',
					'Render the HUD in a separate pass after the world, with depth testing disabled and an orthographic screen-space projection',
					'Draw HUD at world-space z=9999 so it is always in front',
					'Use alpha blending on the HUD layer to composite it on top'
				],
				correct: 1,
				explanation:
					'HUD elements have fixed screen positions unrelated to world geometry. A separate orthographic render pass (after the world pass) with depth testing disabled guarantees HUD always appears on top — regardless of what world geometry happens to occupy the same screen coordinates. Drawing HUD first would let world objects occlude it; using z=9999 breaks for cameras with finite far planes and requires all world objects to have z<9999.'
			}
		];
		let answered = 0,
			correct = 0;
		function buildQuiz() {
			const c = document.getElementById('quiz-container');
			c.innerHTML = '';
			quizData.forEach((q, qi) => {
				const div = document.createElement('div');
				div.className = 'question';
				div.innerHTML = `<div class="q-text"><span class="q-num">${qi + 1}.</span>${q.q}</div><div class="options" id="opts-${qi}">${q.options.map((o, oi) => `<div class="option" onclick="answer(${qi},${oi})" id="opt-${qi}-${oi}">${o}</div>`).join('')}</div><div class="feedback" id="fb-${qi}"></div>`;
				c.appendChild(div);
			});
		}
		function answer(qi, oi) {
			const q = quizData[qi];
			document.querySelectorAll(`#opts-${qi} .option`).forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById(`fb-${qi}`);
			if (oi === q.correct) {
				document.getElementById(`opt-${qi}-${oi}`).classList.add('correct');
				fb.textContent = '✓ ' + q.explanation;
				fb.className = 'feedback ok';
				correct++;
			} else {
				document.getElementById(`opt-${qi}-${oi}`).classList.add('wrong');
				document.getElementById(`opt-${qi}-${q.correct}`).classList.add('correct');
				fb.textContent = '✗ ' + q.explanation;
				fb.className = 'feedback bad';
			}
			answered++;
			if (answered === quizData.length) {
				const s = document.getElementById('quiz-score');
				s.style.display = 'block';
				document.getElementById('score-num').textContent = `${correct}/${quizData.length}`;
				s.style.borderColor =
					correct === quizData.length
						? 'var(--accent3)'
						: correct >= 3
							? 'var(--accent2)'
							: 'var(--accent)';
			}
		}
		buildQuiz();
		_addWinListener('scroll', () => {
			const _rp = document.getElementById('reading-progress');
			if (_rp) {
				_rp.style.width =
					Math.min(
						100,
						(window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
					) + '%';
				_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));
			}
		});

		if (typeof drawFSM === 'function') actions.drawFSM = drawFSM;
		if (typeof scoreKill === 'function') actions.scoreKill = scoreKill;
		if (typeof scoreCoin === 'function') actions.scoreCoin = scoreCoin;
		if (typeof scoreHit === 'function') actions.scoreHit = scoreHit;
		if (typeof scoreLevelClear === 'function') actions.scoreLevelClear = scoreLevelClear;
		if (typeof scoreReset === 'function') actions.scoreReset = scoreReset;
		if (typeof updateScUI === 'function') actions.updateScUI = updateScUI;
		if (typeof drawScore === 'function') actions.drawScore = drawScore;
		if (typeof buildJuiceToggles === 'function') actions.buildJuiceToggles = buildJuiceToggles;
		if (typeof toggleJ === 'function') actions.toggleJ = toggleJ;
		if (typeof drawJuice === 'function') actions.drawJuice = drawJuice;
		if (typeof rnd === 'function') actions.rnd = rnd;
		if (typeof clamp === 'function') actions.clamp = clamp;
		if (typeof aabb === 'function') actions.aabb = aabb;
		if (typeof makePlats === 'function') actions.makePlats = makePlats;
		if (typeof makeEnemies === 'function') actions.makeEnemies = makeEnemies;
		if (typeof makeCoins === 'function') actions.makeCoins = makeCoins;
		if (typeof spawnParts === 'function') actions.spawnParts = spawnParts;
		if (typeof addFloat === 'function') actions.addFloat = addFloat;
		if (typeof shake === 'function') actions.shake = shake;
		if (typeof buildLevel === 'function') actions.buildLevel = buildLevel;
		if (typeof startGame === 'function') actions.startGame = startGame;
		if (typeof pDie === 'function') actions.pDie = pDie;
		if (typeof pHit === 'function') actions.pHit = pHit;
		if (typeof updatePlayer === 'function') actions.updatePlayer = updatePlayer;
		if (typeof updateEnemies === 'function') actions.updateEnemies = updateEnemies;
		if (typeof updateBullets === 'function') actions.updateBullets = updateBullets;
		if (typeof updateCoins === 'function') actions.updateCoins = updateCoins;
		if (typeof updateShake === 'function') actions.updateShake = updateShake;
		if (typeof checkWin === 'function') actions.checkWin = checkWin;
		if (typeof drawWorld === 'function') actions.drawWorld = drawWorld;
		if (typeof drawHUD === 'function') actions.drawHUD = drawHUD;
		if (typeof drawOverlay === 'function') actions.drawOverlay = drawOverlay;
		if (typeof gameLoop === 'function') actions.gameLoop = gameLoop;
		if (typeof buildPolish === 'function') actions.buildPolish = buildPolish;
		if (typeof toggleP === 'function') actions.toggleP = toggleP;
		if (typeof buildQuiz === 'function') actions.buildQuiz = buildQuiz;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			_listeners.forEach((l) => l.target.removeEventListener(...l.args));
		};
	});
</script>

<div class="page-wrapper">
	<header class="course-header">
		<div>
			<div class="course-label">Game Development Fundamentals</div>
			<div class="course-title">From Pixels to Play</div>
		</div>
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 11 of 12</div>
	</header>
	<div class="module-hero">
		<div class="module-number">11</div>
		<div class="module-tag">Module 11 · Capstone</div>
		<h1 class="module-title">Building a<br /><span>Complete 2D Game</span></h1>
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
			<li><a href="#fsm">State Machines</a></li>
			<li><a href="#progression">Progression &amp; Scoring</a></li>
			<li><a href="#hud">HUD &amp; UI</a></li>
			<li><a href="#polish">Polish &amp; Juice</a></li>
			<li><a href="#game">The Complete Game</a></li>
			<li><a href="#packaging">Packaging</a></li>
			<li><a href="#quiz">Quiz</a></li>
		</ul>
	</nav>
	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Design and implement a game FSM (menu → gameplay → game-over)</li>
			<li>Build a scoring system with combo multipliers and high-score persistence</li>
			<li>Render a HUD in screen space independent of the game world</li>
			<li>Apply screen shake, particles, hit-flash, and coyote time</li>
			<li>Integrate all prior modules into a fully playable 2D game</li>
		</ul>
	</section>

	<!-- 11.01 FSM -->
	<section id="fsm" class="section">
		<div class="section-header">
			<span class="section-num">11.01</span>
			<h2 class="section-title">Game State Machines</h2>
		</div>
		<p>
			Every game alternates between distinct modes: the title screen, the gameplay loop, a pause
			overlay, a game-over screen. A <strong>finite state machine (FSM)</strong> makes these
			transitions explicit and safe. Each state implements three hooks: <code>on_enter</code>,
			<code>update</code>, and <code>on_exit</code>. The machine routes calls to the current state
			only, and applies pending transitions at the end of each frame to avoid mid-frame teardown.
		</p>
		<pre><code
				><span class="kw">class</span> <span class="fn">GameFSM</span>:
    <span class="kw">def</span> <span class="fn">__init__</span
				>(self): self._states=&#123;&#125;; self._current=<span class="kw">None</span
				>; self._pending=<span class="kw">None</span>

    <span class="kw">def</span> <span class="fn">transition</span
				>(self, name, **kw): self._pending=(name,kw)  <span class="cm"># deferred!</span>

    <span class="kw">def</span> <span class="fn">end_frame</span>(self):
        <span class="kw">if not</span> self._pending: <span class="kw">return</span>
        name,kw=self._pending; self._pending=<span class="kw">None</span>
        <span class="kw">if</span> self._current: self._current.<span class="fn">on_exit</span>()
        self._current=self._states[name]; self._current.<span class="fn">on_enter</span>(**kw)

<span class="kw">class</span> <span class="fn">GameplayState</span>:
    <span class="kw">def</span> <span class="fn">on_enter</span>(self, level=<span class="num"
					>1</span
				>, score=<span class="num">0</span>, lives=<span class="num">3</span>):
        self.world=<span class="fn">build_level</span>(level); self.score,self.lives=score,lives
    <span class="kw">def</span> <span class="fn">update</span>(self, dt, inp):
        <span class="fn">run_systems</span>(self.world, dt, inp)
        <span class="kw">if</span> self.lives&lt;=<span class="num">0</span>: fsm.<span class="fn"
					>transition</span
				>(<span class="str">'gameover'</span>, score=self.score)
        <span class="kw">if</span> self.world.cleared: fsm.<span class="fn">transition</span>(<span
					class="str">'victory'</span
				>, score=self.score)<span class="lang-tag">python</span></code
			></pre>
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Game State Machine</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Click any state to trigger a transition and see its lifecycle hooks.
				</p>
				<canvas
					id="fsm-canvas"
					width="860"
					height="260"
					style="width: 100%; background: var(--code-bg)"
					aria-label="Fsm Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>
				<div
					id="fsm-detail"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								background: var(--code-bg);
								border: 1px solid var(--border);
								font-size: 12px;
								min-height: 52px;
								color: var(--muted);
							"
				>
					Click a state node to see its on_enter / update / on_exit hooks and valid transitions.
				</div>
			</div>
		</div>
		<div class="callout blue">
			<div class="callout-label">Deferred Transitions</div>
			Always queue transitions and apply them at end-of-frame. Transitioning mid-update tears down the
			current world while systems still hold references — a certain crash. The pending flag costs one
			frame of latency that is invisible to players.
		</div>
	</section>

	<!-- 11.02 PROGRESSION -->
	<section id="progression" class="section">
		<div class="section-header">
			<span class="section-num">11.02</span>
			<h2 class="section-title">Progression, Scoring, and Combo Systems</h2>
		</div>
		<p>
			A <strong>combo multiplier</strong> rewards skilled, uninterrupted play. The formula
			<code>multiplier = 1 + (combo - 1) × 0.5</code> gives 1× on the first kill, 1.5× on the second,
			2× on the third, and so on. Any damage taken resets the combo — creating meaningful risk.
		</p>
		<pre><code
				><span class="kw">def</span> <span class="fn">on_enemy_killed</span>(self, base_pts=<span
					class="num">20</span
				>):
    self.combo += <span class="num">1</span>
    mult = <span class="num">1</span> + (self.combo - <span class="num">1</span>) * <span
					class="num">0.5</span
				>
    pts  = <span class="fn">int</span>(base_pts * mult)
    self.score += pts
    <span class="kw">return</span> pts, mult   <span class="cm"># caller shows floating text</span>

<span class="kw">def</span> <span class="fn">on_player_hit</span>(self):
    self.combo = <span class="num">0</span>    <span class="cm"># streak reset</span>
    self.lives -= <span class="num">1</span>
    <span class="kw">if</span> self.score > self.high_score: <span class="fn">save_high_score</span
				>(self.score)<span class="lang-tag">python</span></code
			></pre>
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Combo Scoring</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button class="btn gold" onclick={(e) => actions.scoreKill()}>⚔ Kill Enemy</button>
					<button class="btn" onclick={(e) => actions.scoreCoin()}>★ Collect Coin</button>
					<button class="btn active" onclick={(e) => actions.scoreHit()}>💥 Take Hit</button>
					<button class="btn g" onclick={(e) => actions.scoreLevelClear()}>✓ Level Clear</button>
					<button class="btn" onclick={(e) => actions.scoreReset()}>↺ Reset</button>
				</div>
				<canvas
					id="score-canvas"
					width="860"
					height="140"
					style="width: 100%"
					aria-label="Score Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>
				<div class="two-col" style="margin-top: 0.75rem">
					<div class="info-panel">
						<div class="info-row">
							<span class="info-key">score</span><span class="info-val" id="sc-score">0</span>
						</div>
						<div class="info-row">
							<span class="info-key">high score</span><span class="info-val" id="sc-hi">0</span>
						</div>
						<div class="info-row">
							<span class="info-key">combo</span><span class="info-val" id="sc-combo">0</span>
						</div>
						<div class="info-row">
							<span class="info-key">multiplier</span><span class="info-val" id="sc-mult">1.0×</span
							>
						</div>
						<div class="info-row">
							<span class="info-key">lives</span><span class="info-val" id="sc-lives">3</span>
						</div>
					</div>
					<div
						id="sc-log"
						style="
									background: var(--code-bg);
									border: 1px solid var(--border);
									padding: 0.5rem;
									height: 120px;
									overflow-y: auto;
									font-size: 11px;
								"
					></div>
				</div>
			</div>
		</div>
	</section>

	<!-- 11.03 HUD -->
	<section id="hud" class="section">
		<div class="section-header">
			<span class="section-num">11.03</span>
			<h2 class="section-title">HUD and UI Overlays</h2>
		</div>
		<p>
			The HUD renders in screen space — always on top, always at fixed pixel coordinates — using an
			orthographic projection after the main world render pass. Depth testing is disabled for the
			HUD pass so nothing in the game world can obscure a health bar or score display.
		</p>
		<pre><code
				><span class="kw">def</span> <span class="fn">render_hud</span>(ctx, state):
    ctx.<span class="fn">disable</span>(moderngl.DEPTH_TEST)    <span class="cm"
					># always on top</span
				>
    <span class="fn">draw_rect</span>(<span class="num">16</span>,<span class="num">16</span>,<span
					class="num">140</span
				>,<span class="num">12</span>, color=(<span class="num">.15</span>,<span class="num"
					>.05</span
				>,<span class="num">.05</span>))            <span class="cm"># HP background</span>
    <span class="fn">draw_rect</span>(<span class="num">16</span>,<span class="num">16</span>,<span
					class="num">140</span
				>*(state.hp/state.max_hp),<span class="num">12</span>, color=(<span class="num">.9</span
				>,<span class="num">.2</span>,<span class="num">.2</span>))  <span class="cm"
					># HP fill</span
				>
    <span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span
				>(state.lives): <span class="fn">draw_icon</span>(<span class="str">'heart'</span>, <span
					class="num">16</span
				>+i*<span class="num">20</span>, <span class="num">36</span>)
    <span class="fn">draw_text</span>(<span class="fn">f</span><span class="str"
					>'&#123;state.score:06d&#125;'</span
				>, W-<span class="num">16</span>, <span class="num">16</span>, align=<span class="str"
					>'right'</span
				>)
    ctx.<span class="fn">enable</span>(moderngl.DEPTH_TEST)<span class="lang-tag">python</span
				></code
			></pre>
		<div class="callout green">
			<div class="callout-label">Draw Order</div>
			Sort all draw calls by layer: background (0) → game world (1) → particles/effects (2) → HUD (3).
			Issue draw calls in ascending layer order. GPU draw order is not guaranteed without explicit sorting
			or depth values.
		</div>
	</section>

	<!-- 11.04 POLISH -->
	<section id="polish" class="section">
		<div class="section-header">
			<span class="section-num">11.04</span>
			<h2 class="section-title">Polish and Juice</h2>
		</div>
		<p>
			<strong>Juice</strong> is the collection of small effects — screen shake, particles, squash/stretch,
			combo text, hit-flash — that make a game feel responsive. None of these change the rules, but they
			communicate events viscerally. The perceived quality gap between a prototype and a finished game
			is mostly juice.
		</p>
		<table>
			<thead>
				<tr>
					<th>Effect</th>
					<th>Trigger</th>
					<th>Implementation</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Screen shake</td>
					<td>Explosion, heavy hit</td>
					<td>Offset camera by decaying random vector; use trauma²</td>
				</tr>
				<tr>
					<td>Hit flash</td>
					<td>Damage taken</td>
					<td>Render sprite white for 2–4 frames</td>
				</tr>
				<tr>
					<td>Particles</td>
					<td>Kill, collect, jump dust</td>
					<td>N velocity-diverging sprites with gravity and fade</td>
				</tr>
				<tr>
					<td>Squash/stretch</td>
					<td>Jump, land</td>
					<td>Scale transform: stretch up on jump, squash on land</td>
				</tr>
				<tr>
					<td>Coyote time</td>
					<td>Walk off ledge</td>
					<td>Allow jump ~80ms after leaving ground</td>
				</tr>
				<tr>
					<td>Jump buffer</td>
					<td>Press jump before landing</td>
					<td>Queue input for ~100ms; fire on next ground contact</td>
				</tr>
				<tr>
					<td>Floating text</td>
					<td>Score event</td>
					<td>Text rises with ease-out, alpha fades over 1.5s</td>
				</tr>
			</tbody>
		</table>
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Juice Effects</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Toggle effects on/off. Click canvas to trigger. Feel the difference.
				</p>
				<div
					style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem"
					id="juice-toggles"
				></div>
				<canvas
					id="juice-canvas"
					width="860"
					height="200"
					style="width: 100%"
					aria-label="Juice Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- 11.05 THE GAME -->
	<section id="game" class="section">
		<div class="section-header">
			<span class="section-num">11.05</span>
			<h2 class="section-title">The Complete Game — ASTRAL DASH</h2>
		</div>
		<p>
			Every module from 1–10 converges here. ASTRAL DASH is a 2D platformer-shooter with: a
			four-state FSM, delta-time movement, AABB platform collision, enemy patrol AI, a combo scoring
			system with floating text, a full HUD, screen shake, particles, hit-flash, squash/stretch,
			coyote time, and a win condition that advances levels.
		</p>
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">★ ASTRAL DASH — Fully Playable</div>
				<span class="demo-badge g">PLAYABLE</span>
			</div>
			<div class="demo-body" style="padding: 1rem">
				<canvas
					id="game-canvas"
					width="860"
					height="480"
					style="width: 100%"
					aria-label="Game Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>
				<div
					id="game-hint"
					style="font-size: 11px; color: var(--muted); margin-top: 0.5rem; text-align: center"
				>
					Click canvas to start · WASD/Arrows = move · Space/W/↑ = jump (hold for height) · Mouse =
					aim · Click = shoot · R = restart · ESC = pause
				</div>
				<div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.75rem">
					<div class="slider-row" style="flex: 1; min-width: 160px">
						<label for="dummy">Gravity</label><input
							type="range"
							id="gm-gravity"
							min="200"
							max="1200"
							value="600"
						/><span class="slider-val" id="gm-gravity-val">600</span>
					</div>
					<div class="slider-row" style="flex: 1; min-width: 160px">
						<label for="dummy">Juice level</label><input
							type="range"
							id="gm-juice"
							min="0"
							max="100"
							value="80"
						/><span class="slider-val" id="gm-juice-val">80%</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- 11.06 PACKAGING -->
	<section id="packaging" class="section">
		<div class="section-header">
			<span class="section-num">11.06</span>
			<h2 class="section-title">Packaging for Distribution</h2>
		</div>
		<p>
			Use <strong>PyInstaller</strong> to bundle the game into a standalone folder. Players need no Python
			installation.
		</p>
		<pre><code
				><span class="cm"># Build</span>
pip install pyinstaller
pyinstaller --noconfirm --onedir main.py \
    --add-data <span class="str">"assets:assets"</span> \
    --name <span class="str">"AstralDash"</span>

<span class="cm"># main.py — locate assets whether bundled or not</span>
<span class="kw">import</span> sys, os
BASE = sys._MEIPASS <span class="kw">if</span> <span class="fn">getattr</span>(sys,<span class="str"
					>'frozen'</span
				>,<span class="kw">False</span>) <span class="kw">else</span> os.path.<span class="fn"
					>dirname</span
				>(__file__)
ASSETS = os.path.<span class="fn">join</span>(BASE, <span class="str">'assets'</span>)<span
					class="lang-tag">shell + python</span
				></code
			></pre>
		<table>
			<thead>
				<tr>
					<th>Platform</th>
					<th>Tool</th>
					<th>Notes</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Windows</td>
					<td>PyInstaller (on Windows)</td>
					<td>Produces .exe — must build on target OS</td>
				</tr>
				<tr>
					<td>macOS</td>
					<td>PyInstaller (on Mac)</td>
					<td>Produces .app — sign for Gatekeeper</td>
				</tr>
				<tr>
					<td>Linux</td>
					<td>PyInstaller (on Linux)</td>
					<td>ELF binary — test on target distro</td>
				</tr>
				<tr>
					<td>Web</td>
					<td>Pygbag (experimental)</td>
					<td>Transpiles pygame to WebAssembly</td>
				</tr>
				<tr>
					<td>Itch.io</td>
					<td>Zip dist/ folder</td>
					<td>Free game hosting, widely used for indie games</td>
				</tr>
			</tbody>
		</table>
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Pre-Ship Checklist</div>
				<span class="demo-badge a">CHECKLIST</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Work through this before distributing. Click each item to mark done.
				</p>
				<div id="polish-list"></div>
				<div
					style="margin-top: 1rem; font-size: 12px; color: var(--muted)"
					id="polish-progress"
				></div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module Quiz</div>
		<div class="quiz-sub">5 questions · State machines, scoring, and polish</div>
		<div id="quiz-container"></div>
		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-num">0/5</div>
			<div style="font-size: 12px; color: var(--muted); margin-top: 0.25rem">
				Module 11 complete. One module remains.
			</div>
		</div>
	</section>

	<div class="nav-links">
		<a href="." class="prev-link">← 10 · Engine Architecture</a>
		<a class="next-module" href=".">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">12 · Introduction to 3D Concepts</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</div>
</div>

<!-- /page-wrapper -->

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
		max-width: 640px;
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
	:global(pre) {
		background: var(--code-bg);
		border: 1px solid var(--border);
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
		color: var(--muted);
		letter-spacing: 0.1em;
	}
	:global(.kw) {
		color: #c084fc;
	}
	:global(.fn) {
		color: #67e8f9;
	}
	:global(.str) {
		color: #fde68a;
	}
	:global(.cm) {
		color: #2d235a;
	}
	:global(.num) {
		color: #f9a8d4;
	}
	.ty {
		color: var(--accentL);
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
	:global(.callout.gold) {
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 5%, var(--surface));
	}
	:global(.callout.green) {
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 5%, var(--surface));
	}
	:global(.callout.blue) {
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
	:global(.callout.gold) .callout-label {
		color: var(--accent2);
	}
	:global(.callout.green) .callout-label {
		color: var(--accent3);
	}
	:global(.callout.blue) .callout-label {
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
	:global(.demo-badge) {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	:global(.demo-badge.i) {
		color: var(--accent);
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 10%, transparent);
	}
	:global(.demo-badge.g) {
		color: var(--accent3);
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
	}
	:global(.demo-badge.a) {
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
	:global(.slider-row) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0.5rem 0;
	}
	:global(.slider-row) label {
		font-size: 11px;
		min-width: 110px;
		color: var(--muted);
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
		background: var(--accent);
		cursor: pointer;
	}
	:global(.slider-val) {
		font-size: 12px;
		color: var(--accent);
		min-width: 44px;
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
	:global(.btn.g:hover),
	:global(.btn.g.active) {
		border-color: var(--accent3);
		color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
	}
	.btn.gold:hover,
	:global(.btn.gold.active) {
		border-color: var(--accent2);
		color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 10%, transparent);
	}
	:global(.info-panel) {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 0.85rem 1rem;
		font-size: 12px;
	}
	:global(.info-row) {
		display: flex;
		justify-content: space-between;
		padding: 0.2rem 0;
		border-bottom: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
	}
	.info-row:last-child {
		border-bottom: none;
	}
	:global(.info-key) {
		color: var(--muted);
	}
	:global(.info-val) {
		color: var(--accent3);
		font-weight: 600;
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
	:global(.polish-item) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.4rem 0;
		border-bottom: 1px solid color-mix(in srgb, var(--border) 50%, transparent);
	}
	:global(.polish-item:last-child) {
		border-bottom: none;
	}
	:global(.polish-check) {
		width: 16px;
		height: 16px;
		border: 1px solid var(--border2);
		border-radius: 2px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 10px;
		flex-shrink: 0;
		transition: all 0.12s;
	}
	:global(.polish-check.done) {
		background: var(--accent3);
		border-color: var(--accent3);
		color: #000;
	}
	:global(.polish-label) {
		font-size: 12px;
	}
	:global(.polish-label.done) {
		color: var(--muted);
		text-decoration: line-through;
	}
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
		margin-bottom: 0.25rem;
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
		color: var(--accent2);
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
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
		color: var(--accent3);
	}
	:global(.option.wrong) {
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 10%, transparent);
		color: var(--accent);
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
		color: var(--accent3);
	}
	:global(.feedback.bad) {
		color: var(--accent);
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
		color: var(--accent);
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
	:global(.prev-link) {
		font-size: 12px;
		color: var(--muted);
		text-decoration: none;
		border: 1px solid var(--border);
		padding: 0.75rem 1.25rem;
		transition: all 0.2s;
	}
	:global(.prev-link:hover) {
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
	#game-canvas {
		border: 2px solid var(--border2);
		background: #04020c;
		cursor: none;
		touch-action: none;
		display: block;
	}
	#juice-canvas {
		border: 1px solid var(--border2);
		background: #04020c;
		cursor: pointer;
	}
	#score-canvas {
		border: 1px solid var(--border2);
	}
	#fsm-canvas {
		border: 1px solid var(--border2);
		cursor: pointer;
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
