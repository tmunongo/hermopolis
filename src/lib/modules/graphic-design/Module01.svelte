<script>
	import { onMount } from 'svelte';

	/** @type {HTMLCanvasElement | null} */
	let canvas;
	/** @type {CanvasRenderingContext2D | null} */
	let ctx;

	// Canvas Controls State
	let enableGrid = false;
	let alignElements = false;
	let establishHierarchy = false;

	// Form Follows Function State
	let hoveredRole = 'none'; // 'thumbnail' or 'website'

	onMount(() => {
		canvas = /** @type {HTMLCanvasElement} */ (document.getElementById('demo-canvas'));
		if (canvas) {
			ctx = canvas.getContext('2d');
			// Handle high DPI displays
			const dpr = window.devicePixelRatio || 1;
			const rect = canvas.getBoundingClientRect();
			canvas.width = rect.width * dpr;
			canvas.height = rect.height * dpr;
			if (ctx) ctx.scale(dpr, dpr);
			drawCanvas();
		}
	});

	function toggleGrid() {
		enableGrid = !enableGrid;
		drawCanvas();
	}

	function toggleAlign() {
		alignElements = !alignElements;
		drawCanvas();
	}

	function toggleHierarchy() {
		establishHierarchy = !establishHierarchy;
		drawCanvas();
	}

	function drawCanvas() {
		if (!ctx || !canvas) return;
		const width = canvas.width / (window.devicePixelRatio || 1);
		const height = canvas.height / (window.devicePixelRatio || 1);

		// Clear background
		ctx.fillStyle = '#0f172a'; // Deep night blue
		ctx.fillRect(0, 0, width, height);

		// Grid Layer
		if (enableGrid) {
			ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
			ctx.lineWidth = 1;
			ctx.beginPath();
			// 3x3 Grid (Rule of Thirds)
			for (let i = 1; i <= 2; i++) {
				ctx.moveTo((width / 3) * i, 0);
				ctx.lineTo((width / 3) * i, height);
				ctx.moveTo(0, (height / 3) * i);
				ctx.lineTo(width, (height / 3) * i);
			}
			ctx.stroke();
		}

		// Positional calculations
		const titleX = alignElements ? width * 0.1 : width * 0.25;
		const titleY = alignElements ? height * 0.35 : height * 0.15;
		const titleSize = establishHierarchy ? 56 : 32;
		const titleColor = establishHierarchy ? '#ffffff' : '#94a3b8';

		const subX = alignElements ? width * 0.1 : width * 0.4;
		const subY = alignElements ? height * 0.55 : height * 0.6;
		const subSize = establishHierarchy ? 28 : 32;
		const subColor = establishHierarchy ? '#f43f5e' : '#94a3b8'; // --gd-rose

		const shapeX = alignElements ? width * 0.75 : width * 0.6;
		const shapeY = alignElements ? height * 0.5 : height * 0.75;
		const shapeScale = establishHierarchy ? 1 : 0.7;

		// Draw decorative shapes (Subject)
		ctx.save();
		ctx.translate(shapeX, shapeY);
		if (!alignElements) ctx.rotate(0.4);
		ctx.scale(shapeScale, shapeScale);

		// Abstract organic shape overlapping
		ctx.fillStyle = '#8b5cf6'; // --gd-violet
		ctx.beginPath();
		ctx.arc(-20, -20, 90, 0, Math.PI * 2);
		ctx.fill();

		ctx.fillStyle = '#0ea5e9'; // --gd-sky
		ctx.beginPath();
		ctx.rect(0, 0, 100, 100);
		ctx.fill();
		ctx.restore();

		// Draw Text
		ctx.textAlign = 'left';
		ctx.textBaseline = 'middle';
		ctx.font = `bold ${titleSize}px Inter, sans-serif`;
		ctx.fillStyle = titleColor;
		ctx.fillText('DESIGN IS', titleX, titleY);

		ctx.font = `bold ${subSize}px Inter, sans-serif`;
		ctx.fillStyle = subColor;
		ctx.fillText('INTENTIONAL', subX, subY);
	}
</script>

