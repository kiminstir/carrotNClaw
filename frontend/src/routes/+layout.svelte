<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import AudioPlayer from '$lib/components/AudioPlayer.svelte';

	let { data, children } = $props();
	const showPlayer = $derived(data.settings.music.enabled && data.settings.music.tracks.length > 0);
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex min-h-dvh flex-col">
	<Header header={data.settings.header} />

	{#key page.url.pathname}
		<main class="flex-1" in:fade={{ duration: 200 }}>
			{@render children()}
		</main>
	{/key}

	<Footer footer={data.settings.footer} />

	{#if showPlayer}
		<AudioPlayer music={data.settings.music} />
	{/if}
</div>
