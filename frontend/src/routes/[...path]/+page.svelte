<script lang="ts">
	import BlockRenderer from '$lib/blocks/BlockRenderer.svelte';

	let { data } = $props();
	const title = $derived(data.page.meta.seo_title || data.page.title);
</script>

<svelte:head>
	<title>{title} · Carrot&Claw</title>
	{#if data.page.meta.search_description}
		<meta name="description" content={data.page.meta.search_description} />
	{/if}
</svelte:head>

{#if data.page.body[0]?.type !== 'hero'}
	<header class="mx-auto max-w-6xl px-4 pt-12 pb-4">
		<h1 class="font-display text-4xl md:text-5xl">{data.page.title}</h1>
		{#if data.page.intro}<p class="mt-3 max-w-2xl text-lg text-muted">{data.page.intro}</p>{/if}
	</header>
{/if}

<BlockRenderer blocks={data.page.body} />
