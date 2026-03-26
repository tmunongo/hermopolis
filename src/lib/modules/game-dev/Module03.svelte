<script lang="ts">
	import { onMount } from 'svelte';

	let readingProgress = 0;

	// ── MATRIX HELPERS ──
	function mat3() {
		return [
			[1, 0, 0],
			[0, 1, 0],
			[0, 0, 1]
		];
	}
	function matMul(A: number[][], B: number[][]) {
		const C = [
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0]
		];
		for (let i = 0; i < 3; i++)
			for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) C[i][j] += A[i][k] * B[k][j];
		return C;
	}
	function matVec(M: number[][], v: number[]) {
		return [
			M[0][0] * v[0] + M[0][1] * v[1] + M[0][2] * v[2],
			M[1][0] * v[0] + M[1][1] * v[1] + M[1][2] * v[2],
			M[2][0] * v[0] + M[2][1] * v[1] + M[2][2] * v[2]
		];
	}
	function transMat(tx: number, ty: number) {
		return [
			[1, 0, tx],
			[0, 1, ty],
			[0, 0, 1]
		];
	}
	function rotMat(deg: number) {
		const r = (deg * Math.PI) / 180,
			c = Math.cos(r),
			s = Math.sin(r);
		return [
			[c, -s, 0],
			[s, c, 0],
			[0, 0, 1]
		];
	}
	function scaleMat(sx: number, sy: number) {
		return [
			[sx, 0, 0],
			[0, sy, 0],
			[0, 0, 1]
		];
	}
	function applyMat(M: number[][], pts: number[][]) {
		return pts.map((p) => matVec(M, [p[0], p[1], 1]));
	}
	function fmt(v: number) {
		return Math.abs(v) < 0.001 ? '0' : v.toFixed(2);
	}

	// Arrow shape in local space
	const ARROW_PTS = [
		[0, -40],
		[15, -15],
		[8, -15],
		[8, 30],
		[-8, 30],
		[-8, -15],
		[-15, -15]
	];
	const HOUSE_PTS = [
		[-30, 30],
		[30, 30],
		[30, -10],
		[0, -40],
		[-30, -10]
	];
	const DIAMOND_PTS = [
		[0, -22],
		[14, 0],
		[0, 22],
		[-14, 0]
	];

	function drawShapeCtx(
		ctx: CanvasRenderingContext2D,
		pts: number[][],
		fill: string,
		stroke: string,
		lw = 1.5
	) {
		if (pts.length < 2) return;
		ctx.beginPath();
		ctx.moveTo(pts[0][0], pts[0][1]);
		pts.slice(1).forEach((p) => ctx.lineTo(p[0], p[1]));
		ctx.closePath();
		ctx.fillStyle = fill;
		ctx.fill();
		ctx.strokeStyle = stroke;
		ctx.lineWidth = lw;
		ctx.stroke();
	}
	function drawAxes(ctx: CanvasRenderingContext2D, M: number[][], len = 40, label = '') {
		const ox = matVec(M, [0, 0, 1]),
			xx = matVec(M, [len, 0, 1]),
			yx = matVec(M, [0, -len, 1]);
		ctx.beginPath();
		ctx.moveTo(ox[0], ox[1]);
		ctx.lineTo(xx[0], xx[1]);
		ctx.strokeStyle = '#ef4444';
		ctx.lineWidth = 1.5;
		ctx.stroke();
		ctx.beginPath();
		ctx.moveTo(ox[0], ox[1]);
		ctx.lineTo(yx[0], yx[1]);
		ctx.strokeStyle = '#22c55e';
		ctx.lineWidth = 1.5;
		ctx.stroke();
		if (label) {
			ctx.font = '11px IBM Plex Mono';
			ctx.fillStyle = '#aaa';
			ctx.textAlign = 'center';
			ctx.fillText(label, ox[0], ox[1] + 16);
		}
	}

	// ── SPACES DEMO ──
	let spacesCanvas: HTMLCanvasElement;
	let spaceMode = 'local';
	let spacesDesc =
		'Local space: The arrow is defined around (0,0) — its own center. Vertex coordinates in a mesh file are always in local space.';
	const spaceDescs: { [k: string]: string } = {
		local:
			'Local space: The arrow is defined around (0,0) — its own center. Axes are aligned to the object. Vertex coordinates in a mesh file are always in local space.',
		world:
			'World space: The arrow has been placed at position (200, 120) in the scene and rotated 30°. The world origin (0,0) is fixed at top-left. The local axes have rotated with the object.',
		screen:
			'Screen space: After the camera transform, coordinates are mapped to pixel positions. (0,0) is top-left, y increases downward. This is what the rasterizer works with.'
	};

	function drawSpaces() {
		if (!spacesCanvas) return;
		const ctx = spacesCanvas.getContext('2d')!;
		const W = spacesCanvas.width,
			H = spacesCanvas.height;
		ctx.clearRect(0, 0, W, H);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, W, H);
		const grid = 40;
		ctx.strokeStyle = '#111922';
		ctx.lineWidth = 1;
		for (let x = 0; x < W; x += grid) {
			ctx.beginPath();
			ctx.moveTo(x, 0);
			ctx.lineTo(x, H);
			ctx.stroke();
		}
		for (let y = 0; y < H; y += grid) {
			ctx.beginPath();
			ctx.moveTo(0, y);
			ctx.lineTo(W, y);
			ctx.stroke();
		}
		const cx = W / 2,
			cy = H / 2;
		if (spaceMode === 'local') {
			ctx.strokeStyle = '#1a2228';
			ctx.lineWidth = 1;
			ctx.beginPath();
			ctx.moveTo(0, cy);
			ctx.lineTo(W, cy);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(cx, 0);
			ctx.lineTo(cx, H);
			ctx.stroke();
			const M = transMat(cx, cy);
			drawShapeCtx(ctx, applyMat(M, ARROW_PTS), '#a78bfa30', '#a78bfa', 2);
			drawAxes(ctx, M, 50, 'local (0,0)');
			ctx.font = '10px IBM Plex Mono';
			ctx.fillStyle = '#a78bfa';
			ctx.textAlign = 'center';
			ARROW_PTS.forEach((p) => {
				const wp = matVec(M, [p[0], p[1], 1]);
				ctx.fillText(`(${p[0]},${p[1]})`, wp[0], wp[1] - 6);
			});
		} else if (spaceMode === 'world') {
			ctx.strokeStyle = '#253038';
			ctx.lineWidth = 1;
			ctx.beginPath();
			ctx.moveTo(0, cy);
			ctx.lineTo(W, cy);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(0, H);
			ctx.stroke();
			ctx.font = '11px IBM Plex Mono';
			ctx.fillStyle = '#4a606c';
			ctx.textAlign = 'left';
			ctx.fillText('world (0,0)', 6, 14);
			const ox = cx - 60,
				oy = cy - 40;
			const M = matMul(transMat(ox, oy), rotMat(-30));
			drawShapeCtx(ctx, applyMat(M, ARROW_PTS), '#a78bfa30', '#a78bfa', 2);
			drawAxes(ctx, M, 50, '');
			ctx.font = '11px IBM Plex Mono';
			ctx.fillStyle = '#a78bfa';
			ctx.textAlign = 'center';
			ctx.fillText(`world pos (${Math.round(ox)}, ${Math.round(oy)})`, ox, oy - 40);
		} else {
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(W, 0);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(0, H);
			ctx.stroke();
			ctx.font = '11px IBM Plex Mono';
			ctx.fillStyle = '#4a606c';
			ctx.textAlign = 'left';
			ctx.fillText('(0, 0)', 6, 14);
			ctx.fillText(`(${W}, ${H})`, W - 70, H - 6);
			ctx.strokeStyle = '#253038';
			ctx.lineWidth = 1;
			ctx.setLineDash([4, 4]);
			ctx.beginPath();
			ctx.moveTo(0, cy);
			ctx.lineTo(W, cy);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(cx, 0);
			ctx.lineTo(cx, H);
			ctx.stroke();
			ctx.setLineDash([]);
			ctx.fillStyle = '#253038';
			ctx.textAlign = 'center';
			ctx.fillText('NDC center (0,0)', cx, cy - 8);
			const M = matMul(transMat(cx + 80, cy - 30), matMul(rotMat(-15), scaleMat(0.9, 0.9)));
			drawShapeCtx(ctx, applyMat(M, ARROW_PTS), '#a78bfa30', '#a78bfa', 2);
			const c = matVec(M, [0, 0, 1]);
			ctx.fillStyle = '#a78bfa';
			ctx.fillText(`pixel (${Math.round(c[0])}, ${Math.round(c[1])})`, c[0], c[1] - 36);
		}
		spacesDesc = spaceDescs[spaceMode];
	}

	function setSpaceMode(mode: string) {
		spaceMode = mode;
		drawSpaces();
	}

	// ── TRANSFORM PLAYGROUND ──
	let tfCanvas: HTMLCanvasElement;
	let tx = 0,
		ty = 0,
		rot = 0,
		sx = 100,
		sy = 100;
	let matCells: string[] = Array(9).fill('');

	function drawTransform() {
		if (!tfCanvas) return;
		const ctx = tfCanvas.getContext('2d')!;
		const W = tfCanvas.width,
			H = tfCanvas.height,
			cx = W / 2,
			cy = H / 2;
		ctx.clearRect(0, 0, W, H);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, W, H);
		const grid = 40;
		ctx.strokeStyle = '#111922';
		ctx.lineWidth = 1;
		for (let x = 0; x < W; x += grid) {
			ctx.beginPath();
			ctx.moveTo(x, 0);
			ctx.lineTo(x, H);
			ctx.stroke();
		}
		for (let y = 0; y < H; y += grid) {
			ctx.beginPath();
			ctx.moveTo(0, y);
			ctx.lineTo(W, y);
			ctx.stroke();
		}
		ctx.strokeStyle = '#1e3040';
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(0, cy);
		ctx.lineTo(W, cy);
		ctx.stroke();
		ctx.beginPath();
		ctx.moveTo(cx, 0);
		ctx.lineTo(cx, H);
		ctx.stroke();
		const T = transMat(tx, -ty);
		const R = rotMat(-rot);
		const S = scaleMat(sx / 100, sy / 100);
		const M = matMul(matMul(T, R), S);
		// update matrix display
		const flat = [M[0][0], M[0][1], M[0][2], M[1][0], M[1][1], M[1][2], M[2][0], M[2][1], M[2][2]];
		matCells = flat.map((v) => fmt(v));
		// ghost
		drawShapeCtx(ctx, applyMat(transMat(cx, cy), ARROW_PTS), '#ffffff08', '#253038', 1);
		// transformed
		const fullM = matMul(transMat(cx, cy), M);
		drawShapeCtx(ctx, applyMat(fullM, ARROW_PTS), '#a78bfa25', '#a78bfa', 2);
		drawAxes(ctx, fullM, 44);
		const o = matVec(fullM, [0, 0, 1]);
		ctx.beginPath();
		ctx.arc(o[0], o[1], 5, 0, Math.PI * 2);
		ctx.fillStyle = '#a78bfa';
		ctx.fill();
	}

	// ── MATRIX MULTIPLY VIZ ──
	let matCanvas: HTMLCanvasElement;
	let matPreset = 'translate';
	let matFormula = 'Hover an output value to see the dot-product calculation.';
	const matPresets: Record<string, { M: number[][]; v: number[]; label: string }> = {
		translate: {
			M: [
				[1, 0, 80],
				[0, 1, 40],
				[0, 0, 1]
			],
			v: [30, 20, 1],
			label: 'Translation (+80,+40)'
		},
		rotate: {
			M: [
				[0.707, -0.707, 0],
				[0.707, 0.707, 0],
				[0, 0, 1]
			],
			v: [60, 0, 1],
			label: 'Rotation 45°'
		},
		scale: {
			M: [
				[2, 0, 0],
				[0, 2, 0],
				[0, 0, 1]
			],
			v: [30, 20, 1],
			label: 'Scale 2×'
		},
		combined: {
			M: matMul(
				matMul(
					[
						[1, 0, 50],
						[0, 1, 30],
						[0, 0, 1]
					],
					[
						[0.707, -0.707, 0],
						[0.707, 0.707, 0],
						[0, 0, 1]
					]
				),
				[
					[1.5, 0, 0],
					[0, 1.5, 0],
					[0, 0, 1]
				]
			),
			v: [30, 20, 1],
			label: 'T × R × S combined'
		}
	};

	function drawMatCanvas(highlightRow = -1) {
		if (!matCanvas) return;
		const ctx = matCanvas.getContext('2d')!;
		const W = matCanvas.width,
			H = matCanvas.height;
		ctx.clearRect(0, 0, W, H);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, W, H);
		const { M, v } = matPresets[matPreset];
		const result = matVec(M, v);
		const cellW = 70,
			cellH = 52,
			matX = 80,
			vecX = matX + 3 * cellW + 80,
			resX = vecX + cellW + 120,
			startY = 40;
		ctx.font = 'bold 13px IBM Plex Mono';
		M.forEach((row, ri) =>
			row.forEach((val, ci) => {
				const x = matX + ci * cellW,
					y = startY + ri * cellH,
					hi = highlightRow === ri;
				ctx.fillStyle = hi ? '#a78bfa20' : '#0d1215';
				ctx.fillRect(x, y, cellW - 3, cellH - 3);
				ctx.strokeStyle = hi ? '#a78bfa' : '#1a2228';
				ctx.lineWidth = 1;
				ctx.strokeRect(x, y, cellW - 3, cellH - 3);
				ctx.fillStyle = hi ? '#a78bfa' : '#cdd8e0';
				ctx.textAlign = 'right';
				ctx.fillText(val.toFixed(2), x + cellW - 10, y + cellH / 2 + 5);
			})
		);
		v.forEach((val, ri) => {
			const x = vecX,
				y = startY + ri * cellH,
				hi = highlightRow >= 0;
			ctx.fillStyle = hi ? '#34d39920' : '#0d1215';
			ctx.fillRect(x, y, cellW - 3, cellH - 3);
			ctx.strokeStyle = hi ? '#34d399' : '#1a2228';
			ctx.lineWidth = 1;
			ctx.strokeRect(x, y, cellW - 3, cellH - 3);
			ctx.fillStyle = hi ? '#34d399' : '#cdd8e0';
			ctx.font = 'bold 13px IBM Plex Mono';
			ctx.textAlign = 'right';
			ctx.fillText(val.toFixed(2), x + cellW - 10, y + cellH / 2 + 5);
		});
		ctx.font = '20px IBM Plex Mono';
		ctx.fillStyle = '#4a606c';
		ctx.textAlign = 'center';
		ctx.fillText('×', matX + 3 * cellW + 30, startY + cellH * 1.5 + 5);
		ctx.fillText('=', vecX + cellW + 30, startY + cellH * 1.5 + 5);
		result.forEach((val, ri) => {
			const x = resX,
				y = startY + ri * cellH,
				hi = highlightRow === ri;
			ctx.fillStyle = hi ? '#fb923c20' : '#0d1215';
			ctx.fillRect(x, y, cellW - 3, cellH - 3);
			ctx.strokeStyle = hi ? '#fb923c' : '#1a2228';
			ctx.lineWidth = 1;
			ctx.strokeRect(x, y, cellW - 3, cellH - 3);
			ctx.fillStyle = hi ? '#fb923c' : '#6b7280';
			ctx.font = 'bold 13px IBM Plex Mono';
			ctx.textAlign = 'right';
			ctx.fillText(val.toFixed(2), x + cellW - 10, y + cellH / 2 + 5);
		});
		ctx.font = '11px IBM Plex Mono';
		ctx.fillStyle = '#4a606c';
		ctx.textAlign = 'right';
		["x'", "y'", "w'"].forEach((lbl, ri) =>
			ctx.fillText(lbl, resX - 18, startY + ri * cellH + cellH / 2 + 5)
		);
		if (highlightRow >= 0) {
			const row = M[highlightRow];
			const terms = row.map((c, ci) => `${c.toFixed(2)}×${v[ci].toFixed(2)}`).join(' + ');
			matFormula = `Row ${highlightRow}: ${terms} = ${result[highlightRow].toFixed(2)}`;
		} else {
			matFormula = 'Hover an output value to see the dot-product calculation.';
		}
	}

	function onMatMove(e: MouseEvent) {
		const rect = matCanvas.getBoundingClientRect();
		const scaleY = matCanvas.height / rect.height;
		const my = (e.clientY - rect.top) * scaleY;
		const cellH = 52,
			startY = 40,
			row = Math.floor((my - startY) / cellH);
		drawMatCanvas(row >= 0 && row < 3 ? row : -1);
	}

	// ── HIERARCHY ──
	let hierCanvas: HTMLCanvasElement;
	let h_rootRot = 0,
		h_rootTx = 0,
		h_armRot = 30,
		h_handRot = -20;
	let hi_root = '0°',
		hi_arm = '30°',
		hi_hand = '10°';

	function drawHier() {
		if (!hierCanvas) return;
		const ctx = hierCanvas.getContext('2d')!;
		const W = hierCanvas.width,
			H = hierCanvas.height;
		const cx = W / 2 + h_rootTx,
			cy = H / 2 + 40;
		ctx.clearRect(0, 0, W, H);
		ctx.fillStyle = '#08080f';
		ctx.fillRect(0, 0, W, H);
		const grid = 40;
		ctx.strokeStyle = '#111922';
		ctx.lineWidth = 1;
		for (let x = 0; x < W; x += grid) {
			ctx.beginPath();
			ctx.moveTo(x, 0);
			ctx.lineTo(x, H);
			ctx.stroke();
		}
		for (let y = 0; y < H; y += grid) {
			ctx.beginPath();
			ctx.moveTo(0, y);
			ctx.lineTo(W, y);
			ctx.stroke();
		}
		const rootM = matMul(transMat(cx, cy), rotMat(-h_rootRot));
		drawShapeCtx(ctx, applyMat(rootM, HOUSE_PTS), '#34d39920', '#34d399', 2);
		drawAxes(ctx, rootM, 35, 'root');
		hi_root = h_rootRot + '°';
		const armOffset = matMul(rootM, transMat(0, -50));
		const armM = matMul(armOffset, rotMat(-h_armRot));
		drawShapeCtx(
			ctx,
			applyMat(armM, [
				[-8, 0],
				[8, 0],
				[8, -60],
				[-8, -60]
			]),
			'#a78bfa20',
			'#a78bfa',
			2
		);
		drawAxes(ctx, armM, 28, 'arm');
		hi_arm = h_rootRot + h_armRot + '°';
		const handM = matMul(matMul(armM, transMat(0, -60)), rotMat(-h_handRot));
		drawShapeCtx(ctx, applyMat(handM, DIAMOND_PTS), '#fb923c20', '#fb923c', 2);
		drawAxes(ctx, handM, 22, 'hand');
		hi_hand = h_rootRot + h_armRot + h_handRot + '°';
	}

	// ── QUIZ ──
	const quizData = [
		{
			q: 'A model matrix rotates then translates (M = T × R). In which order are transforms applied to a vertex?',
			options: [
				'Translate first, then rotate',
				'Rotate first, then translate',
				'Both simultaneously',
				'The order depends on the vertex'
			],
			correct: 1,
			explanation:
				"Matrix multiplication is applied right-to-left: v' = T × R × v means R is applied first (closest to v), then T."
		},
		{
			q: 'What goes wrong if you apply transforms in the order Scale × Translate × Rotate instead of Translate × Rotate × Scale?',
			options: [
				'The object disappears',
				'The translation distance gets scaled, placing the object at the wrong position',
				'The rotation axis is incorrect',
				'Scale has no effect'
			],
			correct: 1,
			explanation:
				'If you scale before translating, the translation values are also scaled. A translate of 100 units after a 2× scale becomes 200 units in world space.'
		},
		{
			q: 'Why do 2D transforms use 3×3 matrices rather than 2×2?',
			options: [
				'For efficiency reasons',
				'So rotation can be represented',
				'To include translation as a matrix multiplication via homogeneous coordinates',
				'Because GPUs require 3×3 matrices'
			],
			correct: 2,
			explanation:
				"A 2×2 matrix can represent rotation and scale but not translation. Adding a homogeneous w component allows translation to be expressed as a matrix multiplication: [x', y', 1] = M × [x, y, 1]."
		},
		{
			q: "A child object's local rotation is 30°. Its parent's world rotation is 45°. What is the child's world rotation?",
			options: ['30°', '45°', '75°', '15°'],
			correct: 2,
			explanation:
				'World transforms accumulate through the hierarchy: world_child = parent_world × child_local. Rotations add: 45° + 30° = 75°.'
		},
		{
			q: 'In screen space (pixel coordinates), which direction does positive y point?',
			options: [
				'Up (away from viewer)',
				'Down (increasing row number)',
				'Toward the viewer',
				'It depends on the API'
			],
			correct: 1,
			explanation:
				'Screen space has (0,0) at the top-left, with y increasing downward as row numbers increase. This is the opposite of standard math convention where y points up.'
		}
	];
	let quizAnswers: (number | null)[] = quizData.map(() => null);
	let quizDone = false;
	let quizScore = 0;

	function answerQuiz(qi: number, oi: number) {
		if (quizAnswers[qi] !== null) return;
		quizAnswers[qi] = oi;
		quizAnswers = [...quizAnswers];
		if (quizAnswers.every((a) => a !== null)) {
			quizDone = true;
			quizScore = quizData.filter((q, i) => quizAnswers[i] === q.correct).length;
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
		drawSpaces();
		drawTransform();
		drawMatCanvas();
		drawHier();
		return () => window.removeEventListener('scroll', onScroll);
	});
