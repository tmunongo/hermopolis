<script>
	/* eslint-disable @typescript-eslint/no-unused-vars */
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
		/* ══════════════════════════ MATH ══════════════════════════ */
		function v3(x, y, z) {
			return [x, y, z];
		}
		function v3add(a, b) {
			return [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
		}
		function v3sub(a, b) {
			return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
		}
		function v3scale(v, s) {
			return [v[0] * s, v[1] * s, v[2] * s];
		}
		function v3dot(a, b) {
			return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
		}
		function v3cross(a, b) {
			return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
		}
		function v3len(v) {
			return Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
		}
		function v3norm(v) {
			const l = v3len(v) || 1;
			return [v[0] / l, v[1] / l, v[2] / l];
		}

		// 4×4 matrices (column-major flat array, 16 elements)
		function mat4id() {
			return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
		}
		function mat4mul(A, B) {
			const R = new Array(16).fill(0);
			for (let i = 0; i < 4; i++)
				for (let j = 0; j < 4; j++)
					for (let k = 0; k < 4; k++) R[i + j * 4] += A[i + k * 4] * B[k + j * 4];
			return R;
		}
		function mat4mulvec4(M, [x, y, z, w]) {
			return [
				M[0] * x + M[4] * y + M[8] * z + M[12] * w,
				M[1] * x + M[5] * y + M[9] * z + M[13] * w,
				M[2] * x + M[6] * y + M[10] * z + M[14] * w,
				M[3] * x + M[7] * y + M[11] * z + M[15] * w
			];
		}
		function rotY(a) {
			const c = Math.cos(a),
				s = Math.sin(a);
			return [c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1];
		}
		function rotX(a) {
			const c = Math.cos(a),
				s = Math.sin(a);
			return [1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1];
		}
		function perspective4(fovDeg, aspect, near, far) {
			const f = 1 / Math.tan((fovDeg * Math.PI) / 360);
			const nf = 1 / (near - far);
			return [
				f / aspect,
				0,
				0,
				0,
				0,
				f,
				0,
				0,
				0,
				0,
				(far + near) * nf,
				-1,
				0,
				0,
				2 * far * near * nf,
				0
			];
		}
		function lookAt4(eye, target, up) {
			const f = v3norm(v3sub(target, eye));
			const r = v3norm(v3cross(f, v3norm(up)));
			const u = v3cross(r, f);
			return [
				r[0],
				u[0],
				-f[0],
				0,
				r[1],
				u[1],
				-f[1],
				0,
				r[2],
				u[2],
				-f[2],
				0,
				-v3dot(r, eye),
				-v3dot(u, eye),
				v3dot(f, eye),
				1
			];
		}
		function fmt2(v) {
			return (v >= 0 ? '+' : '') + v.toFixed(2);
		}

		/* ══════════════════════════ 3D PIPELINE STAGES ══════════════════════════ */
		const p3dDetails = [
			`<strong style="color:var(--accent)">Model Space</strong> — Vertices of a mesh defined around their own origin. A cube's corners are at (±1, ±1, ±1). This data never changes — it is uploaded to the VBO once and stays. The model matrix transforms it into world space.`,
			`<strong style="color:var(--accent)">× Model Matrix</strong> — Translates, rotates, and scales the mesh into world space. Composed of the same translation/rotation/scale matrices from Module 3, now 4×4. Applying this matrix places the object at the right position, orientation, and size in the scene.`,
			`<strong style="color:var(--accent)">× View Matrix</strong> — Transforms world space into camera space: the camera is at the origin, looking down −Z. Built with look_at(eye, target, up). The world "moves around the camera" rather than the camera moving through the world — mathematically equivalent, computationally simpler.`,
			`<strong style="color:var(--accent)">× Projection Matrix</strong> — Applies perspective (or orthographic) distortion. After this, coordinates are in clip space — a 4D homogeneous space. Points within the view frustum have |x/w|, |y/w|, |z/w| ≤ 1 after the perspective divide. This stage is where depth foreshortening is baked in.`,
			`<strong style="color:var(--accent)">÷ w (Perspective Divide)</strong> — The hardware automatically divides x, y, z by w. For perspective projection, w = −camera_z, so distant vertices get larger denominators and smaller NDC coordinates — they appear smaller on screen. After this step, NDC: x,y ∈ [−1,1], z ∈ [−1,1] (near/far mapped).`,
			`<strong style="color:var(--accent)">Viewport Transform</strong> — Maps NDC (−1 to +1 in x and y) to actual pixel coordinates. x=−1 → left edge, x=+1 → right edge. z is mapped to depth buffer range [0,1]. This transform is configured once with <code>ctx.viewport</code> or automatically matches the framebuffer size.`
		];
		function show3DStage(i, el) {
			document.querySelectorAll('.p3d-stage').forEach((s) => s.classList.remove('active'));
			el.classList.add('active');
			document.getElementById('p3d-detail').innerHTML = p3dDetails[i];
		}

		/* ══════════════════════════ PROJECTION DEMO ══════════════════════════ */
		const projC = document.getElementById('proj-canvas');
		const projX = projC.getContext('2d');
		let projMode = 'perspective';
		function setProj(m, btn) {
			projMode = m;
			document.querySelectorAll('[id^=proj-]').forEach((b) => {
				if (b.tagName === 'BUTTON') b.classList.remove('active');
			});
			btn.classList.add('active');
			drawProj();
		}

		const PROJ_CUBE_VERTS = [
			[-1, -1, -1],
			[1, -1, -1],
			[1, 1, -1],
			[-1, 1, -1],
			[-1, -1, 1],
			[1, -1, 1],
			[1, 1, 1],
			[-1, 1, 1]
		];
		const PROJ_EDGES = [
			[0, 1],
			[1, 2],
			[2, 3],
			[3, 0],
			[4, 5],
			[5, 6],
			[6, 7],
			[7, 4],
			[0, 4],
			[1, 5],
			[2, 6],
			[3, 7]
		];

		function drawProj() {
			const W = projC.width,
				H = projC.height;
			projX.clearRect(0, 0, W, H);
			projX.fillStyle = '#030609';
			projX.fillRect(0, 0, W, H);
			const fov = parseInt(document.getElementById('sl-fov').value);
			const camZ = parseInt(document.getElementById('sl-camz').value);
			document.getElementById('vl-fov').textContent = fov + '°';
			document.getElementById('vl-camz').textContent = camZ.toFixed(1);
			const halfW = W / 2 - 40;
			// Left: frustum diagram
			drawFrustumDiagram(projX, 40, 20, halfW, H - 40, fov, camZ, projMode);
			// Right: projected cube
			drawProjectedCube(projX, W / 2 + 20, 20, halfW, H - 40, fov, camZ, projMode);
			// Info
			const near = 0.1,
				far = 20,
				aspect = 1;
			const f = 1 / Math.tan((fov * Math.PI) / 360);
			document.getElementById('proj-info').innerHTML =
				projMode === 'perspective'
					? `<span style="color:var(--muted)">f = 1/tan(${fov}°/2) = <span style="color:var(--accent)">${f.toFixed(3)}</span> &nbsp;·&nbsp; objects at z=${camZ} appear ${(f / camZ).toFixed(2)}× smaller than at z=1</span>`
					: `<span style="color:var(--muted)">Orthographic: all objects same size regardless of depth &nbsp;·&nbsp; no w divide</span>`;
		}
		function drawFrustumDiagram(ctx, x, y, w, h, fov, camZ, mode) {
			ctx.fillStyle = '#0c1620';
			ctx.fillRect(x, y, w, h);
			ctx.strokeStyle = '#142030';
			ctx.lineWidth = 1;
			ctx.strokeRect(x, y, w, h);
			ctx.font = '9px IBM Plex Mono';
			ctx.fillStyle = '#2a4860';
			ctx.textAlign = 'center';
			ctx.fillText(
				mode === 'perspective' ? 'PERSPECTIVE FRUSTUM' : 'ORTHOGRAPHIC FRUSTUM',
				x + w / 2,
				y + 14
			);
			const cy = y + h / 2,
				scaleH = h * 0.35;
			const nearX = x + w * 0.15,
				farX = x + w * 0.85;
			const halfAngle = ((fov / 2) * Math.PI) / 180;
			if (mode === 'perspective') {
				const nearH = scaleH * 0.15;
				const farH = scaleH;
				// Frustum outline
				ctx.beginPath();
				ctx.moveTo(x + w * 0.08, cy);
				ctx.lineTo(nearX, cy - nearH);
				ctx.lineTo(farX, cy - farH);
				ctx.moveTo(nearX, cy + nearH);
				ctx.lineTo(farX, cy + farH);
				ctx.moveTo(x + w * 0.08, cy);
				ctx.lineTo(nearX, cy + nearH);
				ctx.strokeStyle = '#1c3044';
				ctx.lineWidth = 1.5;
				ctx.stroke();
				// Top/bottom lines
				ctx.beginPath();
				ctx.moveTo(nearX, cy - nearH);
				ctx.lineTo(nearX, cy + nearH);
				ctx.moveTo(farX, cy - farH);
				ctx.lineTo(farX, cy + farH);
				ctx.strokeStyle = '#22d3ee40';
				ctx.lineWidth = 1;
				ctx.stroke();
				// Camera dot
				ctx.beginPath();
				ctx.arc(x + w * 0.08, cy, 5, 0, Math.PI * 2);
				ctx.fillStyle = '#0ea5e9';
				ctx.fill();
				ctx.fillStyle = '#0ea5e9';
				ctx.textAlign = 'center';
				ctx.font = '9px IBM Plex Mono';
				ctx.fillText('cam', x + w * 0.08, cy - 12);
				ctx.fillText(`z=${camZ}`, farX, cy - farH - 8);
			} else {
				const bh = scaleH * 0.5;
				ctx.fillStyle = '#22d3ee08';
				ctx.fillRect(nearX, cy - bh, farX - nearX, bh * 2);
				ctx.beginPath();
				ctx.moveTo(nearX, cy - bh);
				ctx.lineTo(farX, cy - bh);
				ctx.moveTo(nearX, cy + bh);
				ctx.lineTo(farX, cy + bh);
				ctx.moveTo(nearX, cy - bh);
				ctx.lineTo(nearX, cy + bh);
				ctx.moveTo(farX, cy - bh);
				ctx.lineTo(farX, cy + bh);
				ctx.strokeStyle = '#22d3ee50';
				ctx.lineWidth = 1.5;
				ctx.stroke();
				ctx.beginPath();
				ctx.arc(nearX - 20, cy, 5, 0, Math.PI * 2);
				ctx.fillStyle = '#0ea5e9';
				ctx.fill();
			}
		}
		function drawProjectedCube(ctx, x, y, w, h, fov, camZ, mode) {
			ctx.fillStyle = '#0c1620';
			ctx.fillRect(x, y, w, h);
			ctx.strokeStyle = '#142030';
			ctx.lineWidth = 1;
			ctx.strokeRect(x, y, w, h);
			ctx.font = '9px IBM Plex Mono';
			ctx.fillStyle = '#2a4860';
			ctx.textAlign = 'center';
			ctx.fillText('PROJECTED VIEW', x + w / 2, y + 14);
			const cx = x + w / 2,
				cy = y + h / 2;
			// Project each vertex
			const projected = PROJ_CUBE_VERTS.map(([vx, vy, vz]) => {
				const wvz = vz - camZ; // move cube in front of camera
				if (mode === 'perspective') {
					const f = 1 / Math.tan((fov * Math.PI) / 360);
					const ww = -wvz || 0.001;
					return [((f * vx) / ww) * w * 0.3 + cx, ((-f * vy) / ww) * h * 0.3 + cy];
				} else {
					return [vx * w * 0.2 + cx, -vy * h * 0.2 + cy];
				}
			});
			// Edges
			PROJ_EDGES.forEach(([a, b]) => {
				ctx.beginPath();
				ctx.moveTo(projected[a][0], projected[a][1]);
				ctx.lineTo(projected[b][0], projected[b][1]);
				ctx.strokeStyle = '#0ea5e9';
				ctx.lineWidth = 1.5;
				ctx.stroke();
			});
			// Verts
			projected.forEach(([px, py]) => {
				ctx.beginPath();
				ctx.arc(px, py, 3, 0, Math.PI * 2);
				ctx.fillStyle = '#7dd3fc';
				ctx.fill();
			});
		}
		['sl-fov', 'sl-camz'].forEach((id) =>
			document.getElementById(id).addEventListener('input', drawProj)
		);
		drawProj();

		/* ══════════════════════════ LOOK_AT DEMO ══════════════════════════ */
		const laC = document.getElementById('lookat-canvas');
		const laX = laC.getContext('2d');

		function buildLookAt() {
			const ex = parseFloat(document.getElementById('cam-x').value);
			const ey = parseFloat(document.getElementById('cam-y').value);
			const ez = parseFloat(document.getElementById('cam-z').value);
			document.getElementById('cam-x-v').textContent = ex.toFixed(1);
			document.getElementById('cam-y-v').textContent = ey.toFixed(1);
			document.getElementById('cam-z-v').textContent = ez.toFixed(1);
			const eye = [ex, ey, ez],
				target = [0, 0, 0],
				up = [0, 1, 0];
			const f = v3norm(v3sub(target, eye));
			const r = v3norm(v3cross(f, v3norm(up)));
			const u = v3cross(r, f);
			const V = lookAt4(eye, target, up);
			// Display matrix
			const mc = document.getElementById('view-mat');
			mc.innerHTML = '';
			for (let row = 0; row < 4; row++) {
				for (let col = 0; col < 4; col++) {
					const el = document.createElement('div');
					el.className = 'm4c';
					el.textContent = fmt2(V[row + col * 4]);
					mc.appendChild(el);
				}
			}
			document.getElementById('la-eye').textContent =
				`(${ex.toFixed(1)}, ${ey.toFixed(1)}, ${ez.toFixed(1)})`;
			document.getElementById('la-fwd').textContent =
				`(${f[0].toFixed(2)}, ${f[1].toFixed(2)}, ${f[2].toFixed(2)})`;
			document.getElementById('la-right').textContent =
				`(${r[0].toFixed(2)}, ${r[1].toFixed(2)}, ${r[2].toFixed(2)})`;
			document.getElementById('la-up').textContent =
				`(${u[0].toFixed(2)}, ${u[1].toFixed(2)}, ${u[2].toFixed(2)})`;
			drawLookAt(eye, f, r, u, V);
		}

		function drawLookAt(eye, f, r, u, V) {
			const W = laC.width,
				H = laC.height;
			laX.clearRect(0, 0, W, H);
			laX.fillStyle = '#030609';
			laX.fillRect(0, 0, W, H);
			// Top-down view (x-z plane)
			const cx = W / 2,
				cy = H / 2,
				scale = 28;
			laX.strokeStyle = '#0c1620';
			laX.lineWidth = 1;
			for (let x = 0; x < W; x += scale) {
				laX.beginPath();
				laX.moveTo(x, 0);
				laX.lineTo(x, H);
				laX.stroke();
			}
			for (let y = 0; y < H; y += scale) {
				laX.beginPath();
				laX.moveTo(0, y);
				laX.lineTo(W, y);
				laX.stroke();
			}
			// Axes
			laX.strokeStyle = '#142030';
			laX.lineWidth = 1;
			laX.beginPath();
			laX.moveTo(0, cy);
			laX.lineTo(W, cy);
			laX.stroke();
			laX.beginPath();
			laX.moveTo(cx, 0);
			laX.lineTo(cx, H);
			laX.stroke();
			laX.font = '9px IBM Plex Mono';
			laX.fillStyle = '#2a4860';
			laX.textAlign = 'left';
			laX.fillText('X', cx + 4, H - 4);
			laX.fillText('Z', W - 10, cy - 4);
			// Target
			laX.beginPath();
			laX.arc(cx, cy, 6, 0, Math.PI * 2);
			laX.fillStyle = '#f9731640';
			laX.fill();
			laX.strokeStyle = '#f97316';
			laX.lineWidth = 1;
			laX.stroke();
			laX.fillStyle = '#f97316';
			laX.textAlign = 'center';
			laX.fillText('target(0,0,0)', cx, cy - 12);
			// Camera (project eye onto xz plane)
			const ex = cx + eye[0] * scale,
				ez = cy + eye[2] * scale;
			laX.beginPath();
			laX.arc(ex, ez, 8, 0, Math.PI * 2);
			laX.fillStyle = '#0ea5e940';
			laX.fill();
			laX.strokeStyle = '#0ea5e9';
			laX.lineWidth = 2;
			laX.stroke();
			laX.fillStyle = '#0ea5e9';
			laX.textAlign = 'center';
			laX.fillText('eye', ex, ez - 14);
			// Forward ray
			laX.beginPath();
			laX.moveTo(ex, ez);
			laX.lineTo(ex + f[0] * scale * 3, ez + f[2] * scale * 3);
			laX.strokeStyle = '#34d399';
			laX.lineWidth = 1.5;
			laX.setLineDash([3, 4]);
			laX.stroke();
			laX.setLineDash([]);
			laX.fillStyle = '#34d399';
			laX.textAlign = 'left';
			laX.fillText('f', ex + f[0] * scale * 3 + 4, ez + f[2] * scale * 3);
			// Right ray
			laX.beginPath();
			laX.moveTo(ex, ez);
			laX.lineTo(ex + r[0] * scale * 2, ez + r[2] * scale * 2);
			laX.strokeStyle = '#ef4444';
			laX.lineWidth = 1.5;
			laX.stroke();
			laX.fillStyle = '#ef4444';
			laX.fillText('r', ex + r[0] * scale * 2 + 4, ez + r[2] * scale * 2);
		}
		['cam-x', 'cam-y', 'cam-z'].forEach((id) =>
			document.getElementById(id).addEventListener('input', buildLookAt)
		);
		buildLookAt();

		/* ══════════════════════════ DEPTH DEMO ══════════════════════════ */
		const depC = document.getElementById('depth-canvas');
		const depX = depC.getContext('2d');
		let depthTestOn = true,
			depthBuffer = [],
			colorBuffer = [],
			depthTris = [];
		const DEP_W = depC.width,
			DEP_H = depC.height;

		function depthReset() {
			depthBuffer = new Array(DEP_W * DEP_H).fill(1);
			colorBuffer = new Array(DEP_W * DEP_H * 3).fill(0);
			depthTris = [];
			drawDepth();
		}
		function toggleDepthTest() {
			depthTestOn = !depthTestOn;
			document.getElementById('depth-test-btn').textContent =
				'Depth test: ' + (depthTestOn ? 'ON' : 'OFF');
			document.getElementById('depth-test-btn').classList.toggle('o', depthTestOn);
			depthReset();
		}

		const DEPTH_COLORS = ['#0ea5e9', '#f97316', '#22d3ee', '#a3e635', '#e879f9', '#fbbf24'];
		function depthDraw() {
			const tri = {
				x0: 30 + Math.random() * (DEP_W - 100),
				y0: 20 + Math.random() * (DEP_H - 80),
				x1: 0,
				y1: 0,
				x2: 0,
				y2: 0,
				depth0: Math.random(),
				depth1: Math.random(),
				depth2: Math.random(),
				color: DEPTH_COLORS[depthTris.length % DEPTH_COLORS.length],
				order: depthTris.length + 1
			};
			tri.x1 = tri.x0 + (-60 + Math.random() * 120);
			tri.y1 = tri.y0 + (20 + Math.random() * 60);
			tri.x2 = tri.x0 + (-60 + Math.random() * 120);
			tri.y2 = tri.y0 + (20 + Math.random() * 60);
			depthTris.push(tri);
			// Rasterize into buffers
			const minX = Math.max(0, Math.floor(Math.min(tri.x0, tri.x1, tri.x2)));
			const maxX = Math.min(DEP_W - 1, Math.ceil(Math.max(tri.x0, tri.x1, tri.x2)));
			const minY = Math.max(0, Math.floor(Math.min(tri.y0, tri.y1, tri.y2)));
			const maxY = Math.min(DEP_H - 1, Math.ceil(Math.max(tri.y0, tri.y1, tri.y2)));
			const col = [
				parseInt(tri.color.slice(1, 3), 16),
				parseInt(tri.color.slice(3, 5), 16),
				parseInt(tri.color.slice(5, 7), 16)
			];
			for (let y = minY; y <= maxY; y++)
				for (let x = minX; x <= maxX; x++) {
					const d = (tri.x1 - tri.x0) * (y - tri.y0) - (tri.y1 - tri.y0) * (x - tri.x0);
					const e = (tri.x2 - tri.x1) * (y - tri.y1) - (tri.y2 - tri.y1) * (x - tri.x1);
					const f = (tri.x0 - tri.x2) * (y - tri.y2) - (tri.y0 - tri.y2) * (x - tri.x2);
					if ((d >= 0 && e >= 0 && f >= 0) || (d <= 0 && e <= 0 && f <= 0)) {
						const sum = Math.abs(d) + Math.abs(e) + Math.abs(f) || 1;
						const w0 = Math.abs(d) / sum,
							w1 = Math.abs(e) / sum,
							w2 = Math.abs(f) / sum;
						const fragZ = tri.depth0 * w0 + tri.depth1 * w1 + tri.depth2 * w2;
						const idx = y * DEP_W + x;
						if (!depthTestOn || fragZ < depthBuffer[idx]) {
							depthBuffer[idx] = fragZ;
							colorBuffer[idx * 3] = col[0];
							colorBuffer[idx * 3 + 1] = col[1];
							colorBuffer[idx * 3 + 2] = col[2];
						}
					}
				}
			drawDepth();
		}

		function drawDepth() {
			depX.fillStyle = '#030609';
			depX.fillRect(0, 0, DEP_W, DEP_H);
			// Colour buffer
			const id = depX.createImageData(DEP_W, DEP_H);
			for (let i = 0; i < DEP_W * DEP_H; i++) {
				id.data[i * 4] = colorBuffer[i * 3];
				id.data[i * 4 + 1] = colorBuffer[i * 3 + 1];
				id.data[i * 4 + 2] = colorBuffer[i * 3 + 2];
				id.data[i * 4 + 3] =
					colorBuffer[i * 3] || colorBuffer[i * 3 + 1] || colorBuffer[i * 3 + 2] ? 255 : 0;
			}
			depX.putImageData(id, 0, 0);
			// Triangle outlines
			depthTris.forEach((t) => {
				depX.beginPath();
				depX.moveTo(t.x0, t.y0);
				depX.lineTo(t.x1, t.y1);
				depX.lineTo(t.x2, t.y2);
				depX.closePath();
				depX.strokeStyle = t.color + '60';
				depX.lineWidth = 1;
				depX.stroke();
				depX.font = '11px IBM Plex Mono';
				depX.fillStyle = t.color;
				depX.textAlign = 'center';
				depX.fillText('#' + t.order, (t.x0 + t.x1 + t.x2) / 3, (t.y0 + t.y1 + t.y2) / 3 + 4);
			});
			document.getElementById('depth-info').innerHTML =
				`<span style="color:var(--muted)">triangles drawn: <span style="color:var(--accent4)">${depthTris.length}</span></span>` +
				`<span style="color:var(--muted)">depth test: <span style="color:${depthTestOn ? 'var(--accent4)' : 'var(--accent2)'}">${depthTestOn ? 'ON — correct Z-order' : 'OFF — last drawn wins'}</span></span>` +
				`<span style="color:var(--muted)">depth buffer: 24-bit float [0,1]</span>`;
		}
		depthReset();

		/* ══════════════════════════ NORMAL DEMO ══════════════════════════ */
		const normC = document.getElementById('normal-canvas');
		const normX = normC.getContext('2d');
		let lightAngleNorm = 45,
			normDrag = false;

		function drawNormal() {
			const W = normC.width,
				H = normC.height;
			normX.clearRect(0, 0, W, H);
			normX.fillStyle = '#030609';
			normX.fillRect(0, 0, W, H);
			const cx = W / 2,
				cy = H * 0.6;
			const lightRad = (lightAngleNorm * Math.PI) / 180;
			const lx = Math.cos(lightRad) * 110,
				ly = -Math.sin(lightRad) * 110;
			const N = [0, -1, 0]; // surface normal (pointing up, y-up in screen is down)
			const L = v3norm([lx, ly, 0]);
			const dot = Math.max(0, v3dot(N, [L[0], L[1], L[2]]));
			const ambient = 0.15,
				total = Math.min(1, ambient + dot * 0.85);

			// Surface
			const surfColor = `rgb(${Math.round(56 * total)},${Math.round(189 * total)},${Math.round(248 * total)})`;
			normX.fillStyle = surfColor + '40';
			normX.fillRect(cx - 120, cy, 240, 40);
			normX.strokeStyle = surfColor;
			normX.lineWidth = 2;
			normX.strokeRect(cx - 120, cy, 240, 40);
			normX.font = '10px IBM Plex Mono';
			normX.fillStyle = surfColor;
			normX.textAlign = 'center';
			normX.fillText('surface', cx, cy + 26);

			// Normal vector
			normX.beginPath();
			normX.moveTo(cx, cy);
			normX.lineTo(cx, cy - 90);
			normX.strokeStyle = '#22d3ee';
			normX.lineWidth = 2;
			normX.stroke();
			normX.beginPath();
			normX.moveTo(cx, cy - 90);
			normX.lineTo(cx - 6, cy - 80);
			normX.lineTo(cx + 6, cy - 80);
			normX.closePath();
			normX.fillStyle = '#22d3ee';
			normX.fill();
			normX.font = '11px IBM Plex Mono';
			normX.fillStyle = '#22d3ee';
			normX.textAlign = 'left';
			normX.fillText('N (0,1,0)', cx + 8, cy - 85);

			// Light direction
			normX.beginPath();
			normX.moveTo(cx, cy);
			normX.lineTo(cx + lx, cy + ly);
			normX.strokeStyle = '#fbbf24';
			normX.lineWidth = 2;
			normX.stroke();
			normX.beginPath();
			normX.arc(cx + lx, cy + ly, 6, 0, Math.PI * 2);
			normX.fillStyle = '#fbbf2440';
			normX.fill();
			normX.strokeStyle = '#fbbf24';
			normX.lineWidth = 1.5;
			normX.stroke();
			normX.font = '11px IBM Plex Mono';
			normX.fillStyle = '#fbbf24';
			normX.textAlign = 'left';
			normX.fillText('L (drag)', cx + lx + 8, cy + ly + 4);

			// Angle arc
			const angleDeg =
				(Math.acos(
					Math.max(-1, Math.min(1, v3dot(N, [0, -1, 0]) + v3dot([0, 0, 0], [L[0], L[1], 0])))
				) *
					180) /
				Math.PI;
			const dotAngle =
				(Math.acos(Math.max(-1, Math.min(1, dot + (dot < 0.001 ? 0 : 0)))) * 180) / Math.PI;

			normX.font = '11px IBM Plex Mono';
			normX.fillStyle = '#a3e635';
			normX.textAlign = 'center';
			normX.fillText(`dot(N,L) = ${dot.toFixed(3)}`, cx, cy - 110);
			normX.fillStyle = '#f97316';
			normX.fillText(`angle = ${Math.round(90 - lightAngleNorm)}°`, cx, cy - 126);

			// Info
			document.getElementById('norm-n').textContent = '(0.0, 1.0, 0.0)';
			document.getElementById('norm-l').textContent =
				`(${L[0].toFixed(2)}, ${L[1].toFixed(2)}, 0.0)`;
			document.getElementById('norm-dot').textContent = dot.toFixed(4);
			document.getElementById('norm-diff').textContent = (dot * 0.85).toFixed(4);
			document.getElementById('norm-total').textContent = total.toFixed(4);
			document.getElementById('normal-color-preview').style.background =
				`rgb(${Math.round(56 * total)},${Math.round(189 * total)},${Math.round(248 * total)})`;
		}

		normC.addEventListener('mousemove', (e) => {
			const r = normC.getBoundingClientRect();
			const mx = ((e.clientX - r.left) / r.width) * normC.width - normC.width / 2;
			const my = ((e.clientY - r.top) / r.height) * normC.height - normC.height * 0.6;
			lightAngleNorm = ((Math.atan2(-my, mx) * 180) / Math.PI + 360) % 360;
			drawNormal();
		});
		drawNormal();

		/* ══════════════════════════ 3D CUBE ══════════════════════════ */
		const cubeC = document.getElementById('cube-canvas');
		const cubeX = cubeC.getContext('2d');
		let cubeRotY = 0,
			cubeRotX = 0.4,
			cubeRunning = true,
			cubeDrag = null,
			cubePrevMouse = { x: 0, y: 0 };
		let cubeDepthTest = true,
			cubeLighting = true,
			cubeWire = false,
			cubeShowNormals = false;
		let cubeRAF = null,
			cubeLastT = performance.now();

		// Cube geometry: 6 faces, each as 2 triangles
		const FACE_COLORS = ['#3b82f6', '#f97316', '#22c55e', '#ef4444', '#fbbf24', '#a855f7'];
		const FACE_NORMALS = [
			[0, 0, 1],
			[0, 0, -1],
			[0, 1, 0],
			[0, -1, 0],
			[1, 0, 0],
			[-1, 0, 0]
		];
		const FACE_VERTS = [
			[
				[-1, -1, 1],
				[1, -1, 1],
				[1, 1, 1],
				[-1, 1, 1]
			], // front
			[
				[1, -1, -1],
				[-1, -1, -1],
				[-1, 1, -1],
				[1, 1, -1]
			], // back
			[
				[-1, 1, -1],
				[1, 1, -1],
				[1, 1, 1],
				[-1, 1, 1]
			], // top
			[
				[-1, -1, 1],
				[1, -1, 1],
				[1, -1, -1],
				[-1, -1, -1]
			], // bottom
			[
				[1, -1, 1],
				[1, -1, -1],
				[1, 1, -1],
				[1, 1, 1]
			], // right
			[
				[-1, -1, -1],
				[-1, -1, 1],
				[-1, 1, 1],
				[-1, 1, -1]
			] // left
		];

		function toggleCube() {
			cubeRunning = !cubeRunning;
			document.getElementById('cube-play-btn').textContent = cubeRunning ? '⏸ Pause' : '▶ Play';
			if (cubeRunning) cubeLoop();
		}
		function resetCube() {
			cubeRotY = 0;
			cubeRotX = 0.4;
		}
		function toggleCubeDepth(btn) {
			cubeDepthTest = !cubeDepthTest;
			btn.classList.toggle('active', cubeDepthTest);
		}
		function toggleCubeLight(btn) {
			cubeLighting = !cubeLighting;
			btn.classList.toggle('active', cubeLighting);
		}
		function toggleCubeWire(btn) {
			cubeWire = !cubeWire;
			btn.classList.toggle('active', cubeWire);
		}
		function toggleCubeNormals(btn) {
			cubeShowNormals = !cubeShowNormals;
			btn.classList.toggle('active', cubeShowNormals);
		}

		cubeC.addEventListener('pointerdown', (e) => {
			cubeDrag = true;
			cubePrevMouse = { x: e.clientX, y: e.clientY };
			e.preventDefault();
		});
		cubeC.addEventListener('pointermove', (e) => {
			if (!cubeDrag) return;
			cubeRotY += (e.clientX - cubePrevMouse.x) * 0.012;
			cubeRotX += (e.clientY - cubePrevMouse.y) * 0.012;
			cubeRotX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, cubeRotX));
			cubePrevMouse = { x: e.clientX, y: e.clientY };
			e.preventDefault();
		});
		_addWinListener('pointerup', () => (cubeDrag = false));

		function drawCube() {
			const W = cubeC.width,
				H = cubeC.height;
			cubeX.clearRect(0, 0, W, H);
			cubeX.fillStyle = '#02040a';
			cubeX.fillRect(0, 0, W, H);
			// Starfield
			for (let i = 0; i < 60; i++) {
				const sx = (i * 347) % W,
					sy = (i * 211) % H;
				cubeX.fillStyle = `rgba(255,255,255,${0.1 + (0.2 * ((i * 13) % 10)) / 10})`;
				cubeX.fillRect(sx, sy, 1, 1);
			}

			const fov = parseInt(document.getElementById('cube-fov').value);
			const lightAngleDeg = parseInt(document.getElementById('cube-light-angle').value);
			document.getElementById('cube-fov-v').textContent = fov + '°';
			document.getElementById('cube-light-angle-v').textContent = lightAngleDeg + '°';
			const lightRad = (lightAngleDeg * Math.PI) / 180;
			const LD = v3norm([Math.cos(lightRad), 0.6, -Math.sin(lightRad)]);

			// Camera
			const camDist = 4.5;
			const camX = Math.sin(0) * camDist,
				camY = 2.0,
				camZ = camDist;
			const V = lookAt4([camX, camY, camZ], [0, 0, 0], [0, 1, 0]);
			const P = perspective4(fov, W / H, 0.1, 50);
			const M = mat4mul(rotY(cubeRotY), rotX(cubeRotX));
			const MVP = mat4mul(P, mat4mul(V, M));

			// Project and render faces
			const faceData = FACE_VERTS.map((verts, fi) => {
				const worldNorm = FACE_NORMALS[fi];
				const rotNorm = [
					M[0] * worldNorm[0] + M[4] * worldNorm[1] + M[8] * worldNorm[2],
					M[1] * worldNorm[0] + M[5] * worldNorm[1] + M[9] * worldNorm[2],
					M[2] * worldNorm[0] + M[6] * worldNorm[1] + M[10] * worldNorm[2]
				];
				const diff = cubeLighting ? Math.max(0, v3dot(rotNorm, LD)) : 1;
				const ambient = 0.15,
					brightness = cubeLighting ? ambient + diff * 0.85 : 1;
				// Project all 4 verts
				const projected = verts.map((v) => {
					const c = mat4mulvec4(MVP, [v[0], v[1], v[2], 1]);
					const w = c[3] || 0.001;
					return {
						x: (c[0] / w) * W * 0.4 + W / 2,
						y: (-c[1] / w) * H * 0.4 + H / 2,
						z: c[2] / w,
						depth: c[2] / w
					};
				});
				const centreZ =
					(projected[0].depth + projected[1].depth + projected[2].depth + projected[3].depth) / 4;
				return { fi, projected, brightness, centreZ, rotNorm, worldNorm };
			});

			// Sort back-to-front if depth test on
			faceData.sort((a, b) => (cubeDepthTest ? b.centreZ - a.centreZ : 0));

			let visibleFaces = 0;
			faceData.forEach(({ fi, projected, brightness, rotNorm, centreZ }) => {
				// Back-face cull (in view space, normal facing away from camera)
				const camDir = v3norm([0, 0, -1]); // camera looks -Z
				if (v3dot(rotNorm, camDir) > 0 && cubeDepthTest) {
					return;
				}
				visibleFaces++;
				const pts = projected;
				const col = FACE_COLORS[fi];
				const r = parseInt(col.slice(1, 3), 16),
					g = parseInt(col.slice(3, 5), 16),
					b = parseInt(col.slice(5, 7), 16);
				const fr = Math.round(r * brightness),
					fg = Math.round(g * brightness),
					fb = Math.round(b * brightness);

				if (!cubeWire) {
					// Fill quads as 2 triangles
					[
						[0, 1, 2],
						[0, 2, 3]
					].forEach(([ia, ib, ic]) => {
						cubeX.beginPath();
						cubeX.moveTo(pts[ia].x, pts[ia].y);
						cubeX.lineTo(pts[ib].x, pts[ib].y);
						cubeX.lineTo(pts[ic].x, pts[ic].y);
						cubeX.closePath();
						cubeX.fillStyle = `rgb(${fr},${fg},${fb})`;
						cubeX.fill();
					});
				}
				// Edges
				cubeX.beginPath();
				cubeX.moveTo(pts[0].x, pts[0].y);
				pts.forEach((p) => cubeX.lineTo(p.x, p.y));
				cubeX.closePath();
				cubeX.strokeStyle = cubeWire ? col : `rgba(0,0,0,0.3)`;
				cubeX.lineWidth = cubeWire ? 1.5 : 0.5;
				cubeX.stroke();

				// Normal arrows
				if (cubeShowNormals) {
					const mx = pts.reduce((s, p) => s + p.x, 0) / 4,
						my = pts.reduce((s, p) => s + p.y, 0) / 4;
					const nProj = mat4mulvec4(MVP, [rotNorm[0] * 0.5, rotNorm[1] * 0.5, rotNorm[2] * 0.5, 0]);
					cubeX.beginPath();
					cubeX.moveTo(mx, my);
					cubeX.lineTo(mx + nProj[0] * 50, my - nProj[1] * 50);
					cubeX.strokeStyle = '#34d399';
					cubeX.lineWidth = 1.5;
					cubeX.stroke();
					cubeX.beginPath();
					cubeX.arc(mx + nProj[0] * 50, my - nProj[1] * 50, 3, 0, Math.PI * 2);
					cubeX.fillStyle = '#34d399';
					cubeX.fill();
				}
			});

			// Light indicator
			const lx = W - 50,
				ly = 60;
			cubeX.beginPath();
			cubeX.arc(lx + Math.cos(lightRad) * 30, ly - Math.sin(lightRad) * 30, 8, 0, Math.PI * 2);
			cubeX.fillStyle = '#fbbf2440';
			cubeX.fill();
			cubeX.strokeStyle = '#fbbf24';
			cubeX.lineWidth = 1;
			cubeX.stroke();
			cubeX.font = '9px IBM Plex Mono';
			cubeX.fillStyle = '#fbbf24';
			cubeX.textAlign = 'center';
			cubeX.fillText('☀', lx + Math.cos(lightRad) * 30, ly - Math.sin(lightRad) * 30 + 3);

			// Update MVP display
			const mc = document.getElementById('mvp-display');
			mc.innerHTML = '';
			for (let row = 0; row < 4; row++) {
				for (let col = 0; col < 4; col++) {
					const el = document.createElement('div');
					el.className = 'm4c';
					const v = MVP[row + col * 4];
					el.textContent = fmt2(v);
					if (Math.abs(v) > 0.01) el.classList.add('hi');
					mc.appendChild(el);
				}
			}

			document.getElementById('cube-roty').textContent =
				(((cubeRotY * 180) / Math.PI) % 360).toFixed(1) + '°';
			document.getElementById('cube-rotx').textContent =
				((cubeRotX * 180) / Math.PI).toFixed(1) + '°';
			document.getElementById('cube-campos').textContent =
				`(${camX.toFixed(1)}, ${camY.toFixed(1)}, ${camZ.toFixed(1)})`;
			document.getElementById('cube-faces').textContent = `${visibleFaces} / 6`;
			document.getElementById('cube-lightdir').textContent =
				`(${LD[0].toFixed(2)}, ${LD[1].toFixed(2)}, ${LD[2].toFixed(2)})`;
		}

		function cubeLoop() {
			if (!cubeRunning) return;
			const now = performance.now(),
				dt = Math.min((now - cubeLastT) / 1000, 0.05);
			cubeLastT = now;
			if (!cubeDrag) cubeRotY += dt * 0.6;
			drawCube();
			cubeRAF = requestAnimationFrame(cubeLoop);
		}
		['cube-fov', 'cube-light-angle'].forEach((id) =>
			document.getElementById(id).addEventListener('input', () => {
				if (!cubeRunning) drawCube();
			})
		);
		cubeLoop();

		/* ══════════════════════════ QUIZ ══════════════════════════ */
		const quizData = [
			{
				q: 'The MVP matrix is computed as M = Projection × View × Model. When applied to a vertex, which transform is applied first?',
				options: [
					'Projection — it is the leftmost matrix',
					'View — it is the centre matrix',
					'Model — matrices are applied right-to-left; Model is rightmost so it acts on the vertex first',
					'The order is arbitrary; matrix multiplication is commutative in 3D'
				],
				correct: 2,
				explanation:
					'Matrix multiplication is right-to-left: the rightmost matrix is applied first. Writing P × V × M means the vertex is first transformed by M (model → world), then by V (world → camera), then by P (camera → clip). The notation reads "finally project, then view, then model" but the execution is the reverse.'
			},
			{
				q: 'A perspective projection matrix produces a w component equal to −camera_z. After the perspective divide (÷w), what happens to objects further from the camera?',
				options: [
					'Their x and y become larger, making distant objects appear bigger',
					'Their x and y become smaller, making distant objects appear smaller — this is perspective foreshortening',
					'Their z becomes negative, causing them to fail the depth test',
					'Their w becomes 0, causing a division-by-zero that clips the vertex'
				],
				correct: 1,
				explanation:
					'For an object at camera-space z = −5, w = 5. After dividing x and y by 5, the NDC coordinates are 5× smaller than they would be at z = −1. This is exactly perspective foreshortening: the further an object is, the smaller its screen-space footprint. Objects at z = −1 divide by 1 (no change); objects at z = −10 divide by 10 (appear 10× smaller).'
			},
			{
				q: 'You render two overlapping triangles: A at depth 0.3 and B at depth 0.7. B is drawn first. With depth testing enabled, what do you see?',
				options: [
					'Triangle B entirely, since it was drawn first',
					'Triangle A on top of B where they overlap, B everywhere else — depth test keeps the closer fragment',
					'Alternating pixels of A and B — the depth test averages the two depths',
					'Triangle A entirely, since it has the smaller depth value'
				],
				correct: 1,
				explanation:
					"After B is rasterised, the depth buffer holds 0.7 where B covered pixels. When A is rasterised at depth 0.3, each fragment passes the depth test (0.3 < 0.7) and overwrites those pixels. Where they don't overlap, B remains. The draw order doesn't matter when depth testing is enabled — the GPU always keeps whichever fragment has the smaller depth value."
			},
			{
				q: 'The look_at function takes an eye position, a target point, and an "up" vector. What does it produce?',
				options: [
					'A matrix that moves the camera to the eye position',
					'A matrix that transforms world space so the camera is at the origin looking down −Z',
					'A rotation-only matrix; translation is handled separately',
					"A projection matrix customised for the camera's field of view"
				],
				correct: 1,
				explanation:
					'look_at produces the view matrix. Rather than moving the camera, it transforms the entire world so the camera sits at the origin looking down −Z. This is mathematically identical to moving a physical camera but computationally simpler — there is only one coordinate space to maintain. The resulting 4×4 matrix encodes camera orientation (right, up, forward) and the translation needed to put the camera at the origin.'
			},
			{
				q: 'A mesh has a face normal computed with cross(edge1, edge2). After applying a non-uniform scale (e.g. scale x=2, y=1, z=1), this normal is incorrect. What is the fix?',
				options: [
					'Multiply the normal by the model matrix, same as position vertices',
					'Renormalise the normal after transforming it by the model matrix',
					"Transform the normal by the transpose of the inverse of the model matrix's 3×3 part",
					'Non-uniform scale does not affect normals — only rotation and translation do'
				],
				correct: 2,
				explanation:
					'Normals are perpendicular to surfaces. Under non-uniform scale, a surface stretches more in one direction — the normal must tilt to remain perpendicular, but multiplying by the model matrix tilts it incorrectly. The mathematically correct transform is the transpose of the inverse of the upper-left 3×3 of the model matrix. In GLSL: mat3 normalMatrix = transpose(inverse(mat3(u_model))). This is computed on the CPU to avoid the expensive GPU inverse.'
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
				div.innerHTML = `<div class="q-text"><span class="q-num">${qi + 1}.</span>${q.q}</div>
      <div class="options" id="opts-${qi}">${q.options.map((o, oi) => `<div class="option" onclick="answer(${qi},${oi})" id="opt-${qi}-${oi}">${o}</div>`).join('')}</div>
      <div class="feedback" id="fb-${qi}"></div>`;
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
						? 'var(--accent4)'
						: correct >= 3
							? 'var(--accent3)'
							: 'var(--accent2)';
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

		if (typeof v3 === 'function') actions.v3 = v3;
		if (typeof v3add === 'function') actions.v3add = v3add;
		if (typeof v3sub === 'function') actions.v3sub = v3sub;
		if (typeof v3scale === 'function') actions.v3scale = v3scale;
		if (typeof v3dot === 'function') actions.v3dot = v3dot;
		if (typeof v3cross === 'function') actions.v3cross = v3cross;
		if (typeof v3len === 'function') actions.v3len = v3len;
		if (typeof v3norm === 'function') actions.v3norm = v3norm;
		if (typeof mat4id === 'function') actions.mat4id = mat4id;
		if (typeof mat4mul === 'function') actions.mat4mul = mat4mul;
		if (typeof mat4mulvec4 === 'function') actions.mat4mulvec4 = mat4mulvec4;
		if (typeof rotY === 'function') actions.rotY = rotY;
		if (typeof rotX === 'function') actions.rotX = rotX;
		if (typeof perspective4 === 'function') actions.perspective4 = perspective4;
		if (typeof lookAt4 === 'function') actions.lookAt4 = lookAt4;
		if (typeof fmt2 === 'function') actions.fmt2 = fmt2;
		if (typeof show3DStage === 'function') actions.show3DStage = show3DStage;
		if (typeof setProj === 'function') actions.setProj = setProj;
		if (typeof drawProj === 'function') actions.drawProj = drawProj;
		if (typeof drawFrustumDiagram === 'function') actions.drawFrustumDiagram = drawFrustumDiagram;
		if (typeof drawProjectedCube === 'function') actions.drawProjectedCube = drawProjectedCube;
		if (typeof buildLookAt === 'function') actions.buildLookAt = buildLookAt;
		if (typeof drawLookAt === 'function') actions.drawLookAt = drawLookAt;
		if (typeof depthReset === 'function') actions.depthReset = depthReset;
		if (typeof toggleDepthTest === 'function') actions.toggleDepthTest = toggleDepthTest;
		if (typeof depthDraw === 'function') actions.depthDraw = depthDraw;
		if (typeof drawDepth === 'function') actions.drawDepth = drawDepth;
		if (typeof drawNormal === 'function') actions.drawNormal = drawNormal;
		if (typeof toggleCube === 'function') actions.toggleCube = toggleCube;
		if (typeof resetCube === 'function') actions.resetCube = resetCube;
		if (typeof toggleCubeDepth === 'function') actions.toggleCubeDepth = toggleCubeDepth;
		if (typeof toggleCubeLight === 'function') actions.toggleCubeLight = toggleCubeLight;
		if (typeof toggleCubeWire === 'function') actions.toggleCubeWire = toggleCubeWire;
		if (typeof toggleCubeNormals === 'function') actions.toggleCubeNormals = toggleCubeNormals;
		if (typeof drawCube === 'function') actions.drawCube = drawCube;
		if (typeof cubeLoop === 'function') actions.cubeLoop = cubeLoop;
		if (typeof buildQuiz === 'function') actions.buildQuiz = buildQuiz;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			if (typeof cubeRAF !== 'undefined' && cubeRAF) cancelAnimationFrame(cubeRAF);
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
		<div style="font-size: 11px; color: var(--muted); text-align: right">Module 12 of 12</div>
	</header>

	<div class="module-hero">
		<div class="module-number">12</div>
		<div class="module-tag">Module 12 · Final Module</div>
		<h1 class="module-title">Introduction to<br /><span>3D Concepts</span></h1>
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
			<li><a href="#from-2d">From 2D to 3D</a></li>
			<li><a href="#projection">Perspective Projection</a></li>
			<li><a href="#camera">Camera Matrices</a></li>
			<li><a href="#depth">Depth Testing</a></li>
			<li><a href="#normals">Normals and Lighting</a></li>
			<li><a href="#practical">Practical: Rotating Cube</a></li>
			<li><a href="#complete">Course Complete</a></li>
			<li><a href="#quiz">Final Quiz</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Understand the 3D rendering pipeline: model → world → view → clip → NDC → screen</li>
			<li>Implement perspective and orthographic projection matrices</li>
			<li>Build a view matrix from camera position and target</li>
			<li>Explain the depth buffer and why it solves the painter's algorithm problem</li>
			<li>Compute surface normals and apply diffuse lighting</li>
			<li>Render and interactively control a lit, rotating 3D cube in moderngl</li>
		</ul>
	</section>

	<!-- ══ 12.01 FROM 2D TO 3D ══ -->
	<section id="from-2d" class="section">
		<div class="section-header">
			<span class="section-num">12.01</span>
			<h2 class="section-title">From 2D to 3D: What Changes</h2>
		</div>

		<p>
			Every concept from this course still applies in 3D. Vertices still go through a pipeline,
			rasterisation still produces fragments, shaders still compute colours. What changes is the
			<em>coordinate space</em>: vertices now have three components (x, y, z), and the pipeline must
			project that 3D geometry onto a 2D screen.
		</p>
		<p>
			The extended transformation chain is:
			<em>Model Space → World Space → View Space → Clip Space → NDC → Screen Space</em>. Each step
			is a matrix multiplication. The combined matrix
			<em>MVP = Projection × View × Model</em> transforms a vertex from its local mesh coordinates all
			the way to a clip-space position in one operation.
		</p>

		<!-- 3D PIPELINE -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · 3D Transformation Pipeline</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Click each stage to understand the transformation it applies.
				</p>
				<div class="pipeline3d" id="pipeline3d">
					<div
						class="p3d-stage"
						onclick={(e) => actions.show3DStage(0, e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.show3DStage(0, e.currentTarget);
							}
						}}
					>
						<div class="p3d-name">Model</div>
						<div class="p3d-sub">local space</div>
					</div>
					<div
						class="p3d-stage"
						onclick={(e) => actions.show3DStage(1, e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.show3DStage(1, e.currentTarget);
							}
						}}
					>
						<div class="p3d-name">× Model</div>
						<div class="p3d-sub">→ world</div>
					</div>
					<div
						class="p3d-stage"
						onclick={(e) => actions.show3DStage(2, e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.show3DStage(2, e.currentTarget);
							}
						}}
					>
						<div class="p3d-name">× View</div>
						<div class="p3d-sub">→ camera</div>
					</div>
					<div
						class="p3d-stage"
						onclick={(e) => actions.show3DStage(3, e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.show3DStage(3, e.currentTarget);
							}
						}}
					>
						<div class="p3d-name">× Proj</div>
						<div class="p3d-sub">→ clip</div>
					</div>
					<div
						class="p3d-stage"
						onclick={(e) => actions.show3DStage(4, e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.show3DStage(4, e.currentTarget);
							}
						}}
					>
						<div class="p3d-name">÷ w</div>
						<div class="p3d-sub">→ NDC</div>
					</div>
					<div
						class="p3d-stage"
						onclick={(e) => actions.show3DStage(5, e.currentTarget)}
						role="button"
						tabindex="0"
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								actions.show3DStage(5, e.currentTarget);
							}
						}}
					>
						<div class="p3d-name">Viewport</div>
						<div class="p3d-sub">→ pixels</div>
					</div>
				</div>
				<div class="p3d-detail" id="p3d-detail">Click a stage to see what it does.</div>
			</div>
		</div>

		<pre><code
				><span class="cm"># The MVP matrix — computed once per object per frame</span>
