<script lang="ts">
	import type { SliderImage } from '$lib/api/types';
	import Picture from './Picture.svelte';
	import { track } from '$lib/analytics';

	// Full-viewport image viewer built on the native <dialog>: the top layer escapes any ancestor
	// transform, Escape closes it, focus is trapped while open and restored to the trigger on
	// close. Given several items it also browses them with side buttons and the arrow keys,
	// wrapping at the ends. `open` and `index` are two-way bound so the trigger owns the state.
	let {
		items,
		index = $bindable(0),
		open = $bindable(false)
	}: { items: SliderImage[]; index?: number; open?: boolean } = $props();
	let dialog: HTMLDialogElement | undefined = $state();

	const current = $derived(items[Math.min(index, items.length - 1)]);
	const many = $derived(items.length > 1);
	const hasStrip = $derived(many || current.caption !== '');

	$effect(() => {
		if (!dialog) return;
		if (open && !dialog.open) dialog.showModal();
		else if (!open && dialog.open) dialog.close();
	});

	function step(delta: number) {
		index = (index + delta + items.length) % items.length;
		track('lightbox-arrow', { direction: delta > 0 ? 'next' : 'prev' });
	}

	function onKeydown(event: KeyboardEvent) {
		if (!many) return;
		if (event.key === 'ArrowRight') step(1);
		else if (event.key === 'ArrowLeft') step(-1);
		else return;
		event.preventDefault();
	}

	function onBackdropClick(event: MouseEvent) {
		// The dialog itself fills the viewport, so any click that is not on the image closes it.
		if (event.target === dialog) open = false;
	}
</script>

<dialog
	bind:this={dialog}
	class="lightbox"
	class:has-strip={hasStrip}
	aria-label={current.image.alt || 'Enlarged image'}
	onclose={() => (open = false)}
	onclick={onBackdropClick}
	onkeydown={onKeydown}
>
	<button type="button" class="lightbox-close" aria-label="Close" onclick={() => (open = false)}>
		<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
			<path
				d="M6 6l12 12M18 6L6 18"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
			/>
		</svg>
	</button>
	{#if many}
		<button
			type="button"
			class="lightbox-nav lightbox-prev"
			aria-label="Previous image"
			onclick={() => step(-1)}
		>
			<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
				<path
					d="M14.5 6L8.5 12l6 6"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					fill="none"
				/>
			</svg>
		</button>
		<button
			type="button"
			class="lightbox-nav lightbox-next"
			aria-label="Next image"
			onclick={() => step(1)}
		>
			<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
				<path
					d="M9.5 6l6 6-6 6"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					fill="none"
				/>
			</svg>
		</button>
	{/if}
	<!-- Hidden dialogs are display:none, so the lazy image only loads once the lightbox opens.
	     Keyed so a change of image swaps the element rather than reusing a stale src. -->
	{#key current.image.id}
		<Picture image={current.image} sizes="100vw" class="lightbox-image" />
	{/key}
	{#if hasStrip}
		<div class="lightbox-strip">
			{#if current.caption}<span class="lightbox-caption">{current.caption}</span>{/if}
			{#if many}
				<span class="lightbox-counter" data-testid="lightbox-counter"
					>{index + 1} of {items.length}</span
				>
			{/if}
		</div>
	{/if}
</dialog>

<style>
	.lightbox {
		/* Breathing room between the image and the screen edge; also the backdrop click target. */
		--gutter: clamp(1.25rem, 4vw, 3rem);
		--strip: 0px;
		position: fixed;
		inset: 0;
		width: 100vw;
		height: 100vh;
		max-width: none;
		max-height: none;
		margin: 0;
		padding: var(--gutter);
		padding-bottom: calc(var(--gutter) + var(--strip));
		box-sizing: border-box;
		border: 0;
		background: transparent;
		color: var(--color-ink);
		cursor: zoom-out;
	}
	.lightbox.has-strip {
		--strip: 1.9rem;
	}
	.lightbox::backdrop {
		background: color-mix(in srgb, var(--forest-deep) 92%, transparent);
	}
	.lightbox[open] {
		display: grid;
		place-items: center;
		opacity: 1;
		transition: opacity 200ms ease-out;
	}
	@starting-style {
		.lightbox[open] {
			opacity: 0;
		}
	}
	.lightbox :global(.lightbox-image) {
		display: block;
		width: auto;
		height: auto;
		max-width: calc(100vw - 2 * var(--gutter));
		max-height: calc(100vh - 2 * var(--gutter) - var(--strip));
		object-fit: contain;
		cursor: default;
	}
	.lightbox-close,
	.lightbox-nav {
		position: absolute;
		z-index: 1;
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border-radius: 9999px;
		background: var(--color-surface);
		color: var(--color-ink);
		box-shadow: 0 1px 3px rgb(0 0 0 / 0.4);
		cursor: pointer;
	}
	.lightbox-close {
		top: 0.75rem;
		right: 0.75rem;
	}
	.lightbox-nav {
		top: 50%;
		translate: 0 -50%;
	}
	.lightbox-prev {
		left: 0.75rem;
	}
	.lightbox-next {
		right: 0.75rem;
	}
	.lightbox-strip {
		position: absolute;
		left: var(--gutter);
		right: var(--gutter);
		bottom: 0.7rem;
		display: flex;
		justify-content: center;
		align-items: baseline;
		gap: 1.25rem;
		font-size: 0.9rem;
		color: var(--color-muted);
		cursor: default;
	}
	.lightbox-caption {
		font-family: var(--font-display);
		font-style: italic;
		color: #e3d9bf;
		text-align: center;
	}
	.lightbox-counter {
		flex-shrink: 0;
		font-size: 0.8rem;
		letter-spacing: 0.02em;
		font-variant-numeric: tabular-nums;
	}
</style>
