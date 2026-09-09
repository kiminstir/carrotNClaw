<script lang="ts">
	import type { CardGridValue } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';
	import Branch from '$lib/components/Branch.svelte';
	import CardDialog from '$lib/components/CardDialog.svelte';
	import { track } from '$lib/analytics';
	import {
		PORTRAIT_ASPECT,
		coverSizes,
		focalPositionStyle,
		hasDescription,
		popupImage
	} from './cards';

	let { value, id }: { value: CardGridValue; id: string } = $props();
	const cols = $derived(
		{ '2': 'md:grid-cols-2', '3': 'md:grid-cols-3', '4': 'md:grid-cols-2 lg:grid-cols-4' }[
			value.columns
		]
	);
	const sizes = $derived(
		{
			'2': '(min-width: 768px) 50vw, 100vw',
			'3': '(min-width: 768px) 33vw, 100vw',
			'4': '(min-width: 1024px) 25vw, (min-width: 768px) 50vw, 100vw'
		}[value.columns]
	);
	const portrait = $derived(value.style === 'portrait');
	// Index of the card whose pop-up is open; the dialog's close event clears it.
	let openIndex: number | null = $state(null);

	function openCard(i: number) {
		openIndex = i;
		track('card-open', { title: value.cards[i].title });
	}
</script>

<div class="card-grid mx-auto grid max-w-6xl {cols}">
	{#each value.cards as card, i (i)}
		{@const interactive = hasDescription(card)}
		{@const dialogId = `${id}-card-${i}`}
		<article
			class="tavern-card"
			class:card-portrait={portrait}
			class:card-artwork={!portrait}
			class:is-interactive={interactive}
		>
			{#if i === 0}<Branch kind="oak" />
			{:else if i === value.cards.length - 1}<Branch kind="willow" corner="bottom-right" />{/if}
			{#if card.image}
				{#if portrait}
					<!-- The photo fills the whole card; the focal point set in the admin decides which
					     part the cover crop keeps in view. The text sits over the bottom band. -->
					<figure class="card-figure">
						<Picture
							image={card.image}
							sizes={coverSizes(sizes, card.image, PORTRAIT_ASPECT)}
							class="card-art"
							style={focalPositionStyle(card.image)}
						/>
					</figure>
				{:else}
					<!-- Card images are cut-out artwork on a transparent background (menu dishes, drinks),
					     so they are shown whole and centered rather than cropped to a cover. -->
					<Picture image={card.image} {sizes} class="card-art" />
				{/if}
			{/if}
			<div class="card-content">
				<div class="flex items-baseline justify-between gap-2">
					<h3>
						{#if interactive}
							<!-- The button's ::after stretches over the whole card, so any click opens the
							     pop-up; the card link keeps its own stacking level and still works. -->
							<button
								type="button"
								class="card-open"
								aria-haspopup="dialog"
								aria-controls={dialogId}
								onclick={() => openCard(i)}>{card.title}</button
							>
						{:else}
							{card.title}
						{/if}
					</h3>
					{#if card.price}<span class="card-price">{card.price}</span>{/if}
				</div>
				{#if card.subtitle}<p class="text-sm text-muted">{card.subtitle}</p>{/if}
				{#if card.text}<p class="mt-2 text-sm">{card.text}</p>{/if}
				{#if card.link}
					<!-- eslint-disable svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
					<a
						href={card.link.href}
						target={card.link.external ? '_blank' : undefined}
						rel={card.link.external ? 'noopener' : undefined}
						class="card-link">{card.link.label}</a
					>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
				{:else if interactive}
					<span class="card-more" aria-hidden="true">Read more</span>
				{/if}
			</div>
		</article>
		{#if interactive}
			<CardDialog
				id={dialogId}
				title={card.title}
				subtitle={card.subtitle}
				price={card.price}
				description={card.description}
				image={popupImage(card)}
				imageFit={portrait ? 'cover' : 'contain'}
				open={openIndex === i}
				onclose={() => (openIndex = null)}
			/>
		{/if}
	{/each}
</div>