<span class="kw">import</span> numpy <span class="kw">as</span> np

<span class="cm"># Model matrix: places the object in world space</span>
M = <span class="fn">translation</span>(ox, oy, oz) @ <span class="fn">rotation_y</span
				>(angle) @ <span class="fn">scale</span>(sx, sy, sz)

<span class="cm"># View matrix: transforms world to camera space</span>
V = <span class="fn">look_at</span>(eye=[<span class="num">0</span>,<span class="num">3</span>,<span
					class="num">6</span
				>], target=[<span class="num">0</span>,<span class="num">0</span>,<span class="num">0</span
				>], up=[<span class="num">0</span>,<span class="num">1</span>,<span class="num">0</span>])

<span class="cm"># Projection matrix: applies perspective</span>
P = <span class="fn">perspective</span>(fov_deg=<span class="num">60</span>, aspect=<span
					class="num">16</span
				>/<span class="num">9</span>, near=<span class="num">0.1</span>, far=<span class="num"
					>100</span
				>)

MVP = P @ V @ M   <span class="cm"># right-to-left: Model first, then View, then Projection</span>

<span class="cm"># In the vertex shader:</span>
<span class="cm"># gl_Position = MVP * vec4(in_position, 1.0);</span><span class="lang-tag"
					>python</span
				></code
			></pre>

		<table>
			<thead>
				<tr>
					<th>Space</th>
					<th>Coordinate meaning</th>
					<th>Transform applied</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Model / Local</td>
					<td>Relative to mesh origin</td>
					<td>—</td>
				</tr>
				<tr>
					<td>World</td>
					<td>Relative to scene origin</td>
					<td>Model matrix</td>
				</tr>
				<tr>
					<td>View / Eye / Camera</td>
					<td>Relative to camera; camera at (0,0,0) looking −Z</td>
					<td>View matrix</td>
				</tr>
				<tr>
					<td>Clip</td>
					<td>Homogeneous; clipping uses ±w</td>
					<td>Projection matrix</td>
				</tr>
				<tr>
					<td>NDC</td>
					<td>x,y,z all in [−1,1] after ÷w</td>
					<td>Perspective divide</td>
				</tr>
				<tr>
					<td>Screen / Window</td>
					<td>Pixel coordinates</td>
					<td>Viewport transform</td>
				</tr>
			</tbody>
		</table>
	</section>

	<!-- ══ 12.02 PROJECTION ══ -->
	<section id="projection" class="section">
		<div class="section-header">
			<span class="section-num">12.02</span>
			<h2 class="section-title">Perspective and Orthographic Projection</h2>
		</div>

		<p>
			<strong>Perspective projection</strong> mimics how a real camera or eye works: objects further away
			appear smaller. This is encoded by dividing x and y by the depth z — the further a point is, the
			smaller its screen-space extent. The resulting "frustum" shape defines what is visible.
		</p>
		<p>
			<strong>Orthographic projection</strong> removes this depth scaling: objects remain the same screen
			size regardless of distance. Used for 2D games, technical drawings, and isometric views where depth
			cues would be misleading or unwanted.
		</p>

		<!-- PROJECTION DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Perspective vs Orthographic</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Toggle between projection modes. Adjust FOV and observe how the frustum and projected
					image change.
				</p>
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button
						class="btn active"
						id="proj-persp"
						onclick={(e) => actions.setProj('perspective', e.currentTarget)}
					>
						Perspective
					</button>
					<button
						class="btn"
						id="proj-ortho"
						onclick={(e) => actions.setProj('ortho', e.currentTarget)}
					>
						Orthographic
					</button>
				</div>
				<div class="slider-row">
					<label for="sl-fov">FOV (deg)</label>
					<input type="range" id="sl-fov" min="20" max="140" value="60" />
					<span class="slider-val" id="vl-fov">60°</span>
				</div>
				<div class="slider-row">
					<label for="sl-camz">Camera Z</label>
					<input type="range" id="sl-camz" min="2" max="12" value="6" />
					<span class="slider-val" id="vl-camz">6.0</span>
				</div>
				<canvas
					id="proj-canvas"
					width="860"
					height="300"
					style="width: 100%; border: 1px solid var(--border2); background: var(--code-bg)"
					aria-label="Proj Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>
				<div style="margin-top: 0.75rem" id="proj-info"></div>
			</div>
		</div>

		<pre><code
				><span class="kw">def</span> <span class="fn">perspective</span
				>(fov_deg, aspect, near, far) -> np.ndarray:
    f  = <span class="num">1</span> / np.<span class="fn">tan</span>(np.<span class="fn"
					>radians</span
				>(fov_deg) / <span class="num">2</span>)
    nf = <span class="num">1</span> / (near - far)
    <span class="kw">return</span> np.<span class="fn">array</span>([
        [f / aspect, <span class="num">0</span>,            <span class="num">0</span
				>,               <span class="num">0</span>],
        [<span class="num">0</span>,          f,            <span class="num">0</span
				>,               <span class="num">0</span>],
        [<span class="num">0</span>,          <span class="num">0</span>,  (far+near)*nf,  <span
					class="num">2</span
				>*far*near*nf],
        [<span class="num">0</span>,          <span class="num">0</span>,           -<span
					class="num">1</span
				>,               <span class="num">0</span>],
    ], dtype=<span class="str">'f4'</span>)

