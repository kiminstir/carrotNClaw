<script lang="ts">
	import type { ApiImage } from '$lib/api/types';
	import DialogSlider from './DialogSlider.svelte';

	// Detail pop-up for a card, built on the native <dialog> like Lightbox: the top layer escapes
	// ancestor transforms, Escape closes it, focus is trapped while open and restored on close.
	// `open` is owned by the card grid; every way of closing ends in the dialog's `close` event,
	// which reports back through `onclose`.
	let {
		id,
		title,
		subtitle = '',
		price = '',
		description,
		images = [],
		imageFit = 'contain',
		open = false,
		onclose
	}: {
		id: string;
		title: string;
		subtitle?: string;
		price?: string;
		description: string;
		/** Several photos become a slider; one is shown as a plain figure. */
		images?: ApiImage[];
		/** cover: 3:4 portrait crop around the focal point (photos); contain: shown whole (artwork). */
		imageFit?: 'cover' | 'contain';
		open?: boolean;
		onclose: () => void;
	} = $props();
	const hasImages = $derived(images.length > 0);
	// Side by side the figure is up to 46% of a 76rem panel; stacked it is the full panel.
	const boxSizes = '(min-width: 768px) 35rem, 100vw';
	let dialog: HTMLDialogElement | undefined = $state();

	$effect(() => {
		if (!dialog) return;
		if (open && !dialog.open) dialog.showModal();
		else if (!open && dialog.open) dialog.close();
	});

	function onBackdropClick(event: MouseEvent) {
		// The dialog element fills the viewport; the panel sits inside it, so a click on the
		// dialog itself is a click on the backdrop.
		if (event.target === dialog) dialog?.close();
	}
</script>

<dialog
	bind:this={dialog}
	{id}
	class="card-dialog"
	aria-labelledby="{id}-title"
	{onclose}
	onclick={onBackdropClick}
>
	<article class="card-dialog-panel" class:has-image={hasImages}>
		<button
			type="button"
			class="card-dialog-close"
			aria-label="Close"
			onclick={() => dialog?.close()}
		>
			<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
				<path
					d="M6 6l12 12M18 6L6 18"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
				/>
			</svg>
		</button>
		{#if hasImages}
			<figure class="card-dialog-figure fit-{imageFit}">
				<DialogSlider {images} fit={imageFit} sizes={boxSizes} />
			</figure>
		{/if}
		<div class="card-dialog-body">
			<header class="card-dialog-header">
				<h2 id="{id}-title">{title}</h2>
				{#if price}<span class="card-price">{price}</span>{/if}
			</header>
			{#if subtitle}<p class="card-dialog-subtitle">{subtitle}</p>{/if}
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			<div class="content-copy prose">{@html description}</div>
		</div>
	</article>
</dialog>

<style>
	.card-dialog {
		--gutter: clamp(1rem, 4vw, 3rem);
		position: fixed;
		inset: 0;
		width: 100vw;
		height: 100vh;
		max-width: none;
		max-height: none;
		margin: 0;
		padding: var(--gutter);
		box-sizing: border-box;
		border: 0;
		background: transparent;
		color: var(--color-ink);
	}
	.card-dialog::backdrop {
		background: color-mix(in srgb, var(--forest-deep) 88%, transparent);
	}
	.card-dialog[open] {
		display: grid;
		place-items: center;
	}
	.card-dialog-panel {
		position: relative;
		display: grid;
		width: min(100%, 76rem);
		max-height: calc(100vh - 2 * var(--gutter));
		overflow: auto;
		border: 1px solid var(--wood-edge);
		border-radius: 6px;
		background: var(--wood-grain), var(--wood);
		box-shadow:
			inset 0 0 0 4px #171e1640,
			0 24px 60px #00000080;
		opacity: 1;
		transform: none;
		transition:
			opacity 220ms ease-out,
			transform 220ms ease-out;
	}
	@starting-style {
		.card-dialog[open] .card-dialog-panel {
			opacity: 0;
			transform: translateY(0.75rem);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.card-dialog-panel {
			transition: none;
		}
	}
	/* The slider sizes the photos: whole for artwork, a 3:4 cover crop for portraits. The figure
	   sets the box and, via --photo-max-height, how tall a whole artwork may grow. */
	.card-dialog-figure {
		--photo-max-height: 45vh;
		margin: 4px 4px 0;
		display: grid;
		place-items: center;
		overflow: hidden;
		background: #0000003d;
		border-radius: 3px 3px 0 0;
	}
	.card-dialog-figure.fit-cover {
		position: relative;
		aspect-ratio: 3 / 4;
		max-height: 55vh;
	}
	.card-dialog-body {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		padding: 2rem 2.25rem 2.5rem;
	}
	.card-dialog-header {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
		padding-right: 2.5rem;
	}
	.card-dialog-header h2 {
		font-family: var(--font-display);
		font-size: clamp(1.6rem, 3vw, 2.1rem);
		line-height: 1.15;
		letter-spacing: -0.025em;
	}
	.card-dialog-subtitle {
		margin-top: -0.35rem;
		color: var(--color-muted);
		font-size: 0.95rem;
	}
	.card-dialog-body :global(.prose) {
		max-width: none;
		margin-top: 0.5rem;
	}
	.card-dialog-close {
		position: absolute;
		top: 0.75rem;
		right: 0.75rem;
		z-index: 1;
		display: grid;
		place-items: center;
		width: 2.5rem;
		height: 2.5rem;
		border-radius: 9999px;
		background: var(--color-surface);
		color: var(--color-ink);
		box-shadow: 0 1px 3px rgb(0 0 0 / 0.4);
	}
	@media (min-width: 768px) {
		/* The photo takes just under half the panel, capped so a 3:4 figure still fits the
		   viewport height (minus the dialog gutters and the panel's inner frame). */
		.card-dialog-panel.has-image {
			--figure-width: min(46%, calc((100vh - 2 * var(--gutter) - 8px) * 3 / 4));
			grid-template-columns: var(--figure-width) minmax(0, 1fr);
		}
		.card-dialog-figure {
			--photo-max-height: calc(100vh - 2 * var(--gutter) - 8px);
			margin: 4px 0 4px 4px;
			align-self: stretch;
			border-radius: 3px 0 0 3px;
		}
		/* Side by side, the 3:4 figure sets the panel height; longer text stretches it and the
		   cover crop simply shows a little more of the photo. */
		.card-dialog-figure.fit-cover {
			max-height: none;
		}
		.card-dialog-body {
			padding: 2.75rem 3rem 3rem;
		}
		.card-dialog-header h2 {
			font-size: clamp(1.8rem, 2.6vw, 2.4rem);
		}
	}
</style>