<div class="gd-theme page-wrapper">
	<div class="container pb-32">
		<!-- HEADER -->
		<header class="py-16 border-b border-[var(--gd-border)] mb-12">
			<div
				class="inline-block px-3 py-1 bg-[var(--gd-surface)] border border-[var(--gd-border)] rounded-full text-[var(--gd-rose)] text-sm font-bold tracking-wide uppercase mb-6"
			>
				Module 01
			</div>
			<h1 class="text-5xl font-black text-white tracking-tight mb-4">
				What Design Is <span class="text-[var(--gd-muted)] font-normal">(and Isn't)</span>
			</h1>
			<p class="text-[var(--gd-text)] text-xl max-w-2xl leading-relaxed">
				The myth of raw talent. We break down design into methodical problem-solving, turning
				invisible structures into conscious decisions.
			</p>
		</header>

		<!-- SECTION: THE MYTH -->
		<section class="mb-20">
			<h2 class="text-3xl font-bold text-white mb-6">The Myth of "Being Artistic"</h2>
			<div class="prose max-w-none text-[var(--gd-text)] text-lg mb-8 space-y-4">
				<p>
					The biggest barrier to creating a cohesive visual identity is the belief that design
					requires innate artistic talent. It doesn't. While art is an expression of the self that
					asks questions, <strong
						>graphic design is a tool that solves problems and communicates.</strong
					>
				</p>
			</div>

			<div class="concept-box">
				<div class="concept-header">
					<div class="concept-badge">CORE CONCEPT</div>
					<h3 class="font-bold text-white">Art vs. Design</h3>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
					<div class="p-6 bg-[var(--gd-bg)] rounded-xl border border-[var(--gd-border)]">
						<h4 class="text-[var(--gd-violet)] font-bold text-xl mb-3">🎨 Art</h4>
						<ul class="space-y-2 text-[var(--gd-text)]">
							<li><span class="text-[var(--gd-muted)]">•</span> Seeks to express an emotion</li>
							<li><span class="text-[var(--gd-muted)]">•</span> Asks questions and challenges</li>
							<li>
								<span class="text-[var(--gd-muted)]">•</span> Relies on talent and inspiration
							</li>
							<li>
								<span class="text-[var(--gd-muted)]">•</span> Is subjective and open to interpretation
							</li>
						</ul>
					</div>
					<div class="p-6 bg-[var(--gd-bg)] rounded-xl border border-[var(--gd-border)]">
						<h4 class="text-[var(--gd-amber)] font-bold text-xl mb-3">📐 Design</h4>
						<ul class="space-y-2 text-[var(--gd-text)]">
							<li><span class="text-[var(--gd-muted)]">•</span> Seeks to solve a problem</li>
							<li><span class="text-[var(--gd-muted)]">•</span> Provides answers and informs</li>
							<li><span class="text-[var(--gd-muted)]">•</span> Relies on rules and systems</li>
							<li>
								<span class="text-[var(--gd-muted)]">•</span> Is objective and measurable by success
							</li>
						</ul>
					</div>
				</div>
			</div>
		</section>

		<!-- SECTION: INTERACTIVE DEMO -->
		<section class="mb-20">
			<h2 class="text-3xl font-bold text-white mb-6">The Invisible Structure</h2>
			<p class="text-[var(--gd-text)] text-lg mb-8">
				When you have "good taste" but struggle to create, it's because you can instinctively sense
				the rules of design without knowing how to build upon them. Let's look at how applying three
				simple rules—Grids, Alignment, and Hierarchy—transforms layout chaos into a deliberate
				composition.
			</p>

			<div class="demo-box">
				<div
					class="demo-header flex justify-between items-center border-b border-[var(--gd-border)] pb-4 mb-6"
				>
					<h3 class="font-bold text-white">Interactive Playground</h3>
					<span class="demo-badge">INTERACTIVE</span>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
					<!-- Canvas Area -->
					<div
						class="lg:col-span-2 bg-black rounded-xl overflow-hidden border border-[var(--gd-border)] relative aspect-[16/9]"
					>
						<canvas id="demo-canvas" class="w-full h-full block touch-action-none"></canvas>
					</div>

					<!-- Controls -->
					<div class="flex flex-col gap-4">
						<div class="text-[var(--gd-muted)] text-sm font-semibold uppercase tracking-wider mb-2">
							Apply Rules
						</div>

						<button
							class="btn {enableGrid ? 'active gd-btn-sky' : 'gd-btn-outline'}"
							onclick={toggleGrid}
						>
							{#if enableGrid}
								▣ Structure: Rule of Thirds
							{:else}
								◻ Enable Grid
							{/if}
						</button>
						<div
							class="text-[var(--gd-text)] text-sm mb-4 ps-2 border-l-2 border-[var(--gd-border)]"
						>
							Grids provide the invisible scaffolding that anchors our elements.
						</div>

						<button
							class="btn {alignElements ? 'active gd-btn-amber' : 'gd-btn-outline'}"
							onclick={toggleAlign}
						>
							{#if alignElements}
								├┤ Elements Snapped
							{:else}
								╬ Align Elements
							{/if}
						</button>
						<div
							class="text-[var(--gd-text)] text-sm mb-4 ps-2 border-l-2 border-[var(--gd-border)]"
						>
							Alignment creates order. Chaos feels accidental; alignment feels intentional.
						</div>

						<button
							class="btn {establishHierarchy ? 'active gd-btn-rose' : 'gd-btn-outline'}"
							onclick={toggleHierarchy}
						>
							{#if establishHierarchy}
								⇡ Visual Hierarchy Set
							{:else}
								⇡ Establish Hierarchy
							{/if}
						</button>
						<div class="text-[var(--gd-text)] text-sm ps-2 border-l-2 border-[var(--gd-border)]">
							Hierarchy tells the viewer what to read first through scale, color, and contrast.
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- SECTION: FORM FOLLOWS FUNCTION -->
		<section class="mb-20">
			<h2 class="text-3xl font-bold text-white mb-6">Form Follows Function</h2>
			<p class="text-[var(--gd-text)] text-lg mb-8">
				In design, there is no single definition of "pretty." The success of a design completely
				depends on what it is trying to achieve. The visual weight and style of a YouTube thumbnail
				are entirely wrong for a high-end portfolio website, and vice versa.
			</p>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
				<!-- Context A -->
				<div
					class="p-6 rounded-xl border border-[var(--gd-border)] transition-all cursor-pointer {hoveredRole ===
					'thumbnail'
						? 'bg-[var(--gd-surface)] border-[var(--gd-amber)]'
						: 'bg-[var(--gd-bg)]'}"
					onmouseenter={() => (hoveredRole = 'thumbnail')}
					onmouseleave={() => (hoveredRole = 'none')}
					role="presentation"
				>
					<div
						class="aspect-video bg-[#1a1c29] rounded-lg mb-4 flex items-center justify-center p-4 border border-[var(--gd-border)] overflow-hidden relative"
					>
						<div
							class="absolute inset-0 bg-gradient-to-br from-[#f59e0b] to-[#dc2626] opacity-20"
						></div>
						<div class="z-10 text-center">
							<h4
								class="text-[#facc15] font-black text-4xl uppercase drop-shadow-[0_4px_4px_rgba(0,0,0,0.8)] transform -skew-x-6 rotate-[-2deg]"
							>
								MIND BLOWING!
							</h4>
							<div
								class="bg-white text-black font-bold uppercase py-1 px-3 mt-2 inline-block shadow-xl transform rotate-1"
							>
								Don't Miss This
							</div>
						</div>
					</div>
					<h3 class="font-bold text-white text-xl mb-2">The YouTube Thumbnail</h3>
					<p class="text-[var(--gd-muted)] text-sm mb-4">
						Goal: Capture attention in less than 0.5 seconds on a crowded screen.
					</p>

					<ul
						class="space-y-2 text-sm text-[var(--gd-text)] {hoveredRole === 'thumbnail'
							? 'opacity-100'
							: 'opacity-50'} transition-opacity"
					>
						<li>
							<span class="text-[var(--gd-amber)] font-bold">✓</span> Maximum contrast and saturation
						</li>
						<li>
							<span class="text-[var(--gd-amber)] font-bold">✓</span> Massive, legible typography
						</li>
						<li>
							<span class="text-[var(--gd-amber)] font-bold">✓</span> Zero negative space (fill the frame)
						</li>
					</ul>
				</div>

				<!-- Context B -->
				<div
					class="p-6 rounded-xl border border-[var(--gd-border)] transition-all cursor-pointer {hoveredRole ===
					'website'
						? 'bg-[var(--gd-surface)] border-[var(--gd-sky)]'
						: 'bg-[var(--gd-bg)]'}"
					onmouseenter={() => (hoveredRole = 'website')}
					onmouseleave={() => (hoveredRole = 'none')}
					role="presentation"
				>
					<div
						class="aspect-video bg-[#0f1115] rounded-lg mb-4 flex items-end justify-start p-8 border border-[var(--gd-border)] overflow-hidden"
					>
						<div>
							<div class="text-[#e2e8f0] font-light text-sm tracking-[0.2em] mb-4 uppercase">
								Selected Works
							</div>
							<h4 class="text-white font-serif text-3xl font-light">
								Elegance in the digital void.
							</h4>
						</div>
					</div>
					<h3 class="font-bold text-white text-xl mb-2">The Premium Portfolio</h3>
					<p class="text-[var(--gd-muted)] text-sm mb-4">
						Goal: Convey luxury, professionalism, and thoughtful pacing.
					</p>

					<ul
						class="space-y-2 text-sm text-[var(--gd-text)] {hoveredRole === 'website'
							? 'opacity-100'
							: 'opacity-50'} transition-opacity"
					>
						<li>
							<span class="text-[var(--gd-sky)] font-bold">✓</span> Muted, sophisticated palette
						</li>
						<li>
							<span class="text-[var(--gd-sky)] font-bold">✓</span> Elegant, thin typographic pairing
						</li>
						<li>
							<span class="text-[var(--gd-sky)] font-bold">✓</span> Abundant negative space (allows breathing)
						</li>
					</ul>
				</div>
			</div>
		</section>

		<!-- KEY INSIGHT SUMMARY -->
		<div
			class="key-insight relative overflow-hidden bg-[var(--gd-surface)] border-l-4 border-[var(--gd-rose)] p-8 rounded-r-xl shadow-lg"
		>
			<div
				class="absolute -right-4 -top-4 text-[var(--gd-border)] text-9xl font-serif opacity-20 transform rotate-12 rotate-[-5deg]"
			>
				"
			</div>
			<div
				class="key-insight-label text-[var(--gd-rose)] font-bold tracking-wider uppercase text-sm mb-4 flex items-center gap-2"
			>
				<span class="w-2 h-2 rounded-full bg-[var(--gd-rose)] animate-pulse"></span> Key Takeaway
			</div>
			<p class="text-2xl font-light text-white leading-relaxed relative z-10">
				Design is a framework. You are not creating "art"—you are strategically applying rules like
				grids, alignment, and hierarchy to solve a communication problem.
				<strong class="font-bold text-white block mt-4"
					>Once you understand the rules, you can control the outcome.</strong
				>
			</p>
		</div>
	</div>
