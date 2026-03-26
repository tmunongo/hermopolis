<script lang="ts">
	import { gameDevCourse, gameDevModules } from '$lib/data/courses';
	const course = gameDevCourse;
	const modules = gameDevModules;
</script>

<svelte:head>
	<title>Course Platform — Game Development Fundamentals</title>
	<meta
		name="description"
		content="Learn game development from pixels to a complete 2D game. Interactive modules with visualizations, code, and quizzes."
	/>
</svelte:head>

<!-- HERO -->
<section class="hero">
	<div class="hero-inner">
		<div class="hero-eyebrow">COURSE PLATFORM</div>
		<h1 class="hero-title">Learn <span>Game Dev</span><br />from First Principles</h1>
		<p class="hero-desc">
			Interactive courses that take you from the fundamentals of computer graphics all the way to
			building complete games — with visualizations, code, and quizzes at every step.
		</p>
	</div>
	<div class="hero-grid-bg" aria-hidden="true"></div>
</section>

<!-- COURSES -->
<main class="courses-section">
	<div class="courses-inner">
		<div class="section-label">AVAILABLE COURSES</div>

		<a href="/courses/game-dev" class="course-card">
			<div class="card-accent-bar"></div>
			<div class="card-body">
				<div class="card-eyebrow">12 Modules · Python + GPU Fundamentals</div>
				<h2 class="card-title">{course.title}</h2>
				<p class="card-subtitle">{course.subtitle}</p>
				<p class="card-desc">{course.description}</p>
				<div class="card-meta">
					<div class="meta-modules">
						{#each modules as mod}
							<div
								class="meta-dot"
								class:active={mod.status === 'available'}
								title={mod.title}
							></div>
						{/each}
					</div>
					<span class="meta-count"
						>{modules.filter((m) => m.status === 'available').length} / {modules.length} modules available</span
					>
				</div>
				<div class="card-cta">Start Learning →</div>
			</div>
		</a>

		<!-- Placeholder for future courses -->
		<div class="course-card soon">
			<div class="card-body">
				<div class="card-eyebrow" style="color: var(--muted)">COMING SOON</div>
				<h2 class="card-title" style="color: var(--muted)">More Courses</h2>
				<p class="card-desc" style="color: var(--muted)">
					Additional courses are in development. Check back soon for new content on web development,
					systems programming, and more.
				</p>
			</div>
		</div>
	</div>
</main>

<style>
	/* ── HERO ── */
	.hero {
		position: relative;
		min-height: 60vh;
		display: flex;
		align-items: center;
		overflow: hidden;
		border-bottom: 1px solid var(--border);
	}
	.hero-inner {
		max-width: 960px;
		margin: 0 auto;
		padding: 6rem 2rem;
		position: relative;
		z-index: 1;
	}
	.hero-eyebrow {
		font-size: 10px;
		letter-spacing: 0.3em;
		text-transform: uppercase;
		color: var(--accent);
		margin-bottom: 1.5rem;
	}
	.hero-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(42px, 8vw, 84px);
		font-weight: 800;
		line-height: 1.05;
		color: #fff;
		margin-bottom: 2rem;
	}
	.hero-title span {
		color: var(--accent);
	}
	.hero-desc {
		font-size: 14px;
		color: var(--muted);
		max-width: 560px;
		line-height: 1.9;
		margin: 0;
	}
	.hero-grid-bg {
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(var(--border) 1px, transparent 1px),
			linear-gradient(90deg, var(--border) 1px, transparent 1px);
		background-size: 60px 60px;
		mask-image: radial-gradient(ellipse 80% 80% at 80% 50%, black, transparent);
		opacity: 0.4;
	}

	/* ── COURSES ── */
	.courses-section {
		padding: 4rem 0 8rem;
	}
	.courses-inner {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem;
	}
	.section-label {
		font-size: 10px;
		letter-spacing: 0.3em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 2rem;
	}

	/* ── COURSE CARD ── */
	.course-card {
		display: block;
		position: relative;
		border: 1px solid var(--border);
		background: var(--surface);
		text-decoration: none;
		color: inherit;
		margin-bottom: 1.5rem;
		transition:
			border-color 0.2s,
			transform 0.2s;
		overflow: hidden;
	}
	.course-card:not(.soon):hover {
		border-color: var(--accent);
		transform: translateY(-2px);
	}
	.course-card.soon {
		opacity: 0.4;
		cursor: default;
	}
	.card-accent-bar {
		height: 2px;
		background: linear-gradient(90deg, var(--accent), var(--accent3), var(--accent2));
	}
	.card-body {
		padding: 2rem;
	}
	.card-eyebrow {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--accent);
		margin-bottom: 1rem;
	}
	.card-title {
		font-family: 'Syne', sans-serif;
		font-size: 28px;
		font-weight: 800;
		color: #fff;
		margin-bottom: 0.25rem;
	}
	.card-subtitle {
		font-size: 13px;
		color: var(--accent3);
		margin-bottom: 1.5rem;
	}
	.card-desc {
		font-size: 13px;
		color: var(--muted);
		line-height: 1.9;
		margin-bottom: 1.5rem;
	}
	.card-meta {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
	}
	.meta-modules {
		display: flex;
		gap: 4px;
	}
	.meta-dot {
		width: 8px;
		height: 8px;
		border-radius: 1px;
		background: var(--border2);
		transition: background 0.2s;
	}
	.meta-dot.active {
		background: var(--accent);
	}
	.meta-count {
		font-size: 11px;
		color: var(--muted);
	}
	.card-cta {
		display: inline-block;
		font-size: 12px;
		color: var(--accent);
		border: 1px solid var(--accent);
		padding: 6px 18px;
		transition: all 0.15s;
	}
	.course-card:not(.soon):hover .card-cta {
		background: color-mix(in srgb, var(--accent) 15%, transparent);
	}
</style>
