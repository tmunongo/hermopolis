<script lang="ts">
	import { onMount } from 'svelte';

	let readingProgress = 0;

	// ── PIXEL GRID ──
	let pgCanvas: HTMLCanvasElement;
	let pgZoom = 1;
	let pgType = 'gradient';
	const IMG_W = 64,
		IMG_H = 64;
	let pgData = new Uint8ClampedArray(IMG_W * IMG_H * 4);
	let pxCoords = 'Position: —';
	let pxRgb = 'RGB: —';
	let pxHex = 'Hex: —';
	let pxChannelsHtml = '';

	// ── COLOR MIXER ──
	let R = 80,
		G = 180,
		B = 220,
		A = 255;
	$: hexOut = `#${toHex(R)}${toHex(G)}${toHex(B)}${toHex(A)}`;
	$: rgbOut = `rgb(${R}, ${G}, ${B})`;
	$: rgbaOut = `rgba(${R}, ${G}, ${B}, ${(A / 255).toFixed(2)})`;
	$: normOut = `vec4(${(R / 255).toFixed(2)}, ${(G / 255).toFixed(2)}, ${(B / 255).toFixed(2)}, ${(A / 255).toFixed(2)})`;
	$: bytesOut = `${toHex(R)} ${toHex(G)} ${toHex(B)} ${toHex(A)}`;
	$: swatchColor = `rgba(${R},${G},${B},${A / 255})`;
	$: rStrip = `linear-gradient(to right, #1a0000, rgb(${R},0,0))`;
	$: gStrip = `linear-gradient(to right, #001a00, rgb(0,${G},0))`;
	$: bStrip = `linear-gradient(to right, #00001a, rgb(0,0,${B}))`;

	// ── MEMORY LAYOUT ──
	let memCanvas: HTMLCanvasElement;
	let memFormula = 'Hover a pixel to see its byte offset.';
	const MEM_W = 4,
		MEM_H = 4;
	let memColors: number[][] = [];
	let memCells: {
		pixel: number;
		channel: number;
		label: string;
		color: string;
		value: string;
		highlighted: boolean;
	}[] = [];

	// ── RASTER VS VECTOR ──
	let rasterCanvas: HTMLCanvasElement;
	let vectorCanvas: HTMLCanvasElement;
	let rvZoom = 1;
	const rasterPixels = new Uint8ClampedArray(64 * 40 * 4);

	// ── GRADIENT ──
	let gradCanvas: HTMLCanvasElement;
	let gradType = 0;
	let gradCodeHtml = '';
	const gradLabels = ['Horizontal', 'Vertical', '2D (RG)', 'Radial', 'Angular'];
	const gradCodes = [
		`img[:, :, 0] = xs  # red increases left → right\nimg[:, :, 1] = 0\nimg[:, :, 2] = 0`,
		`img[:, :, 0] = 0\nimg[:, :, 1] = ys  # green increases top → bottom\nimg[:, :, 2] = 128`,
		`img[:, :, 0] = xs  # red = x\nimg[:, :, 1] = ys  # green = y\nimg[:, :, 2] = 128`,
		`# radial gradient\nd = np.sqrt((xs - W/2)**2 + (ys - H/2)**2)\nt = np.clip(1 - d / (W/2), 0, 1)\nimg = (t[:,:,None] * [0, 229, 200]).astype(np.uint8)`,
		`# angular gradient\nangle = np.arctan2(ys - H/2, xs - W/2)\nt = (angle + np.pi) / (2 * np.pi)\nimg[:,:,0] = (t * 255).astype(np.uint8)\nimg[:,:,2] = ((1-t) * 200).astype(np.uint8)`
	];

	// ── SHAPE ──
	let shapeCanvas: HTMLCanvasElement;
	let shapeType = 'circle';
	let shapeCodeHtml = '';
	const shapeCodes: Record<string, string> = {
		circle: `dist_sq = (xs - cx)**2 + (ys - cy)**2\nimg[dist_sq <= r**2] = [0, 229, 200]`,
		ring: `dist_sq = (xs - cx)**2 + (ys - cy)**2\nring = (dist_sq >= (r-3)**2) & (dist_sq <= r**2)\nimg[ring] = [255, 95, 58]`,
		rect: `mask = (xs >= x0) & (xs < x1) & (ys >= y0) & (ys < y1)\nimg[mask] = [0, 229, 200]`,
		stripe: `stripe = (xs // 20) % 2 == 0\nimg[stripe] = [0, 229, 200]`,
		checker: `checker = ((xs // 20) + (ys // 20)) % 2 == 0\nimg[checker] = [0, 229, 200]`
	};

	// ── QUIZ ──
	const quizData = [
		{
			q: 'An RGBA image is 100 pixels wide and 80 pixels tall. How many bytes does it occupy in memory?',
			options: ['800 bytes', '8,000 bytes', '24,000 bytes', '32,000 bytes'],
			correct: 3,
			explanation:
				'100 × 80 × 4 bytes (RGBA) = 32,000 bytes. Each pixel stores one byte per channel.'
		},
		{
			q: 'What color does RGB(255, 255, 255) represent?',
			options: ['Black', 'White', 'Gray (50%)', 'Transparent'],
			correct: 1,
			explanation:
				'All channels at maximum intensity produce white. RGB is an additive model — maximum of all three primaries gives white.'
		},
		{
			q: 'You want pixel (x=5, y=3) in a 10-pixel-wide RGBA image. What is its byte offset?',
			options: ['Offset 120', 'Offset 35', 'Offset 140', 'Offset 20'],
			correct: 2,
			explanation: '(y × W + x) × 4 = (3 × 10 + 5) × 4 = 35 × 4 = 140.'
		},
		{
			q: 'Which of these is NOT an advantage of vector graphics over raster?',
			options: [
				'Scales without quality loss',
				'Can represent photographic detail',
				'Resolution-independent',
				'Smaller file size for simple shapes'
			],
			correct: 1,
			explanation:
				'Vectors are defined by mathematical shapes and cannot represent the arbitrary per-pixel color data found in photographs.'
		},
		{
			q: 'What is the purpose of double buffering in a game engine?',
			options: [
				'To store twice as many textures',
				'To prevent the screen showing partial frames mid-render',
				'To double the rendering speed',
				'To support two monitors simultaneously'
			],
			correct: 1,
			explanation:
				'Double buffering keeps the front buffer (displayed) separate from the back buffer (in progress). After rendering, buffers swap — users never see an incomplete frame.'
		}
	];
	let quizAnswers: (number | null)[] = quizData.map(() => null);
	let quizDone = false;
	let quizScore = 0;

	function toHex(v: number) {
		return Math.round(v).toString(16).padStart(2, '0').toUpperCase();
	}

	function buildPGImage() {
		for (let y = 0; y < IMG_H; y++) {
			for (let x = 0; x < IMG_W; x++) {
				const i = (y * IMG_W + x) * 4;
				if (pgType === 'gradient') {
					pgData[i] = Math.round((x / (IMG_W - 1)) * 255);
					pgData[i + 1] = Math.round((y / (IMG_H - 1)) * 255);
					pgData[i + 2] = 128;
					pgData[i + 3] = 255;
				} else if (pgType === 'circle') {
					const cx = IMG_W / 2,
						cy = IMG_H / 2,
						r = IMG_W * 0.38;
					const d = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
					if (d < r) {
						pgData[i] = Math.round(255 * (1 - d / r));
						pgData[i + 1] = Math.round(229 * (d / r));
						pgData[i + 2] = 200;
						pgData[i + 3] = 255;
					} else {
						pgData[i] = 20;
						pgData[i + 1] = 20;
						pgData[i + 2] = 30;
						pgData[i + 3] = 255;
					}
				} else if (pgType === 'checkerboard') {
					const c = (Math.floor(x / 4) + Math.floor(y / 4)) % 2 === 0 ? 220 : 40;
					pgData[i] = c;
					pgData[i + 1] = c;
					pgData[i + 2] = c;
					pgData[i + 3] = 255;
				} else if (pgType === 'noise') {
					pgData[i] = Math.round(Math.random() * 100 + 80);
					pgData[i + 1] = Math.round(Math.random() * 100 + 80);
					pgData[i + 2] = Math.round(Math.random() * 100 + 80);
					pgData[i + 3] = 255;
				}
			}
		}
	}

	function drawPGCanvas() {
		if (!pgCanvas) return;
		const ctx = pgCanvas.getContext('2d')!;
		ctx.clearRect(0, 0, pgCanvas.width, pgCanvas.height);
		const scale = pgZoom;
		const visW = Math.ceil(pgCanvas.width / scale);
		const visH = Math.ceil(pgCanvas.height / scale);
		const offX = Math.max(0, Math.floor((IMG_W - visW) / 2));
		const offY = Math.max(0, Math.floor((IMG_H - visH) / 2));
		for (let y = 0; y < visH && y + offY < IMG_H; y++) {
			for (let x = 0; x < visW && x + offX < IMG_W; x++) {
				const pi = ((y + offY) * IMG_W + (x + offX)) * 4;
				ctx.fillStyle = `rgb(${pgData[pi]},${pgData[pi + 1]},${pgData[pi + 2]})`;
				ctx.fillRect(x * scale, y * scale, scale, scale);
			}
		}
		if (scale >= 8) {
			ctx.strokeStyle = 'rgba(255,255,255,0.08)';
			ctx.lineWidth = 0.5;
			for (let x = 0; x < pgCanvas.width; x += scale) {
				ctx.beginPath();
				ctx.moveTo(x, 0);
				ctx.lineTo(x, pgCanvas.height);
				ctx.stroke();
			}
			for (let y = 0; y < pgCanvas.height; y += scale) {
				ctx.beginPath();
				ctx.moveTo(0, y);
				ctx.lineTo(pgCanvas.width, y);
				ctx.stroke();
			}
		}
	}

	function onPGMove(e: MouseEvent) {
		const rect = pgCanvas.getBoundingClientRect();
		const cx = Math.floor(((e.clientX - rect.left) / rect.width) * pgCanvas.width);
		const cy = Math.floor(((e.clientY - rect.top) / rect.height) * pgCanvas.height);
		const scale = pgZoom;
		const visW = Math.ceil(pgCanvas.width / scale);
		const visH = Math.ceil(pgCanvas.height / scale);
		const offX = Math.max(0, Math.floor((IMG_W - visW) / 2));
		const offY = Math.max(0, Math.floor((IMG_H - visH) / 2));
		const px = Math.floor(cx / scale) + offX;
		const py = Math.floor(cy / scale) + offY;
		if (px >= 0 && px < IMG_W && py >= 0 && py < IMG_H) {
			const pi = (py * IMG_W + px) * 4;
			const rv = pgData[pi],
				gv = pgData[pi + 1],
				bv = pgData[pi + 2];
			pxCoords = `Position: (${px}, ${py})`;
			pxRgb = `RGB: (${rv}, ${gv}, ${bv})`;
			pxHex =
				`Hex: #${rv.toString(16).padStart(2, '0')}${gv.toString(16).padStart(2, '0')}${bv.toString(16).padStart(2, '0')}`.toUpperCase();
			pxChannelsHtml = `<div style="display:grid;grid-template-columns:30px 1fr 30px;gap:4px;align-items:center;font-size:11px;">
				<span style="color:#ff5f5f">R</span><div style="height:6px;background:linear-gradient(to right,#1a0000,#ff5f5f);border-radius:2px;overflow:hidden;"><div style="width:${(rv / 255) * 100}%;height:100%;background:#ff5f5f;"></div></div><span>${rv}</span>
				<span style="color:#5fff80">G</span><div style="height:6px;background:linear-gradient(to right,#001a00,#5fff80);border-radius:2px;overflow:hidden;"><div style="width:${(gv / 255) * 100}%;height:100%;background:#5fff80;"></div></div><span>${gv}</span>
				<span style="color:#5f9fff">B</span><div style="height:6px;background:linear-gradient(to right,#00001a,#5f9fff);border-radius:2px;overflow:hidden;"><div style="width:${(bv / 255) * 100}%;height:100%;background:#5f9fff;"></div></div><span>${bv}</span>
			</div>`;
		}
	}

	// ── MEMORY LAYOUT ──
	function initMemColors() {
		memColors = Array.from({ length: MEM_W * MEM_H }, () => [
			Math.floor(Math.random() * 200 + 30),
			Math.floor(Math.random() * 200 + 30),
			Math.floor(Math.random() * 200 + 30),
			255
		]);
		buildMemCells(-1);
	}

	function buildMemCells(highlighted: number) {
		const labels = ['R', 'G', 'B', 'A'];
		const labelColors = ['#ff5f5f', '#5fff80', '#5f9fff', '#aaa'];
		memCells = [];
		for (let i = 0; i < MEM_W * MEM_H; i++) {
			for (let c = 0; c < 4; c++) {
				memCells.push({
					pixel: i,
					channel: c,
					label: labels[c],
					color: labelColors[c],
					value: String(memColors[i]?.[c] ?? 0),
					highlighted: i === highlighted
				});
			}
		}
	}

	function drawMemCanvas(highlightPx = -1) {
		if (!memCanvas) return;
		const ctx = memCanvas.getContext('2d')!;
		const cw = memCanvas.width / MEM_W;
		const ch = memCanvas.height / MEM_H;
		for (let y = 0; y < MEM_H; y++) {
			for (let x = 0; x < MEM_W; x++) {
				const pi = y * MEM_W + x;
				const [r, g, b] = memColors[pi] ?? [0, 0, 0];
				ctx.fillStyle = pi === highlightPx ? '#fff' : `rgb(${r},${g},${b})`;
				ctx.fillRect(x * cw, y * ch, cw, ch);
				if (pi === highlightPx) {
					ctx.fillStyle = `rgb(${r},${g},${b})`;
					ctx.fillRect(x * cw + 4, y * ch + 4, cw - 8, ch - 8);
				}
				ctx.strokeStyle = 'rgba(0,0,0,0.5)';
				ctx.lineWidth = 1;
				ctx.strokeRect(x * cw, y * ch, cw, ch);
				ctx.fillStyle = '#fff';
				ctx.font = '10px IBM Plex Mono';
				ctx.textAlign = 'center';
				ctx.fillText(`${x},${y}`, x * cw + cw / 2, y * ch + ch / 2 + 4);
			}
		}
	}

	function onMemMove(e: MouseEvent) {
		const rect = memCanvas.getBoundingClientRect();
		const mx = Math.floor(((e.clientX - rect.left) / rect.width) * MEM_W);
		const my = Math.floor(((e.clientY - rect.top) / rect.height) * MEM_H);
		const px = my * MEM_W + mx;
		if (px >= 0 && px < MEM_W * MEM_H) {
			drawMemCanvas(px);
			buildMemCells(px);
			const x = px % MEM_W,
				y = Math.floor(px / MEM_W);
			const offset = px * 4;
			const [r, g, b, a] = memColors[px] ?? [0, 0, 0, 255];
			memFormula = `Pixel (${x}, ${y}) → offset = (${y} × ${MEM_W} + ${x}) × 4 = <span style="color:var(--accent)">${offset}</span><br>Bytes ${offset}–${offset + 3}: [R=${r}, G=${g}, B=${b}, A=${a}]`;
		}
	}

	// ── RASTER vs VECTOR ──
	function buildRasterSource() {
		const BASE_W = 64,
			BASE_H = 40;
		for (let y = 0; y < BASE_H; y++) {
			for (let x = 0; x < BASE_W; x++) {
				const i = (y * BASE_W + x) * 4;
				const d = Math.sqrt((x - BASE_W / 2) ** 2 + (y - BASE_H / 2) ** 2);
				if (d < 14) {
					rasterPixels[i] = 0;
					rasterPixels[i + 1] = 229;
					rasterPixels[i + 2] = 200;
					rasterPixels[i + 3] = 255;
				} else {
					rasterPixels[i] = 20;
					rasterPixels[i + 1] = 20;
					rasterPixels[i + 2] = 35;
					rasterPixels[i + 3] = 255;
				}
			}
		}
	}

	function drawRasterVector() {
		if (!rasterCanvas || !vectorCanvas) return;
		const BASE_W = 64,
			BASE_H = 40;
		const z = rvZoom;
		const W = rasterCanvas.width,
			H = rasterCanvas.height;
		const rCtx = rasterCanvas.getContext('2d')!;
		const vCtx = vectorCanvas.getContext('2d')!;
		rCtx.clearRect(0, 0, W, H);
		rCtx.fillStyle = '#14141f';
		rCtx.fillRect(0, 0, W, H);
		const visW = Math.ceil(W / z),
			visH = Math.ceil(H / z);
		const ox = Math.max(0, Math.floor((BASE_W - visW) / 2));
		const oy = Math.max(0, Math.floor((BASE_H - visH) / 2));
		for (let ry = 0; ry < visH && ry + oy < BASE_H; ry++) {
			for (let rx = 0; rx < visW && rx + ox < BASE_W; rx++) {
				const pi = ((ry + oy) * BASE_W + (rx + ox)) * 4;
				rCtx.fillStyle = `rgb(${rasterPixels[pi]},${rasterPixels[pi + 1]},${rasterPixels[pi + 2]})`;
				rCtx.fillRect(rx * z, ry * z, z, z);
			}
		}
		if (z >= 4) {
			rCtx.strokeStyle = 'rgba(255,255,255,0.06)';
			rCtx.lineWidth = 0.5;
			for (let x = 0; x < W; x += z) {
				rCtx.beginPath();
				rCtx.moveTo(x, 0);
				rCtx.lineTo(x, H);
				rCtx.stroke();
			}
			for (let y = 0; y < H; y += z) {
				rCtx.beginPath();
				rCtx.moveTo(0, y);
				rCtx.lineTo(W, y);
				rCtx.stroke();
			}
		}
		vCtx.clearRect(0, 0, W, H);
		vCtx.fillStyle = '#14141f';
		vCtx.fillRect(0, 0, W, H);
		vCtx.beginPath();
		vCtx.arc(W / 2, H / 2, 14 * z, 0, Math.PI * 2);
		vCtx.fillStyle = '#00e5c8';
		vCtx.fill();
	}

	function drawGradient() {
		if (!gradCanvas) return;
		const ctx = gradCanvas.getContext('2d')!;
		const W = gradCanvas.width,
			H = gradCanvas.height;
		const imgd = ctx.createImageData(W, H);
		const d = imgd.data;
		for (let y = 0; y < H; y++) {
			for (let x = 0; x < W; x++) {
				const i = (y * W + x) * 4;
				const xn = x / (W - 1),
					yn = y / (H - 1);
				let r = 0,
					g = 0,
					b = 0;
				if (gradType === 0) {
					r = xn * 255;
				} else if (gradType === 1) {
					g = yn * 255;
					b = 128;
				} else if (gradType === 2) {
					r = xn * 255;
					g = yn * 255;
					b = 128;
				} else if (gradType === 3) {
					const dx = xn - 0.5,
						dy = yn - 0.5;
					const t = Math.max(0, 1 - Math.sqrt(dx * dx + dy * dy) * 2);
					g = t * 229;
					b = t * 200;
				} else if (gradType === 4) {
					const angle = Math.atan2(yn - 0.5, xn - 0.5);
					const t = (angle + Math.PI) / (2 * Math.PI);
					r = t * 255;
					b = (1 - t) * 200;
				}
				d[i] = r;
				d[i + 1] = g;
				d[i + 2] = b;
				d[i + 3] = 255;
			}
		}
		ctx.putImageData(imgd, 0, 0);
		gradCodeHtml = `<span class="lang-tag">python</span><span class="cm"># ${gradLabels[gradType]} gradient</span>\n${gradCodes[gradType]}`;
	}

	function drawShape() {
		if (!shapeCanvas) return;
		const ctx = shapeCanvas.getContext('2d')!;
		const W = shapeCanvas.width,
			H = shapeCanvas.height;
		const imgd = ctx.createImageData(W, H);
		const d = imgd.data;
		const cx = W / 2,
			cy = H / 2,
			r = Math.min(W, H) * 0.35;
		for (let y = 0; y < H; y++) {
			for (let x = 0; x < W; x++) {
				const i = (y * W + x) * 4;
				d[i] = 20;
				d[i + 1] = 20;
				d[i + 2] = 35;
				d[i + 3] = 255;
				let hit = false;
				if (shapeType === 'circle') {
					hit = (x - cx) ** 2 + (y - cy) ** 2 <= r * r;
				} else if (shapeType === 'ring') {
					const d2 = (x - cx) ** 2 + (y - cy) ** 2;
					hit = d2 >= (r - 6) ** 2 && d2 <= r * r;
				} else if (shapeType === 'rect') {
					const hw = r * 0.75,
						hh = r * 0.55;
					hit = Math.abs(x - cx) < hw && Math.abs(y - cy) < hh;
				} else if (shapeType === 'stripe') {
					hit = Math.floor(x / 30) % 2 === 0;
				} else if (shapeType === 'checker') {
					hit = (Math.floor(x / 30) + Math.floor(y / 30)) % 2 === 0;
				}
				if (hit) {
					d[i] = 0;
					d[i + 1] = 229;
					d[i + 2] = 200;
					d[i + 3] = 255;
				}
			}
		}
		ctx.putImageData(imgd, 0, 0);
		shapeCodeHtml = `<span class="lang-tag">python</span><span class="cm"># ${shapeType}</span>\n${shapeCodes[shapeType]}`;
	}

	function selectGrad(i: number) {
		gradType = i;
		drawGradient();
	}
	function selectShape(s: string) {
		shapeType = s;
		drawShape();
	}

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
		// reading progress
		const onScroll = () => {
			const scrolled = window.scrollY;
			const total = document.body.scrollHeight - window.innerHeight;
			readingProgress = Math.min(100, (scrolled / total) * 100);
		};
		window.addEventListener('scroll', onScroll);

		// init demos
		buildPGImage();
		drawPGCanvas();
		initMemColors();
		drawMemCanvas();
		buildRasterSource();
		drawRasterVector();
		drawGradient();
		drawShape();

		// noise animation
		let noiseRaf: number;
		function noiseTick() {
			if (pgType === 'noise') {
				buildPGImage();
				drawPGCanvas();
			}
			noiseRaf = requestAnimationFrame(noiseTick);
		}
		noiseTick();

		return () => {
			window.removeEventListener('scroll', onScroll);
			cancelAnimationFrame(noiseRaf);
		};
	});
