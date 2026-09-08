<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import { prefersReducedMotion } from 'svelte/motion';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import AudioPlayer from '$lib/components/AudioPlayer.svelte';

	let { data, children } = $props();
	const showPlayer = $derived(data.settings.music.enabled && data.settings.music.tracks.length > 0);
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<a href="#main-content" class="skip-link">Skip to content</a>
<div class="site-shell" class:has-player={showPlayer}>
	<Header header={data.settings.header} />

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