<span class="kw">def</span> <span class="fn">orthographic</span
				>(left, right, bottom, top, near, far) -> np.ndarray:
    <span class="kw">return</span> np.<span class="fn">array</span>([
        [<span class="num">2</span>/(right-left), <span class="num">0</span>,             <span
					class="num">0</span
				>,         -(right+left)/(right-left)],
        [<span class="num">0</span>,            <span class="num">2</span>/(top-bottom), <span
					class="num">0</span
				>,         -(top+bottom)/(top-bottom)],
        [<span class="num">0</span>,              <span class="num">0</span>,   -<span class="num"
					>2</span
				>/(far-near), -(far+near)/(far-near)     ],
        [<span class="num">0</span>,              <span class="num">0</span>,             <span
					class="num">0</span
				>,                           <span class="num">1</span>],
    ], dtype=<span class="str">'f4'</span>)<span class="lang-tag">python</span></code
			></pre>

		<div class="callout orange">
			<div class="callout-label">The w Component</div>
			After the perspective projection matrix, the vertex's w component holds −z (the original camera-space
			depth). The hardware performs the<em>perspective divide</em> automatically: it divides x, y, z by
			w to produce NDC. This is what causes distant objects to appear smaller — their x and y get divided
			by a larger number.
		</div>
	</section>

	<!-- ══ 12.03 CAMERA ══ -->
	<section id="camera" class="section">
		<div class="section-header">
			<span class="section-num">12.03</span>
			<h2 class="section-title">Camera Matrices: look_at</h2>
		</div>

		<p>
			The <strong>view matrix</strong> transforms the entire world so that the camera sits at the
			origin, looking down the −Z axis. Instead of moving the camera, you move everything else in
			the opposite direction. The <code>look_at</code> function constructs this matrix from three
			intuitive inputs: where the camera is (<em>eye</em>), what it looks at (<em>target</em>), and
			which direction is up (<em>up</em>).
		</p>

		<pre><code
				><span class="kw">def</span> <span class="fn">look_at</span>(eye, target, up) -> np.ndarray:
    eye, target, up = np.<span class="fn">array</span>(eye, dtype=float), \
                      np.<span class="fn">array</span>(target, dtype=float), \
                      np.<span class="fn">array</span>(up, dtype=float)

    f = <span class="fn">normalize</span>(target - eye)    <span class="cm"
					># forward (−Z in camera space)</span
				>
    r = <span class="fn">normalize</span>(np.<span class="fn">cross</span>(f, up)) <span class="cm"
					># right (X in camera space)</span
				>
    u = np.<span class="fn">cross</span>(r, f)             <span class="cm"
					># up (Y in camera space, re-computed)</span
				>

    <span class="kw">return</span> np.<span class="fn">array</span>([
        [ r[<span class="num">0</span>],  r[<span class="num">1</span>],  r[<span class="num"
					>2</span
				>], -np.<span class="fn">dot</span>(r, eye)],
        [ u[<span class="num">0</span>],  u[<span class="num">1</span>],  u[<span class="num"
					>2</span
				>], -np.<span class="fn">dot</span>(u, eye)],
        [-f[<span class="num">0</span>], -f[<span class="num">1</span>], -f[<span class="num"
					>2</span
				>],  np.<span class="fn">dot</span>(f, eye)],
        [    <span class="num">0</span>,      <span class="num">0</span>,      <span class="num"
					>0</span
				>,               <span class="num">1</span>],
    ], dtype=<span class="str">'f4'</span>)