</script>

<!-- ── HERO ── -->
<div class="module-hero">
	<div class="module-number" aria-hidden="true">01</div>
	<div class="module-tag">Module 01 · Theory + Practice</div>
	<h1 class="module-title">Pixels and the<br /><span>Structure of Images</span></h1>
	<div class="progress-bar-wrap">
		<div class="progress-bar-fill" style="width:{readingProgress}%"></div>
	</div>
</div>

<!-- ── TOC ── -->
<nav class="toc">
	<div class="toc-label">Contents</div>
	<ul class="toc-list">
		<li><a href="#objectives">Objectives</a></li>
		<li><a href="#what-is-pixel">What is a Pixel</a></li>
		<li><a href="#color-models">Color Models</a></li>
		<li><a href="#memory-layout">Memory Layout</a></li>
		<li><a href="#raster-vector">Raster vs Vector</a></li>
		<li><a href="#framebuffers">Framebuffers</a></li>
		<li><a href="#practical">Practical Work</a></li>
		<li><a href="#quiz">Quiz</a></li>
	</ul>
</nav>

<!-- ── OBJECTIVES ── -->
<section id="objectives" class="objectives">
	<div class="objectives-label">Learning Objectives</div>
	<ul>
		<li>Understand color models, pixel grids, and image channels</li>
		<li>Explain the difference between raster and vector representations</li>
		<li>Manipulate pixel data directly using Python and NumPy</li>
	</ul>
