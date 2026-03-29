<script>
	/* eslint-disable @typescript-eslint/no-unused-vars */
	import { onMount } from 'svelte';

	onMount(() => {
		/* ════════════════════════════
   UTILS
════════════════════════════ */
		const C = {
			gold: '#f0a830',
			coral: '#e8553a',
			mint: '#4ecbb4',
			lav: '#c4a8f0',
			muted: '#7a6e5e',
			border: '#28221a',
			border2: '#3c342a',
			raised: '#1c1812',
			surface: '#131009',
			bg: '#0b0906',
			dim: '#4a4035',
			text: '#ede5d4'
		};
		const lerp = (a, b, t) => a + (b - a) * t;
		const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
		const eio = (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t);
		const eout = (t) => 1 - Math.pow(1 - t, 3);
		const deg2rad = (d) => (d * Math.PI) / 180;
		const rad2deg = (r) => (r * 180) / Math.PI;

		function lerpAngle(a, b, t) {
			let d = b - a;
			while (d > Math.PI) d -= Math.PI * 2;
			while (d < -Math.PI) d += Math.PI * 2;
			return a + d * t;
		}

		/* ════════════════════════════
   DEMO 6.1 — FK HIERARCHY
════════════════════════════ */
		const BONE_DEFS = [
			{
				id: 'root',
				name: 'Root',
				parent: null,
				length: 0,
				restAngle: 0,
				angle: 0,
				color: C.gold,
				info: 'Root bone — the origin of the entire hierarchy. Moving the root moves the entire character.'
			},
			{
				id: 'spine',
				name: 'Spine',
				parent: 'root',
				length: 68,
				restAngle: -90,
				angle: 0,
				color: C.coral,
				info: 'Spine — child of Root. Tilting the spine tilts the whole upper body including arms and head.'
			},
			{
				id: 'head',
				name: 'Head',
				parent: 'spine',
				length: 32,
				restAngle: 0,
				angle: 0,
				color: C.lav,
				info: 'Head — child of Spine. Rotate it independently of the body for nods, turns, and tilts.'
			},
			{
				id: 'upperL',
				name: 'L. Upper Arm',
				parent: 'spine',
				length: 48,
				restAngle: 60,
				angle: 0,
				color: C.mint,
				info: 'Left Upper Arm — child of Spine. Swings from the shoulder joint. Parent rotates drive it.'
			},
			{
				id: 'lowerL',
				name: 'L. Forearm',
				parent: 'upperL',
				length: 40,
				restAngle: 0,
				angle: 0,
				color: '#3aab94',
				info: 'Left Forearm — child of Upper Arm. Bends at the elbow. Can only flex, not extend past straight.'
			},
			{
				id: 'upperR',
				name: 'R. Upper Arm',
				parent: 'spine',
				length: 48,
				restAngle: 120,
				angle: 0,
				color: C.mint,
				info: 'Right Upper Arm — mirrors the left. Both arms share Spine as their parent.'
			},
			{
				id: 'lowerR',
				name: 'R. Forearm',
				parent: 'upperR',
				length: 40,
				restAngle: 0,
				angle: 0,
				color: '#3aab94',
				info: 'Right Forearm — child of Right Upper Arm. Independently bends.'
			},
			{
				id: 'thighL',
				name: 'L. Thigh',
				parent: 'root',
				length: 52,
				restAngle: 80,
				angle: 0,
				color: '#d09020',
				info: 'Left Thigh — child of Root (hip). Part of the leg chain. Drives the shin.'
			},
			{
				id: 'shinL',
				name: 'L. Shin',
				parent: 'thighL',
				length: 46,
				restAngle: 0,
				angle: 0,
				color: '#a07010',
				info: 'Left Shin — child of Left Thigh. Bends at the knee. IK is often used for legs.'
			},
			{
				id: 'thighR',
				name: 'R. Thigh',
				parent: 'root',
				length: 52,
				restAngle: 100,
				angle: 0,
				color: '#d09020',
				info: 'Right Thigh — mirrors left. Root is the shared parent.'
			},
			{
				id: 'shinR',
				name: 'R. Shin',
				parent: 'thighR',
				length: 46,
				restAngle: 0,
				angle: 0,
				color: '#a07010',
				info: 'Right Shin — child of Right Thigh.'
			}
		];

		const fkCanvas = document.getElementById('fkCanvas');
		const fkCtx = fkCanvas.getContext('2d');
		const FKW = fkCanvas.width,
			FKH = fkCanvas.height;
		const FK_ORIGIN = { x: FKW / 2, y: FKH * 0.38 };

		let selectedBone = null;
		let fkDragging = false,
			fkDragStartX = 0,
			fkDragStartAngle = 0;
		let fkAnimating = false,
			fkAnimRaf = null,
			fkAnimLastTs = null,
			fkAnimT = 0;

		// Compute world positions of all bones
		function computeFK() {
			const worldPos = {};
			const worldAngle = {};
			BONE_DEFS.forEach((b) => {
				if (!b.parent) {
					worldPos[b.id] = { x: FK_ORIGIN.x, y: FK_ORIGIN.y };
					worldAngle[b.id] = b.angle;
				} else {
					const parentPos = worldPos[b.parent];
					const parentBone = BONE_DEFS.find((x) => x.id === b.parent);
					const parentWorldAngle = worldAngle[b.parent];
					const effectiveAngle = parentWorldAngle + deg2rad(b.restAngle);
					worldPos[b.id] = {
						x:
							parentPos.x +
							Math.cos(effectiveAngle + deg2rad(b.angle * (b.parent === 'root' ? 1 : 1))) *
								parentBone.length,
						y:
							parentPos.y +
							Math.sin(effectiveAngle + deg2rad(b.angle * (b.parent === 'root' ? 1 : 1))) *
								parentBone.length
					};
					worldAngle[b.id] = effectiveAngle + deg2rad(b.angle);
				}
			});
			return { worldPos, worldAngle };
		}

		function computeBoneEndWorld(boneId, worldPos, worldAngle) {
			const b = BONE_DEFS.find((x) => x.id === boneId);
			const start = worldPos[boneId];
			const angle = worldAngle[boneId];
			return { x: start.x + Math.cos(angle) * b.length, y: start.y + Math.sin(angle) * b.length };
		}

		function drawFK() {
			fkCtx.clearRect(0, 0, FKW, FKH);
			const { worldPos, worldAngle } = computeFK();

			// Ground
			fkCtx.strokeStyle = C.border2;
			fkCtx.lineWidth = 1;
			fkCtx.beginPath();
			fkCtx.moveTo(10, FKH - 24);
			fkCtx.lineTo(FKW - 10, FKH - 24);
			fkCtx.stroke();

			BONE_DEFS.forEach((b) => {
				if (b.length === 0) return;
				const start = worldPos[b.id];
				const end = computeBoneEndWorld(b.id, worldPos, worldAngle);
				const isSelected = selectedBone === b.id;
				const thickness = isSelected ? 5 : 3;

				// Bone body
				fkCtx.strokeStyle = isSelected ? '#fff' : b.color + 'cc';
				fkCtx.lineWidth = thickness;
				fkCtx.lineCap = 'round';
				fkCtx.beginPath();
				fkCtx.moveTo(start.x, start.y);
				fkCtx.lineTo(end.x, end.y);
				fkCtx.stroke();

				// Tip dot
				fkCtx.fillStyle = isSelected ? '#fff' : b.color;
				fkCtx.beginPath();
				fkCtx.arc(end.x, end.y, isSelected ? 6 : 4, 0, Math.PI * 2);
				fkCtx.fill();

				// Joint dot
				fkCtx.fillStyle = isSelected ? C.coral : b.color + '99';
				fkCtx.beginPath();
				fkCtx.arc(start.x, start.y, isSelected ? 7 : 5, 0, Math.PI * 2);
				fkCtx.fill();
			});

			// Selected bone rotation arc
			if (selectedBone) {
				const b = BONE_DEFS.find((x) => x.id === selectedBone);
				const start = worldPos[selectedBone];
				const angle = worldAngle[selectedBone];
				fkCtx.strokeStyle = C.coral + '55';
				fkCtx.lineWidth = 1.5;
				fkCtx.beginPath();
				fkCtx.arc(start.x, start.y, 28, angle - Math.PI / 3, angle + Math.PI / 3);
				fkCtx.stroke();
			}
		}

		// Build hierarchy tree
		function buildHierTree() {
			const tree = document.getElementById('hierTree');
			tree.innerHTML = '';
			function renderNode(parentId, indent) {
				const children = BONE_DEFS.filter((b) => b.parent === parentId);
				children.forEach((b) => {
					const row = document.createElement('div');
					const wrap = document.createElement('div');
					wrap.style.paddingLeft = indent * 14 + 'px';
					const node = document.createElement('div');
					node.className = 'hier-node' + (selectedBone === b.id ? ' selected' : '');
					node.innerHTML = `<span class="hier-icon" style="color:${b.color}">⬥</span><span class="hier-name">${b.name}</span><span class="hier-type">${b.length > 0 ? 'Bone' : 'Root'}</span>`;
					node.onclick = () => {
						selectedBone = b.id;
						document.getElementById('hierInfo').textContent = b.info;
						buildHierTree();
						drawFK();
						document.getElementById('selectedBoneName').textContent = b.name;
					};
					wrap.appendChild(node);
					row.appendChild(wrap);
					tree.appendChild(row);
					renderNode(b.id, indent + 1);
				});
			}
			renderNode(null, 0);
		}
		buildHierTree();
		drawFK();

		// FK drag
		function getFKPos(e) {
			const r = fkCanvas.getBoundingClientRect(),
				sc = fkCanvas.width / r.width;
			const raw = e.touches ? e.touches[0] : e;
			return { x: (raw.clientX - r.left) * sc, y: (raw.clientY - r.top) * sc };
		}
		fkCanvas.addEventListener('mousedown', (e) => {
			const pos = getFKPos(e);
			const { worldPos } = computeFK();
			let hit = null,
				minDist = Infinity;
			BONE_DEFS.forEach((b) => {
				if (b.length === 0) return;
				const { x, y } = worldPos[b.id];
				const d = Math.hypot(pos.x - x, pos.y - y);
				if (d < 20 && d < minDist) {
					minDist = d;
					hit = b.id;
				}
			});
			if (hit) {
				selectedBone = hit;
				fkDragging = true;
				fkDragStartX = pos.x;
				fkDragStartAngle = BONE_DEFS.find((b) => b.id === hit).angle;
				buildHierTree();
				const b = BONE_DEFS.find((x) => x.id === hit);
				document.getElementById('hierInfo').textContent = b.info;
				document.getElementById('selectedBoneName').textContent = b.name;
			}
		});
		fkCanvas.addEventListener(
			'touchstart',
			(e) => {
				e.preventDefault();
				fkCanvas.dispatchEvent(
					new MouseEvent('mousedown', {
						clientX: e.touches[0].clientX,
						clientY: e.touches[0].clientY
					})
				);
			},
			{ passive: false }
		);

		window.addEventListener('mousemove', (e) => {
			if (!fkDragging || !selectedBone) return;
			const pos = getFKPos(e);
			const dx = pos.x - fkDragStartX;
			const b = BONE_DEFS.find((x) => x.id === selectedBone);
			b.angle = fkDragStartAngle + dx * 0.8;
			drawFK();
			document.getElementById('selectedBoneAngle').textContent = b.angle.toFixed(1) + '°';
		});
		window.addEventListener('mouseup', () => {
			fkDragging = false;
		});

		function resetFK() {
			BONE_DEFS.forEach((b) => (b.angle = 0));
			selectedBone = null;
			buildHierTree();
			drawFK();
			document.getElementById('selectedBoneName').textContent = 'none';
			document.getElementById('selectedBoneAngle').textContent = '—';
		}

		// Idle animation
		const FK_IDLE = [
			{
				spine: 5,
				head: -8,
				upperL: -25,
				lowerL: 15,
				upperR: 20,
				lowerR: 10,
				thighL: -8,
				shinL: 5,
				thighR: 10,
				shinR: 8
			},
			{
				spine: -3,
				head: 5,
				upperL: 20,
				lowerL: 8,
				upperR: -20,
				lowerR: 18,
				thighL: 10,
				shinL: 8,
				thighR: -6,
				shinR: 4
			}
		];
		function toggleFKAnim(btn) {
			fkAnimating = !fkAnimating;
			btn.textContent = fkAnimating ? '⏸ Stop' : '▶ Idle Animation';
			btn.classList.toggle('active', fkAnimating);
			if (fkAnimating) {
				fkAnimLastTs = null;
				fkAnimRaf = requestAnimationFrame(fkIdleTick);
			} else {
				cancelAnimationFrame(fkAnimRaf);
				BONE_DEFS.forEach((b) => (b.angle = 0));
				drawFK();
			}
		}
		function fkIdleTick(ts) {
			if (!fkAnimLastTs) fkAnimLastTs = ts;
			fkAnimT += ((ts - fkAnimLastTs) / 1000) * 0.5;
			fkAnimLastTs = ts;
			if (fkAnimT > 1) fkAnimT -= 1;
			const t = fkAnimT < 0.5 ? eio(fkAnimT * 2) : eio((1 - fkAnimT) * 2);
			const pA = FK_IDLE[0],
				pB = FK_IDLE[1];
			const map = {
				spine: 'spine',
				head: 'head',
				upperL: 'upperL',
				lowerL: 'lowerL',
				upperR: 'upperR',
				lowerR: 'lowerR',
				thighL: 'thighL',
				shinL: 'shinL',
				thighR: 'thighR',
				shinR: 'shinR'
			};
			Object.entries(map).forEach(([boneId, key]) => {
				const b = BONE_DEFS.find((x) => x.id === boneId);
				if (b) b.angle = lerp(pA[key] || 0, pB[key] || 0, t);
			});
			drawFK();
			fkAnimRaf = requestAnimationFrame(fkIdleTick);
		}

		/* ════════════════════════════
   DEMO 6.2 — FK vs IK
════════════════════════════ */
		// ── FK PANEL ──
		const fkikFKCanvas = document.getElementById('fkikFKCanvas');
		const fkikFKCtx = fkikFKCanvas.getContext('2d');
		const FKFKW = fkikFKCanvas.width,
			FKFKH = fkikFKCanvas.height;
		const FKFK_SX = FKFKW * 0.35,
			FKFK_SY = FKFKH * 0.2;
		const L1 = 80,
			L2 = 65,
			L3 = 40; // upper arm, forearm, hand

		function drawFKPanel(shoulderDeg, elbowDeg, wristDeg) {
			fkikFKCtx.clearRect(0, 0, FKFKW, FKFKH);
			const sx = FKFK_SX,
				sy = FKFK_SY;
			const sa = deg2rad(-shoulderDeg - 90);
			const ex = sx + Math.cos(sa) * L1,
				ey = sy + Math.sin(sa) * L1;
			const ea = sa + deg2rad(elbowDeg);
			const wx = ex + Math.cos(ea) * L2,
				wy = ey + Math.sin(ea) * L2;
			const wa = ea + deg2rad(wristDeg);
			const hx = wx + Math.cos(wa) * L3,
				hy = wy + Math.sin(wa) * L3;

			// Bones
			[
				[sx, sy, ex, ey, C.gold, 'Shoulder'],
				[ex, ey, wx, wy, C.coral, 'Elbow'],
				[wx, wy, hx, hy, C.mint, 'Wrist']
			].forEach(([x1, y1, x2, y2, col, label]) => {
				fkikFKCtx.strokeStyle = col + 'cc';
				fkikFKCtx.lineWidth = 12;
				fkikFKCtx.lineCap = 'round';
				fkikFKCtx.beginPath();
				fkikFKCtx.moveTo(x1, y1);
				fkikFKCtx.lineTo(x2, y2);
				fkikFKCtx.stroke();
				// Joint dot
				fkikFKCtx.fillStyle = col;
				fkikFKCtx.beginPath();
				fkikFKCtx.arc(x1, y1, 7, 0, Math.PI * 2);
				fkikFKCtx.fill();
				// Label
				fkikFKCtx.fillStyle = col + '99';
				fkikFKCtx.font = `8px 'JetBrains Mono'`;
				fkikFKCtx.textAlign = 'center';
				fkikFKCtx.fillText(label, (x1 + x2) / 2 + 12, (y1 + y2) / 2 - 8);
			});
			// End effector (hand)
			fkikFKCtx.fillStyle = '#fff';
			fkikFKCtx.beginPath();
			fkikFKCtx.arc(hx, hy, 8, 0, Math.PI * 2);
			fkikFKCtx.fill();
			// Shoulder pin
			fkikFKCtx.fillStyle = C.gold;
			fkikFKCtx.strokeStyle = C.bg;
			fkikFKCtx.lineWidth = 2;
			fkikFKCtx.beginPath();
			fkikFKCtx.arc(sx, sy, 9, 0, Math.PI * 2);
			fkikFKCtx.fill();
			fkikFKCtx.stroke();
		}

		['fkShoulder', 'fkElbow', 'fkWrist'].forEach((id) => {
			document.getElementById(id).oninput = function () {
				const key = id === 'fkShoulder' ? 'Shoulder' : id === 'fkElbow' ? 'Elbow' : 'Wrist';
				document.getElementById(id + 'Val').textContent = this.value + '°';
				renderFKPanel();
			};
		});
		function renderFKPanel() {
			drawFKPanel(
				parseInt(document.getElementById('fkShoulder').value),
				parseInt(document.getElementById('fkElbow').value),
				parseInt(document.getElementById('fkWrist').value)
			);
		}
		renderFKPanel();

		// ── IK PANEL ──
		const fkikIKCanvas = document.getElementById('fkikIKCanvas');
		const fkikIKCtx = fkikIKCanvas.getContext('2d');
		const FKIKW = fkikIKCanvas.width,
			FKIKH = fkikIKCanvas.height;
		const IK_SX = FKIKW * 0.35,
			IK_SY = FKIKH * 0.2;
		let ikTarget = { x: IK_SX + L1 + L2 * 0.7, y: IK_SY + 50 };
		let ikDragging = false;

		function solveIK2Bone(sx, sy, tx, ty, l1, l2) {
			const dx = tx - sx,
				dy = ty - sy;
			const dist = clamp(Math.hypot(dx, dy), Math.abs(l1 - l2) + 1, l1 + l2 - 1);
			const targetAngle = Math.atan2(dy, dx);
			const cosA = (dist * dist + l1 * l1 - l2 * l2) / (2 * dist * l1);
			const a1 = Math.acos(clamp(cosA, -1, 1));
			const elbowAngle = targetAngle - a1;
			const ex = sx + Math.cos(elbowAngle) * l1;
			const ey = sy + Math.sin(elbowAngle) * l1;
			return { ex, ey, elbowAngle };
		}

		function drawIKPanel() {
			fkikIKCtx.clearRect(0, 0, FKIKW, FKIKH);
			const sx = IK_SX,
				sy = IK_SY;
			const { ex, ey } = solveIK2Bone(sx, sy, ikTarget.x, ikTarget.y, L1, L2);

			// Reach radius guide
			fkikIKCtx.strokeStyle = C.border + '88';
			fkikIKCtx.lineWidth = 1;
			fkikIKCtx.setLineDash([3, 4]);
			fkikIKCtx.beginPath();
			fkikIKCtx.arc(sx, sy, L1 + L2, 0, Math.PI * 2);
			fkikIKCtx.stroke();
			fkikIKCtx.setLineDash([]);

			// Bones
			fkikIKCtx.strokeStyle = C.mint + 'cc';
			fkikIKCtx.lineWidth = 12;
			fkikIKCtx.lineCap = 'round';
			fkikIKCtx.beginPath();
			fkikIKCtx.moveTo(sx, sy);
			fkikIKCtx.lineTo(ex, ey);
			fkikIKCtx.stroke();
			fkikIKCtx.strokeStyle = C.lav + 'cc';
			fkikIKCtx.beginPath();
			fkikIKCtx.moveTo(ex, ey);
			fkikIKCtx.lineTo(ikTarget.x, ikTarget.y);
			fkikIKCtx.stroke();

			// Joints
			[
				[sx, sy, C.mint, 'Shoulder'],
				[ex, ey, C.lav, 'Elbow']
			].forEach(([x, y, col, label]) => {
				fkikIKCtx.fillStyle = col;
				fkikIKCtx.beginPath();
				fkikIKCtx.arc(x, y, 7, 0, Math.PI * 2);
				fkikIKCtx.fill();
				fkikIKCtx.fillStyle = col + '88';
				fkikIKCtx.font = `8px 'JetBrains Mono'`;
				fkikIKCtx.textAlign = 'center';
				fkikIKCtx.fillText(label, x, y - 12);
			});

			// IK target
			fkikIKCtx.fillStyle = C.mint;
			fkikIKCtx.strokeStyle = C.bg;
			fkikIKCtx.lineWidth = 2;
			fkikIKCtx.save();
			fkikIKCtx.translate(ikTarget.x, ikTarget.y);
			fkikIKCtx.rotate(Math.PI / 4);
			fkikIKCtx.beginPath();
			fkikIKCtx.rect(-8, -8, 16, 16);
			fkikIKCtx.fill();
			fkikIKCtx.stroke();
			fkikIKCtx.restore();
			fkikIKCtx.fillStyle = C.mint;
			fkikIKCtx.font = `8px 'JetBrains Mono'`;
			fkikIKCtx.textAlign = 'center';
			fkikIKCtx.fillText('Target', ikTarget.x, ikTarget.y + 20);

			// Shoulder pin
			fkikIKCtx.fillStyle = C.gold;
			fkikIKCtx.strokeStyle = C.bg;
			fkikIKCtx.lineWidth = 2;
			fkikIKCtx.beginPath();
			fkikIKCtx.arc(sx, sy, 9, 0, Math.PI * 2);
			fkikIKCtx.fill();
			fkikIKCtx.stroke();

			const dist = Math.hypot(ikTarget.x - IK_SX, ikTarget.y - IK_SY).toFixed(0);
			document.getElementById('ikReadout').innerHTML =
				`Target at (${Math.round(ikTarget.x - IK_SX)}, ${Math.round(ikTarget.y - IK_SY)}) — reach: ${dist}px<br><span style="color:var(--mint)">◆ Drag the target</span> anywhere within the circle`;
		}

		function getIKPos(e) {
			const r = fkikIKCanvas.getBoundingClientRect(),
				sc = fkikIKCanvas.width / r.width;
			const raw = e.touches ? e.touches[0] : e;
			return { x: (raw.clientX - r.left) * sc, y: (raw.clientY - r.top) * sc };
		}
		fkikIKCanvas.addEventListener('mousedown', (e) => {
			const p = getIKPos(e);
			if (Math.hypot(p.x - ikTarget.x, p.y - ikTarget.y) < 20) ikDragging = true;
		});
		fkikIKCanvas.addEventListener(
			'touchstart',
			(e) => {
				e.preventDefault();
				const p = getIKPos(e);
				if (Math.hypot(p.x - ikTarget.x, p.y - ikTarget.y) < 28) ikDragging = true;
			},
			{ passive: false }
		);
		window.addEventListener('mousemove', (e) => {
			if (!ikDragging) return;
			const p = getIKPos(e);
			ikTarget = { x: p.x, y: p.y };
			drawIKPanel();
		});
		window.addEventListener(
			'touchmove',
			(e) => {
				if (!ikDragging) return;
				e.preventDefault();
				const p = getIKPos(e);
				ikTarget = { x: p.x, y: p.y };
				drawIKPanel();
			},
			{ passive: false }
		);
		window.addEventListener('mouseup', () => {
			ikDragging = false;
		});
		window.addEventListener('touchend', () => {
			ikDragging = false;
		});
		drawIKPanel();

		/* ════════════════════════════
   DEMO 6.3 — BONE WEIGHTING
════════════════════════════ */
		const weightCanvas = document.getElementById('weightCanvas');
		const wctx = weightCanvas.getContext('2d');
		const WW = weightCanvas.width,
			WH = weightCanvas.height;
		let weightBone = 'upper',
			weightBend = 60;

		const WEIGHT_DESCS = {
			upper: `<span style="color:var(--coral)">Upper Arm bone:</span> vertices at the shoulder have full weight here. Vertices near the elbow are shared with the Lower Arm bone, creating smooth blending.`,
			lower: `<span style="color:var(--coral)">Lower Arm bone:</span> vertices around the elbow region are split between Upper and Lower arm. Near the wrist they shift to full Lower Arm control.`,
			hand: `<span style="color:var(--coral)">Hand bone:</span> only the finger and palm vertices belong here. Everything above the wrist is controlled by the Forearm.`
		};

		function selectWeightBone(btn, bone) {
			weightBone = bone;
			document
				.querySelectorAll('#weightBoneSelector .btn')
				.forEach((b) => b.classList.remove('active'));
			btn.classList.add('active');
			document.getElementById('weightDesc').innerHTML = WEIGHT_DESCS[bone];
			renderWeight();
		}

		function getWeight(segY, totalH) {
			// segY: 0=shoulder, 1=wrist
			const t = segY;
			const upper = t < 0.4 ? 1 : t < 0.65 ? lerp(1, 0, (t - 0.4) / 0.25) : 0;
			const lower =
				t < 0.4
					? 0
					: t < 0.65
						? lerp(0, 0.8, (t - 0.4) / 0.25)
						: t < 0.85
							? lerp(0.8, 1, (t - 0.65) / 0.2)
							: 1;
			const hand = t < 0.85 ? 0 : lerp(0, 1, (t - 0.85) / 0.15);
			return { upper, lower, hand };
		}

		function weightColor(w, bone) {
			if (bone === 'upper') return `rgba(232,85,58,${w})`;
			if (bone === 'lower') return `rgba(240,168,48,${w})`;
			return `rgba(78,203,180,${w})`;
		}

		function renderWeight() {
			wctx.clearRect(0, 0, WW, WH);
			const bend = parseFloat(document.getElementById('weightBend').value);
			document.getElementById('weightBendVal').textContent = bend + '°';

			const SX = WW * 0.4,
				SY = 30;
			const SEG = 20,
				segH = 9;
			const totalH = SEG * segH;

			// Arm baseline (not bent) for reference
			const baselineH = totalH + 40;

			// Compute bent arm positions
			const upperLen = SEG * 0.4,
				lowerLen = SEG * 0.4,
				handLen = SEG * 0.2;
			const baseAngle = (-90 * Math.PI) / 180;
			const elbowAngle = baseAngle + deg2rad(bend);

			const shoulderX = SX,
				shoulderY = SY;
			const elbowX = shoulderX + Math.cos(baseAngle) * upperLen * segH;
			const elbowY = shoulderY + Math.sin(baseAngle) * upperLen * segH;
			const wristX = elbowX + Math.cos(elbowAngle) * lowerLen * segH;
			const wristY = elbowY + Math.sin(elbowAngle) * lowerLen * segH;
			const tipX = wristX + Math.cos(elbowAngle) * handLen * segH;
			const tipY = wristY + Math.sin(elbowAngle) * handLen * segH;

			// Draw arm as mesh segments with weights
			for (let i = 0; i < SEG; i++) {
				const t = i / SEG;
				const { upper, lower, hand } = getWeight(t, 1);

				let x1, y1, x2, y2;
				if (t < 0.4) {
					const st = t / 0.4;
					x1 = lerp(shoulderX, elbowX, st);
					y1 = lerp(shoulderY, elbowY, st);
					const st2 = (t + 1 / SEG) / 0.4;
					x2 = lerp(shoulderX, elbowX, Math.min(1, st2));
					y2 = lerp(shoulderY, elbowY, Math.min(1, st2));
				} else if (t < 0.8) {
					const st = (t - 0.4) / 0.4;
					x1 = lerp(elbowX, wristX, st);
					y1 = lerp(elbowY, wristY, st);
					const st2 = (t + 1 / SEG - 0.4) / 0.4;
					x2 = lerp(elbowX, wristX, Math.min(1, st2));
					y2 = lerp(elbowY, wristY, Math.min(1, st2));
				} else {
					const st = (t - 0.8) / 0.2;
					x1 = lerp(wristX, tipX, st);
					y1 = lerp(wristY, tipY, st);
					const st2 = (t + 1 / SEG - 0.8) / 0.2;
					x2 = lerp(wristX, tipX, Math.min(1, st2));
					y2 = lerp(wristY, tipY, Math.min(1, st2));
				}

				const w = weightBone === 'upper' ? upper : weightBone === 'lower' ? lower : hand;
				const baseCol =
					weightBone === 'upper'
						? [232, 85, 58]
						: weightBone === 'lower'
							? [240, 168, 48]
							: [78, 203, 180];
				const alpha = 0.2 + w * 0.7;

				wctx.strokeStyle = `rgba(${baseCol[0]},${baseCol[1]},${baseCol[2]},${alpha})`;
				wctx.lineWidth = 18;
				wctx.lineCap = 'round';
				wctx.beginPath();
				wctx.moveTo(x1, y1);
				wctx.lineTo(x2, y2);
				wctx.stroke();
			}

			// Draw bones on top
			[
				[shoulderX, shoulderY, elbowX, elbowY, 'upper'],
				[elbowX, elbowY, wristX, wristY, 'lower'],
				[wristX, wristY, tipX, tipY, 'hand']
			].forEach(([x1, y1, x2, y2, boneId]) => {
				const active = weightBone === boneId;
				wctx.strokeStyle = active ? '#fff' : '#fff4';
				wctx.lineWidth = active ? 2 : 1;
				wctx.lineCap = 'round';
				wctx.beginPath();
				wctx.moveTo(x1, y1);
				wctx.lineTo(x2, y2);
				wctx.stroke();
				wctx.fillStyle = active ? '#fff' : '#fff4';
				wctx.beginPath();
				wctx.arc(x1, y1, active ? 5 : 3, 0, Math.PI * 2);
				wctx.fill();
			});
			wctx.fillStyle = '#fff';
			wctx.beginPath();
			wctx.arc(tipX, tipY, 4, 0, Math.PI * 2);
			wctx.fill();

			// Labels
			wctx.fillStyle = C.muted;
			wctx.font = `9px 'JetBrains Mono'`;
			wctx.textAlign = 'left';
			[
				[shoulderX + 10, shoulderY, 'Shoulder'],
				[elbowX + 10, elbowY, 'Elbow'],
				[wristX + 8, wristY, 'Wrist']
			].forEach(([x, y, label]) => {
				wctx.fillText(label, x, y + 4);
			});

			// Weight readout at elbow
			const elbowWeights = getWeight(0.4, 1);
			const rows = [
				{ bone: 'Upper Arm', w: elbowWeights.upper, col: [232, 85, 58] },
				{ bone: 'Lower Arm', w: elbowWeights.lower, col: [240, 168, 48] },
				{ bone: 'Hand', w: elbowWeights.hand, col: [78, 203, 180] }
			];
			const ro = document.getElementById('weightReadout');
			ro.innerHTML = '';
			rows.forEach((r) => {
				const row = document.createElement('div');
				row.style.cssText =
					'display:flex;align-items:center;gap:.5rem;font-family:var(--ff-mono);font-size:10px;';
				row.innerHTML = `<div style="width:50px;color:rgba(${r.col.join(',')},1)">${r.bone}</div><div style="flex:1;height:4px;background:var(--border2);border-radius:2px;overflow:hidden;"><div style="width:${r.w * 100}%;height:100%;background:rgba(${r.col.join(',')},1);border-radius:2px;"></div></div><span style="color:var(--muted);min-width:32px;text-align:right">${r.w.toFixed(2)}</span>`;
				ro.appendChild(row);
			});
		}

		document.getElementById('weightBend').oninput = function () {
			weightBend = parseInt(this.value);
			renderWeight();
		};
		renderWeight();

		/* ════════════════════════════
   DEMO 6.4 — CONTROLLER RIG
════════════════════════════ */
		const ctrlCanvas = document.getElementById('ctrlCanvas');
		const cctx = ctrlCanvas.getContext('2d');
		const CW = ctrlCanvas.width,
			CH = ctrlCanvas.height;
		let showRig = true;

		const CONTROLLERS = [
			{
				id: 'root',
				name: 'Root',
				shape: 'circle',
				size: 14,
				x: CW / 2,
				y: CH * 0.75,
				color: C.gold,
				locked: false,
				info: 'Root controller — moves the entire character'
			},
			{
				id: 'hip',
				name: 'Hip',
				shape: 'diamond',
				size: 11,
				x: CW / 2,
				y: CH * 0.58,
				color: C.gold,
				locked: false,
				info: 'Hip controller — tilts the pelvis, drives leg hierarchy'
			},
			{
				id: 'chest',
				name: 'Chest',
				shape: 'diamond',
				size: 10,
				x: CW / 2,
				y: CH * 0.38,
				color: C.coral,
				locked: false,
				info: 'Chest controller — rotates upper body independently of hips'
			},
			{
				id: 'head',
				name: 'Head',
				shape: 'circle',
				size: 9,
				x: CW / 2,
				y: CH * 0.16,
				color: C.lav,
				locked: false,
				info: 'Head controller — nod, turn, tilt — keeps head mobile'
			},
			{
				id: 'handL',
				name: 'L.Hand',
				shape: 'square',
				size: 9,
				x: CW * 0.28,
				y: CH * 0.48,
				color: C.mint,
				locked: false,
				info: 'Left Hand IK target — drag to place hand anywhere in reach'
			},
			{
				id: 'handR',
				name: 'R.Hand',
				shape: 'square',
				size: 9,
				x: CW * 0.72,
				y: CH * 0.48,
				color: C.mint,
				locked: false,
				info: 'Right Hand IK target — mirrors left hand'
			},
			{
				id: 'footL',
				name: 'L.Foot',
				shape: 'square',
				size: 9,
				x: CW * 0.38,
				y: CH * 0.88,
				color: C.lav,
				locked: false,
				info: 'Left Foot IK target — pins foot to ground during walk'
			},
			{
				id: 'footR',
				name: 'R.Foot',
				shape: 'square',
				size: 9,
				x: CW * 0.62,
				y: CH * 0.88,
				color: C.lav,
				locked: false,
				info: 'Right Foot IK target — pins foot to ground during walk'
			}
		];

		// Default positions
		const CTRL_DEFAULTS = CONTROLLERS.map((c) => ({ id: c.id, x: c.x, y: c.y }));

		let ctrlDragging = null,
			ctrlDragOX = 0,
			ctrlDragOY = 0,
			ctrlActiveCtrl = null;

		function drawCtrlCharacter() {
			// Draw simplified character body from controller positions
			const get = (id) => CONTROLLERS.find((c) => c.id === id);
			const root = get('root'),
				hip = get('hip'),
				chest = get('chest'),
				head = get('head');
			const handL = get('handL'),
				handR = get('handR'),
				footL = get('footL'),
				footR = get('footR');

			const drawLimb = (x1, y1, x2, y2, col, w = 10) => {
				cctx.strokeStyle = col + 'cc';
				cctx.lineWidth = w;
				cctx.lineCap = 'round';
				cctx.beginPath();
				cctx.moveTo(x1, y1);
				cctx.lineTo(x2, y2);
				cctx.stroke();
			};

			// Legs
			drawLimb(hip.x, hip.y, footL.x, footL.y, C.gold, 14);
			drawLimb(hip.x, hip.y, footR.x, footR.y, C.gold, 14);
			// Mid elbow approximation
			const elbowLX = lerp(chest.x, handL.x, 0.5),
				elbowLY = lerp(chest.y, handL.y, 0.5) + 20;
			const elbowRX = lerp(chest.x, handR.x, 0.5),
				elbowRY = lerp(chest.y, handR.y, 0.5) + 20;
			// Arms
			drawLimb(chest.x, chest.y, elbowLX, elbowLY, C.coral, 11);
			drawLimb(elbowLX, elbowLY, handL.x, handL.y, C.coral, 9);
			drawLimb(chest.x, chest.y, elbowRX, elbowRY, C.coral, 11);
			drawLimb(elbowRX, elbowRY, handR.x, handR.y, C.coral, 9);
			// Spine
			drawLimb(hip.x, hip.y, chest.x, chest.y, C.raised, 18);
			drawLimb(hip.x, hip.y, chest.x, chest.y, C.lav, 8);
			// Head
			cctx.fillStyle = C.lav + 'cc';
			cctx.beginPath();
			cctx.arc(head.x, head.y, 22, 0, Math.PI * 2);
			cctx.fill();
			// Eyes
			cctx.fillStyle = '#fff';
			cctx.beginPath();
			cctx.ellipse(head.x - 7, head.y - 3, 4, 5, -0.1, 0, Math.PI * 2);
			cctx.fill();
			cctx.beginPath();
			cctx.ellipse(head.x + 7, head.y - 3, 4, 5, 0.1, 0, Math.PI * 2);
			cctx.fill();
			cctx.fillStyle = C.bg;
			cctx.beginPath();
			cctx.arc(head.x - 7, head.y - 2, 2.5, 0, Math.PI * 2);
			cctx.fill();
			cctx.beginPath();
			cctx.arc(head.x + 7, head.y - 2, 2.5, 0, Math.PI * 2);
			cctx.fill();
			// Feet
			drawLimb(footL.x, footL.y, footL.x - 14, footL.y, C.gold, 9);
			drawLimb(footR.x, footR.y, footR.x + 14, footR.y, C.gold, 9);
		}

		function drawControllers() {
			CONTROLLERS.forEach((c) => {
				const isActive = ctrlActiveCtrl === c.id;
				cctx.save();
				cctx.translate(c.x, c.y);
				if (c.shape === 'circle') {
					cctx.strokeStyle = isActive ? '#fff' : c.color;
					cctx.lineWidth = isActive ? 2.5 : 1.5;
					cctx.beginPath();
					cctx.arc(0, 0, c.size, 0, Math.PI * 2);
					cctx.stroke();
					if (isActive) {
						cctx.fillStyle = c.color + '33';
						cctx.fill();
					}
				} else if (c.shape === 'diamond') {
					cctx.strokeStyle = isActive ? '#fff' : c.color;
					cctx.lineWidth = isActive ? 2.5 : 1.5;
					cctx.rotate(Math.PI / 4);
					cctx.beginPath();
					cctx.rect(-c.size, -c.size, c.size * 2, c.size * 2);
					cctx.stroke();
					if (isActive) {
						cctx.fillStyle = c.color + '33';
						cctx.fill();
					}
				} else {
					cctx.strokeStyle = isActive ? '#fff' : c.color;
					cctx.lineWidth = isActive ? 2.5 : 1.5;
					cctx.beginPath();
					cctx.rect(-c.size, -c.size, c.size * 2, c.size * 2);
					cctx.stroke();
					if (isActive) {
						cctx.fillStyle = c.color + '33';
						cctx.fill();
					}
				}
				// Label
				cctx.restore();
				if (showRig) {
					cctx.fillStyle = isActive ? c.color : c.color + '88';
					cctx.font = `8px 'JetBrains Mono'`;
					cctx.textAlign = 'center';
					cctx.fillText(c.name, c.x, c.y + c.size + 12);
				}
			});
		}

		// Bone lines overlay
		function drawRigOverlay() {
			const get = (id) => CONTROLLERS.find((c) => c.id === id);
			const pairs = [
				['root', 'hip'],
				['hip', 'chest'],
				['chest', 'head'],
				['chest', 'handL'],
				['chest', 'handR'],
				['hip', 'footL'],
				['hip', 'footR']
			];
			cctx.strokeStyle = '#fff2';
			cctx.lineWidth = 1;
			cctx.setLineDash([3, 4]);
			pairs.forEach(([a, b]) => {
				const ca = get(a),
					cb = get(b);
				cctx.beginPath();
				cctx.moveTo(ca.x, ca.y);
				cctx.lineTo(cb.x, cb.y);
				cctx.stroke();
			});
			cctx.setLineDash([]);
		}

		function renderCtrl() {
			cctx.clearRect(0, 0, CW, CH);
			// Ground
			cctx.strokeStyle = C.border2;
			cctx.lineWidth = 1;
			cctx.beginPath();
			cctx.moveTo(10, CH - 14);
			cctx.lineTo(CW - 10, CH - 14);
			cctx.stroke();
			drawCtrlCharacter();
			if (showRig) {
				drawRigOverlay();
				drawControllers();
			}
		}

		// Controller list sidebar
		function buildCtrlList() {
			const list = document.getElementById('ctrlList');
			list.innerHTML = '';
			CONTROLLERS.forEach((c) => {
				const row = document.createElement('div');
				row.style.cssText = 'display:flex;align-items:center;gap:.4rem;padding:2px 0;';
				const shape = c.shape === 'circle' ? '○' : c.shape === 'diamond' ? '◇' : '□';
				row.innerHTML = `<span style="color:${c.color};font-size:12px;">${shape}</span><span style="color:var(--muted)">${c.name}</span>`;
				list.appendChild(row);
			});
		}
		buildCtrlList();

		function toggleRigView(btn) {
			showRig = !showRig;
			btn.textContent = showRig ? 'Hide Rig' : 'Show Rig';
			btn.classList.toggle('active', showRig);
			renderCtrl();
		}
		function resetCtrl() {
			CTRL_DEFAULTS.forEach((d) => {
				const c = CONTROLLERS.find((x) => x.id === d.id);
				if (c) {
					c.x = d.x;
					c.y = d.y;
				}
			});
			ctrlActiveCtrl = null;
			document.getElementById('ctrlActiveInfo').textContent =
				'Drag a controller to pose the character.';
			renderCtrl();
		}

		function getCtrlPos(e) {
			const r = ctrlCanvas.getBoundingClientRect(),
				sc = ctrlCanvas.width / r.width;
			const raw = e.touches ? e.touches[0] : e;
			return { x: (raw.clientX - r.left) * sc, y: (raw.clientY - r.top) * sc };
		}
		ctrlCanvas.addEventListener('mousedown', (e) => {
			const p = getCtrlPos(e);
			let hit = null,
				minD = Infinity;
			CONTROLLERS.forEach((c) => {
				const d = Math.hypot(p.x - c.x, p.y - c.y);
				if (d < c.size + 10 && d < minD) {
					minD = d;
					hit = c;
				}
			});
			if (hit) {
				ctrlDragging = hit;
				ctrlActiveCtrl = hit.id;
				ctrlDragOX = p.x - hit.x;
				ctrlDragOY = p.y - hit.y;
				document.getElementById('ctrlActiveInfo').innerHTML =
					`<span style="color:${hit.color}">${hit.name}</span><br>${hit.info}`;
				renderCtrl();
			}
		});
		ctrlCanvas.addEventListener(
			'touchstart',
			(e) => {
				e.preventDefault();
				ctrlCanvas.dispatchEvent(
					new MouseEvent('mousedown', {
						clientX: e.touches[0].clientX,
						clientY: e.touches[0].clientY
					})
				);
			},
			{ passive: false }
		);
		window.addEventListener('mousemove', (e) => {
			if (!ctrlDragging) return;
			const p = getCtrlPos(e);
			ctrlDragging.x = p.x - ctrlDragOX;
			ctrlDragging.y = p.y - ctrlDragOY;
			renderCtrl();
		});
		window.addEventListener(
			'touchmove',
			(e) => {
				if (!ctrlDragging) return;
				e.preventDefault();
				const p = getCtrlPos(e);
				ctrlDragging.x = p.x - ctrlDragOX;
				ctrlDragging.y = p.y - ctrlDragOY;
				renderCtrl();
			},
			{ passive: false }
		);
		window.addEventListener('mouseup', () => {
			ctrlDragging = null;
		});
		window.addEventListener('touchend', () => {
			ctrlDragging = null;
		});
		renderCtrl();

		/* ════════════════════════════
   DEMO 6.5 — WALK CYCLE
════════════════════════════ */
		const WALK_POSES = [
			{
				name: 'Contact',
				num: '01',
				color: C.coral,
				desc: 'Leading heel strikes the ground. Maximum stride width. Arms swing opposite to legs — left arm forward with right leg, and vice versa. The body is at mid-height.',
				// Angles: spine, headTilt, armL, armR, thighL, shinL, thighR, shinR
				spine: 2,
				headTilt: -3,
				armL: -35,
				forearmL: 20,
				armR: 40,
				forearmR: 15,
				thighL: -38,
				shinL: 8,
				thighR: 28,
				shinR: 12
			},
			{
				name: 'Down',
				num: '02',
				color: C.gold,
				desc: 'The body is at its lowest point — weight is fully on the lead foot and the body drops as it passes over. This is the "recoil" or compression phase. Arms are more level.',
				spine: -2,
				headTilt: 2,
				armL: -18,
				forearmL: 12,
				armR: 22,
				forearmR: 10,
				thighL: -18,
				shinL: 22,
				thighR: 12,
				shinR: 38
			},
			{
				name: 'Passing',
				num: '03',
				color: C.mint,
				desc: 'The free leg passes beneath the body. The body is at its highest point — the planted leg is fully extended, lifting the hips. Arms cross near the centre.',
				spine: 0,
				headTilt: 0,
				armL: 5,
				forearmL: 8,
				armR: -5,
				forearmR: 8,
				thighL: 5,
				shinL: 55,
				thighR: -10,
				shinR: 5
			},
			{
				name: 'Up',
				num: '04',
				color: C.lav,
				desc: 'The free leg has swung forward and is about to make contact. The body is at mid-height and descending. Arms reach their opposite swing extremes — mirroring the Contact pose.',
				spine: 2,
				headTilt: -2,
				armL: 38,
				forearmL: 15,
				armR: -32,
				forearmR: 18,
				thighL: 26,
				shinL: 10,
				thighR: -35,
				shinR: 6
			}
		];

		// Build pose strip
		const strip = document.getElementById('poseStrip');
		WALK_POSES.forEach((p, i) => {
			const card = document.createElement('div');
			card.className = 'pose-card' + (i === 0 ? ' active' : '');
			card.dataset.index = i;
			card.innerHTML = `<div class="pose-num">${p.num}</div><div class="pose-name" style="color:${i === 0 ? p.color : 'var(--text)'}">${p.name}</div><div class="pose-desc">${p.desc.substring(0, 40)}…</div>`;
			card.onclick = () => setWalkPose(i);
			strip.appendChild(card);
		});

		const walkCanvas = document.getElementById('walkCanvas');
		const wkCtx = walkCanvas.getContext('2d');
		const WKW = walkCanvas.width,
			WKH = walkCanvas.height;
		let walkPoseIdx = 0,
			walkT = 0,
			walkPlaying = true,
			walkRaf = null,
			walkLastTs = null;
		let walkSpeed = 1.0,
			walkStride = 48,
			walkBob = 10;

		function lerpPose(a, b, t) {
			const keys = [
				'spine',
				'headTilt',
				'armL',
				'forearmL',
				'armR',
				'forearmR',
				'thighL',
				'shinL',
				'thighR',
				'shinR'
			];
			const out = {};
			keys.forEach((k) => (out[k] = lerp(a[k], b[k], eio(t))));
			return out;
		}

		function drawWalkChar(pose, bobY) {
			wkCtx.clearRect(0, 0, WKW, WKH);
			// Ground
			wkCtx.strokeStyle = C.border2;
			wkCtx.lineWidth = 1;
			wkCtx.beginPath();
			wkCtx.moveTo(10, WKH - 24);
			wkCtx.lineTo(WKW - 24, WKH - 24);
			wkCtx.stroke();

			const cx = WKW / 2,
				gy = WKH - 24;
			const hipY = gy - 75 + bobY;
			const spineA = deg2rad(-90 + pose.spine);
			const chestX = cx + Math.cos(spineA) * 45,
				chestY = hipY + Math.sin(spineA) * 45;
			const headX = chestX + Math.cos(spineA) * 28 + pose.headTilt * 0.4;
			const headY = chestY + Math.sin(spineA) * 28;

			const strokeLimb = (x1, y1, a1deg, a2deg, l1, l2, col, w1 = 11, w2 = 9) => {
				const a1 = deg2rad(a1deg),
					a2 = deg2rad(a2deg);
				const mx = x1 + Math.cos(a1) * l1,
					my = y1 + Math.sin(a1) * l1;
				const ex = mx + Math.cos(a1 + a2) * l2,
					ey = my + Math.sin(a1 + a2) * l2;
				wkCtx.strokeStyle = col;
				wkCtx.lineCap = 'round';
				wkCtx.lineWidth = w1;
				wkCtx.beginPath();
				wkCtx.moveTo(x1, y1);
				wkCtx.lineTo(mx, my);
				wkCtx.stroke();
				wkCtx.lineWidth = w2;
				wkCtx.beginPath();
				wkCtx.moveTo(mx, my);
				wkCtx.lineTo(ex, ey);
				wkCtx.stroke();
				wkCtx.fillStyle = col;
				wkCtx.beginPath();
				wkCtx.arc(mx, my, 5, 0, Math.PI * 2);
				wkCtx.fill();
				return { mx, my, ex, ey };
			};

			// Back leg (drawn first)
			strokeLimb(
				cx,
				hipY,
				-90 + pose.thighR,
				pose.shinR,
				walkStride * 0.85,
				walkStride * 0.75,
				C.gold + '88',
				13,
				10
			);
			// Back arm
			strokeLimb(chestX, chestY, -90 + pose.armR * -1, pose.forearmR, 36, 28, C.coral + '88', 9, 7);

			// Torso
			wkCtx.strokeStyle = C.lav + 'cc';
			wkCtx.lineWidth = 16;
			wkCtx.lineCap = 'round';
			wkCtx.beginPath();
			wkCtx.moveTo(cx, hipY);
			wkCtx.lineTo(chestX, chestY);
			wkCtx.stroke();

			// Front leg
			strokeLimb(
				cx,
				hipY,
				-90 + pose.thighL,
				pose.shinL,
				walkStride * 0.85,
				walkStride * 0.75,
				C.gold + 'ee',
				13,
				10
			);
			// Front arm
			strokeLimb(chestX, chestY, -90 + pose.armL, pose.forearmL, 36, 28, C.coral + 'ee', 9, 7);

			// Head
			wkCtx.fillStyle = C.lav + 'cc';
			wkCtx.beginPath();
			wkCtx.arc(headX, headY, 20, 0, Math.PI * 2);
			wkCtx.fill();
			wkCtx.fillStyle = '#fff';
			wkCtx.beginPath();
			wkCtx.ellipse(headX - 6, headY - 2, 3.5, 4.5, -0.1, 0, Math.PI * 2);
			wkCtx.fill();
			wkCtx.beginPath();
			wkCtx.ellipse(headX + 6, headY - 2, 3.5, 4.5, 0.1, 0, Math.PI * 2);
			wkCtx.fill();
			wkCtx.fillStyle = C.bg;
			wkCtx.beginPath();
			wkCtx.arc(headX - 6, headY - 1, 2, 0, Math.PI * 2);
			wkCtx.fill();
			wkCtx.beginPath();
			wkCtx.arc(headX + 6, headY - 1, 2, 0, Math.PI * 2);
			wkCtx.fill();

			// Hip dot
			wkCtx.fillStyle = C.gold;
			wkCtx.beginPath();
			wkCtx.arc(cx, hipY, 7, 0, Math.PI * 2);
			wkCtx.fill();
		}

		function drawWalkTimeline(t, poseIdx) {
			const tlC = document.getElementById('walkTimelineCanvas');
			const tlCtx = tlC.getContext('2d');
			const TW = tlC.width,
				TH = tlC.height;
			tlCtx.clearRect(0, 0, TW, TH);

			tlCtx.fillStyle = C.bg;
			tlCtx.fillRect(0, 0, TW, TH);
			const poseW = TW / WALK_POSES.length;
			WALK_POSES.forEach((p, i) => {
				const isActive = i === poseIdx;
				tlCtx.fillStyle = isActive ? p.color + '22' : C.raised;
				tlCtx.fillRect(i * poseW, 0, poseW - 1, TH);
				tlCtx.fillStyle = isActive ? p.color : C.dim;
				tlCtx.font = `8px 'JetBrains Mono'`;
				tlCtx.textAlign = 'center';
				tlCtx.fillText(p.name, i * poseW + poseW / 2, TH / 2 + 3);
			});

			// Playhead
			const ph = (poseIdx + t) * poseW;
			tlCtx.fillStyle = C.coral;
			tlCtx.fillRect(ph - 1, 0, 2, TH);
		}

		function setWalkPose(idx) {
			walkPoseIdx = idx;
			document.querySelectorAll('.pose-card').forEach((c, i) => {
				c.classList.toggle('active', i === idx);
				c.querySelector('.pose-name').style.color = i === idx ? WALK_POSES[i].color : 'var(--text)';
			});
			document.getElementById('walkPoseName').textContent = WALK_POSES[idx].name;
			document.getElementById('walkPoseDesc').textContent = WALK_POSES[idx].desc;
			drawWalkTimeline(0, idx);
			if (!walkPlaying) {
				const p = WALK_POSES[idx];
				drawWalkChar(p, 0);
				document.getElementById('walkFrameNum').textContent = `Pose ${idx + 1}/4`;
			}
		}

		function walkTick(ts) {
			if (!walkLastTs) walkLastTs = ts;
			const dt = (ts - walkLastTs) / 1000;
			walkLastTs = ts;
			walkT += dt * walkSpeed * 1.8;
			if (walkT > 1) walkT -= 1;

			const poseIdx = Math.floor(walkT * WALK_POSES.length) % WALK_POSES.length;
			const poseFrac = (walkT * WALK_POSES.length) % 1;
			const pA = WALK_POSES[poseIdx];
			const pB = WALK_POSES[(poseIdx + 1) % WALK_POSES.length];
			const blended = lerpPose(pA, pB, poseFrac);
			const bobY = Math.sin(walkT * Math.PI * 2) * walkBob;

			drawWalkChar(blended, bobY);
			drawWalkTimeline(poseFrac, poseIdx);

			document.getElementById('walkPoseName').textContent = pA.name;
			document.getElementById('walkFrameNum').textContent = `Frame ${Math.round(walkT * 24)}/24`;
			document.querySelectorAll('.pose-card').forEach((c, i) => {
				c.classList.toggle('active', i === poseIdx);
				c.querySelector('.pose-name').style.color =
					i === poseIdx ? WALK_POSES[i].color : 'var(--text)';
			});

			walkRaf = requestAnimationFrame(walkTick);
		}

		const walkPlayBtn = document.getElementById('walkPlayBtn');
		walkPlayBtn.onclick = () => {
			walkPlaying = !walkPlaying;
			walkPlayBtn.textContent = walkPlaying ? '⏸ Pause' : '▶ Play';
			walkPlayBtn.classList.toggle('active', walkPlaying);
			if (walkPlaying) {
				walkLastTs = null;
				walkRaf = requestAnimationFrame(walkTick);
			} else cancelAnimationFrame(walkRaf);
		};
		document.getElementById('walkPrevBtn').onclick = () => {
			if (walkPlaying) {
				walkPlaying = false;
				cancelAnimationFrame(walkRaf);
				walkPlayBtn.textContent = '▶ Play';
				walkPlayBtn.classList.remove('active');
			}
			setWalkPose((walkPoseIdx - 1 + WALK_POSES.length) % WALK_POSES.length);
			drawWalkChar(WALK_POSES[walkPoseIdx], 0);
		};
		document.getElementById('walkNextBtn').onclick = () => {
			if (walkPlaying) {
				walkPlaying = false;
				cancelAnimationFrame(walkRaf);
				walkPlayBtn.textContent = '▶ Play';
				walkPlayBtn.classList.remove('active');
			}
			setWalkPose((walkPoseIdx + 1) % WALK_POSES.length);
			drawWalkChar(WALK_POSES[walkPoseIdx], 0);
		};
		document.getElementById('walkSpeed').oninput = function () {
			walkSpeed = parseFloat(this.value);
			document.getElementById('walkSpeedVal').textContent = this.value + '×';
		};
		document.getElementById('walkStride').oninput = function () {
			walkStride = parseInt(this.value);
			document.getElementById('walkStrideVal').textContent = this.value;
		};
		document.getElementById('walkBob').oninput = function () {
			walkBob = parseInt(this.value);
			document.getElementById('walkBobVal').textContent = this.value;
		};

		// Init
		setWalkPose(0);
		drawWalkChar(WALK_POSES[0], 0);
		// Auto-start
		setTimeout(() => {
			walkLastTs = null;
			walkRaf = requestAnimationFrame(walkTick);
		}, 400);

		/* ════════════════════════════
   QUIZ
════════════════════════════ */
		let quizScores = {};
		function answer(optEl, qId, result) {
			const qEl = document.getElementById(qId);
			if (qEl.querySelector('.option.correct') || qEl.querySelector('.option.wrong')) return;
			const fb = document.getElementById(qId + '-feedback');
			optEl.classList.add(result === 'correct' ? 'correct' : 'wrong');
			qEl.querySelectorAll('.option').forEach((o) => o.classList.add('disabled'));
			if (result === 'correct') {
				fb.textContent = '✓ Correct.';
				fb.className = 'feedback ok';
				quizScores[qId] = true;
			} else {
				fb.textContent = '✗ Not quite — review the section above.';
				fb.className = 'feedback bad';
				quizScores[qId] = false;
				qEl.querySelectorAll('.option').forEach((o) => {
					if (o.getAttribute('onclick') && o.getAttribute('onclick').includes("'correct'"))
						o.classList.add('correct');
				});
			}
			if (Object.keys(quizScores).length === 5) {
				const c = Object.values(quizScores).filter(Boolean).length;
				document.getElementById('scoreNum').textContent = `${c}/5`;
				document.getElementById('scoreLbl').textContent =
					c === 5
						? 'Perfect — Module 6 Complete!'
						: c >= 4
							? 'Strong — review any you missed.'
							: 'Good effort — re-read the sections.';
				document.getElementById('quizScore').classList.add('visible');
			}
		}

		/* eslint-disable no-undef */
		if (typeof renderWeight === 'function') window.renderWeight = renderWeight;
		if (typeof renderCtrl === 'function') window.renderCtrl = renderCtrl;
		if (typeof drawCtrlCharacter === 'function') window.drawCtrlCharacter = drawCtrlCharacter;
		if (typeof toggleRigView === 'function') window.toggleRigView = toggleRigView;
		if (typeof drawFK === 'function') window.drawFK = drawFK;
		if (typeof buildHierTree === 'function') window.buildHierTree = buildHierTree;
		if (typeof lerpAngle === 'function') window.lerpAngle = lerpAngle;
		if (typeof drawWalkTimeline === 'function') window.drawWalkTimeline = drawWalkTimeline;
		if (typeof getIKPos === 'function') window.getIKPos = getIKPos;
		if (typeof renderNode === 'function') window.renderNode = renderNode;
		if (typeof weightColor === 'function') window.weightColor = weightColor;
		if (typeof getFKPos === 'function') window.getFKPos = getFKPos;
		if (typeof toggleFKAnim === 'function') window.toggleFKAnim = toggleFKAnim;
		if (typeof resetCtrl === 'function') window.resetCtrl = resetCtrl;
		if (typeof renderFKPanel === 'function') window.renderFKPanel = renderFKPanel;
		if (typeof walkTick === 'function') window.walkTick = walkTick;
		if (typeof drawFKPanel === 'function') window.drawFKPanel = drawFKPanel;
		if (typeof selectWeightBone === 'function') window.selectWeightBone = selectWeightBone;
		if (typeof drawRigOverlay === 'function') window.drawRigOverlay = drawRigOverlay;
		if (typeof drawControllers === 'function') window.drawControllers = drawControllers;
		if (typeof drawIKPanel === 'function') window.drawIKPanel = drawIKPanel;
		if (typeof computeFK === 'function') window.computeFK = computeFK;
		if (typeof getWeight === 'function') window.getWeight = getWeight;
		if (typeof buildCtrlList === 'function') window.buildCtrlList = buildCtrlList;
		if (typeof fkIdleTick === 'function') window.fkIdleTick = fkIdleTick;
		if (typeof solveIK2Bone === 'function') window.solveIK2Bone = solveIK2Bone;
		if (typeof setWalkPose === 'function') window.setWalkPose = setWalkPose;
		if (typeof lerpPose === 'function') window.lerpPose = lerpPose;
		if (typeof drawWalkChar === 'function') window.drawWalkChar = drawWalkChar;
		if (typeof answer === 'function') window.answer = answer;
		if (typeof computeBoneEndWorld === 'function') window.computeBoneEndWorld = computeBoneEndWorld;
		if (typeof resetFK === 'function') window.resetFK = resetFK;
		if (typeof getCtrlPos === 'function') window.getCtrlPos = getCtrlPos;
		/* eslint-enable no-undef */

		return () => {
			if (typeof fkAnimRaf !== 'undefined' && fkAnimRaf) cancelAnimationFrame(fkAnimRaf);
			if (typeof walkRaf !== 'undefined' && walkRaf) cancelAnimationFrame(walkRaf);
			// Note: window event listeners use anonymous functions and cannot be auto-removed.
			// Consider refactoring to named handlers for proper cleanup.
		};
	});
