<script>
	/* eslint-disable @typescript-eslint/no-unused-vars, svelte/prefer-svelte-reactivity, no-useless-assignment, no-useless-escape */
	import { onMount } from 'svelte';

	onMount(() => {
		/* ════════════════════════════════════════════════════
   GLOBAL INPUT STATE (shared across demos)
════════════════════════════════════════════════════ */
		const heldKeys = new Set();
		const justPressed = new Set();
		const justReleased = new Set();
		let mousePos = { x: 0, y: 0 };
		let mouseDelta = { x: 0, y: 0 };
		let mouseRawDelta = { x: 0, y: 0 };
		let scrollDelta = { x: 0, y: 0 };
		const mouseButtons = new Set();
		const mousePressedThisFrame = new Set();
		const mouseReleasedThisFrame = new Set();
		let pressHistory = []; // for last-key-wins policy

		// Capture all keyboard events from the document
		document.addEventListener('keydown', (e) => {
			if (e.repeat) return;
			const k = e.key;
			justPressed.add(k);
			heldKeys.add(k);
			pressHistory.push(k);
			if (pressHistory.length > 10) pressHistory.shift();
			logEvent('press', `keydown: ${k}`);
			updateStateTable();
			updateKbVis();
			updateInputMap();
			// Don't prevent default for F-keys etc, but prevent scrolling
			if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(k)) e.preventDefault();
		});
		document.addEventListener('keyup', (e) => {
			const k = e.key;
			heldKeys.delete(k);
			justReleased.add(k);
			logEvent('release', `keyup: ${k}`);
			updateStateTable();
			updateKbVis();
		});

		// Clear per-frame sets periodically (simulate frame boundary)
		setInterval(() => {
			justPressed.clear();
			justReleased.clear();
			mousePressedThisFrame.clear();
			mouseReleasedThisFrame.clear();
			mouseRawDelta = { x: 0, y: 0 };
			updateKbVis();
			updateStateTable();
			updateInputMap();
		}, 100); // ~10 frame-ticks per second for vis purposes

		/* ════════════════════════════════════════════════════
   EVENT LOG
════════════════════════════════════════════════════ */
		const MAX_LOG = 40;
		let logLines = [];
		function logEvent(type, msg) {
			logLines.push({ type, msg, t: performance.now() });
			if (logLines.length > MAX_LOG) logLines.shift();
			renderEventLog('event-log-a');
		}
		function renderEventLog(id) {
			const el = document.getElementById(id);
			if (!el) return;
			el.innerHTML = logLines
				.slice(-20)
				.reverse()
				.map(
					(l) =>
						`<div class="event-line ${l.type}">[${((l.t / 1000) % 100).toFixed(2)}] ${l.msg}</div>`
				)
				.join('');
		}

		/* ════════════════════════════════════════════════════
   STATE TABLE
════════════════════════════════════════════════════ */
		function updateStateTable() {
			const fmt = (s) => (s.size ? '{' + [...s].join(', ') + '}' : '{}');
			document.getElementById('st-held').textContent = fmt(heldKeys);
			document.getElementById('st-pressed').textContent = fmt(justPressed);
			document.getElementById('st-released').textContent = fmt(justReleased);
			document.getElementById('st-mouse').textContent = `(${mousePos.x}, ${mousePos.y})`;
			document.getElementById('st-mbuttons').textContent = mouseButtons.size
				? '{' + [...mouseButtons].map((b) => ['left', 'mid', 'right'][b]).join(', ') + '}'
				: '{}';
			document.getElementById('st-scroll').textContent =
				`(${scrollDelta.x.toFixed(0)}, ${scrollDelta.y.toFixed(0)})`;
		}

		/* ════════════════════════════════════════════════════
   KEYBOARD VISUALIZER
════════════════════════════════════════════════════ */
		const KB_LAYOUT = [
			['Escape', 'F1', 'F2', 'F3', 'F4'],
			['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
			['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
			['CapsLock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
			['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
			['Control', 'Alt', ' ', 'Alt', 'Control']
		];
		const KB_KEY_MAP = {
			Escape: 'Escape',
			' ': ' ',
			Enter: 'Enter',
			Backspace: 'Backspace',
			Tab: 'Tab',
			Shift: 'Shift',
			Control: 'Control',
			Alt: 'Alt',
			CapsLock: 'CapsLock',
			ArrowLeft: 'ArrowLeft',
			ArrowRight: 'ArrowRight',
			ArrowUp: 'ArrowUp',
			ArrowDown: 'ArrowDown'
		};
		const KB_DISPLAY = {
			' ': 'Space',
			Backspace: '⌫',
			CapsLock: 'Caps',
			Control: 'Ctrl',
			ArrowLeft: '←',
			ArrowRight: '→',
			ArrowUp: '↑',
			ArrowDown: '↓'
		};

		function buildKbVis() {
			const container = document.getElementById('keyboard-vis');
			container.innerHTML = '';
			KB_LAYOUT.forEach((row) => {
				const rowEl = document.createElement('div');
				rowEl.className = 'key-row';
				row.forEach((k) => {
					const el = document.createElement('div');
					el.className = 'key' + (k.length > 3 ? ' wide' : '') + (k === ' ' ? ' space' : '');
					el.id = 'key-' + k.replace(/[^a-zA-Z0-9]/g, '_');
					el.textContent = KB_DISPLAY[k] ?? k.toUpperCase();
					rowEl.appendChild(el);
				});
				container.appendChild(rowEl);
			});
			// Add arrow keys row
			const arrowRow = document.createElement('div');
			arrowRow.className = 'key-row';
			arrowRow.style.marginTop = '4px';
			['ArrowLeft', 'ArrowUp', 'ArrowDown', 'ArrowRight'].forEach((k) => {
				const el = document.createElement('div');
				el.className = 'key';
				el.id = 'key-' + k;
				el.textContent = KB_DISPLAY[k];
				arrowRow.appendChild(el);
			});
			container.appendChild(arrowRow);
		}

		function updateKbVis() {
			const allKeys = new Set([...heldKeys, ...justPressed, ...justReleased]);
			document.querySelectorAll('.key').forEach((el) => {
				el.classList.remove('held', 'just-pressed', 'just-released');
			});
			heldKeys.forEach((k) => {
				const el =
					document.getElementById('key-' + k.replace(/[^a-zA-Z0-9]/g, '_')) ||
					document.getElementById('key-' + k);
				if (el) el.classList.add('held');
			});
			justPressed.forEach((k) => {
				const el =
					document.getElementById('key-' + k.replace(/[^a-zA-Z0-9]/g, '_')) ||
					document.getElementById('key-' + k);
				if (el && !heldKeys.has(k)) el.classList.add('just-pressed');
			});
			justReleased.forEach((k) => {
				const el =
					document.getElementById('key-' + k.replace(/[^a-zA-Z0-9]/g, '_')) ||
					document.getElementById('key-' + k);
				if (el) el.classList.add('just-released');
			});
			// Update text displays
			document.getElementById('kb-held').textContent = heldKeys.size
				? [...heldKeys].join(', ')
				: '—';
			document.getElementById('kb-pressed').textContent = justPressed.size
				? [...justPressed].join(', ')
				: '—';
			document.getElementById('kb-released').textContent = justReleased.size
				? [...justReleased].join(', ')
				: '—';
		}
		buildKbVis();

		/* ════════════════════════════════════════════════════
   MOUSE DEMO
════════════════════════════════════════════════════ */
		const mC = document.getElementById('mouse-canvas');
		const mX = mC.getContext('2d');
		const mvC = document.getElementById('movement-canvas');
		const mvX = mvC.getContext('2d');
		let trail = [];
		let lastMouseOnCanvas = { x: 0, y: 0 };
		let scrollAccum = 0;

		mC.addEventListener('mousemove', (e) => {
			const r = mC.getBoundingClientRect();
			const nx = (((e.clientX - r.left) / r.width) * mC.width) | 0;
			const ny = (((e.clientY - r.top) / r.height) * mC.height) | 0;
			const dx = nx - lastMouseOnCanvas.x,
				dy = ny - lastMouseOnCanvas.y;
			lastMouseOnCanvas = { x: nx, y: ny };
			mousePos = { x: nx, y: ny };
			mouseDelta = { x: dx, y: dy };
			mouseRawDelta = { x: e.movementX, y: e.movementY };
			trail.push({ x: nx, y: ny, t: performance.now() });
			if (trail.length > 80) trail.shift();
			document.getElementById('m-pos').textContent = `(${nx}, ${ny})`;
			document.getElementById('m-delta').textContent = `(${dx}, ${dy})`;
			document.getElementById('m-raw-delta').textContent =
				`(${e.movementX.toFixed(0)}, ${e.movementY.toFixed(0)})`;
			logEvent('mouse', `mousemove (${nx}, ${ny}) Δ(${dx}, ${dy})`);
			updateStateTable();
			drawMouseCanvas();
			drawTrail();
		});
		mC.addEventListener('mousedown', (e) => {
			const btnNames = ['left', 'middle', 'right'];
			mouseButtons.add(e.button);
			document.getElementById('m-' + (btnNames[e.button] || 'left')).textContent = 'DOWN';
			document.getElementById('m-' + (btnNames[e.button] || 'left')).className = 'info-val hot';
			logEvent('press', `mousedown: button ${e.button}`);
			e.preventDefault();
		});
		mC.addEventListener('mouseup', (e) => {
			const btnNames = ['left', 'middle', 'right'];
			mouseButtons.delete(e.button);
			document.getElementById('m-' + (btnNames[e.button] || 'left')).textContent = 'up';
			document.getElementById('m-' + (btnNames[e.button] || 'left')).className = 'info-val';
		});
		mC.addEventListener(
			'wheel',
			(e) => {
				scrollAccum += e.deltaY;
				document.getElementById('m-scroll').textContent = e.deltaY.toFixed(0);
				logEvent('scroll', `scroll Δy: ${e.deltaY.toFixed(0)}`);
				e.preventDefault();
			},
			{ passive: false }
		);
		mC.addEventListener('contextmenu', (e) => e.preventDefault());

		function drawMouseCanvas() {
			const W = mC.width,
				H = mC.height;
			mX.clearRect(0, 0, W, H);
			mX.fillStyle = '#07030a';
			mX.fillRect(0, 0, W, H);
			// Grid
			mX.strokeStyle = '#190f14';
			mX.lineWidth = 1;
			for (let x = 0; x < W; x += 40) {
				mX.beginPath();
				mX.moveTo(x, 0);
				mX.lineTo(x, H);
				mX.stroke();
			}
			for (let y = 0; y < H; y += 40) {
				mX.beginPath();
				mX.moveTo(0, y);
				mX.lineTo(W, y);
				mX.stroke();
			}
			// Crosshair
			mX.strokeStyle = '#3a1828';
			mX.lineWidth = 1;
			mX.beginPath();
			mX.moveTo(mousePos.x, 0);
			mX.lineTo(mousePos.x, H);
			mX.stroke();
			mX.beginPath();
			mX.moveTo(0, mousePos.y);
			mX.lineTo(W, mousePos.y);
			mX.stroke();
			// Cursor dot
			mX.beginPath();
			mX.arc(mousePos.x, mousePos.y, 8, 0, Math.PI * 2);
			mX.fillStyle = mouseButtons.size ? '#f43f5e' : '#f43f5e50';
			mX.fill();
			mX.strokeStyle = '#fff';
			mX.lineWidth = 1.5;
			mX.stroke();
			// Coords label
			mX.font = '11px IBM Plex Mono';
			mX.fillStyle = '#f43f5e';
			mX.textAlign = 'left';
			mX.fillText(`(${mousePos.x}, ${mousePos.y})`, mousePos.x + 12, mousePos.y - 8);
			// Delta arrow
			if (Math.abs(mouseDelta.x) > 1 || Math.abs(mouseDelta.y) > 1) {
				const scale = 4;
				mX.beginPath();
				mX.moveTo(mousePos.x, mousePos.y);
				mX.lineTo(mousePos.x + mouseDelta.x * scale, mousePos.y + mouseDelta.y * scale);
				mX.strokeStyle = '#38bdf8';
				mX.lineWidth = 2;
				mX.stroke();
			}
		}
		function drawTrail() {
			const W = mvC.width,
				H = mvC.height;
			mvX.clearRect(0, 0, W, H);
			mvX.fillStyle = '#07030a';
			mvX.fillRect(0, 0, W, H);
			const now = performance.now();
			trail.forEach((pt, i) => {
				const age = (now - pt.t) / 1000;
				const alpha = Math.max(0, 1 - age * 2);
				if (alpha <= 0) return;
				mvX.beginPath();
				mvX.arc((pt.x / mC.width) * W, H / 2 + (pt.y - mC.height / 2) * 0.3, 2, 0, Math.PI * 2);
				mvX.fillStyle = `rgba(244,63,94,${alpha * 0.8})`;
				mvX.fill();
			});
			requestAnimationFrame(drawTrail);
		}
		drawMouseCanvas();
		drawTrail();

		/* ════════════════════════════════════════════════════
   INPUT MAP BUILDER
════════════════════════════════════════════════════ */
		const inputMapDef = [
			{ action: 'move_left', bindings: ['ArrowLeft', 'a'], icon: '←' },
			{ action: 'move_right', bindings: ['ArrowRight', 'd'], icon: '→' },
			{ action: 'jump', bindings: [' ', 'w', 'ArrowUp'], icon: '↑' },
			{ action: 'attack', bindings: ['z', 'x'], icon: '⚔' },
			{ action: 'interact', bindings: ['e', 'f'], icon: '✦' },
			{ action: 'pause', bindings: ['Escape', 'p'], icon: '⏸' }
		];
		let activeBindings = {};
		inputMapDef.forEach((a) => {
			activeBindings[a.action] = new Set(a.bindings);
		});

		function buildInputMapUI() {
			const el = document.getElementById('input-map-ui');
			el.innerHTML = inputMapDef
				.map(
					(a) =>
						`<div class="action-row">
      <div class="action-name">${a.icon} ${a.action}</div>
      <div class="action-bindings" id="bindings-${a.action}">
        ${a.bindings
					.map(
						(b) =>
							`<div class="binding-chip ${activeBindings[a.action]?.has(b) ? 'active-bind' : ''}"
           onclick="toggleBinding('${a.action}','${b}',this)">${b == ' ' ? 'Space' : b}</div>`
					)
					.join('')}
      </div>
    </div>`
				)
				.join('');
		}
		function toggleBinding(action, key, el) {
			if (activeBindings[action].has(key)) activeBindings[action].delete(key);
			else activeBindings[action].add(key);
			el.classList.toggle('active-bind');
			updateInputMap();
		}
		function updateInputMap() {
			const active = [];
			inputMapDef.forEach((a) => {
				const bound = [...activeBindings[a.action]];
				const isActive = bound.some((k) => heldKeys.has(k) || justPressed.has(k));
				if (isActive) active.push(a.action);
			});
			const el = document.getElementById('active-actions');
			if (el)
				el.innerHTML = active.length
					? active
							.map(
								(a) =>
									`<span style="padding:3px 10px;border:1px solid var(--accent3);color:var(--accent3);font-size:11px;">${a}</span>`
							)
							.join('')
					: '<span style="color:var(--muted);font-size:12px;">none — press a bound key</span>';
		}
		buildInputMapUI();

		/* ════════════════════════════════════════════════════
   SIMULTANEOUS INPUT DEMO
════════════════════════════════════════════════════ */
		const simC = document.getElementById('sim-canvas');
		const simX = simC.getContext('2d');
		let simPolicy = 'cancel';
		let simBall = { x: 430, y: 100, vx: 0, vy: 0 };
		const SIM_SPEED = 180,
			SIM_GRAVITY = 400,
			SIM_GROUND = 160;
		let simLastT = performance.now();
		const simPressHistory = [];

		function setPolicy(p, btn) {
			simPolicy = p;
			document.querySelectorAll('#sim-canvas ~ div button, .demo-box .btn').forEach((b) => {
				if (['Neutral / Cancel', 'Last Key Wins', 'Normalized Diagonal'].includes(b.textContent))
					b.classList.remove('active');
			});
			btn.classList.add('active');
		}

		function getSimAxis() {
			const left = heldKeys.has('ArrowLeft') || heldKeys.has('a');
			const right = heldKeys.has('ArrowRight') || heldKeys.has('d');
			const up = heldKeys.has('ArrowUp') || heldKeys.has('w') || heldKeys.has(' ');
			const down = heldKeys.has('ArrowDown') || heldKeys.has('s');

			if (simPolicy === 'cancel') {
				return { dx: (right ? 1 : 0) - (left ? 1 : 0), dy: (down ? 1 : 0) - (up ? 1 : 0) };
			} else if (simPolicy === 'last') {
				let dx = 0;
				if (left && right) {
					const lastH = [...pressHistory]
						.reverse()
						.find((k) => ['ArrowLeft', 'a', 'ArrowRight', 'd'].includes(k));
					dx = lastH === 'ArrowLeft' || lastH === 'a' ? -1 : 1;
				} else dx = (right ? 1 : 0) - (left ? 1 : 0);
				return { dx, dy: (down ? 1 : 0) - (up ? 1 : 0) };
			} else {
				// normalized
				let dx = (right ? 1 : 0) - (left ? 1 : 0);
				let dy = (down ? 1 : 0) - (up ? 1 : 0);
				const len = Math.sqrt(dx * dx + dy * dy) || 1;
				return { dx: dx / len, dy: dy / len };
			}
		}

		function drawSimCanvas() {
			const W = simC.width,
				H = simC.height;
			const now = performance.now();
			const dt = Math.min((now - simLastT) / 1000, 0.05);
			simLastT = now;

			const { dx, dy } = getSimAxis();
			simBall.vx += dx * SIM_SPEED * dt * 6;
			simBall.vx *= 1 - dt * 4;
			simBall.vy += SIM_GRAVITY * dt;
			simBall.x += simBall.vx * dt;
			simBall.y += simBall.vy * dt;
			if (simBall.y >= H - SIM_GROUND) {
				simBall.y = H - SIM_GROUND;
				simBall.vy = -Math.abs(simBall.vy) * 0.5;
			}
			if (simBall.x < 20) {
				simBall.x = 20;
				simBall.vx = Math.abs(simBall.vx) * 0.6;
			}
			if (simBall.x > W - 20) {
				simBall.x = W - 20;
				simBall.vx = -Math.abs(simBall.vx) * 0.6;
			}

			simX.clearRect(0, 0, W, H);
			simX.fillStyle = '#080306';
			simX.fillRect(0, 0, W, H);
			simX.fillStyle = '#190f14';
			simX.fillRect(0, H - SIM_GROUND, W, SIM_GROUND);
			simX.strokeStyle = '#28101a';
			simX.lineWidth = 1;
			simX.beginPath();
			simX.moveTo(0, H - SIM_GROUND);
			simX.lineTo(W, H - SIM_GROUND);
			simX.stroke();

			// Direction indicator
			const dirLen = 40;
			simX.beginPath();
			simX.moveTo(simBall.x, simBall.y);
			simX.lineTo(simBall.x + dx * dirLen, simBall.y + dy * dirLen);
			simX.strokeStyle = '#f43f5e';
			simX.lineWidth = 2;
			simX.stroke();

			simX.beginPath();
			simX.arc(simBall.x, simBall.y, 14, 0, Math.PI * 2);
			simX.fillStyle = '#f43f5e30';
			simX.fill();
			simX.strokeStyle = '#f43f5e';
			simX.lineWidth = 2;
			simX.stroke();

			const policyDescs = {
				cancel: 'Neutral/Cancel: LEFT+RIGHT → dx=0, object stops.',
				last: 'Last Key Wins: most recently pressed direction takes priority.',
				norm: 'Normalized: diagonal = same speed as cardinal (len=1 always).'
			};
			document.getElementById('sim-info').innerHTML =
				`<span style="color:var(--muted)">policy: <span style="color:var(--accent)">${simPolicy}</span></span>` +
				`<span style="color:var(--muted)">dx=${dx.toFixed(2)} dy=${dy.toFixed(2)}</span>` +
				`<span style="color:var(--muted)">vx=${simBall.vx.toFixed(0)} vy=${simBall.vy.toFixed(0)}</span>` +
				`<span style="color:var(--muted);font-size:11px;">${policyDescs[simPolicy]}</span>`;

			requestAnimationFrame(drawSimCanvas);
		}
		drawSimCanvas();

		/* ════════════════════════════════════════════════════
   FULL GAME SCENE
════════════════════════════════════════════════════ */
		const gcC = document.getElementById('game-canvas');
		const gcX = gcC.getContext('2d');
		let gcActive = false;

		const PLATFORMS = [
			{ x: 0, y: 340, w: 500, h: 40 }, // ground
			{ x: 80, y: 260, w: 120, h: 12 },
			{ x: 260, y: 200, w: 100, h: 12 },
			{ x: 370, y: 270, w: 80, h: 12 },
			{ x: 140, y: 150, w: 80, h: 12 }
		];
		const COINS = [
			{ x: 130, y: 230, r: 8, collected: false },
			{ x: 305, y: 170, r: 8, collected: false },
			{ x: 400, y: 240, r: 8, collected: false },
			{ x: 180, y: 120, r: 8, collected: false }
		];

		let player = {
			x: 60,
			y: 280,
			vx: 0,
			vy: 0,
			w: 20,
			h: 28,
			onGround: false,
			facing: 1,
			jumpHeld: false,
			jumpTime: 0
		};
		let gcMouse = { x: 250, y: 190 };
		let projectiles = [];
		let gcScore = 0;
		let gcT = 0,
			gcLastT = performance.now();
		let shotCooldown = 0;

		function gcReset() {
			player = {
				x: 60,
				y: 280,
				vx: 0,
				vy: 0,
				w: 20,
				h: 28,
				onGround: false,
				facing: 1,
				jumpHeld: false,
				jumpTime: 0
			};
			COINS.forEach((c) => (c.collected = false));
			projectiles = [];
			gcScore = 0;
		}

		gcC.addEventListener('click', () => {
			if (!gcActive) {
				gcActive = true;
				document.getElementById('game-hint').textContent =
					'WASD/Arrows move · Space/W/↑ jump (hold) · Mouse aim · Click shoot · R reset';
			}
		});
		gcC.addEventListener('mousemove', (e) => {
			const r = gcC.getBoundingClientRect();
			gcMouse = {
				x: ((e.clientX - r.left) / r.width) * gcC.width,
				y: ((e.clientY - r.top) / r.height) * gcC.height
			};
		});
		gcC.addEventListener('mousedown', (e) => {
			if (!gcActive) return;
			if (e.button === 0 && shotCooldown <= 0) {
				const dx = gcMouse.x - (player.x + player.w / 2);
				const dy = gcMouse.y - (player.y + player.h / 2);
				const len = Math.sqrt(dx * dx + dy * dy) || 1;
				projectiles.push({
					x: player.x + player.w / 2,
					y: player.y + player.h / 2,
					vx: (dx / len) * 400,
					vy: (dy / len) * 400,
					life: 2
				});
				shotCooldown = 0.25;
			}
			e.preventDefault();
		});
		gcC.addEventListener('contextmenu', (e) => e.preventDefault());

		function aabb(ax, ay, aw, ah, bx, by, bw, bh) {
			return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
		}

		function updateGame(dt) {
			if (!gcActive) return;
			const accel = parseInt(document.getElementById('g-accel').value);
			const friction = parseInt(document.getElementById('g-friction').value);
			const jumpForce = parseInt(document.getElementById('g-jump').value);
			const gravity = parseInt(document.getElementById('g-gravity').value);

			// Check "R" for reset (one-shot)
			if (justPressed.has('r') || justPressed.has('R')) gcReset();

			// Horizontal
			const left = heldKeys.has('ArrowLeft') || heldKeys.has('a') || heldKeys.has('A');
			const right = heldKeys.has('ArrowRight') || heldKeys.has('d') || heldKeys.has('D');
			if (left) {
				player.vx -= accel * dt;
				player.facing = -1;
			}
			if (right) {
				player.vx += accel * dt;
				player.facing = 1;
			}
			player.vx *= 1 - friction * dt;

			// Jump
			const jumpKey =
				heldKeys.has(' ') || heldKeys.has('w') || heldKeys.has('W') || heldKeys.has('ArrowUp');
			const jumpJustPressed =
				justPressed.has(' ') ||
				justPressed.has('w') ||
				justPressed.has('W') ||
				justPressed.has('ArrowUp');
			if (jumpJustPressed && player.onGround) {
				player.vy = -jumpForce;
				player.jumpHeld = true;
				player.jumpTime = 0;
			}
			if (jumpKey && player.jumpHeld) {
				player.jumpTime += dt;
				if (player.jumpTime < 0.2) player.vy -= jumpForce * 0.8 * dt;
				else player.jumpHeld = false;
			}
			if (!jumpKey) player.jumpHeld = false;

			// Gravity
			player.vy += gravity * dt;
			player.x += player.vx * dt;
			player.y += player.vy * dt;

			// Platform collision
			player.onGround = false;
			PLATFORMS.forEach((p) => {
				if (aabb(player.x, player.y, player.w, player.h, p.x, p.y, p.w, p.h)) {
					const overlapBottom = player.y + player.h - p.y;
					const overlapTop = p.y + p.h - player.y;
					const overlapRight = player.x + player.w - p.x;
					const overlapLeft = p.x + p.w - player.x;
					const minOverlap = Math.min(overlapBottom, overlapTop, overlapRight, overlapLeft);
					if (minOverlap === overlapBottom && player.vy >= 0) {
						player.y = p.y - player.h;
						player.vy = 0;
						player.onGround = true;
						player.jumpHeld = false;
					} else if (minOverlap === overlapTop && player.vy < 0) {
						player.y = p.y + p.h;
						player.vy = 0;
					} else if (minOverlap === overlapRight) {
						player.x = p.x - player.w;
						player.vx = 0;
					} else {
						player.x = p.x + p.w;
						player.vx = 0;
					}
				}
			});

			// Clamp to canvas
			if (player.x < 0) {
				player.x = 0;
				player.vx = 0;
			}
			if (player.x + player.w > gcC.width) {
				player.x = gcC.width - player.w;
				player.vx = 0;
			}
			if (player.y > gcC.height) {
				player.y = -40;
			}

			// Projectiles
			shotCooldown -= dt;
			projectiles.forEach((proj) => {
				proj.x += proj.vx * dt;
				proj.y += proj.vy * dt;
				proj.life -= dt;
			});
			projectiles = projectiles.filter((p) => p.life > 0);

			// Coins
			COINS.forEach((c) => {
				if (
					!c.collected &&
					aabb(player.x, player.y, player.w, player.h, c.x - c.r, c.y - c.r, c.r * 2, c.r * 2)
				) {
					c.collected = true;
					gcScore++;
				}
				// Projectile hit
				projectiles.forEach((proj) => {
					if (!c.collected && Math.hypot(proj.x - c.x, proj.y - c.y) < c.r + 4) {
						c.collected = true;
						gcScore++;
					}
				});
			});

			// Respawn coins
			if (COINS.every((c) => c.collected)) COINS.forEach((c) => (c.collected = false));
		}

		function drawGame() {
			const W = gcC.width,
				H = gcC.height;
			gcX.clearRect(0, 0, W, H);
			gcX.fillStyle = '#080306';
			gcX.fillRect(0, 0, W, H);

			// Background grid
			gcX.strokeStyle = '#100810';
			gcX.lineWidth = 1;
			for (let x = 0; x < W; x += 40) {
				gcX.beginPath();
				gcX.moveTo(x, 0);
				gcX.lineTo(x, H);
				gcX.stroke();
			}
			for (let y = 0; y < H; y += 40) {
				gcX.beginPath();
				gcX.moveTo(0, y);
				gcX.lineTo(W, y);
				gcX.stroke();
			}

			// Platforms
			PLATFORMS.forEach((p, i) => {
				gcX.fillStyle = i === 0 ? '#190f14' : '#28101a';
				gcX.fillRect(p.x, p.y, p.w, p.h);
				gcX.strokeStyle = i === 0 ? '#3a1828' : '#f43f5e30';
				gcX.lineWidth = 1;
				gcX.strokeRect(p.x, p.y, p.w, p.h);
			});

			// Coins
			COINS.forEach((c) => {
				if (c.collected) return;
				gcX.beginPath();
				gcX.arc(c.x, c.y, c.r, 0, Math.PI * 2);
				gcX.fillStyle = '#fbbf2420';
				gcX.fill();
				gcX.strokeStyle = '#fbbf24';
				gcX.lineWidth = 1.5;
				gcX.stroke();
				gcX.fillStyle = '#fbbf24';
				gcX.font = 'bold 10px IBM Plex Mono';
				gcX.textAlign = 'center';
				gcX.fillText('★', c.x, c.y + 4);
			});

			// Projectiles
			projectiles.forEach((proj) => {
				gcX.beginPath();
				gcX.arc(proj.x, proj.y, 4, 0, Math.PI * 2);
				gcX.fillStyle = '#f43f5e';
				gcX.fill();
				gcX.beginPath();
				gcX.arc(proj.x, proj.y, 8, 0, Math.PI * 2);
				gcX.strokeStyle = '#f43f5e40';
				gcX.lineWidth = 1;
				gcX.stroke();
			});

			// Aim line
			if (gcActive) {
				const px = player.x + player.w / 2,
					py = player.y + player.h / 2;
				const dx = gcMouse.x - px,
					dy = gcMouse.y - py;
				const len = Math.sqrt(dx * dx + dy * dy) || 1;
				gcX.beginPath();
				gcX.moveTo(px, py);
				gcX.lineTo(px + (dx / len) * 30, py + (dy / len) * 30);
				gcX.strokeStyle = '#f43f5e60';
				gcX.lineWidth = 1;
				gcX.setLineDash([3, 4]);
				gcX.stroke();
				gcX.setLineDash([]);
			}

			// Player
			const px = player.x,
				py = player.y,
				pw = player.w,
				ph = player.h;
			gcX.fillStyle = '#f43f5e20';
			gcX.fillRect(px, py, pw, ph);
			gcX.strokeStyle = '#f43f5e';
			gcX.lineWidth = 2;
			gcX.strokeRect(px, py, pw, ph);
			// Face direction indicator
			gcX.fillStyle = '#f43f5e';
			gcX.fillRect(px + (player.facing > 0 ? pw - 4 : 0), py + 6, 4, 4);
			// Eyes
			gcX.fillStyle = '#fff';
			const eyeX = px + (player.facing > 0 ? pw - 8 : 4);
			gcX.fillRect(eyeX, py + 8, 4, 4);

			// HUD
			if (!gcActive) {
				gcX.fillStyle = 'rgba(0,0,0,0.6)';
				gcX.fillRect(0, 0, W, H);
				gcX.fillStyle = '#f43f5e';
				gcX.font = 'bold 14px IBM Plex Mono';
				gcX.textAlign = 'center';
				gcX.fillText('Click to activate', W / 2, H / 2);
			}
			gcX.font = '12px IBM Plex Mono';
			gcX.fillStyle = '#f43f5e';
			gcX.textAlign = 'left';
			gcX.fillText(`★ ${gcScore}`, 12, 20);
			gcX.fillStyle = '#5a2840';
			gcX.textAlign = 'right';
			gcX.fillText(shotCooldown > 0 ? `reload ${shotCooldown.toFixed(1)}s` : 'ready', W - 12, 20);

			// Update stats
			if (gcActive) {
				document.getElementById('gs-pos').textContent =
					`(${Math.round(player.x)}, ${Math.round(player.y)})`;
				document.getElementById('gs-vel').textContent =
					`(${Math.round(player.vx)}, ${Math.round(player.vy)})`;
				document.getElementById('gs-ground').textContent = player.onGround ? 'true' : 'false';
				document.getElementById('gs-jump').textContent = player.jumpHeld ? 'true' : 'false';
				document.getElementById('gs-facing').textContent = player.facing > 0 ? 'right' : 'left';
				document.getElementById('gs-score').textContent = gcScore;
				['g-accel', 'g-friction', 'g-jump', 'g-gravity'].forEach((id) => {
					document.getElementById(id + '-val').textContent = document.getElementById(id).value;
				});
			}
		}

		function gameLoop() {
			const now = performance.now();
			const dt = Math.min((now - gcLastT) / 1000, 0.05);
			gcLastT = now;
			gcT += dt;
			updateGame(dt);
			drawGame();
			requestAnimationFrame(gameLoop);
		}
		gameLoop();

		/* ════════════════════════════════════════════════════
   ASSESSMENT
════════════════════════════════════════════════════ */
		const assessData = [
			{
				title: 'Scenario 1 · Missing event drain',
				q: `A game loop processes input by only reading pygame.key.get_pressed() — the polling API — and never calls pygame.event.pump() or processes the event queue. What problem occurs?`,
				options: [
					'Keyboard state is always empty — polling never works without events',
					'The window appears frozen and unresponsive to the OS after a few seconds',
					'Only the first key press is detected; subsequent presses are ignored',
					'Key repeat events fire constantly, causing unintended actions'
				],
				correct: 1,
				explanation:
					'pygame.key.get_pressed() reads hardware state directly and works without the event queue. But the OS sends window management events (close button, resize, alt-tab) into the queue. If you never drain it, the queue fills up and the OS marks the app as "not responding". You must call pygame.event.get() or pump() every frame even if you use polling for gameplay input.'
			},
			{
				title: 'Scenario 2 · Just-pressed for movement',
				q: `A developer writes: if event.type == KEYDOWN and event.key == K_RIGHT: player.x += 10
This runs in the event loop, not the game loop. What is the problem?`,
				options: [
					'KEYDOWN fires continuously while the key is held, moving the player too fast',
					'The player only moves on the single frame the key was pressed, then stops',
					'The player moves in the wrong direction because KEYDOWN is inverted',
					'event.key returns a string, not an integer constant, so the comparison always fails'
				],
				correct: 1,
				explanation:
					'KEYDOWN fires once when the key is first pressed, then again only for OS key-repeat events (after a delay, at the OS repeat rate). The player will stutter: one step on press, a pause, then repeated steps at the OS typing rate. The fix for continuous movement is to use heldKeys to track state, then apply movement every frame in the update loop.'
			},
			{
				title: 'Scenario 3 · Diagonal speed',
				q: `A top-down character uses: dx = (RIGHT held ? 1 : 0) - (LEFT held ? 1 : 0), dy = (DOWN held ? 1 : 0) - (UP held ? 1 : 0). Then: player.x += dx * speed * dt, player.y += dy * speed * dt. What is the bug when moving diagonally?`,
				options: [
					'The character cannot move diagonally — diagonal inputs cancel each other',
					'The character moves at √2 × speed diagonally instead of speed',
					'The character oscillates because dx and dy conflict each frame',
					'No bug — this is the correct implementation'
				],
				correct: 1,
				explanation:
					'When both dx and dy are ±1, the movement vector has length √(1²+1²) = √2 ≈ 1.414. Multiplied by speed, the character moves ~41% faster diagonally than cardinally. Fix: normalize the vector — divide by its length — so that (1,1) becomes (0.707, 0.707), preserving direction with length 1.'
			},
			{
				title: 'Scenario 4 · Input mapping benefit',
				q: `You have hard-coded "if inp.held(\'SPACE\'): player.jump()" throughout 15 game files. A playtest reveals players want to jump with W as well. What is the minimum-change fix with an input map?`,
				options: [
					'Find and replace all 15 occurrences of SPACE with a conditional checking both SPACE and W',
					'Change one line in the InputMap setup: actions.bind("jump", "SPACE", "W") — no game logic changes needed',
					'Add a second input handler class that checks W and runs alongside the first',
					'The input map does not help here — you still need to update all 15 call sites'
				],
				correct: 1,
				explanation:
					'The input map decouples the action ("jump") from the physical key. All 15 files ask actions.held("jump", inp) — they never mention SPACE directly. To add W as an additional jump key, you change exactly one line in the binding setup. This is the entire point of the abstraction.'
			},
			{
				title: 'Scenario 5 · Variable-height jump',
				q: `To implement a variable-height jump (tap for small jump, hold for big jump), which combination of key states is needed?`,
				options: [
					'just_pressed only — to launch the jump on the first frame of press',
					'held only — to continuously apply upward force while the key is down',
					'just_pressed to launch, held to continue applying upward boost, just_released to cut velocity early',
					'just_released only — to finalize the jump height when the key is lifted'
				],
				correct: 2,
				explanation:
					'A variable-height jump requires all three states: (1) just_pressed detects the exact frame the key was pushed — fire the initial jump impulse here. (2) held allows continued upward acceleration while the key remains down, up to a maximum hold time. (3) just_released detects the early release — cut upward velocity (e.g. vy *= 0.5) so the player gets a shorter jump. Using only one state cannot express all three phases of the interaction.'
			}
		];

		let assessAnswered = 0,
			assessCorrect = 0;
		function buildAssess() {
			const c = document.getElementById('assess-container');
			c.innerHTML = '';
			assessData.forEach((p, pi) => {
				const div = document.createElement('div');
				div.className = 'challenge-box';
				div.innerHTML =
					`<div class="challenge-num">Question ${pi + 1} · ${p.title}</div>` +
					`<div class="challenge-q">${p.q}</div>` +
					`<div class="ch-options" id="ch-opts-${pi}">${p.options.map((o, oi) => `<div class="ch-option" onclick="assessAns(${pi},${oi})" id="ch-opt-${pi}-${oi}">${o}</div>`).join('')}</div>` +
					`<div class="ch-feedback" id="ch-fb-${pi}"></div>`;
				c.appendChild(div);
			});
		}
		function assessAns(pi, oi) {
			const p = assessData[pi];
			document
				.querySelectorAll(`#ch-opts-${pi} .ch-option`)
				.forEach((o) => o.classList.add('disabled'));
			const fb = document.getElementById(`ch-fb-${pi}`);
			if (oi === p.correct) {
				document.getElementById(`ch-opt-${pi}-${oi}`).classList.add('correct');
				fb.textContent = '✓ ' + p.explanation;
				fb.className = 'ch-feedback ok';
				assessCorrect++;
			} else {
				document.getElementById(`ch-opt-${pi}-${oi}`).classList.add('wrong');
				document.getElementById(`ch-opt-${pi}-${p.correct}`).classList.add('correct');
				fb.textContent = '✗ ' + p.explanation;
				fb.className = 'ch-feedback bad';
			}
			assessAnswered++;
			if (assessAnswered === assessData.length) {
				const s = document.getElementById('assess-score');
				s.style.display = 'block';
				document.getElementById('assess-score-num').textContent =
					`${assessCorrect}/${assessData.length}`;
				s.style.borderColor =
					assessCorrect === assessData.length
						? 'var(--accent3)'
						: assessCorrect >= 3
							? 'var(--accent4)'
							: 'var(--accent)';
			}
		}
		buildAssess();

		window.addEventListener('scroll', () => {
			document.getElementById('reading-progress').style.width =
				Math.min(100, (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100) +
				'%';
		});

		if (typeof logEvent === 'function') window.logEvent = logEvent;
		if (typeof updateStateTable === 'function') window.updateStateTable = updateStateTable;
		if (typeof drawTrail === 'function') window.drawTrail = drawTrail;
		if (typeof buildKbVis === 'function') window.buildKbVis = buildKbVis;
		if (typeof updateGame === 'function') window.updateGame = updateGame;
		if (typeof renderEventLog === 'function') window.renderEventLog = renderEventLog;
		if (typeof updateInputMap === 'function') window.updateInputMap = updateInputMap;
		if (typeof buildAssess === 'function') window.buildAssess = buildAssess;
		if (typeof setPolicy === 'function') window.setPolicy = setPolicy;
		if (typeof assessAns === 'function') window.assessAns = assessAns;
		if (typeof gameLoop === 'function') window.gameLoop = gameLoop;
		if (typeof drawMouseCanvas === 'function') window.drawMouseCanvas = drawMouseCanvas;
		if (typeof gcReset === 'function') window.gcReset = gcReset;
		if (typeof getSimAxis === 'function') window.getSimAxis = getSimAxis;
		if (typeof updateKbVis === 'function') window.updateKbVis = updateKbVis;
		if (typeof toggleBinding === 'function') window.toggleBinding = toggleBinding;
		if (typeof drawGame === 'function') window.drawGame = drawGame;
		if (typeof drawSimCanvas === 'function') window.drawSimCanvas = drawSimCanvas;
		if (typeof buildInputMapUI === 'function') window.buildInputMapUI = buildInputMapUI;
		if (typeof aabb === 'function') window.aabb = aabb;

		return () => {
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
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 08 of 12</div>
	</header>

	<div class="module-hero">
		<div class="module-number">08</div>
		<div class="module-tag">Module 08 · Theory + Practice</div>
		<h1 class="module-title">Input and<br /><span>Player Interaction</span></h1>
		<div class="progress-bar-wrap">
			<div class="progress-bar-fill" id="reading-progress"></div>
		</div>
	</div>

	<nav class="toc">
		<div class="toc-label">Contents</div>
		<ul class="toc-list">
			<li><a href="#objectives">Objectives</a></li>
			<li><a href="#models">Event-Driven vs Polling</a></li>
			<li><a href="#keyboard">Keyboard State</a></li>
			<li><a href="#mouse">Mouse Input</a></li>
			<li><a href="#mapping">Input Mapping</a></li>
			<li><a href="#simultaneous">Simultaneous Inputs</a></li>
			<li><a href="#practical">Practical Work</a></li>
			<li><a href="#assessment">Assessment</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand the difference between event-driven and polling input models</li>
			<li>Track keyboard state across frames: held, just-pressed, just-released</li>
			<li>Read mouse position, delta, buttons, and scroll</li>
			<li>Build an input mapping layer that decouples game logic from raw keys</li>
			<li>Handle simultaneous inputs without conflict</li>
		</ul>
	</section>

	<!-- ══ 08.01 MODELS ══ -->
	<section id="models" class="section">
		<div class="section-header">
			<span class="section-num">08.01</span>
			<h2 class="section-title">Event-Driven vs Polling Models</h2>
		</div>

		<p>
			There are two fundamentally different ways to read input. Understanding the difference — and
			knowing when to use each — is necessary before writing a single line of input code.
		</p>
		<p>
			In the <strong>event-driven model</strong>, the OS pushes input events into a queue. You drain
			the queue once per frame. Each item is a discrete event: a key was pressed at a specific
			moment, a mouse button was released. This model is exact — you never miss an event that
			happened between frames.
		</p>
		<p>
			In the <strong>polling model</strong>, you ask the input system right now: "is this key
			currently down?" You call this every frame. It tells you the current hardware state, not what
			happened since you last asked. This is simpler for movement — you just check "is LEFT held?" —
			but it cannot detect events that start and finish between two polls.
		</p>

		<table>
			<thead>
				<tr>
					<th>Property</th>
					<th>Event-Driven</th>
					<th>Polling</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Detects rapid tap (sub-frame)</td>
					<td>Yes — event is queued</td>
					<td>No — may be missed</td>
				</tr>
				<tr>
					<td>Held-key movement</td>
					<td>Awkward — needs state tracking</td>
					<td>Natural — check every frame</td>
				</tr>
				<tr>
					<td>Text input</td>
					<td>Correct — uses key repeat events</td>
					<td>Wrong — must implement yourself</td>
				</tr>
				<tr>
					<td>OS integration</td>
					<td>Required for window events (resize, quit)</td>
					<td>Only for state, not OS signals</td>
				</tr>
				<tr>
					<td>Used for</td>
					<td>UI actions, typing, one-shot abilities</td>
					<td>Continuous movement, camera control</td>
				</tr>
			</tbody>
		</table>

		<p>
			In practice, game engines use <em>both</em>: the event queue provides the raw input, and each
			frame's events are processed to update a persistent state table that can be polled. This gives
			you exact event timing <em>and</em> the convenience of polling.
		</p>

		<!-- EVENT VS POLL VISUALIZER -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Event Queue vs State Table</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Press keys on the keyboard below. Watch events accumulate in the queue (left) and the
					persistent state table update (right).
				</p>
				<div class="two-col" style="align-items: start">
					<div>
						<div
							style="
										font-size: 10px;
										letter-spacing: 0.15em;
										text-transform: uppercase;
										color: var(--muted);
										margin-bottom: 0.5rem;
									"
						>
							Event Queue (drained each frame)
						</div>
						<div class="event-log" id="event-log-a"></div>
						<div style="font-size: 10px; color: var(--muted); margin-top: 0.4rem">
							<span style="color: var(--accent)">■</span> keydown &nbsp;
							<span style="color: var(--accent2)">■</span> keyup &nbsp;
							<span style="color: var(--accent4)">■</span> mousemove &nbsp;
							<span style="color: var(--accent3)">■</span> scroll
						</div>
					</div>
					<div>
						<div
							style="
										font-size: 10px;
										letter-spacing: 0.15em;
										text-transform: uppercase;
										color: var(--muted);
										margin-bottom: 0.5rem;
									"
						>
							State Table (polled each frame)
						</div>
						<div class="info-panel" id="state-table">
							<div class="info-row">
								<span class="info-key">keys_held</span><span class="info-val" id="st-held"
									>&#123;&#125;</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">just_pressed</span><span class="info-val hot" id="st-pressed"
									>&#123;&#125;</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">just_released</span><span
									class="info-val"
									style="color: var(--accent2)"
									id="st-released">&#123;&#125;</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">mouse_pos</span><span class="info-val" id="st-mouse"
									>(0, 0)</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">mouse_buttons</span><span class="info-val" id="st-mbuttons"
									>&#123;&#125;</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">scroll_delta</span><span class="info-val" id="st-scroll"
									>(0, 0)</span
								>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ 08.02 KEYBOARD ══ -->
	<section id="keyboard" class="section">
		<div class="section-header">
			<span class="section-num">08.02</span>
			<h2 class="section-title">Keyboard State: Held, Just-Pressed, Just-Released</h2>
		</div>

		<p>
			Tracking three distinct keyboard states solves almost every input need. <em>Held</em> is true
			while the key is down. <em>Just-pressed</em> is true for exactly one frame — the frame the key
			was pushed down. <em>Just-released</em> is true for exactly one frame — the frame the key was lifted.
		</p>

		<pre><code
				><span class="kw">class</span> <span class="fn">InputState</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self._held         = <span class="fn">set</span>()   <span class="cm"
					># keys currently down</span
				>
        self._just_pressed = <span class="fn">set</span>()   <span class="cm"
					># keys pressed THIS frame</span
				>
        self._just_released= <span class="fn">set</span>()   <span class="cm"
					># keys released THIS frame</span
				>

    <span class="kw">def</span> <span class="fn">begin_frame</span>(self):
        <span class="cm"># Clear per-frame sets at the start of each frame</span>
        self._just_pressed.<span class="fn">clear</span>()
        self._just_released.<span class="fn">clear</span>()

    <span class="kw">def</span> <span class="fn">on_key_down</span>(self, key):
        <span class="kw">if</span> key <span class="kw">not in</span> self._held:   <span class="cm"
					># ignore OS key-repeat events</span
				>
            self._just_pressed.<span class="fn">add</span>(key)
        self._held.<span class="fn">add</span>(key)

    <span class="kw">def</span> <span class="fn">on_key_up</span>(self, key):
        self._held.<span class="fn">discard</span>(key)
        self._just_released.<span class="fn">add</span>(key)

    <span class="cm"># Polling API — call these anywhere in the update step</span>
    <span class="kw">def</span> <span class="fn">held</span>(self, key):          <span class="kw"
					>return</span
				> key <span class="kw">in</span> self._held
    <span class="kw">def</span> <span class="fn">just_pressed</span>(self, key):  <span class="kw"
					>return</span
				> key <span class="kw">in</span> self._just_pressed
    <span class="kw">def</span> <span class="fn">just_released</span>(self, key): <span class="kw"
					>return</span
				> key <span class="kw">in</span> self._just_released<span class="lang-tag">python</span
				></code
			></pre>

		<!-- KEYBOARD VISUALIZER -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Key State Visualizer</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Press and hold keys. Watch the three state layers update. The just-pressed and
					just-released states flash for exactly one simulated frame.
				</p>
				<div id="keyboard-vis-container">
					<div class="keyboard-vis" id="keyboard-vis"></div>
				</div>
				<div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem; font-size: 12px">
					<span
						><span
							style="
										display: inline-block;
										width: 12px;
										height: 12px;
										background: var(--accent);
										margin-right: 5px;
										vertical-align: middle;
									"
						></span>Held</span
					>
					<span
						><span
							style="
										display: inline-block;
										width: 12px;
										height: 12px;
										background: color-mix(in srgb, var(--accent) 50%, transparent);
										border: 1px solid var(--accent);
										margin-right: 5px;
										vertical-align: middle;
									"
						></span>Just Pressed (1 frame)</span
					>
					<span
						><span
							style="
										display: inline-block;
										width: 12px;
										height: 12px;
										background: color-mix(in srgb, var(--accent2) 20%, transparent);
										border: 1px solid var(--accent2);
										margin-right: 5px;
										vertical-align: middle;
									"
						></span>Just Released (1 frame)</span
					>
				</div>
				<div class="info-panel" style="margin-top: 0.75rem">
					<div
						style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem"
						id="kb-state-display"
					>
						<div>
							<div style="font-size: 10px; color: var(--muted); margin-bottom: 0.25rem">held</div>
							<div style="color: var(--accent); min-height: 1.4em" id="kb-held"></div>
						</div>
						<div>
							<div style="font-size: 10px; color: var(--muted); margin-bottom: 0.25rem">
								just_pressed
							</div>
							<div style="color: var(--accent3); min-height: 1.4em" id="kb-pressed"></div>
						</div>
						<div>
							<div style="font-size: 10px; color: var(--muted); margin-bottom: 0.25rem">
								just_released
							</div>
							<div style="color: var(--accent2); min-height: 1.4em" id="kb-released"></div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="callout gold">
			<div class="callout-label">OS Key Repeat</div>
			When you hold a key, the OS fires repeated keydown events after an initial delay — the same behaviour
			as holding a key in a text editor. For game movement, this is incorrect: you should only count the
			physical key-down transition, not the OS repeats. The fix is the guard<code
				>if key not in self._held</code
			> before adding to just_pressed — ignoring repeated events for already-held keys.
		</div>

		<pre><code
				><span class="cm"># Usage in the game update step</span>
<span class="kw">def</span> <span class="fn">update</span>(player, inp, dt):
    <span class="cm"># Continuous movement — uses held()</span>
    <span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str">'LEFT'</span
				>):  player.vx -= ACCEL * dt
    <span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str">'RIGHT'</span
				>): player.vx += ACCEL * dt

    <span class="cm"># One-shot action — uses just_pressed()</span>
    <span class="kw">if</span> inp.<span class="fn">just_pressed</span>(<span class="str"
					>'SPACE'</span
				>) <span class="kw">and</span> player.on_ground:
        player.vy = JUMP_FORCE

    <span class="cm"># Released trigger — uses just_released()</span>
    <span class="kw">if</span> inp.<span class="fn">just_released</span>(<span class="str"
					>'SPACE'</span
				>) <span class="kw">and</span> player.vy &lt; <span class="num">0</span>:
        player.vy *= <span class="num">0.5</span>   <span class="cm"
					># variable-height jump cut</span
				><span class="lang-tag">python</span></code
			></pre>
	</section>

	<!-- ══ 08.03 MOUSE ══ -->
	<section id="mouse" class="section">
		<div class="section-header">
			<span class="section-num">08.03</span>
			<h2 class="section-title">Mouse Input</h2>
		</div>

		<p>
			Mouse input provides four distinct data streams: <em>absolute position</em> in window
			coordinates, <em>delta</em> (movement since last frame), <em>button states</em> (left, right,
			middle — using the same held/pressed/released model as keyboard), and
			<em>scroll wheel</em> delta.
		</p>
		<p>
			Absolute position is used for cursor-based UI and aiming. Delta is used for first-person
			camera rotation — capturing the mouse removes its cursor from the window and gives you raw
			movement data, which you integrate over time to get a camera angle.
		</p>

		<!-- MOUSE DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Mouse State Inspector</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Move, click, and scroll inside the canvas. Every mouse data stream is captured and
					displayed.
				</p>
				<div class="two-col" style="align-items: start">
					<div>
						<canvas id="mouse-canvas" width="380" height="300" style="width: 100%"></canvas>
					</div>
					<div style="display: flex; flex-direction: column; gap: 0.75rem">
						<div class="info-panel">
							<div class="info-row">
								<span class="info-key">position</span><span class="info-val" id="m-pos">(0, 0)</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">delta (this frame)</span><span class="info-val" id="m-delta"
									>(0, 0)</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">left button</span><span class="info-val" id="m-left">up</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">right button</span><span class="info-val" id="m-right"
									>up</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">middle button</span><span class="info-val" id="m-mid"
									>up</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">scroll y</span><span class="info-val" id="m-scroll">0</span>
							</div>
							<div class="info-row">
								<span class="info-key">raw delta (px)</span><span class="info-val" id="m-raw-delta"
									>(0, 0)</span
								>
							</div>
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
								Movement trail
							</div>
							<canvas
								id="movement-canvas"
								width="300"
								height="100"
								style="
											width: 100%;
											border: 1px solid var(--border2);
											background: var(--code-bg);
										"
							></canvas>
						</div>
					</div>
				</div>
			</div>
		</div>

		<pre><code
				><span class="kw">class</span> <span class="fn">MouseState</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self.pos           = (<span class="num">0</span>, <span class="num">0</span>)
        self.delta         = (<span class="num">0</span>, <span class="num">0</span>)   <span
					class="cm"># cleared each frame</span
				>
        self.scroll        = (<span class="num">0</span>, <span class="num">0</span>)   <span
					class="cm"># cleared each frame</span
				>
        self._buttons_held = <span class="fn">set</span>()
        self._just_pressed = <span class="fn">set</span>()
        self._just_released= <span class="fn">set</span>()

    <span class="kw">def</span> <span class="fn">begin_frame</span>(self):
        self.delta  = (<span class="num">0</span>, <span class="num">0</span>)
        self.scroll = (<span class="num">0</span>, <span class="num">0</span>)
        self._just_pressed.<span class="fn">clear</span>()
        self._just_released.<span class="fn">clear</span>()

    <span class="kw">def</span> <span class="fn">on_move</span>(self, x, y, dx, dy):
        self.pos   = (x, y)
        self.delta = (self.delta[<span class="num">0</span>] + dx, self.delta[<span class="num"
					>1</span
				>] + dy)

    <span class="kw">def</span> <span class="fn">on_scroll</span>(self, dx, dy):
        self.scroll = (self.scroll[<span class="num">0</span>] + dx, self.scroll[<span class="num"
					>1</span
				>] + dy)<span class="lang-tag">python</span></code
			></pre>

		<div class="callout blue">
			<div class="callout-label">Mouse Capture</div>
			For first-person or top-down camera control, you typically "capture" or "lock" the mouse:
			<code>pygame.mouse.set_visible(False)</code> and <code>pygame.event.set_grab(True)</code>.
			This hides the OS cursor and prevents it from leaving the window, giving you unbounded delta
			movement. Toggle capture on/off (e.g. with Escape) so players can reach the window chrome.
		</div>
	</section>

	<!-- ══ 08.04 INPUT MAPPING ══ -->
	<section id="mapping" class="section">
		<div class="section-header">
			<span class="section-num">08.04</span>
			<h2 class="section-title">Input Mapping Abstraction</h2>
		</div>

		<p>
			Hard-coding raw key names throughout your game logic is a maintenance trap. If you want to
			change Jump from Space to Z, or add gamepad support, you touch dozens of files. An
			<strong>input map</strong> decouples game actions from physical inputs: the game asks
			<em>"is JUMP pressed?"</em>, and the input map decides which keys or buttons satisfy that.
		</p>

		<pre><code
				><span class="kw">class</span> <span class="fn">InputMap</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        <span class="cm"># Map action name → list of key/button names</span>
        self._bindings = &#123;&#125;

    <span class="kw">def</span> <span class="fn">bind</span>(self, action, *keys):
        self._bindings[action] = <span class="fn">list</span>(keys)

    <span class="kw">def</span> <span class="fn">pressed</span>(self, action, inp):
        <span class="kw">return</span> <span class="fn">any</span>(inp.<span class="fn"
					>just_pressed</span
				>(k) <span class="kw">for</span> k <span class="kw">in</span> self._bindings.<span
					class="fn">get</span
				>(action, []))

    <span class="kw">def</span> <span class="fn">held</span>(self, action, inp):
        <span class="kw">return</span> <span class="fn">any</span>(inp.<span class="fn">held</span
				>(k) <span class="kw">for</span> k <span class="kw">in</span> self._bindings.<span
					class="fn">get</span
				>(action, []))

    <span class="kw">def</span> <span class="fn">released</span>(self, action, inp):
        <span class="kw">return</span> <span class="fn">any</span>(inp.<span class="fn"
					>just_released</span
				>(k) <span class="kw">for</span> k <span class="kw">in</span> self._bindings.<span
					class="fn">get</span
				>(action, []))

<span class="cm"># Setup — only done once</span>
actions = <span class="fn">InputMap</span>()
actions.<span class="fn">bind</span>(<span class="str">'move_left'</span>,  <span class="str"
					>'LEFT'</span
				>, <span class="str">'A'</span>)
actions.<span class="fn">bind</span>(<span class="str">'move_right'</span>, <span class="str"
					>'RIGHT'</span
				>, <span class="str">'D'</span>)
actions.<span class="fn">bind</span>(<span class="str">'jump'</span>,       <span class="str"
					>'SPACE'</span
				>, <span class="str">'W'</span>, <span class="str">'UP'</span>)
actions.<span class="fn">bind</span>(<span class="str">'attack'</span>,     <span class="str"
					>'Z'</span
				>, <span class="str">'LCTRL'</span>)
actions.<span class="fn">bind</span>(<span class="str">'pause'</span>,      <span class="str"
					>'ESCAPE'</span
				>, <span class="str">'P'</span>)

<span class="cm"># Usage in update — clean and rebindable</span>
<span class="kw">if</span> actions.<span class="fn">held</span>(<span class="str">'move_right'</span
				>, inp):
    player.vx += ACCEL * dt
<span class="kw">if</span> actions.<span class="fn">pressed</span>(<span class="str">'jump'</span
				>, inp):
    player.<span class="fn">jump</span>()<span class="lang-tag">python</span></code
			></pre>

		<!-- INPUT MAP BUILDER -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Input Map Builder</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Click bindings to toggle them on/off. Press keys on your keyboard — active actions light
					up green.
				</p>
				<div id="input-map-ui"></div>
				<div
					style="
								margin-top: 1rem;
								padding: 0.75rem;
								background: var(--code-bg);
								border: 1px solid var(--border);
							"
				>
					<div
						style="
									font-size: 10px;
									letter-spacing: 0.15em;
									text-transform: uppercase;
									color: var(--muted);
									margin-bottom: 0.5rem;
								"
					>
						Active actions this frame
					</div>
					<div
						style="display: flex; gap: 0.5rem; flex-wrap: wrap; min-height: 24px"
						id="active-actions"
					></div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ 08.05 SIMULTANEOUS ══ -->
	<section id="simultaneous" class="section">
		<div class="section-header">
			<span class="section-num">08.05</span>
			<h2 class="section-title">Handling Simultaneous Inputs</h2>
		</div>

		<p>
			When multiple direction keys are held at once, naïve code produces incorrect results. Pressing
			LEFT and RIGHT simultaneously can zero out velocity (cancellation), double it (addition), or
			cause undefined behaviour. Each case needs a deliberate policy.
		</p>

		<pre><code
				><span class="cm"># Naïve — gives zero velocity when both left and right held</span>
<span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str">'LEFT'</span
				>):  vx -= SPEED
<span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str">'RIGHT'</span
				>): vx += SPEED

<span class="cm"># Policy A: last key wins — most game-feel-correct option</span>
<span class="kw">def</span> <span class="fn">axis</span>(neg_key, pos_key, inp, pressed_history):
    <span class="kw">if</span> inp.<span class="fn">held</span>(neg_key) <span class="kw">and</span
				> inp.<span class="fn">held</span>(pos_key):
        <span class="cm"># return the direction of whichever was pressed most recently</span>
        <span class="kw">return</span> -<span class="num">1</span> <span class="kw">if</span
				> pressed_history[-<span class="num">1</span>] == neg_key <span class="kw">else</span> <span
					class="num">1</span
				>
    <span class="kw">elif</span> inp.<span class="fn">held</span>(neg_key):  <span class="kw"
					>return</span
				> -<span class="num">1</span>
    <span class="kw">elif</span> inp.<span class="fn">held</span>(pos_key):  <span class="kw"
					>return</span
				>  <span class="num">1</span>
    <span class="kw">return</span> <span class="num">0</span>

<span class="cm"># Policy B: neutral — cancel to zero</span>
h = (<span class="num">-1</span> <span class="kw">if</span> inp.<span class="fn">held</span>(<span
					class="str">'LEFT'</span
				>) <span class="kw">else</span> <span class="num">0</span>) + (<span class="num">1</span
				> <span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str"
					>'RIGHT'</span
				>) <span class="kw">else</span> <span class="num">0</span>)

<span class="cm"># Policy C: normalize diagonal speed for 8-directional movement</span>
<span class="kw">import</span> math
dx = (<span class="num">1</span> <span class="kw">if</span> inp.<span class="fn">held</span>(<span
					class="str">'RIGHT'</span
				>) <span class="kw">else</span> <span class="num">0</span>) - (<span class="num">1</span
				> <span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str">'LEFT'</span
				>) <span class="kw">else</span> <span class="num">0</span>)
dy = (<span class="num">1</span> <span class="kw">if</span> inp.<span class="fn">held</span>(<span
					class="str">'DOWN'</span
				>)  <span class="kw">else</span> <span class="num">0</span>) - (<span class="num">1</span
				> <span class="kw">if</span> inp.<span class="fn">held</span>(<span class="str">'UP'</span
				>)   <span class="kw">else</span> <span class="num">0</span>)
length = math.<span class="fn">sqrt</span>(dx*dx + dy*dy) <span class="kw">or</span> <span
					class="num">1</span
				>
dx, dy = dx/length, dy/length   <span class="cm"># diagonal speed = cardinal speed</span><span
					class="lang-tag">python</span
				></code
			></pre>

		<!-- SIMULTANEOUS INPUT DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Simultaneous Input Policies</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Hold multiple arrow keys. Toggle between the three conflict resolution policies to feel
					the difference.
				</p>
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button
						class="btn active"
						id="pol-cancel"
						onclick={(e) => {
							window.setPolicy('cancel', e.currentTarget);
						}}
					>
						Neutral / Cancel
					</button>
					<button
						class="btn"
						id="pol-last"
						onclick={(e) => {
							window.setPolicy('last', e.currentTarget);
						}}
					>
						Last Key Wins
					</button>
					<button
						class="btn"
						id="pol-norm"
						onclick={(e) => {
							window.setPolicy('norm', e.currentTarget);
						}}
					>
						Normalized Diagonal
					</button>
				</div>
				<canvas
					id="sim-canvas"
					width="860"
					height="200"
					style="width: 100%; border: 1px solid var(--border2); background: #080306"
				></canvas>
				<div
					style="
								margin-top: 0.75rem;
								font-size: 12px;
								display: flex;
								gap: 1.5rem;
								flex-wrap: wrap;
							"
					id="sim-info"
				></div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- ══ 08.06 PRACTICAL ══ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">08.06</span>
			<h2 class="section-title">Practical Work</h2>
		</div>

		<p>
			The interactive scene below puts all input concepts together: accelerated movement with
			delta-time, jump with variable height, mouse-aimed projectile, and a collectible object. Click
			the canvas and use your keyboard to play.
		</p>

		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Full Input Test Scene</div>
				<span class="demo-badge a">LIVE</span>
			</div>
			<div class="demo-body">
				<div class="two-col" style="align-items: start">
					<div>
						<canvas id="game-canvas" width="500" height="380" style="width: 100%"></canvas>
						<div class="game-hint" id="game-hint">
							▶ Click canvas to activate · WASD/Arrows = move · Space = jump · Mouse = aim · Click =
							shoot
						</div>
					</div>
					<div style="display: flex; flex-direction: column; gap: 0.75rem">
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
								Physics
							</div>
							<div class="slider-row">
								<label for="dummy">Acceleration</label><input
									type="range"
									id="g-accel"
									min="100"
									max="1200"
									value="600"
								/><span class="slider-val" id="g-accel-val">600</span>
							</div>
							<div class="slider-row">
								<label for="dummy">Friction</label><input
									type="range"
									id="g-friction"
									min="1"
									max="20"
									value="8"
								/><span class="slider-val" id="g-friction-val">8</span>
							</div>
							<div class="slider-row">
								<label for="dummy">Jump force</label><input
									type="range"
									id="g-jump"
									min="200"
									max="800"
									value="450"
								/><span class="slider-val" id="g-jump-val">450</span>
							</div>
							<div class="slider-row">
								<label for="dummy">Gravity</label><input
									type="range"
									id="g-gravity"
									min="100"
									max="1200"
									value="600"
								/><span class="slider-val" id="g-gravity-val">600</span>
							</div>
						</div>
						<div class="info-panel" id="game-stats">
							<div class="info-row">
								<span class="info-key">position</span><span class="info-val" id="gs-pos">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">velocity</span><span class="info-val" id="gs-vel">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">on_ground</span><span class="info-val" id="gs-ground">—</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">jump_held</span><span class="info-val" id="gs-jump">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">facing</span><span class="info-val" id="gs-facing"
									>right</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">score</span><span class="info-val" id="gs-score">0</span>
							</div>
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
								Controls summary
							</div>
							<div style="font-size: 11px; color: var(--muted); line-height: 2">
								<div><span style="color: var(--accent)">A / ← →</span> Move left/right</div>
								<div>
									<span style="color: var(--accent)">W / Space / ↑</span> Jump (hold for higher)
								</div>
								<div><span style="color: var(--accent)">Mouse</span> Aim direction</div>
								<div><span style="color: var(--accent)">Click</span> Fire projectile</div>
								<div><span style="color: var(--accent)">R</span> Reset scene</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- ══ ASSESSMENT ══ -->
	<section id="assessment" class="assess-section">
		<div class="assess-header">Assessment · Input Behaviour Analysis</div>
		<div class="assess-sub">Read each scenario and select the correct outcome or fix.</div>
		<div id="assess-container"></div>
		<div class="assess-score" id="assess-score">
			<div class="assess-score-num" id="assess-score-num">0/5</div>
			<div style="font-size: 12px; color: var(--muted); margin-top: 0.25rem">
				Module 08 complete. Proceed to Module 09 when ready.
			</div>
		</div>
	</section>

	<div class="nav-links">
		<a href="." class="prev-link">← 07 · Time and Animation</a>
		<a class="next-module" href=".">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">09 · Collisions and Simple Physics</div>
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
		color: #3a1828;
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
	.callout.blue {
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 5%, var(--surface));
	}
	.callout.green {
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 5%, var(--surface));
	}
	.callout.gold {
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
	.callout.blue .callout-label {
		color: var(--accent2);
	}
	.callout.green .callout-label {
		color: var(--accent3);
	}
	.callout.gold .callout-label {
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
		color: var(--accent3);
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
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
		min-width: 100px;
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
	.btn.b:hover,
	.btn.b.active {
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
	.info-val.hot {
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

	/* Key visualizer */
	.keyboard-vis {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin: 1rem 0;
	}
	.key-row {
		display: flex;
		gap: 4px;
	}
	.key {
		min-width: 36px;
		height: 36px;
		border: 1px solid var(--border2);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 10px;
		font-family: 'IBM Plex Mono', monospace;
		color: var(--muted);
		transition: all 0.08s;
		border-radius: 2px;
		padding: 0 6px;
		user-select: none;
	}
	.key.held {
		background: var(--accent);
		border-color: var(--accent);
		color: #000;
		font-weight: 700;
		transform: translateY(2px);
		box-shadow: 0 0 8px color-mix(in srgb, var(--accent) 40%, transparent);
	}
	.key.just-pressed {
		background: color-mix(in srgb, var(--accent) 60%, transparent);
		border-color: var(--accent);
		color: var(--accent);
	}
	.key.just-released {
		background: color-mix(in srgb, var(--accent2) 20%, transparent);
		border-color: var(--accent2);
		color: var(--accent2);
	}
	.key.wide {
		min-width: 60px;
	}
	.key.wider {
		min-width: 80px;
	}
	.key.space {
		flex: 1;
	}

	/* Event log */
	.event-log {
		background: var(--code-bg);
		border: 1px solid var(--border);
		height: 120px;
		overflow-y: auto;
		font-size: 11px;
		padding: 0.5rem;
	}
	.event-line {
		padding: 1px 0;
		border-bottom: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
	}
	.event-line.press {
		color: var(--accent);
	}
	.event-line.release {
		color: var(--accent2);
	}
	.event-line.mouse {
		color: var(--accent4);
	}
	.event-line.scroll {
		color: var(--accent3);
	}

	/* Mouse tracker */
	#mouse-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
		cursor: crosshair;
	}
	#movement-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
	}

	/* Input map builder */
	.action-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid var(--border);
	}
	.action-row:last-child {
		border-bottom: none;
	}
	.action-name {
		font-size: 12px;
		min-width: 100px;
		color: var(--accent);
	}
	.action-bindings {
		display: flex;
		gap: 0.4rem;
		flex-wrap: wrap;
	}
	.binding-chip {
		font-size: 11px;
		padding: 2px 8px;
		border: 1px solid var(--border2);
		color: var(--muted);
		cursor: pointer;
		transition: all 0.12s;
	}
	.binding-chip:hover {
		border-color: var(--accent);
		color: var(--accent);
	}
	.binding-chip.active-bind {
		border-color: var(--accent3);
		color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
	}
	.add-bind {
		font-size: 11px;
		padding: 2px 8px;
		border: 1px dashed var(--border2);
		color: var(--muted);
		cursor: pointer;
	}
	.add-bind:hover {
		border-color: var(--accent4);
		color: var(--accent4);
	}

	/* Game canvas */
	#game-canvas {
		border: 1px solid var(--border2);
		background: #080306;
		cursor: none;
		touch-action: none;
	}
	.game-hint {
		font-size: 11px;
		color: var(--muted);
		margin-top: 0.5rem;
		letter-spacing: 0.05em;
	}

	/* Assessment */
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
	.challenge-box {
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 1.5rem;
		margin: 1.5rem 0;
	}
	.challenge-num {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--accent2);
		margin-bottom: 0.75rem;
	}
	.challenge-q {
		font-size: 13px;
		color: #fff;
		margin-bottom: 1rem;
	}
	.ch-options {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	.ch-option {
		padding: 0.5rem 1rem;
		border: 1px solid var(--border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		font-family: 'IBM Plex Mono', monospace;
		user-select: none;
	}
	.ch-option:hover {
		border-color: var(--border2);
		background: var(--raised);
	}
	.ch-option.correct {
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 10%, transparent);
		color: var(--accent3);
	}
	.ch-option.wrong {
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 10%, transparent);
		color: var(--accent);
	}
	.ch-option.disabled {
		pointer-events: none;
	}
	.ch-feedback {
		font-size: 12px;
		margin-top: 0.75rem;
		min-height: 1.4em;
		color: var(--muted);
	}
	.ch-feedback.ok {
		color: var(--accent3);
	}
	.ch-feedback.bad {
		color: var(--accent);
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
		border-color: var(--accent4);
		color: var(--accent4);
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
