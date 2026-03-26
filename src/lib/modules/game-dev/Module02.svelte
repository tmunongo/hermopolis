<script lang="ts">
	import { onMount } from 'svelte';

	let readingProgress = 0;

	// ── PIPELINE ──
	let activePipeStage = -1;
	const pipeDetails = [
		`<strong>Vertex Input</strong> — Raw geometry data is uploaded to the GPU as a buffer of numbers. Each vertex carries a position (x, y, z) and optionally: a color, a texture coordinate (UV), a normal vector, or any custom attribute.`,
		`<strong>Primitive Assembly</strong> — Individual vertices are grouped into primitives according to the draw mode (TRIANGLES, TRIANGLE_STRIP, etc). Three vertices become one triangle.`,
		`<strong>Rasterization</strong> — Each triangle is converted into a set of <em>fragments</em> — candidate pixels that the triangle covers. The edge function test determines which pixel centers fall inside the triangle boundary.`,
		`<strong>Fragment Shading</strong> — For each fragment, a shader program computes the final color. The shader can read textures, interpolate vertex attributes, apply lighting, and produce any color value.`,
		`<strong>Output Merge</strong> — The computed color is written to the framebuffer. Depth testing, blending (transparency), and stenciling all happen here. Only fragments that pass all tests write to the final image.`
	];
	let pipeDetail = 'Select a stage above to see what it does.';

	function showPipe(i: number) {
		activePipeStage = i;
		pipeDetail = pipeDetails[i];
	}

	// ── PRIMITIVES ──
	let primCanvas: HTMLCanvasElement;
	let primType = 'triangles';
	const primDescs: Record<string, string> = {
		triangles:
			'TRIANGLES: Every 3 vertices form one independent triangle. 9 vertices → 3 triangles. No vertex is shared between primitives.',
		strip:
			'TRIANGLE_STRIP: Each new vertex (after the first two) adds one triangle by reusing the previous two vertices. 7 vertices → 5 triangles. Efficient for connected surfaces.',
		fan: 'TRIANGLE_FAN: All triangles share a common center vertex (v0). Each new vertex adds a triangle connecting back to v0. 8 vertices → 6 triangles. Perfect for circular shapes.',
		mesh: 'Complex mesh: any polygon can be tessellated into triangles. This pentagon (5 vertices) becomes 3 triangles.'
	};
	let primDesc = primDescs.triangles;

	// ── STEP RASTERIZER ──
	let stepCanvas: HTMLCanvasElement;
	const STEP_GRID = 15,
		STEP_PX = 16;
	const stepTri = { v0: [2, 12], v1: [7, 2], v2: [13, 11] };
	let stepPixels: { x: number; y: number; e0: number; e1: number; e2: number; inside: boolean }[] =
		[];
	let stepState: (null | 'tested' | 'inside')[] = [];
	let stepIdx = 0;
	let stepTimer: ReturnType<typeof setInterval> | null = null;
	let stepPlaying = false;
	let stepSpeed = 3;
	let statBbox = '—',
		statTested = 0,
		statInside = 0,
		statEff = '—',
		statCur = '—',
		statEdge = '—';
	let stepInfo = 'Pixel 0 / 0';

	// ── DRAGGABLE RASTERIZER ──
	let rastCanvas: HTMLCanvasElement;
	const CELL = 20;
	let overlays = { bbox: true, grid: true, verts: true, edges: false };
	let verts = [
		{ x: 120, y: 340 },
		{ x: 430, y: 60 },
		{ x: 740, y: 340 }
	];
	let dragging: number | null = null;
	let rastBbox = '—',
		rastTested = '—',
		rastFilled = '—',
		rastBbarea = '—',
		rastTarea = '—',
		rastEff = '—';
	let rastCodeHtml = '';

	// ── DEBUG ASSESSMENT ──
	const debugQuestions = [
		{
			title: 'Bug 01 · No pixels drawn',
			code: [
				'def edge_fn(ax, ay, bx, by, px, py):',
				'    return (bx - ax) * (py - ay) - (by - ay) * (px - ax)',
				'',
				'def rasterize(fb, v0, v1, v2, color):',
				'    min_x = int(min(v0[0], v1[0], v2[0]))',
				'    max_x = int(max(v0[0], v1[0], v2[0]))',
				'    min_y = int(min(v0[1], v1[1], v2[1]))',
				'    max_y = int(max(v0[1], v1[1], v2[1]))',
				'    for y in range(min_y, max_y + 1):',
				'        for x in range(min_x, max_x + 1):',
				'            e0 = edge_fn(*v0, *v1, x, y)       # ← bug here',
				'            e1 = edge_fn(*v1, *v2, x, y)',
				'            e2 = edge_fn(*v2, *v0, x, y)',
				'            if e0 >= 0 and e1 >= 0 and e2 >= 0:',
				'                fb[y, x] = color'
			],
			bugLine: 10,
			options: [
				'The bounding box is computed incorrectly — it should use float() not int()',
				'The edge function is called with x, y instead of x+0.5, y+0.5 — pixels on exact edges test as zero',
				'The range should be range(min_y, max_y) without the + 1',
				'The winding order is wrong — the conditions should be e0 <= 0'
			],
			correct: 1,
			explanation: 'Pixel centers are at (x+0.5, y+0.5), not (x, y). Always test pixel centers.'
		},
		{
			title: 'Bug 02 · Triangle flickers — only visible sometimes',
			code: [
				'def rasterize(fb, v0, v1, v2, color):',
				'    min_x = max(0, int(min(v0[0], v1[0], v2[0])))',
				'    max_x = min(WIDTH, int(max(v0[0], v1[0], v2[0])))  # ← bug here',
				'    min_y = max(0, int(min(v0[1], v1[1], v2[1])))',
				'    max_y = min(HEIGHT-1, int(max(v0[1], v1[1], v2[1])))',
				'    for y in range(min_y, max_y + 1):',
				'        for x in range(min_x, max_x + 1):',
				'            e0 = edge_fn(*v0, *v1, x+0.5, y+0.5)',
				'            e1 = edge_fn(*v1, *v2, x+0.5, y+0.5)',
				'            e2 = edge_fn(*v2, *v0, x+0.5, y+0.5)',
				'            if e0 >= 0 and e1 >= 0 and e2 >= 0:',
				'                fb[y, x] = color'
			],
			bugLine: 2,
			options: [
				'The edge functions are called with the wrong vertex order',
				'max_x clips to WIDTH instead of WIDTH-1, causing an out-of-bounds write when the triangle reaches the right edge',
				'The framebuffer index is wrong — it should be fb[x, y] not fb[y, x]',
				'The condition should use > 0, not >= 0, to avoid shared edges'
			],
			correct: 1,
			explanation:
				'Valid framebuffer column indices are 0 to WIDTH-1. Clamping max_x to WIDTH allows x to reach WIDTH inside the loop, causing an out-of-bounds write. Always clamp to WIDTH-1 and HEIGHT-1.'
		},
		{
			title: 'Bug 03 · Overlapping triangles show wrong colors',
			code: [
				'framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)',
				'',
				'# Draw triangle A (background)',
				'rasterize(framebuffer, (50,200),(200,50),(350,200), [0,229,200])',
				'',
				'# Draw triangle B (foreground)',
				'rasterize(framebuffer, (100,200),(250,50),(400,200), [255,95,58])',
				'',
				'def draw_frame():',
				'    triangles = get_scene_triangles()',
				'    random.shuffle(triangles)  # ← bug here',
				'    for tri in triangles:',
				'        rasterize(framebuffer, *tri)'
			],
			bugLine: 10,
			options: [
				'The framebuffer is not cleared before drawing — old pixels remain',
				'rasterize() is missing the color argument inside draw_frame()',
				'Triangles are shuffled before drawing — in a software rasterizer, draw order determines visibility. Without a depth buffer, later draws always overwrite earlier ones.',
				'The bounding boxes of the two triangles overlap, which the rasterizer does not handle'
			],
			correct: 2,
			explanation:
				"A software rasterizer with no depth buffer uses the painter's algorithm — later drawn triangles always overwrite earlier ones. Shuffling the draw order randomizes which triangle wins at overlapping pixels. Fix: sort back-to-front, or implement a depth buffer."
		}
	];
	let dbgAnswers: (number | null)[] = debugQuestions.map(() => null);
	let dbgDone = false;
	let dbgScore = 0;

	function edgeFn(ax: number, ay: number, bx: number, by: number, px: number, py: number) {
		return (bx - ax) * (py - ay) - (by - ay) * (px - ax);
	}

	// ── PRIMITIVES DRAWING ──
	function drawPrimitives() {
		if (!primCanvas) return;
		const ctx = primCanvas.getContext('2d')!;
		const W = primCanvas.width,
			H = primCanvas.height;
		ctx.clearRect(0, 0, W, H);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, W, H);
		const colors = ['#00e5c8', '#ff5f3a', '#a78bfa', '#ffd166', '#5f9fff', '#ff79c6'];

		if (primType === 'triangles') {
			const tris = [
				[
					[80, 180],
					[140, 60],
					[200, 180]
				],
				[
					[240, 180],
					[300, 60],
					[360, 180]
				],
				[
					[400, 180],
					[460, 60],
					[520, 180]
				]
			] as [number, number][][];
			tris.forEach((tri, i) => {
				drawTri(ctx, tri[0], tri[1], tri[2], colors[i], true);
				tri.forEach((v, j) =>
					drawVertex(ctx, v[0], v[1], String.fromCharCode(65 + i * 3 + j), '#fff')
				);
			});
		} else if (primType === 'strip') {
			const vverts: number[][] = [
				[60, 180],
				[110, 60],
				[180, 180],
				[250, 60],
				[320, 180],
				[390, 60],
				[460, 180]
			];
			for (let i = 0; i < vverts.length - 2; i++) {
				const a = vverts[i],
					b = vverts[i + 1],
					c = vverts[i + 2];
				drawTri(ctx, i % 2 === 0 ? a : b, i % 2 === 0 ? b : a, c, colors[i % colors.length], true);
			}
			vverts.forEach((v, i) => drawVertex(ctx, v[0], v[1], 'v' + i, '#fff'));
		} else if (primType === 'fan') {
			const cx = 250,
				cy = 130,
				r = 100;
			const fverts: number[][] = [[cx, cy]];
			for (let a = 0; a <= 360; a += 60)
				fverts.push([
					cx + r * Math.cos((a * Math.PI) / 180),
					cy + r * Math.sin((a * Math.PI) / 180)
				]);
			for (let i = 1; i < fverts.length - 1; i++)
				drawTri(ctx, fverts[0], fverts[i], fverts[i + 1], colors[(i - 1) % colors.length], true);
			fverts.forEach((v, i) =>
				drawVertex(ctx, v[0], v[1], i === 0 ? 'v0' : 'v' + i, i === 0 ? '#ffd166' : '#fff')
			);
		} else {
			const cx = 200,
				cy = 120,
				r = 90;
			const pts: number[][] = [];
			for (let a = -90; a < 270; a += 72)
				pts.push([cx + r * Math.cos((a * Math.PI) / 180), cy + r * Math.sin((a * Math.PI) / 180)]);
			for (let i = 1; i < pts.length - 1; i++)
				drawTri(ctx, pts[0], pts[i], pts[i + 1], colors[i - 1], true);
			pts.forEach((v, i) => drawVertex(ctx, v[0], v[1], String(i), '#fff'));
			ctx.fillStyle = '#5a5a80';
			ctx.font = '14px IBM Plex Mono';
			ctx.textAlign = 'center';
			ctx.fillText('tessellated into', 430, 80);
		}
		primDesc = primDescs[primType];
	}

	function drawTri(
		ctx: CanvasRenderingContext2D,
		a: number[] | [number, number],
		b: number[] | [number, number],
		c: number[] | [number, number],
		color: string,
		_: boolean
	) {
		ctx.beginPath();
		ctx.moveTo(a[0], a[1]);
		ctx.lineTo(b[0], b[1]);
		ctx.lineTo(c[0], c[1]);
		ctx.closePath();
		ctx.fillStyle = color + '40';
		ctx.fill();
		ctx.strokeStyle = color;
		ctx.lineWidth = 1.5;
		ctx.stroke();
	}
	function drawVertex(
		ctx: CanvasRenderingContext2D,
		x: number,
		y: number,
		label: string,
		color: string
	) {
		ctx.beginPath();
		ctx.arc(x, y, 5, 0, Math.PI * 2);
		ctx.fillStyle = color || '#fff';
		ctx.fill();
		ctx.font = '11px IBM Plex Mono';
		ctx.fillStyle = '#aaa';
		ctx.textAlign = 'center';
		ctx.fillText(label, x, y - 10);
	}

	// ── STEP RASTERIZER ──
	function buildStepPixels() {
		const { v0, v1, v2 } = stepTri;
		stepPixels = [];
		const minX = Math.max(0, Math.floor(Math.min(v0[0], v1[0], v2[0])));
		const maxX = Math.min(STEP_GRID - 1, Math.floor(Math.max(v0[0], v1[0], v2[0])));
		const minY = Math.max(0, Math.floor(Math.min(v0[1], v1[1], v2[1])));
		const maxY = Math.min(STEP_GRID - 1, Math.floor(Math.max(v0[1], v1[1], v2[1])));
		statBbox = `(${minX},${minY})→(${maxX},${maxY})`;
		for (let y = minY; y <= maxY; y++)
			for (let x = minX; x <= maxX; x++) {
				const e0 = edgeFn(v0[0], v0[1], v1[0], v1[1], x + 0.5, y + 0.5);
				const e1 = edgeFn(v1[0], v1[1], v2[0], v2[1], x + 0.5, y + 0.5);
				const e2 = edgeFn(v2[0], v2[1], v0[0], v0[1], x + 0.5, y + 0.5);
				stepPixels.push({ x, y, e0, e1, e2, inside: e0 >= 0 && e1 >= 0 && e2 >= 0 });
			}
	}

	function drawStep(cur = -1) {
		if (!stepCanvas) return;
		const ctx = stepCanvas.getContext('2d')!;
		const { v0, v1, v2 } = stepTri;
		ctx.clearRect(0, 0, stepCanvas.width, stepCanvas.height);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, stepCanvas.width, stepCanvas.height);
		for (let y = 0; y < STEP_GRID; y++)
			for (let x = 0; x < STEP_GRID; x++) {
				const s = stepState[y * STEP_GRID + x];
				let bg = '#0e0e1a';
				if (s === 'inside') bg = '#00e5c820';
				else if (s === 'tested') bg = '#33335540';
				ctx.fillStyle = bg;
				ctx.fillRect(x * STEP_PX, y * STEP_PX, STEP_PX, STEP_PX);
				ctx.strokeStyle = '#1a1a2e';
				ctx.lineWidth = 0.5;
				ctx.strokeRect(x * STEP_PX, y * STEP_PX, STEP_PX, STEP_PX);
			}
		if (stepPixels.length > 0) {
			const mnX = Math.min(...stepPixels.map((p) => p.x)),
				mxX = Math.max(...stepPixels.map((p) => p.x));
			const mnY = Math.min(...stepPixels.map((p) => p.y)),
				mxY = Math.max(...stepPixels.map((p) => p.y));
			ctx.strokeStyle = '#ffd16660';
			ctx.lineWidth = 1.5;
			ctx.setLineDash([3, 3]);
			ctx.strokeRect(
				mnX * STEP_PX,
				mnY * STEP_PX,
				(mxX - mnX + 1) * STEP_PX,
				(mxY - mnY + 1) * STEP_PX
			);
			ctx.setLineDash([]);
		}
		for (let i = 0; i < stepState.length; i++) {
			if (stepState[i] === 'inside') {
				const x = i % STEP_GRID,
					y = Math.floor(i / STEP_GRID);
				ctx.fillStyle = '#00e5c8';
				ctx.fillRect(x * STEP_PX + 1, y * STEP_PX + 1, STEP_PX - 2, STEP_PX - 2);
			}
		}
		if (cur >= 0 && cur < stepPixels.length) {
			const { x, y } = stepPixels[cur];
			ctx.fillStyle = 'rgba(255,255,255,0.85)';
			ctx.fillRect(x * STEP_PX + 2, y * STEP_PX + 2, STEP_PX - 4, STEP_PX - 4);
		}
		ctx.beginPath();
		ctx.moveTo(v0[0] * STEP_PX + STEP_PX / 2, v0[1] * STEP_PX + STEP_PX / 2);
		ctx.lineTo(v1[0] * STEP_PX + STEP_PX / 2, v1[1] * STEP_PX + STEP_PX / 2);
		ctx.lineTo(v2[0] * STEP_PX + STEP_PX / 2, v2[1] * STEP_PX + STEP_PX / 2);
		ctx.closePath();
		ctx.strokeStyle = '#ff5f3a';
		ctx.lineWidth = 1.5;
		ctx.stroke();
	}

	function updateStepStats(cur: number) {
		statTested = stepPixels.slice(0, stepIdx).length;
		statInside = stepPixels.slice(0, stepIdx).filter((p) => p.inside).length;
		statEff = stepPixels.length
			? ((statInside / (stepPixels.length || 1)) * 100).toFixed(1) + '%'
			: '—';
		stepInfo = `Pixel ${Math.min(stepIdx, stepPixels.length)} / ${stepPixels.length}`;
		if (cur >= 0 && cur < stepPixels.length) {
			const p = stepPixels[cur];
			statCur = `(${p.x},${p.y})`;
			statEdge = `${p.e0.toFixed(1)} / ${p.e1.toFixed(1)} / ${p.e2.toFixed(1)}`;
		} else {
			statCur = '—';
			statEdge = '—';
		}
	}

	function doStepOnce() {
		if (stepIdx >= stepPixels.length) return;
		const p = stepPixels[stepIdx];
		stepState[p.y * STEP_GRID + p.x] = p.inside ? 'inside' : 'tested';
		stepState = [...stepState];
		drawStep(stepIdx + 1 < stepPixels.length ? stepIdx + 1 : -1);
		updateStepStats(stepIdx);
		stepIdx++;
	}

	function doStepReset() {
		if (stepTimer) {
			clearInterval(stepTimer);
			stepTimer = null;
		}
		stepPlaying = false;
		buildStepPixels();
		stepIdx = 0;
		stepState = new Array(STEP_GRID * STEP_GRID).fill(null);
		drawStep(-1);
		updateStepStats(-1);
	}

	function doStepPlay() {
		if (stepTimer) {
			clearInterval(stepTimer);
			stepTimer = null;
			stepPlaying = false;
			return;
		}
		if (stepIdx >= stepPixels.length) doStepReset();
		stepPlaying = true;
		const speeds = [250, 120, 60, 25, 8];
		const spd = speeds[stepSpeed - 1];
		stepTimer = setInterval(() => {
			doStepOnce();
			if (stepIdx >= stepPixels.length) {
				clearInterval(stepTimer!);
				stepTimer = null;
				stepPlaying = false;
			}
		}, spd);
	}

	// ── DRAGGABLE RASTERIZER ──
	function getCanvasPos(e: PointerEvent) {
		const rect = rastCanvas.getBoundingClientRect();
		return {
			x: (e.clientX - rect.left) * (rastCanvas.width / rect.width),
			y: (e.clientY - rect.top) * (rastCanvas.height / rect.height)
		};
	}
	function onRastDown(e: PointerEvent) {
		const { x, y } = getCanvasPos(e);
		for (let i = 0; i < verts.length; i++) {
			if (Math.hypot(verts[i].x - x, verts[i].y - y) < 18) {
				dragging = i;
				e.preventDefault();
				return;
			}
		}
	}
	function onRastMove(e: PointerEvent) {
		if (dragging === null) return;
		const { x, y } = getCanvasPos(e);
		verts[dragging] = {
			x: Math.max(0, Math.min(rastCanvas.width, x)),
			y: Math.max(0, Math.min(rastCanvas.height, y))
		};
		verts = [...verts];
		renderRast();
		e.preventDefault();
	}
	function onRastUp() {
		dragging = null;
	}

	function renderRast() {
		if (!rastCanvas) return;
		const ctx = rastCanvas.getContext('2d')!;
		const W = rastCanvas.width,
			H = rastCanvas.height;
		ctx.clearRect(0, 0, W, H);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, W, H);
		const v0 = verts[0],
			v1 = verts[1],
			v2 = verts[2];
		if (overlays.grid) {
			ctx.strokeStyle = '#12122a';
			ctx.lineWidth = 0.5;
			for (let x = 0; x < W; x += CELL) {
				ctx.beginPath();
				ctx.moveTo(x, 0);
				ctx.lineTo(x, H);
				ctx.stroke();
			}
			for (let y = 0; y < H; y += CELL) {
				ctx.beginPath();
				ctx.moveTo(0, y);
				ctx.lineTo(W, y);
				ctx.stroke();
			}
		}
		const minX = Math.max(0, Math.floor(Math.min(v0.x, v1.x, v2.x) / CELL) * CELL);
		const maxX = Math.min(W, Math.ceil(Math.max(v0.x, v1.x, v2.x) / CELL) * CELL);
		const minY = Math.max(0, Math.floor(Math.min(v0.y, v1.y, v2.y) / CELL) * CELL);
		const maxY = Math.min(H, Math.ceil(Math.max(v0.y, v1.y, v2.y) / CELL) * CELL);
		let tested = 0,
			filled = 0;
		for (let y = minY; y < maxY; y += CELL)
			for (let x = minX; x < maxX; x += CELL) {
				const cx = x + CELL / 2,
					cy = y + CELL / 2;
				const e0 = edgeFn(v0.x, v0.y, v1.x, v1.y, cx, cy);
				const e1 = edgeFn(v1.x, v1.y, v2.x, v2.y, cx, cy);
				const e2 = edgeFn(v2.x, v2.y, v0.x, v0.y, cx, cy);
				tested++;
				if (e0 >= 0 && e1 >= 0 && e2 >= 0) {
					ctx.fillStyle = '#00e5c8';
					ctx.fillRect(x + 1, y + 1, CELL - 2, CELL - 2);
					filled++;
				}
			}
		if (overlays.bbox) {
			ctx.strokeStyle = '#ffd166aa';
			ctx.lineWidth = 1.5;
			ctx.setLineDash([5, 4]);
			ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
			ctx.setLineDash([]);
		}
		ctx.beginPath();
		ctx.moveTo(v0.x, v0.y);
		ctx.lineTo(v1.x, v1.y);
		ctx.lineTo(v2.x, v2.y);
		ctx.closePath();
		ctx.strokeStyle = '#ff5f3aee';
		ctx.lineWidth = 2;
		ctx.stroke();
		ctx.fillStyle = '#ff5f3a08';
		ctx.fill();
		if (overlays.edges) {
			[
				[v0, v1],
				[v1, v2],
				[v2, v0]
			].forEach(([a, b]) => {
				const mx = (a.x + b.x) / 2,
					my = (a.y + b.y) / 2,
					dx = b.x - a.x,
					dy = b.y - a.y,
					len = Math.sqrt(dx * dx + dy * dy);
				const nx = (-dy / len) * 25,
					ny = (dx / len) * 25;
				ctx.beginPath();
				ctx.moveTo(mx, my);
				ctx.lineTo(mx + nx, my + ny);
				ctx.strokeStyle = '#a78bfa';
				ctx.lineWidth = 1.5;
				ctx.stroke();
				ctx.beginPath();
				ctx.arc(mx + nx, my + ny, 3, 0, Math.PI * 2);
				ctx.fillStyle = '#a78bfa';
				ctx.fill();
			});
		}
		if (overlays.verts) {
			const labels = ['v0', 'v1', 'v2'],
				colors = ['#ffd166', '#00e5c8', '#ff5f3a'];
			verts.forEach((v, i) => {
				ctx.beginPath();
				ctx.arc(v.x, v.y, dragging === i ? 10 : 7, 0, Math.PI * 2);
				ctx.fillStyle = colors[i];
				ctx.fill();
				ctx.strokeStyle = '#fff';
				ctx.lineWidth = 1.5;
				ctx.stroke();
				ctx.fillStyle = '#fff';
				ctx.font = 'bold 12px IBM Plex Mono';
				ctx.textAlign = 'center';
				ctx.fillText(labels[i], v.x, v.y - 15);
				ctx.fillStyle = '#aaa';
				ctx.font = '10px IBM Plex Mono';
				ctx.fillText(`(${Math.round(v.x / CELL)},${Math.round(v.y / CELL)})`, v.x, v.y - 3);
			});
		}
		const bbW = Math.ceil((maxX - minX) / CELL),
			bbH = Math.ceil((maxY - minY) / CELL);
		rastBbox = `(${Math.round(minX / CELL)},${Math.round(minY / CELL)}) → (${Math.round(maxX / CELL)},${Math.round(maxY / CELL)})`;
		rastTested = String(tested);
		rastFilled = String(filled);
		rastBbarea = `${bbW} × ${bbH} = ${bbW * bbH} px`;
		const triArea = Math.abs(edgeFn(v0.x, v0.y, v1.x, v1.y, v2.x, v2.y)) / (2 * CELL * CELL);
		rastTarea = `~${triArea.toFixed(1)} px`;
		rastEff = tested ? ((filled / tested) * 100).toFixed(1) + '%' : '—';
		rastCodeHtml = `<span class="lang-tag">vertices</span>v0 = (${Math.round(v0.x / CELL)}, ${Math.round(v0.y / CELL)})\nv1 = (${Math.round(v1.x / CELL)}, ${Math.round(v1.y / CELL)})\nv2 = (${Math.round(v2.x / CELL)}, ${Math.round(v2.y / CELL)})\n\n<span class="cm"># bounding box</span>\nmin = (${Math.round(minX / CELL)}, ${Math.round(minY / CELL)})\nmax = (${Math.round(maxX / CELL)}, ${Math.round(maxY / CELL)})\n\ntested = ${tested}\nfilled = ${filled}`;
	}

	function toggleOverlay(name: keyof typeof overlays) {
		overlays[name] = !overlays[name];
		overlays = { ...overlays };
		renderRast();
	}

	function answerDebug(qi: number, oi: number) {
		if (dbgAnswers[qi] !== null) return;
		dbgAnswers[qi] = oi;
		dbgAnswers = [...dbgAnswers];
		if (dbgAnswers.every((a) => a !== null)) {
			dbgDone = true;
			dbgScore = debugQuestions.filter((q, i) => dbgAnswers[i] === q.correct).length;
		}
	}

	onMount(() => {
		const onScroll = () => {
			readingProgress = Math.min(
				100,
				(window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
			);
		};
		window.addEventListener('scroll', onScroll);
		drawPrimitives();
		buildStepPixels();
		stepState = new Array(STEP_GRID * STEP_GRID).fill(null);
		drawStep(-1);
		updateStepStats(-1);
		renderRast();
		return () => {
			window.removeEventListener('scroll', onScroll);
			if (stepTimer) clearInterval(stepTimer);
		};
	});
</script>

<!-- ── HERO ── -->
<div class="module-hero">
	<div class="module-number" aria-hidden="true">02</div>
	<div class="module-tag">Module 02 · Theory + Practice</div>
	<h1 class="module-title">The <span>Rendering</span><br />Process</h1>
	<div class="progress-bar-wrap">
		<div class="progress-bar-fill" style="width:{readingProgress}%"></div>
	</div>
</div>

<!-- ── TOC ── -->
<nav class="toc">
	<div class="toc-label">Contents</div>
	<ul class="toc-list">
		<li><a href="#objectives">Objectives</a></li>
		<li><a href="#geometry-to-pixels">Geometry to Pixels</a></li>
		<li><a href="#triangles">Triangles as Primitives</a></li>
		<li><a href="#rasterization">The Rasterization Algorithm</a></li>
		<li><a href="#sw-vs-hw">Software vs Hardware</a></li>
		<li><a href="#why-gpu">Why GPUs Exist</a></li>
		<li><a href="#practical">Practical Work</a></li>
		<li><a href="#assessment">Assessment</a></li>
	</ul>
</nav>

<!-- ── OBJECTIVES ── -->
<section id="objectives" class="objectives" style="border-left-color:var(--accent2);">
	<div class="objectives-label" style="color:var(--accent2);">Learning Objectives</div>
	<ul>
		<li>Understand the conceptual stages of a rendering pipeline</li>
		<li>Explain vertices, primitives, rasterization, and framebuffer output</li>
		<li>Implement a software triangle rasterizer from scratch</li>
		<li>Visualize and reason about rasterization step-by-step</li>
	</ul>
</section>

<!-- ── SECTION 1 ── -->
<section id="geometry-to-pixels" class="section">
	<div class="section-header">
		<span class="section-num">02.01</span>
		<h2 class="section-title">From Geometric Data to Pixels</h2>
	</div>
	<p>
		A game scene is described geometrically: characters as meshes of triangles, positions as
		coordinates, surfaces as mathematical relationships. None of this is directly displayable. The
		rendering pipeline converts this abstract geometric description into a concrete grid of pixel
		colors.
	</p>
	<p>
		At the end of every pipeline, the answer to the same question is written into the framebuffer: <em
			>what color should this pixel be?</em
		> Everything before that is preparation.
	</p>
	<!-- Pipeline Demo -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Rendering Pipeline Stages</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1.25rem;">
				Click any stage to learn what happens there.
			</p>
			<div class="pipeline">
				{#each [['📐', 'Vertex Input', 'Positions, colors, UVs'], ['🔺', 'Primitive Assembly', 'Vertices → triangles'], ['⬜', 'Rasterization', 'Triangles → fragments'], ['🎨', 'Fragment Shading', 'Compute pixel color'], ['🖥️', 'Output', 'Write to framebuffer']] as [icon, name, desc], i}
					<div
						class="pipeline-stage"
						class:active={activePipeStage === i}
						on:click={() => showPipe(i)}
						role="button"
						tabindex="0"
						on:keydown={(e) => e.key === 'Enter' && showPipe(i)}
					>
						<div class="pipe-icon">{icon}</div>
						<div class="pipe-name">{name}</div>
						<div class="pipe-desc">{desc}</div>
					</div>
				{/each}
			</div>
			<div class="pipeline-detail">{@html pipeDetail}</div>
		</div>
	</div>
	<p>
		The pipeline is one-directional — data flows forward, one stage at a time. This strict ordering
		is what allows GPUs to process many primitives simultaneously without conflict.
	</p>
</section>

<!-- ── SECTION 2 ── -->
<section id="triangles" class="section">
	<div class="section-header">
		<span class="section-num">02.02</span>
		<h2 class="section-title">Triangles as the Universal Primitive</h2>
	</div>
	<p>
		All rendering hardware works with triangles. A triangle is the simplest polygon that defines a
		surface: any three non-collinear points define a unique plane, and the interior of the triangle
		is always flat and always convex.
	</p>
	<p>
		Any polygon can be decomposed into triangles (<em>tessellation</em>). Any curve can be
		approximated by a sequence of small triangles. This universality means hardware only needs to
		solve one problem.
	</p>
	<div class="callout info">
		<div class="callout-label">Why Not Quads?</div>
		A quadrilateral requires four vertices. If those four points are not coplanar (common in 3D), the
		"quad" has no well-defined surface — two of its possible triangulations produce different planes.
		Triangles never have this ambiguity. GPUs convert quads to triangles internally anyway.
	</div>
	<!-- Primitives Demo -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Primitive Types and Triangle Construction</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<div class="prim-btn-row">
				{#each [['triangles', 'TRIANGLES'], ['strip', 'TRIANGLE_STRIP'], ['fan', 'TRIANGLE_FAN'], ['mesh', 'Complex Mesh']] as [val, label]}
					<button
						class="btn orange"
						class:active={primType === val}
						on:click={() => {
							primType = val;
							drawPrimitives();
						}}>{label}</button
					>
				{/each}
			</div>
			<canvas
				bind:this={primCanvas}
				width="860"
				height="220"
				style="width:100%;border:1px solid var(--border2);background:#0a0a16;display:block;"
			></canvas>
			<div style="margin-top:0.75rem;font-size:12px;color:var(--muted);">{primDesc}</div>
		</div>
	</div>
	<table>
		<thead
			><tr
				><th>Primitive Mode</th><th>Vertices Needed</th><th>Triangles Produced</th><th
					>Typical Use</th
				></tr
			></thead
		>
		<tbody>
			<tr><td>TRIANGLES</td><td>3N</td><td>N</td><td>General geometry</td></tr>
			<tr><td>TRIANGLE_STRIP</td><td>N+2</td><td>N</td><td>Terrain strips, ribbons</td></tr>
			<tr><td>TRIANGLE_FAN</td><td>N+2</td><td>N</td><td>Circles, cones, radial shapes</td></tr>
		</tbody>
	</table>
</section>

<!-- ── SECTION 3 ── -->
<section id="rasterization" class="section">
	<div class="section-header">
		<span class="section-num">02.03</span>
		<h2 class="section-title">The Rasterization Algorithm</h2>
	</div>
	<p>
		Rasterization answers the question: <em>which pixels does this triangle cover?</em> The standard
		approach is the <strong>edge function test</strong>. For each candidate pixel, three tests
		determine whether the pixel center falls inside the triangle.
	</p>
	<pre><code
			><span class="kw">def</span> <span class="fn">edge</span>(ax, ay, bx, by, px, py):
    <span class="cm"># Signed area of the parallelogram formed by (A→B) and (A→P).</span>
    <span class="cm"># Positive if P is to the left of A→B (counter-clockwise winding).</span>
    <span class="kw">return</span> (bx - ax) * (py - ay) - (by - ay) * (px - ax)<span
				class="lang-tag">python</span
			></code
		></pre>
	<p>
		A pixel is inside the triangle if all three edge functions return the same sign. For
		counter-clockwise vertex ordering, all three must be <strong>≥ 0</strong>.
	</p>
	<!-- Step-by-step Rasterizer -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Animated · Step-by-Step Rasterization</span>
			<span class="demo-badge animated">ANIMATED</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Watch the algorithm test every pixel in the bounding box. Yellow = bounding box, teal =
				inside triangle.
			</p>
			<div class="step-controls">
				<button class="btn" on:click={doStepPlay}>{stepPlaying ? '⏸ Pause' : '▶ Play'}</button>
				<button class="btn" on:click={doStepOnce}>Step →</button>
				<button class="btn" on:click={doStepReset}>↺ Reset</button>
				<div style="display:flex;gap:0.75rem;align-items:center;margin-left:0.5rem;">
					<span style="font-size:11px;color:var(--muted);">Speed</span>
					<input
						type="range"
						bind:value={stepSpeed}
						min="1"
						max="5"
						style="width:80px;-webkit-appearance:none;height:3px;background:var(--border2);outline:none;"
					/>
				</div>
				<span class="step-info">{stepInfo}</span>
			</div>
			<div class="two-col" style="align-items:start;">
				<div>
					<canvas
						bind:this={stepCanvas}
						width="240"
						height="240"
						style="border:1px solid var(--border2);width:100%;image-rendering:pixelated;display:block;"
					></canvas>
				</div>
				<div style="display:flex;flex-direction:column;gap:1rem;">
					<div class="stats-panel">
						<div class="stat-row">
							<span class="stat-label">Bounding box</span><span class="stat-val">{statBbox}</span>
						</div>
						<div class="stat-row">
							<span class="stat-label">Pixels tested</span><span class="stat-val">{statTested}</span
							>
						</div>
						<div class="stat-row">
							<span class="stat-label">Pixels inside</span><span class="stat-val">{statInside}</span
							>
						</div>
						<div class="stat-row">
							<span class="stat-label">Efficiency</span><span class="stat-val">{statEff}</span>
						</div>
						<div class="stat-row">
							<span class="stat-label">Current pixel</span><span class="stat-val">{statCur}</span>
						</div>
						<div class="stat-row">
							<span class="stat-label">e0 / e1 / e2</span><span class="stat-val">{statEdge}</span>
						</div>
					</div>
					<div style="font-size:11px;color:var(--muted);line-height:1.8;">
						<span
							style="display:inline-block;width:10px;height:10px;background:var(--accent4);margin-right:6px;vertical-align:middle;"
						></span>Bounding box<br />
						<span
							style="display:inline-block;width:10px;height:10px;background:#333355;margin-right:6px;vertical-align:middle;"
						></span>Tested, outside<br />
						<span
							style="display:inline-block;width:10px;height:10px;background:var(--accent);margin-right:6px;vertical-align:middle;"
						></span>Inside triangle<br />
						<span
							style="display:inline-block;width:10px;height:10px;background:#fff;margin-right:6px;vertical-align:middle;"
						></span>Current test
					</div>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- ── SECTION 4 ── -->
<section id="sw-vs-hw" class="section">
	<div class="section-header">
		<span class="section-num">02.04</span>
		<h2 class="section-title">Software vs Hardware Rendering</h2>
	</div>
	<p>
		The rasterizer you just saw running step-by-step is a <em>software rasterizer</em>. It executes
		on the CPU, one pixel at a time, in a Python loop. This is instructive — but it is also orders
		of magnitude too slow for real games.
	</p>
	<table>
		<thead><tr><th></th><th>Software Renderer (CPU)</th><th>Hardware Renderer (GPU)</th></tr></thead
		>
		<tbody>
			<tr><td>Pixel processing</td><td>Sequential</td><td>Massively parallel</td></tr>
			<tr><td>Cores available</td><td>4–32</td><td>Thousands to tens of thousands</td></tr>
			<tr><td>Programming model</td><td>Arbitrary code</td><td>Constrained shader programs</td></tr>
			<tr><td>Memory bandwidth</td><td>General RAM</td><td>Dedicated VRAM (much faster)</td></tr>
			<tr><td>Frame rate at 1080p</td><td>Often &lt;1 FPS</td><td>60–240+ FPS</td></tr>
		</tbody>
	</table>
</section>

<!-- ── SECTION 5 ── -->
<section id="why-gpu" class="section">
	<div class="section-header">
		<span class="section-num">02.05</span>
		<h2 class="section-title">Why GPUs Exist</h2>
	</div>
	<p>
		The key observation is that computing the color of pixel (100, 200) is entirely independent of
		computing the color of pixel (101, 200). Both can be computed at exactly the same time on
		different hardware units.
	</p>
	<p>
		This is called <strong>data parallelism</strong>. CPUs are built to execute a single stream of
		instructions as quickly as possible. GPUs trade most of that complexity for sheer number of
		arithmetic units — they run <em>many simple programs simultaneously</em>.
	</p>
	<div class="callout warn">
		<div class="callout-label">The Trade-off</div>
		GPU cores are much simpler than CPU cores. They cannot make independent decisions efficiently — if
		one thread in a group of 32 takes a different code path, all 32 threads wait. This is called<em
			>warp divergence</em
		>, and writing GPU-friendly code means understanding it.
	</div>
</section>

<hr class="divider" />

<!-- ── SECTION 6: PRACTICAL ── -->
<section id="practical" class="section">
	<div class="section-header">
		<span class="section-num">02.06</span>
		<h2 class="section-title">Practical Work</h2>
	</div>
	<p>
		The exercise builds a complete software rasterizer. The final version handles arbitrary triangle
		positions, computes bounding boxes, applies the edge function test, and writes to a NumPy
		framebuffer.
	</p>
	<!-- Draggable Rasterizer -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Draggable Triangle Rasterizer</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Drag the three vertices. The software rasterizer recomputes in real time. Toggle overlays to
				inspect internals.
			</p>
			<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
				{#each [['bbox', 'Bounding Box'], ['grid', 'Pixel Grid'], ['verts', 'Vertices'], ['edges', 'Edge Normals']] as [key, label]}
					<button
						class="btn green"
						class:active={overlays[key as keyof typeof overlays]}
						on:click={() => toggleOverlay(key as keyof typeof overlays)}>{label}</button
					>
				{/each}
			</div>
			<canvas
				bind:this={rastCanvas}
				width="860"
				height="400"
				style="width:100%;border:1px solid var(--border2);background:#08080f;touch-action:none;display:block;cursor:crosshair;"
				on:pointerdown={onRastDown}
				on:pointermove={onRastMove}
				on:pointerup={onRastUp}
			></canvas>
			<div class="two-col" style="margin-top:1rem;">
				<div class="stats-panel">
					<div class="stat-row">
						<span class="stat-label">Bounding box</span><span class="stat-val">{rastBbox}</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Total pixels tested</span><span class="stat-val"
							>{rastTested}</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Pixels filled</span><span class="stat-val">{rastFilled}</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Bounding box area</span><span class="stat-val"
							>{rastBbarea}</span
						>
					</div>
					<div class="stat-row">
						<span class="stat-label">Triangle area</span><span class="stat-val">{rastTarea}</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Fill efficiency</span><span class="stat-val">{rastEff}</span>
					</div>
				</div>
				<pre
					style="font-size:11px;max-height:160px;overflow:auto;margin:0;">{@html rastCodeHtml}</pre>
			</div>
		</div>
	</div>
</section>

<hr class="divider" />

<!-- ── ASSESSMENT ── -->
<section id="assessment" class="assessment-section">
	<div class="assessment-header">Assessment · Debug the Rasterizer</div>
	<div class="assessment-sub">3 broken implementations. Identify the bug in each.</div>
	{#each debugQuestions as q, qi}
		<div class="debug-question">
			<div class="debug-q-header">Question {qi + 1} · {q.title}</div>
			<div style="position:relative;">
				<pre
					style="margin:0;padding:1rem 1.25rem;font-size:12px;line-height:1.7;overflow-x:auto;"><!--
-->{#each q.code as line, li}<div
							class:bug-highlight={li === q.bugLine}>{line
								.replace(/&/g, '&amp;')
								.replace(/</g, '&lt;')
								.replace(/>/g, '&gt;')}</div>{/each}<span class="lang-tag">python</span></pre>
			</div>
			<div class="debug-options">
				{#each q.options as opt, oi}
					<div
						class="debug-option"
						class:correct={dbgAnswers[qi] !== null && oi === q.correct}
						class:wrong={dbgAnswers[qi] === oi && oi !== q.correct}
						class:disabled={dbgAnswers[qi] !== null}
						on:click={() => answerDebug(qi, oi)}
						role="button"
						tabindex="0"
						on:keydown={(e) => e.key === 'Enter' && answerDebug(qi, oi)}
					>
						{opt}
					</div>
				{/each}
			</div>
			{#if dbgAnswers[qi] !== null}
				<div
					class="debug-feedback"
					class:ok={dbgAnswers[qi] === q.correct}
					class:bad={dbgAnswers[qi] !== q.correct}
				>
					{dbgAnswers[qi] === q.correct ? '✓' : '✗'}
					{q.explanation}
				</div>
			{/if}
		</div>
	{/each}
	{#if dbgDone}
		<div
			class="quiz-score"
			style="border-color:{dbgScore === 3
				? 'var(--accent)'
				: dbgScore >= 2
					? 'var(--accent3)'
					: 'var(--accent2)'}"
		>
			<div class="score-num" style="color:var(--accent2);">{dbgScore}/3</div>
			<div class="score-label">Assessment complete. Proceed to Module 03 when ready.</div>
		</div>
	{/if}
</section>

<style>
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
		color: var(--accent2);
		border: 1px solid var(--accent2);
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
		color: var(--accent2);
	}
	.prim-btn-row {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}
	.step-controls {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
		align-items: center;
	}
	.step-info {
		font-size: 12px;
		color: var(--muted);
		margin-left: auto;
	}
</style>