</section>

<!-- ── SECTION 1: WHAT IS A PIXEL ── -->
<section id="what-is-pixel" class="section">
	<div class="section-header">
		<span class="section-num">01.01</span>
		<h2 class="section-title">What is a Pixel?</h2>
	</div>
	<p>
		The word <em>pixel</em> is a contraction of <strong>pic</strong>ture <strong>el</strong>ement. A
		pixel is the smallest addressable unit in a raster image. Every digital image you have ever seen
		— on a phone screen, in a browser, in a game — is a rectangular grid of pixels, each assigned a
		color value.
	</p>
	<p>
		When you look at a high-resolution photograph, you perceive continuous tone: smooth gradients,
		sharp edges, fine detail. That perception is an illusion of density. Zoom in far enough and the
		grid becomes visible. This is the fundamental nature of raster images: they are <em>discrete</em
		>, not continuous.
	</p>
	<div class="callout">
		<div class="callout-label">Definition</div>
		A pixel has no inherent physical size. It is simply a position in a grid with an associated color.
		Physical size depends on the output device: a 100×100 image displayed at 96 dpi looks different than
		the same image at 300 dpi.
	</div>
	<!-- Demo: Pixel Grid -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Pixel Grid Explorer</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Hover over the canvas to inspect individual pixels. Use the zoom slider to reveal the
				discrete grid structure.
			</p>
			<div class="two-col" style="align-items:start;">
				<div>
					<canvas
						bind:this={pgCanvas}
						width="280"
						height="280"
						on:mousemove={onPGMove}
						style="border:1px solid var(--border2);cursor:crosshair;width:100%;"
					></canvas>
					<div class="pixel-info">
						<span style="color:var(--muted)">{pxCoords}</span>
					</div>
				</div>
				<div>
					<div class="slider-row">
						<label>Zoom</label>
						<input
							type="range"
							min="1"
							max="32"
							bind:value={pgZoom}
							on:input={() => drawPGCanvas()}
						/>
						<span class="slider-val">{pgZoom}×</span>
					</div>
					<div class="slider-row">
						<label>Image</label>
						<select
							bind:value={pgType}
							on:change={() => {
								buildPGImage();
								drawPGCanvas();
							}}
						>
							<option value="gradient">Gradient</option>
							<option value="circle">Circle</option>
							<option value="checkerboard">Checkerboard</option>
							<option value="noise">Noise</option>
						</select>
					</div>
					<div style="margin-top:1.5rem;font-size:12px;color:var(--muted);line-height:1.7;">
						<div style="margin-bottom:0.5rem;color:#fff;font-weight:500;">
							Pixel data at cursor:
						</div>
						<div>{pxCoords}</div>
						<div>{pxRgb}</div>
						<div>{pxHex}</div>
						<div style="margin-top:0.75rem;">{@html pxChannelsHtml}</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<p>
		The number of pixels in an image is its <strong>resolution</strong>. A 1920×1080 image contains
		exactly 2,073,600 pixels. This is the quantity that determines how much detail the image can
		represent — not its file size, and not its physical dimensions.
	</p>
