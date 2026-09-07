<script lang="ts">
	import type { CardGridValue } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';

	let { value }: { value: CardGridValue } = $props();
	const cols = {
		'2': 'md:grid-cols-2',
		'3': 'md:grid-cols-3',
		'4': 'md:grid-cols-2 lg:grid-cols-4'
	}[value.columns];
</script>

<div class="mx-auto grid max-w-6xl gap-6 px-4 py-6 {cols}">
	{#each value.cards as card, i (i)}
		<article class="flex flex-col overflow-hidden rounded-lg border border-white/10 bg-surface-2">
			{#if card.image}
				<Picture
					image={card.image}
					sizes="(min-width: 768px) 33vw, 100vw"
					class="aspect-[4/3] w-full object-cover"
				/>
			{/if}
			<div class="flex flex-1 flex-col gap-1 p-4">
				<div class="flex items-baseline justify-between gap-2">
					<h3 class="font-display text-xl">{card.title}</h3>
					{#if card.price}<span class="text-accent">{card.price}</span>{/if}
				</div>
				{#if card.subtitle}<p class="text-sm text-muted">{card.subtitle}</p>{/if}
				{#if card.text}<p class="mt-2 text-sm">{card.text}</p>{/if}
				{#if card.link}
					<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
					<a href={card.link.href} class="mt-auto pt-3 text-sm text-accent underline"
						>{card.link.label}</a
					>
				{/if}
			</div>
		</article>
	{/each}
</div>