</div>

<style>
	/* Module-specific styles using --gd prefix variables defined in app.css */

	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.75rem 1.5rem;
		border-radius: 0.5rem;
		font-weight: 600;
		transition: all 0.2s;
		cursor: pointer;
		width: 100%;
		border: 1px solid transparent;
	}

	.gd-btn-outline {
		background-color: transparent;
		color: var(--gd-text);
		border-color: var(--gd-border);
	}

	.gd-btn-outline:hover {
		background-color: var(--gd-surface);
		color: white;
	}

	.gd-btn-sky {
		background-color: rgba(14, 165, 233, 0.1);
		color: var(--gd-sky);
		border-color: var(--gd-sky);
	}

	.gd-btn-amber {
		background-color: rgba(245, 158, 11, 0.1);
		color: var(--gd-amber);
		border-color: var(--gd-amber);
	}

	.gd-btn-rose {
		background-color: rgba(244, 63, 94, 0.1);
		color: var(--gd-rose);
		border-color: var(--gd-rose);
	}

	.concept-box {
		background: var(--gd-surface);
		border: 1px solid var(--gd-border);
		border-radius: 1rem;
		padding: 2rem;
		position: relative;
		overflow: hidden;
	}

	.concept-header {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.concept-badge {
		background: rgba(139, 92, 246, 0.15);
		color: var(--gd-violet);
		padding: 0.25rem 0.75rem;
		border-radius: 999px;
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 1px;
		width: fit-content;
	}

	.demo-badge {
		background: var(--gd-border);
		color: var(--gd-text);
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
		font-size: 0.7rem;
		font-weight: 700;
		letter-spacing: 1px;
	}
</style>
