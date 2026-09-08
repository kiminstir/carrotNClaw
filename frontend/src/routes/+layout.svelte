<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import { prefersReducedMotion } from 'svelte/motion';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import AudioPlayer from '$lib/components/AudioPlayer.svelte';

	let { data, children } = $props();
	const showPlayer = $derived(data.settings.music.enabled && data.settings.music.tracks.length > 0);
</script>

<svelte:head>
	<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48" />
	<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
	<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png" />
	<link rel="icon" type="image/png" sizes="512x512" href="/icon-512.png" />
	<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
	<meta name="theme-color" content="#17291f" />
</svelte:head>

<a href="#main-content" class="skip-link">Skip to content</a>
<div class="site-shell" class:has-player={showPlayer}>
	<Header header={data.settings.header} hours={data.settings.hours} />

	{#key page.url.pathname}
		<main
			id="main-content"
			tabindex="-1"
			in:fade={{ duration: prefersReducedMotion.current ? 0 : 200 }}
		>
			{@render children()}
		</main>
	{/key}

	<Footer footer={data.settings.footer} siteTitle={data.settings.header.site_title} />

	{#if showPlayer}
		<AudioPlayer music={data.settings.music} />
	{/if}
</div>
