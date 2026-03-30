<script lang="ts">
	import Module01 from '$lib/modules/graphic-design/Module01.svelte';
	import Module02 from '$lib/modules/graphic-design/Module02.svelte';
	import Module03 from '$lib/modules/graphic-design/Module03.svelte';
	import Module04 from '$lib/modules/graphic-design/Module04.svelte';
	import Module05 from '$lib/modules/graphic-design/Module05.svelte';
	import ScrollProgress from '$lib/components/ScrollProgress.svelte';
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

<div class="page-wrapper gd-theme">
	<!-- TOP NAV -->
	<header class="module-nav">
		<a href="/courses/graphic-design" class="nav-back">← All Modules</a>
		<div class="nav-breadcrumb">
			<span>Graphic Design &amp; Visual Storytelling</span>
			<span class="bc-sep">/</span>
			<span style="color:{accent}">Module {mod.id}</span>
		</div>
	</header>

	<ScrollProgress accentColor={accent} />

	<!-- MODULE CONTENT (switch by id) -->
	{#if mod.id === '01'}
		<Module01 />
	{:else if mod.id === '02'}
		<Module02 />
	{:else if mod.id === '03'}
		<Module03 />
	{:else if mod.id === '04'}
		<Module04 />
	{:else if mod.id === '05'}
		<Module05 />
	{:else}
		<div style="padding:4rem 0;text-align:center;color:var(--gd-muted);">
			<div style="font-size:48px;margin-bottom:1rem;">🚧</div>
			<div style="font-size:14px;">
				Module {mod.id} · {mod.title} is coming soon.
			</div>
		</div>
	{/if}

	<!-- PREV / NEXT NAV -->
	<div class="module-footer-nav">
		{#if prev && prev.status === 'available'}
			<a href="/courses/graphic-design/{prev.id}" class="fnav-card prev">
				<div class="fnav-label">← Previous</div>
				<div class="fnav-title">{prev.id} · {prev.title}</div>
			</a>
		{:else}
			<div></div>
		{/if}
		{#if next}
			<a
				href="/courses/graphic-design/{next.id}"
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
		border-bottom: 1px solid var(--gd-border);
		padding: 1.25rem 0;
		display: flex;
		align-items: center;
		gap: 1rem;
		justify-content: space-between;
	}
	.nav-back {
		font-size: 11px;
		color: var(--gd-muted);
		text-decoration: none;
		transition: color 0.15s;
	}
	.nav-back:hover {
		color: var(--gd-rose);
	}
	.nav-breadcrumb {
		font-size: 11px;
		color: var(--gd-muted);
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
		background: var(--gd-border);
		margin: 4rem 0 0;
		border-top: 1px solid var(--gd-border);
	}
	.fnav-card {
		display: block;
		padding: 1.5rem;
		background: var(--gd-surface);
		text-decoration: none;
		transition: background 0.15s;
	}
	.fnav-card:hover:not(.disabled) {
		background: var(--gd-raised);
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
		color: var(--gd-muted);
		margin-bottom: 0.5rem;
	}
	.fnav-title {
		font-family: 'Syne', sans-serif;
		font-size: 14px;
		font-weight: 700;
		color: #fff;
	}
	.fnav-soon {
		font-size: 10px;
		color: var(--gd-muted);
		margin-top: 0.25rem;
	}
</style>
