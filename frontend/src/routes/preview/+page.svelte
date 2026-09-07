<script lang="ts">
	import BlockRenderer from '$lib/blocks/BlockRenderer.svelte';

	let { data } = $props();
</script>

<svelte:head><title>Preview · {data.page.title}</title></svelte:head>

<p class="bg-accent-2 px-4 py-1 text-center text-sm">Preview — unpublished changes</p>

{#if data.page.body[0]?.type !== 'hero'}
	<header class="mx-auto max-w-6xl px-4 pt-12 pb-4">
		<h1 class="font-display text-4xl md:text-5xl">{data.page.title}</h1>
		{#if data.page.intro}<p class="mt-3 max-w-2xl text-lg text-muted">{data.page.intro}</p>{/if}
	</header>
{/if}

<BlockRenderer blocks={data.page.body} />
