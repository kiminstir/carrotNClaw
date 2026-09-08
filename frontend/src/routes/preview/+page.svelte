<script lang="ts">
	import BlockRenderer from '$lib/blocks/BlockRenderer.svelte';

	let { data } = $props();
</script>

<svelte:head><title>Preview · {data.page.title}</title></svelte:head>

<p class="bg-accent-2 px-4 py-1 text-center text-sm">Preview — unpublished changes</p>

{#if data.page.body[0]?.type !== 'hero'}
	<header class="page-heading">
		<h1>{data.page.title}</h1>
		{#if data.page.intro}<p>{data.page.intro}</p>{/if}
	</header>
{/if}

<BlockRenderer blocks={data.page.body} />
