<script lang="ts">
	import { onMount } from 'svelte';
	import { VINE_WIDTH, leafGrown, vineLayout, vineProgress, type VineLayout } from '$lib/vine';

	// A vine drawn down the left gutter of <main> as the visitor scrolls, with a leaf beside the
	// top of every content block. It needs real measurements, so it renders nothing on the
	// server and appears after mount; CSS keeps it hidden where there is no gutter.
	const LEAF_OFFSET = 28; // px below a block's top edge, roughly level with its first line

	let layout: VineLayout | null = $state(null);
	let top = $state(0); // px from the top of <main>
	let height = $state(0);
	let progress = $state(1);
	let stem: SVGPathElement | undefined = $state();
	let length = $state(0);

	onMount(() => {
		const main = document.getElementById('main-content');
		if (!main) return;
		const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		let docTop = 0; // vine top in document coordinates
		let frame = 0;

		function update() {
			frame = 0;
			progress = reduce ? 1 : vineProgress(window.scrollY, window.innerHeight, docTop, height);
		}
		function onScroll() {
			if (!frame) frame = requestAnimationFrame(update);
		}
		function measure() {
			const sections = [
				...main!.querySelectorAll<HTMLElement>(
					':scope > section[data-block]:not([data-block="hero"])'
				)
			];
			if (sections.length === 0) {
				layout = null;
				return;
			}
			const first = sections[0];
			const last = sections[sections.length - 1];
			top = first.offsetTop;
			height = last.offsetTop + last.offsetHeight - top;
			docTop = main!.getBoundingClientRect().top + window.scrollY + top;
			layout = vineLayout(
				height,
				sections.map((s) => s.offsetTop - top + LEAF_OFFSET)
			);
			update();
		}

		measure();
		const observer = new ResizeObserver(measure);
		observer.observe(main);
		window.addEventListener('scroll', onScroll, { passive: true });
		window.addEventListener('resize', measure);
		return () => {
			observer.disconnect();
			window.removeEventListener('scroll', onScroll);
			window.removeEventListener('resize', measure);
			if (frame) cancelAnimationFrame(frame);
		};
	});

	$effect(() => {
		if (stem && layout) length = stem.getTotalLength();
	});
</script>

{#if layout && height > 0}
	<svg
		class="scroll-vine"
		style="--vine-top: {top}px; --vine-height: {height}px; --vine-width: {VINE_WIDTH}px"
		viewBox="0 0 {VINE_WIDTH} {height}"
		width={VINE_WIDTH}
		{height}
		aria-hidden="true"
		data-testid="scroll-vine"
	>
		<defs>
			<!-- Same leaf as the willow branch artwork. -->
			<g id="vine-leaf">
				<path
					d="M0 0C-17-11-15-34-4-54C5-35 10-15 0 0Z"
					fill="#5e7048"
					stroke="#8c9a6b"
					stroke-width=".7"
				/>
				<path d="M0 0Q-4-22-4-45" stroke="#a3aa78" stroke-width=".65" fill="none" />
			</g>
		</defs>
		<path
			bind:this={stem}
			class="vine-stem"
			d={layout.d}
			style="stroke-dasharray: {length}; stroke-dashoffset: {length *
				(1 - progress)}; opacity: {length ? 1 : 0}"
		/>
		{#each layout.leaves as leaf, i (i)}
			<g
				class="vine-leaf"
				class:is-grown={leafGrown(leaf.y, progress, height)}
				transform="translate({leaf.x} {leaf.y}) rotate({leaf.angle}) scale(0.62)"
			>
				<use href="#vine-leaf" class="vine-leaf-shape" />
			</g>
		{/each}
	</svg>
{/if}