</section>

<!-- ── SECTION 2: COLOR MODELS ── -->
<section id="color-models" class="section">
	<div class="section-header">
		<span class="section-num">01.02</span>
		<h2 class="section-title">Color Models: RGB, RGBA, and Formats</h2>
	</div>
	<p>
		A color model defines how color is represented numerically. The dominant model in game
		development and computer graphics is <strong>RGB</strong>: three channels, one each for red,
		green, and blue. By combining different intensities of these three primaries, every visible
		color can be approximated.
	</p>
	<p>
		In the most common representation, each channel is stored as an 8-bit unsigned integer, giving
		256 possible values per channel (0–255). Three channels give you 256³ = 16,777,216 possible
		colors. This is commonly written as <code>uint8</code> format.
	</p>
	<table>
		<thead><tr><th>Format</th><th>Channels</th><th>Bits per pixel</th><th>Use case</th></tr></thead>
		<tbody>
			<tr><td>RGB8</td><td>R, G, B</td><td>24</td><td>Standard opaque images</td></tr>
			<tr><td>RGBA8</td><td>R, G, B, A</td><td>32</td><td>Images with transparency</td></tr>
			<tr><td>R8 (Grayscale)</td><td>L</td><td>8</td><td>Heightmaps, masks</td></tr>
			<tr><td>RGB16F</td><td>R, G, B</td><td>48</td><td>HDR rendering</td></tr>
			<tr><td>RGBA32F</td><td>R, G, B, A</td><td>128</td><td>Floating point framebuffers</td></tr>
		</tbody>
	</table>
	<p>
		The <strong>alpha channel</strong> (A) represents opacity. A value of 255 means fully opaque; 0 means
		fully transparent. Alpha is used extensively in game development for sprite rendering, UI overlays,
		and compositing effects.
	</p>
	<p>
		Note that some systems normalize color values to the range <code>[0.0, 1.0]</code> as floating
		point, rather than <code>[0, 255]</code> as integers. GPU shaders always work in the normalized range.
		You will convert frequently between the two.
	</p>
	<!-- Demo: Color Mixer -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · RGBA Color Mixer</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<div class="two-col">
				<div>
					<div class="slider-row">
						<label style="color:#ff5f5f;">Red</label><input
							type="range"
							min="0"
							max="255"
							bind:value={R}
						/><span class="slider-val">{R}</span>
					</div>
					<div class="channel-strip" style="background:{rStrip}"></div>
					<div class="slider-row" style="margin-top:0.8rem;">
						<label style="color:#5fff80;">Green</label><input
							type="range"
							min="0"
							max="255"
							bind:value={G}
						/><span class="slider-val">{G}</span>
					</div>
					<div class="channel-strip" style="background:{gStrip}"></div>
					<div class="slider-row" style="margin-top:0.8rem;">
						<label style="color:#5f9fff;">Blue</label><input
							type="range"
							min="0"
							max="255"
							bind:value={B}
						/><span class="slider-val">{B}</span>
					</div>
					<div class="channel-strip" style="background:{bStrip}"></div>
					<div class="slider-row" style="margin-top:0.8rem;">
						<label>Alpha</label><input type="range" min="0" max="255" bind:value={A} /><span
							class="slider-val">{A}</span
						>
					</div>
					<div
						class="channel-strip"
						style="background:linear-gradient(to right,transparent,white)"
					></div>
				</div>
				<div style="display:flex;flex-direction:column;gap:1rem;">
					<div
						style="height:100px;border:1px solid var(--border2);position:relative;overflow:hidden;"
					>
						<div
							style="position:absolute;inset:0;background-image:repeating-conic-gradient(#333 0% 25%,#444 0% 50%);background-size:16px 16px;"
						></div>
						<div style="position:absolute;inset:0;background:{swatchColor};"></div>
					</div>
					<div style="font-size:12px;line-height:2;">
						<div>Hex: <span style="color:var(--accent)">{hexOut}</span></div>
						<div>RGB: <span style="color:var(--accent)">{rgbOut}</span></div>
						<div>RGBA: <span style="color:var(--accent)">{rgbaOut}</span></div>
						<div>Normalized: <span style="color:var(--accent3)">{normOut}</span></div>
						<div>Bytes: <span style="color:var(--muted)">{bytesOut}</span></div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="callout warn">
		<div class="callout-label">Common Confusion</div>
		RGB is an<em>additive</em> color model — mixing all three channels at full intensity gives white,
		not black. This is the opposite of paint mixing (subtractive). In games, mixing lights and colors
		on screen always follows additive rules.
	</div>