</script>

<!-- ── HERO ── -->
<div class="module-hero">
	<div class="module-number" aria-hidden="true">03</div>
	<div class="module-tag" style="color:var(--accent3);border-color:var(--accent3);">
		Module 03 · Theory + Practice
	</div>
	<h1 class="module-title" style="--hi:var(--accent3)">
		Coordinate Systems<br /><span>and Transformations</span>
	</h1>
	<div class="progress-bar-wrap">
		<div
			class="progress-bar-fill"
			style="width:{readingProgress}%;background:var(--accent3);"
		></div>
	</div>
</div>

<!-- ── TOC ── -->
<nav class="toc" style="border-color:var(--accent3);">
	<div class="toc-label" style="color:var(--accent3);">Contents</div>
	<ul class="toc-list">
		<li><a href="#objectives">Objectives</a></li>
		<li><a href="#coords">Coordinate Spaces</a></li>
		<li><a href="#affine">Affine Transformations</a></li>
		<li><a href="#matrices">Matrix Math</a></li>
		<li><a href="#combining">Combining Transforms</a></li>
		<li><a href="#hierarchy">Hierarchical Transforms</a></li>
		<li><a href="#practical">Practical Work</a></li>
		<li><a href="#quiz">Quiz</a></li>
	</ul>
</nav>