<span class="kw">def</span> <span class="fn">normalize</span>(v):
    return v / (np.<span class="fn">linalg</span>.<span class="fn">norm</span>(v) or <span
					class="num">1</span
				>)<span class="lang-tag">python</span></code
			></pre>

		<!-- LOOK_AT DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · look_at Camera Explorer</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Drag the camera position. The look_at matrix updates live and the view of the scene
					changes.
				</p>
				<div class="slider-row">
					<label for="dummy">Camera X</label><input
						type="range"
						id="cam-x"
						min="-6"
						max="6"
						value="3"
						step="0.1"
					/><span class="slider-val" id="cam-x-v">3.0</span>
				</div>
				<div class="slider-row">
					<label for="dummy">Camera Y</label><input
						type="range"
						id="cam-y"
						min="0"
						max="8"
						value="3"
						step="0.1"
					/><span class="slider-val" id="cam-y-v">3.0</span>
				</div>
				<div class="slider-row" style="margin-bottom: 1rem">
					<label for="dummy">Camera Z</label><input
						type="range"
						id="cam-z"
						min="2"
						max="10"
						value="6"
						step="0.1"
					/><span class="slider-val" id="cam-z-v">6.0</span>
				</div>
				<div class="two-col" style="align-items: start">
					<div>
						<canvas
							id="lookat-canvas"
							width="380"
							height="300"
							style="width: 100%; border: 1px solid var(--border2); background: var(--code-bg)"
							aria-label="Lookat Canvas Demonstration"
							role="application"
							tabindex="0"
						></canvas>
					</div>
					<div>
						<div class="mat-label">View Matrix (look_at result)</div>
						<div style="overflow-x: auto"><div class="mat4" id="view-mat"></div></div>
						<div class="info-panel" style="margin-top: 0.75rem">
							<div class="info-row">
								<span class="info-key">eye</span><span class="info-val" id="la-eye">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">target</span><span class="info-val">(0, 0, 0)</span>
							</div>
							<div class="info-row">
								<span class="info-key">forward (−Z)</span><span class="info-val" id="la-fwd">—</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">right (+X)</span><span class="info-val" id="la-right">—</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">up (+Y)</span><span class="info-val" id="la-up">—</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ══ 12.04 DEPTH ══ -->
	<section id="depth" class="section">
		<div class="section-header">
			<span class="section-num">12.04</span>
			<h2 class="section-title">The Depth Buffer</h2>
		</div>

		<p>
			Without depth information, the last-drawn triangle always wins — the "painter's algorithm"
			problem. Drawing a distant mountain after a near tree would obscure the tree. The
			<strong>depth buffer</strong> (or z-buffer) solves this: each pixel stores the depth value of the
			closest fragment drawn so far. A new fragment only writes to the framebuffer if its depth is less
			than the stored value.
		</p>
		<p>
			Depth values are stored in the range [0, 1], where 0 is the near plane and 1 is the far plane.
			The depth buffer has a fixed precision (usually 24 bits), and that precision is not
			distributed uniformly — most of the range is compressed near the near plane.
		</p>

		<!-- DEPTH BUFFER DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Depth Buffer Visualizer</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Click "Draw" to render triangles in a random order. Toggle depth testing to see how it
					prevents incorrect overdraw.
				</p>
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button class="btn g" onclick={(e) => actions.depthReset()}>↺ Clear</button>
					<button class="btn" onclick={(e) => actions.depthDraw()}>+ Draw triangle</button>
					<button
						class="btn o active"
						id="depth-test-btn"
						onclick={(e) => actions.toggleDepthTest()}
					>
						Depth test: ON
					</button>
				</div>
				<canvas
					id="depth-canvas"
					width="860"
					height="260"
					style="width: 100%; border: 1px solid var(--border2); background: var(--code-bg)"
					aria-label="Depth Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>
				<div
					style="
								margin-top: 0.75rem;
								font-size: 12px;
								display: flex;
								gap: 1.5rem;
								flex-wrap: wrap;
							"
					id="depth-info"
				></div>
			</div>
		</div>

		<pre><code
				><span class="cm"># moderngl: enable depth testing (always do this in 3D)</span>
