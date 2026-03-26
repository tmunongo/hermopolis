<script lang="ts">
	import { gameDevCourse, gameDevModules } from '$lib/data/courses';
	const course = gameDevCourse;
	const modules = gameDevModules;

	const accentColors: Record<string, string> = {
		'--accent': '#00e5c8',
		'--accent2': '#ff5f3a',
		'--accent3': '#a78bfa'
	};
</script>

<svelte:head>
	<title>{course.title} — {course.subtitle}</title>
	<meta name="description" content={course.description} />
</svelte:head>

<div class="page-wrapper">
	<!-- HEADER -->
	<header class="course-header">
		<div>
			<a href="/" class="back-link">← Course Platform</a>
			<div class="course-name">{course.title}</div>
		</div>
		<div class="course-tag">{course.totalModules} Modules</div>
	</header>

	<!-- HERO -->
	<div class="course-hero">
		<div class="hero-ghost" aria-hidden="true">COURSE</div>
		<div class="hero-label">Game Development Fundamentals</div>
		<h1 class="hero-title">From <span>Pixels</span> to Play</h1>
		<p class="hero-desc">{course.description}</p>
		<div class="hero-tags">
			<span class="tag">Python</span>
			<span class="tag">GPU Fundamentals</span>
			<span class="tag">Interactive</span>
			<span class="tag">12 Modules</span>
			<span class="tag free">Free</span>
		</div>
	</div>

	<!-- MODULE GRID -->
	<section class="modules-section">
		<div class="modules-label">Course Modules</div>
		<div class="modules-grid">
			{#each modules as mod}
				{#if mod.status === 'available'}
					<a href="/courses/game-dev/{mod.id}" class="module-card available">
						<div class="card-num" style="color: {accentColors[mod.accentVar] ?? 'var(--accent)'}">
							{mod.id.padStart(2, '0')}
						</div>
						<div
							class="card-tag"
							style="color: {accentColors[mod.accentVar] ??
								'var(--accent)'}; border-color: {accentColors[mod.accentVar] ?? 'var(--accent)'}"
						>
							{mod.subtitle}
						</div>
						<div class="card-title">{mod.title}</div>
						<div class="card-desc">{mod.description}</div>
						<div class="card-go" style="color: {accentColors[mod.accentVar] ?? 'var(--accent)'}">
							Open Module →
						</div>
					</a>
				{:else}
					<div class="module-card coming-soon">
						<div class="card-num">{mod.id.padStart(2, '0')}</div>
						<div class="card-badge">Coming Soon</div>
						<div class="card-title">{mod.title}</div>
						<div class="card-desc">{mod.description}</div>
					</div>
				{/if}
			{/each}
		</div>
	</section>
</div>

<style>
	.course-header {
		border-bottom: 1px solid var(--border);
		padding: 1.5rem 0;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.back-link {
		font-size: 11px;
		color: var(--muted);
		text-decoration: none;
		display: block;
		margin-bottom: 0.25rem;
		transition: color 0.15s;
	}
	.back-link:hover {
		color: var(--accent);
	}
	.course-name {
		font-family: 'Syne', sans-serif;
		font-size: 14px;
		color: var(--text);
		font-weight: 600;
	}
	.course-tag {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--muted);
		border: 1px solid var(--border);
		padding: 4px 12px;
	}

	/* ── HERO ── */
	.course-hero {
		padding: 5rem 0 4rem;
		border-bottom: 1px solid var(--border);
		position: relative;
		overflow: hidden;
	}
	.hero-ghost {
		font-family: 'Syne', sans-serif;
		font-size: clamp(60px, 12vw, 120px);
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
	.hero-label {
		font-size: 10px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--accent);
		margin-bottom: 1rem;
	}
	.hero-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(36px, 6vw, 64px);
		font-weight: 800;
		line-height: 1.1;
		color: #fff;
		margin-bottom: 1.5rem;
	}
	.hero-title span {
		color: var(--accent);
	}
	.hero-desc {
		font-size: 13px;
		color: var(--muted);
		max-width: 600px;
		line-height: 1.9;
		margin-bottom: 2rem;
	}
	.hero-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.tag {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		border: 1px solid var(--border2);
		color: var(--muted);
		padding: 3px 10px;
	}
	.tag.free {
		border-color: var(--accent);
		color: var(--accent);
	}

	/* ── MODULES GRID ── */
	.modules-section {
		margin: 4rem 0;
	}
	.modules-label {
		font-size: 10px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 2rem;
	}
	.modules-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 1px;
		background: var(--border);
	}

	.module-card {
		background: var(--surface);
		padding: 1.75rem;
		position: relative;
		transition: background 0.2s;
		text-decoration: none;
		color: inherit;
		display: block;
	}
	.module-card.available:hover {
		background: var(--raised);
	}
	.module-card.coming-soon {
		opacity: 0.4;
		cursor: default;
	}

	.card-num {
		font-family: 'Syne', sans-serif;
		font-size: 11px;
		letter-spacing: 0.12em;
		font-weight: 700;
		margin-bottom: 0.75rem;
	}
	.card-tag {
		font-size: 9px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		border: 1px solid;
		padding: 2px 8px;
		display: inline-block;
		margin-bottom: 1rem;
	}
	.card-badge {
		font-size: 9px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		border: 1px solid var(--border2);
		color: var(--muted);
		padding: 2px 8px;
		display: inline-block;
		margin-bottom: 1rem;
	}
	.card-title {
		font-family: 'Syne', sans-serif;
		font-size: 16px;
		font-weight: 700;
		color: #fff;
		margin-bottom: 0.5rem;
		line-height: 1.3;
	}
	.card-desc {
		font-size: 11px;
		color: var(--muted);
		line-height: 1.8;
		margin-bottom: 1rem;
	}
	.card-go {
		font-size: 11px;
		letter-spacing: 0.05em;
	}

	@media (max-width: 640px) {
		.modules-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