</script>

<div class="page-wrapper">
	<!-- ══ HERO ══ -->
	<header class="module-hero">
		<svg
			class="hero-deco"
			viewBox="0 0 200 400"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
			aria-hidden="true"
		>
			<circle cx="100" cy="40" r="18" stroke="#e8553a" stroke-width="1.5" />
			<line x1="100" y1="58" x2="100" y2="100" stroke="#e8553a" stroke-width="1.5" />
			<circle cx="100" cy="100" r="8" fill="#e8553a" opacity=".6" />
			<line x1="100" y1="108" x2="100" y2="180" stroke="#e8553a" stroke-width="1.5" />
			<circle cx="100" cy="180" r="8" fill="#e8553a" opacity=".4" />
			<line x1="100" y1="188" x2="72" y2="260" stroke="#e8553a" stroke-width="1.5" />
			<line x1="100" y1="188" x2="128" y2="260" stroke="#e8553a" stroke-width="1.5" />
			<circle cx="72" cy="260" r="7" fill="#e8553a" opacity=".3" />
			<circle cx="128" cy="260" r="7" fill="#e8553a" opacity=".3" />
			<line x1="72" y1="267" x2="72" y2="340" stroke="#e8553a" stroke-width="1.5" />
			<line x1="128" y1="267" x2="128" y2="340" stroke="#e8553a" stroke-width="1.5" />
			<circle cx="72" cy="340" r="6" fill="#e8553a" opacity=".2" />
			<circle cx="128" cy="340" r="6" fill="#e8553a" opacity=".2" />
			<!-- arms -->
			<line x1="100" y1="120" x2="44" y2="155" stroke="#f0a830" stroke-width="1.5" />
			<line x1="100" y1="120" x2="156" y2="155" stroke="#f0a830" stroke-width="1.5" />
			<circle cx="44" cy="155" r="7" fill="#f0a830" opacity=".4" />
			<circle cx="156" cy="155" r="7" fill="#f0a830" opacity=".4" />
			<line x1="44" y1="155" x2="20" y2="200" stroke="#f0a830" stroke-width="1.5" />
			<line x1="156" y1="155" x2="180" y2="200" stroke="#f0a830" stroke-width="1.5" />
		</svg>
		<div class="module-eyebrow">Animation Fundamentals · Module 06</div>
		<h1 class="module-title">Rigging for <em>2D Characters</em></h1>
		<p class="module-subtitle">
			Building the skeleton that lets a character move without being redrawn every frame.
		</p>
		<div class="objectives">
			<div class="obj-label">Learning Objectives</div>
			<ul>
				<li>Understand what a rig is and why it enables efficient character animation</li>
				<li>Explain hierarchies — how parent bones drive child bones</li>
				<li>
					Distinguish Forward Kinematics (FK) from Inverse Kinematics (IK) and know when to use each
				</li>
				<li>Understand bone weighting and how it controls mesh/shape deformation</li>
				<li>Build and animate a basic walk cycle from its four key poses</li>
			</ul>
		</div>
	</header>

	<!-- ══ SECTION 1: WHAT IS A RIG ══ -->
	<section class="section" id="s1">
		<div class="section-header">
			<span class="section-num">01</span>
			<h2 class="section-title">What Is a Rig?</h2>
		</div>
		<p>
			In the pre-digital era, if you wanted to animate a character walking across a room, you drew
			them — completely, from scratch — in every single frame. A three-second walk at 24fps meant 72
			complete drawings. Change your mind about the character's proportions? Redraw all 72.
		</p>
		<p>
			A <strong>rig</strong> solves this by separating
			<em>what the character looks like</em> from <em>how it moves</em>. The artwork — the shapes,
			textures, and colours — is drawn once and attached to a skeleton of invisible
			<strong>bones</strong>. Moving a bone deforms or repositions the artwork automatically. The
			animator then poses the skeleton, not the drawings.
		</p>
		<div class="callout coral">
			<div class="callout-label">The Core Bargain</div>
			Rigging requires up-front time and technical setup. In return, you get a character you can re-pose
			in seconds rather than redrawing hours. For a recurring host character in a YouTube series, this
			payoff is enormous — you build the rig once and animate it for every video.
		</div>
		<p>
			Rigging is the bridge between Module 4 (designing shapes for animation) and Module 7
			(animating dialogue and expression). A well-rigged character makes everything downstream
			faster and more consistent. A badly rigged one creates problems in every single shot.
		</p>
	</section>

	<!-- ══ SECTION 2: HIERARCHIES ══ -->
	<section class="section" id="s2">
		<div class="section-header">
			<span class="section-num">02</span>
			<h2 class="section-title">Hierarchies — Parent &amp; Child Bones</h2>
		</div>
		<p>
			Every rig is a <strong>hierarchy</strong> — a tree of bones where each bone has at most one
			parent and any number of children. When a parent bone moves, all its children move with it.
			When a child bone moves, it does so <em>relative to its parent</em>, leaving the parent
			unchanged.
		</p>
		<p>
			Think of your arm. When your shoulder rotates, your elbow and hand follow. When your elbow
			bends, your hand follows but your shoulder stays put. The shoulder is the parent of the elbow;
			the elbow is the parent of the wrist; the wrist is the parent of the hand. This is a
			hierarchy.
		</p>

		<div class="callout gold">
			<div class="callout-label">Reading a Hierarchy</div>
			In animation software, hierarchies are displayed as indented trees — the root bone at the top, children
			indented beneath their parents. The deepest items in the tree (bones with no children) are called<strong
				>leaf bones</strong
			>. Always design your hierarchy to match the physical chain of influence in the character's
			body.
		</div>

		<!-- DEMO 6.1: Hierarchy Explorer + FK Arm -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 6.1 — Bone Hierarchy &amp; Forward Kinematics</span>
				<span class="demo-badge">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					<strong style="color: var(--coral)">Click a bone</strong> in the hierarchy tree or
					directly on the rig to select it. Then
					<strong style="color: var(--coral)">drag</strong> on the canvas to rotate it. Notice how child
					bones follow their parent — this is Forward Kinematics.
				</p>
				<div
					style="
								display: grid;
								grid-template-columns: 200px 1fr;
								gap: 1.25rem;
								align-items: start;
								flex-wrap: wrap;
							"
				>
					<!-- Tree -->
					<div>
						<div
							style="
										font-family: var(--ff-mono);
										font-size: 9px;
										color: var(--muted);
										letter-spacing: 0.12em;
										text-transform: uppercase;
										margin-bottom: 0.5rem;
									"
						>
							Bone Hierarchy
						</div>
						<div class="hier-tree" id="hierTree"></div>
						<div
							id="hierInfo"
							style="
										margin-top: 0.75rem;
										padding: 0.65rem 0.85rem;
										border: 1px solid var(--border);
										background: var(--raised);
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--muted);
										line-height: 1.7;
										min-height: 3.5em;
									"
						></div>
					</div>
					<!-- Canvas -->
					<div>
						<canvas
							id="fkCanvas"
							width="380"
							height="340"
							style="
										background: var(--raised);
										border: 1px solid var(--border);
										max-width: 100%;
										cursor: crosshair;
										touch-action: none;
									"
						></canvas>
						<div style="margin-top: 0.5rem; display: flex; gap: 1.5rem; flex-wrap: wrap">
							<div style="font-family: var(--ff-mono); font-size: 10px; color: var(--muted)">
								Selected: <span id="selectedBoneName" style="color: var(--coral)">none</span>
							</div>
							<div style="font-family: var(--ff-mono); font-size: 10px; color: var(--muted)">
								Angle: <span id="selectedBoneAngle" style="color: var(--gold)">—</span>
							</div>
						</div>
						<div class="btn-row" style="margin-top: 0.65rem">
							<button
								class="btn"
								onclick={(e) => {
									window.resetFK();
								}}>↺ Reset Pose</button
							>
							<button
								class="btn gold"
								id="fkAnimBtn"
								onclick={(e) => {
									window.toggleFKAnim(e.currentTarget);
								}}
							>
								▶ Idle Animation
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ SECTION 3: FK vs IK ══ -->
	<section class="section" id="s3">
		<div class="section-header">
			<span class="section-num">03</span>
			<h2 class="section-title">FK vs. IK — Two Ways to Pose a Limb</h2>
		</div>
		<p>
			There are two fundamental approaches to moving a chain of bones, and understanding the
			difference is one of the most important things a rigger must know.
		</p>
		<p>
			<strong>Forward Kinematics (FK)</strong> means you rotate each bone individually from the root outward.
			To move a hand, you rotate the shoulder, then the elbow, then the wrist. This matches how you conceptually
			think about a joint hierarchy, and it produces natural-looking arcs — but it requires rotating multiple
			bones to achieve a simple endpoint position.
		</p>
		<p>
			<strong>Inverse Kinematics (IK)</strong> flips this. You place the end of the chain (the hand, the
			foot) where you want it, and the software automatically calculates how every joint between the root
			and the end must rotate to reach that position. IK is indispensable for keeping feet planted on
			the ground during a walk cycle, or for precise hand placement on surfaces.
		</p>

		<div class="callout mint">
			<div class="callout-label">When to Use Each</div>
			<div
				style="
							display: grid;
							grid-template-columns: 1fr 1fr;
							gap: 0.5rem 1.5rem;
							font-size: 12px;
							margin-top: 0.4rem;
						"
			>
				<div>
					<strong style="color: var(--gold)">Use FK for:</strong><br />Arms swinging freely<br
					/>Tails and hair<br />Spine arching<br />Any limb not touching something
				</div>
				<div>
					<strong style="color: var(--mint)">Use IK for:</strong><br />Feet on the ground<br />Hands
					gripping objects<br />Characters leaning on surfaces<br />Any limb with a fixed endpoint
				</div>
			</div>
		</div>

		<!-- DEMO 6.2: FK vs IK -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 6.2 — FK vs. IK Side by Side</span>
				<span class="demo-badge coral">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					<strong style="color: var(--gold)">FK (left):</strong> drag the angle sliders to rotate
					each joint individually.
					<strong style="color: var(--mint)">IK (right):</strong> drag the hand target directly — the
					elbow and shoulder solve automatically.
				</p>
				<div class="fkik-split">
					<div class="fkik-panel">
						<div class="fkik-header">
							<div>
								<div class="fkik-title">Forward Kinematics</div>
								<div class="fkik-tag">Rotate joints manually from root</div>
							</div>
							<span
								style="
											font-family: var(--ff-mono);
											font-size: 9px;
											color: var(--gold);
											border: 1px solid var(--gold);
											padding: 1px 6px;
										">FK</span
							>
						</div>
						<div style="padding: 1rem">
							<canvas
								id="fkikFKCanvas"
								width="260"
								height="240"
								style="
											background: var(--raised);
											border: 1px solid var(--border);
											display: block;
											max-width: 100%;
										"
							></canvas>
							<div style="margin-top: 0.75rem">
								<div class="ctrl-row">
									<span class="ctrl-label">Shoulder</span>
									<input type="range" class="gold" id="fkShoulder" min="-90" max="90" value="-30" />
									<span class="ctrl-val" id="fkShoulderVal" style="color: var(--gold)">-30°</span>
								</div>
								<div class="ctrl-row">
									<span class="ctrl-label">Elbow</span>
									<input type="range" class="gold" id="fkElbow" min="0" max="150" value="60" />
									<span class="ctrl-val" id="fkElbowVal" style="color: var(--gold)">60°</span>
								</div>
								<div class="ctrl-row">
									<span class="ctrl-label">Wrist</span>
									<input type="range" class="gold" id="fkWrist" min="-60" max="60" value="0" />
									<span class="ctrl-val" id="fkWristVal" style="color: var(--gold)">0°</span>
								</div>
							</div>
						</div>
					</div>
					<div class="fkik-panel">
						<div class="fkik-header">
							<div>
								<div class="fkik-title">Inverse Kinematics</div>
								<div class="fkik-tag">Drag the hand target</div>
							</div>
							<span
								style="
											font-family: var(--ff-mono);
											font-size: 9px;
											color: var(--mint);
											border: 1px solid var(--mint);
											padding: 1px 6px;
										">IK</span
							>
						</div>
						<div style="padding: 1rem">
							<canvas
								id="fkikIKCanvas"
								width="260"
								height="240"
								style="
											background: var(--raised);
											border: 1px solid var(--border);
											display: block;
											max-width: 100%;
											cursor: crosshair;
											touch-action: none;
										"
							></canvas>
							<div
								style="
											margin-top: 0.75rem;
											font-family: var(--ff-mono);
											font-size: 10px;
											color: var(--muted);
											line-height: 1.6;
										"
								id="ikReadout"
							>
								Drag the <span style="color: var(--mint)">◆ target</span> anywhere — the elbow and shoulder
								rotate automatically to reach it.
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ SECTION 4: BONE WEIGHTING ══ -->
	<section class="section" id="s4">
		<div class="section-header">
			<span class="section-num">04</span>
			<h2 class="section-title">Bone Weighting</h2>
		</div>
		<p>
			Bones don't directly move pixels or shapes — they influence them through
			<strong>weights</strong>. Every vertex (or control point) in a mesh is given a weight value
			for each nearby bone, from 0.0 (no influence) to 1.0 (full control). When multiple bones
			influence the same vertex, their weighted contributions blend together.
		</p>
		<p>
			This blending is what creates smooth deformation at joints — the elbow skin doesn't crack in
			half, it bends fluidly because the vertices near the joint are shared between the upper arm
			and forearm bones. The quality of this weighting is the difference between
			professional-looking deformation and the "collapsing joint" problem that plagues amateur rigs.
		</p>

		<!-- DEMO 6.3: Weight Painting -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 6.3 — Bone Weighting Visualiser</span>
				<span class="demo-badge gold">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					Select a bone to see its influence zone highlighted on the mesh. Drag the slider to bend
					the joint — notice how the weight gradient produces smooth deformation at the elbow.
				</p>
				<div
					style="
								display: grid;
								grid-template-columns: 1fr 1fr;
								gap: 1.25rem;
								align-items: start;
							"
				>
					<!-- Weight canvas -->
					<div>
						<canvas
							id="weightCanvas"
							width="300"
							height="280"
							style="
										background: var(--raised);
										border: 1px solid var(--border);
										display: block;
										max-width: 100%;
									"
						></canvas>
						<div class="weight-legend" style="margin-top: 0.5rem">
							<div class="wl-item">
								<div class="wl-swatch" style="background: #e8553a"></div>
								Full influence (1.0)
							</div>
							<div class="wl-item">
								<div class="wl-swatch" style="background: #f0a830"></div>
								Partial (0.5)
							</div>
							<div class="wl-item">
								<div
									class="wl-swatch"
									style="background: #1c1812; border: 1px solid var(--border2)"
								></div>
								No influence (0.0)
							</div>
						</div>
					</div>
					<!-- Controls -->
					<div style="display: flex; flex-direction: column; gap: 0.85rem">
						<div>
							<div
								style="
											font-family: var(--ff-mono);
											font-size: 10px;
											color: var(--muted);
											margin-bottom: 0.5rem;
											letter-spacing: 0.1em;
											text-transform: uppercase;
										"
							>
								Select Bone
							</div>
							<div class="btn-row" id="weightBoneSelector">
								<button
									class="btn active"
									data-bone="upper"
									onclick={(e) => {
										window.selectWeightBone(e.currentTarget, 'upper');
									}}
								>
									Upper Arm
								</button>
								<button
									class="btn"
									data-bone="lower"
									onclick={(e) => {
										window.selectWeightBone(e.currentTarget, 'lower');
									}}
								>
									Lower Arm
								</button>
								<button
									class="btn"
									data-bone="hand"
									onclick={(e) => {
										window.selectWeightBone(e.currentTarget, 'hand');
									}}
								>
									Hand
								</button>
							</div>
						</div>
						<div class="ctrl-row">
							<span class="ctrl-label">Bend angle</span>
							<input type="range" class="coral" id="weightBend" min="0" max="130" value="60" />
							<span class="ctrl-val" id="weightBendVal">60°</span>
						</div>
						<div
							style="
										padding: 0.85rem;
										border: 1px solid var(--border);
										background: var(--raised);
										font-family: var(--ff-mono);
										font-size: 11px;
										color: var(--muted);
										line-height: 1.7;
									"
							id="weightDesc"
						>
							<span style="color: var(--coral)">Upper Arm bone:</span> vertices at the top of the arm
							have full weight here. Vertices near the elbow are shared with the lower arm bone — this
							is what creates smooth blending.
						</div>
						<div
							style="
										padding: 0.75rem;
										border: 1px solid var(--border);
										background: var(--raised);
									"
						>
							<div
								style="
											font-family: var(--ff-mono);
											font-size: 9px;
											color: var(--muted);
											letter-spacing: 0.1em;
											text-transform: uppercase;
											margin-bottom: 0.5rem;
										"
							>
								Weight at elbow joint
							</div>
							<div
								style="display: flex; flex-direction: column; gap: 0.25rem"
								id="weightReadout"
							></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ SECTION 5: CONTROLLERS ══ -->
	<section class="section" id="s5">
		<div class="section-header">
			<span class="section-num">05</span>
			<h2 class="section-title">Controllers &amp; Handles</h2>
		</div>
		<p>
			Directly manipulating bones can be cumbersome — you have to click precisely on thin bone
			shapes, and the hierarchy can be confusing. Professional rigs solve this with
			<strong>controllers</strong> (also called controls or handles): visible shapes drawn in a separate,
			non-rendered layer that are linked to bones but are easier to click and drag.
		</p>
		<p>
			A controller might be a circle at the shoulder, a square at the hand, or a diamond at the
			root. They are never visible in the final render — they exist purely as UI for the animator. A
			well-designed controller set makes a rig feel fast and intuitive to use, like a well-designed
			tool. A badly designed one means the animator fights the rig on every shot.
		</p>
		<div class="callout mint">
			<div class="callout-label">For Educational Animation</div>
			Your character rig probably only needs five to eight controllers for explainer video work: root,
			hip, torso/chest, head, left arm IK target, right arm IK target, and optional foot controls. Resist
			the temptation to over-rig. Every extra control is complexity that must be animated in every shot.
		</div>

		<!-- DEMO 6.4: Controller Rig -->
		<div class="demo-box">
			<div class="demo-header">
				<span class="demo-label">Demo 6.4 — Controller-Based Rig</span>
				<span class="demo-badge mint">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					A complete character rig driven by controllers.
					<strong style="color: var(--mint)">Drag any controller</strong> to pose the character. Toggle
					between the clean view (what the audience sees) and the rig view (what the animator sees).
				</p>
				<div style="display: flex; gap: 1.25rem; flex-wrap: wrap; align-items: flex-start">
					<canvas
						id="ctrlCanvas"
						width="380"
						height="360"
						style="
									background: var(--raised);
									border: 1px solid var(--border);
									max-width: 100%;
									cursor: crosshair;
									touch-action: none;
								"
					></canvas>
					<div
						style="
									flex: 1;
									min-width: 180px;
									display: flex;
									flex-direction: column;
									gap: 0.75rem;
								"
					>
						<div class="btn-row">
							<button
								class="btn mint active"
								id="ctrlShowRigBtn"
								onclick={(e) => {
									window.toggleRigView(e.currentTarget);
								}}
							>
								Show Rig
							</button>
							<button
								class="btn"
								onclick={(e) => {
									window.resetCtrl();
								}}>↺ Reset</button
							>
						</div>
						<div
							style="
										padding: 0.75rem;
										border: 1px solid var(--border);
										background: var(--raised);
									"
						>
							<div
								style="
											font-family: var(--ff-mono);
											font-size: 9px;
											color: var(--muted);
											letter-spacing: 0.1em;
											text-transform: uppercase;
											margin-bottom: 0.5rem;
										"
							>
								Controllers
							</div>
							<div
								style="
											display: flex;
											flex-direction: column;
											gap: 0.25rem;
											font-family: var(--ff-mono);
											font-size: 10px;
										"
								id="ctrlList"
							></div>
						</div>
						<div
							id="ctrlActiveInfo"
							style="
										padding: 0.75rem;
										border: 1px solid var(--border);
										background: var(--raised);
										font-family: var(--ff-mono);
										font-size: 10px;
										color: var(--muted);
										line-height: 1.6;
										min-height: 3em;
									"
						>
							Drag a controller to pose the character.
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ SECTION 6: WALK CYCLE ══ -->
	<section class="section" id="s6">
		<div class="section-header">
			<span class="section-num">06</span>
			<h2 class="section-title">The Walk Cycle</h2>
		</div>
		<p>
			The <strong>walk cycle</strong> is the foundational animation exercise for any character rigger.
			It is a looping animation of a character walking in place, typically 16 or 24 frames (2/3 or 1 full
			second at 24fps), that can be played continuously while the character's position is moved across
			the screen.
		</p>
		<p>
			A walk cycle is built from <strong>four key poses</strong>, each representing a distinct phase
			of the walking stride. Everything between these four poses is in-between work — either
			hand-keyed or tweened from the keys. Memorise these four poses; they are the vocabulary of
			locomotion.
		</p>

		<!-- Walk cycle poses -->
		<div class="pose-strip" id="poseStrip"></div>

		<!-- DEMO 6.5: Walk Cycle -->
		<div class="demo-box" style="margin-top: 0; border-top: none">
			<div class="demo-header">
				<span class="demo-label">Demo 6.5 — Walk Cycle Builder</span>
				<span class="demo-badge gold">interactive</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 13px; color: var(--muted); margin-bottom: 1.25rem">
					Step through each key pose or play the full cycle. Adjust timing to feel the difference
					between a slow, heavy walk and a quick, light one.
				</p>
				<div style="display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: flex-start">
					<div>
						<canvas
							id="walkCanvas"
							width="320"
							height="300"
							style="background: var(--raised); border: 1px solid var(--border); display: block"
						></canvas>
						<div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem">
							<div style="font-family: var(--ff-mono); font-size: 10px; color: var(--muted)">
								Pose:
							</div>
							<div
								style="
											font-family: var(--ff-display);
											font-size: 14px;
											font-weight: 700;
											color: var(--gold);
										"
								id="walkPoseName"
							>
								Contact
							</div>
							<div
								style="
											margin-left: auto;
											font-family: var(--ff-mono);
											font-size: 10px;
											color: var(--dim);
										"
								id="walkFrameNum"
							>
								Frame 0
							</div>
						</div>
					</div>
					<div
						style="
									flex: 1;
									min-width: 200px;
									display: flex;
									flex-direction: column;
									gap: 0.85rem;
								"
					>
						<div class="btn-row">
							<button class="btn" id="walkPrevBtn">← Prev Pose</button>
							<button class="btn" id="walkNextBtn">Next Pose →</button>
							<button class="btn gold active" id="walkPlayBtn">▶ Play</button>
						</div>

						<div class="ctrl-row">
							<span class="ctrl-label">Cycle speed</span>
							<input
								type="range"
								class="gold"
								id="walkSpeed"
								min="0.3"
								max="2.5"
								step="0.1"
								value="1.0"
							/>
							<span class="ctrl-val" id="walkSpeedVal">1.0×</span>
						</div>
						<div class="ctrl-row">
							<span class="ctrl-label">Step width</span>
							<input type="range" id="walkStride" min="20" max="80" value="48" />
							<span class="ctrl-val" id="walkStrideVal">48</span>
						</div>
						<div class="ctrl-row">
							<span class="ctrl-label">Bob height</span>
							<input type="range" id="walkBob" min="0" max="20" value="10" />
							<span class="ctrl-val" id="walkBobVal">10</span>
						</div>

						<div
							style="
										padding: 0.75rem;
										border: 1px solid var(--border);
										background: var(--raised);
									"
						>
							<div
								style="
											font-family: var(--ff-mono);
											font-size: 9px;
											color: var(--muted);
											letter-spacing: 0.1em;
											text-transform: uppercase;
											margin-bottom: 0.35rem;
										"
							>
								4-Pose Timeline
							</div>
							<canvas
								id="walkTimelineCanvas"
								width="220"
								height="36"
								style="display: block; background: var(--bg); border: 1px solid var(--border)"
							></canvas>
						</div>

						<div
							id="walkPoseDesc"
							style="
										font-family: var(--ff-mono);
										font-size: 11px;
										color: var(--muted);
										line-height: 1.7;
										padding: 0.75rem;
										border: 1px solid var(--border);
										background: var(--raised);
									"
						></div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ QUIZ ══ -->
	<div class="quiz-section" id="quiz">
		<div class="quiz-header-bar">
			<div>
				<div class="quiz-title">Module Check</div>
				<div class="quiz-sub">5 questions · Rigging fundamentals</div>
			</div>
			<span class="demo-badge" style="border-color: var(--coral)">Assessment</span>
		</div>
		<div class="quiz-body">
			<div class="question" id="q1">
				<div class="q-num">Q1 of 5</div>
				<div class="q-text">
					In a bone hierarchy, you rotate the pelvis (hip) bone. Which other bones are affected?
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
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q1', 'wrong');
							}
						}}
					>
						Only the pelvis itself — child bones must be moved independently
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q1', 'correct');
							}
						}}
					>
						All bones that are children of the pelvis — the entire lower body moves with it
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q1', 'wrong');
							}
						}}
					>
						The parent of the pelvis — rotation propagates upward, not downward
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q1', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q1', 'wrong');
							}
						}}
					>
						No other bones — hierarchy only matters for translation, not rotation
					</div>
				</div>
				<div class="feedback" id="q1-feedback"></div>
			</div>

			<div class="question" id="q2">
				<div class="q-num">Q2 of 5</div>
				<div class="q-text">
					A character needs to pick up a cup from a table. Her hand must land precisely on the cup's
					handle and stay there as her arm bends. Should you use FK or IK for this arm, and why?
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
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q2', 'wrong');
							}
						}}
					>
						FK — because rotating from the shoulder gives the most control over the arm's shape
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q2', 'correct');
							}
						}}
					>
						IK — because the hand (end effector) has a fixed target position, and IK automatically
						solves the elbow and shoulder to reach it
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q2', 'wrong');
							}
						}}
					>
						FK — IK is only for legs and feet, never arms
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q2', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q2', 'wrong');
							}
						}}
					>
						Neither — you should hand-draw every frame when precision is needed
					</div>
				</div>
				<div class="feedback" id="q2-feedback"></div>
			</div>

			<div class="question" id="q3">
				<div class="q-num">Q3 of 5</div>
				<div class="q-text">
					A vertex near the elbow joint has a weight of 0.7 on the upper arm bone and 0.3 on the
					lower arm bone. When the lower arm bone rotates 90°, how is this vertex affected?
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
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q3', 'wrong');
							}
						}}
					>
						It moves exactly as if rotated 90° — any weight above 0 means full influence
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q3', 'correct');
							}
						}}
					>
						It moves partially — blending 70% of the upper arm's transform and 30% of the lower
						arm's rotation, producing smooth deformation at the joint
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q3', 'wrong');
							}
						}}
					>
						It does not move at all — it primarily belongs to the upper arm bone
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q3', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q3', 'wrong');
							}
						}}
					>
						It moves twice as far as intended — weights above 1.0 amplify motion
					</div>
				</div>
				<div class="feedback" id="q3-feedback"></div>
			</div>

			<div class="question" id="q4">
				<div class="q-num">Q4 of 5</div>
				<div class="q-text">
					What is the purpose of a controller (or handle) in a character rig?
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
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q4', 'wrong');
							}
						}}
					>
						It renders as a visible part of the final character design
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q4', 'correct');
							}
						}}
					>
						It is a non-rendered UI shape that makes bones easier to select and manipulate — it
						exists only to improve the animator's workflow
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q4', 'wrong');
							}
						}}
					>
						It automatically generates in-between frames between keyframes
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q4', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q4', 'wrong');
							}
						}}
					>
						It locks a bone so that it cannot be accidentally moved
					</div>
				</div>
				<div class="feedback" id="q4-feedback"></div>
			</div>

			<div class="question" id="q5">
				<div class="q-num">Q5 of 5</div>
				<div class="q-text">In the four key poses of a walk cycle, the "Contact" pose is when:</div>
				<div class="options">
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q5', 'wrong');
							}
						}}
					>
						Both feet are together and the body is at its highest point
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'correct');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q5', 'correct');
							}
						}}
					>
						The leading foot heel strikes the ground — the stride is at maximum width and the body
						is at mid-height
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q5', 'wrong');
							}
						}}
					>
						One foot is entirely off the ground and passing beneath the body
					</div>
					<div
						class="option"
						onclick={(e) => {
							window.answer(e.currentTarget, 'q5', 'wrong');
						}}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								window.answer(e.currentTarget, 'q5', 'wrong');
							}
						}}
					>
						The body is at its lowest point, compressing under the weight of the step
					</div>
				</div>
				<div class="feedback" id="q5-feedback"></div>
			</div>
		</div>
		<div class="quiz-score" id="quizScore">
			<div class="score-big" id="scoreNum">0/5</div>
			<div class="score-lbl" id="scoreLbl">Module 6 Complete</div>
		</div>
	</div>

	<!-- ══ NAV ══ -->
	<nav class="nav-links">
		<a href="/courses/animation/05" class="prev-link">← Module 5: Digital 2D Tools</a>
		<a href="/courses/animation/07" class="next-module">
			<div>
				<div class="next-label">Next Module</div>
				<div class="next-title">Lip Sync &amp; Expression</div>
			</div>
			<div class="next-arrow">→</div>
		</a>
	</nav>