<!-- ── OBJECTIVES ── -->
<section id="objectives" class="objectives" style="border-left-color:var(--accent3);">
	<div class="objectives-label" style="color:var(--accent3);">Learning Objectives</div>
	<ul>
		<li>Use matrices to perform translation, rotation, and scaling</li>
		<li>Understand local, world, and screen coordinate spaces</li>
		<li>Combine transforms correctly through matrix multiplication</li>
		<li>Implement hierarchical transforms for scene organization</li>
	</ul>
</section>

<!-- ── 03.01 COORDINATE SPACES ── -->
<section id="coords" class="section">
	<div class="section-header">
		<span class="section-num" style="color:var(--accent3);">03.01</span>
		<h2 class="section-title">Coordinate Spaces</h2>
	</div>
	<p>
		Every position in a game scene is expressed relative to some <em>frame of reference</em>. That
		frame is called a coordinate space. There is no single "correct" space — positions only have
		meaning when you know which space they are measured in.
	</p>
	<table>
		<thead><tr><th>Space</th><th>Origin</th><th>Axes</th><th>Used for</th></tr></thead>
		<tbody>
			<tr
				><td><strong style="color:var(--accent2)">Local / Object</strong></td><td>Object center</td
				><td>Aligned to object</td><td>Vertex positions in mesh data</td></tr
			>
			<tr
				><td><strong style="color:var(--accent)">World</strong></td><td>Scene origin</td><td
					>Fixed, global</td
				><td>Object placement in scene</td></tr
			>
			<tr
				><td><strong style="color:var(--accent3)">Screen / NDC</strong></td><td
					>Center or top-left</td
				><td>Pixel or [-1,1]</td><td>Final rasterization</td></tr
			>
		</tbody>
	</table>
	<!-- SPACES DEMO -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Three Coordinate Spaces</span><span class="demo-badge interactive"
				>INTERACTIVE</span
			>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Click each space to see where the same shape lives relative to different origins.
			</p>
			<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
				{#each [['local', 'Local Space'], ['world', 'World Space'], ['screen', 'Screen Space']] as [mode, label]}
					<button
						class="btn purple"
						class:active={spaceMode === mode}
						on:click={() => setSpaceMode(mode)}>{label}</button
					>
				{/each}
			</div>
			<canvas
				bind:this={spacesCanvas}
				width="860"
				height="320"
				style="width:100%;border:1px solid var(--border2);display:block;"
			></canvas>
			<div style="font-size:12px;color:var(--muted);margin-top:0.75rem;">{spacesDesc}</div>
		</div>
	</div>
	<div class="callout info">
		<div class="callout-label">Practical Rule</div>
		If a number feels wrong — a position that should be (0,0) appearing somewhere else, or a rotation
		that seems off-center — the first question to ask is:<em>which coordinate space am I in?</em> Most
		transform bugs are space confusion.
	</div>
</section>

<!-- ── 03.02 AFFINE TRANSFORMS ── -->
<section id="affine" class="section">
	<div class="section-header">
		<span class="section-num" style="color:var(--accent3);">03.02</span>
		<h2 class="section-title">Affine Transformations</h2>
	</div>
	<p>
		An <strong>affine transformation</strong> is any transformation that preserves straight lines and
		the ratio of distances along those lines. The three fundamental affine transforms are translation,
		rotation, and scale. Parallel lines remain parallel after the transform.
	</p>
	<p>
		In 2D, the <em>homogeneous coordinate</em> trick adds a third component (w = 1) so that all three
		operations — including translation — can be expressed as matrix multiplication.
	</p>
	<pre><code
			><span class="cm"># Translation by (tx, ty)</span>
T = [[<span class="num">1</span>, <span class="num">0</span>, tx],
     [<span class="num">0</span>, <span class="num">1</span>, ty],
     [<span class="num">0</span>, <span class="num">0</span>,  <span class="num">1</span>]]

<span class="cm"># Rotation by angle θ (counter-clockwise)</span>
R = [[<span class="fn">cos</span>(θ), -<span class="fn">sin</span>(θ), <span class="num">0</span>],
     [<span class="fn">sin</span>(θ),  <span class="fn">cos</span>(θ), <span class="num">0</span>],
     [      <span class="num">0</span>,        <span class="num">0</span>, <span class="num">1</span
			>]]

<span class="cm"># Scale by (sx, sy)</span>
S = [[sx,  <span class="num">0</span>, <span class="num">0</span>],
     [ <span class="num">0</span>, sy, <span class="num">0</span>],
     [ <span class="num">0</span>,  <span class="num">0</span>, <span class="num">1</span>]]<span
				class="lang-tag">python</span
			></code
		></pre>
	<!-- TRANSFORM PLAYGROUND -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Transform Playground</span><span class="demo-badge interactive"
				>INTERACTIVE</span
			>
		</div>
		<div class="demo-body">
			<div class="two-col" style="align-items:start;">
				<div>
					<canvas
						bind:this={tfCanvas}
						width="380"
						height="360"
						style="width:100%;border:1px solid var(--border2);display:block;"
					></canvas>
				</div>
				<div>
					<div style="margin-bottom:1.25rem;">
						<div
							style="font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent2);margin-bottom:.5rem;"
						>
							Translation
						</div>
						<div class="slider-row">
							<label>tx</label><input
								type="range"
								min="-150"
								max="150"
								bind:value={tx}
								on:input={drawTransform}
							/><span class="slider-val">{tx}</span>
						</div>
						<div class="slider-row">
							<label>ty</label><input
								type="range"
								min="-150"
								max="150"
								bind:value={ty}
								on:input={drawTransform}
							/><span class="slider-val">{ty}</span>
						</div>
					</div>
					<div style="margin-bottom:1.25rem;">
						<div
							style="font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);margin-bottom:.5rem;"
						>
							Rotation
						</div>
						<div class="slider-row">
							<label>θ (deg)</label><input
								type="range"
								min="-180"
								max="180"
								bind:value={rot}
								on:input={drawTransform}
							/><span class="slider-val">{rot}°</span>
						</div>
					</div>
					<div style="margin-bottom:1.25rem;">
						<div
							style="font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent3);margin-bottom:.5rem;"
						>
							Scale
						</div>
						<div class="slider-row">
							<label>sx</label><input
								type="range"
								min="10"
								max="300"
								bind:value={sx}
								on:input={drawTransform}
							/><span class="slider-val">{(sx / 100).toFixed(2)}</span>
						</div>
						<div class="slider-row">
							<label>sy</label><input
								type="range"
								min="10"
								max="300"
								bind:value={sy}
								on:input={drawTransform}
							/><span class="slider-val">{(sy / 100).toFixed(2)}</span>
						</div>
					</div>
					<button
						class="btn"
						style="width:100%;margin-bottom:1rem;"
						on:click={() => {
							tx = 0;
							ty = 0;
							rot = 0;
							sx = 100;
							sy = 100;
							drawTransform();
						}}>↺ Reset</button
					>
					<div class="mat-label">Combined Matrix M = T × R × S</div>
					<div style="display:flex;justify-content:center;margin-top:.5rem;">
						<div class="mat-display">
							{#each matCells as val, i}
								<div
									class="mat-cell"
									class:hi={val !== '0' && val !== '1' && !(i === 0 || i === 4 || i === 8)}
								>
									{val}
								</div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- ── 03.03 MATRIX MULTIPLY ── -->
<section id="matrices" class="section">
	<div class="section-header">
		<span class="section-num" style="color:var(--accent3);">03.03</span>
		<h2 class="section-title">Matrix Multiplication</h2>
	</div>
	<p>
		Applying a transform to a point means multiplying a 3×3 matrix by a 3×1 column vector. Each
		output component is the <em>dot product</em> of a row of the matrix with the input vector.
	</p>
	<pre><code
			><span class="kw">def</span> <span class="fn">mat_vec</span>(M, p):
    x = M[<span class="num">0</span>][<span class="num">0</span>]*p[<span class="num">0</span
			>] + M[<span class="num">0</span>][<span class="num">1</span>]*p[<span class="num">1</span
			>] + M[<span class="num">0</span>][<span class="num">2</span>]*p[<span class="num">2</span>]
    y = M[<span class="num">1</span>][<span class="num">0</span>]*p[<span class="num">0</span
			>] + M[<span class="num">1</span>][<span class="num">1</span>]*p[<span class="num">1</span
			>] + M[<span class="num">1</span>][<span class="num">2</span>]*p[<span class="num">2</span>]
    w = M[<span class="num">2</span>][<span class="num">0</span>]*p[<span class="num">0</span
			>] + M[<span class="num">2</span>][<span class="num">1</span>]*p[<span class="num">1</span
			>] + M[<span class="num">2</span>][<span class="num">2</span>]*p[<span class="num">2</span>]
    <span class="kw">return</span> [x, y, w]

<span class="cm"># In practice, use numpy:</span>
result = M @ np.<span class="fn">array</span>([x, y, <span class="num">1.0</span>])<span
				class="lang-tag">python</span
			></code
		></pre>
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Matrix × Vector Step-by-Step</span><span class="demo-badge interactive"
				>INTERACTIVE</span
			>
		</div>
		<div class="demo-body">
			<div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem;">
				{#each [['translate', 'Translation (+80,+40)'], ['rotate', 'Rotation 45°'], ['scale', 'Scale 2×'], ['combined', 'T × R × S']] as [p, label]}
					<button
						class="btn purple"
						class:active={matPreset === p}
						on:click={() => {
							matPreset = p;
							drawMatCanvas();
						}}>{label}</button
					>
				{/each}
			</div>
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Hover over an output value to see which row and column contribute to it.
			</p>
			<canvas
				bind:this={matCanvas}
				width="860"
				height="280"
				style="width:100%;border:1px solid var(--border2);display:block;"
				on:mousemove={onMatMove}
				on:mouseleave={() => drawMatCanvas()}
			></canvas>
			<div style="font-size:12px;color:var(--muted);margin-top:.75rem;text-align:center;">
				{matFormula}
			</div>
		</div>
	</div>
</section>

<!-- ── 03.04 COMBINING ── -->
<section id="combining" class="section">
	<div class="section-header">
		<span class="section-num" style="color:var(--accent3);">03.04</span>
		<h2 class="section-title">Combining Transforms and Order</h2>
	</div>
	<p>
		Multiple transforms can be <em>combined</em> into a single matrix by multiplication. The order matters
		— matrix multiplication is not commutative. The standard convention for game objects:
	</p>
	<pre><code
			><span class="cm"># Standard object matrix: TRS = Translate × Rotate × Scale</span>
<span class="cm"># Applied right-to-left: Scale first, then Rotate, then Translate</span>
M = T @ R @ S

<span class="cm"># Apply to a vertex in homogeneous coordinates</span>
vertex_world = M @ np.array([vx, vy, <span class="num">1.0</span>])<span class="lang-tag"
				>python</span
			></code
		></pre>
	<div class="callout warn">
		<div class="callout-label">Order Matters</div>
		T × R × S ≠ S × R × T. In the first, Scale is applied first (close to the vertex). In the second,
		Translate is applied first. The resulting positions are different. Always apply Scale → Rotate → Translate
		(right-to-left in the multiplication).
	</div>
</section>

<!-- ── 03.05 HIERARCHY ── -->
<section id="hierarchy" class="section">
	<div class="section-header">
		<span class="section-num" style="color:var(--accent3);">03.05</span>
		<h2 class="section-title">Hierarchical Transforms</h2>
	</div>
	<p>
		Game scenes are organized as trees. Each node has a local transform relative to its parent. The
		world transform is computed by multiplying all parent transforms together. This means: if the
		parent moves, all children move with it automatically.
	</p>
	<pre><code
			><span class="cm"># World transform = parent_world × child_local</span>
body_world = T_body
arm_world  = body_world @ T_arm_local
hand_world = arm_world  @ T_hand_local<span class="lang-tag">python</span></code
		></pre>
	<!-- HIERARCHY DEMO -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Scene Hierarchy (3 Levels)</span><span class="demo-badge interactive"
				>INTERACTIVE</span
			>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Move the root body and observe how children accumulate transformations.
			</p>
			<div class="two-col" style="align-items:start;">
				<div>
					<canvas
						bind:this={hierCanvas}
						width="500"
						height="320"
						style="width:100%;border:1px solid var(--border2);display:block;"
						on:input={drawHier}
					></canvas>
				</div>
				<div>
					<div style="margin-bottom:1rem;">
						<div
							style="font-size:10px;color:#34d399;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.5rem;"
						>
							Root Body
						</div>
						<div class="slider-row">
							<label>tx</label><input
								type="range"
								min="-150"
								max="150"
								bind:value={h_rootTx}
								on:input={drawHier}
							/><span class="slider-val">{h_rootTx}</span>
						</div>
						<div class="slider-row">
							<label>rot</label><input
								type="range"
								min="-180"
								max="180"
								bind:value={h_rootRot}
								on:input={drawHier}
							/><span class="slider-val">{h_rootRot}°</span>
						</div>
					</div>
					<div style="margin-bottom:1rem;">
						<div
							style="font-size:10px;color:var(--accent3);letter-spacing:.15em;text-transform:uppercase;margin-bottom:.5rem;"
						>
							Arm (child of root)
						</div>
						<div class="slider-row">
							<label>rot</label><input
								type="range"
								min="-180"
								max="180"
								bind:value={h_armRot}
								on:input={drawHier}
							/><span class="slider-val">{h_armRot}°</span>
						</div>
					</div>
					<div style="margin-bottom:1rem;">
						<div
							style="font-size:10px;color:#fb923c;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.5rem;"
						>
							Hand (child of arm)
						</div>
						<div class="slider-row">
							<label>rot</label><input
								type="range"
								min="-180"
								max="180"
								bind:value={h_handRot}
								on:input={drawHier}
							/><span class="slider-val">{h_handRot}°</span>
						</div>
					</div>
					<div class="stats-panel" style="margin-top:1rem;">
						<div class="stat-row">
							<span class="stat-label" style="color:#34d399;">Root world rot</span><span
								class="stat-val">{hi_root}</span
							>
						</div>
						<div class="stat-row">
							<span class="stat-label" style="color:var(--accent3);">Arm world rot</span><span
								class="stat-val">{hi_arm}</span
							>
						</div>
						<div class="stat-row">
							<span class="stat-label" style="color:#fb923c;">Hand world rot</span><span
								class="stat-val">{hi_hand}</span
							>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>

<hr class="divider" />

<!-- ── QUIZ ── -->
<section id="quiz" class="quiz-section">
	<div class="quiz-header" style="border-left-color:var(--accent3);">Module Quiz</div>
	<div class="quiz-sub">5 questions · Coordinate systems and matrix transforms</div>
	{#each quizData as q, qi}
		<div class="question">
			<div class="q-text">
				<span class="q-num" style="color:var(--accent3)">{qi + 1}.</span>{q.q}
			</div>
			<div class="options">
				{#each q.options as opt, oi}
					<div
						class="option"
						class:correct={quizAnswers[qi] !== null && oi === q.correct}
						class:wrong={quizAnswers[qi] === oi && oi !== q.correct}
						class:disabled={quizAnswers[qi] !== null}
						on:click={() => answerQuiz(qi, oi)}
						role="button"
						tabindex="0"
						on:keydown={(e) => e.key === 'Enter' && answerQuiz(qi, oi)}
					>
						{opt}
					</div>
				{/each}
			</div>
			{#if quizAnswers[qi] !== null}
				<div
					class="feedback"
					class:ok={quizAnswers[qi] === q.correct}
					class:bad={quizAnswers[qi] !== q.correct}
				>
					{quizAnswers[qi] === q.correct ? '✓ Correct.' : '✗'}
					{q.explanation}
				</div>
			{/if}
		</div>
	{/each}
	{#if quizDone}
		<div
			class="quiz-score"
			style="border-color:{quizScore === 5
				? 'var(--accent3)'
				: quizScore >= 3
					? 'var(--accent)'
					: 'var(--accent2)'}"
		>
			<div class="score-num" style="color:var(--accent3);">{quizScore}/{quizData.length}</div>
			<div class="score-label">Module 03 complete. Proceed to Module 04 when ready.</div>
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
	.module-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(28px, 5vw, 48px);
		font-weight: 800;
		line-height: 1.1;
		color: #fff;
		max-width: 600px;
	}
	.module-title span {
		color: var(--accent3);
	}
</style>