ctx.enable(moderngl.DEPTH_TEST)

<span class="cm"># Create a framebuffer with both colour and depth attachments</span>
fbo = ctx.<span class="fn">framebuffer</span>(
    color_attachments=[ctx.<span class="fn">texture</span>((W, H), <span class="num">4</span>)],
    depth_attachment =ctx.<span class="fn">depth_renderbuffer</span>((W, H)),
)
fbo.<span class="fn">use</span>()

<span class="cm"># Clear BOTH colour and depth at the start of each frame</span>
ctx.<span class="fn">clear</span>(<span class="num">0.1</span>, <span class="num">0.1</span>, <span
					class="num">0.15</span
				>, depth=<span class="num">1.0</span>)  <span class="cm"
					># depth=1.0 means "nothing drawn yet"</span
				><span class="lang-tag">python + moderngl</span></code
			></pre>

		<div class="callout cyan">
			<div class="callout-label">Z-Fighting</div>
			When two surfaces at nearly the same depth are rendered, floating-point precision limits cause the
			depth test to alternate between them frame to frame — a flickering artefact called<em
				>z-fighting</em
			>. Mitigations: keep the near plane as far from the camera as possible (this spreads precision
			across the scene), use <code>glPolygonOffset</code> for decals, or separate co-planar geometry by
			a small offset in the vertex shader.
		</div>
	</section>

	<!-- ══ 12.05 NORMALS ══ -->
	<section id="normals" class="section">
		<div class="section-header">
			<span class="section-num">12.05</span>
			<h2 class="section-title">Surface Normals and Diffuse Lighting</h2>
		</div>

		<p>
			A <strong>surface normal</strong> is a unit vector perpendicular to a surface. It encodes which
			direction the surface is "facing". Lighting calculations depend entirely on normals: a surface facing
			directly toward a light receives maximum illumination; one facing away receives none.
		</p>
		<p>
			For a triangle with vertices A, B, C, the face normal is computed by the cross product of two
			edge vectors:
		</p>

		<pre><code
				><span class="kw">import</span> numpy <span class="kw">as</span> np

