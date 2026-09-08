<script lang="ts">
	import type { ApiImage } from '$lib/api/types';
	import Picture from './Picture.svelte';

	// Full-viewport image viewer built on the native <dialog>: the top layer escapes any ancestor
	// transform, Escape closes it, focus is trapped while open and
	// restored to the trigger on close. `open` is two-way bound so the trigger owns the state.
	let { image, open = $bindable(false) }: { image: ApiImage; open?: boolean } = $props();
	let dialog: HTMLDialogElement | undefined = $state();

	$effect(() => {
		if (!dialog) return;
		if (open && !dialog.open) dialog.showModal();
		else if (!open && dialog.open) dialog.close();
	});

	function onBackdropClick(event: MouseEvent) {
		// The dialog itself fills the viewport, so any click that is not on the image closes it.
		if (event.target === dialog) open = false;
	}
</script>

<dialog
	bind:this={dialog}
	class="lightbox"
	aria-label={image.alt || 'Enlarged image'}
	onclose={() => (open = false)}
	onclick={onBackdropClick}
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
	<!-- Hidden dialogs are display:none, so the lazy image only loads once the lightbox opens. -->
	<Picture {image} sizes="100vw" class="lightbox-image" />
</dialog>

<style>
	.lightbox {
		/* Breathing room between the image and the screen edge; also the backdrop click target. */
		--gutter: clamp(1.25rem, 4vw, 3rem);
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
		cursor: zoom-out;
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
		max-height: calc(100vh - 2 * var(--gutter));
		object-fit: contain;
		cursor: default;
	}
	.lightbox-close {
		position: absolute;
		top: 0.75rem;
		right: 0.75rem;
		z-index: 1;
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border-radius: 9999px;
		background: var(--color-surface);
		color: var(--color-ink);
		box-shadow: 0 1px 3px rgb(0 0 0 / 0.4);
	}
</style>