</section>

<!-- ── SECTION 3: MEMORY LAYOUT ── -->
<section id="memory-layout" class="section">
	<div class="section-header">
		<span class="section-num">01.03</span>
		<h2 class="section-title">Image Memory Layout</h2>
	</div>
	<p>
		Images are stored in memory as a flat, one-dimensional array of bytes. There is no inherent
		two-dimensionality in RAM. The 2D structure is a convention: rows of pixels are packed
		sequentially, and software applies a formula to locate any pixel by its (x, y) coordinates.
	</p>
	<p>
		For an image with width <code>W</code> and height <code>H</code> in RGBA format (4 bytes per
		pixel), the byte offset of pixel at column <code>x</code>, row <code>y</code> is:
	</p>
	<pre><code
			><span class="cm"># byte offset of pixel (x, y) in an RGBA image</span>
offset = (y * W + x) * 4

<span class="cm"># the four channel bytes at that offset:</span>
R = image_data[offset + 0]
G = image_data[offset + 1]
B = image_data[offset + 2]
A = image_data[offset + 3]<span class="lang-tag">python</span></code
		></pre>
	<p>
		This row-major ordering means that iterating across columns (increasing x) is cache-friendly —
		consecutive pixels are adjacent in memory. Iterating down rows (increasing y) jumps by <code
			>W × bytes_per_pixel</code
		> each step.
	</p>
	<!-- Demo: Memory Layout -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Memory Layout Visualizer</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				A 4×4 RGBA image. Hover over a pixel to highlight its corresponding bytes in memory.
			</p>
			<div style="display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;">
				<div>
					<div style="font-size:10px;color:var(--muted);margin-bottom:0.5rem;letter-spacing:0.1em;">
						IMAGE GRID (4×4)
					</div>
					<canvas
						bind:this={memCanvas}
						width="160"
						height="160"
						on:mousemove={onMemMove}
						style="cursor:pointer;border:1px solid var(--border2);display:block;"
					></canvas>
				</div>
				<div style="flex:1;min-width:200px;">
					<div style="font-size:10px;color:var(--muted);margin-bottom:0.5rem;letter-spacing:0.1em;">
						FLAT MEMORY ARRAY (64 bytes)
					</div>
					<div class="mem-grid">
						{#each memCells as cell}
							<div
								class="mem-cell"
								style="color:{cell.highlighted
									? 'var(--accent)'
									: cell.color};background:{cell.highlighted
									? 'rgba(0,229,200,0.15)'
									: ''};border-color:{cell.highlighted ? 'var(--accent)' : ''};"
							>
								{cell.highlighted ? cell.value : cell.label}
							</div>
						{/each}
					</div>
					<div style="font-size:11px;color:var(--muted);margin-top:0.75rem;">
						{@html memFormula}
					</div>
				</div>
			</div>
		</div>
	</div>
	<pre><code
			><span class="kw">import</span> numpy <span class="kw">as</span> np

