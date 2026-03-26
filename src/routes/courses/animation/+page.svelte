<script lang="ts">
	import { animationCourse, animationModules } from '$lib/data/courses';
	const course = animationCourse;
	const modules = animationModules;
</script>

<svelte:head>
	<title>{course.title} — {course.subtitle}</title>
	<meta name="description" content={course.description} />
</svelte:head>

<div class="page-wrapper">
	<!-- HEADER -->
	<header class="course-header">
		<div>
			<a href="/" class="back-link">← Hermopolis</a>
			<div class="course-name">{course.title}</div>
		</div>
		<div class="course-tag">{course.totalModules} Modules</div>
	</header>

	<!-- HERO -->
	<div class="course-hero">
		<div class="hero-ghost" aria-hidden="true">ANIM</div>
		<div class="hero-label">Animation Fundamentals</div>
		<h1 class="hero-title">Motion, Characters & Visual <span>Storytelling</span></h1>
		<p class="hero-desc">{course.description}</p>
		<div class="hero-tags">
			<span class="tag" style="border-color: var(--anim-gold); color: var(--anim-gold)">Motion</span
			>
			<span class="tag">Rigging</span>
			<span class="tag">Interactive</span>
			<span class="tag">10 Modules</span>
			<span class="tag free">Free</span>
		</div>
	</div>

	<!-- MODULE GRID -->
	<section class="modules-section">
		<div class="modules-label">Course Modules</div>
		<div class="modules-grid">
			{#each modules as mod}
				{#if mod.status === 'available'}
					<a href="/courses/animation/{mod.id}" class="module-card available">
						<div class="card-num" style="color: var({mod.accentVar})">
							{mod.id.padStart(2, '0')}
						</div>
						<div
							class="card-tag"
							style="color: var({mod.accentVar}); border-color: var({mod.accentVar})"
						>
							{mod.subtitle}
						</div>
						<div class="card-title">{mod.title}</div>
						<div class="card-desc">{mod.description}</div>
						<div class="card-go" style="color: var({mod.accentVar})">Open Module →</div>
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
	<footer>
		<div class="footer-content">
			<div class="footer-logo">Hermopolis</div>
			<!-- <div class="footer-links">
				<a href="/courses">Courses</a>
				<a href="/about">About</a>
				<a href="/contact">Contact</a>
			</div> -->
			<div>
				<p>All rights reserved © 2026 Hermopolis</p>
				<p>
					Built for <strong>learners</strong> by
					<a class="footer-link" href="https://tawandamunongo.dev/">Tawanda Munongo</a>
				</p>
			</div>
		</div>
	</footer>
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
		color: var(--anim-gold);
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
		font-family: 'Fraunces', serif;
		font-size: clamp(60px, 12vw, 120px);
		font-weight: 800;
		line-height: 1;
		color: transparent;
		-webkit-text-stroke: 1px var(--anim-border2);
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
		color: var(--anim-gold);
		margin-bottom: 1rem;
	}
	.hero-title {
		font-family: 'Fraunces', serif;
		font-size: clamp(36px, 6vw, 64px);
		font-weight: 800;
		line-height: 1.1;
		color: #fff;
		margin-bottom: 1.5rem;
	}
	.hero-title span {
		color: var(--anim-gold);
		font-style: italic;
	}
	.hero-desc {
		font-family: 'Plus Jakarta Sans', sans-serif;
		font-size: 14px;
		color: var(--anim-muted);
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
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		border: 1px solid var(--anim-border2);
		color: var(--anim-muted);
		padding: 3px 10px;
	}
	.tag.free {
		border-color: var(--anim-gold);
		color: var(--anim-gold);
	}

	/* ── MODULES GRID ── */
	.modules-section {
		margin: 4rem 0;
	}
	.modules-label {
		font-size: 10px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--anim-muted);
		margin-bottom: 2rem;
	}
	.modules-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 1px;
		background: var(--anim-border);
	}

	.module-card {
		background: var(--anim-surface);
		padding: 1.75rem;
		position: relative;
		transition: background 0.2s;
		text-decoration: none;
		color: inherit;
		display: block;
	}
	.module-card.available:hover {
		background: var(--anim-raised);
	}
	.module-card.coming-soon {
		opacity: 0.4;
		cursor: default;
	}

	.card-num {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		letter-spacing: 0.12em;
		font-weight: 700;
		margin-bottom: 0.75rem;
	}
	.card-tag {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		border: 1px solid;
		padding: 2px 8px;
		display: inline-block;
		margin-bottom: 1rem;
	}
	.card-badge {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		border: 1px solid var(--anim-border2);
		color: var(--anim-muted);
		padding: 2px 8px;
		display: inline-block;
		margin-bottom: 1rem;
	}
	.card-title {
		font-family: 'Fraunces', serif;
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-bottom: 0.5rem;
		line-height: 1.3;
	}
	.card-desc {
		font-family: 'Plus Jakarta Sans', sans-serif;
		font-size: 13px;
		color: var(--anim-muted);
		line-height: 1.8;
		margin-bottom: 1rem;
	}
	.card-go {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		letter-spacing: 0.05em;
	}

	@media (max-width: 640px) {
		.modules-grid {
			grid-template-columns: 1fr;
		}
	}

	.footer-link {
		text-decoration: underline;
	}
</style>