<span class="kw">def</span> <span class="fn">face_normal</span>(A, B, C):
    edge1 = B - A
    edge2 = C - A
    n = np.<span class="fn">cross</span>(edge1, edge2)
    <span class="kw">return</span> n / np.<span class="fn">linalg</span>.<span class="fn">norm</span
				>(n)   <span class="cm"># normalize to length 1</span>

<span class="cm"># GLSL diffuse lighting in the fragment shader</span>
<span class="cm"># N = surface normal (unit vector), L = direction to light (unit vector)</span>
<span class="cm"># diffuse = max(dot(N, L), 0)  — clamped to avoid negative light</span><span
					class="lang-tag">python / glsl</span
				></code
			></pre>

		<!-- NORMAL DEMO -->
		<div class="demo-box">
			<div class="demo-header">
				<div class="demo-header-left">Interactive · Surface Normal and Lighting Angle</div>
				<span class="demo-badge i">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Drag the light source. The dot product between the normal and light direction determines
					diffuse brightness.
				</p>
				<div class="two-col" style="align-items: start">
					<div>
						<canvas
							id="normal-canvas"
							width="380"
							height="300"
							style="width: 100%"
							aria-label="Normal Canvas Demonstration"
							role="application"
							tabindex="0"
						></canvas>
					</div>
					<div style="display: flex; flex-direction: column; gap: 0.75rem">
						<div class="info-panel">
							<div class="info-row">
								<span class="info-key">normal N</span><span class="info-val" id="norm-n">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">light dir L</span><span class="info-val" id="norm-l">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">dot(N, L)</span><span class="info-val" id="norm-dot">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">diffuse</span><span class="info-val" id="norm-diff">—</span>
							</div>
							<div class="info-row">
								<span class="info-key">ambient</span><span class="info-val">0.15</span>
							</div>
							<div class="info-row">
								<span class="info-key">total</span><span class="info-val" id="norm-total">—</span>
							</div>
						</div>
						<div
							id="normal-color-preview"
							style="
										height: 56px;
										border: 1px solid var(--border2);
										transition: background 0.05s;
									"
						></div>
						<div style="font-size: 12px; color: var(--muted); line-height: 1.8">
							The GLSL calculation:<br />
							<code style="font-size: 11px">float diff = max(dot(N,L), 0.0);</code><br />
							<code style="font-size: 11px">vec3 lit = ambient + diffuse*diff;</code>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="callout green">
			<div class="callout-label">Normal Transformation</div>
			Normals cannot be transformed by the same matrix as positions. If the model matrix includes a non-uniform
			scale, it distorts normals incorrectly. The correct matrix to transform normals is the<em
				>normal matrix</em
			>: the transpose of the inverse of the upper-left 3×3 of the model matrix. In GLSL:
			<code>mat3 normalMatrix = transpose(inverse(mat3(u_model)));</code>
		</div>
	</section>

	<hr class="divider" />

	<!-- ══ 12.06 PRACTICAL ══ -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">12.06</span>
			<h2 class="section-title">Practical: Rotating Lit Cube</h2>
		</div>

		<p>
			The complete moderngl program below renders a rotating cube with per-face diffuse lighting.
			Every concept from this module is exercised: MVP matrix, look_at, perspective projection,
			depth testing, normals, and a Phong-style fragment shader.
		</p>

		<pre><code
				><span class="cm"># Cube: 6 faces × 2 triangles × 3 vertices = 36 vertices</span>