<span class="cm"># Create a blank 100×100 RGBA image (all zeros = transparent black)</span>
img = np.zeros(<span class="num">100</span>, <span class="num">100</span>, <span class="num">4</span
			>), dtype=np.uint8)

<span class="cm"># Set pixel at (x=30, y=50) to opaque red</span>
img[<span class="num">50</span>, <span class="num">30</span>] = [<span class="num">255</span>, <span
				class="num">0</span
			>, <span class="num">0</span>, <span class="num">255</span>]

<span class="cm"># Set the entire red channel of a row to 128</span>
img[<span class="num">25</span>, :, <span class="num">0</span>] = <span class="num">128</span><span
				class="lang-tag">python</span
			></code
		></pre>
	<div class="callout">
		<div class="callout-label">Note</div>
		OpenGL and many GPU APIs use a different convention: the y-axis is flipped, with (0,0) at the bottom-left
		rather than the top-left. You will encounter this mismatch repeatedly when moving data between NumPy
		images and GPU textures.
	</div>
</section>

<!-- ── SECTION 4: RASTER vs VECTOR ── -->
<section id="raster-vector" class="section">
	<div class="section-header">
		<span class="section-num">01.04</span>
		<h2 class="section-title">Raster vs Vector Representations</h2>
	</div>
	<p>
		Raster images store colors on a fixed grid. Vector images store <em>instructions</em> for drawing
		shapes: "draw a circle of radius 50 at position (100, 100), filled with blue." The rendering engine
		executes those instructions at display time.
	</p>
	<!-- Demo -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Raster vs Vector at Scale</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				Drag the zoom slider. One representation degrades; the other remains sharp.
			</p>
			<div class="slider-row" style="margin-bottom:1.5rem;">
				<label>Zoom</label>
				<input
					type="range"
					min="1"
					max="12"
					bind:value={rvZoom}
					on:input={() => drawRasterVector()}
				/>
				<span class="slider-val">{rvZoom}×</span>
			</div>
			<div class="two-col">
				<div>
					<div
						style="font-size:10px;color:var(--accent2);letter-spacing:0.15em;margin-bottom:0.5rem;"
					>
						RASTER (bitmap)
					</div>
					<canvas
						bind:this={rasterCanvas}
						width="280"
						height="180"
						style="border:1px solid var(--border2);width:100%;"
					></canvas>
					<div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
						Pixels revealed at high zoom → aliasing
					</div>
				</div>
				<div>
					<div
						style="font-size:10px;color:var(--accent);letter-spacing:0.15em;margin-bottom:0.5rem;"
					>
						VECTOR (re-rendered at scale)
					</div>
					<canvas
						bind:this={vectorCanvas}
						width="280"
						height="180"
						style="border:1px solid var(--border2);width:100%;"
					></canvas>
					<div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
						Re-calculated at every zoom level → crisp
					</div>
				</div>
			</div>
		</div>
	</div>
	<table>
		<thead><tr><th>Property</th><th>Raster</th><th>Vector</th></tr></thead>
		<tbody>
			<tr><td>Storage</td><td>Grid of color values</td><td>Shape definitions</td></tr>
			<tr><td>Scaling</td><td>Degrades (aliasing)</td><td>Resolution-independent</td></tr>
			<tr><td>Detail</td><td>Photographic / arbitrary</td><td>Geometric / structured</td></tr>
			<tr><td>GPU processing</td><td>Direct texture upload</td><td>Must be rasterized first</td></tr
			>
			<tr><td>Game usage</td><td>Sprites, textures, maps</td><td>UI, fonts (pre-rasterized)</td></tr
			>
		</tbody>
	</table>
	<p>
		Game engines work almost exclusively with raster images at runtime. Vector assets (SVGs, fonts)
		are <em>rasterized</em> — converted to pixel grids — before being sent to the GPU. Once on the GPU,
		everything is pixels.
	</p>
