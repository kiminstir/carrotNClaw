<script lang="ts">
	import BlockRenderer from '$lib/blocks/BlockRenderer.svelte';
	import ScrollVine from '$lib/components/ScrollVine.svelte';

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
	<header class="page-heading">
		<h1>{data.page.title}</h1>
		{#if data.page.intro}<p>{data.page.intro}</p>{/if}
	</header>
{/if}

<BlockRenderer blocks={data.page.body} />
<ScrollVine />
