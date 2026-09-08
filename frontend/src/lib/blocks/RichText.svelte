<script lang="ts">
	import type { RichTextValue } from '$lib/api/types';
	import { layoutRichTextImages } from './richTextImages';
	import { richTextClasses } from './richTextStyles';

	let { value }: { value: RichTextValue } = $props();
	const styleClasses = $derived(richTextClasses(value));
	const html = $derived(layoutRichTextImages(value.text));
</script>

<!-- eslint-disable-next-line svelte/no-at-html-tags -->
<div class="content-copy mx-auto prose max-w-3xl px-4 py-6 {styleClasses}">{@html html}</div>