</section>

<!-- ── SECTION 5: FRAMEBUFFERS ── -->
<section id="framebuffers" class="section">
	<div class="section-header">
		<span class="section-num">01.05</span>
		<h2 class="section-title">Framebuffers and Drawing by Writing</h2>
	</div>
	<p>
		A <strong>framebuffer</strong> is a region of memory that holds the pixel data for a single frame
		— what you see on screen right now. The display hardware reads this memory continuously, refreshing
		the screen at 60 or more times per second.
	</p>
	<p>
		"Rendering" a game frame means <em>writing pixel values into the framebuffer</em>. There is
		nothing magical about it. The GPU executes programs (shaders) that calculate what color each
		pixel should be, writes those values into memory, and the display hardware reads them out.
	</p>
	<p>
		Modern applications use at least two framebuffers: the <em>front buffer</em> (currently
		displayed) and the <em>back buffer</em> (currently being drawn into). When rendering is
		complete, the buffers are <em>swapped</em>. This prevents the user from seeing partial frames —
		a technique called <strong>double buffering</strong>.
	</p>
	<pre><code
			><span class="cm"># Conceptually, every frame the GPU does something like this:</span>
<span class="kw">for</span> y <span class="kw">in</span> <span class="fn">range</span>(height):
    <span class="kw">for</span> x <span class="kw">in</span> <span class="fn">range</span>(width):
        back_buffer[y, x] = <span class="fn">compute_pixel_color</span>(x, y, scene)

<span class="fn">swap_buffers</span>()  <span class="cm"
				># back becomes front, front becomes back</span
			><span class="lang-tag">python (pseudocode)</span></code
		></pre>
	<div class="callout">
		<div class="callout-label">Note</div>
		In reality, GPUs evaluate thousands of pixels in parallel using shader programs. The simple nested
		loop above is the correct mental model, but not the execution model. The parallelism is why GPUs exist.
	</div>
</section>

<hr class="divider" />

