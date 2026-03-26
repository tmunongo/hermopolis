<script lang="ts">
	import '../app.css';
</script>

<slot />

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

<style>
	footer {
		border-top: 1px solid var(--border);
		padding: 2rem 0;
		text-align: center;
		font-size: 12px;
		color: var(--muted);
	}
	.footer-content {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem;
	}
	.footer-logo {
		font-family: 'Syne', sans-serif;
		font-size: 24px;
		font-weight: 800;
		color: var(--accent);
	}
	.footer-link {
		color: var(--accent);
		text-decoration: none;
	}
	.footer-link:hover {
		text-decoration: underline;
	}
</style>
