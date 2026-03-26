<script lang="ts">
	import Module01 from '$lib/modules/animation/Module01.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
	$: mod = data.module;
	$: prev = data.prev;
	$: next = data.next;

	$: accent = `var(${mod.accentVar})`;
</script>

<svelte:head>
	<title>Module {mod.id} · {mod.title}</title>
	<meta name="description" content={mod.description} />
</svelte:head>

<div class="page-wrapper anim-theme">
	<!-- TOP NAV -->
	<header class="module-nav">
		<a href="/courses/animation" class="nav-back">← All Modules</a>
		<div class="nav-breadcrumb">
			<span>Animation Fundamentals</span>
			<span class="bc-sep">/</span>
			<span style="color:{accent}">Module {mod.id}</span>
		</div>
	</header>

	<!-- MODULE CONTENT (switch by id) -->
	{#if mod.id === '01'}
		<Module01 />
	{:else}
		<div style="padding:4rem 0;text-align:center;color:var(--anim-muted);">
			<div style="font-size:48px;margin-bottom:1rem;">🚧</div>
			<div style="font-size:14px;">
				Module {mod.id} · {mod.title} is coming soon.
			</div>
		</div>
	{/if}

	<!-- PREV / NEXT NAV -->
	<div class="module-footer-nav">
		{#if prev && prev.status === 'available'}
			<a href="/courses/animation/{prev.id}" class="fnav-card prev">
				<div class="fnav-label">← Previous</div>
				<div class="fnav-title">{prev.id} · {prev.title}</div>
			</a>
		{:else}
			<div></div>
		{/if}
		{#if next}
			<a
				href="/courses/animation/{next.id}"
				class="fnav-card next"
				class:disabled={next.status !== 'available'}
			>
				<div class="fnav-label">Next →</div>
				<div class="fnav-title">{next.id} · {next.title}</div>
				{#if next.status === 'coming-soon'}<div class="fnav-soon">Coming Soon</div>{/if}
			</a>
		{:else}
			<div></div>
		{/if}
	</div>
</div>

<style>
	/* ── NAV ── */
	.module-nav {
		border-bottom: 1px solid var(--border);
		padding: 1.25rem 0;
		display: flex;
		align-items: center;
		gap: 1rem;
		justify-content: space-between;
	}
	.nav-back {
		font-size: 11px;
		color: var(--muted);
		text-decoration: none;
		transition: color 0.15s;
	}
	.nav-back:hover {
		color: var(--anim-gold);
	}
	.nav-breadcrumb {
		font-size: 11px;
		color: var(--muted);
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.bc-sep {
		opacity: 0.4;
	}

	/* ── FOOTER NAV ── */
	.module-footer-nav {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1px;
		background: var(--border);
		margin: 4rem 0 0;
		border-top: 1px solid var(--border);
	}
	.fnav-card {
		display: block;
		padding: 1.5rem;
		background: var(--surface);
		text-decoration: none;
		transition: background 0.15s;
	}
	.fnav-card:hover:not(.disabled) {
		background: var(--anim-surface);
	}
	.fnav-card.disabled {
		opacity: 0.4;
		pointer-events: none;
	}
	.fnav-card.next {
		text-align: right;
	}
	.fnav-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 0.5rem;
	}
	.fnav-title {
		font-family: 'Fraunces', serif;
		font-size: 14px;
		font-weight: 700;
		color: #fff;
	}
	.fnav-soon {
		font-size: 10px;
		color: var(--anim-muted);
		margin-top: 0.25rem;
	}
</style>