<!-- ── SECTION 6: PRACTICAL ── -->
<section id="practical" class="section">
	<div class="section-header">
		<span class="section-num">01.06</span>
		<h2 class="section-title">Practical Work</h2>
	</div>
	<p>
		The exercises below build toward direct manipulation of pixel data. No image libraries are used
		for drawing — only NumPy array operations and Pillow for display output.
	</p>

	<div style="margin:2rem 0;">
		<div
			style="font-size:10px;letter-spacing:0.2em;text-transform:uppercase;color:var(--accent2);margin-bottom:0.75rem;"
		>
			Exercise 1 · Create Images with Gradients
		</div>
		<p>A gradient sets pixel brightness proportional to position. For a horizontal gradient:</p>
		<pre><code
				><span class="kw">import</span> numpy <span class="kw">as</span> np
<span class="kw">from</span> PIL <span class="kw">import</span> Image

W, H = <span class="num">256</span>, <span class="num">256</span>
img = np.zeros((H, W, <span class="num">3</span>), dtype=np.uint8)

<span class="cm"># Horizontal gradient: red increases left → right</span>
<span class="kw">for</span> x <span class="kw">in</span> <span class="fn">range</span>(W):
    img[:, x, <span class="num">0</span>] = x

<span class="cm"># 2D gradient (more Pythonic using broadcasting)</span>
xs = np.arange(W, dtype=np.uint8)
ys = np.arange(H, dtype=np.uint8)
img[:, :, <span class="num">0</span>] = xs[np.newaxis, :]
img[:, :, <span class="num">1</span>] = ys[:, np.newaxis]

Image.<span class="fn">fromarray</span>(img).<span class="fn">save</span>(<span class="str"
					>"gradient.png"</span
				>)<span class="lang-tag">python</span></code
			></pre>
	</div>

	<!-- Demo: Gradient Builder -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Gradient Builder</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">
				{#each gradLabels as label, i}
					<button class="btn" class:active={gradType === i} on:click={() => selectGrad(i)}
						>{label}</button
					>
				{/each}
			</div>
			<canvas
				bind:this={gradCanvas}
				width="512"
				height="200"
				style="width:100%;border:1px solid var(--border2);image-rendering:auto;display:block;"
			></canvas>
			<pre style="margin-top:1rem;font-size:12px;">{@html gradCodeHtml}</pre>
		</div>
	</div>

	<div style="margin:2rem 0;">
		<div
			style="font-size:10px;letter-spacing:0.2em;text-transform:uppercase;color:var(--accent2);margin-bottom:0.75rem;"
		>
			Exercise 2 · Draw Shapes Using Pixel Math
		</div>
		<p>
			Drawing a circle without a graphics library means testing whether each pixel lies within the
			circle's equation: <em>x² + y² ≤ r²</em>. This is exactly how GPU fragment shaders draw
			shapes.
		</p>
		<pre><code
				><span class="kw">import</span> numpy <span class="kw">as</span> np
<span class="kw">from</span> PIL <span class="kw">import</span> Image

W, H = <span class="num">256</span>, <span class="num">256</span>
img = np.zeros((H, W, <span class="num">3</span>), dtype=np.uint8)
ys, xs = np.mgrid[<span class="num">0</span>:H, <span class="num">0</span>:W]
cx, cy, r = <span class="num">128</span>, <span class="num">128</span>, <span class="num">80</span>
dist_sq = (xs - cx)**<span class="num">2</span> + (ys - cy)**<span class="num">2</span>

<span class="cm"># Filled circle</span>
img[dist_sq &lt;= r**<span class="num">2</span>] = [<span class="num">0</span>, <span class="num"
					>229</span
				>, <span class="num">200</span>]

<span class="cm"># Ring (outline only)</span>
ring = (dist_sq &gt;= (r-<span class="num">2</span>)**<span class="num">2</span
				>) &amp; (dist_sq &lt;= r**<span class="num">2</span>)
img[ring] = [<span class="num">255</span>, <span class="num">95</span>, <span class="num">58</span
				>]<span class="lang-tag">python</span></code
			></pre>
	</div>

	<!-- Demo: Shape Renderer -->
	<div class="demo-box">
		<div class="demo-header">
			<span>Interactive · Pixel Shape Renderer</span>
			<span class="demo-badge interactive">INTERACTIVE</span>
		</div>
		<div class="demo-body">
			<p style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
				All shapes are drawn by evaluating a mathematical condition per pixel. No draw calls.
			</p>
			<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
				{#each Object.keys(shapeCodes) as s}
					<button class="btn" class:active={shapeType === s} on:click={() => selectShape(s)}
						>{s.charAt(0).toUpperCase() + s.slice(1)}</button
					>
				{/each}
			</div>
			<canvas
				bind:this={shapeCanvas}
				width="512"
				height="220"
				style="width:100%;border:1px solid var(--border2);image-rendering:auto;display:block;"
			></canvas>
			<pre style="margin-top:1rem;font-size:12px;">{@html shapeCodeHtml}</pre>
		</div>
	</div>
</section>

<hr class="divider" />

<!-- ── QUIZ ── -->
<section id="quiz" class="quiz-section">
	<div class="quiz-header">Module Quiz</div>
	<div class="quiz-sub">5 questions · Color spaces and pixel operations</div>
	{#each quizData as q, qi}
		<div class="question">
			<div class="q-text"><span class="q-num">{qi + 1}.</span>{q.q}</div>
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
			style="border-color:{quizScore === quizData.length
				? 'var(--accent)'
				: quizScore >= 3
					? 'var(--accent3)'
					: 'var(--accent2)'}"
		>
			<div class="score-num">{quizScore}/{quizData.length}</div>
			<div class="score-label">Module 01 complete. Proceed to Module 02 when ready.</div>
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
	.pixel-info {
		margin-top: 1rem;
		font-size: 12px;
		min-height: 1.4em;
	}
</style>