<span class="cm"># Each vertex: [x,y,z, nx,ny,nz, r,g,b]  (position, normal, color)</span>
cube_vertices = np.<span class="fn">array</span>([
    <span class="cm"># Front face (normal 0,0,1)</span>
    -<span class="num">1</span>,-<span class="num">1</span>, <span class="num">1</span>,  <span
					class="num">0</span
				>,<span class="num">0</span>,<span class="num">1</span>,  <span class="num">0.3</span>,<span
					class="num">0.6</span
				>,<span class="num">1.0</span>,
     <span class="num">1</span>,-<span class="num">1</span>, <span class="num">1</span>,  <span
					class="num">0</span
				>,<span class="num">0</span>,<span class="num">1</span>,  <span class="num">0.3</span>,<span
					class="num">0.6</span
				>,<span class="num">1.0</span>,
     <span class="num">1</span>, <span class="num">1</span>, <span class="num">1</span>,  <span
					class="num">0</span
				>,<span class="num">0</span>,<span class="num">1</span>,  <span class="num">0.3</span>,<span
					class="num">0.6</span
				>,<span class="num">1.0</span>,
    <span class="cm"># ... (all 36 vertices)</span>
], dtype=<span class="str">'f4'</span>)

vertex_src = <span class="str"
					>"""
#version 330
uniform mat4 u_mvp;
uniform mat3 u_normal_matrix;
in vec3 in_position;
in vec3 in_normal;
in vec3 in_color;
out vec3 v_normal;
out vec3 v_color;
void main() &#123;
    v_normal = normalize(u_normal_matrix * in_normal);
    v_color  = in_color;
    gl_Position = u_mvp * vec4(in_position, 1.0);
&#125;
"""</span
				>

