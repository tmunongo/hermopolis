<script lang="ts">
	import { onMount } from 'svelte';

	export let accentColor = 'var(--accent)';

	let readingProgress = 0;

	onMount(() => {
		const onScroll = () => {
			const scrolled = window.scrollY;
			const total = document.body.scrollHeight - window.innerHeight;
			readingProgress = total > 0 ? Math.min(100, (scrolled / total) * 100) : 0;
		};
		window.addEventListener('scroll', onScroll);
		onScroll(); // initialize

		return () => {
			window.removeEventListener('scroll', onScroll);
		};
	});
</script>

<div class="universal-progress-wrap">
	<div
		class="universal-progress-fill"
		style="width:{readingProgress}%; background:{accentColor};"
	></div>
</div>

<style>
	.universal-progress-wrap {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 3px;
		background: transparent;
		z-index: 1000;
		pointer-events: none;
	}
	.universal-progress-fill {
		height: 100%;
		width: 0;
		transition: width 0.1s ease-out;
	}
</style>