</div>

<!-- /page-wrapper -->

<style>
	.page-wrapper {
		background: var(--anim-bg);
		color: var(--anim-text);
		font-family: var(--ff-body);
		font-size: 15px;
		line-height: 1.8;
	}

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
	.page-wrapper {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem 8rem;
	}

	/* ── HERO ── */
	.module-hero {
		padding: 5rem 0 4rem;
		border-bottom: 1px solid var(--anim-border);
		margin-bottom: 4rem;
		position: relative;
		overflow: hidden;
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
	.module-eyebrow::before,
	.module-eyebrow::after {
		content: '';
		display: inline-block;
		width: 24px;
		height: 1px;
		background: var(--anim-gold);
	}
	.module-title {
		font-size: clamp(28px, 5vw, 54px);
		color: #fff;
		margin-bottom: 0.5rem;
		letter-spacing: -0.02em;
	}
	.module-title em {
		color: var(--anim-coral);
		font-style: italic;
	}
	.module-subtitle {
		font-size: 16px;
		color: var(--anim-muted);
		font-weight: 400;
		margin-bottom: 2.5rem;
	}
	.objectives {
		border: 1px solid var(--anim-border);
		border-left: 3px solid var(--anim-coral);
		background: var(--anim-surface);
		padding: 1.5rem 2rem;
	}
	.obj-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--anim-coral);
		margin-bottom: 1rem;
	}
	.objectives ul {
		list-style: none;
	}
	.objectives li {
		padding: 0.25rem 0 0.25rem 1.5rem;
		position: relative;
		font-size: 14px;
	}
	.objectives li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--anim-gold);
	}

	/* hero deco — bone chain */
	.hero-deco {
		position: absolute;
		top: 0;
		right: 0;
		bottom: 0;
		width: 200px;
		opacity: 0.05;
		pointer-events: none;
	}

	/* ── SECTIONS ── */
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
		color: var(--anim-gold);
		letter-spacing: 0.1em;
	}
	.section-title {
		font-family: var(--ff-display);
		font-size: 26px;
		color: #fff;
		font-weight: 600;
	}

	/* ── CALLOUT ── */
	.callout {
		margin: 1.75rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--anim-lavender);
		background: color-mix(in srgb, var(--anim-lavender) 5%, var(--anim-surface));
		font-size: 13.5px;
	}
	.callout.gold {
		border-color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 5%, var(--anim-surface));
	}
	.callout.coral {
		border-color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 5%, var(--anim-surface));
	}
	.callout.mint {
		border-color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 5%, var(--anim-surface));
	}
	.callout-label {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		margin-bottom: 0.4rem;
		font-weight: 500;
		color: var(--anim-lavender);
	}
	.callout.gold .callout-label {
		color: var(--anim-gold);
	}
	.callout.coral .callout-label {
		color: var(--anim-coral);
	}
	.callout.mint .callout-label {
		color: var(--anim-mint);
	}

	/* ── DEMO BOX ── */
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
	.demo-badge {
		font-family: var(--ff-mono);
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid var(--anim-coral);
		color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 10%, transparent);
	}
	.demo-badge.gold {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
		background: color-mix(in srgb, var(--anim-gold) 10%, transparent);
	}
	.demo-badge.mint {
		border-color: var(--anim-mint);
		color: var(--anim-mint);
		background: color-mix(in srgb, var(--anim-mint) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}
	canvas {
		display: block;
	}

	/* ── CONTROLS ── */
	:global(.btn) {
		background: transparent;
		border: 1px solid var(--anim-border2);
		color: var(--anim-text);
		padding: 5px 14px;
		font-family: var(--ff-mono);
		font-size: 10px;
		cursor: pointer;
		transition: all 0.15s;
		letter-spacing: 0.05em;
		user-select: none;
	}
	:global(.btn:hover) {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
	}
	:global(.btn.active) {
		border-color: var(--anim-coral);
		color: var(--anim-coral);
		background: color-mix(in srgb, var(--anim-coral) 12%, transparent);
	}
	.btn.gold:hover,
	:global(.btn.gold.active) {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
	}
	:global(.btn.gold.active) {
		background: color-mix(in srgb, var(--anim-gold) 12%, transparent);
	}
	:global(.btn.mint:hover),
	:global(.btn.mint.active) {
		border-color: var(--anim-mint);
		color: var(--anim-mint);
	}
	:global(.btn.mint.active) {
		background: color-mix(in srgb, var(--anim-mint) 12%, transparent);
	}
	:global(.btn-row) {
		display: flex;
		gap: 0.4rem;
		flex-wrap: wrap;
	}
	:global(.ctrl-row) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0.35rem 0;
		flex-wrap: wrap;
	}
	:global(.ctrl-label) {
		font-family: var(--ff-mono);
		font-size: 10px;
		color: var(--anim-muted);
		min-width: 80px;
	}
	:global(.ctrl-val) {
		font-family: var(--ff-mono);
		font-size: 11px;
		color: var(--anim-coral);
		font-weight: 500;
		min-width: 44px;
	}
	:global(input[type='range']) {
		flex: 1;
		-webkit-appearance: none;
		height: 2px;
		background: var(--anim-border2);
		outline: none;
		min-width: 80px;
	}
	:global(input[type='range']::-webkit-slider-thumb) {
		-webkit-appearance: none;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--anim-coral);
		cursor: pointer;
		border: 2px solid var(--anim-bg);
	}
	input[type='range'].gold::-webkit-slider-thumb {
		background: var(--anim-gold);
	}
	input[type='range'].mint::-webkit-slider-thumb {
		background: var(--anim-mint);
	}

	/* ── HIERARCHY TREE ── */
	.hier-tree {
		font-family: var(--ff-mono);
		font-size: 11px;
		line-height: 1.8;
		padding: 0.75rem 1rem;
		border: 1px solid var(--anim-border);
		background: var(--anim-bg);
	}
	.hier-node {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		cursor: pointer;
		padding: 2px 4px;
		border-radius: 2px;
		transition: background 0.12s;
	}
	.hier-node:hover {
		background: var(--anim-raised);
	}
	.hier-node.selected {
		background: color-mix(in srgb, var(--anim-coral) 10%, var(--anim-raised));
	}
	.hier-node .hier-icon {
		color: var(--anim-coral);
		font-size: 10px;
	}
	.hier-node .hier-name {
		color: var(--anim-text);
	}
	.hier-node .hier-type {
		color: var(--anim-dim);
		font-size: 9px;
		margin-left: auto;
	}
	.hier-indent {
		padding-left: 1.2rem;
		border-left: 1px solid var(--anim-border);
		margin-left: 0.5rem;
	}

	/* ── FK/IK SPLIT ── */
	.fkik-split {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1px;
		background: var(--anim-border);
		border: 1px solid var(--anim-border);
	}
	@media (max-width: 560px) {
		.fkik-split {
			grid-template-columns: 1fr;
		}
	}
	.fkik-panel {
		background: var(--anim-surface);
		display: flex;
		flex-direction: column;
	}
	.fkik-header {
		padding: 0.65rem 1rem;
		border-bottom: 1px solid var(--anim-border);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.fkik-title {
		font-family: var(--ff-display);
		font-size: 15px;
		font-weight: 700;
		color: #fff;
	}
	.fkik-tag {
		font-family: var(--ff-mono);
		font-size: 9px;
		color: var(--anim-muted);
	}

	/* ── WALK CYCLE POSES ── */
	.pose-strip {
		display: flex;
		gap: 1px;
		background: var(--anim-border);
		border: 1px solid var(--anim-border);
		overflow: hidden;
	}
	.pose-card {
		flex: 1;
		background: var(--anim-surface);
		display: flex;
		flex-direction: column;
		cursor: pointer;
		transition: background 0.12s;
		min-width: 80px;
	}
	.pose-card:hover {
		background: var(--anim-raised);
	}
	.pose-card.active {
		background: color-mix(in srgb, var(--anim-gold) 6%, var(--anim-raised));
	}
	.pose-card.active .pose-name {
		color: var(--anim-gold);
	}
	.pose-num {
		font-family: var(--ff-mono);
		font-size: 9px;
		color: var(--anim-dim);
		padding: 0.4rem 0.75rem 0.1rem;
		letter-spacing: 0.1em;
	}
	.pose-name {
		font-family: var(--ff-display);
		font-size: 13px;
		font-weight: 700;
		color: var(--anim-text);
		padding: 0 0.75rem 0.3rem;
	}
	.pose-desc {
		font-family: var(--ff-mono);
		font-size: 9px;
		color: var(--anim-muted);
		padding: 0 0.75rem 0.5rem;
		line-height: 1.4;
	}

	/* ── WEIGHT LEGEND ── */
	.weight-legend {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin: 0.5rem 0;
	}
	.wl-item {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-family: var(--ff-mono);
		font-size: 10px;
		color: var(--anim-muted);
	}
	.wl-swatch {
		width: 12px;
		height: 12px;
		border-radius: 2px;
		flex-shrink: 0;
	}

	/* ── QUIZ ── */
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
	:global(.q-num) {
		font-family: var(--ff-mono);
		font-size: 10px;
		letter-spacing: 0.1em;
		color: var(--anim-coral);
		margin-bottom: 0.4rem;
	}
	:global(.q-text) {
		font-size: 14px;
		color: #fff;
		margin-bottom: 0.75rem;
		line-height: 1.6;
	}
	:global(.options) {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
	:global(.option) {
		padding: 0.65rem 1rem;
		border: 1px solid var(--anim-border);
		cursor: pointer;
		font-size: 13px;
		font-family: var(--ff-body);
		transition: all 0.15s;
		user-select: none;
		background: var(--anim-bg);
	}
	:global(.option:hover) {
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
	:global(.feedback) {
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

	/* ── NAV ── */
	.nav-links {
		display: flex;
		justify-content: space-between;
		margin-top: 4rem;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.prev-link {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 1.5rem 2rem;
		border: 1px solid var(--anim-border);
		background: var(--anim-surface);
		text-decoration: none;
		transition: all 0.2s;
		color: var(--anim-muted);
		font-family: var(--ff-mono);
		font-size: 11px;
	}
	.prev-link:hover {
		border-color: var(--anim-muted);
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
		min-width: 260px;
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
		.page-wrapper {
			padding: 0 1.25rem 6rem;
		}
	}
</style>