fragment_src = <span class="str"
					>"""
#version 330
uniform vec3 u_light_dir;    // normalized direction TO light
in vec3 v_normal;
in vec3 v_color;
out vec4 out_color;
void main() &#123;
    float ambient  = 0.18;
    float diffuse  = max(dot(v_normal, u_light_dir), 0.0);
    float lit      = ambient + diffuse * 0.82;
    out_color = vec4(v_color * lit, 1.0);
&#125;
"""</span
				><span class="lang-tag">python + moderngl</span></code
			></pre>

		<!-- THE INTERACTIVE 3D CUBE -->
		<div class="demo-box" style="border-color: var(--accent)">
			<div class="demo-header" style="border-color: var(--accent)">
				<div class="demo-header-left" style="color: var(--accent)">
					Interactive · 3D Lit Rotating Cube
				</div>
				<span class="demo-badge g">3D RENDERER</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--muted); margin-bottom: 1rem">
					Drag to orbit. All computation uses the math from this module: MVP matrix, look_at,
					perspective, depth sorting, normals, diffuse lighting.
				</p>
				<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem">
					<button class="btn g active" id="cube-play-btn" onclick={(e) => actions.toggleCube()}>
						⏸ Pause
					</button>
					<button class="btn" onclick={(e) => actions.resetCube()}>↺ Reset</button>
					<button
						class="btn active"
						id="cube-depth-btn"
						onclick={(e) => actions.toggleCubeDepth(e.currentTarget)}
					>
						Depth Test
					</button>
					<button
						class="btn active"
						id="cube-light-btn"
						onclick={(e) => actions.toggleCubeLight(e.currentTarget)}
					>
						Lighting
					</button>
					<button
						class="btn"
						id="cube-wire-btn"
						onclick={(e) => actions.toggleCubeWire(e.currentTarget)}
					>
						Wireframe
					</button>
					<button
						class="btn"
						id="cube-normals-btn"
						onclick={(e) => actions.toggleCubeNormals(e.currentTarget)}
					>
						Show Normals
					</button>
				</div>
				<div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem">
					<div class="slider-row" style="flex: 1; min-width: 200px">
						<label for="dummy">FOV</label><input
							type="range"
							id="cube-fov"
							min="20"
							max="120"
							value="60"
						/><span class="slider-val" id="cube-fov-v">60°</span>
					</div>
					<div class="slider-row" style="flex: 1; min-width: 200px">
						<label for="dummy">Light angle</label><input
							type="range"
							id="cube-light-angle"
							min="0"
							max="360"
							value="45"
						/><span class="slider-val" id="cube-light-angle-v">45°</span>
					</div>
				</div>
				<div class="two-col" style="align-items: start">
					<canvas
						id="cube-canvas"
						width="460"
						height="400"
						style="width: 100%"
						aria-label="Cube Canvas Demonstration"
						role="application"
						tabindex="0"
					></canvas>
					<div style="display: flex; flex-direction: column; gap: 0.75rem">
						<div class="mat-label">u_mvp (Model × View × Proj)</div>
						<div style="overflow-x: auto"><div class="mat4" id="mvp-display"></div></div>
						<div class="info-panel">
							<div class="info-row">
								<span class="info-key">rotation Y</span><span class="info-val" id="cube-roty"
									>0°</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">rotation X</span><span class="info-val" id="cube-rotx"
									>0°</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">camera pos</span><span class="info-val" id="cube-campos"
									>—</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">visible faces</span><span class="info-val" id="cube-faces"
									>—</span
								>
							</div>
							<div class="info-row">
								<span class="info-key">light dir</span><span class="info-val" id="cube-lightdir"
									>—</span
								>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- COURSE COMPLETE -->
	<section id="complete">
		<div class="complete-banner">
			<div class="complete-title">Course Complete</div>
			<div class="complete-sub">Game Development Fundamentals: From Pixels to Play</div>
			<p style="font-size: 13px; color: var(--text); max-width: 600px; margin: 0 auto 1.5rem">
				You have covered the full stack of 2D game development — from raw pixel arrays to GPU
				shaders, from collision geometry to engine architecture, all the way to a complete playable
				game and an introduction to 3D rendering.
			</p>
			<div class="module-grid">
				<div class="mod-chip done">01 · Pixels</div>
				<div class="mod-chip done">02 · Rendering</div>
				<div class="mod-chip done">03 · Transforms</div>
				<div class="mod-chip done">04 · GPU in Python</div>
				<div class="mod-chip done">05 · Shaders</div>
				<div class="mod-chip done">06 · Textures</div>
				<div class="mod-chip done">07 · Time & Anim</div>
				<div class="mod-chip done">08 · Input</div>
				<div class="mod-chip done">09 · Physics</div>
				<div class="mod-chip done">10 · Architecture</div>
				<div class="mod-chip done">11 · Complete Game</div>
				<div class="mod-chip done">12 · 3D Intro</div>
			</div>
			<div style="margin-top: 2rem; font-size: 12px; color: var(--muted)">
				Suggested next steps: Optional module — Transition to C++ · Build your own complete game ·
				Explore a commercial engine
			</div>
		</div>
	</section>

	<!-- QUIZ -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Final Quiz — Module 12</div>
		<div class="quiz-sub">5 questions · Projection, depth, normals, and the MVP pipeline</div>
		<div id="quiz-container"></div>
		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-num">0/5</div>
			<div style="font-size: 12px; color: var(--muted); margin-top: 0.25rem">
				Course complete. Well done.
			</div>
		</div>
	</section>

	<div class="nav-links">
		<a href="." class="prev-link">← 11 · Building a Complete 2D Game</a>
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
		color: var(--accent4);
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
		color: var(--accent4);
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
		color: #1a3050;
	}
	:global(.num) {
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
		color: var(--accentL);
	}

	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--accent);
		background: color-mix(in srgb, var(--accent) 5%, var(--surface));
		font-size: 13px;
	}
	:global(.callout.orange) {
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 5%, var(--surface));
	}
	:global(.callout.cyan) {
		border-color: var(--accent3);
		background: color-mix(in srgb, var(--accent3) 5%, var(--surface));
	}
	:global(.callout.green) {
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
	:global(.callout.orange) .callout-label {
		color: var(--accent2);
	}
	:global(.callout.cyan) .callout-label {
		color: var(--accent3);
	}
	:global(.callout.green) .callout-label {
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
	:global(.demo-badge.a) {
		color: var(--accent2);
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 10%, transparent);
	}
	:global(.demo-badge.g) {
		color: var(--accent4);
		border-color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 10%, transparent);
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
		min-width: 100px;
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
	:global(.btn.o:hover),
	:global(.btn.o.active) {
		border-color: var(--accent2);
		color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 10%, transparent);
	}
	:global(.btn.g:hover),
	:global(.btn.g.active) {
		border-color: var(--accent4);
		color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 10%, transparent);
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
		color: var(--accent4);
		font-weight: 600;
	}

	/* Matrix grid */
	:global(.mat4) {
		display: inline-grid;
		grid-template-columns: repeat(4, 64px);
		gap: 2px;
		background: var(--code-bg);
		border: 1px solid var(--border);
		padding: 0.6rem;
		font-size: 11px;
		position: relative;
	}
	.mat4::before,
	.mat4::after {
		content: '';
		position: absolute;
		top: 4px;
		bottom: 4px;
		width: 3px;
		border: 1px solid var(--border2);
	}
	.mat4::before {
		left: -4px;
		border-right: none;
	}
	.mat4::after {
		right: -4px;
		border-left: none;
	}
	:global(.m4c) {
		padding: 2px 4px;
		text-align: right;
		color: var(--text);
		transition: background 0.15s;
	}
	:global(.m4c.hi) {
		background: color-mix(in srgb, var(--accent) 15%, transparent);
		color: var(--accent);
	}
	:global(.mat-label) {
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.4rem;
	}

	/* Pipeline viz */
	:global(.pipeline3d) {
		display: flex;
		align-items: center;
		gap: 0;
		overflow-x: auto;
		margin: 1.5rem 0;
	}
	:global(.p3d-stage) {
		min-width: 100px;
		padding: 0.7rem 0.6rem;
		border: 1px solid var(--border);
		border-right: none;
		text-align: center;
		cursor: pointer;
		transition: all 0.15s;
		flex: 1;
	}
	:global(.p3d-stage:last-child) {
		border-right: 1px solid var(--border);
	}
	:global(.p3d-stage:hover),
	:global(.p3d-stage.active) {
		background: color-mix(in srgb, var(--accent) 8%, var(--surface));
		border-color: var(--accent);
	}
	:global(.p3d-name) {
		font-size: 11px;
		font-weight: 600;
		color: #fff;
	}
	:global(.p3d-sub) {
		font-size: 9px;
		color: var(--muted);
		margin-top: 0.2rem;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}
	:global(.p3d-detail) {
		padding: 1rem 1.25rem;
		border: 1px solid var(--border2);
		border-top: none;
		background: color-mix(in srgb, var(--accent) 4%, var(--surface));
		font-size: 12px;
		color: var(--muted);
		min-height: 52px;
	}

	/* depth viz */
	:global(.depth-strip) {
		height: 24px;
		display: flex;
		gap: 2px;
		margin: 0.5rem 0;
	}
	:global(.depth-cell) {
		flex: 1;
		border: 1px solid var(--border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 9px;
		transition: background 0.2s;
	}

	/* Normal viz */
	#normal-canvas {
		border: 1px solid var(--border2);
		background: var(--code-bg);
		cursor: pointer;
		touch-action: none;
	}

	/* Main 3D canvas */
	#cube-canvas {
		border: 1px solid var(--border2);
		background: #02040a;
		cursor: grab;
		touch-action: none;
	}
	#cube-canvas:active {
		cursor: grabbing;
	}

	/* Course complete banner */
	:global(.complete-banner) {
		margin: 4rem 0;
		padding: 3rem 2rem;
		background: var(--raised);
		border: 1px solid var(--accent);
		text-align: center;
	}
	:global(.complete-title) {
		font-family: 'Syne', sans-serif;
		font-size: 36px;
		font-weight: 800;
		color: var(--accent);
		margin-bottom: 0.5rem;
	}
	:global(.complete-sub) {
		font-size: 14px;
		color: var(--muted);
		margin-bottom: 1.5rem;
	}
	:global(.module-grid) {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.5rem;
		margin-top: 1.5rem;
	}
	@media (max-width: 500px) {
		:global(.module-grid) {
			grid-template-columns: repeat(2, 1fr);
		}
	}
	:global(.mod-chip) {
		border: 1px solid var(--border2);
		padding: 0.4rem 0.5rem;
		font-size: 10px;
		color: var(--muted);
		text-align: center;
	}
	:global(.mod-chip.done) {
		border-color: var(--accent4);
		color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 8%, transparent);
	}

	/* quiz */
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
		border-color: var(--accent4);
		background: color-mix(in srgb, var(--accent4) 10%, transparent);
		color: var(--accent4);
	}
	:global(.option.wrong) {
		border-color: var(--accent2);
		background: color-mix(in srgb, var(--accent2) 10%, transparent);
		color: var(--accent2);
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
		color: var(--accent4);
	}
	:global(.feedback.bad) {
		color: var(--accent2);
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
		justify-content: center;
		align-items: center;
		margin-top: 4rem;
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

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
